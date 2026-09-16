# lora-finetune

> **一个 LoRA 微调的「数据与实验库」。**
> 把每次 LoRA 工作产生的**数据集、训练配置、实验记录、评测结果**集中存放 ——
> 数据是怎么造的、参数是怎么选的、哪次成了哪次废了，都在这里。

**这是一个库，不是一次性的项目。** 新的 LoRA 数据进来就新增一个目录，不改动已有的。

---

## 目录

| | |
|---|---|
| **数据集** | [`datasets/`](datasets/README.md) —— 3 个数据集，各带数据卡 |
| **实验** | [`experiments/`](experiments/README.md) —— E01–E03 已跑过 · E04/E05 ⬜ 方案已就绪 |
| **训练产物** | [`experiments/artifacts训练产物/`](experiments/artifacts训练产物/README.md) —— 五组运行的日志，**每个 loss 都可复算** |
| **配置** | [`configs/`](configs/) —— 9 个训练配置 |
| **脚本** | [`scripts/`](scripts/README.md) —— 数据工程 + 评测 |
| **结果** | [`results/`](results/README.md) —— 评测产物（⚠️ **现有评测不可用**，原因已写明） |
| **部署** | [`deploy/`](deploy/README.md) —— GGUF 导出 + Ollama |
| **子方向** | [`subprojects/`](subprojects/README.md) —— 代码补全 · 查询改写（**均无实验记录**） |
| **网关** | [`gateway/`](gateway/) —— FastAPI 推理网关 |
| **溯源** | [`docs/`](docs/README.md) —— 整合报告 · 上游说明 · 执行日志 |
| **模板** | [`template数据卡.md`](template数据卡.md) · [`template实验记录.md`](template实验记录.md) |

---

## 一 · 数据集

| 数据集 | 条数 | 来源 | 许可证 |
|---|---|---|---|
| [`alpaca-clean-500条/`](datasets/alpaca-clean-500条/) | 500 + 50 | `yahma/alpaca-cleaned` 前 550 条切分 | `CC BY-NC 4.0` |
| [`qa-general-194条/`](datasets/qa-general-194条/) | 194 | 开源 100 条 + 本地 Ollama `qwen3:8b` 生成 94 条 | 混采 |
| [`code-completion代码补全/`](datasets/code-completion代码补全/) | 250 | Python 代码提取<br>⚠️ 来源**未记录**（回忆指向本机依赖，**未经确认**） | ⚠️ 待确认 |

> ⚠️ **两个数据集都含一个叫 `my_dataset.json` 的文件，但不是同一个东西。**
> 这是整理历史文件时发现的坑。**看目录名，别只看文件名。**
>
> 📌 `alpaca-clean-500条/` 里还放着 **E04 用的两组 194 条数据**
> （`E04-A组-194条.json` / `E04-B组-194条.json`）—— 它们是**从 500 条那份派生**的，
> 由 `scripts/datasets/make_e04_datasets.py` 固定种子生成。

每个数据集都有**数据卡**，记录它的构造过程、统计、**以及已知缺陷**。
总索引见 [`datasets/README.md`](datasets/README.md)。

---

## 二 · 实验现状（**这一节请务必看完**）

| # | 改了什么 | 训练 loss | 耗时 | 结论 |
|---|---|---|---|---|
| **E01** 基线 | rank 8 · lr 2e-4 · 3 epochs | **0.5603** | 181.5 s | 基线 |
| **E02** rank16 | **rank 8 → 16** | 0.8462 | 301.0 s | 🔴 loss +51%，慢 +66% |
| **E03** lr5e-5-epoch5 | **lr ÷4，epochs 3 → 5** | 0.9941 | 479.1 s | 🔴 loss +77%，慢 +164% |

**观察到的现象**：**两次调参都让 loss 更高、耗时更长；什么都没调的基线反而最好。**

### ⛔ 但这些不能当成结论 —— 三个理由

1. **三组实验全是「改参数」，没有一组「改数据」**
   → 本库一直关注的判断是「**数据质量 ≫ 超参数**」。这个判断**一次都没有被检验过**。
   要检验它，需要 **E04：固定全部参数，只换数据集** —— ⬜ **还没做**。
   （设计已修正为**同源同语言同条数**，唯一变量是「抽样代表性」；
   早先那版混了来源/语言/质量三个变量，已推翻，见 `experiments/E04-数据集对照.md` §二）

2. **训练 loss ≠ 输出质量**
   → 目前**没有任何输出质量证据**（没有人工判断、没有对照样例、没有自动指标）。
   「越调越差」**只是 loss 现象，不是质量结论**。

3. **三次实验之间严格来说不可直接横比**
   → E03 跑了 5 epoch 而 E01/E02 只有 3 epoch（**315 步 vs 189 步**），
   「末值 loss」是在**不同训练步数**上取的。且 E03 **同时改了两个变量**，即使有差异也**无法归因**。
   （~~E01 多了早停配置~~ → **已推翻**：核实训练产物后，五组训练的 `best_model_checkpoint` 全为 `None`，
   早停**从未生效**，见 `experiments/E01-baseline.md` §四。）

