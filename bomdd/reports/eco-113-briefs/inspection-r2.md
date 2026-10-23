[INFORM / COMPLETE]

ACCEPT

- inspector: EQ-002 / Codex CLI / GPT-5
- HEAD at start / at end: fcd9fd70977da709cd4152e9f66b98bf0e23ea3c / fcd9fd70977da709cd4152e9f66b98bf0e23ea3c
- commits: 0 / files changed: 0
- selftests run: bomdd-run `ADVANCE OK: selftest PASS(...)`, bomdd-job `bomdd-job selftest PASS(...)`, bomdd-witness `ADVANCE OK: selftest PASS(...)`

## Items

| # | item | verdict | evidence (file:line, command and the key output) |
|---|---|---|---|
| 1 | IA-01 repaired | PASS | `bomdd-run.py:709-755` reads records in order using separate `opened` and `started` state. Invalid duplicate-open starts and close-before-any-start go to corrupt; repeated closing is harmless; reuse after close reopens. `bomdd-run --selftest` exit 0 includes `v4f-duplicate-start`, `v4f-close-before-start`, `v4f-repeated-end`, and `v4q-reuse-opens`. The isolated `A4iii-order` mutation produced exit 1 naming `v4f-close-before-start`; mutation driver exit 0. |
| 2 | IA-02 repaired | PASS | `bomdd-run.py:683-742` rejects non-object records, invalid/empty `run_id`, non-integer/bool offsets, offsets after their record or off a line boundary, and digest mismatches. Invalid quarantines exclude nothing; valid ones exclude prior corrupt lines in order. V4(f) arms at `bomdd-run.py:2511-2604` cover every required case. The isolated `A4iv-digest` mutation produced exit 1 naming `v4f-q-digest`; mutation driver exit 0. |
| 3 | Amended text against code | PASS | J1 `order:125-129`, J2 `:130-140`, R3 `:149-152`, A3/A4 `:165-175`, and L11 `:274-278` agree with `journal_read`, `_quarantine_fault`, `open_runs`, `judge`, and `_recover`. S4 retains `corrupt_offset` as the first corrupt complete line at `order:217`; code supplies `corrupt[0][0]` at `bomdd-run.py:783-784`. |
| 4 | Acceptance evidence | PASS | V4(f)/(q) are stated at `order:346-354,369`; the repair arms are at `bomdd-run.py:2511-2615`. `repair/README.md` maps the arms and seven A4 mutations. Recorded evidence reports ECO-113 27/27 and ECO-112 9/9 mutations detected, each on its intended arm. Two higher-risk mutations were independently rerun and confirmed. |
| 5 | Regression | PASS | All three selftests independently exited 0. `bomdd-run` reports `ECO-113 V1-V4 PASS · branch: msvcrt.locking + Job Object (Windows)`. Repair evidence records the earlier 20 ECO-113 and all 9 ECO-112 mutations still caught. `git diff 2271102..fcd9fd7 -- method/tools/bomdd-witness.py` was empty. |
| 6 | Scope under exception ruling | PASS | `diff_window.py . f2d91d4 fcd9fd7` exited 0 and reported PASS: five ECO-113 commits, 36 paths, none outside `allowed_paths`. It records the excluded ECO-112 commits, three independent record groups, and their reasons. Positive control `--control-include 597e842` exited 1 and detected the 126-path record commit outside scope. |
| 7 | Records | PASS | Order §5 accurately records r1 IA-01/IA-02; §6 `:496-528` accurately describes the implementation, arms, and 27/27 + 9/9 results. Amendment loop A `:688-718` preserves its unconverged result; A2 `:720-738` records convergence and the moved mutation obligation. Register `:3554-3582` remains consistent with implemented status, paths, gates, and responsibilities. No unsupported claim found. |

## Findings (IA-03, …)

None.

## Not checked (limits)

- No network or CI query was performed, as prohibited.
- Of the 36 recorded rule mutations, two repair-critical cases (`A4iii-order`, `A4iv-digest`) were rerun; the remaining mutations were assessed from committed evidence plus the complete current selftests.
- No real-repository `bomdd-run.py ECO-113 …` invocation was made.
- Repository status and diff were empty at completion. The inspected ECO-113 run journal, runs journal, ledger lock, and witness retained their starting sizes and SHA-256 values; the held `ECO-113.lock` was not read, stopped, or released.

human_action: none. Inspection scope is complete.