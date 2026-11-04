# ECO-122 filing basis — why the dwell view takes 40 s on ViewTube, and what reusing each blob's parse gives

All runs on the user's machine, 2026-11-04, read-only on the repositories. ViewTube's register is
`bomdd/process/change-register.yaml` at `42936d96` (1,732 commits). The caches the scripts build were in the session's scratchpad,
outside every repository, and are not kept.

| File | What it is |
|---|---|
| `prototype.py` | Reads the register's history twice with the tool's own `_dwell_snapshot`: once with an empty per-blob cache (cold), once with the same cache (warm); checks that the warm snapshots equal the cold ones. Serial; a sizing prototype, not the design. |
| `prototype.txt` | Its output on ViewTube. |
| `tool-baseline.txt` | ECO-120's `bomdd-job.py --dwell --json` on ViewTube, two runs, wall clock (parallel, no cache). |
| `costs.py` | The stages that are not parsing: `git log`, the blob ids (`cat-file --batch-check`), `git status -uall`, and loading one JSON file that holds every blob's snapshot (made with its `--merge` mode from the prototype's per-blob files). |
| `costs.txt` | Its output on ViewTube (three runs each). |

## Manufacture (order section 4) — `manufacture/`

| File | What it is |
|---|---|
| `v1.py`, `v1.txt` | V1: five registers, four ways (ECO-120's tool, the new tool without a cache, cold, warm) at one fixed `now`, text and JSON compared byte for byte. |
| `v23.py`, `v23.txt` | V2 and V3: growth, an amend, a corrupt cache, another version key, an unwritable cache path, a parse failure, and the declared limit (a well-formed wrong entry), on a throwaway repository. |
| `mutants.py`, `mutants.txt` | V3's known-bad: four broken copies of the changed tool (M1-M4), each run through `v23.py`; each must turn its arm red. |
| `v45.py`, `v45.txt` | V4 (existing modes byte-identical, both selftests, each repository's status and git directory unchanged by a cold run) and V5 (ViewTube cold and warm times by the command line). |
| `mutants_selftest.py`, `mutants_selftest.txt` | At closure (order section 5): the same four broken copies run through the tool's own `--selftest`; M2 red, M4 unmeasurable, M1 and M3 green (a recorded limit). |
