# deploy/ · 部署与量化索引

> 建立：2026-09-16
> ⚠️ **本目录的路径都是原环境（AutoDL）的**，直接跑会失败，需改成你自己的。

---

## 一 · 这里有什么

| 文件 | 作用 |
|---|---|
| `Modelfile.exp1_q4km` | Ollama 的 Modelfile（`exp1` 的 Q4_K_M GGUF 版）—— 供 `ollama create` 用 |
| `Ollama部署微调模型.md` | 把 LoRA 适配器部署到 Ollama 的完整步骤 |
| `训练数据速查.md` | 训练参数速查表（rank / alpha / lr / epochs 的含义与调优方向） |
| `out-GGUF-Script/llama_cpp_outGGUF_q4km.py` | 用 llama.cpp 把模型导出为 **Q4_K_M** 量化 GGUF |
| `out-GGUF-Script/README.md` | 上面那个脚本的用法（含合并 LoRA 权重的方案） |

---

## 二 · 整条链路

```
训练产出 adapter
      ↓  llamafactory-cli export（合并 LoRA 到基座）
  完整模型目录
      ↓  out-GGUF-Script/llama_cpp_outGGUF_q4km.py
  Q4_K_M 量化 GGUF
      ↓  Modelfile + ollama create
  可 ollama run 的模型
```

---

## 三 · ⚠️ 两处要留意

1. **本目录的文件提到「yaml 文件中有早停，记得查看最后输出的 loss」**
   —— ⚠️ **该早停配置从未生效过**（五组训练的 `best_model_checkpoint` 全为 `None`，
   因为没有配置验证集）。**不要据此判断"该用哪个 checkpoint"。**
   详见 `../experiments/E01-baseline.md` §四。

2. **`out-GGUF-Script/README.md` 里的「方案」涉及 checkpoint 选择**
   —— 但仓库里的 `exp1_baseline` 实际只产出过 `checkpoint-100` / `checkpoint-189`
   （**没有 `checkpoint-75`**）。选 checkpoint 前先看实际目录里有什么，
   详见 `../experiments/E01-baseline.md` §六。

> 📌 **本目录没有部署结果记录** —— 导出过哪些 GGUF、量化前后差多少，**均未留档**。
