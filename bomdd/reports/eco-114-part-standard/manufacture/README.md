# ECO-114 manufacture — acceptance V1 and V2 measured before the manufacture commit

Run 2026-10-24 on the manufactured working tree (from the repository root). All files are LF; sha256 of the committed bytes.

| File | What | sha256 |
|---|---|---|
| `check_v1_v2.py` | V1 (each rule once in its canonical place, the copies matching, the template fields with their place comments, §9's split) and V2's field-name check (the templates parse and carry every path the rehearsal reads) | `4b30eba06db0eeddd348b1a8b7b9dd67dd803473acbfd62d023a7b5853047fbd` |
| `v1-v2.txt` | its output on the manufactured tree: V1 PASS, V2-fields PASS | `87aac9c76b7b0b8b9cc7e8761c91e2a695e4466c9a17bffb27bc1a36ce9c8f53` |
| `v1-v2-control-before-manufacture.txt` | the same script on the tree at the filing commit `25bea38` (`git archive`): V1 FAIL, V2-fields FAIL (27 of 29 checks fail) — the positive control | `fe47c5b23eff37565d79d4888de79aa7c47f83a872e9e91580e4b6ee8b540217` |
| `rehearsal-at-manufacture.txt` | `../run_rehearsal.py` re-run after manufacture: byte-identical to `../rehearsal.txt` (both real BOMs no failure; 23 one-change cases as expected) | `cd0ecedf95d4356b07ba3a3e7dc4ae83442a929bef9e567a1957655fcc38e813` |

Commands:

```
python -B bomdd/reports/eco-114-part-standard/manufacture/check_v1_v2.py bomdd/reports/eco-114-part-standard/manufacture/v1-v2.txt
(cd bomdd/reports/eco-114-part-standard && python -B run_rehearsal.py ../../../../ViewPrism2 ../../../../ViewTube manufacture/rehearsal-at-manufacture.txt)
```

Instrument defects found while measuring (both in `check_v1_v2.py`, corrected before these outputs): its step-order check matched a "3. K-BOM" elsewhere in the
playbook (now limited to §4.6's item), and on the control tree it stopped with a traceback on a missing heading instead of reporting FAIL (missing
headings and paths now count as FAIL).
