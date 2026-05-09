#!/usr/bin/env python3
"""
Gradio frontend for AsiaMath OCR.

Requires the FastAPI backend running:  python app.py
Then:  python gradio_app.py
"""

import base64
import io
import re

import gradio as gr
import pandas as pd
import requests
from PIL import Image

API_BASE = "http://localhost:7860"
USERNAME = "admin"
PASSWORD = "123"


def data_url_to_pil(data_url: str) -> Image.Image:
    img_data = base64.b64decode(data_url.split(",")[1])
    return Image.open(io.BytesIO(img_data))


def _parse_table_block(lines: list[str]) -> pd.DataFrame | None:
    # Remove separator rows (|---|---|)
    data_lines = [l for l in lines if not re.match(r"^\|[\s\-:|]+\|?$", l)]
    if len(data_lines) < 2:
        return None
    rows = [[c.strip() for c in row.strip("|").split("|")] for row in data_lines]
    try:
        return pd.DataFrame(rows[1:], columns=rows[0])
    except Exception:
        return None


def parse_markdown_tables(md_text: str) -> list[pd.DataFrame]:
    tables, buf, in_table = [], [], False
    for line in md_text.splitlines():
        if line.strip().startswith("|"):
            buf.append(line.strip())
            in_table = True
        else:
            if in_table and buf:
                df = _parse_table_block(buf)
                if df is not None:
                    tables.append(df)
            buf, in_table = [], False
    if in_table and buf:
        df = _parse_table_block(buf)
        if df is not None:
            tables.append(df)
    return tables


def tables_to_html(tables: list[pd.DataFrame]) -> str:
    if not tables:
        return "<p style='color:#888'>No tables detected.</p>"
    style = (
        "<style>"
        "table{border-collapse:collapse;width:100%;margin-bottom:16px}"
        "th,td{border:1px solid #ccc;padding:6px 10px;text-align:left;font-size:13px}"
        "th{background:#f0f4f8;font-weight:600}"
        "tr:nth-child(even){background:#fafafa}"
        "</style>"
    )
    parts = [style]
    for i, df in enumerate(tables, 1):
        parts.append(f"<h4>Table {i}</h4>")
        parts.append(df.to_html(index=False, border=0))
    return "".join(parts)


DOC_TYPE_RULES = [
    ("檢驗報告", ["檢驗", "檢查結果", "檢驗報告", "lab", "血液", "尿液", "生化", "血糖", "白血球", "紅血球", "肝功能", "腎功能"]),
    ("病理報告", ["病理", "切片", "病理報告", "組織", "細胞學", "pathology", "腫瘤", "惡性", "良性"]),
    ("護理紀錄", ["護理", "護理紀錄", "生命徵象", "體溫", "血壓", "脈搏", "護理評估", "護理計畫"]),
    ("同意書", ["同意書", "簽署", "告知", "手術同意", "麻醉同意", "知情同意", "授權"]),
]

DEPT_RULES = [
    ("內科", ["內科", "心臟", "腸胃", "胸腔", "腎臟", "感染", "風濕", "內分泌", "血液腫瘤", "神經內科"]),
    ("外科", ["外科", "手術", "骨科", "泌尿", "整形", "神經外科", "心臟外科", "胸腔外科"]),
    ("婦產科", ["婦產", "產檢", "婦科", "產科", "子宮", "卵巢", "胎兒", "妊娠", "分娩"]),
    ("小兒科", ["小兒", "兒童", "兒科", "新生兒", "嬰兒", "pediatric"]),
]


def classify_medical_doc(text: str) -> pd.DataFrame:
    """Classify document type and department based on OCR keywords."""
    text_lower = text.lower()

    def _match(rules):
        results = []
        for label, keywords in rules:
            matched = [kw for kw in keywords if kw.lower() in text_lower]
            if matched:
                results.append((label, matched))
        return results

    doc_matches = _match(DOC_TYPE_RULES)
    dept_matches = _match(DEPT_RULES)

    rows = []
    if doc_matches:
        for label, kws in doc_matches:
            rows.append({"分類維度": "文件分類", "分類結果": label, "命中關鍵字": "、".join(kws)})
    else:
        rows.append({"分類維度": "文件分類", "分類結果": "無法辨識", "命中關鍵字": ""})

    if dept_matches:
        for label, kws in dept_matches:
            rows.append({"分類維度": "科別", "分類結果": label, "命中關鍵字": "、".join(kws)})
    else:
        rows.append({"分類維度": "科別", "分類結果": "無法辨識", "命中關鍵字": ""})

    return pd.DataFrame(rows)


def run_ocr(file):
    if file is None:
        return "No file uploaded.", [], [], "<p>No tables.</p>", pd.DataFrame()

    session = requests.Session()
    session.post(f"{API_BASE}/login", data={"username": USERNAME, "password": PASSWORD})

    filename = file.name if hasattr(file, "name") else "upload"
    with open(filename, "rb") as f:
        resp = session.post(
            f"{API_BASE}/api/ocr",
            files={"file": (filename.split("/")[-1], f)},
            timeout=300,
        )

    if resp.status_code != 200:
        return f"Error {resp.status_code}: {resp.text}", [], [], "", pd.DataFrame()

    data = resp.json()
    markdown = data.get("markdown", "(No text detected)")

    layout_imgs = [data_url_to_pil(url) for url in data.get("layout_images", [])]

    crop_imgs = [
        (data_url_to_pil(item["url"]), item["label"])
        for item in data.get("crop_images", [])
    ]

    tables = parse_markdown_tables(markdown)
    tables_html = tables_to_html(tables)

    classification = classify_medical_doc(markdown)

    return markdown, layout_imgs, crop_imgs, tables_html, classification


with gr.Blocks(title="AsiaMath OCR") as demo:
    gr.Markdown("## AsiaMath OCR")

    with gr.Row():
        file_input = gr.File(
            label="Upload PDF / Image",
            file_types=[".pdf", ".jpg", ".jpeg", ".png"],
            scale=4,
        )
        run_btn = gr.Button("Run OCR", variant="primary", scale=1)

    with gr.Row(equal_height=False):
        with gr.Column(scale=2):
            md_output = gr.Markdown(label="Markdown Preview", value="")

        with gr.Column(scale=1):
            layout_gallery = gr.Gallery(
                label="Layout",
                columns=1,
                object_fit="contain",
                height=500,
            )

        with gr.Column(scale=2):
            crop_gallery = gr.Gallery(
                label="Crops",
                columns=3,
                object_fit="contain",
                height=500,
            )

    gr.Markdown("### 文件分類（依 OCR 關鍵字）")
    classification_output = gr.Dataframe(
        headers=["分類維度", "分類結果", "命中關鍵字"],
        label="文件分類",
        interactive=False,
    )

    gr.Markdown("### Extracted Tables")
    tables_output = gr.HTML(value="<p style='color:#888'>Upload a file and run OCR.</p>")

    run_btn.click(
        fn=run_ocr,
        inputs=file_input,
        outputs=[md_output, layout_gallery, crop_gallery, tables_output, classification_output],
    )

if __name__ == "__main__":
    demo.launch(server_port=8086, server_name="0.0.0.0", theme=gr.themes.Default())
