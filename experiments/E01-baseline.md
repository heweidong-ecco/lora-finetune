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
| 微调框架 | LLaMA-Factory ｜ 上游 commit **`2ebe7be6`**（2026-07-24）<br>⚠️ **推断**：由 AutoDL 那份仓库的 `.git` 判定，日志未直接记录版本号 |
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

**✅ 本实验独有的配置**（E02/E03 **没有**）：
```yaml
load_best_model_at_end: true
metric_for_best_model: loss
greater_is_better: false
eval_strategy: steps
eval_steps: 25
```
⚠️ **这一条很重要** —— 它使 E01 的训练过程与 E02/E03 **不完全可比**（见 §六）。

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
  3. ⚠️ 但 E01 多了一段 E02/E03 没有的**早停+评估配置**，且三者 epochs 不同，
     **train_loss 严格来说不可直接横比**
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
| LLaMA-Factory 版本为**推断**（`2ebe7be6`） | 版本号来自 `.git` 而非训练日志 —— **不要当成实测** |
| ~~无数据卡（500 条那份）~~ | ✅ **已补**：`datasets/alpaca-clean-500条/数据卡-alpaca500.md`（2026-09-16） |
| 无 `all_results.json` 原件 | 两个指标无法复算 |
| 硬件/日期为推断 | 标注了「推断」，**不要当成实测** |
