#!/usr/bin/env python3
"""
FastAPI backend for AsiaMath OCR with custom HTML/CSS/JS frontend.

Requires vLLM server running:  bash launch_server.sh
Then:  python app.py
"""

import base64
import io
import os
import re
import tempfile
import logging
import uuid
import secrets

os.environ["GLOG_minloglevel"] = "3"
os.environ["PADDLE_INFERENCE_LOG_LEVEL"] = "0"
os.environ["FLAGS_eager_delete_tensor_gb"] = "0.0"
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

for _n in ("httpx", "httpcore", "openai", "paddlex"):
    logging.getLogger(_n).setLevel(logging.WARNING)

import numpy as np
import opencc
import pypdfium2 as pdfium
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from paddleocr import PaddleOCRVL
from starlette.middleware.sessions import SessionMiddleware

# ===================== Configuration =====================

VLLM_URL = "http://localhost:8000/v1"
VL_REC_MAX_CONCURRENCY = 16
SUPPORTED_EXT = (".pdf", ".jpg", ".jpeg", ".png")
AUTH_USER = "admin"
AUTH_PASS = "123"

# ===================== Init pipeline once =====================

print("Initializing PaddleOCRVL pipeline...")
pipeline = PaddleOCRVL(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_chart_recognition=False,
    vl_rec_backend="vllm-server",
    vl_rec_server_url=VLLM_URL,
    vl_rec_max_concurrency=VL_REC_MAX_CONCURRENCY,
)
cc = opencc.OpenCC("s2t")
print("Pipeline ready.")

# ===================== FastAPI app =====================

app = FastAPI(title="AsiaMath OCR")
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ── Auth ──

