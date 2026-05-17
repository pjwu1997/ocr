# AsiaMath AIOCR — API Reference (v1)

Implementation of `ai_api_spec.md` over the `/v1/aiocr/*` namespace.
Base URL: `http://<host>:7860`
Auth: session cookie from `POST /login` (form fields `username`, `password`).
All `v1/aiocr/*` endpoints require an authenticated session.

---

## Endpoints

### `POST /login`

Form-encoded login. Sets a session cookie on success.

```
POST /login
Content-Type: application/x-www-form-urlencoded

username=admin&password=123
```

→ `200` (redirect to `/`) on success, `401` on failure.

---

### `GET /v1/aiocr/flows`

Returns the full flow → doctype catalogue. Useful for populating UI selectors.

**Response 200**

```json
{
  "marriage": {
    "label": "結婚慶賀金",
    "doctypes": [
      {"code": "wedding_invitation", "label": "喜帖",
       "description": "中文紅色喜帖，常見金色裝飾文字…"},
      ...
    ]
  },
  "funeral":     { "label": "喪葬奠儀",      "doctypes": [...] },
  "contract":    { "label": "手寫合約辨識",  "doctypes": [...] },
  "onboarding":  { "label": "面試通過者文件", "doctypes": [...] }
}
```

---

### `POST /v1/aiocr/analyze`

Run OCR on one or more files within a flow. Each file → one document
(classified + field-extracted independently). Multipart form.

**Request**

```
POST /v1/aiocr/analyze
Content-Type: multipart/form-data

case_id        = string              (any ERP case identifier)
flow_key       = string              (one of: marriage|funeral|contract|onboarding)
file_manifest  = JSON string         (optional — see below)
files          = file[] (1..N)       (PDF, JPG, JPEG, PNG)
```

`file_manifest` is a JSON array that lets the caller assign stable IDs to files
so they can be referenced back in the response:

```json
[
  {"file_id": "FILE-001", "file_name": "marriage_cert.pdf"},
  {"file_id": "FILE-002", "file_name": "household.jpg"}
]
```

If omitted, the filename itself is used as `file_id`.

**Response 200** — completed

```json
{
  "job_id":  "AIJOB-20260517-3d3a434f",
  "status":  "completed",        // completed | partial | failed
  "case_id": "CASE-2026-001",
  "flow_key": "marriage",
  "documents": [
    {
      "document_id": "DOC-232f44eb",
      "file_id":     "FILE-001",
      "file_name":   "7.喜帖(中文).jpg",
      "doc_type": {
        "code":  "wedding_invitation",
        "label": "喜帖",
        "confidence": 0.90,
        "evidence_image_url": "/evidence/AIJOB-…/documents/DOC-…_type.png"
      },
      "fields": [
        {
          "key":   "employee_name",
          "label": "員工姓名",
          "value": "何承澄",
          "normalized_value": "何承澄",
          "confidence": 0.78,
          "needs_review": true,
          "evidence_image_url": ""
        },
        ...
      ]
    }
  ],
  "warnings": []
}
```

**Response 200** — error case

```json
{
  "job_id": "AIJOB-…",
  "status": "failed",
  "case_id": "…",
  "flow_key": "x",
  "error": { "code": "INVALID_FLOW_KEY", "message": "Unknown flow: x" }
}
```

**Error codes** (in `error.code` or `warnings[].code`)

| Code | Meaning |
|---|---|
| `INVALID_FLOW_KEY` | `flow_key` not one of the four allowed values |
| `UNSUPPORTED_FILE_TYPE` | File extension not in `.pdf .jpg .jpeg .png` |
| `FILE_UNREADABLE` | PDF/image couldn't be decoded |
| `OCR_FAILED` | Qwen call or downstream processing threw |
| `INTERNAL_ERROR` | Unexpected server error |

`UNSUPPORTED_FILE_TYPE` / `OCR_FAILED` are emitted as per-file `warnings`
when other files succeed; `INVALID_FLOW_KEY` aborts the whole request.

---

## Confidence semantics

Each `confidence` ∈ `[0.0, 1.0]`. Derived from agreement across the 3-variant
Qwen ensemble (raw image / adaptive-threshold / resize-1280):

| Variants agree | Confidence | UI band | `needs_review` |
|---:|---:|---|:-:|
| 3/3 | 0.95 | green  | false |
| 2/3 | 0.78 | yellow | true  |
| 1/3 | 0.55 | red    | true  |
| 0/3 | 0.00 | red    | true  |

