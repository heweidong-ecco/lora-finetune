# 第2步：从 The Stack 提取 Python 代码片段
# 外部下载
#!/usr/bin/env python3
"""
从 The Stack 数据集提取 Python 代码片段，构建代码补全微调数据集
集成 ast.parse 语法检查，过滤语法错误的输出
"""
import os
from modelscope import MsDataset
os.makedirs("data", exist_ok=True)

import ast
import json
import random
from datasets import load_dataset

# ==================== 配置 ====================
MAX_SAMPLES = 300            # 目标提取数量
MIN_LINES = 8                # 最少代码行数
MAX_LINES = 50               # 最多代码行数
MIN_CHARS = 50               # 最少字符数
OUTPUT_FILE = "data/code_completion_dataset.json"

# ==================== 辅助函数 ====================
def is_valid_code(code):
    """初步筛选：检查代码片段的基本特征"""
    if len(code) < MIN_CHARS:
        return False
    
    lines = code.strip().split('\n')
    if len(lines) < MIN_LINES or len(lines) > MAX_LINES:
        return False
    
    # 过滤纯注释或纯空行的代码
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
    if len(code_lines) < 3:
        return False
    
    # 过滤包含非ASCII字符过多的代码（可能是乱码）
    non_ascii = sum(1 for c in code if ord(c) > 127)
    if non_ascii > len(code) * 0.1:
        return False
    
    return True

def is_valid_python(code):
    """检查代码是否为有效的 Python 语法"""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False

def create_fim_pair(code):
    """
    将完整代码转为代码补全训练对（FIM格式）
    策略：随机截断，前半作为 input，后半作为 output
    返回 None 如果生成失败或语法错误
    """
    lines = code.strip().split('\n')
    total = len(lines)
    
    # 随机选择截断点（保留30%-70%作为前缀）
    cut_ratio = random.uniform(0.3, 0.7)
    cut_point = max(2, int(total * cut_ratio))
    
    prefix = '\n'.join(lines[:cut_point])
    suffix = '\n'.join(lines[cut_point:])
    
    # 后缀太少行，无法构成有效补全
    if len(suffix.strip().split('\n')) < 2:
        return None
    
    # 拼接完整代码并检查语法
    full_code = prefix + "\n" + suffix
    if not is_valid_python(full_code):
        return None  # 语法错误，丢弃
    
    return {
        "instruction": "补全以下Python代码，保持代码风格一致",
        "input": prefix,
        "output": suffix
    }

# ==================== 主流程 ====================
def main():
    print("正在加载 MsDataset codefuse-ai 数据集（CodeExercise-Python-27k）...")
    # 无法下载：需要HuggingFace授权的“门控数据集”
    # dataset = load_dataset("bigcode/the-stack", data_dir="data/python", split="train", streaming=True)
    dataset = MsDataset.load("codefuse-ai/CodeExercise-Python-27k", split="train")
    
    dataset_list = []
    print(f"开始提取，目标: {MAX_SAMPLES} 条...")
    
    for i, item in enumerate(dataset):
        if len(dataset_list) >= MAX_SAMPLES:
            break
        
        code = item.get("content", "")
        if not is_valid_code(code):
            continue
        
        pair = create_fim_pair(code)
        if pair:
            dataset_list.append(pair)
        
        if (i + 1) % 1000 == 0:
            print(f"  已处理 {i+1} 条原始代码，有效补全对 {len(dataset_list)} 条")
    
    # 保存
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(dataset_list, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据集已生成: {OUTPUT_FILE}")
    print(f"   总样本数: {len(dataset_list)} 条")
    if dataset_list:
        print(f"   示例 input: {dataset_list[0]['input'][:80]}...")
        print(f"   示例 output: {dataset_list[0]['output'][:80]}...")

if __name__ == "__main__":
    main()