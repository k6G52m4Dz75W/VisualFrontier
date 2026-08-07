#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — 把带 include 指令与变量的源模板 (*.src.md) 生成最终 .md

用法:
    python build.py [--root .]

源模板支持两种机制:
1) 片段引用（include）
    <!-- include: _partials/zh/weights.md -->
    - 递归内联，带循环保护；片段路径相对于仓库根目录。

2) 变量替换（{{VAR}}）
    - 模板 / 片段中的 {{VAR_NAME}} 会被 .src.md frontmatter 里
      `vars:` 指向的变量文件中的值替换。
    - 变量文件为极简 key: value 格式（支持 # 注释与空白行），
      无需额外依赖。
    - 例如 _partials/vars/deepseek-ocr-2.yml:
          MODEL_NAME: DeepSeek-OCR-2
          ENV_NAME: deepseek-ocr-2
    - 未定义的变量保留原样（如 {{UNKNOWN}}），不报错。
    - 另含**步骤自动编号占位符**（无需 yml，由 build.py 在 inline + 语言过滤后
      统一计算，zh/en 两版序号必然一致）：
        {{STEP}}        ：普通顺序步骤，按文档顺序补零 2 位（01, 02, ...）
        {{STEP_GROUP}} ：并行“二选一”组的首个选项（如 02-A）
        {{STEP_ALT}}   ：同组后续选项，大号相同、字母递增（02-B, 02-C）
        {{OPTIONAL}}   ：可选步骤/小节的“（可选）/[Optional]”标签，在语言过滤阶段
            按当前语言展开（zh → 【可选】，en → [Optional]）
      可选步骤不含 {{STEP}}，不消耗序号，排在编号步骤之间但不带数字。
    - 另含**内置自动变量**（日期，无需 yml，用户 yml 同名可覆盖）：
        {{DATE_ZH}} / {{DATE_EN}}：取「本次 build 的时间」（重新生成那一刻的
            日期），分别格式化为中文点号(2026.7.25) / 英文短横线(2026-7-25)。
            用于「最后更新」等场景——改了部件重新 build，日期就是 build 当天。
        {{DATE_ZH:path}} / {{DATE_EN:path}}：同为 build 时间（path 仅作占位，
            保留语法兼容，不再按文件取时间）。
      日期 = build 时间，直观且符合「修改 → 重新生成 → 日期刷新」的预期。
      为兼容 CI 漂移检查：build.py 判断「是否需重写 .md」时会忽略「最后更新 /
      Last updated」所在行，因此跨天重新 build 不会因日期变化产生无意义 diff，
      仅在「除日期外」的内容真正变化时才重写并触发 CI 漂移告警。

输出文件 = 同目录、同名但去掉 .src（README.src.md -> README.md）。
生成时自动剔除 frontmatter 中的 `vars:` 行，保持 .md 整洁。

