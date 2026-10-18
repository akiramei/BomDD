[INFORM / COMPLETE]

REJECT IA-01, IA-02

- inspector: EQ-002 / Codex CLI / GPT-5
- HEAD at start / at end: `2752d18a8b738ab1dd4d3a327a599a2e935c9d0c` / `2752d18a8b738ab1dd4d3a327a599a2e935c9d0c`
- commits: 0 / files changed: 0
- selftests run: bomdd-run `ADVANCE OK: selftest PASS(...)`, bomdd-job `bomdd-job selftest PASS(...)`, bomdd-witness `ADVANCE OK: selftest PASS(...)`

## Items

| # | item | verdict | evidence (file:line, command and the key output) |
|---:|---|---|---|
| 1 | Scope | PASS | `git diff --stat 2271102..2752d18` shows only the twelve permitted paths. Witness diff is empty. `git diff 5ddd428..2271102 -- method/` changes only `method/improvements.md`. |
| 2 | X — exclusion | PASS | `bomdd-run.py:604-646`: common-dir lock path, persistent file, required open flags, byte-0 nonblocking lock, conflict/error distinction and handle lifetime. Live-holder/kill/concurrency/read-only arms passed. |
| 3 | W — ownership | PASS | `bomdd-run.py:467-545,1194-1213,1250-1290`: kill-on-close only; existing name rejected; suspended `Popen` followed immediately by handle assignment; entry remains outside; resume occurs after records; outer `finally` closes the job. No pid is used for judgement or stopping. |
| 4 | J — judgement | **FAIL — blocking** | `bomdd-run.py:708-719` accumulates all closing IDs globally, without event ordering. Probe: `release(r)` followed by `start(r)` produced `open_runs=[]`. Thus a genuinely open later run can disappear and is not classified. See IA-01. |
| 5 | R — recovery | PASS | `bomdd-run.py:1298-1387`: options are isolated; active human equipment required; release and quarantine hold the ECO lock; `CELL_ALIVE` is refused; neither path resumes nor stops anything. |
| 6 | A — records | **FAIL — non-blocking** | Normal writes satisfy A1/A2 (`bomdd-run.py:649-705`): one binary `os.write` per line, short-write rejection, `fsync`, torn-tail repair. However structurally valid but invalid journal records are accepted or silently ignored; probe with `quarantine.offset=999999` suppressed a later corrupt line. See IA-02. |
| 7 | S and O | PASS | `bomdd-run.py:1063-1295` follows the required ordering, including report recheck under the launching lock, start→ledger→line→resume, end retries, and outer exception handling. `RUN_IN_FLIGHT` appears in `bomdd-run.py:135`, `bomdd-job.py:60-71`, and `operator-layer.md:55,132,149`. |
| 8 | T and acceptance evidence | PASS, conditionally qualified | All three selftests independently returned exit 0 and matched the filed first lines. Manufacture evidence maps V1–V5 to named arms; 20 ECO-113 and 9 ECO-112 mutations report red with their intended arm. These tests do not cover IA-01/IA-02, so they do not qualify the broader claim that every open run is classified. |
| 9 | Boundary exploration | **FAIL — blocking** | Throwaway probe: release-before-start → `[]`; duplicate starts → only the first start retained; past-EOF quarantine offset → `bad=0, excluded=1`. Directory/report timing and nested same-ECO invocation fail closed; large journals can exhaust memory but reach O3 rather than proceed. |
| 10 | Records and limits | **FAIL — blocking** | §4 accurately reports the exercised arms and the three recorded selftests. L1–L12 are otherwise honest, but §1 J2 and the register summary claim “every open run is classified”; IA-01 disproves that claim. L11 mentions manual deletion, not semantic mutation or malformed valid-JSON records. |

## Findings (IA-01, IA-02, …)

- **IA-01 — blocking — `method/tools/bomdd-run.py:708-719,766`.** `open_runs()` treats any `end`, `abort`, or `release` with a `run_id` as closing every start with that ID, regardless of record order. It also collapses duplicate starts with `setdefault`. Because IDs are UTC timestamps rather than guaranteed-unique values, clock rollback or an exact timestamp reuse can produce a later legitimate `start` already present in `closed`. After its entry disappears, classification sees no open run and permits another launch. On POSIX this can duplicate a still-running cell; on Windows it also matters when another handle keeps the job alive. Suggested repair: use an unguessable collision-resistant ID and parse the journal as an ordered state machine; reject duplicate live starts and closing-before-start records as journal corruption. Add negative arms for release/end-before-start, reused IDs, and duplicate starts pointing at different jobs.

- **IA-02 — non-blocking — `method/tools/bomdd-run.py:693-719`.** Journal validation stops at “JSON object.” Non-string `run_id` records are silently ignored, duplicate starts are collapsed, and any integer quarantine offset—including one past EOF—can exclude corrupt records without validating its position or `excluded_sha256`. These cases currently require corruption or modification outside the normal writer, so L11’s trust boundary limits immediate exploitability, but the boundary is not stated broadly enough and corruption can fail open. Suggested repair: validate event schemas and transitions, require quarantine offsets to be within the journal and on a line boundary, verify the excluded digest, and classify invalid complete records as `JOURNAL_CORRUPT`. Alternatively, explicitly extend L11 to exclude all journal modification and semantic corruption, while retaining fail-closed parsing for accidental damage.

## Not checked (limits)

- POSIX `flock`, native POSIX process behavior, and cross-host/shared-filesystem locking were not measured.
- CI and V6/V8 closure evidence were outside this in-flight inspection.
- Full mutation suites were not rerun; their checked-in outputs and mutation driver were inspected. The three permitted selftests were rerun.
- No destructive lock/symlink experiment was performed against the real repository.
- Calibration: evidence measurement was observed; qualification is conditional because Q3/Q10/Q11 expose the untested semantic-journal classes above. No repository files or run-state directories were changed.

human_action: none. Execution is complete; the blocking finding requires correction and a subsequent correction-confirmation inspection.