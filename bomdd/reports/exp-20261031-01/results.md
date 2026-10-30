# EXP-20261031-01 — results (run 2026-10-31 on the user's "A: 両方走らせる"; read by definitions section 9)

## 0. The reading

- **Part 2: 2 of 2 writers wrote a `SetFps:*` step** (EXP-20261030-05: 0 of 2). By section 9: **"given a domain model that lists
  the output frame rate, fresh writers bring it into the scenarios (here)".**
- **Part 1: no item is named by both models.** Model A names D01 (both classifiers); the other 7 (model, item) pairs are touch for
  both classifiers. Descriptive; four items give no rate.
- **The re-manufacture earns a proposal**, on part 2's 2 of 2 (the second trigger, 2 of 4 items named by both models, is not met:
  0 of 4). Its design and start are the user's.
- Measured besides, with nothing in question: other = 0 and f false alarms 0 for both writers; agreeing and masked 0.

## 1. Run (section 8, in order)

1. `items.py` exit 0 (7 items, window closed, `items.json` unchanged); `check_model.py selftest` PASS (5); `prepare.py
   prompt-diff` PASS.
2. Two deriver folders, identical (4 files, same SHA-256 in both); the derivers started together. A 240.7 s, B 314.1 s, both well
   inside the 60-minute bound; both `check_model.py` clean on their own run and again here; isolation
   (`../exp-20261030-04/isolation.py` on each transcript): 0 flags. Frozen: A `4ce36104…4d7475`, B `e27f1891…0dce` (`derive-*/`).
3. P holds for both, by machine and by hand: each has `OutputSettings.fps`, "the output frame rate", initial = the source's
   rate, set by `SetFps`, values the source rate and 24 / 30 / 60 / 120 (A also `ExportRequest.outFps`, `OutputFile.frameRate`;
   B also `ExportRequest.outFps`, `Exporter.vfrFpsFilter`, `ExportClock.F`).
4. Classifier folder (`prepare.py classify`), copied once per classifier (identical; the six inputs in `classify/sha256.txt`,
   the same in both folders after the run); two classifiers; isolation 0 flags;
   verdicts in `classify/verdicts-1.json`, `-2.json`; per (model, item) the two agree on all 8.
5. Two writer folders (`prepare.py write`): the package files match EXP-20261030-05's `package-sha256.txt` byte for byte; only
   `prompt.md` (one added line, checked) and `domain-model.json` differ. Started together 01:36:21; A 214 s, B 179 s. Isolation 0
   flags; the package unchanged after the run (re-hashed: `run-*/package-sha256.txt`). Both writers read `domain-model.json` (their tool calls). Frozen:
   A `7b198e99…40f8`, B `58537602…68d2`; 25 scenarios each, none dropped. `compare.py selftest` PASS; walked clean and over the 31
   mutants (rebuilt from `mutant-edits.json`, 0 mismatches; clean mock `f3a4841d…0e65`).
