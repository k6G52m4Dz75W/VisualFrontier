#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_nvidia_driver.py — 一键查询并更新 NVIDIA 驱动版本号与下载直链。

为什么不用 processFind.aspx？
  旧版脚本调用 www.nvidia.com/Download/processFind.aspx，但该接口按具体显卡
  (psid/pfid) 返回分支专属版本，在我们的运行环境里还被反向代理钉死在 610.57，
  拿不到页面上“GeForce Game Ready 驱动”真正展示的最新版（如 610.88）。

正确数据源（与 nvidia.cn/drivers 页面完全一致）：
  nvidia.cn 的“最新驱动程序下载 / GeForce Game Ready 驱动”卡片，浏览器在选中
  GeForce 后由前端调用 GFE Web 服务：
      https://gfwsl.geforce.cn/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup
  我们用同样的参数（GeForce Game Ready Driver 的 psid/pfid/osID）去查，取回的
  downloadInfo.Version 就是页面上显示的那个最新版（610.88）。

工作机制：
  1. 调用 GFE DriverManualLookup，取最新 GeForce Game Ready 驱动版本号与直链。
  2. 由官方返回的 DownloadURL 派生出「中国(cn)」与「全球(us)」两个 desktop 镜像直链。
  3. 与 _partials/vars/shared.yml 中现有版本比较：
       - 抓到更新版本  -> 写回 shared.yml，并打印更新摘要。
       - 抓到版本不更新（接口返回陈旧 / 分支特定）-> 保留原值并警告，绝不静默降级。
       - 网络失败      -> 报错退出，不动文件。

用法：
    python scripts/fetch_nvidia_driver.py

依赖：仅标准库（urllib / json），无需 pip 安装。
注意：本脚本只“查询并写变量文件”，更新后请运行 `python build.py` 重新生成
      文档、审阅 git diff 再提交 —— 这是 doc-as-code 的标准流程。
"""
import os
import re
import sys
import json
import urllib.request
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED = os.path.join(ROOT, "_partials", "vars", "shared.yml")

# GFE Web 服务（与 nvidia.cn/drivers 页面“GeForce Game Ready 驱动”卡片同源）。
# 参数来自前端 clientlib-driverflownvlookup 中 popularDownloadsDriverSettingsGrd：
#   psid=123 (GeForce)  pfid=976 (GeForce Game Ready Driver 系列)
#   osID=57  (Windows 11 64-bit)  languageCode=1033 (en-US)
#   dch=1 (DCH 驱动)  isWHQL=0 / dltype=-1 (取全部，再按版本号取最新)
GFE_BASE = "https://gfwsl.geforce.cn/services_toolkit/services/com/nvidia/services/AjaxDriverService.php"
QUERY = {
    "func": "DriverManualLookup",
    "psid": "123",
    "pfid": "976",
    "osID": "57",
    "languageCode": "1033",
    "beta": "0",
    "isWHQL": "0",
    "dltype": "-1",
    "dch": "1",
    "upCRD": "0",
    "qnf": "0",
    "ctk": "null",
    "sort1": "1",
    "numberOfResults": "20",
}

# 桌面版直链文件名特征（区别于 notebook 笔记本版）。
DESKTOP_TOKEN = "desktop"


def fetch_latest():
    """查询 GFE 接口，返回 (version_str, download_url) 。

    version_str 如 '610.88'；download_url 为官方返回的直链（notebook 形态，
    调用方会再派生桌面版 cn/us 直链）。
    """
    url = GFE_BASE + "?" + urllib.parse.urlencode(QUERY)
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://www.nvidia.cn/drivers/",
            "Accept": "*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode("utf-8", "ignore")

    # 接口通常返回 JSON；个别情况下是 JS 对象字面量，做双重兜底。
    try:
        obj = json.loads(raw)
    except Exception:
        obj = eval(raw, {"__builtins__": {}}, {})

    ids = (obj or {}).get("IDS") or []
    if not ids:
        raise RuntimeError("GFE 接口未返回任何驱动数据（接口结构可能变化或网络异常）")

    # 在所有返回的 GRD 里挑版本号最大者（DRIVER 版本形如 610.88）。
    best = None
    best_v = -1.0
    for it in ids:
        d = it.get("downloadInfo", {})
        ver = d.get("Version", "")
        m = re.match(r"^(\d{3}\.\d{2,3})$", ver or "")
        if not m:
            continue
        try:
            fv = float(ver)
        except ValueError:
            continue
        if fv > best_v:
            best_v = fv
            best = d
    if best is None:
        raise RuntimeError("未能从 GFE 接口解析出任何 6xx 版本号")

    return best["Version"], best.get("DownloadURL", "")


def derive_links(version, download_url):
    """由官方直链派生桌面版 cn / us 两个镜像直链。

    官方 DownloadURL 形如：
      https://us.download.nvidia.com/Windows/610.88/610.88-notebook-win10-win11-64bit-international-dch-whql.exe
    桌面版只是把 notebook 换成 desktop；cn 镜像则把主机名 us 换成 cn。
    若官方未返回 DownloadURL（极少），退回到固定模板（已验证对 610.88 可解析）。
    """
    if download_url:
        desktop = download_url.replace("notebook", DESKTOP_TOKEN)
    else:
        desktop = (
            f"https://us.download.nvidia.com/Windows/{version}/"
            f"{version}-desktop-win10-win11-64bit-international-dch-whql.exe"
        )
    cn = desktop.replace("us.download.nvidia.com", "cn.download.nvidia.com")
    us = desktop
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
        ver, dl = fetch_latest()
    except Exception as e:
        print(f"[错误] 查询 NVIDIA GFE 接口失败：{e}")
        sys.exit(1)

    cn, us = derive_links(ver, dl)

    if cur is None:
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

    write_shared(ver, cn, us)
    print(f"[更新] NVIDIA 驱动 {cur} -> {ver}")
    print(f"  CN: {cn}")
    print(f"  US: {us}")
    print("已写入 _partials/vars/shared.yml，运行 python build.py 重新生成文档后提交。")


if __name__ == "__main__":
    main()
