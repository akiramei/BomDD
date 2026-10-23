# Change Order — ECO-113 (in-flight runs: exclusion by an OS file lock, the cell owned by an OS job, in-flight judgement, recovery from an abnormal end, and atomic journal records)

> Ruling: user, 2026-10-18, "1:A 2:A 3:A" on the evaluation of an external proposal ("AI製造と外部ワークフロー制御の分離"), with the condition for ③:
> when only a start record exists, **do not conclude an abnormal end**; distinguish running / abnormal end / unknown; **prevent duplicate launches**.
>
> Split ruling: user, 2026-10-18, "B". ③ leaves ECO-112 and is designed here, independently and in parallel (not deferred). Further conditions:
> - **Abolish the hand-made lock-breaking scheme**; design again with an **OS file lock** as the candidate.
> - Treat **exclusion, in-flight judgement, recovery from an abnormal end, and the atomic commit of records as separate responsibilities.**
> - **The replacement by an OS lock is itself an object of independent review.**
> - The split relaxes no convergence rule (two consecutive rounds with zero new findings, limit 3); manufacture starts after this design converges.
> - No new workflow engine, LLM wiki or context access control; use the existing operator layer.
>
> Extension ruling: user, 2026-10-18, "2:A" after loop 1 ended unconverged (12→5→4). Conditions:
> - **A design in which pid reuse can make the tool misidentify or stop unrelated processes is not adopted.**
> - **First re-evaluate whether identifying or stopping the process tree is really needed for recovery.** If needed, consider an OS-managed
>   process-ownership mechanism such as a Job Object.
> - **Avoid complicating with home-made process-tree tracking or lock management.**
> - No manufacture before the design converges.
>
> Second extension: user, 2026-10-18, "2:A" after loop 2 ended unconverged (5→5→4; material 3→1→0). Conditions: first remove the common cause
> (one rule written in several places) — each rule gets one canonical place and is referred to elsewhere by its ID, keeping every acceptance observation
> and pass condition; keep the simplified design (OS file lock, Job Object); add no new mechanism or instrument; do not change the existing DoD; record
> each new finding as an existing design defect, an inconsistency from duplicated text, or a new defect from the consolidation.
>
> Third extension: user, 2026-10-18, "2:A" after loop 3 ended unconverged (4→3→2; material 0→0→0). Repair the two remaining findings — state as an
> acceptance condition that quarantine is refused while a cell runs; give an unexpected exception escaping `run()` an exit distinguishable from a normal
> refusal — keep the OS file lock and Job Object, add no new control mechanism, keep the default convergence rule, no manufacture before convergence.
>
> Fourth extension: user, 2026-10-18, "2:A" after loop 4 (1→0→1). Complete `JOURNAL_CORRUPT`'s record, line and recovery — and not only that
> omission: enumerate every S4 refusal reason and check mechanically that each has its ledger record, line and recovery rule. Keep the existing
> mechanisms; add no new state-management mechanism; keep the default convergence rule; no manufacture before convergence.
>
> Amendment ruling: user, 2026-10-24, "1:A 2:a" after inspection r1 (REJECT IA-01, IA-02; §5). **1:A** — the journal is read in order and invalid
> records stop classification as `JOURNAL_CORRUPT`; the amendment covers J1, J2's claim sentence, A4, L11 and the acceptance observations V4(f) and
> V4(q) (an acceptance change the user saw before ruling), with the references they directly affect (J2's `JOURNAL_CORRUPT` bullet, A3's
> interface, R3's exclusion, the coverage line); S4's table (reasons and ways out) is unchanged; no
> new state or mechanism; the amended text converges by the default rule (two consecutive rounds with zero new findings, limit 3) before the repair is
> manufactured; then inspection r2 (是正確認+回帰). **2:a** — V8's diff window is ruled for ECO-113 as an exception by ECO-112's method (§8 of
> ECO-112): the commits that are not ECO-113's are excluded with their reasons, non-interference is checked by diff, ECO-113's change set is enumerated
> in full as r2's target, and OBS-20261018-02 records its second case; not a general rule.
>
> Extension ruling: user, 2026-10-24, "A" after amendment loop A ended unconverged (7→2→1; every finding of rounds 2 and 3 in V4(f)'s prose recipes
> for building the quarantine arms). Remove the common cause first: V4(f) states what is observed, not how an arm is built; that each A4 check is
> needed is shown by T1's rule mutations, one per clause; then a new loop by the default rule (two consecutive rounds with zero new findings,
> limit 3).
>
> Records are English-primary.

## Equipment

- Filing and design: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- producer: EQ-004
- inspector: EQ-002
- Converge round reviewer: a fresh context of the same model that has not seen ECO-112's loops (context independence), read-only, resumed each round.
- Independent inspection: EQ-002 (Codex) — the OS-lock and the OS-job replacement included (user condition).

## 0. Basis

- **Gap ③ (measured at baseline `3a9de06`).** The decision record is written (`bomdd-run.py:456`) and the first line printed (`:460`) before `launch()`
  (`:462`); the cell runs under a blocking `subprocess.run(..., shell=True)` (`:320`). If the entry dies mid-cell, the ledger holds a decision with no cell
  record; the next invocation does not read the ledger and launches again. Two concurrent invocations for the same ECO both launch. The ledger path is
  free (`--ledger`) and defaults under the per-worktree git dir. The `--report` existence check (`:434`) runs before anything that could serialize runs.
- **What loop 1 taught.** Exclusion by an OS lock drew no finding after round 1. Every later material finding came from deciding whether the **cell**
  is still alive after its entry died: with `shell=True` the cell is a process tree under a shell, and any rule that follows that tree by pid meets pid
  reuse (R3-1: a false "alive", and a recovery procedure that could stop unrelated processes).
- **Re-evaluation (user condition): is identifying or stopping the cell's process tree needed for recovery?**
  - **Stopping: not needed.** If the OS ends the cell's whole tree when its entry ends, no process is ever left for recovery to stop. The tool, and the
    recovery procedure, then stop nothing.
  - **Identifying: needed only to tell "abnormal end" from "unknown"** (user condition ③). An OS-owned container answers it by its own existence,
    with no pid involved.
  - **Mechanism: a Job Object with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`** that the entry creates and names, and into which it places the cell —
    **the entry itself stays outside the job** (loop-2 review L2R1-1: an entry inside its own kill-on-close job kills any in-process caller, the selftest
    included, and nested self-assignment fails at depth 101). The cell is started suspended, assigned through the process handle the entry holds, and
    resumed, so everything the cell starts is in the job from creation. The entry holds the job's only handle; when the entry ends, normally or not, the
    handle closes and the OS ends every process still in the job.
    Measured on this machine (Windows 11, CPython 3.13, 2026-10-18, scratchpad probes; the probing process was itself already inside a job, so the
    jobs are nested): K1 with the cell started suspended (`shell=True`), assigned by handle and resumed (its one thread), the entry was **not** in the
    job and the job counted 2 active processes (`cmd.exe`, the command), whose counter advanced; K2 in-process: after the cell exited the job still
    existed with 0 active processes, and once the entry closed its handle it no longer opened by name (`ERROR_FILE_NOT_FOUND`, 2); K3 a separate entry
    killed mid-cell → the command's counter stopped and the job was gone. (The earlier probe J1-J4, with the entry inside the job, showed the same
    kill-on-close behaviour; that placement is dropped for the reason above.)
  - **POSIX has no Job Object.** No home-made substitute is built (user condition): on POSIX an open run whose entry is gone reads `UNKNOWN`.
- **The OS lock, measured on this machine (loop 1):** a live holder blocks a non-blocking attempt with `EACCES` (13); after the holder is killed the lock
  was free at once; the lock is freed with the holder's death whether or not a child inherited the handle; a second handle in the same process is blocked.
  `EDEADLK` comes only from `LK_LOCK`. Opening a read-only lock file also gives errno 13 — from `os.open`, not from the lock. A file opened without
  `O_BINARY` writes `\n` as `\r\n`. Unlocked concurrent ledger appends (3 × 3000) lost 1269 lines and tore 24. **POSIX `flock` is not measured here.**

## 1. Change request — the rule register

**Each rule below is the canonical text of that rule; every other section of this order refers to it by its ID and does not restate it**
(user ruling "2:A", 2026-10-18). The five responsibilities stay apart and meet only in the launch sequence S1: **X** exclusion (may this entry act now),
**W** ownership (the cell lives no longer than its entry), **J** judgement (is an earlier run open, and in what state), **R** recovery (close an open
run), **A** records (commit and read lines). **S** is the launch sequence, **O** output, **T** selftests. Judgement never follows processes.

### X — exclusion

- **X1 — the lock file.** `<git-common-dir>/bomdd-run/<ECO>.lock`, one per clone whatever `--ledger` says and whichever worktree runs. It holds no
  state; bomdd-run never deletes it (deleting a held lock file on POSIX lets a second process lock a new file of the same name). A `<git-common-dir>`
  that cannot be derived is X2's `LOCK_UNAVAILABLE`.
- **X2 — acquiring it.** `os.open(O_RDWR | O_CREAT | O_BINARY | O_NOINHERIT)` (POSIX: `O_CLOEXEC`), then a non-blocking exclusive lock: Windows
  `msvcrt.locking(fd, LK_NBLCK, 1)` at offset 0; POSIX `fcntl.flock(fd, LOCK_EX | LOCK_NB)`. **Only the locking call's conflict** (Windows `EACCES`
  from `LK_NBLCK`; POSIX `EWOULDBLOCK`/`EAGAIN`) means another entry is alive → cause `ENTRY_ALIVE` (the "running" state). Any error from `os.open`,
  the directory, or any other error from the locking call → cause `LOCK_UNAVAILABLE`; its way out is fixing the environment, not recovery.
- **X3 — who holds it.** A launching invocation (`--cell`) from before classification until it returns; a release or quarantine for its whole run; a dry
  invocation only for its classification. The OS releases it when the holder's handle closes or the holder dies.

### W — ownership (Windows)

- **W1 — the job.** The launching entry creates a Job Object named `Local\BomDD-run-<ECO>-<run_id>` with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` and
  no breakaway flag. **The entry is never in the job**, so in-process callers (the selftest) are unaffected.
