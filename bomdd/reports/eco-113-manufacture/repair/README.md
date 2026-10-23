# ECO-113 repair manufacture — evidence (order §6)

Measured on the repaired `method/tools/bomdd-run.py` (sha256 `a114d971b61f…`) before the repair commit; the design: the order at `860097d` (the
amendment converged in loop A2). Windows 11, CPython 3.13.

| file | what it is |
|---|---|
| `selftest-bomdd-run.txt`, `selftest-bomdd-job.txt`, `selftest-bomdd-witness.txt` | the three selftests' output, each exit 0 |
| `rule-mutations.txt` | `../rule_mutations.py` on the repaired tools: 27 cases — the 20 of the manufacture and the seven V4(f) requires, one per A4 clause (`A4i-not-object`, `A4ii-run-id`, `A4iii-order`, `A4iv-integer`, `A4iv-position`, `A4iv-boundary`, `A4iv-digest`) — each red on its own arm |
| `rule-mutations-eco-112.txt` | ECO-112's nine rule mutations, unchanged, re-run on the repaired tools: each still red on its own arm |

The new arms (selftest block `V4(f)/(q)(ECO-113 修正 1:A)`): `v4f-not-object`, `v4f-run-id-*` (start, end, abort and release with `run_id` 5; a start
with an empty id), `v4f-duplicate-start` (+ `-first-open`), `v4f-close-before-start` (+ `-open`; r1's probe), `v4f-q-integer`, `v4f-q-position`,
`v4f-q-boundary`, `v4f-q-digest` (each quarantine built so that only its own check makes it invalid), `v4f-q-r1-probe` (offset 999999), `v4f-repeated-end`,
`v4q-reuse-opens`, `v4q-reuse-release`. Each invalid journal is then quarantined by R3 and must read clean.

As in the manufacture, the W1 and W3 cases leave suspended cells; they were resumed by hand after the run.
