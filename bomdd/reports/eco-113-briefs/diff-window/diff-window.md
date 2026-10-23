# ECO-113 diff window under the exception ruling — `f2d91d4..7a7df00`

ECO-113 `diff_audit.allowed_paths` (register at `7a7df00`): `method/tools/bomdd-run.py`, `method/tools/bomdd-job.py`, `method/templates/product-profile/operator-layer.md`, `method/improvements.md`, `bomdd/60-change-order-eco-113.md`, `bomdd/60-change-register.yaml`, `bomdd/reports/eco-113-refusal-matrix/`, `bomdd/reports/eco-113-probes/`, `bomdd/reports/eco-113-manufacture/`, `bomdd/reports/eco-113-briefs/`

| # | commit | attributed to | paths changed |
|---|---|---|---|
| 1 | `ced3ffc` | excluded | 3 |
| 2 | `3c7781c` | ECO-113 | 15 |
| 3 | `e394af0` | excluded | 1 |
| 4 | `4d2c05f` | excluded | 10 |
| 5 | `436f0c6` | excluded | 3 |
| 6 | `48f65ba` | excluded | 6 |
| 7 | `0b6a784` | excluded | 4 |
| 8 | `5ddd428` | excluded | 5 |
| 9 | `597e842` | excluded | 126 |
| 10 | `7a107bf` | excluded | 10 |
| 11 | `2271102` | excluded | 4 |
| 12 | `2752d18` | ECO-113 | 12 |
| 13 | `9163625` | ECO-113 | 3 |
| 14 | `860097d` | ECO-113 | 2 |
| 15 | `fcd9fd7` | ECO-113 | 11 |
| 16 | `7a7df00` | ECO-113 | 3 |

## C1 — excluded commits and why

- `ced3ffc` — ECO-112's commit — manufactured first by ECO-112 M1; ECO-113 is built on its verified tools. (record(eco-112): independent inspection r1 REJECT IA-01, IA-02 - both …)
- `e394af0` — ECO-112's commit — manufactured first by ECO-112 M1; ECO-113 is built on its verified tools. (design(eco-112): amendment for inspection r1 - B2 rolls back only the …)
- `4d2c05f` — ECO-112's commit — manufactured first by ECO-112 M1; ECO-113 is built on its verified tools. (fix(eco-112): repair manufacture for inspection r1 - the rollback remo…)
- `436f0c6` — ECO-112's commit — manufactured first by ECO-112 M1; ECO-113 is built on its verified tools. (record(eco-112): independent inspection r2 REJECT IA-03 - IA-01 and IA…)
- `48f65ba` — ECO-112's commit — manufactured first by ECO-112 M1; ECO-113 is built on its verified tools. (record(eco-112): exception ruling on the diff window - V6 and inspecti…)
- `0b6a784` — ECO-112's commit — manufactured first by ECO-112 M1; ECO-113 is built on its verified tools. (record(eco-112): V3 re-run on the repaired tool PASS - the pinned inst…)
- `5ddd428` — ECO-112's commit — manufactured first by ECO-112 M1; ECO-113 is built on its verified tools. (accept(eco-112): verified - r3 ACCEPT (IA-03 resolved under the except…)
- `597e842` — measurement record of ECO-112/113's review rounds (bomdd/reports/session-effort-20261018/, review-origin-20261018/) — no ECO's change. (record: session effort and review-finding origin measured for ECO-112/…)
- `7a107bf` — OBS-20261019-01's hook feasibility experiment (bomdd/reports/obs-20261019-01-hook-experiment/, improvements.md) — on hold, no ECO. (record(OBS-20261019-01): hook feasibility experiment - a temporary loc…)
- `2271102` — OBS-20261019-01's design premises (the same folder, improvements.md) — on hold, no ECO. (record(OBS-20261019-01): design premises for an ECO (user AGREE, premi…)

## C2 — the excluded commits against ECO-113's own records and register entry

- `ced3ffc`: ECO-113 records touched: none; ECO-113 register entry byte-identical: True
- `e394af0`: ECO-113 records touched: none; ECO-113 register entry byte-identical: True
- `4d2c05f`: ECO-113 records touched: none; ECO-113 register entry byte-identical: True
- `436f0c6`: ECO-113 records touched: none; ECO-113 register entry byte-identical: True
- `48f65ba`: ECO-113 records touched: none; ECO-113 register entry byte-identical: True
- `0b6a784`: ECO-113 records touched: none; ECO-113 register entry byte-identical: True
- `5ddd428`: ECO-113 records touched: none; ECO-113 register entry byte-identical: True
- `597e842`: ECO-113 records touched: none; ECO-113 register entry byte-identical: True
- `7a107bf`: ECO-113 records touched: none; ECO-113 register entry byte-identical: True
- `2271102`: ECO-113 records touched: none; ECO-113 register entry byte-identical: True

