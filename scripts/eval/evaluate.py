
'''
有自动化评估：一个脚本，按回车。3分钟后，一份完整的评估报告出现在你面前。报告包含：基座模型和微调模型对50条数据的完整回答、每条数据的胜负判定、整体胜率统计、Bad Case分类。下次换模型，同一套脚本再跑一遍，结果直接和上一份报告并列对比。

自动化评估的本质：把“人肉评测”变成“代码执行”，让评估可重复、可对比、可追溯。

评估管道的五步流水线
text
加载测试集  → 基座模型推理 → 微调模型推理 → 裁判对比 → 输出报告
    ↓              ↓               ↓            ↓         ↓
test_dataset   base_model   tuned_model   judge_model  report
50条数据       直接回答      加载LoRA      公正评判    JSON+总结
每一步都是代码自动执行，全程无需人工参与。

通用性设计
evaluate.py 不仅用于本次评估，后续所有微调任务均可复用：
修改项	方式
切换测试集	修改 TEST_FILE 路径
切换待评估模型	修改 TUNED_MODELS 字典
切换裁判模型	修改 JUDGE_MODEL
增加对比维度	在 TUNED_MODELS 中增加条目

完整工作流总结：
text
微调完成 → 导出 GGUF → Ollama 导入 → evaluate.py 快速评估
    ↓
效果达标 → vLLM 部署 → Locust 压测 → 生产上线
'''
# 自动化评估流水线——一键评估基座模型 vs 微调模型 （支持多个checkpoint）
# 调用API 使用 Ollama 及 GGUF格式
# !/usr/bin/env python3
"""
自动化评估流水线
一键评估基座模型 vs 微调模型（支持多个checkpoint）
"""

import json
import time
import requests
import os
import re
import sys
from datetime import datetime

# ==================== 配置区 ====================
# 测试集路径,测试数据集在自定义的 AI数据处理 文件夹中
TEST_FILE = "BadCase_AI_evaluation_pipeline/data/my_test_dataset.json"

# 基座模型（Ollama中已加载）
BASE_MODEL = "qwen3:8b"

# 微调模型配置（可以放多个，自动全部评估）
TUNED_MODELS = {
    "final": {
        "path": "/root/autodl-fs/LLaMA-Factory/saves/exp1_baseline",
        "label": "最终权重(step 189)"
    },
    "checkpoint_75": {
        "path": "/root/autodl-fs/LLaMA-Factory/saves/exp1_baseline/checkpoint-75",
        "label": "最低loss(step 75)"
    },
    # 如果没有某个checkpoint，注释掉或删除对应条目
}

# 裁判模型
JUDGE_MODEL = "qwen3:8b"

# 输出文件
OUTPUT_DIR = "evaluation_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==================== 数据加载 ====================
def load_test_data(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✅ 已加载测试集: {len(data)} 条数据")
    return data

# ==================== 模型推理 ====================
def generate_ollama(model_name, instruction, input_text="", temperature=0.0, max_tokens=512):
    """调用 Ollama 模型生成回答"""
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
                "temperature": temperature,
                "num_predict": max_tokens
            }
        },
        timeout=120
    )
    
    if response.status_code == 200:
        return response.json().get("response", "")
    else:
        return f"[ERROR: HTTP {response.status_code}]"


def generate_tuned(model_name, instruction, input_text="", temperature=0.0, max_tokens=512):
    """调用已部署到 Ollama 的微调模型"""
    return generate_ollama(model_name, instruction, input_text, temperature, max_tokens)


# ==================== 批量推理 ====================
def batch_inference(test_data, base_model, tuned_models, tuned_name=None):
    """对测试集进行批量推理"""
    results = []
    total = len(test_data)
    
    for i, item in enumerate(test_data):
        instruction = item["instruction"]
        input_text = item.get("input", "")
        reference = item.get("output", "")
        
        print(f"  推理进度: {i+1}/{total} - {instruction[:60]}...")
        
        # 基座模型推理
        base_response = generate_ollama(base_model, instruction, input_text)
        time.sleep(0.3)
        
        # 微调模型推理
        tuned_response = generate_tuned(tuned_name, instruction, input_text)
        time.sleep(0.3)
        
        result = {
            "id": i,
            "instruction": instruction,
            "input": input_text,
            "reference_output": reference,
            "base_model_response": base_response,
            "tuned_model_response": tuned_response
        }
        results.append(result)
    
    return results


