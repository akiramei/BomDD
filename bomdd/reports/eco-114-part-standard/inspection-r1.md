[INFORM / COMPLETE]
REJECT IA-01 IA-02 IA-03 IA-04

1. Scope — FAIL (IA-01).
2. Each rule against the text — FAIL (IA-02, IA-03).
3. Rules against the rest of the method — PASS. No additional contradiction found with §§4.4–4.7, package/oracle ownership, existing template fields, or measured BOM shapes.
4. Acceptance evidence — FAIL (IA-03, IA-04). Rehearsal reproduced byte-identically after supplying process-local Git safe-directory settings.
5. Records — FAIL (IA-01). All 12 README SHA-256 values checked match the committed bytes.

## Findings

### IA-01 — blocking — audited diff exceeds ECO-114’s allowed paths

Location: `bomdd/60-change-register.yaml:3598-3601`; `bomdd/60-change-order-eco-114.md:206-210,244-272`.

Evidence:

`git diff --name-only 25bea38b41060a04f9f4c0b9563462f01d73e2d3..286d02c944ed7429e0f899a70342cbed518e81ad`

includes ten files under `bomdd/reports/eco-115-advance-decision/`. ECO-114’s `diff_audit.allowed_paths` permits only `bomdd/reports/eco-114-part-standard/` among report directories. The intervening commit is `afabdb1`, followed by the ECO-114 manufacture commit.

This also conflicts with §4’s statement that ECO-115’s held draft “is not mixed in” when evaluated over the inspection brief’s prescribed diff window.

Direction: give ECO-114 a revision window whose changed paths are entirely allowed, or explicitly amend the audited baseline/allowed paths and manufacture record.

### IA-02 — blocking — O4 is not stated in its declared canonical place

Location: `bomdd/60-change-order-eco-114.md:129-131,177-184`; `method/bomdd-playbook-v1.md:413-422,894-901`.

The rule map assigns O4 to §4.6’s “Phase 3 の順序と担当”, with §9 as a copy. Section 4.6 describes the six steps and points to the roles table, but does not state O4’s exact layer split or the requirement that the orchestrating AI has the same “may see / must not see” permissions as the designer. Those provisions exist only in §9.

Therefore O4 is not present once in its named canonical place; the purported copy currently holds normative content absent from the canonical text.

Direction: state all of O4 in §4.6 and keep §9 as a matching copy.

### IA-03 — blocking — V1 does not verify the acceptance claim that rules and copies match

Location: `bomdd/reports/eco-114-part-standard/manufacture/check_v1_v2.py:28-57`; `bomdd/60-change-order-eco-114.md:218-220,263-266`.

The checker establishes heading/label occurrence, selected substrings, step numbers, and field names. It does not compare the substance of P1–P4, O1–O4, C1, A1’s scope and seven clauses, or A2 against the order, nor does it compare all mapped copies with their canonical rules.

For O4 specifically, line 30 assigns O4 to the mere presence of the §4.6 heading, while line 37 independently checks only two §9 substrings. This produces V1 PASS despite IA-02.

Re-run result: exit 0 with `V1 PASS` and `V2-fields PASS`. The stored control reports V1/V2-fields FAIL, but that positive control does not demonstrate sensitivity to weakened, stronger, or differing rule text.

Direction: make V1 compare each normative clause and scope requirement, including O4’s complete canonical text and copy equivalence, rather than checking labels and selected tokens.

### IA-04 — blocking — the rehearsal does not implement C1’s measurement semantics

Location: `bomdd/60-change-order-eco-114.md:135-138,221-240`; `bomdd/reports/eco-114-part-standard/rehearse_part.py:100-112`.

C1 requires that a listing row actually measure some part of the referenced `provides` entry, list no entry it does not measure, and identify unmeasured portions in `known_limits` with the entry ID.

The rehearsal checks only:

- whether every `provides` ID appears in some row;
- whether at least one such row is in the unit’s `acceptance_refs`;
- whether every listed ID exists.

It never reads a row’s characteristic, fixture, oracle, test vectors, or `known_limits`. A completely unrelated row can therefore cite the ID and pass C1. The evidence consequently supports reference integrity, not the claimed C1 rule.

Direction: add adversarial cases where an unrelated row cites an entry and where an incompletely measuring row omits the entry-specific `known_limits`; define and exercise an inspectable criterion for “measures some part.”

## Out of range observations

- The first rehearsal attempt was blocked by Git’s dubious-ownership protection for the two product repositories. Re-running with process-local `GIT_CONFIG_*` safe-directory values succeeded without changing Git configuration.
- The successful rehearsal output SHA-256 was `cd0ecedf…`, byte-identical to the committed manufacture output.
- Basis figures sampled against `measurements.txt` and `shapes.txt` match §0, including unit/E-item cardinalities, connection counts, legacy `interface_contract` counts, and empty `acceptance_refs`.
- `check_v1_v2.py` exits 0 even when its report says FAIL. The stated interface defines the report’s final lines as the result, so this was not counted as a separate finding.

## Not examined

- Network or CI state; network access was prohibited.
- Product runtime behavior beyond the prescribed read-only rehearsal.
- ECO-115’s substantive design.
- Full semantic correctness of unrelated pre-existing method rules.
- `self-conformance.py`, because this inspection is read-only and the brief did not request it.

Start HEAD: `286d02c944ed7429e0f899a70342cbed518e81ad`  
End HEAD: `286d02c944ed7429e0f899a70342cbed518e81ad`  
Start/end `git status --short`: empty.  
Reasoning effort: not exposed by the harness.  
human_action: none. Inspection complete; no repository file was created, changed, or deleted.