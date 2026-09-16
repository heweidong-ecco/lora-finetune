#!/usr/bin/env python3
"""
生成「对照样例」供人工判断 —— 把同一条 prompt 同时喂给两个模型，并排输出。

为什么需要它
------------
本库历史上做过一次「基座 vs 微调」的评测，但**结果不可用**：
50 条里 24 条两边回答都是空的，裁判把其中 20 条算成了「平局」。
完整分析见 `results/readme说明.md`。

本脚本把那次踩的坑固化成**三道自动检查**：
  ① 两边回答都为空的条目 → 标 ERROR，**不计入胜率分母**
  ② 同一条 prompt 两边输出**逐字相同** → 报警（提示两个端点可能其实是同一个模型）
  ③ 平局分类留给人工，但**强制要求分开记 `both_good` 与 `both_bad`**（见产出的 md）

用法
----
    # Ollama 后端
    python scripts/eval/make_comparison_samples.py \
        --prompts datasets/alpaca-clean-500条/my_test_dataset.json \
        --model-a qwen3:8b --model-b qwen3:8b-e04-a --backend ollama \
        --out results/comparison_samples

    # OpenAI 兼容后端（vLLM / TGI / 任何兼容服务）
    python scripts/eval/make_comparison_samples.py \
        --prompts datasets/alpaca-clean-500条/my_test_dataset.json \
        --model-a Qwen/Qwen3-8B --model-b /path/to/adapter-merged \
        --backend openai --base-url http://localhost:8001 \
        --out results/comparison_samples

产出
----
    <out>.json   结构化结果（含所有检查标记）
    <out>.md     人看的对照表，「判断」列留空供逐条填
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


# ───────────────────────── 后端调用 ─────────────────────────

def call_ollama(base_url, model, prompt, temperature, max_tokens, timeout):
    url = base_url.rstrip("/") + "/api/generate"
    body = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    return _post(url, body, timeout, lambda d: d.get("response", ""))


def call_openai(base_url, model, prompt, temperature, max_tokens, timeout):
    url = base_url.rstrip("/") + "/v1/chat/completions"
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    return _post(url, body, timeout,
                 lambda d: d["choices"][0]["message"]["content"])


def _post(url, body, timeout, extract):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return extract(json.loads(r.read().decode("utf-8")))


# ───────────────────────── 主流程 ─────────────────────────

def build_prompt(item):
    """Alpaca 三字段 → 一条 prompt。两边必须用完全相同的拼法。"""
    ins = str(item.get("instruction", "")).strip()
    inp = str(item.get("input", "")).strip()
    return f"{ins}\n\n{inp}" if inp else ins


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompts", required=True, help="JSON 数组，每条含 instruction/input")
    ap.add_argument("--model-a", required=True, help="对照组模型标识")
    ap.add_argument("--model-b", required=True, help="实验组模型标识")
    ap.add_argument("--backend", choices=["ollama", "openai"], default="ollama")
    ap.add_argument("--base-url", default=None, help="默认 ollama=http://localhost:11434, openai=http://localhost:8000")
    ap.add_argument("--temperature", type=float, default=0.0,
                    help="默认 0（贪心解码）—— 降低随机性，让对照更可比")
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--limit", type=int, default=None, help="只跑前 N 条（试跑用）")
    ap.add_argument("--out", required=True, help="输出前缀，不含扩展名")
    args = ap.parse_args()

    if args.model_a == args.model_b:
        print("⛔ --model-a 与 --model-b 相同 —— 那不是在对比两个模型，先改过来。")
        return 1

    base_url = args.base_url or (
        "http://localhost:11434" if args.backend == "ollama" else "http://localhost:8000")
    call = call_ollama if args.backend == "ollama" else call_openai

    with open(args.prompts, encoding="utf-8") as f:
        items = json.load(f)
    if args.limit:
        items = items[:args.limit]

    print(f"prompt 集  : {args.prompts}（{len(items)} 条）")
    print(f"模型 A(对照): {args.model_a}")
    print(f"模型 B(实验): {args.model_b}")
    print(f"后端       : {args.backend} @ {base_url}  temperature={args.temperature}")
    print("-" * 60)

    records, n_err, n_same = [], 0, 0
    for i, item in enumerate(items):
        p = build_prompt(item)
        rec = {"id": i, "prompt": p}
        for tag, model in (("a", args.model_a), ("b", args.model_b)):
            try:
                rec[f"{tag}_response"] = call(base_url, model, p, args.temperature,
                                              args.max_tokens, args.timeout)
                rec[f"{tag}_error"] = None
            except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError) as e:
                rec[f"{tag}_response"] = ""
                rec[f"{tag}_error"] = f"{type(e).__name__}: {e}"

        a, b = rec["a_response"].strip(), rec["b_response"].strip()
        rec["both_empty"] = (not a) and (not b)
        rec["identical"] = bool(a) and a == b          # ← 检查 ②
        if rec["both_empty"]:
            n_err += 1                                  # ← 检查 ①
        if rec["identical"]:
            n_same += 1
        rec["judgment"] = ""                            # 留给人工填
        records.append(rec)
        mark = "⛔两边都空" if rec["both_empty"] else ("⚠️逐字相同" if rec["identical"] else "✅")
        print(f"  [{i+1:>3}/{len(items)}] {mark}")

    # ── 写 JSON ──
    out_json = args.out + ".json"
    os.makedirs(os.path.dirname(out_json) or ".", exist_ok=True)
    payload = {
        "meta": {
            "prompts": args.prompts, "model_a": args.model_a, "model_b": args.model_b,
            "backend": args.backend, "base_url": base_url,
            "temperature": args.temperature, "max_tokens": args.max_tokens,
            "total": len(records),
        },
        "summary": {"both_empty": n_err, "identical": n_same,
                    "usable": len(records) - n_err},
        "records": records,
    }
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # ── 写人工判断用的 md ──
    out_md = args.out + ".md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(f"# 对照样例 · 人工判断表\n\n")
        f.write(f"> 模型 A（对照组）：`{args.model_a}`\n")
        f.write(f"> 模型 B（实验组）：`{args.model_b}`\n")
        f.write(f"> 后端 `{args.backend}` @ {base_url} ｜ temperature={args.temperature} ｜ max_tokens={args.max_tokens}\n")
        f.write(f"> 共 {len(records)} 条 ｜ 两边都空 {n_err} 条 ｜ 逐字相同 {n_same} 条\n\n")
        f.write("**判断口径**（每条只填一个，填在下面的「判断」行）：\n\n")
        f.write("| 值 | 含义 |\n|---|---|\n")
        f.write("| `A` | A 明显更好 |\n| `B` | B 明显更好 |\n")
        f.write("| `both_good` | 都好，难分高下 |\n")
        f.write("| `both_bad` | **都差**（答非所问/空/明显错误） |\n")
        f.write("| `skip` | 无法判断（题目有歧义等）—— **要写理由** |\n\n")
        f.write("> ⚠️ **`both_bad` 和 `both_good` 必须分开记。** 混在一起算「平局」，\n")
        f.write("> 就会重复历史那次评测的错误（20 条 `both_bad` 被算成打平）。\n\n---\n\n")
        for r in records:
            tag = "⛔ 两边都空（标 ERROR，不计入胜率）" if r["both_empty"] else (
                  "⚠️ 两边逐字相同（可疑！先排查是不是同一个模型）" if r["identical"] else "")
            f.write(f"## {r['id']+1}. {tag}\n\n")
            f.write(f"**Prompt**\n\n```\n{r['prompt'][:1500]}\n```\n\n")
            f.write(f"**A（{args.model_a}）**\n\n```\n{r['a_response'][:3000]}\n```\n\n")
            f.write(f"**B（{args.model_b}）**\n\n```\n{r['b_response'][:3000]}\n```\n\n")
            f.write(f"**判断**：\n\n---\n\n")

    # ── 三道检查的汇总 ──
    print("-" * 60)
    print(f"✅ 产出：{out_json}")
    print(f"✅ 产出：{out_md}")
    print()
    print("── 三道检查 ──")
    print(f"  ① 两边都空   : {n_err} / {len(records)}"
          f"{'  ⛔ 这些必须标 ERROR，不计入胜率分母' if n_err else '  ✅'}")
    print(f"  ② 逐字相同   : {n_same} / {len(records)}"
          f"{'  ⚠️ 可疑！两个端点可能其实是同一个模型，先排查' if n_same else '  ✅'}")
    print(f"  ③ 有效可判   : {len(records) - n_err} / {len(records)}")
    if n_err or n_same:
        print()
        print("  ⚠️ 有条目未通过检查 —— 建议先排查再下结论。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
