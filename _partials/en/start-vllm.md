## 10. 🌐 Start the vLLM Server

Once the vLLM server is running, you can access it via the OpenAI-compatible endpoint: <http://127.0.0.1:8000/>

```bash
vllm serve ~/.cache/modelscope/models/deepseek-ai--{{MODEL_NAME}}/snapshots/master/ --served-model-name {{MODEL_NAME}} --logits_processors vllm.model_executor.models.deepseek_ocr:NGramPerReqLogitsProcessor --no-enable-prefix-caching --mm-processor-cache-gb 0
```
