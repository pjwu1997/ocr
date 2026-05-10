"""
SQLite database layer for OCR rules and results.

Tables:
  - rules: extraction rule definitions per document type
  - ocr_results: persisted OCR results with human review
"""

import csv
import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "ocr.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "test_rules.csv")

_conn: sqlite3.Connection | None = None


def get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA foreign_keys=ON")
    return _conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS rules (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            welfare_item    TEXT,
            category        TEXT NOT NULL,
            doc_type        TEXT NOT NULL,
            fields_json     TEXT NOT NULL DEFAULT '[]',
            notes           TEXT DEFAULT '',
            created_at      TEXT NOT NULL,
            updated_at      TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS ocr_results (
            id              TEXT PRIMARY KEY,
            filename        TEXT NOT NULL,
            rule_id         INTEGER,
            detected_type   TEXT,
            ocr_markdown    TEXT,
            fields_json     TEXT NOT NULL DEFAULT '[]',
            edit_reason     TEXT DEFAULT '',
            status          TEXT NOT NULL DEFAULT 'pending',
            created_at      TEXT NOT NULL,
            reviewed_at     TEXT,
            FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE SET NULL
        );
    """)
    conn.commit()

    # Seed rules from CSV if table is empty
    count = conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0]
    if count == 0:
        _seed_rules_from_csv(conn)


# ── Rules CRUD ──

def get_rules() -> list[dict]:
    rows = get_conn().execute(
        "SELECT * FROM rules ORDER BY CAST(welfare_item AS INTEGER), id"
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_rule(rule_id: int) -> dict | None:
    row = get_conn().execute("SELECT * FROM rules WHERE id = ?", (rule_id,)).fetchone()
    return _row_to_dict(row) if row else None


def create_rule(welfare_item: str, category: str, doc_type: str,
                fields: list[dict], notes: str = "") -> dict:
    now = _now()
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO rules (welfare_item, category, doc_type, fields_json, notes, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (welfare_item, category, doc_type, json.dumps(fields, ensure_ascii=False), notes, now, now),
    )
    conn.commit()
    return get_rule(cur.lastrowid)


def update_rule(rule_id: int, **kwargs) -> dict | None:
    allowed = {"welfare_item", "category", "doc_type", "fields_json", "notes"}
    sets = []
    vals = []
    for k, v in kwargs.items():
        if k not in allowed:
            continue
        if k == "fields_json" and isinstance(v, list):
            v = json.dumps(v, ensure_ascii=False)
        sets.append(f"{k} = ?")
        vals.append(v)
    if not sets:
        return get_rule(rule_id)
    sets.append("updated_at = ?")
    vals.append(_now())
    vals.append(rule_id)
    conn = get_conn()
    conn.execute(f"UPDATE rules SET {', '.join(sets)} WHERE id = ?", vals)
    conn.commit()
    return get_rule(rule_id)


def delete_rule(rule_id: int) -> bool:
    conn = get_conn()
    cur = conn.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
    conn.commit()
    return cur.rowcount > 0


# ── OCR Results CRUD ──

def create_ocr_result(filename: str, rule_id: int | None, detected_type: str,
                      ocr_markdown: str, fields: list[dict]) -> dict:
    result_id = str(uuid.uuid4())
    now = _now()
    conn = get_conn()
    conn.execute(
        "INSERT INTO ocr_results (id, filename, rule_id, detected_type, ocr_markdown, fields_json, status, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)",
        (result_id, filename, rule_id, detected_type, ocr_markdown,
         json.dumps(fields, ensure_ascii=False), now),
    )
    conn.commit()
    return get_ocr_result(result_id)


def update_ocr_result(result_id: str, fields: list[dict], edit_reason: str = "") -> dict | None:
    now = _now()
    conn = get_conn()
    conn.execute(
        "UPDATE ocr_results SET fields_json = ?, edit_reason = ?, status = 'reviewed', reviewed_at = ? WHERE id = ?",
        (json.dumps(fields, ensure_ascii=False), edit_reason, now, result_id),
    )
    conn.commit()
    return get_ocr_result(result_id)


def get_ocr_result(result_id: str) -> dict | None:
    row = get_conn().execute("SELECT * FROM ocr_results WHERE id = ?", (result_id,)).fetchone()
    return _row_to_dict(row) if row else None


def get_ocr_results(limit: int = 100) -> list[dict]:
    rows = get_conn().execute(
        "SELECT * FROM ocr_results ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


# ── Helpers ──

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for key in ("fields_json",):
        if key in d and isinstance(d[key], str):
            try:
                d[key] = json.loads(d[key])
            except (json.JSONDecodeError, TypeError):
                pass
    return d


# ── CSV Seeding ──

# Pre-built regex patterns for known document types
_REGEX_PRESETS: dict[str, list[dict]] = {
    # NOTE: Regex patterns run against HTML-stripped plain text from OCR markdown.
    # After strip_html(), HTML table rows become a SINGLE LINE with spaces between cells.
    # Patterns must account for this: use \s+ instead of \n between table cell values,
    # and use (?:\s|$) or (?=\s) instead of (?:\n|$) for boundaries within table rows.

    # ── 12.公文.pdf ──
    # Stripped sample (line-based, no tables):
    #   # 臺中市政府經濟發展局 函
    #   發文日期：中華民國114年12月30日
    #   發文字號：中市經登字第1140089030號
    #   主旨：依工廠管理輔導法...請查照。
    #   ## 說明：
    "公文": [
        {"name": "檔案名稱", "type": "filename"},
        {"name": "發文者", "type": "text", "regex_patterns": [
            r"#\s*(.+?)\s*函",
            r"(?:發文者|發文機關|機關)\s*[：:]\s*(.+?)(?:\n|$)",
            r"([\w]+(?:政府|局|處|署|部|院|所|中心|委員會|公所))\s*(?:函|書|令|公告)?",
        ]},
        {"name": "發文日期", "type": "date", "regex_patterns": [
            r"發文日期[：:]\s*中華民國\s*(.+?)(?:\n|$)",
            r"發文日期[：:]\s*(.+?)(?:\n|$)",
            r"中華民國\s*(\d{2,3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日",
        ]},
        {"name": "發文字號", "type": "text", "regex_patterns": [
            r"發文字號[：:]\s*(.+?)(?:\n|$)",
            r"([\w]*字第[\w-]+號)",
        ]},
        {"name": "主旨", "type": "text", "regex_patterns": [
            r"主旨[：:]\s*(.+?)(?=\n|$)",
        ]},
        {"name": "說明", "type": "text", "regex_patterns": [
            r"說明[：:]\s*\n(.+?)(?=\n\s*(?:正本|副本|辦法|擬辦)|$)",
        ]},
        {"name": "是否包含「罰款」關鍵字", "type": "boolean_keyword", "keyword": "罰款"},
        {"name": "兩字關鍵字", "type": "two_char_keywords"},
    ],

    # ── 1.接駁車搭乘登記表.pdf ──
    # Stripped: single line with all table cells joined by spaces:
    #   駕駛填寫 紀錄日期： 2026-01-26 星期一 路線名稱： 二林→臺中（第三班）-小巴 ...
    #   人數統計 5 0 終點 ... 搭車日 2026-1-26
    "接駁車搭乘登記表": [
        {"name": "路線名稱", "type": "text", "regex_patterns": [
            r"路線名稱[：:]\s*(.+?)(?=\s+(?:駕駛|車輛|聯絡|廠別|$))",
            r"路線名稱[：:]\s*(\S+(?:\s*→\s*\S+)?(?:（[^）]*）)?(?:-\S+)?)",
        ]},
        {"name": "搭車日期", "type": "date", "regex_patterns": [
            r"紀錄日期[：:]\s*(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})",
            r"搭車日\s+(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})",
        ]},
        {"name": "駕駛姓名", "type": "text", "regex_patterns": [
            r"駕駛姓名[：:]\s*(\S+)",
        ]},
        {"name": "車輛號碼", "type": "text", "regex_patterns": [
            r"車輛號碼[：:]\s*(\S+)",
        ]},
        {"name": "登記人數", "type": "passenger_count"},
        {"name": "實際搭乘名單", "type": "passenger_rode_list"},
        {"name": "沒搭乘名單", "type": "passenger_noshow_list"},
    ],

    # ── 2.用餐費用調整表.pdf ──
    # Stripped: title line "# 棟餐廳用餐費用調整表Canteen Dining Expenses Adjustment Table"
    # Table rows become single long lines with cell data separated by spaces.
    # e.g. "1 2/ ■午餐Lunch... ■+1 □-1 26041 貨有鄧華翔"
    "用餐費用調整表": [
        {"name": "餐廳", "type": "text", "regex_patterns": [
            r"((?:EL|DF|CS)\s*廠\s*\S+\s*棟\s*餐廳)",
            r"#\s*(\S*棟餐廳)",
        ]},
        {"name": "調整明細", "type": "meal_adjustment_list"},
    ],

    # ── 3.繳費證明+戶口名簿.pdf / 5.繳費收據.jpg ──
    # File 3 stripped:
    #   # 國立臺灣大學 111學年度第一學期學雜費繳費證明
    #   學號 Student ID Number B08A01118 系所 Department 法律系法學組 姓名 Name 蔡明珊 年級 Year 4
    #   ...總計 Total Amount (NTD) 新臺幣 參萬陸仟零柒拾玖元整 36,079 2022/10/2 印製
    # File 5 stripped:
    #   華語文教學中心 學號 C11110500 姓名 波琳 項目 09月-11月 學雜費 現金收費
    #   金額 新臺幣：壹萬肆仟伍佰零拾NT$：14,500
    "繳費收據": [
        {"name": "學生姓名", "type": "text", "regex_patterns": [
            r"姓\s*名\s+(?:Name\s+)?(\S{2,10})(?=\s+(?:年級|項目|學號|班級|科系|系所|Year))",
            r"姓\s*名\s+(?:Name\s+)?(\S{2,10})",
        ]},
        {"name": "學期", "type": "text", "regex_patterns": [
            r"(\d+\s*學年度?\s*第?\s*[一二12]\s*學期)",
            r"(From\s+\d{4}/\d{2}\s+to\s+\d{4}/\d{2})",
            r"(\d{2}月-\d{2}月)",
        ]},
        {"name": "繳費總金額", "type": "text", "regex_patterns": [
            r"NT\s*\$\s*[：:]?\s*([\d,]+)",
            r"(?:總計|Total\s*Amount).*?(\d[\d,]+)",
            r"金\s*額\s+.*?(\d[\d,]+)",
        ]},
    ],

    # ── 4.成績單.jpg ──
    # Stripped:
    #   # 臺中市潭子區潭陽國小110學年第2學期
    #   # 日常行為及學習成績評量通知書
    #   座號：2 姓名：王宥皓
    "成績單": [
        {"name": "學生姓名", "type": "text", "regex_patterns": [
            r"姓名[：:]\s*(\S+)",
            r"姓\s*名\s*[：:]\s*(\S+)",
            r"姓名\s+(\S+)",
        ]},
        {"name": "學期", "type": "text", "regex_patterns": [
            r"(\d+\s*學年[度]?\s*第?\s*[一二12]\s*學期)",
        ]},
        {"name": "各科成績", "type": "grade_table"},
    ],

    # ── 6.清潔打卡資料.pdf ──
    # Stripped: table becomes single line:
    #   AI TE 微電腦音樂打卡鐘 No. 姓名 劉 聿 見 單位
    #   ## 攷勤表
    #   中華民國115年1月份
    #   ... 1 2 2006:12 2016:02 3 4 2006:09 2016:02 ...
    "清潔打卡資料": [
        {"name": "姓名", "type": "text", "regex_patterns": [
            r"姓名\s+(.+?)(?=\s+單位)",
            r"姓\s*名\s+(\S+)",
        ]},
        {"name": "年月", "type": "text", "regex_patterns": [
            r"中華民國\s*(\d{2,3}\s*年\s*\d{1,2}\s*月)",
            r"(\d{2,4}\s*年\s*\d{1,2}\s*月)",
        ]},
        {"name": "每日上下班時間", "type": "multi_time_clock"},
    ],

    # ── 7.喜帖(中文).jpg ──
    # Stripped:
    #   謹唐於中華民國一一五年國曆元月十二日（星期一）
    #   爲盈志與蕭志賢先生今壞紅葉小姐舉行結婚
    "喜帖": [
        {"name": "員工姓名", "type": "text", "regex_patterns": [
            # Chinese wedding invitation
            r"與\s*(\S{2,5})\s*先生",
            r"(\S{2,5})\s*先生.*舉行",
            # English marriage certificate (HUSBAND column)
            r"HUSBAND\s+(?:WIFE\s+)?\(First\)\s+(\S+)",
        ]},
        {"name": "配偶姓名", "type": "text", "regex_patterns": [
            # Chinese wedding invitation
            r"今壞?\s*(\S{2,5})\s*小姐",
            r"(\S{2,5})\s*小姐.*(?:舉行|結婚)",
            # English marriage certificate (WIFE column)
            r"\(First\)\s+\S+\s+\(First\)\s+(\S+)",
        ]},
        {"name": "宴客日期", "type": "date", "regex_patterns": [
            # Chinese wedding invitation
            r"中華民國\s*(一{0,3}[零一二三四五六七八九十百]+年\s*(?:國曆|農曆)?\s*[零一二三四五六七八九十元]+月\s*[零一二三四五六七八九十初廿卅]+日)",
            r"(?:國曆|農曆)\s*([\S]+月[\S]+日)",
            r"民國\s*(\S+年\S+月\S+日)",
            # English marriage certificate — full date with month name
            r"Date of Marriage[：:]?\s*(\d+)\s*\(Day\)\s*([A-Z]+)\s*\(Month\)\s*(\d{4})\s*\(Year\)",
            r"Date of Marriage[：:]?\s*(\d+)\s*\(Day\)\s*([A-Z]+)\s*.*?(\d{4})",
            r"Date of Marriage[：:]?\s*(\d+\s+[A-Z]+\s+\d{4})",
            # Fallback: RECEIVED BY date stamp (e.g. "Date JAN 1 5 2024" = JAN 15 2024)
            r"Date\s+([A-Z]{3}\s+[\d\s]+\d{4})",
            # Day-only fallback
            r"16\.\s*Date of Marriage[：:]?\s*(\d+)",
        ]},
        {"name": "新郎父母", "type": "text", "regex_patterns": [
            r"([\u4e00-\u9fff]{2,4})\s*鞠躬",
        ]},
        {"name": "餐廳", "type": "text", "regex_patterns": [
            # OCR garbles 席設 to various forms: 房設/黃唐設/美店設 etc.
            # Match: any_chars + 設 + ： + venue name ending in 館/廳/店
            r"\S*設\s*[：:]\s*(.+?(?:館|廳|店|莊|園|堂))",
            r"(?:席設|筵席|地點)\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
        {"name": "地址", "type": "text", "regex_patterns": [
            r"地址\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
        {"name": "電話", "type": "text", "regex_patterns": [
            r"(?:\S?)電話\s*[：:]\s*([\d-]+)",
        ]},
        {"name": "時間", "type": "text", "regex_patterns": [
            r"(?:\S?)時間\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
    ],

    # ── 7.結婚證明(英文).pdf ──
    # Stripped: single line table:
    #   ...1. Name of Contracting Parties HUSBAND WIFE (First) JQJO (First) JENNY
    #   (Middle) AGUILAR (Middle) ORTEGA (Last) FAJARDO (Last) CABRERA...
    #   16. Date of Marriage: 14 (Day) (Month) (Year)...
    #   21. RECEIVED BY ... Date JAN 1 5 2024
    "結婚證書": [
        {"name": "員工姓名", "type": "text", "regex_patterns": [
            r"HUSBAND\s+WIFE\s+\(First\)\s+(\S+)",
            r"HUSBAND.*?\(First\)\s+(\S+)",
            r"(?:新郎|丈夫)\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
        {"name": "配偶姓名", "type": "text", "regex_patterns": [
            r"HUSBAND\s+WIFE\s+\(First\)\s+\S+\s+\(First\)\s+(\S+)",
            r"WIFE.*?\(First\)\s+(\S+)",
            r"(?:新娘|妻子)\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
        {"name": "結婚生效日期", "type": "date", "regex_patterns": [
            # Full date: "14 (Day) JANUARY (Month) 2024 (Year)"
            r"Date of Marriage[：:]?\s*(\d+)\s*\(Day\)\s*([A-Z]+)\s*\(Month\)\s*(\d{4})\s*\(Year\)",
            # Day + month + year spread across fields (OCR may drop labels)
            r"Date of Marriage[：:]?\s*(\d+)\s*\(Day\)\s*([A-Z]+)\s*.*?(\d{4})",
            # Fallback: extract from RECEIVED BY date stamp (e.g. "JAN 1 5 2024")
            r"Date\s+([A-Z]{3}\s+[\d\s]+\d{4})",
            # Day-only fallback
            r"Date of Marriage[：:]?\s*(\d+)\s+\(Day\)",
            r"(?:Date of Marriage|DATE OF MARRIAGE)\s*[：:]?\s*(\d+\s*\w+\s*\d{4})",
            r"Registry No\.\s*(\d{4}-\d+)",
            r"(?:結婚日期|結婚生效日)\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
        {"name": "登記編號", "type": "text", "regex_patterns": [
            r"Registry No\.\s*(\S+)",
        ]},
    ],

    # ── 8.訃聞.pdf ──
    # Stripped (multi-line, no tables):
    #   擇訂於民國一一五年元月二十四日（農曆一一四年十二月初六
    #   星期六假該處【永仁廳】舉行告別式奠禮
    #   隨即發引臺中市東海火化場火化
    #   孝
    #   女
    #   詩淇
    #   杖期夫潘慶發
    "訃聞": [
        {"name": "亡者姓名", "type": "obituary_deceased"},
        {"name": "享年", "type": "text", "regex_patterns": [
            r"享\S*(\d+)\S*歲",
            r"享[壽年]\s*(.+?歲)",
            r"([\u4e00-\u9fff]+(?:十|百)\S*歲)",
        ]},
        {"name": "配偶", "type": "text", "regex_patterns": [
            r"杖期\s*夫\s*(\S+)",
            r"杖期\s*妻\s*(\S+)",
            r"(?:未亡人|遺孀)\s*(\S{2,5})",
        ]},
        {"name": "孝子女", "type": "obituary_children"},
        {"name": "儀式日期", "type": "date", "regex_patterns": [
            # Chinese obituary
            r"(?:訂於|擇訂)(?:於)?民國\s*([\S]+年[\S]+月[\S]+日)",
            r"民國\s*(一{0,3}[\S]+年[\S]+月[\S]+日)",
            # Vietnamese death certificate
            r"ngày\s+(\d+\s+tháng\s+\d+\s+năm\s+\d+)",
            r"(\d{4}[/.-]\d{1,2}[/.-]\d{1,2})",
        ]},
        {"name": "公祭時間", "type": "text", "regex_patterns": [
            # "公 奠：上午八時四十分" — match 公奠 specifically
            r"公\s*奠\s*[：:]\s*((?:上午|下午)\S+時\S*分?)",
            r"公\s*祭\s*[：:]\s*((?:上午|下午)\S+時\S*分?)",
        ]},
        {"name": "儀式地點", "type": "text", "regex_patterns": [
            r"(?:星期.{1,2})假(.+?)(?:舉行|告別)",
            r"([\S]*火化場[\S]*)",
            r"假\s*(.{2,30}?)(?:舉行|火化|告別)",
            # Vietnamese death certificate
            r"(?:TRÍCH LỤC|GIẤY CHỨNG TỬ).*?(?:NGHĨA|NAM)\s*(?:.*?\n){0,5}.*?((?:Độc lập|CHỦ TÍCH|PHÓ CHỦ TÍCH).+?)(?:\n|$)",
            # English death certificate
            r"(?:Place of Death|PLACE OF DEATH)\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
        # Vietnamese death certificate additional fields (ignored for Chinese 訃聞)
        {"name": "文件編號", "type": "text", "regex_patterns": [
            r"Số[：:]?\s*(\d+/\d+)",
            r"(?:No|Number|編號)[.：:]?\s*(\S+)",
        ]},
        {"name": "簽署人", "type": "text", "regex_patterns": [
            # Match the last line (name) after PHÓ CHỦ TÍCH or CHỦ TÍCH
            r"PHÓ CHỦ TÍCH\n(.+?)(?:\n|$)",
            r"^CHỦ TÍCH\n(.+?)(?:\n|$)",
            r"(?:Signed by|Certified by)\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
    ],

    # ── 8.死亡證明(英文).pdf ──
    # Stripped (Vietnamese death certificate):
    #   # TRÍCH LỤC KHAI TỬ (BẢN SAO)
    #   Họ, chữ đệm, tên: NGUYỄN THANH PHƯỚNG
    #   Số: 122/2025 ngày 22 tháng 12 năm 2025
    "死亡證明": [
        {"name": "姓名", "type": "text", "regex_patterns": [
            r"(?:Họ|Ho)[,\s]*(?:chữ đệm|chu dem)?[,\s]*(?:tên|ten)\s*[：:]\s*(.+?)(?:\n|$)",
            r"(?:Name|NAME)\s*[：:]\s*(.+?)(?:\n|$)",
            r"姓\s*名\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
        {"name": "死亡日期", "type": "date", "regex_patterns": [
            r"ngày\s+(\d+\s+tháng\s+\d+\s+năm\s+\d+)",
            r"Số[：:]\s*\d+/\d+\s+ngày\s+(\d+\s+tháng\s+\d+\s+năm\s+\d+)",
            r"(?:Date of Death|DATE OF DEATH)\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
        {"name": "文件編號", "type": "text", "regex_patterns": [
            r"Số[：:]?\s*(\d+/\d+)",
            r"(?:No|Number|編號)[.：:]?\s*(\S+)",
        ]},
        {"name": "簽署人", "type": "text", "regex_patterns": [
            # Vietnamese: name after PHÓ CHỦ TÍCH or CHỦ TÍCH
            r"(?:PHÓ CHỦ TÍCH|CHỦ TÍCH)\n(.+?)(?:\n|$)",
            r"(?:PHÓ CHỦ TÍCH|CHỦ TÍCH)\s+(.+?)(?:\n|$)",
            # English
            r"(?:Signed by|Certified by)\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
    ],

    # ── 9.出生證明(英文).pdf ──
    # Stripped: table becomes single line:
    #   ...DETAILS OF CHILD'S BIRTH 1. CHILD'S LAST NAME 5. DATE OF BIRTH
    #   (Ex. 01 January 2000) 2. CHILD'S FIRST NAME 6. SEX...
    #   ...FATHER MOTHER (MAIDEN INFORMATION) 9. LAST NAME SALES ELUZON
    #   10. FIRST NAME JHORDAN RACHELLE 11. MIDDLE NAME SEMINIANO DE LA PENA
    "出生證明": [
        {"name": "姓名", "type": "text", "regex_patterns": [
            r"9\.\s*LAST NAME\s+(\S+)\s+\S+\s+10\.\s*FIRST NAME\s+(\S+)",
            r"CHILD.S LAST NAME\s+(\S+)",
            r"CHILD.S FIRST NAME\s+(\S+)",
        ]},
        {"name": "出生日期", "type": "date", "regex_patterns": [
            r"5\.\s*DATE OF BIRTH\s+(?!.*Ex\.)(\d+\s+\w+\s+\d{4})",
            r"DATE OF BIRTH\s+(?!.*Ex\.)(\d+\s+\w+\s+\d{4})",
            r"出生日期\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
        {"name": "父親姓名", "type": "text", "regex_patterns": [
            r"FATHER.*?9\.\s*LAST NAME\s+(\S+)",
            r"9\.\s*LAST NAME\s+(\S+)",
            r"10\.\s*FIRST NAME\s+(\S+)",
            r"父\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
        {"name": "母親姓名", "type": "text", "regex_patterns": [
            r"MOTHER\s+\(MAIDEN INFORMATION\)\s+9\.\s*LAST NAME\s+\S+\s+(\S+)",
            r"10\.\s*FIRST NAME\s+\S+\s+(\S+)",
            r"母\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
    ],

    # ── 10.活動發票.png ──
    # Stripped (mostly line-based):
    #   # 電子發票證明聯
    #   112年03-04月
    #   2023-04-21 12:45:41
    #   買方 05785249
    #   總計$1463
    "發票": [
        {"name": "發票號碼", "type": "text", "regex_patterns": [
            r"(?:\d{2,3}年\d{2}-\d{2}月)\s*#?\s*([A-Z]{2}-?\d{8})",
            r"#\s*([A-Z]{2}-\d{8})",
            r"([A-Z]{2}-\d{8})",
        ]},
        {"name": "消費日期", "type": "date", "regex_patterns": [
            r"(\d{4}-\d{2}-\d{2})",
            r"(\d{2,3}年\d{2}-\d{2}月)",
        ]},
        {"name": "買方統編", "type": "text", "regex_patterns": [
            r"買方\s*(\d{8})",
            r"(?:統一編號|統編)\s*[：:]?\s*(\d{8})",
        ]},
        {"name": "消費金額", "type": "text", "regex_patterns": [
            r"總計\s*\$?\s*([\d,]+)",
            r"(?:Total|合計)\s*\$?\s*([\d,]+)",
        ]},
    ],

    # ── 11.診斷證明.jpg ──
    # Stripped: table becomes single line:
    #   姓名 身分證字號 性別 男 出生日期 民國47年09月17日 科別 血液科 病歷號碼 病名
    #   呼吸器依賴狀態，無期別（ICD-10: Z99·11） 醫療名 茲證明該員係罹患重大傷病。
    #   以上病人經本院醫師診斷屬實特予證明 院長 陳鹹明 診治醫師：52728 號
    #   開立證明日期：民國114年04月17日
    "診斷證明": [
        {"name": "員工姓名", "type": "text", "regex_patterns": [
            r"姓\s*名\s+((?!身分證|性別|科別|病名)\S+?)(?=\s+(?:身分證|性別))",
            r"姓\s*名\s+((?!身分證|性別|科別|病名)\S+)",
        ]},
        {"name": "應診日期", "type": "date", "regex_patterns": [
            r"開立證明日期[：:]\s*(.+?)(?=\s+印製|\n|$)",
            r"(?:就診日期|應診日期)\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
        {"name": "科別", "type": "text", "regex_patterns": [
            r"科\s*別\s+(.+?)(?=\s+(?:病歷號碼|病歷|病名))",
            r"科\s*別\s+(\S+)",
        ]},
        {"name": "病名", "type": "text", "regex_patterns": [
            r"病\s*名\s+(.+?)(?=\s+(?:醫[囑療]|茲證明))",
            r"病\s*名\s+(.+?)(?=\s+醫療名)",
        ]},
        {"name": "醫囑", "type": "text", "regex_patterns": [
            r"茲證明(.+?)(?=\s+以上)",
            r"(?:醫\s*囑)\s+(.+?)(?=\s+(?:以上|院長)|\n)",
        ]},
    ],

    # ── 13.手寫信件(含簡體字).pdf ──
    # Stripped:
    #   10:
    #   ## Mailpro
    #   ## 【信函】
    #   普通掛號函件
    #   新莊思源路郵局
    "郵件信封": [
        {"name": "掛號類型", "type": "text", "regex_patterns": [
            r"(普通掛號函件|掛號函件|限時掛號|普通信件)",
            r"(掛號\S*)",
        ]},
        {"name": "寄件者", "type": "text", "regex_patterns": [
            r"(\S+郵局)",
            r"(?:寄件人?|FROM)\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
        {"name": "收件者姓名", "type": "envelope_address_crop", "regex_patterns": [
            # Patterns to apply against cropped address area OCR text
            r"([\u4e00-\u9fff]{2,5})\s*(?:先生|女士|小姐|收)",
            r"(?:Name|TO|收件人?)\s*[：:]?\s*(.+?)(?:\n|$)",
        ]},
        {"name": "收件者地址", "type": "envelope_address_crop", "regex_patterns": [
            r"((?:臺|台)[\u4e00-\u9fff]+(?:路|街|巷|弄|號)[\S]*)",
            r"(\d+號\S*)",
        ]},
        {"name": "收件者部門", "type": "envelope_address_crop", "regex_patterns": [
            r"(?:矽品|砂品|矽|碩品)\s*(\S+部)",
            r"(\S+(?:財務部|人資部|總務部|業務部|管理部|工程部))",
        ]},
    ],

    # ── 15.矽品特約合約書.pdf ──
    # Stripped (line-based, no tables):
    #   # SPIL Highly Confidential 砲品精密 互惠契約商店合約書機密 Siliconware
    #   乙方：矽品精密工業股份有限公司職工福利委員會
    #   甲方：
    #   電話：FAX.
    #   ✓（九）本合約期間自西元 年 月 日起至西元 年 月 日止
    # ── 15.矽品特約合約書.pdf ──
    # Stripped (line-based, contract template with mostly blank甲方 fields):
    #   甲方：
    #   地址：
    #   甲方應取得合法...
    #   乙方：矽品精密工業股份有限公司職工福利委員會
    "特約商合約": [
        {"name": "廠商名稱", "type": "text", "regex_patterns": [
            # 甲方： followed by actual company name (not blank, not 地址/統一編號)
            r"甲方[：:]\s*([^\s地統電負簽][^\n]+?)(?:\n|$)",
            r"甲\s*方\s*[：:]\s*([^\s地統電負簽][^\n]+?)(?:\n|$)",
        ]},
        {"name": "優惠方案", "type": "text", "regex_patterns": [
            # Only capture if there's actual content between 優惠如下 and the clauses
            # The line "優惠如下：" is immediately followed by （一）clause = blank
            r"優惠如下[：:]?\s*\n([^（\(].+?)(?=\n\s*(?:（|[\(]))",
        ]},
        {"name": "合約到期日", "type": "date", "regex_patterns": [
            # Only match if there are actual digits (not blank template fields)
            r"合約期間自.*?至\s*(?:西元\s*)?(\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)",
            r"(?:合約期間|有效期|到期).*?至\s*(\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)",
        ]},
        {"name": "廠商電話", "type": "text", "regex_patterns": [
            r"電話[：:]\s*([\d()#-]+)",
            r"電話[：:]([\s\S]*?)(?:FAX|傳真|\n)",
        ]},
        {"name": "乙方名稱", "type": "text", "regex_patterns": [
            r"乙方[：:]\s*(.+?)(?:\n|$)",
        ]},
        {"name": "乙方地址", "type": "text", "regex_patterns": [
            # Match actual address content (not blank lines or 統一編號)
            r"地址[：:]\s*((?:臺|台)[\u4e00-\u9fff]+(?:路|街|巷|弄|號)\S*)",
            r"((?:臺|台)中市\S+區\S+路\S+號)",
        ]},
        {"name": "乙方統一編號", "type": "text", "regex_patterns": [
            r"統一編號[：:]\s*(\d{8})",
        ]},
    ],

    # ── 15.廠商特約優惠內容.pdf ──
    # Stripped (line-based):
    #   公司名稱：矽品精密工業股份有限公司職工福利委員會
    #   電話：04-25215188#1113
    #   ...有效期自即日起至 2026 年 12 月 30 日止。
    "廠商特約優惠內容": [
        {"name": "廠商名稱", "type": "text", "regex_patterns": [
            r"(?:公司名稱|廠商)\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
        {"name": "優惠方案", "type": "text", "regex_patterns": [
            r"((?:SK|ST|DK|Room|標準|雅緻|經典|豪華|精緻|套房|單人|雙人|四人)[\s\S]*?(?:\d{1,2}\s*坪|\d[\d,]+)[\s\S]*?(?:\d[\d,]+))",
            r"(?:Room\s+Category|房型)[\s\S]*?((?:SK|ST|DK|Room|標準|雅緻|經典|豪華)[\s\S]*?\d[\d,]+)",
            r"(?:優惠方案|折扣|discount|Preferred)[\s\S]*?(\S[\s\S]*?)(?:\n\s*(?:Terms|條款|##)|$)",
        ]},
        {"name": "合約到期日", "type": "date", "regex_patterns": [
            r"(?:有效期|到期|until).*?至\s*(\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)",
            r"until\s+(\S+\s+\d+,?\s+\d{4})",
            r"至\s*(\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)",
        ]},
        {"name": "廠商電話", "type": "text", "regex_patterns": [
            r"電話[：:]\s*([\d()#+-]+)",
            r"(?:Tel|TEL|Telephone)[^：:]*[：:]\s*([\d\s#+-]+?)(?:\n|$)",
        ]},
    ],

    # ── 16.餐廳廚房安全衛生巡檢表.pdf ──
    # Stripped:
    #   # 餐廳廚房安全衛生巡檢表
    #   日期：2025年11月6日
    "巡檢表": [
        {"name": "文件標題", "type": "text", "regex_patterns": [
            r"(?:^|\n)\s*#+\s+(.+?(?:巡檢表|檢查表|紀錄表|計畫書|體檢|健檢)\S*)",
            r"(?:^|\n)\s*(.+?(?:巡檢表|檢查表|紀錄表|計畫書|體檢|健檢)\S*)",
        ]},
        {"name": "檢查日期", "type": "date", "regex_patterns": [
            r"日期[：:]\s*(\d+年\d+月\d+日)",
            r"日\s*期\s*[：:]?\s*(\d+\s*年\s*\d+\s*月\s*\d+\s*日)",
            r"施工日期\s+(\d+\s*年\s*\d+\s*月\s*\d+\s*日)",
        ]},
    ],

    # ── 16.體檢資料.pdf ──
    # Stripped: table becomes single line:
    #   ## 食品從業人員/供膳作業健康檢查紀錄表
    #   姓 名 性 別 出生日期 身 分 證 字 號 病 歷 號 碼 檢杏日期
    "體檢表": [
        {"name": "文件標題", "type": "text", "regex_patterns": [
            r"#+\s+(.+?(?:健康檢查|體檢|紀錄表|健檢)\S*)",
            r"^(.+(?:檢查|體檢|紀錄表|健檢))",
        ]},
        {"name": "姓名", "type": "text", "regex_patterns": [
            r"姓\s*名\s+(.+?)(?=\s+(?:性\s*別|出生|身\s*分))",
            r"姓\s*名\s+(\S+)",
        ]},
        {"name": "檢查日期", "type": "date", "regex_patterns": [
            # OCR may read 查 as 杏; date may be in same line after field label
            r"檢[杏查]\s*日\s*期\s+(\S+)",
            r"檢[杏查]日期\s*[：:]?\s*(.+?)(?:\n|$)",
        ]},
    ],

    # ── 16.病媒防治施作計畫書.pdf ──
    # Stripped: title on first line, then line-based + table single line:
    #   病媒防治施作計畫書
    #   病媒防治業名稱：恩博格有限公司
    #   客戶名稱：矽品精密工業股份有限公司 ... 施工日期 14 年 12 月 22 日 14 時 00 分
    "病媒防治施作計畫書": [
        {"name": "文件標題", "type": "text", "regex_patterns": [
            r"^(病媒防治施作計畫書)",
            r"^(.+(?:計畫書|施作))",
        ]},
        {"name": "施工日期", "type": "date", "regex_patterns": [
            r"施工日期\s+(\d+\s*年\s*\d+\s*月\s*\d+\s*日)",
            r"施工日期\s*[：:]?\s*(\d+\s*年\s*\d+\s*月?\s*\d*\s*日?)",
        ]},
        {"name": "客戶名稱", "type": "text", "regex_patterns": [
            r"客戶名稱[：:]\s*(.+?)(?=\s+(?:病媒|地址|負責人))",
            r"客\s*戶?\s*名稱\s*[：:]\s*(.+?)(?:\n|$)",
        ]},
    ],
}

# Mapping from CSV category to doc_type keys in _REGEX_PRESETS
_CSV_DOC_TYPE_MAP = {
    "接駁車": "接駁車搭乘登記表",
    "用餐調整表": "用餐費用調整表",
    "員工子女教(托)育補助金": "繳費收據",
    "教育獎學金": "成績單",
    "員工進修補助金": "繳費收據",
    "清潔打卡資料": "清潔打卡資料",
    "結婚慶賀金": "喜帖",
    "喪葬奠儀": "訃聞",
    "生育慶賀金": "出生證明",
    "活動請款": "發票",
    "急難救助金": "診斷證明",
    "公文分發": "公文",
    "郵件分發": "郵件信封",
    "廠商合約": "特約商合約",
    "矽品特約合約書": "廠商特約優惠內容",
    "例行表單寄給特定單位窗口": "巡檢表",
}


def _seed_rules_from_csv(conn: sqlite3.Connection):
    """Parse test_rules.csv and seed the rules table."""
    if not os.path.exists(CSV_PATH):
        return

    # Parse CSV — handle merged-row format
    raw_rules = []
    current = None

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # skip header

        for row in reader:
            if not row:
                continue

            # Pad row
            while len(row) < 5:
                row.append("")

            welfare_num = row[0].strip()
            category = row[1].strip()
            doc_type_csv = row[2].strip()
            note = row[3].strip()

            if welfare_num:
                # New rule entry
                if current:
                    raw_rules.append(current)
                current = {
                    "welfare_item": welfare_num,
                    "category": category,
                    "doc_type": doc_type_csv,
                    "notes": [note] if note else [],
                }
            else:
                # Continuation row — append note
                if current and note:
                    current["notes"].append(note)

        if current:
            raw_rules.append(current)

    # Insert into DB
    now = _now()
    for rule in raw_rules:
        cat = rule["category"]
        doc_key = _CSV_DOC_TYPE_MAP.get(cat, cat)
        fields = _REGEX_PRESETS.get(doc_key, [])

        # If no preset, create simple fields from notes
        if not fields and rule["notes"]:
            fields = _parse_fields_from_notes(rule["notes"])

        conn.execute(
            "INSERT INTO rules (welfare_item, category, doc_type, fields_json, notes, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                rule["welfare_item"],
                cat,
                rule["doc_type"],
                json.dumps(fields, ensure_ascii=False),
                "\n".join(rule["notes"]),
                now, now,
            ),
        )
    conn.commit()


def _parse_fields_from_notes(notes: list[str]) -> list[dict]:
    """Extract field names from 備註 text lines."""
    fields = []
    for note in notes:
        # Remove leading number + dot (e.g., "1.", "2.")
        cleaned = re.sub(r"^\d+\.\s*", "", note.strip())
        if not cleaned:
            continue
        # Take the first meaningful segment before parenthetical
        name = re.split(r"[（(]", cleaned)[0].strip()
        if name and len(name) < 50:
            fields.append({"name": name, "type": "text"})
    return fields
