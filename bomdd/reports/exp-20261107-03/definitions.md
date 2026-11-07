# EXP-20261107-03 — definitions (fixed before any writer starts)

Fixed 2026-11-07. A change after this point is a departure (section 11).

## 1. The question

The user built BehaviorForge after feedback that the re-implementations of MoviePad, ViewTube and ViewPrism2 had software CAD
and mocks but a weak domain model and weak verification. EXP-20261107-01/02 tried it on MoviePad's undo / redo and saw no
difference, but on an input that did not follow the re-implementation's path: the writers were given MoviePad-Remake's
requirements (a past re-implementation's own output) and an observation list and start screen that I had made from the
authority, so the step where re-implementations go wrong — building the skeleton (what states exist, what the screen shows)
from the original — was solved before they started. This run keeps that step inside the measurement.

**Basis for the feature** (wording as reviewed with the user, 2026-11-07): past research observed the frame-rate operation
dropping out of scenarios (EXP-20261030-05: 0 of 2 writers wrote a frame-rate step), on a constrained input (a state list made
from a mock, with no frame-rate state). That a past re-implementation *product* lacked frame-rate features is **unconfirmed**;
the specific text of the "weak domain model / weak verification" feedback is not in hand. Neither is a start condition.

**The question:** given only MoviePad itself (`126eae9`: its code, tests, user docs and design mock), do fresh writers who use
BehaviorForge extract the original's frame-rate behaviour — its operations, states, displays and consequences — more completely
and with fewer wrong statements than fresh writers given the same task without the kit?

Corrections made while preparing this filing: MoviePad's `README.md` / `README.ja.md` do not describe the output frame rate
setting (fps appears once, in number formatting); `docs/QUICKSTART.md` / `.ja.md` §4.6 do, with a screenshot.

This is a measurement. It changes no method text, kit file or product. MoviePad is read by `git show` / `git archive` only;
BehaviorForge is read and copied, never written.

## 2. The sealed list

`targets.md`: sixteen frame-rate behaviours T01-T16 read from the code, each with its evidence lines, a **class** (a: in the user
docs, b: on screen only, c: in the code only) and whether it can be executed on the harness's sample. It is the scoring key and is
given to no writer and to no mapper. Coverage is reported per class, so a writer who copies the quick start is told apart from
one who read the code.

## 3. What every writer is given (`prepare.py package`, written before the writers start)

A folder per writer outside every repository:

- `moviepad/` — `git archive 126eae9` of MoviePad **minus BomDD management material**: `bomdd/`, `bomdd-kit/`, `bomdd.lock`,
  `.claude/`, `AGENTS.md`, `CLAUDE.md`, `docs/golden-checklist-p1.ja.md`, `docs/windows-verification-p1.ja.md`,
  `docs/windows-verification-p1-report.ja.md`. Everything else stays: the code, `tests/`, `tools/`, `README*`,
  `docs/QUICKSTART*` and `docs/images/`, `design_handoff_moviepad/` (the product's own design mock), `.github/`.
- `check_examples.py` — checks the form of `examples.json` only, never its values.
- **Arm K only:** `kit/` — BehaviorForge's 18 files as on disk at packaging (hashed).

Not given: MoviePad-Remake, any experiment's files, `targets.md`, the harness, its menu. The writers may read; they may not
build or run the application (no existing isolation covers the settings file MoviePad writes, EXP-20261030-04 D8).

## 4. Arms and writers

- **K:** the kit's `prompts/start.md` with its fields filled — target: MoviePad re-implementation, the output frame rate and
  everything in the original that depends on it; sources: `moviepad/` (the original, authoritative); permitted: reading and
  documents; not permitted: building, running, other folders — followed by the common section.
- **C:** a neutral prompt — "from the original, write the requirements, a domain model and the behaviour of the output frame
  rate and everything in the original that depends on it, and list what you would ask the product's owner" — followed by the
  same common section.
- **Common section (identical bytes):** the folder boundary; deliverables (documents under `out/`, and `examples.json`); the
  examples form (section 5); 75 minutes; a short final report.
- Two writers per arm (K1, K2, C1, C2), fresh Claude agents (general-purpose, the session's default model), started together.
  Bound 75 minutes (the input is a source tree, not three files as in EXP-20261107-01's 45 minutes); liveness by the newest
  file's modification time every 10 minutes; a writer past the bound is stopped and frozen as it is.

## 5. The examples (`examples.json`) — in the screen's own words

```
{"examples": [{"id": "EX-01", "title": "...",
               "steps": [{"press": "<the control as the user sees it: its label and where it is>",
                          "expect": [{"element": "<what the user looks at>", "shows": "<text shown, or visible / hidden / active / not active>"}]}]}]}
```
Every example starts from "a 30 fps constant-frame-rate clip has just been opened; nothing else has been done". The first step
may have `"press": null` (what is shown at that start). 3-20 examples, 1-8 steps each. A value not written is not asserted.
This sentence about the start is the only fact about the fixture any writer is given.

## 6. Scoring (the reading's measure)

A fresh scorer gets `targets.md` and the four writers' `out/` and `examples.json` under shuffled labels W1-W4 (key hashed
before it starts), not the product tree (the list carries the authority's behaviour and evidence). Per writer and item:

- **correct** — a statement of the result that agrees with the item (in any words; a value shown through a derived display
  counts; a statement that gives the item's main result counts even if it leaves a detail out);
- **wrong** — a statement of a result that differs; a statement of mechanism is `wrong` only if it entails a result on that item
  that differs from the authority;
- **open** — the writer names the item as undecided or asks about it;
- **absent** — not mentioned.

The scorer also counts the writer's questions to the owner and how many the original answers (code, docs or mock).

## 7. Readings (fixed now)

Per writer, never pooled; a direction only when the arms do not overlap.

- **R1:** items `correct` (of 16). K1 and K2 both above C1 and C2 → "with the kit, more of the original's frame-rate behaviour
  was extracted"; the reverse → the reverse; otherwise no claim.
- **R2:** items `wrong`. Both K below both C → "with the kit, fewer wrong statements"; the reverse → the reverse; otherwise no
  claim.
- Reported, not read: `correct` per class (a / b / c), `open`, `absent`, questions and how many the original answers, time.
- **All writers extracting everything is a valid result.** No second topic is searched for if this one shows no difference.

## 8. Execution on the authority (descriptive, after the scoring; not a reading)

1. Archive `126eae9`, build EXP-20261107-01's observing harness against it, `harness selftest`; record
   `%LOCALAPPDATA%\MoviePad\settings.json`'s time before and after every run.
2. **The menu** (`menu.json`, evaluator side, hashed): each on-screen control and display that bears on T03-T13, by its English
   and Japanese labels from `Resources/Strings*.resx`, mapped to a command or view-model path (for example `OutFpsText`,
   `FpsText`, `FpsUpsampling`, `FpsSourceActive`, `FpsSourceTip`, `Edited`, `CanUndo`, `PlayheadTc`, `SetFpsCommand`).
3. **The slice:** a hand-made examples file with one planted wrong value and one unmappable element must give exactly those two
   outcomes before any writer's examples are mapped.
4. **The mapper** — a fresh agent given only the writers' `examples.json` (shuffled labels) and `menu.json`, never `targets.md`
   or the documents — maps each `press` and `element` to one menu entry only when the words identify it unambiguously; otherwise
   `unmappable`. It adds nothing a writer did not write.
5. Observe on the sample; compare (`shows` against the read value; text by exact match after trimming, numbers within 0.0005,
   visible / active as booleans). Reported per writer: asserted, hold, fail, unmappable, not run.

## 9. Limits

- The feature is named in the task, so whether a writer would leave the frame rate out of a whole-app skeleton is **not
  measured**; this run measures extraction completeness and correctness inside it.
- The kit's own example (`examples/video-export.md`) is an output-frame-rate setting, and its start prompt's placeholder is
  "the export settings of a video-editing re-implementation": the claim is "the kit as distributed, with a worked example of
  the same kind", not "the kit's procedure alone". The kit's documents also name MoviePad and EXP-20261107-01/02's result.
- MoviePad's code comments cite BomDD ECO numbers (for example `Services/ExportClock.cs`); the original is given as it is.
- Writers may read the code: what is measured is building a model from the original, not inferring behaviour unseen.
- The start sentence of section 5 tells every writer the fixture's source rate and that it is constant.
- Five items (T01, T02, T14, T15, T16) cannot be executed on the sample; execution covers T03-T13 only, and is descriptive.
- The scorer judges meaning; one scorer, no second. EXP-20261107-01/02's scorers drew a line differently once (F5); section 6
  fixes the line in writing for this one.
- Evaluator caution (not a scoring item): a reference that leaves out history can be wrong on undo / redo (EXP-20261030-05);
  T10 is scored from the code, not from a mock.
- Two writers per arm, one feature, one model; no rate.

## 10. Order

1. File this folder (`definitions.md`, `targets.md`) with the ledger entry; self-conformance before the push.
2. On the user's word: write `prepare.py`, `check_examples.py` and the prompts; check the checker on a hand-made file; package;
   hash.
3. Four writers together; isolation by `../exp-20261030-04/isolation.py`; packages verified after; freeze.
4. Scorer (section 6); open the key; tally R1 / R2; `results.md` with the verdict.
5. Execution (section 8) if the user wants it after the verdict; its result is added to `results.md` as descriptive.

## 11. Departures

(none yet)
