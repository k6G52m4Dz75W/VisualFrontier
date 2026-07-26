## 10. 🌐 启动vLLM服务

启动vLLM服务后，可以通过OpenAI兼容接口直接访问：<http://127.0.0.1:8000/>

```bash
vllm serve ~/.cache/modelscope/models/deepseek-ai--DeepSeek-OCR-2/snapshots/master/ --served-model-name DeepSeek-OCR-2 --logits_processors vllm.model_executor.models.deepseek_ocr:NGramPerReqLogitsProcessor --no-enable-prefix-caching --mm-processor-cache-gb 0
```
