# 量化对比测试
# 编写一个简单的测试脚本，对比默认版本、4-bit、8-bit 三个版本的推理速度。
# 在 JupyterLab 中创建 test_benchmark_quant.py：

import requests
import time

def benchmark(model, prompt="用Python写一个快速排序算法", temperature=0.3):
    """测试模型的推理速度"""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "stream": False
    }
    
    start = time.time()
    response = requests.post(url, json=payload)
    duration = time.time() - start
    
    result = response.json()
    tokens_per_sec = result.get("eval_count", 0) / duration if duration > 0 else 0
    
    print(f"模型: {model}")
    print(f"  耗时: {duration:.2f}秒")
    print(f"  生成token数: {result.get('eval_count', 'N/A')}")
    print(f"  速度: {tokens_per_sec:.2f} tokens/s")
    print(f"  回答前100字: {result['response'][:100]}...")
    print()
    
    return duration, tokens_per_sec

if __name__ == "__main__":
    models = ["qwen3:1.5b", "qwen2.5:3b", "qwen2.5:7b"]
    for model in models:
        benchmark(model)

'''
运行测试：
bash
python benchmark_quant.py
观察三种模型的推理速度和回答质量差异，记录到笔记中。
'''

