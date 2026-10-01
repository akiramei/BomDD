# ECO-089 較正測定 — 現行 bomdd-lint に「測定できなかった」を当てた結果(是正前)

- 測定日: 2026-10-01
- 土台の出所: BomDD-Plm `d02052b`(git archive HEAD)・作業木: clean。変異前(A1)は 2 土台とも両ゲート exit 0 を確認済み
- 計器: `packages/cli/dist/main.js`・evaluate.js sha256 先頭 12= `cd8d8bb4e679`・node v22.13.1
- 期待は本スクリプトの ARMS に実装の前に固定(契約後の判定)。現行出力は期待と突き合わせるだけで、期待の導出に使っていない。
- 母集団の限界: 土台 2 種・変異 8 種(minimal のみ変種 2 本を追加)・各 1 回。変異の分布は私の設計であり、実在の事故の分布ではない。「差分」は土台(A1)に対する所見の増減。

## 土台 plm-self

| arm | 壊したもの | ゲート | 期待(契約後) | 現行の exit | 現行の読み | error の増分 | 所見の差分 |
|---|---|---|---|---|---|---|---|
| A1-clean | 変異なし(土台) | always | PASS | 0 | 一致 | +0 | 差なし |
| A1-clean | 変異なし(土台) | acceptance | PASS | 0 | 一致 | +0 | 差なし |
| A2-rename-mbom-key | 32-mbom の manufacturing_units を process_units へ改名(キー空振り) | always | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +8 | error R-003 +8, info R-005 +31 |
| A2-rename-mbom-key | 32-mbom の manufacturing_units を process_units へ改名(キー空振り) | acceptance | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +8 | error R-003 +8, info R-005 +31, info R-050 +1 |
| A3-rename-cp-key | 33-control-plan の characteristics を checks へ改名(キー空振り) | always | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +158 | error R-003 +158, info R-005 +1 |
| A3-rename-cp-key | 33-control-plan の characteristics を checks へ改名(キー空振り) | acceptance | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +158 | error R-003 +158, info R-005 +1 |
| A4-broken-mbom-yaml | 32-mbom.yaml の末尾へ YAML 構文エラーを 1 行足す(読めない入力) | always | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +9 | error R-003 +8, error X-PARSE-001 +1, info R-005 +31 |
| A4-broken-mbom-yaml | 32-mbom.yaml の末尾へ YAML 構文エラーを 1 行足す(読めない入力) | acceptance | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +9 | error R-003 +8, error X-PARSE-001 +1, info R-005 +31, info R-050 +1 |
| A5-broken-cp-yaml | 33-control-plan.yaml の末尾へ YAML 構文エラーを 1 行足す(読めない入力) | always | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +159 | error R-003 +158, error X-PARSE-001 +1, info R-005 +1, warn R-003 +11 |
| A5-broken-cp-yaml | 33-control-plan.yaml の末尾へ YAML 構文エラーを 1 行足す(読めない入力) | acceptance | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +159 | error R-003 +158, error X-PARSE-001 +1, info R-005 +1, warn R-003 +11 |
| A6-empty-mbom | 32-mbom.yaml を空文書にする(対象 0 件・上流の 30-ebom は実現を要する品目を持つ) | always | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +8 | error R-003 +8, info R-005 +31, warn X-TYPE-001 +1 |
| A6-empty-mbom | 32-mbom.yaml を空文書にする(対象 0 件・上流の 30-ebom は実現を要する品目を持つ) | acceptance | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +8 | error R-003 +8, info R-005 +31, info R-050 +1, warn X-TYPE-001 +1 |
| A7-dangling-ref | 32-mbom の ebom_refs の 1 件を存在しない ID へ(既知の違反) | always | RED | 1 | 一致 | +1 | error R-003 +1 |
| A7-dangling-ref | 32-mbom の ebom_refs の 1 件を存在しない ID へ(既知の違反) | acceptance | RED | 1 | 一致 | +1 | error R-003 +1 |
| A8-ab-fail-row | 50-as-built の最後の result: pass を result: fail へ(既知の違反・R-050 は acceptance ゲートの規則) | always | PASS | 0 | 一致 | +0 | 差なし |
| A8-ab-fail-row | 50-as-built の最後の result: pass を result: fail へ(既知の違反・R-050 は acceptance ゲートの規則) | acceptance | RED | 1 | 一致 | +1 | error R-050 +1 |

## 土台 minimal

