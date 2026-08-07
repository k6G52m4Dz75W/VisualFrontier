---
title: DeepSeek-OCR-2 Local Installation and Deployment Guide for Windows WSL
source: "https://github.com/k6G52m4Dz75W/VisualFrontier/blob/main/DeepSeek-OCR-2/DeepSeek-OCR-2_Local_Installation_and_Deployment_Guide_for_Windows_WSL.en.md"
author: Visual Frontier (https://github.com/k6G52m4Dz75W/VisualFrontier), DeepSeek, Hy3@WorkBuddy
created: 2026-07-24
description: This article provides a practical guide for fully installing and deploying the DeepSeek-OCR-2 model on Windows WSL using Miniconda, vLLM, and domestic mirror acceleration, and starting the OpenAI-compatible service.
tags:
  - DeepSeek-OCR-2
  - WSL
  - Windows Subsystem for Linux
  - vLLM
---

# 🛠️ DeepSeek-OCR-2 Local Installation and Deployment Guide for Windows WSL

🕒 Last updated: `2026-8-8`

## 01. 💻 Install/Update NVIDIA Drivers

Visit the official website entry, select GeForce, and download the latest driver.

- Global official site: <https://www.nvidia.com/en-us/drivers/>

> Current latest version: `610.88`
> Official download page: <https://www.nvidia.com/en-us/drivers/details/274384/>

> 💡 Click the **Download** button on the page to download (the page provides a valid Referer, so no 403).

**Advanced: download directly from the command line**

If you are comfortable with the command line (headless, remote server, or automation), copy the command below to fetch the installer directly. The `Referer` header is built in to bypass NVIDIA CDN's 403 hotlink restriction — just paste and run it in a terminal:

```bash
curl -L --referer "https://www.nvidia.com/" -O "https://us.download.nvidia.com/Windows/610.88/610.88-desktop-win10-win11-64bit-international-dch-whql.exe"
```

## 02. 🪟 Install WSL

Launch PowerShell as administrator and install WSL:

```Powershell
wsl --install
```

Wait for the automatic installation to complete.

## 03. 🐧 Start Ubuntu

Click the Ubuntu icon in the Start menu to launch it.

![Ubuntu icon](Ubuntu.png)

## 04. 🐍 Install Miniconda and Configure Conda and Pip Mirrors (China)

In the Ubuntu command line, enter or copy-paste the entire block below and press Enter to run it directly. No need to copy line by line; same applies below.

```bash
# Install Miniconda
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# Configure conda domestic mirrors (Tsinghua)
# Add Tsinghua conda-forge mirror
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
# Show channel URLs to verify configuration
conda config --set show_channel_urls yes
# Clear cache to apply changes
conda clean -i

# Configure pip domestic mirror
# Set Tsinghua as default index
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# Add as trusted host to avoid SSL/network issues
pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn
```

## 05. ⚡ Install uv and Configure uv Mirror (China)

uv is extremely fast and saves cache space; highly recommended as a pip replacement.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Configure uv domestic mirror
echo 'export UV_DEFAULT_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"' >> ~/.bashrc
# Apply immediately in current terminal
source ~/.bashrc
```

## 06. ☁️ Install modelscope

For users in China, modelscope is the preferred choice – straightforward, no worries about slow Hugging Face downloads or restrictions.

```bash
pip install modelscope
```

### 🤗 [Optional] Install Hugging Face Hub and Configure Mirror (China)

```bash
# Install huggingface_hub
pip install huggingface_hub

# Configure Hugging Face domestic mirror
echo 'export HF_ENDPOINT=https://hf-mirror.com' >> ~/.bashrc
# Apply immediately
source ~/.bashrc
```

## 07. 📥 Download Model Weights

```bash
modelscope download --model deepseek-ai/DeepSeek-OCR-2
# Default download directory: ~/.cache/modelscope/models/deepseek-ai--DeepSeek-OCR-2
```

### 🤗 [Optional] Download via Hugging Face

```bash
hf download deepseek-ai/DeepSeek-OCR-2
```

## 08. 🌱 Create and Activate Conda Environment

Create a conda environment using the recommended Python version.

```bash
conda create -n deepseek-ocr-2 python=3.12.9 -y
conda activate deepseek-ocr-2
```

## 09. ⚙️ Install CUDA Toolkit and Set Environment Variables

```bash
# Install the latest CUDA toolkit
conda install nvidia::cuda-toolkit -y
# Create environment variable config directory
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
# Write setting commands (automatically executed when environment is activated)
echo 'export LIBRARY_PATH=/usr/lib/wsl/lib:$LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo 'export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
# (Optional) Add corresponding unset commands when deactivating
echo 'unset LD_LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
# After setting, reactivate the environment for changes to take effect
conda deactivate
conda activate deepseek-ocr-2
```

## 10. 🚀 Install vLLM and Backend

**Important:** Do **not** follow the official installation instructions – they are only valid for older versions. In particular:

- **Do not** install torch with a pinned version
- **Do not** install vLLM with a pinned version
- **Do not** install **any version** of flash-attn
- **Do not** install the `requirements.txt` dependencies

The following approach is the current best practice:

```bash
# Official tip source: https://docs.vllm.ai/projects/recipes/en/latest/DeepSeek/DeepSeek-OCR-2.html
uv pip install -U vllm --torch-backend auto
```

## 11. 🌐 Start the vLLM Server

Once the vLLM server is running, you can access it via the OpenAI-compatible endpoint: <http://127.0.0.1:8000/>

```bash
vllm serve ~/.cache/modelscope/models/deepseek-ai--DeepSeek-OCR-2/snapshots/master/ --served-model-name DeepSeek-OCR-2 --logits_processors vllm.model_executor.models.deepseek_ocr:NGramPerReqLogitsProcessor --no-enable-prefix-caching --mm-processor-cache-gb 0
```

🔍 VibeOCR is recommended for OCR scanning tasks:

> - **[VibeOCR](https://github.com/k6G52m4Dz75W/VibeOCR)** - Intelligent End‑to‑End Book OCR Solution — Multi‑model AI powered, PDF to plain text in one click

## 📂 [Optional] Clone the Repository

The repository is for development reference only and is not required to run the model.

```bash
mkdir -p ~/workspace
cd ~/workspace
git clone https://github.com/deepseek-ai/DeepSeek-OCR-2.git
```
