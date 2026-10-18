[INFORM / COMPLETE]

ACCEPT

- inspector: EQ-002 / Codex CLI / GPT-5
- HEAD at start / at end: 0b6a784ea8e54b7822e7e4f2e09465a702e96a59 / 0b6a784ea8e54b7822e7e4f2e09465a702e96a59
- commits: 0 / files changed: 0
- selftests run: bomdd-run `ADVANCE OK: selftest PASS(起動4/dry2/kb5/job1/不能3/独立性9/報告27/gate6/構文5/台帳3/引数13/表)`, bomdd-job `bomdd-job selftest PASS(整合 NONE / …)`, bomdd-witness `ADVANCE OK: selftest PASS(known-good / …)`
- IA-03: resolved under the ruling

## Items

| # | item | verdict | evidence (file:line, command and the key output) |
|---|---|---|---|
| 1 | Ruling record | PASS | `bomdd/60-change-order-eco-112.md:358-368`: §8 excludes only `3c7781c`, identifies it as ECO-113’s filing, explains why it is outside ECO-112 manufacture, and states no other commit through the then-current range is excluded. Final-head run likewise found exactly one excluded commit. |
| 2 | Non-interference | PASS | `git show --stat 3c7781c` showed ECO-113’s order, 14 ECO-113 evidence paths, and the shared register only. Register diff added 29 lines solely as the ECO-113 entry and removed none; ECO-112’s entry was byte-identical. `diff_window.py` C2/C3 reported the shared register as the only intersecting path, no ECO-112 commit touching the 14 ECO-113 paths, and no later change to them. Inspection of ECO-112 tools/evidence found no dependency on those paths. |
| 3 | Diff-window check | PASS | `diff_window.py` header and implementation cover C1–C5. Final-head run on `3a9de06..0b6a784…` exited 0: 9 ECO-112 commits, one excluded ECO-113 commit, 38 ECO-112 paths, no path outside `allowed_paths`, register remainder equal to baseline. Positive control with `--control-include 3c7781c` exited 1 and named all ECO-113 paths outside scope. Subject-tag attribution, register-entry boundaries, and directory-prefix matching were inspected; the actual window’s subjects and diffs support the classification. |
| 4 | ECO-112 change set | PASS | C4 enumerated all 38 paths with their commits and found all inside ECO-112 `allowed_paths`. `git diff 3a9de06..0b6a784… -- method/tools/bomdd-witness.py` was empty. `git diff 3c7781c..HEAD` over ECO-113’s order/evidence paths was empty. No lock, journal, Job Object, or `RUN_IN_FLIGHT` implementation occurs in an ECO-112 commit. |
| 5 | Regression | PASS | `git diff 4d2c05f..0b6a784… -- method/` changed only `method/improvements.md`; ECO-112 executable/template files were unchanged. All three selftests exited 0. The permitted `rule_mutations.py` rerun exited 0 with all 9 mutations detected, including IA-01 rollback and IA-02 execution-copy arms. Thus r2’s IA-01/IA-02, G1–G5, B1–B5, O1, and T1–T6 PASS results still hold. |
| 6 | Records | PASS | `bomdd/60-change-order-eco-112.md:327-375`, both READMEs, and OBS-20261018-02 agree with the evidence. V3 run 2 records PASS: 101 calls, 73 cell calls/targets, 73 OWN, 0 MASKED/CRASH, no cross-check gap. Hashes matched: instrument `7abaa22324cc…`, measured tool `69e849630f90…`, JSON `5d65f538842c…`, summary `ccba23787ade…`; `bomdd-run.py` is byte-identical to `4d2c05f`. Diff evidence hashes also matched the §8 prefixes. |

## Findings (IA-04, IA-05, …)

- None.

## Not checked (limits)

- V3’s approximately 1.5-hour instrument was not rerun, as instructed; its committed records, hashes, counts, and measured-tool identity were checked.
- No network access was used. CI was therefore not queried live; the recorded successful CI and the fact that the executable `method/` tree is unchanged since `4d2c05f` were checked locally.
