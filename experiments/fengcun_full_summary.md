# 封存 Benchmark — /v1/aiocr/analyze

_Per-flow: 30, Total elapsed: 772.1s_


## Classification accuracy

| Flow | Cases | Matched | Accuracy |
|---|---:|---:|---:|
| marriage | 30 | 13 | 43% |
| funeral | 30 | 11 | 37% |
| contract | 30 | 24 | 80% |
| onboarding | 30 | 10 | 33% |

## marriage

| Case | GT doctype | Predicted | Match | Type conf | Fields filled | Avg conf | Time |
|---|---|---|---|---:|---:|---:|---:|
| marriage_baseline_001 | 喜帖/結婚證明 | 喜帖 (`wedding_invitation`) | ✓ | 0.9 | 3/4 | 0.71 | 4.1s |
| marriage_case_002 | 喜帖 | 喜帖 (`wedding_invitation`) | ✓ | 0.9 | 3/4 | 0.71 | 4.3s |
| marriage_case_003 | 結婚證明 | 結婚證書 / 結婚證明 (`marriage_certificate`) | ✓ | 0.9 | 5/5 | 0.95 | 5.0s |
| marriage_case_004 | 關係證明 | 戶口名簿 / 戶籍謄本 (`household_registration_marriage`) | ✗ | 0.9 | 3/3 | 0.95 | 4.1s |
| marriage_case_005 | 喜帖 | 喜帖 (`wedding_invitation`) | ✓ | 0.9 | 3/4 | 0.71 | 4.4s |
| marriage_case_006 | 結婚慶賀金混合文件 | 喜帖 (`wedding_invitation`) | ✗ | 0.9 | 4/4 | 0.95 | 4.7s |
| marriage_case_007 | 喜帖與申請便條 | 補助申請表 (`benefit_application_form`) | ✗ | 0.9 | 2/2 | 0.95 | 3.6s |
| marriage_case_008 | 結婚證明 | 結婚證書 / 結婚證明 (`marriage_certificate`) | ✓ | 0.9 | 3/5 | 0.57 | 4.5s |
| marriage_case_009 | 關係證明 | 戶口名簿 / 戶籍謄本 (`household_registration_marriage`) | ✗ | 0.9 | 3/3 | 0.95 | 4.1s |
| marriage_case_010 | 喜帖 | 喜帖 (`wedding_invitation`) | ✓ | 0.9 | 3/4 | 0.71 | 4.3s |
| marriage_case_011 | 結婚慶賀金混合文件 | 喜帖 (`wedding_invitation`) | ✗ | 0.9 | 4/4 | 0.95 | 4.6s |
| marriage_case_012 | 結婚慶賀金申請頁 | 補助申請表 (`benefit_application_form`) | ✗ | 0.9 | 2/2 | 0.95 | 3.8s |
| marriage_case_013 | 喜帖與申請便條 | 補助申請表 (`benefit_application_form`) | ✗ | 0.9 | 2/2 | 0.95 | 3.7s |
| marriage_case_014 | 關係證明 | 關係證明 (`relationship_proof`) | ✓ | 0.9 | 2/2 | 0.95 | 3.5s |
| marriage_case_015 | 喜帖 | 喜帖 (`wedding_invitation`) | ✓ | 0.9 | 3/4 | 0.71 | 4.4s |
| marriage_case_016 | 結婚慶賀金審核頁 | 補助申請表 (`benefit_application_form`) | ✗ | 0.9 | 2/2 | 0.86 | 3.7s |
| marriage_case_017 | 結婚證明 | 補助申請表 (`benefit_application_form`) | ✗ | 0.9 | 2/2 | 0.95 | 3.7s |
| marriage_case_018 | 結婚慶賀金申請頁 | 補助申請表 (`benefit_application_form`) | ✗ | 0.9 | 1/2 | 0.47 | 3.4s |
| marriage_case_019 | 喜帖與申請便條 | 喜帖 (`wedding_invitation`) | ✓ | 0.9 | 4/4 | 0.95 | 4.7s |
| marriage_case_020 | 結婚日期證明 | 結婚證書 / 結婚證明 (`marriage_certificate`) | ✗ | 0.9 | 3/5 | 0.57 | 4.6s |
| marriage_case_021 | 喜帖與手寫註記 | 喜帖 (`wedding_invitation`) | ✓ | 0.9 | 3/4 | 0.71 | 4.3s |
| marriage_case_022 | 結婚慶賀金附件清單 | 補助申請表 (`benefit_application_form`) | ✗ | 0.9 | 1/2 | 0.47 | 3.4s |
| marriage_case_023 | 結婚慶賀金混合文件 | 喜帖 (`wedding_invitation`) | ✗ | 0.9 | 3/4 | 0.71 | 4.3s |
| marriage_case_024 | 結婚慶賀金封面頁 | 補助申請表 (`benefit_application_form`) | ✗ | 0.9 | 1/2 | 0.47 | 3.4s |
| marriage_case_025 | 喜帖與申請便條 | 喜帖 (`wedding_invitation`) | ✓ | 0.9 | 4/4 | 0.95 | 4.6s |
| marriage_case_026 | 關係證明 | 關係證明 (`relationship_proof`) | ✓ | 0.9 | 2/2 | 0.95 | 3.5s |
| marriage_case_027 | 喜帖 | 喜帖 (`wedding_invitation`) | ✓ | 0.9 | 3/4 | 0.71 | 4.4s |
| marriage_case_028 | 結婚慶賀金審核頁 | 補助申請表 (`benefit_application_form`) | ✗ | 0.9 | 1/2 | 0.47 | 3.4s |
| marriage_case_029 | 結婚慶賀金申請頁 | 補助申請表 (`benefit_application_form`) | ✗ | 0.9 | 2/2 | 0.95 | 3.6s |
| marriage_case_030 | 結婚慶賀金混合文件 | 補助申請表 (`benefit_application_form`) | ✗ | 0.9 | 2/2 | 0.95 | 3.8s |

### Field-level detail


**marriage_baseline_001** → 喜帖

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 王小明 | 王小明 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 林小雅 | 林小雅 | 0.95 | ✓ |
| 宴客日期 (`banquet_date`) | 2026-01-18 | 2026-01-18 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | — |  | 0.0 | ⚠ |

**marriage_case_002** → 喜帖

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 林冠宇 | 林冠宇 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 吳雅婷 | 吳雅婷 | 0.95 | ✓ |
| 宴客日期 (`banquet_date`) | 2026-05-16 | 2026-05-16 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | — |  | 0.0 | ⚠ |

**marriage_case_003** → 結婚證書 / 結婚證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 張柏翰 | 張柏翰 | 0.95 | ✓ |
| 員工英文姓名 (`employee_english_name`) | Brian Chang | Brian Chang | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 陳品妤 | 陳品妤 | 0.95 | ✓ |
| 結婚生效日 / 登記日 (`marriage_date`) | 2026-07-21 | 2026-07-21 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | 2026-07-21 | 2026-07-21 | 0.95 | ✓ |

**marriage_case_004** → 戶口名簿 / 戶籍謄本

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 黃怡君 | 黃怡君 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 蔡承恩 | 蔡承恩 | 0.95 | ✓ |
| 結婚生效日 / 登記日 (`marriage_date`) | 2026-03-09 | 2026-03-09 | 0.95 | ✓ |

**marriage_case_005** → 喜帖

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 趙子豪 | 趙子豪 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 林佳穎 | 林佳穎 | 0.95 | ✓ |
| 宴客日期 (`banquet_date`) | 2026-09-05 | 2026-09-05 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | — |  | 0.0 | ⚠ |

**marriage_case_006** → 喜帖

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 鄭宇翔 | 鄭宇翔 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 李安琪 | 李安琪 | 0.95 | ✓ |
| 宴客日期 (`banquet_date`) | 2026-11-14 | 2026-11-14 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | 2026-05-12 | 2026-05-12 | 0.95 | ✓ |

**marriage_case_007** → 補助申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 林柏翰 | 林柏翰 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | 2026-03-25 | 2026-03-25 | 0.95 | ✓ |

**marriage_case_008** → 結婚證書 / 結婚證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 吳承洋 | 吳承洋 | 0.95 | ✓ |
| 員工英文姓名 (`employee_english_name`) | — |  | 0.0 | ⚠ |
| 配偶姓名 (`spouse_name`) | 黃雅婷 | 黃雅婷 | 0.95 | ✓ |
| 結婚生效日 / 登記日 (`marriage_date`) | 2026-02-06 | 2026-02-06 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | — |  | 0.0 | ⚠ |

**marriage_case_009** → 戶口名簿 / 戶籍謄本

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 張祐誠 | 張祐誠 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 李欣芸 | 李欣芸 | 0.95 | ✓ |
| 結婚生效日 / 登記日 (`marriage_date`) | 2026-03-12 | 2026-03-12 | 0.95 | ✓ |

**marriage_case_010** → 喜帖

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 蕭宇翔 | 蕭宇翔 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 郭佳穎 | 郭佳穎 | 0.95 | ✓ |
| 宴客日期 (`banquet_date`) | 2026-05-09 | 2026-05-09 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | — |  | 0.0 | ⚠ |

**marriage_case_011** → 喜帖

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 蔡明哲 | 蔡明哲 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 周品萱 | 周品萱 | 0.95 | ✓ |
| 宴客日期 (`banquet_date`) | 2026-06-20 | 2026-06-20 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | 2026-06-02 | 2026-06-02 | 0.95 | ✓ |

**marriage_case_012** → 補助申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 何冠廷 | 何冠廷 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | 2026-03-05 | 2026-03-05 | 0.95 | ✓ |

**marriage_case_013** → 補助申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 曾柏宇 | 曾柏宇 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | 2026-07-01 | 2026-07-01 | 0.95 | ✓ |

**marriage_case_014** → 關係證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 傅庭安 | 傅庭安 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 沈佳玲 | 沈佳玲 | 0.95 | ✓ |

**marriage_case_015** → 喜帖

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 羅昱辰 | 羅昱辰 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 江采蓉 | 江采蓉 | 0.95 | ✓ |
| 宴客日期 (`banquet_date`) | 2026-09-12 | 2026-09-12 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | — |  | 0.0 | ⚠ |

