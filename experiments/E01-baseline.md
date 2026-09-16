# 实验 E01 · 建立 LoRA 微调基线（rank 8 / lr 2e-4 / 3 epochs）

> 由 `mlflow.db` 真库 + `configs/exp1_baseline.yaml` 重建，2026-09-16。
> ⚠️ **原始实验时未写记录**，本文件是事后从产物反推的，缺口已在 §七 标注。

---

## 一 · 假设

> **一句话**：先跑一组**没有任何调优**的默认参数，作为后续 E02/E03 的对照基准。

- **本实验属于哪一类**：
  - [ ] 改数据（数据集内容 / 配比 / 清洗规则）
  - [x] **改参数**（lr / rank / epochs / target_modules …）
  - [ ] 其他：______

## 二 · 变量

| | 值 |
|---|---|
| **自变量** | 无（本实验是基线，不设自变量） |
| 对照组 | — |
| 控制变量 | 见 §四（E02/E03 以此为基准） |

## 三 · 环境

| 项 | 值 |
|---|---|
| 硬件 | ⚠️ **推断**：AutoDL · RTX 4090 · 24GB 显存<br>（依据：备份脚本文件名 `AutoDLRTX4090备份文件目录2026.7.25LoRA`；**训练日志中未直接记录**） |
| 基座模型 | `Qwen3-8B`（路径 `/root/autodl-fs/vllm-models/Qwen3-8B/models/Qwen--Qwen3-8B/snapshots/master`） |
| 微调框架 | LLaMA-Factory ｜ 上游 **`v0.9.5` 之后 41 个提交**（`git describe` = `v0.9.5-41-g2ebe7be6`，commit 日期 2026-07-24）<br>✅ 由归档仓库的 `git describe` 判定（非推断） |
| 关键依赖版本 | ⚠️ **未记录** |
| 训练时长 | **181.5449 秒**（`train_runtime`） |
| 实验日期 | ⚠️ **推断** ≈ 2026-07-27（依据：配置文件 mtime）<br>⚠️ AutoDL 侧原始时间戳在下载时已全部丢失 |

## 四 · 配置

- 配置文件路径：`configs/exp1_baseline.yaml`

| 参数 | 值 |
|---|---|
| learning_rate | 2.0e-4 |
| lora_rank | 8 |
| lora_alpha | 16 |
| lora_dropout | 0.05 |
| lora_target | all |
| epochs | 3 |
| batch_size | 2 |
| gradient_accumulation_steps | 4 |
| cutoff_len | 1024 |
| max_samples | 500 |
| template | qwen |
| 数据集 | `datasets/alpaca-clean-500条/`（500 条 alpaca-cleaned 切分） |

**⚠️ 修正（2026-09-16）：早停段【从未生效】**

本记录早先写着「E01 独有早停配置，E02/E03 没有，所以不可比」。
**用训练产物核对后，这个说法不成立** —— 那条配置确实存在，但**从未真正跑过**：

| 证据 | 说明 |
|---|---|
| 五组训练的 `trainer_state.json` 里 **`best_model_checkpoint` 全是 `None`** | 早停/评估**一次都没触发过** |
| 本目录只有 `checkpoint-100` 与 `checkpoint-189` | 对应 `save_steps: 100`，**不是 50** |
| 归档中 AutoDL 上的同名配置 | `save_steps: 100` / `save_total_limit: 2` / **无早停段** |

**原因**：`eval_strategy: steps` 需要配置验证集（`val_size` 或 `eval_dataset`）才会触发评估，
而三份配置里都没有 —— 所以**从未产生过任何一次评估**。

👉 **结论：E01/E02/E03 的训练过程其实是干净的**（都无早停、都无评估）。
✅ 详见 `configs/exp1_baseline.yaml` 顶部说明。

## 五 · 结果

| 指标 | 值 | 出处 |
|---|---|---|
| **训练 loss（末值）** | **0.5602585398961627** | mlflow run `29e37dbcef0e` |
| train_runtime | **181.5449 秒** | 同上 |
| epoch | 3.0 | 同上 |
| train_samples_per_second | 8.262 | `all_results.json` 转抄 |
| train_steps_per_second | 1.041 | 同上 |
| total_flos | 15138681363628032 | 同上 |
| **评测分数** | ⚠️ **未记录**（无 BLEU/ROUGE/裁判打分） | — |
| **人工判断（关键）** | ❌ **完全没有记录** | — |

### ⚠️ 两个「loss」不是同一个量（**很关键，别混用**）

| 名称 | 值 | 出处 |
|---|---|---|
| **`train_loss`**（HF 汇总的末值） | **0.5602585398961627** | `all_results.json` / `mlflow.db` |
| **最后一条逐步记录**（step 180） | **0.810824** | `trainer_state.json` 的 `log_history` |

两者**差得很多**，但都不是错的 —— 它们是不同的量。**引用时必须说清用的是哪一个。**

**逐步 loss（`log_history`，每 10 步一条）**：

| step | loss | step | loss |
|---|---|---|---|
| 80 | 0.8654 | 140 | 0.9297 |
| 90 | 1.0247 | 150 | 0.8792 |
| 100 | 0.9326 | 160 | 0.8709 |
| 110 | 0.9798 | 170 | 0.9281 |
| 120 | 0.8850 | **180** | **0.8108** |
| 130 | 1.0507 | | |

> ⚠️ `exp1_baseline/trainer_state.json` 的 `log_history` **前 7 条（step 10–70）不是本次的** ——
> 那几条的 epoch（0.41/0.82/…/2.82）对应的是 **25 步/epoch**，即 **200 条**那组配置；
> 而 exp1 是 500 条（63 步/epoch）。**上表已剔除那 7 条。**
> 📌 总步数可精确复算：`ceil(500 ÷ 8) × 3 = 63 × 3 = 189` ✅

