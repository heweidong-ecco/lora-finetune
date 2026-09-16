# compare_and_judge.py
# 第5步：大模型对比评估脚本
# 这是最关键的脚本，prompt必须严格设计以确保客观性。
# 大模型裁判对比评估 （含胜率统计）
import json
import requests

def load_results(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def judge_single_pair(item, judge_model="qwen3:8b"):
    """让大模型作为公正裁判，对比两个回答"""
    
    prompt = f"""You are an impartial AI output evaluator. Your task is to compare two AI responses to the same instruction and determine which one is better.

CRITICAL RULES - You MUST follow these strictly:
1. You are NOT the assistant. You are a JUDGE evaluating two other AIs.
2. Do NOT try to answer the instruction yourself.
3. Compare ONLY the two responses given below.
4. Be objective. If both are equally good or equally bad, say so.
5. Do NOT favor longer responses. Quality > Quantity.
6. Ignore the "reference output" if it biases you. Judge the actual responses.

Evaluation Criteria (in order of importance):
- Accuracy: Does the response correctly address the instruction?
- Completeness: Does it cover all parts of the instruction?
- Clarity: Is it well-structured and easy to understand?
- Conciseness: No unnecessary filler content.

Instruction:
{{
  "instruction": "{item['instruction']}",
  "input": "{item.get('input', '')}"
}}

Response A (Base Model):
{{
  "response": "{item['base_model_response'][:500]}"
}}

Response B (Fine-tuned Model):
{{
  "response": "{item['tuned_model_response'][:500]}"
}}

Please output your judgment in the following JSON format ONLY. No other text.
{{
  "winner": "A" or "B" or "TIE",
  "confidence": "high" or "medium" or "low",
  "reason": "Brief explanation in English (max 100 words)",
  "category": "A_better" or "B_better" or "both_good" or "both_bad"
}}"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": judge_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 300
            }
        }
    )
    
    return response.json().get("response", "")

def run_judgment(results_file, output_file):
    results = load_results(results_file)
    judgments = []
    
    for i, item in enumerate(results):
        print(f"评判 {i+1}/{len(results)}...")
        judgment_text = judge_single_pair(item)
        
        # 尝试解析JSON
        try:
            import re
            json_match = re.search(r'\{.*\}', judgment_text, re.DOTALL)
            if json_match:
                judgment = json.loads(json_match.group())
            else:
                judgment = {"winner": "ERROR", "reason": judgment_text}
        except:
            judgment = {"winner": "ERROR", "reason": judgment_text}
        
        judgment["id"] = i
        judgment["instruction"] = item["instruction"]
        judgments.append(judgment)
    
    # 统计
    a_wins = sum(1 for j in judgments if j.get("winner") == "A")
    b_wins = sum(1 for j in judgments if j.get("winner") == "B")
    ties = sum(1 for j in judgments if j.get("winner") == "TIE")
    errors = sum(1 for j in judgments if j.get("winner") == "ERROR")
    
    summary = {
        "total": len(judgments),
        "base_model_wins": a_wins,
        "tuned_model_wins": b_wins,
        "ties": ties,
        "errors": errors,
        "base_win_rate": f"{a_wins/len(judgments)*100:.1f}%",
        "tuned_win_rate": f"{b_wins/len(judgments)*100:.1f}%",
        "details": judgments
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 评估完成 ===")
    print(f"总测试数: {len(judgments)}")
    print(f"基座模型胜: {a_wins} ({summary['base_win_rate']})")
    print(f"微调模型胜: {b_wins} ({summary['tuned_win_rate']})")
    print(f"平局: {ties}")
    print(f"解析错误: {errors}")
    print(f"详细结果保存到: {output_file}")

# 执行
run_judgment("evaluation_results.json", "final_judgment.json")