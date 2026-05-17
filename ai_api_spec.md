# AIOCR API 對接規格草案

本文件定義 AIOCR DEMO 階段，ERP 文件處理系統與 AI OCR 服務之間的 API 格式、回傳格式，以及雙方必須一致使用的代碼表。

目前 DEMO 包含四個流程：

| flow_key | 流程名稱 |
|---|---|
| `marriage` | 結婚慶賀金 |
| `funeral` | 喪葬奠儀 |
| `contract` | 手寫合約辨識 |
| `onboarding` | 面試通過者文件 |

## API

### 執行 OCR 分析

```http
POST /v1/aiocr/analyze
Content-Type: multipart/form-data
```

### Request

| 欄位 | 型態 | 必填 | 說明 |
|---|---|---|---|
| `case_id` | string | 是 | ERP 系統案件編號 |
| `flow_key` | string | 是 | 流程代碼，固定為四個流程之一 |
| `files` | file[] | 是 | 一次可上傳多個 PDF / 圖片 |
| `file_manifest` | JSON string | 建議 | 檔案對照資料，用於回傳時對應原始檔案 |

`file_manifest` 範例：

```json
[
  {
    "file_id": "FILE-001",
    "file_name": "A.pdf"
  },
  {
    "file_id": "FILE-002",
    "file_name": "B.jpg"
  }
]
```

> `file_id` 由 ERP 系統產生，AI OCR 服務回傳時需原樣帶回，避免多檔案同名時無法對應。

## Response

### 成功回傳

```json
{
  "job_id": "AIJOB-20260516-001",
  "status": "completed",
  "case_id": "CASE-20260516-001",
  "flow_key": "marriage",
  "documents": [
    {
      "document_id": "DOC-001",
      "file_id": "FILE-001",
      "file_name": "A.pdf",
      "doc_type": {
        "code": "wedding_invitation",
        "label": "喜帖",
        "confidence": 0.92,
        "evidence_image_url": "/evidence/AIJOB-20260516-001/documents/DOC-001_type.png"
      },
      "fields": [
        {
          "key": "employee_name",
          "label": "員工姓名",
          "value": "王小明",
          "normalized_value": "王小明",
          "confidence": 0.95,
          "needs_review": false,
          "evidence_image_url": "/evidence/AIJOB-20260516-001/fields/DOC-001_employee_name.png"
        },
        {
          "key": "spouse_name",
          "label": "配偶姓名",
          "value": "林小雅",
          "normalized_value": "林小雅",
          "confidence": 0.91,
          "needs_review": false,
          "evidence_image_url": "/evidence/AIJOB-20260516-001/fields/DOC-001_spouse_name.png"
        }
      ]
    }
  ],
  "warnings": []
}
```

### Response 欄位說明

| 欄位 | 型態 | 說明 |
|---|---|---|
| `job_id` | string | AI OCR 任務編號 |
| `status` | string | `completed` / `failed` |
| `case_id` | string | ERP 系統案件編號 |
| `flow_key` | string | 流程代碼 |
| `documents` | array | 文件分類與欄位抽取結果 |
| `warnings` | array | 非阻斷性警告 |

### documents

| 欄位 | 型態 | 說明 |
|---|---|---|
| `document_id` | string | AI OCR 產生的文件結果編號 |
| `file_id` | string | ERP 上傳時提供的檔案 ID |
| `file_name` | string | 原始檔名 |
| `doc_type` | object | 文件分類結果 |
| `fields` | array | 此文件抽取到的欄位 |

### doc_type

| 欄位 | 型態 | 說明 |
|---|---|---|
| `code` | string | 文件類型代碼，必須使用雙方約定的 `doctype_code` |
| `label` | string | 文件類型中文名稱 |
| `confidence` | number | 文件分類信心值，範圍 `0` 到 `1` |
| `evidence_image_url` | string | 已標注好的文件分類證據截圖 |

### fields

| 欄位 | 型態 | 說明 |
|---|---|---|
| `key` | string | 欄位代碼，必須使用雙方約定的 `field_key` |
| `label` | string | 欄位中文名稱 |
| `value` | string | AI 原始辨識值 |
| `normalized_value` | string | 標準化後的值，例如日期統一為 `YYYY-MM-DD` |
| `confidence` | number | 欄位辨識信心值，範圍 `0` 到 `1` |
| `needs_review` | boolean | AI OCR 是否建議人工覆核 |
| `evidence_image_url` | string | 已標注好的欄位證據截圖 |

