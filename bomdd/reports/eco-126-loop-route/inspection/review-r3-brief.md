# Review brief — ECO-126, one scoped round: correction confirmation and regression of the repairs in commit 12cc2be

You are a reviewer in a fresh context. You have not seen how these changes were made. Your job is to find what is wrong
with them. **Read-only: change nothing in the repository, repair nothing, commit nothing.** Write temporary files only
under a new folder you create with `tempfile.mkdtemp` (outside the repository) and say where it is.

Repository: `C:\Users\akira\source\repos\BomDD` (branch `main`). The change under review is exactly
`git diff acc7c05..12cc2be` (one commit). Two paths in the working tree are unrelated and must be ignored:
`method/improvements.md` (modified) and `bomdd/reports/count-survey-20261110/` (untracked).

## Range (nothing else is in range)

The user limited this round to **the repaired places and the regressions those repairs could cause**. A defect that
existed before `acc7c05` and is not one of the items below goes under OUT OF RANGE and is not counted.

The items that were repaired, as the earlier review named them (`bomdd/reports/eco-126-loop-route/inspection/review-r2-report.md`
has the list; the statements below are the earlier findings, not claims that they are now fixed):

- **KD-02** `method/tools/handover-stamp.py check`: a malformed manifest (`main` / `program` not a string) or a log that is
  a directory ended in a traceback with exit 1, the code the skill reads as "another build ran".
- **KD-03** `method/tools/loop-count.py --check` did not check six rules its format names: a reply with no reaction row;
  duplicate report ids; `jig`; missing or non-numeric `limits` / `budget`; the contents of `launches`; an item's `round`.
- **KD-05** `method/templates/product-profile/skills/eco-turn.md`: the instruction for the launcher check's exit 3 did not
  fit the record's fields; exit 2 was not mentioned.
- **KD-06** the words for an item's kind, disposition and outcome were explained nowhere in the kit; the skill's two lists
  and the confirmation items were not mapped to them.
- **KD-07** the status note "golden 待ち" was set one step late.
- **KD-08** two entry texts said less than the route (`CLAUDE.product.md`, `skills/eco-file.md`).
- **KD-09** a three-state product's return from the confirmation items to a round was stated from reading, not measured.
- **KD-10** the self-tests of the two tools covered part of their checks (22 of 47 and 13 of 25 of the reviewer's mutants).
- **V2** (`bomdd/reports/eco-126-loop-route/v2_count.py`) needed a table that was not in the repository.
- **V4** (`bomdd/reports/eco-126-loop-route/v4_route.py`) had one PASS line that did not depend on the exit code it printed.

## What to do

1. **Correction confirmation.** For each item above decide `closed`, `not closed` or `partly`, by running the tool or
   reading the text — not by reading the commit message. For the two tools, try inputs of the named class that the
   self-test does not already contain (at least three per tool). For the texts, check each sentence that changed against
   what the tools do (exit codes, field names, the words of the record's format in `loop-count.py`'s header).
2. **Regression.** Look for something that was right at `acc7c05` and is wrong now, in the changed files only:
   - a record that follows the format in `loop-count.py`'s header and now fails `--check`, or a record with a gap that
     now passes; a traceback; a wrong exit code;
   - `handover-stamp.py`: a wrong exit code for stamp or check on any input; anything the new catch-all hides that should
     be exit 1;
   - a sentence in the changed texts that now contradicts another sentence of the kit
     (`method/templates/product-profile/change-management.md` section 3.5 and R3/R4/R6, `skills/eco-turn.md`,
     `skills/eco-accept.md`, `skills/eco-fix.md`, the two tools' headers);
   - `v4_route.py`: any line whose PASS does not depend on the exit code of the tool it reports; whether the new
     three-state lines (`C.back`, `C.back.status`, `C.back.rec`, `D.*`) measure what their text says; whether
     `v4_sabotage.py` shows what it says.
   - `v2_count.py`: does it run from the repository alone, and does it refuse a table with other bytes?
3. **The self-tests as evidence.** `bomdd/reports/eco-126-loop-route/mutants_tools.py` and its output claim which removed
   checks the self-tests notice. Spot-check it: pick at least five checks yourself (not from its lists), remove each in a
   copy of the tool under your temp folder, and see whether `--selftest` goes red.

You may run: `python method/tools/loop-count.py …`, `python method/tools/handover-stamp.py …`, both `--selftest`,
`python bomdd/reports/eco-126-loop-route/v2_count.py`, and copies of the tools under your temp folder. Set
`PYTHONIOENCODING=utf-8`. **Do not run** `v4_route.py`, `v4_sabotage.py`, `mutants_tools.py` or
`method/tools/self-conformance.py` (each takes many minutes and writes into the repository); read them and their
outputs instead. Do not touch `.git`.

## Your report (your final message; nothing else is read)

```
VERDICT: <NO NEW SERIOUS FINDING | SERIOUS FINDING>   (serious = a wrong verdict or exit code of a tool, a traceback on
          input of a class the repair names, or a text that would make a session do the wrong thing)

ITEMS
- KD-02 closed | not closed | partly — <one line: what you ran or read>
- … (KD-03, KD-05, KD-06, KD-07, KD-08, KD-09, KD-10, V2, V4)

FINDINGS IN RANGE
- R3-01 [serious | minor] [tool | text | evidence] <one sentence>
  where: <file:line>
  input / observed / expected: <…>
(Write "none" if there are none.)

OUT OF RANGE
- <observations that are not about the repaired places; "none" if none>

WHAT I RAN
- <commands and counts; your mutants and what each self-test did; your temp folder>

NOT CHECKED
- <…>

git status --short at the start and at the end (both must show only the two unrelated paths)
```
