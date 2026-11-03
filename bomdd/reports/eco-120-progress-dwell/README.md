# ECO-120 — measurement of dwell in the change registers (2026-11-04)

Read-only. Nothing in any product repository was changed.

| File | What it is |
|---|---|
| `dwell.py` | For one register: reads the register at every commit that touched it (`git log --reverse`), records each ECO's status changes with the committer date, and the days in the current status. A commit whose register does not parse is counted and listed, not skipped silently. `--status-commits` reads only the commits whose diff adds or removes a `status:` line (a superset of the commits where a status can change). |
| `summarize.py` | Per repository: open ECOs by status and age bucket, the past dwell in each status (closed spans only), the eight oldest open ECOs. |
| `<repo>.json` | `dwell.py`'s output for each register. |
| `summary.txt` | `summarize.py` over the six JSON files. Ages are as of the run (2026-11-04, about 00:30-00:45 JST). |
| `heads.txt` | Each repository's HEAD and its count of dirty paths when the files were copied here. |

Runs:

- BomDD (`bomdd/60-change-register.yaml`, 347 commits), ViewPrism2 (437), TimetableAdv (601), BomDD-Plm (19), MoviePad-Remake (21),
  ViewTube (`bomdd/process/change-register.yaml`, 1,728 commits). Parse failures: 0 in all six.
- One register parse of ViewTube's 3.8 MB register took 0.18 s (CSafeLoader); the full ViewTube run took about 5 minutes.
- `--status-commits` against the full run: identical histories for every ECO on BomDD (315 of 347 commits read) and ViewPrism2
  (371 of 437). It saves little, because most register commits touch a status line.

Terminal statuses in `dwell.py`: verified, applied, superseded, rejected, withdrawn, cancelled, closed. `censored` marks an ECO whose
current status was already present at the first commit of the register's history, so its true entry date is earlier than shown.

Manufacture (the order's section 4):

| File | What it is |
|---|---|
| `v1_compare.py`, `v1/` | V1: `bomdd-job.py --dwell --json` on the six registers against the reference JSON above (start commit per open entry); `results.txt` and each run's JSON. |
| `v5/` | V5: the filing tree's tool and the changed tool on the same tree (`*-before.*` / `*-after.*`, byte-identical); the two selftests' outputs with exit codes. |
| `mutants.py`, `mutants-results.txt` | Six broken copies of `bomdd-job.py`, each run with `--selftest`; the dwell line must turn red. |
| `v7/` | V7: `--dwell` (text) on each of the six registers. |

Read by hand after the run (2026-11-04), recorded in the order's section 0:

- TimetableAdv: 62 of its 78 `staged` entries carry `implementation_started: True`; 68 carry a `next_gate`. The register has 665
  uncommitted lines (ECO-118 filed only in the working tree, file mtime 2026-10-05); the last commit is 2026-09-28; 2,191 dirty paths.
- ViewTube: 76 of its 116 `staged` entries carry a key starting `blocks_application_golden` (dated variants such as
  `blocks_application_golden_added_2026_10_08_eco_vt_239`).
- ViewPrism2: the 20 open `implemented` entries are ECO-003 to ECO-036, from 2026-06-22 to 2026-07-06.
