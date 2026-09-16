# Ollama部署微调模型
## 前置环境

```
cd /root/autodl-fs/LLaMA-Factory
source llama-factory-env/bin/activate

ls -lh saves/exp1_q4km.gguf
#如果没有 Q4_K_M 版本，用 FP16 版本也可以
ls -lh saves/exp1_fp16.gguf
## 方案一：LLaMA-Factory 支持直接导出为 Ollama 可用的 Modelfile：
bash
llamafactory-cli export \
    --model_name_or_path /root/autodl-fs/models/Qwen3-8B-Instruct \
    --adapter_name_or_path /root/autodl-fs/LLaMA-Factory/saves/exp1_baseline \
    --template qwen \
    --finetuning_type lora \
    --export_dir /root/autodl-fs/LLaMA-Factory/saves/exp1_ollama \
    --export_ollama true
这会自动生成 Modelfile 和所需的模型文件，直接执行：

bash
ollama create my-fine-tuned-model -f /root/autodl-fs/LLaMA-Factory/saves/exp1_ollama/Modelfile

如果需要量化可以使用方案二中的量化工具进行量化
## 方案二：原始创建法
```
- 合并 LoRA HuggingFace 格式文件，在out-GGUF-Script 文件夹中的 README.md
- 转换 GGUF 格式   在out-GGUF-Script 文件夹中的 README.md
- 量化 GGUF   在out-GGUF-Script 文件夹中的 README.md
- 创建 Modelfile.后缀 文件
  在 /root/autodl-fs/LLaMA-Factory/ 下创建 Modelfile
```
#Modelfile - 微调模型部署配置
#指定 GGUF 文件路径
FROM /root/autodl-fs/LLaMA-Factory/saves/exp1_q4km.gguf

#系统提示词（定义模型的行为和风格）
SYSTEM """You are a helpful AI assistant trained on the Alpaca dataset. 
You provide accurate, clear, and concise responses to user questions.
You follow instructions carefully and respond in the same language as the user."""

#推理参数
PARAMETER temperature 0.7 
PARAMETER top_p 0.9 
PARAMETER top_k 40 
PARAMETER num_predict 512  

#模板（对话格式，Qwen系列用 chatml）
TEMPLATE """<|im_start|>system
{{ .System }}<|im_end|>
<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
"""
```
- 参数解释：
  参数	含义	推荐值
FROM	GGUF 文件路径	你的实际路径
SYSTEM	系统提示词，定义模型人设	根据微调任务自定义
temperature	创造性（0=稳定，1=狂野）	日常用0.7，评估用0.0
top_p	核采样概率	0.9
top_k	候选token数	40
num_predict	最大输出长度	512
TEMPLATE	对话格式模板	Qwen系列用 chatml
如果你用的是 FP16 版本，把 FROM 改为：
dockerfile
FROM /root/autodl-fs/LLaMA-Factory/saves/exp1_fp16.gguf

# 导入模型到 Ollama并进行测试
```
- 导入模型到 Ollama
#创建模型（给模型起个名字）
#后续的指令名要 根据这个进行更改 
ollama create my-fine-tuned-model -f Modelfile
看到 success 即导入成功。验证：
bash
ollama list
#应该能看到 my-fine-tuned-model 在列表中
- 功能测试——验证模型能正常回答
bash
#测试1：简单问候
ollama run my-fine-tuned-model "Hello, how are you?"
#测试2：指令跟随（用 alpaca 数据集中的典型问题）
ollama run my-fine-tuned-model "Explain the concept of gravity in simple terms."
#测试3：知识问答
ollama run my-fine-tuned-model "What is the capital of France?"
观察要点：

回答是否流畅（无明显截断、重复）
回答是否切题（和问题相关）
回答语言是否统一（英文问题英文回答）
回答是否有乱码或特殊字符
- 性能测试——对比推理速度

#测试基座模型速度
echo "基座模型 (qwen3:8b):"
time ollama run qwen3:8b "Explain machine learning in one paragraph." --verbose 2>&1 | grep -E "eval duration|total duration"
#测试微调模型速度
echo "微调模型 (my-fine-tuned-model):"
time ollama run my-fine-tuned-model "Explain machine learning in one paragraph." --verbose 2>&1 | grep -E "eval duration|total duration"
- 记录对比数据：
模型	推理时长	每秒token数	备注
qwen3:8b（基座）	?	?	原始模型
my-fine-tuned-model	?	?	微调后+Q4_K_M量化
- 用 API 方式调用
bash
#测试 API 端点
curl http://localhost:11434/api/generate -d '{
  "model": "my-fine-tuned-model",
  "prompt": "What is the difference between AI and ML?",
  "stream": false
}'
```
- 使用测试和评估 脚本，综合评估LoRA微调效果，用微调模型批量回答测试集的 10 个问题，和第13天的评估管道对接
测试和评估 脚本：在 BadCase_AI_evaluation_pipeline 文件夹中
测试数据集使用之前 BadCase_AI_evaluation_pipeline/data 中的 my_test_dataset.json
python test_lora_evaluation.py 
产物 evaluation_results.json
python compare_and_judge.py
产物 final_judgment.json