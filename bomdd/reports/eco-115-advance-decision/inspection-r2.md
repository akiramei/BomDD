[INFORM / COMPLETE]
REJECT IA-08 IA-09 IA-10
1. FAIL — IA-01 PASS; IA-02 FAIL (IA-09/IA-10); IA-03 FAIL, non-blocking (IA-08); IA-04–IA-07 PASS. Evidence: repaired arms pass, while the manufacture-tree controls fail for their original reasons.
2. FAIL — all 24 changed paths are allowed; unchanged manufactured files retain identical blobs; four rehearsals exit 0 and are byte-identical; real-data conclusions are unchanged; V1/V2 is 120/120 and the `35961c3` control is 116/120. IA-09 is a repair-introduced regression.
3. FAIL — all 29 README SHA-256 entries match committed bytes, and register/diff/§5 otherwise agree; §6 and the repair README inaccurately call the inserted scale statement “L7’s scale” despite IA-08’s one-versus-two-delivery discrepancy.

## Findings

### IA-08 — non-blocking — the manufactured L7 scale differs from §1

Location: `bomdd/60-change-order-eco-115.md:320-321`; `method/bomdd-playbook-v1.md:333-334`; repair account at order `:494` and `repair-r1/README.md:17`.

Evidence: order L7 says MoviePad-Remake was rehearsed on “first per-delivery records (one delivery)”; the playbook says “納品 2 回の記録”. Thus IA-03’s direction to add L7’s measured scale was not reproduced faithfully, although the two-delivery statement matches the expanded D5 evidence.

Direction: choose the evidenced scale and make order §1 L7, the playbook, §6, and the repair README agree.

### IA-09 — blocking — malformed bounds short-circuit independent I3a checks

Location: `bomdd/reports/eco-115-advance-decision/rehearse_decision_v2.py:110-147`.

Evidence: the IA-02 repair uses `if bd: ... elif HEX40.fullmatch(frozen):`, so a bounds defect suppresses the ref/path, ancestry, and byte-binding checks. A throwaway probe combined `holds 0` with swapped `mbom_ref` and `control_plan_ref`; its complete defect output was only:

```text
[["work-order-fix", "the bounds line '- 前進の判定の上限: holds 0, decisions 5' is outside I2"]]
```

Without the malformed bounds, the existing swapped-ref arm reports the ref defects. This contradicts I3a’s requirement to list each failure and is introduced by the repair.

Direction: make bounds validation independent of the remaining I3a checks and add a combined malformed-bounds-plus-bad-refs arm.

### IA-10 — blocking — I2 accepts numeric values the D5 rehearsal cannot evaluate

Location: order `:124-125`; playbook `:219`; `rehearse_decision_v2.py:50-60`; `rehearse_sequence.py:176-181`.

Evidence: the declared domain permits any decimal integer of 1 or more. With a 5,000-digit positive `holds` value, `bounds_defect()` returns `None`, but `work_bounds()` raises:

```text
ValueError: Exceeds the limit (4300 digits) for integer string conversion
```

Thus an I2-valid bounds line has no rehearsal result, so the repaired domain is not operationally closed.

Direction: either place an explicit finite magnitude/digit bound in order §1, playbook, template, and I3a, or parse/compare arbitrarily long valid integers without this conversion failure; add boundary arms.

## Repair confirmation details

- IA-01: PASS — `method/bomdd-playbook-v1.md:681` limits the new-delivery rule to entry through D and preserves distribution-defined outside-D entry.
- IA-02: FAIL — ordinary malformed arms and Z1/Z2 pass, but IA-09 and IA-10 leave the rule incomplete.
- IA-03: FAIL, non-blocking — the scale limitation exists but disagrees with §1.
- IA-04: PASS — three ref/path arms pass; running the repaired driver with the manufacture-tree decision code produces three `MISSED` results.
- IA-05: PASS — Y6 reports C5 and Y7 stays green; the old C5 clause produces `Y6 BAD`, 41/42.
- IA-06: PASS — current output reports D4 written on every decided case; the manufacture-tree decision code reports it false.
- IA-07: PASS — all three drivers return nonzero on missed expectations, and the wrapper rejects `MISSED`/false summaries. The decision red-first run exited 1 with eight `MISSED`.

## Calibration receipt

- V1 presence claim: observed, conditionally qualified; current 120/120 and `35961c3` control 116/120.
- V2 full-rule claim: observed but not qualified because IA-09 and IA-10 leave false assurance paths.
- Instrument defects: IA-09 and IA-10.
- Detection limits: no shipped product integration, non-git delivery, remote CI, or exhaustive Unicode/spelling mutation was tested.
- Battery: Q1–Q7 and Q9–Q11 asked; Q8 NA.

## Out of range observations

- `git diff --check` reports trailing whitespace in `repair-r1/redfirst-decision.txt:133`; it does not affect this verdict.
- Git emitted global-ignore permission warnings during final sibling-repository status checks; all three status outputs contained no entries.

## Not examined

- V4 self-conformance and remote CI.
- The older v1 rehearsal and basis-only measurement scripts.
- Product behavior beyond the fixed revisions used by the four specified rehearsals.
- Mechanical enforcement after distribution into a product repository.

Start HEAD: `2aa2d7df9ec902f1c295f455c82ef78b3da6bb7a`  
End HEAD: `2aa2d7df9ec902f1c295f455c82ef78b3da6bb7a`  
Start/end `git status --short`: empty. No repository or sibling-product files changed; no network used.

Reasoning effort: not exposed to the inspector.

human_action: none. Execution: COMPLETE — repair confirmation and regression inspection finished.