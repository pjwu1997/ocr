"""
AI OCR specification — document types and field definitions per the ai_api_spec.md contract.

Replaces the regex-based rule system with LLM prompts. Each doctype has:
- label: Chinese display name
- description: hints for LLM classification
- fields: list of field_keys with extraction hints

A flow_key maps to a set of allowed doctype_codes.
"""

# ─── Flow → allowed doctype_codes ───────────────────────────────────────

FLOWS = {
    "marriage": {
        "label": "結婚慶賀金",
        "doctypes": [
            "wedding_invitation",
            "marriage_certificate",
            "household_registration_marriage",
            "relationship_proof",
            "benefit_application_form",
        ],
    },
    "funeral": {
        "label": "喪葬奠儀",
        "doctypes": [
            "obituary",
            "death_certificate",
            "deregistered_household_registration",
            "relationship_proof",
            "funeral_permit_or_cremation_proof",
            "funeral_application_form",
        ],
    },
    "contract": {
        "label": "手寫合約辨識",
        "doctypes": [
            "handwritten_contract",
            "contract_attachment",
            "signature_stamp_page",
            "handwritten_note",
            "unclear_scan",
        ],
    },
    "onboarding": {
        "label": "面試通過者文件",
        "doctypes": [
            "onboarding_form",
            "id_card",
            "education_certificate",
            "health_check_report",
            "bank_account_copy",
            "professional_license",
            "insurance_transfer_proof",
            "photo",
            "previous_employment_proof",
        ],
    },
}

# ─── Document type definitions ──────────────────────────────────────────

