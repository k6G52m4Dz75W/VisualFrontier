<!-- zh --> ## 10. 🌐 启动vLLM服务
<!-- en --> ## 10. 🌐 Start the vLLM Server

<!-- zh --> 启动vLLM服务后，可以通过OpenAI兼容接口直接访问：<http://127.0.0.1:8000/>
<!-- en --> Once the vLLM server is running, you can access it via the OpenAI-compatible endpoint: <http://127.0.0.1:8000/>

```bash
vllm serve ~/.cache/modelscope/models/deepseek-ai--{{MODEL_NAME}}/snapshots/master/ --served-model-name {{MODEL_NAME}} --logits_processors vllm.model_executor.models.deepseek_ocr:NGramPerReqLogitsProcessor --no-enable-prefix-caching --mm-processor-cache-gb 0
```
