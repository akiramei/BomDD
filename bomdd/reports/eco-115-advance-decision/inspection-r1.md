[INFORM / COMPLETE]
REJECT IA-01 IA-02 IA-03 IA-04 IA-05 IA-06 IA-07
1. PASS — Scope: all 13 changed paths are within `diff_audit.allowed_paths`; none of the prohibited paths changed.
2. FAIL — Rule text: §6.1 contradicts D3, the bounds input is under-specified, and declared limit L7 is absent.
3. FAIL — Rest of method: §6.1 prevents the product-specific known-defect path that D3/D5 explicitly preserve.
4. FAIL — Acceptance evidence: re-run succeeds 116/116, but V2 omits or mismeasures parts of I3a, C5, and D4, and three drivers are fail-open.
5. PASS — Records: manufacture/register statements, diff, committed hashes, and stored evidence hashes agree.

## Findings

### IA-01 — blocking — §6.1 excludes D3’s retained human path

Location: `method/bomdd-playbook-v1.md:256-261`, `method/bomdd-playbook-v1.md:679`; order `bomdd/60-change-order-eco-115.md:171-178,208-210`.

Evidence: D3 says a product may decide at distribution that a held individual enters Phase 5 through an outside-D mechanism such as ECO-108/ECO-111 known-defect acceptance. D5 repeats that this is a possible human disposition. Section 6.1 instead says Phase 5 measures only individuals classified `advances`, and every held individual returns solely as a new delivery. The reference is therefore stronger than the canonical rule and makes the retained path unusable.

Direction: qualify §6.1 as “through D” and explicitly preserve any distribution-defined outside-D disposition.

### IA-02 — blocking — D5 cannot classify an invalid first bounds line

Location: `method/bomdd-playbook-v1.md:195-218,279-287`; `method/templates/40-work-order.md:7-8`.

Evidence: D5 reads `holds <n>, decisions <m>` from the first issue, but I2 defines no domain for `n` or `m`, I3a does not validate this line, and D5 supplies no result or route for malformed, non-numeric, missing-half, negative, or otherwise unusable explicit values. Absence has a default; invalid presence does not. Consequently convergence cannot always be computed from an allowed record.

Direction: define the bounds grammar and numeric domain, then classify an invalid first bounds line with a deterministic result and route; add negative arms.

### IA-03 — non-blocking — declared scale limit L7 is absent from the manufactured item

Location: order `bomdd/60-change-order-eco-115.md:316-317`; manufactured limits at `method/bomdd-playbook-v1.md:321-333`.

Evidence: L7 declares the narrow empirical basis—two products, ViewPrism2 real records, one MoviePad delivery, and synthetic inputs. The manufactured limits bullet contains no equivalent scale/generalization statement. V1’s limit token list likewise has no L7 check: `manufacture/check_v1_v2.py:110-112`.

Direction: add L7’s measured scale and generalization limit to the limits paragraph and its V1 clause set.

### IA-04 — blocking — V2 does not bind reference paths to the documents it decides

Location: `rehearse_decision_v2.py:99-117,120-125,263-264`; V2 claim at order `:358-361`.

Evidence: `mbom_ref` and `control_plan_ref` paths are parsed and used only for freeze-versus-issue comparison. `decide()` separately accepts M-BOM, Control Plan, and delivered-copy bytes from its caller without proving those bytes came from those paths. A throwaway probe changed both refs to unrelated nonexistent paths while supplying the original documents; the decision returned `advances`.

Probe result:

```text
{'result': 'advances', ...}
```

Direction: load all compared/decided bytes through the recorded refs, or compare caller-provided bytes with `git show(frozen_commit, recorded_path)` and fail on missing paths. Add swapped and nonexistent-path arms.

### IA-05 — blocking — the C5 rehearsal ignores `row_changes`’ recorded cause

Location: `rehearse_sequence.py:66-95`, especially `:86` where `_via` is discarded; rule at `method/bomdd-playbook-v1.md:301-305`.

