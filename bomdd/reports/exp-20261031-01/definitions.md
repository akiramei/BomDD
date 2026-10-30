# EXP-20261031-01 — definitions (fixed before any model is derived or any writer is started)

Fixed 2026-10-31. A change after this point is a departure (section 11).

## 1. The question, and a correction made before filing

The user's question (2026-10-30, after EXP-20261030-05): in ICONIX the static side is a **domain model** — an entity such as
the video has attributes (length, size, frame rate) and a boundary displays them. Was no domain model made in this work, and is
that why the frame rate was missed? The user chose "A": a desk measurement first, whose reading decides whether a re-manufacture
of MoviePad with the domain model first and the screens in scope earns a proposal.

**Corrected while orienting, before this filing:** the frame rate was not missing from the upstream. MoviePad-Remake's REQ-013
says the output frame rate starts at the source rate and can be set to 24, 30, 60 or 120, and spec §2.5 has `fps = source fps` and
`SetFps(f)`. EXP-20261030-05's writers were given that requirements file and still wrote no frame-rate step ("no state shows it",
in both reports). The omission was in the step from the upstream to the scenarios, not in the upstream. So the question splits:

- **Part 1 (the desk count).** Would a domain model derived from MoviePad-Remake's upstream **as it stood before manufacture** have
  named the defects that were repaired in that upstream later? Section 3 says why there are only four countable items.
- **Part 2 (the frame rate).** Given the same package as EXP-20261030-05 plus such a domain model, do fresh writers write a
  frame-rate step? This is the direct test of the user's hypothesis that a model attribute is what puts the frame rate in view.

This is a measurement. It changes no method text, template, tool or product. Nothing is written into MoviePad or MoviePad-Remake;
both are read by `git show` or `git diff` only.

## 2. The pin

MoviePad-Remake **`22e2213`** (G2 passed; before the E-BOM `6e81322`, the K-BOM `255e6de` and any work order or manufacture).
The deriver is given `bomdd/10-requirements.yaml` and `bomdd/20-spec.md` at this commit, and nothing else.

- Requirements: the last statement change is `bb79898` (before the pin); the only later change, `24cc6ed`, replaces the
  authority's local path with an environment variable name.
- The E-BOM, K-BOM, M-BOM and Control Plan are not given: they are downstream of the step a domain model stands in, and they
  record the repairs.

## 3. The items (`items.py`, `items.json`)

