# Independent inspection brief r2 — BomDD ECO-112 (repair of IA-01, IA-02; regression) — inspector EQ-002

- **Role: inspector.** EQ-002 (Codex CLI). Responsibility: judge whether the repair manufacture fixes the two findings of r1 and whether anything that
  passed in r1 now fails. Range of this round: **是正確認+回帰** (repair confirmation and regression).
- **Target:** BomDD commit `4d2c05fe3ce1294f59b3f979aa53010cd9178f86` (the repair commit). Report `git rev-parse HEAD` at start and at end (they must be equal; otherwise UNMEASURABLE).
- **Observable prohibitions:** no file in the repository created, changed or deleted (`git status --short` empty at the end), no commit, no network.
  You MAY run, with `python -B`: `method/tools/bomdd-run.py --selftest`, `method/tools/bomdd-job.py --selftest`, `method/tools/bomdd-witness.py --selftest`
  (they use their own temp directories), `bomdd/reports/eco-112-arm-inventory/manufacture/repair/rule_mutations.py <repo>/method/tools <temp dir>`, and
  small throwaway probes of your own in a temp directory outside the repository.
  The V3 instrument (`bomdd/reports/eco-112-arm-inventory/arm_inventory_v2.py`) is being re-run on this commit by the operator (about 2-3 hours); do not
  re-run it. Its result is not part of this round (say so in "Not checked"); the acceptance waits for it.
- **What was rejected in r1** (`bomdd/reports/eco-112-briefs/inspection-r1.md`):
  - IA-01 — the brief was stored before the decision record; a failed ledger write left a stored brief for a launch that never happened.
  - IA-02 — the cell was handed the stored (archival) file as `BOMDD_BRIEF`; a cell that deleted it made B4 see an empty store and pass.
- **Read:** the order `bomdd/60-change-order-eco-112.md` — the amended rules B2, B3, B4's closure sentence, L4, L5, L10 (§1), the acceptance V2(g)-(j)
  (§3), the repair record §6, and the receipt "Amendment loop A2"; the diff `git diff f2d91d4e4eb523ef9970d71e38f2e8a651408770..4d2c05fe3ce1294f59b3f979aa53010cd9178f86` (`f2d91d4e4eb523ef9970d71e38f2e8a651408770` = the r1 target, the first
  manufacture); `method/tools/bomdd-run.py` (header R13, `store_brief`, `exec_copy`, `remove_exec_copy`, `rollback_brief`, `launch`, `run`, the selftest's
  `b-*` arms); `bomdd/reports/eco-112-arm-inventory/manufacture/` (`v3-run1-*` and `repair/`).
- **Report path:** do not write the report yourself; your final message is saved by the harness. Its first non-empty line (after an optional
  `[INFORM / COMPLETE]`) starts with `ACCEPT`, `REJECT` (followed by the finding IDs) or `UNMEASURABLE <reason>`.

## What to check (each item: PASS / FAIL with evidence; a FAIL is blocking or non-blocking)

1. **Scope.** `git diff --stat f2d91d4e4eb523ef9970d71e38f2e8a651408770..4d2c05fe3ce1294f59b3f979aa53010cd9178f86` stays inside the order §2's paths; `git diff f2d91d4e4eb523ef9970d71e38f2e8a651408770..4d2c05fe3ce1294f59b3f979aa53010cd9178f86 -- method/tools/bomdd-witness.py` is
   empty; no ECO-113 rule (lock, journal, Job Object, `RUN_IN_FLIGHT`) is in the diff.
2. **IA-01 repaired (B2).** After storing, a failure of the execution copy or of the decision record launches nothing and removes the stored file only
   if this invocation created it; an already stored brief is left with its bytes; a removal failure prints `brief left in store: <12 hex> (<error>)`
   after the first line and exits 2; a spawn failure is not rolled back. Probe it yourself (e.g. an unwritable `--ledger`, a brief already stored).
3. **IA-02 repaired (B3).** The cell's `BOMDD_BRIEF` is never `store_ref`: it is a new file with the same bytes in a fresh temporary directory outside
   the worktree and the store, re-hashed; it and its directory are removed after the cell and on every path that does not launch; a cell that deletes
   or changes it leaves the archival copy intact, and B4 still demands its committed copy. Probe it with a cell of your own (`--cell` launching a small
   `python -c` that deletes `%BOMDD_BRIEF%`, against a throwaway git repository, not this one).
4. **Stored, not launched (B3, B4).** The code and comments no longer equate a stored brief with a launch; B4's closure duty and L4/L5/L10 agree with
   the code.
5. **The selftest.** The new arms V2(g)-(j) go red for their own reasons (the rule mutations record it; you may re-run them); `b-store`,
   `b-refused-stores-nothing` and `b-other-ledger-same-store` read only their own call's record and check each call right after it (T2); the shape T5
   requires is kept.
6. **Regression.** Everything r1 found PASS still holds: G1-G5, B1, B4, B5, O1 (first lines within 80 columns), T1-T6; the three selftests exit 0.
7. **Records.** §6 and the receipt claim nothing that the code or the evidence does not show.

## Report format (your final message, in full)

```
[INFORM / COMPLETE]

ACCEPT            ← or REJECT IA-03, IA-04, … / UNMEASURABLE <reason>

- inspector: EQ-002 / Codex CLI / <model>
- HEAD at start / at end: <sha> / <sha>
- commits: 0 / files changed: 0
- selftests run: bomdd-run <first line>, bomdd-job <first line>, bomdd-witness <first line>
- IA-01: repaired | not repaired (why) / IA-02: repaired | not repaired (why)

## Items
| # | item | verdict | evidence (file:line, command and the key output) |

## Findings (IA-03, IA-04, …)
- each: blocking / non-blocking, where, what is wrong, a suggested repair

## Not checked (limits)
```
