# datasets/ · 数据集索引

> **这是一个「库」，不是一个项目。** 一个数据集 = 一个子目录，自带数据卡和数据文件。
> **以后有新的 LoRA 数据进来，就往下加一个目录，不改动已有的。**
> 建立：2026-09-16

---

## 一 · 数据集总索引

| 数据集 | 条数 | 来源 | 许可证 | 用于 |
|---|---|---|---|---|
| [`alpaca-clean-500条/`](alpaca-clean-500条/) | **500 + 50** | `yahma/alpaca-cleaned` 前 550 条切分 | `CC BY-NC 4.0` | ⭐ `experiments/` 里 E01–E03 的训练；基座 vs 微调 对比评测 |
| [`qa-general-194条/`](qa-general-194条/) | **194** | 开源 100 条 + 本地 Ollama `qwen3:8b` 生成 94 条 | 混采（见数据卡） | 数据集工程实验（造 / 洗 / 合并 / 质检） |
| [`code-completion代码补全/`](code-completion代码补全/) | **250** | Python 代码提取 —— ⚠️ **来源未记录**（回忆指向本机依赖，未确认） | ⚠️ 待确认 | `subprojects/code-completion-lora/` 的代码补全微调 |

> ⚠️ **两个数据集都含一个叫 `my_dataset.json` 的文件，但不是同一个东西。**
> 这是 2026-09-16 整理历史文件时发现的坑。**看目录名，别只看文件名。**

### 派生数据（E04 用的两组）

`alpaca-clean-500条/` 里另有两份**从它派生**的 194 条数据：

| 文件 | 怎么来的 |
|---|---|
| `E04-A组-194条.json` | 从**全部 51760 条**随机抽 194 条 |
| `E04-B组-194条.json` | 从**前 550 条**那个区块抽 194 条 |

由 `scripts/datasets/make_e04_datasets.py` **固定种子**生成，已验证两次跑 MD5 一致。
用途见 `../experiments/E04-数据集对照.md`。**它们不是独立的数据集，故不单独建目录。**

---

## 二 · 每个数据集目录里应该有什么

```
<数据集名>/
├── 数据卡-<简称>.md       ← 必填。按 ../template数据卡.md 写
└── <数据文件>              ← 清洗后的数据（原始数据视许可决定是否入库）
```

**数据卡是本目录的重心** —— 它要细到能解释「为什么这份数据有效」。
模板见 [`../template数据卡.md`](../template数据卡.md)。

---

## 三 · 新数据集进来时怎么做

1. **在 `datasets/` 下建目录**，命名按本仓库采用的规范 ①：
   **英文功能词 + 中文释义**，需要时用 `-` 接限定词
   （例：`alpaca-clean-500条/` · `qa-general-194条/` · `code-completion代码补全/`）
2. **从 `../template数据卡.md` 复制一份数据卡**，填完 —— **尤其不能空着 §五「已知缺陷」**
3. **在本文件 §一 的表里登记一行**
4. **原始数据**：来源可公开且体积小的可入库；否则**放下载脚本 + 数据卡**（见 §四）
5. 若有对应的训练实验，在 `experiments/` 里建记录并**指回本数据集目录名**

---

## 四 · ⚠️ 没有进仓库的数据

| 文件 | 体积 | 为什么不在 |
|---|---|---|
| `datasets_open_source_data.json` | 42 MB | 一行脚本即可重新下载；且**不是合法 JSON**（51760 个对象直接拼接） |
| `datasets_open_source_data_cleaned.json` | 42 MB | 同上 |
| `code-completion代码补全/code_completion_dataset.json` | 187 KB | **主动撤出**：来源未确认，含混合第三方许可风险（见其数据卡 §五-3） |

**重新获取**：`python scripts/datasets/datasets_open_source_data.py`
（需先 `export HF_ENDPOINT=https://hf-mirror.com`）

---

## 五 · 许可证汇总

| 数据集 | 许可证 | 限制 |
|---|---|---|
| alpaca-clean-500条 | **`CC BY-NC 4.0`** | ⛔ **非商用**。数据集卡原文：*「用该数据集训出的模型不应超出研究用途」* |
| qa-general-194条 | 混采：开源部分 `CC BY-NC 4.0` + 本地生成部分自建 | 见其数据卡 §一 |
| code-completion代码补全 | ⚠️ **待确认** | 取决于实际来源（ModelScope 数据集 / 本地库），见其数据卡 |

> ⛔ **不要把 alpaca-cleaned 的许可证写成 "Apache-2.0"** ——
> 那是**配套代码**的许可，**不是数据本身**的。

---

## 六 · 数据血缘

两条独立的数据线（详见各数据卡）：

```
【qa-general-194条】
  yahma/alpaca-cleaned (51760)
      └─ datasets_open_source_data.py → datasets_clean_json.py(max_samples=100) → 开源 100 条 ┐
  本地 Ollama qwen3:8b                                                                        ├─ datasets_merge_script.py
      └─ datasets_generated_data_单主题.py → datasets_clean_json.py → 生成 94 条 ─────────────┘
                                                                              ↓
                                                            my_dataset.json = 194 条
                                                                              ↓ datasets_check_data_quality.py
                                                                    data-quality-report质检报告.txt

【alpaca-clean-500条】
  yahma/alpaca-cleaned (51760)
      └─ scripts/eval/prepare_data.py  （取前 550 → seed 42 打乱 → 500/50 切分）
              ↓                                          ↓
        my_dataset.json (500)                 my_test_dataset.json (50)
```

> ⚠️ **`alpaca-clean-500条` 的抽样方式有已知缺陷**（取连续前 550 条，非随机抽样，
> 实测 `instruction` 均长偏出总体 +31%）—— 详见其数据卡 §五-1。**这不是笔误，是实测结论。**