**marriage_case_016** → 補助申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 邱冠宇 | 邱冠宇 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | 2026-01-16 | 2026-01-16 | 0.78 | ⚠ |

**marriage_case_017** → 補助申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 洪偉倫 | 洪偉倫 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | 2026-09-25 | 2026-09-25 | 0.95 | ✓ |

**marriage_case_018** → 補助申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 葉品妍 | 葉品妍 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | — |  | 0.0 | ⚠ |

**marriage_case_019** → 喜帖

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 林哲宇 | 林哲宇 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 陳宥蓁 | 陳宥蓁 | 0.95 | ✓ |
| 宴客日期 (`banquet_date`) | 2026-01-26 | 2026-01-26 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | 2026-01-28 | 2026-01-28 | 0.95 | ✓ |

**marriage_case_020** → 結婚證書 / 結婚證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 郭佳翰 | 郭佳翰 | 0.95 | ✓ |
| 員工英文姓名 (`employee_english_name`) | — |  | 0.0 | ⚠ |
| 配偶姓名 (`spouse_name`) | 郭佳婷 | 郭佳婷 | 0.95 | ✓ |
| 結婚生效日 / 登記日 (`marriage_date`) | 2026-02-09 | 2026-02-09 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | — |  | 0.0 | ⚠ |

**marriage_case_021** → 喜帖

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 潘柏翰 | 潘柏翰 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 謝宜庭 | 謝宜庭 | 0.95 | ✓ |
| 宴客日期 (`banquet_date`) | 2026-03-21 | 2026-03-21 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | — |  | 0.0 | ⚠ |

**marriage_case_022** → 補助申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 許家豪 | 許家豪 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | — |  | 0.0 | ⚠ |

**marriage_case_023** → 喜帖

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 鄭宇軒 | 鄭宇軒 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 王若琳 | 王若琳 | 0.95 | ✓ |
| 宴客日期 (`banquet_date`) | 2026-05-18 | 2026-05-18 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | — |  | 0.0 | ⚠ |

**marriage_case_024** → 補助申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 陳昱安 | 陳昱安 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | — |  | 0.0 | ⚠ |

**marriage_case_025** → 喜帖

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 吳柏翰 | 吳柏翰 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 張宜庭 | 張宜庭 | 0.95 | ✓ |
| 宴客日期 (`banquet_date`) | 2026-07-02 | 2026-07-02 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | 2026-07-05 | 2026-07-05 | 0.95 | ✓ |

**marriage_case_026** → 關係證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 黃冠霖 | 黃冠霖 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 林沛妤 | 林沛妤 | 0.95 | ✓ |

**marriage_case_027** → 喜帖

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 蔡承翰 | 蔡承翰 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | 葉柔安 | 葉柔安 | 0.95 | ✓ |
| 宴客日期 (`banquet_date`) | 2026-09-19 | 2026-09-19 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | — |  | 0.0 | ⚠ |

**marriage_case_028** → 補助申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 鄭凱文 | 鄭凱文 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | — |  | 0.0 | ⚠ |

**marriage_case_029** → 補助申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 林子瑜 | 林子瑜 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | 2026-11-13 | 2026-11-13 | 0.95 | ✓ |

**marriage_case_030** → 補助申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 周庭瑄 | 周庭瑄 | 0.95 | ✓ |
| 文件核發日 (`document_issue_date`) | 2026-12-08 | 2026-12-08 | 0.95 | ✓ |

## funeral

| Case | GT doctype | Predicted | Match | Type conf | Fields filled | Avg conf | Time |
|---|---|---|---|---:|---:|---:|---:|
| funeral_baseline_001 | 訃聞 | 訃聞 (`obituary`) | ✓ | 0.9 | 5/5 | 0.85 | 4.8s |
| funeral_case_002 | 訃聞 | 訃聞 (`obituary`) | ✓ | 0.9 | 5/5 | 0.95 | 4.9s |
| funeral_case_003 | 死亡證明 | 死亡證明書 / 死亡診斷證明 (`death_certificate`) | ✓ | 0.9 | 2/2 | 0.95 | 3.6s |
| funeral_case_004 | 關係證明 | 關係證明 (`relationship_proof`) | ✓ | 0.9 | 1/2 | 0.47 | 3.4s |
| funeral_case_005 | 訃聞 | 訃聞 (`obituary`) | ✓ | 0.9 | 5/5 | 0.95 | 4.8s |
| funeral_case_006 | 喪葬奠儀混合文件 | 申請表 (`funeral_application_form`) | ✗ | 0.9 | 3/3 | 0.95 | 3.9s |
| funeral_case_007 | 訃聞 | 申請表 (`funeral_application_form`) | ✗ | 0.9 | 3/3 | 0.95 | 3.8s |
| funeral_case_008 | 死亡日期證明 | 死亡證明書 / 死亡診斷證明 (`death_certificate`) | ✗ | 0.9 | 2/2 | 0.95 | 3.5s |
| funeral_case_009 | 關係證明 | 申請表 (`funeral_application_form`) | ✗ | 0.9 | 3/3 | 0.95 | 3.7s |
| funeral_case_010 | 訃聞 | 申請表 (`funeral_application_form`) | ✗ | 0.9 | 3/3 | 0.95 | 3.7s |
| funeral_case_011 | 喪葬奠儀混合文件 | 訃聞 (`obituary`) | ✗ | 0.9 | 5/5 | 0.92 | 4.9s |
| funeral_case_012 | 喪葬奠儀申請頁 | 申請表 (`funeral_application_form`) | ✗ | 0.9 | 3/3 | 0.82 | 3.8s |
| funeral_case_013 | 訃聞 | 申請表 (`funeral_application_form`) | ✗ | 0.9 | 3/3 | 0.95 | 3.8s |
| funeral_case_014 | 死亡日期說明 | 死亡證明書 / 死亡診斷證明 (`death_certificate`) | ✗ | 0.9 | 2/2 | 0.95 | 3.5s |
| funeral_case_015 | 關係證明 | 申請表 (`funeral_application_form`) | ✗ | 0.9 | 3/3 | 0.95 | 3.8s |
| funeral_case_016 | 訃聞 | 訃聞 (`obituary`) | ✓ | 0.9 | 3/5 | 0.54 | 4.1s |
| funeral_case_017 | 喪葬奠儀混合文件 | 訃聞 (`obituary`) | ✗ | 0.9 | 5/5 | 0.87 | 4.3s |
| funeral_case_018 | 喪葬奠儀申請頁 | 申請表 (`funeral_application_form`) | ✗ | 0.9 | 3/3 | 0.89 | 3.8s |
| funeral_case_019 | 訃聞 | 訃聞 (`obituary`) | ✓ | 0.9 | 3/5 | 0.57 | 4.3s |
| funeral_case_020 | 死亡日期說明 | 申請表 (`funeral_application_form`) | ✗ | 0.9 | 3/3 | 0.95 | 3.8s |
| funeral_case_021 | 關係證明 | 關係證明 (`relationship_proof`) | ✓ | 0.9 | 1/2 | 0.47 | 3.3s |
| funeral_case_022 | 訃聞 | 申請表 (`funeral_application_form`) | ✗ | 0.9 | 3/3 | 0.95 | 3.8s |
| funeral_case_023 | 喪葬奠儀混合文件 | 申請表 (`funeral_application_form`) | ✗ | 0.9 | 3/3 | 0.95 | 3.8s |
| funeral_case_024 | 喪葬奠儀申請頁 | 申請表 (`funeral_application_form`) | ✗ | 0.9 | 3/3 | 0.95 | 3.7s |
| funeral_case_025 | 訃聞 | 訃聞 (`obituary`) | ✓ | 0.9 | 3/5 | 0.57 | 4.2s |
| funeral_case_026 | 死亡日期說明 | 申請表 (`funeral_application_form`) | ✗ | 0.9 | 3/3 | 0.95 | 3.7s |
| funeral_case_027 | 關係證明 | 關係證明 (`relationship_proof`) | ✓ | 0.9 | 1/2 | 0.47 | 3.3s |
| funeral_case_028 | 訃聞 | 訃聞 (`obituary`) | ✓ | 0.9 | 3/5 | 0.57 | 4.2s |
| funeral_case_029 | 喪葬奠儀混合文件 | 申請表 (`funeral_application_form`) | ✗ | 0.9 | 3/3 | 0.95 | 3.9s |
| funeral_case_030 | 喪葬奠儀申請頁 | 申請表 (`funeral_application_form`) | ✗ | 0.9 | 3/3 | 0.89 | 3.7s |

### Field-level detail


**funeral_baseline_001** → 訃聞

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 亡者姓名 (`deceased_name`) | 陳美玉 | 陳美玉 | 0.95 | ✓ |
| 儀式日期 (`funeral_date`) | 2026-02-08 | 2026-02-08 | 0.95 | ✓ |
| 儀式地點 (`funeral_location`) | 台中市北區安和會館（台中市北區太原路三段二四六號） | 台中市北區安和會館（台中市北區太原路三段二四六號） | 0.78 | ⚠ |
| 員工姓名 (`employee_name`) | 陳明德 | 陳明德 | 0.78 | ⚠ |
| 亡者關係 (`relationship`) | 子 | 子 | 0.78 | ⚠ |

**funeral_case_002** → 訃聞

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 亡者姓名 (`deceased_name`) | 李秀琴 | 李秀琴 | 0.95 | ✓ |
| 儀式日期 (`funeral_date`) | 2026-04-18 | 2026-04-18 | 0.95 | ✓ |
| 儀式地點 (`funeral_location`) | 台中市東區懷恩會館 | 台中市東區懷恩會館 | 0.95 | ✓ |
| 員工姓名 (`employee_name`) | 林冠宇 | 林冠宇 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 孝孫 | 孝孫 | 0.95 | ✓ |

**funeral_case_003** → 死亡證明書 / 死亡診斷證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 亡者姓名 (`deceased_name`) | 王進福 | 王進福 | 0.95 | ✓ |
| 死亡日期 (`death_date`) | 2026-06-04 | 2026-06-04 | 0.95 | ✓ |

**funeral_case_004** → 關係證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 黃怡君 | 黃怡君 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | — |  | 0.0 | ⚠ |

