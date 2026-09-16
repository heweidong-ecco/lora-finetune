# 实例终端运行指令
'''
# 第一步：编写默认 路径
autodl数据保存在，文件存储中，每次启动必须运行指令
bash
export PATH="/root/autodl-fs/ollama/bin:$PATH"
export OLLAMA_MoDELS=/root/aotudl-fs/models

# 运行ollama拉取大模型，运行
ollama pull qwen2.5:7b #已经下载的模型
bash
ollama serve
ollama run qwen2.5:7b

# 编写Python调用脚本
bash
mkdir -p /root/autodl-fs/llm-gateway
cd /root/autodl-fs/llm-gateway
pip install requests
'''
# 进入 /root/autodl-fs/llm-gateway,选择 New → Text File
# 新建 test_ollama.py
# 终端运行
'''
bash 
cd /root/autodl-fs/llm-gateway
python test_ollama.py
如果一切正常，你应该能看到模型返回的回复内容。
'''
# 存储备份
'''
1. 下载代码文件到本地
在 JupyterLab 中，右键 test_ollama.py，选择 Download，保存到你的Mac本地。
2. 确认数据卷中有你的文件
bash
ls /root/autodl-tmp/llm-gateway/
应该能看到 test_ollama.py。
'''
