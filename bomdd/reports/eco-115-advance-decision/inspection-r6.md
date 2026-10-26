[INFORM / COMPLETE]
ACCEPT

1. PASS — IA-14 and IA-15 resolved. `repair-r4/redfirst_all.py:48-84,123-165` produced 5/5 exact revision-specific signatures with clean expected output and refused 2/2 wrong setups. V1/V2 passed 144/144. The repeated IA-15 `| maintainer` probe failed 141/144; built-in added/removed-value mutations were all caught (`manufacture/check_v1_v2.py:196-279`).
2. PASS — Regression. The range changed 13 paths, all within ECO-115 `diff_audit.allowed_paths`; `method/` and its templates are unchanged. All four rehearsals exited 0 and were byte-identical to committed outputs. IA-01–IA-13 remain resolved.
3. PASS — Records. Order §14 (`bomdd/60-change-order-eco-115.md:658`), register (`bomdd/60-change-register.yaml:3615`), diff, and evidence agree. All 54 SHA-256 entries across the evidence READMEs match committed bytes.

Findings: none.

## Run record

- Start HEAD: `47b4df7637157392705a498fd2687e426f5474f0`
- End HEAD: `47b4df7637157392705a498fd2687e426f5474f0`
- BomDD start/end status: empty.
- ViewPrism2 and MoviePad-Remake end status: empty.
- V1/V2: exit 0, 144/144.
- Rehearsal hashes matched: `ab2df806…`, `47e978e5…`, `35731c0b…`, `e741a9bd…`.
- Red-first: 5/5 signatures; 2/2 wrong setups refused.

## Calibration receipt

- IA-14 repair: observed, qualified.
- IA-15 repair: observed, qualified.
- Regression and records: observed, qualified within the specified revisions and narrowed range.
- Instrument defects detected: none.
- Battery: Q1–Q7 asked; Q8 NA; Q9–Q11 asked.
- Detection limits: fixed revisions and declared mutations only; no exhaustive setup mutation, distributed-product enforcement, or remote CI.

## Out of range observations

- Initial V1/V2 and red-first attempts were unmeasurable because Git rejected sibling/BomDD ownership. They were not counted; both were rerun successfully using process-local `safe.directory`.
- Sibling status checks emitted global-ignore permission warnings but exited 0 with no status entries.

## Not examined

- New defect classes beyond IA-14/IA-15.
- V4 self-conformance and remote CI.
- Product behavior beyond the four fixed rehearsals.
- Enforcement after distribution.

Reasoning effort: not exposed to the inspector.

human_action: none. Execution: COMPLETE — r6 repair confirmation and regression inspection finished.