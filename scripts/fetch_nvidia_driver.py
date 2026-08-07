#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_nvidia_driver.py — 一键查询并更新 NVIDIA 驱动版本号与下载链接。

为什么不用 processFind.aspx？
  旧版脚本调用 www.nvidia.com/Download/processFind.aspx，但该接口按具体显卡
  (psid/pfid) 返回分支专属版本，在我们的运行环境里还被反向代理钉死在 610.57，
  拿不到页面上“GeForce Game Ready 驱动”真正展示的最新版（如 610.88）。

正确数据源（与 nvidia.cn/drivers 页面完全一致）：
  nvidia.cn 的“最新驱动程序下载 / GeForce Game Ready 驱动”卡片，浏览器在选中
  GeForce 后由前端调用 GFE Web 服务：
      https://gfwsl.geforce.cn/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup
  我们用同样的参数（GeForce Game Ready Driver 的 psid/pfid/osID）去查。
  注意：国际站 gfwsl.geforce.com 与该端点结构【完全相同】，但本脚本刻意锁定
  .cn 端点 —— 因为中文文档与用户在 nvidia.cn 页面看到的最新版应保持一致，避免
  出现“脚本报 615.x 但页面仍是 610.88”的错位。

关于下载链接的 403 问题（重要）：
  NVIDIA 下载 CDN（Akamai）对裸 .exe 直链做了【Referer 热链保护】：
    - Referer 为 nvidia.com / nvidia.cn  -> 200，可下载。
    - Referer 为第三方域名或直接地址栏打开（无 Referer）-> 403 Forbidden。
  因此裸 exe 直链从文档里点出去几乎必 403（不是链接拼错）。
  解法：主下载链接改用官方【下载页 DetailsURL】（实测 200 正常打开，无 403），
  用户在页面上点它自带的 Download 按钮即可（此时 Referer 合法）。裸 exe 直链
  仅作为“备用”保留，并在文档中标注可能 403 的提示。

工作机制：
  1. 调用 GFE DriverManualLookup，过滤出 GeForce Game Ready 驱动（WHQL=1），
     按发布时间取最新一条，得到 version / 官方 DownloadURL / 官方 DetailsURL。
  2. 由 DetailsURL 派生「中国页(cn)」与「全球页(us)」两个官方下载页链接。
  3. 由官方 DownloadURL 派生桌面版 cn / us 两个裸 exe 直链（备用）。
  4. 与 _partials/vars/shared.yml 中现有版本比较：
       - 抓到更新版本 -> 写回 shared.yml，并打印更新摘要。
       - 抓到版本不更新 -> 保留原值并警告，绝不静默降级。
       - 网络失败     -> 报错退出，不动文件。

用法：
    python scripts/fetch_nvidia_driver.py

依赖：仅标准库（urllib / json / re），无需 pip 安装。
注意：本脚本只“查询并写变量文件”，更新后请运行 `python build.py` 重新生成
      文档、审阅 git diff 再提交 —— 这是 doc-as-code 的标准流程。
"""
import os
import re
import sys
import json
import urllib.request
import urllib.parse
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED = os.path.join(ROOT, "_partials", "vars", "shared.yml")

# GFE Web 服务（与 nvidia.cn/drivers 页面“GeForce Game Ready 驱动”卡片同源）。
# 参数来自前端 clientlib-driverflownvlookup 中 popularDownloadsDriverSettingsGrd：
#   psid=123 (GeForce)  pfid=976 (GeForce Game Ready Driver 系列)
#   osID=57  (Windows 11 64-bit)  languageCode=1033 (en-US)
#   dch=1 (DCH 驱动)  isWHQL=0 / dltype=-1 (取全部，再按版本号取最新 GRD)
# 锁定 .cn 端点，与中文文档页面保持一致（见文件头说明）。
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
    "sort1": "1",            # 按发布时间降序：最新在前
    "numberOfResults": "20",
}

# 桌面版直链文件名特征（区别于 notebook 笔记本版）。
DESKTOP_TOKEN = "desktop"


def fetch_latest():
    """查询 GFE 接口，返回 (version_str, download_url, details_url)。

    version_str  如 '610.88'；
    download_url 为官方返回的裸直链（notebook 形态，调用方再派生桌面版）；
    details_url  为官方下载【页】地址（如 .../drivers/details/274384/），
                 可安全作为主下载链接，规避裸 exe 的 Referer 403。
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

    # 过滤出 GeForce Game Ready 驱动（WHQL=1），再按发布时间取最新一条
    # （sort1=1 已让最新的排在最前）。避免误抓其它分支或更高但非 GRD 的版本。
    grd = []
    for it in ids:
        d = it.get("downloadInfo", {})
        # API 的 Name 是 URL 编码的（如 GeForce%20Game%20Ready%20Driver），
        # 先做 unquote 再匹配。
        name = unquote(d.get("Name", "") or "")
        if "Game Ready" in name and str(d.get("IsWHQL")) == "1":
            grd.append(d)
    if not grd:
        raise RuntimeError("未能从 GFE 接口解析出任何 GeForce Game Ready 驱动")

    best = grd[0]  # 最新（发布时间降序）
    ver = best.get("Version", "")
    if not re.match(r"^\d{3}\.\d{2,3}$", ver or ""):
        raise RuntimeError(f"解析到的版本号格式异常：{ver!r}")
    return ver, best.get("DownloadURL", ""), best.get("DetailsURL", "")


