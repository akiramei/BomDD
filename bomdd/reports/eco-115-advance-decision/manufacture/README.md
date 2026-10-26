# ECO-115 manufacture — acceptance V1 and V2 (measured at manufacture)

Run 2026-10-26 from the BomDD root. All files are LF; sha256 of the committed bytes.

| File | What | sha256 |
|---|---|---|
| `check_v1_v2.py` | (repaired after inspections r1 to r5 — r4: the bounds sentence's copies checked against the playbook; r5: I2's closed values read from the playbook and every copy compared as a set, with mutations; the repaired clauses added; a stored output recording a missed case fails V2 — the outputs below were made with the script at `35961c3`) V1: playbook 4.4's item "前進の判定" with each of I0-I4, D0-D5 once as a label, each rule's clauses (identifiers and values verbatim, the rest in the item's words) inside that rule's own segment, the limits, I2's values; one line each in section 1 and 6.1; the on_fail sentence pointing at the item with no value outside I2; every M1 template field with a comment naming the item; I2's values in the template comments; the work order's frozen line with its comment on the next line and the bounds line. V2: (a) every field the rehearsals read present in the parsed templates by key path; (b) `run_rehearsal_v2.py`, `run_moviepad.py`, `run_moviepad_d2.py` and `rehearse_sequence.py` re-run against the stored outputs byte for byte (each reads fixed commits, not a HEAD) | `1d879c3da9e5b1b9964f8a73a4b3d2b0a4ae25fbe56df0eabb2b4b0ad893b8fa` |
| `v1-v2.txt` | its output on the manufactured tree: PASS 116/116 | `949dac426227a38b7a9a25b944a261405dcbc6c98956c4bc58010da624ad46ae` |
| `v1-v2-control-before-manufacture.txt` | the same script on the filing tree (`db16fa3`, the manufacture's edits stashed): FAIL 22/116 — 94 checks fail; the 22 that pass are the four re-runs, the parse, fields and comment values the templates already had | `e825dd0a6ef6cadbd68f28a4be6ee1d037faaa4ea5ee71f449457b7af6b1b346` |

Command:

```
python -B bomdd/reports/eco-115-advance-decision/manufacture/check_v1_v2.py . ../ViewPrism2 ../MoviePad-Remake <scratch directory>
```

The clause check measures presence, not meaning: whether the item's Japanese says what the order's English clause says is the independent
inspection's (V3). It was made clause by clause from the start because ECO-114's inspection r1 (IA-03) found that a label check passed while a rule's
content was missing. Defects of this script found before these outputs: the second bold "D5" in D5's own text counted as a second label (the text was
reworded so the label appears once), and `result` matched the validation block's field before the decision record's (the search now starts at
`test_evidence_refs`).
