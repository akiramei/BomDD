# PLM-ready 契約

この契約は、BOM-DD PLM が `bomdd/` 成果物を機械的に読み、足りないもの、粗すぎるもの、粒度不整合、トレース切れ、実装開始停止状態を判定するための最低条件である。

## 1. BOM の目的

| BOM | 目的 | 読み手 |
|---|---|---|
| E-BOM | 仕様から見た設計部品表。何を作るか、なぜ存在するかを示す | 仕様担当、設計者、PLM |
| K-BOM | 外部知識、設計根拠、依存バージョン、制約、AI が暗黙に補いそうな判断を管理する | 設計者、製造装置、保守担当 |
| M-BOM | 製造単位、入力、出力 artifact、工程、検査を管理する | 製造工程管理者、製造 AI、PLM |
| S-BOM / Service BOM | 保守時に障害、外部依存更新、AI モデル更新から逆引きする | 保守、サポート、PLM |

一般的な Software Bill of Materials と区別するため、保守 BOM はこのリポジトリでは `Service BOM` と呼ぶ。ユーザー要求や PLM 契約上の `S-BOM` は、この `Service BOM` を指す。

## 2. 各 BOM の必須項目

### E-BOM item

```yaml
id: E-BOOKING-001
name: Booking rule engine
purpose: Enforce availability, overlap, and idempotency rules.
classification: core                  # core | surface
rationale_type: requirement           # requirement | defect-class | constraint | external-knowledge | design-token
granularity:
  level: component
  rationale: One component owns booking validity decisions and maps to CP-BOOKING-001.
requirement_refs: [REQ-003, REQ-004]
kbom_refs: [K-IDEMPOTENCY-001]
display_contract_refs: []
depends_on: [E-CALENDAR-001]
acceptance_refs: [CP-BOOKING-001]
output_artifact_ref: src/Booking/BookingRules.cs
trace_links:
  - trace_id: TL-REQ-E-001
    from: REQ-003
    to: E-BOOKING-001
    relation: satisfies
lifecycle_state: ready-for-plm
lineage:
  supersedes: []
  superseded_by: []
  split_by: []
  change_ref: ~
unresolved_questions: []
```

### K-BOM item

```yaml
id: K-SQLITE-001
name: SQLite persistence conventions
knowledge_kind: tool-grammar          # tool-grammar | design-system | domain-convention | dependency-version | policy
version: 3.46
source: bomdd/plm-intake/sqlite-notes.md
managed_knowledge:
  - Store UTC timestamps as ISO-8601 literal-Z text.
risk_if_implicit: Factories may mix local time, unix epoch, or provider defaults.
consumers: [E-BOOKING-001, M-PERSISTENCE-001]
acceptance_refs: [CP-PERSISTENCE-001]
lifecycle_state: ready-for-plm
unresolved_questions: []
```

### M-BOM unit

```yaml
id: M-BOOKING-API-001
name: Booking API manufacturing unit
purpose: Produce API endpoints and service layer for booking operations.
ebom_refs: [E-BOOKING-001]
kbom_refs: [K-SQLITE-001]
input_refs: [bomdd/20-spec.md, bomdd/30-ebom.yaml]
output_artifact_ref: src/Booking.Api
interface_contract:
  endpoints: [POST /bookings, GET /bookings/{id}]
invariants: [INV-001]
depends_on: [M-PERSISTENCE-001]
acceptance_refs: [CP-BOOKING-API-001]
routing_refs: [ROUTE-MANUFACTURE-API-001]
lifecycle_state: manufacturing-ready
unresolved_questions: []
```

### Service BOM item

```yaml
id: SB-BOOKING-PERSISTENCE-001
part_ref: E-BOOKING-001
classification: surface
external_deps:
  - kbom_ref: K-SQLITE-001
    version: 3.46
as_built_ref: AB-forward-01-factory-01
reinspect_on_change:
  - cp_ref: CP-PERSISTENCE-001
    depth: L3
replacement_decision_vocabulary: no-change / kbom-update-only / remanufacture-required
lifecycle_state: as-built
```

