# ECO-114 manufacture — acceptance V1 and V2 (measured at manufacture; V1's checker repaired after inspection r1's IA-03)

Run 2026-10-24 (from the repository root). All files are LF; sha256 of the committed bytes.

| File | What | sha256 |
|---|---|---|
| `check_v1_v2.py` | V1 clause by clause (each rule's clauses from the order's §1 present in its canonical text; each copy holding its canonical text's clauses; §9's two rows with equal may-see / must-not-see; the prompt's step order; the template fields with their place comments) and V2's field-name check; `--mutations` removes each clause in memory and expects V1 to fail for that rule | `5c049088dbdb55bed98153214f406b1227c841c6b49bfea17e3da2693681ca75` |
| `v1-v2.txt` | its output on the repaired tree: V1 PASS, V2-fields PASS | `13b629b544e102d49010d8dc2a3d127fc66f54923ca5bd5625a1edf14eddbee0` |
| `v1-mutations.txt` | `--mutations`: 64 clauses removed one at a time; 64 caught (V1 fails for the clause's own rule), 0 missed | `ece325f266fbc7a1aa8ad7288f712e7561ffd90df4b05474d71c4a37ffd2da46` |
| `v1-v2-control-before-manufacture.txt` | the same script on the tree at the filing commit `25bea38` (`git archive`): V1 FAIL (14 rule groups), V2-fields FAIL | `71c3716680feab04eb902c7912682aeddf0a3274105784a0a80b4509b1e865fd` |
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
