# 第3步：质量检查
# python3 << 'EOF'
import json

with open("data/code_completion_dataset.json", "r") as f:
    data = json.load(f)

print(f"总样本数: {len(data)}")

# 检查空值
empty_input = [d for d in data if not d["input"].strip()]
empty_output = [d for d in data if not d["output"].strip()]
print(f"空input: {len(empty_input)} 条")
print(f"空output: {len(empty_output)} 条")

# 检查input/output比例
for i, d in enumerate(data[:5]):
    in_lines = len(d["input"].split("\n"))
    out_lines = len(d["output"].split("\n"))
    print(f"样本{i}: input={in_lines}行, output={out_lines}行")

# 检查重复
inputs = [d["input"] for d in data]
duplicates = len(inputs) - len(set(inputs))
print(f"重复input: {duplicates} 条")

# 统计代码特征
total_in_lines = sum(len(d["input"].split("\n")) for d in data)
total_out_lines = sum(len(d["output"].split("\n")) for d in data)
print(f"\ninput 平均行数: {total_in_lines/len(data):.1f}")
print(f"output 平均行数: {total_out_lines/len(data):.1f}")
# EOF