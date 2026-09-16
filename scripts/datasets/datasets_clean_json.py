"""
清洗 Alpaca 格式的训练数据 JSON 文件
支持：
- 文件中包含多个 JSON 对象（非数组）
- 文件中有额外文字或注释
- 多条数据连在一起
- 缺失字段自动补全

用法：将需要清洗的文件路径写在脚本末尾的 files_to_clean 列表中，直接运行即可。
清洗后文件会保存为 原文件名_cleaned.json
"""

import json
import os
import random

def load_json_objects_strict(filepath):
    """
    尽可能加载文件中的 JSON 对象，返回包含所有对象的列表。
    如果文件本身是合法的 JSON 数组，直接返回该数组。
    否则使用 raw_decode 逐个解析对象。
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if not content.strip():
        return []

    # 先尝试直接解析为 JSON 数组
    try:
        data = json.loads(content)
        if isinstance(data, list):
            # 已经是数组，检查每个元素是否为字典
            return [item for item in data if isinstance(item, dict)]
        elif isinstance(data, dict):
            # 单个对象，包装成列表
            return [data]
    except json.JSONDecodeError:
        pass

    # 如果直接解析失败，使用 raw_decode 逐个提取
    objects = []
    decoder = json.JSONDecoder()
    idx = 0
    while idx < len(content):
        # 跳过空白字符
        while idx < len(content) and content[idx].isspace():
            idx += 1
        if idx >= len(content):
            break
        try:
            obj, idx = decoder.raw_decode(content, idx)
            if isinstance(obj, dict):
                objects.append(obj)
            elif isinstance(obj, list):
                objects.extend([item for item in obj if isinstance(item, dict)])
        except json.JSONDecodeError:
            # 跳过无法解析的部分，移动到下一个字符
            idx += 1
    return objects

def clean_entry(entry):
    """确保每个数据条目都有 instruction, input, output 三个字段"""
    if not isinstance(entry, dict):
        return None
    # 保留需要的字段，缺失的设为空字符串
    cleaned = {
        "instruction": str(entry.get("instruction", entry.get("question", ""))).strip(),
        "input": str(entry.get("input", "")).strip(),
        "output": str(entry.get("output", entry.get("answer", ""))).strip()
    }
    # 如果 instruction 和 output 都为空，视为无效数据
    if not cleaned["instruction"] and not cleaned["output"]:
        return None
    return cleaned

def clean_json_file(filepath, output_path=None, max_samples=None):
    """
    清洗单个 JSON 文件
    """
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return

    print(f"🧹 正在清洗: {filepath}")
    raw_objects = load_json_objects_strict(filepath)
    cleaned_objects = []
    for obj in raw_objects:
        cleaned = clean_entry(obj)
        if cleaned:
            cleaned_objects.append(cleaned)
    print(f"   有效条目: {len(cleaned_objects)} (原始对象数: {len(raw_objects)})")
    
    # 如果指定了 max_samples，随机抽取
    if max_samples and len(cleaned_objects) > max_samples:
        cleaned_objects = random.sample(cleaned_objects, max_samples)  # 随机
        # 或者 cleaned_objects = cleaned_objects[:max_samples]         # 顺序取前N条
    # ... 写入文件 ...
        print(f"   随机抽取 {max_samples} 条")
    
    # 生成输出文件名
    if output_path is None:
        base, ext = os.path.splitext(filepath)
        if max_samples is not None:
            output_path = f"{base}_cleaned_{max_samples}{ext}"
        else:
            output_path = f"{base}_cleaned{ext}"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_objects, f, ensure_ascii=False, indent=2)

    print(f"   已保存至: {output_path}")

if __name__ == "__main__":
    # ========== 配置区 ==========
    files_to_clean = [
        "datasets_open_source_data.json",
        "datasets_generated_data.json"
    ]
    max_samples = 100  # 设置为 None 则不抽取，保留全部
    print(f"max_samples = {max_samples}")
    # ============================

    for f in files_to_clean:
        clean_json_file(f, max_samples=max_samples)
        print()