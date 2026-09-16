# 第3步：质量检查
# 对 生成的改写内容 进行 质量检查
'''
常见问题处理
问题	原因	解决方案
生成的改写版本少于3个	大模型输出格式不稳定	减少生成版本数到2个，或多次调用
改写和原文完全相同	temperature 太低，模型太保守	提高 temperature 到 0.9-1.0
改写后完全偏离原意	temperature 太高，模型太发散	降低 temperature 到 0.5-0.7
output 为空	模型输出被截断或格式异常	重试该条数据
'''
# python3 << 'EOF'...EOF
# 
import json

with open("data/query_rewrite_dataset.json", "r") as f:
    data = json.load(f)

print(f"总样本数: {len(data)}")

# 检查空值
empty_output = [d for d in data if not d["output"].strip()]
print(f"空output: {len(empty_output)} 条")

# 检查重复
seen = set()
duplicates = []
for d in data:
    key = d["input"] + "|||" + d["output"]
    if key in seen:
        duplicates.append(d)
    seen.add(key)
print(f"完全重复: {len(duplicates)} 条")

# 检查改写后是否和原文相同
unchanged = [d for d in data if d["input"].strip() == d["output"].strip()]
print(f"改写后未变化: {len(unchanged)} 条")

# 统计长度
input_lengths = [len(d["input"]) for d in data]
output_lengths = [len(d["output"]) for d in data]
print(f"\ninput 平均长度: {sum(input_lengths)/len(input_lengths):.0f} 字符")
print(f"output 平均长度: {sum(output_lengths)/len(output_lengths):.0f} 字符")
print(f"改写平均增加了 {sum(output_lengths)/len(output_lengths) - sum(input_lengths)/len(input_lengths):.0f} 字符")

# 质量判断
if len(data) >= 100 and len(empty_output) == 0 and len(unchanged) < len(data) * 0.1:
    print("\n✅ 数据集质量合格，可以用于微调")
else:
    print("\n⚠️ 数据集需要进一步清洗")

