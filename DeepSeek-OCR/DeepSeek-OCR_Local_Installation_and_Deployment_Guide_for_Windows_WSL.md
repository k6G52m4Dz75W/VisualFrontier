---
title: DeepSeek-OCR Windows WSL本地安装部署指南
source: "https://github.com/k6G52m4Dz75W/VisualFrontier/blob/main/DeepSeek-OCR/DeepSeek-OCR_Local_Installation_and_Deployment_Guide_for_Windows_WSL.md"
author: Visual Frontier (https://github.com/k6G52m4Dz75W/VisualFrontier), DeepSeek, Hy3@WorkBuddy
created: 2026-07-24
description: 本文提供了在Windows WSL中通过Miniconda、vLLM和国内镜像加速，完整安装部署DeepSeek-OCR模型并启动OpenAI兼容服务的实操指南。
tags:
  - DeepSeek-OCR
  - WSL
  - Windows Subsystem for Linux
  - vLLM
---

# 🛠️ DeepSeek-OCR Windows WSL本地安装部署指南

🕒 最后更新：`2026.8.8`

## 01. 💻 安装/更新nvidia驱动程序

访问官方驱动下载入口，选择GeForce，下载最新驱动程序

- 官方驱动下载入口（中国站）：<https://www.nvidia.cn/drivers/>

> 当前最新版本：`610.88`
> 最新版本下载页面：<https://www.nvidia.cn/zh-cn/drivers/details/274384/>

> 💡 在最新版本下载页面中点击 **下载** 按钮即可下载（页面自带合法 Referer，不会报 403）。

**进阶用法：命令行直接下载**

如果你熟悉命令行（无图形界面、远程服务器或想写进自动化脚本），可复制下方命令直接拉取安装包。命令已内置 `Referer` 请求头，可绕过 NVIDIA CDN 的 403 热链限制，在终端粘贴执行即可：

```bash
curl -L --referer "https://www.nvidia.cn/" -O "https://cn.download.nvidia.com/Windows/610.88/610.88-desktop-win10-win11-64bit-international-dch-whql.exe"
```

## 02. 🪟 安装WSL

以管理员权限启动Powershell，安装WSL

```Powershell
wsl --install
```

等待自动安装完成

## 03. 🐧 启动Ubuntu

点击开始菜单中的Ubuntu图标启动它

![Ubuntu图标](Ubuntu.png)

## 04. 🐍 安装miniconda并配置conda和pip国内镜像

在Ubuntu的命令行界面中输入或复制粘贴以下整段代码回车即可直接运行，无需逐行复制粘贴，下同

```bash
# 安装miniconda
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# 配置conda国内镜像
# 添加清华 conda-forge 镜像
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
# 配置为显示channel地址，方便确认是否生效
conda config --set show_channel_urls yes
# 清除缓存使配置生效
conda clean -i

# 配置pip国内镜像
# 配置清华源为默认下载源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# 将该源添加为受信任主机，避免SSL或其他网络问题
pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn
```

## 05. ⚡ 安装uv并配置uv国内镜像

uv速度飞快，且节省缓存空间，强烈推荐替代pip

```bash
# 安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 配置uv国内镜像
echo 'export UV_DEFAULT_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"' >> ~/.bashrc
# 使当前终端立即生效
source ~/.bashrc
```

## 06. ☁️ 安装modelscope

国内首选使用modelscope，简单直接，不用考虑hf下载速度慢和受限制问题

```bash
pip install modelscope
```

### 🤗 【可选】安装huggingface并配置国内huggingface国内镜像

```bash
# 安装huggingface
pip install huggingface_hub

# 配置huggingface国内镜像
echo 'export HF_ENDPOINT=https://hf-mirror.com' >> ~/.bashrc
# 使当前终端立即生效
source ~/.bashrc
```

## 07. 📥 下载模型权重

```bash
modelscope download --model deepseek-ai/DeepSeek-OCR
# 默认下载目录：~/.cache/modelscope/models/deepseek-ai--DeepSeek-OCR
```

### 🤗 【可选】使用huggingface下载

```bash
hf download deepseek-ai/DeepSeek-OCR
```

## 08. 🌱 安装并激活环境

使用官方推荐python版本创建环境

```bash
conda create -n deepseek-ocr python=3.12.9 -y
conda activate deepseek-ocr
```

## 09. ⚙️ 安装cuda-toolkit并设置环境变量

```bash
# 安装最新版本的cuda-toolkit
conda install nvidia::cuda-toolkit -y
# 创建环境变量配置文件
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
# 写入设置命令（每次激活环境时自动执行）
echo 'export LIBRARY_PATH=/usr/lib/wsl/lib:$LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo 'export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
#（可选）添加对应的卸载命令（退出环境时恢复）
echo 'unset LD_LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
# 设置完成后，重新激活环境即可生效
conda deactivate
conda activate deepseek-ocr
```

## 10. 🚀 安装vLLM及后端

注意：**不要**遵照官方的安装流程执行安装，那仅适用于当时的版本状况，尤其

- **不要**以指定版本方式安装torch
- **不要**以指定版本方式安装vllm
- **不要**安装**任何版本**flash-attn
- **不要**安装requiements.txt依赖包

当前使用以下方法安装才是最佳实践

```bash
# 官方秘诀出处：https://docs.vllm.ai/projects/recipes/en/latest/DeepSeek/DeepSeek-OCR.html
uv pip install -U vllm --torch-backend auto
```

## 11. 🌐 启动vLLM服务

启动vLLM服务后，可以通过OpenAI兼容接口直接访问：<http://127.0.0.1:8000/>

```bash
vllm serve ~/.cache/modelscope/models/deepseek-ai--DeepSeek-OCR/snapshots/master/ --served-model-name DeepSeek-OCR --logits_processors vllm.model_executor.models.deepseek_ocr:NGramPerReqLogitsProcessor --no-enable-prefix-caching --mm-processor-cache-gb 0
```

🔍 推荐使用VibeOCR来进行OCR扫描任务：

> - **[VibeOCR](https://github.com/k6G52m4Dz75W/VibeOCR)** - 智能端到端书籍OCR解决方案 — 多模型AI驱动，PDF到纯文本一键提取

## 📂 【可选】克隆仓库

仓库仅供开发参考，不是启用模型的必要条件

```bash
mkdir -p ~/workspace
cd ~/workspace
git clone https://github.com/deepseek-ai/DeepSeek-OCR.git
```

# ⚠️ 注意事项

本模型无论是按照官方安装指引还是按照以上vLLM智能安装得到的结果，抑或是硅基流动平台服务部署的结果都极大概率会随机性出现文本乱码或缺失、重复大段文本的问题，强烈建议使用升级后的[DeepSeek-OCR-2](https://github.com/deepseek-ai/DeepSeek-OCR-2)模型替代。
