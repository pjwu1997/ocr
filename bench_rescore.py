"""LLM-as-judge re-scoring of fengcun_full_results.json."""
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from openai import OpenAI

ROOT = Path("/home/asiamath/Users/PJ/ocr")
RESULTS = ROOT / "experiments" / "fengcun_full_results.json"
OUT_MD = ROOT / "experiments" / "fengcun_full_summary_v2.md"
OUT_JSON = ROOT / "experiments" / "fengcun_full_rescore.json"

QWEN_URL = "http://localhost:8010/v1"
QWEN_MODEL = "qwen3.5-27b"


def judge(client: OpenAI, gt: str, pred_label: str, pred_code: str) -> tuple[bool, str]:
    prompt = (
        f"判斷以下兩個文件類型名稱是否指相同類型：\n"
        f"A：{gt}\n"
        f"B：{pred_label}（代碼 {pred_code}）\n"
        f"如果語意相同或互為同義（例如『體檢資料』與『體檢報告』），回答 yes；否則回答 no。\n"
        f"只回答 yes 或 no，不要解釋。"
    )
    try:
        r = client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": ""},
            ],
            max_tokens=8,
            temperature=0.0,
            extra_body={"add_generation_prompt": False, "continue_final_message": True},
        )
        out = (r.choices[0].message.content or "").strip().lower()
        return out.startswith("yes"), out
    except Exception as e:
        return False, f"ERR: {e}"


def main():
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    client = OpenAI(base_url=QWEN_URL, api_key="dummy")

    judge_pairs = []  # (flow, case_id, gt, pred_label, pred_code, original_match)
    for flow_key, rows in data.items():
        for r in rows:
            if r.get("match") == "miss" and not r.get("error"):
                judge_pairs.append((
                    flow_key,
                    r["case_id"],
                    r["gt_doctype"],
                    r.get("predicted_label", ""),
                    r.get("predicted_code", ""),
                ))

    print(f"Judging {len(judge_pairs)} miss pairs with Qwen…")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=8) as ex:
        verdicts = list(ex.map(
            lambda p: judge(client, p[2], p[3], p[4]),
            judge_pairs,
        ))
    elapsed = time.time() - t0
    print(f"Judged in {elapsed:.1f}s")

    # Build flips dict
    flips = {}  # (flow, case_id) → (is_match, raw)
    for (flow, case_id, gt, pred_label, pred_code), (is_match, raw) in zip(judge_pairs, verdicts):
        flips[(flow, case_id)] = (is_match, raw, gt, pred_label)

    # Recompute stats
    summary = {}
    for flow_key, rows in data.items():
        strict_match = sum(1 for r in rows if r.get("match") == "match")
        semantic_match = strict_match
        flipped = []
        for r in rows:
            if r.get("match") == "miss" and not r.get("error"):
                key = (flow_key, r["case_id"])
                if key in flips and flips[key][0]:
                    semantic_match += 1
                    flipped.append((r["case_id"], flips[key][2], flips[key][3]))
        summary[flow_key] = {
            "total": len(rows),
            "strict_match": strict_match,
            "semantic_match": semantic_match,
            "flipped": flipped,
        }

    # Write JSON
    OUT_JSON.write_text(json.dumps({
        "verdicts": [
            {"flow": p[0], "case_id": p[1], "gt": p[2], "pred_label": p[3], "pred_code": p[4],
             "judge_yes": v[0], "judge_raw": v[1]}
            for p, v in zip(judge_pairs, verdicts)
        ],
        "summary": {k: {"total": v["total"], "strict_match": v["strict_match"],
                        "semantic_match": v["semantic_match"]}
                    for k, v in summary.items()},
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write markdown
    md = ["# 封存 Benchmark — Strict vs Semantic Classification Accuracy\n",
          f"_LLM-as-judge re-scoring using Qwen3.5-27B on {len(judge_pairs)} strict-miss pairs. Judge time: {elapsed:.1f}s._\n",
          "\n## Overall accuracy\n",
          "| Flow | Cases | Strict match | Semantic match (LLM judge) | Strict % | Semantic % |",
          "|---|---:|---:|---:|---:|---:|"]
    total = strict_total = sem_total = 0
    for fk, s in summary.items():
        total += s["total"]
        strict_total += s["strict_match"]
        sem_total += s["semantic_match"]
        sp = f"{s['strict_match']/s['total']*100:.0f}%"
        sem = f"{s['semantic_match']/s['total']*100:.0f}%"
        md.append(f"| {fk} | {s['total']} | {s['strict_match']} | {s['semantic_match']} | {sp} | {sem} |")
    md.append(f"| **all** | **{total}** | **{strict_total}** | **{sem_total}** | "
              f"**{strict_total/total*100:.0f}%** | **{sem_total/total*100:.0f}%** |")

    md.append("\n## Cases the LLM judge flipped (strict-miss → semantic-match)\n")
    for fk, s in summary.items():
        if not s["flipped"]:
            continue
        md.append(f"\n### {fk}\n")
        md.append("| Case | GT label | Predicted label |")
        md.append("|---|---|---|")
        for case_id, gt, pred in s["flipped"]:
            md.append(f"| {case_id} | {gt} | {pred} |")

    md.append("\n## Cases that remain misses even after fuzzy judging\n")
    for fk, rows in data.items():
        remaining = []
        for r in rows:
            if r.get("match") == "miss" and not r.get("error"):
                key = (fk, r["case_id"])
                if key not in flips or not flips[key][0]:
                    remaining.append((r["case_id"], r["gt_doctype"], r.get("predicted_label", "")))
        if not remaining:
            continue
        md.append(f"\n### {fk}\n")
        md.append("| Case | GT label | Predicted label |")
        md.append("|---|---|---|")
        for case_id, gt, pred in remaining:
            md.append(f"| {case_id} | {gt} | {pred} |")

    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote: {OUT_MD}")
    print(f"Wrote: {OUT_JSON}")
    print(f"\nOverall: strict {strict_total}/{total} ({strict_total/total*100:.0f}%) → "
          f"semantic {sem_total}/{total} ({sem_total/total*100:.0f}%)")


if __name__ == "__main__":
    main()
