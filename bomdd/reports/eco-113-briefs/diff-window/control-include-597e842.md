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
| 9 | `597e842` | ECO-113 | 126 |
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
- `7a107bf`: ECO-113 records touched: none; ECO-113 register entry byte-identical: True
- `2271102`: ECO-113 records touched: none; ECO-113 register entry byte-identical: True

## C3 — the excluded commits precede ECO-113's manufacture; the manufacture's input

- ECO-113's filing: `3c7781c`; first ECO-113 commit after it: `597e842`; excluded commits after that: ['7a107bf', '2271102']
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
- `bomdd/reports/review-origin-20261018/README.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/anchors/112-0b6a784.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/anchors/112-19243e5.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/anchors/112-436f0c6.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/anchors/112-48f65ba.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/anchors/112-4d2c05f.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/anchors/112-5ddd428.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/anchors/112-ced3ffc.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/anchors/112-e394af0.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/anchors/112-f2d91d4.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/anchors/113-3c7781c.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/anchors/index.json` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/baseline/3a9de06--AGENTS.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/baseline/3a9de06--bomdd_60-change-register.yaml` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/baseline/3a9de06--method_templates_60-change-register.yaml` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/baseline/3a9de06--method_templates_product-profile_operator-layer.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/baseline/3a9de06--method_tools_bomdd-job.py` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/baseline/3a9de06--method_tools_bomdd-run.py` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/baseline/3a9de06--method_tools_bomdd-witness.py` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/baseline/order-eco-112.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/baseline/order-eco-113.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/control-drop-edit-38.txt` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/extract_primary.py` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/findings.jsonl` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/make_anchors.py` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/measure_origin.py` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/edits.jsonl` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history.json` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v10` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v11` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v12` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v2` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v3` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v4` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v5` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v6` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v7` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v8` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v9` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/6aec2b20f6061e17_at_v1` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/6aec2b20f6061e17_at_v2` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/6aec2b20f6061e17_at_v3` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/7789ce16d0a36d94_at_v2` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/7789ce16d0a36d94_at_v3` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/7789ce16d0a36d94_at_v4` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/7789ce16d0a36d94_at_v5` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/7789ce16d0a36d94_at_v6` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/file-history/7789ce16d0a36d94_at_v8` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/reviews.jsonl` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/132-112.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/137-112.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/137-113.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/144-113.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/149-113.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/153-113.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/155-112.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/161-113.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/165-113.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/170-113.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/173-113.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/206-113.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/218-113s.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/219-113s.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/227-113s.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/233-113s.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/238-113s.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/334-113s.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/337-113s.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/354-112.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/355-112.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/361-112.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/365-112.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/374-112.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/394-112.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/520-112.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/88-112.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/97-112.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/failures.json` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/shell-replays/index.json` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/primary/sources.json` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/rebuild_versions.py` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/round_map.json` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/summary.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions.json` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-A2R1.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-A2R2.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-A2R3.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-A2R4.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-AR1.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-AR2.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-AR3.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L1R1.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L1R2.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L1R3.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L2R1.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L2R2.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L2R3.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L3R1.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L3R2.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L3R3.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L4R1.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L4R2.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L4R3.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L5R1.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L5R2.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L5R3.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-112-L5R4.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-113-L1R1.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-113-L1R2.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-113-L1R3.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-113-L2R1.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-113-L2R2.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-113-L2R3.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-113-L3R1.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-113-L3R2.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-113-L3R3.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-113-L4R1.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-113-L4R2.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-113-L4R3.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-113-L5R1.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-113-L5R2.md` — 597e842 **OUTSIDE**
- `bomdd/reports/review-origin-20261018/versions/ECO-113-L5R3.md` — 597e842 **OUTSIDE**
- `bomdd/reports/session-effort-20261018/effort-summary.md` — 597e842 **OUTSIDE**
- `bomdd/reports/session-effort-20261018/effort.md` — 597e842 **OUTSIDE**
- `bomdd/reports/session-effort-20261018/session_effort.py` — 597e842 **OUTSIDE**
- `method/improvements.md` — 597e842, fcd9fd7
- `method/templates/product-profile/operator-layer.md` — 2752d18
- `method/tools/bomdd-job.py` — 2752d18
- `method/tools/bomdd-run.py` — 2752d18, fcd9fd7

