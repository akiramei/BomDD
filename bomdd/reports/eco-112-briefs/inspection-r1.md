[INFORM / COMPLETE]

REJECT IA-01, IA-02

- inspector: EQ-002 / Codex CLI / GPT-5
- HEAD at start / at end: f2d91d4e4eb523ef9970d71e38f2e8a651408770 / f2d91d4e4eb523ef9970d71e38f2e8a651408770
- commits: 0 / files changed: 0
- selftests run: bomdd-run `ADVANCE OK: selftest PASS(起動4/dry2/...)`, bomdd-job `bomdd-job selftest PASS(整合 NONE / ...)`, bomdd-witness `ADVANCE OK: selftest PASS(known-good / ...)`

## Items

| # | item | verdict | evidence (file:line, command and the key output) |
|---|---|---|---|
| 1 | Scope | PASS | `git diff --stat 19243e5..f2d91d4` shows only §2 paths; `git diff ... -- method/tools/bomdd-witness.py` was empty. |
| 2 | G1–G5 | PASS | [bomdd-job.py](C:/Users/akira/source/repos/BomDD/method/tools/bomdd-job.py:392) validates a non-empty, trimmed, duplicate-free string list; lines 399–427 strip fences/comments, require exactly one column-0 line, parse it, and compare sets. [bomdd-run.py](C:/Users/akira/source/repos/BomDD/method/tools/bomdd-run.py:334) verifies the witness first; lines 366–390 apply R11, `GATES_UNDECLARED`, exact-name `REQUIRED_GATE_MISSING`, then committed-copy checking. Required/matched gates are recorded separately. Witness verification remains the sole reader of declared exits. Boundary review found empty lists and whitespace/case variants fail closed; duplicate witness names cannot hide a red exit because witness verification precedes G3. |
| 3 | B1–B5 | FAIL (blocking) | Argument ordering, CR rejection, hashing, same-directory temporary replacement, re-read, `BOMDD_BRIEF`, tree-bound lookup and ignored leftovers conform at [bomdd-run.py](C:/Users/akira/source/repos/BomDD/method/tools/bomdd-run.py:198), lines 211–298 and 599–638. However, lines 611–624 store the brief before attempting the ledger write; IA-01. Lines 255–259 treat a missing per-ECO store as an empty successful set, permitting IA-02. Directory briefs and a store directory that is a file fail closed; relative and external brief paths are copied by content as specified. Blob candidates are size-filtered but fully re-hashed. |
| 4 | O1 | PASS | `entry_code` is distinct from witness `code` at [bomdd-run.py](C:/Users/akira/source/repos/BomDD/method/tools/bomdd-run.py:303); lines 489–509 put every new code in the first line and `_fit` bounds emitted decision lines to 80 columns. |
| 5 | T1–T6 | PASS | Selftest calls carry `--brief`; refusal arms test unique fragments; `kb-ledger-unwritable` and `kb-ledger-inside` include executors; report cleanup uses `unlink(missing_ok=True)`. G/B/O arms and the four recorded rule mutations go red for their intended reason. `_selftest_body`, literal argv calls, `fails`, and the absence of real `INSTRUMENT_MUTATION` messages preserve the V3 shape. Live runs of all three selftests exited 0. |
| 6 | Acceptance evidence | PASS with stated limit | Manufacture hashes match the current tools and pinned instrument. Recorded selftest exits are 0; mutations report G3-off 16 failures, B4-off 7, LF-off 1, and B1-first 1. The live inspection launch ledger records brief SHA-256 `4df6cdca…68c26e4`, size 5906; re-fetching `BOMDD_BRIEF` produced the same hash and size. The manufactured V3 instrument result is explicitly pending and was not claimed complete at this commit. |
| 7 | Boundary exploration | FAIL (blocking) | IA-01 and IA-02 are fail-open/loss boundaries. Other examined cases—empty/duplicate/whitespace gate declarations, ID case, fenced/comment/mid-line declarations, directory brief, store-directory-as-file, same-size/different-byte blobs, missing `bomdd/reports/`, linked worktree, relative/external brief paths—either fail closed or behave as declared. |
| 8 | Records | FAIL (blocking) | The manufacture record and L4 are stronger than the implementation at the two findings below. L4 discloses deletion “by hand” but does not honestly cover deletion by the launched cell through the exact writable `BOMDD_BRIEF` path supplied by B3, followed by promotion success. Other L1–L3 and L5–L9 limits match the inspected behavior. |

## Findings (IA-01, IA-02, …)

- **IA-01 — blocking — [bomdd-run.py](C:/Users/akira/source/repos/BomDD/method/tools/bomdd-run.py:611).**  
  `store_brief()` completes before `write_ledger()` at line 624. If an otherwise advancing invocation uses a real brief but its ledger is unwritable, the invocation returns `UNMEASURABLE`, launches nothing, yet leaves the brief in the store. This contradicts B2’s “a refused invocation stores nothing” and can later make promotion demand a committed copy for a cell that never ran. The existing `kb-ledger-unwritable` arm uses `--brief none`, so it cannot expose this defect.  
  Suggested repair: make failed ledger recording roll back a newly created store object safely, with concurrency-aware ownership, and add a real-brief/unwritable-ledger arm that checks both no launch and no new store entry.

- **IA-02 — blocking — [bomdd-run.py](C:/Users/akira/source/repos/BomDD/method/tools/bomdd-run.py:255).**  
  A launched cell receives the writable store path as `BOMDD_BRIEF`. If it deletes that file—or the per-ECO directory—promotion sees `FileNotFoundError` and returns success with zero copies. The decision ledger still proves that a brief was launched, but B4 never reconciles against it. Thus the original content is no longer re-fetchable and promotion fails open. L4 mentions deletion “by hand” outside the trust boundary, but not deletion by the ordinary launched cell to which B3 deliberately exposes the path.  
  Suggested repair: make the cell’s reference read-only where enforceable and, more importantly, retain an append-only manifest or reconcile promotion against all recorded launched brief hashes; a missing historical object must produce `BRIEF_STORE_FAILED` or `BRIEF_NOT_COMMITTED`. Add a cell arm that deletes `BOMDD_BRIEF` and verifies subsequent promotion refuses.

## Not checked (limits)

- The pinned V3 instrument was not re-run; the brief states it takes roughly 45 minutes, and its manufactured-result artifact is explicitly pending at this commit.
- No network, push, commit, or repository write was performed.
- Symlink/race attacks involving deliberate mutation of `.git/bomdd-run` were not exhaustively exercised; they share the store’s declared trust-boundary limitation.
- Closure-only V4, V7 and V8 cannot be observed at this manufacture commit.

human_action: none. Inspection is complete; the two blocking findings require correction and reinspection before ACCEPT.