def derive_links(version, download_url, details_url):
    """由官方返回派生：下载页(cn/us) + 裸 exe 直链(cn/us)。

    下载页：官方 DetailsURL 形如
        https://www.nvidia.com/en-us/drivers/details/274384/
      全球页直接用它；中国页把 'www.nvidia.com/en-us/' 换成 'www.nvidia.cn/zh-cn/'。
    裸 exe：官方 DownloadURL 形如
        https://us.download.nvidia.com/Windows/610.88/610.88-notebook-...exe
      桌面版只是把 notebook 换成 desktop；cn 镜像则把主机名 us 换成 cn。
    """
    # —— 下载页（主链接，无 403）——
    us_page = details_url
    if not us_page:
        us_page = f"https://www.nvidia.com/en-us/drivers/details/"
    cn_page = us_page.replace("www.nvidia.com/en-us/", "www.nvidia.cn/zh-cn/")
    if cn_page == us_page and "nvidia.cn" not in cn_page:
        # DetailsURL 不是预期的 nvidia.com/en-us 形态，则中美页都用原值兜底。
        cn_page = us_page

    # —— 裸 exe 直链（备用，可能 403）——
    if download_url:
        desktop = download_url.replace("notebook", DESKTOP_TOKEN)
    else:
        desktop = (
            f"https://us.download.nvidia.com/Windows/{version}/"
            f"{version}-desktop-win10-win11-64bit-international-dch-whql.exe"
        )
    cn_exe = desktop.replace("us.download.nvidia.com", "cn.download.nvidia.com")
    us_exe = desktop
    return cn_page, us_page, cn_exe, us_exe


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


def write_shared(values):
    """把若干 key=value 写回 shared.yml：已有的行就地替换，缺失的行追加在末尾。

    values: dict，如
      {'NVIDIA_DRIVER_VERSION': '610.88',
       'NVIDIA_DRIVER_PAGE_CN': '...', 'NVIDIA_DRIVER_PAGE_US': '...',
       'NVIDIA_DRIVER_URL_CN': '...', 'NVIDIA_DRIVER_URL_US': '...'}
    """
    with open(SHARED, encoding="utf-8") as f:
        lines = f.readlines()

    pending = dict(values)
    out = []
    for ln in lines:
        m = re.match(r"^(\s*[A-Z_][A-Z0-9_]*)(:)(.*)$", ln)
        if m and m.group(1).strip() in pending:
            key = m.group(1).strip()
            out.append(f"{key}: {pending.pop(key)}\n")
        else:
            out.append(ln)

    if pending:
        if out and not out[-1].endswith("\n"):
            out[-1] += "\n"
        for k, v in pending.items():
            out.append(f"{k}: {v}\n")

    with open(SHARED, "w", encoding="utf-8") as f:
        f.writelines(out)


def main():
    cur = read_shared().get("NVIDIA_DRIVER_VERSION")
    try:
        ver, dl, details = fetch_latest()
    except Exception as e:
        print(f"[错误] 查询 NVIDIA GFE 接口失败：{e}")
        sys.exit(1)

    cn_page, us_page, cn_exe, us_exe = derive_links(ver, dl, details)

    if cur is None:
        write_shared({
            "NVIDIA_DRIVER_VERSION": ver,
            "NVIDIA_DRIVER_PAGE_CN": cn_page,
            "NVIDIA_DRIVER_PAGE_US": us_page,
            "NVIDIA_DRIVER_URL_CN": cn_exe,
            "NVIDIA_DRIVER_URL_US": us_exe,
        })
        print(f"[写入] 首次设置 NVIDIA 驱动版本为 {ver}")
        _print_links(cn_page, us_page, cn_exe, us_exe)
        print("已写入 _partials/vars/shared.yml，运行 python build.py 重新生成文档后提交。")
        return

    if float(ver) <= float(cur):
        print(f"[跳过] 接口返回 {ver}，不比现有 {cur} 更新。")
        print("       可能为镜像陈旧或分支特定版本，已保留现有值（未静默降级）。")
        print("       若确认需强制更新，请手动编辑 _partials/vars/shared.yml。")
        sys.exit(0)

    write_shared({
        "NVIDIA_DRIVER_VERSION": ver,
        "NVIDIA_DRIVER_PAGE_CN": cn_page,
        "NVIDIA_DRIVER_PAGE_US": us_page,
        "NVIDIA_DRIVER_URL_CN": cn_exe,
        "NVIDIA_DRIVER_URL_US": us_exe,
    })
    print(f"[更新] NVIDIA 驱动 {cur} -> {ver}")
    _print_links(cn_page, us_page, cn_exe, us_exe)
    print("已写入 _partials/vars/shared.yml，运行 python build.py 重新生成文档后提交。")


def _print_links(cn_page, us_page, cn_exe, us_exe):
    print(f"  官方下载页(中国): {cn_page}")
    print(f"  官方下载页(全球): {us_page}")
    print(f"  裸直链(中国/备用): {cn_exe}")
    print(f"  裸直链(全球/备用): {us_exe}")


if __name__ == "__main__":
    main()
