# 第2步：对数据集 用大模型批量 生成改写版本
#!/usr/bin/env python3
"""用 qwen3:8b 为每个种子问题生成3个不同的改写版本"""

import json
import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:8b"
INSTRUCTION = "将以下用户口语查询改写为精确的检索查询，解决指代不明、用词模糊、信息缺失等问题。"

def generate_rewrites(original_query):
    """为一个原始问题生成3个改写版本"""
    prompt = f"""你是一个查询改写专家。给定一个用户的原始口语化查询，请生成3个不同的改写版本。
每个改写版本需要：
1. 补全缺失的信息（产品名、品牌、具体需求等）
2. 消除指代不明的词语（"那个"、"这个"、"它"等）
3. 将口语化表达转为正式书面语
4. 如果是多意图，拆分为单一意图
5. 保持原意不变，不要添加用户没问的内容

原始查询："{original_query}"

请直接输出3个改写版本，每行一个，格式如下：
改写1: [改写后的查询]
改写2: [改写后的查询]
改写3: [改写后的查询]

不要输出其他内容。"""
    
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,  # 提高温度增加多样性
                "num_predict": 512
            }
        },
        timeout=60
    )
    
    text = response.json().get("response", "")
    
    # 解析改写版本
    rewrites = []
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("改写") and ":" in line:
            query = line.split(":", 1)[1].strip()
            if query:
                rewrites.append(query)
    
    return rewrites[:3]  # 最多取3个


# 加载种子数据
with open("data/query_rewrite_seeds.json", "r") as f:
    seeds = json.load(f)

# 批量生成
dataset = []
for i, item in enumerate(seeds):
    original = item["input"]
    print(f"[{i+1}/{len(seeds)}] 改写: {original[:50]}...")
    
    rewrites = generate_rewrites(original)
    
    for j, rewrite in enumerate(rewrites):
        dataset.append({
            "instruction": INSTRUCTION,
            "input": original,
            "output": rewrite
        })
        print(f"    版本{j+1}: {rewrite[:60]}...")
    
    time.sleep(0.5)  # 控制请求速度

# 保存数据集
output_path = "data/query_rewrite_dataset.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print(f"\n✅ 数据集已生成: {output_path}")
print(f"   原始问题: {len(seeds)} 个")
print(f"   总样本数: {len(dataset)} 条")