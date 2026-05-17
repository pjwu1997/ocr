#!/usr/bin/env python3
"""
FastAPI backend for AsiaMath OCR with custom HTML/CSS/JS frontend.

Requires vLLM server running:  bash launch_server.sh
Then:  python app.py
"""

import base64
import io
import json
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
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from paddleocr import PaddleOCRVL
from starlette.middleware.sessions import SessionMiddleware

import db
from openai import OpenAI
from ocr_preprocess import preprocess_for_ocr, preprocess_for_qwen, PDF_HIGH_DPI

# ===================== Configuration =====================

VLLM_URL = "http://localhost:8000/v1"  # legacy PaddleOCR (removed)
QWEN3_URL = "http://localhost:8010/v1"
QWEN3_MODEL = "qwen3.5-27b"  # served-model-name from docker-compose qwen-llm-server
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

app = FastAPI(
    title="AsiaMath AIOCR",
    description=(
        "LLM-first OCR for ERP welfare-document flows.\n\n"
        "**Auth:** Login via `POST /login` (form: `username`, `password`) — "
        "session cookie is required for all `/v1/aiocr/*` endpoints.\n\n"
        "**Main endpoint:** `POST /v1/aiocr/analyze` — multi-file analyze "
        "with per-field confidence scoring.\n\n"
        "See `/v1/aiocr/flows` for the available flow → doctype catalogue."
    ),
    version="1.0.0",
    openapi_tags=[
        {"name": "aiocr-v1", "description": "Spec-compliant LLM-first OCR (ERP-facing)"},
        {"name": "auth", "description": "Session login / logout"},
        {"name": "legacy", "description": "Pre-v1 rule-based endpoints (kept for transition)"},
    ],
)
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


def pil_to_base64(img) -> str:
    """Convert a PIL Image to a raw base64 string (no data URL prefix)."""
    if isinstance(img, np.ndarray):
        img = Image.fromarray(img)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def qwen3_extract(img: Image.Image, doc_type: str, field_names: list[str]) -> tuple[dict, str]:
    """Single-step Qwen3 OCR: image → JSON field extraction directly.

    Returns (extracted_fields_dict, raw_response_text).
    """
    try:
        client = OpenAI(base_url=QWEN3_URL, api_key="dummy")
        preprocessed = preprocess_for_qwen(img)
        img_b64 = pil_to_base64(preprocessed)

        fields_list = "\n".join(f"- {name}" for name in field_names)
        resp = client.chat.completions.create(
            model=QWEN3_MODEL,
            messages=[
                {"role": "system", "content": "你是精確的繁體中文OCR系統。辨識圖片中所有文字並提取指定欄位。注意區分不同角色（如喜帖中：令媛/令嬡後面是新娘名字，不是母親；鞠躬前是父母名字）。以JSON回覆。"},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                    {"type": "text", "text": f"請仔細辨識這張「{doc_type}」文件中的文字，提取以下欄位：\n{fields_list}\n\n以JSON回覆，只回覆JSON。"},
                ]}
            ],
            max_tokens=1024,
            temperature=0.0,
        )
        raw = resp.choices[0].message.content
        # Strip Qwen3 <think>...</think> reasoning blocks
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

        # Parse JSON (handle ```json``` wrapper)
        json_str = raw
        if json_str.startswith("```"):
            lines = json_str.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            json_str = "\n".join(lines)
        extracted = json.loads(json_str)
        return extracted, raw
    except Exception as e:
        logging.warning("Qwen3 extraction failed: %s", e)
        return {}, ""


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


# ── Field extraction pipeline ──




def strip_html(text: str) -> str:
    """Remove HTML tags from OCR markdown to get plain text for regex matching."""
    # Remove HTML tags
    plain = re.sub(r"<[^>]+>", " ", text)
    # Collapse whitespace but keep newlines
    plain = re.sub(r"[ \t]+", " ", plain)
    # Remove empty lines
    plain = "\n".join(line.strip() for line in plain.split("\n") if line.strip())
    return plain


def _extract_passenger_list(html: str) -> list[dict]:
    """Parse the shuttle bus HTML table to extract passengers.

    The table has columns: 班次 | 單位 | 搭乘廠區 | 姓名 | 簽名欄
    The 簽名欄 is a single rowspan image covering all rows — we cannot
    detect per-row signatures from OCR alone. Instead we compare the
    registered count (登記人數) vs actual count (實際搭乘人數) from 人數統計.
    """
    passengers = []

    # Find all table rows
    rows = re.findall(r"<tr>(.*?)</tr>", html, re.DOTALL)

    in_passenger_section = False

    for row_html in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row_html, re.DOTALL)
        cell_texts = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]

        # Detect header row with 班次 + 姓名
        if any("班次" in t for t in cell_texts) and any("姓名" in t for t in cell_texts):
            in_passenger_section = True
            continue

        if not in_passenger_section:
            continue

        # Skip empty rows
        if not any(t for t in cell_texts):
            continue

        # Find Chinese name in cells
        pname = ""
        for t in cell_texts:
            if re.search(r"[\u4e00-\u9fff]{2,}", t):
                pname = t
                break
        if not pname:
            continue

        # Parse shift, dept, area
        shift = dept = area = ""
        factory_codes = {"EL", "DF", "CS"}
        for t in cell_texts:
            if not shift and re.match(r"^\d{2}$", t):
                shift = t
            elif not area and t in factory_codes:
                area = t
            elif not dept and t and t not in factory_codes and t != pname and re.match(r"^[A-Za-z0-9#/]+$", t):
                dept = t

        passengers.append({
            "name": pname,
            "dept": dept or "?",
            "area": area or "?",
        })

    return passengers


