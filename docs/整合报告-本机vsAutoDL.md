# 整合报告 · 本机 vs AutoDL

> 扫描范围：`原始文件/` 全部 743 个文件（已排除上游 LLaMA-Factory 官方仓库自带文件）
> 生成：2026-09-16 ｜ 判据：MD5 内容比对 + 产物反推，**不依赖时间戳**
>
> 📦 **2026-09-16 更新：`原始文件/` 已整块移出本仓库**，现位于：
> `/Users/heweidong/Desktop/Product/lora-finetune-原始文件归档/`
> **本报告中所有 `本机/…`、`AutoDL下载/…` 的相对路径，均以该归档目录为根。**
> 中间稿 `整合后/` 已删除（内容 100% 已进本仓库）。

---

## 一 · 先说三个最重要的结论

### 结论 1：这不是「新旧关系」，是**两条工作线 + 双向同步**

`cp` 备份脚本（`本机/LLaMA-Factory/AutoDLRTX4090备份文件目录2026.7.25LoRA`）显示，
AutoDL 上的文件是**双向流动**的，而且经过一个中间目录：

```
LLaMA-Factory-stable/  ──cp──▶  2026.7.25LoRA/  ──cp──▶  LLaMA-Factory/
                              （备份中转站）              （主工作目录）
```

所以**不存在「一边全是新的」**——必须逐文件判。

### 结论 2：AutoDL 侧的修改时间**全部失效**

AutoDL 下载下来的 **每一个文件**，时间戳都是 `2026-09-16 15:04–15:06`——**就是下载那一刻**。
原始修改时间已丢失，**不能作为判据**。

本机侧的时间戳是**真实可信**的（7/19 – 8/17）。

### 结论 3：**总体本机更晚，但有 3 个脚本 AutoDL 才是修好的版本**

- 本机最新文件到 **2026-08-17**；AutoDL 快照内容反映的是 **≈7/25–7/26** 的状态
  （依据：本机 `examples/train_lora/` 里有 7/28 才建的文件 `code_completion_lora.yaml`、`README.md`，
  AutoDL 侧**没有**——说明 AutoDL 那份是更早的快照）
- ⚠️ **但 `datasets_*.py` 三个脚本反过来**：本机侧是**坏的**，AutoDL 侧是**修好的**（见第三节）

---

## 二 · 真重复（同名 + 内容完全一致）—— 直接留一份，**无需你裁**

| 文件 | 所在（两边都有） | 证据 |
|---|---|---|
| `datasets_check_data_quality.py` | 本机根 / AutoDL `2026.7.25LoRA` | MD5 相同 `27f598a…` |
| `datasets_handcraft_data.py` | 同上 | MD5 相同 `a5e2525…` |
| `datasets_open_source_data.py` | 同上 | MD5 相同 `6ce9ad5…` |
| `datasets_visualize_data.py` | 同上 | MD5 相同 `704aebc…` |
| `datesets_handcraft_data.json` | 同上 | MD5 相同 `527af9a…` |
| `exp2_rank16.yaml` | 两边 `examples/train_lora` | MD5 相同 `b005340…` |
| `exp3_lr5e5_epoch5.yaml` | 同上 | MD5 相同 `c05c8d2…` |
| `summarize_dataset.py` | 两边 `BadCase_...` | MD5 相同 `d023ac1…` |
| `datasets_open_source_data_cleaned.json` | AutoDL 内部**两处**重复（`2026.7.25LoRA/` 与 `BadCase_.../`） | MD5 相同 `71be64d…` |

> 以上 9 组是**真重复**，各留一份即可。

---

## 三 · 真冲突（同名 + 内容不同）—— ⚠️ **需要你逐条裁**

### 🔴 冲突组 A：三个数据集脚本 —— 证据指向 **AutoDL 是修好的版本**

| 文件 | 本机版 | AutoDL 版 | 证据 | 建议 |
|---|---|---|---|---|
| `datasets_clean_json.py` | **跑不起来** | 能跑 | 本机版第 94 行用了 `random.sample()`，但**全文件没有 `import random`** → 一运行就 `NameError`。AutoDL 版第 15 行有 `import random` | **取 AutoDL** |
| `datasets_merge_script.py` | 引用**不存在**的文件 | 引用存在的文件 | 本机版读 `datasets_open_source_data.json_cleaned`（这个文件名**仓库里没有**）；AutoDL 版读 `datasets_open_source_data_cleaned_100.json`（**存在**）。且 AutoDL 版运行结果 = 100 + 94 = **194 条**，正好等于 `2026.7.25LoRA/my_dataset.json` 的实际条数 ✅ | **取 AutoDL** |
| `datasets_generated_data.py` | 多领域版生效 | 单主题版生效 | 见下方 ⬇️ | **请你裁** |

