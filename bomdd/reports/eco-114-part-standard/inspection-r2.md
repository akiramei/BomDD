[INFORM / COMPLETE]
REJECT IA-05

1. IA-01 repaired under 1:A — PASS. `be96698..faffcf9` passes C1–C5. Including `afabdb1` as the positive control fails C4/C5. It is the sole excluded commit, precedes manufacture, changes only ECO-115 records, and leaves ECO-114 inputs and records untouched. §6 and the diff-window README record the ruling and reason.

2. IA-02 repaired — PASS. Playbook §4.6 now states the complete O4 layer ownership and gives the orchestrating AI the designer’s may-see/must-not-see permissions. §9 is a matching copy.

3. IA-03 repaired — FAIL (IA-05). The current registered 64 fragments all pass; all 64 removal mutations fail their assigned rule; the filing control tree fails V1 and V2-fields. However, the fragment list does not cover every normative clause in §1, so V1 is not the claimed complete comparison.

4. IA-04 under 2:A — PASS. Playbook §4.5 and order L2 explicitly assign “measures” to orchestrating-AI judgement and independent inspection. V2 claims only reference integrity. The rehearsal makes no broader claim.

5. Regression — PASS. The repair changes only §6-listed areas. The method relationships r1 found sound remain intact; all 18 SHA-256 entries across the evidence READMEs match committed bytes. The rehearsal output is byte-identical to `rehearsal.txt` and `rehearsal-at-manufacture.txt` (`cd0ecedf95d4356b07ba3a3e7dc4ae83442a929bef9e567a1957655fcc38e813`).

## Findings

### IA-05 — blocking — V1’s clause inventory remains incomplete

Location: `bomdd/reports/eco-114-part-standard/manufacture/check_v1_v2.py:26-92`; order §1.

Evidence: `CLAUSES` contains 64 selected fragments, rather than every normative clause in §1. Material omissions include:

- P1: replacement of `interface_contract`; the required `statement` boundary/results/errors/side-effects content; `form` being a manufacturing decision while the promise remains ruled text.
- P2: the human determines external boundaries with E-BOM release.
- O1: several step-specific owners/details and the requirement that Control Plan remains before manufacture.
- O2: the A1 check and both failure dispositions.
- O3: the orchestrating AI’s pre-G3 re-check of both A1 and C1.
- C1: “list none it does not measure,” the unit-`acceptance_refs` constraint, and the P3/O2 disposition when no row can measure an entry.
- A1: the full scope for clauses 2, 5 and 7, the lazy rule, and substantial conditions inside several numbered clauses.
- A2: step-5 selection, dual listing, receiving-side/human execution ownership, and non-replacement of A1.

An in-memory probe removed O3’s explicit pre-G3 C1/A1 re-check from the canonical playbook text. `v1()` still returned no failed rules and reported `V1 PASS`. Thus the mutation result proves sensitivity only for the registered fragments, not for all §1 clauses or complete canonical/copy equivalence.

Direction: derive or enumerate every normative §1 clause—including copy obligations—and add a negative mutation for each; V1 must fail when any such clause is removed or altered.

## Out of range observations

- None affecting the verdict.

## Not examined

- New design-boundary exploration.
- Network and CI state, as prohibited.
- ECO-115’s substantive design.
- Product runtime behavior beyond the prescribed rehearsal.
- `self-conformance.py`, which was outside the requested read-only regression checks.

Start HEAD: `faffcf9d21d20f9755d881c68ff82d4815466507`  
End HEAD: `faffcf9d21d20f9755d881c68ff82d4815466507`  
Start/end `git status --short`: empty.

human_action: none. Inspection complete; no repository file was created, changed, or deleted.