DOCTYPES = {
    # ── marriage ──
    "wedding_invitation": {
        "label": "喜帖",
        "description": "中文紅色喜帖，常見金色裝飾文字，內容包含新郎新娘姓名、宴客日期、餐廳。",
        "fields": ["employee_name", "spouse_name", "banquet_date", "document_issue_date"],
    },
    "marriage_certificate": {
        "label": "結婚證書 / 結婚證明",
        "description": "正式結婚登記文件，含雙方姓名、結婚生效日、登記機關。可能為英文表格。",
        "fields": ["employee_name", "employee_english_name", "spouse_name", "marriage_date", "document_issue_date"],
    },
    "household_registration_marriage": {
        "label": "戶口名簿 / 戶籍謄本",
        "description": "戶政機關核發的戶口名簿或戶籍謄本，含戶長、成員、婚姻狀態。",
        "fields": ["employee_name", "spouse_name", "marriage_date"],
    },
    "relationship_proof": {
        "label": "關係證明",
        "description": "證明親屬或配偶關係的文件，如戶籍謄本、出生證明等。",
        "fields": ["employee_name", "spouse_name"],
    },
    "benefit_application_form": {
        "label": "補助申請表",
        "description": "員工自行填寫的補助申請書或表單。",
        "fields": ["employee_name", "document_issue_date"],
    },

    # ── funeral ──
    "obituary": {
        "label": "訃聞",
        "description": "傳統中文訃聞，常用直書，內容包含亡者姓名、儀式日期、儀式地點、家屬名單。",
        "fields": ["deceased_name", "funeral_date", "funeral_location", "employee_name", "relationship"],
    },
    "death_certificate": {
        "label": "死亡證明書 / 死亡診斷證明",
        "description": "醫院或戶政機關核發的死亡證明，含亡者姓名、死亡日期、死亡原因。",
        "fields": ["deceased_name", "death_date"],
    },
    "deregistered_household_registration": {
        "label": "除戶戶籍謄本",
        "description": "戶政機關核發的除戶謄本，記載亡者除戶資料與親屬關係。",
        "fields": ["deceased_name", "death_date", "employee_name", "relationship"],
    },
    "funeral_permit_or_cremation_proof": {
        "label": "埋葬 / 火化 / 殯葬證明",
        "description": "殯葬處或政府核發的火化、埋葬或殯葬許可證明。",
        "fields": ["deceased_name", "funeral_date", "funeral_location"],
    },
    "funeral_application_form": {
        "label": "申請表",
        "description": "員工自行填寫的奠儀申請書或表單。",
        "fields": ["employee_name", "deceased_name", "relationship"],
    },

    # ── contract ──
    "handwritten_contract": {
        "label": "手寫合約主文件",
        "description": "手寫的合約全文，可能為直書或橫書，內容含甲乙雙方、合約條款、金額。",
        "fields": [
            "contract_title", "party_a_name", "party_b_name", "contract_no",
            "effective_date", "start_date", "end_date",
            "service_scope", "amount", "payment_terms",
            "handwritten_text", "signature_or_stamp_present",
        ],
    },
    "contract_attachment": {
        "label": "合約附件",
        "description": "合約的附件，可能為印刷或手寫補充資料。",
        "fields": ["contract_title", "handwritten_text"],
    },
    "signature_stamp_page": {
        "label": "簽名 / 用印頁",
        "description": "合約最末頁，含雙方簽名與印章。",
        "fields": ["party_a_name", "party_b_name", "signature_or_stamp_present"],
    },
    "handwritten_note": {
        "label": "手寫補充條款 / 備註",
        "description": "合約附帶的手寫補充條款或備註。",
        "fields": ["handwritten_text", "low_confidence_segments"],
    },
    "unclear_scan": {
        "label": "模糊掃描件",
        "description": "影像品質過低，無法可靠辨識。",
        "fields": ["handwritten_text", "low_confidence_segments"],
    },

    # ── onboarding ──
    "onboarding_form": {
        "label": "人事基本資料表 / 報到表",
        "description": "新進人員填寫的基本資料表單，含姓名、出生日期、應徵職務等。",
        "fields": [
            "candidate_name", "candidate_english_name", "id_number",
            "birth_date", "position_name",
        ],
    },
    "id_card": {
        "label": "身分證 / 居留證 / 護照",
        "description": "身分證明文件，含姓名、身分證字號、出生日期。",
        "fields": ["candidate_name", "candidate_english_name", "id_number", "birth_date"],
    },
    "education_certificate": {
        "label": "最高學歷證明",
        "description": "學校核發的畢業證書或學歷證明。",
        "fields": ["candidate_name", "education_level", "school_name"],
    },
    "health_check_report": {
        "label": "體檢報告",
        "description": "醫院核發的體檢報告，含體檢日期與項目。",
        "fields": ["candidate_name", "health_check_date"],
    },
    "bank_account_copy": {
        "label": "存摺封面 / 薪轉帳戶",
        "description": "銀行存摺封面或薪轉帳戶影本。",
        "fields": ["candidate_name", "bank_name", "bank_account"],
    },
    "professional_license": {
        "label": "專業證照",
        "description": "專業執照、證書，含證照名稱、編號、效期。",
        "fields": ["candidate_name", "license_name"],
    },
    "insurance_transfer_proof": {
        "label": "勞健保轉出 / 退保證明",
        "description": "勞健保局核發的轉出或退保證明。",
        "fields": ["candidate_name", "id_number"],
    },
    "photo": {
        "label": "識別證照片",
        "description": "員工識別證大頭照。",
        "fields": ["candidate_name"],
    },
    "previous_employment_proof": {
        "label": "離職 / 服務證明",
        "description": "前公司核發的離職或在職服務證明。",
        "fields": ["candidate_name", "position_name"],
    },
}

# ─── Field definitions ──────────────────────────────────────────────────

