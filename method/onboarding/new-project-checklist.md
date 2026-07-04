# 新規プロジェクト開始チェックリスト

> **スキャフォールド**: リポ骨格(bomdd/ テンプレ・CLAUDE.md・スキル・CAD リポ)は
> `python method/tools/bomdd-init.py <Product> --dir <親dir> [--gui]` で生成できる。
> 人間の協働作法は [working-with-ai.md](working-with-ai.md)、通しの流れの実例は
> [example-session-log.md](example-session-log.md)(スキャフォールド→Phase 0-5→納品→ECO の模擬ログ)。

このチェックリストは、`bomdd/` を作り始める前後に人間と AI が一緒に埋める。未確定項目は空欄にせず、`unknown`、`not-applicable`、`unresolved` のいずれかで明示する。

既存実装や既存 `bomdd/` を持つプロジェクトは、このチェックリストではなく [migration-checklist.md](migration-checklist.md) を使う。

## 1. 入力資料

| 問い | 状態 | 置き場所 / メモ |
|---|---|---|
| 仕様書はあるか | yes / no / partial | `bomdd/plm-intake/` または `bomdd/20-spec.md` |
| GUI アプリか | yes / no | yes の場合は UI Gate が必須 |
| UI/UX モックはあるか | yes / no / partial | `bomdd/ui/mock/` |
| DB/永続化はあるか | yes / no / unknown | `bomdd/db/schema-intent.md`、`bomdd/db/ddl/` |
| 外部依存はあるか | yes / no / unknown | `31-kbom.yaml`、`32-mbom.yaml procurement` |
| テスト方針はあるか | yes / no / partial | `33-control-plan.yaml` |
| リリース/配布形態はあるか | yes / no / unknown | `00-charter.md`、`53-service-bom.yaml` |
| 保守対象は何か | defined / unknown | 外部知識、依存、データ、AI モデル、UI デザイン |

## 2. 人間が最初に配置すべきファイル

| 優先度 | ファイル | 標準配置 | 備考 |
|---|---|---|---|
| 必須 | 既存仕様、要件メモ、チケット export | `bomdd/plm-intake/` | 正とする資料を明記する |
| GUI の場合必須 | UI モック、スクリーンショット、Figma export、HTML mock | `bomdd/ui/mock/` | 画面名、状態名、承認者を添える |
| DB の場合必須 | DDL、ERD、schema メモ、migration 方針 | `bomdd/db/` | 既存データ保持要件を分ける |
| ある場合 | 既存テスト、受入条件、運用手順 | `bomdd/plm-intake/` | Control Plan の種にする |
| ある場合 | 外部 API docs、ライブラリ制約、デザインシステム | `bomdd/plm-intake/` | K-BOM の種にする |

## 3. AI が最初に生成すべき成果物

順序を守る。実装ファイルはこの段階で生成しない。

1. `bomdd/00-charter.md`
2. `bomdd/10-requirements.yaml`
3. `bomdd/20-spec.md`
4. GUI の場合: `bomdd/ui/<screen-or-flow>/ui-ir.json`
5. GUI の場合: `bomdd/ui/<screen-or-flow>/ui-bom.json`
6. GUI の場合: `bomdd/ui/<screen-or-flow>/ui-trace-map.json`
7. DB の場合: `bomdd/db/schema-intent.md`
8. `bomdd/30-ebom.yaml`
9. `bomdd/31-kbom.yaml`
10. `bomdd/32-mbom.yaml`
11. `bomdd/33-control-plan.yaml`
12. `bomdd/34-routing.yaml`
13. UI-CAD の場合: `bomdd/35-design-system-bom.yaml`
14. `bomdd/40-work-order.md`

## 4. PLM 同期前のセルフチェック

| 確認 | 合否 |
|---|---|
| 全 REQ が `REQ-*` ID を持つ | pass / fail |
| 仕様節から REQ へ戻れる | pass / fail |
| UI 要素がある場合、表示契約または out-of-scope 理由がある | pass / fail |
| DB がある場合、entity、field、lifecycle、migration 方針がある | pass / fail |
| UI-CAD の場合、`35-design-system-bom.yaml` があり required design parts が固定されている | pass / fail |
| E-BOM item が `requirement_refs` または `kbom_refs` を持つ | pass / fail |
| M-BOM unit が `ebom_refs` と `output_artifact_ref` を持つ | pass / fail |
| Control Plan が各 M-BOM unit を検査する | pass / fail |
| `depends_on` が存在する場合、相手 ID が実在する | pass / fail |
| 未解決事項が `unresolved_questions` に集約されている | pass / fail |

## 5. PLM 同期後に確認すべきこと

| PLM 指摘 | 人間/AI の処理 |
|---|---|
| 足りない成果物 | 該当テンプレを作成し、参照元を追記する |
| 粗すぎる BOM | `bom-granularity-guide.md` に従い分割する |
| 粒度不整合 | E-BOM、M-BOM、Control Plan の単位を揃える |
| トレース切れ | `traceability-rules.md` に従い TraceLink を修復する |
| PLM-ready 契約違反 | `plm-ready-contract.md` の必須フィールドを埋める |
| 実装停止状態 | 実装へ進まず、`bomdd/plm-intake/00-index.md` と `bomdd/plm-intake/{CandidateNo}.md` へ積む |

## 6. 実装開始判定

実装開始は、次をすべて満たした後に限る。

- G1: 要求の根拠精度が adequate、または未解決が blocker ではない。
- G2: 仕様が一意に読める。UI/DB の入口情報が仕様へ接続済み。
- G2': 測定できない REQ がない。人間承認が必要なものは承認者がいる。
- G3: BOM 自己完結性ドライランで blocker 質問がない。
- PLM: stop 状態がない。warning は `plm-intake/00-index.md` と個別作業票にあり、裁定済み。
