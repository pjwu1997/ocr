# AsiaMath OCR — API Usage Guide

Two OCR engines on dual RTX 5090 GPUs, accessible via OpenAI-compatible APIs.

## Services

| Service | GPU | Model | Port | Speed | Best for |
|---------|-----|-------|------|-------|----------|
| **PaddleOCR** | GPU 0 | PaddleOCR-VL-1.5-0.9B | `8000` | ~2s | Printed text, tables, forms |
| **Qwen3-VL** | GPU 1 | Qwen3-VL-32B-Instruct-AWQ | `8010` | ~30s | Handwriting, gold text, English docs |
| **Web UI** | — | Both | `7860` | — | Interactive (login: admin/123) |

All services auto-restart on reboot via `docker compose`.

```
GPU 0 (RTX 5090, 30GB)              GPU 1 (RTX 5090, 28GB)
┌─────────────────────┐             ┌─────────────────────────┐
│ ocr-vllm-server     │             │ qwen3-vl-server         │
│ PaddleOCR-VL-1.5    │             │ Qwen3-VL-32B-AWQ        │
│ vLLM 0.10.2         │             │ vLLM 0.20.2 (Docker)    │
│ port 8000           │             │ port 8010               │
└────────┬────────────┘             └────────┬────────────────┘
         │                                   │
         └──────────┐       ┌────────────────┘
                    ▼       ▼
              ┌─────────────────┐
              │   ocr-web-app   │
              │   FastAPI       │
              │   port 7860     │
              │                 │
              │ POST /api/ocr        → PaddleOCR (fast)
              │ POST /api/ocr/detail → Qwen3 (accurate)
              │ GET  /api/rules      → rule list
              │ GET  /api/results    → history
              └─────────────────┘
```

---

## 1. PaddleOCR — Fast OCR (port 8000)

Uses layout detection + VLM pipeline. Best for printed Chinese documents, tables, forms.

### Via Web App API (recommended — includes layout detection + field extraction)

```python
import requests

# Authenticate
session = requests.Session()
session.post("http://localhost:7860/login",
             data={"username": "admin", "password": "123"})

# Run OCR with field extraction
with open("document.pdf", "rb") as f:
    resp = session.post(
        "http://localhost:7860/api/ocr",
        files={"file": ("document.pdf", f)},
        data={"rule_id": 12},  # 12=公文, see Rule IDs below
        timeout=300,
    )

data = resp.json()
print(data["markdown"])           # Full OCR text (markdown)
print(data["extracted_fields"])   # Structured fields
# [{"field": "發文者", "ai_value": "臺中市政府經濟發展局"}, ...]
```

### Via vLLM API directly (raw VLM, no layout detection)

```python
from openai import OpenAI
import base64

client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")

with open("image.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

resp = client.chat.completions.create(
    model="PaddleOCR-VL-1.5-0.9B",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
            {"type": "text", "text": "OCR:"},
        ]
    }],
    max_tokens=4096,
    temperature=0.0,
)
print(resp.choices[0].message.content)
```

> **Note:** Direct vLLM calls skip layout detection. Use the web app API for multi-region documents.

---

## 2. Qwen3-VL — Detail Mode (port 8010)

32B general-purpose VLM. Reads entire image, extracts fields via prompt. Best for handwriting, low-contrast text, English documents.

### Via Web App API

```python
with open("wedding_invitation.jpg", "rb") as f:
    resp = session.post(
        "http://localhost:7860/api/ocr/detail",
        files={"file": ("invitation.jpg", f)},
        data={"rule_id": 7},   # 7=結婚慶賀金
        timeout=600,            # Qwen3 is slower
    )

data = resp.json()
print(data["extracted_fields"])
```

### Via vLLM API directly (full prompt control)

```python
client = OpenAI(base_url="http://localhost:8010/v1", api_key="dummy")

with open("document.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

resp = client.chat.completions.create(
    model="QuantTrio/Qwen3-VL-32B-Instruct-AWQ",
    messages=[
        {
            "role": "system",
            "content": "你是精確的繁體中文OCR系統。辨識圖片中所有文字並提取指定欄位。以JSON回覆。"
        },
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                {"type": "text", "text": "請辨識這張文件中的文字，提取以下欄位：\n- 發文者\n- 發文日期\n- 主旨\n\n以JSON回覆。"},
            ]
        }
    ],
    max_tokens=2048,
    temperature=0.0,
)
print(resp.choices[0].message.content)
```

### Prompt templates for common document types

