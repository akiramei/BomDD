# ECO-113 manufacture — evidence (order §4)

Measured on the manufactured tools before the manufacture commit (the design: the order at `3c7781c`; the tools started from `2271102` = ECO-112's
verified bytes). Windows 11, CPython 3.13.

| file | what it is |
|---|---|
| `selftest-bomdd-run.txt`, `selftest-bomdd-job.txt`, `selftest-bomdd-witness.txt` | the three selftests' output (each exit 0); bomdd-run's second line names the platform branch exercised (V1(g)) |
| `rule_mutations.py` | breaks one rule per case in a copy of `method/tools` and checks that the bomdd-run selftest goes red and names that rule's own arm |
| `rule-mutations.txt` | its run on the manufactured tools (20 cases) |
| `rule-mutations-eco-112.txt` | ECO-112's nine rule mutations (`bomdd/reports/eco-112-arm-inventory/manufacture/repair/rule_mutations.py`, unchanged) re-run on the manufactured tools — the earlier arms still go red for their own reasons |

Run: `python -B rule_mutations.py <repo>/method/tools <work dir> [case …]` (Windows; one case at a time — two selftests at once can turn ECO-112's
V2(g) arms red without cause, OBS-20261018-03). The W1 and W3 cases break the job, so the mutated selftest leaves suspended cells behind; they hold
no lock and are resumed by hand afterwards (the script writes output to files, not pipes, for this reason).

## Acceptance items → selftest arms (the selftest block `ECO-113(R15)` in `method/tools/bomdd-run.py`)

Arm names are the prefixes of the selftest's failure messages; a rule mutation names the arm it turned red.

| item | arms |
|---|---|
| V1(a) live holder → `ENTRY_ALIVE`, no launch | `v1a-entry-alive` (a child entry runs a slow cell; the in-process launch is refused) |
| V1(b) holder killed → lock within 5 s | `v1b-lock-after-kill` |
| V1(c) concurrent launches: same ledger, other ledgers, two worktrees | `v1c-same-ledger`, `v1c-other-ledger`, `v1c-two-worktrees` (two child entries; exactly one cell runs) |
| V1(d) dry while a cell runs | `v1d-dry-while-running` |
| V1(e) lock file kept | `v1e-lock-file-kept` |
| V1(f) read-only lock file, unwritable directory | `v1f-readonly-lock`, `v1f-unwritable-dir` |
| V1(g) branch recorded | the PASS report's second line |
| V2(a) entry killed mid-cell | `v2a-entry-killed`, `v2a-abnormal-end` |
| V2(b) another handle keeps the job | `v2b-cell-alive`, `v2b-holder-closed` |
| V2(c) job create / configure / assign fails | `v2c-_job_create`, `v2c-_job_configure`, `v2c-_job_assign` |
| V2(d) job query error, other session / appcontainer / host | `v2d-job-query-error`, `v2d-other-session`, `v2d-other-appcontainer`, `v2d-other-host` |
| V2(e) Windows branch off | `v2e-posix-unknown`, `v2e-popen-after-first-line` |
| V2(f) no pid in classification | `v2f-no-pid` |
| V2(g) entry outside the job, empty job, exception before resume | `v2g-entry-outside`, `v2g-empty-job`, `v2g-exception-before-resume` |
| V2(h) resume fails | `v2h-resume-failed` |
| V2(i) journal only, empty ledger | `v2i-journal-only` |
| V3(a) release `ABNORMAL_END` and `UNKNOWN`, next launch proceeds | `v3a-release-abnormal-end`, `v3a-release-unknown`, `v3a-next-launch` (and every later `*-release` arm) |
| V3(b) release `CELL_ALIVE` refused; release while the lock is held | `v3b-release-cell-alive`, `v3b-release-entry-alive` |
| V3(c) wrong RUN_ID, non-human `--by`, other options | `v3c-arg` (four calls, each with its own fragment) |
| V3(d) two concurrent releases | `v3d-concurrent-release` |
| V3(e) quarantine; parsed runs stay open; refused while `CELL_ALIVE` | `v3e-quarantine`, `v3e-parsed-run-stays-open`, `v3e-quarantine-cell-alive` |
| V3(f) nothing stopped | `v3f-nothing-stopped` (the cell keeps running through a refused release and a refused quarantine) |
| V4(a) `start` commit fails | `v4a-start-commit-failed` |
| V4(b) ledger decision record fails after `start` | `v4b-ledger-after-start` |
| V4(c) torn tail | `v4c-torn-absent`, `v4c-torn-repaired` |
| V4(d) `end` commit fails | `v4d-end-failed`, `v4d-run-open` |
| V4(e) short write | `v4e-short-write`, `v4e-short-write-repaired` |
| V4(f) corrupt line; U+2028 / U+0085 | `v4f-journal-corrupt`, `v4f-release-refused-while-corrupt`, `v4f-quarantined`, `v4f-line-separators` |
| V4(g) no CR | `v4g-no-cr` |
| V4(h) interrupted wait | `v4h-interrupted`, `v4h-run-open` |
| V4(i) `--report` created before the lock | `v4i-report-exists-under-lock` |
| V4(j) three concurrent ledger writers | `v4j-ledger-concurrent` (3 × 300 records) |
| V4(k) exits and first lines per O1 | every refusal arm checks its exit and its line through `row()`; every other arm checks its exit and line |
| V4(l) `RUN_IN_FLIGHT` in both vocabularies | `v4l-vocabulary`, and the existing `DELIVERY と job の停止語彙が一致しない` |
| V4(m) O3 at three points | `v4m-first_line`, `v4m-after_wait`, `v4m-cell_record` (each with its `-open` / closed check) |
| V4(n) S4 row by row | `v1a-entry-alive` (`ENTRY_ALIVE`), `v1f-*` (`LOCK_UNAVAILABLE`), `v4o-journal-unreadable` (`JOURNAL_UNREADABLE`), `v2a-abnormal-end` (`ABNORMAL_END`), `v2b-cell-alive` (`CELL_ALIVE`), `v2d-*` (`UNKNOWN`), `v4f-journal-corrupt` and `v4n-journal-corrupt-cell-alive` (`JOURNAL_CORRUPT`), `v4i-report-exists-under-lock` (`REPORT_EXISTS`, no record) |
| V4(o) unreadable journal | `v4o-journal-unreadable` |
| V4(p) refusal record cannot be written | `v4p-refusal-unwritable` |
| V4(q) precedence | `v4q-precedence` |
| V5 existing selftests, witness unchanged | the existing arms in all three selftests; `git diff -- method/tools/bomdd-witness.py` empty |
