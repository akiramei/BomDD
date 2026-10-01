# ECO-089 延長 1 周 — 連鎖所見の帰属(契約 5)が実装できるかの実測

- 測定日: 2026-10-01・計器= BomDD-Plm `d02052b` の bomdd-lint(受入ゲート・graph.json と diagnostics.json を入力)
- 規則: 未解決の参照先の族に定義ノードが 1 件も無い → 「測定不能の連鎖」/ 1 件以上ある → 「違反」。検査器は変えず、出力への後処理だけ。
  C-b= graph.json の未解決参照すべて(粗い版)/ C-b'= R-003 の severity=error の所見だけ(厳格ファミリーに自動で絞られる)。
- 限界: 族は参照先 ID の先頭節で判定(id-grammar を読まない近似)。arms は私の設計した変異。コーパスの帰属の正しさは人が読んで判定する(自動判定ではない)。

## (1) arms: 連鎖は測定不能へ・本物の違反は違反へ分かれるか

| 土台 | arm | 期待 | C-b 未解決 | C-b 測定不能へ | C-b 違反へ | C-b 読み | C-b' 対象(R-003 error) | C-b' 測定不能へ | C-b' 違反へ | C-b' 読み |
|---|---|---|---|---|---|---|---|---|---|---|
| plm-self | A1-clean | PASS | 0 | 0 | 0 | 未解決なし | 0 | 0 | 0 | 未解決なし |
| plm-self | A2-rename-mbom-key | MEASUREMENT_FAILURE | 33 | 33 | 0 | 全て測定不能の連鎖へ | 8 | 8 | 0 | 全て測定不能の連鎖へ |
| plm-self | A3-rename-cp-key | MEASUREMENT_FAILURE | 165 | 165 | 0 | 全て測定不能の連鎖へ | 158 | 158 | 0 | 全て測定不能の連鎖へ |
| plm-self | A4-broken-mbom-yaml | MEASUREMENT_FAILURE | 33 | 33 | 0 | 全て測定不能の連鎖へ | 8 | 8 | 0 | 全て測定不能の連鎖へ |
| plm-self | A5-broken-cp-yaml | MEASUREMENT_FAILURE | 176 | 176 | 0 | 全て測定不能の連鎖へ | 158 | 158 | 0 | 全て測定不能の連鎖へ |
| plm-self | A6-empty-mbom | MEASUREMENT_FAILURE | 33 | 33 | 0 | 全て測定不能の連鎖へ | 8 | 8 | 0 | 全て測定不能の連鎖へ |
| plm-self | A7-dangling-ref | RED | 1 | 0 | 1 | 違反へ | 1 | 0 | 1 | 違反へ |
| plm-self | A8-ab-fail-row | RED | 0 | 0 | 0 | 該当参照なし(別規則で RED) | 0 | 0 | 0 | 該当参照なし(別規則で RED) |
| minimal | A1-clean | PASS | 0 | 0 | 0 | 未解決なし | 0 | 0 | 0 | 未解決なし |
| minimal | A2-rename-mbom-key | MEASUREMENT_FAILURE | 1 | 1 | 0 | 全て測定不能の連鎖へ | 1 | 1 | 0 | 全て測定不能の連鎖へ |
| minimal | A3-rename-cp-key | MEASUREMENT_FAILURE | 3 | 3 | 0 | 全て測定不能の連鎖へ | 3 | 3 | 0 | 全て測定不能の連鎖へ |
| minimal | A4-broken-mbom-yaml | MEASUREMENT_FAILURE | 1 | 1 | 0 | 全て測定不能の連鎖へ | 1 | 1 | 0 | 全て測定不能の連鎖へ |
| minimal | A5-broken-cp-yaml | MEASUREMENT_FAILURE | 3 | 3 | 0 | 全て測定不能の連鎖へ | 3 | 3 | 0 | 全て測定不能の連鎖へ |
| minimal | A6-empty-mbom | MEASUREMENT_FAILURE | 1 | 1 | 0 | 全て測定不能の連鎖へ | 1 | 1 | 0 | 全て測定不能の連鎖へ |
| minimal | A7-dangling-ref | RED | 1 | 0 | 1 | 違反へ | 1 | 0 | 1 | 違反へ |
| minimal | A8-ab-fail-row | RED | 0 | 0 | 0 | 該当参照なし(別規則で RED) | 0 | 0 | 0 | 該当参照なし(別規則で RED) |
| minimal | A1b-clean-unreferenced | PASS | 0 | 0 | 0 | 未解決なし | 0 | 0 | 0 | 未解決なし |
| minimal | A9-rename-mbom-key-unreferenced | MEASUREMENT_FAILURE | 0 | 0 | 0 | 対象 0 件 — 捕まらない | 0 | 0 | 0 | 対象 0 件 — 捕まらない |

## (2) 実在リポ(コーパス): 規則を当てたとき測定不能の連鎖へ回る参照

