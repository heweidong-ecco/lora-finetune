# 用 matplotlib 画长度分布直方图
#!/usr/bin/env python3
"""数据集长度分布可视化"""
import json
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# 设置中文字体（解决中文显示为方框的问题）
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

def load_dataset(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def plot_length_distribution(data, save_path="length_distribution.png"):
    """
    绘制 instruction 和 output 的长度分布直方图
    """
    # 提取长度
    inst_lengths = [len(item.get("instruction", "")) for item in data]
    out_lengths = [len(item.get("output", "")) for item in data]
    
    # 创建画布：1行2列
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # ---- 左图：instruction 长度分布 ----
    ax1 = axes[0]
    ax1.hist(inst_lengths, bins=30, color='#4ECDC4', edgecolor='white', alpha=0.8)
    ax1.axvline(np.mean(inst_lengths), color='red', linestyle='--', 
                label=f'均值: {np.mean(inst_lengths):.0f} 字符')
    ax1.axvline(np.median(inst_lengths), color='orange', linestyle='--', 
                label=f'中位数: {np.median(inst_lengths):.0f} 字符')
    ax1.set_title('Instruction 长度分布', fontsize=14, fontweight='bold')
    ax1.set_xlabel('字符数', fontsize=12)
    ax1.set_ylabel('样本数量', fontsize=12)
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', alpha=0.3)
    
    # ---- 右图：output 长度分布 ----
    ax2 = axes[1]
    ax2.hist(out_lengths, bins=30, color='#FF6B6B', edgecolor='white', alpha=0.8)
    ax2.axvline(np.mean(out_lengths), color='red', linestyle='--', 
                label=f'均值: {np.mean(out_lengths):.0f} 字符')
    ax2.axvline(np.median(out_lengths), color='orange', linestyle='--', 
                label=f'中位数: {np.median(out_lengths):.0f} 字符')
    ax2.set_title('Output 长度分布', fontsize=14, fontweight='bold')
    ax2.set_xlabel('字符数', fontsize=12)
    ax2.set_ylabel('样本数量', fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(axis='y', alpha=0.3)
    
    # 总标题
    fig.suptitle(f'数据集长度分布分析（总样本数: {len(data)}）', 
                 fontsize=16, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"图表已保存至: {save_path}")
    
    # 输出统计摘要
    print(f"""
========================================
  长度分布统计摘要
========================================
Instruction:
  - 均值: {np.mean(inst_lengths):.1f} 字符
  - 中位数: {np.median(inst_lengths):.1f} 字符
  - 最小值: {np.min(inst_lengths)} 字符
  - 最大值: {np.max(inst_lengths)} 字符
  - 标准差: {np.std(inst_lengths):.1f}

Output:
  - 均值: {np.mean(out_lengths):.1f} 字符
  - 中位数: {np.median(out_lengths):.1f} 字符
  - 最小值: {np.min(out_lengths)} 字符
  - 最大值: {np.max(out_lengths)} 字符
  - 标准差: {np.std(out_lengths):.1f}
========================================
""")

def analyze_distribution(data):
    """
    判断数据分布是否合理
    """
    inst_lengths = [len(item.get("instruction", "")) for item in data]
    out_lengths = [len(item.get("output", "")) for item in data]
    
    issues = []
    
    # 检查1：instruction 不能太短
    short_inst = sum(1 for x in inst_lengths if x < 5)
    if short_inst > len(data) * 0.05:
        issues.append(f"⚠️ {short_inst}条({short_inst/len(data)*100:.1f}%) instruction 过短 (< 5字符)")
    
    # 检查2：output 不能太短
    short_out = sum(1 for x in out_lengths if x < 10)
    if short_out > len(data) * 0.05:
        issues.append(f"⚠️ {short_out}条({short_out/len(data)*100:.1f}%) output 过短 (< 10字符)")
    
    # 检查3：长度方差不能太大（数据质量不稳定）
    if np.std(inst_lengths) > np.mean(inst_lengths):
        issues.append(f"⚠️ instruction 长度标准差过大 ({np.std(inst_lengths):.0f})，数据质量可能不稳定")
    
    if not issues:
        print("✅ 数据长度分布合理，没有发现明显问题。")
    else:
        for issue in issues:
            print(issue)

def main():
    filepath = "/root/autodl-fs/LLaMA-Factory/data/my_dataset.json"
    data = load_dataset(filepath)
    print(f"已加载 {len(data)} 条数据\n")
    
    plot_length_distribution(data, save_path="/root/autodl-fs/LLaMA-Factory/length_distribution.png")
    analyze_distribution(data)

if __name__ == "__main__":
    main()

'''
如何看图判断数据是否合理：
现象	                        含义   处理建议
直方图接近正态分布（中间高两边低）	✅     理想状态，数据多样性好	无需处理
有两个明显的峰（双峰分布）	       ⚠️     数据可能来自两个不同来源	检查来源，确认是否都需要
instruction 大部分 < 5 字符	     ❌     问题太短，模型学不到规律	补充更详细的问题
output 有大量 > 1000 字符的	     ⚠️     少数超长样本可能影响训练稳定性	考虑截断或单独处理
长尾严重（少数极长，多数极短）      ⚠️     数据分布不均	对过长的做截断处理
'''