# experiments/ · 实验记录总览

> 建立：2026-09-16（由 `mlflow.db` 真库 + 配置文件重建，**未补编任何数字**）
> 一次实验 = 一个文件，从 `../template实验记录.md` 复制。

---

## ⚠️ 先说一个最重要的结论：**现有三组实验回答不了本仓库的核心问题**

本仓库的论点是「**LoRA 的效果主要由数据集决定，不是超参数**」（`CLAUDE.md` §一）。

而 `E01 / E02 / E03` 三组实验：

| | 数据集 | rank | learning_rate | epochs |
|---|---|---|---|---|
| E01 baseline | **同一份**（500 条） | 8 | 2e-4 | 3 |
| E02 rank16 | **同一份**（500 条） | **16** | 2e-4 | 3 |
| E03 lr5e-5-epoch5 | **同一份**（500 条） | 8 | **5e-5** | **5** |

👉 **三组全都在「改参数」，一次「改数据」都没有。**
所以它们只能说明「改参数会让 loss 变化」，**无法支撑「数据比参数重要」这个结论**。

**要支撑核心判断，还缺一组 E04：固定全部参数，只换数据集**。

> ⚠️ **设计要点：两组的条数必须相同**（E04 定为各 **194 条**）。
> 若拿 194 条 vs 500 条比，就把「数据内容」和「数据条数」两个变量混在了一起，**归因不成立**。
> 方案见 [`E04-数据集对照.md`](E04-数据集对照.md)。

**另有 E05：把「输出质量」变成可记录的量** —— 没有它，所有 loss 都变不成质量结论。
方案见 [`E05-人工判断.md`](E05-人工判断.md)。

**这两组方案都已写好待跑，缺的是 GPU 环境。**

---

## 一 · 数据来源（先纠正一个容易搞错的地方）

三组实验的配置里都写 `dataset: my_dataset` + `max_samples: 500`，
而 `configs/best_lora_config.yaml` 第 12 行自述：

> 「最优LoRA微调配置（基于 **500 条 alpaca-cleaned** 数据验证）」

**所以训练用的是 `datasets/alpaca-clean-500条/`，不是 `分支A` 的 194 条。**

> ⚠️ 仓库里有两个同名 `my_dataset.json`（194 条 / 500 条），
> 这正是本次整合发现的坑，已分别放进 `分支A` 和 `分支B`。
> **写文档或口头讲解时务必说清是哪一份。**

---

## 二 · MLflow 真库（`mlflow.db`）里的 6 次运行

从 `mlflow.db` 直接查询所得，**全部 `FINISHED`**。
> 📦 **本仓库已收录训练产物**，全部数字可直接复算 →
> [`artifacts训练产物/`](artifacts训练产物/README.md)（五组运行，110 个文件 / 约 0.5 MB）。
> ⚠️ **读之前务必看那份说明的 §二「三个读数陷阱」** —— 尤其是
> `train_loss` 与「最后一条逐步记录」不是同一个量（exp1 是 0.5603 vs 0.8108）。
>
> 原始 `mlflow.db` 则在该归档中：
> `/Users/heweidong/Desktop/Product/lora-finetune-原始文件归档/AutoDL下载/LLaMA-Factory/mlflow.db`
> （1 MB SQLite；已按 `.gitignore` 排除，不进本仓库）
⚠️ 6 次运行的 `mlflow.runName` **都是自动名 `capable-auk-759`**（没手动命名过）。

| # | run_id | lr | epochs | train_loss | train_runtime | 对应 |
|---|---|---|---|---|---|---|
| 1 | `55ab5df2b466` | 2e-4 | 3 | **0.0000** | **14.32 s** | ✅ **= `my_first_lora`**（见下方） |
| 2 | `e6be105c5b7d` | 2e-4 | 3 | 0.9509 | 114.99 s | ❓ 无对应实验 |
| 3 | `29e37dbcef0e` | 2e-4 | 3 | **0.5603** | 181.5449 s | ✅ **E01 baseline** |
| 4 | `b2db7731cd35` | 2e-4 | 3 | **0.8462** | 300.9799 s | ✅ **E02 rank16** |
| 5 | `beee18c8dc15` | 5e-5 | 5 | **0.9941** | 479.0966 s | ✅ **E03 lr5e-5-epoch5** |
| 6 | `c0beed18beb7` | 2e-4 | 3 | 1.0588 | 120.52 s | ✅ **= `my_second_lora`**（见下方） |

> 📌 **纠正一处旧记录**：`configs/best_lora_config.yaml` 第 42–46 行抄了一张三行表格
> （run `c0beed18` / `beee18c8` / `b2db7731`），看起来像「三次实验的结果」。
> 对照真库，那是**按时间倒序取最后 3 行的查询结果**，**漏掉了 E01 的 run（`29e37dbc`）**，
> 却混进了两次无关运行。**以本文件的真库表为准。**
>
> ✅ **出处已定位到本仓库自己的文件**：`scripts/eval/mlflow_data.py` 里写着
> ```python
> recent = runs.sort_values("start_time", ascending=False).head(3)
> ```
> —— 取的是**最近 3 次运行**，不是「三次实验」。该 yaml 中那三行的顺序
> （`c0beed18` → `beee18c8` → `b2db7731`）与真库按 `start_time` 倒序排列的结果**完全一致**。
> 另外该脚本要取的 `params.lora_rank` 列在 mlflow 里**根本不存在**（见 §三），取出来是空的。
> （该 yaml 里手写的那句 `总运行次数: 6` 是**对的**。）

