# ECO-112 repair manufacture — evidence (order §6)

Measured on the repaired `method/tools/bomdd-run.py` before the repair commit (the design at `e394af0`).

| file | what it is |
|---|---|
| `selftest-bomdd-run.txt`, `selftest-bomdd-job.txt`, `selftest-bomdd-witness.txt` | first lines of the three selftests (all exit 0) |
| `rule_mutations.py` | the manufacture's rule-mutation script with five cases added for the rollback (B2) and the execution copy (B3) |
| `rule-mutations.txt` | its run on the repaired tools: each mutated copy's selftest is red and names the rule's arm |

Run: `python -B rule_mutations.py <repo>/method/tools <work dir>` (it copies the tools directory per case; the repository is not touched).

V3's first run (before this repair, FAIL) is in the parent directory: `v3-run1-arm-inventory.json`, `v3-run1-summary.txt`.
