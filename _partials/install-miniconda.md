<!-- zh --> ## {{STEP}}. 🐍 安装miniconda并配置conda和pip国内镜像
<!-- en --> ## {{STEP}}. 🐍 Install Miniconda and Configure Conda and Pip Mirrors (China)

<!-- zh --> 在Ubuntu的命令行界面中输入或复制粘贴以下整段代码回车即可直接运行，无需逐行复制粘贴，下同
<!-- en --> In the Ubuntu command line, enter or copy-paste the entire block below and press Enter to run it directly. No need to copy line by line; same applies below.

```bash
<!-- zh --> # 安装miniconda
<!-- en --> # Install Miniconda
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

<!-- zh --> # 配置conda国内镜像
<!-- en --> # Configure conda domestic mirrors (Tsinghua)
<!-- zh --> # 添加清华 conda-forge 镜像
<!-- en --> # Add Tsinghua conda-forge mirror
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
<!-- zh --> # 配置为显示channel地址，方便确认是否生效
<!-- en --> # Show channel URLs to verify configuration
conda config --set show_channel_urls yes
<!-- zh --> # 清除缓存使配置生效
<!-- en --> # Clear cache to apply changes
conda clean -i

<!-- zh --> # 配置pip国内镜像
<!-- en --> # Configure pip domestic mirror
<!-- zh --> # 配置清华源为默认下载源
<!-- en --> # Set Tsinghua as default index
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
<!-- zh --> # 将该源添加为受信任主机，避免SSL或其他网络问题
<!-- en --> # Add as trusted host to avoid SSL/network issues
pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn
```
