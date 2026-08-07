<!-- zh --> ## {{STEP}}. ☁️ 安装modelscope
<!-- en --> ## {{STEP}}. ☁️ Install modelscope

<!-- zh --> 国内首选使用modelscope，简单直接，不用考虑hf下载速度慢和受限制问题
<!-- en --> For users in China, modelscope is the preferred choice – straightforward, no worries about slow Hugging Face downloads or restrictions.

```bash
pip install modelscope
```

<!-- zh --> ### 🤗 {{OPTIONAL}}安装huggingface并配置国内huggingface国内镜像
<!-- en --> ### 🤗 {{OPTIONAL}} Install Hugging Face Hub and Configure Mirror (China)

```bash
<!-- zh --> # 安装huggingface
<!-- en --> # Install huggingface_hub
pip install huggingface_hub

<!-- zh --> # 配置huggingface国内镜像
<!-- en --> # Configure Hugging Face domestic mirror
echo 'export HF_ENDPOINT=https://hf-mirror.com' >> ~/.bashrc
<!-- zh --> # 使当前终端立即生效
<!-- en --> # Apply immediately
source ~/.bashrc
```
