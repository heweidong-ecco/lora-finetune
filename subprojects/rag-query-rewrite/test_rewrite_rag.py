# 构建RAG对比测试
#!/usr/bin/env python3
"""对比三种方案：无改写 vs 云端API改写 vs 本地模型改写"""

import requests
import time
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

# 测试问题（覆盖你数据集中五种类型）
TEST_QUERIES = [
    "那个蓝色的怎么卖？",                    # 指代不明
    "上次说的那个方案定了吗？",               # 用词模糊
    "最新款多少钱？",                        # 信息缺失
    "有没有那种不用插电就能用的？",           # 口语化严重
    "帮我查一下订单还有那个物流",             # 多意图混合
]

def rewrite_with_local_model(query):
    """方案3：本地微调模型改写"""
    response = requests.post(OLLAMA_URL, json={
        "model": "query-rewriter",
        "prompt": f"将以下用户口语查询改写为精确的检索查询：{query}",
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 100}
    })
    return response.json().get("response", query)

def rewrite_with_cloud_api(query):
    """方案2：云端API改写（用8B模型模拟）"""
    response = requests.post(OLLAMA_URL, json={
        "model": "qwen3:8b",
        "prompt": f"将以下用户口语查询改写为精确的检索查询：{query}",
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 100}
    })
    return response.json().get("response", query)

def simulate_search(query):
    """模拟向量检索（简化版）"""
    # 在实际RAG中，这里会调用向量数据库
    return f"[检索结果] 关于 '{query}' 的相关信息..."

# 运行对比
results = []

for i, query in enumerate(TEST_QUERIES):
    print(f"\n[{i+1}/{len(TEST_QUERIES)}] 原始查询: {query}")
    
    # 方案1：无改写
    start = time.time()
    raw_results = simulate_search(query)
    raw_time = time.time() - start
    
    # 方案2：云端8B改写
    start = time.time()
    cloud_rewrite = rewrite_with_cloud_api(query)
    cloud_results = simulate_search(cloud_rewrite)
    cloud_time = time.time() - start
    
    # 方案3：本地3B微调模型改写
    start = time.time()
    local_rewrite = rewrite_with_local_model(query)
    local_results = simulate_search(local_rewrite)
    local_time = time.time() - start
    
    results.append({
        "original": query,
        "no_rewrite_time": round(raw_time, 3),
        "cloud_rewrite": cloud_rewrite,
        "cloud_rewrite_time": round(cloud_time, 3),
        "local_rewrite": local_rewrite,
        "local_rewrite_time": round(local_time, 3),
    })
    
    print(f"  无改写: {raw_time:.3f}s")
    print(f"  云端改写: {cloud_rewrite[:50]}... ({cloud_time:.3f}s)")
    print(f"  本地改写: {local_rewrite[:50]}... ({local_time:.3f}s)")

# 统计
avg_raw = sum(r["no_rewrite_time"] for r in results) / len(results)
avg_cloud = sum(r["cloud_rewrite_time"] for r in results) / len(results)
avg_local = sum(r["local_rewrite_time"] for r in results) / len(results)

print(f"\n{'='*50}")
print(f"平均延迟对比：")
print(f"  无改写:     {avg_raw:.3f}s (基线)")
print(f"  云端8B改写:  {avg_cloud:.3f}s ({(avg_cloud/avg_raw - 1)*100:+.0f}%)")
print(f"  本地3B改写:  {avg_local:.3f}s ({(avg_local/avg_raw - 1)*100:+.0f}%)")
print(f"  本地比云端快: {(1 - avg_local/avg_cloud)*100:.0f}%")

# 保存结果
with open("rewrite_comparison.json", "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)