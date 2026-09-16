# prepare_data.py
# 提前数据集中的内容
# 第1步：准备数据集和测试集
from datasets import load_dataset
import json
import random
import os 

# 确保输出目录存在
os.makedirs("data", exist_ok=True)

# 下载 alpaca-cleaned,已经下载，并清洗了
# dataset = load_dataset("yahma/alpaca-cleaned", split="train")

# 如果文件就在当前目录，可以用下面的：
file_path = "datasets_open_source_data_cleaned.json"

# 直接读取已有的 JSON 文件
with open(file_path, "r", encoding="utf-8") as f:
    full_data = json.load(f)
    
# 取前550条（500条训练 + 50条测试）
data = []
for i, item in enumerate(full_data):
    if i >= 550:
        break
    data.append({
        "instruction": item["instruction"],
        "input": item.get("input", ""),
        "output": item["output"]
    })

# 随机打乱（alpaca-cleaned默认按任务类型排序，前550条可能全是同一类）
random.seed(42)
random.shuffle(data)

# 切分
train_data = data[:500]
test_data = data[500:550]

# 保存
with open("data/my_dataset.json", "w", encoding="utf-8") as f:
    json.dump(train_data, f, ensure_ascii=False, indent=2)

with open("data/my_test_dataset.json", "w", encoding="utf-8") as f:
    json.dump(test_data, f, ensure_ascii=False, indent=2)

print(f"训练集: {len(train_data)} 条")
print(f"测试集: {len(test_data)} 条")

'''
为什么是500+50而不是200+20：

500条训练数据足够LoRA学到稳定模式，loss曲线会更平滑
50条测试数据能给出有统计意义的评估结果
alpaca-cleaned是高质量数据，多点训练不会过拟合
'''
'''
为什么是500+50而不是200+20：

500条训练数据足够LoRA学到稳定模式，loss曲线会更平滑
50条测试数据能给出有统计意义的评估结果
alpaca-cleaned是高质量数据，多点训练不会过拟合
'''