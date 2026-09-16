# 训练产物 · 说明与**读数前必看**

> 收录：2026-09-16 ｜ 共 **110 个文件 / 约 0.5 MB**
> 来源：五组训练的 `saves/` 目录，**权重（`adapter_model.safetensors`）与优化器状态（`optimizer.pt`）
> 因体积过大（单个 85–170 MB）已剔除**，只保留用于**复算**的小文本文件。

**为什么收这些**：本库第一铁律要求「每个数字都要能复算」。
收了这些文件，`experiments/E01~E03` 里的每一个 loss 数字，**外人可以自己验**。

---

## 一 · 五组运行

| 目录 | 对应配置 | 总步数 | `all_results.json` 的 `train_loss` | `train_runtime` |
|---|---|---|---|---|
| `exp1_baseline/` | `configs/exp1_baseline.yaml` | **189** | 0.5602585398961627 | 181.5449 s |
| `exp2_rank16/` | `configs/exp2_rank16.yaml` | **189** | 0.8462307465770257 | 300.9799 s |
| `exp3_lr5e5_epoch5/` | `configs/exp3_lr5e5_epoch5.yaml` | **315** | 0.9941337812514532 | 479.0966 s |
| `qwen3-8B-lora-my-first/` | `configs/my_first_lora.yaml` | **75** | ⚠️ **0.0**（见 §三） | ⚠️ 14.3212 s |
| `qwen3-8B-lora-my-second/` | `configs/my_second_lora.yaml` | **75** | 1.0587651125590007 | 120.5208 s |

**总步数可精确复算**：`ceil(条数 ÷ (batch 2 × grad_accum 4)) × epochs`

```
ceil(500/8) × 3 = 63 × 3 = 189   → exp1 / exp2
ceil(500/8) × 5 = 63 × 5 = 315   → exp3
ceil(200/8) × 3 = 25 × 3 =  75   → my-first / my-second
```

---

## 二 · ⚠️ 三个「读数陷阱」（**不看清一定会读错**）

### ① `train_loss` 与「最后一条逐步记录」**不是同一个量**

以 `exp1_baseline` 为例：

| 名称 | 值 | 在哪个文件 |
|---|---|---|
| **`train_loss`**（HF 汇总的末值） | **0.5602585398961627** | `all_results.json` / `trainer_state.json` 末条 |
| **最后一条逐步记录**（step 180） | **0.810824** | `trainer_state.json` → `log_history` |

两者相差很大，**但都不是错的** —— 它们是不同的量。
👉 **引用时必须写清用的是哪一个**，否则同一个实验会得出两个"正确"的 loss。

### ② ⚠️ `exp1_baseline/trainer_state.json` 的 `log_history` **混入了另一次运行的记录**

该文件的前 7 条（step 10–70）**不属于 exp1**：

| 判断依据 | 说明 |
|---|---|
| epoch 字段 | 前 7 条的 epoch 是 0.41 / 0.82 / … / 2.82 → **25 步/epoch**，即 **200 条**那组配置 |
| exp1 本身 | 是 **500 条** → **63 步/epoch** |
| 回跳 | step 70 的 epoch=2.82，step 80 突然变成 1.27 —— **不连续** |

👉 **读 exp1 的曲线时，请从 step 80 起读**（`exp2` / `exp3` 无此问题，已核过）。

### ③ `my-first` 的 `train_loss = 0.0` 是**产物本身就有的**，不只是显示问题

`/qwen3-8B-lora-my-first/all_results.json` 与 `train_results.json` 里都是 `"train_loss": 0.0`，
且 `train_runtime` 只有 **14.32 秒**（同配置的 my-second 是 120.52 秒，慢 8.4 倍）。

👉 **这一组的数据不可用于任何比较** —— 它的 loss 与耗时都不可信。
（对应 mlflow 里那次 `train_loss = 0.0` 的运行，见 `experiments/README.md` §二。）

---

## 三 · 每个目录里有什么

| 文件 | 作用 |
|---|---|
| `all_results.json` ★ | **权威末值** —— `train_loss` / `train_runtime` / `train_samples_per_second` |
| `train_results.json` | 与 `all_results.json` 内容相同（实测五组均一致） |
| `trainer_state.json` ★ | `log_history`（**逐步 loss**）、`global_step`、`best_model_checkpoint` |
| `trainer_log.jsonl` | 逐步 loss 的 jsonl 版（`current_steps` / `loss` / `lr` / `elapsed_time`） |
| `training_loss.png` ★ | loss 曲线图 |
| `adapter_config.json` | 基座模型路径、`r` / `lora_alpha` / `target_modules` |
| `training_args.bin` | **实际用了哪些参数的权威记录**（二进制，读它需要 `torch`） |
| `checkpoint-*/` | 各检查点的 `trainer_state.json` / `adapter_config.json` 等 |
| `README.md` / `chat_template.jinja` / `tokenizer_config.json` | HF 自动生成，**与复算无关** |

---

## 四 · 复算示例

```bash
# ① 三次实验的末值 loss（与 experiments/README.md 的表对得上）
for r in exp1_baseline exp2_rank16 exp3_lr5e5_epoch5; do
  echo -n "$r: "
  python3 -c "import json;d=json.load(open('experiments/artifacts训练产物/$r/all_results.json'));print(d['train_loss'], d['train_runtime'])"
done

# ② exp1 的逐步 loss（注意从 step 80 起读，见 §二-②）
python3 -c "
import json
d=json.load(open('experiments/artifacts训练产物/exp1_baseline/trainer_state.json'))
for x in d['log_history']:
    if 'loss' in x and x['step']>=80: print(x['step'], round(x['loss'],6))
"

# ③ 核实「早停从未生效」：五组的 best_model_checkpoint 应全为 None
python3 -c "
import json,glob
for p in sorted(glob.glob('experiments/artifacts训练产物/*/trainer_state.json')):
    d=json.load(open(p)); print(p.split('/')[2], '->', d.get('best_model_checkpoint'))
"
```

---

## 五 · 没收录的东西

| 文件 | 体积 | 为什么不在 |
|---|---|---|
| `adapter_model.safetensors` | **85 MB / 个** | 权重应放 HuggingFace / 魔搭，仓库只放链接（见 `CLAUDE.md` 第二铁律） |
| `optimizer.pt` | **171 MB / 个** | 优化器状态，只在续训时有用 |
| `tokenizer.json` | 11 MB / 个 | 与基座模型重复 |
| `rng_state.pth` / `scheduler.pt` | 各 1–14 KB | 训练状态，与复算无关 |
| `.ipynb_checkpoints/` | — | 编辑器临时文件 |

> 📌 **因此：这些产物能复算「数字」，但不能复现「模型」。** 要跑推理请重新训练，或找权重的外链。
