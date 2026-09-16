# scripts/ · 脚本索引

> 建立：2026-09-16
> ⚠️ **本目录的脚本都带「当时的原始路径」**（`/root/autodl-fs/...`），
> 直接跑会失败，需要改成你自己的路径 —— 这是**已知缺陷**，不是没写完。

---

## datasets/ · 数据工程（10 个）

**管线顺序**（`|` 表示并列，不是都必须跑）：

```
datasets_open_source_data.py  → datasets_clean_json.py ─┐
                                                         ├→ datasets_merge_script.py → my_dataset.json(194)
datasets_generated_data_*.py  → datasets_clean_json.py ─┘
                                                         ↓
                                          datasets_check_data_quality.py
                                          datasets_visualize_data.py
```

| 脚本 | 作用 | 产出 | 注意 |
|---|---|---|---|
| `datasets_open_source_data.py` | 从 HF 镜像下载 `yahma/alpaca-cleaned` | `datasets_open_source_data.json`（**51760 条 · 42 MB · 非合法 JSON**） | 需 `export HF_ENDPOINT=https://hf-mirror.com` |
| `datasets_clean_json.py` | 逐对象 `raw_decode` 解析 → 补全字段 → 剔除双空 → 随机抽 N | `*_cleaned_100.json` | ⚠️ `max_samples = 100` **写死在配置区**；要全量须改成 `None` |
| `datasets_generated_data_单主题.py` | 本地 Ollama `qwen3:8b` 生成，**单主题**版生效 | `datasets_generated_data.json` | ⚠️ 两个 `__main__` 块**写同一个输出名**，会互相覆盖 |
| `datasets_generated_data_多领域.py` | 同上，**多领域**版生效；输出名不冲突 | `datasets_qa_general*.json` | ⚠️ 现存数据**不是**这一版产出的 |
| `datasets_handcraft_data.py` | 手工数据 | — | ⛔ **未启用**：配套 json 里是格式占位符，不是真实数据 |
| `datasets_merge_script.py` | 开源 100 + 生成 94 合并 | `my_dataset.json`（**194 条**） | ✅ 运行结果与产物条数对得上 |
| `datasets_check_data_quality.py` | 五项质检：空值 / 长度 / 格式 / 重复 / 乱码 | `data_quality_report.txt` | ✅ 可跑 |
| `datasets_visualize_data.py` | 长度分布可视化 | 图 | ✅ 可跑 |
| `make_e04_datasets.py` | 构造 E04 的两组 194 条数据（**同源同语言同条数**） | E04-A组 / E04-B组 | ✅ 固定种子，已验证确定性 |

> 📌 **两版生成脚本为什么并存**：它们是同一次工作的两个分支（一个改命名、一个没改），
> 都有历史价值，故不删。详见 `../docs/整合报告-本机vsAutoDL.md` §三。

---

## eval/ · 评测（11 个）

**主流程**（`notes.txt` 里的原始顺序）：

```
prepare_data.py → summarize_dataset.py → [训练] → batch_evaluate.py → compare_and_judge.py
```

| 脚本 | 作用 | 产出 | 注意 |
|---|---|---|---|
| `prepare_data.py` | 取 alpaca 前 550 条 → `seed 42` 打乱 → 切 500/50 | `my_dataset.json` + `my_test_dataset.json` | ✅ **可精确复现**；⚠️ 但抽样有偏，见数据卡 §五-1 |
| `summarize_dataset.py` | 调 LLM 总结数据集领域（中英双语） | `dataset_summary.txt` | ⚠️ 是**模型判断**，非人工标注 |
| `batch_evaluate.py` | 基座 + 微调 批量推理 | `evaluation_results.json` | 🔴 **两边传的是同一个模型名**，见下 |
| `compare_and_judge.py` | LLM 裁判 A/B 对比 | `final_judgment.json` | ⚠️ 结论不可用，见下 |
| `evaluate.py` | 五步自动化评估流水线（支持多 checkpoint） | `report_*.json/.txt` | 🔴 **胜率分母含 ERROR**，见下 |
| `mlflow_data.py` | 查 MLflow 运行 | 打印表格 | ⚠️ 用 `sort_values(...).head(3)` 取**最近 3 次**，容易被误读成「三次实验」 |
| `make_comparison_samples.py` | **E05 用**：同 prompt 喂两个模型，出对照表 | `comparison_samples.json/.md` | ✅ 含三道检查（空值 / 逐字相同 / 平局须分类） |
| `test_evaluation.py` · `test_lora_evaluation.py` | 早期测试脚本 | — | 历史遗留 |
| `notes.txt` | 操作记录 + 脚本体系表 | — | 有用的流程说明 |

### 🔴 三个已查实的缺陷（**改动前必看**）

| 缺陷 | 证据 |
|---|---|
| **基座与微调用了同一个模型** | `batch_evaluate.py:63-66` —— 两处都传 `"qwen3:8b"`。所以 `evaluation_results.json` 里的对比**与微调效果无关** |
| **胜率分母把 ERROR 算了进去** | `evaluate.py:217-220` —— `valid_total` 算出来**从未被使用**，`win_rate` 除的是 `total` |
| **早期抽查的两边回答逐字相同** | 见 `../results/README.md` §二 |

> 📌 这三条都已写进 `../experiments/E05-人工判断.md` 作为**必须避开的坑**。
> **不要照抄这些脚本去跑 E04/E05。**
