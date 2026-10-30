# EXP-20261030-05 — definitions (fixed before any scenario is written or any walk is run)

Fixed 2026-10-30. A change after this point is a departure (section 11).

## 1. The question

Stage 2 of the user's question (EXP-20261030-04 section 1): with an imperfect upstream, a failed or silent check cannot be told
apart — is the upstream wrong, or the mechanism? Stage 1 (`../exp-20261030-04/`) fixed a correct upstream and found the mechanism
sound inside coverage (20 of 20 a-e caught, 0 false alarms on f; qualification, by construction). The user chose to file stage 2
("A: 起票する", 2026-10-30).

**Stage 2:** the same clean mock and the same 31 mutants, walked by the same checks, with **ordinary upstreams** — use case
scenarios drafted by fresh AI writers from the requirements, not from the code and not certified. Because the mock is the
authority's, every flag on the clean mock is an error of the scenario, and every miss on a mutant can be placed: **outside** the
scenarios' coverage, **masked** by an error already flagged at that step, **agreeing** (the scenario's error matches the defect, so
a flag disappears), or **other** (none of these: the mechanism). Does every miss fall into the first three, and how do they split?

This is a measurement. It changes no method text, template, tool or product. Nothing is written into MoviePad or MoviePad-Remake;
both are read by `git show` only.

## 2. Reused from stage 1 (by path and hash; nothing regenerated)