| リポ | 入力 | exit | C-b 未解決 | C-b 測定不能へ | C-b 違反へ | C-b' 対象(R-003 error) | C-b' 測定不能へ | C-b' 違反へ | C-b' で測定不能へ回る族(定義数・件数・例) |
|---|---|---|---|---|---|---|---|---|---|
| BomDD-Plm | BomDD-Plm | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — |
| BomDD-UnitConv-Sample | BomDD-UnitConv-Sample | 1 | 116 | 113 | 3 | 86 | 86 | 0 | CP(定義 0・59 件・例 CP-CATEGORY-001, CP-CONVERT-001, CP-EXITCODES 空単位); INV(定義 0・9 件・例 INV-001 -0 なし, INV-001 6 桁, INV-001 指数表記なし(非開示)); K(定義 0・8 件・例 K-DOTNET-CLI-001, K-XUNIT-001); REQ(定義 0・10 件・例 REQ-001, REQ-002, REQ-003) |
| BomDD-LibraryLending-Sample | BomDD-LibraryLending-Sample | 1 | 44 | 41 | 3 | 41 | 41 | 0 | CP(定義 0・16 件・例 CP-API-CONTRACT-001, CP-API-DATETIME-001, CP-CORE-AVAIL-001); E(定義 0・14 件・例 E-BOOK-INVENTORY-001, E-DATETIME-POLICY-001, E-DUE-FINE-001); INV(定義 0・2 件・例 INV-3(>のみ), INV-5(rev2)); K(定義 0・6 件・例 K-ERROR-SCHEMA-001, K-HTTP-REST-001, K-ID-001); None(定義 0・3 件・例 v0.4-forward-02(factory-eco2-01-opus), v0.6-forward-04(factory-eco5-01-sonnet)) |
| ViewTube | bomdd-workspace.yaml | 1 | 100 | 16 | 84 | 98 | 14 | 84 | CAPA(定義 0・3 件・例 CAPA-VT-001); ECO(定義 0・8 件・例 ECO-VT-025, ECO-VT-054, ECO-VT-055); None(定義 0・3 件・例 ScopedCollectionDeletion, ScopedEntityBadge, ViewPackWorkflow) |
| ViewPrism2 | bomdd-workspace.yaml | 1 | 0 | 0 | 0 | 0 | 0 | 0 | — |
| BomDD-Transfer03 | BomDD-Transfer03 | 1 | 91 | 83 | 8 | 78 | 70 | 8 | K(定義 0・20 件・例 K-CSV-001, K-DOTNET-001, K-FILESTORE-001); REQ(定義 0・50 件・例 REQ-001, REQ-002, REQ-003) |
| TimetableAdv | TimetableAdv | 1 | 766 | 332 | 434 | 465 | 53 | 412 | CA(定義 0・4 件・例 CA-ACC-FIX-040, CA-ACC-FIX-041); CORE(定義 0・3 件・例 CORE-V3-CP-AI-ROLE-GATE-001, CORE-V3-CP-CANDIDATE-MUTATION-001); CPS(定義 0・22 件・例 CPS-FACTORY-FINAL-001, CPS-FACTORY-RELOCATION-001); DE(定義 0・2 件・例 DE-UI-ACT-001..024, DE-UI-STATE-001..011); FIXED(定義 0・4 件・例 FIXED-ORACLE-PHASE5-001); None(定義 0・16 件・例 UI:time-reuse-experiment); SIT(定義 0・2 件・例 SIT-CP-HUMAN-002, SIT-CP-HUMAN-003) |

### 粗い版(C-b)で測定不能へ回る族の数(誤帰属の目安)

| リポ | 測定不能へ回る族の数(定義 0・未解決あり) | うち C-b' でも回る族の数 |
|---|---|---|
| BomDD-Plm | 0 | 0 |
| BomDD-UnitConv-Sample | 5 | 4 |
| BomDD-LibraryLending-Sample | 5 | 5 |
| ViewTube | 3 | 3 |
| ViewPrism2 | 0 | 0 |
| BomDD-Transfer03 | 3 | 2 |
| TimetableAdv | 37 | 7 |

### C-b' で測定不能へ回った参照 ID の内訳(族が判定できたか・定義が字面で存在するか)

族が判定できない(先頭節が ID 族の形でない語)は、この規則では帰属を決められない(「帰属不明」)。族が判定できたものは、bomdd/ 配下に `id: <ID>` の字面の定義があるかを数える:
あれば「定義はあるのに検査器の定義サイトが読めていない」= 測定不能の帰属が妥当。無ければ「本当に未定義かもしれない」= 違反か測定不能か曖昧。

| リポ | 測定不能へ回った参照(ID の異なり数) | 帰属不明(族が判定できない) | 族あり | うち字面の定義あり(帰属が妥当) | うち字面の定義なし(曖昧) | 定義なしの族(件数) |
|---|---|---|---|---|---|---|
| BomDD-Plm | 0 | 0 | 0 | 0 | 0 | — |
| BomDD-UnitConv-Sample | 26 | 0 | 26 | 16 | 10 | INV(9), CP(1) |
| BomDD-LibraryLending-Sample | 33 | 2 | 31 | 29 | 2 | INV(2) |
| ViewTube | 12 | 3 | 9 | 8 | 1 | CAPA(1) |
| ViewPrism2 | 0 | 0 | 0 | 0 | 0 | — |
| BomDD-Transfer03 | 14 | 0 | 14 | 14 | 0 | — |
| TimetableAdv | 12 | 1 | 11 | 4 | 7 | CORE(2), DE(2), SIT(2), FIXED(1) |

読み方: (1) は規則が原理的に区別できるかの確認。(2) は実在リポで、定義サイトが散文の族・別リポの族・ID でない語まで「測定不能」と読む誤帰属が出るかの目安。
C-b' で測定不能へ回る族は、定義サイトが本当に読めていない(構文エラー・必須成果物の欠落)のか、方言・別リポの族なのかを人が確かめる。
