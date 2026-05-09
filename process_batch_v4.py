#!/usr/bin/env python3
"""
Batch OCR with PaddleOCR-VL-1.5 + vLLM continuous batching.

Processes all PDFs and images (.jpg, .jpeg, .png) in the input directory.
Outputs Traditional Chinese markdown files.

Usage:
  1. Start vLLM server:  bash launch_server.sh
  2. Run this script:    python process_batch_v4.py
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

INPUT_ROOT = "/home/asiamath/Users/PJ/funcry_test"
OUTPUT_ROOT = "/home/asiamath/Users/PJ/funcry_test_output2"
VLLM_URL = "http://localhost:8000/v1"

# Supported file extensions (excluding .7z and other archives)
SUPPORTED_EXT = (".pdf", ".jpg", ".jpeg", ".png")

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
            if not fname.lower().endswith(SUPPORTED_EXT):
                continue

            src = os.path.join(root, fname)
            md_out = os.path.join(dest_dir, os.path.splitext(fname)[0] + ".md")

            # Resume: skip if output already exists and is non-empty
            if os.path.exists(md_out) and os.path.getsize(md_out) > 0:
                skipped += 1
                continue

            # Pre-validate PDF header (only for PDFs, not images)
            if fname.lower().endswith(".pdf") and not is_valid_pdf(src):
                invalid.append(src)
                continue

            tasks.append((src, dest_dir))

    return tasks, skipped, invalid


def save_result(results, src_path, dest_folder, cc):
    """Save OCR results as Traditional Chinese markdown + segmented images."""
    base = os.path.splitext(os.path.basename(src_path))[0]
    final_md = os.path.join(dest_folder, f"{base}.md")
    seg_dir = os.path.join(dest_folder, f"{base}_segments")

    all_parts = []

    for page_idx, res in enumerate(results):
        # --- Save markdown ---
        with tempfile.TemporaryDirectory() as tmp:
            res.save_to_markdown(save_path=tmp)
            md_files = sorted(f for f in os.listdir(tmp) if f.endswith(".md"))
            for mf in md_files:
                with open(os.path.join(tmp, mf), "r", encoding="utf-8") as f:
                    all_parts.append(f.read())

        # --- Save layout visualization ---
        os.makedirs(seg_dir, exist_ok=True)
        vis_imgs = res.img
        if "layout_det_res" in vis_imgs:
            vis_imgs["layout_det_res"].save(
                os.path.join(seg_dir, f"p{page_idx}_layout.jpg")
            )

        # --- Save cropped region images ---
        # From imgs_in_doc (image/figure blocks already cropped by pipeline)
        for item in res.get("imgs_in_doc", []):
            img = item.get("img")
            coord = item.get("coordinate", ())
            label = item.get("label", "region")
            if img and coord:
                fname = f"p{page_idx}_{label}_{coord[0]}_{coord[1]}_{coord[2]}_{coord[3]}.jpg"
                img.save(os.path.join(seg_dir, fname))

        # From layout_det_res boxes (crop all detected regions)
        layout_res = res.get("layout_det_res")
        if layout_res:
            input_img = layout_res.get("input_img")
            if input_img is not None:
                from PIL import Image as _PILImage
                pil_img = _PILImage.fromarray(input_img) if not isinstance(input_img, _PILImage.Image) else input_img
                for box in layout_res.get("boxes", []):
                    x1, y1, x2, y2 = [int(c) for c in box["coordinate"]]
                    label = box.get("label", "unknown")
                    cropped = pil_img.crop((x1, y1, x2, y2))
                    fname = f"p{page_idx}_crop_{label}_{x1}_{y1}_{x2}_{y2}.jpg"
                    cropped.save(os.path.join(seg_dir, fname))

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
    print(f"Supported: {SUPPORTED_EXT}")
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