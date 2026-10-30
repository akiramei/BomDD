# EXP-20261030-03 — results

Run 2026-10-30 on the user's "A: 走らせる", by `definitions.md` as filed in `f178242` (departures in section 4).

## 1. The run

- Six fresh Claude derivers (general-purpose agents), one per package, started together at 05:37Z, each given only its folder and
  "read prompt.md and do what it says". Derivation times (first to last transcript entry): T01 17.2, T02 16.4, T03 21.3, T04 16.4,
  T05 20.5, T06 18.6 minutes — all inside the 30-minute bound.
- Every deriver wrote `table.json` itself, by a script of its own (no `Write` was refused this time); T02, T05 and T06 left the
  hand-back block out as too large, and T01, T03 and T04's hand-back blocks parse to the same table as the file. Each file's
  SHA-256 matches the one its deriver reported. Copies: `tables/T01.json`-`T06.json` (1.1 MB).
- Isolation (every Read/Glob/Grep path, Bash command and written script content scanned for another package, a repository or the
  memory folder): no deriver touched another package. T05 read two files under the harness's `tool-results/`, both its own command
  output (the requirements file and the mock), referenced in no other transcript.
- Table sizes (states / entities / operations as written): T01 35/15/62, T02 38/13/73, T03 30/16/76, T04 36/18/79, T05 98/21/143,
  T06 74/26/162. Every table places all of `actions.txt` (T1 = 0 in all six).

## 2. Verdict by the fixed reading (`definitions.md` section 7)

| item | layer T: matching flags pre / post | caught | layer M (descriptive) |
|---|---|---|---|
| D1 | 6 / 4 | no | caught (`BatchAssignTag` on pre, none on post) |
| D2 | 0 / 0 | no | outside layer M |
| D3 | 4 / 3 | no | not caught (`ShowCollectionArchive` on both) |

**Layer T: 0 of 3 caught — by the fixed reading, the table form does not reach these on these inputs.** The noise qualifier is
not reached; for the record, stop flags (T2-T5) on the post packages are 49 (T02), 38 (T04) and 115 (T06), all above 25.

Flags per check:

| package | M1 | T2 | T3 | T4 | T5 | T6 |
|---|---|---|---|---|---|---|
| T01 D1 pre | 5 | 11 | 10 | 10 | 4 | 3 |
| T02 D1 post | 4 | 9 | 7 | 6 | 27 | 3 |
| T03 D2 pre | 4 | 10 | 9 | 8 | 6 | 5 |
| T04 D2 post | 4 | 12 | 8 | 13 | 5 | 2 |
| T05 D3 pre | 10 | 13 | 18 | 15 | 55 | 5 |
| T06 D3 post | 10 | 15 | 16 | 17 | 67 | 11 |

## 3. Read after the verdict (not readings; `after_verdict_why.py`, `after_verdict_repro.py`)

1. **D1 — the defect's own row behaved as intended; the item missed on a different operation.** On T01 the deriver gave
   `BatchAssignTag` the counterpart `BatchUnassignTag`, a text-only row (no mock action), so T3 fired on it; on T02 both are drawn
   (`BatchAssignTag` ↔ `BatchUnassignTag`) and that flag is gone. What kept D1 from "caught" is the detail pane's tag assign and
   unassign: the text requires them (REQ-024, spec §2.9), neither mock state draws them, so T2/T3 fire on them in both states — and
   in both derivations of the D1-post input (T02 and T03). The matching (section 6) is a pattern over the item's words, so it cannot
   tell two operations on one entity apart. Whether the detail-pane gap was itself a recorded defect was not checked (a later mock,
   T06, has `ToggleQuickActionTag`).
