# Part Lineage / Reattribution — <ECO/CAPA-ID>

> Phase 7 の split / supersede / retire 用補助票。  
> 目的は、旧 E-BOM ID を履歴として残しつつ、現行 baseline の active graph からは完全に外すこと。  
> 影響分析は [61-impact-analysis.md](61-impact-analysis.md)、変更オーダー本体は [60-change-order.md](60-change-order.md) に記録する。

## 1. 操作

- operation: SplitPart / SupersedePart / RetirePart
- ECO/CAPA:
- old_part_id:
- old lifecycle before:
- old lifecycle after: superseded / retired
- new_part_ids:
- reason:
- decision owner:
- change register ref:

## 2. Lineage update

旧 ID は来歴参照に残してよい。ただし active 構造参照には残さない。

```yaml
old_part:
  id: E-<OLD>-001
  lifecycle_state: superseded
  lineage:
    superseded_by: [E-<NEW-A>-001, E-<NEW-B>-001]
    split_by: [E-<NEW-A>-001, E-<NEW-B>-001]
    change_ref: ECO-<ID>

new_parts:
  - id: E-<NEW-A>-001
    lifecycle_state: ready-for-plm
    lineage:
      supersedes: [E-<OLD>-001]
      change_ref: ECO-<ID>
```

## 3. Reattribution map

| old responsibility | new part id(s) | rationale | acceptance impact |
|---|---|---|---|
| | | | |

## 4. Active reference repoint checklist

各行は `done` / `not-applicable` / `deferred-content-only` のいずれかにする。`deferred-content-only` は prose の同期遅れにだけ使える。ID ラベルの張り替えには使えない。

| active reference surface | old refs before | new refs after | status | evidence |
|---|---|---|---|---|
| E-BOM `items[].depends_on` | | | | |
| E-BOM `items[].graph_edges.owner` | | | | |
| E-BOM `items[].graph_edges.consumers[]` | | | | |
| E-BOM `display_contracts[].elements[].ebom_item_ref` | | | | |
| M-BOM active `manufacturing_units[].ebom_refs[]` | | | | |
| Control Plan `characteristics[].verifies[]` | | | | |
| Service BOM active/as-built `items[].part_ref` | | | | |
| UI-BOM promoted `promotion.ebomItemRef` | | | | |
| UI-BOM accepted/promoted `ebomIntegrationCandidates[].suggestedEbomId` | | | | |
| UI trace-map `mappings[].ebomItemRef` | | | | |
| UI trace-map `ebomPromotionDecisions[].ebomItemRef` | | | | |
| Design System BOM formalized owner / consumer refs | | | | |
| active TraceLinks `from` / `to` | | | | |

## 5. Acceptance and manufacturing impact

| item | added | moved | retired | unchanged | evidence |
|---|---|---|---|---|---|
| E-BOM acceptance_refs | | | | | |
| M-BOM units | | | | | |
| Control Plan rows | | | | | |
| Fixed oracle rows | | | | | |
| Routing steps | | | | | |
| Service BOM items | | | | | |

## 6. Active Graph Integrity gate

- Gate timing: manufacturing freeze / PLM Gate / ECO completion
- Active E-BOM set excludes: retired, superseded
- Expected findings:
  - `missing-target`: 0
  - `retired-active-reference`: 0
  - `stale-active-tracelink`: 0
  - `lineage-without-retirement`: 0
  - `reattribution-incomplete`: 0
- PLM sync result:
- Repair queue refs:

## 7. Deferred content sync

Prose や説明文の同期遅れは、active ID 参照の張り替えが完了している場合だけ許可する。

| artifact / field | old wording | required update | due milestone | owner | risk if delayed |
|---|---|---|---|---|---|
| | | | | | |

## 8. Completion checklist

- 旧 ID は `superseded` または `retired` になっている。
- 新 ID は `supersedes` または変更理由を持つ。
- `reattribution_map` が旧責務を漏れなく新 ID へ割り付けている。
- active reference repoint checklist に未処理の ID ラベルが無い。
- acceptance / manufacturing impact が Control Plan と M-BOM に反映済み。
- Active Graph Integrity gate が 0 stop finding で通っている。
