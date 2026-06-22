# Traceability Rules

この文書は、BomDD 成果物の TraceLink、参照フィールド、修復キュー化の規則を定義する。

## 1. 必須トレース経路

最低限、次の経路が双方向にたどれること。

```text
REQ -> Spec -> E-BOM -> M-BOM -> Control Plan -> Routing -> As-Built -> Service BOM
```

UI がある場合:

```text
UI mock -> UI-IR -> UI-BOM -> UI trace map -> Display Contract -> E-BOM -> Control Plan
```

DB がある場合:

```text
schema intent -> DB entity/field -> E-BOM -> M-BOM persistence unit -> Control Plan -> As-Built
```

## 2. TraceLink の標準語彙

| relation | 意味 |
|---|---|
| `satisfies` | REQ を E-BOM item が満たす |
| `specified-by` | item が仕様節で定義される |
| `realizes` | M-BOM unit が E-BOM item を製造する |
| `verifies` | Control Plan が item を検査する |
| `manufactures` | Routing step が M-BOM unit を製造する |
| `produces` | M-BOM / Routing / As-Built が artifact を出す |
| `depends-on` | item が別 item または K-BOM に依存する |
| `records` | As-Built が製造結果を記録する |
| `maintains` | Service BOM が保守逆引きを提供する |

## 3. TraceLink の形

BOM 定義 YAML 内では、PLM の item 抽出と衝突しないよう、TraceLink 子レコードの識別子は `id` ではなく `trace_id` と書く。Markdown 表では列名を `TraceLink` としてよい。

```yaml
trace_links:
  - trace_id: TL-REQ-E-001
    from: REQ-003
    to: E-BOOKING-RULES-001
    relation: satisfies
    evidence: bomdd/20-spec.md#booking-rules
    status: active
```

`trace_links` を置けない Markdown では、表で表現してよい。

| TraceLink | From | Relation | To | Evidence | Status |
|---|---|---|---|---|---|
| TL-REQ-E-001 | REQ-003 | satisfies | E-BOOKING-RULES-001 | `bomdd/20-spec.md#booking-rules` | active |

## 4. 参照フィールドの規則

### active 参照と来歴参照

BomDD の参照は、現行 baseline を構成する `active_structural_ref` と、変更履歴を説明する `lineage_ref` を分けて扱う。

| 種別 | 例 | retired / superseded ID |
|---|---|---|
| `active_structural_ref` | `depends_on`, `graph_edges.consumers`, M-BOM `ebom_refs`, Control Plan `verifies`, Service BOM `part_ref`, UI-BOM/trace-map の昇格済み E-BOM 参照 | 禁止 |
| `active_trace_ref` | `status: active` の TraceLink | 禁止 |
| `lineage_ref` | `supersedes`, `superseded_by`, `split_by`, reattribution table の `old_part_id` | 許可 |
| `historical_narrative_ref` | ECO 本文、change register、原因説明、議事録 | 許可 |

ECO/CAPA の編集中に一時的な不整合が生じることはあるが、製造凍結、PLM Gate、ECO 完了時点では `active_structural_ref` と `active_trace_ref` が active item だけを指していなければならない。

legacy 成果物では、`lifecycle_state` が欠落している E-BOM item を active とみなす。欠落 item を非 active として除外すると、旧成果物の参照走査が空振りし、トレース切れを見逃すためである。PLM はこの場合 `legacy-lifecycle-defaulted` warning を出し、明示的な lifecycle migration を修復キューに載せる。

PLM は参照エラーだけでなく、参照フィールドを認識できたかを検査する。artifact が存在するのに既知スキーマの参照フィールドを掴めない場合、`coverage-gap` または `unrecognized-schema` として stop する。これは「0件検出」を「問題なし」と誤解する vacuous pass を防ぐための規則である。

UI-BOM / trace-map の既知参照フィールドは少なくとも次を含む:

- `promotion.ebomItemRef`
- `items[].ebomCandidate.items[]`(legacy UI-BOM 互換)
- `meta.ebomItemsReferenced[]`
- `ebomIntegrationCandidates[].suggestedEbomId`(`decision` が accepted/promoted のもの)
- `mappings[].ebomItemRef`
- `ebomPromotionDecisions[].ebomItemRef`

