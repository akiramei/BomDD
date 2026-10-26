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
| `rehearse_decision_v2.py` | loop 4 (redesign after EXP-20261024-01): the decision as the draft now states it — `frozen_commit` resolved at receipt, ancestry and frozen ≠ delivered, `delivered` `{commit, tree}` only, `identity` read from the evidence, the `line` format; after loop 4 round 1: git required, the tree checked, freeze ≤ issue, a failure no counted row owns; after the user's cut-off "A": the BOM equal at freeze and issue, implied clauses dropped, git missing still lists the rest, unowned failures route control-plan-fix | `07109636808d96e328a02688d5856d0c1323013c58af590aa8157bcb5790ca26` |
| `run_rehearsal_v2.py` | its driver on ViewPrism2 (freeze = issue = `f697a82`, delivery `504921a`, ancestry and tree on ViewPrism2's git) and the synthetic cases on a stub git history and the synthetic cases | `f56f0e744ee48e3d8fc6f9b89d8ec6844f2faaec154a7100e53043d9c3d2327f` |
| `rehearsal-v2.txt` | its output | `ab2df806dc40d22efee02866207b9b2ab0ec93f6b2d45c58e6be179f50e05c6d` |
| `run_moviepad.py` | the decision on MoviePad-Remake delivery 1's real records (`git show`, read-only): M0 as they are, M1a/M1b a migrated copy (edits listed; M1b's stamp ASSUMED), M2 known-bad freezes, M3 known-bad evidence lines | `4234c507f07bdd7066610521810ba48f468e36011beefc0657011b6b2c8e5b83` |
| `rehearsal-moviepad.txt` | its output | `47e978e5d03936d6c79f6d5484fc837d021b603fdeca5feff5611f384825392c` |
| `run_moviepad_d2.py` | calibration on MoviePad-Remake delivery 2's real records (`b53f048`, AB-FORWARD-01-factory-02): N0 as written, N1 with only check_mapping and the decision records added, N2 three known-bad inputs | `05a33ef6442efd2d16bff99016111b94e00d488154c413347fa51e0ddf9272a8` |
| `rehearsal-moviepad-d2.txt` | its output | `35731c0b63302a557cb0322e7026538e4f1cc82f63f4d7c97125fad712c4a96c` |
| `rehearse_sequence.py` | D5 (loops 5-6): a work's decisions over time on the per-row ledger — convergence against the bounds, control signals C1-C6, the alternation candidate; 45 arms with expectations fixed in the script, including R1/R2 on MoviePad-Remake's two deliveries | `2fa6143b556ccb487d95bedd6edd7b94b896dac94ec118cbd49501a733372c9c` |
| `rehearsal-sequence.txt` | its output (45/45 after inspection r3's repair) | `e741a9bd88d13dc94fdaf8145c122a4d43c6b229167b10f7a2bc284e447a4ced` |
| `inspection-brief-r1.md` | the committed copy of independent inspection r1's brief (EQ-002, range 境界探索; the stored brief has the same sha256) | `59530f9585a205db2534c1a385b081cf91360b37b5a6e276c09f5df2542c8dd6` |
| `inspection-r1.md` | inspection r1's report as the harness saved it: REJECT IA-01 to IA-07 | `b60b27fb44bb049ce95f21c8463fa52c8b3fdc38c92d206f1a578fd35e55fe26` |
| `repair-r1/` | the repairs after inspection r1: red-first runs, the control on the manufacture tree, V1/V2 after the repairs (its README) | — |
| `inspection-brief-r2.md` | the committed copy of independent inspection r2's brief (EQ-002, range 是正確認+回帰; the stored brief has the same sha256) | `28baf7e52a77a4f8ef4c5051205552acde13a1938d2138cfb852589532b26410` |
| `inspection-r2.md` | inspection r2's report as the harness saved it: REJECT IA-08 to IA-10 (IA-01 and IA-04 to IA-07 confirmed resolved) | `2e1c73685c430ea10ab714bf8a17e006807f83bc2fd3370510d552fda6fa67b6` |
| `repair-r2/` | the repairs after inspection r2: red-first runs, the control on the tree of r1's repairs, V1/V2 after the repairs (its README) | — |
| `inspection-brief-r3.md` | the committed copy of independent inspection r3's brief (EQ-002, range 是正確認+回帰; the stored brief has the same sha256) | `61b3d8617ee7cc564803c00400aee46ac5a4987057b521aac59b13139ff83f5d` |
| `inspection-r3.md` | inspection r3's report as the harness saved it: REJECT IA-11, at the review loop's bound | `86bc522e37c64c3ec24c47e353e4938b11d860daed6f14b3269188ec621eccdc` |
| `repair-r3/` | the repair after inspection r3 under the user's "A": red-first run, the control on the tree of r2's repairs, V1/V2 (its README) | — |
| `inspection-brief-r4.md` | the committed copy of independent inspection r4's brief (EQ-002, range 是正確認+回帰; the extension round) | `88bc75f933064ee4f433b64a25027d79f272e611c885ade97552bc520d3cd2f1` |
| `inspection-r4.md` | inspection r4's report: REJECT IA-12, IA-13, at the extended bound | `b7f01551303e3cf045bbe69abdb56685f1a4c958e9d0b8f8a1846ac1c062b7e6` |

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