#### `datasets_generated_data.py` 的细节（这个要你定）

这个文件里**有两个 `__main__` 块**，用 `'''` 决定哪个生效。两版各激活了不同的那个：

| | 本机版 | AutoDL 版 |
|---|---|---|
| **生效的** `__main__` | 第 115 行（**多领域**：自然科学 50 + 历史 50 + 地理 30 + 生活百科 50 + 计算机 40） | 第 96 行（**单主题**「通用知识问答」） |
| 生成条数 | 目标 220 | `num = 120`（注释还写着「一次生成 100 条」——**注释没跟着改**） |
| 输出文件名 | 单主题→`datasets_qa_general.json`<br>多领域→`datasets_qa_general_mix.json` | 单主题→`datasets_generated_data.json`<br>多领域→`datasets_generated_data.json`（**两个块写同一个名字，会互相覆盖**） |

**两边的取舍正好相反：**
- **本机版**：修了「两个块输出同名」的 bug（命名更规范），但**现在的数据文件不是按它命名产出的**
- **AutoDL 版**：名字更朴素，但**现存的 `datasets_generated_data.json`（94 条）就是按它产出的**
  （本机版若跑，会产出 `datasets_qa_general.json`——**这个文件不存在**）

👉 **要你裁**：以后按哪套命名/哪套流程走？

---

### 🟡 冲突组 B：训练配置 yaml —— 证据指向 **本机是更完整的版本**

| 文件 | 本机版 | AutoDL 版 | 建议 |
|---|---|---|---|
| `best_lora_config.yaml` | **3592 B**，含**真实 MLflow 数据**（3 次 run 的 run_id / train_loss / train_runtime）+ 完整参数块 + 适用条件说明 | **1711 B**，只有骨架 + 一张全是 `?` 的表格 | **取本机** |
| `exp1_baseline.yaml` | 多了**早停与评估**配置段（`load_best_model_at_end`、`eval_strategy`、`eval_steps`）+ 行内注释；`save_steps: 50`、`save_total_limit: 5` | 无早停段；`save_steps: 100`、`save_total_limit: 2` | **取本机** |
| `my_first_lora.yaml` | **1453 B**，全套中文分节注释（`### 模型配置`…）+ 训练参数速查表 | 637 B（`LLaMA-Factory/` 版）/ 617 B（`2026.7.25LoRA/` 版），基本无注释 | **取本机** |
| `my_second_lora.yaml` | 比 AutoDL 版多 2 个空行，**实质内容相同** | — | 随便取一版 |

> **注意**：`my_first_lora.yaml` 有**三个版本**（本机 / AutoDL`LLaMA-Factory` / AutoDL`2026.7.25LoRA`）。
> 三者的 `learning_rate` 写法不同（`2.0e-4` vs `0.0002`，**值一样**）、
> `output_dir` 大小写不同（`qwen3-8b-...` vs `qwen3-8B-...`）——都是**排版差异，不是参数差异**。

---

### 🟡 冲突组 C：BadCase 评测管线 —— 证据指向 **本机脚本更全，但产物只在 AutoDL**

| 文件 | 本机版 | AutoDL 版 | 建议 |
|---|---|---|---|
| `batch_evaluate.py` | 注释更全（`# 基座模型回答和微调模型的批量推理 脚本`） | `# 基座模型回答和微调模型回答 脚本` | **取本机** |
| `compare_and_judge.py` | 多一行 `# 大模型裁判对比评估 （含胜率统计）` | 无 | **取本机** |
| `prepare_data.py` | 多一段说明（为什么是 500+50 而不是 200+20） | 无 | **取本机** |
| `notes.txt` | **4261 B**，含完整操作记录 + **脚本体系表**（脚本/功能/产出）+ 复制命令 | 3652 B，较简 | **取本机** |

---

## 四 · ⚠️ 最坑的一处：**两个 `my_dataset.json` 根本不是同一个东西**

这是本次整理**最重要**的发现。你问「哪些是重复的」——**这两个不是重复，是同名不同物**：

| | `AutoDL/2026.7.25LoRA/my_dataset.json` | `AutoDL/LLaMA-Factory/data/my_dataset.json` |
|---|---|---|
| **条数** | **194 条** | **500 条** |
| **怎么来的** | 数据集工程线：`datasets_merge_script.py` 合并<br>（开源 100 条 + 模型生成 94 条） | 评测线：`BadCase/.../prepare_data.py` 切分<br>（alpaca-cleaned 切出 500 训练 + 50 测试） |
| **用途** | 训练 `my_first_lora` 等 LoRA | 基座 vs 微调模型的对比评测 |
| **首条内容** | `"Edit the following sentence...simple past tense"` | `"Come up with a creative tagline for a beauty product."` |
| **配套测试集** | 无 | `my_test_dataset.json`（**50 条**） |

