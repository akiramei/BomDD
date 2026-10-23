# ECO-115 basis and design evidence — the advance decision's inputs in two products, and the decision run on ViewPrism2's real data (read-only)

Measured and run 2026-10-24 for the filing of [the ECO-115 draft](draft-order.md) (not filed; held by the user's "3:A") (§0 and the receipt). Nothing in either product repository was
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
| `draft-order.md` | the ECO-115 design draft as held (not filed; D3 reverted to the ruling "2:A"), with its basis, rules, acceptance and the converge receipt of all loops | — |
| `measure_freeze.py` | whether each product's work order has the frozen-revision line and its As-Built the references the freeze check reads (HEAD, `git show`) | `1d1454282329984fde3c164756f28a7ff8705f7eb4a1f91d87be93c86cec6424` |
| `freeze-inputs.txt` | its output | `e530fc266debdc424010ee53e721adc5b8058080dd7f9f08e50b9c403d869967` |

Commands (from this folder):

```
python measure_cp_fields.py ../../../../ViewPrism2 ../../../../ViewTube cp-fields.txt
python measure_inputs.py ../../../../ViewPrism2 ../../../../ViewTube inputs-outside-i2.txt
python -B run_rehearsal.py ../../../../ViewPrism2 rehearsal-real.txt
python -B measure_freeze.py ../../../../ViewPrism2 ../../../../ViewTube freeze-inputs.txt
```