### 📌 已辨认出的运行：`c0beed18beb7` = `my_second_lora`

`configs/my_second_lora.yaml` 与 `my_first_lora.yaml` **参数完全相同**（200 条、rank 8、lr 2e-4、3 epochs），
只是 `output_dir` 不同 —— 也就是说**同一套配置跑过两次**，它们本该也在 mlflow 里各占一次运行。

其中 `my_second_lora` 的训练产物对得上：

| 指标 | 该次 mlflow 运行 | `my_second_lora` 的训练产物 |
|---|---|---|
| `train_loss` | 1.058765 | **1.0587651125590007** ✅ |
| `train_runtime` | 120.5208 | **120.5208** ✅ |

**两项都精确到小数点后 7 位一致** —— 可以认定是同一次运行。

**顺带可复算的两条**（纯算术，不依赖日志）：
- 200 条 × 3 epoch ÷ (batch 2 × grad_accum 4 = 8) = **75 步** —— 与其 `total_steps: 75` 吻合
- 而 500 条的 `exp1_baseline` = **187.5 步** ≈ 189 —— 与 `evaluate.py` 里标的「step 189」吻合

> ⚠️ **还剩 2 次运行未辨认**（`55ab5df2b466` loss 0.0、`e6be105c5b7d` loss 0.9509）。
> 需要对应的训练产物才能确认，**不要猜**。

---

## 三 · ⚠️ MLflow 记录本身的缺陷（影响可复现性）

查 `params` 表，6 次运行**只记录了 4 个参数**：

```
learning_rate · num_train_epochs · per_device_train_batch_size · gradient_accumulation_steps
```

**没有记录**：`lora_rank`、`lora_alpha`、`dataset`、`model_name_or_path`、`cutoff_len`

后果：
- **E01 与 E02 的唯一区别是 rank（8 vs 16），但 MLflow 里看不到 rank** ——
  只能在 `configs/exp1_baseline.yaml` 与 `configs/exp2_rank16.yaml` 里对比才能确认。
- 第 1、2、6 次运行（loss 0.0 / 0.9509 / 1.0588）参数**完全相同**（lr 2e-4、3 epochs），
  却得到三个差别很大的 loss，**无法从 MLflow 判断它们各自是什么配置**。
- **这三条为什么跑、是不是废弃的尝试，目前无记录。**

👉 **建议**：下次训练在 yaml 里加 `run_name:`，或在 `report_to: mlflow` 的同时把
`lora_rank` 等写进 `params`，否则「哪次实验是哪组参数」这条链会断。

---

## 四 · ⚠️ 缺口清单（**这些不是"没写"，是"确实没有"**）

| 模板要求的项 | 状态 |
|---|---|
| 人工判断（哪个输出更好） | ❌ **完全没有记录** |
| 对照样例（同一 prompt 的对照组/实验组输出） | ❌ **没有** |
| 评测分数（BLEU/ROUGE/裁判打分） | ❌ 未记录。⚠️ `results/` 里那份**已查实不可用**，不能拿来顶（见下） |
| LLaMA-Factory 版本 | ✅ **`v0.9.5` 之后 41 个提交**（`v0.9.5-41-g2ebe7be6`，2026-07-24）<br>由归档仓库 `git describe` 判定 |
| 关键依赖版本 | ❌ 未记录 |
| 硬件 | ⚠️ 仅能**推断**（见各记录 §三） |
| 数据卡 | ✅ **已补** `datasets/alpaca-clean-500条/数据卡-alpaca500.md`（2026-09-16） |
| 实验日期 | ⚠️ 仅能**推断**（AutoDL 时间戳已丢失） |

> 📌 **`results/` 里那份评测：已查实不可用，两处都不能拿它顶。**
>
> 它来自 BadCase 管线（500 条训练 / 50 条测试），本意是比较**基座模型 vs 微调模型**，
> **不是** E01/E02/E03 之间的对比。但更严重的是：
>
> | 问题 | 证据 |
> |---|---|
> | **两边跑的是同一个模型** | `scripts/eval/batch_evaluate.py:63-66` 两处都传 `"qwen3:8b"` |
> | **一半推理是空的** | 50 条里 **24 条**两边回答都空，只有 **19 条**可比 |
> | **23 条「平局」里 20 条是「都答不出来」** | `final_judgment.json` 的 `category` 分布 |
>
> 👉 **它既不能代表 E01–E03，本身也不是一次有效评测。** 详见 `results/README.md`。

---

## 五 · 现有实验索引

| 编号 | 一句话 | 类型 | 文件 |
|---|---|---|---|
| E01 | rank 8 · lr 2e-4 · 3 epochs（基线） | 改参数 | `E01-baseline.md` |
| E02 | rank 16 · lr 2e-4 · 3 epochs | 改参数 | `E02-rank16.md` |
| E03 | rank 8 · lr 5e-5 · 5 epochs | 改参数 | `E03-lr5e-5-epoch5.md` |
| **E04** | **固定参数，只换数据集**（两组各 194 条） | **改数据** | ⬜ 方案已就绪，待跑 —— [`E04-数据集对照.md`](E04-数据集对照.md) |
| **E05** | **人工判断 / 对照样例**（测量方法） | — | ⬜ 方案已就绪，待跑 —— [`E05-人工判断.md`](E05-人工判断.md) |
