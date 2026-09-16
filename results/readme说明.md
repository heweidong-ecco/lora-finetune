# results/ · 评测产物说明

> 建立：2026-09-16
> ⚠️ **本节最重要的结论：本目录现有的评测结果【不可用】。** 原因见下。

---

## 一 · 这里有什么

| 文件 | 内容 | 状态 |
|---|---|---|
| `evaluation_results.json` | 50 条测试样本，含 base / tuned 两个模型的回答 + 参考答案 | ⛔ **42% 失败** |
| `final_judgment.json` | 大模型裁判的对比判决（含胜率统计） | ⛔ **结论不可用** |
| `dataset_summary.txt` | 用 LLM 对测试集领域构成的总结（中英双语） | ✅ 可用 |

---

## 二 · ⛔ 为什么不可用（**这是实测，不是猜测**）

### 1. 一半的推理失败了

对 `evaluation_results.json` 逐条复算，**两边回答都非空**的只有 **19 / 50**：

| 状态 | 条数 |
|---|---|
| **两边回答都空** | **24** |
| 仅 `base_model_response` 空 | 3 |
| 仅 `tuned_model_response` 空 | 4 |
| ✅ **两边都非空（唯一可对比的）** | **19** |

### 2. 「平局」绝大多数不是真的打平，是**都答不出来**

裁判判决分布（`final_judgment.json` 详情，50 条）：

| winner | 条数 |
|---|---|
| TIE | **23** |
| ERROR | **21** |
| A（基座胜） | 5 |
| B（微调胜） | **1** |

分类（`category`）分布：

| category | 条数 |
|---|---|
| **`both_bad`（两边都差）** | **20** |
| `A_better` | 5 |
| `both_good` | **3** |
| `B_better` | 1 |
| （ERROR 无分类） | 21 |

> 👉 **真正「两边都有像样回答」的只有 3 + 5 + 1 = 9 条。**
> 也就是说 50 条里只有 **9 条**能拿来说「谁更好」。

### 3. ⚠️ 抽样一条可用的，两边回答**逐字相同**

```
instruction: Rewrite the following sentence without changing the meaning.
base  (32 字符): The sales report was inaccurate.
tuned (32 字符): The sales report was inaccurate.
```

**完全一样。**

**✅ 原因已确认**（证据在本仓库自己的文件里）：`scripts/eval/batch_evaluate.py` 第 63–66 行
把**基座模型和微调模型都传成了 `qwen3:8b`** —— 注释写着「需要先用 Ollama 加载 LoRA」，
**但那一 步当时从未做**。

👉 **那次评测比的是「qwen3:8b vs qwen3:8b」**，两边逐字相同是必然结果，**与微调效果完全无关**。

### 附带发现：胜率分母也算错了

`scripts/eval/evaluate.py` 第 217–220 行，`valid_total` 被算出来后**从未使用**，
胜率的分母用的是 `total`（**把 ERROR 也算了进去**）。见 `experiments/E05-人工判断.md` §五。

---

## 三 · 那么这份评测能说明什么

**几乎什么都说明不了。** 尤其是：

- ⛔ **不能**说「微调后模型变差」（虽然 tuned 只赢 1 条）—— 因为 42% 的请求根本没返回
- ⛔ **不能**说「微调和基座差不多」—— 23 条平局里 20 条是「都答不出来」
- ⛔ **不能**拿 `base_win_rate 10.0%` / `tuned_win_rate 2.0%` 这两个数字做任何结论

**唯一可靠的结论是：这次评测的执行环节本身是失败的，需要重做。**

> 📌 `final_judgment.json` 里自带 `errors: 21` 这个字段 —— **脚本自己就标出来了**，
> 只是当时没有据此判断「整次评测无效」。

---

## 四 · 要重做的话，必须加的三道检查

写进 `experiments/E05-人工判断.md` 的计划里：

1. **每条都要检查两个模型的回答非空** —— 空的直接标 ERROR，**不计入胜率分母**
2. **先确认两个端点真的不同** —— 同一条 prompt 跑两边，若输出**逐字相同**，要报警
3. **平局要分类** —— 区分「都好」和「都差」，`both_bad` 的平局不能算「打平」

---

## 五 · 复算方式

```bash
# 本文的每个数字都可由这两个文件复算
python3 - <<'EOF'
import json
ev = json.load(open("results/evaluation_results.json", encoding="utf-8"))
ne = lambda x: bool(str(x).strip())
print("两边都非空:", sum(1 for x in ev if ne(x["base_model_response"]) and ne(x["tuned_model_response"])))
print("两边都空  :", sum(1 for x in ev if not ne(x["base_model_response"]) and not ne(x["tuned_model_response"])))
f = json.load(open("results/final_judgment.json", encoding="utf-8"))
print("errors    :", f["errors"])
EOF
```
