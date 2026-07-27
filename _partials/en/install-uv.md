## 4. ⚡ Install uv and Configure uv Mirror (China)

uv is extremely fast and saves cache space; highly recommended as a pip replacement.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Configure uv domestic mirror
echo 'export UV_DEFAULT_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"' >> ~/.bashrc
# Apply immediately in current terminal
source ~/.bashrc
```