For `doc_type.confidence`, scoring is heuristic on the classifier response
(starts-with the code → 0.90; substring match → 0.70; fallback → 0.30).

**ERP integration guidance**

- `needs_review == false` → safe to autopost.
- `needs_review == true && value != ""` → surface for human review with the
  evidence URL.
- `value == ""` → field genuinely missing on the document.

---

## Normalization

`normalized_value` is currently populated for date fields only.
All other types are passthrough (= `value`).

Date inputs accepted and rewritten to `YYYY-MM-DD`:

| Input | Normalized |
|---|---|
| `2026-03-20`     | `2026-03-20` |
| `2026/3/20`      | `2026-03-20` |
| `2026.3.20`      | `2026-03-20` |
| `中華民國 115 年 3 月 20 日` | `2026-03-20` |
| `民國 115 年 3 月 20 日`    | `2026-03-20` |
| anything else    | passthrough |

---

## Flows × Doctypes × Fields

### marriage — 結婚慶賀金

| Code | Label | Required-fields |
|---|---|---|
| `wedding_invitation` | 喜帖 | employee_name, spouse_name, banquet_date, document_issue_date |
| `marriage_certificate` | 結婚證書 / 結婚證明 | employee_name, employee_english_name, spouse_name, marriage_date, document_issue_date |
| `household_registration_marriage` | 戶口名簿 / 戶籍謄本 | employee_name, spouse_name, marriage_date |
| `relationship_proof` | 關係證明 | employee_name, spouse_name |
| `benefit_application_form` | 補助申請表 | employee_name, document_issue_date |

### funeral — 喪葬奠儀

| Code | Label | Required-fields |
|---|---|---|
| `obituary` | 訃聞 | deceased_name, funeral_date, funeral_location, employee_name, relationship |
| `death_certificate` | 死亡證明書 / 死亡診斷證明 | deceased_name, death_date |
| `deregistered_household_registration` | 除戶戶籍謄本 | deceased_name, death_date, employee_name, relationship |
| `relationship_proof` | 關係證明 | employee_name, spouse_name |
| `funeral_permit_or_cremation_proof` | 埋葬 / 火化 / 殯葬證明 | deceased_name, funeral_date, funeral_location |
| `funeral_application_form` | 申請表 | employee_name, deceased_name, relationship |

### contract — 手寫合約辨識

| Code | Label | Required-fields |
|---|---|---|
| `handwritten_contract` | 手寫合約主文件 | contract_title, party_a_name, party_b_name, contract_no, effective_date, start_date, end_date, service_scope, amount, payment_terms, handwritten_text, signature_or_stamp_present |
| `contract_attachment` | 合約附件 | contract_title, handwritten_text |
| `signature_stamp_page` | 簽名 / 用印頁 | party_a_name, party_b_name, signature_or_stamp_present |
| `handwritten_note` | 手寫補充條款 / 備註 | handwritten_text, low_confidence_segments |
| `unclear_scan` | 模糊掃描件 | handwritten_text, low_confidence_segments |

### onboarding — 面試通過者文件

| Code | Label | Required-fields |
|---|---|---|
| `onboarding_form` | 人事基本資料表 / 報到表 | candidate_name, candidate_english_name, id_number, birth_date, position_name |
| `id_card` | 身分證 / 居留證 / 護照 | candidate_name, candidate_english_name, id_number, birth_date |
| `education_certificate` | 最高學歷證明 | candidate_name, education_level, school_name |
| `health_check_report` | 體檢報告 | candidate_name, health_check_date |
| `bank_account_copy` | 存摺封面 / 薪轉帳戶 | candidate_name, bank_name, bank_account |
| `professional_license` | 專業證照 | candidate_name, license_name |
| `insurance_transfer_proof` | 勞健保轉出 / 退保證明 | candidate_name, id_number |
| `photo` | 識別證照片 | candidate_name |
| `previous_employment_proof` | 離職 / 服務證明 | candidate_name, position_name |

---

## Field reference

