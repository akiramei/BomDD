[INFORM / COMPLETE]

REJECT IA-03

- inspector: EQ-002 / Codex CLI / GPT-5
- HEAD at start / at end: 4d2c05fe3ce1294f59b3f979aa53010cd9178f86 / 4d2c05fe3ce1294f59b3f979aa53010cd9178f86
- commits: 0 / files changed: 0
- selftests run: bomdd-run `ADVANCE OK: selftest PASS(起動4/dry2/kb5/job1/不能3/独立性9/報告27/gate6/構文5/台帳3/引数13/表)`, bomdd-job `bomdd-job selftest PASS(整合 NONE / …)`, bomdd-witness `ADVANCE OK: selftest PASS(known-good / …)`
- IA-01: repaired / IA-02: repaired

## Items

| # | item | verdict | evidence (file:line, command and the key output) |
|---|---|---|---|
| 1 | Scope | FAIL (blocking) | `git diff --stat f2d91d4..4d2c05f` includes `bomdd/60-change-order-eco-113.md` and `bomdd/reports/eco-113-*`, outside ECO-112 §2’s list at `bomdd/60-change-order-eco-112.md:185-191`. The range contains commit `3c7781c file(eco-113): in-flight runs`, including lock, journal and Job Object rules. The witness diff is empty, and no ECO-113 mechanism entered `method/tools/bomdd-run.py`, but the required full-range scope condition is false. |
| 2 | IA-01 repaired (B2) | PASS | `method/tools/bomdd-run.py:215-254` records whether this invocation created the stored object; `:282-292` removes only such an object; `:674-686` rolls back execution-copy and ledger failures and emits the required second line on removal failure. `:690-695` does not roll back after launch/spawn attempt. Live selftest passed; mutations `rollback-not-own`, `rollback-off`, and `left-line-off` each went red for their intended arm. |
| 3 | IA-02 repaired (B3) | PASS | `method/tools/bomdd-run.py:261-279` creates, re-hashes and removes a fresh temporary execution copy; `:496-504` passes only `exec_brief` as `BOMDD_BRIEF`; `:691-694` removes it in `finally`. Independent throwaway-repository probe: `cell_exit=0 exec_removed=True dir_removed=True archival=True bytes=True B4=BRIEF_NOT_COMMITTED names_sha=True`. Mutations `exec-is-store` and `exec-not-removed` went red. |
| 4 | Stored, not launched | PASS | R13 at `method/tools/bomdd-run.py:51-57`, `committed_copies()` at `:295-320`, B3 at `bomdd/60-change-order-eco-112.md:96-108`, B4 at `:109-117`, and L4/L5/L10 at `:163-171` consistently distinguish stored briefs from ledger-recorded launches. |
| 5 | Selftest and mutations | PASS | Live selftests all exited 0. The repair mutation instrument exited 0 with `rule mutations PASS`; all 9 mutations were detected, including all five repair mutations. `b-store`, the three `b-refused-stores-nothing` checks, and `b-other-ledger-same-store` use per-call record counts/checks at `method/tools/bomdd-run.py:1082-1108,1150-1159,1232-1237`. The T5 shape remains intact. |
| 6 | Regression | PASS | Live three-tool selftests passed. Static review found G1–G5, B1, B4, B5, O1 and T1–T6 retained. First-line formatting remains routed through `_fit`; mutation controls for G3, B4, LF and B1-first still went red for their own reasons. |
| 7 | Records | FAIL (blocking, same IA-03) | The §6 hashes were reproduced exactly: design `319a97a47fe2`, old tool `bfea9b4d6d3d`, V3 instrument `7abaa22324cc`, V3 run-1 JSON `b18d908a147f`, and summary `24ae76a6a9a1`. The repair descriptions match the code and evidence. However, the round’s mandated `f2d91d4..4d2c05f` scope contains ECO-113 rule material, contrary to the scope claim checked in item 1. |

## Findings (IA-03, IA-04, …)

- **IA-03 — blocking — diff scope.** The mandated inspection range contains the intervening ECO-113 filing and probe artifacts, including the lock, journal and Job Object rules. This violates the explicit scope condition and ECO-112 V6, even though the ECO-112 repair commit itself does not implement those mechanisms. Suggested repair: provide a ruled inspection target/history whose `f2d91d4..target` range contains only ECO-112 §2 paths and no ECO-113 rules, or formally amend the scope/acceptance before reinspection.

## Calibration receipt

- Claims assessed: IA-01 repair, IA-02 repair, regression, mutation sensitivity and scope compliance.
- Measurement: observed. Repair/regression evidence is qualified; scope evidence is qualified and proves failure.
- Instrument defects detected: none.
- Battery: Q1–Q6, Q9–Q11 asked; Q7 asked through the nine mutation controls; Q8 NA.
- Limits: the independent dynamic probe covered cell deletion, archival preservation, cleanup and B4 refusal, but did not exhaust concurrency or hostile store mutation.

## Not checked (limits)

- The V3 instrument was not re-run, as instructed. Its repaired-commit result is operator-run, pending, and not evidence in this round; final acceptance waits for it.
- No network, push, commit, repository write, self-conformance run, CI check, or closure promotion was performed.
- Deliberate mutation of the clone-local store and the L10 concurrent-launch race were not exercised.