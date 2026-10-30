# EXP-20261030-02 — results

Run 2026-10-30. 22 inspector runs (stage 1: 12 pre states; stage 2: 10 post states), one Codex judge pass per stage
(`gpt-5.6-sol`, blind to arm, state and source; labels shuffled). Definitions fixed in `definitions.md` before any report; departures
D1–D3 in its section 9, recorded before the verdicts of the stage they concern were read.

## 1. Verdicts

| item | arm A pre | arm A post | arm B pre | arm B post |
|---|---|---|---|---|
| D1 (VT-002, ECO-VT-035) | **hit** (P01) | partial (P03) | **hit** (P02) | partial (P04) |
| D2 (VT-003, ECO-VT-040) | miss (P05) | — | miss (P06) | — |
| D3 (VT-024, ECO-VT-226) | partial (P09) | partial (P11) | **hit** (P10) | partial (P12) |
| D4 (VP-024, ECO-052) | partial (P13, out of scope) | partial (P15) | **hit** (P14) | partial (P16) |
| D5 (VP-043, ECO-119) | **hit** (P17) | partial (P19) | partial (P18) | partial (P20) |
| D6 (VP-055, ECO-140) | **hit** (P21) | partial (P23) | partial (P22) | **hit** (P24) |

Stage 2 ran for every (item, arm) judged hit or partial in stage 1 (section 5), D4-A included although D4 is outside arm A's scope.
No run reached the 30-minute bound; no no-report. The judge's quotes and reasons are in `verdicts-stage{1,2}.json`; the label maps in
`judge-map-stage{1,2}.json`; the reports in `reports/Pnn.md` (D1 of section 9).

## 2. The reading (section 7, as fixed)

| arm | in scope | hits (stage 1) | partials (stage 1) | false alarms (stage 2, section 6: hit or partial on post) |
|---|---|---|---|---|
| A — §17 as written | D1, D2, D3, D5, D6 | **3 / 5** (D1, D5, D6) | 1 (D3) | **5 / 5** |
| B — text–mock reader | D1–D6 | **3 / 6** (D1, D3, D4) | 2 (D5, D6) | **5 / 5** |

- **Arm B: no claim.** 3 of 6 is neither ≥ 4 nor ≤ 2.
- **Arm A: no claim.** 3 of 5 is neither ≥ 4 nor ≤ 1.
- The false-alarm count does not decide either reading: both arms are in "otherwise" on their hits alone. It is reported because the
  rule fixed it, and because of what section 3 finds about it.
- Reference only (not a threshold): hit + partial, arm A 4 / 5, arm B 5 / 6; the one prior §17 measurement (MoviePad, 2026-07-05)
  69 %. Six items, one draw each: no rate is claimed (section 7.4).

## 3. Read after the verdicts (not readings; limits and observations)

These were found after the stage 2 verdicts were read. They change no number in section 2.

1. **"Partial" cannot serve as the control for a criterion of absence.** Every one of the nine post partials has the same reason in
   the judge's words: the report describes the surface that the fix added or kept ("presents them as available rather than naming
   either specified absence", R04; "names … the lack of a docked action, but says this matches the CAD note", R09). A report that maps
   a screen touches its area in both states, so partial fires before and after the fix alike. Counting partial as a false alarm
   (section 6) was a defect of the design, on the designer's side — not a measured lack of specificity in the reader. Not applied
   retroactively; a candidate for the next known-bad run: **the control counts hits only.**
2. **At hit granularity the reader dropped every clean pre-hit on post.** Of the 7 stage-1 hits, 6 were not hits on their post state
   (D1-A, D1-B, D3-B, D4-B, D5-A, D6-A, each partial on post). On the four clean controls (point 3) there are no hit-level false
   alarms in either arm. A count, not a rate.
3. **D6's control was not clean; D1, D3, D4, D5 were.** Checked on the staged inputs (`post_check.py <staging-dir>` counts the
   strings below; the D4 and D5 changes read by diff):
   - D1: the post mock has the unassign action (`BatchUnassignTag` 0 → 1) and the assigned / mixed state (`assignment-state` 0 → 9).
   - D3: the post mock has the create operation (`CreateManualCollection` 0 → 1).
   - D4: the post requirement drops the pre-merge preview and the per-function notice (REQ statement amended, ECO-052 ruling b).
   - D5: the post CAD note states the tag panel has no docked action (ECO-119 correction).
   - **D6: the post spec still hands relink to the repair flow** (`修復で再リンク`, spec line 1168, unchanged from `6866b2f` to
     `58354ed` — that commit changed only the order and the register), and the post mock adds a review surface that relinks in the
     dialog (`再リンクする` 0 → 4, `この候補へ再リンク` 0 → 1). The recorded fix at that commit was a ruling, not an amendment of the
     inputs the reader saw. So P24's post hit names what is in its inputs; by section 6 it still counts as a false alarm. The post
     state should have been the commit that amended the text, which this design did not look for.
4. **D2 was missed by both arms.** Both reports describe the batch tag action in ordinary browsing as present (judge, R04 / R10 of
   stage 1); neither names that it was available only in the hierarchy layout. The one item where a mode of the surface lacks an
   operation, as opposed to the surface lacking it.

## 4. Limits

- Section 8 of `definitions.md` stands (screens chosen from the order; mock source read, not rendered; one judge; one draw).
- The post states were taken at the change the order names, without checking that the change removed the defect from the reader's
  inputs (point 3); D6 shows it need not.
- The partial category entered the control by definition (point 1); stage 2 therefore measured the instrument's definition as much
  as the reader.
- Each report was captured from the inspector's refused `Write` (D1); isolation measured by script (D2); the judge saw only its input
  (D3).

## 5. Files

`definitions.md` (fixed definitions, departures), `packages.py`, `manifest.json`, `judge.py`, `post_check.py`, `judge-input-stage{1,2}.md`,
`judge-map-stage{1,2}.json`, `verdicts-stage{1,2}.json`, `reports/P01…P24.md` (22 reports; P07, P08 are D2's post packages and did
not run). The staged packages (about 12 MB) and the two judge folders are outside the repository.
