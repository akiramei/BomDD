# EXP-20261031-02 — definitions (fixed before any prompt is written, any agent is started or any folder is built)

Fixed 2026-10-31. A change after this point is a departure (section 12).

## 1. The question, and where it comes from

EXP-20261031-01 (results 2026-10-31) read: given a domain model that lists the output frame rate, fresh writers bring it into the
scenarios (2 of 2; EXP-20261030-05: 0 of 2). By its section 9 the re-manufacture earned a proposal, and the user chose
"A: 起票する" (2026-10-31). The same result left a gap: both writers wrote `unknown` after `SetFps:24` / `SetFps:60`, because the 27
states they were given (stage 1's, read from the authority's view model) have no state that shows a changed output rate. The model
brought the step in; it did not bring the state that would let a walk check the step's effect.

The re-manufacture's two changes against MoviePad-Remake are the ones the user named: **the domain model first, and the screens in
scope.** The screens are where a value becomes a visible state. So the question of this experiment's first stage is:

**When the upstream is written in the order requirements → domain model → screens → use case scenarios → spec, by fresh authors,
does every attribute the model says can be set reach a scenario step whose expected state shows its new value — the output frame
rate in particular — and how many of the scenarios execute as written on the authority?**

Relation to the open entries:
- **EXP-20261024-01** (MoviePad-Remake, open) is the earlier re-manufacture: core and export only, no screens, no domain model,
  upstream written by the designer (this session). Its charter calls the screens "a later trial step". This experiment does not
  extend that product: MoviePad-Remake is read only (`git show`), and its records stay as they are. Its isolation measure (M4: what
  the agents read outside their package) is reused here (section 5).
- **EXP-20261031-01** (open until this filing) supplies the trigger and the domain-model form (`check_model.py`), which is reused.

This is a measurement. It changes no method text, template, tool or product. Nothing is written into MoviePad or
MoviePad-Remake.

## 2. Two stages; only stage A is filed

- **Stage A (this filing): the upstream only.** Five artefacts, each written by a fresh author and audited by a fresh auditor
  (section 4), then measured (section 7). No E-BOM, K-BOM, M-BOM, work order or code. It stops at its reading (section 9).
- **Stage B (not filed): E-BOM to manufacture**, from stage A's upstream. It earns a proposal only by section 9; its design (the
  product repository, the CAD repository the screens need, the factory) and its start are the user's.

Why staged: MoviePad-Remake's whole forward run took about 5 days and 104 commits; its upstream (G0 to G2) took about 6 hours
(2026-10-24 14:07 to 20:04). Stage A is the part the question is about, and the cheaper part (measure the cheapest first).

## 3. Proposed defaults (the user's at the start; any can be changed then)

