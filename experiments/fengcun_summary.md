# 封存 Benchmark — /v1/aiocr/analyze

_Per-flow: 1, Total elapsed: 28.6s_


## Classification accuracy

| Flow | Cases | Matched | Accuracy |
|---|---:|---:|---:|
| marriage | 1 | 1 | 100% |
| funeral | 1 | 1 | 100% |
| contract | 1 | 1 | 100% |
| onboarding | 1 | 0 | 0% |

## marriage

| Case | GT doctype | Predicted | Match | Type conf | Fields filled | Avg conf | Time |
|---|---|---|---|---:|---:|---:|---:|
| marriage_baseline_001 | 喜帖/結婚證明 | 喜帖 (`wedding_invitation`) | ✓ | 0.9 | 3/4 | 0.71 | 4.3s |

### Field-level detail


**marriage_baseline_001** → 喜帖

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 王小明 | 王小明 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 林小雅 | 林小雅 | 0.95 | ✓ |
| 宴客日期 (`banquet_date`) | 2026-01-18 | 2026-01-18 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | — |  | 0.0 | ⚠ |

## funeral

| Case | GT doctype | Predicted | Match | Type conf | Fields filled | Avg conf | Time |
|---|---|---|---|---:|---:|---:|---:|
| funeral_baseline_001 | 訃聞 | 訃聞 (`obituary`) | ✓ | 0.9 | 5/5 | 0.85 | 4.9s |

### Field-level detail


**funeral_baseline_001** → 訃聞

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 亡者姓名 (`deceased_name`) | 陳美玉 | 陳美玉 | 0.95 | ✓ |
| 儀式日期 (`funeral_date`) | 2026-02-08 | 2026-02-08 | 0.95 | ✓ |
| 儀式地點 (`funeral_location`) | 台中市北區安和會館（台中市北區太原路三段二四六號） | 台中市北區安和會館（台中市北區太原路三段二四六號） | 0.78 | ⚠ |
| 員工姓名 (`employee_name`) | 陳明德 | 陳明德 | 0.78 | ⚠ |
| 亡者關係 (`relationship`) | 子 | 子 | 0.78 | ⚠ |

## contract

| Case | GT doctype | Predicted | Match | Type conf | Fields filled | Avg conf | Time |
|---|---|---|---|---:|---:|---:|---:|
| contract_baseline_001 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 11/12 | 0.84 | 15.6s |

### Field-level detail


**contract_baseline_001** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 清潔服務合約 | 清潔服務合約 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 安和科技股份有限公司 | 安和科技股份有限公司 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 明新清潔服務行 | 明新清潔服務行 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-03-28 | 2026-03-28 | 0.95 | ✓ |
| 履約起日 (`start_date`) | 2026-04-01 | 2026-04-01 | 0.95 | ✓ |
| 履約迄日 (`end_date`) | 2027-03-31 | 2027-03-31 | 0.95 | ✓ |
| 服務 / 履約內容 (`service_scope`) | 每週三進行辦公區清潔與巡檢。 | 每週三進行辦公區清潔與巡檢。 | 0.95 | ✓ |
| 金額 (`amount`) | 每月新台幣 16,000 元整 | 每月新台幣 16,000 元整 | 0.78 | ⚠ |
| 付款條件 (`payment_terms`) | 每月月底前請款，30日內匯款完成。 | 每月月底前請款，30日內匯款完成。 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 清潔服務合約  一、合約名稱：清潔服務合約 二、立約人： 甲方：安和科技股份有限公司（虛構） 乙方：明新清潔服務行（虛構 | 清潔服務合約

一、合約名稱：清潔服務合約
二、立約人：
甲 | 0.78 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

## onboarding

| Case | GT doctype | Predicted | Match | Type conf | Fields filled | Avg conf | Time |
|---|---|---|---|---:|---:|---:|---:|
| onboarding_baseline_001 | 體檢資料 | 體檢報告 (`health_check_report`) | ✗ | 0.9 | 2/2 | 0.95 | 3.7s |

### Field-level detail


**onboarding_baseline_001** → 體檢報告

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 林怡君 | 林怡君 | 0.95 | ✓ |
| 體檢日期 (`health_check_date`) | 2026-03-20 | 2026-03-20 | 0.95 | ✓ |