def extract_fields(text: str, rule: dict, filename: str,
                    original_pages: list | None = None,
                    ocr_results_raw: list | None = None) -> list[dict]:
    """Extract fields from OCR text using regex patterns defined in the rule."""
    field_defs = rule.get("fields_json", [])
    if not field_defs:
        return [{"field": "檔案名稱", "ai_value": filename}]

    plain = strip_html(text)

    results = [{"field": "檔案名稱", "ai_value": filename}]
    # Cache for crop-based re-OCR text (shared across fields in same call)
    _crop_cache = {}

    for fdef in field_defs:
        name = fdef.get("name", "")
        ftype = fdef.get("type", "text")

        if ftype == "filename":
            continue

        # Boolean keyword check
        if ftype == "boolean_keyword":
            keyword = fdef.get("keyword", "")
            value = "是" if keyword and keyword in plain else "否"
            results.append({"field": name, "ai_value": value})
            continue

        # Passenger count from HTML table rows (for 接駁車搭乘登記表)
        if ftype == "passenger_count":
            passengers = _extract_passenger_list(text)
            results.append({"field": name, "ai_value": str(len(passengers)) if passengers else "0"})
            continue

        # Rode / no-show passenger lists (for 接駁車搭乘登記表)
        # Uses per-stop 人數統計 to split passengers into rode vs no-show
        if ftype in ("passenger_rode_list", "passenger_noshow_list"):
            passengers = _extract_passenger_list(text)
            if not passengers:
                results.append({"field": name, "ai_value": "no"})
                continue

            # Parse per-stop actual counts from 人數統計
            stops = re.findall(r"廠別\s+((?:[A-Z]{2}\s*)+)", plain)
            stop_names = stops[0].split() if stops else []
            actual_counts = {}
            m = re.search(r"人數統計\s+([\d\s]+?)(?:終點|$)", plain)
            if m and stop_names:
                nums = re.findall(r"\d+", m.group(1))
                for i, sname in enumerate(stop_names):
                    if i < len(nums):
                        actual_counts[sname] = int(nums[i])

            # Group passengers by area, determine rode vs no-show per stop
            from collections import defaultdict
            by_area = defaultdict(list)
            for p in passengers:
                by_area[p["area"]].append(p)

            rode = []
            no_show = []
            for area, plist in by_area.items():
                act = actual_counts.get(area, len(plist))
                # First `act` passengers rode, rest are no-shows
                rode.extend(plist[:act])
                no_show.extend(plist[act:])

            if ftype == "passenger_rode_list":
                if rode:
                    results.append({"field": name, "ai_value": ", ".join(p["name"] for p in rode)})
                else:
                    results.append({"field": name, "ai_value": "無"})
            else:
                if no_show:
                    results.append({"field": name, "ai_value": ", ".join(p["name"] for p in no_show)})
                else:
                    results.append({"field": name, "ai_value": "無"})
            continue

        # Meal adjustment list (for 用餐費用調整表)
        # Each row: {row#} {date?} ■{meal}...■{reason}... ■+1/■-1 {card#} {name}
        if ftype == "meal_adjustment_list":
            # Extract all rows: number ... ■+1/■-1 card_number name
            rows = re.findall(
                r'(\d{1,2})\s+(\d{1,2}/)?\s*'             # row number, optional date
                r'(■午餐|■晚餐|■宵夜|■加值餐)'              # meal type (checked)
                r'.*?'                                       # skip unchecked options
                r'(■無法刷卡|■取消用餐|■異常退費|■新人用餐|■訂餐又刷卡)'  # reason (checked)
                r'.*?'                                       # skip
                r'(■\+1|■-1)\s+(?:□\+1|□-1)\s+'            # quantity
                r'(\d{4,6})\s+'                              # card number
                r'([\u4e00-\u9fff]{2,5})',                   # name
                plain
            )
            if rows:
                entries = []
                for row_num, date, meal, reason, qty, card, pname in rows:
                    meal_s = meal.replace("■", "")
                    reason_s = reason.replace("■", "")
                    qty_s = qty.replace("■", "")
                    entries.append(f"{pname}（卡號{card}）：{meal_s}, {qty_s}, {reason_s}")
                results.append({"field": name, "ai_value": "\n".join(entries)})
            else:
                results.append({"field": name, "ai_value": "no"})
            continue

        # Grade table extraction (for 成績單)
        # Full-page OCR often misses dense grade tables. If grades aren't
        # in the text, re-OCR a cropped table region from the original image.
        if ftype == "grade_table":
            subjects = [
                "國語文", "本國語文", "本土語言", "英語", "數學",
                "社會", "自然", "自然與生活科技", "藝術", "音樂", "美勞",
                "體育", "健康", "綜合活動", "生活", "彈性",
                "活力健康", "有品", "溫馨鄉土", "欣閒", "科學天文",
            ]
            # First try parsing from existing text
            found_grades = []
            for subj in subjects:
                pat = re.escape(subj) + r"[\S]*\s+\d+\s+\S+\s+(優|甲|乙|丙|丁)"
                m = re.search(pat, plain)
                if m:
                    found_grades.append(f"{subj}：{m.group(1)}")

            # If no grades found, re-OCR the table crop from original image
            # using layout detection coordinates for precise cropping
            if not found_grades and original_pages and ocr_results_raw:
                try:
                    # Find table bounding box from layout detection
                    table_box = None
                    for res in ocr_results_raw:
                        layout_res = res.get("layout_det_res")
                        if layout_res:
                            for box in layout_res.get("boxes", []):
                                if box.get("label") == "table":
                                    coord = box.get("coordinate", [])
                                    if len(coord) >= 4:
                                        x1, y1, x2, y2 = [int(c) for c in coord]
                                        # Use the largest table
                                        area = (x2 - x1) * (y2 - y1)
                                        if table_box is None or area > table_box[4]:
                                            table_box = (x1, y1, x2, y2, area)

                    if table_box and original_pages:
                        x1, y1, x2, y2, _ = table_box
                        img = original_pages[0]
                        # Expand crop slightly and skip the header row
                        header_offset = int((y2 - y1) * 0.15)
                        table_crop = img.crop((x1, y1 + header_offset, x2, y2))
                        crop_results = run_ocr_on_image(table_crop)
                        crop_md = ""
                        for cres in crop_results:
                            with tempfile.TemporaryDirectory() as tmpdir:
                                cres.save_to_markdown(save_path=tmpdir)
                                for mf in sorted(os.listdir(tmpdir)):
                                    if mf.endswith(".md"):
                                        with open(os.path.join(tmpdir, mf), "r", encoding="utf-8") as f:
                                            crop_md += f.read()
                        crop_plain = strip_html(cc.convert(crop_md))
                        for subj in subjects:
                            pat = re.escape(subj) + r"[\S]*\s+\d+\s+\S+\s+(優|甲|乙|丙|丁)"
                            m = re.search(pat, crop_plain)
                            if m:
                                found_grades.append(f"{subj}：{m.group(1)}")
                except Exception as e:
                    logging.warning("Grade table re-OCR failed: %s", e)

            if found_grades:
                results.append({"field": name, "ai_value": "\n".join(found_grades)})
            else:
                results.append({"field": name, "ai_value": "no"})
            continue

        # Multi time-clock extraction (for 清潔打卡資料)
        if ftype == "multi_time_clock":
            # Pattern: day_num HHmm:ss or 20HH:MM format
            # OCR outputs like "2006:12 2016:02" meaning 06:12 in, 16:02 out
            time_pairs = re.findall(r'(\d{1,2})\s+20(\d{2}:\d{2})\s+20(\d{2}:\d{2})', plain)
            if time_pairs:
                entries = []
                for day, t_in, t_out in time_pairs:
                    entries.append(f"Day{day}: {t_in}-{t_out}")
                results.append({"field": name, "ai_value": ", ".join(entries)})
            else:
                # Try alternate pattern
                time_entries = re.findall(r'20(\d{2}:\d{2})', plain)
                if time_entries:
                    results.append({"field": name, "ai_value": ", ".join(time_entries)})
                else:
                    results.append({"field": name, "ai_value": "no"})
            continue

        # Two-character keywords extraction (for 公文)
        if ftype == "two_char_keywords":
            # Extract important 2-char keywords from the document
            important_keywords = [
                "罰款", "危險", "申報", "工廠", "演練", "違規", "裁罰",
                "檢查", "稽查", "處分", "繳納", "限期", "改善", "停工",
                "撤銷", "廢止", "勒令", "歇業", "公告", "通知", "函送",
                "移送", "起訴", "判決", "賠償", "保險", "消防", "安全",
                "防災", "環保", "污染", "排放", "噪音", "廢棄", "回收",
                "許可", "執照", "登記", "變更", "註銷", "合併", "解散",
            ]
            found_kw = [kw for kw in important_keywords if kw in plain]
            if found_kw:
                results.append({"field": name, "ai_value": ", ".join(found_kw)})
            else:
                results.append({"field": name, "ai_value": "no"})
            continue

        # Obituary deceased name (for 訃聞)
        # Combines formal title (潘媽潘夫人) with given name (映築) if available
        if ftype == "obituary_deceased":
            deceased = None
            # Try: "母親/父親 + 潘媽潘夫人" pattern
            m = re.search(r"(?:母親|父親)\s*([\u4e00-\u9fff]+(?:夫人|先生|老大人|翁|媽|公))", plain)
            if m:
                deceased = m.group(1)
            # Also try: 先慈/先嚴 + name
            if not deceased:
                m = re.search(r"先[慈嚴考妣]\s*([\u4e00-\u9fff]{2,5})", plain)
                if m:
                    deceased = m.group(1)
            # Look for given name: "名映築" or "閩名映築" — exactly 2 chars after 名
            if deceased:
                m2 = re.search(r"(?:閩名|名)([\u4e00-\u9fff]{2})", plain)
                if m2:
                    deceased = f"{deceased}（{m2.group(1)}）"
            # Vietnamese death certificate fallback
            if not deceased:
                m = re.search(r"(?:Họ|Ho)[,\s]*(?:chữ đệm|chu dem)?[,\s]*(?:tên|ten)\s*[：:]\s*(.+?)(?:\n|$)", plain)
                if m:
                    deceased = m.group(1).strip()
            results.append({"field": name, "ai_value": deceased or "no"})
            continue

        # Obituary children list (for 訃聞)
        if ftype == "obituary_children":
            children = []
            seen = set()
            # Pattern 1: 孝\n女\n(name) — newline-separated vertical text
            for m in re.finditer(r"孝\n(女|子|男)\n(\S+)", plain):
                entry = f"孝{m.group(1)} {m.group(2)}"
                if entry not in seen:
                    children.append(entry)
                    seen.add(entry)
            # Pattern 2: 孝男X、Y暨 — inline list from cropped text
            for m in re.finditer(r"孝(男|女|子)([\u4e00-\u9fff]{2,5})([\u4e00-\u9fff]{2,5})(?:暨|及)", plain):
                for name_val in [m.group(2), m.group(3)]:
                    entry = f"孝{m.group(1)} {name_val}"
                    if entry not in seen:
                        children.append(entry)
                        seen.add(entry)
            # Pattern 3: 孝 女 name — space-separated fallback
            if not children:
                for m in re.finditer(r"孝\s*(女|子|男)\s+(\S{2,5})", plain):
                    entry = f"孝{m.group(1)} {m.group(2)}"
                    if entry not in seen:
                        children.append(entry)
                        seen.add(entry)
            if children:
                results.append({"field": name, "ai_value": ", ".join(children)})
            else:
                results.append({"field": name, "ai_value": "no"})
            continue

        # Envelope address crop re-OCR (for 手寫信件)
        # When full-page OCR misses handwritten address, crop the address label
        # area and re-OCR it
        if ftype == "envelope_address_crop":
            # First try regex on existing text
            patterns = fdef.get("regex_patterns", [])
            found_in_text = False
            for pat in patterns:
                m_addr = re.search(pat, plain, re.MULTILINE)
                if m_addr:
                    val = m_addr.group(1).strip() if m_addr.lastindex else m_addr.group(0).strip()
                    if val and val != "no":
                        results.append({"field": name, "ai_value": val})
                        found_in_text = True
                        break

            if not found_in_text and original_pages:
                # Try crop-based re-OCR on the address area
                if "envelope" not in _crop_cache:
                    try:
                        page_img = original_pages[0]
                        w, h = page_img.size
                        # Address label area: x: 35%-75%, y: 12%-35%
                        x1 = int(w * 0.35)
                        x2 = int(w * 0.75)
                        y1 = int(h * 0.12)
                        y2 = int(h * 0.35)
                        crop = page_img.crop((x1, y1, x2, y2))
                        # Resize crop for better OCR (ensure adequate resolution)
                        crop_w, crop_h = crop.size
                        if crop_w < 800:
                            scale = 800 / crop_w
                            crop = crop.resize(
                                (int(crop_w * scale), int(crop_h * scale)),
                                Image.LANCZOS
                            )
                        crop_results = run_ocr_on_image(crop)
                        crop_md = ""
                        for cres in crop_results:
                            with tempfile.TemporaryDirectory() as tmpdir:
                                cres.save_to_markdown(save_path=tmpdir)
                                for mf in sorted(os.listdir(tmpdir)):
                                    if mf.endswith(".md"):
                                        with open(os.path.join(tmpdir, mf), "r", encoding="utf-8") as f:
                                            crop_md += f.read()
                        _crop_cache["envelope"] = strip_html(cc.convert(crop_md))
                        logging.info("Envelope crop OCR text: %s", _crop_cache["envelope"])
                    except Exception as e:
                        logging.warning("Envelope crop re-OCR failed: %s", e)
                        _crop_cache["envelope"] = ""

                crop_plain = _crop_cache.get("envelope", "")
                found_in_crop = False
                if crop_plain:
                    for pat in patterns:
                        m_addr = re.search(pat, crop_plain, re.MULTILINE)
                        if m_addr:
                            val = m_addr.group(1).strip() if m_addr.lastindex else m_addr.group(0).strip()
                            if val and val != "no":
                                results.append({"field": name, "ai_value": val})
                                found_in_crop = True
                                break
                if not found_in_crop:
                    results.append({"field": name, "ai_value": "no"})
            elif not found_in_text:
                results.append({"field": name, "ai_value": "no"})
            continue

        # Try regex patterns
        patterns = fdef.get("regex_patterns", [])
        matched = False
        for pat in patterns:
            m = re.search(pat, plain, re.MULTILINE | re.DOTALL)
            if m:
                if m.lastindex and m.lastindex >= 3:
                    value = "/".join(m.group(i) for i in range(1, m.lastindex + 1))
                elif m.lastindex:
                    value = m.group(1).strip()
                else:
                    value = m.group(0).strip()
                # Clean multi-line values
                lines = [l.strip() for l in value.split("\n") if l.strip()]
                value = "\n".join(lines) if lines else "no"
                results.append({"field": name, "ai_value": value})
                matched = True
                break

        if not matched:
            results.append({"field": name, "ai_value": "no"})

    return results


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
async def run_ocr(
    request: Request,
    file: UploadFile = File(...),
    rule_id: int = Form(default=0),
):
    require_auth(request)

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in SUPPORTED_EXT:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    # Load rule if provided
    rule = db.get_rule(rule_id) if rule_id else None

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
        all_raw_results = []

        if ext == ".pdf":
            # PDF: let PaddleOCR handle natively (best quality for PDFs)
            results = list(pipeline.predict(tmp_path))
            all_raw_results.extend(results)
            md, lay, crops = process_ocr_results(results)
            all_md_parts.extend(md)
            all_layout_images.extend(lay)
            all_crop_images.extend(crops)
        else:
            # Image: check if it needs slicing
            img = original_pages[0]
            strips = slice_long_image(img)

            if len(strips) == 1 and strips[0] is img:
                # Preprocess image to optimal size for PaddleOCR-VL
                preprocessed = preprocess_for_ocr(img)
                results = run_ocr_on_image(preprocessed)
                all_raw_results.extend(results)
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
                    all_raw_results.extend(results)
                    md, lay, crops = process_ocr_results(results, i)
                    all_md_parts.extend(md)
                    all_layout_images.extend(lay)
                    all_crop_images.extend(crops)

        raw_md = "\n\n".join(all_md_parts) if all_md_parts else ""
        plain_check = re.sub(r"<[^>]+>", " ", raw_md).strip()

        # If OCR text is suspiciously short for a full page, try re-OCR
        # on cropped halves (catches missed vertical text, side panels, etc.)
        if len(plain_check) < 500 and original_pages:
            logging.info("Short OCR text (%d chars), trying crop re-OCR", len(plain_check))
            page = original_pages[0]
            w, h = page.size
            # Try right half and left half crops
            for crop_name, box in [("right", (w//2, 0, w, h)), ("left", (0, 0, w//2, h))]:
                crop_img = page.crop(box)
                crop_results = run_ocr_on_image(preprocess_for_ocr(crop_img))
                crop_md_parts, _, _ = process_ocr_results(crop_results)
                if crop_md_parts:
                    crop_plain = re.sub(r"<[^>]+>", " ", "\n".join(crop_md_parts)).strip()
                    # Only add if the crop found substantially new text
                    if len(crop_plain) > len(plain_check) * 0.3:
                        all_md_parts.extend(crop_md_parts)
                        logging.info("Crop '%s' added %d chars", crop_name, len(crop_plain))

        markdown_text = (
            cc.convert("\n\n".join(all_md_parts))
            if all_md_parts
            else "(No text detected)"
        )

        # Extract fields using selected rule (hybrid: regex + LLM)
        if rule:
            extracted_fields = extract_fields(
                markdown_text, rule, file.filename, original_pages, all_raw_results
            )
            detected_type = rule.get("doc_type", "")
        else:
            extracted_fields = [{"field": "檔案名稱", "ai_value": file.filename}]
            detected_type = ""

        # Save pending OCR result to DB
        ocr_result = db.create_ocr_result(
            filename=file.filename,
            rule_id=rule_id if rule else None,
            detected_type=detected_type,
            ocr_markdown=markdown_text,
            fields=extracted_fields,
        )

        return {
            "result_id": ocr_result["id"],
            "detected_type": detected_type,
            "original_pages": [pil_to_data_url(p) for p in original_pages],
            "markdown": markdown_text,
            "layout_images": [pil_to_data_url(p) for p in all_layout_images],
            "crop_images": [
                {"url": pil_to_data_url(img), "label": label}
                for img, label in all_crop_images
            ],
            "extracted_fields": extracted_fields,
        }

    finally:
        os.unlink(tmp_path)


# ── Detail OCR endpoint (Qwen3 VLM) ──

@app.post("/api/ocr/detail")
async def run_detail_ocr(
    request: Request,
    file: UploadFile = File(...),
    rule_id: int = Form(default=0),
):
    """Detail Mode — single-step Qwen3-VL-32B OCR for all fields."""
    require_auth(request)

    rule = db.get_rule(rule_id) if rule_id else None
    if not rule:
        raise HTTPException(status_code=400, detail="Please select a document type")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in SUPPORTED_EXT:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        if ext == ".pdf":
            pages = render_pdf_pages(tmp_path)
            img = pages[0] if pages else None
            original_pages = pages
        else:
            img = Image.open(tmp_path).copy()
            original_pages = [img]

        if img is None:
            raise HTTPException(status_code=400, detail="Could not read image")

        field_defs = rule.get("fields_json", [])
        field_names = [f["name"] for f in field_defs if f.get("type") != "filename"]
        if not field_names:
            raise HTTPException(status_code=400, detail="No fields defined for this rule")

        doc_type = rule.get("doc_type", "")
        extracted, ocr_text = qwen3_extract(img, doc_type, field_names)

        if not extracted and not ocr_text:
            raise HTTPException(status_code=503, detail="Detail Mode server is not available")

        fields = [{"field": "檔案名稱", "ai_value": file.filename}]
        for name in field_names:
            val = str(extracted.get(name, "no")).strip()
            if not val or val == "null":
                val = "no"
            fields.append({"field": name, "ai_value": val})

        ocr_result = db.create_ocr_result(
            filename=file.filename,
            rule_id=rule_id,
            detected_type=doc_type,
            ocr_markdown=ocr_text,
            fields=fields,
        )

        return {
            "result_id": ocr_result["id"],
            "detected_type": doc_type,
            "original_pages": [pil_to_data_url(p) for p in original_pages],
            "markdown": ocr_text,
            "layout_images": [],
            "crop_images": [],
            "extracted_fields": fields,
        }
    finally:
        os.unlink(tmp_path)


# =====================================================================
# AIOCR v1 — Spec-compliant LLM-first OCR endpoint
# Replaces /api/ocr + /api/ocr/detail with a single unified pipeline
# =====================================================================

import asyncio
import uuid as uuid_module
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, Field
from typing import Literal
from enum import Enum
import aiocr_spec
from ocr_preprocess import preprocess_for_ocr

_executor = ThreadPoolExecutor(max_workers=4)


# ── Response models (for OpenAPI schema) ──

# Auto-generated from aiocr_spec.DOCTYPES so the enum stays in sync with the spec.
DocTypeCode = Enum(
    "DocTypeCode",
    {code.upper(): code for code in aiocr_spec.DOCTYPES.keys()},
    type=str,
)
FlowKey = Enum(
    "FlowKey",
    {key.upper(): key for key in aiocr_spec.FLOWS.keys()},
    type=str,
)


class AIOCRDocType(BaseModel):
    code: DocTypeCode = Field(..., description="Doctype identifier — restricted to one of the flow's allowed codes (see /v1/aiocr/flows)")
    label: str = Field(..., description="Display label in zh-Hant")
    confidence: float = Field(..., ge=0, le=1, description="Classifier confidence 0..1")
    evidence_image_url: str = Field("", description="Placeholder URL for evidence crop (v1 demo: empty path returned)")


class AIOCRField(BaseModel):
    key: str = Field(..., description="Stable field identifier")
    label: str = Field(..., description="Display label in zh-Hant")
    value: str = Field("", description="Raw extracted value; empty string if not found")
    normalized_value: str = Field("", description="Normalized form (dates → YYYY-MM-DD); same as value for other types")
    confidence: float = Field(..., ge=0, le=1, description="Ensemble agreement score: 0.95 (3/3), 0.78 (2/3), 0.55 (1/3), 0.0 (missing)")
    needs_review: bool = Field(..., description="True when confidence < 0.85 or value is empty")
    evidence_image_url: str = Field("", description="Placeholder URL for evidence crop")


class AIOCRDocument(BaseModel):
    document_id: str
    file_id: str = Field(..., description="From request file_manifest, or the filename if omitted")
    file_name: str
    doc_type: AIOCRDocType
    fields: list[AIOCRField]


class AIOCRWarning(BaseModel):
    code: str = Field(..., description="Error code, e.g. UNSUPPORTED_FILE_TYPE, OCR_FAILED")
    message: str = ""


class AIOCRError(BaseModel):
    code: str
    message: str = ""


class AIOCRResponse(BaseModel):
    job_id: str = Field(..., description="AIJOB-YYYYMMDD-<uuid8>")
    status: Literal["completed", "failed", "partial"]
    case_id: str
    flow_key: FlowKey = Field(..., description="One of: marriage | funeral | contract | onboarding")
    documents: list[AIOCRDocument] = []
    warnings: list[AIOCRWarning] = []
    error: AIOCRError | None = None


class AIOCRFlowDoctype(BaseModel):
    code: DocTypeCode
    label: str
    description: str


class AIOCRFlow(BaseModel):
    label: str
    doctypes: list[AIOCRFlowDoctype]


def _adaptive_threshold(img: "Image.Image") -> "Image.Image":
    """Preprocessing variant: adaptive threshold (best for handwritten on aged paper)."""
    import cv2
    arr = np.array(img.convert("RGB"))
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
    )
    return Image.fromarray(cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB))


def _resize_long_side(img: "Image.Image", target: int = 1280) -> "Image.Image":
    """Preprocessing variant: resize to target long side (best for Arabic digits)."""
    w, h = img.size
    scale = target / max(w, h)
    if abs(scale - 1.0) < 0.05:
        return img
    interp = Image.LANCZOS if scale > 1 else Image.LANCZOS
    return img.resize((int(w * scale), int(h * scale)), interp)


def _qwen_ocr(img: "Image.Image", prompt: str, max_tokens: int = 1024) -> str:
    """Call Qwen with assistant-prefix trick to suppress chain-of-thought."""
    client = OpenAI(base_url=QWEN3_URL, api_key="dummy")
    img_b64 = pil_to_base64(img)
    try:
        resp = client.chat.completions.create(
            model=QWEN3_MODEL,
            messages=[
                {"role": "user", "content": [
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                    {"type": "text", "text": prompt},
                ]},
                {"role": "assistant", "content": ""},
            ],
            max_tokens=max_tokens,
            temperature=0.0,
            extra_body={"add_generation_prompt": False, "continue_final_message": True},
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        logging.warning("Qwen OCR call failed: %s", e)
        return ""


def _parse_json_response(text: str) -> dict:
    """Parse JSON from Qwen response, stripping markdown fences if present."""
    text = text.strip()
    if text.startswith("```"):
        lines = [l for l in text.split("\n") if not l.strip().startswith("```")]
        text = "\n".join(lines)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass
    return {}


def _classify_document(img: "Image.Image", flow_key: str) -> tuple[str, float]:
    """Ask LLM which doctype this document is. Returns (doctype_code, confidence)."""
    prompt = aiocr_spec.classification_prompt(flow_key)
    response = _qwen_ocr(img, prompt, max_tokens=64)
    allowed = aiocr_spec.FLOWS[flow_key]["doctypes"]
    response_lower = response.lower().strip()
    for code in allowed:
        if code in response_lower:
            # Single clear answer = high confidence
            confidence = 0.9 if response_lower.startswith(code) or len(response_lower) < 30 else 0.7
            return code, confidence
    # Fallback to first option
    return allowed[0], 0.3


def _extract_fields_from_variant(img: "Image.Image", doctype_code: str) -> dict:
    """Run extraction prompt on one image variant. Returns {field_key: value}."""
    prompt = aiocr_spec.extraction_prompt(doctype_code)
    response = _qwen_ocr(img, prompt, max_tokens=1024)
    parsed = _parse_json_response(response)
    return {k: str(v).strip() for k, v in parsed.items() if v}


def _ensemble_extract(img: "Image.Image", doctype_code: str) -> dict[str, dict]:
    """Run multiple preprocessing variants in parallel, score by agreement.

    Returns {field_key: {"value": str, "confidence": float, "alternatives": [str], "sources": [str]}}
    """
    variants = {
        "raw": img,
        "adaptive": _adaptive_threshold(img),
        "resize_1280": _resize_long_side(img, 1280),
    }

    # Run all variants in parallel via executor
    loop = asyncio.get_event_loop() if False else None
    results = {}
    futures = {name: _executor.submit(_extract_fields_from_variant, v_img, doctype_code)
               for name, v_img in variants.items()}
    for name, fut in futures.items():
        try:
            results[name] = fut.result(timeout=120)
        except Exception as e:
            logging.warning("Variant %s failed: %s", name, e)
            results[name] = {}

    # Aggregate per field
    dt = aiocr_spec.DOCTYPES[doctype_code]
    aggregated = {}
    for field_key in dt["fields"]:
        candidates = {}  # value → list of variant names
        for variant_name, fields in results.items():
            v = fields.get(field_key, "").strip()
            if v and v.lower() not in ("null", "none", "no", "n/a"):
                candidates.setdefault(v, []).append(variant_name)

        if not candidates:
            aggregated[field_key] = {
                "value": "", "confidence": 0.0, "alternatives": [], "sources": [],
            }
            continue

        # Confidence: more variants agree → higher
        sorted_cands = sorted(candidates.items(), key=lambda x: -len(x[1]))
        best_value, best_sources = sorted_cands[0]
        n_agree = len(best_sources)
        total = len(variants)
        # 3/3 agree: 0.95, 2/3: 0.75, 1/3: 0.50
        if n_agree == total:
            confidence = 0.95
        elif n_agree >= 2:
            confidence = 0.78
        else:
            confidence = 0.55
        alternatives = [v for v, _ in sorted_cands[1:]]

        aggregated[field_key] = {
            "value": best_value,
            "confidence": confidence,
            "alternatives": alternatives,
            "sources": best_sources,
        }
    return aggregated


def _build_field_response(field_key: str, ext: dict) -> dict:
    """Build a spec-compliant field response object."""
    field_def = aiocr_spec.FIELDS.get(field_key, {"label": field_key, "type": "string"})
    value = ext["value"]
    normalized = aiocr_spec.normalize_value(value, field_key) if value else ""
    needs_review = ext["confidence"] < 0.85 or not value
    return {
        "key": field_key,
        "label": field_def["label"],
        "value": value,
        "normalized_value": normalized,
        "confidence": round(ext["confidence"], 2),
        "needs_review": needs_review,
        "evidence_image_url": "",  # placeholder for v1
    }


@app.post(
    "/v1/aiocr/analyze",
    tags=["aiocr-v1"],
    response_model=AIOCRResponse,
    summary="Analyze one or more files in a flow",
    response_description="Per-file classification + extraction with confidence scoring",
)
async def aiocr_analyze(
    request: Request,
    files: list[UploadFile] = File(..., description="One or more files (PDF, JPG, PNG)"),
    case_id: str = Form(..., description="ERP case identifier (any string)"),
    flow_key: str = Form(..., description="One of: marriage | funeral | contract | onboarding"),
    file_manifest: str = Form(
        default="[]",
        description='JSON array assigning file_ids: [{"file_id":"FILE-001","file_name":"a.pdf"}]. Optional — defaults to using the filename as file_id.',
    ),
):
    """
    Spec-compliant endpoint: process multiple files in one flow with confidence.

    Each file → one document, independently classified and field-extracted.
    Returns `documents[]` with doc_type + fields[] (value, normalized_value,
    confidence ∈ [0,1], needs_review flag).
    """
    require_auth(request)

    job_id = f"AIJOB-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid_module.uuid4().hex[:8]}"

    # Validate flow_key
    if flow_key not in aiocr_spec.FLOWS:
        return {
            "job_id": job_id, "status": "failed",
            "case_id": case_id, "flow_key": flow_key,
            "error": {"code": "INVALID_FLOW_KEY", "message": f"Unknown flow: {flow_key}"},
        }

    # Parse file_manifest into {filename: file_id} mapping
    try:
        manifest = json.loads(file_manifest) if file_manifest else []
        manifest_by_name = {m.get("file_name"): m.get("file_id") for m in manifest}
    except json.JSONDecodeError:
        manifest_by_name = {}

    documents = []
    warnings = []

    for upload in files:
        ext = os.path.splitext(upload.filename or "")[1].lower()
        if ext not in SUPPORTED_EXT:
            warnings.append({
                "code": "UNSUPPORTED_FILE_TYPE",
                "message": f"{upload.filename}: unsupported extension {ext}",
            })
            continue

        # Save to temp + load image
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            content = await upload.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            if ext == ".pdf":
                pages = render_pdf_pages(tmp_path, dpi=200)
                if not pages:
                    warnings.append({"code": "FILE_UNREADABLE", "message": upload.filename})
                    continue
                img = pages[0]
            else:
                img = Image.open(tmp_path).convert("RGB")

            # Classify
            doctype_code, type_conf = _classify_document(img, flow_key)
            doctype_def = aiocr_spec.DOCTYPES[doctype_code]

            # Ensemble extract
            extracted = _ensemble_extract(img, doctype_code)
            fields = [_build_field_response(k, v) for k, v in extracted.items()]

            doc_id = f"DOC-{uuid_module.uuid4().hex[:8]}"
            documents.append({
                "document_id": doc_id,
                "file_id": manifest_by_name.get(upload.filename, upload.filename),
                "file_name": upload.filename,
                "doc_type": {
                    "code": doctype_code,
                    "label": doctype_def["label"],
                    "confidence": round(type_conf, 2),
                    "evidence_image_url": f"/evidence/{job_id}/documents/{doc_id}_type.png",
                },
                "fields": fields,
            })
        except Exception as e:
            logging.exception("Failed to process %s", upload.filename)
            warnings.append({"code": "OCR_FAILED", "message": f"{upload.filename}: {e}"})
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    status = "completed" if documents else "failed"
    response = {
        "job_id": job_id,
        "status": status,
        "case_id": case_id,
        "flow_key": flow_key,
        "documents": documents,
        "warnings": warnings,
    }
    if status == "failed" and not documents:
        response["error"] = {"code": "OCR_FAILED", "message": "No documents processed"}

    return response


@app.get(
    "/v1/aiocr/flows",
    tags=["aiocr-v1"],
    response_model=dict[str, AIOCRFlow],
    summary="List flows and allowed doctypes",
)
async def aiocr_flows(request: Request):
    """List available flows + their doctypes (for frontend selectors)."""
    require_auth(request)
    return {
        flow_key: {
            "label": flow["label"],
            "doctypes": [
                {
                    "code": code,
                    "label": aiocr_spec.DOCTYPES[code]["label"],
                    "description": aiocr_spec.DOCTYPES[code]["description"],
                }
                for code in flow["doctypes"]
            ],
        }
        for flow_key, flow in aiocr_spec.FLOWS.items()
    }


# ── Rules API (legacy) ──

@app.get("/api/rules")
async def list_rules(request: Request):
    require_auth(request)
    return db.get_rules()


@app.post("/api/rules")
async def create_rule_endpoint(request: Request):
    require_auth(request)
    body = await request.json()
    rule = db.create_rule(
        welfare_item=body.get("welfare_item", ""),
        category=body.get("category", ""),
        doc_type=body.get("doc_type", ""),
        fields=body.get("fields_json", []),
        notes=body.get("notes", ""),
    )
    return rule


@app.put("/api/rules/{rule_id}")
async def update_rule_endpoint(rule_id: int, request: Request):
    require_auth(request)
    body = await request.json()
    rule = db.update_rule(rule_id, **body)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@app.delete("/api/rules/{rule_id}")
async def delete_rule_endpoint(rule_id: int, request: Request):
    require_auth(request)
    if not db.delete_rule(rule_id):
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"ok": True}


# ── OCR Results API ──

@app.get("/api/results")
async def list_results(request: Request):
    require_auth(request)
    return db.get_ocr_results()


@app.get("/api/results/{result_id}")
async def get_result(result_id: str, request: Request):
    require_auth(request)
    result = db.get_ocr_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@app.post("/api/results/{result_id}/review")
async def review_result(result_id: str, request: Request):
    require_auth(request)
    body = await request.json()
    result = db.update_ocr_result(
        result_id,
        fields=body.get("fields", []),
        edit_reason=body.get("edit_reason", ""),
    )
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


# ===================== Startup =====================

@app.on_event("startup")
async def startup():
    db.init_db()
    print(f"Database initialized. Rules count: {len(db.get_rules())}")


# ===================== Run =====================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