| arm | 壊したもの | ゲート | 期待(契約後) | 現行の exit | 現行の読み | error の増分 | 所見の差分 |
|---|---|---|---|---|---|---|---|
| A1-clean | 変異なし(土台) | always | PASS | 0 | 一致 | +0 | 差なし |
| A1-clean | 変異なし(土台) | acceptance | PASS | 0 | 一致 | +0 | 差なし |
| A2-rename-mbom-key | 32-mbom の manufacturing_units を process_units へ改名(キー空振り) | always | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +1 | error R-003 +1 |
| A2-rename-mbom-key | 32-mbom の manufacturing_units を process_units へ改名(キー空振り) | acceptance | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +2 | error R-003 +1, error R-012 +1, info R-050 +1 |
| A3-rename-cp-key | 33-control-plan の characteristics を checks へ改名(キー空振り) | always | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +3 | error R-003 +3, info R-005 +1 |
| A3-rename-cp-key | 33-control-plan の characteristics を checks へ改名(キー空振り) | acceptance | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +3 | error R-003 +3, info R-005 +1 |
| A4-broken-mbom-yaml | 32-mbom.yaml の末尾へ YAML 構文エラーを 1 行足す(読めない入力) | always | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +2 | error R-003 +1, error X-PARSE-001 +1 |
| A4-broken-mbom-yaml | 32-mbom.yaml の末尾へ YAML 構文エラーを 1 行足す(読めない入力) | acceptance | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +3 | error R-003 +1, error R-012 +1, error X-PARSE-001 +1, info R-050 +1 |
| A5-broken-cp-yaml | 33-control-plan.yaml の末尾へ YAML 構文エラーを 1 行足す(読めない入力) | always | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +4 | error R-003 +3, error X-PARSE-001 +1, info R-005 +1 |
| A5-broken-cp-yaml | 33-control-plan.yaml の末尾へ YAML 構文エラーを 1 行足す(読めない入力) | acceptance | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +4 | error R-003 +3, error X-PARSE-001 +1, info R-005 +1 |
| A6-empty-mbom | 32-mbom.yaml を空文書にする(対象 0 件・上流の 30-ebom は実現を要する品目を持つ) | always | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +1 | error R-003 +1, warn X-TYPE-001 +1 |
| A6-empty-mbom | 32-mbom.yaml を空文書にする(対象 0 件・上流の 30-ebom は実現を要する品目を持つ) | acceptance | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +2 | error R-003 +1, error R-012 +1, info R-050 +1, warn X-TYPE-001 +1 |
| A7-dangling-ref | 32-mbom の ebom_refs の 1 件を存在しない ID へ(既知の違反) | always | RED | 1 | 一致 | +1 | error R-003 +1 |
| A7-dangling-ref | 32-mbom の ebom_refs の 1 件を存在しない ID へ(既知の違反) | acceptance | RED | 1 | 一致 | +2 | error R-003 +1, error R-012 +1 |
| A8-ab-fail-row | 50-as-built の最後の result: pass を result: fail へ(既知の違反・R-050 は acceptance ゲートの規則) | always | PASS | 0 | 一致 | +0 | 差なし |
| A8-ab-fail-row | 50-as-built の最後の result: pass を result: fail へ(既知の違反・R-050 は acceptance ゲートの規則) | acceptance | RED | 1 | 一致 | +2 | error R-050 +2 |
| A1b-clean-unreferenced | 33 の verifies から M ID の参照を外した変種(M ID を他ファイルが参照しない構成・変異なし) | always | PASS | 0 | 一致 | +0 | info R-005 +1 |
| A1b-clean-unreferenced | 33 の verifies から M ID の参照を外した変種(M ID を他ファイルが参照しない構成・変異なし) | acceptance | PASS | 0 | 一致 | +0 | info R-005 +1 |
| A9-rename-mbom-key-unreferenced | A1b の 32-mbom の manufacturing_units を process_units へ改名(M ID の被参照なし) | always | MEASUREMENT_FAILURE | 0 | **FALSE-PASS**(測定不能が無音で緑) | +0 | info R-005 -1 |
| A9-rename-mbom-key-unreferenced | A1b の 32-mbom の manufacturing_units を process_units へ改名(M ID の被参照なし) | acceptance | MEASUREMENT_FAILURE | 1 | 混在(測定不能が違反と同じ error) | +1 | error R-012 +1, info R-005 -1, info R-050 +1 |

## 集計(期待= MEASUREMENT_FAILURE の arm。plm-self は 5 件・minimal は 6 件〔A9 を含む〕)

| 土台 | ゲート | 無音で緑(FALSE-PASS) | 違反と混在(exit 1) | ツール失敗(exit 2) | 混在した arm の error 増分 |
|---|---|---|---|---|---|
| plm-self | always | 0/5 | 5/5 | 0/5 | +8, +158, +9, +159, +8 |
| plm-self | acceptance | 0/5 | 5/5 | 0/5 | +8, +158, +9, +159, +8 |
| minimal | always | 1/6 | 5/6 | 0/6 | +1, +3, +2, +4, +1, +0 |
| minimal | acceptance | 0/6 | 6/6 | 0/6 | +2, +3, +3, +4, +2, +1 |

読み方: 契約が成立していれば、MEASUREMENT_FAILURE の arm は PASS とも RED とも区別できる出力になる。
「無音で緑」は測れていないことを合格と区別できない状態、「違反と混在」は不良を見つけたのか測れなかったのかが出力から分からない状態。