| Key | Label | Type |
|---|---|---|
| employee_name | 員工姓名 | string |
| employee_english_name | 員工英文姓名 | string |
| spouse_name | 配偶姓名 | string |
| marriage_date | 結婚生效日 / 登記日 | date |
| banquet_date | 宴客日期 | date |
| document_issue_date | 文件核發日 | date |
| deceased_name | 亡者姓名 | string |
| relationship | 亡者關係 | string |
| death_date | 死亡日期 | date |
| funeral_date | 儀式日期 | date |
| funeral_location | 儀式地點 | string |
| contract_title | 文件標題 | string |
| party_a_name | 甲方名稱 | string |
| party_b_name | 乙方名稱 | string |
| contract_no | 合約編號 | string |
| effective_date | 生效日期 | date |
| start_date | 履約起日 | date |
| end_date | 履約迄日 | date |
| service_scope | 服務 / 履約內容 | string |
| amount | 金額 | string |
| payment_terms | 付款條件 | string |
| handwritten_text | 手寫全文 | string |
| low_confidence_segments | 低信心段落 | string |
| signature_or_stamp_present | 是否簽名 / 用印 | boolean |
| candidate_name | 面試者姓名 | string |
| candidate_english_name | 英文姓名 | string |
| id_number | 身分證字號 | string |
| birth_date | 出生日期 | date |
| position_name | 應徵職務 | string |
| education_level | 最高學歷 | string |
| school_name | 學校名稱 | string |
| health_check_date | 體檢日期 | date |
| bank_name | 銀行名稱 | string |
| bank_account | 銀行帳號 | string |
| license_name | 證照名稱 | string |

---

## Example — full request/response

```bash
# 1. Login (session cookie saved to /tmp/cookie)
curl -s -c /tmp/cookie -d "username=admin&password=123" \
  -L http://localhost:7860/login > /dev/null

# 2. Analyze
curl -s -b /tmp/cookie \
  -F "case_id=CASE-2026-001" \
  -F "flow_key=marriage" \
  -F 'file_manifest=[{"file_id":"FILE-001","file_name":"invitation.jpg"}]' \
  -F "files=@invitation.jpg" \
  http://localhost:7860/v1/aiocr/analyze | jq
```

Response:

```json
{
  "job_id": "AIJOB-20260517-3d3a434f",
  "status": "completed",
  "case_id": "CASE-2026-001",
  "flow_key": "marriage",
  "documents": [{
    "document_id": "DOC-232f44eb",
    "file_id": "FILE-001",
    "file_name": "invitation.jpg",
    "doc_type": {
      "code": "wedding_invitation", "label": "喜帖",
      "confidence": 0.9,
      "evidence_image_url": "/evidence/AIJOB-…/documents/DOC-…_type.png"
    },
    "fields": [
      {"key": "employee_name", "label": "員工姓名",
       "value": "王小明", "normalized_value": "王小明",
       "confidence": 0.95, "needs_review": false,
       "evidence_image_url": ""},
      {"key": "banquet_date", "label": "宴客日期",
       "value": "中華民國 115 年 1 月 18 日",
       "normalized_value": "2026-01-18",
       "confidence": 0.95, "needs_review": false,
       "evidence_image_url": ""}
    ]
  }],
  "warnings": []
}
```

---

## Pipeline (informational)

Each file is processed independently:

1. **Decode** — PDF rendered at 200 DPI (first page), images opened as RGB.
2. **Classify** — Qwen3.5-27B-AWQ called with `classification_prompt(flow_key)`; picks one of the flow's allowed codes.
3. **Extract (ensemble)** — three preprocessing variants run in parallel:
   - `raw` — image as decoded
   - `adaptive` — OpenCV adaptive Gaussian threshold (block 31, C 10)
   - `resize_1280` — Lanczos resize to 1280 px long-side
   Each variant gets the same `extraction_prompt(doctype_code)` JSON-shape prompt with the assistant-prefix trick (`continue_final_message=true` + empty assistant string) to suppress chain-of-thought.
4. **Aggregate** — per field, majority value wins; confidence is set from variant agreement.
5. **Normalize** — date fields rewritten to `YYYY-MM-DD`; others passthrough.

Model: `qwen3.5-27b` served by vLLM at `http://qwen-llm-server:8000/v1`
(host port `8010`). Ensemble runs in a 4-worker `ThreadPoolExecutor`.

Typical latency: 3–5 s per page (text-only docs), 10–16 s for handwritten
contracts with the `handwritten_text` field (longer generation).

---

## Notes & limitations (v1 / demo)

- `evidence_image_url` is **placeholder only** — the route exists in the
  response but no image is served at that path yet.
- Multi-page PDFs are processed as **first page only**.
- No queueing — each request blocks for the full ensemble duration.
- `partial` status is reserved but not currently emitted; `completed` returns
  even when individual fields are empty.
