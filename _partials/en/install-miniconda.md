## 3. 🐍 Install Miniconda and Configure Conda and Pip Mirrors (China)

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