FIELDS = {
    # marriage
    "employee_name":          {"label": "員工姓名",        "type": "string"},
    "employee_english_name":  {"label": "員工英文姓名",    "type": "string"},
    "spouse_name":            {"label": "配偶姓名",        "type": "string"},
    "marriage_date":          {"label": "結婚生效日 / 登記日", "type": "date"},
    "banquet_date":           {"label": "宴客日期",        "type": "date"},
    "document_issue_date":    {"label": "文件核發日",      "type": "date"},

    # funeral
    "deceased_name":          {"label": "亡者姓名",        "type": "string"},
    "relationship":           {"label": "亡者關係",        "type": "string"},
    "death_date":             {"label": "死亡日期",        "type": "date"},
    "funeral_date":           {"label": "儀式日期",        "type": "date"},
    "funeral_location":       {"label": "儀式地點",        "type": "string"},

    # contract
    "contract_title":         {"label": "文件標題",        "type": "string"},
    "party_a_name":           {"label": "甲方名稱",        "type": "string"},
    "party_b_name":           {"label": "乙方名稱",        "type": "string"},
    "contract_no":            {"label": "合約編號",        "type": "string"},
    "effective_date":         {"label": "生效日期",        "type": "date"},
    "start_date":             {"label": "履約起日",        "type": "date"},
    "end_date":               {"label": "履約迄日",        "type": "date"},
    "service_scope":          {"label": "服務 / 履約內容", "type": "string"},
    "amount":                 {"label": "金額",            "type": "string"},
    "payment_terms":          {"label": "付款條件",        "type": "string"},
    "handwritten_text":       {"label": "手寫全文",        "type": "string"},
    "low_confidence_segments":{"label": "低信心段落",      "type": "string"},
    "signature_or_stamp_present": {"label": "是否簽名 / 用印", "type": "boolean"},

    # onboarding
    "candidate_name":         {"label": "面試者姓名",      "type": "string"},
    "candidate_english_name": {"label": "英文姓名",        "type": "string"},
    "id_number":              {"label": "身分證字號",      "type": "string"},
    "birth_date":             {"label": "出生日期",        "type": "date"},
    "position_name":          {"label": "應徵職務",        "type": "string"},
    "education_level":        {"label": "最高學歷",        "type": "string"},
    "school_name":            {"label": "學校名稱",        "type": "string"},
    "health_check_date":      {"label": "體檢日期",        "type": "date"},
    "bank_name":              {"label": "銀行名稱",        "type": "string"},
    "bank_account":           {"label": "銀行帳號",        "type": "string"},
    "license_name":           {"label": "證照名稱",        "type": "string"},
}


# ─── Prompt builders ────────────────────────────────────────────────────

def classification_prompt(flow_key: str) -> str:
    """Build a prompt asking the VLM to classify the document into one of the flow's doctypes."""
    flow = FLOWS[flow_key]
    options = []
    for code in flow["doctypes"]:
        dt = DOCTYPES[code]
        options.append(f"- {code}: {dt['label']} — {dt['description']}")
    options_str = "\n".join(options)
    return (
        f"這是「{flow['label']}」流程中的一份文件。請判斷它屬於以下哪一種類型：\n\n"
        f"{options_str}\n\n"
        f"只回覆一個代碼，例如：wedding_invitation"
    )


def extraction_prompt(doctype_code: str) -> str:
    """Build a prompt to extract fields from a classified document."""
    dt = DOCTYPES[doctype_code]
    field_lines = []
    for key in dt["fields"]:
        f = FIELDS[key]
        hint = f""
        if f["type"] == "date":
            hint = "（請以 YYYY-MM-DD 格式輸出；若為民國年請換算為西元年）"
        elif f["type"] == "boolean":
            hint = "（請以 true 或 false 回答）"
        field_lines.append(f'  "{key}": ""  // {f["label"]}{hint}')
    fields_str = "{\n" + ",\n".join(field_lines) + "\n}"
    return (
        f"這是一份「{dt['label']}」。請辨識文件中的文字，提取以下欄位：\n\n"
        f"{fields_str}\n\n"
        f"找不到的欄位請填空字串。只回覆 JSON，不要任何解釋。"
    )


def normalize_value(value: str, field_key: str) -> str:
    """Normalize value per field type. Dates → YYYY-MM-DD, others passthrough."""
    if not value:
        return value
    f = FIELDS.get(field_key)
    if not f:
        return value
    if f["type"] == "date":
        return _normalize_date(value)
    return value


def _normalize_date(s: str) -> str:
    """Convert various Chinese/Western date formats to YYYY-MM-DD."""
    import re
    s = s.strip()
    # YYYY-MM-DD already
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    # 中華民國 X年 Y月 Z日 → ROC year + 1911 = Western year
    m = re.search(r"(?:中華民國|民國)?\s*(\d{2,3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日?", s)
    if m:
        year = int(m.group(1))
        if year < 200:
            year += 1911
        return f"{year}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    # YYYY/MM/DD
    m = re.match(r"^(\d{4})[/.](\d{1,2})[/.](\d{1,2})$", s)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    return s  # passthrough if unrecognised
