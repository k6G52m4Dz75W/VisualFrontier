## 5. ☁️ 安装modelscope

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
