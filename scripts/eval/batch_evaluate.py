# batch_evaluate.py
# 第4步：批量整合测试文档，
# 基座模型回答和微调模型的批量推理 脚本
# 
import json
import requests
import time

def load_test_data(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def generate_response(model_name, instruction, input_text=""):
    """调用Ollama生成回答"""
    prompt = instruction
    if input_text:
        prompt = input_text + "\n\n" + instruction
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 512
            }
        }
    )
    return response.json().get("response", "")

def run_evaluation(test_file, base_model, tuned_model, output_file):
    test_data = load_test_data(test_file)
    results = []
    
    for i, item in enumerate(test_data):
        print(f"处理 {i+1}/{len(test_data)}: {item['instruction'][:60]}...")
        
        # 基座模型回答
        base_response = generate_response(base_model, item["instruction"], item.get("input", ""))
        time.sleep(0.5)
        
        # 微调模型回答
        tuned_response = generate_response(tuned_model, item["instruction"], item.get("input", ""))
        time.sleep(0.5)
        
        results.append({
            "id": i,
            "instruction": item["instruction"],
            "input": item.get("input", ""),
            "reference_output": item["output"],
            "base_model_response": base_response,
            "tuned_model_response": tuned_response
        })
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"评估完成，结果保存到 {output_file}")

# 执行
run_evaluation(
    "data/my_test_dataset.json",
    "qwen3:8b",                # 基座模型
    "qwen3:8b",                # 微调模型（需要先用 Ollama 加载 LoRA）
    "evaluation_results.json"
)