def require_auth(request: Request):
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=401, detail="Not authenticated")


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Login — AsiaMath OCR</title>
      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
      <style>
        :root { --brand: #0f766e; --brand-strong: #0a5b55; --line: #d6e4f2; --bg: #f2f7fc; }
        * { box-sizing: border-box; }
        body {
          margin: 0; font-family: "IBM Plex Sans", sans-serif;
          background: radial-gradient(circle at 12% 0%, #d8f7ea 0%, transparent 32%),
                      radial-gradient(circle at 92% 0%, #ffe7d3 0%, transparent 28%), var(--bg);
          min-height: 100vh; display: flex; align-items: center; justify-content: center;
        }
        .card {
          background: #fff; border: 1px solid var(--line); border-radius: 14px;
          box-shadow: 0 16px 36px rgba(15,35,56,0.13); padding: 36px 32px; width: 360px;
        }
        .brand { display: flex; align-items: center; gap: 10px; margin-bottom: 24px; }
        .brand-dot { width: 15px; height: 15px; border-radius: 50%; background: linear-gradient(120deg, #ff8c42, #0f766e); }
        .brand-title { font-size: 18px; font-weight: 700; }
        label { display: block; font-size: 13px; color: #48627d; margin-bottom: 4px; }
        input {
          width: 100%; border: 1px solid #c9d9ea; border-radius: 8px;
          padding: 9px 10px; font: inherit; font-size: 14px; margin-bottom: 14px;
        }
        button {
          width: 100%; border: none; border-radius: 10px; padding: 11px;
          font: inherit; font-weight: 600; font-size: 14px; cursor: pointer;
          color: #fff; background: linear-gradient(120deg, var(--brand), var(--brand-strong));
        }
        .error { color: #b91c1c; font-size: 13px; margin-bottom: 10px; }
      </style>
    </head>
    <body>
      <div class="card">
        <div class="brand">
          <span class="brand-dot"></span>
          <span class="brand-title">AsiaMath OCR</span>
        </div>
        <form method="POST" action="/login">
          <div id="error" class="error"></div>
          <label>Username</label>
          <input name="username" type="text" required autofocus />
          <label>Password</label>
          <input name="password" type="password" required />
          <button type="submit">Sign In</button>
        </form>
      </div>
    </body>
    </html>
    """


@app.post("/login")
async def login_submit(request: Request):
    form = await request.form()
    username = form.get("username", "")
    password = form.get("password", "")
    if username == AUTH_USER and password == AUTH_PASS:
        request.session["authenticated"] = True
        return RedirectResponse(url="/", status_code=303)
    return HTMLResponse(
        content=(await login_page()).replace(
            '<div id="error" class="error"></div>',
            '<div id="error" class="error">Invalid credentials</div>',
        ),
        status_code=401,
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/login")
    with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


# ── Helpers ──

def pil_to_data_url(img) -> str:
    """Convert a PIL Image or numpy array to a base64 data URL."""
    if isinstance(img, np.ndarray):
        img = Image.fromarray(img)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


def render_pdf_pages(pdf_path, dpi=150):
    """Render each PDF page as a PIL image."""
    doc = pdfium.PdfDocument(pdf_path)
    pages = []
    for i in range(len(doc)):
        page = doc[i]
        bitmap = page.render(scale=dpi / 72)
        pages.append(bitmap.to_pil())
    doc.close()
    return pages


# ── 公文 field extraction ──

def extract_gongwen_fields(markdown: str, filename: str) -> list[dict]:
    """Parse OCR markdown to extract 公文 fields. Returns 'no' if not found."""
    text = markdown

    # 發文者: look for common patterns
    sender = "no"
    for pat in [
        r"(?:發文者|發文機關|機關)\s*[：:]\s*(.+)",
        r"^(.+?(?:政府|局|處|署|部|院|所|中心|委員會|公所))\s*(?:函|書|令|公告)?",
    ]:
        m = re.search(pat, text, re.MULTILINE)
        if m:
            val = m.group(1).strip()
            # Clean trailing document type chars
            val = re.sub(r"[函書令公告]+$", "", val).strip()
            if val:
                sender = val
                break

    # 發文日期: support ROC dates (中華民國XXX年XX月XX日) and standard dates
    date = "no"
    for pat in [
        r"(?:發文日期|日\s*期)\s*[：:]\s*[中華民國\s]*(.+?)(?:\n|$)",
        r"中華民國\s*(\d{2,3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日",
        r"(\d{2,4}[/.年]\d{1,2}[/.月]\d{1,2}日?)",
    ]:
        m = re.search(pat, text)
        if m:
            if m.lastindex and m.lastindex >= 3:
                date = f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
            else:
                date = m.group(1).strip()
            break

    # 發文字號
    ref_no = "no"
    for pat in [
        r"(?:發文字號|文\s*號)\s*[：:]\s*(.+?)(?:\n|$)",
        r"([\w]*字第[\w-]+號)",
    ]:
        m = re.search(pat, text, re.MULTILINE)
        if m:
            ref_no = m.group(1).strip()
            break

    # 主旨: capture everything until 說明 or 辦法 section
    subject = "no"
    m = re.search(
        r"主\s*旨\s*[：:]\s*(.+?)(?=\n\s*(?:說\s*明|辦\s*法|正\s*本|副\s*本)|$)",
        text,
        re.DOTALL,
    )
    if m:
        lines = [l.strip() for l in m.group(1).strip().split("\n") if l.strip()]
        subject = "\n".join(lines) if lines else "no"

    # 說明: capture everything until 正本/副本/辦法/擬辦 or end
    description = "no"
    m = re.search(
        r"說\s*明\s*[：:]\s*(.+?)(?=\n\s*(?:正\s*本|副\s*本|辦\s*法|擬\s*辦)|$)",
        text,
        re.DOTALL,
    )
    if m:
        lines = [l.strip() for l in m.group(1).strip().split("\n") if l.strip()]
        description = "\n".join(lines) if lines else "no"

    # 是否包含「罰款」關鍵字: check if "罰款" appears anywhere in the full text
    has_fine = "是" if "罰款" in text else "否"

    return [
        {"field": "檔案名稱", "ai_value": filename},
        {"field": "發文者", "ai_value": sender},
        {"field": "發文日期", "ai_value": date},
        {"field": "發文字號", "ai_value": ref_no},
        {"field": "主旨", "ai_value": subject},
        {"field": "說明", "ai_value": description},
        {"field": "是否包含「罰款」關鍵字", "ai_value": has_fine},
    ]


# ── Long image slicing ──

SLICE_MAX_HEIGHT = 1500  # Max strip height in pixels
SLICE_OVERLAP = 150      # Overlap between strips to avoid cutting text


def slice_long_image(img: Image.Image) -> list[Image.Image]:
    """Split a tall image into overlapping horizontal strips.

    Returns the original image in a list if it doesn't need slicing.
    Triggers when height > 2 * width and height > SLICE_MAX_HEIGHT.
    """
    w, h = img.size
    if h <= SLICE_MAX_HEIGHT or h <= 2 * w:
        return [img]

    strips = []
    y = 0
    while y < h:
        y_end = min(y + SLICE_MAX_HEIGHT, h)
        strip = img.crop((0, y, w, y_end))
        strips.append(strip)
        y += SLICE_MAX_HEIGHT - SLICE_OVERLAP
        if y_end == h:
            break
    return strips


def run_ocr_on_image(img: Image.Image):
    """Run the OCR pipeline on a single PIL image via a temp file."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img.save(tmp, format="PNG")
        tmp_img_path = tmp.name
    try:
        return list(pipeline.predict(tmp_img_path))
    finally:
        os.unlink(tmp_img_path)


def process_ocr_results(results, page_idx_offset=0):
    """Extract markdown, layout images, and crop images from OCR results."""
    md_parts = []
    layout_images = []
    crop_images = []

    for page_idx, res in enumerate(results):
        idx = page_idx + page_idx_offset

        # Markdown
        with tempfile.TemporaryDirectory() as tmpdir:
            res.save_to_markdown(save_path=tmpdir)
            md_files = sorted(f for f in os.listdir(tmpdir) if f.endswith(".md"))
            for mf in md_files:
                with open(os.path.join(tmpdir, mf), "r", encoding="utf-8") as f:
                    md_parts.append(f.read())

        # Layout visualization
        vis_imgs = res.img
        if "layout_det_res" in vis_imgs:
            layout_images.append(vis_imgs["layout_det_res"])

        # Cropped regions from layout_det_res boxes
        layout_res = res.get("layout_det_res")
        if layout_res:
            input_img = layout_res.get("input_img")
            if input_img is not None:
                pil_img = (
                    Image.fromarray(input_img)
                    if not isinstance(input_img, Image.Image)
                    else input_img
                )
                for box in layout_res.get("boxes", []):
                    x1, y1, x2, y2 = [int(c) for c in box["coordinate"]]
                    label = box.get("label", "unknown")
                    cropped = pil_img.crop((x1, y1, x2, y2))
                    crop_images.append(
                        (cropped, f"p{idx}_{label} ({x1},{y1})-({x2},{y2})")
                    )

        # Image blocks from pipeline
        for item in res.get("imgs_in_doc", []):
            img = item.get("img")
            coord = item.get("coordinate", ())
            label = item.get("label", "image")
            if img and coord:
                crop_images.append(
                    (
                        img,
                        f"p{idx}_{label} ({coord[0]},{coord[1]})-({coord[2]},{coord[3]})",
                    )
                )

    return md_parts, layout_images, crop_images


# ── OCR endpoint ──

@app.post("/api/ocr")
async def run_ocr(request: Request, file: UploadFile = File(...)):
    require_auth(request)

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in SUPPORTED_EXT:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    # Save uploaded file to temp
    suffix = ext
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Original pages (for display)
        if ext == ".pdf":
            original_pages = render_pdf_pages(tmp_path)
        else:
            original_pages = [Image.open(tmp_path).copy()]

        # Run OCR
        all_md_parts = []
        all_layout_images = []
        all_crop_images = []

        if ext == ".pdf":
            # PDF: let PaddleOCR handle multi-page natively
            results = list(pipeline.predict(tmp_path))
            md, lay, crops = process_ocr_results(results)
            all_md_parts.extend(md)
            all_layout_images.extend(lay)
            all_crop_images.extend(crops)
        else:
            # Image: check if it needs slicing
            img = original_pages[0]
            strips = slice_long_image(img)

            if len(strips) == 1 and strips[0] is img:
                # Normal image, run directly on original file
                results = list(pipeline.predict(tmp_path))
                md, lay, crops = process_ocr_results(results)
                all_md_parts.extend(md)
                all_layout_images.extend(lay)
                all_crop_images.extend(crops)
            else:
                # Long image — process each strip
                logging.info(
                    "Slicing long image (%dx%d) into %d strips",
                    img.size[0], img.size[1], len(strips),
                )
                for i, strip in enumerate(strips):
                    results = run_ocr_on_image(strip)
                    md, lay, crops = process_ocr_results(results, i)
                    all_md_parts.extend(md)
                    all_layout_images.extend(lay)
                    all_crop_images.extend(crops)

        markdown_text = (
            cc.convert("\n\n".join(all_md_parts))
            if all_md_parts
            else "(No text detected)"
        )

        # Extract 公文 fields from markdown
        gongwen_fields = extract_gongwen_fields(markdown_text, file.filename)

        return {
            "original_pages": [pil_to_data_url(p) for p in original_pages],
            "markdown": markdown_text,
            "layout_images": [pil_to_data_url(p) for p in all_layout_images],
            "crop_images": [
                {"url": pil_to_data_url(img), "label": label}
                for img, label in all_crop_images
            ],
            "gongwen_fields": gongwen_fields,
        }

    finally:
        os.unlink(tmp_path)


# ===================== Run =====================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
