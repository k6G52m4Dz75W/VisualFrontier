## 4. ⚡ 安装uv并配置uv国内镜像

uv速度飞快，且节省缓存空间，强烈推荐替代pip

```bash
# 安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 配置uv国内镜像
echo 'export UV_DEFAULT_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"' >> ~/.bashrc
# 使当前终端立即生效
source ~/.bashrc
```