2. **D2 — on the same input, the flags depended on the derivation; the outcome did not (missed by both).** T02 and T03 are the same input (section 2 of the
   definitions). T03's deriver put the batch tag operations inside the assignment modal (absent in every Videos state) and the
   modal's opener `OpenTagAssignment` enabled in every selection-capable state, so T5 has nothing to fire on; T02's deriver produced
   five tag-matching T5 flags (`OpenTagAssignment`, `BatchAssignTag`, `BatchUnassignTag`, `NavigateTags`, `EditAssignmentValue`).
   The D2 post (T04) has none, but T02's five are not the defect (corrected at closure; the run commit said that T02 as the pre
   would have caught D2). ECO-VT-040's defect is the batch action shown only in the classification surface and absent from
   ordinary browsing. T02 has the opener `OpenTagAssignment` enabled in "Videos" and "通常" and `not_drawn` in "モード すべて",
   "モード 未分類" and "タグ付与 失敗"; `BatchAssignTag`, `BatchUnassignTag` and `EditAssignmentValue` are enabled only in "タグ付与
   失敗"; `NavigateTags` only in "Videos". The flags come from cells the deriver left `not_drawn`, and the opener's availability points the other way
   from the defect (enabled in the state the deriver called "通常"). That "通常" is not ordinary browsing: in both tables it is
   the mock's `cad.state.normal` (T02 `ok`, T03 `ST-VIDEOS-NORMAL`), and the pre mock (`2060849`) draws one Videos surface, the
   classification browse (view select, すべて / 未分類, the 人物カタログ › 出演者 path), whose results head has the opener. So
   "enabled" there is a faithful transcription, not a misreading. The defect sits in a state only the text names — ordinary
   collection or filter results with batch selection (definitions section 2) — which the mock does not draw; listed as its own
   state, its opener cell would be `not_drawn` and T5 would fire. Neither table lists it, so neither could have caught D2 as
   defined: D2 was lost in the state list, not in a cell (corrected again at closure, after a review of the records the user
   brought; the first closure text read "通常" as ordinary browsing).
3. **D3 — the table's entity granularity hid it.** T05's deriver merged manual and channel collections into one entity
   (`Collection（manual/channel 取得元）`) whose drawn create is `ConfirmChannelCollection`, so T4 is silent; T05 has no create or
   add row whose id, label or mock action names manual (manual / 手動), drawn or not. The defect is the absence of a create for one kind of an entity; T4 sees an
   entity only as the deriver splits it.
4. **Reproducibility (T02 vs T03, the same input).** States 38 / 30, entities 13 / 16, operations 73 / 76 as written; T5 27 / 6;
   flag Jaccard 0.145 on `(check, mock action or id)` and 0.314 on flags keyed by a mock action only.
5. **The checks fire on what the table carries, and what the table carries is the deriver's reading.** In D1 the deterministic
   part did what it was built for on the defect's row; D2 and D3 were lost before any check ran — in the state list and the entity
   split, which varied between two derivations of one input. This is the result's shape, recorded, not a claim (three items, one
   derivation each, in-sample checks).

## 4. Departures

- **D1 (source of the tables).** Section 5.1 named the refused `Write` content, else the hand-back block. No `Write` was refused:
  each deriver wrote `table.json` by its own script. `extract_tables.py` was changed (before any check ran) to take that file as
  written, ahead of the two pre-registered sources, and to report whether a hand-back block parses to the same table (3 of 3 that
  had one: same).
- **D2 (dropped rows; a defect of the design).** The prompt says "write `null` where the inputs say nothing"; the validator
  required `owner_surfaces` to be a list. 38 operation rows had `owner_surfaces: null` (T01 6, T02 8, T03 8, T04 8, T05 0, T06 0),
  all text-only operations (collection, view and backup create/delete, metadata refresh, and so on), and were dropped as section 5.1
  says. Sensitivity (`sensitivity.py`, null read as an empty list, nothing dropped): the verdict is unchanged (0 of 3; matching flags
  the same for all three items); post stop flags become 62, 51 and 115.

## 5. Limits

- Three items, one derivation per state; in-sample checks, lexicon and matching patterns; no human ruling of the table; the mock
  read as source. The hold-out (EXP-20261030-01's other ViewTube structural items) was not run.
- The derivers were given a schema with `selection_possible` and `counterpart` fields, which names the shape of two of the three
  defects; this could only have helped them.

## 6. Files

`definitions.md`, `manifest.json`, `packages.py`, `checks.py` (`run` writes `flags.json`), `extract_tables.py`, `flags.json`,
`tables/T01.json`-`T06.json`, `sensitivity.py`, `after_verdict_why.py`, `after_verdict_repro.py`. The staging folder (packages,
the derivers' own build scripts) is outside every repository and is deleted after this commit on the user's word.