DEMO 第一版不要求 AI OCR 回傳 `bbox`、`source_page`、`evidence_note`。證據圖片需由 AI OCR 服務直接產生已標注好的截圖，ERP 前端只負責顯示。

## 錯誤回傳

```json
{
  "job_id": "AIJOB-20260516-001",
  "status": "failed",
  "case_id": "CASE-20260516-001",
  "flow_key": "marriage",
  "error": {
    "code": "UNSUPPORTED_FILE_TYPE",
    "message": "不支援的檔案格式"
  }
}
```

### 錯誤代碼

| code | 說明 |
|---|---|
| `INVALID_FLOW_KEY` | 未知流程代碼 |
| `UNSUPPORTED_FILE_TYPE` | 不支援的檔案格式 |
| `FILE_UNREADABLE` | 檔案無法讀取 |
| `IMAGE_TOO_BLURRY` | 影像過於模糊 |
| `OCR_FAILED` | OCR 分析失敗 |
| `INTERNAL_ERROR` | AI OCR 服務內部錯誤 |

## 信心值規則

ERP 系統第一版建議依下列規則處理：

| confidence | ERP 顯示與處理 |
|---|---|
| `>= 0.85` | 視為高信心，可直接顯示為通過 |
| `0.60 - 0.84` | 標示待覆核 |
| `< 0.60` | 標示低信心，必須人工確認 |

如果 AI OCR 回傳 `needs_review = true`，即使 `confidence >= 0.85`，ERP 系統仍應標示待覆核。

## 文件類型代碼

本節只定義 AI OCR 服務可回傳的文件類型代碼。文件是否必要、是否缺件、是否允許擇一，屬於 ERP 系統業務規則，不放在 AI API contract 內。

### 結婚慶賀金 `marriage`

| doctype_code | 文件名稱 | 說明 |
|---|---|---|
| `wedding_invitation` | 喜帖 | 結婚流程可能出現的喜帖或宴客佐證文件 |
| `marriage_certificate` | 結婚證書 / 結婚證明 | 結婚日期、配偶姓名、登記資料來源 |
| `household_registration_marriage` | 戶口名簿 / 戶籍謄本 | 婚姻狀態、配偶關係或戶籍資料來源 |
| `relationship_proof` | 關係證明 | 配偶關係或親屬關係來源 |
| `benefit_application_form` | 補助申請表 | 申請書或系統外部表單來源 |

### 喪葬奠儀 `funeral`

| doctype_code | 文件名稱 | 說明 |
|---|---|---|
| `obituary` | 訃聞 | 儀式日期、地點、亡者資訊可能來源 |
| `death_certificate` | 死亡證明書 / 死亡診斷證明 | 亡者姓名、死亡日期來源 |
| `deregistered_household_registration` | 除戶戶籍謄本 | 除戶與親屬資料來源 |
| `relationship_proof` | 申請人與亡者關係證明 | 申請人與亡者關係來源 |
| `funeral_permit_or_cremation_proof` | 埋葬 / 火化 / 殯葬證明 | 殯葬、火化或埋葬資料來源 |
| `funeral_application_form` | 申請表 | 申請書或系統外部表單來源 |

### 手寫合約辨識 `contract`

| doctype_code | 文件名稱 | 說明 |
|---|---|---|
| `handwritten_contract` | 手寫合約主文件 | 合約全文與條款來源 |
| `contract_attachment` | 合約附件 | 合約補充資料或附件 |
| `signature_stamp_page` | 簽名 / 用印頁 | 簽名、用印或確認頁來源 |
| `handwritten_note` | 手寫補充條款 / 備註 | 手寫補充條款或備註來源 |
| `unclear_scan` | 模糊掃描件 | AI OCR 判斷影像品質不足時使用 |

### 面試通過者文件 `onboarding`

| doctype_code | 文件名稱 | 說明 |
|---|---|---|
| `onboarding_form` | 人事基本資料表 / 報到表 | 新進人員基本資料來源 |
| `id_card` | 身分證 / 居留證 / 護照 | 身分資料來源 |
| `education_certificate` | 最高學歷證明 | 學歷資料來源 |
| `health_check_report` | 體檢報告 | 體檢日期與體檢結果來源 |
| `bank_account_copy` | 存摺封面 / 薪轉帳戶 | 銀行與帳號資料來源 |
| `professional_license` | 專業證照 | 證照名稱、證照編號或效期來源 |
| `insurance_transfer_proof` | 勞健保轉出 / 退保證明 | 保險轉出或退保資料來源 |
| `photo` | 識別證照片 | 識別證照片來源 |
| `previous_employment_proof` | 離職 / 服務證明 | 前職服務或離職資料來源 |

