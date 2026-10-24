# ECO-114 diff window under the exception ruling — `be96698..5ac2145`

ECO-114 `diff_audit.allowed_paths` (register at `5ac2145`): `method/bomdd-playbook-v1.md`, `method/templates/30-ebom.yaml`, `method/templates/32-mbom.yaml`, `method/templates/33-control-plan.yaml`, `method/prompts/phase3-design.md`, `method/improvements.md`, `bomdd/60-change-order-eco-114.md`, `bomdd/60-change-register.yaml`, `bomdd/reports/eco-114-part-standard/`

| # | commit | attributed to | paths changed |
|---|---|---|---|
| 1 | `25bea38` | ECO-114 | 13 |
| 2 | `afabdb1` | excluded | 12 |
| 3 | `286d02c` | ECO-114 | 13 |
| 4 | `5bc708a` | ECO-114 | 4 |
| 5 | `faffcf9` | ECO-114 | 13 |
| 6 | `45fcc66` | ECO-114 | 4 |
| 7 | `c221153` | ECO-114 | 7 |
| 8 | `5ac2145` | ECO-114 | 4 |

## C1 — excluded commits and why

- `afabdb1` — ECO-115's held design draft kept as a record (bomdd/reports/eco-115-advance-decision/) - not filed, no ECO's change. (record(bomdd): ECO-115 design held unconverged by the user's "3:A" - t…)

## C2 — the excluded commits against ECO-114's own records and register entry

- `afabdb1`: ECO-114 records touched: none; ECO-114 register entry byte-identical: True

## C3 — the excluded commits precede ECO-114's manufacture; the manufacture's input

- ECO-114's filing: `25bea38`; first ECO-114 commit after it: `286d02c`; excluded commits after that: none
- `method/bomdd-playbook-v1.md` at the input `afabdb1`: `eb52d1200143` (order §4: `eb52d1200143`) — equal
- `method/templates/30-ebom.yaml` at the input `afabdb1`: `b203de2c40f2` (order §4: `b203de2c40f2`) — equal
- `method/templates/32-mbom.yaml` at the input `afabdb1`: `9d5a58b4466f` (order §4: `9d5a58b4466f`) — equal
- `method/templates/33-control-plan.yaml` at the input `afabdb1`: `838ee238911e` (order §4: `838ee238911e`) — equal
- `method/prompts/phase3-design.md` at the input `afabdb1`: `efbfbb76e75f` (order §4: `efbfbb76e75f`) — equal

## C4 — the ECO-114 change set, enumerated (V8)

- `bomdd/60-change-order-eco-114.md` — 25bea38, 286d02c, 5bc708a, faffcf9, 45fcc66, c221153, 5ac2145
- `bomdd/60-change-register.yaml` — 25bea38, 286d02c, 5bc708a, faffcf9, 45fcc66, c221153, 5ac2145
- `bomdd/reports/eco-114-part-standard/README.md` — 25bea38
- `bomdd/reports/eco-114-part-standard/diff-window/README.md` — faffcf9
- `bomdd/reports/eco-114-part-standard/diff-window/control-include-afabdb1.md` — faffcf9
- `bomdd/reports/eco-114-part-standard/diff-window/diff-window-to-r1.md` — faffcf9
- `bomdd/reports/eco-114-part-standard/diff-window/diff_window.py` — faffcf9
- `bomdd/reports/eco-114-part-standard/inspection-brief-r1.md` — 5bc708a
- `bomdd/reports/eco-114-part-standard/inspection-brief-r2.md` — 45fcc66
- `bomdd/reports/eco-114-part-standard/inspection-brief-r3.md` — 5ac2145
- `bomdd/reports/eco-114-part-standard/inspection-r1.md` — 5bc708a
- `bomdd/reports/eco-114-part-standard/inspection-r2.md` — 45fcc66
- `bomdd/reports/eco-114-part-standard/inspection-r3.md` — 5ac2145
- `bomdd/reports/eco-114-part-standard/manufacture/README.md` — 286d02c, faffcf9, c221153
- `bomdd/reports/eco-114-part-standard/manufacture/check_v1_v2.py` — 286d02c, faffcf9, c221153
- `bomdd/reports/eco-114-part-standard/manufacture/rehearsal-at-manufacture.txt` — 286d02c
- `bomdd/reports/eco-114-part-standard/manufacture/v1-mutations.txt` — faffcf9, c221153
- `bomdd/reports/eco-114-part-standard/manufacture/v1-v2-control-before-manufacture.txt` — 286d02c, faffcf9, c221153
- `bomdd/reports/eco-114-part-standard/manufacture/v1-v2.txt` — 286d02c, faffcf9, c221153
- `bomdd/reports/eco-114-part-standard/measure.py` — 25bea38
- `bomdd/reports/eco-114-part-standard/measurements.txt` — 25bea38
- `bomdd/reports/eco-114-part-standard/rehearsal-bom.yaml` — 25bea38
- `bomdd/reports/eco-114-part-standard/rehearsal.txt` — 25bea38
- `bomdd/reports/eco-114-part-standard/rehearse_part.py` — 25bea38
- `bomdd/reports/eco-114-part-standard/run_rehearsal.py` — 25bea38
- `bomdd/reports/eco-114-part-standard/shapes.py` — 25bea38
- `bomdd/reports/eco-114-part-standard/shapes.txt` — 25bea38
- `bomdd/reports/eco-114-part-standard/vp2-cp-results-summary.txt` — 25bea38
- `bomdd/reports/eco-114-part-standard/vp2-cp-results.json` — 25bea38
- `method/bomdd-playbook-v1.md` — 286d02c, faffcf9
- `method/improvements.md` — 286d02c, faffcf9
- `method/prompts/phase3-design.md` — 286d02c
- `method/templates/30-ebom.yaml` — 286d02c
- `method/templates/32-mbom.yaml` — 286d02c
- `method/templates/33-control-plan.yaml` — 286d02c

ECO-114 commits: 7 (`25bea38`, `286d02c`, `5bc708a`, `faffcf9`, `45fcc66`, `c221153`, `5ac2145`); paths: 35.

## C5 — the net diff from the manufacture's input to head

- `afabdb1..5ac2145`: 24 paths; equal to the union of ECO-114's commits after the input: True; outside the allowed paths: none

## Result

**PASS** — every check holds.
