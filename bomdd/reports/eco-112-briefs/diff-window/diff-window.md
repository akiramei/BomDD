# ECO-112 diff window under the exception ruling — `3a9de06..436f0c6ec010`

ECO-112 `diff_audit.allowed_paths` (register at `436f0c6ec010`): `method/tools/bomdd-run.py`, `method/tools/bomdd-job.py`, `method/templates/60-change-register.yaml`, `method/templates/product-profile/operator-layer.md`, `method/improvements.md`, `bomdd/60-change-order-eco-112.md`, `bomdd/60-change-register.yaml`, `bomdd/reports/eco-112-arm-inventory/`, `bomdd/reports/eco-112-briefs/`

| commit | attributed to | paths changed |
|---|---|---|
| `19243e5` | ECO-112 | 7 |
| `d762270` | ECO-112 | 1 |
| `f2d91d4` | ECO-112 | 15 |
| `ced3ffc` | ECO-112 | 3 |
| `3c7781c` | ECO-113 | 15 |
| `e394af0` | ECO-112 | 1 |
| `4d2c05f` | ECO-112 | 10 |
| `436f0c6` | ECO-112 | 3 |

## Excluded commits (C1) and why

- `3c7781c` — ECO-113: file(eco-113): in-flight runs - an OS file lock, a kill-on-close Job Object owning the cell, judgeme… — another ECO's filing, outside ECO-112's manufacture (user ruling 2026-10-18 "A").

## C2 — the excluded commits against ECO-112's paths and register entry

- `3c7781c`: paths inside ECO-112's allowed paths: ['bomdd/60-change-register.yaml']
  - register: removed lines 0; added hunks [(3553, 29)] inside ECO-113's entry (lines 3553-3581): True; ECO-112 entry byte-identical before/after: True

## C3 — paths the excluded commits introduced, after them

- `3c7781c`: 14 paths; touched by an ECO-112 commit: none; changed between `3c7781c` and head: none

## C4 — the ECO-112 change set, enumerated (V6)

- `bomdd/60-change-order-eco-112.md` — 19243e5, f2d91d4, ced3ffc, e394af0, 4d2c05f, 436f0c6
- `bomdd/60-change-register.yaml` — 19243e5, f2d91d4
- `bomdd/reports/eco-112-arm-inventory/README.md` — 19243e5, d762270
- `bomdd/reports/eco-112-arm-inventory/arm-inventory.json` — 19243e5
- `bomdd/reports/eco-112-arm-inventory/arm_inventory.py` — 19243e5
- `bomdd/reports/eco-112-arm-inventory/arm_inventory_v2.py` — 19243e5
- `bomdd/reports/eco-112-arm-inventory/manufacture/README.md` — f2d91d4
- `bomdd/reports/eco-112-arm-inventory/manufacture/repair/README.md` — 4d2c05f
- `bomdd/reports/eco-112-arm-inventory/manufacture/repair/rule-mutations.txt` — 4d2c05f
- `bomdd/reports/eco-112-arm-inventory/manufacture/repair/rule_mutations.py` — 4d2c05f
- `bomdd/reports/eco-112-arm-inventory/manufacture/repair/selftest-bomdd-job.txt` — 4d2c05f
- `bomdd/reports/eco-112-arm-inventory/manufacture/repair/selftest-bomdd-run.txt` — 4d2c05f
- `bomdd/reports/eco-112-arm-inventory/manufacture/repair/selftest-bomdd-witness.txt` — 4d2c05f
- `bomdd/reports/eco-112-arm-inventory/manufacture/rule-mutations.txt` — f2d91d4
- `bomdd/reports/eco-112-arm-inventory/manufacture/rule_mutations.py` — f2d91d4
- `bomdd/reports/eco-112-arm-inventory/manufacture/selftest-bomdd-job.txt` — f2d91d4
- `bomdd/reports/eco-112-arm-inventory/manufacture/selftest-bomdd-run.txt` — f2d91d4
- `bomdd/reports/eco-112-arm-inventory/manufacture/selftest-bomdd-witness.txt` — f2d91d4
- `bomdd/reports/eco-112-arm-inventory/manufacture/selftest-exits.txt` — f2d91d4
- `bomdd/reports/eco-112-arm-inventory/manufacture/v3-inputs.sha256` — f2d91d4
- `bomdd/reports/eco-112-arm-inventory/manufacture/v3-run1-arm-inventory.json` — 4d2c05f
- `bomdd/reports/eco-112-arm-inventory/manufacture/v3-run1-summary.txt` — 4d2c05f
- `bomdd/reports/eco-112-arm-inventory/summary.txt` — 19243e5
- `bomdd/reports/eco-112-briefs/inspection-brief-r1.md` — ced3ffc
- `bomdd/reports/eco-112-briefs/inspection-brief-r2.md` — 436f0c6
- `bomdd/reports/eco-112-briefs/inspection-r1.md` — ced3ffc
- `bomdd/reports/eco-112-briefs/inspection-r2.md` — 436f0c6
- `method/improvements.md` — f2d91d4
- `method/templates/60-change-register.yaml` — f2d91d4
- `method/templates/product-profile/operator-layer.md` — f2d91d4
- `method/tools/bomdd-job.py` — f2d91d4
- `method/tools/bomdd-run.py` — f2d91d4, 4d2c05f

ECO-112 commits: 7 (`19243e5`, `d762270`, `f2d91d4`, `ced3ffc`, `e394af0`, `4d2c05f`, `436f0c6`); paths: 32.

## C5 — the net diff without the excluded commits' own entries

- net paths (excluded commits' own paths removed): 32; outside ECO-112's allowed paths: none
- register with the excluded ECOs' entries removed: everything outside the ECO-112 entry equals the baseline: True

## Result

**PASS** — every check holds.
