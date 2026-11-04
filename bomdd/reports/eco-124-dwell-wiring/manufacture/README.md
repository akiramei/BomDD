# ECO-124 manufacture evidence

Run from this folder with `python -X utf8 <script> C:/Users/akira/source/repos` (v6 also takes the old tool's path; mutants124 takes
the BomDD root). Outputs are LF.

| File | Gate | What it shows |
|---|---|---|
| `v1.py` / `v1.txt` | V1 | the brief's numbers and ids equal an independent derivation from the same `dwell()` result, five registers, fixed now |
| (`bomdd-job.py --selftest`) | V2 | the ECO-124 arms named on the dwell selftest's PASS line |
| `mutants124.py` / `mutants124.txt` | V2, V3 known-bad | four brief mutants and four hook mutants each turn a selftest red; unchanged copies green |
| (`dwell-session-hook.py --selftest`) | V3 | the hook's arms (no register, register, failures, bound, input without cwd, --check) |
| `v4.txt` | V4 | the user-level settings edit, before and after (hooks section only), and `--check` both ways |
| `v5.py` / `v5.txt` | V5 | a new headless session in BomDD and ViewTube quoting the brief it received — not measured on the first run (CLI authentication expired) |
| `v6.py` / `v6.txt` | V6 | the full view, JSON and the job modes unchanged against the filing tree's tool; three selftests; the hook's warm time on ViewTube |
