# ModelScope（魔搭）国内环境大模型下载最有用
# 安装 modelscope
# pip install modelscope
# 如果用# 用 Python 命令直接下载
'''
python -c "from modelscope import snapshot_download; snapshot_download('Qwen/Qwen2.5-7B-Instruct', cache_dir='/root/autodl-fs/models/qwen2.5-7b-instruct')"
'''
# 如果用.py文件下载就执行这个文件。代码如下
from modelscope import snapshot_download
snapshot_download(
    "Qwen/Qwen2.5-7B-Instruct", 
    cache_dir="/root/autodl-fs/models/qwen2.5-7b-instruct"
    )
'''
ModelScope（魔搭）终端指令
pip install modelscope
modelscope search qwen2.5-7b  命令行搜索
modelscope show Qwen/Qwen2.5-7B-Instruct 查看某个模型的详细信息
验证某个模型是否在 ModelScope 上
你可以在终端里用这个命令快速测试：
bash
modelscope download Qwen/Qwen2.5-7B-Instruct --dry-run
通用命令：ModelScope 下载任意模型
python
from modelscope import snapshot_download
# 下载 Qwen 系列
snapshot_download("Qwen/Qwen2.5-7B-Instruct", cache_dir="/root/autodl-fs/models/qwen2.5-7b")
# 下载 Llama 3
snapshot_download("LLM-Research/Meta-Llama-3-8B-Instruct", cache_dir="/root/autodl-fs/models/llama3-8b")
# 下载 ChatGLM
snapshot_download("ZhipuAI/chatglm3-6b", cache_dir="/root/autodl-fs/models/chatglm3-6b")
# 下载 DeepSeek
snapshot_download("deepseek-ai/DeepSeek-V2-Chat", cache_dir="/root/autodl-fs/models/deepseek-v2")
'''