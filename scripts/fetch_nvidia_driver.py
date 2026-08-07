#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_nvidia_driver.py — 一键查询并更新 NVIDIA 驱动版本号与下载直链。

工作机制：
  1. 查询 NVIDIA 官方 processFind 接口，取最新 GeForce Game Ready 驱动版本号。
  2. 按固定模板拼出「中国(cn)」与「全球(us)」两个镜像的 .exe 直链。
  3. 与 _partials/vars/shared.yml 中现有版本比较：
       - 抓到更新版本  -> 写回 shared.yml，并打印更新摘要。
       - 抓到版本不更新（接口返回陈旧 / 分支特定）-> 保留原值并警告，绝不静默降级。
       - 网络失败      -> 报错退出，不动文件。

用法：
    python scripts/fetch_nvidia_driver.py

依赖：仅标准库（urllib），无需 pip 安装。
注意：本脚本只“查询并写变量文件”，更新后请运行 `python build.py` 重新生成
      文档、审阅 git diff 再提交 —— 这是 doc-as-code 的标准流程。
"""
import os
import re
import sys
import urllib.request
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED = os.path.join(ROOT, "_partials", "vars", "shared.yml")

# 查询参数：GeForce(psid=95) + 代表卡(RTX 4090, pfid=949) + Win11 64-bit(osid=57) + WHQL
# 若你发现返回的不是最新（比如命中了某卡/分支的特定版本），可调这里的 pfid/osid。
QUERY = {"psid": "95", "pfid": "949", "osid": "57", "lid": "2", "whql": "1", "lang": "en-us", "ctk": "0"}


def fetch_latest_version():
    """查询 NVIDIA 接口，返回最新 GeForce 版本号的原始字符串（如 '610.88'）。"""
    url = "https://www.nvidia.com/Download/processFind.aspx"
    data = urllib.parse.urlencode(QUERY).encode()
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode("utf-8", "ignore")
    # 抓所有 6xx.xx 版本（数据中心驱动是 x.y 形式，如 13.3，会被本正则排除），取数值最大者
    toks = re.findall(r"6\d{2}\.\d{2,3}", html)
    if not toks:
        raise RuntimeError("未能从 NVIDIA 接口解析出任何 6xx 版本号（接口结构可能变化）")
    return max(toks, key=lambda t: float(t))


def build_urls(ver):
    cn = f"https://cn.download.nvidia.com/Windows/{ver}/{ver}-desktop-win10-win11-64bit-international-dch-whql.exe"
    us = f"https://us.download.nvidia.com/Windows/{ver}/{ver}-desktop-win10-win11-64bit-international-dch-whql.exe"
    return cn, us


def read_shared():
    d = {}
    if os.path.exists(SHARED):
        with open(SHARED, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or ":" not in line:
                    continue
                k, v = line.split(":", 1)
                d[k.strip()] = v.strip()
    return d


def write_shared(ver, cn, us):
    with open(SHARED, encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r"(?m)^NVIDIA_DRIVER_VERSION:.*$", f"NVIDIA_DRIVER_VERSION: {ver}", text)
    text = re.sub(r"(?m)^NVIDIA_DRIVER_URL_CN:.*$", f"NVIDIA_DRIVER_URL_CN: {cn}", text)
    text = re.sub(r"(?m)^NVIDIA_DRIVER_URL_US:.*$", f"NVIDIA_DRIVER_URL_US: {us}", text)
    with open(SHARED, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    cur = read_shared().get("NVIDIA_DRIVER_VERSION")
    try:
        ver = fetch_latest_version()
    except Exception as e:
        print(f"[错误] 查询 NVIDIA 接口失败：{e}")
        sys.exit(1)

    if cur is None:
        cn, us = build_urls(ver)
        write_shared(ver, cn, us)
        print(f"[写入] 首次设置 NVIDIA 驱动版本为 {ver}")
        print(f"  CN: {cn}")
        print(f"  US: {us}")
        print("已写入 _partials/vars/shared.yml，运行 python build.py 重新生成文档后提交。")
        return

    if float(ver) <= float(cur):
        print(f"[跳过] 接口返回 {ver}，不比现有 {cur} 更新。")
        print("       可能为镜像陈旧或分支特定版本，已保留现有值（未静默降级）。")
        print("       若确认需强制更新，请手动编辑 _partials/vars/shared.yml。")
        sys.exit(0)

    cn, us = build_urls(ver)
    write_shared(ver, cn, us)
    print(f"[更新] NVIDIA 驱动 {cur} -> {ver}")
    print(f"  CN: {cn}")
    print(f"  US: {us}")
    print("已写入 _partials/vars/shared.yml，运行 python build.py 重新生成文档后提交。")


if __name__ == "__main__":
    main()