## 欄位代碼

### 結婚慶賀金 `marriage`

| field_key | 欄位名稱 | 說明 |
|---|---|---|
| `employee_name` | 員工姓名 | ERP 比對員工主檔 |
| `employee_english_name` | 員工英文姓名 | ERP 比對員工主檔 |
| `spouse_name` | 配偶姓名 | 文件抽取 |
| `marriage_date` | 結婚生效日 / 登記日 | ERP 判斷入廠滿 3 個月 |
| `banquet_date` | 宴客日期 | 喜帖常見欄位 |
| `document_issue_date` | 文件核發日 | 輔助判斷 |

### 喪葬奠儀 `funeral`

| field_key | 欄位名稱 | 說明 |
|---|---|---|
| `employee_name` | 員工姓名 | ERP 比對員工主檔 |
| `employee_english_name` | 員工英文姓名 | ERP 比對員工主檔 |
| `deceased_name` | 亡者姓名 | 文件抽取 |
| `relationship` | 亡者關係 | ERP 比對親屬規則 |
| `death_date` | 死亡日期 | 文件抽取 |
| `funeral_date` | 儀式日期 | 訃聞常見欄位 |
| `funeral_location` | 儀式地點 | 訃聞常見欄位 |

### 手寫合約辨識 `contract`

| field_key | 欄位名稱 | 說明 |
|---|---|---|
| `contract_title` | 文件標題 | 文件抽取 |
| `party_a_name` | 甲方名稱 | 文件抽取 |
| `party_b_name` | 乙方名稱 | 文件抽取 |
| `contract_no` | 合約編號 | 文件抽取 |
| `effective_date` | 生效日期 | 文件抽取 |
| `start_date` | 履約起日 | 文件抽取 |
| `end_date` | 履約迄日 | 文件抽取 |
| `service_scope` | 服務 / 履約內容 | 文件抽取 |
| `amount` | 金額 | 文件抽取 |
| `payment_terms` | 付款條件 | 文件抽取 |
| `handwritten_text` | 手寫全文 | OCR 全文 |
| `low_confidence_segments` | 低信心段落 | AI 標示 |
| `signature_or_stamp_present` | 是否簽名 / 用印 | AI 判斷 |

### 面試通過者文件 `onboarding`

| field_key | 欄位名稱 | 說明 |
|---|---|---|
| `candidate_name` | 面試者姓名 | ERP 比對面試者資料 |
| `candidate_english_name` | 英文姓名 | ERP 比對面試者資料 |
| `id_number` | 身分證字號 | ERP 顯示時需遮罩 |
| `birth_date` | 出生日期 | 文件抽取 |
| `position_name` | 應徵職務 | ERP 比對面試者資料 |
| `education_level` | 最高學歷 | 文件抽取 |
| `school_name` | 學校名稱 | 文件抽取 |
| `health_check_date` | 體檢日期 | 文件抽取 |
| `bank_name` | 銀行名稱 | 文件抽取 |
| `bank_account` | 銀行帳號 | ERP 顯示時需遮罩 |
| `license_name` | 證照名稱 | 文件抽取 |

## ERP 系統比對與規則

AI OCR 回傳後，ERP 系統依下列順序處理：

1. 檢查 `flow_key` 是否正確。
2. 依 `doctype_code` 檢查文件是否缺件。
3. 依 `field_key` 整理欄位結果。
4. 低信心或 `needs_review = true` 的欄位標示待覆核。
5. 比對員工主檔或面試者資料。
6. 執行流程規則，例如入廠滿 3 個月、親屬關係、體檢日期、缺件清單。
7. 產生案件狀態。
8. 進入人工覆核。
9. 覆核完成後保存 AI 原值、人工修正值、信心值與證據截圖。

## 案件狀態建議

| status_code | 中文狀態 | 說明 |
|---|---|---|
| `passed` | 通過 | 文件與規則皆通過 |
| `needs_review` | 待覆核 | 有低信心欄位或資料需人工確認 |
| `missing_documents` | 缺件 | 必要文件不足 |
| `data_mismatch` | 資料不一致 | OCR 結果與主檔不一致 |
| `rule_failed` | 規則不符 | 日期、資格、關係或其他規則不通過 |
| `unknown_document_type` | 文件類型不明 | AI 無法判斷文件類型 |
| `poor_image_quality` | 影像品質不佳 | 掃描模糊或無法辨識 |