> ⚠️ **`my_dataset.json` 这个名字被两条线各用了一次，内容完全不同。**
> 整合时必须**改其中一个的名字**，否则一定会串。
> 建议：`my_dataset_194条_数据集工程版.json` / `my_dataset_500条_评测用.json`。
>
> 附带影响：`LLaMA-Factory/data/my_dataset.json`（500 条）很可能是 `prepare_data.py`
> **覆盖**了 `datasets_merge_script.py` 的产出（两者输出路径相同）——**建议你回忆确认**。

---

## 五 · 互补（不是冲突，**两边都要**）

BadCase 评测管线是**「本机有脚本、AutoDL 有产物」**：

| 类型 | 本机有 | AutoDL 有 |
|---|---|---|
| 脚本 | ✅ 7 个（含 `test_evaluation.py`、`test_lora_evaluation.py` 两个 AutoDL **没有**的） | ✅ 5 个 |
| **产物** | ❌ **一个都没有** | ✅ `dataset_summary.txt`、`evaluation_results.json`(63 KB)、`final_judgment.json`(17 KB)、`my_test_dataset.json`(50 条)、`data/my_dataset.json`(500 条)、`datasets_open_source_data_cleaned.json`(42 MB) |

👉 **本机缺的是评测结果**（这是仓库要的证据），**AutoDL 缺的是两个测试脚本**。两边合起来才完整。

---

## 六 · 只在一侧的文件

### 只在本机（AutoDL 没有）
- `LLaMA-Factory/` 根：`evaluate.py`、`mlflow_data.py`、`Modelfile.exp1_q4km`、`训练数据速查.md`、`Ollama部署微调模型.md`、备份脚本
- `examples/train_lora/`：`README.md`、`YAML_LoRA通用优化策略`、`code_completion_lora.yaml`（**7/28 建，是判定 AutoDL 快照更早的关键证据**）
- 整个 `out-GGUF-Script/`、整个 `RAG_query_rewrite/`、整个 `Code-completion-LoRA/`
- **整个 `llm-gateway/`**（27 个文件）
- `LLaMA-Factory/environment.yml`、`requirements.txt` —— ⚠️ **两个都是 0 字节空文件**

### 只在 AutoDL（本机没有）
- `2026.7.25LoRA/`：`datasets_open_source_data.json`(**42 MB**)、`datasets_open_source_data_cleaned.json`(**42 MB**)、
  `datasets_open_source_data_cleaned_100.json`、`datasets_generated_data.json`、`datasets_generated_data_cleaned_100.json`、
  `data_quality_report.txt`、`my_dataset.json`(194 条)
- `BadCase_.../`：全部**产物**（见第五节）+ `datasets_open_source_data_cleaned.json`(42 MB)
- `LLaMA-Factory/data/`：`my_dataset.json`(500 条) —— ⚠️ 混在上游 demo 数据里
- `mlflow.db`(1 MB)、`.env.local`、`.dataset_info.json.swp`（临时文件）

---

## 七 · ⚠️ 回答你的问题：「能公开吗」—— **要打一个问号**

数据来自 **`yahma/alpaca-cleaned`**（HuggingFace，`datasets_open_source_data.py` 里写死的）。

**它不是 Apache 2.0，而是 `CC BY-NC 4.0`**：

> - **NC = NonCommercial（非商用）**
> - 数据集卡原话：*「models trained using the dataset should not be used outside of research purposes」*
>   （用该数据集训出的模型，不应超出研究用途使用）
> - Apache 2.0 只覆盖**配套代码**，**不覆盖数据本身**

**结论：**
- ✅ **可以公开**（CC BY-NC 允许非商业再分发，条件是**署名**）
- ⚠️ **必须标注许可证**，且**用它训出的 LoRA 不能用于商业产品**
- ✅ 对研究 / 展示用途**没有影响**
- ⛔ 但**不能**在 README 里写「可商用」或对许可证闭口不提

**关于要不要把 42 MB 原始数据放进仓库 —— 我的建议是：不放。**
理由：① 体积（两份共 84 MB，GitHub 单文件超 50 MB 会警告）
② 没必要——`datasets_open_source_data.py` **一行就能重新下载**，
③ 符合仓库第二铁律「只放数据卡」。
👉 放**下载脚本 + 数据卡（写明 `CC BY-NC 4.0` + 来源 URL）**，任何人都能一键复现。

