VERDICT: REJECT

ROUND-1 FINDINGS

- IA-01 closed — Original and list-valued `touches_confirmed` variations exited 1, naming the omitted overlapping ruled/user ruling.
- IA-02 closed — Original duplicate rows and numeric/string-equivalent row IDs exited 1 with `行が重複`.
- IA-03 closed — Empty-list and null-field cases both ran GU7 and exited 1 with `touches_confirmed が空`.
- IA-04 closed — Both quoted `"false"` and `"true"` on open touching rulings produced GU7 `blocking でない` failures.
- IA-05 closed — Numeric `1` and `1.5` rulings, including a string-form checked-row ID, exited 0 with `[GU7] PASS`.
- IA-06 closed — Integer/string and float/string ID collisions exited 1 with `文字列にすると同じ`.
- IA-07 closed — The corrected listed arm passed, the omission arm failed, and removing the overlap check made self-test fail.
- IA-08 not closed — The original bundle target and a dictionary-decided target failed, but `touches_confirmed: [H, null]` silently discarded the null target and passed.

NEW FINDINGS

- IB-01 [false pass] Empty members of a non-empty `touches_confirmed` list are filtered out instead of validated.
  input: `r2-variants/regression_mixed_empty_target.yaml`
  observed: new exits 0 with `[GU7] PASS` and `all executed gates passed`; r1 exited 1 with `touches_confirmed の None が台帳に存在しない`.
  expected: GU7 must fail because every referenced target must be a `status: ruled`, `decided_by: user` ruling, consistent with the template wording.
- IB-02 [false pass] A confirmed human ruling can point `touches_confirmed` to itself and satisfy rule (b).
  input: `r2-variants/regression_self_reference.yaml`
  observed: exit 0 with `[GU7] PASS` and `all executed gates passed`.
  expected: GU7 must fail because rule (b), and template rule 9, require a separate standalone ruling for the touching decision.

WHAT I RAN

- Ran the repaired tool on all 7 round-1 adversarial fixture folders and 11 added ledger variations.
- Ran `python new/ui-cad-gate.py --selftest`: exit 0, 16 arms.
- Created 7 mutation copies under `r2-mutations/`, removing each IA-01/07, IA-02, IA-03, IA-04, IA-05, IA-06, or IA-08 repair check; all 7 self-tests exited 1 and named the corresponding arm. No mutant stayed green.
- Compared old versus new exit codes and complete combined output on 14 no-open-bundle/no-`touches_confirmed` cases: all 14 were byte-for-byte equivalent after capture.
- Ran the repaired tool against the template example and compared r1 versus new on the mixed-empty-target regression.

NOT CHECKED

- GU6/`--mock` extraction integration, unrelated to GU7.
- Exhaustive YAML alias/tag fuzzing.
- Declared non-goals: truth of `touches: no`, semantic overlap beyond equal `ui_ids`, and untyped bundles.