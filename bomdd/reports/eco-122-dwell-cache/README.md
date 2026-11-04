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
