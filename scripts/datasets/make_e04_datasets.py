#!/usr/bin/env python3
"""
E04 用数据集准备 —— 构造**同源、同语言、同条数**的两组数据。

为什么这样设计（**这是本脚本存在的理由**）
--------------------------------------------
E04 的目的是检验「**数据质量 ≫ 超参数**」。要能归因，两组之间**只能有一个变量**。

早先的设计（A=alpaca 抽 194 ／ B=qa-general 194）**不成立** ——
实测两组同时在三个维度上不同：

| | 来源 | 语言 | 数据质量 |
|---|---|---|---|
| A（alpaca） | alpaca-cleaned | **0% 中文** | ？ |
| B（qa-general） | 开源 + 模型生成 | **48% 中文** | ？ |

→ **即使跑出差异，也分不清是哪一个造成的。**

现在的设计：**唯一变量 = 抽样代表性**

| | 来源 | 语言 | 条数 | 抽样方式 |
|---|---|---|---|---|
| **A 组** | `yahma/alpaca-cleaned` | 英文 | 194 | 从**全部 51760 条**随机抽 |
| **B 组** | `yahma/alpaca-cleaned` | 英文 | 194 | 从**前 550 条**那个区块里抽 |

B 组取的是**前 550 条**——正是 `datasets/数据卡-alpaca500.md` §五-1 实测出
**`instruction` 均长偏出总体 +31%** 的那个区块。
👉 所以这组实验**同时在验证那个抽样偏倚到底有没有实际影响**。

前置数据
--------
需要一个含**全部 51760 条**的合法 JSON 数组文件（默认 `datasets_open_source_data_cleaned.json`）。

⚠️ **该文件不在仓库里**（42 MB）。生成方式：

    export HF_ENDPOINT=https://hf-mirror.com
    python scripts/datasets/datasets_open_source_data.py      # → datasets_open_source_data.json
    # 把 datasets_clean_json.py 里的 max_samples 改成 None，再跑：
    python scripts/datasets/datasets_clean_json.py            # → datasets_open_source_data_cleaned.json

用法
----
    python scripts/datasets/make_e04_datasets.py [--full <路径>] [--seed 42]

产出
----
    datasets/alpaca-clean-500条/E04-A组-194条.json
    datasets/alpaca-clean-500条/E04-B组-194条.json

确定性：固定种子，**同输入必得同输出**，可逐条复算。
"""

import argparse
import json
import os
import random
import sys

SEED = 42
N = 194            # 两组都必须 194 —— 条数相同是设计要点
B_BLOCK = 550      # B 组从「前 550 条」里抽（即数据卡里实测偏 +31% 的那个区块）
DEFAULT_FULL = "datasets_open_source_data_cleaned.json"
OUT_DIR = "datasets/alpaca-clean-500条"
FIELDS = ("instruction", "input", "output")


def load_full(path):
    if not os.path.exists(path):
        print(f"❌ 找不到全量数据文件：{path}")
        print()
        print("   该文件约 42 MB，**不在仓库里**。生成方式见本脚本文件头的『前置数据』一节。")
        print("   生成后放到仓库根目录，或加参数 --full <路径> 指定位置。")
        return None
    d = json.load(open(path, encoding="utf-8"))
    if not isinstance(d, list):
        print(f"❌ 该文件不是 JSON 数组（读到 {type(d).__name__}）—— 请确认用的是 `_cleaned` 那份")
        return None
    print(f"✅ 全量数据：{path}（{len(d)} 条）")
    return d


def norm(items):
    return [{k: x.get(k, "") for k in FIELDS} for x in items]


def main():
    ap = argparse.ArgumentParser(description="构造 E04 的两组数据（同源同语言同条数）")
    ap.add_argument("--full", default=DEFAULT_FULL, help=f"全量 JSON（默认 {DEFAULT_FULL}）")
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    full = load_full(args.full)
    if full is None:
        return 1
    if len(full) < B_BLOCK:
        print(f"❌ 全量只有 {len(full)} 条，不足 {B_BLOCK} 条，B 组无法构造")
        return 1

    os.makedirs(OUT_DIR, exist_ok=True)

    # A 组：从全部里随机抽
    random.seed(args.seed)
    a = random.sample(norm(full), N)

    # B 组：从「前 550 条」那个区块里抽（先取区块，再抽；种子同 A）
    block = norm(full[:B_BLOCK])
    random.seed(args.seed)
    b = random.sample(block, N)

    pa = os.path.join(OUT_DIR, "E04-A组-194条.json")
    pb = os.path.join(OUT_DIR, "E04-B组-194条.json")
    for p, d in ((pa, a), (pb, b)):
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        print(f"✅ 已生成：{p}（{len(d)} 条）")

    # ── 自检：设计要点是否成立 ──
    print()
    print("自检：")
    ok = True
    if len(a) != len(b) != N:
        print(f"  ⛔ 条数不等：A={len(a)} B={len(b)}"); ok = False
    else:
        print(f"  ✅ 条数相同：各 {N} 条")

    # A 与 B 的重合度（都是同一来源，重合是正常的；完全重合则说明抽错了）
    ka = {json.dumps(x, sort_keys=True, ensure_ascii=False) for x in a}
    kb = {json.dumps(x, sort_keys=True, ensure_ascii=False) for x in b}
    overlap = len(ka & kb)
    print(f"  ℹ️ A∩B 重合 {overlap} / {N} 条（同源，重合属正常）")
    if overlap == N:
        print("  ⛔ 两组完全相同 —— 抽样出了问题，不要拿去跑实验"); ok = False

    # 分布差异（这才是本实验的「自变量」所在）
    import statistics as st
    la = st.mean(len(x["instruction"]) for x in a)
    lb = st.mean(len(x["instruction"]) for x in b)
    print(f"  ℹ️ instruction 均长：A={la:.1f}  B={lb:.1f}  （B 来自有偏区块，应明显更长）")

    print()
    print("  ✅ 设计与自检通过" if ok else "  ⛔ 自检未通过")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
