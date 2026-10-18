# ECO-112 manufacture — evidence (2026-10-18)

Measured on the manufactured tools before the manufacture commit (Windows 11, CPython 3.13):

| tool | sha256 |
|---|---|
| `method/tools/bomdd-run.py` | `bfea9b4d6d3db0ddb5fc6b48ca64eaeda070df2b53b59ef57950e2f3aae10fa3` |
| `method/tools/bomdd-job.py` | `823eafd97d6fc468e2966ef42be11fa99d880b0ab05f32d3244ec060818ee31b` |
| `method/tools/bomdd-witness.py` (unchanged) | `1c6a40804092f0894b8c61dc8e394fa5bb27d9bc8a79bc494e8dbe1b00fefeca` |

- `selftest-bomdd-run.txt`, `selftest-bomdd-job.txt`, `selftest-bomdd-witness.txt`, `selftest-exits.txt` — the three selftests, each exit 0 (V1, V2's arms,
  V3's existing selftests).
- `rule_mutations.py`, `rule-mutations.txt` — each new rule broken in a copy of the tools (G3 off, B4 off, the CR refusal off, the `--brief` check moved
  before the other argument checks); the selftest went red and named the rule's arm in all four (T4).
- `v3-inputs.sha256` — the inputs of the V3 instrument's run (the pinned instrument and the manufactured `bomdd-run.py`). The run's result is added to
  this folder when it ends. Note: `bomdd-job.py` received a comment-only edit (header (7)) after that run had started; the instrument loads it from the
  same directory, so the run measures the earlier comment text with identical code.
