# ECO-089 製造後の受入 V1・V4 の観測

- 測定日: 2026-10-01・対象= `method/schemas/draft/ref-edges.draft.yaml`
- V4 の計器= BomDD-Plm `d02052b`(clean)の bomdd-lint。同梱スキーマ= ref-v0.11(`schemas/ref-v0`)・比較は diagnostics.json から refSchema(版の表記)を除いた内容と終了コード。

## V1(スキーマ本体の構造を YAML 解析で読む)

| 観測項目 | 結果 | 詳細 |
|---|---|---|
| edges_version が ref-v0.12 | 一致 | ref-v0.12 |
| measurability 節がある | 一致 |  |
| 4 状態 | 一致 | ['PASS', 'RED', 'MEASUREMENT_FAILURE', 'NOT_APPLICABLE'] |
| 原因の閉語彙 4 つ | 一致 |  |
| pass_rule がある | 一致 |  |
| zero_target_rule がある | 一致 |  |
| boundary_rule がある | 一致 |  |
| output_rule がある | 一致 |  |
| 上流宣言の対象が R-011・R-012・R-014・R-050 | 一致 | ['R-011', 'R-012', 'R-014', 'R-050'] |
| 各上流宣言が reads・expectation_source・on_empty を持つ | 一致 |  |
| deferred に cascade-attribution と exit-code-value | 一致 | ['cascade-attribution', 'exit-code-value'] |
| lint_rules が 19 規則 | 一致 | 19 |
| R-050 の gate=acceptance・severity=error が不変 | 一致 |  |
| R-050 (d) が上流の宣言を参照 | 一致 |  |
| R-050 note の『所見なし』の定義(抑止・支持すること・支持しないこと)が不変 | 一致 |  |
| R-011 の note が measurability を参照 | 一致 |  |
| R-012 の note が measurability を参照 | 一致 |  |
| R-014 の note が measurability を参照 | 一致 |  |

## V4(改訂後スキーマの直指定で、現行実装の出力が同梱スキーマの出力と同一か)

制御= 同梱スキーマの複製を --schema で指定した出力が、既定の同梱と同一であること(比較手順そのものの健全性)。

| 土台 | arm | ゲート | exit | 制御(同梱の複製)が同一 | 改訂後スキーマが同一 |
|---|---|---|---|---|---|
| plm-self | A1-clean | always | 0 | 同一 | 同一 |
| plm-self | A1-clean | acceptance | 0 | 同一 | 同一 |
| plm-self | A2-rename-mbom-key | always | 1 | 同一 | 同一 |
| plm-self | A2-rename-mbom-key | acceptance | 1 | 同一 | 同一 |
| plm-self | A6-empty-mbom | always | 1 | 同一 | 同一 |
| plm-self | A6-empty-mbom | acceptance | 1 | 同一 | 同一 |
| plm-self | A7-dangling-ref | always | 1 | 同一 | 同一 |
| plm-self | A7-dangling-ref | acceptance | 1 | 同一 | 同一 |
| plm-self | A8-ab-fail-row | always | 0 | 同一 | 同一 |
| plm-self | A8-ab-fail-row | acceptance | 1 | 同一 | 同一 |
| minimal | A1-clean | always | 0 | 同一 | 同一 |
| minimal | A1-clean | acceptance | 0 | 同一 | 同一 |
| minimal | A2-rename-mbom-key | always | 1 | 同一 | 同一 |
| minimal | A2-rename-mbom-key | acceptance | 1 | 同一 | 同一 |
| minimal | A6-empty-mbom | always | 1 | 同一 | 同一 |
| minimal | A6-empty-mbom | acceptance | 1 | 同一 | 同一 |
| minimal | A7-dangling-ref | always | 1 | 同一 | 同一 |
| minimal | A7-dangling-ref | acceptance | 1 | 同一 | 同一 |
| minimal | A8-ab-fail-row | always | 0 | 同一 | 同一 |
| minimal | A8-ab-fail-row | acceptance | 1 | 同一 | 同一 |
| minimal | A1b-clean-unreferenced | always | 0 | 同一 | 同一 |
| minimal | A1b-clean-unreferenced | acceptance | 0 | 同一 | 同一 |
| minimal | A9-rename-mbom-key-unreferenced | always | 0 | 同一 | 同一 |
| minimal | A9-rename-mbom-key-unreferenced | acceptance | 1 | 同一 | 同一 |

陽性対照(比較が差を検出できること)= R-012 の gate を G3→always に変えた変種を minimal の A2(acceptance)へ当てると、出力が**差あり**(検出できた)(exit 1→1)。
参考(副次の観測)= 同じ手順で R-012 の severity を error→warn に変えた変種は、出力が**同一**(exit 1→1) — この規則・この arm では実装は schema の severity を読まず、所見の severity を自身で持つ(他の規則は未確認)。severity の変更では比較の感度を測れない

集計: V1 18/18 項目一致・V4 24/24 組同一(標本 24 組)。
限界: V4 の標本は私の設計した arms(2 土台)で、実在リポの全数ではない。比較は diagnostics.json の内容と終了コードまで(text 出力・sarif は見ていない)。