> **目前能证明的只有**：在这个设置下，这两次调参都没有收益，且都更慢。
> 更多的，等 E04 和人工判断。详见 [`experiments/README.md`](experiments/README.md)。
>
> 📌 **E04 / E05 的方案已写好待跑**：
> [`experiments/E04-数据集对照.md`](experiments/E04-数据集对照.md)（固定参数只换数据集，两组各 194 条，**同源同语言**）·
> [`experiments/E05-人工判断.md`](experiments/E05-人工判断.md)（对照样例 + 人工判断，含三道自动检查）。
> **需要有 GPU 的环境才能执行。**

---

## 三 · 仓库结构

```
lora-finetune/
├── datasets/          ⭐ 库的核心增长轴（一个数据集一个目录）
│   ├── README.md
│   ├── alpaca-clean-500条/
│   ├── qa-general-194条/
│   └── code-completion代码补全/
├── configs/           训练配置
├── scripts/           ← 索引见 README.md
│   ├── datasets/      数据工程（下载/清洗/合并/质检/可视化）
│   └── eval/          评测（切分/批量推理/大模型裁判）
├── experiments/       实验记录（+ artifacts训练产物/ 五组运行的训练产物，可复算）
├── results/           评测产物
├── deploy/            GGUF 导出 + Ollama
├── subprojects/       代码补全 · 查询改写（两个子方向，均无实验记录）
├── gateway/           FastAPI 推理网关
├── docs/              溯源与说明
└── template*.md       数据卡 / 实验记录模板
```

---

## 四 · 快速开始

```bash
# ── 数据管线（可复现）──────────────────────────────
export HF_ENDPOINT=https://hf-mirror.com
python scripts/datasets/datasets_open_source_data.py     # → 51760 条原始（42MB，不入库）
python scripts/datasets/datasets_clean_json.py           # → 清洗 + 随机抽 100
python scripts/datasets/datasets_merge_script.py         # → qa-general-194条/my_dataset.json
python scripts/datasets/datasets_check_data_quality.py   # → 质检报告

# ── 评测用切分（✅ 可精确复现：脚本内 random.seed(42)）──
python scripts/eval/prepare_data.py                      # → alpaca-clean-500条/ 500 + 50

# ── E04 的两组数据集（✅ 可精确复现：固定种子）
#    需要先有一个含全部 51760 条的合法 JSON（42 MB，不入库），生成方式见脚本文件头
python scripts/datasets/make_e04_datasets.py
#    → alpaca-clean-500条/E04-A组-194条.json（从全量随机抽）
#    → alpaca-clean-500条/E04-B组-194条.json（从前 550 区块抽）

# ── 训练（需要 GPU + 本地模型，见 configs/）───────────
llamafactory-cli train configs/exp1_baseline.yaml
```

> ⚠️ **`configs/` 里的 `model_name_or_path` 与 `output_dir` 仍是原环境（AutoDL）上的路径**
> （`/root/autodl-fs/...`），**直接跑会失败**，需要改成你自己的路径。这是已知缺陷。

---

## 五 · 环境

| 项 | 值 |
|---|---|
| 训练硬件 | **AutoDL · RTX 4090 · 24GB**（⚠️ 推断，训练日志未直接记录） |
| 基座模型 | **Qwen3-8B**（另有 Qwen3-Coder-7B 用于代码补全子方向） |
| 微调框架 | **LLaMA-Factory**，上游 **`v0.9.5` 之后 41 个提交**（`v0.9.5-41-g2ebe7be6`，2026-07-24，由 `git describe` 判定） |

---

## 六 · ⚠️ 本库目前没有的东西

> 这一节是**故意**放这儿的。写不出缺陷 = 没真的检查过。

| 缺什么 | 后果 |
|---|---|
| **E04：改数据的对照实验** | 核心判断无法被验证（⬜ 方案已就绪，缺 GPU 环境） |
| **人工判断 / 对照样例** | 所有 loss 数字**无法变成质量结论**（⬜ 方案 + 脚本已就绪） |
| 自动评测分数（BLEU/ROUGE/裁判） | ⚠️ `results/` 里那份「基座 vs 微调」的评测**已查实不可用** —— 两边跑的其实是同一个模型。见 `results/README.md` |
| **启动命令**（日志级） | 别人**无法精确复现** E01–E03。⚠️ 框架版本**已知**（`v0.9.5-41-g2ebe7be6`），缺的是**当时敲的那行命令** |
| `code-completion代码补全` 的来源与许可 | ✅ 已处置：**数据文件已撤出仓库**，只留数据卡。来源仍未确认 |

**这些不是"还没写"，是"确实没有"。** 不会为了让文档好看而填上。

---

## 七 · 许可

| 对象 | 许可证 |
|---|---|
| **本库代码** | **MIT**（见 [`LICENSE`](LICENSE)） |
| 数据 `yahma/alpaca-cleaned` | **`CC BY-NC 4.0`** —— ⛔ **非商用**。数据集卡原文：*「用该数据集训出的模型不应超出研究用途」* |
| 数据 `codefuse-ai/CodeExercise-Python-27k` 或本地库源码 | ⚠️ **待确认** |
| 上游 LLaMA-Factory | Apache-2.0 —— **不是本库的代码**，本库不含其副本 |

> ⛔ **不要把数据许可证写成 Apache-2.0** —— 那是 alpaca-cleaned **配套代码**的许可，不是数据本身的。
