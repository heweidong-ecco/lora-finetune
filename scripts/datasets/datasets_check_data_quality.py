#!/usr/bin/env python3
# 数据质量检查脚本
"""数据集质量检查脚本"""
import json
import re
from collections import Counter

def load_dataset(filepath):
    """加载 JSON 格式数据集"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def check_empty_fields(data):
    """检查空值：instruction / output 是否为空"""
    issues = []
    for i, item in enumerate(data):
        if not item.get("instruction", "").strip():
            issues.append(f"[空值] 第{i}条: instruction 为空")
        if not item.get("output", "").strip():
            issues.append(f"[空值] 第{i}条: output 为空")
    return issues

def check_length(data, min_inst=5, max_inst=500, min_out=10, max_out=2000):
    """检查异常长度"""
    issues = []
    for i, item in enumerate(data):
        inst_len = len(item.get("instruction", ""))
        out_len = len(item.get("output", ""))
        
        if inst_len < min_inst:
            issues.append(f"[长度] 第{i}条: instruction 过短 ({inst_len}字符)")
        if inst_len > max_inst:
            issues.append(f"[长度] 第{i}条: instruction 过长 ({inst_len}字符)")
        if out_len < min_out:
            issues.append(f"[长度] 第{i}条: output 过短 ({out_len}字符)")
        if out_len > max_out:
            issues.append(f"[长度] 第{i}条: output 过长 ({out_len}字符)")
    return issues

def check_format(data):
    """检查格式：字段是否完整、input 是否存在"""
    issues = []
    required_fields = ["instruction", "output"]
    optional_fields = ["input"]
    
    for i, item in enumerate(data):
        # 检查必要字段
        for field in required_fields:
            if field not in item:
                issues.append(f"[格式] 第{i}条: 缺少必要字段 '{field}'")
        
        # 检查可选字段
        for field in optional_fields:
            if field not in item:
                issues.append(f"[格式] 第{i}条: 缺少可选字段 '{field}'，已自动补充")
                item[field] = ""
    
    return issues

def check_duplicates(data):
    """检查重复数据"""
    issues = []
    seen = {}
    for i, item in enumerate(data):
        key = item.get("instruction", "") + "|||" + item.get("output", "")
        if key in seen:
            issues.append(f"[重复] 第{i}条 与 第{seen[key]}条 内容重复")
        else:
            seen[key] = i
    return issues

def check_special_chars(data):
    """检查特殊字符和乱码"""
    issues = []
    # 检测常见的乱码模式
    garbled_patterns = [
        r'[□■◆◇○●]',  # 替换字符
        r'[\x00-\x08\x0b\x0c\x0e-\x1f]',  # 控制字符
    ]
    
    for i, item in enumerate(data):
        text = item.get("instruction", "") + item.get("output", "")
        for pattern in garbled_patterns:
            if re.search(pattern, text):
                issues.append(f"[乱码] 第{i}条: 检测到异常字符 (模式: {pattern})")
                break
    return issues

def generate_report(data, issues_by_type):
    """生成质量报告"""
    total = len(data)
    total_issues = sum(len(v) for v in issues_by_type.values())
    
    # 统计字段长度分布
    inst_lengths = [len(item.get("instruction", "")) for item in data]
    out_lengths = [len(item.get("output", "")) for item in data]
    
    # 统计 input 非空比例
    has_input = sum(1 for item in data if item.get("input", "").strip())
    
    report = f"""
========================================
  数据集质量检查报告
========================================
基本信息:
  - 总样本数: {total}
  - 总问题数: {total_issues}
  - 问题样本比例: {total_issues/total*100:.1f}%

字段统计:
  - instruction 平均长度: {sum(inst_lengths)/total:.1f} 字符
  - output 平均长度: {sum(out_lengths)/total:.1f} 字符
  - 含 input 上下文的样本: {has_input}/{total} ({has_input/total*100:.1f}%)

各类型问题数:
"""
    for check_type, issues in issues_by_type.items():
        report += f"  - {check_type}: {len(issues)} 个\n"
    
    report += f"\n详细问题列表（前20条）:\n"
    report += "-" * 40 + "\n"
    
    all_issues = []
    for issues in issues_by_type.values():
        all_issues.extend(issues)
    
    for issue in all_issues[:20]:
        report += f"  {issue}\n"
    
    report += "\n========================================\n"
    
    return report

def main():
    # 加载数据集
    filepath = "/root/autodl-fs/LLaMA-Factory/data/my_dataset.json"
    data = load_dataset(filepath)
    print(f"已加载 {len(data)} 条数据，开始质量检查...\n")
    
    # 执行各项检查
    issues_by_type = {
        "空值检查": check_empty_fields(data),
        "长度检查": check_length(data),
        "格式检查": check_format(data),
        "重复检查": check_duplicates(data),
        "乱码检查": check_special_chars(data),
    }
    
    # 生成报告
    report = generate_report(data, issues_by_type)
    print(report)
    
    # 保存报告
    with open("/root/autodl-fs/LLaMA-Factory/data_quality_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("报告已保存至: data_quality_report.txt")
    
    # 判断是否达标
    total_issues = sum(len(v) for v in issues_by_type.values())
    if total_issues == 0:
        print("✅ 数据集质量检查全部通过！可以开始训练。")
    elif total_issues < len(data) * 0.05:
        print(f"⚠️ 存在少量问题，建议修复后训练。")
    else:
        print(f"❌ 问题较多，建议先清理数据再训练。")

if __name__ == "__main__":
    main()

'''
数据集的质量标准
指标	               达标线	    优秀线
空值率	               < 1%	       0%
重复率	               < 3%	       0%
格式错误率	            < 1%	    0%
instruction 平均长度	> 10 字符	> 20 字符
output 平均长度	        > 30 字符	> 50 字符
乱码/异常字符	         0	        0
'''