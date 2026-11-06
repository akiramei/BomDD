# EXP-20261107-02 — definitions (fixed before any writer starts)

Fixed 2026-11-07. A change after this point is a departure (section 8).

## 1. The question

EXP-20261107-01 found no difference between writers with BehaviorForge (K) and without it (C) on MoviePad's undo / redo:
988 asserted values, none contradicted by the authority, no open fact stated wrongly. Two explanations fit and that run
separates neither (its results section 3): (a) the common scaffolding — above all the machine form's `unresolved` field and
the sentence telling a writer that an unwritten value says nothing — carried the kit's central idea into the control; (b) the
model writes this way anyway. The user chose "A: 素の対照を足す".

**The question:** with the `unresolved` field and that sentence removed and everything else as C had it, do fresh writers
assert values that the authority contradicts — in particular on the facts the sources leave open (F6-F11 of EXP-20261107-01
section 2)?

One variable is removed. The observed start screen and the observation list stay: without them most values at the start would
be guesses about the sample, and a fail there would say nothing about undo. So (a) is tested only for the field, not for the
CAD.

## 2. Reused (by path and hash)

EXP-20261107-01's sources, `cad/actions.json`, `cad/observations.json`, `cad/start-screen.json`, the head of C's prompt
(`../exp-20261107-01/prompts/head-c.md`), the observing harness (the build of that run, same staging), `prepare.py runs`,
`compare.py` and its fact placement, the scorer prompt and `tally.py`'s direction rule. The facts F1-F11 and their D / N
classes as filed in `../exp-20261107-01/definitions.md` section 2 (F5's class flagged contestable there; kept).

## 3. What changes (this folder)

- `prompts/common-bare.md` = EXP-20261107-01's `common.md` with two edits only: the schema line without `"unresolved"`, and the
  `expect` sentence cut to "`expect` は、その手順のあとに画面に出ている値です。" (the diff is the whole change; the word
  `unresolved` appears nowhere in the package).
- `check_examples.py` = EXP-20261107-01's with the `unresolved` key rejected as unknown and its checks removed.
- Writers **B1, B2**: prompt = `head-c.md` + `common-bare.md`; fresh Claude agents (general-purpose, the session's default
  model), started together, each given only its folder; bound 45 minutes; liveness every 10 minutes.

## 4. Measures and reading (fixed now)

Per writer, never pooled; compared with C1 and C2 of EXP-20261107-01 (fails 0 and 0, N facts wrong 0 and 0).

- **R1′:** fails on the authority. Both B writers ≥ 1 → "without the field, writers asserted what the authority
  contradicts — on this feature the field carried the discipline (explanation a, for the field)". Both 0 → "the field did not
  carry it here; explanation (b) or the remaining scaffolding". One each → no claim.
- **R2′:** N facts (F6-F11) scored `wrong` by a fresh scorer (the same prompt; labels W1 / W2 by a hashed shuffle). Read the
  same way against C's 0 and 0.
- Reported as measures: asserted values, values after a press and directly after Undo / Redo, fails by placed fact, fails
  placed at N facts (F6-F10), the scorer's per-fact verdicts, questions and how many the sources answer, time.

## 5. Order

1. Commit this folder (filing). No push before the end (AGENTS.md rule 4 gates the push; self-conformance runs once before it).
2. `prepare.py package` into EXP-20261107-01's staging folder; `verify`.
3. Slice: the bare checker accepts the slice of EXP-20261107-01 with its `unresolved` entries removed and rejects it with them
   (done at filing: C2's examples, OK 12 / 3 errors on the first steps; recorded here).
4. Two writers; isolation by `../exp-20261030-04/isolation.py`; packages verified after.
5. Freeze (`../exp-20261107-01/freeze.py freeze` writes into that folder, so a copy of its freeze step writes `run-B*/` here);
   observe; compare; scorer; key opened; tally; `results.md`.

## 6. Limits

- One variable (the field and its sentence); the observed CAD stays.
- Two writers; one feature; one model. A difference against C is against a run made earlier the same night.
- The writers can still leave a value unwritten; what is removed is the invitation, not the possibility.

## 7. Files

This file, `prepare.py`, `check_examples.py`, `prompts/common-bare.md`; at the run `run-B1/`, `run-B2/`, `scoring/`,
`results.md`.

## 8. Departures

- **D1 — "the word `unresolved` appears nowhere in the package" is false (found after packaging, before the writers
  started).** It appears in the source `10-requirements.yaml` as the field name `unresolved_questions`, as it did for every
  writer of EXP-20261107-01. The prompt and the checker carry no `unresolved`; section 3's claim holds for them only.
- Writers B1 and B2 started 02:31:52 (agents `a71db1f5…` B1, `ad01cb21…` B2).
