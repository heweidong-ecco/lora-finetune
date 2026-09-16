# 创建 test_evaluation.py
# 这个脚本是 分别执行基座模型和微调模型
# 对象是：测试文件，分别得到两个产物 evaluation_base.json 和 evaluation_finetuned.json
# 先启动 启动基座模型对话 启动微调模型对话（需要指定LoRA适配器路径
# llamafactory-cli chat examples/inference/... 和 llamafactory-cli chat examples/inference/...
# 人工并行对比，也可以给使用 脚本 用AI模型进行对比，改一下输入路径即可，
# 下面的 微调模型对话 适配器还没有集成到 Ollama基座上，暂时用模拟的 Ollama API调用模拟进行。
import json
import requests
import time

def load_test_data(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def test_model(model_name, test_data, api_url="http://localhost:8000/v1/generate"):
    """对测试集进行批量推理"""
    results = []
    
    for i, item in enumerate(test_data):
        prompt = item["instruction"]
        if item.get("input"):
            prompt = item["input"] + "\n" + prompt
        
        start = time.time()
        # 这里用Ollama API调用（需要先将模型部署到Ollama）
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.0}
            }
        )
        duration = time.time() - start
        
        result = {
            "id": i,
            "instruction": item["instruction"],
            "expected_output": item["output"],
            "actual_output": response.json().get("response", ""),
            "duration": round(duration, 2)
        }
        results.append(result)
        print(f"完成 {i+1}/{len(test_data)}: {item['instruction'][:50]}...")
    
    return results

# 执行测试
test_data = load_test_data("data/test_dataset.json")
# 测试基座模型
base_results = test_model("qwen2.5:7b", test_data)
# 测试微调模型
fine_tuned_results = test_model("my-fine-tuned-model", test_data)

# 保存结果
with open("evaluation_base.json", "w") as f:
    json.dump(base_results, f, ensure_ascii=False, indent=2)
with open("evaluation_finetuned.json", "w") as f:
    json.dump(fine_tuned_results, f, ensure_ascii=False, indent=2)

print("评估完成，结果已保存")