6. The flagged writer scenarios executed on the authority (`verify/`, as EXP-20261030-05's D3): the flagged scenarios' actions
   were read first (edits, undo / redo, `DismissFfmpegSetup`; no `SwitchLanguage`, no installer); MoviePad's
   `settings.json` modification time 21:24:07 before and after.

## 2. Part 1 — the four countable items

| item | what was repaired | model A | model B |
|---|---|---|---|
| D01 | export error order (ffmpeg unavailability moved after the empty-output errors) | **named** (question 19) | touch (`ExportRun.outcome`) |
| D02 | acceptance audio compared by decoded content | touch | touch |
| D03 | the keyframe lookup's window | touch | touch |
| D06 | a silent source stays copy-eligible after a volume change | touch | touch |

- A's D01 is named by the question alone: A asks why `FfmpegUnavailable` precedes `ZeroDuration` / `NoRegions` when REQ-018 says
  empty output is refused before ffmpeg runs — the point the repair changed. A's attribute `ExportJob.outcome` keeps the
  pre-fix order.
- The other seven: both models state the pre-fix text (D03: the window `[max(0, target − L), target]`; D06: copy only when speed
  and volume are 1). Both classifiers found D02 on the touch / no border (the changed sentence is an acceptance measure, not a
  domain state) and chose touch by the same reading for both models.
- Section 3 expected this by kind: D01 is an order, D02 a measure, D03 an algorithm; D06, the only relation between attributes,
  was copied as written. The one named item came from the model's `questions` (a requirement and the spec disagreeing), not from
  its entities.

Model measures (descriptive, `check_model.py`): A 18 entities, 89 attributes (78 with an initial rule, 42 with a setting
operation), 47 relations, 24 questions; B 16, 88 (76, 41), 42, 18. Both raise the same open point first: whether the `fps` passed
to the edits is the source's or the output's rate.

## 3. Part 2 — the frame rate

| | EXP-20261030-05 A | EXP-20261030-05 B | **this A** | **this B** |
|---|---|---|---|---|
| `SetFps:*` steps | 0 | 0 | **2** (UC-15: `source` → ST-13, `24` → unknown) | **2** (UC-14: `60` from ST-16 → unknown; UC-15: `30` → ST-13) |
| M15 (`SetFps:60` removed) | outside | outside | outside | **caught** (W1 at UC-14#1) |
| caught / outside (a–e, 25) | 23 / 2 | 22 / 3 | 21 / 4 | 23 / 2 |
| agreeing / masked / other | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| f false alarms | 0 | 0 | 0 | 0 |
| coverage pairs / 774; actions / 44 | 50; 35 | 53; 33 | 52; 32 | 54; 34 |
| clean stop flags | 6 (W3) | 7 (W3) | 11 (W1 5, W3 6) | 4 (W3) |

- All four `SetFps` steps are counted (their pair is enabled on the clean mock). Both writers still found no state that shows a
  changed output rate and wrote `unknown` after 24 / 60 (A's report item 3, B's item 1), as EXP-20261030-05's writers said — but this
  time they wrote the step rather than skip it. Each also named the inconsistency with how they treated language and zoom.
- M15 is caught only by a `SetFps:60` step; A chose 24. Against EXP-20261030-05's A, this A's outside set adds M03 (speed 1.5
  not used) and M09.
- Every miss of both writers is placed (other 0); the five a–e classes as before.

## 4. Read after the verdict: the clean flags on the authority (descriptive, not readings)

9 flagged writer scenarios with stage 1's states and setups, executed by stage 1's harness (`verify/certify.json`): 27 of 31
scenarios certify; ST-02 / -03 / -04 / -05 / -08 again ambiguous (undo / redo depend on the history), the same five as
EXP-20261030-05.

- **A, 11 flags:** 4 are the writer's errors on the authority — UC-03#3 (Redo disabled after a new edit), UC-06#0 (`SetTrimIn`
  disabled), UC-08#0 (`Split` disabled; A wrote "refused operations" as pressed buttons, report item 6), UC-20#0 (after "Later" the
  authority holds ST-13, not ST-01 — the error both EXP-20261030-05 writers made); 3 lie after a failed step and were not reached
  (UC-03#4, UC-08#1, #2); **4 are the mock's** (UC-02 ×3, UC-05: the scenarios certify, the states are history-ambiguous).
- **B, 4 flags: all the mock's** (UC-02 ×2, UC-03, UC-07; certify, history-ambiguous).
- No flag falls on a `SetFps` step, and none on a step a placement depends on (agreeing and masked 0). OBS-20261030-07's mechanism
  recurs on the same reference with a second input; its second-case condition asks for another generated reference, so it is not
  counted.

## 5. Limits (section 10, as they bear on this result)

- **Two writers each time, one prompt.** 0 of 2 then and 2 of 2 now differ by the model (and fresh writers); between-writer
  variation is not measured, so the result is "here", not a rate. The frame-rate requirement (REQ-013) and the READMEs were in
  both packages; what changed is that a model attribute stood next to them.
- **The vocabulary is unchanged.** The 27 states have no frame-rate state, and both writers still could not say where `SetFps:24`
  / `:60` leads. The model brought the step in; it did not supply the state the walk would need to check its effect.
- Part 1 is four items, three of kinds a domain model is not built to name; its 0 of 4 says nothing general about domain models.
- The models are an AI's derivations, not a designer's ruled model. One computation-heavy product.

## 6. Departures

None. Added beside section 8 and not a reading: the isolation check (`../exp-20261030-04/isolation.py`) on every agent
transcript, and the package re-hash after the writers.

## 7. Files

`derive-a/`, `derive-b/` (model, `sha256.txt`, report verbatim; A's own `fix_initials.py`), `classify/` (`sha256.txt`,
`verdicts-1.json`, `verdicts-2.json`, reports), `writer/started.txt`, `run-a/`, `run-b/` (`scenarios-written.json`,
`scenarios-frozen.json`, `freeze.json`, `flags.json`, `package-sha256.txt`, report verbatim), `verify/` (`scenarios.json`, `certify.json`). The staging
folder (`exp06/` in the session scratchpad) is kept until the user's word.
