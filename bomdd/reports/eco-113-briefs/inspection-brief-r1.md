# Independent inspection brief r1 — BomDD ECO-113 (in-flight runs: an OS file lock, a kill-on-close Job Object, the run journal) — inspector EQ-002

- **Role: inspector.** EQ-002 (Codex CLI). Responsibility: judge whether the manufactured tools and documents implement the order's rules, and whether the
  acceptance evidence shows what the order claims. Range of this round: **境界探索** (boundary exploration — where the rules can be read wrongly, fail open,
  or be stronger in the record than in the code). **The replacement of the earlier hand-made exclusion by an OS file lock, and the ownership of the cell by
  an OS Job Object, are themselves objects of this inspection** (the user's condition in the order's ruling block).
- **Target:** BomDD commit `2752d18a8b738ab1dd4d3a327a599a2e935c9d0c` (the manufacture commit). Report `git rev-parse HEAD` at start and at end (they must be equal; otherwise UNMEASURABLE).
- **You are running inside the entry you inspect:** this cell was launched by the manufactured `bomdd-run.py`, so on Windows your process tree is in a
  kill-on-close Job Object named `Local\BomDD-run-ECO-113-<run_id>`, and the entry holds the lock `<git-common-dir>/bomdd-run/ECO-113.lock` until you end.
  Do not try to stop or release that run, and do not run `bomdd-run.py ECO-113 …` against the real repository (it would read `ENTRY_ALIVE`, by design).
- **Observable prohibitions:** no file in the repository created, changed or deleted (`git status --short` empty at the end), no commit, no network, nothing
  written under the repository's `.git/bomdd-run/` or `.git/bomdd-witness/`. You MAY run, with `python -B`: `method/tools/bomdd-run.py --selftest` (about
  70 seconds; it builds its own temporary git repository, starts child entries and kills some of them on purpose), `method/tools/bomdd-job.py --selftest`,
  `method/tools/bomdd-witness.py --selftest`, the rule-mutation script `bomdd/reports/eco-113-manufacture/rule_mutations.py <repo>/method/tools <a temp
  dir> [case …]` (it copies the tools per case; each case is one selftest run), and small throwaway probes of your own in a temp directory outside the
  repository. Run the selftests one at a time (two at once can turn ECO-112's V2(g) arms red without cause — OBS-20261018-03).
- **Read:** the order `bomdd/60-change-order-eco-113.md` (the rule register §1 X/W/J/R/A/S/O/T and the declared limits, the acceptance §3, the manufacture
  record §4 with its preflight receipt); the register entry ECO-113 in `bomdd/60-change-register.yaml`; the diff `git diff 22711020d37d0cb812df81c6e3716bcd7f00d15e..2752d18a8b738ab1dd4d3a327a599a2e935c9d0c`;
  `method/tools/bomdd-run.py` (header R15; the ECO-113 block from `RUN_IN_FLIGHT` to `in_flight_rec`; `cell_env`, `_ledger_lock`, `write_ledger`, `run`,
  `_teardown`, `_refuse`, `_run`, `_recover`; the selftest block headed `ECO-113(R15)`); `method/tools/bomdd-job.py` (`STOP_VOCABULARY`);
  `method/templates/product-profile/operator-layer.md` §2, §7 and adapter A1; `bomdd/reports/eco-113-manufacture/` (the evidence);
  `bomdd/reports/eco-113-probes/` (the OS probes the design cites).
- **Report path:** do not write the report yourself; your final message is saved by the harness. Its first non-empty line (after an optional
  `[INFORM / COMPLETE]`) starts with `ACCEPT`, `REJECT` (followed by the finding IDs) or `UNMEASURABLE <reason>`.

## What to check (each item: PASS / FAIL with evidence; a FAIL is blocking or non-blocking)

1. **Scope.** `git diff --stat 22711020d37d0cb812df81c6e3716bcd7f00d15e..2752d18a8b738ab1dd4d3a327a599a2e935c9d0c` stays inside the order §2's paths; `git diff 22711020d37d0cb812df81c6e3716bcd7f00d15e..2752d18a8b738ab1dd4d3a327a599a2e935c9d0c -- method/tools/bomdd-witness.py` is empty.
   `22711020d37d0cb812df81c6e3716bcd7f00d15e` is ECO-112's verified head plus the record commits after it (no tool change between `5ddd428` and `22711020d37d0cb812df81c6e3716bcd7f00d15e`: check with
   `git diff 5ddd428..22711020d37d0cb812df81c6e3716bcd7f00d15e -- method/`, which shows only `method/improvements.md`).
