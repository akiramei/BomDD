[INFORM / COMPLETE]
REJECT IA-12 IA-13

1. FAIL (blocking) — IA-11’s line-end repair works, but IA-10 remains incomplete because the work-order template omits the no-leading-zero rule.
2. FAIL (blocking) — Scope, four rehearsals, real-data results, and the `7eddaba` control pass their checks, but r3 broke two earlier red-first procedures.
3. FAIL (blocking) — Hashes and ledger records agree, but §10 overstates textual consistency and the r1/r2 READMEs now give stale procedures.

## Findings

### IA-12 — blocking — work-order template does not state IA-10’s lexical domain

Location: `bomdd/60-change-order-eco-115.md:124-127,538`; `method/bomdd-playbook-v1.md:219`; `method/templates/40-work-order.md:8`; `manufacture/check_v1_v2.py:80,178`.

Evidence: §1 and the playbook require integers from 1–999 “without leading zeros.” The template says only “1 以上 999 以下の 10 進の整数,” which does not exclude `04`. The current implementation rejects `holds 04, decisions 7` as outside I2 and D5 uses defaults `3/5`. V1 still reports 120/120 because it checks the full clause only in the playbook and merely checks that the template contains a bounds line.

Direction: add the no-leading-zero lexical rule to the template comment and make V1 check the template’s complete form, values, and line-end contract.

### IA-13 — blocking — r3 made the r1/r2 red-first controls fail for unrelated setup reasons

Location: `rehearse_sequence.py:43-47,182-183`; `repair-r1/redfirst_c5.py:6-15` and `repair-r1/README.md:24-26`; `repair-r2/redfirst_domain.py:9-18` and `repair-r2/README.md:20-22`.

Evidence:

- Running the r1 C5 command as documented produced only `exit 1`: the scratch sequence now imports `rehearse_decision_v2`, which the procedure does not copy. The helper suppresses stderr and exits 0 itself, so this unrelated failure can masquerade as a successful negative control.
- Running the r2 domain command as documented exited 1 at `assert s.count(closed) == 1`; r3 moved the regex from `rehearse_sequence.py` into the shared parser.
- With the missing dependency staged, the C5 control correctly produced `Y6 BAD`, `Y7 OK`, 44/45.
- Mutating the new shared parser instead correctly reproduced IA-10’s 5,000-digit `ValueError`.

Direction: update both helpers and READMEs for the shared-parser layout, and make each helper verify the expected failure signature rather than accepting any child failure.

## Confirmed evidence

- IA-11 implementation: `parse_bounds` is shared by I3a and D5.
- Independent probe: all 998,001 valid numeric pairs agreed; five ASCII space/tab endings agreed; 28 other Unicode whitespace characters, six other trailing characters, and seven invalid value forms were rejected consistently.
- r3 red-first against `7eddaba`: exit 1 for the intended reason; output SHA-256 exactly `bf70f0ae…`, with NBSP/ideographic-space misses and failed 84-line agreement.
- Current V1/V2: exit 0, 120/120.
- Control on `7eddaba`: exit 1, 119/120, solely missing the line-end clause.
- Four rehearsals: all exit 0 and are byte-identical to their stored outputs; D5 is 45/45.
- All 18 paths in `7eddaba..11982a4` and all 38 paths in `35961c3..11982a4` are within `diff_audit.allowed_paths`.
- All 41 SHA-256 entries across the five READMEs match committed bytes.
- IA-01–IA-09 remain resolved; IA-10 is operationally closed in code but not consistently stated in the template.

## Calibration receipt

- IA-11 repair claim: observed and qualified by current/known-bad paired runs.
- V1 completeness claim: observed but not qualified because IA-12 is outside its effective coverage.
- Regression-control claim: observed but not qualified because of IA-13.
- Instrument defects: IA-12’s V1 coverage gap and IA-13’s stale controls.
- Battery: Q1–Q7 and Q9–Q11 asked; Q8 NA.
- Limits: no shipped product integration, non-git delivery, remote CI, or mechanical distribution enforcement was tested.

## Preflight receipt

Classification: bug-fix/continuation inspection. Target specimen, failing behavior, expected behavior, and acceptance target were confirmed from the brief, ECO, register, and r1–r3 reports. Decision: PROCEED; overrides: none.

## Records

Start HEAD: `11982a45097fa6418b04eb6df32a689be0ed78d0`  
End HEAD: `11982a45097fa6418b04eb6df32a689be0ed78d0`

End status: BomDD, ViewPrism2, and MoviePad-Remake all had zero status entries. No repository or sibling-product files changed; no network was used.

## Out of range observations

- `git diff --check` still reports historical trailing whitespace in `inspection-r3.md` and its red-first transcript.
- Sibling status checks emitted global-ignore permission warnings but completed with empty status output.

## Not examined

- V4 self-conformance and remote CI.
- The older v1 rehearsal and basis-only measurement scripts.
- Product behavior beyond the fixed revisions used by the four rehearsals.
- Mechanical enforcement after distribution.

Reasoning effort: not exposed to the inspector.

human_action: none for this inspection. Execution: COMPLETE — r4 inspection finished; under order §10, this REJECT returns ECO-115 to pending human disposition.