# DeepSeek-OCR Local Installation and Deployment Guide for Windows WSL

Last updated: `2027.7.24`

## 0. Install/Update NVIDIA Drivers

Visit the official website entry, select GeForce, and download the latest driver.

- Chinese official site: <https://www.nvidia.cn/drivers/>
- Global official site: <https://www.nvidia.com/en-us/drivers/>

> Current latest version: `610.74`
> Direct download link for the latest version: <https://cn.download.nvidia.com/Windows/610.74/610.74-desktop-win10-win11-64bit-international-dch-whql.exe>

## 1. Install WSL

Launch PowerShell as administrator and install WSL:

```Powershell
wsl --install
```

Wait for the automatic installation to complete.

## 2. Start Ubuntu

Click the Ubuntu icon in the Start menu to launch it.

![Ubuntu icon](Ubuntu.png)

## 3. Install Miniconda and Configure Conda and Pip Mirrors (China)

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

## 4. Install uv and Configure uv Mirror (China)

uv is extremely fast and saves cache space; highly recommended as a pip replacement.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Configure uv domestic mirror
echo 'export UV_DEFAULT_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"' >> ~/.bashrc
# Apply immediately in current terminal
source ~/.bashrc
```

## 5. Install modelscope

For users in China, modelscope is the preferred choice – straightforward, no worries about slow Hugging Face downloads or restrictions.

```bash
pip install modelscope
```

### [Optional] Install Hugging Face Hub and Configure Mirror (China)

```bash
# Install huggingface_hub
pip install huggingface_hub

# Configure Hugging Face domestic mirror
echo 'export HF_ENDPOINT=https://hf-mirror.com' >> ~/.bashrc
# Apply immediately
source ~/.bashrc
```

## 6. Download Model Weights

```bash
modelscope download --model deepseek-ai/DeepSeek-OCR
# Default download directory: ~/.cache/modelscope/models/deepseek-ai--DeepSeek-OCR
```

### [Optional] Download via Hugging Face

```bash
hf download deepseek-ai/DeepSeek-OCR
```

## 7. Create and Activate Conda Environment

Create a conda environment using the recommended Python version.

```bash
conda create -n deepseek-ocr python=3.12.9 -y
conda activate deepseek-ocr
```

## 8. Install CUDA Toolkit and Set Environment Variables

```bash
# Install the latest CUDA toolkit
conda install nvidia::cuda-toolkit -y
# Create environment variable config directory
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
# Write setting commands (automatically executed when environment is activated)
echo 'export LIBRARY_PATH=/usr/lib/wsl/lib:$LIBRARY_PATH' > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo 'export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH' > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
# (Optional) Add corresponding unset commands when deactivating
echo 'unset LD_LIBRARY_PATH' > $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
# After setting, reactivate the environment for changes to take effect
conda deactivate
conda activate deepseek-ocr
```

## 9. Install vLLM and Backend

**Important:** Do **not** follow the official installation instructions – they are only valid for older versions. In particular:

- **Do not** install torch with a pinned version
- **Do not** install vLLM with a pinned version
- **Do not** install **any version** of flash-attn
- **Do not** install the `requirements.txt` dependencies

The following approach is the current best practice:

```bash
# Official tip source: https://docs.vllm.ai/projects/recipes/en/latest/DeepSeek/DeepSeek-OCR.html
uv pip install -U vllm --torch-backend auto
```

## 10. Start the vLLM Server

Once the vLLM server is running, you can access it via the OpenAI-compatible endpoint: <http://127.0.0.1:8000/>

```bash
vllm serve ~/.cache/modelscope/models/deepseek-ai--DeepSeek-OCR/snapshots/master/ --served-model-name DeepSeek-OCR --logits_processors vllm.model_executor.models.deepseek_ocr:NGramPerReqLogitsProcessor --no-enable-prefix-caching --mm-processor-cache-gb 0
```

> VibeOCR is recommended for OCR scanning tasks:
> VibeOCR - Intelligent End‑to‑End Book OCR Solution — Multi‑model AI powered, PDF to plain text in one click
> <https://github.com/k6G52m4Dz75W/VibeOCR>

## [Optional] Clone the Repository

The repository is for development reference only and is not required to run the model.

```bash
mkdir -p ~/workspace
cd ~/workspace
git clone https://github.com/deepseek-ai/DeepSeek-OCR.git
```