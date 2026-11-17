ACCEPT

CHANGES
- C1 closed — Round-2 null plus two new empty/blank-string list-member variants each exited 1 with `[GU7] FAIL … list に空の要素`; template wording is consistent.
- C2 closed — Round-2 self-reference plus list and numeric/string-normalized variants each exited 1 and reported `自分自身`; template requires a separate standalone ruling.
- C3 closed — Dictionary, missing, and padded-`user` deciders each exited 1 with `人が裁定していない`; the template explicitly requires exactly `decided_by: user`.
- IA-08 closed — Bundle, dictionary, and mixed-empty targets all failed GU7.

REGRESSION
- IA-01: holds — omitted overlapping human ruling failed.
- IA-02: holds — duplicate normalized rows failed.
- IA-03: holds — empty `touches_confirmed` failed.
- IA-04: holds — quoted `"false"` failed GU7’s Boolean check.
- IA-05: holds — round-1 numeric-ID fixture exited 0 with `[GU7] PASS`.
- IA-06: holds — numeric/string ID collision failed.
- IA-07: holds — corrected positive passed; omission remained detected.
- false fails: none; valid ruled/user, open/blocking, multi-target numeric, corrected-positive, and template-example cases all produced `[GU7] PASS`.
- false passes in the same path: none; empty members, self-references, non-user rulers, and malformed list/mapping targets failed.
- tracebacks: none in a 40-case sweep.
- no-bundle identity: 6 cases, identical exit codes, stdout, and stderr between `old/` and `new/`.

NEW FINDINGS (in range)
- none

OUT-OF-RANGE OBSERVATIONS
- `r2-variants/ia05_zero_id.yaml` exits 1 because GU4 treats numeric ID `0` as missing, although GU7 passes it. This behavior is pre-existing and outside C1–C3.

WHAT I RAN
- `python new/ui-cad-gate.py --selftest`: exit 0, `PASS(19 腕: known-bad 15・known-good 4)`.
- Ran C1 on 3 ledgers, C2 on 3, C3 on 3, IA-08 on 3, all round-1 fixture regressions, valid/malformed same-path cases, and the template example.
- Compared `old/` and `new/` in memory on the 3 round-2 no-bundle ledgers and 3 new variations; all complete outputs and exit codes matched.
- `inspection-work/mutants/no_c1.py --selftest`: exit 1, naming the IB-01 arm as expected-1/actual-0.
- `inspection-work/mutants/no_c2.py --selftest`: exit 1, naming the IB-02 arm as expected-1/actual-0.
- `inspection-work/mutants/no_c3.py --selftest`: exit 1, naming the non-user ruled arm as expected-1/actual-0.
- Rechecked protected tool hashes; `new/`, `r2/`, and `old/` retained the disclosed hashes.

NOT CHECKED
- GU6/`--mock` extraction integration, unrelated to these repairs.
- Exhaustive YAML alias/tag/depth fuzzing.
- Declared non-goals: truth of `touches: no`, semantic overlap beyond equal `ui_ids`, and untyped bundles.