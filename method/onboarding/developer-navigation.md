# 開発者向けナビゲーション

> **本書で頻出する BOM-DD PLM とは**: 台帳のつながり(仕様↔BOM↔検査↔変更)を機械検査する装置。指摘は `bomdd/plm-intake/` に作業票として届く。
> **人間は直接操作しない** — 設計者 AI に「PLM で同期して」と依頼し、届いた指摘(CAND-xxx)の裁定だけを行う。

この文書は、人間の開発者が「何をどこに置き、AI に何を渡し、いつ PLM で同期するか」を迷わないためのナビゲーションである。

既存プロジェクトを新しい BomDD 方法論へ移行する場合は、まず [existing-project-migration.md](existing-project-migration.md) と [migration-checklist.md](migration-checklist.md) を使い、実装変更を始める前に棚卸し、source map、PLM 作業票を揃える。

## 1. 仕様書をどこに置くか

- 原典資料、チケット、メモ、議事録は `bomdd/plm-intake/` に置く。
- BomDD 仕様として昇格したものは `bomdd/20-spec.md` に置く。
- 仕様の各節は `REQ-*` を明記する。
- 未確定の仕様は本文で確定させず、`unresolved questions` に残す。

推奨:

```text
bomdd/plm-intake/source-spec-v0.md
bomdd/plm-intake/user-interview-notes.md
bomdd/20-spec.md
```

## 2. UI/UX モックをどこに置くか

- 人間が作ったモック、スクリーンショット、Figma export、HTML mock は `bomdd/ui/mock/` に置く。
- AI が抽出した UI-IR、UI-BOM、trace map は `bomdd/ui/<screen-or-flow>/` に置く。
- UI 表示要素は `20-spec.md` の表示契約、`30-ebom.yaml` の display contract、`33-control-plan.yaml` の表示パリティ行へ接続する。

推奨:

```text
bomdd/ui/mock/checkout.html
bomdd/ui/mock/checkout-empty.png
bomdd/ui/checkout/ui-ir.json
bomdd/ui/checkout/ui-bom.json
bomdd/ui/checkout/ui-trace-map.json
```

## 3. DB DDL / schema intent をどこに置くか

- DB の意図は最初に `bomdd/db/schema-intent.md` に書く。
- 既存 DDL は `bomdd/db/ddl/` に置く。
- 移行方針、既存データ保持、migration fixture は `bomdd/db/migrations/` に置く。
- DB entity と field は `REQ-*`、E-BOM、M-BOM、Control Plan へ接続する。

推奨:

```text
bomdd/db/schema-intent.md
bomdd/db/ddl/initial.sql
bomdd/db/migrations/001-membership-tier.md
```

## 4. AI へ何を渡すか

設計 AI へ渡す:

- `bomdd/plm-intake/` の原典資料
- 人間が置いた UI/DB 資料
- 既存の `bomdd/` 成果物
- このオンボーディングパック
- `method/contracts/` の契約文書

製造 AI へ渡す:

- `bomdd/20-spec.md`
- `bomdd/30-ebom.yaml`
- `bomdd/31-kbom.yaml`
- `bomdd/32-mbom.yaml`
- `bomdd/33-control-plan.yaml`
- `bomdd/34-routing.yaml`
- UI-CAD 案件では `bomdd/35-design-system-bom.yaml`
- `bomdd/40-work-order.md`
- in-process 題材のみ観測契約

製造 AI へ渡さない:

- 仕様策定の会話履歴
- 固定オラクルの期待値
- 探索プローブ
- 他工場の成果
- PLM repair queue の裁定前メモ

## 5. いつ BOM-DD PLM で同期するか

| タイミング | 目的 |
|---|---|
| `00/10/20` 作成後 | 仕様、REQ、UI/DB 入口の不足を検出する |
| `30-34` 作成後(UI-CAD 案件は `35` も含む) | BOM 粒度、必須フィールド、TraceLink、PLM-ready 契約を検査する |
| G3 ドライラン前 | 製造開始を止めるべき契約違反を先に消す |
| 製造後 | As-Built、test evidence、cheat、artifact hash を接続する |
| 変更/是正時 | 影響分析、Control Plan 更新、Service BOM 逆引きを検査する |

## 6. PLM の指摘をどう修復キューにするか

PLM 指摘は、BOM-DD PLM の実装に合わせて `bomdd/plm-intake/00-index.md` と `bomdd/plm-intake/{CandidateNo}.md` の個別 Markdown 作業票で管理する。ViewPrism2 側 AI や PLM は、個別作業票の `status` を追跡する。

`status` は PLM が認識する語彙に限定する: `proposed` / `assigned` / `applied` / `verified` / `rejected` / `not-exported`。

標準配置:

```text
bomdd/plm-intake/
  00-index.md
  CAND-001.md
  CAND-002.md
  sync-results/
```

`00-index.md` の例:

```markdown
## PLM Intake Index

| CandidateNo | PLM finding | severity | owner | target ticket | status |
|---|---|---|---|---|---|
| CAND-001 | E-BOOKING-001 lacks acceptance_refs | stop | AI | `bomdd/plm-intake/CAND-001.md` | proposed |
```

個別作業票 `bomdd/plm-intake/CAND-001.md` の例:

```markdown
# CAND-001 - E-BOOKING-001 lacks acceptance_refs

status: proposed
severity: stop
owner: AI
target_artifacts:
- bomdd/30-ebom.yaml
- bomdd/33-control-plan.yaml

## Finding
E-BOOKING-001 lacks acceptance_refs.

## Required action
Add CP-BOOKING-001 and a TraceLink, then update this ticket status.

## Resolution
- status: applied / verified / rejected / not-exported
- evidence:
```

修復先の原則:

- 要求の欠落: `10-requirements.yaml`
- 仕様の曖昧さ: `20-spec.md`
- UI 表示欠落: `20-spec.md`、`30-ebom.yaml`、`33-control-plan.yaml`
- DB 粒度欠落: `db/schema-intent.md`、`30-ebom.yaml`、`32-mbom.yaml`
- 外部知識欠落: `31-kbom.yaml`
- 製造単位不明: `32-mbom.yaml`
- 検査不足: `33-control-plan.yaml`
- 工程不明: `34-routing.yaml`
- 製造指示不明: `40-work-order.md`
- 来歴不足: `50-as-built.yaml`
- 保守逆引き不足: `53-service-bom.yaml`

## 7. 実装開始前に通す Gate

実装開始前に、次の Gate を通す。

| Gate | 通過条件 |
|---|---|
| G0 Intake | 人間が正とする資料の置き場所が明示されている |
| G1 Requirements | 全 REQ が根拠、分類、受入意図を持つ |
| G2 Spec | 仕様節、UI 表示契約、DB 意図、不変条件が REQ へ接続されている |
| G2' Measurement | 測定不能な REQ がない。G depth は承認者がいる |
| G3 BOM Dry Run | fresh AI が製造パッケージだけで着手可能。blocker 質問がない |
| PLM Gate | stop finding が 0。warning は `plm-intake/00-index.md` と個別作業票で裁定済み |

Gate を通らない場合、AI は実装を始めない。修復キューを処理し、必要な成果物へ逆流してから再同期する。
