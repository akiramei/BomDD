# EXP-20261030-05 — results (stage 2)

Run 2026-10-30 on the user's "A: 走らせる", by `definitions.md` as filed in `4cc64af` (departures D1-D3 in section 11).
Nothing was written into MoviePad or MoviePad-Remake (both read by `git show`).

## 1. The run, in the order of section 8

1. **Package** (`prepare.py package`): 27 states, 45 action rows, the two READMEs and MoviePad-Remake's requirements; hashes in
   `writer/package-sha256.txt`. The 31 mutants rebuilt from stage 1's `mutant-edits.json`: 0 mismatches.
2. **`compare.py selftest` PASS**, 13 cases: each category (caught, outside, agreeing, masked, other) and the f false alarm with
   a planted case and a twin, uncounted steps, and (after D2) W3 on an `"unknown"` expect.
3. **Real slice** (`slice/`): it found that a wrong surface cannot be written (D1); with a disabled pair planted instead, the
   clean keys were exactly the two planted ones, and M01 agreeing, M02 / M04 / M05 / M11 caught, 20 outside, f silent — each
   checked by hand.
4. **Two writers**, fresh Claude agents started together at 23:00:57 with the same prompt (`writer/prompt.md`): A finished in
   about 3.6 minutes, B in about 2.5 (bound 60). Isolation 0 flags for both; both packages unchanged after the run. A reports
   reading the files the prompt named; B reports not reading `README.md` (it read the Japanese one).
5. **Frozen** (no scenario dropped by the form check):

| writer | scenarios (main / alternate) | steps | `"unknown"` expects | ending steps | SHA-256 |
|---|---|---|---|---|---|
| A | 25 (17 / 8) | 61 | 4 | 4 | `bb48a8fe…` (`run-a/freeze.json`) |
| B | 26 (14 / 12) | 70 | 6 | 5 | `520deebe…` (`run-b/freeze.json`) |

   Walk on the clean mock and the 31 mutants (`run-a/flags.json`, `run-b/flags.json`).

## 2. Verdict by the fixed reading (`definitions.md` section 6)

| category | A | B | stage 1 (inside / outside, for comparison) |
|---|---|---|---|
| caught | 23 | 22 | 20 inside |
| outside | 2 | 3 | 5 outside |
| agreeing | 0 | 0 | — |
| masked | 0 | 0 | — |
| other | **0** | **0** | — |
| f false alarms | **0** of 6 | **0** of 6 | 0 |

**For both writers other = 0 and f gives 0 false alarms → by reading 6.1, "with an ordinary upstream, every miss of the walk is
placed — coverage or the upstream's error — once a correct reference is at hand".** Every miss was placed as outside; no defect
was masked by, or agreed with, a writer's error. Other = 0 was expected by construction (section 5).

Per class (caught / outside): A — a 4/1, b 4/1, c 5/0, d 5/0, e 5/0; B — a 4/1, b 3/2, c 5/0, d 5/0, e 5/0.
Outside: A M07, M15; B M07, M09, M15. The two writers place 24 of the 25 alike (M09: A caught, B outside).

Measures (section 6):
- **Clean stop flags:** A W1 0 / W2 0 / W3 6; B 0 / 0 / 7. W2 is 0 by construction (D1); no writer step used a pair that is
  disabled or absent on the clean mock (counted 61 of 61 and 70 of 70).
- **Coverage:** pairs A 50 / 774, B 53 / 774 (stage 1 44); actions A 35 / 44, B 33 / 44 (stage 1 32). Counted pairs shared by A
  and B 42 (union 61); with stage 1, A 30 and B 31 (union of all three 73).
