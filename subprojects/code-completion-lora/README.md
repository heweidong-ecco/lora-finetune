# LoRA-- code completion（代码补全） 
##  代码补全的数据格式
和之前的通用微调不同，代码补全使用的是 FIM（Fill-in-the-Middle，中间填充）格式：

```text
<fim_prefix>def quick_sort(arr):<fim_suffix><fim_middle>
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
```

阿里通义灵码格式（更简单，推荐）：

```json
{
  "instruction": "补全以下Python代码",
  "input": "def quick_sort(arr):\n    \"\"\"快速排序算法\"\"\"",
  "output": "    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + middle + quick_sort(right)"
}
```
## 操作流程
- 下载代码专用模型
代码编辑专用模型 Qwen3-Coder-7B
from huggingface_hub import snapshot_download
snapshot_download(
    "Qwen/Qwen3-Coder-7B-Instruct",
    local_dir="/root/autodl-fs/models/Qwen3-Coder-7B-Instruct"
)
- 第1步：前置条件
cd /root/autodl-fs/LLaMA-Factory
source llama-factory-env/bin/activate
pip install datasets huggingface_hub -q
- 第2步：数据集从 The Stack 提取 Python 代码片段，并验证 ast.parse 语法检查 确保数据质量。
  The Stack 需要HuggingFace授权的“门控数据集”无法使用
  备选：- 使用 ModelScope 上的代码数据集
  from modelscope.msdatasets import MsDataset
dataset = MsDataset.load("codefuse-ai/CodeExercise-Python-27k", split="train")
- python extract_code_data.py
- 最快有效方法， 使用本地 Python 库提取代码片段
  python local_code_extractor.py
- 第3步：质量检查
  python check_quality.py
- 注册数据集
  编辑 data/dataset_info.json，添加：
```json
"code_completion": {
  "file_name": "code_completion_dataset.json"
}
```
- 第4步：创建微调配置
  examples/train_lora/code_completion_lora.yaml
  训练约3-5分钟完成（250条数据，7B模型）。观察loss曲线，确认正常下降后继续。
- 第5步：导出并部署到Ollama
```#导出为Ollama可用格式
llamafactory-cli export \
    --model_name_or_path /root/autodl-fs/models/Qwen3-Coder-7B-Instruct \
    --adapter_name_or_path /root/autodl-fs/LLaMA-Factory/saves/code_completion_lora \
    --template qwen \
    --finetuning_type lora \
    --export_dir /root/autodl-fs/LLaMA-Factory/saves/code_completion_ollama \
    --export_ollama true
#导入到Ollama
ollama create code-completer -f /root/autodl-fs/LLaMA-Factory/saves/code_completion_ollama/Modelfile
验证：
ollama list | grep code-completer
- 第6步：功能测试
#测试1：函数补全
ollama run code-completer "def fibonacci(n):
    \"\"\"返回斐波那契数列第n项\"\"\""

#测试2：类方法补全
ollama run code-completer "class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
    
    def transfer(self, target, amount):
        \"\"\"转账到另一个账户\"\"\"" 

#测试3：注释转代码
ollama run code-completer "# 读取CSV文件，计算每列的平均值，返回字典"
- 第7步：与通用模型对比
#用同一个问题测试基座模型（未微调）
ollama run qwen3:8b "def quicksort(arr):
    \"\"\"快速排序\"\"\""

#对比微调后的代码模型
ollama run code-completer "def quicksort(arr):
    \"\"\"快速排序\"\"\""
```