ECO-113 commits: 7 (`3c7781c`, `597e842`, `2752d18`, `9163625`, `860097d`, `fcd9fd7`, `7a7df00`); paths: 163.

## C5 — the net diff from the manufacture's input to head

- `2271102..7a7df00`: 25 paths; equal to the union of ECO-113's commits after the input: True; outside the allowed paths: none

## Result

**FAIL**
- C3: excluded commits after ECO-113's manufacture began: ['7a107bf', '2271102']
- C4: bomdd/reports/review-origin-20261018/README.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/anchors/112-0b6a784.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/anchors/112-19243e5.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/anchors/112-436f0c6.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/anchors/112-48f65ba.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/anchors/112-4d2c05f.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/anchors/112-5ddd428.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/anchors/112-ced3ffc.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/anchors/112-e394af0.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/anchors/112-f2d91d4.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/anchors/113-3c7781c.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/anchors/index.json outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/baseline/3a9de06--AGENTS.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/baseline/3a9de06--bomdd_60-change-register.yaml outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/baseline/3a9de06--method_templates_60-change-register.yaml outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/baseline/3a9de06--method_templates_product-profile_operator-layer.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/baseline/3a9de06--method_tools_bomdd-job.py outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/baseline/3a9de06--method_tools_bomdd-run.py outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/baseline/3a9de06--method_tools_bomdd-witness.py outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/baseline/order-eco-112.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/baseline/order-eco-113.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/control-drop-edit-38.txt outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/extract_primary.py outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/findings.jsonl outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/make_anchors.py outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/measure_origin.py outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/edits.jsonl outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history.json outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v10 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v11 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v12 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v2 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v3 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v4 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v5 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v6 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v7 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v8 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/6035726b6a9bc78f_at_v9 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/6aec2b20f6061e17_at_v1 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/6aec2b20f6061e17_at_v2 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/6aec2b20f6061e17_at_v3 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/7789ce16d0a36d94_at_v2 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/7789ce16d0a36d94_at_v3 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/7789ce16d0a36d94_at_v4 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/7789ce16d0a36d94_at_v5 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/7789ce16d0a36d94_at_v6 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/file-history/7789ce16d0a36d94_at_v8 outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/reviews.jsonl outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/132-112.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/137-112.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/137-113.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/144-113.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/149-113.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/153-113.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/155-112.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/161-113.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/165-113.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/170-113.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/173-113.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/206-113.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/218-113s.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/219-113s.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/227-113s.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/233-113s.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/238-113s.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/334-113s.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/337-113s.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/354-112.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/355-112.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/361-112.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/365-112.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/374-112.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/394-112.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/520-112.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/88-112.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/97-112.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/failures.json outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/shell-replays/index.json outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/primary/sources.json outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/rebuild_versions.py outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/round_map.json outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/summary.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions.json outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-A2R1.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-A2R2.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-A2R3.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-A2R4.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-AR1.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-AR2.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-AR3.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L1R1.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L1R2.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L1R3.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L2R1.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L2R2.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L2R3.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L3R1.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L3R2.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L3R3.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L4R1.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L4R2.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L4R3.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L5R1.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L5R2.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L5R3.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-112-L5R4.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-113-L1R1.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-113-L1R2.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-113-L1R3.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-113-L2R1.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-113-L2R2.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-113-L2R3.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-113-L3R1.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-113-L3R2.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-113-L3R3.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-113-L4R1.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-113-L4R2.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-113-L4R3.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-113-L5R1.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-113-L5R2.md outside allowed_paths
- C4: bomdd/reports/review-origin-20261018/versions/ECO-113-L5R3.md outside allowed_paths
- C4: bomdd/reports/session-effort-20261018/effort-summary.md outside allowed_paths
- C4: bomdd/reports/session-effort-20261018/effort.md outside allowed_paths
- C4: bomdd/reports/session-effort-20261018/session_effort.py outside allowed_paths