2. **X (exclusion) against the code.** One lock file per ECO and clone, never deleted; `os.open` flags; the non-blocking lock at offset 0; only the locking
   call's conflict is `ENTRY_ALIVE`, every other error `LOCK_UNAVAILABLE`; who holds it and for how long (a launching run until it returns, recovery for its
   whole run, a dry run only for its classification).
3. **W (ownership) against the code.** The job is created and configured with kill-on-close only; the cell is started suspended and assigned through the
   `Popen` handle with nothing in between; the entry is not in the job; the resume; the job handle closed on every exit from `run()` (exceptions included);
   W4's failures; the namespace key in the `start` record; nothing on POSIX. **No pid is used for judgement or for stopping.**
4. **J (judgement) against the code.** The journal is the only source (the ledger is not read); every open run classified; the classes and their order;
   `JOURNAL_CORRUPT`; a start without an end never read as an abnormal end by itself.
5. **R (recovery) against the code.** The two commands, the options they refuse, `--by` (human, active), release and quarantine (records, refusals,
   nothing moved or deleted, nothing stopped).
6. **A (records) against the code.** One line per record, one `os.write`, binary, `fsync`, under the lock; a short write is a failure; the torn tail
   truncated by the next writer with a `repair` record; the read splits on `\n` only; quarantine exclusion; the ledger lock (10 s).
7. **S and O.** The launch order S1 (argument checks and the ledger path before the lock; classify; the `--report` re-check under the lock; `decide()`;
   the job, `start`, the ledger decision record, the first line, the resume, the wait, `end` retried, the ledger cell record, the handle closed); S2; S3;
   S4's table row by row (reason, record fields, line, way out); O1's verdicts and exits; O3; O2's vocabulary in both places and in operator-layer.md.
8. **T and the acceptance evidence.** V1-V5 as recorded in §4 and `bomdd/reports/eco-113-manufacture/`: do the recorded runs show what V1-V5 require?
   Does each refusal arm check a reason unique to itself? Does each rule's arm go red for its own reason (the rule mutations)? The manufacture choices
   §4 lists as derived (not in the rule text): are they consistent with the rules, or do any of them change a rule?
9. **Boundary exploration (the main work of this round).** Look for inputs and timings where the new rules read wrongly or fail open, for example: the lock
   file replaced by a directory or a symlink; a lock taken by another kind of Python on the same clone (L8); a journal line that is valid JSON but not an
   object, or an object with a non-string `run_id`; two `start` records with the same `run_id`; a `release` for a run that never started; a quarantine
   `offset` that is not an integer or points past the file; a journal larger than memory would like; a cell that itself starts `bomdd-run.py` for the same
   ECO; a cell that exits before the entry resumes it; the entry interrupted between `start` and the ledger record; a `--report` path that becomes a
   directory under the lock; `CELL_ALIVE` that never clears (L3); the job name reused across clones; Ctrl+C reaching both the entry and the cell.
10. **Records.** The order's §4 and the register entry claim nothing that the code or the evidence does not show; the declared limits (L1-L12) are honest.

## Report format (your final message, in full)

```
[INFORM / COMPLETE]

ACCEPT            ← or REJECT IA-01, IA-02, … / UNMEASURABLE <reason>

- inspector: EQ-002 / Codex CLI / <model>
- HEAD at start / at end: <sha> / <sha>
- commits: 0 / files changed: 0
- selftests run: bomdd-run <first line>, bomdd-job <first line>, bomdd-witness <first line>

## Items
| # | item | verdict | evidence (file:line, command and the key output) |

## Findings (IA-01, IA-02, …)
- each: blocking / non-blocking, where, what is wrong, a suggested repair

## Not checked (limits)
```
