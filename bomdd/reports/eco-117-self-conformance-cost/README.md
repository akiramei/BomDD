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

The scripts carry the absolute path of the repository on the machine where they ran. Each builds its scaffold in a temporary directory and removes it; none writes into the repository.

The CI figures (survey §4) were read with `gh run view <run> --json jobs` for runs 40701637554, 40590058612 and 40589149810; the job and step times are in the survey's table.
