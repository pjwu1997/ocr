# 封存 Benchmark — Strict vs Semantic Classification Accuracy

_LLM-as-judge re-scoring using Qwen3.5-27B on 62 strict-miss pairs. Judge time: 3.7s._


## Overall accuracy

| Flow | Cases | Strict match | Semantic match (LLM judge) | Strict % | Semantic % |
|---|---:|---:|---:|---:|---:|
| marriage | 30 | 13 | 13 | 43% | 43% |
| funeral | 30 | 11 | 15 | 37% | 50% |
| contract | 30 | 24 | 24 | 80% | 80% |
| onboarding | 30 | 10 | 16 | 33% | 53% |
| **all** | **120** | **58** | **68** | **48%** | **57%** |

## Cases the LLM judge flipped (strict-miss → semantic-match)


### funeral

| Case | GT label | Predicted label |
|---|---|---|
| funeral_case_012 | 喪葬奠儀申請頁 | 申請表 |
| funeral_case_018 | 喪葬奠儀申請頁 | 申請表 |
| funeral_case_024 | 喪葬奠儀申請頁 | 申請表 |
| funeral_case_030 | 喪葬奠儀申請頁 | 申請表 |

### onboarding

| Case | GT label | Predicted label |
|---|---|---|
| onboarding_baseline_001 | 體檢資料 | 體檢報告 |
| onboarding_case_002 | 體檢資料 | 體檢報告 |
| onboarding_case_007 | 體檢資料 | 體檢報告 |
| onboarding_case_013 | 體檢資料 | 體檢報告 |
| onboarding_case_019 | 體檢資料 | 體檢報告 |
| onboarding_case_025 | 體檢資料 | 體檢報告 |

## Cases that remain misses even after fuzzy judging


### marriage

| Case | GT label | Predicted label |
|---|---|---|
| marriage_case_004 | 關係證明 | 戶口名簿 / 戶籍謄本 |
| marriage_case_006 | 結婚慶賀金混合文件 | 喜帖 |
| marriage_case_007 | 喜帖與申請便條 | 補助申請表 |
| marriage_case_009 | 關係證明 | 戶口名簿 / 戶籍謄本 |
| marriage_case_011 | 結婚慶賀金混合文件 | 喜帖 |
| marriage_case_012 | 結婚慶賀金申請頁 | 補助申請表 |
| marriage_case_013 | 喜帖與申請便條 | 補助申請表 |
| marriage_case_016 | 結婚慶賀金審核頁 | 補助申請表 |
| marriage_case_017 | 結婚證明 | 補助申請表 |
| marriage_case_018 | 結婚慶賀金申請頁 | 補助申請表 |
| marriage_case_020 | 結婚日期證明 | 結婚證書 / 結婚證明 |
| marriage_case_022 | 結婚慶賀金附件清單 | 補助申請表 |
| marriage_case_023 | 結婚慶賀金混合文件 | 喜帖 |
| marriage_case_024 | 結婚慶賀金封面頁 | 補助申請表 |
| marriage_case_028 | 結婚慶賀金審核頁 | 補助申請表 |
| marriage_case_029 | 結婚慶賀金申請頁 | 補助申請表 |
| marriage_case_030 | 結婚慶賀金混合文件 | 補助申請表 |

### funeral

| Case | GT label | Predicted label |
|---|---|---|
| funeral_case_006 | 喪葬奠儀混合文件 | 申請表 |
| funeral_case_007 | 訃聞 | 申請表 |
| funeral_case_008 | 死亡日期證明 | 死亡證明書 / 死亡診斷證明 |
| funeral_case_009 | 關係證明 | 申請表 |
| funeral_case_010 | 訃聞 | 申請表 |
| funeral_case_011 | 喪葬奠儀混合文件 | 訃聞 |
| funeral_case_013 | 訃聞 | 申請表 |
| funeral_case_014 | 死亡日期說明 | 死亡證明書 / 死亡診斷證明 |
| funeral_case_015 | 關係證明 | 申請表 |
| funeral_case_017 | 喪葬奠儀混合文件 | 訃聞 |
| funeral_case_020 | 死亡日期說明 | 申請表 |
| funeral_case_022 | 訃聞 | 申請表 |
| funeral_case_023 | 喪葬奠儀混合文件 | 申請表 |
| funeral_case_026 | 死亡日期說明 | 申請表 |
| funeral_case_029 | 喪葬奠儀混合文件 | 申請表 |

### contract

| Case | GT label | Predicted label |
|---|---|---|
| contract_case_006 | 手寫合約附件 | 手寫合約主文件 |
| contract_case_012 | 手寫合約與修正便條 | 手寫合約主文件 |
| contract_case_018 | 手寫合約與更正便條 | 手寫合約主文件 |
| contract_case_024 | 手寫合約與修正便條 | 手寫合約主文件 |
| contract_case_029 | 手寫合約附件 | 手寫合約主文件 |
| contract_case_030 | 手寫合約與更正便條 | 手寫合約主文件 |

### onboarding

| Case | GT label | Predicted label |
|---|---|---|
| onboarding_case_003 | 銀行帳戶影本 | 存摺封面 / 薪轉帳戶 |
| onboarding_case_006 | 到職文件清單 | 人事基本資料表 / 報到表 |
| onboarding_case_008 | 銀行帳戶影本 | 存摺封面 / 薪轉帳戶 |
| onboarding_case_011 | 到職文件清單 | 人事基本資料表 / 報到表 |
| onboarding_case_012 | 到職文件混合包 | 人事基本資料表 / 報到表 |
| onboarding_case_014 | 銀行帳戶影本 | 存摺封面 / 薪轉帳戶 |
| onboarding_case_017 | 到職文件清單 | 人事基本資料表 / 報到表 |
| onboarding_case_018 | 到職文件混合包 | 人事基本資料表 / 報到表 |
| onboarding_case_020 | 銀行帳戶影本 | 存摺封面 / 薪轉帳戶 |
| onboarding_case_023 | 到職文件清單 | 人事基本資料表 / 報到表 |
| onboarding_case_024 | 到職文件混合包 | 人事基本資料表 / 報到表 |
| onboarding_case_026 | 銀行帳戶影本 | 存摺封面 / 薪轉帳戶 |
| onboarding_case_029 | 到職文件清單 | 人事基本資料表 / 報到表 |
| onboarding_case_030 | 到職文件混合包 | 人事基本資料表 / 報到表 |