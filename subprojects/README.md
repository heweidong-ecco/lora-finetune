# subprojects/ · 子方向索引

> 建立：2026-09-16
> ⚠️ **这两个子方向都没有实验记录**（无 loss、无评测、无对照样例）——
> 它们只到「脚本写好了」这一步。**这不是漏写，是确实没跑完。**

---

## 一 · 两个子方向

| 子方向 | 主题 | 基座模型 | 数据 | 状态 |
|---|---|---|---|---|
| `code-completion-lora/` | **代码补全**（FIM / 通义灵码格式） | `Qwen3-Coder-7B-Instruct` | `../datasets/code-completion代码补全/`（250 条） | 脚本齐 · ⬜ 无实验记录 |
| `rag-query-rewrite/` | **查询改写**（RAG 前置） | 小模型（3B 级） | 150 条（50 种子 × 3 改写） | 脚本齐 · ⬜ 无实验记录 |

---

## 二 · code-completion-lora/

| 文件 | 作用 |
|---|---|
| `README.md` | 完整操作流程：数据格式（FIM vs 通义灵码）→ 数据来源 → 训练 → 导出 → Ollama → 测试 |
| `extract_code_data.py` | 从 **ModelScope `codefuse-ai/CodeExercise-Python-27k`** 提取 Python 片段（含 `ast.parse` 语法过滤） |
| `local_code_extractor.py` | **备选**：扫本机 `site-packages` 提取，不依赖下载（README 称其为「最快有效方法」） |
| `check_quality.py` | 数据质检 |

### ⚠️ 三个已知问题

1. **数据来源未确认** —— 上面两个脚本**写同一个输出文件**，250 条到底是哪个产出的**没有记录**。
   （数据文件本身已按最保守方案撤出仓库，见 `../datasets/code-completion代码补全/数据卡-codecompletion.md`）
2. **注释与代码不一致** —— `extract_code_data.py` 文件头仍写「从 The Stack 提取」，
   但生效的代码用的是 ModelScope 那个数据集（The Stack 是门控数据集，用不了）
3. **无实验记录** —— README 说「训练约 3–5 分钟完成」，但**没有 loss、没有评测、没有对照样例**

---

## 三 · rag-query-rewrite/

| 文件 | 作用 |
|---|---|
| `README.md` | 操作步骤（标题是空的，正文就是「第1步：确认环境」直接开始） |
| `generate_seeds.py` | 生成 50 个「有缺陷的查询」种子（指代不明 / 用词模糊 / 信息缺失 / 口语化 / 多意图） |
| `generate_rewrites.py` | 用大模型为每个种子生成 3 个改写版本 |
| `check_quality.py` | 数据质检 |
| `test_rewrite_rag.py` | 三种方案对比（无改写 / 云端改写 / 本地微调改写） |

### ⚠️ 两个已知问题

1. **`test_rewrite_rag.py` 只测延迟，不测质量** —— 脚本里的「检索」是占位函数（`simulate_search()`），
   **没有接向量库**；也**没有裁判 prompt、没有胜率、没有打分**
2. **无人工判断记录** —— 只在一处练习题里写了「随机抽 10 条人工判断通过率」，**没有通过率数字**

---

## 四 · 要把这两个子方向补齐，需要

- ⬜ 各自的训练实验记录（loss / 时长 / 版本）
- ⬜ 评测口径与结果（不能只看延迟）
- ⬜ `code-completion` 的来源与许可证确认

> 📌 两者都可以复用 `../experiments/E05-人工判断.md` 的口径与
> `../scripts/eval/make_comparison_samples.py` 的脚本。