| item | proposed default | what it trades |
|---|---|---|
| authority | MoviePad **`126eae9`**, as MoviePad-Remake (manual, its own `bomdd/` records, source, behaviour; behaviour wins) | the same source as MoviePad-Remake, so stage A's repairs can be compared with MoviePad-Remake's |
| scope of stage A | MoviePad-Remake's REQ scope (editing core, output settings, export) **plus every screen at `126eae9`**: MainWindow, TitleBar, Toolbar, Timeline, Inspector, Preview, Transport, ExportDialog, AboutDialog | the preview's video rendering and playback timing are out (perceptual; nothing can execute them); what the preview shows as values (position, duration, playing or not) is in |
| place | this folder (`bomdd/reports/exp-20261031-02/`) for the artefacts and the records; staging folders in the session scratchpad; **no product repository until stage B** | no kit gate machinery (process-core, hooks) runs in stage A; the gates are this experiment's audits with the kit's G1 / G2 questions (section 4) |
| record language | English | — |
| GitHub | none (MoviePad-Remake's decision, 2026-10-26: the lessons are the deliverable) | — |

## 4. Who writes the upstream, and how it is audited

**The authors are fresh agents, not this session.** This session (the operator) has read every repair made to MoviePad-Remake's
upstream (EXP-20261031-01 section 3) and knows that the output frame rate is the answer of section 9. If it wrote the artefacts,
the reading would be written by someone who knows it. So:

- Each artefact S1–S5 (below) is written by **one fresh Claude agent** (an author), in its own staging folder holding only what the
  table gives it and its prompt. Bound 60 minutes per run; the operator checks the folder's newest modification time every 15
  minutes and stops a run that has written nothing for 30 minutes (reported, not retried silently).
- Each artefact is then read by **one fresh auditor** (a new agent per round) with the questions in the table, which reports
  findings with a severity (blocker / material / minor). The author (continued with its own context) answers every finding. Up to
  **3 audit rounds** per artefact (MoviePad-Remake's budget). The operator relays findings **verbatim** and does not edit an
  artefact; the only text the operator writes into an artefact folder is the prompt.
- **Unconverged at the budget** (a blocker or material finding still open after round 3): stage A stops at that artefact and the
  user decides (cut off, extend, or stop). It is not reported as converged.
- Each artefact is frozen by SHA-256 when its audit closes; the next author gets the frozen bytes.

| step | artefact | the author is given | the auditor asks |
|---|---|---|---|
| S1 | `10-requirements.yaml` (the kit's template 10) | the authority archive; the scope of section 3 | the kit's G1: each requirement derived from the authority with its source; scope complete; counterexamples |
| S2 | `domain-model.json` (EXP-20261031-01's form, `check_model.py`) | S1; the authority archive | the form passes; every attribute has an initial rule and its setting operations, or a question; every requirement's nouns are placed |
| S3 | `screens.json` (section 6) | S1, S2; the authority archive | every screen of section 3 present; every element's displayed attributes and invoked operation exist in S2; what the authority shows and S3 does not |
| S4 | `scenarios.json` (section 6) | S1, S2, S3; the authority archive | every requirement has a scenario; every step's element and operation exist in S3 / S2; each expected state is reachable as written |
| S5 | `20-spec.md` (the kit's template 20) | S1–S4; the authority archive | the kit's G2: every requirement specified and measurable; the spec agrees with S2–S4 |

The prompts (written at run step 1, committed before any agent starts) may say what the artefact is, its form, the scope of
section 3 and the authority's precedence. They **do not** name the output frame rate, export settings in particular, any defect or
repair of MoviePad-Remake, the measures of section 7, or this experiment's question.

## 5. Isolation (MoviePad-Remake's M4, reused)

Every agent's transcript is read by `../exp-20261030-04/isolation.py`: a read or a command touching a path outside its own staging
folder is a flag. Named especially: MoviePad-Remake, BomDD (this repository), the authority's checkout (the agents get a
`git archive` copy, not the checkout), and the other staging folders. Flags are reported per agent with the path; a flagged
artefact is kept and marked, not re-made silently.

## 6. The linking form (the counting rule depends on it)

The keys below are what section 7 counts. The authors may add fields; they may not rename these.

- **Attribute key** = `Entity.attribute` from `domain-model.json`. An attribute is **settable** when its `set_by` is not empty.
- `screens.json`:
  `{"screens": [{"id": "SCR-…", "name", "authority_view", "elements": [{"id": "EL-…", "kind": "display"|"input"|"command",
  "shows": [<attribute key>], "invokes": <operation>|null, "param": <value>|null, "enabled_when": <text>}]}]}`
- `scenarios.json`:
  `{"states": [{"id": "ST-…", "screen": "SCR-…", "shows": {<attribute key>: <literal value>|"unknown"}}],
  "scenarios": [{"id": "UC-…", "title", "requirement": ["REQ-…"], "flow": "main"|"alternate",
  "steps": [{"in": "ST-…", "element": "EL-…", "operation": <operation>, "param": <value>|null, "expect": "ST-…"|"unknown"}]}]}`
- Operations are the names in the model's `set_by` lists (and any further operations the model lists); `operation` of a step must
  be one of them.

A form checker (`check_upstream.py`, written at run step 1 with a selftest of known-good and per-rule broken fixtures, run on the
first real artefact before it is relied on) reports form errors; an author fixes its own form errors within its run.

## 7. Measures

**A1 — the chain, per settable attribute (machine, `check_upstream.py`).** For a settable attribute X with setting operations O:
- **L1 displayed:** some element of `screens.json` has X in `shows`.
- **L2 stated:** some state of `scenarios.json` has X in `shows`.
- **L3 set:** some step has `operation` in O.
- **L4 checked:** some step with `operation` in O has an `expect` state whose `shows[X]` is a literal value (not `"unknown"`).

Reported: n settable attributes; per link the count holding; **k = attributes with all four links**; the rows. **The frame-rate
row** is the attribute that EXP-20261031-01's `output_frame_rate` rule selects (the output frame rate), confirmed by hand.
Besides: steps whose `expect` is `unknown`, of all steps (EXP-20261031-01's writers: both wrote `unknown` after a frame-rate step).

**A2 — the scenarios on the authority (descriptive).** A fresh **binder** agent, given S3, S4, the authority archive and the view
model paths that stage 1's harness lists (`harness extract`), writes for each state a predicate over the authority's view model
and for each step an action id, in stage 1's scenario schema (EXP-20261030-04 section 3). Stage 1's harness (`build_harness.py`
from this repository and a `git archive` of `126eae9`; its I/O read first; `SwitchLanguage` kept on the no-execute list; MoviePad's
`settings.json` modification time recorded before and after) certifies them. Reported: states bound / all; steps certified / all;
each failure read by hand **after** the counts into the upstream's error, the binder's error, or history-ambiguous (OBS-20261030-07).
Read after, not a reading.

**A3 — MoviePad-Remake's repairs, again (descriptive).** For the four countable items of EXP-20261031-01 (D01 error order, D02
acceptance audio measure, D03 keyframe lookup window, D06 silent-source copy eligibility), two fresh classifiers each read S2, S4
and S5 with the item's before- and after-texts and say: **after** (stage A states the repaired behaviour), **before** (it states
the pre-fix text), **question** (it raises the point as open), **absent**. Counted only when both agree; a split is reported.
MoviePad-Remake's spec at `22e2213` is **before** on all four by construction.

**A4 — cost (descriptive).** Wall time per step, agent runs, audit rounds and findings per round, operator interventions.
Against MoviePad-Remake's upstream (6 hours, 4 commits, no model, no screens): not a like-for-like comparison.

## 8. Order of the run (each step before the next)

1. Write and commit: the prompts (authors, auditors, binder, classifiers), `check_upstream.py` with its selftest (PASS), and
   `prepare.py` (builds each staging folder and records its hashes). Prompt check against section 4's exclusions, by `grep` for the
   excluded words, recorded.
2. S1 → S5 in order, each: folder built and hashed; author run; form check; audit rounds; frozen.
3. `check_upstream.py` on the frozen S2–S4: A1.
4. Binder folder; binder run; harness built and run: A2.
5. Classifier folder; two classifiers: A3.
6. Isolation on every transcript; A4 from the run log.
7. Results written, then read by section 9.

The staging folders are outside every repository and are deleted on the user's word.

## 9. Reading (fixed now)

**The frame-rate row (the question of section 1):**
- **L1–L4 all hold** → "with the domain model first and the screens in scope, the output frame rate reaches a checked scenario
  state (here)".
- **L1–L3 hold, L4 does not** → "the screens did not supply the checked state; EXP-20261031-01's gap is not closed by putting the
  screens in scope".
- **L1 or L3 fails** → reported as the link that broke (a regression against EXP-20261031-01, whose writers wrote the step); no
  claim about the screens.

**k of n** is reported with the rows; no threshold is set (there is no baseline: MoviePad-Remake has no model, no screens and no
scenarios). A2, A3 and A4 are descriptive.

**Stage B earns a proposal** when the frame-rate row holds all four links **and** A2 ran (the binder bound the states and the
harness executed the scenarios), so that stage B would manufacture from an upstream that has been executed against the authority.
Otherwise stage B is not proposed on this evidence, and the report names what is missing. A2's failures, A3's counts and k of n go
into the proposal's design if there is one. Stage B's design and start are the user's either way.

## 10. Stops

- An artefact unconverged at 3 audit rounds (section 4).
- An author or binder run that fails its bound or goes silent (section 4).
- A form error the author cannot clear within its run.
- Stage A not finished within **2 days** of its start: stopped and reported where it is.
Each stop goes to the user; none is extended by the operator.

## 11. Limits (declared now)

- **The operator knows the answer** and writes the prompts, relays the audits and runs the counts. The authors, auditors, binder
  and classifiers are fresh; the prompts are checked against section 4's exclusions; the operator does not edit artefacts. The
  operator's choice of the screen scope (section 3) puts the export dialog, which shows the frame rate, in scope — the user's
  stated design, not a test of whether an author would choose it.
- **The authority is given whole**, as in MoviePad-Remake: its views show the frame rate, so L1 is expected to hold. The question is
  L4, which EXP-20261031-01 measured as failing for a fixed vocabulary.
- **Different authors.** A3 compares fresh authors with a domain model and screens against MoviePad-Remake's spec, written by this
  session without them. A difference cannot be given to the model or the screens alone.
- **One author per artefact**, one product (computation-heavy; product-repo representativeness). No rate; "here".
- **A2's binding is an AI's.** A failure may be the upstream's or the binder's; the split is read by hand after the counts. The
  harness executes the view model and the views' bindings, not rendering or I/O.
- The model is an AI's derivation audited by an AI, not a designer's ruled model.

## 12. Departures

1. **S1 frozen by the user's cut-off, not by convergence** (user: "A: 打ち切って進む", 2026-10-31). S1 stopped unconverged at
   section 4's budget (blocker / material 0 / 10, 0 / 3, 1 / 7). The author answers round 3 and the result is frozen without a
   re-audit; the round-3 blocker (REQ-058 / REQ-060, whether pressing the speed or volume slider records an undo step) is carried
   as an open question. The S2–S5 prompts, committed before any agent started, call the requirements "監査を通ったもの"; they are
   not reworded — the frozen S1 is audited up to its round-2 answers, and its round-3 answers are not.
2. **The tools in the agents' folders named what is measured** (found 2026-10-31 at S2; the operator's error at step 1).
   Section 4 keeps the measured words out of the author and auditor prompts, but `check_model.py` (its `FPS` / `OUTPUT` rule
   and the `output_frame_rate` count, printed by `check_upstream.py model`) and `check_upstream.py` (its docstring naming this
   experiment, the `chain` command and the frame-rate rows) were copied into every folder unchanged. The first S2 author read
   the rule, reworded three descriptions and dropped a quoted note so that the rule would select one attribute, and said so in
   its report. **Repair** (an instrument repair: sections 7 and 9 are unchanged): authors and auditors get `blind/check_model.py`
   and `blind/check_upstream.py` — the same file names and commands, the same form checks, no frame-rate rule, no `chain`,
   neutral selftest fixtures — and the full tools stay with the operator for A1. `equiv_blind.py` shows the two pairs give the
   same ERROR lists on the leaked S2 model and 26 broken copies of it and of a screens / scenarios fixture (27 of 27, every
   broken arm caught; a blind copy with one check removed fails it), and the same counts apart from the frame-rate key.
   `prepare.py prompt-check` now holds the blind tools to the excluded-word rule of the prompts, with the full tools as its
   positive control. The leaked S2 draft is kept as `s2/draft-leaked.json` and is not audited or used; S2 restarts with a fresh
   author. **S1 is not redone:** all four S1 agents saw the tools' source (the auditors of rounds 1 and 2 the rule itself), no
   S1 finding singles out the output frame rate as something examined, and S1's frame-rate content (REQ-001, 020, 056, 070, 071,
   077, 078, 085–087) is the product's own; the exposure is a limit of S1, recorded in the run log.
3. **A standing cut-off for S2–S5** (user: "B: 以後も打ち切り", 2026-10-31, on S2's stop at 0 / 6, 0 / 1, 0 / 3). S2 is frozen
   as S1 was (the author answers round 3, no re-audit). From S3 on, a step that reaches section 4's budget with a material
   finding open is cut off the same way without returning to the user; a step that reaches it with a **blocker** open still
   stops and returns (a blocker may change what A1 can count). Each cut-off is recorded in the run log with its counts.

## 13. Files

`definitions.md`. Written at run step 1: the prompts, `check_upstream.py`, `prepare.py`. Written by the run: `s1/` … `s5/` (the
frozen artefact, its hashes, the author's report and every audit round verbatim), `a1.json`, `bind/`, `verify/`, `classify/`,
`run-log.md`, `results.md`.