**funeral_case_005** → 訃聞

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 亡者姓名 (`deceased_name`) | 趙文昌 | 趙文昌 | 0.95 | ✓ |
| 儀式日期 (`funeral_date`) | 2026-10-09 | 2026-10-09 | 0.95 | ✓ |
| 儀式地點 (`funeral_location`) | 新竹市東區思源會館 | 新竹市東區思源會館 | 0.95 | ✓ |
| 員工姓名 (`employee_name`) | 吳怡真 | 吳怡真 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 子媳 | 子媳 | 0.95 | ✓ |

**funeral_case_006** → 申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 鄭宇翔 | 鄭宇翔 | 0.95 | ✓ |
| 亡者姓名 (`deceased_name`) | 鄭秋月 | 鄭秋月 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 母親 | 母親 | 0.95 | ✓ |

**funeral_case_007** → 申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 劉怡安 | 劉怡安 | 0.95 | ✓ |
| 亡者姓名 (`deceased_name`) | 劉文德 | 劉文德 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 父女 | 父女 | 0.95 | ✓ |

**funeral_case_008** → 死亡證明書 / 死亡診斷證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 亡者姓名 (`deceased_name`) | 陳美玉 | 陳美玉 | 0.95 | ✓ |
| 死亡日期 (`death_date`) | 2026-01-22 | 2026-01-22 | 0.95 | ✓ |

**funeral_case_009** → 申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 王思潔 | 王思潔 | 0.95 | ✓ |
| 亡者姓名 (`deceased_name`) | 王志明 | 王志明 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 父女 | 父女 | 0.95 | ✓ |

**funeral_case_010** → 申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 林家宏 | 林家宏 | 0.95 | ✓ |
| 亡者姓名 (`deceased_name`) | 林秋菊 | 林秋菊 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 祖孫 | 祖孫 | 0.95 | ✓ |

**funeral_case_011** → 訃聞

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 亡者姓名 (`deceased_name`) | 許明仁 | 許明仁 | 0.95 | ✓ |
| 儀式日期 (`funeral_date`) | 2026-02-16 | 2026-02-16 | 0.95 | ✓ |
| 儀式地點 (`funeral_location`) | 福澤殯儀館景行廳 | 福澤殯儀館景行廳 | 0.78 | ⚠ |
| 員工姓名 (`employee_name`) | 許庭瑋 | 許庭瑋 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 父子 | 父子 | 0.95 | ✓ |

**funeral_case_012** → 申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 趙雅雯 | 趙雅雯 | 0.95 | ✓ |
| 亡者姓名 (`deceased_name`) | 趙箎昌 | 趙箎昌 | 0.55 | ⚠ |
| 亡者關係 (`relationship`) | 祖父女 | 祖父女 | 0.95 | ✓ |

**funeral_case_013** → 申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 張庭維 | 張庭維 | 0.95 | ✓ |
| 亡者姓名 (`deceased_name`) | 張瑞芳 | 張瑞芳 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 母子 | 母子 | 0.95 | ✓ |

**funeral_case_014** → 死亡證明書 / 死亡診斷證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 亡者姓名 (`deceased_name`) | 周建成 | 周建成 | 0.95 | ✓ |
| 死亡日期 (`death_date`) | 2026-08-19 | 2026-08-19 | 0.95 | ✓ |

**funeral_case_015** → 申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 林宜蓁 | 林宜蓁 | 0.95 | ✓ |
| 亡者姓名 (`deceased_name`) | 林正國 | 林正國 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 父女 | 父女 | 0.95 | ✓ |

**funeral_case_016** → 訃聞

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 亡者姓名 (`deceased_name`) | 許清河 | 許清河 | 0.95 | ✓ |
| 儀式日期 (`funeral_date`) | — |  | 0.0 | ⚠ |
| 儀式地點 (`funeral_location`) | — |  | 0.0 | ⚠ |
| 員工姓名 (`employee_name`) | 許佩珊 | 許佩珊 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 祖父女 | 祖父女 | 0.78 | ⚠ |

**funeral_case_017** → 訃聞

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 亡者姓名 (`deceased_name`) | 高明宗 | 高明宗 | 0.95 | ✓ |
| 儀式日期 (`funeral_date`) | 2026-11-04 | 2026-11-04 | 0.55 | ⚠ |
| 儀式地點 (`funeral_location`) | 家中 | 家中 | 0.95 | ✓ |
| 員工姓名 (`employee_name`) | 高宇翔 | 高宇翔 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 父子 | 父子 | 0.95 | ✓ |

**funeral_case_018** → 申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 陳鈞凱 | 陳鈞凱 | 0.78 | ⚠ |
| 亡者姓名 (`deceased_name`) | 陳玉霞 | 陳玉霞 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 母子 | 母子 | 0.95 | ✓ |

**funeral_case_019** → 訃聞

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 亡者姓名 (`deceased_name`) | 黃建民 | 黃建民 | 0.95 | ✓ |
| 儀式日期 (`funeral_date`) | — |  | 0.0 | ⚠ |
| 儀式地點 (`funeral_location`) | — |  | 0.0 | ⚠ |
| 員工姓名 (`employee_name`) | 黃怡君 | 黃怡君 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 父女 | 父女 | 0.95 | ✓ |

**funeral_case_020** → 申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 蔡宗翰 | 蔡宗翰 | 0.95 | ✓ |
| 亡者姓名 (`deceased_name`) | 蔡淑貞 | 蔡淑貞 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 母子 | 母子 | 0.95 | ✓ |

**funeral_case_021** → 關係證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 葉佳蓉 | 葉佳蓉 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | — |  | 0.0 | ⚠ |

**funeral_case_022** → 申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 吳承恩 | 吳承恩 | 0.95 | ✓ |
| 亡者姓名 (`deceased_name`) | 吳清源 | 吳清源 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 祖孫 | 祖孫 | 0.95 | ✓ |

**funeral_case_023** → 申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 沈佩君 | 沈佩君 | 0.95 | ✓ |
| 亡者姓名 (`deceased_name`) | 沈榮華 | 沈榮華 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 父女 | 父女 | 0.95 | ✓ |

**funeral_case_024** → 申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 林冠廷 | 林冠廷 | 0.95 | ✓ |
| 亡者姓名 (`deceased_name`) | 林淑惠 | 林淑惠 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 母子 | 母子 | 0.95 | ✓ |

**funeral_case_025** → 訃聞

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 亡者姓名 (`deceased_name`) | 林美惠 | 林美惠 | 0.95 | ✓ |
| 儀式日期 (`funeral_date`) | — |  | 0.0 | ⚠ |
| 儀式地點 (`funeral_location`) | — |  | 0.0 | ⚠ |
| 員工姓名 (`employee_name`) | 林俊宏 | 林俊宏 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 母子 | 母子 | 0.95 | ✓ |

**funeral_case_026** → 申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 王雅婷 | 王雅婷 | 0.95 | ✓ |
| 亡者姓名 (`deceased_name`) | 王志遠 | 王志遠 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 父女 | 父女 | 0.95 | ✓ |

**funeral_case_027** → 關係證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 陳以涵 | 陳以涵 | 0.95 | ✓ |
| 配偶姓名 (`spouse_name`) | — |  | 0.0 | ⚠ |

**funeral_case_028** → 訃聞

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 亡者姓名 (`deceased_name`) | 劉安國 | 劉安國 | 0.95 | ✓ |
| 儀式日期 (`funeral_date`) | — |  | 0.0 | ⚠ |
| 儀式地點 (`funeral_location`) | — |  | 0.0 | ⚠ |
| 員工姓名 (`employee_name`) | 劉怡安 | 劉怡安 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 父女 | 父女 | 0.95 | ✓ |

**funeral_case_029** → 申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 張維倫 | 張維倫 | 0.95 | ✓ |
| 亡者姓名 (`deceased_name`) | 張素琴 | 張素琴 | 0.95 | ✓ |
| 亡者關係 (`relationship`) | 母子 | 母子 | 0.95 | ✓ |

**funeral_case_030** → 申請表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 員工姓名 (`employee_name`) | 許雅筑 | 許雅筑 | 0.95 | ✓ |
| 亡者姓名 (`deceased_name`) | 許榮昌 | 許榮昌 | 0.78 | ⚠ |
| 亡者關係 (`relationship`) | 父女 | 父女 | 0.95 | ✓ |

## contract

| Case | GT doctype | Predicted | Match | Type conf | Fields filled | Avg conf | Time |
|---|---|---|---|---:|---:|---:|---:|
| contract_baseline_001 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 11/12 | 0.84 | 15.5s |
| contract_case_002 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 11/12 | 0.84 | 16.0s |
| contract_case_003 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 12/12 | 0.87 | 15.1s |
| contract_case_004 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 12/12 | 0.87 | 14.3s |
| contract_case_005 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 11/12 | 0.83 | 18.6s |
| contract_case_006 | 手寫合約附件 | 手寫合約主文件 (`handwritten_contract`) | ✗ | 0.9 | 12/12 | 0.81 | 12.1s |
| contract_case_007 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 10/12 | 0.78 | 17.0s |
| contract_case_008 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 11/12 | 0.83 | 12.8s |
| contract_case_009 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 9/12 | 0.63 | 14.5s |
| contract_case_010 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 9/12 | 0.71 | 14.0s |
| contract_case_011 | 手寫合約附件 | 合約附件 (`contract_attachment`) | ✓ | 0.9 | 2/2 | 0.75 | 6.7s |
| contract_case_012 | 手寫合約與修正便條 | 手寫合約主文件 (`handwritten_contract`) | ✗ | 0.9 | 9/12 | 0.7 | 19.0s |
| contract_case_013 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 9/12 | 0.63 | 14.1s |
| contract_case_014 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 10/12 | 0.76 | 14.3s |
| contract_case_015 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 10/12 | 0.73 | 13.9s |
| contract_case_016 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 10/12 | 0.78 | 17.1s |
| contract_case_017 | 手寫合約附件 | 合約附件 (`contract_attachment`) | ✓ | 0.9 | 2/2 | 0.75 | 7.5s |
| contract_case_018 | 手寫合約與更正便條 | 手寫合約主文件 (`handwritten_contract`) | ✗ | 0.9 | 8/12 | 0.63 | 13.9s |
| contract_case_019 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 9/12 | 0.66 | 13.4s |
| contract_case_020 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 10/12 | 0.76 | 14.8s |
| contract_case_021 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 9/12 | 0.66 | 12.2s |
| contract_case_022 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 9/12 | 0.71 | 13.7s |
| contract_case_023 | 手寫合約附件 | 合約附件 (`contract_attachment`) | ✓ | 0.9 | 2/2 | 0.75 | 7.6s |
| contract_case_024 | 手寫合約與修正便條 | 手寫合約主文件 (`handwritten_contract`) | ✗ | 0.9 | 11/12 | 0.86 | 12.5s |
| contract_case_025 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 11/12 | 0.87 | 15.7s |
| contract_case_026 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 10/12 | 0.76 | 14.8s |
| contract_case_027 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 10/12 | 0.74 | 14.4s |
| contract_case_028 | 手寫合約 | 手寫合約主文件 (`handwritten_contract`) | ✓ | 0.9 | 11/12 | 0.87 | 14.7s |
| contract_case_029 | 手寫合約附件 | 手寫合約主文件 (`handwritten_contract`) | ✗ | 0.9 | 11/12 | 0.67 | 13.9s |
| contract_case_030 | 手寫合約與更正便條 | 手寫合約主文件 (`handwritten_contract`) | ✗ | 0.9 | 8/12 | 0.59 | 12.8s |

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

