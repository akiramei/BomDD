# AI Onboarding Pack - BomDD 新規プロジェクト開始用

この文書は、新規開発プロジェクトの `bomdd/` を作り始める AI に最初に渡す入口パックである。目的は、AI が個体差少なく、仕様、UI、DB、BOM、工程、検査、保守の順で成果物を固め、BOM-DD PLM が読める状態にすること。

既存実装や既存 `bomdd/` を持つプロジェクトを移行する場合は、この文書ではなく [existing-project-migration.md](existing-project-migration.md) を最初に読む。既存プロジェクトでは、まず実装を変更せず棚卸しと PLM-ready 化を行う。

## 1. BomDD 方法論の目的

BomDD は、AI 製造を「会話の勢い」ではなく、PLM で追跡できる成果物群として管理する方法論である。

- 要求を `REQ-*` として台帳化する。
- 仕様を、製造装置と検査器の両方が読める契約にする。
- E-BOM / K-BOM / M-BOM / Control Plan / Routing へ分解する。
- 受入と製造来歴を `As-Built` として残す。
- 保守時は S-BOM / Service BOM から外部知識、依存、AI モデル劣化を逆引きする。

AI の仕事は、実装を急ぐことではなく、実装を始めてもよい状態を作ることである。

## 2. AI が最初に読むべき前提

1. BomDD 方法論は成果物の種類、命名、粒度、必須項目、ID、テンプレート、完了条件、オンボーディング手順を定義する。
2. 開発対象プロジェクトはリポジトリ直下の `bomdd/` に実際の成果物、BOM、工程証跡、テスト証跡を置く。
3. BOM-DD PLM は `bomdd/` を読み、分類し、不足、粗すぎる粒度、粒度不整合、トレース切れ、PLM-ready 契約違反を指摘する。
4. AI は Gate を通すまで実装を始めない。
5. 不明点は推測で埋めず、各成果物の `unresolved_questions` または `unresolved questions` に残す。
6. 製造装置へ渡してよいものは、製造パッケージだけである。設計対話、固定オラクルの期待値、他工場の成果と cheat は渡さない。

## 3. 成果物一覧

| パス | 役割 | PLM が見る主なキー |
|---|---|---|
| `bomdd/00-charter.md` | 目的、境界、工場構成、Gate、承認者 | project, scope, factory, gates |
| `bomdd/10-requirements.yaml` | 要求台帳 | `requirements[].id`, `statement`, `rationale`, `acceptance_intent` |
| `bomdd/20-spec.md` | 仕様書、表示契約、不変条件 | REQ refs, INV refs, UI refs, DB refs |
| `bomdd/ui/mock/` | 人間が置く UI/UX モック | source files, screenshots, notes |
| `bomdd/ui/**/ui-ir.json` | UI 観測中間表現 | `nodes[].id`, `sourceRef`, `traceRefs` |
| `bomdd/ui/**/ui-bom.json` | UI-BOM 候補 | `items[].tempPartNo`, `kind`, `traceRefs` |
| `bomdd/ui/**/ui-trace-map.json` | UI から仕様/BOM への対応 | selector, ui id, ebom ref |
| `bomdd/db/` | DDL、schema intent、ERD、migration intent | entity ids, field ids, persistence rules |
| `bomdd/30-ebom.yaml` | 設計部品表 | `ebom.items[].id`, `requirement_refs`, `acceptance_refs` |
| `bomdd/31-kbom.yaml` | 知識部品表 | `kbom.items[].id`, `source`, `version`, `consumers` |
| `bomdd/32-mbom.yaml` | 製造部品表 | `mbom.manufacturing_units[].id`, `ebom_refs`, `output_artifact_ref` |
| `bomdd/33-control-plan.yaml` | 検査特性と深さ | `control_plan.characteristics[].id`, `depth`, `fixture` |
| `bomdd/34-routing.yaml` | 製造工程 | `routing.steps[].id`, `input`, `output`, `gate` |
| `bomdd/35-design-system-bom.yaml` | UI-CAD 案件のデザインシステム部品表 | required design parts, coverage matrix |
| `bomdd/40-work-order.md` | 製造装置への指示 | allowed inputs, build steps, cheat report |
| `bomdd/50-as-built.yaml` | 製造来歴 | `as_built[].id`, `bom refs`, `artifacts_sha256`, `test_evidence_refs` |
| `bomdd/53-service-bom.yaml` | S-BOM / Service BOM。保守部品表 | `service_bom.items[].id`, `external_deps`, `reinspect_on_change` |
| `bomdd/plm-intake/` | PLM への追加投入、同期ログ、修復キュー | intake manifest, repair queue, sync result |

