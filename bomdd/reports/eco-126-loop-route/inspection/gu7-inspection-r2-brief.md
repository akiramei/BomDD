# Independent inspection brief, round 2 (the last round) — the repair of GU7 in `ui-cad-gate.py`

You are an independent inspector of a different lineage from the producer. Round 1 of this inspection ended in REJECT with eight
findings (IA-01 to IA-08); the report is `r1-report.md` in this folder and the fixtures it used are under `fixtures/`.
The producer has repaired the tool. This round is **correction confirmation and regression**: read-only, adversarial, no repairs.

## What you have (this folder is your whole workspace)

- `old/ui-cad-gate.py` — the tool before the whole change (unchanged from round 1).
- `r1/ui-cad-gate.py` — the tool round 1 inspected.
- `new/ui-cad-gate.py` — the repaired tool. **Do not modify it.**
- `r1-to-new.diff` — the repair. `old-to-new.diff` — the whole change.
- `template-37-ui-rulings.yaml` — the ledger template after the repair.
- `r1-report.md`, `fixtures/` — round 1's report and fixtures.

You may create fixtures anywhere inside this folder and run the three tools on them with `python <tool> --ui-dir <dir>`.
Python with PyYAML is available. No network. Nothing outside this folder.

## What the repair claims (the only thing disclosed about the producer's reasoning)

- IA-01 / IA-07: the exemption is removed. A ruling that was taken out of the bundle and has since been ruled by the user is a
  human-decided ruling like any other and must be listed when its `ui_ids` overlap the bundle. The former known-good self-test arm
  is now a known-bad arm, and a new known-good arm lists it.
- IA-02: a second row for the same id in `confirmed_checked` fails.
- IA-03: a `touches_confirmed` field that is present but empty fails; the presence of the field (even empty) makes GU7 run.
- IA-04: rule (c) requires the boolean `true`; anything else (including the string "false" or "true") fails while the entry is open.
- IA-05 / IA-06: GU7 compares ids as strings; a numeric id can be listed; ids of different types that become the same string fail.
- IA-08: the target of `touches_confirmed` must be a ruling with `status: ruled` and `decided_by: user`.
- Unchanged claims: on a ledger with no open `provisional-bundle` and no `touches_confirmed` field, the new tool's exit code and
  whole output are identical to the old tool's. Declared limits are as in round 1 (the truth of `touches: no` is not judged;
  overlap is equality of `ui_ids` strings; an untyped bundle is not read; "human" means `decided_by` is exactly `user`).

## What to do

1. For each of IA-01 to IA-08, decide **closed** or **not closed**, using round 1's fixture and at least one variation of it.
2. Regression: look for a verdict that the repair made wrong — a ledger that satisfies (a), (b), (c) and is now failed by GU7
   (a false fail), or a new false pass, or a traceback. Re-check the no-bundle claim (old versus new) on your round-1 cases and a
   few new ones.
3. The self-test (`python new/ui-cad-gate.py --selftest`): for the arms added in the repair, would each stay green if the repaired
   check it names were removed? (Mutate a copy under another file name; never edit `new/`.)
4. The template's wording against what the tool now enforces.

## Your report

Put your whole report in **your final message** (nothing else is read):

```
VERDICT: ACCEPT | REJECT
(REJECT means: under the stated intent and claims, the repaired change should not be accepted as it is.)

ROUND-1 FINDINGS
- IA-01 closed | not closed — <one line: what you ran and saw>
- ... (all eight)

NEW FINDINGS
- IB-01 [false pass | false fail | crash | selftest | wording | other] <one sentence>
  input: <smallest ledger or fixture path>
  observed: <exit code and output lines>
  expected: <what the stated intent requires>
(Write "none" if there are none.)

WHAT I RAN
- <commands and counts>

NOT CHECKED
- <what you did not or could not check>
```
