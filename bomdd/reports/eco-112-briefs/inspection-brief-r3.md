# Independent inspection brief r3 — BomDD ECO-112 (IA-03 under the user's exception ruling; regression) — inspector EQ-002

- **Role: inspector.** EQ-002 (Codex CLI). Responsibility: judge whether r2's one blocking finding, IA-03, is resolved under the user's ruling, and
  whether anything that passed in r2 now fails. Range of this round: **是正確認+回帰** (repair confirmation and regression).
- **Target:** BomDD commit `0b6a784ea8e54b7822e7e4f2e09465a702e96a59`. Report `git rev-parse HEAD` at start and at end (they must be equal; otherwise UNMEASURABLE).
- **Observable prohibitions:** no file in the repository created, changed or deleted (`git status --short` empty at the end), no commit, no network.
  You MAY run, with `python -B`: the three selftests (`method/tools/bomdd-run.py --selftest`, `bomdd-job.py --selftest`, `bomdd-witness.py --selftest`),
  `bomdd/reports/eco-112-briefs/diff-window/diff_window.py`, `bomdd/reports/eco-112-arm-inventory/manufacture/repair/rule_mutations.py <repo>/method/tools
  <temp dir>`, and small probes of your own in a temp directory outside the repository. Do not run the selftests concurrently with each other.
  V3's re-run on `4d2c05f`'s tool is recorded in §6 (PASS; `bomdd/reports/eco-112-arm-inventory/manufacture/repair/v3-run2-*`). Check the record
  against those files and that the tool is unchanged since `4d2c05f`; do not re-run the instrument (about 1.5 hours).
- **What r2 rejected** (`bomdd/reports/eco-112-briefs/inspection-r2.md`): IA-03 — the range r2's brief named, `f2d91d4..4d2c05f`, contained ECO-113's
  filing commit `3c7781c`, outside the order §2's paths.
- **The user's ruling** (the order §8, verbatim conditions there): for ECO-112's V6 and its inspections, the change set is the commits attributed to
  ECO-112; `3c7781c` is not part of ECO-112's manufacture; conditions (1)-(5): the exclusion and its reason recorded; a diff showing that ECO-113's commit
  does not affect ECO-112's products or acceptance evidence; ECO-112's changes enumerated in full and that set inspected (this round); V6 applying the
  ruling with the included and excluded ranges kept as evidence; the CI and acceptance checks on the actual final tree not skipped. Not a general rule
  (OBS-20261018-02).
- **Your target set (condition 3):** the commits attributed to ECO-112 in `3a9de06..0b6a784ea8e54b7822e7e4f2e09465a702e96a59`, as listed by
  `python -B bomdd/reports/eco-112-briefs/diff-window/diff_window.py . 3a9de06 0b6a784ea8e54b7822e7e4f2e09465a702e96a59` (C4 lists every path with its commits). Inspect that set,
  not the literal range.
- **Read:** the order `bomdd/60-change-order-eco-112.md` §7 and §8 (and §1-§6 as needed); `bomdd/reports/eco-112-briefs/diff-window/`;
  `method/improvements.md` OBS-20261018-02; `git show 3c7781c --stat` and `git show 3c7781c -- bomdd/60-change-register.yaml`.
- **Report path:** do not write the report yourself; your final message is saved by the harness. Its first non-empty line (after an optional
  `[INFORM / COMPLETE]`) starts with `ACCEPT`, `REJECT` (followed by the finding IDs) or `UNMEASURABLE <reason>`.

## What to check (each item: PASS / FAIL with evidence; a FAIL is blocking or non-blocking)

1. **The ruling's record (condition 1).** §8 names the excluded commit and its reason; nothing else is excluded.
2. **Non-interference (condition 2).** Independently of the script: ECO-113's commit changes no ECO-112 path except the shared register; in the register
   it only adds lines inside ECO-113's own entry and leaves ECO-112's entry unchanged; none of its other paths is changed afterwards by an ECO-112
   commit; ECO-112's tools and evidence do not read or depend on any ECO-113 path.
3. **The check itself.** `diff_window.py` does what its header says (C1-C5); its run on `3a9de06..0b6a784ea8e54b7822e7e4f2e09465a702e96a59` passes; its positive control
   (`--control-include 3c7781c`) fails. Look for a way it could pass wrongly (attribution by subject tag, entry boundaries, path prefixes).
4. **The ECO-112 change set (conditions 3, 4).** Every path the ECO-112 commits change lies inside the register's ECO-112 `allowed_paths` (V6 as ruled);
   `git diff 3a9de06..0b6a784ea8e54b7822e7e4f2e09465a702e96a59 -- method/tools/bomdd-witness.py` is empty; no ECO-113 rule (lock, journal, Job Object, `RUN_IN_FLIGHT`) is in an
   ECO-112 commit.
5. **Regression.** `git diff 4d2c05f..0b6a784ea8e54b7822e7e4f2e09465a702e96a59 -- method/` changes only `method/improvements.md` (the OBS); r2's PASS items still hold: IA-01 and
   IA-02 repaired, G1-G5, B1-B5, O1, T1-T6; the three selftests exit 0.
6. **Records.** §6's V3 run-2 lines, §7, §8, the READMEs and OBS-20261018-02 claim nothing the code or the evidence does not show (verdict, counts,
   sha256 of the tool measured and of the evidence files).

## Report format (your final message, in full)

```
[INFORM / COMPLETE]

ACCEPT            ← or REJECT IA-04, IA-05, … / UNMEASURABLE <reason>

- inspector: EQ-002 / Codex CLI / <model>
- HEAD at start / at end: <sha> / <sha>
- commits: 0 / files changed: 0
- selftests run: bomdd-run <first line>, bomdd-job <first line>, bomdd-witness <first line>
- IA-03: resolved under the ruling | not resolved (why)

## Items
| # | item | verdict | evidence (file:line, command and the key output) |

## Findings (IA-04, IA-05, …)
- each: blocking / non-blocking, where, what is wrong, a suggested repair

## Not checked (limits)
```
