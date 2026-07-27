## 9. 🚀 安装vLLM及后端

注意：**不要**遵照官方的安装流程执行安装，那仅适用于当时的版本状况，尤其

- **不要**以指定版本方式安装torch
- **不要**以指定版本方式安装vllm
- **不要**安装**任何版本**flash-attn
- **不要**安装requiements.txt依赖包

当前使用以下方法安装才是最佳实践

```bash
# 官方秘诀出处：https://docs.vllm.ai/projects/recipes/en/latest/DeepSeek/{{MODEL_NAME}}.html
uv pip install -U vllm --torch-backend auto
```
