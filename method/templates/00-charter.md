# Charter — <プロジェクト名>

<!-- 固定の強さ(phase0-charter.md):
     工場構成・予算・役割・境界種別 = この時点で固定(以後不変)
     題材・スコープ = 仮置き可。`(仮)` を付け、Phase 1 終了時(G1)に確定 -->

## 題材
- 何を作るか(1〜3行):
- 種別: CLI / Web-API / GUI / ライブラリ / イベント駆動 / その他
- 黒箱境界: wire(HTTP) / in-process(観測契約が必要) / GUI(golden+承認者が必要)

## スコープ
- 含む:
- 含まない(理由付き):

## 工場構成(受入経済性 — playbook §5.2)
- ティア: 最小(1工場) / 推奨(初回2–3工場→収束後1工場) / 研究(全ループ多工場)
- 使用モデル:
- 収束ループ予算(回数上限):

## 役割
- 設計者(ユーザー+設計AI):
- 仕様監査リーダー数(G2):
- 承認者(知覚・golden がある場合は必須):

## 完了の定義
- 固定オラクル全通過(=現固定オラクル被覆で未観測差分ゼロ)
- blocker ずるゼロ
- 納品物: 成果物 + bomdd/ 一式(BOM・オラクル・治具・As-Built・cheat-log)

## 標準成果物パス
<!-- 新規プロジェクトでは、まずこの一覧を作成予定として PLM に見せる。
     不要なものは削除せず not-applicable と理由を書く。 -->
- `bomdd/00-charter.md`
- `bomdd/10-requirements.yaml`
- `bomdd/20-spec.md`
- `bomdd/ui/mock/`
- `bomdd/ui/**/ui-ir.json`
- `bomdd/ui/**/ui-bom.json`
- `bomdd/ui/**/ui-trace-map.json`
- `bomdd/db/`
- `bomdd/30-ebom.yaml`
- `bomdd/31-kbom.yaml`
- `bomdd/32-mbom.yaml`
- `bomdd/33-control-plan.yaml`
- `bomdd/34-routing.yaml`
- `bomdd/35-design-system-bom.yaml`(UI-CAD 案件のみ必須。非UI案件は not-applicable)
- `bomdd/40-work-order.md`
- `bomdd/50-as-built.yaml`
- `bomdd/53-service-bom.yaml`
- `bomdd/plm-intake/`

## 実装開始 Gate
<!-- AI はこの Gate が通るまで実装を始めない。 -->
| Gate | 判定 | 証跡 |
|---|---|---|
| G0 Charter | pass / fail | 固定項目完備+完了の定義(phase0-charter.md)。前提として Intake(人間が最初に配置した資料一覧)を含む |
| G1 Requirements | pass / fail | `10-requirements.yaml` |
| G2 Spec | pass / fail | `20-spec.md` |
| G2' Measurement | pass / fail | `33-control-plan.yaml` |
| G3 BOM dry run | pass / fail | ドライラン質問リストと補正記録(記録先: `bomdd/plm-intake/00-index.md` 推奨) |
| PLM Gate | pass / fail | PLM sync result(bomdd-lint が無い環境は **PLM-lite** — plm-ready-contract §12.5 で代替し、その旨をここに明記) |

## PLM 同期方針
- 初回同期タイミング: `00/10/20` 作成後
- 製造前同期タイミング: `30-34/40` 作成後
- 指摘の修復先: `bomdd/plm-intake/00-index.md` と `bomdd/plm-intake/{CandidateNo}.md`
- stop finding がある場合: 実装開始しない

## 未解決事項
<!-- 推測で埋めず、質問として残す。blocker は Gate を止める。 -->
| ID | Question | Severity | Owner | Target artifact | Status |
|---|---|---|---|---|---|
| UQ-001 | <最初に人間へ確認すること> | blocker / non-blocker | human / AI | 10 / 20 / 30 / 31 / 32 / 33 | open |