**contract_case_002** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 設備保養服務合約 | 設備保養服務合約 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 安辰科技股份有限公司 | 安辰科技股份有限公司 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 立信保養工程行 | 立信保養工程行 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-04-20 | 2026-04-20 | 0.95 | ✓ |
| 履約起日 (`start_date`) | 2026-05-01 | 2026-05-01 | 0.95 | ✓ |
| 履約迄日 (`end_date`) | 2027-04-30 | 2027-04-30 | 0.95 | ✓ |
| 服務 / 履約內容 (`service_scope`) | 每月第一週進行設備巡檢，並提供保養及異常報告。 | 每月第一週進行設備巡檢，並提供保養及異常報告。 | 0.95 | ✓ |
| 金額 (`amount`) | 18000 | 18000 | 0.78 | ⚠ |
| 付款條件 (`payment_terms`) | 每月月底請款，30日內匯款完成。 | 每月月底請款，30日內匯款完成。 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 設備保養服務合約 一、合約名稱：設備保養服務合約 二、立約人： 甲方：安辰科技股份有限公司（虛構） 乙方：立信保養工程行 | 設備保養服務合約
一、合約名稱：設備保養服務合約
二、立約人 | 0.78 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_003** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 服務合約書 | 服務合約書 | 0.78 | ⚠ |
| 甲方名稱 (`party_a_name`) | 和悅管理顧問 | 和悅管理顧問 | 0.78 | ⚠ |
| 乙方名稱 (`party_b_name`) | 明新清潔服務行 | 明新清潔服務行 | 0.78 | ⚠ |
| 合約編號 (`contract_no`) | HC-2026-0601 | HC-2026-0601 | 0.95 | ✓ |
| 生效日期 (`effective_date`) | 2026-05-22 | 2026-05-22 | 0.95 | ✓ |
| 履約起日 (`start_date`) | 2026-06-01 | 2026-06-01 | 0.95 | ✓ |
| 履約迄日 (`end_date`) | 2026-12-31 | 2026-12-31 | 0.95 | ✓ |
| 服務 / 履約內容 (`service_scope`) | 每週三巡檢廚房清潔，並回報清潔狀況及改善建議。 | 每週三巡檢廚房清潔，並回報清潔狀況及改善建議。 | 0.95 | ✓ |
| 金額 (`amount`) | 12,000 | 12,000 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 月結30日，銀行轉帳匯款。 | 月結30日，銀行轉帳匯款。 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 餐廳清潔巡檢合約 甲方：和悅管理顧問（虛構） 乙方：明新清潔服務行（虛構） 2026年6月1日至2026年12月31日止 | 餐廳清潔巡檢合約
甲方：和悅管理顧問（虛構）
乙方：明新清潔 | 0.55 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_004** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 倉儲搬運協議 | 倉儲搬運協議 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 佳禾科技(虛構) | 佳禾科技(虛構) | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 建盛搬運行(虛構) | 建盛搬運行(虛構) | 0.78 | ⚠ |
| 合約編號 (`contract_no`) | CH-20260718 | CH-20260718 | 0.95 | ✓ |
| 生效日期 (`effective_date`) | 2026-07-18 | 2026-07-18 | 0.95 | ✓ |
| 履約起日 (`start_date`) | 2026-08-01 | 2026-08-01 | 0.95 | ✓ |
| 履約迄日 (`end_date`) | 2027-07-31 | 2027-07-31 | 0.95 | ✓ |
| 服務 / 履約內容 (`service_scope`) | 週五協助倉儲搬運與清點 | 週五協助倉儲搬運與清點 | 0.95 | ✓ |
| 金額 (`amount`) | 28,000 | 28,000 | 0.78 | ⚠ |
| 付款條件 (`payment_terms`) | 月結，次月10日前付款 | 月結，次月10日前付款 | 0.78 | ⚠ |
| 手寫全文 (`handwritten_text`) | 佳禾科技(虛構) 建盛搬運行(虛構) 2026年8月1日至2027年7月31日 週五協助倉儲搬運與清點 月結，次月10日 | 佳禾科技(虛構)
建盛搬運行(虛構)
2026年8月1日至2 | 0.55 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_005** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 文書整理委託合約 | 文書整理委託合約 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 星河電子 | 星河電子 | 0.78 | ⚠ |
| 乙方名稱 (`party_b_name`) | 展益文管工作室 | 展益文管工作室 | 0.78 | ⚠ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-09-01 | 2026-09-01 | 0.95 | ✓ |
| 履約起日 (`start_date`) | 2026-09-15 | 2026-09-15 | 0.95 | ✓ |
| 履約迄日 (`end_date`) | 2027-03-14 | 2027-03-14 | 0.95 | ✓ |
| 服務 / 履約內容 (`service_scope`) | 每月整理掃描文件與歸檔清冊，並提供電子檔備份。 | 每月整理掃描文件與歸檔清冊，並提供電子檔備份。 | 0.95 | ✓ |
| 金額 (`amount`) | 15000 | 15000 | 0.78 | ⚠ |
| 付款條件 (`payment_terms`) | 驗收後請款，30日內匯款完成。 | 驗收後請款，30日內匯款完成。 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 文書整理委託合約 一、合約名稱：文書整理委託合約 二、立約人： 甲方：星河電子（虛構） 乙方：展益文管工作室（虛構） 三 | 文書整理委託合約
一、合約名稱：文書整理委託合約
二、立約人 | 0.95 | ✓ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_006** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 清潔服務追加協議書 | 清潔服務追加協議書 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 陳明德 | 陳明德 | 0.78 | ⚠ |
| 乙方名稱 (`party_b_name`) | 明冠清潔服務行 | 明冠清潔服務行 | 0.55 | ⚠ |
| 合約編號 (`contract_no`) | AH-2026-032 | AH-2026-032 | 0.95 | ✓ |
| 生效日期 (`effective_date`) | 2026-12-01 | 2026-12-01 | 0.95 | ✓ |
| 履約起日 (`start_date`) | 2026-12-01 | 2026-12-01 | 0.95 | ✓ |
| 履約迄日 (`end_date`) | 2026-12-31 | 2026-12-31 | 0.95 | ✓ |
| 服務 / 履約內容 (`service_scope`) | 每週增加一次地面清潔。 | 每週增加一次地面清潔。 | 0.78 | ⚠ |
| 金額 (`amount`) | 每月新台幣8000元整（未稅） | 每月新台幣8000元整（未稅） | 0.78 | ⚠ |
| 付款條件 (`payment_terms`) | 每月新臺幣8000元整（未稅） | 每月新臺幣8000元整（未稅） | 0.55 | ⚠ |
| 手寫全文 (`handwritten_text`) | 甲方聯絡人：陳明德 聯絡電話：0912-345-678 甲方聯絡人：陳勇技 聯絡基地：0912-287-654 乙方本簽 | 甲方聯絡人：陳明德
聯絡電話：0912-345-678
甲方 | 0.55 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_007** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 合約補充約定書 | 合約補充約定書 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 林品安 | 林品安 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 周冠宇 | 周冠宇 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-04-12 | 2026-04-12 | 0.95 | ✓ |
| 履約起日 (`start_date`) | — |  | 0.0 | ⚠ |
| 履約迄日 (`end_date`) | 2026-05-30 | 2026-05-30 | 0.95 | ✓ |
| 服務 / 履約內容 (`service_scope`) | 乙方依原合約規範，提供系統開發與後續維護服務，並依本約定之交付期限完成。 | 乙方依原合約規範，提供系統開發與後續維護服務，並依本約定之交 | 0.95 | ✓ |
| 金額 (`amount`) | 新台幣 36,500 元整（含稅） | 新台幣 36,500 元整（含稅） | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 甲方於驗收完成並確認無誤後，於七日內以銀行匯款方式支付予乙方。 | 甲方於驗收完成並確認無誤後，於七日內以銀行匯款方式支付予乙方 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 合約補充約定書  立合約補充約定書人： 甲方：林品安（以下簡稱甲方） 乙方：周冠宇（以下簡稱乙方）  雙方就原合約內容， | 合約補充約定書

