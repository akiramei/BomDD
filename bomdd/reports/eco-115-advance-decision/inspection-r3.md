[INFORM / COMPLETE]
REJECT IA-11

1. FAIL — IA-08, IA-09 and IA-03 are resolved; IA-02/IA-10 remain incomplete because I3a and D5 disagree on otherwise identical bounds lines with trailing whitespace (IA-11).
2. PASS — all 20 changed paths are allowed; other manufactured files are unchanged; four rehearsals exited 0 and were byte-identical; real-data conclusions are unchanged; IA-01 and IA-04–IA-07 remain resolved; V1/V2 passed 120/120, while the `2aa2d7d` control exited 1 at 119/120 on the repaired I2 clause.
3. FAIL — all 36 README SHA-256 entries match committed bytes, and the register, diff and recorded executions otherwise agree. However, §8 and `repair-r2/README.md` incorrectly claim the domain is operationally closed (IA-11).

## Findings

### IA-11 — blocking — I3a and D5 parse trailing whitespace differently

Location: `bomdd/reports/eco-115-advance-decision/rehearse_decision_v2.py:54-60`; `rehearse_sequence.py:174-181`; closure claims at order `:536-543` and `repair-r2/README.md:17-18`.

Evidence: I3a validates `found[0].rstrip()`, while D5 applies `BOUNDS_LINE.fullmatch()` without the same normalization. A throwaway probe exhaustively confirmed agreement for all 998,001 declared numeric pairs, but found:

```text
trailing-space I3a=None D5={'holds': 3, 'decisions': 5}
trailing-tab   I3a=None D5={'holds': 3, 'decisions': 5}
trailing-nbsp  I3a=None D5={'holds': 3, 'decisions': 5}
```

Thus `- 前進の判定の上限: holds 999, decisions 999 ` passes I3a without `input-defect`, yet D5 silently applies defaults 3/5. This contradicts §1’s claim that every I2-valid line can be read and can cause the work to reach a bound prematurely.

The IA-09 independence repair itself passed: a probe combining malformed bounds with each applicable I3a failure retained both reasons in 44/44 cases.

Direction: use one shared parser/normalization rule for I3a and D5—either reject trailing whitespace in both or explicitly normalize it in both—and add paired space/tab/Unicode-whitespace boundary arms.

## Calibration receipt

- V1 presence claim: observed, conditionally qualified; current 120/120 and the `2aa2d7d` control 119/120.
- V2 full-rule claim: observed but not qualified because IA-11 leaves an accepted-input/effective-value mismatch.
- Instrument defect: IA-11.
- Negative controls: the r2 decision red-first exited 1 with three `MISSED`; the open-domain control reproduced the 5,000-digit `ValueError`; the C5 control produced Y6 BAD/Y7 OK.
- Detection limits: no shipped product integration, non-git delivery, remote CI, or exhaustive Unicode/spelling mutation was tested.
- Battery: Q1–Q7 and Q9–Q11 asked; Q8 NA.

## Out of range observations

- `git diff --check` reports trailing whitespace in `inspection-r2.md:75-76` and `repair-r2/redfirst-decision.txt:138`; this does not affect the verdict.
- Git emitted global-ignore permission warnings during sibling-repository status checks; neither sibling reported status entries.

## Not examined

- V4 self-conformance and remote CI.
- The older v1 rehearsal and basis-only measurement scripts.
- Product behavior beyond the fixed revisions used by the four specified rehearsals.
- Mechanical enforcement after distribution into a product repository.

Start HEAD: `7eddaba48d486b17bb6943d0d88e8eb3ef60df24`  
End HEAD: `7eddaba48d486b17bb6943d0d88e8eb3ef60df24`

Start/end `git status --short`: empty. Both sibling-product statuses were also empty. No repository or sibling-product files changed; no network was used.

Reasoning effort: not exposed to the inspector.

human_action: none. Execution: COMPLETE — the final repair-confirmation and regression inspection is finished.