`items.py` lists every commit in `22e2213..a2ca41e` that touches a ruled file (10, 20, 30, 31) and places each one; it stops on a
commit it cannot place. Repairs (their commits say "repaired" or are an ECO's correction): `bbce170` (G3 round 1, spec), `0522643`
(G3 round 2, K-BOM), `b06a5bf` (ECO-003, spec), `ec6e549` (ECO-003, K-BOM). Not repairs: `6e81322` and `255e6de` (the E-BOM's and
K-BOM's first text), `24cc6ed` (a path name), `0b50020` (Control Plan references only), `31273e7` (ECO-005, the user's re-ruled
E-BOM boundary; EXP-20261030-01 classed it a feature with both classifiers). Each repair's diff hunk (3 lines of context) is one
item: **7 items**.

| item | file | what was repaired | in the deriver's input |
|---|---|---|---|
| D01 | spec §2.6 REQ-018 | the export error order: ffmpeg unavailability moved from 2nd to 4th ("only a trial run could decide") | yes |
| D02 | spec §2.7 acceptance | audio compared by decoded content, not by `framemd5` over packets | yes |
| D03 | spec §2.9 copy start | the keyframe lookup's window and answer rule | yes |
| D04 | K-BOM filters | the `fps=` filter rule without a clock plan | no |
| D05 | K-BOM toolchain | Windows x64 host; NuGet reachable | no |
| D06 | spec §2.9 eligibility | a volume change does not make a silent source ineligible for copy | yes |
| D07 | K-BOM progress | 1.0 is reported twice, not once | no |

`items.py` checks that every input item's before-text stands in the pinned file (it does for D01, D02, D03, D06): the defect is in
the input before the run (OBS-20261030-04). **Four items are countable** (D01, D02, D03, D06); D04, D05 and D07 are outside the
input and are reported as such, not classified.

**Not counted: the 19 G2 audit topics** that EXP-20261030-01 used. Their finding texts are not kept, and the spec's first commit
(`bb79898`) already carries every fix, so there is no text before the fix to derive from; a model derived from the pinned spec
would be credited with fixes it was given. EXP-20261030-01 classed those topics values, orders, tolerances and formats (N for both
classifiers, 1 of 20 structural); a domain model lists entities, attributes, relations and defaults, so the expected count on that
set would be near 0 by the same reasoning — stated here so that it is not discovered afterwards.

The same holds for the four countable items by kind: D01 is an order, D02 an acceptance measure, D03 an algorithm. D06 is the only
one whose subject is a relation between attributes (the source's audio and the copy eligibility).

## 4. Part 1 — derivation

- **Two derivers** (fresh Claude agents, A and B), started together with the same prompt (`deriver/prompt.md`), each in its own
  folder built by `prepare.py derive <out>` outside every repository: the two pinned texts, `check_model.py` and the prompt.
  Bound 60 minutes each. The prompt does not mention the frame rate, export settings, defects, repairs or this experiment.
- The model's form (`check_model.py`): entities with attributes (name, description, type, initial, set_by, source) and relations,
  and `questions` for what the texts do not settle; every cited `REQ-` / `SPEC-` / `INV-` id must exist in the given texts. A
  deriver fixes its own `ERROR` lines; a model still failing at the bound is reported and not used.
- Each model is frozen by SHA-256 at the end of its deriver's run.

## 5. Part 1 — naming (the four countable items)

Two **classifiers** (fresh Claude agents), each given both models, the four items' before- and after-texts and the pinned texts
(`prepare.py classify`), and the rule in `classifier/prompt.md`, for every (model, item):

- **named** — the model has a question whose subject is the very point the repair changed, or the model states an attribute,
  default, relation or operation differently from the before-text and as the after-text does;
- **touch** — not named, but the model lists the attribute, entity or operation that the changed sentence is about;
- **no** — neither.

An item is **named by a model** when both classifiers say named; a split is reported as a split. Near is not named.

## 6. Part 1 — measures and the precondition (machine, `check_model.py`)

Per model: entities, attributes, relations, questions; attributes with an initial rule (not `unknown`), with a setting operation,
citing a requirement, citing the spec. These are descriptive. A "displayed by" link is not measured: the pinned upstream has no
screens (MoviePad-Remake's first scope), so that column would be 0 by construction.

**Precondition P (for part 2):** the model lists the **output** frame rate — an attribute whose name or description matches
`fps|frame.?rate|フレームレート` and whose entity, description or setting operations mention output or `SetFps` (`counts()`,
`output_frame_rate`). Confirmed by hand as well.

## 7. Part 2 — writers with the domain model

- Two **writers** (fresh Claude agents, A and B), started together. Writer A gets model A, writer B model B (so the two derivations'
  differences reach part 2). Each folder is built by `prepare.py write <out> <model>`: EXP-20261030-05's package (`prepare.py
  package` there: the 27 states, 45 action rows, the two READMEs at MoviePad `126eae9`, MoviePad-Remake's requirements at
  `a2ca41e`), its `check_schema.py`, the model as `domain-model.json`, and the prompt.
- **The prompt is EXP-20261030-05's with one line added** (the file list names `domain-model.json`); `prepare.py prompt-diff`
  checks that the difference is exactly that line, and `write` refuses otherwise.
- After the run: EXP-20261030-05's `compare.py` (freeze, clean, run) on stage 1's clean mock and 31 mutants, as filed there, and
  its `verify_on_authority.py` on the flagged scenarios (stage 1's harness executes them on the authority's view model;
  `SwitchLanguage` stays on the harness's no-execute list, OBS-20261030-06).
- Part 2 runs only if P holds for both models. If P fails for a model, part 2 is not run with it and that is reported (the
  derivation itself dropped the attribute).

## 8. Order of the run (each step before the next)

1. `python items.py` (the window closed, 7 items, before-texts in the pin); `python check_model.py selftest` PASS;
   `python prepare.py prompt-diff` PASS.
2. Part 1: two deriver folders, hashes recorded; the derivers started together; form check; frozen.
3. P on each model (machine and by hand).
4. Part 1 naming: the classifier folder, hashes recorded; two classifiers; per (model, item) verdicts compared.
5. Part 2 (if P holds): two writer folders, hashes recorded; the writers started together; frozen; walked; flagged scenarios
   executed on the authority.
6. Results written, then read by section 9.

The staging folders are outside every repository (the session's scratchpad) and are deleted on the user's word.

## 9. Reading (fixed now)

**Part 1 (descriptive; no rate).** Four items: each is reported as named / touch / no per model, with the classifiers' splits.
Four items give no rate and the reading makes no claim from part 1 alone, except as the second trigger below.

**Part 2 (the frame rate).** The count is of writers who write at least one step whose action is a `SetFps:*` row (EXP-20261030-05:
0 of 2).
- **2 of 2** → "given a domain model that lists the output frame rate, fresh writers bring it into the scenarios (here)".
- **0 of 2** → "a domain model that lists the attribute did not bring it in; the skipping in EXP-20261030-05 is not explained by
  the missing domain model".
- **1 of 2** → no claim.
- Measured besides: M15 (`SetFps:60` removed) caught or outside; the categories of EXP-20261030-05 §6 (other must be 0, f false
  alarms 0 — otherwise the walk itself is in question and that is reported first); coverage; the writers' own "could not settle"
  lists; clean flags executed on the authority (writer's error or the mock's).

**The re-manufacture (the user's next stage) earns a proposal** when part 2 reads 2 of 2, or when at least 2 of the 4 countable
items are named by both models. Otherwise it is not proposed on this evidence. Its design and start are the user's either way.

## 10. Limits (declared now)

- **Experimenter contamination.** I know that the output frame rate is the answer of part 2 and I have read every repair. The
  derivers, classifiers and writers are fresh agents given only the pinned or packaged files; the prompts do not name the frame
  rate, the repairs or the experiment. The classifier rule is fixed before any model exists.
- **Four countable items**, three of them orders, measures or algorithms, which a domain model is not built to name (section 3).
  The G2 topics are not countable at all. Part 1 cannot show that a domain model is useless or useful in general.
- **One product, computation-heavy** (MoviePad-Remake is not representative of a general application; product-repo
  representativeness), two derivers, two classifiers, two writers. No rate.
- The model is an AI's derivation, not a designer's ruled domain model; a designer's would be reviewed and kept.
- Part 2's writers get the model and the old package together; a frame-rate step can come from the model, from REQ-013 or the
  READMEs (all present in EXP-20261030-05 as well) — the difference against EXP-20261030-05 is the model alone, with fresh writers
  (two from one prompt each time; between-writer variation is not measured).
- The walk's states have no frame-rate state; a frame-rate step must still be written in the 27 states' terms (EXP-20261030-05's
  writers said "no state shows it"). Part 2 measures whether the model changes that choice, not whether the vocabulary allows it.

## 11. Departures

None yet.

## 12. Files

`definitions.md`, `items.py`, `items.json`, `check_model.py`, `prepare.py`, `deriver/prompt.md`, `classifier/prompt.md`,
`writer/prompt.md`. Written by the run: `derive-a/`, `derive-b/` (model, hashes, report), `classify/`, `run-a/`, `run-b/`,
`results.md`.
