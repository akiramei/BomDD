VERDICT: REJECT

FINDINGS
- IA-01 [false pass] A ruled/user ruling that itself carries `touches_confirmed` is wrongly exempted from bundle completeness.
  input: `fixtures/ia01_omitted_touched_human`
  observed: exit 0; `[GU7] PASS` although overlapping ruling `H` is absent from `B.confirmed_checked`.
  expected: exit non-zero with `[GU7] FAIL` naming omitted ruling `H` under rule (a).
- IA-02 [false pass] A duplicate later `touches: no` row overwrites an earlier `touches: yes` row, bypassing rule (b).
  input: `fixtures/ia02_duplicate_rows`
  observed: exit 0; `[GU7] PASS` with no separate `touches_confirmed: H` ruling.
  expected: `[GU7] FAIL`, because each `touches: yes` row requires a separate ruling.
- IA-03 [false pass] An empty-list `touches_confirmed` field is treated as absent, allowing an open non-blocking ruling through.
  input: `fixtures/ia05_empty_touch_list`
  observed: exit 0; GU7 is not listed at all.
  expected: `[GU7] FAIL` under rule (c), or rejection of the malformed empty reference.
- IA-04 [false pass] GU7 tests `blocking` by truthiness, so quoted `"false"` satisfies rule (c).
  input: `fixtures/ia03_quoted_false`
  observed: exit 1 with `[GU3] FAIL` but `[GU7] PASS`.
  expected: exit non-zero with a `[GU7] FAIL` stating that the open touching ruling is not `blocking: true`.
- IA-05 [false fail] Numeric ruling IDs are stringified in `confirmed_checked` but looked up in a raw-key dictionary.
  input: `fixtures/ia04_numeric_id`
  observed: exit 1; `[GU7] FAIL ... confirmed_checked の 1 が台帳に存在しない`.
  expected: exit 0; numeric ID `1` exists and is correctly listed with `touches: no`.
- IA-06 [false pass] GU7 conflates numeric ID `1` and string ID `"1"`, letting one row cover two distinct rulings.
  input: `fixtures/ia07_mixed_id_collision`
  observed: exit 0; `[GU7] PASS`.
  expected: `[GU7] FAIL` because numeric ruling `1` is omitted; alternatively the tool must reject the two IDs as duplicates if IDs are normalized to strings.
- IA-07 [selftest] The built-in ruled-touching “known-good” arm itself violates rule (a), embedding IA-01 into the calibration.
  input: `_GU7_ARMS` in `new/ui-cad-gate.py`, arm `known-good GU7: 触れる決定を単独で立て、人が裁定済み`
  observed: `python new/ui-cad-gate.py --selftest` exits 0, although ruled/user `UQ-ST-3` overlaps the bundle and is absent from `confirmed_checked`.
  expected: that arm must either list `UQ-ST-3` or be known-bad with a GU7 omission failure.
- IA-08 [wording] The template says `touches_confirmed` identifies a human-decided ruling, but GU7 accepts an open bundle as its target.
  input: `fixtures/ia06_bundle_pointer`; see `template-37-ui-rulings.yaml:139`
  observed: exit 0; `[GU7] PASS` when `T.touches_confirmed` points to bundle `B`.
  expected: enforcement consistent with the template—reject a target that is not `status: ruled` and `decided_by: user`.

WHAT I RAN
- Ran `python new/ui-cad-gate.py --selftest`: 9 arms, exit 0.
- Ran 7 adversarial GU7 fixture folders with the new tool.
- Compared old versus new on 10 no-bundle/no-`touches_confirmed` ledger cases across 4 exit classes; exit code and complete combined output were identical in all 10.
- Copied the tool under three names and independently disabled the direct (a), (b), and (c) checks; all three mutant self-tests exited 1 and named the matching known-bad label.
- Total: 11 fixture folders containing 17 ledger cases, plus 3 mutation copies.

NOT CHECKED
- GU6/`--mock` integration and raw-IR extraction, which are unrelated to GU7.
- Exhaustive recursive-alias or exotic YAML-tag fuzzing; no new-only traceback was found in the tested shapes.
- The declared non-goals: truth of `touches: no`, semantic overlap beyond equal `ui_ids`, and untyped bundles.