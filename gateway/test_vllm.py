from vllm import LLM, SamplingParams

# 加载模型
llm = LLM(model="qwen2.5:7b", tokenizer="qwen2.5:7b")

# 配置采样参数
sampling_params = SamplingParams(temperature=0.7, top_p=0.9, max_tokens=100)

# 执行推理
prompts = ["用一句话解释什么是GPU。"]
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(output.outputs[0].text)

# 使用 OpenAI 兼容 API 服务 来启动 vLLM，使它有可访问的本地主机地址。 
'''
第3步：启动 vLLM 的 OpenAI 兼容 API 服务
vLLM 内置了一个和 OpenAI 完全兼容的 API 服务，这意味着你可以用调用 ChatGPT 一样的方式调用它。
国内加速加载：
bash
export HF_ENDPOINT=https://hf-mirror.com

方法一：让 vLLM 自动从 HuggingFace 下载模型 自动下载模型到默认缓存目录
bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-7B-Instruct \
  --served-model-name my-local-model \
  --host 0.0.0.0 \
  --port 8001
  启动成功后，你会看到 INFO: Uvicorn running on http://0.0.0.0:8001。
这里的 Qwen/Qwen2.5-7B-Instruct 是 HuggingFace 上的模型标识符。
vLLM 会自动下载模型到默认缓存目录（通常在 ~/.cache/huggingface/hub/）。
首次运行时会自动下载模型到 ~/.cache/huggingface/hub/ 目录，之后无需重复下载。

方案二：手动下载模型到文件存储，再用 vLLM 加载
如果你想指定下载路径（比如放到文件存储中永久保留），可以先用 Python 脚本手动下载：
python
from huggingface_hub import snapshot_download
snapshot_download(
    "Qwen/Qwen2.5-7B-Instruct",
    local_dir="/root/autodl-fs/models/qwen2.5-7b-instruct"
)
然后在启动 vLLM 时指定本地路径：
bash
python -m vllm.entrypoints.openai.api_server \
  --model /root/autodl-fs/models/qwen2.5-7b-instruct \
  --served-model-name my-local-model \
  --host 0.0.0.0 \
  --port 8001
  启动成功后，你会看到 INFO: Uvicorn running on http://0.0.0.0:8001。
这里的model /root/autodl-fs/models/qwen2.5-7b-instruct就是下载好的HuggingFace格式模型路径。


第4步：用 curl 测试 vLLM 的 API
打开一个新的终端窗口，执行：
bash
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "my-local-model",
    "messages": [
      {"role": "user", "content": "用一句话解释什么是GPU"}
    ],
    "temperature": 0.7
  }'
如果一切正常，你会收到一个标准的 OpenAI Chat Completion 格式的 JSON 响应。
'''

#第5步：用 Python 客户端调用 vLLM
#你可以像使用 OpenAI 库一样调用它：
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8001/v1", api_key="not-needed")
response = client.chat.completions.create(
    model="my-local-model",
    messages=[{"role": "user", "content": "你好"}]
)

print(response.choices[0].message.content)
