# ECO-126 — the one confirmation after the scoped repair (2026-11-17): the reviewer's report, and what was done with it

> **Later record (2026-11-17, after this file was written):** the dispositions below are as of `5655ef2`. On the user's
> second instruction R3-01 and R3-02 were repaired and R3-03, R3-06 and R3-08 were corrected in the text (`7f5a4dc`; the
> order's section 7). The table is left as it was written.

A fresh context of the producer's equipment (EQ-006; not another lineage), read-only, on commit `12cc2be` against `acc7c05`.
Range: the repaired places and the regressions those repairs could cause. The brief is `review-r3-brief.md` beside this file.
**Nothing was repaired after this report** (the user's instruction for this return: one confirmation; on a new serious
finding, do not go on repairing — report the remaining risk and the scope that can be used). The reviewer's text below is
shortened only where it lists what it ran; the findings are as written. The producer reproduced R3-01, R3-02 and R3-03
(`repro` lines at the end).

## The reviewer's verdict

**SERIOUS FINDING** — one finding, R3-01, "and only by the letter of the first clause, 'a wrong exit code of a tool'":
`loop-count.py --check` exits 0 for an item whose `round` is `true` / `yes` / `1.0`. "Its practical weight is low. If that
clause is read as 'on input a session would realistically write', the verdict is NO NEW SERIOUS FINDING. No traceback on any
input I tried, no regression in either tool, and no text I would expect to make a session do the wrong thing."

## Items

| Item | Reviewer | What the reviewer ran or read |
|---|---|---|
| KD-02 | closed | 59 inputs through `handover-stamp.py`, 0 tracebacks, exit codes as the header states; on a copy of the `acc7c05` tool the same inputs gave traceback + exit 1 for `main` list / mapping, `program` list and log-is-directory |
| KD-03 | **partly** | five of the six rules held on 72 hand-made records and 2106 structural mutations; the sixth, an item's `round`, accepts `true` / `yes` / `1.0` when round 1 exists (R3-01) |
| KD-05 | closed | exit 0 / 1 / 3 always print a record line, exit 2 never does; `{count: 0, matching: 0}` with a reply passes `--check`; one inaccurate parenthesis in the exit-2 bullet (R3-03) |
| KD-06 | **partly** | all 6 kinds, 9 dispositions and 7 outcomes are explained and mapped; two gaps (R3-05, R3-02) |
| KD-07 | closed | the note is set where the confirmation items are handed over; consistent with `eco-accept.md:13`, `eco-fix.md:53/58` and R4 |
| KD-08 | closed | `CLAUDE.product.md` names both stops; `eco-file.md:41` lists the same five things as §3.5's step 1 |
| KD-09 | closed | by reading the committed `v4-output.txt` (`C.back` PASS, `D.back.ctl` refused by E01); the kit hashes in that output equal the files at `12cc2be`; one line measures less than its text (R3-06) |
| KD-10 | **partly** | both self-tests pass (54 and 26 arms); 6 entries of `mutants-tools-output.txt` reproduced identically; of the reviewer's own 35 mutants outside the lists, 22 survive, four of them on checks this repair added (R3-07) |
| V2 | closed | run with no arguments from a `git archive` export of 6 files at `12cc2be`: exit 0, stdout and regenerated files identical to the committed ones; five altered tables each exit 1 with "nothing else was run" |
| V4 | closed | by reading every `check(` call: each line that reports a tool's verdict uses its return code; `C.back`, `C.back.rec` and `D.*` measure what they say, `C.back.status` does not (R3-06); `v4_sabotage.py` matches its output by reading, not re-run |

## Findings in range (the reviewer's), with the producer's disposition

| # | Rated | Finding | Disposition |
|---|---|---|---|
| R3-01 | serious (by the letter) | tool — the new item-round check accepts a YAML bool or float as a round number, because it compares with Python equality (`True == 1`); `loop-count.py:232`, same root at `:269`. `round: true`, `yes` or `1.0` with round 1 present → exit 0, `gaps: 0`; `"1"`, `0`, `null`, `3`, `no` → exit 1. Not a regression: `acc7c05` did not check the field at all | **not repaired; reproduced.** A known false pass of `--check` |
| R3-02 | minor | text — the repair added the rule "to_user_report … reports にも 1 行", which `--check` does not check and "見ないもの" does not declare, although §3.5 says the unchecked rules are listed in the header. A record with a `to_user_report` item and no `reports` row → exit 0 | **not repaired; reproduced.** An unchecked rule that is not declared |
| R3-03 | minor | text — the exit-2 bullet of `eco-turn.md` says exit 2 covers a broken trace ("跡が壊れている"), but the tool exits 1 for malformed trace lines and uses those words in its exit-1 message. A session keyed on the exit code still acts conservatively | **not repaired; reproduced.** One inaccurate phrase in the kit |
| R3-04 | minor | text — the exit-1 bullet says not to treat the reply as a reaction to the handed build, but not whether to write `reply.words` and a reaction row; the new rule then fails a record with the reply and no row. It fails closed | not repaired |
| R3-05 | minor | text — no disposition word for a reader's finding repaired in the product after manufacture, which P3 names ("直したか"); the self-test's own good record gives a maker's `notice` ("直さなかったこと") the disposition `fixed`, against both meanings. The V2 table has no such row | not repaired |
| R3-06 | minor | evidence — `C.back.status` cannot fail once `C.impl` has passed (the return commit stages only `src/app.txt`), so the "status stays implemented" half of "両方を…実測" is what the script did, not something observed of the validator. The measured facts are `C.back` and `C.e`. The skill's new step "status 注記を「周 N 候補・利用待ち」に戻し" is a register edit under `implemented`, which no V4 commit drives | not repaired. The order's section 6.4 is worded to what was measured; the kit's sentence says more than that |
| R3-07 | minor | evidence — the self-tests do not hold four parts of the checks this repair added: `limits.rounds < 1` allowed, negative `launches` allowed, "reply with no reaction row" satisfied by a reaction of any round, the `program`-is-a-string half removed. The arm `program: 7` already exited 2 at `acc7c05`, so it does not exercise the repair. By reading, V2's known-bad on the two-round record would catch the third | not repaired. The headers claim nothing for a check in no list; the numbers in section 6.2 are of the lists only |
| R3-08 | minor | evidence — `mutants_tools.py`'s docstring says "47 and 25 entries, one of them a skip"; `HS_REVIEW` has 26 entries (25 mutants + 1 skip) | not repaired (a docstring of an evidence script) |

## Out of range (the reviewer's; not counted, not repaired)

- `loop-count --check`: a record with no `eco` line, or with `items:` empty, exits 0; neither is in "見ないもの". A
  reaction's `round: true` has the same leniency as R3-01. All predate `acc7c05`.
- `v4_route.py`: the label "eco-turn R3 / R4" is still on `*.e.gate` (KD-11). The `passed_commit` lines print "status in
  HEAD = … (unchanged)" without that status entering PASS.
- `v2_count.py` with the table file missing ends in a traceback (exit 1).
- `handover-stamp stamp` that fails midway (`launch.cmd` unwritable) now prints `[internal] 測れない` with exit 2 (before:
  traceback, exit 1) and still leaves `handover.json` written; a later `check` exits 3.
- A stamped file locked by another process during `check`: `acc7c05` traceback exit 1, now exit 2 `[internal]`. Nothing was
  found that the catch-all hides and that should be exit 1.
- `eco-turn.md` section 4 on a second pass after a return in a three-state product still says to place the `implemented`
  transition commit, though the status is already `implemented`. The exit-1 bullet does not mention malformed trace lines.
- In the diff but not on the item list, not reviewed: `v5-output.txt`, the brief and the report of the GU7 inspection.

## What the reviewer ran (condensed) and did not check

- Both self-tests (exit 0; 54 and 26 arms). 72 records through `--check`; 2106 structural mutations of a format-following
  record, `12cc2be` against a copy of `acc7c05`: 0 tracebacks in either, 0 loosened, 177 tightened, all in the six rule areas.
  59 cases through `handover-stamp` (stamp and check), 0 tracebacks. 35 mutants of its own (18 + 17): 13 killed, 22
  survived (three of the survivors likely equivalent, by its reading). V2 from a `git archive` export, and 5 altered tables in
  both call forms. Its temp folder: `C:\Users\akira\AppData\Local\Temp\eco126-r3-review-92gbwavx`. `git status --short` at
  the start and at the end showed only the two unrelated paths; HEAD `12cc2be` at both points.
- **Not checked**: `v4_route.py`, `v4_sabotage.py`, `mutants_tools.py` and `self-conformance.py` were read, not run
  (`v4-sabotage-output.txt` carries no hash that ties it to the committed script); whether the embedded lists equal the
  round-2 reviewer's originals; a register note edit under `implemented`; the POSIX launcher; a record that is not UTF-8
  (KD-01); the installed `SKILL.md` after `bomdd-init` substitutes `{{METHOD}}`.

## The producer's reproduction (on the committed tools, files under a temp folder only)

```
good record: exit 0, no gap
R3-01 item round: true  -> exit 0, no gap
R3-01 item round: yes   -> exit 0, no gap
R3-01 item round: 1.0   -> exit 0, no gap
R3-01 item round: "1"   -> exit 1, [gap] items F-1: round が rounds に無い('1')
R3-01 item round: 0     -> exit 1, [gap] items F-1: round が rounds に無い(0)
R3-01 item round: no    -> exit 1, [gap] items F-1: round が rounds に無い(False)
R3-02 a to_user_report item and no reports row -> exit 0, no gap
R3-03 a log with one malformed line -> exit 1, [malformed] 読めない行が 1 行ある(跡が壊れている — 数に入れていない)
```

Cost of this confirmation: 303,050 tokens (one subagent, 48 tool uses).
