# 既存プロジェクト移行チェックリスト

このチェックリストは、既存プロジェクトを新しい BomDD 方法論へ移行するときに、人間と AI が一緒に埋める。

## 1. 移行モードの確認

| 問い | 状態 | メモ |
|---|---|---|
| 移行中に実装を変更しない合意があるか | yes / no | no の場合は移行を開始しない |
| 既存 `bomdd/` はあるか | yes / no / partial | ある場合は旧成果物として棚卸し |
| 既存仕様はあるか | yes / no / partial | 正とする資料を指定 |
| 既存 UI/UX 資料はあるか | yes / no / partial | GUI の場合は必須 |
| 既存 DB/永続化資料はあるか | yes / no / partial | DB がある場合は必須 |
| 既存テスト/CI/受入証跡はあるか | yes / no / partial | As-Built seed に使う |
| 既存依存/障害/運用資料はあるか | yes / no / partial | Service BOM に使う |

## 2. 最初に作る移行成果物

| 成果物 | 必須 | 状態 |
|---|---|---|
| `bomdd/plm-intake/migration-inventory.md` | yes | todo / done |
| `bomdd/plm-intake/source-map.md` | yes | todo / done |
| `bomdd/plm-intake/00-index.md` | yes | todo / done |
| `bomdd/plm-intake/{CandidateNo}.md` | PLM 指摘がある場合 yes | todo / done |

## 3. 既存資料の対応付け

| 既存資料 | 移行先 | 処理 | 状態 |
|---|---|---|---|
| 仕様/README/設計メモ | `10-requirements.yaml` / `20-spec.md` | reference / summarize / split | todo / done |
| UI モック/スクリーンショット | `bomdd/ui/mock/` | reference / copy | todo / done |
| UI 抽出結果 | `bomdd/ui/<screen-or-flow>/` | generate | todo / done |
| DB DDL/migration | `bomdd/db/` | reference / copy / summarize | todo / done |
| 既存実装 | `30/32` | reference | todo / done |
| 外部依存 | `31/32/53` | summarize | todo / done |
| 既存テスト/CI | `33/50` | map | todo / done |
| 障害/運用履歴 | `53` | summarize | todo / done |

## 4. 標準成果物の充足

| パス | 状態 | 備考 |
|---|---|---|
| `bomdd/00-charter.md` | present / missing / not-applicable | 移行方針と freeze を明記 |
| `bomdd/10-requirements.yaml` | present / missing | 既存仕様から REQ 化 |
| `bomdd/20-spec.md` | present / missing | source_ref を残す |
| `bomdd/ui/mock/` | present / missing / not-applicable | GUI の場合 present |
| `bomdd/ui/**/ui-ir.json` | present / missing / not-applicable | GUI の場合 present |
| `bomdd/ui/**/ui-bom.json` | present / missing / not-applicable | GUI の場合 present |
| `bomdd/ui/**/ui-trace-map.json` | present / missing / not-applicable | GUI の場合 present |
| `bomdd/db/schema-intent.md` | present / missing / not-applicable | DB がある場合 present |
| `bomdd/30-ebom.yaml` | present / missing | |
| `bomdd/31-kbom.yaml` | present / missing | |
| `bomdd/32-mbom.yaml` | present / missing | |
| `bomdd/33-control-plan.yaml` | present / missing | |
| `bomdd/34-routing.yaml` | present / missing | |
| `bomdd/35-design-system-bom.yaml` | present / missing / not-applicable | UI-CAD の場合 present |
| `bomdd/40-work-order.md` | present / missing | 移行中は製造しない場合 draft |
| `bomdd/50-as-built.yaml` | present / missing | 既存実装を seed として記録 |
| `bomdd/53-service-bom.yaml` | present / missing / not-applicable | 保守対象がある場合 present |

## 5. PLM 同期後チェック

| 確認 | 合否 |
|---|---|
| stop finding が 0 | pass / fail |
| warning が `00-index.md` と個別作業票で裁定済み | pass / fail |
| 作業票 status が PLM 語彙のみ | pass / fail |
| REQ -> Spec -> E-BOM -> M-BOM -> Control Plan が到達可能 | pass / fail |
| 既存テストが Control Plan と As-Built に接続済み | pass / fail |
| 既存依存が K-BOM / procurement / Service BOM に接続済み | pass / fail |
| unresolved question が blocker / non-blocker に分類済み | pass / fail |

## 6. 実装変更へ進める条件

移行完了後、実装変更へ進むには次を満たす。

- M0-M5 Gate が pass。
- 既存実装の As-Built seed がある。
- 実装変更の目的が `60-change-order.md` または CAPA として書かれている。
- 影響分析 `61-impact-analysis.md` がある。
- 変更用 Control Plan が先に更新されている。
- 製造 AI へ渡す Work Order が移行作業ではなく変更/是正作業として明記されている。

## 7. 技術移行シナリオを続行する場合

BomDD 導入移行の完了後、C#/.NET + WPF へ再実装し既存 RDB を継続利用する場合だけ、[legacy-to-wpf-rdb 専用キット](../scenarios/legacy-to-wpf-rdb/README.md)を明示的に有効化する。通常の新規開発では有効化しない。
