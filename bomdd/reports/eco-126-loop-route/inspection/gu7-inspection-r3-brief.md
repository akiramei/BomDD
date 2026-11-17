# Independent inspection brief, round 3 (one scoped round) — three repairs of GU7 in `ui-cad-gate.py` that no inspector has seen

Role: **inspector**. You are of a different lineage from the producer. Responsibility: a verdict on the tool revision in `new/`
within the range below, and your findings. Range: **correction confirmation and regression** (是正確認+回帰). Read-only,
adversarial, no repairs.

## Why this round exists

Round 2 of this inspection (the report is `r2-report.md` here) ended in REJECT: IA-08 not closed through IB-01, and two new
findings IB-01 and IB-02. After that round the producer changed the tool three times. No inspector has seen those changes.
This round looks at those three changes and at what they may have broken. Nothing else is in range.

## What you have (this folder is your whole workspace)

- `r2/ui-cad-gate.py` — the tool round 2 inspected (sha256 `1f397cfb…e4e3938`).
- `new/ui-cad-gate.py` — the tool now (sha256 `8f7e25ca…f70b9902a`). **Do not modify it.**
- `old/ui-cad-gate.py` — the tool before the whole change.
- `r2-to-new.diff` — everything changed since round 2. `old-to-new.diff` — the whole change.
- `template-37-ui-rulings.yaml` — the ledger template now; `r2-template-37-ui-rulings.yaml` — as round 2 saw it;
  `r2-to-new-template.diff`.
- `r1-report.md`, `r2-report.md`, `fixtures/` (round 1), `r2-variants/` (round 2's ledgers, yours).

You may create fixtures anywhere inside this folder and run the tools on them with `python <tool> --ui-dir <dir>`.
Python with PyYAML is available. No network. Nothing outside this folder. Your environment differs from the producer's on
purpose (a sandboxed copy, not the repository): if a result depends on that, say so and name the cause.

## What the three changes are said to do (the only thing disclosed about the producer's reasoning)

- **C1 (for IB-01):** an empty member (null, empty or blank string) of a `touches_confirmed` list fails GU7; it is no longer
  dropped silently.
- **C2 (for IB-02):** a ruling that names itself in `touches_confirmed` fails GU7.
- **C3 (not from an inspector; from the producer's own review):** an entry that carries `touches_confirmed` and has
  `status: ruled` fails GU7 unless its `decided_by` is exactly `user`.
- Unchanged claims: on a ledger with no open `provisional-bundle` and no `touches_confirmed` field, the tool's exit code and
  whole output are identical to `old/`'s. Declared limits are as before (the truth of `touches: no` is not judged; overlap is
  equality of `ui_ids` strings; an untyped bundle is not read; "human" means `decided_by` is exactly `user`).

## What to do

1. For each of C1, C2 and C3 decide **closed** or **not closed**: does `new/` fail the input class the change names? Use round
   2's ledgers (`r2-variants/regression_mixed_empty_target.yaml`, `regression_self_reference.yaml`) and at least two variations
   of each class that you write yourself. IA-08 (not closed in round 2 only through IB-01): closed or not closed now.
2. Regression, limited to what these three changes could affect:
   - a ledger that satisfies the stated rules and is now failed by GU7 (a false fail);
   - a new false pass in the same code path (the handling of `touches_confirmed` members and of who ruled);
   - a traceback;
   - IA-01 to IA-07: does each still hold on round 1's fixture (one run each is enough);
   - the no-bundle claim (`old/` against `new/`) on round 2's no-bundle ledgers and a few of your own.
3. The self-test (`python new/ui-cad-gate.py --selftest`): for the three arms added for C1, C2 and C3, does each turn red when
   the check it names is removed? (Mutate a copy under another file name; never edit `new/`, `r2/` or `old/`.)
4. The template's wording (`r2-to-new-template.diff`) against what the tool now enforces for C1, C2 and C3.

Anything you notice outside this range goes under OUT-OF-RANGE OBSERVATIONS and is **not** part of the verdict.

## Observable limits on you

No change to `new/`, `r2/`, `old/`, the reports or the templates in this folder; nothing written outside this folder; no git
commands that write. Do not repair anything: write what you find.

## Your report

**Your final message is the report, and it is the only channel**: the harness saves it. Do not write a report file yourself.
The **first line** of the final message must be exactly one of the three words below, alone, starting at column 0:

```
ACCEPT
```
or `REJECT` or `UNMEASURABLE`.

- `ACCEPT` — within the range above, the tool in `new/` does what C1, C2 and C3 say and the regression checks found nothing wrong.
- `REJECT` — one of C1, C2, C3 is not closed, or the regression checks found a wrong verdict or a traceback.
- `UNMEASURABLE` — you could not run enough to decide (say what stopped you).

Then, in this order:

```
CHANGES
- C1 closed | not closed — <one line: what you ran and saw>
- C2 closed | not closed — <...>
- C3 closed | not closed — <...>
- IA-08 closed | not closed — <...>

REGRESSION
- IA-01 … IA-07: <holds | does not hold> each, one line
- false fails: <none | finding>
- false passes in the same path: <none | finding>
- tracebacks: <none | finding>
- no-bundle identity: <n cases, identical | finding>

NEW FINDINGS (in range)
- IC-01 [false pass | false fail | crash | selftest | wording] <one sentence>
  input: <smallest ledger or fixture path>
  observed: <exit code and output lines>
  expected: <what the stated rule requires>
  severity: <blocking | minor>
(Write "none" if there are none.)

OUT-OF-RANGE OBSERVATIONS
- <anything outside the range; "none" if none>

WHAT I RAN
- <commands and counts; the three mutants and what each self-test did>

NOT CHECKED
- <what you did not or could not check>
```