立合約補充約定書人：
甲方：林品安（以下簡 | 0.78 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_008** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 手寫供測合約 | 手寫供測合約 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 黃子維 | 黃子維 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 鄭安琪 | 鄭安琪 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-03-08 | 2026-03-08 | 0.95 | ✓ |
| 履約起日 (`start_date`) | 2026-03-08 | 2026-03-08 | 0.78 | ⚠ |
| 履約迄日 (`end_date`) | 2026-04-20 | 2026-04-20 | 0.78 | ⚠ |
| 服務 / 履約內容 (`service_scope`) | 甲方委託乙方依約定提供產品，乙方同意接受並按期交付。 | 甲方委託乙方依約定提供產品，乙方同意接受並按期交付。 | 0.95 | ✓ |
| 金額 (`amount`) | 58,200元 | 58,200元 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 甲方於驗收完成後七個工作日內，以匯款方式支付。 | 甲方於驗收完成後七個工作日內，以匯款方式支付。 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 手寫供測合約 本合約由以下雙方同意簽訂，以茲共同遵守： 一、甲方委託乙方依約定提供產品，乙方同意接受並按期交付。 二、產 | 手寫供測合約
本合約由以下雙方同意簽訂，以茲共同遵守：
一、 | 0.78 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_009** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 服務確認單 | 服務確認單 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 陳彥廷 | 陳彥廷 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 林佑祥 | 林佑祥 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-06-02 | 2026-06-02 | 0.95 | ✓ |
| 履約起日 (`start_date`) | — |  | 0.0 | ⚠ |
| 履約迄日 (`end_date`) | — |  | 0.0 | ⚠ |
| 服務 / 履約內容 (`service_scope`) | 甲方委託乙方進行文件整理、分類、掃描，建檔，命名及相關資料彙整作業，並協助建文電子化查詢系統。 | 甲方委託乙方進行文件整理、分類、掃描，建檔，命名及相關資料彙 | 0.55 | ⚠ |
| 金額 (`amount`) | 12800 | 12800 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 於驗收完成後7個工作天內一次付清。 | 於驗收完成後7個工作天內一次付清。 | 0.78 | ⚠ |
| 手寫全文 (`handwritten_text`) | 服務確認單 姓名：陳彥廷 日期：2026/06/02 項目：文件整理與資料建檔 備註：完成後歸檔查詢  一、服務內容：  | 服務確認單
姓名：陳彥廷
日期：2026/06/02
項目： | 0.55 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_010** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 臨時協議書 | 臨時協議書 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 許念庭 | 許念庭 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 林以恩 | 林以恩 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-01-19 | 2026-01-19 | 0.95 | ✓ |
| 履約起日 (`start_date`) | — |  | 0.0 | ⚠ |
| 履約迄日 (`end_date`) | — |  | 0.0 | ⚠ |
| 服務 / 履約內容 (`service_scope`) | 甲方同意於本協議簽署後，提供乙方所需之資料與協助，資料總數量為 375 筆。乙方應於收到資料後七個工作天內完成檢核，並回 | 甲方同意於本協議簽署後，提供乙方所需之資料與協助，資料總數量 | 0.95 | ✓ |
| 金額 (`amount`) | 7,650 | 7,650 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 經雙方確認無誤後，甲方同意支付乙方協助費用新台幣：7,650 元整（含稅）。 | 經雙方確認無誤後，甲方同意支付乙方協助費用新台幣：7,650 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 臨時協議書  甲方：許念庭 乙方：林以恩 日期：2026/01/19  緣雙方於今日就相關事項達成臨時協議，條款如下：  | 臨時協議書

甲方：許念庭
乙方：林以恩
日期：2026/0 | 0.95 | ✓ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_011** → 合約附件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 合約手寫附件 | 合約手寫附件 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 員工：郭家棟 日期：2026/05/11 款項：25,000元 數喜：42 備註：件壹詢轉檔 茲就本次作有目，雙方同放以 | 員工：郭家棟
日期：2026/05/11
款項：25,000 | 0.55 | ⚠ |

**contract_case_012** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 手寫合約內容 | 手寫合約內容 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 簡孟軒 | 簡孟軒 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 高語晴 | 高語晴 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-02-25 | 2026-02-25 | 0.95 | ✓ |
| 履約起日 (`start_date`) | — |  | 0.0 | ⚠ |
| 履約迄日 (`end_date`) | — |  | 0.0 | ⚠ |
| 服務 / 履約內容 (`service_scope`) | 1. 紙本文件掃描與數位化 2. 資料分類、整理與建檔 3. 資料上傳與備份 4. 提供查詢與交付 | 1. 紙本文件掃描與數位化
2. 資料分類、整理與建檔
3. | 0.78 | ⚠ |
| 金額 (`amount`) | 93,100 | 93,100 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 乙方完成全部交付項目並經甲方確認後，甲方應於以下付款日支付款項予乙方。付款日：2026/03/15 | 乙方完成全部交付項目並經甲方確認後，甲方應於以下付款日支付款 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 手寫合約內容  一、立約人： 甲方：簡孟軒（以下簡稱甲方） 乙方：高語晴（以下簡稱乙方）  二、合約日期：2026/02 | 手寫合約內容

一、立約人：
甲方：簡孟軒（以下簡稱甲方）
 | 0.95 | ✓ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_013** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 手寫合約紀錄 | 手寫合約紀錄 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 王昱翔 | 王昱翔 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 林采薇 | 林采薇 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-07-07 | 2026-07-07 | 0.95 | ✓ |
| 履約起日 (`start_date`) | — |  | 0.0 | ⚠ |
| 履約迄日 (`end_date`) | — |  | 0.0 | ⚠ |
| 服務 / 履約內容 (`service_scope`) | 甲方委託乙方提供「資料建檔服務」，乙方同意依本合約規定內容執行。服務內容：將甲方提供之紙本文件，依指定欄位進行建檔，並繳 | 甲方委託乙方提供「資料建檔服務」，乙方同意依本合約規定內容執 | 0.55 | ⚠ |
| 金額 (`amount`) | 18,400 | 18,400 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 驗收完成後，乙方開立收據，甲方應於月底前付清款項。 | 驗收完成後，乙方開立收據，甲方應於月底前付清款項。 | 0.55 | ⚠ |
| 手寫全文 (`handwritten_text`) | 甲方：王昱翔 乙方：林采薇 日期：2026/07/07 項目：資料建檔服務 數量：64 單價：每件 287.50 元 金 | 甲方：王昱翔
乙方：林采薇
日期：2026/07/07
項目 | 0.78 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_014** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 手寫供測合約 | 手寫供測合約 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 鄭凱翔 | 鄭凱翔 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 陳語柔 | 陳語柔 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-08-21 | 2026-08-21 | 0.95 | ✓ |
| 履約起日 (`start_date`) | — |  | 0.0 | ⚠ |
| 履約迄日 (`end_date`) | 2026-09-10 | 2026-09-10 | 0.95 | ✓ |
| 服務 / 履約內容 (`service_scope`) | 乙方依甲方需求提供商品組裝服務。 | 乙方依甲方需求提供商品組裝服務。 | 0.95 | ✓ |
| 金額 (`amount`) | 44,700 | 44,700 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 甲方於驗收完成並確認無誤後七日內，以銀行匯款方式支付乙方款項。 | 甲方於驗收完成並確認無誤後七日內，以銀行匯款方式支付乙方款項 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 手寫供測合約  立合約書人： 甲方：鄭凱翔（以下簡稱甲方） 乙方：陳語柔（以下簡稱乙方） 雙方就以下合作內容，經協議達成 | 手寫供測合約

立合約書人：
甲方：鄭凱翔（以下簡稱甲方）
 | 0.55 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_015** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 服務交付約定 | 服務交付約定 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 何冠霖 | 何冠霖 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 蔡依婷 | 蔡依婷 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-09-14 | 2026-09-14 | 0.78 | ⚠ |
| 履約起日 (`start_date`) | — |  | 0.0 | ⚠ |
| 履約迄日 (`end_date`) | 2026-10-05 | 2026-10-05 | 0.95 | ✓ |
| 服務 / 履約內容 (`service_scope`) | 一、交付項目：資料整理 二、服務內容：乙方依甲方提供之原始資料，進行分類，整理與建檔，並提供檔案與報表，確保內容正確與完 | 一、交付項目：資料整理
二、服務內容：乙方依甲方提供之原始資 | 0.78 | ⚠ |
| 金額 (`amount`) | 72,300 | 72,300 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 五、付款方式：甲方於驗收確認無誤後，三日內以銀行匯款方式支付乙方款項。 | 五、付款方式：甲方於驗收確認無誤後，三日內以銀行匯款方式支付 | 0.78 | ⚠ |
| 手寫全文 (`handwritten_text`) | 服務交付約定  甲方：何冠霖（以下簡稱甲方） 乙方：蔡依婷（以下簡稱乙方）  雙方就以下事項達成約定如下：  一、交付項 | 服務交付約定

甲方：何冠霖（以下簡稱甲方）
乙方：蔡依婷（ | 0.78 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_016** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 合約補充條款 | 合約補充條款 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 楊承浩 | 楊承浩 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 許庭瑜 | 許庭瑜 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-10-09 | 2026-10-09 | 0.95 | ✓ |
| 履約起日 (`start_date`) | — |  | 0.0 | ⚠ |
| 履約迄日 (`end_date`) | 2026-11-05 | 2026-11-05 | 0.95 | ✓ |
| 服務 / 履約內容 (`service_scope`) | 乙方同意依照原合約規範，協助甲方進行資料彙整與文件處理，並確保內容正確與完整。 | 乙方同意依照原合約規範，協助甲方進行資料彙整與文件處理，並確 | 0.95 | ✓ |
| 金額 (`amount`) | 9850 | 9850 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 於乙方完成所有交付項目並經甲方確認無誤後，甲方將一次性支付上述款項。 | 於乙方完成所有交付項目並經甲方確認無誤後，甲方將一次性支付上 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 合約補充條款  立合約補充條款人： 甲方：楊承浩（以下簡稱甲方） 乙方：許庭瑜（以下簡稱乙方）  雙方就原合約內容，經協 | 合約補充條款

立合約補充條款人：
甲方：楊承浩（以下簡稱甲 | 0.78 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_017** → 合約附件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 手寫合約附件 | 手寫合約附件 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 一、甲方同意改成本合約所完提或提供服務，乙方同意約方付致額。 二、乙方應於交付期限內完或驗收，若、有瑕疵，甲方協要求改善 | 一、甲方同意改成本合約所完提或提供服務，乙方同意約方付致額。 | 0.55 | ⚠ |

**contract_case_018** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 合約更正紀錄 | 合約更正紀錄 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 劉品妤 | 劉品妤 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 洪哲宇 | 洪哲宇 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-12-09 | 2026-12-09 | 0.95 | ✓ |
| 履約起日 (`start_date`) | — |  | 0.0 | ⚠ |
| 履約迄日 (`end_date`) | — |  | 0.0 | ⚠ |
| 服務 / 履約內容 (`service_scope`) | 雙方同意針對本合約內容進行以下更正，並以更正後內容為準。 | 雙方同意針對本合約內容進行以下更正，並以更正後內容為準。 | 0.95 | ✓ |
| 金額 (`amount`) | 22,500 | 22,500 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | — |  | 0.0 | ⚠ |
| 手寫全文 (`handwritten_text`) | 合約更正紀錄  雙方同意針對本合約內容進行以下更正，並以更正後內容為準。  一、基本資料 甲方：劉品妤 乙方：洪哲宇 日 | 合約更正紀錄