## 4. 標準フォルダ構成

```text
bomdd/
  00-charter.md
  10-requirements.yaml
  20-spec.md
  ui/
    mock/
    <screen-or-flow>/
      ui-ir.json
      ui-bom.json
      ui-trace-map.json
      extraction-report.md
      unresolved-questions.md
  db/
    schema-intent.md
    ddl/
    migrations/
  30-ebom.yaml
  31-kbom.yaml
  32-mbom.yaml
  33-control-plan.yaml
  34-routing.yaml
  35-design-system-bom.yaml  # UI-CAD 案件のみ必須。非UI案件は not-applicable
  40-work-order.md
  50-as-built.yaml
  53-service-bom.yaml
  plm-intake/
    intake-manifest.yaml
    00-index.md
    CAND-001.md
    sync-results/
```

## 5. 命名規則

### ファイル名

- 標準成果物は番号付きの固定名を使う。
- 任意追加成果物は `bomdd/plm-intake/` か、該当領域の下に置き、参照元に `source_ref` を残す。
- UI は `bomdd/ui/mock/` に原典、抽出後は `bomdd/ui/<screen-or-flow>/` に置く。
- DB は `bomdd/db/schema-intent.md` を最初に作り、DDL は `bomdd/db/ddl/`、移行意図は `bomdd/db/migrations/` に置く。

### ID

| 種別 | 形式 | 例 |
|---|---|---|
| Requirement | `REQ-NNN` | `REQ-001` |
| Invariant | `INV-NNN` | `INV-001` |
| TraceLink | `TL-<SRC>-<DST>-NNN` | `TL-REQ-E-001` |
| Display Contract | `DC-<SCREEN>-NNN` | `DC-CHECKOUT-001` |
| Display Element | `DE-<SCREEN>-NNN` | `DE-CHECKOUT-003` |
| E-BOM | `E-<DOMAIN>-NNN` | `E-BOOKING-001` |
| K-BOM | `K-<DOMAIN>-NNN` | `K-SQLITE-001` |
| M-BOM | `M-<DOMAIN>-NNN` | `M-BOOKING-API-001` |
| Control Plan | `CP-<DOMAIN>-NNN` | `CP-BOOKING-001` |
| Routing | `ROUTING-<DOMAIN>-NNN` | `ROUTING-BOOKING-001` |
| Routing Step | `ROUTE-<DOMAIN>-NNN` | `ROUTE-BUILD-001` |
| Work Order | `WO-<LOOP>-NNN` | `WO-forward-01-001` |
| As-Built | `AB-<LOOP>-factory-NN` | `AB-forward-01-factory-01` |
| Service BOM | `SB-<DOMAIN>-NNN` | `SB-BOOKING-001` |

ID は人間が読めるドメイン語を含め、同じ意味の部品には同じ ID を維持する。意味が変わった場合は ID を再利用せず、旧 ID からの関係を TraceLink に残す。

## 6. BOM 粒度の判断基準

### 共通判定

BOM item は、次の問いに答えられる粒度にする。

- 何のために存在するかを 1 文で言えるか。
- `requirement_refs` または `kbom_refs` に接続できるか。
- `acceptance_refs` で単独または明確な組として検査できるか。
- 変更時に影響分析の単位として意味があるか。
- 製造または保守で独立に再製造、交換、再検査できるか。

### 最小粒度

- E-BOM: 仕様担当が存在理由を理解でき、1 つ以上の REQ、表示契約、制約、外部知識に接続できる最小単位。
- K-BOM: AI が暗黙に補いそうな外部知識、設計根拠、依存バージョン、制約を 1 つの管理対象として固定できる最小単位。
- M-BOM: 製造工程管理者が、現在どのユニットを作っているか、どの artifact が出るか、どの検査を通すかを把握できる最小単位。
- S-BOM: 保守担当者が障害、外部依存更新、モデル更新から逆引きできる最小単位。

### 最大粒度

- 1 item が複数の独立した責務、複数の unrelated REQ、複数の異なる acceptance depth を持つなら粗すぎる。
- `depends_on` が説明できない大量の内部要素を含むなら粗すぎる。
- 「アプリ全体」「UI 全体」「DB 全体」は原則として上位 grouping であり、PLM item としては粗すぎる。

## 7. PLM で読める必須フィールド

BOM item と traceable item は原則として次を持つ。

