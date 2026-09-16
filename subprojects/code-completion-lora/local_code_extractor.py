# 从本地 Python 库提取代码片段，构建代码补全微调数据集
# 不依赖任何外部下载，直接读取已安装库的源码
#!/usr/bin/env python3
"""
备选方案：从本地 Python 库提取代码片段，构建代码补全微调数据集
不依赖任何外部下载，直接读取已安装库的源码
"""

import ast
import json
import os
import random
import sys

# ==================== 配置 ====================
MAX_SAMPLES = 250            # 目标提取数量
MIN_LINES = 6                # 最少代码行数（函数/类体）
MAX_LINES = 40               # 最多代码行数
OUTPUT_FILE = "data/code_completion_dataset.json"

# ==================== 辅助函数 ====================
def is_valid_python(code):
    """检查代码是否为有效的 Python 语法"""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False

def extract_functions_and_classes(source_code):
    """从 Python 源码中提取所有函数和类定义"""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []
    
    items = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            # 获取节点的行号范围
            start_line = node.lineno
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 10
            
            lines = source_code.split('\n')
            # 提取函数/类定义及其全部体
            if start_line <= len(lines) and end_line <= len(lines):
                code = '\n'.join(lines[start_line-1:end_line])
                if MIN_LINES <= len(code.strip().split('\n')) <= MAX_LINES:
                    items.append(code)
    return items

def create_fim_pair(code):
    """将完整代码块转为代码补全训练对"""
    lines = code.strip().split('\n')
    total = len(lines)
    if total < MIN_LINES:
        return None
    
    # 保留函数/类签名（第一行），从函数体内部随机截断
    # 确保 input 至少包含签名行
    if total <= 3:
        return None
    
    # 截断点：保留签名的前几行和部分体
    cut_ratio = random.uniform(0.2, 0.6)
    cut_point = max(2, int(total * cut_ratio))
    
    prefix = '\n'.join(lines[:cut_point])
    suffix = '\n'.join(lines[cut_point:])
    
    if len(suffix.strip().split('\n')) < 2:
        return None
    
    # 拼接并检查语法
    full_code = prefix + "\n" + suffix
    if not is_valid_python(full_code):
        return None
    
    return {
        "instruction": "补全以下Python代码，保持代码风格一致",
        "input": prefix,
        "output": suffix
    }

# ==================== 主流程 ====================
def main():
    # 获取 site-packages 路径
    site_packages = [p for p in sys.path if 'site-packages' in p]
    if not site_packages:
        print("未找到 site-packages，使用当前目录作为源码路径")
        site_packages = ["/usr/lib/python3", "/root/autodl-fs"]
    
    print(f"搜索目录: {site_packages[:3]}...")
    
    # 收集所有 .py 文件
    py_files = []
    for base_dir in site_packages[:3]:  # 只搜索前3个目录，避免文件太多
        for root, dirs, files in os.walk(base_dir):
            # 跳过隐藏目录和测试目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and 'test' not in d.lower()]
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    py_files.append(os.path.join(root, file))
    
    print(f"找到 {len(py_files)} 个 Python 文件")
    
    # 随机打乱
    random.shuffle(py_files)
    
    # 提取代码块
    all_items = []
    for py_file in py_files:
        if len(all_items) >= MAX_SAMPLES * 3:  # 多收集一些，后续过滤
            break
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                source = f.read()
            items = extract_functions_and_classes(source)
            all_items.extend(items)
        except:
            continue
    
    print(f"提取到 {len(all_items)} 个函数/类定义")
    
    # 生成补全对
    dataset = []
    for code in all_items:
        pair = create_fim_pair(code)
        if pair:
            dataset.append(pair)
            if len(dataset) >= MAX_SAMPLES:
                break
    
    # 保存
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据集已生成: {OUTPUT_FILE}")
    print(f"   总样本数: {len(dataset)} 条")
    if dataset:
        print(f"   示例 input: {dataset[0]['input'][:80]}...")
        print(f"   示例 output: {dataset[0]['output'][:80]}...")

if __name__ == "__main__":
    main()