# ECO-115 — repairs after independent inspection r1 (REJECT IA-01 to IA-07)

Run 2026-10-26 from the BomDD root. All files are LF; sha256 of the committed bytes.

| File | What | sha256 |
|---|---|---|
| `v1-v2.txt` | `../manufacture/check_v1_v2.py` (repaired) on the repaired tree: PASS 120/120 | `0a586111b33237fdf2b627475a71523c3fda183dc20b00d156975e8d79f9bc30` |
| `control-on-manufacture-tree.txt` | the same script on the manufacture tree (`35961c3`, the repairs stashed): FAIL 116/120 — the four clause groups of IA-02 and IA-03 (the bounds line in I2, I3a and D5; L7's scale) | `135f9d5af05ca1c62c6cfbb32dde99be4563fad13b38a57b9e7f8506640fdf17` |
| `redfirst-decision.txt` | the repaired `run_rehearsal_v2.py` against the manufacture tree's `rehearse_decision_v2.py`: exit 1, 8 MISSED (the three IA-04 arms and five IA-02 arms), D4 not written | `f740fe04d50a02ba4d63827c4cff10e62fb18ccfd5b8fa351480389d50b4b95d` |
| `redfirst_c5.py` | runs the C5 control of `../repair-r4/redfirst_all.py` (the current files with the manufacture tree's C5 clause put back, staged with every file they import); exit 0 only on the signature: exactly Y6 BAD | `30118d96af63481ce72a5f50ae826a093fd153fc09273a180540236035a99407` |
| `redfirst-c5.txt` | its output: Y6 BAD, Y7 OK, exit 1 | `3fd4b8f1622b5f3c4414b669c80dfdba016e702d18b7948567ef70951ff9f644` |

What each repair is (the order's section 6 has the account):
- IA-01 — §6.1's line now says what enters Phase 5 through the decision, and keeps a product's outside-the-decision way (D3).
- IA-02 — the bounds line's grammar in I2, its check in I3a (work-order-fix), and D5's defaults when the first issue's line is outside I2; in the
  order's §1 and in the playbook; arms: six in `run_rehearsal_v2.py`, two in `rehearse_sequence.py` (Z1, Z2).
- IA-03 — L7's scale in the limits bullet.
- IA-04 — `rehearse_decision_v2.py` binds the bytes it decides and compares to the files the refs name at `frozen_commit` and at the delivered
  commit; the drivers' git holds each case's files (a migrated copy stands for the frozen revision's file wherever that file stands); three arms.
- IA-05 — C5 compares the change's recorded cause with the row's open cause; arms Y6 (red) and Y7 (its green twin).
- IA-06 — the decision writes each decision record's D4 `result` into the entry; `run_rehearsal_v2.py` checks it on every case that decided rows.
- IA-07 — the three drivers return exit 1 on a missed case; `check_v1_v2.py` fails a stored output that records one.

Command for the red-first decision run (a scratch folder holding the manufacture tree's `rehearse_decision_v2.py`, the repaired
`run_rehearsal_v2.py` and `vp2-cp-results.xml.gz`): `python -B run_rehearsal_v2.py <ViewPrism2> <out>`. For C5:
`python -B repair-r1/redfirst_c5.py <scratch>` (from `bomdd/reports/eco-115-advance-decision/`).

Since inspection r4 (IA-13): r3 moved the bounds parser into `rehearse_decision_v2.py`, which this helper's first form neither copied nor patched, and it accepted any child failure; it now runs the self-verifying control of `../repair-r4/redfirst_all.py`. That script also re-runs the decision run above, staged with every file it imports, and checks it against its expected misses.