## 3. ID 規則

- ID は成果物内で一意、`bomdd/` 全体で同じ接頭辞ごとに一意にする。
- ID は意味が変わらない限り維持する。
- 意味が変わる場合は新 ID を払い出し、旧 ID との関係を TraceLink に残す。
- 旧 ID に後継がある場合は `superseded` とし、後継が無い廃止は `retired` とする。どちらも active 集合には含めない。
- 旧 ID は `supersedes`、`superseded_by`、`split_by`、ECO 本文、change register、reattribution table などの来歴参照に残してよい。
- PLM は未知接頭辞を warning、重複 ID を stop として扱う。
- 推奨接頭辞は `REQ`, `INV`, `TL`, `DC`, `DE`, `E`, `K`, `M`, `CP`, `ROUTING`, `ROUTE`, `WO`, `AB`, `SB`。

## 3.1 Active Graph Integrity

製造凍結、PLM Gate、ECO 完了時点では、現行 baseline の active graph は active item だけで閉じていなければならない。

active E-BOM item は `lifecycle_state` が `draft`、`ready-for-plm`、`manufacturing-ready` の item とする。`retired` と `superseded` は active 集合から除外する。

legacy 成果物で `lifecycle_state` が欠落している E-BOM item は、後方互換のため **active とみなす**。PLM は `legacy-lifecycle-defaulted` warning を出し、migration queue に載せる。欠落を非 active とみなしてはならない。欠落=非 active にすると、旧成果物の active set が空になり、参照検査が vacuous pass するためである。

PLM が検査する active E-BOM 参照:

| 層 | active 参照フィールド |
|---|---|
| E-BOM | `items[].depends_on`, `items[].graph_edges.owner`, `items[].graph_edges.consumers[]`, `display_contracts[].elements[].ebom_item_ref` |
| M-BOM | active `manufacturing_units[].ebom_refs[]` |
| Control Plan | `characteristics[].verifies[]` の `E-*` |
| Service BOM | active/as-built `items[].part_ref` |
| UI-BOM / trace-map | 昇格済み `promotion.ebomItemRef`, `items[].ebomCandidate.items[]`(legacy UI-BOM 互換), `meta.ebomItemsReferenced[]`, `ebomIntegrationCandidates[].suggestedEbomId`(`decision` が accepted/promoted のもの), `mappings[].ebomItemRef`, `ebomPromotionDecisions[].ebomItemRef` |
| Design System BOM | 正式化済み `root.ebom_item_ref`, `coverage_matrix.owner`, active consumer refs |

PLM は各 artifact について「期待した参照フィールドを実際に読めたか」を coverage として記録する。対象 artifact が存在するのに、既知スキーマの参照フィールドを 1 つも認識できない場合は、参照エラー 0 件として通さず `coverage-gap` / `unrecognized-schema` を出す。`0 stop findings` は「検査対象を読めた上で問題が無い」ことを意味し、「読めなかった」ことを意味してはならない。

来歴参照として許可する場所:

- `supersedes`
- `superseded_by`
- `split_by`
- ECO/CAPA 本文
- change register の履歴説明
- reattribution table の `old_part_id`

PLM finding:

| Finding | 条件 | severity |
|---|---|---|
| `missing-target` | active 参照先 ID が registry に存在しない | stop |
| `retired-active-reference` | active 参照が `retired` / `superseded` E-BOM ID を指す | stop at PLM Gate |
| `stale-active-tracelink` | `status: active` TraceLink が `retired` / `superseded` ID を指す | stop at PLM Gate |
| `lineage-without-retirement` | `supersedes` / `split_by` はあるが旧 item が active のまま | stop at PLM Gate |
| `reattribution-incomplete` | split / supersede 後も旧 ID の active consumer が残る | stop at PLM Gate |
| `coverage-gap` | artifact は存在するが、PLM が期待する参照フィールドを認識できず検査対象を掴めない | stop at PLM Gate |
| `unrecognized-schema` | UI-BOM / Design System BOM / Service BOM などが既知スキーマでも migration 宣言済みスキーマでもない | stop at PLM Gate |
| `legacy-lifecycle-defaulted` | `lifecycle_state` 欠落 item を後方互換で active とみなした | warning + migration queue |

