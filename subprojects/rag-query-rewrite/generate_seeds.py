# 第1步 转换 生成（alpaca 格式）数据集
# generate_seeds.py
import json

seeds = [
    # 指代不明
    {"instruction": "", "input": "那个蓝色的怎么卖？", "output": ""},
    {"instruction": "", "input": "它和之前那个比哪个好？", "output": ""},
    {"instruction": "", "input": "这个能便宜点吗？", "output": ""},
    {"instruction": "", "input": "上次那个还有货吗？", "output": ""},
    
    # 用词模糊
    {"instruction": "", "input": "最近有什么新上的？", "output": ""},
    {"instruction": "", "input": "那种大容量的有吗？", "output": ""},
    {"instruction": "", "input": "有没有更高级的版本？", "output": ""},
    {"instruction": "", "input": "这个系列最好的型号是什么？", "output": ""},
    
    # 信息缺失
    {"instruction": "", "input": "最新款多少钱？", "output": ""},
    {"instruction": "", "input": "能不能分期？", "output": ""},
    {"instruction": "", "input": "保修多久？", "output": ""},
    {"instruction": "", "input": "有现货吗？", "output": ""},
    
    # 口语化严重
    {"instruction": "", "input": "有没有那种不用插电就能用的？", "output": ""},
    {"instruction": "", "input": "给我来个最耐用的那种", "output": ""},
    {"instruction": "", "input": "你们这儿能定制不？", "output": ""},
    {"instruction": "", "input": "那个贼好用的清洁剂还有吗？", "output": ""},
    
    # 多意图混合
    {"instruction": "", "input": "帮我查一下订单还有那个物流", "output": ""},
    {"instruction": "", "input": "这个能退吗还有换货怎么弄", "output": ""},
    {"instruction": "", "input": "对比一下这个和那个的价格和功能", "output": ""},
    {"instruction": "", "input": "上次买的那个质量不行换个牌子有没有推荐", "output": ""}
]

with open("data/query_rewrite_seeds.json", "w", encoding="utf-8") as f:
    json.dump(seeds, f, ensure_ascii=False, indent=2)

print(f"已生成 {len(seeds)} 个种子问题")