- Clean mock: `../exp-20261030-04/run/mock.html`, SHA-256 `f3a4841dd1ccabcf1b368d0012671af7d16639e3003a59d4526230cef7420e65`
  (27 states, 859 elements; the authority's availability, surfaces and transitions on the states stage 1 visited).
- Mutants: rebuilt from `../exp-20261030-04/run/mutant-edits.json` by `record_mutants.py`; each rebuilt file must match its
  recorded SHA-256 before any walk (stage 1 walked the seeder's own files; D9 there).
- Checks: `../exp-20261030-04/walk.py` — W1 walk, W2 surface, W3 transition (stop), W4 reverse coverage (measure), unchanged.
- Stage 1's inside / outside per mutant (`../exp-20261030-04/run/flags.json`), for comparison only.

## 3. What a writer is given

Fixed rule, applied by `prepare.py package`:
- **Requirements:** the authority's `README.md` and `README.ja.md` (MoviePad `126eae9`) and MoviePad-Remake's
  `bomdd/10-requirements.yaml` (`a2ca41e`) — the remake's own upstream as it exists (derived by an AI from the authority's manual,
  code and tests; screens outside its scope).
- **States** (`states.json`): the 27 states that have a section in the clean mock, by id and name only — no predicate, no
  view-model path. Names are stage 1's with the availability terms removed (分割可・結合可・In 可・Out 可) and the undo / redo terms
  said as history (取り消し可 → 直前の編集あり, やり直し可 → 取り消した編集あり). Why this cut: whether Split or a trim end is possible at
  a playhead is design knowledge the writer must infer from the requirements (class a's knowledge); that an edit can be undone is a
  requirement-level fact. **Checked at filing: `prepare.py check` → 27 states, 27 unique names.** With the history terms removed
  too, 15 states would share 6 names (checked the same way), and correct undo / redo scenarios could not be written.
- **Actions** (`actions.json`): 45 rows (44 ids; `Scale:1` has two elements) of id, surface, label — no visibility or
  enabledness conditions.
- **Schema and checker:** the schema of section 4 and `check_schema.py`, which checks ids and form only.
- **Not given:** the code, the mock, the harness, `bindings.json`'s conditions, stage 1's scenarios, mutants, classes or checks.

## 4. Scenario schema (`scenarios.json`)

```
{"scenarios": [{"id", "title", "goal", "flow": "main"|"alternate",
                "steps": [{"in": <state id>, "action": <action id>, "surface": <surface>, "expect": <state id>|"unknown"}]}]}
```
- `in` one of the 27 ids; `action` and `surface` a row of `actions.json`; `expect` one of the 27 ids or `"unknown"` (the result is
  none of the listed states). `"unknown"` is counted; W3 does not read it.
- `Open`, `ConfirmExport`, `InstallFfmpeg` end a scenario (file dialog or external process); the freeze adds `"harness": "no"` to
  them, as stage 1's schema had (W1 and W2 read them, W3 does not).
- 2-10 steps per scenario, 10-25 scenarios (the same guide as stage 1). A scenario failing `check_schema.py` at the freeze is
  dropped and counted.

## 5. Walk and placement (`compare.py`, deterministic)

Per writer: `walk.py` on the clean mock gives the clean stop flags **C**; on each mutant, **M**. A flag's key is (check, `at`),
`at` = scenario id and step index.

- **Changed elements E** of a mutant: for a and e the (state, action) it changes; for b, c, d every (state, action) of the action
  it changes; f has none.
- A step **uses** E when its (`in`, `action`) is in E. A step is **counted** when its (`in`, `action`) is present and enabled on
  the clean mock (a wrong step earns no coverage). **Coverage** = the enabled pairs of the clean mock used by a counted step, over
  774; and the actions used by a counted step, over 44.

Each a-e mutant goes to exactly one category, in this order:

| category | when | attributed to |
|---|---|---|
| caught | M has a key not in C | — |
| outside | no counted step uses E | the upstream's coverage |
| agreeing | a key of C at a step that uses E is absent from M | the upstream's error, matching the defect |
| masked | every counted step that uses E carries a key in C | the upstream's error, flagged already |
| other | none of the above | the mechanism |

For f, any key in M and not in C is a **false alarm**.

**Expected by construction:** the mock is the authority's, so a key in C is an error of the scenario against the authority, and a
counted step with no key in C that uses E must raise one on the mutant (W1 for a, b, c; W2 for d; W3 for e, unless the new goto is
the step's `expect` — which is agreeing only if C had the key) — **other = 0 is expected**. What is not fixed by construction: how
many errors the writers make and of which check, how the misses split between outside, masked and agreeing, the coverage an
ordinary upstream reaches, and whether two writers given the same inputs agree.

## 6. Reading (fixed now)

Per writer, never pooled:
1. **other = 0 and f gives 0 false alarms** → "with an ordinary upstream, every miss of the walk is placed — coverage or the
   upstream's error — once a correct reference (here the authority's mock) is at hand": the user's hypothesis, measured on one
   product with two writers. What follows (a stage that also takes away the given binding between scenario words and a designer's
   mock, or work on the upstream) is the user's; nothing is filed by this result.
2. **other > 0** → the mechanism has a gap that stage 1 did not show, named from the mutant and the step.
3. **A false alarm on f** → the walk reads something not structural, named.

Reported as measures (no threshold): clean stop flags per check (each an upstream error relative to the authority); the split of
the 25 a-e mutants into caught / outside / agreeing / masked; coverage against stage 1's 44 / 774 and 32 / 44; per mutant, the
category for each writer next to stage 1's inside / outside.

## 7. Also reported (descriptive)

Scenarios written / dropped; steps; `"unknown"` expects; steps not counted (wrong pair) by check; the time of each writer; the two
writers' overlap (counted pairs both use; mutants placed alike); W4 on the clean mock.

## 8. Order (each step's output is committed or hashed before the next starts)

1. `prepare.py package` into a new staging folder outside every repository; `record_mutants.py verify` on the 31 (all match).
2. `compare.py selftest`: for each category and for the f false alarm a planted case and a silent twin, on a synthetic mock and
   scenario set, reported case by case.
3. **One real slice end to end** (the `run-new-instrument-on-real-files` rule): one hand-written scenario using the real
   vocabulary, with one deliberately wrong `expect` and one wrong `surface`, walked on the clean mock (exactly the two planted
   keys) and on the rebuilt mutants, placed; categories checked by hand on at least one mutant per category it reaches.
4. **Two writers**, fresh Claude agents started together, each given only its own copy of the package (section 3) and a prompt
   with stage 1's wording (write what a user does: main flows and alternate flows — undo, cancel, retry, another way in — as the
   application behaves by its requirements; not told to pass anything; not told of mocks, mutants or checks). Bound 60 minutes;
   liveness by the output file's modification time every 10 minutes. Isolation by `../exp-20261030-04/isolation.py` over each
   transcript; the package is hashed before and checked after.
5. Freeze each writer's file (SHA-256). Walk clean and the 31 per writer; place; tally.

No product code is executed in stage 2 (stage 1's D8 does not recur): the walk reads the mock only.

## 9. Limits

- **The binding is given:** action ids, surfaces and state ids are the mock's own. A designer's mock with its own names is not
  measured (not filed).
- **The state names leak part of the design:** the history terms imply Undo / Redo availability, and the numbers (regions, trim,
  playhead) are the authority's sample document. The writer is held to the 27 states stage 1 visited; an upstream that would go
  elsewhere cannot.
- The requirements are the remake's, derived by an AI partly from the authority's code; their scope leaves screens out.
- "Error" is relative to the authority, defects included.
- The same 31 mutants from one seeder (stage 1's correlation limit stands). Two writers: no rate is claimed.
- W4 cannot point at a removal (stage 1 section 3).

## 10. Files and the run (when the user starts it)

- Committed at filing: this file and `prepare.py`. At the run: `compare.py`, `check_schema.py`, the writers' prompt, the package's
  hash, each writer's `scenarios-written.json` and frozen file with `freeze.json`, `flags.json`, the slice, `results.md`.
- The staging folder is outside every repository and deleted after the recording commit on the user's word.

## 11. Departures

None yet.
