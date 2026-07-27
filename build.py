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

建议接进 pre-commit 或 GitHub Action：
若生成结果与已提交的 .md 不一致则失败，防止「片段」与「生成文件」漂移。
"""
import argparse
import os
import re

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
            if os.path.exists(out_path):
                with open(out_path, encoding="utf-8") as f:
                    old = f.read()
                if norm(out) == norm(old):
                    print(f"unchanged: {os.path.relpath(out_path, ROOT)}")
                    continue
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(out)
            count += 1
            print(f"built: {os.path.relpath(out_path, ROOT)}")
    print(f"done, {count} file(s) generated")


if __name__ == "__main__":
    main()
