#!/usr/bin/env python3
"""
E04 用数据集准备 —— 从 alpaca-clean-500条 里确定性地抽 194 条。

为什么需要这个脚本
------------------
E04 的自变量是「数据集」，所以两组的**条数必须相同**（都 194）。
否则 194 vs 500 会把「数据内容」和「数据条数」两个变量混在一起，归因不成立。

`qa-general-194条/my_dataset.json` 本来就是 194 条，直接用。
`alpaca-clean-500条/my_dataset.json` 是 500 条，需要抽 194 条 —— 本脚本做这件事。

确定性
------
用固定种子（SEED = 42），**同输入必得同输出**，别人可以逐条复算。

用法
----
    python scripts/datasets/make_e04_datasets.py
    # → datasets/alpaca-clean-500条/E04-A组-194条.json
"""

import json
import os
import random
import sys

SEED = 42
N = 194                       # 与 qa-general-194条 的条数一致 —— 这是本实验的设计要点
SRC = "datasets/alpaca-clean-500条/my_dataset.json"
DST = "datasets/alpaca-clean-500条/E04-A组-194条.json"


def main():
    if not os.path.exists(SRC):
        print(f"❌ 找不到源文件：{SRC}")
        print("   请先确认当前目录是仓库根目录（lora-finetune/）")
        return 1

    with open(SRC, encoding="utf-8") as f:
        pool = json.load(f)

    if len(pool) < N:
        print(f"❌ 源文件只有 {len(pool)} 条，不够抽 {N} 条")
        return 1

    print(f"源文件：{SRC}")
    print(f"  池子 {len(pool)} 条 → 抽 {N} 条（seed={SEED}）")

    random.seed(SEED)
    subset = random.sample(pool, N)
    # 保持与源文件一致的字段顺序，便于人眼比对
    subset = [{k: x.get(k, "") for k in ("instruction", "input", "output")} for x in subset]

    with open(DST, "w", encoding="utf-8") as f:
        json.dump(subset, f, ensure_ascii=False, indent=2)

    print(f"✅ 已生成：{DST}（{len(subset)} 条）")
    print()
    print("自检：")
    print(f"  A 组条数 = {len(subset)}")
    with open("datasets/qa-general-194条/my_dataset.json", encoding="utf-8") as f:
        b = json.load(f)
    print(f"  B 组条数 = {len(b)}")
    print(f"  条数相同 = {'✅' if len(subset) == len(b) else '⛔ 不满足实验设计，请检查'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