- **W2 — placing the cell.** The cell is started with `Popen(..., shell=True, creationflags=CREATE_SUSPENDED)` and assigned to the job through `Popen`'s
  process handle **immediately**, with nothing in between; it is resumed later, at S1's resume step. The resume finds the cell's threads by a thread
  snapshot filtered by the cell's pid, which is safe from pid reuse because the entry holds the process handle throughout. Everything the cell starts is
  in the job from creation. **No pid is used for judgement or for stopping.**
- **W3 — the handle.** The entry holds the job's only handle and closes it **on every exit from `run()` once the job exists, exceptions included**
  (a `finally`): S1.1 (after W4's failure), S1.2, S1.3, S1.6, S2, S3, and any exception between them; if the entry dies, the OS closes it. Closing it ends every process still in the job, and the job ceases to exist.
- **W4 — failing to set up.** Creating or configuring the job, or assigning the cell, fails → the suspended cell is terminated through its handle (it has
  run nothing); code `JOB_UNAVAILABLE`. What is recorded and printed is S1's. (A failed resume is S2's, not this rule's.)
- **W5 — the namespace key.** `Local\` resolves per Windows session and per AppContainer; the `start` record carries `session` (the entry's Windows
  session id) and `appcontainer` (its token's AppContainer SID, or `none`).
- **W6 — POSIX.** No job is created; nothing ties the cell to the entry.

### J — judgement

- **J1 — the source.** The run journal `<git-common-dir>/bomdd-run/<ECO>.runs.jsonl`, read only through A2, **in order** (amendment 1:A). A `start`
  record opens its `run_id`; a later `end`, `abort` or `release` record with that `run_id` closes it; an open run is a `start` that no later closing
  record has closed. A closing record for a `run_id` that is already closed closes nothing (S1.6 may write `end` again); a `start` for a `run_id` that
  was closed earlier opens a new run. Two records break this order and are invalid (A4): a second `start` for a `run_id` that is still open, and a
  closing record for a `run_id` that no earlier `start` opened. An invalid record opens and closes nothing. The ledger (`--ledger`) is not read for this.
- **J2 — the classes.** Only while holding the lock (X3). No open run → proceed. An open run means its entry is gone (else X2 would have refused); it is
  classified by its job, named in its `start` record:
  - `ABNORMAL_END` — Windows; host, `session` and `appcontainer` equal to the classifier's; and opening the job by name fails with
    `ERROR_FILE_NOT_FOUND`, or the job exists with 0 active processes: **no process in the run's job remains**;
  - `CELL_ALIVE` — the job exists with active processes (while the OS is still ending them, or because another process holds a handle to it, which keeps
    kill-on-close from firing);
  - `UNKNOWN` — POSIX; a host, `session` or `appcontainer` that differs or cannot be read; any other error from opening or querying the job;
  - `JOURNAL_CORRUPT` — a complete line that does not parse, or an invalid record (A4).
  A start without an end is never read as an abnormal end by itself. **Every open run that J1 reads is classified**, and an invalid record (A4) is never
  skipped: it is `JOURNAL_CORRUPT` (amendment 1:A); the reported class is the most restrictive
  present — `JOURNAL_CORRUPT` > `CELL_ALIVE` > `UNKNOWN` > `ABNORMAL_END` — and the record lists every open run with its class (S4). Verdicts and exits: O1.

### R — recovery

- **R1 — the commands.** `bomdd-run.py ECO --release RUN_ID --by EQ-NNN` and `bomdd-run.py ECO --quarantine-journal --by EQ-NNN` take no other
  option (`--cell`, `--executor`, `--report`, `--range`, `--ledger`, `--brief` → `ARG_ERROR`). Neither runs `decide()`, launches, or stops a process.
- **R2 — release.** Takes the lock (X2), re-classifies the open run named by RUN_ID (J2): `CELL_ALIVE` refused; `ABNORMAL_END` and `UNKNOWN` closed by a
  `release` record `{run_id, classified, cause, by}`, with `cell: unverified` for `UNKNOWN` (the person releasing asserts that no process of the run is
  running). A RUN_ID that is not an open run → `ARG_ERROR`.
- **R3 — quarantine** (the way out of `JOURNAL_CORRUPT`). Takes the lock and commits into the same journal a `quarantine` record
  `{offset, excluded_sha256, by}` as A4 (iv) defines it; a valid quarantine excludes, from then on, the lines A4 (iv) names (unparsable lines and
  invalid records before `offset`), and an invalid one excludes nothing. Nothing is moved or deleted;
  every parsed open run stays open and needs its own release. Refused while any parsed open run is `CELL_ALIVE`.
- **R4 — `--by`.** Must name equipment with `kind: human`, `status: active` in `bomdd/70-equipment.yaml`; it is self-reported.
- **R5 — what recovery is not.** It does not resume or stop anything. Restarting is a new launch after the release, decided afresh on the current tree
  through the witness (bomdd-run R3). Resumption inside a cell is the cell's own contract.

### A — records

- **A1 — journal write.** One record = one JSON line (`ensure_ascii=True`) ending in `\n`, written by a single `os.write` on a descriptor opened with
  `O_WRONLY | O_APPEND | O_CREAT | O_BINARY | O_NOINHERIT` (POSIX: `O_CLOEXEC`), then `os.fsync`. A short write or an error is a failure. Journal
  writes happen only while holding the lock (X3).
- **A2 — journal read.** Bytes split on `b"\n"` only. A final segment without `\n` is a torn record, treated as absent; the next writer, holding the lock,
  truncates the file to the last `\n` and commits a `repair` record `{truncated_bytes, sha256}`. A torn `start` precedes no started cell (S1 resumes or
  starts the cell only after `start` is committed).
- **A3 — the interface.** commit(record) → ok / failed; read() → records, torn tail, corrupt lines (the unparsable lines and invalid records, A4, read in order and after valid quarantines) — or an error: a journal that exists but cannot be
  read (an `OSError`) → cause `JOURNAL_UNREADABLE`; its way out is fixing the environment. A journal that does not exist has no records. Nothing else
  touches the journal.
- **A4 — a complete unparsable line or an invalid record** cannot come from bomdd-run: it writes no unparsable line (single writer, single write,
  under the lock, binary mode) and no invalid record (a `start` only after J2 found no open run, S1; a closing record only after its own `start`,
  S1.3, S1.6, S2, R2; a `quarantine` from its own read under the lock, R3). It makes J2's `JOURNAL_CORRUPT`, and the way out is R3. For R3 and for S4's `corrupt_offset`, an invalid record counts as a line that does not parse. **Invalid records** (amendment 1:A):
  (i) a line that parses but is not a JSON object; (ii) a `start`, `end`, `abort` or `release` whose `run_id` is not a non-empty string; (iii) a record
  that breaks J1's order; (iv) a `quarantine` whose `offset` is not an integer, is not at a line boundary, or lies after the quarantine record's own
  position, or whose `excluded_sha256` is not the sha256 of the lines it excludes (the not-yet-excluded unparsable lines and invalid records before
  `offset`, in file order, each with its terminating `\n`, concatenated) — such a quarantine excludes nothing. Every other record — `repair`, `interrupted`, any other `event` value, a non-string `event`, a record with no `event`, a near-miss such as
  `"Start"` — opens and closes nothing.
- **A5 — ledger appends.** Every ledger append (existing ones included) holds a short blocking OS lock on `<ledger path>.lock` (outside the worktree,
  like the ledger — bomdd-run R4); not obtained within 10 s → a ledger write failure (the existing handling).

### S — the launch sequence (where X, W, J, A meet)

- **S1 — order.** bomdd-run's existing argument checks, including resolving the ledger path and its bomdd-run R4 checks (they move before the lock;
  their refusals are unchanged and write no record) → lock (X2) → classify (J2; a refusal or an open run → S4) → re-check `--report` (bomdd-run R10,
  now under the lock; cause `REPORT_EXISTS`) → `decide()` → if ADVANCE:
  1. **Windows:** create the job (W1), start the cell suspended and assign it (W2). On W4 failure: the decision becomes `UNMEASURABLE`, code
     `JOB_UNAVAILABLE`; close the job handle if the job was created (W3); the ledger decision record and the first line are written with it; no
     `start`; return per O1.
  2. commit `start` `{run_id, job_name, entry_pid, host, session, appcontainer, started_at}` (A1). On failure: close the job handle (W3); the decision
     becomes `UNMEASURABLE`, code `JOURNAL_WRITE_FAILED`; the ledger decision record and the first line are written with it.
  3. write the ledger decision record (bomdd-run R4). On failure: close the job handle, commit `abort` `{run_id, reason}`, return per O1.
  4. print the first line (bomdd-run R7).
  5. **launch:** Windows — resume the cell (W2); POSIX — `Popen` the cell here (no job, no suspension; W6). Same terminal session, so the cell's
     prompts pass through (bomdd-run R5). Before this step no process of the cell has run.
  6. wait → commit `end` `{run_id, cell_exit}` (retried 3 times) → write the ledger cell record with `journal_end: committed|failed` (one added field;
     the tool's two-record shape and its readers are unchanged) → close the job handle (W3) → return.
- **S2 — a failed resume** (after the first line): close the job handle (the OS ends the suspended cell), commit `end` with `cell_exit: "RESUME_FAILED"`,
  write the ledger cell record with the same `cell_exit`, print the second line `cell not started (RESUME_FAILED)` (where `cell exit N` goes), return
  per O1.
- **S3 — an interrupted wait** (`KeyboardInterrupt` or an exception): commit a non-closing `interrupted` note; write the ledger cell record with
  `cell_exit: "interrupted"`, `journal_end: none`; print `cell interrupted`; close the job handle (the OS ends the cell's tree); return per O1. The run
  then reads `ABNORMAL_END` (J2) and is released (R2).
- **S4 — refusals before `decide()`: the table of every reason this ECO defines.** A refusal reason is defined in this order only by the phrase
  "cause" followed by the reason in backticks inside a rule, or as a class bullet of J2 — the convention the mechanical check reads (receipt, loop 5).
  Each such reason is one row. Any other stop before `decide()` is one of bomdd-run's existing argument refusals (unchanged, no record; S1) or O3.
  Each refusal writes one ledger decision record with `decision` (the verdict from O1), `stop_type` `RUN_IN_FLIGHT`, `cause` (the reason) and the
  fields in the "record" column, and prints the line `<VERDICT> <ECO> RUN_IN_FLIGHT(<cause>) <run_id prefix or -> → operator` (within 80 columns,
  bomdd-run R7) — except where the row says otherwise. **If that record cannot be written** (A5's timeout, a write error), the existing ledger-failure
  line is printed instead and the exit is 2 (the ledger failure wins over the row's verdict).

  | reason (`cause`) | arises in | record: extra fields | line | way out |
  |---|---|---|---|---|
  | `ENTRY_ALIVE` | X2 | none (the journal is not read without the lock) | the standard line, `-` for the run | wait for the other entry; retry (L2) |
  | `LOCK_UNAVAILABLE` | X2 | `lock_error` (the OS error, or `git` when X1's directory cannot be derived) | the standard line, `-` | fix the environment (X2); no release |
  | `JOURNAL_UNREADABLE` | A3 | `journal_error` (the OS error) | the standard line, `-` | fix the environment (A3); no release |
  | `ABNORMAL_END` | J2 | `open_runs` (every open run's `run_id` and class) | the standard line with the first open run | release (R2) |
  | `CELL_ALIVE` | J2 | `open_runs` | the standard line with the first `CELL_ALIVE` run | wait and retry; if persistent, outside the tool (L3) |
  | `UNKNOWN` | J2 | `open_runs`, `unknown_because` (POSIX / host / session / appcontainer / job query error) | the standard line with the first `UNKNOWN` run | release with `cell: unverified` (R2) |
  | `JOURNAL_CORRUPT` | J2 | `corrupt_offset` (the byte offset of the first complete line that does not parse), `open_runs` (those parsed) | the standard line, `-` | quarantine (R3), then release each open run (R2) |
  | `REPORT_EXISTS` | S1, the `--report` re-check under the lock | **no ledger record** (as every `ARG_ERROR` of bomdd-run R10) | `UNMEASURABLE ARG_ERROR: …` (bomdd-run R10's message) | move the existing report aside as evidence (L9) |

### O — output and vocabulary

- **O1 — verdicts and exit codes (bomdd-run R8, amended).** `ENTRY_ALIVE`, `ABNORMAL_END`, `CELL_ALIVE`: `STOP`, stop type `RUN_IN_FLIGHT`, exit 1.
  `LOCK_UNAVAILABLE`, `JOURNAL_UNREADABLE`, `UNKNOWN`, `JOURNAL_CORRUPT`: `UNMEASURABLE`, stop type `RUN_IN_FLIGHT`, exit 2. `REPORT_EXISTS`: `UNMEASURABLE ARG_ERROR`,
  exit 2 (bomdd-run R10, unchanged). `JOB_UNAVAILABLE`, `JOURNAL_WRITE_FAILED`:
  `UNMEASURABLE`, stop type `MISSING_INPUT`, exit 2. A launching run otherwise exits as today (0 when launched), **except S2 (`RESUME_FAILED`) and
  S3 (interrupted), which exit 2**, and S1.3's failure, which exits 2. Release and quarantine: 0 = closed, 1 = refused (`ENTRY_ALIVE`, `CELL_ALIVE`),
  2 = cannot measure or bad arguments; their first line is `RELEASED|QUARANTINED <ECO> <run_id or offset> (<classified>) by <EQ>` or S4's line. An unexpected exception: O3 (exit 2, line `INTERNAL_ERROR`).
  Delivery: operator, for every `RUN_IN_FLIGHT` cause and for `JOB_UNAVAILABLE` and `JOURNAL_WRITE_FAILED`. These verdicts and exits apply to launching and dry invocations; release and quarantine have their own (below).
- **O3 — an unexpected exception.** Any exception (`KeyboardInterrupt` included) that escapes the body of `run()` — outside S3's wait — is caught at
  `run()`'s outer edge after W3's `finally` has closed the job handle: the traceback goes to stderr, the line `UNMEASURABLE <ECO> INTERNAL_ERROR(<class>)
  → operator` is printed (whatever was printed before it), and `run()` returns 2. It is therefore never read as a normal refusal (`STOP`, exit 1), and the
  line names it apart from other exit-2 paths. No ledger record is attempted (the ledger may be what failed). If `start` was already committed, the run stays
  open and is classified next time (J2; the job is gone, so normally `ABNORMAL_END`) and released (R2). O1's table refers to this rule.
- **O2 — vocabulary and documents.** `RUN_IN_FLIGHT` is added to bomdd-job's stop vocabulary (not ledger-derivable; derived by the entry, like
  `INDEPENDENCE_FAIL`), to bomdd-run's delivery table (operator), and to operator-layer.md §2 (11 words). The core gets the word, its delivery, and the
  hand procedure (§7): before launching a cell by hand, confirm that no other launch of the same change is running, and write the launch and its end in
  the change order. The mechanism sentence goes to operator-layer.md's adapter section A1.

### T — selftests

- **T1 — arms.** Each responsibility (X, W, J, R, A, S, O) gets known-bad arms that go red for their own reasons; the observations, and which rules they
  cover, are listed in §3. A refusal arm checks a message fragment or code unique to its own reason, not only the verdict prefix. Existing arms keep
  their verdicts and their reasons. Rules without an arm of their own say why in §3's coverage line.
- **T2 — shape.** New in-process calls follow ECO-112's T5 (in `_selftest_body`, through `call`); the arms that need separate processes (concurrency,
  the killed entry) run bomdd-run as a child process and are outside ECO-112's V3 instrument (ECO-112 T6).

### Manufacture

- ECO-112's **M1** governs the order: ECO-112 first, then this ECO, rebased on ECO-112's verified head.

### Declared limits (each refers to the rule it limits)

- **L1 (X2, W6, J2):** POSIX — no Job Object and no substitute; an open run whose entry is gone reads `UNKNOWN` and is released on a human assertion
  (R2's `cell: unverified`); a wrong assertion allows a duplicate launch. `flock` is not measured here (V1(g) records the branch exercised).
- **L2 (X2, W3):** a just-killed holder may read `ENTRY_ALIVE` briefly, and `CELL_ALIVE` is usually transient (OS unlock and job teardown times are not bounded).
- **L3 (J2, R2):** a persistent `CELL_ALIVE` (another process keeps a handle to the job) has no in-tool way out; the holder is found and closed outside the
  tool, outside the trust boundary.
- **L4 (J2):** `ABNORMAL_END` means "no process in the run's job remains", not "nothing of the run is running": work a cell hands to a broker outside its
  job — a COM/DCOM out-of-process server, WMI `Win32_Process.Create`, Task Scheduler, `wsl.exe`, `docker run`, ShellExecute to an already-running
  application — survives it. Release is a human act for this reason.
- **L5 (W3):** a cell's background processes do not outlive its entry on Windows. Consequences: a harness timeout on the entry ends the cell (the Claude
  Code shell tools stop a foreground command at 2 minutes by default and 10 at most), so long cells are launched as background tasks; a cell child that
  asks for `CREATE_BREAKAWAY_FROM_JOB` fails; a cell ended mid-write can leave `.git/index.lock`, which the witness tree does not show.
- **L6 (W2):** an entry that dies in the instant between `Popen(CREATE_SUSPENDED)` and the assignment leaves a suspended `cmd.exe` outside the job; it
  runs nothing, inherits no handle, and nothing ends it. The run has no `start` record, so nothing reads it as open.
- **L7 (W4):** if the entry is in a job whose limits forbid nested assignment of its child, launching fails closed; the probes ran nested and passed.
- **L8 (X1, W5):** locks or jobs on a git dir shared across hosts or sessions are outside the design. Entries that take different lock mechanisms on one
  clone do not exclude each other (a WSL Python with `flock` on drvfs, or a Cygwin/MSYS Python, against a native Windows Python); run bomdd-run on one
  clone from one kind of Python.
- **L9 (S1, S3):** if the entry dies after the cell exits but before `end`, the run reads `ABNORMAL_END` and its exit and report binding are lost on release;
  a `--report` path that then exists makes the next launch `ARG_ERROR` (bomdd-run R10), and the operator moves it as evidence.
- **L10 (J2, X3):** a sequential relaunch after a completed or released run is not refused; a dry run's classification can make a concurrent launch read
  `ENTRY_ALIVE`.
- **L11 (X1, J1, A4, R4):** deleting the lock file or the journal, or writing records into the journal, by hand is outside the trust boundary; the
  journal is clone-local; `--by` is self-reported. What the reader guarantees for records it did not write is fail-closed reading (A4: an invalid
  record is `JOURNAL_CORRUPT`, never skipped), not detection of a forgery: a well-formed `end` or `release` written by hand closes a run, a
  well-formed `quarantine` with a matching digest excludes lines, and a record A4 counts as "every other record" (a missing or near-miss `event`)
  opens and closes nothing (amendment 1:A).
- **L12 (T1):** the bomdd-run and bomdd-job selftests are not run in CI; they are run locally and recorded (V5).

### Not changed

- `bomdd-witness.py`, `self-conformance.py`, hooks, `.github`, the playbook, skills, `.claude/skills`, the templates other than operator-layer.md.
- Machine distribution to product repositories (EXP-20260914-01 stays suspended).
- No scheduler, workflow engine, LLM wiki or context access control (user condition).

## 2. No-impact prediction (before manufacture; frozen at filing)

- **The diff:** `method/tools/bomdd-run.py`, `method/tools/bomdd-job.py`, `method/templates/product-profile/operator-layer.md`,
  `method/improvements.md`, this order, the register, and `bomdd/reports/eco-113-*/`.
- **Not touched:** `method/tools/bomdd-witness.py`, `method/tools/self-conformance.py`, hooks, `.github`, the playbook, skills, `.claude/skills`.

## 3. Acceptance (conditions; frozen at filing)

required_gates: [V1, V2, V3, V4, V5, inspection]

**Gated** (read by ECO-112's G3 at this ECO's promotion, since ECO-112 is manufactured first): V1-V5, and V7 as the gate `inspection`. **Checked at
closure:** V6 (CI), V8 (the diff window). Each item lists what is observed and what passes; the mechanism is the cited rule's. Every arm checks the cause
or code in the first line and the ledger record (T1).

**Coverage (T1) — the one place that maps rules to items:** X1, X2, X3 → V1(a)-(g). W1 → V2(a), (g); W2 → V2(a), (f); W3 → V2(a), (b), (c), (g), (h);
W4 → V2(c); W5 → V2(d); W6 → V2(e). J1 → V2(i), V4(f), (q); J2 → V2(a), (b), (d), (e), (g), V4(q). R1 → V3(c); R2 → V3(a), (b), (d); R3 → V3(e); R4 → V3(c).
A1 → V4(a), (d), (e), (g); A2 → V4(c), (f); A3 → V4(o); A4 → V4(f); A5 → V4(j). S1 → V4(a), (b), (i), V2(c), (e); S2 → V2(h); S3 → V4(h); S4 → V4(n), (p).
O1 → V4(k); O3 → V4(m), V2(g); O2's code half (the word in bomdd-job's vocabulary and bomdd-run's delivery table) → V4(l).
Without an arm of their own: A3's normal outcomes (the interface; exercised through every A1/A2 arm — its error outcome is V4(o)); R5 (a statement of what recovery does not do; V3(a)'s relaunch goes
through `decide()`, and V3(f) checks that nothing is stopped); O2's text half (the word, the count and the hand procedure in operator-layer.md's core,
the sentence in its adapter section A1 — prose, checked by the independent inspection, V7); T1-T2 (rules about the arms themselves; V7).

- **V1 — exclusion** (real processes): condition =
  (a) a live entry holding the lock → a second launching invocation gets `ENTRY_ALIVE`, and its cell is not launched;
  (b) the holder killed → the lock can be taken within 5 s (polled);
  (c) two concurrent launching invocations, and two with different `--ledger` values or from two worktrees → exactly one launches;
  (d) a dry invocation while a cell runs → `ENTRY_ALIVE`; (e) after a complete run the lock file still exists;
  (f) a read-only lock file or an unwritable directory → `LOCK_UNAVAILABLE`, not `ENTRY_ALIVE`;
  (g) the platform branch exercised is recorded.
- **V2 — ownership and judgement** (Windows, real processes): condition =
  (a) the entry killed mid-cell, the cell being a shell with a child command → the command stops, the job is gone, the run reads `ABNORMAL_END`;
  (b) another process holds a handle to the job when the entry is killed → the cell keeps running and the run reads `CELL_ALIVE`; that handle closed →
      the cell stops and the run reads `ABNORMAL_END`;
  (c) job creation, configuration or assignment failing (patched) → `JOB_UNAVAILABLE`; the ledger decision record and the first line say so; no `start`; the job is gone;
      no process of the cell left running;
  (d) opening the job failing with an error other than not-found (patched) → `UNKNOWN`; a `session` or `appcontainer` that differs from the classifier's,
      or another host → `UNKNOWN`;
  (e) on POSIX (or with the Windows branch patched off) an open run whose entry is gone → `UNKNOWN`, and the cell is started by `Popen` after the first
      line (S1.5);
  (f) classification calls no pid-based liveness function (`os.kill` and the process-snapshot functions patched to raise around the classification call
      only);
  (g) after an in-process launch (the selftest calling `run()`), the selftest's own process is not in the run's job and holds no handle to it, and the job
      is gone; a job existing with 0 active processes → `ABNORMAL_END`; an exception raised (patched) after the cell was assigned and before
      the resume → `run()` returns per O3 and the job is gone;
  (h) a resume failing (patched) → S2's second line, ledger cell record and `end`, exit 2, the job gone;
  (i) J1: an open run recorded only in the journal, with an empty or a different ledger, is still classified (the ledger is not read).
- **V3 — recovery:** condition =
  (a) release of `ABNORMAL_END` and of `UNKNOWN` commits a release record (`cell: unverified` for `UNKNOWN`), and the next launch proceeds;
  (b) release of `CELL_ALIVE` refused; release while another entry holds the lock → `ENTRY_ALIVE`;
  (c) a wrong RUN_ID, a non-human `--by`, and `--release`/`--quarantine-journal` with any other option → `ARG_ERROR`, each with its own message fragment;
  (d) two concurrent releases → one release record;
  (e) quarantine of a journal with a corrupt line commits a quarantine record without moving the file; parsed open runs stay open, each needing its own
      release; a quarantine while a parsed open run's job has active processes (`CELL_ALIVE`) → refused, exit 1, and no quarantine record is written;
  (f) no recovery path stops a process.
- **V4 — records, sequence and output:** condition =
  (a) `start` commit failure (patched) → no launch, `JOURNAL_WRITE_FAILED`; the ledger decision record and the first line say so;
  (b) a ledger decision-record failure after `start` → `abort` committed, no launch, exit 2;
  (c) a torn final line → treated as absent; the next writer truncates it and commits a `repair` record with its sha256;
  (d) `end` commit failure → retried; the ledger cell record carries `journal_end: failed`; the run reads open;
  (e) a short write → failure; (f) a complete unparsable line → `JOURNAL_CORRUPT`; a record containing U+2028 or U+0085 reads as one record;
      each kind of invalid record (A4 (i)-(iv)) → `JOURNAL_CORRUPT` (the refusal, and the record among the reader's corrupt lines): a parsed line
      that is not an object; a `start`, an `end`, an `abort` and a `release` whose `run_id` is not a string or is empty; a second `start` for an open
      `run_id`; a closing record before any `start` of its `run_id` (the r1 probe: `release(r)` then `start(r)`; after a quarantine `r` reads open);
      a quarantine whose `offset` is not an integer, is past its own position (the r1 probe's offset 999999), is not at a line boundary, or whose
      digest does not match — an invalid quarantine excludes nothing, so a corrupt line it names stays a corrupt line; a repeated `end` for a
      closed run is not `JOURNAL_CORRUPT`. **That each of A4's checks is needed is shown by T1's rule mutations** (manufacture evidence), one per
      clause — A4 (i), (ii), (iii), and (iv)'s integer, position, boundary and digest checks: with that check removed from a copy, the selftest goes
      red on that clause's own arm (amendment 1:A, extension "A");
  (g) on Windows, the journal's bytes contain no `\r`;
  (h) an interrupted wait → an `interrupted` note, the ledger cell record with `cell_exit: interrupted` and `journal_end: none`, the line
      `cell interrupted`, exit 2, and `ABNORMAL_END` next time;
  (i) `--report` created between the first check and the lock → `ARG_ERROR` under the lock;
  (j) three processes appending to one ledger concurrently → every line present and parsable;
  (k) each path's exit code and first line match O1;
  (l) O2: `RUN_IN_FLIGHT` is in bomdd-job's stop vocabulary and in bomdd-run's delivery table, and the job vocabulary check fails if either is missing (the arm removes it from one side);
  (m) O3: an exception raised (patched) at three points → each time the line `UNMEASURABLE <ECO> INTERNAL_ERROR(<class>) → operator`, exit 2 (not 1),
      a traceback on stderr, and the job gone; and per point: during S1.4, and between the wait and the `end` commit → the run stays open and reads
      `ABNORMAL_END` next time; after `end` (at the ledger cell-record write) → the run is closed and there is no ledger cell record;
  (n) S4, row by row: each row's reason is produced (real processes or a patched condition), and its ledger record carries exactly the
      row's extra fields (none for `ENTRY_ALIVE`; no record at all for `REPORT_EXISTS`) and its line is the row's line, with the run's prefix or `-`.
  (o) A3's error: a journal that exists but cannot be read (patched) → `JOURNAL_UNREADABLE`, and the record carries `journal_error`;
  (p) S4's ledger failure: a refusal whose record cannot be written (patched) → the existing ledger-failure line, exit 2;
  (q) J2's precedence: two open runs of different classes → the reported class is the more restrictive one, and `open_runs` lists both; a `run_id` reused after its run was closed opens a new run that is classified like any other (amendment 1:A).
- **V5**: condition = the existing selftests of bomdd-run, bomdd-job and bomdd-witness pass, with their reasons unchanged (run locally and recorded);
  `git diff -- method/tools/bomdd-witness.py` is empty.
- **V6 (closure)**: condition = self-conformance exits 0, observed before each commit; CI green on each pushed revision.
- **V7**: condition = independent inspection by EQ-002, ranges 境界探索 (the OS lock and the OS job included) then 是正確認+回帰; ACCEPT, as the gate `inspection`.
- **V8 (closure)**: condition = inside the diff window, only the paths in §2.

## /preflight receipt (start path: self-triggered — applying the filed design, 2026-10-19)

- **Classification:** continuation (applying a filed design; the user's instruction 2026-10-19: manufacture ECO-113 after confirming ECO-112 verified,
  the filed design fixed, the existing manufacture, inspection and acceptance procedure, no widening of scope).
- **Minimum contract:**
  - baseline — the order unchanged since filing `3c7781c` (`git log` shows that commit only; sha256 `aaa0358a3668` at `2271102`) and the tools at
    ECO-112's verified bytes (`bomdd-run.py` `69e849630f90`, the bytes V3 run 2 measured; `bomdd-job.py` `823eafd97d6f`; `operator-layer.md`
    `589082d8dc48`; no tool change in `5ddd428..2271102`): **confirmed**;
  - current work state — ECO-112 `verified` (register, and `bomdd-job.py ECO-112` projects state verified with stop NONE); ECO-113 `filed`, stop NONE:
    **confirmed**;
  - unresolved items — L5R3-1 corrected at filing; OBS-20261018-01/-02/-03 recorded outside this ECO (user: follow the recorded handling, do not widen the
    scope): **confirmed**;
  - handoff state — reconstructable from the order, the register and git: **confirmed**;
  - acceptance target — §3 (V1-V8, frozen at filing): **confirmed**.
- **Discovered (not in the minimum contract):**
  - **the diff window:** the register's `diff_audit.baseline` is `f2d91d4`, so `f2d91d4..head` holds ECO-112's later commits and three record commits
    (`597e842`, `7a107bf`, `2271102`), whose paths are outside §2 — V8 read literally fails at closure. This is OBS-20261018-02's second case; ECO-112's
    ruling was for ECO-112 only, so V8's reading for ECO-113 is the user's (asked at closure, not decided here): **contradicted** (for V8 only);
  - `allowed_paths` lists two of §2's `bomdd/reports/eco-113-*/` folders; the manufacture adds `eco-113-manufacture/` and `eco-113-briefs/` (inside §2):
    **stale**, corrected in the register;
  - Codex runs with its process tree inside a kill-on-close job (probe 2026-10-19, read-only sandbox: exit 0): **confirmed** for the inspection cell.
- **Start decision: PROCEED_WITH_LIMITS** — manufacture, acceptance V1-V5 and the inspection proceed; V8's reading waits for the user. Overrides: none.

## 4. Manufacture (2026-10-19, user instruction: manufacture after ECO-112 verified)

**Inputs fixed:** the design — this order at `3c7781c` (unchanged up to `2271102`), filed by the user's exception ruling; the register entry at
`2271102`; the tools at `2271102` (= ECO-112's verified bytes, above). ECO-112 M1 is met: ECO-112 was verified first (`5ddd428`) and this manufacture is
built on it. OBS-20261019-01 (review snapshots) stays on hold (user), and nothing of it is in this diff.

**What changed, by rule:**
- `bomdd-run.py` — header R15 (an index to §1; the rules stay here). X: `lock_file`, `acquire_lock`, `release_lock`. W: `_job_create`,
  `_job_configure`, `_job_assign`, `_snapshot_threads` (used only by the resume), `_job_resume`, `_job_close`, `_job_query`, `_identity` /
  `_appcontainer` (W5), the `_win_branch` switch (W6). J: `journal_read`, `open_runs`, `classify_run`, `judge`. A: `journal_commit` (the torn tail
  repaired by the next writer), `_ledger_lock` in `write_ledger` (A5). R: `_recover` (`--release`, `--quarantine-journal`). S/O: `run()` is now a
  wrapper — `_run()` for the body, `_teardown()` (W3: the job handle, the lock, the execution copy and the job view on every exit) and O3's
  `INTERNAL_ERROR`; `_run()` follows S1 (the ledger-path checks moved before the lock; the lock; classification; the `--report` re-check;
  `decide()`; S1.1-S1.6; S2; S3); `_refuse()`, `in_flight_rec()`, `in_flight_line()` (S4); `IN_FLIGHT_VERDICT` (O1); `RUN_IN_FLIGHT` in `DELIVERY`
  (O2). `launch()` became `cell_env()` and `cell_record()` (the cell is started at S1.1 on Windows and at S1.5 on POSIX). T1/T2: the selftest block
  `ECO-113(R15)` (in `_selftest_body`, through `call`; the arms that need separate processes start `bomdd-run.py` as a child), the fixture's human
  equipment `EQ-007` (R4), `vocabulary_mismatch()` (V4(l)), and the PASS report's second line naming the platform branch (V1(g)).
- `bomdd-job.py` — `RUN_IN_FLIGHT` in `STOP_VOCABULARY` (O2; not ledger-derivable).
- `operator-layer.md` — §2: 11 words and the `RUN_IN_FLIGHT` row; §7: the hand procedure; adapter A1: the mechanism sentence (O2).
- The register — status `implemented`; `allowed_paths` adds `bomdd/reports/eco-113-manufacture/` and `bomdd/reports/eco-113-briefs/` (inside §2).

**Manufacture choices where the rule text leaves the detail open** (each kept consistent with the cited rule; none changes a rule or an acceptance item):
1. **Recovery records go to the journal only.** R1 gives `--release` and `--quarantine-journal` no `--ledger`; they write no ledger record, and a refusal
   prints S4's line (O1's release/quarantine exits).
2. **Release is refused while the journal has a corrupt line** (`JOURNAL_CORRUPT`, exit 2): S4's way out for that row is quarantine first, then release.
3. **Quarantine's `offset`** is the byte just past the last corrupt line, and `excluded_sha256` is the sha256 of the excluded lines' bytes in order. A
   quarantine with no corrupt line is `ARG_ERROR`.
4. **On Windows the cell's `Popen` is part of S1.1** (W2 starts it suspended there), so a `Popen` failure is W4's `JOB_UNAVAILABLE`, nothing has run,
   and ECO-112's B2 rolls the brief back like any refused launch. On POSIX `Popen` stays at S1.5, after the decision record, and a spawn failure is
   recorded in the cell record as before.
5. **S2 and S3 cell records carry no report binding** (`report: null`): the cell did not complete, and a `MISSING` verdict must not become the ledger's
   last cell record with a report (the inspection gate reads that record — bomdd-run R11).
6. **The line shows the whole `run_id`** (23 characters, within 80 columns for `ECO-NNN`), because `--release` needs the whole id; S4 says "prefix".
7. **`end` is attempted once and retried 3 times** (S1.6: "retried 3 times").
8. **The O3 line names `-`** when the first argument is not a valid ECO id.
9. **A job name that already exists** (`ERROR_ALREADY_EXISTS`) is a W4 failure, never a shared job.
10. **`unknown_because`** is the name of the key (`host`, `session`, `appcontainer`) when a value differs or cannot be read, `POSIX`, or
    `job query error`; it is recorded for the first `UNKNOWN` run.

**Acceptance measured before the manufacture commit** (evidence: `bomdd/reports/eco-113-manufacture/`):
- **V1-V4 — PASS (selftest arms).** `bomdd-run.py --selftest` exit 0; its second line names the branch exercised: `msvcrt.locking + Job Object
  (Windows)` (V1(g)). The arms that need separate processes start `bomdd-run.py` as child entries on the selftest's own temporary repository: a live
  holder and a dry run read `ENTRY_ALIVE` (V1(a)(d)); the killed holder frees the lock within 5 s, its cell's child command stops, the job is gone and the
  run reads `ABNORMAL_END` (V1(b), V2(a)); two concurrent launches — same ledger, two ledgers, two worktrees — launch exactly one cell each time (V1(c));
  a process holding a handle to the job keeps the cell alive (`CELL_ALIVE`) until it closes the handle (V2(b)); two concurrent releases write one
  record (V3(d)); three processes append 900 ledger lines and all 900 parse (V4(j)). The map from every acceptance item to its arms is
  `bomdd/reports/eco-113-manufacture/README.md`. **POSIX is not measured** (L1): the POSIX branch was exercised only as Windows with the branch switched
  off (V2(e)); `flock` and the POSIX `Popen` path did not run.
- **V5 — PASS.** The existing arms keep their verdicts (the first line of the bomdd-run selftest is unchanged); bomdd-job and bomdd-witness selftests
  exit 0; `git diff -- method/tools/bomdd-witness.py` is empty.
- **Rule mutations (T1, "red for its own reason"): 20/20 detected.** One rule broken per case — X2 ×2, W1, W3, W4, J2 ×3, R2 ×2, R3, A1, A2, A5, S1, S1.6, S3,
  S4, O3, O2 — and each turned the selftest red with the rule's own arm named (`rule-mutations.txt`). **ECO-112's nine rule mutations re-run on the
  manufactured tools: 9/9 detected, each naming its own arm** (`rule-mutations-eco-112.txt`).
- **V7 / real cells:** observed with the independent inspection, whose cell is launched through the manufactured entry.

**Found during manufacture (recorded; no rule changed):**
- **Two arms first passed for the wrong reason, found by the rule mutations and corrected before this commit:** the S1.6 arm compared the number of
  `end` attempts with the code's own constant (`1 + END_RETRIES`), so a mutation of the constant was not caught — it now expects the order's number (4);
  and the O2 case first removed the word from bomdd-run's table, which crashes the selftest's own line builder (a crash, not a reason) — the case now
  removes it from bomdd-job's vocabulary, the other side V4(l) names. Both are instrument defects of this manufacture, attributed to the arms, not to
  the rules.
- **A broken job leaks suspended cells.** With kill-on-close removed (W1) or the handle left open (W3), the mutated selftest leaves suspended `cmd.exe`
  cells; they hold inherited handles, so the first mutation driver (reading through a pipe) waited until its timeout. This is the failure W1-W3
  prevent; the driver now writes to files, and the selftest reports a fixture-cleanup failure as a finding instead of a traceback. The leaked cells
  were resumed by hand and ended (they hold no lock).
- **Codex runs inside a kill-on-close job:** a probe (2026-10-19) placed `codex exec` (read-only sandbox) in such a job the way the entry places a cell:
  exit 0, output as asked. L5 (no breakaway) therefore did not stop the inspection cell in that probe; the workspace-write sandbox is observed with r1.
- **The diff window (V8):** see the preflight receipt — asked at closure.

## 5. Independent inspection r1 (2026-10-19, EQ-002, range 境界探索) — REJECT IA-01, IA-02

- **Launched through the manufactured entry** on `2752d18` (CI 39166932515 success; witness tree `a90ecad107b3`, gate self-conformance):
  `bomdd-run.py ECO-113 --cell "codex exec -s workspace-write -m gpt-5.6-sol … - < %BOMDD_BRIEF%" --brief <brief outside the worktree> --executor EQ-002
  --report bomdd/reports/eco-113-briefs/inspection-r1.md --range 境界探索`. Brief `787a5502…` (stored; committed copy
  `bomdd/reports/eco-113-briefs/inspection-brief-r1.md`, same sha256); report `inspection-r1.md` (`48fd4056…`); the ledger's cell record binds it
  (`report REJECT sha256:48fd40561357 (EQ-002)`, `journal_end: committed`). Codex ran at its default reasoning effort (low).
- **Observed on the real cell (V1, V2, A1):** the journal holds `start` and `end` for run `20261018T211926.052338Z` (job
  `Local\BomDD-run-ECO-113-20261018T211926.052338Z`); the Codex cell ran inside the job with the workspace-write sandbox and exited 0; a dry
  invocation while the cell ran read `STOP ECO-113 RUN_IN_FLIGHT(ENTRY_ALIVE) - → operator` and wrote its refusal record to the ledger.
- **Items PASS:** scope (witness diff empty), X, W, R, S and O, T and the acceptance evidence (conditionally: the arms do not cover the findings below).
  **FAIL:** J, A, boundary exploration and records, through two findings:
  - **IA-01 — blocking.** `open_runs()` closes a `start` by any `end`, `abort` or `release` with the same `run_id`, whatever their order, and keeps
    only the first of two `start` records with one id. `run_id` is a UTC timestamp, not a guaranteed-unique value, so a reused id (clock rollback, an
    equal timestamp) can make a later, genuinely open run read as closed — it is then not classified and a second launch is allowed. The inspector's
    probe: `release(r)` then `start(r)` → `open_runs = []`. **The defect is in J1's definition ("a `start` record with no `end`, `abort` or `release`
    for its `run_id`"), which the code follows literally, and in the unstated assumption that ids are unique** — not only in the code. J2's claim
    "every open run is classified" and the register summary repeat it.
  - **IA-02 — non-blocking.** The reader validates a record only as a JSON object: a record whose `run_id` is not a string is skipped silently, and any
    integer quarantine `offset` — one past the end of the file included — excludes corrupt lines without its position or `excluded_sha256` being
    checked (probe: an offset of 999999 hid a later corrupt line). Such records come only from outside the normal writer, so L11's trust boundary limits
    the exposure, but L11 names deletion by hand, not semantic corruption. The inspector offers two repairs: validate (schema, transitions, an offset
    inside the file on a line boundary, the digest) with invalid complete records as `JOURNAL_CORRUPT`, or extend L11.
- **Reproduced by the producer** on `2752d18`'s reader (a throwaway script on temporary journals): `release(r)` then `start(r)` → no open run; two
  `start` records for one id → only the first kept; a `quarantine` with offset 999999 before a corrupt line → 0 corrupt, 1 excluded.
- **Not repaired yet:** both repairs change rule text of the filed design (J1, J2, A4, L11); the user rules how they are made (the user's condition:
  stop and ask before adding a mechanism or changing an acceptance item).

## 6. Repair manufacture (2026-10-24, user ruling "1:A", after amendment loop A2 converged)

**Inputs fixed** (sha256 prefixes; `git show <rev>:<path>`): the design — this order at `860097d` (`78f995207b9e`), the amendment converged (loop A 7→2→1
unconverged → user "A": the common cause removed → loop A2 1→0→0); the tool — `bomdd-run.py` at `2752d18` (`5f27e777e39f`, unchanged up to `860097d`).
Only `bomdd-run.py` and this ECO's evidence change.

**What changed, by rule:**
- **J1, A4 (IA-01, IA-02):** `journal_read` reads the journal in order. A `start` opens its `run_id`, a later closing record closes it, a closing record
  for a closed run closes nothing, and a `start` after close opens a new run. The invalid records of A4 (i)-(iv) go to the corrupt lines and open
  and close nothing: not an object; a `run_id` that is not a non-empty string; a second `start` for an open id; a closing record with no earlier
  `start`; a quarantine whose `offset` is not an integer, lies past its own position, is not at a line boundary, or whose digest is not the sha256 of
  the corrupt lines before `offset` (each with its `\n`). Only a valid quarantine excludes, in order. `_quarantine_fault` holds (iv)'s four checks.
  `journal_read` returns only valid records.
- `open_runs` reads those records in order (no global "closed" set any more). `judge`, `_recover` and the S4 rows are unchanged; `corrupt_offset` is
  the first corrupt line or invalid record (A4). R3's quarantine (offset just past the last corrupt line, the digest of the corrupt lines in order) is
  valid under A4 (iv) by construction.
- **Selftest (V4(f), V4(q)):** arms `v4f-not-object`, `v4f-run-id-*` (a `start`, `end`, `abort` and `release` with `run_id` 5, and a `start` with an
  empty id), `v4f-duplicate-start` (the first `start` stays open), `v4f-close-before-start` (the r1 probe: the release is corrupt, `r` opens), `v4f-q-integer`,
  `v4f-q-position`, `v4f-q-boundary`, `v4f-q-digest` (each built so that only its own check makes the quarantine invalid), `v4f-q-r1-probe` (offset 999999
  hides nothing), `v4f-repeated-end`, `v4q-reuse-opens`; each invalid journal is then quarantined by R3 and must read clean.

**Acceptance measured before the repair commit** (evidence: `bomdd/reports/eco-113-manufacture/repair/`):
- **V1-V5 — PASS:** the bomdd-run selftest exit 0 (all earlier arms and the new ones); bomdd-job and bomdd-witness exit 0;
  `git diff -- method/tools/bomdd-witness.py` empty.
- **Rule mutations: 27/27 ECO-113 cases and 9/9 ECO-112 cases detected, each on its own arm.** The seven V4(f) requires — A4 (i), (ii), (iii), and (iv)'s integer, position, boundary and digest checks — each
  removed in a copy and caught on its own arm, with the 20 earlier ECO-113 cases and ECO-112's 9 re-run on the repaired tool.
- **r1's probes on the repaired reader:** `release(r)` then `start(r)` → `r` open, the release corrupt; two starts → the first open, the second
  corrupt; offset 999999 before a corrupt line → 2 corrupt, 0 excluded.
- **Found during the repair (an instrument defect of the arms, attributed to the selftest, not to the rules):** the first run of the A4 (i) and A4 (iv)
  integer mutations crashed the selftest instead of failing an arm, because the selftest's own helpers called `journal_read` directly, outside
  `run()`'s O3 handler. They now go through one guard (`jread_safe`), which turns a reader exception into a named failure; both mutations then turned
  the selftest red on their own arms.

## 収束 receipt (converge self-application)

### Loop 1

- Round 1: 12 findings (6 material) — the pre-launch order unfixed (F1); refusal path and R4/R7 (F2); `journal_end` placed in a record written before it
  (F3); errno 13 from open vs lock (F4); `CELL_ALIVE` with no way out, zombies, exit code 259 (F5); two release paths that reopen duplicates (F6);
  the reason P3 holds, per platform, and the unlock time (F7); Windows text mode against the single write, `splitlines()` (F8); the `--report` race (F9);
  option list and R8 for release (F10); `RUNNING` covering two facts (F11); `Popen` and interrupts, the operator-layer hand procedure (F12).
- Round 2: 5 findings (3 material) — the interrupt path killed only the shell and closed the run while the command lived (R2-1, measured); quarantine
  moved the journal (R2-2); unlocked ledger appends lose and tear lines (R2-3, measured); refusals did not name the run (R2-4); the inherited-handle arm
  is Windows-only (R2-5).
- Round 3: 4 findings (1 material) — R3-1 the process-tree rule accepts children of a process that reused a dead parent's pid (a false `CELL_ALIVE`, and
  a recovery procedure that could stop unrelated processes); R3-2 V3(f) red on POSIX by design; R3-3 the interrupt path's outputs unstated; R3-4 an
  unreadable creation time not mapped to `UNKNOWN`.
- **判定: 未収束** (round 軌跡: 12→5→4; material 6→3→1). User ruling "2:A": extension, with the conditions in the header.

### Loop 2

- **Re-evaluation first (user condition):** stopping the process tree is not needed for recovery; identifying it is needed only to tell abnormal end from
  unknown, and an OS-owned Job Object with kill-on-close answers that by its existence (measured J1-J4). The pid-based tree rule, the creation-time
  checks, the 15 s tree-stability check, the `spawned` record and the stop-the-tree procedure are **removed**, not repaired. POSIX gets no substitute.
- How the four round-3 findings end: R3-1 removed with the pid rule (no pid is used to classify or to stop; V2(f) checks it); R3-2 removed with the
  descendant arm (POSIX now reads `UNKNOWN` by design, V2(e)); R3-3 specified (1-6, V4(h)); R3-4 removed with the creation-time reads.

- **Round 1, 5 (3 material).** L2R1-1 an entry inside its own kill-on-close job kills in-process callers, the selftest included (reviewer's probe: exit 0
  at handle close; nested self-assignment fails at depth 101) → the entry stays outside; the cell is started suspended, assigned by handle, resumed
  (measured K1-K3). L2R1-2 "job gone, so no process of the run remains" is false for brokered work → the class is restated as "no process in the run's
  job remains" and brokers are declared. L2R1-3 `Local\` is per session and per AppContainer → both recorded and compared. L2R1-4 the job "exists, 0
  active" had no class, and a persistent `CELL_ALIVE` no way out → classified `ABNORMAL_END`, and the way out declared. L2R1-5 harness timeouts,
  breakaway, `index.lock` → declared; long cells as background tasks.
- **Round 2, 5 (1 material).** L2R2-1 a job failure after the first line re-opened round-1 F1 → suspended start and assignment moved before the
  records and the line; only the resume follows, and its failure has a stated second line and cell record. L2R2-2 the instant between `Popen` and the
  assignment → declared, nothing in between. L2R2-3 V2(f) collided with the launch's thread snapshot → limited to classification; the resume's pid filter
  stated safe (handle held). L2R2-4 mixed lock mechanisms (WSL drvfs, Cygwin/MSYS) → declared. L2R2-5 "transient" contradiction → reworded.
  The loop cannot reach two rounds of zero any more (5→5→?); round 3 is run for the trajectory.
- **Round 3, 4 (minor) — not repaired** (a repair would start a third loop). L2R3-1 1-2.3 still lists a resume failure as "no launch", against 1-6;
  L2R3-2 what a `JOB_UNAVAILABLE` decision records and prints is not stated (R4 needs its decision record; `JOURNAL_WRITE_FAILED` has V4(a));
  L2R3-3 the R8 amendment omits the resume-failure exit 2; L2R3-4 the launch order is written only for Windows (POSIX `Popen` must take the place of
  the resume, after the first line).
- **判定: 未収束** (round 軌跡: 5→5→4; material 3→1→0). Limit of 3 rounds reached. **No manufacture and no filing commit** until the user rules.
- **DoD:** ✔ D1; ✔ D2; ✔ D3; ✔ D4; ✘ D5 (L2R3-1, L2R3-4); ✘ D6 (L2R3-2, L2R3-3); ✔ D7 (the Job Object claims measured, K1-K3, and re-read by the
  reviewer); ✔ D8; ✔ D9 (no pid for judgement or stopping); ✔ D10 (no home-made tree tracking; one OS lock, one OS job).
- **Where the findings come from:** after round 1, the material findings were about the launch order; every round-3 finding is the same fact stated in
  two places that disagree (1-2.3 vs 1-6, V2(i) vs V4(a), the R8 list vs the paths, the order vs the platforms).
- **未収束事項:** L2R3-1 to L2R3-4 (unrepaired).

### Loop 3 (user ruling "2:A", 2026-10-18: extension, after removing the duplicated rules first; keep the OS file lock and Job Object design)

- **Common cause removed before review (user condition):** one rule written in several places. §1 is now a rule register (X1-X3, W1-W6, J1-J2, R1-R5,
  A1-A5, S1-S4, O1-O2, T1-T2); each rule's text appears once, and the limits and the acceptance refer to rule IDs. The acceptance keeps every
  observation and pass condition it had. The design is unchanged (one OS lock, one OS job); no new mechanism or instrument; the DoD is unchanged.
- **Where the old section numbers went** (the loop 1-2 records above use them): 1-1→X1-X3; 1-2.1→W1, W2; 1-2.2→W3; 1-2.3→W4; 1-2.4→W5;
  1-2.5→W6; 1-3→J1-J2; 1-4→R1-R5; 1-5→A1-A4; 1-6→S1-S4, O1 and A5; 1-7→O2; 1-8→T1-T2; the shared-file bullet→ECO-112's M1.
- **The four loop-2 round-3 findings, repaired in the register:** L2R3-1 → W4 no longer lists a resume failure (S2 owns it); L2R3-2 → S1.1 states that a
  `JOB_UNAVAILABLE` decision still writes its ledger decision record and first line (V2(c)); L2R3-3 → O1 lists the exit 2 of S2 and S3; L2R3-4 → S1.5
  states the POSIX launch point (V2(e)).
- **Classification of new findings (user condition):** each finding is recorded as one of — **existing design defect** / **inconsistency from duplicated
  text** / **new defect from the consolidation**.

- **Round 1, 4 (minor).** The reviewer compared the register with the previous text rule by rule: nothing dropped. L3R1-1 [new defect from the
  consolidation] T1 promised an arm per rule → T1 is per responsibility again, §3 has a coverage line (rules without an arm say why), and V2(i) (J1)
  and V4(l) (O2) were added. L3R1-2 [new defect from the consolidation] W3 did not list every handle close → it does (S1.1-S1.3, S1.6, S2, S3), and
  V2(c) checks the job is gone. L3R1-3 [inconsistency from duplicated text] S1 repeated O1's stop type and delivery → removed from S1; O1 now also states
  the delivery for `JOB_UNAVAILABLE`/`JOURNAL_WRITE_FAILED` and that its verdicts are those of launching and dry invocations. L3R1-4 [new defect from
  the consolidation] IDs clashing with outside IDs → §0's bullet renamed `Gap ③`; every outside reference qualified (`bomdd-run R3/R4/R5/R7/R8/R10`,
  operator-layer.md's adapter section A1, ECO-112's G3).
- **Round 2, 3 (minor).** Nothing dropped. L3R2-1 [new defect from the consolidation] the coverage line counted O2 as covered though V4(l) covers only its
  code half → split; the text half has no arm, with its reason. L3R2-2 [inconsistency from duplicated text] the rule-to-item mapping was written in the
  coverage line and in the V headings, and they disagreed → the headings no longer list rules; the coverage line is the one place and names items.
  L3R2-3 [existing design defect] W3 closed the handle on named paths only → every exit from `run()`, exceptions included; V2(g) gains an exception arm.
  The loop cannot reach two rounds of zero any more (4→3→?); round 3 is run for the trajectory.
- **Round 3, 2 (minor) — not repaired** (a repair would start a fourth loop). L3R3-1 [existing design defect] R3's refusal while a parsed open run is
  `CELL_ALIVE` has no arm (lost from V3(e) in loop 2); L3R3-2 [existing design defect] an exception escaping `run()` after S1.2 exits 1 (Python's
  traceback), which bomdd-run R8 and O1 reserve for "not launched", while an open run is left for a human release; V2(g)'s new arm says "returns".
  The reviewer checked every letter of the coverage line against the items.
- **判定: 未収束** (round 軌跡: 4→3→2; material 0→0→0). Limit of 3 rounds reached. **No manufacture and no filing commit** until the user rules.
- **Classes in this loop (user condition):** new defect from the consolidation 4 (L3R1-1, L3R1-2, L3R1-4, L3R2-1); inconsistency from duplicated text 2
  (L3R1-3, L3R2-2 — both in the duplication the register itself still had: S1 vs O1, the coverage line vs the V headings); existing design defect 3
  (L3R2-3, L3R3-1, L3R3-2).
- **DoD:** ✔ D1; ✔ D2; ✔ D3; ✔ D4; ✘ D5 (L3R3-1); ✘ D6 (L3R3-2); ✔ D7; ✔ D8; ✔ D9; ✔ D10.
- **未収束事項:** L3R3-1, L3R3-2 (unrepaired).

### Loop 4 (user ruling "2:A", 2026-10-18: extension; repair the two, no new control mechanism)

- L3R3-1 → V3(e) observes the refusal (exit 1, no quarantine record) while a parsed open run is `CELL_ALIVE`.
- L3R3-2 → new rule O3: an exception escaping `run()` is caught at its outer edge after W3's `finally`; line `UNMEASURABLE <ECO> INTERNAL_ERROR(<class>)`,
  exit 2 (never the refusal's 1); O1 refers to it; V2(g) and the new V4(m) observe it; the coverage line maps O3. No new control mechanism (an exit-code
  mapping only).

- **Round 1, 1 (minor).** L4R1-1 [existing design defect, introduced by the O3 repair] V4(m)'s "during S1.6" expected an open run even where `end` was
  already committed → V4(m) names three injection points and the outcome of each. The reviewer confirmed both loop-3 repairs and O3's catch point.
- **Round 2, 0.** Each of V4(m)'s three outcomes follows from S1.6, W3 and O3; nothing else changed; no inconsistency between the register, the limits, the
  coverage line and the acceptance. (A note for manufacture, not a defect: the third injection must raise something other than `OSError`, which
  `write_ledger` already turns into a ledger-write failure.)
- **Round 3, 1 (minor) — not repaired** (a repair would start a fifth loop). L4R3-1 [existing design defect, present since loop 1] S4's list of refusals
  omits `JOURNAL_CORRUPT` (J2 defines it, O1 maps it, V4(f) observes it, but no rule gives its ledger decision record or its line). Suggested repair (not
  applied): add it to S4 — no `run_id`; the line `UNMEASURABLE <ECO> RUN_IN_FLIGHT(JOURNAL_CORRUPT) → operator`.
  The reviewer re-read the whole order against D1-D10 and the header's conditions and found nothing else.
- **判定: 未収束** (round 軌跡: 1→0→1; material 0→0→0). Limit of 3 rounds reached. **No manufacture and no filing commit** until the user rules.
- **Classes in this loop:** existing design defect 2 (L4R1-1, introduced by the O3 repair; L4R3-1); inconsistency from duplicated text 0; new defect from
  the consolidation 0.
- **DoD:** ✔ D1-D5; ✘ D6 (L4R3-1); ✔ D7-D10.
- **未収束事項:** L4R3-1 (unrepaired).

### Loop 5 (user ruling "2:A", 2026-10-18: extension; enumerate every S4 refusal reason and check record, line and recovery mechanically)

- **L4R3-1 and its class of omission, handled together:** S4 is now the complete table of refusals before `decide()` (seven reasons, each with where it
  arises, the extra record fields, the line and the way out); O1 adds `REPORT_EXISTS`; V4(n) observes every row; the coverage line maps S4 to V4(n).
- **Mechanical check (first version; superseded — see Round 1 below):** the first `refusal_matrix.py` derived the pre-`decide()` refusals from X2, J2
  and one hand-coded S1 mapping, and passed this text with seven reasons and two known-bad copies. Round 1 (L5R1-2) showed that it did not measure
  what it claimed; it was rewritten, and its first version and report are not evidence. **The evidence filed in `bomdd/reports/eco-113-refusal-matrix/`
  is the Round 1 version** (its sha256 values are in the Round 1 record and in the filing record below).
- No new state-management mechanism: the table restates existing rules in one place; `REPORT_EXISTS` is bomdd-run R10's existing `ARG_ERROR`.

- **Round 1, 3 (2 material).** L5R1-1 [existing design defect] S4's claim "a reason not in this table does not exist" was false (an unreadable journal, an
  underivable `<git-common-dir>`, a refusal whose record cannot be written) → A3 gains an error outcome (`JOURNAL_UNREADABLE`, a new row), X1's
  underivable directory is `LOCK_UNAVAILABLE`, S1 moves the existing argument and ledger-path checks before the lock, S4 states what happens when its
  record cannot be written (the ledger failure wins, exit 2), and S4's claim is restated as the order's convention (a reason is defined only by the phrase
  "cause" + the reason, or as a J2 class), not as completeness of the code. L5R1-2 [existing design defect, in the loop-5 instrument] the script did not
  measure what the receipt said (three mutated copies passed; cp932 stdout made the exit code meaningless) → rewritten: C1 derives from every "cause"
  phrase in §1 plus J2's classes (no hand mapping); C4 also refuses a way out through R2 for a class R2 refuses; C5 requires one O1 verdict group per
  reason with STOP→1 / UNMEASURABLE→2; stdout is UTF-8 and the verdict is the report's first line. Its first run on the repaired text **found a real
  gap** (`JOURNAL_UNREADABLE` had no acceptance item) → V4(o) added. Calibration (`calibrate_matrix.py`, sha256 `cc41a24b…`): the original PASS, and
  five known-bad copies FAIL by first line and exit — a missing row, a non-existent citation, O1 names removed, a new reason without a row, a way out
  through a refusing rule. Script sha256 `e3a5e001…`; report `876091c7…` (PASS, 8 reasons). L5R1-3 [existing design defect] at most one open run was
  assumed → J2 classifies every open run and reports the most restrictive (`JOURNAL_CORRUPT` > `CELL_ALIVE` > `UNKNOWN` > `ABNORMAL_END`); the rows
  record `open_runs`; V4(q) added. V4(p) observes S4's ledger failure.
- **Round 2, 0.** The reviewer re-read the order and both scripts and ran them: the original PASS; K1, K2, M1, M3 FAIL; its own M1 and M3 now FAIL; the
  script exits 0 under a cp932 stdout. Its original M2 (a refusal written without the word "cause") still reads PASS — outside the order's convention
  and declared as such in S4, the script's docstring and this receipt, so the measurement matches the claim. All eight rows agree with their rules and O1.
- **Round 3, 1 (minor) — not repaired** (a repair would start a sixth loop). L5R3-1 [inconsistency from duplicated text] the loop-5 opening bullet
  still names the superseded script and report (`315fe26d…`, `8a1eb4a5…`, the hand-mapped derivation, "two known-bad copies") as the evidence to file,
  while the Round 1 record names the current ones (`e3a5e001…`, `cc41a24b…`, `876091c7…`). The design itself drew no finding; the reviewer re-hashed the
  scripts (they match Round 1), re-ran the calibration (original PASS, five known-bad FAIL) and the check (PASS, exit 0 under cp932).
- **判定: 未収束** (round 軌跡: 3→0→1; material 2→0→0). Limit of 3 rounds reached. **No manufacture and no filing commit** until the user rules.
- **Classes in this loop:** existing design defect 3 (L5R1-1, L5R1-2, L5R1-3); inconsistency from duplicated text 1 (L5R3-1, a receipt line);
  new defect from the consolidation 0.
- **未収束事項:** L5R3-1 (unrepaired; a record, not the design).

### Exception ruling and filing (user, 2026-10-18, "2:OTHER")

- **The ruling, in substance:** the sixth loop is not opened. The design drew zero findings in two consecutive rounds (loop 5 rounds 2 and 3); the remaining
  finding is a record inconsistency (stale sha256 in the receipt). Correct it and check mechanically that the recorded sha256 match the actual scripts. Do
  not re-read the convergence rule silently: **if the existing contract does not allow separating the design's verdict from the records' integrity, record
  this as an exception ruling.** If the correction changes neither the design nor the check results, no further full design review is required; after the
  integrity check, proceed to filing.
- **Under the existing contract** (the converge skill: two consecutive rounds with zero new findings of any kind) **the verdict stays 未収束 (3→0→1).**
  The contract has no provision for counting design findings apart from record findings, so **filing here is an exception ruled by the user**, not
  convergence. Manufacture of ECO-113 still waits for the user's instruction.
- **The correction:** the loop-5 opening bullet no longer names the superseded script and report; it points to the Round 1 version (L5R3-1).
- **Mechanical checks** (`record_check.py`, sha256 `ea73be04…`):
  - the design (the order up to this receipt) is byte-identical before and after the correction: sha256 `e60ec3a544066e1c…` both times;
  - the receipt's stated sha256 against the evidence files — **before the correction: FAIL** (`refusal_matrix.py` stated `315fe26d`, actual `e3a5e001`;
    `refusal-matrix.md` stated `8a1eb4a5`, actual `876091c7`), **after: PASS** (every stated value matches; each file is named with its current value);
  - the S4 check re-run on the corrected order writes a report byte-identical to the one recorded (`refusal-matrix.md`), and the calibration still reads
    the original PASS and the five known-bad copies FAIL.
- **Evidence filed** in `bomdd/reports/eco-113-refusal-matrix/`: `refusal_matrix.py` `e3a5e001e97df9db…`, `calibrate_matrix.py` `cc41a24bd0ce492a…`,
  `refusal-matrix.md` `876091c7dc3ea920…`, `record_check.py` `ea73be045afb71d4…`; the OS probes cited in §0 in `bomdd/reports/eco-113-probes/`.

### Amendment loop A (user ruling "1:A", 2026-10-24, after inspection r1: J1, J2's claim sentence, A4, L11, V4(f), V4(q) and their direct references; default rule)

- **判定: 未収束** (round 軌跡: 7→2→1; material 2→1→1). Limit of 3 rounds reached without two consecutive rounds with zero findings. **No repair
  manufacture and no commit of the amended text** until the user rules (extension / adoption / return of the design).
- **起動経路:** the user's ruling (1:A names the default convergence rule); reviewer = a fresh context of the same model that has not seen the earlier
  loops, read-only, resumed each round.
- **DoD (fixed before round 1):** D1 every case of r1's findings and probes is read by a rule; D2 each new invalid-record rule has an acceptance
  observation that goes red for its own reason; D3 no record sequence bomdd-run itself writes is read as `JOURNAL_CORRUPT` or misclassified; D4 one
  canonical place per changed rule, no restatement or contradiction; D5 no new state or mechanism, nothing outside the ruled scope but direct
  references; D6 the ruling paragraph matches the text.
- **Round 1, 7 (2 material).** V4(f) had no observation for three A4 clauses (an offset that is not an integer; `run_id` on `end`/`abort`/`release`;
  the empty `run_id`) [new defect from the amendment, material]; V4(f)'s quarantine observations could not be met as written (`corrupt_offset` is
  owned by an earlier line) [new, material]; A4(iv)'s digest bytes unstated [new, minor]; J2 restated A4 in narrower words [duplicated text, minor];
  "never skipped" claimed more than A4 defines (a missing or near-miss `event`) [new, minor]; R3 and A3 still read as before [duplicated text, minor];
  A4's reason did not support its claim [existing design defect — the reason was carried over unchanged from before the amendment, minor]. All repaired.
- **Round 2, 2 (1 material).** V4(f)'s offset arms were not isolated: the r1 probe's quarantine carries a wrong digest, so a reader without the position
  check still flags it [new, material]; the missing/near-miss `event` rule sat in L11, not A4 [duplicated text, minor]. Both repaired.
- **Round 3, 1 (material).** The repaired position arm is still not isolated: offset 999999 is also past the end and so not at a line boundary, and
  "the digest of the corrupt line that follows it" matches only a whole-file reader, not the in-order reader the amendment requires [new defect from
  the round-2 repair]. The reviewer gave a construction that isolates it (an unparsable line before the quarantine; `offset` at a real line boundary
  after the quarantine's own position with no corrupt line between; the earlier line's digest): correct reader → the line still corrupt; position check
  removed → the line excluded. **Not repaired** (a repair would start a fourth round).
- **The rules drew no finding in rounds 2 and 3.** D1, D3, D4, D5 and D6 held in round 3; every finding of rounds 2 and 3 is in V4(f)'s prose recipes for
  building the quarantine arms (D2). **Common cause:** the acceptance text specifies how to build mutation-resistant arms, a job T1 and the
  manufacture's rule mutations already do (each rule broken in a copy; the selftest must go red on that rule's own arm).
- **Classes in this loop:** new defect from the amendment 6 (round 1: 4, round 2: 1, round 3: 1); inconsistency from duplicated text 3; existing design
  defect 1 (round 1); 10 in all.
- **Verified claims (selection):** r1's probes reproduced on `2752d18` (§5); the reviewer's reference readers (in-order, each A4 check switchable) in
  its own scratch directory; D3's sequences (repeated `end`, `abort`, `interrupted` then release, reuse after close, torn tail, `repair`, `note`, R3's
  successive quarantines, a hand-made invalid quarantine followed by R3) read clean under the amended rules.
- **未収束事項:** round 3's finding (the position arm's construction), unrepaired.

### Amendment loop A2 (user ruling "A", 2026-10-24: extension after removing the common cause — V4(f) observations only, each A4 check shown needed by rule mutations)

- **判定: 収束** (round 軌跡: 1→0→0; material 0→0→0). Two consecutive rounds with zero new findings.
- **起動経路:** the user's extension ruling; the same reviewer as loop A (fresh context that has not seen the earlier loops, read-only, resumed).
- **DoD:** loop A's D1-D6, unchanged; D2 read with V4(f)'s mutation requirement as the measured form of "red for its own reason".
- **The common cause removed before round 1:** V4(f) no longer prescribes how an arm is built; it lists the observations (each A4 kind → `JOURNAL_CORRUPT`,
  an invalid quarantine excludes nothing, a repeated `end` is not corrupt) and requires one rule mutation per A4 clause — (i), (ii), (iii), and (iv)'s
  integer, position, boundary and digest checks — each caught on its own arm. Loop A's round-3 finding (the position arm) is thereby a manufacture duty:
  the mutation that removes the position check must be caught, however the arm is built.
- **Round 1, 1 (minor, a record).** Loop A's receipt counted 9 classes for 10 findings (round 1's seventh tagged "wording") [new defect, a record] →
  classed as an existing design defect (A4's reason was carried over unchanged), the class line now 6 + 3 + 1 = 10. The rules and V4(f) drew none.
- **Round 2, 0.** D1-D6 re-checked on the whole amendment; the receipt adds up.
- **Round 3, 0.** Thirteen journal sequences not tried before, through the reviewer's in-order reference reader (each A4 check switchable): an invalid
  record followed by one that could look out of order because of it (`start("")` then `end("")` — both corrupt, nothing open after R3); a closing record
  whose id matches an invalid `start` (it closes the first, valid `start`); interleaved runs with two ids; closing a closed run (`abort` after `end`);
  a partial quarantine; a second quarantine at the same offset (an already-excluded line's digest → invalid; the empty digest → a valid no-op); a no-op
  quarantine at offset 0. Every result follows J1 and A4.
- **Verified claims (selection):** D3's sequences read clean (repeated `end`, `abort`, `interrupted` then release, reuse after close, interleaved ids,
  torn tail, `repair`, `note`, successive R3 quarantines, a retried release or quarantine after a failed fsync); the mutation requirement can be met for
  every listed check (the reviewer's position arm: corrupt lines [34, 39] with the check, [] without).
- **未収束事項:** なし.