```python
# Wedding invitation (喜帖)
prompt = """請從這張喜帖中提取以下欄位：
- 新郎姓名
- 新娘姓名（在「令媛」後面，不是母親名字）
- 宴客日期
- 餐廳名稱
- 地址
- 電話
以JSON回覆。"""

# Obituary (訃聞)
prompt = """請從這份訃聞中提取：
- 亡者姓名
- 享年
- 儀式日期
- 公祭時間
- 儀式地點
以JSON回覆。"""

# Invoice (發票)
prompt = """請從這張發票中提取：
- 發票號碼
- 消費日期
- 買方統編
- 消費金額
以JSON回覆。"""
```

---

## 3. Batch Processing

### PaddleOCR first, Qwen3 fallback for missing fields

```python
import requests
from pathlib import Path

session = requests.Session()
session.post("http://localhost:7860/login",
             data={"username": "admin", "password": "123"})

results = []
for file_path in sorted(Path("./documents").glob("*.pdf")):
    with open(file_path, "rb") as f:
        # Fast pass
        resp = session.post(
            "http://localhost:7860/api/ocr",
            files={"file": (file_path.name, f)},
            data={"rule_id": 12},
            timeout=300,
        )

    data = resp.json()
    fields = {f["field"]: f["ai_value"] for f in data["extracted_fields"]}
    missing = [k for k, v in fields.items() if v == "no"]

    if missing:
        # Qwen3 fallback
        with open(file_path, "rb") as f:
            detail = session.post(
                "http://localhost:7860/api/ocr/detail",
                files={"file": (file_path.name, f)},
                data={"rule_id": 12},
                timeout=600,
            )
        data = detail.json()
        fields = {f["field"]: f["ai_value"] for f in data["extracted_fields"]}

    results.append({"file": file_path.name, **fields})
    print(f"{file_path.name}: {len(fields)} fields, {len(missing)} via Qwen3")
```

### Qwen3 only (all documents through Detail Mode)

```python
for file_path in sorted(Path("./documents").glob("*.*")):
    with open(file_path, "rb") as f:
        resp = session.post(
            "http://localhost:7860/api/ocr/detail",
            files={"file": (file_path.name, f)},
            data={"rule_id": 7},
            timeout=600,
        )
    data = resp.json()
    for f in data["extracted_fields"]:
        print(f"  {f['field']}: {f['ai_value']}")
```

---

## 4. Image Preprocessing (optional)

For better Qwen3 results on difficult images (gold text, low contrast):

```python
import cv2
import numpy as np
from PIL import Image

def preprocess_for_qwen(img_path, target_long_side=1280):
    """Resize + contrast enhance — optimal for Qwen3-VL."""
    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    scale = target_long_side / max(h, w)
    if abs(scale - 1.0) > 0.05:
        interp = cv2.INTER_LANCZOS4 if scale > 1 else cv2.INTER_AREA
        img = cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=interp)

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.convertScaleAbs(l, alpha=1.5, beta=0)
    img = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
```

---

## 5. Rule IDs

| ID | Category | Document Type |
|----|----------|---------------|
| 1 | 接駁車 | 接駁車搭乘登記表 |
| 2 | 用餐調整表 | 用餐費用調整表 |
| 3 | 員工子女教育補助金 | 繳費收據 |
| 4 | 教育獎學金 | 成績單 |
| 5 | 員工進修補助金 | 繳費收據 |
| 6 | 清潔打卡資料 | 出勤卡 |
| 7 | 結婚慶賀金 | 喜帖/結婚證書 |
| 8 | 喪葬奠儀 | 訃聞/死亡證明 |
| 9 | 生育慶賀金 | 出生證明 |
| 10 | 活動請款 | 發票/收據 |
| 11 | 急難救助金 | 診斷證明 |
| 12 | 公文分發 | 公文 |
| 13 | 郵件分發 | 信封 |
| 14 | 廠商合約 | 特約商合約 |
| 15 | 矽品特約合約書 | 優惠內容 |
| 16 | 例行表單 | 巡檢表/體檢表 |

Get full list:
```python
rules = session.get("http://localhost:7860/api/rules").json()
for r in rules:
    print(f"ID={r['id']} {r['category']} → {r['doc_type']}")
```

---

## 6. Docker Management

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f vllm-server      # PaddleOCR
docker compose logs -f qwen3-vl-server  # Qwen3
docker compose logs -f web-app          # Web app

# Restart single service
docker compose restart web-app

# Stop everything
docker compose down
```

---

## 7. Troubleshooting

| Problem | Fix |
|---------|-----|
| Run OCR fails | Check `docker compose logs vllm-server` — PaddleOCR may need restart |
| Detail Mode fails | Check `docker compose logs qwen3-vl-server` — Qwen3 takes ~3 min to start |
| Port conflict | `docker compose down && docker compose up -d --remove-orphans` |
| GPU OOM | Reduce `max-model-len` in docker-compose.yml |
| Slow first request | Models need warmup on first inference after start |
