## 9. 🚀 Install vLLM and Backend

**Important:** Do **not** follow the official installation instructions – they are only valid for older versions. In particular:

- **Do not** install torch with a pinned version
- **Do not** install vLLM with a pinned version
- **Do not** install **any version** of flash-attn
- **Do not** install the `requirements.txt` dependencies

The following approach is the current best practice:

```bash
# Official tip source: https://docs.vllm.ai/projects/recipes/en/latest/DeepSeek/{{MODEL_NAME}}.html
uv pip install -U vllm --torch-backend auto
```
