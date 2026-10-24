# ECO-114 manufacture — acceptance V1 and V2 (measured at manufacture; V1's checker repaired after inspection r1's IA-03)

Run 2026-10-24 (from the repository root). All files are LF; sha256 of the committed bytes.

| File | What | sha256 |
|---|---|---|
| `check_v1_v2.py` | V1 clause by clause (each rule's clauses from the order's §1 present in its canonical text; each copy holding its canonical text's clauses; §9's two rows with equal may-see / must-not-see; the prompt's step order; the template fields with their place comments) and V2's field-name check; `--mutations` removes each clause in memory and expects V1 to fail for that rule | `c82cf0e98c8e0b8c703311e4a8dff20078023e3d934e3b512bfb3b4003dc665e` |
| `v1-v2.txt` | its output on the repaired tree: V1 PASS, V2-fields PASS | `9a966338b2f1dbb95f732a58029b83970da64a2ffe168b1a88fc2bf16122ad64` |
| `v1-mutations.txt` | `--mutations`: 96 clauses removed one at a time (64 after r1, 32 more after r2's IA-05); 96 caught (V1 fails for the clause's own rule), 0 missed | `3d0eea4c85af2e9216efb6b6b0c146da819e203c7be80012c388b2fd7211f6fe` |
| `v1-v2-control-before-manufacture.txt` | the same script on the tree at the filing commit `25bea38` (`git archive`): V1 FAIL (14 rule groups), V2-fields FAIL | `f641d082613a4d23d26d54a5919277496ee9ee8a16eb05e691ceeea1f81a03e3` |
| `rehearsal-at-manufacture.txt` | `../run_rehearsal.py` re-run after manufacture: byte-identical to `../rehearsal.txt` (both real BOMs no failure; 23 one-change cases as expected) | `cd0ecedf95d4356b07ba3a3e7dc4ae83442a929bef9e567a1957655fcc38e813` |

Commands:

```
python -B bomdd/reports/eco-114-part-standard/manufacture/check_v1_v2.py bomdd/reports/eco-114-part-standard/manufacture/v1-v2.txt
python -B bomdd/reports/eco-114-part-standard/manufacture/check_v1_v2.py --mutations bomdd/reports/eco-114-part-standard/manufacture/v1-mutations.txt
(cd bomdd/reports/eco-114-part-standard && python -B run_rehearsal.py ../../../../ViewPrism2 ../../../../ViewTube manufacture/rehearsal-at-manufacture.txt)
```

Instrument defects of `check_v1_v2.py`, all corrected before these outputs: at manufacture, its step-order check matched a "3. K-BOM" elsewhere in the
playbook, and on the control tree it stopped with a traceback instead of reporting FAIL; after inspection r1 (IA-03), it checked labels and selected
tokens instead of each rule's clauses, and so passed while O4 was missing from its canonical place (IA-02) — it now checks clauses and copies, and the
mutation run shows each clause's removal fails its own rule (the first mutation run missed one clause whose bare ID form occurs twice in the section;
the clause was made unique and the run repeated).