## C3 — the excluded commits precede ECO-113's manufacture; the manufacture's input

- ECO-113's filing: `3c7781c`; first ECO-113 commit after it: `2752d18`; excluded commits after that: none
- `method/tools/bomdd-run.py` at the input `2271102`: `69e849630f90` (order §4: `69e849630f90`) — equal
- `method/tools/bomdd-job.py` at the input `2271102`: `823eafd97d6f` (order §4: `823eafd97d6f`) — equal
- `method/templates/product-profile/operator-layer.md` at the input `2271102`: `589082d8dc48` (order §4: `589082d8dc48`) — equal

## C4 — the ECO-113 change set, enumerated (V8)

- `bomdd/60-change-order-eco-113.md` — 3c7781c, 2752d18, 9163625, 860097d, fcd9fd7, 7a7df00
- `bomdd/60-change-register.yaml` — 3c7781c, 2752d18
- `bomdd/reports/eco-113-briefs/diff-window/README.md` — fcd9fd7
- `bomdd/reports/eco-113-briefs/diff-window/diff_window.py` — 860097d
- `bomdd/reports/eco-113-briefs/inspection-brief-r1.md` — 9163625
- `bomdd/reports/eco-113-briefs/inspection-brief-r2.md` — 7a7df00
- `bomdd/reports/eco-113-briefs/inspection-r1.md` — 9163625
- `bomdd/reports/eco-113-briefs/inspection-r2.md` — 7a7df00
- `bomdd/reports/eco-113-manufacture/README.md` — 2752d18
- `bomdd/reports/eco-113-manufacture/repair/README.md` — fcd9fd7
- `bomdd/reports/eco-113-manufacture/repair/rule-mutations-eco-112.txt` — fcd9fd7
- `bomdd/reports/eco-113-manufacture/repair/rule-mutations.txt` — fcd9fd7
- `bomdd/reports/eco-113-manufacture/repair/selftest-bomdd-job.txt` — fcd9fd7
- `bomdd/reports/eco-113-manufacture/repair/selftest-bomdd-run.txt` — fcd9fd7
- `bomdd/reports/eco-113-manufacture/repair/selftest-bomdd-witness.txt` — fcd9fd7
- `bomdd/reports/eco-113-manufacture/rule-mutations-eco-112.txt` — 2752d18
- `bomdd/reports/eco-113-manufacture/rule-mutations.txt` — 2752d18
- `bomdd/reports/eco-113-manufacture/rule_mutations.py` — 2752d18, fcd9fd7
- `bomdd/reports/eco-113-manufacture/selftest-bomdd-job.txt` — 2752d18
- `bomdd/reports/eco-113-manufacture/selftest-bomdd-run.txt` — 2752d18
- `bomdd/reports/eco-113-manufacture/selftest-bomdd-witness.txt` — 2752d18
- `bomdd/reports/eco-113-probes/README.md` — 3c7781c
- `bomdd/reports/eco-113-probes/jobobject/jobholder.py` — 3c7781c
- `bomdd/reports/eco-113-probes/jobobject/jobprobe.py` — 3c7781c
- `bomdd/reports/eco-113-probes/jobobject/jobprobe2.py` — 3c7781c
- `bomdd/reports/eco-113-probes/jobobject/loop.py` — 3c7781c
- `bomdd/reports/eco-113-probes/oslock/holder.py` — 3c7781c
- `bomdd/reports/eco-113-probes/oslock/probe.py` — 3c7781c
- `bomdd/reports/eco-113-probes/reviewer/lockprobe.py` — 3c7781c
- `bomdd/reports/eco-113-probes/reviewer/r2probe.py` — 3c7781c
- `bomdd/reports/eco-113-refusal-matrix/calibrate_matrix.py` — 3c7781c
- `bomdd/reports/eco-113-refusal-matrix/record_check.py` — 3c7781c
- `bomdd/reports/eco-113-refusal-matrix/refusal-matrix.md` — 3c7781c
- `bomdd/reports/eco-113-refusal-matrix/refusal_matrix.py` — 3c7781c
- `method/improvements.md` — fcd9fd7
- `method/templates/product-profile/operator-layer.md` — 2752d18
- `method/tools/bomdd-job.py` — 2752d18
- `method/tools/bomdd-run.py` — 2752d18, fcd9fd7

ECO-113 commits: 6 (`3c7781c`, `2752d18`, `9163625`, `860097d`, `fcd9fd7`, `7a7df00`); paths: 38.

## C5 — the net diff from the manufacture's input to head

- `2271102..7a7df00`: 25 paths; equal to the union of ECO-113's commits after the input: True; outside the allowed paths: none

## Result

**PASS** — every check holds.