## 4. 最小粒度

- E-BOM は、仕様担当が存在理由を理解でき、少なくとも 1 つの `requirement_refs`、`display_contract_refs`、`kbom_refs`、または制約へ接続できる単位にする。
- K-BOM は、AI が暗黙に補う判断を 1 つの版付き知識として管理できる単位にする。
- M-BOM は、製造工程管理者が現在の進捗、入力、出力 artifact、受入を把握できる単位にする。
- Service BOM は、保守担当者が障害または依存変更から逆引きできる単位にする。

## 5. 最大粒度

PLM は次を coarse warning または stop として扱う。

- `E-APP-001: アプリ全体` のように複数の unrelated REQ を抱える。
- 1 item の `acceptance_refs` が複数 depth に散り、検査観点が閉じない。
- `M-ALL-001` のように出力 artifact が多数で、工程状態が追えない。
- `K-EXTERNAL-001` のように外部知識の版、出所、consumers が混在する。
- Service BOM が全依存を 1 item に押し込め、障害時に逆引きできない。

## 6. `requirement_refs` の規則

- core E-BOM item は 1 つ以上の `REQ-*` を持つ。
- surface item は `REQ-*`、`DC-*`、`K-*` のいずれかを持つ。すべて無い場合は orphan。
- `requirement_refs` は実在する `10-requirements.yaml` の ID に限る。
- 1 REQ がどの E-BOM item にも到達しない場合、PLM は unsatisfied requirement として stop にする。

## 7. `depends_on` の規則

- `depends_on` は同じ層か、明示された許可関係に限る。
- E-BOM item は E-BOM item または K-BOM item に依存できる。
- M-BOM unit は M-BOM unit、K-BOM item、procurement item に依存できる。
- 循環依存は、明示的に `cycle_reason` が無い限り stop。
- 依存先が存在しない場合は stop。

## 8. `acceptance_refs` の規則

- E-BOM item と M-BOM unit は 1 つ以上の `CP-*` を持つ。
- `CP-*` は `33-control-plan.yaml` に実在する。
- surface item で外部ツール、UI、DB、同期、知覚を扱う場合、depth は対象に応じて L2、L3、G を使う。unit だけで済ませない。
- Control Plan が M-BOM unit の全出力を覆わない場合、PLM は insufficient acceptance として warning または stop にする。

## 9. `output_artifact_ref` の規則

- M-BOM unit は必ず `output_artifact_ref` または `planned_output_artifact_ref` を持つ。
- 実装後は `50-as-built.yaml` の `artifacts_sha256.path` と一致させる。
- E-BOM item が直接 artifact を持つ場合は `output_artifact_ref` を置いてよいが、製造責務は M-BOM に持たせる。
- `output_artifact_ref` が広すぎるディレクトリルートだけの場合、PLM は coarse artifact として warning にする。

## 10. TraceLink 規則

TraceLink は成果物間の有向リンクである。最低限、次の経路がたどれること。

```text
REQ -> Spec section -> E-BOM -> M-BOM -> Control Plan -> Routing -> As-Built -> Service BOM
```

TraceLink の標準形。BOM 定義 YAML 内では、PLM の item 抽出と衝突しないよう子レコードの識別子は `trace_id` とする。

```yaml
- trace_id: TL-REQ-E-001
  from: REQ-003
  to: E-BOOKING-001
  relation: satisfies       # satisfies | realizes | verifies | manufactures | produces | depends-on | records | maintains
  evidence: bomdd/20-spec.md#2.1
  status: active            # active | proposed | retired
```

PLM は次を警告または停止する。

- `from` または `to` が存在しない。
- `relation` が標準語彙に無い。
- retired / superseded item へ active link が残る場合は、§3.1 の `stale-active-tracelink` として PLM Gate を止める。
- REQ から As-Built まで到達不能な経路がある。

## 11. Control Plan / As-Built / Test Evidence の接続規則