雙方同意針對本合約內容進行以下更正，並以更正 | 0.95 | ✓ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_019** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 合作紀錄單 | 合作紀錄單 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 陳威廷 | 陳威廷 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 林語晴 | 林語晴 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-01-12 | 2026-01-12 | 0.95 | ✓ |
| 履約起日 (`start_date`) | — |  | 0.0 | ⚠ |
| 履約迄日 (`end_date`) | — |  | 0.0 | ⚠ |
| 服務 / 履約內容 (`service_scope`) | 資料整理與建檔作業 | 資料整理與建檔作業 | 0.95 | ✓ |
| 金額 (`amount`) | 15,600 | 15,600 | 0.78 | ⚠ |
| 付款條件 (`payment_terms`) | 甲方於驗收完成後一次付清。 | 甲方於驗收完成後一次付清。 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 合作紀錄單  一、立合約人： 甲方：陳威廷（以下簡稱甲方） 乙方：林語晴（以下簡稱乙方）  二、合作日期：2026/01 | 合作紀錄單

一、立合約人：
甲方：陳威廷（以下簡稱甲方）
 | 0.55 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_020** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 手寫約定書 | 手寫約定書 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 賴冠宇 | 賴冠宇 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 黃品潔 | 黃品潔 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-02-20 | 2026-02-20 | 0.95 | ✓ |
| 履約起日 (`start_date`) | 2026-02-20 | 2026-02-20 | 0.78 | ⚠ |
| 履約迄日 (`end_date`) | — |  | 0.0 | ⚠ |
| 服務 / 履約內容 (`service_scope`) | 乙方同意依甲方需求提供文件整理與檔案建置服務，並協助完成相關資料之分類與數位化作業。 | 乙方同意依甲方需求提供文件整理與檔案建置服務，並協助完成相關 | 0.95 | ✓ |
| 金額 (`amount`) | 66,800 | 66,800 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 甲方於驗收完成後七個工作天內一次付清。 | 甲方於驗收完成後七個工作天內一次付清。 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 手寫約定書  甲方：賴冠宇（以下簡稱甲方） 乙方：黃品潔（以下簡稱乙方）  一、合作事項：乙方同意依甲方需求提供文件整理 | 手寫約定書

甲方：賴冠宇（以下簡稱甲方）
乙方：黃品潔（以 | 0.78 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_021** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 履約確認單 | 履約確認單 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 王品安 | 王品安 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 周柏翰 | 周柏翰 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-03-11 | 2026-03-11 | 0.95 | ✓ |
| 履約起日 (`start_date`) | — |  | 0.0 | ⚠ |
| 履約迄日 (`end_date`) | — |  | 0.0 | ⚠ |
| 服務 / 履約內容 (`service_scope`) | 乙方向甲方提供文件整理與建檔服務，甲方確認內容無誤並同意付款。 | 乙方向甲方提供文件整理與建檔服務，甲方確認內容無誤並同意付款 | 0.95 | ✓ |
| 金額 (`amount`) | 39,200 | 39,200 | 0.78 | ⚠ |
| 付款條件 (`payment_terms`) | 驗收完成後一次付清。 | 驗收完成後一次付清。 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 履約確認單  甲方：王品安（以下簡稱甲方） 乙方：周柏翰（以下簡稱乙方）  一、合作日期：2026/03/11 二、合作 | 履約確認單

甲方：王品安（以下簡稱甲方）
乙方：周柏翰（以 | 0.55 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_022** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 合約補充約定 | 合約補充約定 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 徐子晴 | 徐子晴 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 劉承翰 | 劉承翰 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-04-22 | 2026-04-22 | 0.95 | ✓ |
| 履約起日 (`start_date`) | — |  | 0.0 | ⚠ |
| 履約迄日 (`end_date`) | — |  | 0.0 | ⚠ |
| 服務 / 履約內容 (`service_scope`) | 雙方同意就原合約部分條款進行補充約定，以下條款為本次補充之內容。本補充約定與原合約具有同等效力，如有衝突，以本補充約定為 | 雙方同意就原合約部分條款進行補充約定，以下條款為本次補充之內 | 0.95 | ✓ |
| 金額 (`amount`) | 8,900 | 8,900 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 甲方於驗收完成後七日內付款。 | 甲方於驗收完成後七日內付款。 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 合約補充約定  一、立約人 甲方：徐子晴（以下簡稱甲方） 乙方：劉承翰（以下簡稱乙方）  二、約定內容 1、雙方同意就原 | 合約補充約定

一、立約人
甲方：徐子晴（以下簡稱甲方）
乙 | 0.95 | ✓ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_023** → 合約附件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 手寫協議附件 | 手寫協議附件 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 本附件為雙方合約之律約效定，得雙方同意後生充執行。 一、合作項目：資料輸理機構籍建檔作業。 二、合作內容：乙中依內方提供 | 本附件為雙方合約之律約效定，得雙方同意後生充執行。
一、合作 | 0.55 | ⚠ |

**contract_case_024** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 合約修正備忘 | 合約修正備忘 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 唐冠宇 | 唐冠宇 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 林欣怡 | 林欣怡 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-06-27 | 2026-06-27 | 0.95 | ✓ |
| 履約起日 (`start_date`) | 2026-06-27 | 2026-06-27 | 0.95 | ✓ |
| 履約迄日 (`end_date`) | 2026-12-31 | 2026-12-31 | 0.95 | ✓ |
| 服務 / 履約內容 (`service_scope`) | 資料處理與系統測試服務 | 資料處理與系統測試服務 | 0.95 | ✓ |
| 金額 (`amount`) | 51,600 | 51,600 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 依修正後金額進行付款，付款方式與原合約相同。 | 依修正後金額進行付款，付款方式與原合約相同。 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 合約修正備忘  一、立合約人： 甲方：唐冠宇（以下簡稱甲方） 乙方：林欣怡（以下簡稱乙方）  二、合約基本資料： 日期： | 合約修正備忘

一、立合約人：
甲方：唐冠宇（以下簡稱甲方） | 0.78 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_025** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 手寫工作約定 | 手寫工作約定 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 沈志豪 | 沈志豪 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 林沛恩 | 林沛恩 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-07-13 | 2026-07-13 | 0.95 | ✓ |
| 履約起日 (`start_date`) | 2026-07-13 | 2026-07-13 | 0.95 | ✓ |
| 履約迄日 (`end_date`) | 2026-08-15 | 2026-08-15 | 0.95 | ✓ |
| 服務 / 履約內容 (`service_scope`) | 甲方委託乙方進行資料整理與建檔作業。乙方同意依甲方需求完成相關工作內容。乙方應於約定時間內完成並交付成果。 | 甲方委託乙方進行資料整理與建檔作業。乙方同意依甲方需求完成相 | 0.95 | ✓ |
| 金額 (`amount`) | 13750 | 13750 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 驗收完成並確認無誤後七日內一次付清。 | 驗收完成並確認無誤後七日內一次付清。 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 手寫工作約定  一、立約人： 甲方：沈志豪（以下簡稱甲方） 乙方：林沛恩（以下簡稱乙方）  二、約定日期：2026/07 | 手寫工作約定

一、立約人：
甲方：沈志豪（以下簡稱甲方）
 | 0.95 | ✓ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_026** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 履約手寫紀錄 | 履約手寫紀錄 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 賴柏宇 | 賴柏宇 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 黃若晴 | 黃若晴 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-08-22 | 2026-08-22 | 0.95 | ✓ |
| 履約起日 (`start_date`) | — |  | 0.0 | ⚠ |
| 履約迄日 (`end_date`) | 2026-09-12 | 2026-09-12 | 0.78 | ⚠ |
| 服務 / 履約內容 (`service_scope`) | 甲方委託乙方進行資料整理與系統建檔作業。乙方同意依約定內容與品質標準完成相關工作。乙方應於約定期限內交付成果，並配合甲方 | 甲方委託乙方進行資料整理與系統建檔作業。乙方同意依約定內容與 | 0.95 | ✓ |
| 金額 (`amount`) | 依專案需求估算為 52 份資料檔案。 | 依專案需求估算為 52 份資料檔案。 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 甲方於驗收完成並確認無誤後七日內一次支付。 | 甲方於驗收完成並確認無誤後七日內一次支付。 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 履約手寫紀錄  甲方：賴柏宇（以下簡稱甲方） 乙方：黃若晴（以下簡稱乙方）  日期：2026/08/22  一、約定內容 | 履約手寫紀錄

甲方：賴柏宇（以下簡稱甲方）
乙方：黃若晴（ | 0.78 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_027** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 服務確認手寫單 | 服務確認手寫單 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 周冠廷 | 周冠廷 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 陳思妤 | 陳思妤 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-09-17 | 2026-09-17 | 0.95 | ✓ |
| 履約起日 (`start_date`) | — |  | 0.0 | ⚠ |
| 履約迄日 (`end_date`) | 2026-10-10 | 2026-10-10 | 0.78 | ⚠ |
| 服務 / 履約內容 (`service_scope`) | 甲方委託乙方進行資料整理、文件數位化與檔案建置等相關服務、乙方同意依約 | 甲方委託乙方進行資料整理、文件數位化與檔案建置等相關服務、乙 | 0.95 | ✓ |
| 金額 (`amount`) | 28,300 | 28,300 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 甲方於驗收完成後一次付清。 | 甲方於驗收完成後一次付清。 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 服務確認手寫單  一、立約人： 甲方：周冠廷（以下簡稱甲方） 乙方：陳思妤（以下簡稱乙方）  二、服務內容： 甲方委託乙 | 服務確認手寫單

