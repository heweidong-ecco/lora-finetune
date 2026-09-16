# 上游 LLaMA-Factory 官方文件 · 勿改

> 按你的决定（2026-09-16）：**保留，但单独放一边，标注「上游，勿改」**。

---

## 一 · 它们现在在哪（**没有动过**）

| 位置 | 是什么 | 体积 |
|---|---|---|
| `…/lora-finetune-原始文件归档/AutoDL下载/LLaMA-Factory/` | 一份**完整的 LLaMA-Factory 仓库**（含 `.git/`），里面**混着你的文件** | 75 MB |
| `…/lora-finetune-原始文件归档/本机/LLaMA-Factory/` | 本机侧，**只有你自己的文件**，没有上游代码 | 404 KB |

> 📦 **2026-09-16：整块素材已移出本仓库**，位于
> `/Users/heweidong/Desktop/Product/lora-finetune-原始文件归档/`。
> 本文件中的相对路径均以该归档为根。

---

## 二 · 为什么没有复制进「整合后」

1. **不是你的代码** —— 是 [hiyouga/LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) 的上游开源项目
   （根目录 `LICENSE`、`CITATION.cff`、`.git/` 都在）
2. **体积** —— 光 `src/` 就 3.2 MB、`.git/` 15 MB，复制一份纯属冗余
3. **它本来就已经「单独放一边」了** —— 是一个独立文件夹，没有被拆散

> ⛔ **不要把这些文件当自己的作品提交。** 上游有 `Apache-2.0` 许可证和自己的版权声明，
> 混进「个人开源项目」会构成**署名不实**。

---

## 三 · 上游文件是哪一些（用于识别）

| 目录 / 文件 | 归属 |
|---|---|
| `src/`、`tests/`、`tests_v1/`、`docs/`、`docker/`、`requirements/`、`assets/`、`.github/`、`scripts/` | **上游** |
| `README.md`、`README_zh.md`、`LICENSE`、`CITATION.cff`、`Makefile`、`pyproject.toml`、`MANIFEST.in` | **上游** |
| `.git/`、`.gitignore`、`.pre-commit-config.yaml`、`.dockerignore`、`.gitattributes` | **上游** |
| `examples/` 下的 `qwen3_*.yaml`、`llama3_*.yaml`、`extras/`、`train_full/`、`merge_lora/`、`inference/` | **上游** |
| `data/` 下的 `*_demo.json`、`*_demo.jsonl`、`mllm_demo_data/`、`identity.json` | **上游** |
| `CLAUDE.md`、`.ai/CLAUDE.md`、`.claude/skills/llamafactory-sft/SKILL.md` | **上游** —— ✅ 已用 `git ls-files` 验证，三个文件都被 LLaMA-Factory 仓库追踪（内容也是英文的 `make style` / `make quality` 指引）<br>（原先标为「可疑」，2026-09-16 已排除） |

---

## 三之二 · ⭐ 上游版本（可复现性关键）

用 `.git` 判定，归档中的 `AutoDL下载/LLaMA-Factory/` 停在上游：

```
commit 2ebe7be6    日期 2026-07-24    [ci] pin ruff version and fix lint errors (#10681)
```

**这个版本号有价值**：`experiments/E01~E03` 三组实验的日期推断为 ≈2026-07-27，
**紧接在该 commit 之后**，时间吻合。

> ⚠️ **但这是推断，不是日志记录** —— 训练日志里没有写框架版本号。
> 写 README 时可以说「实验时 AutoDL 上的仓库停在 `2ebe7be6`」，
> **不要写成「已确认实验用的就是这个版本」**。

👉 建议在 README 的复现说明里写明此版本，或直接改成 `pip install llamafactory==<对应版本号>`。

### ⚠️ 上游目录里**混着你的文件**（这些已经提出去放进「整合后」了）

| 混在 | 你的文件 |
|---|---|
| `AutoDL下载/LLaMA-Factory/data/` | `my_dataset.json`（**500 条**，评测用） |
| `AutoDL下载/LLaMA-Factory/examples/train_lora/` | `my_first_lora.yaml`、`my_second_lora.yaml`、`exp1~3`、`best_lora_config.yaml` |
| `AutoDL下载/LLaMA-Factory/BadCase_AI_evaluation_pipeline/` | 整个目录（脚本 + 产物 + 一份 42 MB 数据） |
| `AutoDL下载/LLaMA-Factory/` 根 | `mlflow.db`、`.env.local` |

---

## 四 · 建议

如果要**公开**这个仓库，别把上游仓库整个放进你自己的 repo。两种做法：

| 做法 | 说明 |
|---|---|
| **(a) 只留增量 + 说明依赖**（推荐） | 你自己的 repo 里不放上游代码，README 写「基于 LLaMA-Factory vX.Y.Z，安装见官方文档」，并**记录你 clone 的具体版本/commit** |
| (b) 用 fork | 如果你确实改了上游代码，就 fork，不要另外建一个 repo 装它的副本 |

> 📌 无论哪种，**都要在 README 里写明上游项目和版本**，这是许可证要求，也是诚实标注。
