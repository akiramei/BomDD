# Independent inspection brief — a new check (GU7) in `ui-cad-gate.py`

You are an independent inspector of a different lineage from the producer. This is a **read-only acceptance inspection** of one
change to an inspection tool. Be adversarial: your job is to find inputs for which the changed tool gives a wrong verdict.
Do not repair anything.

## What you have (this folder is your whole workspace)

- `old/ui-cad-gate.py` — the tool before the change.
- `new/ui-cad-gate.py` — the tool after the change. **Do not modify it.**
- `gu7.diff` — the difference between the two.
- `template-37-ui-rulings.yaml` — the ledger template after the change (its comment block, discipline 9, and examples 4 and 5 state
  the rule in the product's words).

You may create fixture folders and files anywhere **inside this folder** and run `python new/ui-cad-gate.py --ui-dir <dir>` and
`python old/ui-cad-gate.py --ui-dir <dir>` on them. Python with PyYAML is available. Do not use the network. Do not touch anything
outside this folder.

## What the change is meant to do (the intent — the only thing disclosed about the producer's reasoning)

The gate reads a UI rulings ledger (`37-ui-rulings.yaml` or `ui-rulings.yaml`) together with `ui-ir.json`, `ui-bom.json`,
`ui-trace-map.json` and an optional dictionary. The new check GU7 applies to a ledger that holds an **open bundle of provisional
decisions** (`type: provisional-bundle`, `status: open`):

- (a) every ruling that a human decided (`status: ruled` and `decided_by: user`) and whose `target.ui_ids` intersect the bundle's
  must be listed in the bundle's `confirmed_checked` as `{id, touches: yes|no, why}`; an omission must make the gate fail;
- (b) for each row with `touches: yes` there must be a separate ruling that carries `touches_confirmed: <that id>`;
- (c) a ruling that carries `touches_confirmed` must be `blocking: true` while it is `open`.

Claims made for the change:

1. **No effect without a bundle.** On any ledger that has no open `provisional-bundle` entry and no `touches_confirmed` field, the
   new tool's exit code and its whole output are identical to the old tool's.
2. **GU7 stops the omission.** A ledger that violates (a), (b) or (c) exits non-zero with a `[GU7] FAIL` line that names the
   reason; a ledger that satisfies them is not failed by GU7.
3. **Declared limits** (not defects, unless the tool contradicts them): GU7 does not judge whether a `touches: no` answer is true;
   overlap is by equality of `ui_ids` strings; a bundle that is not typed `provisional-bundle` is not read; "decided by a human"
   means `decided_by` is exactly `user`.
4. The self-test (`python new/ui-cad-gate.py --selftest`) has arms for GU7 whose known-bad arms are red **for the reason their label
   states**.

## What to look for

- An input that violates (a), (b) or (c) and still passes (a false pass), within the declared limits. Think about: YAML forms of
  yes/no, lists versus scalars in `ui_ids` and `touches_confirmed`, duplicate rows, ids as numbers, a bundle listing itself, two
  bundles, a superseded or rejected ruling, a `touches_confirmed` pointing at the bundle or at a non-existent id, an entry that is
  both a bundle and carries `touches_confirmed`, empty `ui_ids`, `confirmed_checked` rows with extra or missing keys.
- An input with no bundle and no `touches_confirmed` for which old and new differ in exit code or output (claim 1).
- An input that makes the new tool raise an uncaught exception (a traceback) where the old tool did not.
- A self-test arm that would stay green if GU7 were broken in the way its label describes (say how you checked — for example by
  reasoning about, or temporarily copying and mutating, a copy of the tool **under another file name**; never edit `new/`).
- Anything in the template's wording that contradicts what the tool enforces.

## Your report

Put your whole report in **your final message** (nothing else is read). Use this form:

```
VERDICT: ACCEPT | REJECT
(REJECT means: under the stated intent and claims, this change should not be accepted as it is. It is not a statement about the
rest of the tool.)

FINDINGS
- IA-01 [false pass | false fail | crash | selftest | wording | other] <one sentence>
  input: <the smallest ledger (YAML) and the other files' contents, or the path of a fixture folder you created>
  observed: <exit code and the relevant output lines>
  expected: <what the stated intent requires>
- IA-02 ...
(Write "none" if there are no findings.)

WHAT I RAN
- <commands and counts: how many fixtures, how many compared old vs new>

NOT CHECKED
- <what you did not or could not check>
```
