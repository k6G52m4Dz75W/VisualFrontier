<!-- zh --> ## {{STEP}}. 🚀 安装vLLM及后端
<!-- en --> ## {{STEP}}. 🚀 Install vLLM and Backend

<!-- zh --> 注意：**不要**遵照官方的安装流程执行安装，那仅适用于当时的版本状况，尤其
<!-- en --> **Important:** Do **not** follow the official installation instructions – they are only valid for older versions. In particular:

<!-- zh --> - **不要**以指定版本方式安装torch
<!-- en --> - **Do not** install torch with a pinned version
<!-- zh --> - **不要**以指定版本方式安装vllm
<!-- en --> - **Do not** install vLLM with a pinned version
<!-- zh --> - **不要**安装**任何版本**flash-attn
<!-- en --> - **Do not** install **any version** of flash-attn
<!-- zh --> - **不要**安装requiements.txt依赖包
<!-- en --> - **Do not** install the `requirements.txt` dependencies

<!-- zh --> 当前使用以下方法安装才是最佳实践
<!-- en --> The following approach is the current best practice:

```bash
<!-- zh --> # 官方秘诀出处：https://docs.vllm.ai/projects/recipes/en/latest/DeepSeek/{{MODEL_NAME}}.html
<!-- en --> # Official tip source: https://docs.vllm.ai/projects/recipes/en/latest/DeepSeek/{{MODEL_NAME}}.html
uv pip install -U vllm --torch-backend auto
```
