# ECO-117 evidence: the self-conformance cost survey (basis of the filing)

The survey was made on 2026-10-28 at BomDD `cbb71c1`, investigation only, in a side session's notes folder outside this repository. It was copied here unchanged at filing (line endings of the three `.txt` outputs normalised to LF; nothing else). Its §2 still says the files are "next to this note" in `self-conformance-cost-evidence/`; here they sit beside it in this folder.

| File | What it is |
|---|---|
| `survey.md` | The survey: per-check table (§3), CI times (§4), inside C11 (§5), candidates that keep every verdict (§6: S1, S2, S3), candidates that change what is detected (§7: J1-J4), the witness observation (§8, recorded as OBS-20261029-01), the ruling point (§9; the user's "1:A 2:a" on 2026-10-29) |
| `sc_profile.py` | The ECO-105 profiler (`bomdd/reports/eco-105-c11-parallel/sc_profile.py`), copied unchanged: each check timed in the order `main()` runs them, with the subprocesses each starts; it does not write the witness |
| `sc-profile-now.txt` | Its output at `cbb71c1`: total 209.7 s, C11 + C11b 201.7 s, 0 failures |
| `pq_sandbox_timing.py` | One IQ pass and one OQ pass of `process-qualification.py` on a fresh scaffold, timed by sandbox |
| `pq-sandbox-timing.txt` | Its output: IQ 0.8 s; OQ 84.5 s across 23 sandboxes of 2.2-6.6 s |
| `pq_concurrency.py` | N whole OQ passes at once on threads, each with its own base, on one fresh scaffold (a proxy for S1) |
| `pq-concurrency.txt` | Its output: 4 at once 141.9 s, 8 at once 252.4 s; all passed, results identical |

## Manufacture (2026-10-29)

| File | What it is |
|---|---|
| `verify117.py` | V1 and V2 of the order: five throwaway clones of the filing commit `44287a0` (A original; B changed; C changed with `suites: []`; M1, M2 broken versions), each run bounded at 1,500 s; usage in its docstring |
| `v1v2/results.txt` | One line per condition, as the script wrote it |
| `v1v2/progress.txt` | Start and end of each run, and the temporary directory's removal (line endings normalised to LF after the run) |
| `v1v2/<clone>-<mode>.txt` | Each run's exit code, wall time and full output (stdout, then stderr if any) |
| `sc-filing-original.txt` | The original self-conformance (default mode) on this repository at the filing tree `44287a0`, run before the filing commit: exit 0. The baseline for V1's comparison on this repository, made at closure (line endings normalised to LF) |

## Closure (2026-10-29)

| File | What it is |
|---|---|
| `recheck117.py` | Re-reads the saved outputs with every check id (`^\[C\d+[a-z]?\] `): `verify117.py`'s filter missed `[C5a]`/`[C6a]`. Usage in its docstring |
| `v1v2/recheck-results.txt` | Its output: every verdict holds; V1 28 lines, this repository 22 lines, M2 22 lines (line endings normalised to LF) |
| `sc-manufacture-changed.txt` | The changed self-conformance (default mode) on this repository at the manufacture tree, run before commit `2f666c6`: exit 0 |
| `ci-40777824802-extract.txt` | CI run 40777824802 on `2f666c6`: per job, the self-conformance step's header, `[env]`, check lines, `[time]`, `[witness]`, `[cleanup]` and last line, with timestamps (`gh run view --log --job`) |

The scripts carry the absolute path of the repository on the machine where they ran. Each builds its scaffold in a temporary directory and removes it; none writes into the repository.

The CI figures (survey §4) were read with `gh run view <run> --json jobs` for runs 40701637554, 40590058612 and 40589149810; the job and step times are in the survey's table.
