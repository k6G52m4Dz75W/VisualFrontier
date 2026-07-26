#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — 把带 include 指令的源模板 (*.src.md) 生成最终 .md

用法:
    python build.py [--root .]

源模板里用 HTML 注释指令引用共享片段(partial):
    <!-- include: _partials/zh/vibeocr.md -->

规则:
- 递归内联: 片段里还能再 include 其它片段，带循环保护。
- 输出文件 = 同目录、同名但去掉 .src（README.src.md -> README.md）。
- 片段路径相对于仓库根目录。
- 只处理 `*.src.md`；普通 `.md`（含 _partials 里的片段）不会被当作模板。

建议: 把本脚本接进 pre-commit 或 GitHub Action。
若生成结果与已提交的 .md 不一致则失败，防止「片段」与「生成文件」漂移。
"""
import argparse
import os
import re

INCLUDE_RE = re.compile(r"<!--\s*include:\s*([^\s]+)\s*-->")
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


def main():
    global ROOT
    ap = argparse.ArgumentParser(description="生成带 include 的 markdown 文档")
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
            out = inline(text, set())
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