**对照样例**：❌ **没有**（模板要求至少 3 组同 prompt 的对照输出）

> ⚠️ 按本仓库自己的规矩：**训练 loss 不是结论**。
> `CLAUDE.md` §一 的原话是「一直调参只是改变曲线和数值，无法改变输出结果的质量」——
> 那么这组实验**恰恰应该用输出来验证这句话**，而输出质量**没有记录**。
> **本实验目前只能说明 loss 是多少，不能说明模型变好了没有。**

## 六 · 结论

- **假设成立吗**：✅ 成立（基线已建立，有可复现的 loss 与时长）
- **一句话结论**：基线 **0.5603**（181.5 s），是三次里 **loss 最低**的一组
- **意外发现**：
  1. E02（rank 翻倍）的 loss **反而更高**（0.8462，+51%），且**慢 66%**
  2. E03（lr 降 4 倍 + epochs 加到 5）的 loss **更高**（0.9941，+77%），且**慢 2.6 倍**
  3. ⚠️ 三者 **epochs 不同**（E01/E02 是 3，E03 是 5），
     所以「末值 loss」是在**不同训练步数**上取的 —— **这一点仍然成立，不可直接横比**
     （E01/E02 = 189 步，E03 = 315 步）。
     ~~但 E01 多了一段 E02/E03 没有的早停+评估配置~~ → **该说法已于 2026-09-16 推翻**（见 §四）
- **⚠️ 检查点：仓库里的说法自相矛盾，未解决**

  `scripts/eval/evaluate.py` 第 55–60 行列了两个权重：

  | 名称 | 该文件里标注的路径 |
  |---|---|
  | 最终权重 | `saves/exp1_baseline`（标注 `最终权重(step 189)`） |
  | `checkpoint-75` | `saves/exp1_baseline/checkpoint-75`（标注 `最低loss(step 75)`） |

  **但 `checkpoint-75` 与训练配置对不上：**

  - `configs/exp1_baseline.yaml` 里 **`save_steps: 50`** → 检查点只会出现在 **50 / 100 / 150 …**，
    **不会出现 75**
  - 且 **`save_total_limit: 2`** → 只保留最近 2 个，更早的会被删掉
  - 👉 因此 **`saves/exp1_baseline/checkpoint-75` 这个路径是错的**

  **步数可以复算**（纯算术，不依赖任何日志）：

  | 配置 | 条数 | epochs | 有效 batch | **总步数** |
  |---|---|---|---|---|
  | `exp1_baseline` | 500 | 3 | 2×4=8 | **187.5** ≈ 188/189 |
  | `my_first_lora` | 200 | 3 | 2×4=8 | **75.0** ← **正好整除** |
  | `my_second_lora` | 200 | 3 | 2×4=8 | **75.0** |

  👉 **`checkpoint-75` 是 `my_first_lora`（200 条）的产物，不是 `exp1_baseline` 的。**
  `evaluate.py` 把它挂在 `exp1_baseline/` 下 —— **路径写错了**。
  （exp1 的 187.5 步配 `save_steps: 50`，检查点只会是 50 / 100 / 150，**不可能是 75**。）

  ⚠️ 同理 `my_second_lora` 也是 200 条、参数与 `my_first` 完全相同 ——
  **这两个配置会产出步数相同的适配器，只是 `output_dir` 不同。**

  > ⛔ **跑 E05 之前必须先确认 `saves/exp1_baseline/` 下到底有哪些 checkpoint。**
  > ⚠️ 本记录**无法验证** step 189 与 step 75 各自的 loss（`mlflow.db` 里 `train_loss` 只有 1 个点，
  > 即末值 **0.5603**；没有逐步 loss，也没有 `global_step`）。
- **下一步**：
  - ⬜ **人工判断缺口必须先补**——否则「改参数没用」这个结论没有证据
  - ⬜ 本组是「改参数」，**无法支撑仓库核心论点**，需要补 **E04：固定参数只换数据**

---

## 七 · 可复现性检查

- [x] 配置文件已进仓库（`configs/exp1_baseline.yaml`）
- [x] 数据卡已更新 —— **`datasets/alpaca-clean-500条/数据卡-alpaca500.md`**（2026-09-16 补齐，本实验实际用的那份）
- [ ] 脚本能一键重跑 —— ⚠️ 未记录启动命令；autoDL 路径 `/root/autodl-fs/...` 已不存在
- [x] 上表中每个数字都能从仓库文件复算出来 —— ⚠️ **仅限可能**：
      loss/runtime 在 `mlflow.db` 里可查；`samples_per_second` / `total_flos` 只在
      `configs/best_lora_config.yaml` 的转抄文本里，**原始 `all_results.json` 未进仓库**
- [ ] 若结论进了 README，已标注实验编号 —— ⬜ 待办

### ⛔ 本记录的已知缺口（不要当成已完成）

| 缺口 | 影响 |
|---|---|
| 无人工判断 / 无对照样例 | **不能声称"输出质量如何"** |
| ~~LLaMA-Factory 版本为推断~~ | ✅ 已确定为 `v0.9.5-41-g2ebe7be6` |
| ~~无数据卡（500 条那份）~~ | ✅ **已补**：`datasets/alpaca-clean-500条/数据卡-alpaca500.md`（2026-09-16） |
| 无 `all_results.json` 原件 | 两个指标无法复算 |
| 硬件/日期为推断 | 标注了「推断」，**不要当成实测** |
