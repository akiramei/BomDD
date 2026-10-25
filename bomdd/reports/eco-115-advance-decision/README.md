# ECO-115 basis and design evidence — the advance decision's inputs in two products, and the decision run on ViewPrism2's real data (read-only)

Measured and run 2026-10-24 for the filing of [ECO-115](../../60-change-order-eco-115.md) (held as a draft by the user's "3:A"; filed 2026-10-26) (§0 and the receipt). Nothing in either product repository was
written. Text files are LF; the sha256 values are of the bytes the commit stores.

| File | What | sha256 |
|---|---|---|
| `measure_cp_fields.py` | reads `bomdd/32-mbom.yaml` and `33-control-plan.yaml` with `git show`: ViewPrism2 at HEAD, ViewTube at `fc35bf1d` (its newest control plan revision that parses) | `3a1eb42063c8f80c77fca140bc705b8dfe9aef3b90cec8e6658d61eedc0df882` |
| `cp-fields.txt` | its output: ViewPrism2 at `504921a`, ViewTube at `fc35bf1d` | `b0d4937a601900342efff6180486bab8e50253666fe578df19f5e6a87f64b793` |
| `measure_inputs.py` | counts the named rows and units outside the decision's closed values (I2 as first filed; `when` was dropped in loop 2, the counts for `approver` and `on_fail` are unchanged) | `3927f67b7301a156e6e73dbf38b9cd8fac566f2e41f5e00f95bb9b36a596bd9a` |
| `inputs-outside-i2.txt` | its output | `a0203a208342b7e3a89965b666ddfa959485fa534ba61fcd8cd7f543e629dc97` |
| `vp2-cp-results.xml.gz` | ViewPrism2's stored `tests/ViewPrism2.Tests/TestResults/cp-results.xml` (untracked there), gzip with mtime 0; the XML's sha256 is `82c0258c98cf1643ced50d396eb09b0cfac01e583f401d5412027e51db3fdb4c` | `325d26d5456a6c987a5e531e222d8e56635cd7d28c84772fa13e3d26f1c84315` |
| `rehearse_decision.py` | I3a, I3b, D1, D2 and D4 as the order states them (design evidence; not shipped) | `d0eb486b0754a0cf28cb2f6227a9003e00a6a556e15bf681558f59c6b6504431` |
| `run_rehearsal.py` | runs the decision on ViewPrism2's BOM and Control Plan at `504921a` as they are and on a migrated copy (edits listed in its output; the freeze inputs constructed), R-050 (a)/(b) in unit/CP pairs on the records it writes, and 50 synthetic one-change cases (the base included) plus 7 inputs outside I1 | `31660d16d6e2178ac113a16c907177901830d3129ad7d6866c1adbf4cf858a68` |
| `rehearsal-real.txt` | its output | `26c663641df2c407bb748d08fd69b8d1ea76b4edb29a6f82d4509dd82441ee3a` |
| `draft-order.md` | the held ECO-115 draft until its filing (2026-10-26); now a pointer to `bomdd/60-change-order-eco-115.md`, its only copy | — |
| `measure_freeze.py` | whether each product's work order has the frozen-revision line and its As-Built the references the freeze check reads (HEAD, `git show`) | `1d1454282329984fde3c164756f28a7ff8705f7eb4a1f91d87be93c86cec6424` |
| `freeze-inputs.txt` | its output | `e530fc266debdc424010ee53e721adc5b8058080dd7f9f08e50b9c403d869967` |
| `rehearse_decision_v2.py` | loop 4 (redesign after EXP-20261024-01): the decision as the draft now states it — `frozen_commit` resolved at receipt, ancestry and frozen ≠ delivered, `delivered` `{commit, tree}` only, `identity` read from the evidence, the `line` format; after loop 4 round 1: git required, the tree checked, freeze ≤ issue, a failure no counted row owns; after the user's cut-off "A": the BOM equal at freeze and issue, implied clauses dropped, git missing still lists the rest, unowned failures route control-plan-fix | `15316ccefc48cea1f13de7da81be1a767fe55b4c53f7eaba17657eb182073ef8` |
| `run_rehearsal_v2.py` | its driver on ViewPrism2 (freeze = issue = `f697a82`, delivery `504921a`, ancestry and tree on ViewPrism2's git) and the synthetic cases on a stub git history and the synthetic cases | `a937e271e623f3178e996d1cd8691fe5a3ebffc78289da28c12ac845ac426c6b` |
| `rehearsal-v2.txt` | its output | `b6492a6948252ef668aa095ac694c1a8721193e67067280be9bf84108ac5b8ac` |
| `run_moviepad.py` | the decision on MoviePad-Remake delivery 1's real records (`git show`, read-only): M0 as they are, M1a/M1b a migrated copy (edits listed; M1b's stamp ASSUMED), M2 known-bad freezes, M3 known-bad evidence lines | `4234c507f07bdd7066610521810ba48f468e36011beefc0657011b6b2c8e5b83` |
| `rehearsal-moviepad.txt` | its output | `47e978e5d03936d6c79f6d5484fc837d021b603fdeca5feff5611f384825392c` |
| `run_moviepad_d2.py` | calibration on MoviePad-Remake delivery 2's real records (`b53f048`, AB-FORWARD-01-factory-02): N0 as written, N1 with only check_mapping and the decision records added, N2 three known-bad inputs | `05a33ef6442efd2d16bff99016111b94e00d488154c413347fa51e0ddf9272a8` |
| `rehearsal-moviepad-d2.txt` | its output | `35731c0b63302a557cb0322e7026538e4f1cc82f63f4d7c97125fad712c4a96c` |
| `rehearse_sequence.py` | D5 (loops 5-6): a work's decisions over time on the per-row ledger — convergence against the bounds, control signals C1-C6, the alternation candidate; 42 arms with expectations fixed in the script, including R1/R2 on MoviePad-Remake's two deliveries | `f1b7b4839c4aeb50c880a9b183cb0ef9a205a6f3167a274ced87f3fed05fcf55` |
| `rehearsal-sequence.txt` | its output (42/42 after inspection r1's repairs) | `b5d1fcf2e47089f7c01ca4d973782f8e7ad52bdb4a07b77b366591231d9811cb` |
| `inspection-brief-r1.md` | the committed copy of independent inspection r1's brief (EQ-002, range 境界探索; the stored brief has the same sha256) | `59530f9585a205db2534c1a385b081cf91360b37b5a6e276c09f5df2542c8dd6` |
| `inspection-r1.md` | inspection r1's report as the harness saved it: REJECT IA-01 to IA-07 | `b60b27fb44bb049ce95f21c8463fa52c8b3fdc38c92d206f1a578fd35e55fe26` |
| `repair-r1/` | the repairs after inspection r1: red-first runs, the control on the manufacture tree, V1/V2 after the repairs (its README) | — |

Commands (from this folder):

```
python measure_cp_fields.py ../../../../ViewPrism2 ../../../../ViewTube cp-fields.txt
python measure_inputs.py ../../../../ViewPrism2 ../../../../ViewTube inputs-outside-i2.txt
python -B run_rehearsal.py ../../../../ViewPrism2 rehearsal-real.txt
python -B measure_freeze.py ../../../../ViewPrism2 ../../../../ViewTube freeze-inputs.txt
python -B run_rehearsal_v2.py ../../../../ViewPrism2 rehearsal-v2.txt
python -B run_moviepad.py ../../../../MoviePad-Remake rehearsal-moviepad.txt
python -B run_moviepad_d2.py ../../../../MoviePad-Remake rehearsal-moviepad-d2.txt
python -B rehearse_sequence.py rehearsal-sequence.txt
```

MoviePad-Remake is local only (no remote yet); `run_moviepad.py` reads commits `7824ba9`, `f30d771`, `e1d71b3` and the tags `bom-v3`, `bom-v4`
there. Run with `PYTHONIOENCODING=utf-8` on a Windows console.