生成后还会做一次「拼接专属语法自检」（self_check），作为门禁：
  - 代码围栏(```)必须成对（某个 partial 漏写结束 ``` 会被拦下）
  - 不得残留未解析的 include 指令
  - 不得残留未替换的 {{VAR}} 变量
  - 标题层级不得跳级（拼接边界丢失父级标题会触发）
任一项不通过则打印 ::error:: 并以 exit(1) 终止，防止错误文档入库。

建议接进 pre-commit 或 GitHub Action：
若生成结果与已提交的 .md 不一致则失败，防止「片段」与「生成文件」漂移。
"""
import argparse
import os
import re
import sys
from datetime import datetime

INCLUDE_RE = re.compile(r"<!--\s*include:\s*([^\s]+)\s*-->")
VARS_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")
# 带路径的日期变量：{{DATE_ZH:path}} / {{DATE_EN:path}}
DATE_PATH_RE = re.compile(r"\{\{\s*DATE_(ZH|EN)\s*:\s*([^}]*?)\s*\}\}")
ROOT = "."


def norm(t):
    """忽略尾部空行差异，用于判断生成内容是否与已提交 .md 实质一致。"""
    t = t.replace("\r\n", "\n")
    lines = t.split("\n")
    while lines and lines[-1].strip() == "":
        lines.pop()
    return "\n".join(lines)


DATE_LINE_RE = re.compile(r"最后更新|Last updated")


def norm_ignore_date(t):
    """同 norm，但额外忽略「最后更新 / Last updated」所在行。

    日期取 build 时间，跨天重新 build 会因日期变化产生无意义 diff；
    忽略这些行后，仅当「除日期外」的内容真正变化时才视为需重写，
    从而兼容 CI 的漂移检查（内容漂移仍会触发告警）。
    """
    t = norm(t)
    lines = [ln for ln in t.split("\n") if not DATE_LINE_RE.search(ln)]
    return "\n".join(lines)


LANG_LINE_RE = re.compile(r"^\s*<!--\s*(zh|en)\s*-->\s*(.*)$")


def src_lang(fn):
    """根据顶层 src 文件名判定目标语言：.en.src.md → en，其余 → zh。

    语言是文档级（整篇中文或英文），所有被 include 的部件都按同一语言过滤，
    故在 inline 展开后统一过滤一次即可，无需逐层传递。
    """
    return "en" if fn.endswith(".en.src.md") else "zh"


def filter_lang(text, lang):
    """按目标语言抽取行：

    - 以 ``<!-- zh -->`` / ``<!-- en -->`` 开头的行：仅当标记语言 == lang 时
      保留，并去掉标记前缀；另一语言的标记行整行丢弃。保留前先把行内的
      ``{{OPTIONAL}}`` 按语言展开为 ``【可选】``（zh）/ ``[Optional]``（en）。
    - 其余行（命令、代码块、空行、include 指令、普通说明等）原样保留，
      视为中英共用。

    这样「命令/无标记行共用、说明文字逐行分语言」，一个部件文件即可双语同体，
    改一处中英同步，且不会漏改。
    """
    out = []
    for line in text.split("\n"):
        m = LANG_LINE_RE.match(line)
        if m:
            if m.group(1) == lang:
                body = m.group(2)
                if "{{OPTIONAL}}" in body:
                    body = body.replace(
                        "{{OPTIONAL}}", "【可选】" if lang == "zh" else "[Optional]"
                    )
                out.append(body)
        else:
            out.append(line)
    return "\n".join(out)


STEP_RE = re.compile(r"\{\{\s*STEP(_GROUP|_ALT)?\s*\}\}")


def number_steps(text):
    """按文档顺序为步骤占位符分配序号（inline + filter_lang 之后调用）。

    - {{STEP}}      普通顺序步骤：大号 +1，无字母 → 01, 02, ...
    - {{STEP_GROUP}} 并行“二选一”组的首个选项：大号 +1，字母 A → 02-A
    - {{STEP_ALT}}   同组后续选项：大号不变，字母递增 → 02-B, 02-C
    序号统一 2 位补零。可选步骤（无占位符）不消耗序号，排在编号步骤之间但不带数字。
    因 zh/en 两版来自同一 src、同一 include 顺序，占位符出现顺序一致 → 两版序号相同。
    """
    major = 0
    sub = 0

    def repl(m):
        nonlocal major, sub
        kind = m.group(1)
        if kind is None:  # {{STEP}}
            major += 1
            sub = 0
            return f"{major:02d}"
        if kind == "_GROUP":  # {{STEP_GROUP}}
            major += 1
            sub = 1
            return f"{major:02d}-A"
        sub += 1  # {{STEP_ALT}}
        return f"{major:02d}-{chr(ord('A') + sub - 1)}"

    return STEP_RE.sub(repl, text)


def resolve(rel):
    return os.path.normpath(os.path.join(ROOT, rel))


def inline(text, visited):
    def sub(m):
        rel = m.group(1)
        path = resolve(rel)
        if path in visited:
            raise RuntimeError(f"循环 include: {rel}")
        visited.add(path)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        return inline(content, visited)

    return INCLUDE_RE.sub(sub, text)


def extract_vars_path(text):
    """从 frontmatter 中提取 vars: 的值（变量文件路径）。"""
    m = re.search(r"(?m)^vars:\s*(\S+)\s*$", text)
    return m.group(1) if m else None


def load_vars(path):
    """极简 key: value 解析：忽略 # 注释与空白行，按第一个冒号切分。"""
    d = {}
    if not path:
        return d
    p = resolve(path)
    if not os.path.exists(p):
        print(f"warning: vars 文件不存在: {path}")
        return d
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    return d


def fmt_date(dt, lang):
    """lang=ZH -> 2026.7.25（点号）；lang=EN -> 2026-7-25（短横线）。"""
    if lang == "ZH":
        return f"{dt.year}.{dt.month}.{dt.day}"
    return f"{dt.year}-{dt.month}-{dt.day}"


def builtin_vars(build_time):
    """内置自动变量：取「本次 build 的时间」（重新生成那一刻的日期）。

    改了部件重新 build，日期就是 build 当天——直观且符合
    「修改 → 重新生成 → 日期刷新」的预期。用户 yml 同名变量可覆盖。
    """
    return {
        "DATE_ZH": fmt_date(build_time, "ZH"),
        "DATE_EN": fmt_date(build_time, "EN"),
    }


def substitute_vars(text, vars_dict, build_time):
    # 1) 先处理带路径的日期变量 {{DATE_ZH:path}} / {{DATE_EN:path}}
    #    同样取 build 时间（path 仅作占位，保留语法兼容，不再按文件取时间）。
    def repl_date_path(m):
        lang = m.group(1)
        return fmt_date(build_time, lang)

    text = DATE_PATH_RE.sub(repl_date_path, text)

    # 2) 再处理普通变量（含 {{DATE_ZH}}/{{DATE_EN}} 等内置变量）
    def repl(m):
        key = m.group(1)
        return vars_dict.get(key, m.group(0))

    return VARS_RE.sub(repl, text)


def strip_vars_line(text):
    """从 frontmatter 中剔除 vars: 行（连同其换行），保持生成文件整洁。"""
    return re.sub(r"(?m)^vars:[^\n]*\n", "", text)


def self_check(out, rel_path):
    """拼接生成后的硬语法自检（门禁）。返回错误列表，空=通过。"""
    errors = []
    # 1) 代码围栏必须成对（拼接最常见的灾难：某 partial 漏写结束 ```）
    fences = len(re.findall(r"(?m)^```", out))
    if fences % 2 != 0:
        errors.append(
            f"代码围栏(```)未成对：共 {fences} 个，应为偶数（可能有 partial 漏写结束 ```）"
        )
    # 2) 不得残留未解析的 include 指令
    m = INCLUDE_RE.search(out)
    if m:
        errors.append(f"存在未解析的 include 指令：{m.group(1)}（路径错误或循环）")
    # 3) 不得残留未替换的变量
    leftover = set(VARS_RE.findall(out))
    if leftover:
        errors.append(
            f"存在未替换的变量：{', '.join(sorted(leftover))}（vars 文件路径或变量名错误）"
        )
    # 3.5) 不得残留带路径的日期变量（如 {{DATE_ZH:bad/path.md}}）
    leftover_path = set(
        f"DATE_{m.group(1)}:{m.group(2).strip()}" for m in DATE_PATH_RE.finditer(out)
    )
    if leftover_path:
        errors.append(
            f"存在未解析的带路径日期变量：{', '.join(sorted(leftover_path))}（路径错误）"
        )
    # 4) 标题层级不得跳级（拼接边界丢失父级标题会触发）
    #    注意：代码块内的 `# 注释` 不是标题，必须先跳过围栏内部再扫描。
    levels = []
    in_fence = False
    for line in out.split("\n"):
        if re.match(r"^```", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+\S", line)
        if m:
            levels.append(len(m.group(1)))
    for i in range(1, len(levels)):
        if levels[i] > levels[i - 1] + 1:
            errors.append(
                f"标题层级跳级：第 {i + 1} 个标题为 H{levels[i]}，但上一级是 H{levels[i - 1]}"
            )
    # 5) 代码块应有语言标注（等价 markdownlint MD040；拼接切到代码块边界会丢语言）
    in_fence = False
    for line in out.split("\n"):
        m = re.match(r"^```(.*)$", line)
        if m:
            if not in_fence and not m.group(1).strip():
                errors.append(
                    "存在未标注语言的代码块（应以 ```bash / ```powershell 等开头）"
                )
            in_fence = not in_fence
    return errors


def main():
    global ROOT
    ap = argparse.ArgumentParser(description="生成带 include + 变量的 markdown 文档")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    ROOT = os.path.abspath(args.root)
    # 本次 build 的统一时间：所有文档「最后更新」都取这一刻，
    # 符合「改了部件重新 build → 日期刷新为 build 当天」的预期。
    build_time = datetime.now()

    count = 0
    for dirpath, dirnames, files in os.walk(ROOT):
        # 跳过版本库与工具目录
        parts = set(dirpath.split(os.sep))
        if ".git" in parts or ".workbuddy" in parts:
            continue
        for fn in files:
            if not fn.endswith(".src.md"):
                continue
            src = os.path.join(dirpath, fn)
            with open(src, encoding="utf-8") as f:
                text = f.read()
            lang = src_lang(fn)

            # 1. 读取变量文件
            vars_path = extract_vars_path(text)
            vars_dict = load_vars(vars_path) if vars_path else {}

            # 1.5 注入内置自动变量（日期等）；用户 yml 同名变量可覆盖
            #     日期统一取「本次 build 时间」，即重新生成那一刻的日期。
            out_path = os.path.join(dirpath, fn[: -len(".src.md")] + ".md")
            vars_dict.update(builtin_vars(build_time))

            # 2. 递归内联 include
            out = inline(text, set())
            # 2.5 按目标语言过滤行（去掉另一语言的 <!-- zh -->/<!-- en --> 标记行，
            #     并把行内 {{OPTIONAL}} 按语言展开为【可选】/[Optional]）
            out = filter_lang(out, lang)
            # 2.6 步骤自动编号：按文档顺序为 {{STEP}}/{{STEP_GROUP}}/{{STEP_ALT}}
            #     分配 2 位补零序号（zh/en 两版序号一致）
            out = number_steps(out)

            # 3. 变量替换（内联之后，确保片段内的 {{VAR}} 也被替换）
            out = substitute_vars(out, vars_dict, build_time)

            # 4. 剔除 frontmatter 里的 vars: 行
            out = strip_vars_line(out)

            # 5. 归一化末尾：只保留单个换行，避免 include 指令后换行残留空行
            out = out.rstrip("\n") + "\n"

            # 5.5 拼接专属语法自检（门禁）
            rel = os.path.relpath(out_path, ROOT)
            errs = self_check(out, rel)
            if errs:
                print(f"::error:: 语法自检失败 {rel}")
                for e in errs:
                    print(f"  - {e}")
                sys.exit(1)

            if os.path.exists(out_path):
                with open(out_path, encoding="utf-8") as f:
                    old = f.read()
                if norm_ignore_date(out) == norm_ignore_date(old):
                    print(f"unchanged: {rel}")
                    continue
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(out)
            count += 1
            print(f"built: {rel}")
    print(f"done, {count} file(s) generated")


if __name__ == "__main__":
    main()
