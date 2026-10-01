# BomDD ECO-089 V5 — arms を実装後の bomdd-lint に当てた結果

- 測定日: 2026-10-01・計器= BomDD-Plm `0d98371` の作業木の dist(clean)
- 期待は measure-arms.py の ARMS(実装の前に固定)から読み、書き換えていない。

| 土台 | arm | ゲート | 期待 | exit | 判定 | 測定不能の所見 | RED の所見 | measurement | 版 |
|---|---|---|---|---|---|---|---|---|---|
| plm-self | A1-clean | always | PASS | 0 | 一致 | 0 | 0 | 0 | plm-diag/2 |
| plm-self | A1-clean | acceptance | PASS | 0 | 一致 | 0 | 0 | 0 | plm-diag/2 |
| plm-self | A2-rename-mbom-key | always | MEASUREMENT_FAILURE | 1 | 一致 | 8 | 32 | 1 | plm-diag/2 |
| plm-self | A2-rename-mbom-key | acceptance | MEASUREMENT_FAILURE | 1 | 一致 | 8 | 32 | 1 | plm-diag/2 |
| plm-self | A3-rename-cp-key | always | MEASUREMENT_FAILURE | 1 | 一致 | 177 | 11 | 1 | plm-diag/2 |
| plm-self | A3-rename-cp-key | acceptance | MEASUREMENT_FAILURE | 1 | 一致 | 177 | 11 | 2 | plm-diag/2 |
| plm-self | A4-broken-mbom-yaml | always | MEASUREMENT_FAILURE | 1 | 一致 | 9 | 32 | 1 | plm-diag/2 |
| plm-self | A4-broken-mbom-yaml | acceptance | MEASUREMENT_FAILURE | 1 | 一致 | 9 | 32 | 1 | plm-diag/2 |
| plm-self | A5-broken-cp-yaml | always | MEASUREMENT_FAILURE | 1 | 一致 | 189 | 11 | 2 | plm-diag/2 |
| plm-self | A5-broken-cp-yaml | acceptance | MEASUREMENT_FAILURE | 1 | 一致 | 189 | 11 | 3 | plm-diag/2 |
| plm-self | A6-empty-mbom | always | MEASUREMENT_FAILURE | 1 | 一致 | 9 | 32 | 1 | plm-diag/2 |
| plm-self | A6-empty-mbom | acceptance | MEASUREMENT_FAILURE | 1 | 一致 | 9 | 32 | 1 | plm-diag/2 |
| plm-self | A7-dangling-ref | always | RED | 1 | 一致 | 0 | 1 | 0 | plm-diag/2 |
| plm-self | A7-dangling-ref | acceptance | RED | 1 | 一致 | 0 | 1 | 0 | plm-diag/2 |
| plm-self | A8-ab-fail-row | always | PASS | 0 | 一致 | 0 | 0 | 0 | plm-diag/2 |
| plm-self | A8-ab-fail-row | acceptance | RED | 1 | 一致 | 0 | 1 | 0 | plm-diag/2 |
| minimal | A1-clean | always | PASS | 0 | 一致 | 0 | 0 | 0 | plm-diag/2 |
| minimal | A1-clean | acceptance | PASS | 0 | 一致 | 0 | 0 | 0 | plm-diag/2 |
| minimal | A2-rename-mbom-key | always | MEASUREMENT_FAILURE | 1 | 一致 | 1 | 0 | 1 | plm-diag/2 |
| minimal | A2-rename-mbom-key | acceptance | MEASUREMENT_FAILURE | 1 | 一致 | 3 | 0 | 3 | plm-diag/2 |
| minimal | A3-rename-cp-key | always | MEASUREMENT_FAILURE | 1 | 一致 | 3 | 0 | 1 | plm-diag/2 |
| minimal | A3-rename-cp-key | acceptance | MEASUREMENT_FAILURE | 1 | 一致 | 3 | 0 | 2 | plm-diag/2 |
| minimal | A4-broken-mbom-yaml | always | MEASUREMENT_FAILURE | 1 | 一致 | 2 | 0 | 1 | plm-diag/2 |
| minimal | A4-broken-mbom-yaml | acceptance | MEASUREMENT_FAILURE | 1 | 一致 | 4 | 0 | 3 | plm-diag/2 |
| minimal | A5-broken-cp-yaml | always | MEASUREMENT_FAILURE | 1 | 一致 | 4 | 0 | 1 | plm-diag/2 |
| minimal | A5-broken-cp-yaml | acceptance | MEASUREMENT_FAILURE | 1 | 一致 | 4 | 0 | 2 | plm-diag/2 |
| minimal | A6-empty-mbom | always | MEASUREMENT_FAILURE | 1 | 一致 | 2 | 0 | 1 | plm-diag/2 |
| minimal | A6-empty-mbom | acceptance | MEASUREMENT_FAILURE | 1 | 一致 | 4 | 0 | 3 | plm-diag/2 |
| minimal | A7-dangling-ref | always | RED | 1 | 一致 | 0 | 1 | 0 | plm-diag/2 |
| minimal | A7-dangling-ref | acceptance | RED | 1 | 一致 | 0 | 2 | 0 | plm-diag/2 |
| minimal | A8-ab-fail-row | always | PASS | 0 | 一致 | 0 | 0 | 0 | plm-diag/2 |
| minimal | A8-ab-fail-row | acceptance | RED | 1 | 一致 | 0 | 2 | 0 | plm-diag/2 |
| minimal | A1b-clean-unreferenced | always | PASS | 0 | 一致 | 0 | 0 | 0 | plm-diag/2 |
| minimal | A1b-clean-unreferenced | acceptance | PASS | 0 | 一致 | 0 | 0 | 0 | plm-diag/2 |
| minimal | A9-rename-mbom-key-unreferenced | always | MEASUREMENT_FAILURE | 0 | **不一致** | 0 | 0 | 0 | plm-diag/2 |
| minimal | A9-rename-mbom-key-unreferenced | acceptance | MEASUREMENT_FAILURE | 1 | 一致 | 2 | 0 | 2 | plm-diag/2 |

集計: 35/36 組が期待と一致。
