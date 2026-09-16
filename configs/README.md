# configs/ · 训练配置索引

> 建立：2026-09-16 ｜ **本文件原是一段旧笔记，2026-09-16 按实际内容重写**
>
> ⚠️ **本目录所有配置里的 `model_name_or_path` 与 `output_dir` 都是原环境（AutoDL）路径**
> （`/root/autodl-fs/...`），**直接跑会失败**，需改成你自己的路径。这是**已知缺陷**。

---

## 一 · 9 个配置

### ✅ 已跑过并留下产物的（5 个）

| 配置 | 变量 | 总步数 | 末值 loss | 产物 |
|---|---|---|---|---|
| `exp1_baseline.yaml` | 基线（rank 8 · lr 2e-4 · 3 ep） | **189** | 0.5602585398961627 | `experiments/artifacts训练产物/exp1_baseline/` |
| `exp2_rank16.yaml` | **rank 8→16** | **189** | 0.8462307465770257 | `…/exp2_rank16/` |
| `exp3_lr5e5_epoch5.yaml` | **lr÷4 · 3→5 ep** | **315** | 0.9941337812514532 | `…/exp3_lr5e5_epoch5/` |
| `my_first_lora.yaml` | 首次跑通（200 条） | **75** | ⚠️ **0.0** | `…/qwen3-8B-lora-my-first/` |
| `my_second_lora.yaml` | 与 my-first **参数完全相同** | **75** | 1.0587651125590007 | `…/qwen3-8B-lora-my-second/` |

**总步数公式**：`ceil(条数 ÷ (batch 2 × grad_accum 4)) × epochs`
→ `ceil(500/8)×3 = 189` ｜ `ceil(500/8)×5 = 315` ｜ `ceil(200/8)×3 = 75`

> ⚠️ `my_first_lora` 的产物**本身异常**（`train_loss=0.0`、runtime 仅 14.32s，
> 同配置的 my-second 是 120.52s）—— **该组数据不可用于任何比较**。
> 详见 `../experiments/artifacts训练产物/README.md` §二。

### ⬜ 还没跑的（2 个）

| 配置 | 用途 | 状态 |
|---|---|---|
| `E04-A组-random随机194.yaml` | E04 实验组 A：从全部 51760 条随机抽 194 | ⬜ **方案已就绪**，缺 GPU |
| `E04-B组-front550前段194.yaml` | E04 实验组 B：从前 550 区块抽 194 | ⬜ 同上 |

**两个配置的 `diff` 应只有 `dataset` 与 `output_dir` 两行不同** ——
跑之前先 `diff` 确认，这是 E04 能归因的前提。
详见 `../experiments/E04-数据集对照.md`。

### 不是「可跑的配置」的 2 个

| 文件 | 实际是什么 |
|---|---|
| `best_lora_config.yaml` | **混杂文件**：模板占位（`[最优rank]`）+ 真实参数块 + 一张 MLflow 抄录表 + 分析笔记。⚠️ 其中那张三行表是**按时间倒序取最近 3 次运行**的结果，**不是三次实验**，见 `../experiments/README.md` §二 |
| `YAML_LoRA通用优化策略` | 参数速查说明（无 `.yaml` 后缀，不是可跑配置） |

> 📌 另有 `code_completion_lora.yaml` —— 属于**子方向**（代码补全），
> 配套数据卡见 `../datasets/code-completion代码补全/`。⚠️ **无训练产物、无实验记录。**

---

## 二 · ⚠️ 一个被证伪的建议（**别照抄**）

`best_lora_config.yaml` 与 `YAML_LoRA通用优化策略` 里都有一段
「**早停与评估（新增）**」：

```yaml
load_best_model_at_end: true
metric_for_best_model: loss
greater_is_better: false
eval_strategy: steps
eval_steps: 25
```

### ⛔ 这段**从未生效过** —— 2026-09-16 由训练产物核实

| 证据 | 说明 |
|---|---|
| 五组训练的 `trainer_state.json` 里 **`best_model_checkpoint` 全是 `None`** | 早停/评估**一次都没触发过** |
| `exp1_baseline/` 下只有 `checkpoint-100` / `checkpoint-189` | 对应 `save_steps: 100`，**不是 50** |

**原因**：`eval_strategy: steps` **需要配置验证集**（`val_size` 或 `eval_dataset`）才会触发评估。
这三份配置里**都没有** —— 所以从未产生过任何一次评估。

👉 **想用早停，必须先加验证集。** 光加那 5 行没用。
详见 `../experiments/E01-baseline.md` §四。

---

## 三 · ⚠️ `exp1_baseline.yaml` 收录的是「实际跑过的那版」

2026-09-16 修正过一次 —— 此前本仓库收录的是**本地改过、但从未跑过**的版本
（`save_steps: 50` + 上文那段早停）。**判据是训练产物**（只产出 checkpoint-100/189）。

那个改过的版本仍以注释形式保留在 `exp1_baseline.yaml` 文件末尾，**仅供对照，不要拿去跑**。

> 📌 **教训**：整理历史文件时，**「内容更全」≠「实际跑过的那版」**。
> 判断依据要看**产物**，不看文件的完整度。这条已写进 `../CLAUDE.md` 第一铁律。
