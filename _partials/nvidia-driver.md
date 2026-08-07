<!-- zh --> ## {{STEP}}. 💻 安装/更新nvidia驱动程序
<!-- en --> ## {{STEP}}. 💻 Install/Update NVIDIA Drivers

<!-- zh --> 访问官方网站入口，选择GeForce，下载最新驱动程序
<!-- en --> Visit the official website entry, select GeForce, and download the latest driver.

<!-- zh --> - 中文官网：<https://www.nvidia.cn/drivers/>
<!-- en --> - Chinese official site: <https://www.nvidia.cn/drivers/>
<!-- zh --> - 全球官网：<https://www.nvidia.com/en-us/drivers/>
<!-- en --> - Global official site: <https://www.nvidia.com/en-us/drivers/>

<!-- zh --> > 当前最新版本：`{{NVIDIA_DRIVER_VERSION}}`
<!-- en --> > Current latest version: `{{NVIDIA_DRIVER_VERSION}}`
<!-- zh --> > 官方下载页（中国，推荐）：<{{NVIDIA_DRIVER_PAGE_CN}}>
<!-- en --> > Official download page (China, recommended): <{{NVIDIA_DRIVER_PAGE_CN}}>
<!-- zh --> > 官方下载页（全球，推荐）：<{{NVIDIA_DRIVER_PAGE_US}}>
<!-- en --> > Official download page (Global, recommended): <{{NVIDIA_DRIVER_PAGE_US}}>

<!-- zh --> > 💡 在下载页中点击 **Download** 按钮即可下载（页面自带合法 Referer，不会报 403）。
<!-- en --> > 💡 Click the **Download** button on the page to download (the page provides a valid Referer, so no 403).

<!-- zh --> **进阶用法：命令行直接下载**
<!-- en --> **Advanced: download directly from the command line**

<!-- zh --> 如果你熟悉命令行（无图形界面、远程服务器或想写进自动化脚本），可复制下方命令直接拉取安装包。命令已内置 `Referer` 请求头，可绕过 NVIDIA CDN 的 403 热链限制，在终端粘贴执行即可：
<!-- en --> If you are comfortable with the command line (headless, remote server, or automation), copy the command below to fetch the installer directly. The `Referer` header is built in to bypass NVIDIA CDN's 403 hotlink restriction — just paste and run it in a terminal:

```bash
curl -L --referer "https://www.nvidia.cn/" -O "{{NVIDIA_DRIVER_URL_CN}}"
```