一、立約人：
甲方：周冠廷（以下簡稱甲方） | 0.55 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_028** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 合約補充紀錄 | 合約補充紀錄 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 許品妍 | 許品妍 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 郭承宇 | 郭承宇 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-10-20 | 2026-10-20 | 0.95 | ✓ |
| 履約起日 (`start_date`) | 2026-10-20 | 2026-10-20 | 0.95 | ✓ |
| 履約迄日 (`end_date`) | 2026-11-30 | 2026-11-30 | 0.95 | ✓ |
| 服務 / 履約內容 (`service_scope`) | 乙方同意依甲方需求，提供相關資料整理與文件建置服務。 | 乙方同意依甲方需求，提供相關資料整理與文件建置服務。 | 0.95 | ✓ |
| 金額 (`amount`) | 11450 | 11450 | 0.95 | ✓ |
| 付款條件 (`payment_terms`) | 驗收完成後七日內一次付款。 | 驗收完成後七日內一次付款。 | 0.95 | ✓ |
| 手寫全文 (`handwritten_text`) | 合約補充紀錄  一、立合約人： 甲方：許品妍（以下簡稱甲方） 乙方：郭承宇（以下簡稱乙方）  二、合約日期：2026/1 | 合約補充紀錄

一、立合約人：
甲方：許品妍（以下簡稱甲方） | 0.95 | ✓ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

**contract_case_029** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 合約附件手寫單 | 合約附件手寫單 | 0.55 | ⚠ |
| 甲方名稱 (`party_a_name`) | 陳柏霖 | 陳柏霖 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 林柏霖 | 林柏霖 | 0.78 | ⚠ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-11-23 | 2026-11-23 | 0.78 | ⚠ |
| 履約起日 (`start_date`) | 2026-12-15 | 2026-12-15 | 0.95 | ✓ |
| 履約迄日 (`end_date`) | 2026-12-15 | 2026-12-15 | 0.55 | ⚠ |
| 服務 / 履約內容 (`service_scope`) | 甲方委託乙方進行資料整理與建檔作業。乙方同意依甲方需求完成相關工作內容。乙方應於約定期限內完成，並交付成果。 | 甲方委託乙方進行資料整理與建檔作業。乙方同意依甲方需求完成相 | 0.78 | ⚠ |
| 金額 (`amount`) | 新台幣 76,900 元整 | 新台幣 76,900 元整 | 0.78 | ⚠ |
| 付款條件 (`payment_terms`) | 於驗收完成後七日內一次付清。 | 於驗收完成後七日內一次付清。 | 0.78 | ⚠ |
| 手寫全文 (`handwritten_text`) | 合約附件手寫單  一、立合約人： 甲方：陳柏霖（以工幣轉甲方） 乙方：林柏霖（以工幣轉乙方）  二、合約內容： 1、甲方 | 合約附件手寫單

一、立合約人：
甲方：陳柏霖（以工幣轉甲方 | 0.55 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.55 | ⚠ |

**contract_case_030** → 手寫合約主文件

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 文件標題 (`contract_title`) | 合約更正紀錄 | 合約更正紀錄 | 0.95 | ✓ |
| 甲方名稱 (`party_a_name`) | 邱子軒 | 邱子軒 | 0.95 | ✓ |
| 乙方名稱 (`party_b_name`) | 張語涵 | 張語涵 | 0.95 | ✓ |
| 合約編號 (`contract_no`) | — |  | 0.0 | ⚠ |
| 生效日期 (`effective_date`) | 2026-12-18 | 2026-12-18 | 0.95 | ✓ |
| 履約起日 (`start_date`) | — |  | 0.0 | ⚠ |
| 履約迄日 (`end_date`) | — |  | 0.0 | ⚠ |
| 服務 / 履約內容 (`service_scope`) | 經雙方協議，原合約金額需進行更正，如下列金額調整： 原金額：33,000 元整 更正金額：35,800 元整 | 經雙方協議，原合約金額需進行更正，如下列金額調整：
原金額： | 0.78 | ⚠ |
| 金額 (`amount`) | 35,800 | 35,800 | 0.78 | ⚠ |
| 付款條件 (`payment_terms`) | — |  | 0.0 | ⚠ |
| 手寫全文 (`handwritten_text`) | 合約更正紀錄  一、立合約人： 甲方：邱子軒（以下簡稱甲方） 乙方：張語涵（以下簡稱乙方）  二、合約日期：2026/1 | 合約更正紀錄

一、立合約人：
甲方：邱子軒（以下簡稱甲方） | 0.78 | ⚠ |
| 是否簽名 / 用印 (`signature_or_stamp_present`) | True | True | 0.95 | ✓ |

## onboarding

| Case | GT doctype | Predicted | Match | Type conf | Fields filled | Avg conf | Time |
|---|---|---|---|---:|---:|---:|---:|
| onboarding_baseline_001 | 體檢資料 | 體檢報告 (`health_check_report`) | ✗ | 0.9 | 2/2 | 0.95 | 3.8s |
| onboarding_case_002 | 體檢資料 | 體檢報告 (`health_check_report`) | ✗ | 0.9 | 2/2 | 0.95 | 3.7s |
| onboarding_case_003 | 銀行帳戶影本 | 存摺封面 / 薪轉帳戶 (`bank_account_copy`) | ✗ | 0.9 | 2/3 | 0.63 | 4.0s |
| onboarding_case_004 | 學歷證明 | 最高學歷證明 (`education_certificate`) | ✓ | 0.9 | 3/3 | 0.95 | 3.8s |
| onboarding_case_005 | 證照 | 專業證照 (`professional_license`) | ✓ | 0.9 | 2/2 | 0.95 | 3.6s |
| onboarding_case_006 | 到職文件清單 | 人事基本資料表 / 報到表 (`onboarding_form`) | ✗ | 0.9 | 2/5 | 0.38 | 4.3s |
| onboarding_case_007 | 體檢資料 | 體檢報告 (`health_check_report`) | ✗ | 0.9 | 2/2 | 0.95 | 3.7s |
| onboarding_case_008 | 銀行帳戶影本 | 存摺封面 / 薪轉帳戶 (`bank_account_copy`) | ✗ | 0.9 | 3/3 | 0.95 | 4.3s |
| onboarding_case_009 | 學歷證明 | 最高學歷證明 (`education_certificate`) | ✓ | 0.9 | 3/3 | 0.95 | 3.7s |
| onboarding_case_010 | 證照 | 專業證照 (`professional_license`) | ✓ | 0.9 | 2/2 | 0.95 | 3.5s |
| onboarding_case_011 | 到職文件清單 | 人事基本資料表 / 報到表 (`onboarding_form`) | ✗ | 0.9 | 1/5 | 0.19 | 4.0s |
| onboarding_case_012 | 到職文件混合包 | 人事基本資料表 / 報到表 (`onboarding_form`) | ✗ | 0.9 | 1/5 | 0.19 | 3.9s |
| onboarding_case_013 | 體檢資料 | 體檢報告 (`health_check_report`) | ✗ | 0.9 | 2/2 | 0.95 | 3.8s |
| onboarding_case_014 | 銀行帳戶影本 | 存摺封面 / 薪轉帳戶 (`bank_account_copy`) | ✗ | 0.9 | 3/3 | 0.95 | 4.0s |
| onboarding_case_015 | 學歷證明 | 最高學歷證明 (`education_certificate`) | ✓ | 0.9 | 2/3 | 0.63 | 3.8s |
| onboarding_case_016 | 證照 | 專業證照 (`professional_license`) | ✓ | 0.9 | 2/2 | 0.95 | 3.5s |
| onboarding_case_017 | 到職文件清單 | 人事基本資料表 / 報到表 (`onboarding_form`) | ✗ | 0.9 | 1/5 | 0.19 | 3.8s |
| onboarding_case_018 | 到職文件混合包 | 人事基本資料表 / 報到表 (`onboarding_form`) | ✗ | 0.9 | 1/5 | 0.19 | 4.0s |
| onboarding_case_019 | 體檢資料 | 體檢報告 (`health_check_report`) | ✗ | 0.9 | 2/2 | 0.95 | 3.7s |
| onboarding_case_020 | 銀行帳戶影本 | 存摺封面 / 薪轉帳戶 (`bank_account_copy`) | ✗ | 0.9 | 3/3 | 0.95 | 4.0s |
| onboarding_case_021 | 學歷證明 | 最高學歷證明 (`education_certificate`) | ✓ | 0.9 | 3/3 | 0.95 | 3.8s |
| onboarding_case_022 | 證照 | 專業證照 (`professional_license`) | ✓ | 0.9 | 2/2 | 0.95 | 3.5s |
| onboarding_case_023 | 到職文件清單 | 人事基本資料表 / 報到表 (`onboarding_form`) | ✗ | 0.9 | 1/5 | 0.19 | 3.9s |
| onboarding_case_024 | 到職文件混合包 | 人事基本資料表 / 報到表 (`onboarding_form`) | ✗ | 0.9 | 1/5 | 0.19 | 4.0s |
| onboarding_case_025 | 體檢資料 | 體檢報告 (`health_check_report`) | ✗ | 0.9 | 2/2 | 0.95 | 3.7s |
| onboarding_case_026 | 銀行帳戶影本 | 存摺封面 / 薪轉帳戶 (`bank_account_copy`) | ✗ | 0.9 | 3/3 | 0.95 | 3.9s |
| onboarding_case_027 | 學歷證明 | 最高學歷證明 (`education_certificate`) | ✓ | 0.9 | 3/3 | 0.95 | 3.8s |
| onboarding_case_028 | 證照 | 專業證照 (`professional_license`) | ✓ | 0.9 | 2/2 | 0.95 | 3.6s |
| onboarding_case_029 | 到職文件清單 | 人事基本資料表 / 報到表 (`onboarding_form`) | ✗ | 0.9 | 1/5 | 0.19 | 3.9s |
| onboarding_case_030 | 到職文件混合包 | 人事基本資料表 / 報到表 (`onboarding_form`) | ✗ | 0.9 | 1/5 | 0.19 | 4.0s |

### Field-level detail


**onboarding_baseline_001** → 體檢報告

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 林怡君 | 林怡君 | 0.95 | ✓ |
| 體檢日期 (`health_check_date`) | 2026-03-20 | 2026-03-20 | 0.95 | ✓ |

**onboarding_case_002** → 體檢報告

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 張柏翰 | 張柏翰 | 0.95 | ✓ |
| 體檢日期 (`health_check_date`) | 2026-05-08 | 2026-05-08 | 0.95 | ✓ |

