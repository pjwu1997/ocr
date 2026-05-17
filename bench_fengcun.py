"""Run /v1/aiocr/analyze against 封存 fixtures and write a markdown summary."""
import argparse
import json
import os
import sys
import time
from pathlib import Path
import requests

ROOT = Path("/home/asiamath/Users/PJ/ocr")
FENGCUN = ROOT / "封存"
BASE_URL = "http://localhost:7860"
FLOWS = ["marriage", "funeral", "contract", "onboarding"]


def login() -> requests.Session:
    s = requests.Session()
    r = s.post(f"{BASE_URL}/login", data={"username": "admin", "password": "123"},
               allow_redirects=False, timeout=10)
    if r.status_code not in (200, 303, 302):
        raise RuntimeError(f"Login failed: {r.status_code} {r.text}")
    return s


def collect_cases(flow_key: str, limit: int | None) -> list[dict]:
    flow_dir = FENGCUN / flow_key
    cases = []
    for case_dir in sorted(flow_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        gt_path = case_dir / "ground_truth.json"
        if not gt_path.exists():
            continue
        gt = json.loads(gt_path.read_text(encoding="utf-8"))
        pdf = next(case_dir.glob("*.pdf"), None)
        if pdf is None:
            continue
        cases.append({"case_id": gt["case_id"], "gt_doctype": gt["document_type"],
                      "pdf": str(pdf)})
        if limit and len(cases) >= limit:
            break
    return cases


def run_case(s: requests.Session, flow_key: str, case: dict) -> dict:
    pdf_name = os.path.basename(case["pdf"])
    manifest = json.dumps([{"file_id": "FILE-001", "file_name": pdf_name}])
    t0 = time.time()
    with open(case["pdf"], "rb") as fh:
        files = {"files": (pdf_name, fh, "application/pdf")}
        data = {"case_id": case["case_id"], "flow_key": flow_key,
                "file_manifest": manifest}
        r = s.post(f"{BASE_URL}/v1/aiocr/analyze", data=data, files=files,
                   timeout=600)
    elapsed = time.time() - t0
    if not r.ok:
        return {"case_id": case["case_id"], "gt_doctype": case["gt_doctype"],
                "elapsed": elapsed, "error": f"HTTP {r.status_code}: {r.text[:200]}"}
    js = r.json()
    docs = js.get("documents", [])
    if not docs:
        return {"case_id": case["case_id"], "gt_doctype": case["gt_doctype"],
                "elapsed": elapsed, "error": "no documents",
                "warnings": js.get("warnings", [])}
    doc = docs[0]
    fields = doc.get("fields", [])
    return {
        "case_id": case["case_id"],
        "gt_doctype": case["gt_doctype"],
        "predicted_code": doc["doc_type"]["code"],
        "predicted_label": doc["doc_type"]["label"],
        "type_confidence": doc["doc_type"]["confidence"],
        "elapsed": round(elapsed, 1),
        "n_fields": len(fields),
        "n_filled": sum(1 for f in fields if f["value"]),
        "n_review": sum(1 for f in fields if f["needs_review"]),
        "avg_conf": round(sum(f["confidence"] for f in fields) / max(1, len(fields)), 2),
        "fields": fields,
    }


def classification_match(predicted_label: str, gt_doctype: str) -> str:
    """Loose match: ground truth uses '/' as alternates ('喜帖/結婚證明')."""
    if not predicted_label:
        return "miss"
    gt_alts = [p.strip() for p in gt_doctype.split("/")]
    for alt in gt_alts:
        # Substring either direction
        if alt and (alt in predicted_label or predicted_label in alt):
            return "match"
    return "miss"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-flow", type=int, default=1,
                    help="how many cases per flow (None=all)")
    ap.add_argument("--out", default=str(ROOT / "experiments" / "fengcun_summary.md"))
    ap.add_argument("--json-out", default=str(ROOT / "experiments" / "fengcun_results.json"))
    args = ap.parse_args()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    s = login()
    print(f"Logged in. Running {args.per_flow} cases/flow…", flush=True)

    all_results = {}
    overall_start = time.time()
    for flow_key in FLOWS:
        cases = collect_cases(flow_key, args.per_flow)
        print(f"\n[{flow_key}] {len(cases)} cases:", flush=True)
        rows = []
        for c in cases:
            print(f"  - {c['case_id']} (gt={c['gt_doctype']})…", end=" ", flush=True)
            try:
                res = run_case(s, flow_key, c)
                tag = classification_match(res.get("predicted_label", ""), c["gt_doctype"])
                res["match"] = tag
                conf = res.get("type_confidence", "n/a")
                print(f"{res.get('predicted_code','ERR')} ({tag}) conf={conf} "
                      f"fields={res.get('n_filled','?')}/{res.get('n_fields','?')} "
                      f"{res['elapsed']}s", flush=True)
            except Exception as e:
                res = {"case_id": c["case_id"], "gt_doctype": c["gt_doctype"],
                       "error": str(e), "match": "miss"}
                print(f"ERROR: {e}", flush=True)
            rows.append(res)
        all_results[flow_key] = rows

    total_elapsed = round(time.time() - overall_start, 1)

    # Write JSON
    Path(args.json_out).write_text(
        json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Build markdown
    md = ["# 封存 Benchmark — /v1/aiocr/analyze\n",
          f"_Per-flow: {args.per_flow}, Total elapsed: {total_elapsed}s_\n"]

    # Overall classification accuracy
    md.append("\n## Classification accuracy\n")
    md.append("| Flow | Cases | Matched | Accuracy |")
    md.append("|---|---:|---:|---:|")
    for flow_key, rows in all_results.items():
        n = len(rows)
        m = sum(1 for r in rows if r.get("match") == "match")
        acc = f"{m/n*100:.0f}%" if n else "—"
        md.append(f"| {flow_key} | {n} | {m} | {acc} |")

    # Per-case details
    for flow_key, rows in all_results.items():
        md.append(f"\n## {flow_key}\n")
        md.append("| Case | GT doctype | Predicted | Match | Type conf | Fields filled | Avg conf | Time |")
        md.append("|---|---|---|---|---:|---:|---:|---:|")
        for r in rows:
            if "error" in r:
                md.append(f"| {r['case_id']} | {r['gt_doctype']} | — | miss | — | — | — | ERR: {r['error'][:60]} |")
                continue
            md.append(
                f"| {r['case_id']} | {r['gt_doctype']} | {r['predicted_label']} (`{r['predicted_code']}`) | "
                f"{'✓' if r['match']=='match' else '✗'} | "
                f"{r['type_confidence']} | {r['n_filled']}/{r['n_fields']} | {r['avg_conf']} | {r['elapsed']}s |"
            )

        # Per-case field detail (collapsible)
        md.append("\n### Field-level detail\n")
        for r in rows:
            if "error" in r or not r.get("fields"):
                continue
            md.append(f"\n**{r['case_id']}** → {r['predicted_label']}")
            md.append("")
            md.append("| Field | Value | Normalized | Conf | Review |")
            md.append("|---|---|---|---:|:-:|")
            for f in r["fields"]:
                v = (f["value"] or "—").replace("|", "\\|").replace("\n", " ")[:60]
                n = (f["normalized_value"] or "").replace("|", "\\|")[:30]
                md.append(f"| {f['label']} (`{f['key']}`) | {v} | {n} | {f['confidence']} | "
                          f"{'⚠' if f['needs_review'] else '✓'} |")

    Path(args.out).write_text("\n".join(md), encoding="utf-8")
    print(f"\nWrote: {args.out}", flush=True)
    print(f"Wrote: {args.json_out}", flush=True)


if __name__ == "__main__":
    main()
