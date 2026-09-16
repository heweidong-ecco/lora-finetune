# LoRA微调后 转化格式后的GGUF文件 +Modelfile注册后的模型的 测试脚本
# 同时调用基座模型和微调模型，生成评估所需的对比数据

#!/usr/bin/env python3
"""
批量测试脚本：同时调用基座模型和微调模型，生成评估所需的对比数据
"""

import json
import time
import requests

# ==================== 配置 ====================
TEST_FILE = "data/my_test_dataset.json"
OUTPUT_FILE = "evaluation_results.json"
BASE_MODEL = "qwen3:8b"                    # 基座模型（Ollama中已有）
TUNED_MODEL = "my-fine-tuned-model"        # 你的微调模型
MAX_SAMPLES = 10                           # 只处理前10条
OLLAMA_URL = "http://localhost:11434/api/generate"

def generate(model_name, instruction, input_text=""):
    prompt = instruction
    if input_text:
        prompt = input_text + "\n\n" + instruction

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0, "num_predict": 512}
        },
        timeout=120
    )
    if response.status_code == 200:
        return response.json().get("response", "")
    else:
        return f"[ERROR: HTTP {response.status_code}]"

# 加载测试集
with open(TEST_FILE, "r", encoding="utf-8") as f:
    test_data = json.load(f)
test_data = test_data[:MAX_SAMPLES]
print(f"已加载 {len(test_data)} 条测试数据")

results = []
for i, item in enumerate(test_data):
    instruction = item["instruction"]
    input_text = item.get("input", "")
    print(f"[{i+1}/{len(test_data)}] {instruction[:60]}...")

    # 基座模型回答
    base_resp = generate(BASE_MODEL, instruction, input_text)
    time.sleep(0.3)

    # 微调模型回答
    tuned_resp = generate(TUNED_MODEL, instruction, input_text)
    time.sleep(0.3)

    results.append({
        "id": i,
        "instruction": instruction,
        "input": input_text,
        "reference_output": item.get("output", ""),
        "base_model_response": base_resp,
        "tuned_model_response": tuned_resp
    })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✅ 测试完成，结果保存至 {OUTPUT_FILE}")
print("   现在可以运行 compare_and_judge.py 进行评估")