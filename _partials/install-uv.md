<!-- zh --> ## 4. ⚡ 安装uv并配置uv国内镜像
<!-- en --> ## 4. ⚡ Install uv and Configure uv Mirror (China)

<!-- zh --> uv速度飞快，且节省缓存空间，强烈推荐替代pip
<!-- en --> uv is extremely fast and saves cache space; highly recommended as a pip replacement.

```bash
<!-- zh --> # 安装uv
<!-- en --> # Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

<!-- zh --> # 配置uv国内镜像
<!-- en --> # Configure uv domestic mirror
echo 'export UV_DEFAULT_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"' >> ~/.bashrc
<!-- zh --> # 使当前终端立即生效
<!-- en --> # Apply immediately in current terminal
source ~/.bashrc
```
