# 性能测试脚本 test_benchmark_performance.py
# 脚本会对vLLM和Ollama分别进行压测，记录吞吐量和延迟数据。
# 产出性能基线压测 的 JSON文件 和 png图片
'''
文件命名和保存路径/root/autodl-fs/llm-gateway/
核心产出物 test_benchmark_results.json 和 test_benchmark_chart.png 保存好
'''
import time
import requests
import json
import statistics
import random
import os

#==================== 配置 ====================
VLLM_URL = "http://localhost:8001/v1/chat/completions"
OLLAMA_URL = "http://localhost:11434/api/generate"

#固定输入和输出长度
INPUT_TEXT = "人工智能" * 128  # 约512个token
TARGET_OUTPUT_LENGTH = 128    # 目标输出token数

#测试的并发级别
CONCURRENCY_LEVELS = [1, 4, 8]

#==================== 测试函数 ====================
def test_vllm(prompt: str, max_tokens: int) -> dict:
    """测试vLLM的Chat Completions API"""
    start = time.time()
    response = requests.post(VLLM_URL, json={
        "model": "my-local-model",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    })
    duration = time.time() - start
    data = response.json()
    output_text = data["choices"][0]["message"]["content"]
    output_tokens = len(output_text) // 2  # 粗略估算：中文约2字符/token
    return {
        "duration": duration,
        "output_tokens": output_tokens,
        "status": "success" if response.status_code == 200 else "error"
    }

def test_ollama(prompt: str, max_tokens: int) -> dict:
    """测试Ollama的generate API"""
    start = time.time()
    response = requests.post(OLLAMA_URL, json={
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "stream": False
    })
    duration = time.time() - start
    data = response.json()
    output_tokens = data.get("eval_count", 0)
    return {
        "duration": duration,
        "output_tokens": output_tokens,
        "status": "success" if response.status_code == 200 else "error"
    }

def run_benchmark(test_func, concurrency: int, prompt: str, max_tokens: int) -> dict:
    """模拟并发请求（使用同步方式顺序发送）"""
    durations = []
    total_tokens = 0
    
    for _ in range(concurrency):
        result = test_func(prompt, max_tokens)
        if result["status"] == "success":
            durations.append(result["duration"])
            total_tokens += result["output_tokens"]
    
    if not durations:
        return {"error": "所有请求都失败了"}
    
    # 计算指标
    total_duration = max(durations)  # 顺序发送的总耗时≈最慢的那个
    avg_latency = statistics.mean(durations)
    p99_latency = sorted(durations)[int(len(durations) * 0.99)] if len(durations) > 1 else durations[0]
    throughput = total_tokens / total_duration if total_duration > 0 else 0
    
    return {
        "concurrency": concurrency,
        "total_duration": round(total_duration, 2),
        "avg_latency": round(avg_latency, 2),
        "p99_latency": round(p99_latency, 2),
        "total_tokens": total_tokens,
        "throughput": round(throughput, 2)
    }

def create_chart(results: dict, output_path: str):
    """生成 vLLM vs Ollama 性能对比柱状图"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 6))
    engines = ["vLLM", "Ollama"]
    colors = ["#4d96ff", "#ff6b6b"]
    x = range(len(CONCURRENCY_LEVELS))
    width = 0.35
    for i, engine in enumerate(engines):
        throughputs = [r["throughput"] for r in results[engine] if "throughput" in r]
        ax.bar([p + i * width for p in x], throughputs, width, label=engine, color=colors[i])
    ax.set_xlabel("并发数")
    ax.set_ylabel("吞吐量 (tokens/s)")
    ax.set_title("vLLM vs Ollama 性能对比")
    ax.set_xticks([p + width / 2 for p in x])
    ax.set_xticklabels(CONCURRENCY_LEVELS)
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"图表已保存到 {output_path}")

#==================== 主程序 ====================
if __name__ == "__main__":
    print("=" * 60)
    print("vLLM vs Ollama 性能对比测试")
    print(f"输入长度: ~512 tokens | 输出长度: ~{TARGET_OUTPUT_LENGTH} tokens")
    print("=" * 60)
    
    results = {"vLLM": [], "Ollama": []}
    
    for concurrency in CONCURRENCY_LEVELS:
        print(f"\n--- 并发: {concurrency} ---")
        
        # 测试vLLM
        print("测试 vLLM...")
        vllm_result = run_benchmark(test_vllm, concurrency, INPUT_TEXT, TARGET_OUTPUT_LENGTH)
        vllm_result["engine"] = "vLLM"
        results["vLLM"].append(vllm_result)
        print(f"  vLLM: 吞吐量={vllm_result.get('throughput', 'N/A')} tokens/s, "
              f"平均延迟={vllm_result.get('avg_latency', 'N/A')}s, "
              f"P99延迟={vllm_result.get('p99_latency', 'N/A')}s")
        
        # 测试Ollama
        print("测试 Ollama...")
        ollama_result = run_benchmark(test_ollama, concurrency, INPUT_TEXT, TARGET_OUTPUT_LENGTH)
        ollama_result["engine"] = "Ollama"
        results["Ollama"].append(ollama_result)
        print(f"  Ollama: 吞吐量={ollama_result.get('throughput', 'N/A')} tokens/s, "
              f"平均延迟={ollama_result.get('avg_latency', 'N/A')}s, "
              f"P99延迟={ollama_result.get('p99_latency', 'N/A')}s")
    
    # 保存结果到文件
    with open("/root/autodl-fs/llm-gateway/test_benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    create_chart(results, "/root/autodl-fs/llm-gateway/test_benchmark_chart.png")
    print("测试完成！结果已保存到 test_benchmark_results.json和test_benchmark_chart.png")

'''
第1步：准备压测脚本
首先确保vLLM服务正在运行。如果没有运行，启动它：
bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-7B-Instruct \
  --served-model-name my-local-model \
  --host 0.0.0.0 \
  --port 8001
同样，确保Ollama服务也在运行（默认端口11434）。

第2步：运行测试并记录数据
bash
cd /root/autodl-fs/llm-gateway
python test_benchmark_performance.py
测试完成后，你会在当前目录下看到 
test_benchmark_results.json 文件和test_benchmark_chart.png，里面包含了所有测试数据。
'''
