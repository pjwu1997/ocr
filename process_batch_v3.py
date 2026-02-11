#!/usr/bin/env python3
"""
Batch OCR with PaddleOCR-VL + vLLM continuous batching.

Improvements over v2:
  - Single pipeline instance (not re-created per file)
  - vl_rec_max_concurrency sends concurrent requests to vLLM,
    triggering continuous batching on the GPU
  - Resume support: skips files that already have output
  - Pre-validates PDFs (catches corrupt files before OCR)
  - No ProcessPoolExecutor / SIGALRM hacks
  - Proper timeout via server-side limits, not signal tricks

Usage:
  1. Start vLLM server:  bash launch_server.sh
  2. Run this script:    python process_batch_v3.py
"""

import os
import sys
import tempfile
import datetime
import logging
from tqdm import tqdm
import opencc
from paddleocr import PaddleOCRVL

# ===================== Configuration =====================

INPUT_ROOT = "/home/asiamath/Documents/題庫網/整理後的數學題庫"
OUTPUT_ROOT = "/home/asiamath/Documents/題庫網/processed_docs_final2"
VLLM_URL = "http://localhost:8000/v1"

# How many sub-image requests PaddleOCRVL sends concurrently to vLLM.
# vLLM batches these together in one GPU forward pass.
# Start with 16, increase to 32-64 if GPU memory allows.
VL_REC_MAX_CONCURRENCY = 16

# ===================== Silence noisy loggers =====================

os.environ["GLOG_minloglevel"] = "3"
os.environ["PADDLE_INFERENCE_LOG_LEVEL"] = "0"
os.environ["FLAGS_eager_delete_tensor_gb"] = "0.0"

for _logger_name in ("httpx", "httpcore", "openai", "paddlex"):
    logging.getLogger(_logger_name).setLevel(logging.WARNING)

# ===================== Helpers =====================

LOG_SUCCESS = os.path.join(OUTPUT_ROOT, "_log_success.txt")
LOG_ERROR = os.path.join(OUTPUT_ROOT, "_log_error.txt")


def is_valid_pdf(path):
    """Quick header check — catches corrupt files before sending to OCR."""
    try:
        with open(path, "rb") as f:
            return f.read(5) == b"%PDF-"
    except Exception:
        return False


def collect_tasks(input_root, output_root):
    """Walk input tree, skip already-processed and invalid PDFs."""
    tasks = []
    skipped = 0
    invalid = []

    for root, _dirs, files in os.walk(input_root):
        rel_path = os.path.relpath(root, input_root)
        dest_dir = os.path.join(output_root, rel_path)
        os.makedirs(dest_dir, exist_ok=True)

        for fname in files:
            if not fname.lower().endswith(".pdf"):
                continue

            src = os.path.join(root, fname)
            md_out = os.path.join(dest_dir, os.path.splitext(fname)[0] + ".md")

            # Resume: skip if output already exists and is non-empty
            if os.path.exists(md_out) and os.path.getsize(md_out) > 0:
                skipped += 1
                continue

            # Pre-validate PDF header
            if not is_valid_pdf(src):
                invalid.append(src)
                continue

            tasks.append((src, dest_dir))

    return tasks, skipped, invalid


def save_result(results, src_path, dest_folder, cc):
    """Save OCR results as Traditional Chinese markdown."""
    base = os.path.splitext(os.path.basename(src_path))[0]
    final_md = os.path.join(dest_folder, f"{base}.md")

    all_parts = []

    for res in results:
        with tempfile.TemporaryDirectory() as tmp:
            res.save_to_markdown(save_path=tmp)
            md_files = sorted(f for f in os.listdir(tmp) if f.endswith(".md"))
            for mf in md_files:
                with open(os.path.join(tmp, mf), "r", encoding="utf-8") as f:
                    all_parts.append(f.read())

    if not all_parts:
        return False

    content = cc.convert("\n\n".join(all_parts))
    with open(final_md, "w", encoding="utf-8") as f:
        f.write(content)

    return True


# ===================== Main =====================

def main():
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    # --- Scan files ---
    tasks, skipped, invalid = collect_tasks(INPUT_ROOT, OUTPUT_ROOT)

    print(f"Source:  {INPUT_ROOT}")
    print(f"Output:  {OUTPUT_ROOT}")
    print(f"To process: {len(tasks)}  |  Already done: {skipped}  |  Invalid PDFs: {len(invalid)}")

    # Log invalid PDFs once
    if invalid:
        with open(LOG_ERROR, "a", encoding="utf-8") as f:
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n=== Invalid PDFs detected at {ts} ===\n")
            for p in invalid:
                f.write(f"  {os.path.basename(p)} -> PDFium: bad header (skipped)\n")
                print(f"  Skipped invalid: {os.path.basename(p)}")

    if not tasks:
        print("Nothing to process.")
        return

    # --- Initialize pipeline ONCE ---
    print(f"\nInitializing PaddleOCRVL (vl_rec_max_concurrency={VL_REC_MAX_CONCURRENCY})...")
    pipeline = PaddleOCRVL(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_chart_recognition=False,
        vl_rec_backend="vllm-server",
        vl_rec_server_url=VLLM_URL,
        vl_rec_max_concurrency=VL_REC_MAX_CONCURRENCY,
    )
    cc = opencc.OpenCC("s2t")
    print("Pipeline ready.\n")

    # --- Open log files (append mode for resume) ---
    now = datetime.datetime.now()
    for log_path, label in [(LOG_SUCCESS, "Success"), (LOG_ERROR, "Error")]:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n=== Batch {label} ({now}, {len(tasks)} files) ===\n")

    f_succ = open(LOG_SUCCESS, "a", encoding="utf-8")
    f_err = open(LOG_ERROR, "a", encoding="utf-8")

    success_count = 0
    error_count = 0

    try:
        pbar = tqdm(tasks, unit="file", ncols=100, dynamic_ncols=True)

        for src_path, dest_folder in pbar:
            filename = os.path.basename(src_path)
            pbar.set_postfix_str(filename[:40], refresh=False)
            ts = datetime.datetime.now().strftime("%H:%M:%S")

            try:
                results = list(pipeline.predict(src_path))

                if save_result(results, src_path, dest_folder, cc):
                    f_succ.write(f"[{ts}] {filename}\n")
                    f_succ.flush()
                    success_count += 1
                else:
                    msg = "Empty result (no markdown generated)"
                    f_err.write(f"[{ts}] {filename} -> {msg}\n")
                    f_err.flush()
                    error_count += 1
                    pbar.write(f"  WARN: {filename}: {msg}")

            except Exception as e:
                f_err.write(f"[{ts}] {filename} -> {e}\n")
                f_err.flush()
                error_count += 1
                pbar.write(f"  ERROR: {filename}: {e}")

    finally:
        f_succ.close()
        f_err.close()

    # --- Summary ---
    print(f"\nDone!  Success: {success_count}  |  Errors: {error_count}")
    print(f"  Success log: {LOG_SUCCESS}")
    print(f"  Error log:   {LOG_ERROR}")


if __name__ == "__main__":
    main()
