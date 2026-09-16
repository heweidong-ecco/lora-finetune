# summarize_dataset.py
# 第2步：总结数据集领域
# 总结，提取的英文 数据集 中的内容，并翻译，保留中英文内容。
# summarize_dataset.py
import json
import requests

def load_data(filepath, max_items=80):
    with open(filepath, "r") as f:
        data = json.load(f)
    # 随机采样80条用于总结
    import random
    random.seed(42)
    return random.sample(data, min(max_items, len(data)))

def summarize_dataset(data):
    """用 qwen3:8b 总结数据集领域"""
    
    # 只提取 instruction 部分，减少上下文
    instructions = [item["instruction"] for item in data]
    sample_text = "\n".join([f"{i+1}. {inst}" for i, inst in enumerate(instructions)])
    
    prompt = f"""You are a data analyst. Below is a sample of 80 instructions from a training dataset.
Please analyze and summarize:
1. What domains/topics does this dataset cover? (e.g., coding, writing, math, general knowledge)
2. What types of tasks are most common? (e.g., generation, classification, summarization)
3. What is the overall style and quality of the instructions?

Sample instructions:
{sample_text}

Provide your summary in English first, then translate to Chinese.
Format:
=== ENGLISH SUMMARY ===
[Your English summary here]

=== 中文总结 ===
[你的中文翻译]"""
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen3:8b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 1000
            }
        }
    )
    
    return response.json().get("response", "Summary failed")

# 执行
data = load_data("data/my_dataset.json")
summary = summarize_dataset(data)

with open("data/dataset_summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)

print("数据集总结已保存到 data/dataset_summary.txt")
print(summary)