Evidence: C5 requires detecting an open failure moved under a cause other than its own. The implementation checks whether any prior routing cause existed on the row, but never compares the cause stored in `row_changes`. A probe supplied both the row’s own cause and another row’s cause, then recorded the rename as routed by the other row. Expected C5; actual result:

```text
control: in-control
signals: []
```

Thus existing green arms do not test the repaired clause’s decisive field.

Direction: compare each change’s recorded cause with the applicable prior cause, and add a two-cause arm where only the recorded cause distinguishes red from green.

### IA-06 — blocking — V2 does not perform D4’s record write

Location: `rehearse_decision_v2.py:287-334`; D4 at `method/bomdd-playbook-v1.md:262-265`.

Evidence: the decision returns a derived `result` inside its output row, but never writes it into the corresponding `test_evidence_refs` decision record. Probe:

```text
decision= advances returned_row_result= pass record_result_after= None
```

The V2 statement that the rehearsal applies D4 is therefore stronger than the evidence.

Direction: make the rehearsal produce the post-decision As-Built entry and assert each decision record’s persisted D4 value.

### IA-07 — blocking — three V2 drivers cannot fail their caller on missed expectations

Location:

- `run_rehearsal_v2.py:409-429`
- `run_moviepad.py:140-183`
- `run_moviepad_d2.py:104-128`
- `manufacture/check_v1_v2.py:228-238`

Evidence: the drivers print `MISSED` or `all synthetic cases as expected: False` but return exit 0. `check_v1_v2.py` checks only exit status plus byte equality with a stored output. If a stored output also contains the failure text, V2 passes. `rehearse_sequence.py` correctly returns nonzero and does not share this defect. Current committed outputs contain no `MISSED`, but the gate itself is fail-open.

Direction: accumulate failures and return nonzero in all three drivers; have the wrapper also reject `MISSED` and false summaries.

## Acceptance execution

With process-local Git safe-directory settings only:

```text
check_v1_v2.py on manufacture tree: PASS 116/116, exit 0
check_v1_v2.py on archived filing tree db16fa3: FAIL 22/116, exit 1
rehearse_sequence.py: 38/38, byte-identical
```

The filing-tree negative control failed for the intended missing-text/template reasons. The initial manufacture run without process-local safe-directory settings was unmeasurable for three product-repository rehearsals because Git rejected repository ownership; rerunning with environment-only settings resolved this without changing configuration or files.

## Calibration receipt

- V1 presence claim: observed; conditionally qualified because its documented scope is token presence, not semantic equivalence.
- V2 full-rule claim: observed execution, evidence not qualified because IA-04 through IA-07 leave false-positive paths.
- Instrument defects: IA-04 through IA-07.
- Unmeasured dimensions: execution in a shipped product integration and non-git deliveries, as already declared.
- Battery: Q1–Q7 and Q9–Q11 asked; Q8 not applicable.

## Records

- Start HEAD: `35961c32d916c71ecd10a9124df5fee9574a7e0a`
- End HEAD: `35961c32d916c71ecd10a9124df5fee9574a7e0a`
- Start/end `git status --short`: empty.
- Input hash prefixes in §4 match `git show db16fa3:<path>`.
- README SHA-256 values match the committed script and output bytes.
- No repository or product-repository file was created, changed, or deleted; no network was used.

## Out of range observations

- Git’s initial ownership refusal was an execution-environment condition, not an ECO-115 defect.
- Product worktrees reported no status entries after process-local safe-directory qualification.

## Not examined

- V4 self-conformance and remote CI, which are closure checks and network access was prohibited.
- The older v1 rehearsal and the three basis-only measurement scripts were not independently rerun.
- Product behavior beyond the fixed revisions read by the four specified rehearsals.

Reasoning effort: not exposed to the inspector.

human_action: none. Execution: COMPLETE — requested independent inspection finished without modifying the target.