**onboarding_case_003** → 存摺封面 / 薪轉帳戶

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 黃怡君 | 黃怡君 | 0.95 | ✓ |
| 銀行名稱 (`bank_name`) | — |  | 0.0 | ⚠ |
| 銀行帳號 (`bank_account`) | 822-***-***-129 | 822-***-***-129 | 0.95 | ✓ |

**onboarding_case_004** → 最高學歷證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 趙子豪 | 趙子豪 | 0.95 | ✓ |
| 最高學歷 (`education_level`) | 學士 | 學士 | 0.95 | ✓ |
| 學校名稱 (`school_name`) | 大華科技大學 | 大華科技大學 | 0.95 | ✓ |

**onboarding_case_005** → 專業證照

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 鄭宇翔 | 鄭宇翔 | 0.95 | ✓ |
| 證照名稱 (`license_name`) | 職業安全基礎訓練證明 | 職業安全基礎訓練證明 | 0.95 | ✓ |

**onboarding_case_006** → 人事基本資料表 / 報到表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | — |  | 0.0 | ⚠ |
| 英文姓名 (`candidate_english_name`) | Kevin Lin | Kevin Lin | 0.95 | ✓ |
| 身分證字號 (`id_number`) | — |  | 0.0 | ⚠ |
| 出生日期 (`birth_date`) | — |  | 0.0 | ⚠ |
| 應徵職務 (`position_name`) | 製造技術員 | 製造技術員 | 0.95 | ✓ |

**onboarding_case_007** → 體檢報告

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 謝承恩 | 謝承恩 | 0.95 | ✓ |
| 體檢日期 (`health_check_date`) | 2026-04-06 | 2026-04-06 | 0.95 | ✓ |

**onboarding_case_008** → 存摺封面 / 薪轉帳戶

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 林映辰 | 林映辰 | 0.95 | ✓ |
| 銀行名稱 (`bank_name`) | 青禾商業銀行 | 青禾商業銀行 | 0.95 | ✓ |
| 銀行帳號 (`bank_account`) | 12345678901234567890 | 12345678901234567890 | 0.95 | ✓ |

**onboarding_case_009** → 最高學歷證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 吳佳穎 | 吳佳穎 | 0.95 | ✓ |
| 最高學歷 (`education_level`) | 學士 | 學士 | 0.95 | ✓ |
| 學校名稱 (`school_name`) | 晴川科技學院 | 晴川科技學院 | 0.95 | ✓ |

**onboarding_case_010** → 專業證照

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 張又仁 | 張又仁 | 0.95 | ✓ |
| 證照名稱 (`license_name`) | 設備維護基礎證明 | 設備維護基礎證明 | 0.95 | ✓ |

**onboarding_case_011** → 人事基本資料表 / 報到表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 陳家霖 | 陳家霖 | 0.95 | ✓ |
| 英文姓名 (`candidate_english_name`) | — |  | 0.0 | ⚠ |
| 身分證字號 (`id_number`) | — |  | 0.0 | ⚠ |
| 出生日期 (`birth_date`) | — |  | 0.0 | ⚠ |
| 應徵職務 (`position_name`) | — |  | 0.0 | ⚠ |

**onboarding_case_012** → 人事基本資料表 / 報到表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 許庭安 | 許庭安 | 0.95 | ✓ |
| 英文姓名 (`candidate_english_name`) | — |  | 0.0 | ⚠ |
| 身分證字號 (`id_number`) | — |  | 0.0 | ⚠ |
| 出生日期 (`birth_date`) | — |  | 0.0 | ⚠ |
| 應徵職務 (`position_name`) | — |  | 0.0 | ⚠ |

**onboarding_case_013** → 體檢報告

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 黃彥廷 | 黃彥廷 | 0.95 | ✓ |
| 體檢日期 (`health_check_date`) | 2026-07-15 | 2026-07-15 | 0.95 | ✓ |

**onboarding_case_014** → 存摺封面 / 薪轉帳戶

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 吳承恩 | 吳承恩 | 0.95 | ✓ |
| 銀行名稱 (`bank_name`) | 青禾商銀 | 青禾商銀 | 0.95 | ✓ |
| 銀行帳號 (`bank_account`) | **** **** 7392 | **** **** 7392 | 0.95 | ✓ |

**onboarding_case_015** → 最高學歷證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 林庭萱 | 林庭萱 | 0.95 | ✓ |
| 最高學歷 (`education_level`) | — |  | 0.0 | ⚠ |
| 學校名稱 (`school_name`) | 禾岳技術學院 | 禾岳技術學院 | 0.95 | ✓ |

**onboarding_case_016** → 專業證照

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 陳品睿 | 陳品睿 | 0.95 | ✓ |
| 證照名稱 (`license_name`) | 安全作業基礎證明 | 安全作業基礎證明 | 0.95 | ✓ |

**onboarding_case_017** → 人事基本資料表 / 報到表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 李佳容 | 李佳容 | 0.95 | ✓ |
| 英文姓名 (`candidate_english_name`) | — |  | 0.0 | ⚠ |
| 身分證字號 (`id_number`) | — |  | 0.0 | ⚠ |
| 出生日期 (`birth_date`) | — |  | 0.0 | ⚠ |
| 應徵職務 (`position_name`) | — |  | 0.0 | ⚠ |

**onboarding_case_018** → 人事基本資料表 / 報到表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 蘇柏翰 | 蘇柏翰 | 0.95 | ✓ |
| 英文姓名 (`candidate_english_name`) | — |  | 0.0 | ⚠ |
| 身分證字號 (`id_number`) | — |  | 0.0 | ⚠ |
| 出生日期 (`birth_date`) | — |  | 0.0 | ⚠ |
| 應徵職務 (`position_name`) | — |  | 0.0 | ⚠ |

**onboarding_case_019** → 體檢報告

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 林冠宏 | 林冠宏 | 0.95 | ✓ |
| 體檢日期 (`health_check_date`) | 2026-02-06 | 2026-02-06 | 0.95 | ✓ |

**onboarding_case_020** → 存摺封面 / 薪轉帳戶

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 蔡欣妤 | 蔡欣妤 | 0.95 | ✓ |
| 銀行名稱 (`bank_name`) | 禾信商銀 | 禾信商銀 | 0.95 | ✓ |
| 銀行帳號 (`bank_account`) | **** **** 8156 | **** **** 8156 | 0.95 | ✓ |

**onboarding_case_021** → 最高學歷證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 方怡蓁 | 方怡蓁 | 0.95 | ✓ |
| 最高學歷 (`education_level`) | 學士 | 學士 | 0.95 | ✓ |
| 學校名稱 (`school_name`) | 澄禾技術學院 | 澄禾技術學院 | 0.95 | ✓ |

**onboarding_case_022** → 專業證照

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 吳家豪 | 吳家豪 | 0.95 | ✓ |
| 證照名稱 (`license_name`) | 基礎設備操作證明 | 基礎設備操作證明 | 0.95 | ✓ |

**onboarding_case_023** → 人事基本資料表 / 報到表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 張雅婷 | 張雅婷 | 0.95 | ✓ |
| 英文姓名 (`candidate_english_name`) | — |  | 0.0 | ⚠ |
| 身分證字號 (`id_number`) | — |  | 0.0 | ⚠ |
| 出生日期 (`birth_date`) | — |  | 0.0 | ⚠ |
| 應徵職務 (`position_name`) | — |  | 0.0 | ⚠ |

**onboarding_case_024** → 人事基本資料表 / 報到表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 劉彥丞 | 劉彥丞 | 0.95 | ✓ |
| 英文姓名 (`candidate_english_name`) | — |  | 0.0 | ⚠ |
| 身分證字號 (`id_number`) | — |  | 0.0 | ⚠ |
| 出生日期 (`birth_date`) | — |  | 0.0 | ⚠ |
| 應徵職務 (`position_name`) | — |  | 0.0 | ⚠ |

**onboarding_case_025** → 體檢報告

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 洪品蓁 | 洪品蓁 | 0.95 | ✓ |
| 體檢日期 (`health_check_date`) | 2026-07-19 | 2026-07-19 | 0.95 | ✓ |

**onboarding_case_026** → 存摺封面 / 薪轉帳戶

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 楊承恩 | 楊承恩 | 0.95 | ✓ |
| 銀行名稱 (`bank_name`) | 青禾商銀 | 青禾商銀 | 0.95 | ✓ |
| 銀行帳號 (`bank_account`) | **** **** 5274 | **** **** 5274 | 0.95 | ✓ |

**onboarding_case_027** → 最高學歷證明

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 曾雅琪 | 曾雅琪 | 0.95 | ✓ |
| 最高學歷 (`education_level`) | 副學士 | 副學士 | 0.95 | ✓ |
| 學校名稱 (`school_name`) | 晴峰技術學院 | 晴峰技術學院 | 0.95 | ✓ |

**onboarding_case_028** → 專業證照

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 廖冠宇 | 廖冠宇 | 0.95 | ✓ |
| 證照名稱 (`license_name`) | 廠務安全基礎證明 | 廠務安全基礎證明 | 0.95 | ✓ |

**onboarding_case_029** → 人事基本資料表 / 報到表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 何怡萱 | 何怡萱 | 0.95 | ✓ |
| 英文姓名 (`candidate_english_name`) | — |  | 0.0 | ⚠ |
| 身分證字號 (`id_number`) | — |  | 0.0 | ⚠ |
| 出生日期 (`birth_date`) | — |  | 0.0 | ⚠ |
| 應徵職務 (`position_name`) | — |  | 0.0 | ⚠ |

**onboarding_case_030** → 人事基本資料表 / 報到表

| Field | Value | Normalized | Conf | Review |
|---|---|---|---:|:-:|
| 面試者姓名 (`candidate_name`) | 陳柏瑋 | 陳柏瑋 | 0.95 | ✓ |
| 英文姓名 (`candidate_english_name`) | — |  | 0.0 | ⚠ |
| 身分證字號 (`id_number`) | — |  | 0.0 | ⚠ |
| 出生日期 (`birth_date`) | — |  | 0.0 | ⚠ |
| 應徵職務 (`position_name`) | — |  | 0.0 | ⚠ |