- Against stage 1, the writers caught M03, M25 and M27 (both) and M09 (A), which stage 1 missed: they used speed 1.5, Redo in
  ST-15 and `SwitchLanguage` (stage 1's writer avoided it, D8 there) and, for A, volume 150. Both missed M15 (`SetFps:60`), which
  stage 1 caught: neither wrote a frame-rate step ("no state shows it", in both reports). M07 is outside for all three.

## 3. Read after the verdict: the clean flags are mostly the mock's errors (descriptive, not readings; D3)

Section 1 takes every clean flag as the scenario's error "because the mock is the authority's". `verify_on_authority.py` gave the
8 flagged writer scenarios, with stage 1's states, predicates and start setups, to stage 1's harness, which executes them on the
authority's view model (`verify/certify.json`):

- **6 of the 8 certify** — every step's `in` and `expect` holds on the authority: A UC-03, UC-04, UC-08; B UC-03, UC-07, UC-13.
  Their **11 flags are the mock's errors, not the writers'.** With them added, the harness reports ST-02, ST-03, ST-04, ST-05 and
  ST-08 **ambiguous**: what Undo or Redo does from those states depends on the undo history (which edit is undone or redone),
  which the state predicates do not carry. Stage 1's mock took each state's transitions from one instance reached by stage 1's own
  paths; the writers reached the same states by other edits (a speed preset, a volume preset, a split followed by a speed preset,
  a trim end), where Undo and Redo go elsewhere. Availability did not differ (only transitions).
- **2 fail** — A UC-24 and B UC-25: after `DismissFfmpegSetup` the authority holds ST-13 (playhead 6 s, the sample's trim start),
  not ST-01 (playhead 20 s). Both writers made this one error, and both named it as a guess in their reports. It is an error
  against the authority, but the given vocabulary invited it: no state is marked as the startup state, and ST-01's playhead of
  20 s exists only because stage 1's setup put it there.

So of 13 clean flags, **2 are the writers' errors and 11 are the reference's**, which was correct only on the paths it was built
from. None of the 11 fell on a step a mutant placement depends on (agreeing and masked are 0), so the verdict's placements stand —
but had a mutant fallen there, a "masked" miss would have been charged to the upstream when the reference was at fault.

What this says about the user's question: a correct reference separates the upstream's failures from the mechanism's **where it
was built**; a reference generated from one scenario set is a model of the authority on that set's paths, and a flag on another
path can be the reference's own. Telling the two apart took the authority itself (execution), not the mock. Stage 1's claim that
the clean mock is "the authority's transitions on the visited states" (its `definitions.md` section 5) holds only on the visited
paths; recorded as a correction there (its `results.md` section 5).

## 4. Other observations (descriptive)

- The writers' errors are all transitions: no writer wrote an action in a state where the authority disables it. Both reports
  say they left out steps they could not settle (frame rate, abort during export, steps the app might refuse) — the upstream's
  silence goes to coverage (M15), not to flags.
- The writers' own "could not settle" lists named the one real error (ffmpeg Later) and several correct choices (pause, Reset,
  the undo of a second edit).
- W4 on the clean mock: A 724, B 721 enabled elements used by no step.

## 5. Limits (in addition to `definitions.md` section 9)

- The categories agreeing and masked never occurred on real scenarios; they were exercised only by the selftest and the slice
  (agreeing on M01). Whether an upstream's errors hide defects is not measured here — these writers' errors did not meet the
  mutants' places.
- The reference's off-path errors (section 3) are a property of the mock's state abstraction for history-dependent actions; other
  actions showed none, on these paths.
- Two writers from one prompt, one seeder; no rate.

## 6. Files

`definitions.md`, `prepare.py`, `check_schema.py`, `compare.py`, `after_verdict.py`, `verify_on_authority.py`; `writer/`
(prompt, states, actions, package hashes, start time); `slice/`; `run-a/`, `run-b/` (written, frozen, `freeze.json`,
`flags.json`, `flags-as-filed.json` — the walk before D2); `after_verdict.json` (and `-as-filed`); `verify/` (`scenarios.json`,
`certify.json`). The staging folder is outside every repository and deleted on the user's word.