# ==================== 裁判对比 ====================
def judge_single(item, judge_model=JUDGE_MODEL):
    """让大模型公正对比两个回答"""
    
    prompt = f"""You are an impartial AI output evaluator. Compare two responses and decide which is better.

CRITICAL RULES:
1. You are a JUDGE, not an assistant. Do NOT answer the instruction.
2. Compare ONLY the two given responses. Ignore the reference output.
3. Be objective. If both are equally good/bad, say TIE.
4. Do NOT favor longer responses. Quality > Quantity.
5. Output in JSON format ONLY. No other text.

Evaluation Criteria:
- Accuracy: Correctly addresses the instruction?
- Completeness: Covers all parts?
- Clarity: Well-structured and clear?
- Conciseness: No unnecessary filler?

Instruction:
{{"instruction": "{item['instruction']}"}}

Response A (Base Model):
{{"response": "{item['base_model_response'][:800]}"}}

Response B (Tuned Model):
{{"response": "{item['tuned_model_response'][:800]}"}}

Output ONLY this JSON:
{{"winner": "A"/"B"/"TIE", "confidence": "high"/"medium"/"low", "reason": "Brief explanation", "category": "A_better"/"B_better"/"both_good"/"both_bad"}}"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": judge_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0, "num_predict": 300}
        },
        timeout=120
    )
    
    text = response.json().get("response", "")
    
    # 解析JSON
    try:
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    
    return {"winner": "ERROR", "reason": text, "confidence": "low", "category": "parse_error"}


def run_judgment(results, tuned_label=""):
    """对所有结果进行裁判对比"""
    judgments = []
    stats = {"A": 0, "B": 0, "TIE": 0, "ERROR": 0}
    
    total = len(results)
    for i, item in enumerate(results):
        print(f"  裁判进度: {i+1}/{total}")
        judgment = judge_single(item)
        judgment["id"] = i
        judgment["instruction"] = item["instruction"]
        judgments.append(judgment)
        
        winner = judgment.get("winner", "ERROR")
        stats[winner] = stats.get(winner, 0) + 1
    
    # 计算胜率
    valid_total = total - stats.get("ERROR", 0)
    stats["base_win_rate"] = f"{stats['A']/total*100:.1f}%"
    stats["tuned_win_rate"] = f"{stats['B']/total*100:.1f}%"
    stats["tie_rate"] = f"{stats['TIE']/total*100:.1f}%"
    
    return {
        "model_label": tuned_label,
        "total": total,
        "statistics": stats,
        "details": judgments
    }


# ==================== 报告生成 ====================
def generate_report(base_results, tuned_results, tuned_label=""):
    """生成最终评估报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "meta": {
            "timestamp": timestamp,
            "base_model": BASE_MODEL,
            "tuned_model": tuned_label,
            "test_size": len(base_results),
            "judge_model": JUDGE_MODEL
        },
        "tuned_results": tuned_results
    }
    
    # 保存JSON
    json_path = os.path.join(OUTPUT_DIR, f"report_{tuned_label.replace(' ', '_')}_{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 生成可读总结
    stats = tuned_results["statistics"]
    summary = f"""
========================================
  微调模型评估报告
========================================
生成时间: {timestamp}
基座模型: {BASE_MODEL}
微调模型: {tuned_label}
测试数据: {stats['total']} 条
裁判模型: {JUDGE_MODEL}

--- 整体结果 ---
基座模型胜: {stats['A']} 次 ({stats['base_win_rate']})
微调模型胜: {stats['B']} 次 ({stats['tuned_win_rate']})
平局: {stats['TIE']} 次 ({stats['tie_rate']})
解析错误: {stats.get('ERROR', 0)} 次

--- Bad Case 列表（基座模型胜出）---
"""
    
    for j in tuned_results["details"]:
        if j.get("winner") == "A":
            summary += f"\n[{j['id']}] {j['instruction'][:80]}...\n"
            summary += f"  原因: {j.get('reason', 'N/A')}\n"
            summary += f"  置信度: {j.get('confidence', 'N/A')}\n"
    
    summary += "\n--- 正向案例（微调模型胜出，前5条）---\n"
    b_wins = [j for j in tuned_results["details"] if j.get("winner") == "B"]
    for j in b_wins[:5]:
        summary += f"\n[{j['id']}] {j['instruction'][:80]}...\n"
        summary += f"  原因: {j.get('reason', 'N/A')}\n"
    
    summary += f"\n========================================\n"
    summary += f"完整报告: {json_path}\n"
    
    # 保存TXT
    txt_path = json_path.replace(".json", ".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(summary)
    return json_path, txt_path


# ==================== 主流程 ====================
def main():
    print("=" * 60)
    print("  自动化评估流水线")
    print("=" * 60)
    
    # Step 1: 加载测试集
    print("\n[1/4] 加载测试集...")
    test_data = load_test_data(TEST_FILE)
    
    # 对每个微调模型进行评估
    for tuned_name, tuned_config in TUNED_MODELS.items():
        tuned_label = tuned_config["label"]
        tuned_model_name = tuned_name
        
        print(f"\n[2/4] 批量推理 - {tuned_label}...")
        # 注意：这里需要先从checkpoint创建Ollama模型
        # 如果checkpoint模型不存在，跳过
        # 实际使用时，确保微调模型已通过ollama create导入
        
        try:
            results = batch_inference(
                test_data, 
                BASE_MODEL, 
                tuned_model_name,
                tuned_name
            )
            print(f"  推理完成，共 {len(results)} 对回答")
        except Exception as e:
            print(f"  ❌ 推理失败: {e}")
            print(f"  提示: 确保微调模型已通过 ollama create 导入到 Ollama")
            continue
        
        # Step 3: 裁判对比
        print(f"\n[3/4] 裁判对比 - {tuned_label}...")
        judgment = run_judgment(results, tuned_label)
        
        # Step 4: 生成报告
        print(f"\n[4/4] 生成报告 - {tuned_label}...")
        json_path, txt_path = generate_report(results, judgment, tuned_label)
        
        print(f"\n✅ 评估完成!")
        print(f"  JSON报告: {json_path}")
        print(f"  TXT报告: {txt_path}")

if __name__ == "__main__":
    main()