### `requirement_refs`

- REQ への直接参照。
- core item は必須。
- surface item も要求起点なら持つ。

### `depends_on`

- 実装順ではなく、意味上または製造上の依存を表す。
- 依存先 ID と依存理由を確認できるようにする。

### `acceptance_refs`

- `CP-*` への参照。
- 合否を固定する Control Plan が無い item は manufacturing-ready になれない。

### `output_artifact_ref`

- 製造結果の予定または実体のパス。
- M-BOM は必須。
- As-Built の `artifacts_sha256.path` と対応する。

## 5. 例

```yaml
requirements:
  - id: REQ-003
    statement: A user can create a booking only when the room is available.

ebom:
  items:
    - id: E-BOOKING-RULES-001
      requirement_refs: [REQ-003]
      acceptance_refs: [CP-BOOKING-RULES-001]

mbom:
  manufacturing_units:
    - id: M-BOOKING-SERVICE-001
      ebom_refs: [E-BOOKING-RULES-001]
      output_artifact_ref: src/Booking/BookingService.cs
      acceptance_refs: [CP-BOOKING-RULES-001]

control_plan:
  characteristics:
    - id: CP-BOOKING-RULES-001
      verifies: [E-BOOKING-RULES-001, M-BOOKING-SERVICE-001]
      depth: unit

as_built:
  - id: AB-forward-01-factory-01
    artifacts_sha256:
      - path: src/Booking/BookingService.cs
        sha256: <sha256>
    test_evidence_refs:
      - cp_ref: CP-BOOKING-RULES-001
        result: pass
```

## 6. トレース切れの種類

| 種類 | 例 | PLM 判定 |
|---|---|---|
| orphan item | E-BOM item が REQ/K-BOM/DC のどれにも繋がらない | stop |
| unsatisfied requirement | REQ が E-BOM に到達しない | stop |
| unverified item | E-BOM/M-BOM が Control Plan に繋がらない | stop |
| unproduced unit | M-BOM unit に output artifact が無い | stop |
| unrecorded artifact | As-Built に artifact hash が無い | warning/stop |
| retired-active-reference | active 参照が retired / superseded ID を指す | stop at PLM Gate |
| stale historical mention | ECO 本文などの履歴説明に旧 ID が残る | allowed |
| broken dependency | depends_on の相手が存在しない | stop |
| lineage-without-retirement | `supersedes` / `split_by` はあるが旧 item が active のまま | stop at PLM Gate |
| reattribution-incomplete | split / supersede 後も旧 ID の active consumer が残る | stop at PLM Gate |
| coverage-gap | artifact は存在するが、PLM が期待する参照フィールドを認識できない | stop at PLM Gate |
| unrecognized-schema | artifact が既知スキーマでも migration 宣言済みスキーマでもない | stop at PLM Gate |
| legacy-lifecycle-defaulted | lifecycle 欠落 item を active として後方互換処理した | warning + migration queue |

## 7. 修復キュー化

PLM 指摘は、発見した層ではなく原因層へ戻す。

```markdown
| ID | Finding | Cause layer | Fix target | Action |
|---|---|---|---|---|
| RQ-002 | REQ-003 has no E-BOM item | E-BOM | 30-ebom.yaml | Add E-BOOKING-RULES-001 and TL-REQ-E-001 |
```

原因層の目安:

- 要求が曖昧: Requirements / Spec
- 仕様にあるが BOM に無い: E-BOM
- 外部知識が暗黙: K-BOM
- 製造単位が無い: M-BOM
- 検査が無い: Control Plan
- 工程が無い: Routing
- 実体の来歴が無い: As-Built
- 保守逆引きが無い: Service BOM

## 8. 実装開始停止条件

次の TraceLink 欠陥は実装開始を止める。

- `REQ -> E-BOM -> M-BOM -> Control Plan` が切れている。
- 製造凍結または ECO 完了時点で retired / superseded ID への active 参照が残っている。
- UI 表示契約があるのに Control Plan へ繋がらない。
- DB 永続化要件があるのに schema intent または M-BOM persistence unit が無い。
- M-BOM unit が output artifact と Routing step に繋がらない。
- unresolved question が blocker なのに downstream item が ready になっている。