- Control Plan は `CP-*` ごとに depth、tolerance、fixture、oracle、approver を持つ。
- Routing は自己受入で使う command と output evidence を持つ。
- As-Built はどの BOM tag、routing、AI model、prompt hash、artifact hash、self acceptance、設計者側 inspection を記録する。
- Test Evidence は `test_evidence_refs` として As-Built から参照し、`CP-*` の結果へ戻れるようにする。

推奨形:

```yaml
test_evidence_refs:
  - evidence_id: TE-forward-01-001
    cp_ref: CP-BOOKING-001
    result: pass
    evidence_path: bomdd/plm-intake/sync-results/factory-01-booking.json
    observed_at: 2026-06-20T00:00:00Z
```

## 12. PLM が警告すべき状態

- 任意成果物が推奨パス以外にあり、参照が無い。
- `purpose`、`granularity.rationale`、`lifecycle_state` が空。
- `depends_on` はあるが依存理由が弱い。
- UI モックはあるが UI-IR/UI-BOM/trace map が無い。
- DB があるが `schema-intent.md` が無い。
- K-BOM に version または source が無い。
- Service BOM が外部依存を逆引きできない。

## 12.5 PLM-lite — 工具不在時の手動縮退(実証済み N=2 — transfer-01 T0 還元)

BOM-DD PLM 工具(bomdd-lint)が環境に無い場合、PLM Gate は省略ではなく **PLM-lite**(手動照合)へ縮退する。playbook のゲート実行可能性規則(§13)により、工具も本節の代替手順も使えない場合は方法論欠陥として停止する。

- **照合対象は本契約のみ**(§12 の警告状態・§13 の停止状態)。新しい観点リストを作らない — 正本は本契約 1 本。
- **手順**: ①宣言済み成果物と参照済み成果物を全数列挙する ②全参照が同梱成果物または明示的な外部依存へ解決することを確認する ③§13 の各停止条件を 1 行ずつ pass / fail / not-applicable(理由付き)で判定する。
- **記録様式**: 判定表(§13 条件 × 判定 × 根拠)を `bomdd/plm-intake/00-index.md` に残し、charter の PLM Gate 行に「PLM-lite で代替」と明記する。
- **合格条件**: §13 相当の stop 判定が 0 件。fail が残る場合は実装開始しない(工具版と同じ)。
- **限界の自覚**: PLM-lite は人間/設計 AI の読解に依存し、工具版の網羅性(Active Graph Integrity の機械検査等)を持たない。工具が導入できた時点で再同期する。
- **実測**: transfer-01(2 回実施・stop 0・charter に代替明記)/ transfer-02(採用・00-index に判定記録)/ transfer-03(GPT-5.5/Codex — **本節を明示参照して採用**・stop 0)— 2 ベンダー・3 ラウンドで機能= **N=3・ベンダー横断**(candidate 解除は N=2 時点・2026-07-09)。実施様式は 3 例で分岐したまま(契約照合/checklist §4 表の流用)— 合格条件(stop 0 の判定記録)が共通につき、**様式は複数許容として運用**する(統一しない裁定・2026-07-09)。

## 13. PLM が実装開始を止めるべき状態

- 必須成果物 `00/10/20/30/31/32/33/34/40` が欠けている。
- UI-CAD 案件で `35-design-system-bom.yaml` が欠けている。
- 未満足 REQ がある。
- E-BOM item に `requirement_refs`、`kbom_refs`、`display_contract_refs` のいずれも無い。
- M-BOM unit に `output_artifact_ref` または `planned_output_artifact_ref` が無い。
- M-BOM unit に `acceptance_refs` が無い。
- Control Plan の `fixture`、`oracle`、`tolerance`、`approver` が空。
- TraceLink が REQ から Control Plan まで切れている。
- 製造凍結または ECO 完了時点で Active Graph Integrity が失敗している。
- PLM が coarse item を stop と判定し、分割方針が未裁定。
- unresolved question が blocker なのに manufacturing-ready になっている。
- 固定オラクルや設計対話を製造装置へ渡す指示が Work Order に含まれる。
