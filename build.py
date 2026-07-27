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

INCLUDE_RE = re.compile(r"<!--\s*include:\s*([^\s]+)\s*-->")
VARS_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")
ROOT = "."


def norm(t):
    """忽略尾部空行差异，用于判断生成内容是否与已提交 .md 实质一致。"""
    t = t.replace("\r\n", "\n")
    lines = t.split("\n")
    while lines and lines[-1].strip() == "":
        lines.pop()
    return "\n".join(lines)


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


def substitute_vars(text, vars_dict):
    if not vars_dict:
        return text

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

            # 1. 读取变量文件
            vars_path = extract_vars_path(text)
            vars_dict = load_vars(vars_path) if vars_path else {}

            # 2. 递归内联 include
            out = inline(text, set())

            # 3. 变量替换（内联之后，确保片段内的 {{VAR}} 也被替换）
            out = substitute_vars(out, vars_dict)

            # 4. 剔除 frontmatter 里的 vars: 行
            out = strip_vars_line(out)

            # 5. 归一化末尾：只保留单个换行，避免 include 指令后换行残留空行
            out = out.rstrip("\n") + "\n"

            out_path = os.path.join(dirpath, fn[: -len(".src.md")] + ".md")

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
                if norm(out) == norm(old):
                    print(f"unchanged: {rel}")
                    continue
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(out)
            count += 1
            print(f"built: {rel}")
    print(f"done, {count} file(s) generated")


if __name__ == "__main__":
    main()
