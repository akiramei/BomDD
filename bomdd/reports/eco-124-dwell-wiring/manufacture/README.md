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
| `v5.py` / `v5.txt` | V5 | a new headless session in BomDD and ViewTube quoting the brief it received — FAIL on BomDD (`NONE`), PASS on ViewTube (first runs at manufacture could not sign in) |
| `v5rep.py` / `v5rep.txt` | V5 (repeats) | the same session repeated with the hook events shown: BomDD 0/4, ViewTube 3/3; the hook's text reached every session |
| `v5probe.py` / `v5probe.txt` | V5 (attribution) | two other prompts in BomDD: the session first denies, then copies the hook's three lines exactly |
| `v5disc.txt` | V5 (discriminators) | ViewPrism2 also `NONE`; the desktop app's model cannot run on CLI 2.1.207 (run with `v5rep.py`) |
| `v5-compact-observation.txt` | beside V5 | the hook's output on this session's compaction equals the hand-run BomDD brief |
| `v6.py` / `v6.txt` | V6 | the full view, JSON and the job modes unchanged against the filing tree's tool; three selftests; the hook's warm time on ViewTube |
