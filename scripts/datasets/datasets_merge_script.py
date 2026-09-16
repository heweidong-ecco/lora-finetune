# 合并数据并统一格式:推荐使用 
# alpaca 格式：
'''
json
[
  {
    "instruction": "用户的问题或指令",
    "input": "补充上下文（可选，没有就留空字符串）",
    "output": "期望模型给出的回答"
  }
]
'''
# 以下是合并脚本：

import json

# 合并三种来源的数据
all_data = []

# 1. 手工数据（先加入，作为质量基准）
'''with open("datasets_handcraft_data_cleaned.json", "r", encoding="utf-8") as f:
    all_data.extend(json.load(f))
'''
# 2. 开源数据
with open("datasets_open_source_data_cleaned_100.json", "r", encoding="utf-8") as f:
    all_data.extend(json.load(f))

# 3. 模型生成的数据
with open("datasets_generated_data_cleaned_100.json", "r", encoding="utf-8") as f:
    all_data.extend(json.load(f))

# 保存合并后的数据集
with open("/root/autodl-fs/LLaMA-Factory/data/my_dataset.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"合并完成，共 {len(all_data)} 条数据")