```yaml
id: E-BOOKING-001
name: Booking rule engine
purpose: Enforce booking availability and overlap rules
lifecycle_state: draft        # draft | ready-for-plm | manufacturing-ready | as-built | retired
granularity:
  level: component            # feature | component | unit | external-knowledge | evidence
  rationale: One rule engine maps REQ-003/REQ-004 to CP-BOOKING-001.
requirement_refs: [REQ-003, REQ-004]
depends_on: [K-SQLITE-001]
acceptance_refs: [CP-BOOKING-001]
output_artifact_ref: src/Booking/BookingRules.cs
trace_links:
  - trace_id: TL-REQ-E-001
    from: REQ-003
    to: E-BOOKING-001
    relation: satisfies
unresolved_questions: []
```

`output_artifact_ref` がまだ無い段階では `planned_output_artifact_ref` を使う。実装後は `50-as-built.yaml` の artifact hash と接続する。

## 8. やってはいけないこと

- Gate 通過前に実装を始める。
- 仕様、UI、DB、BOM、工程、検査、保守の順序を飛ばす。
- 不明点を AI の慣習で埋めて確定事項にする。
- `unresolved_questions` を空にするために推測で決める。
- UI モックの `div` や `span` をそのまま E-BOM にする。
- 「アプリ全体」「API 全体」のような粗い BOM item で済ませる。
- `requirement_refs`、`acceptance_refs`、`depends_on`、`output_artifact_ref` の無い PLM item を作る。
- Control Plan なしに M-BOM を manufacturing-ready にする。
- 固定オラクルの期待値や設計対話を製造装置へ渡す。
- 不具合発覚後に直接ソースだけを直し、仕様/BOM/Control Plan へ逆流しない。

## 9. 最初に人間へ確認する質問

AI は開始時に、最低限次を確認する。

1. 既存の仕様書、メモ、チケット、会話ログはありますか。どれを正としますか。
2. GUI アプリですか。UI/UX モック、スクリーンショット、Figma、HTML モックはありますか。
3. DB または永続化はありますか。既存 DDL、ERD、データ移行要件はありますか。
4. 外部 API、ライブラリ、クラウド、ツール、デザインシステムへの依存はありますか。
5. テスト方針、既存テスト、受入条件、手動承認者はありますか。
6. リリース、配布、運用形態は何ですか。
7. 保守対象は何ですか。外部知識、依存バージョン、AI モデル更新を追う必要がありますか。
8. 最初に人間が配置できるファイルは何ですか。
9. 実装開始を止めるべき条件は何ですか。
10. PLM 同期後の指摘を誰が裁定しますか。

## 10. 新規プロジェクト開始時の標準フロー

1. `bomdd/` を作り、テンプレートを配置する。
2. 人間が既存資料を `bomdd/plm-intake/`、UI 原典を `bomdd/ui/mock/`、DB 原典を `bomdd/db/` に置く。
3. AI が `00-charter.md` を埋め、スコープ、境界、工場構成、Gate を固定する。
4. AI が `10-requirements.yaml` を作る。曖昧な要求は `needs-refinement` にする。
5. AI が `20-spec.md` を作る。表示契約、不変条件、DB 永続化意図を含める。
6. GUI なら UI モックから `ui-ir.json`、`ui-bom.json`、`ui-trace-map.json` を作る。
7. UI-CAD 案件なら `35-design-system-bom.yaml` を作り、Card / CTA / Chip / Badge / IconButton など required design parts を固定する。
8. DB があるなら `db/schema-intent.md` を作り、DDL や migration intent と接続する。
9. AI が `30-ebom.yaml`、`31-kbom.yaml`、`32-mbom.yaml`、`33-control-plan.yaml`、`34-routing.yaml` を作る。
10. BOM-DD PLM に同期し、不足、粗粒度、トレース切れ、PLM-ready 契約違反を確認する。
11. PLM 指摘を `bomdd/plm-intake/00-index.md` と `bomdd/plm-intake/{CandidateNo}.md` の個別作業票へ落とし、仕様/BOM/Control Plan へ逆流する。
12. G1、G2、G2'、G3 を通す。未解決事項が blocker なら実装開始しない。
13. `40-work-order.md` を作り、製造パッケージだけを fresh factory へ渡す。UI-CAD 案件では `35-design-system-bom.yaml` も製造パッケージに含める。
14. 製造後に `50-as-built.yaml`、テスト証跡、cheat-log、`53-service-bom.yaml` を更新する。