**另外两个数据质量发现（顺手报）：**
- `datasets_open_source_data.json` 后缀是 `.json`，**但它不是合法 JSON**——是
  `to_json(indent=2)` 吐出的**一堆对象直接拼接**（51760 条，310612 行）。
  `datasets_clean_json.py` 里的 `raw_decode` 就是专门为它写的。**建议改名为 `.jsonl`** 或在数据卡里注明。
- 文件名 `datesets_handcraft_data.json` 的 `datesets` 是**少了个 `a` 的笔误**，两边一致。按你的要求整合时**已改回 `datasets_`**。

---

## 八 · 裁决记录（**2026-09-16 已全部裁定**）

> 本节原为「待拍板问题清单」。**7 条已于 2026-09-16 全部裁定，结果如下。**

| # | 问题 | ✅ 裁定 |
|---|---|---|
| 1 | `datasets_generated_data.py` 用哪套？ | **两版都留，改名并存** → `scripts/datasets/datasets_generated_data_单主题.py`（AutoDL 版，现存 94 条数据是它产出的）与 `_多领域.py`（本机版，修了输出重名 bug） |
| 2 | 三个 `datasets_*.py` 全取 AutoDL？ | ✅ 是。`datasets_clean_json.py` 与 `datasets_merge_script.py` 取 AutoDL 版（本机版分别有 `NameError` 和「文件不存在」两处硬缺陷） |
| 3 | 两个 `my_dataset.json` 改名保留？ | ✅ 是。**192/500 两条线彻底分开** → `datasets/qa-general-194条/` 与 `datasets/alpaca-clean-500条/` |
| 4 | 42 MB × 2 原始数据进仓库？ | ⛔ **不进**。放下载脚本 + 数据卡；已写入 `.gitignore` |
| 5 | 两个 0 字节空文件 | ⛔ **已删除**（`environment.yml`、`requirements.txt`） |
| 6 | `mlflow.db` / `.env.local` / `.swp` 留不留？ | ⛔ **都不留**。且 `.env` **已删除**——见下方「密钥事件」 |
| 7 | 上游 LLaMA-Factory 文件 | **不复制进仓库**，单独标注 → `docs/上游-LLaMA-Factory-勿改.md` |

### 🔴 附：密钥事件（本次整合发现，已处置）

裁定问题 6 时检查 `.env.local`，**顺带发现一个真实泄漏**：

- `本机/llm-gateway/.env` 含一个**非空的 22 字符 `API_KEY`**
- 同一个 key **还硬编码在另外 12 处**（含 `main.py:125` 的代码默认值、
  `docker-compose.yml:13` 的默认值兜底、以及 6 处**要公开的文档**）
- **共 36 处**（本机 + 整合后各 18），已按上下文分别替换为
  `os.getenv("API_KEY", "")` / `${API_KEY:?API_KEY 未设置}` / `your-api-key-here`
- **全库复扫已无残留**（另有 10 处为误报：模型名 `my-…el`、CSS 类名、哈希串）

> ⚠️ **仍建议**：该 key 若在别处（如线上服务）用过，**应作废重置**——
> 它已经在本机文件系统里存在过，且曾有副本。

---

## 九 · 产物去向（**2026-09-16 更新**）

整合产物**已经铺进仓库根目录**，不再是「样稿」阶段：

```
/Users/heweidong/Desktop/Product/lora-finetune/
├── datasets/     ← 数据卡 + 三分支数据 + 质检报告
├── configs/      ← 9 个训练配置
├── scripts/
│   ├── datasets/ ← 8 个数据工程脚本
│   └── eval/     ← 9 个评测脚本
├── experiments/  ← E01/E02/E03 实验记录（由 mlflow.db 真库重建）
├── results/      ← 评测产物
├── deploy/       ← GGUF 导出 + Ollama 部署
├── subprojects/  ← code-completion-lora / rag-query-rewrite
├── gateway/      ← llm-gateway（已清密钥）
├── docs/         ← 本报告 + 上游说明
└── .gitignore
```

原始素材已整块移出仓库，位于
`/Users/heweidong/Desktop/Product/lora-finetune-原始文件归档/`（160 MB）；
中间稿 `原始文件/整合后/` 已删除。

> 📌 上游 LLaMA-Factory 官方仓库文件**不在**本仓库内，留在上述归档的
> `AutoDL下载/LLaMA-Factory/` 中，
> 其上游版本为 **commit `2ebe7be6`（2026-07-24）**（由 `.git` 判定）。
