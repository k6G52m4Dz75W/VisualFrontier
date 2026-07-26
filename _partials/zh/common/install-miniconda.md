## 3. 🐍 安装miniconda并配置conda和pip国内镜像

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
