'''
方案一：让 vLLM 自动从 HuggingFace  
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-7B-Instruct \
  --served-model-name my-local-model \
  --host 0.0.0.0 \
  --port 8001
这里的 Qwen/Qwen2.5-7B-Instruct 是 HuggingFace 上的模型标识符。vLLM 会自动下载模型到默认缓存目录（通常在 ~/.cache/huggingface/hub/）。
方案二：手动下载模型到文件存储，再用 vLLM 加载
如果你想指定下载路径（比如放到文件存储中永久保留），
可以先用 Python 脚本手动下载：执行这个python文件。
然后在启动 vLLM 时指定本地路径：
bash
python -m vllm.entrypoints.openai.api_server \
  --model /root/autodl-fs/models/qwen2.5-7b-instruct \
  --served-model-name my-local-model \
  --host 0.0.0.0 \
  --port 8001
结论：当前阶段，直接用 HuggingFace 模型名让 vLLM 自动下载是最方便的方式。 你不需要手动指定路径，vLLM 会帮你处理好。
'''
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from huggingface_hub import snapshot_download

snapshot_download(
    "Qwen/Qwen2.5-7B-Instruct",
    local_dir="/root/autodl-fs/models/qwen2.5-7b-instruct"
)