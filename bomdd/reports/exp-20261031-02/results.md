# EXP-20261031-02 — results (stage A)

Written 2026-10-31 after every measure ran. Read by `definitions.md` section 9. Every number below is in `run-log.md` with the
file it comes from. **EXP-20261031-02 stays open**: the reading of the frame-rate row is left to the user (the last section).

## 1. What ran

Stage A wrote the upstream in the order of section 1, each artefact by one fresh author and up to 3 fresh audits:

| Step | Artefact (frozen) | Audit rounds, blocker / material | End |
|---|---|---|---|
| S1 | `s1/10-requirements.yaml` `24964b9d…` — 95 requirements, 18 open questions | 0/10, 0/3, 1/7 | cut off on the user's "A: 打ち切って進む" |
| S2 | `s2/domain-model.json` `b758d626…` — 25 entities, 217 attributes, 92 settable | 0/6, 0/1, 0/3 | cut off on the user's "B: 以後も打ち切り" |
| S3 | `s3/screens.json` `f46ef7cb…` — 12 screens, 175 elements | 0/1, 0/1, 0/0 | converged at round 3 |
| S4 | `s4/scenarios.json` `ef416e68…` — 221 states, 151 scenarios, 206 steps | 1/3, 0/3, 0/2 | cut off under departure 3 |
| S5 | `s5/20-spec.md` `1043076f…` — 25 spec ids, 33 open items, none blocker | 0/3, 0/10, 0/2 | cut off under departure 3 |

Every step that was cut off is frozen with its author's answers to the last round, which no auditor read (section 6). Four
departures (definitions section 12): S1 frozen by the cut-off; the agents' tools named what is measured, repaired with blind
tools before S2 restarted; the standing cut-off for S2–S5; the binder's folder lacked the setup op's form, repaired before A2
counted.

## 2. A1 — the chain

On the frozen S2–S4 (`a1/chain-frozen.json` `9b46e887…`): **k = 39 of 92 settable attributes hold all four links** (L1
displayed 53, L2 stated 42, L3 set 84, L4 checked 41); 206 steps, 1 with `expect` `"unknown"`. On the last audited S4 draft the
same 92 rows, link for link (`a1/chain-s4-draft-r3.json`).

**The frame-rate row.** The `output_frame_rate` rule selects 7 attributes; 2 are settable and so are rows. Confirmed by hand,
the frame-rate row is `OutputSettings.outputFps`: **L1 false, L2 false, L3 true (20 setting steps), L4 false.**

**By hand, after the counts.** The model states the frame rate as one settable value (`outputFps`) and five derived attributes
without a setting operation of their own (`set_by: []`): the export summary's "{n} fps" text, the preset shown selected,
whether Source is selected, whether the duplicate-frames note shows, Source's tooltip. The screens show only the derived
ones (the five preset buttons, the note, the summary) and the states state only them (four of them in 53 states, the text in
20). Of the 6 `SetFps` steps, 5 expect a state with literal derived values (UC-109 60 then Source, UC-111 24, UC-113 120 then
30); UC-110's expect states none. This decomposition is in every S2 draft from the first; no screens or scenarios draft ever
shows or states `outputFps`. It is the model's form, not the unaudited edits.

**Read by section 9 as fixed:** L1 fails, so the row is "reported as the link that broke (a regression against
EXP-20261031-01, whose writers wrote the step); no claim about the screens". The link that broke is L1 (and L2): the settable
value is never displayed or stated; its derived values are. L3 holds — the step is written, as in EXP-20261031-01. **Stage B
does not earn a proposal on this reading** (the frame-rate row does not hold all four links).

## 3. A2 — the scenarios on the authority

Stage 1's harness, unchanged, built against `126eae9` (selftest PASS; `extract` byte-equal to stage 1's bindings). MoviePad's
`settings.json` was 2026-10-30 21:24:07.3149497 before and after every run.

- **The binder** (a fresh one after departure 4) wrote 221 of 221 states with a predicate (937 state-attribute values
  unbound) and **56 of 151 scenarios** — a scenario with any step it could not bind is left out whole (116 of 206 steps
  unbound: operations with no command binding, view-only and double values, key steps).
- **Certified on the authority** (`bind/run1/`): **16 of 56 scenarios certified; kept 0** (all 16 touch a state the harness
  finds ambiguous, stage 1's D2); 17 of 206 steps pass.
- **The failures, read by hand after the counts** (`bind/diag1/`): of the 35 scenarios failing at their start, **27 fail only
  on localized strings**, 5 on localized strings and others, 3 only on others. The 8 with other keys are exactly the binder's
  own list of starts setup cannot reach (undo history, an export format object, a `talk.mp4` clip). The localized failures are
  **the environment**, a bin outside section 7's three: the harness builds the view model in the thread's UI culture, `ja-JP`
  on this machine, and the upstream's sample states carry English strings with no stated language premise (S4 names the
  language only in its startup-language scenarios).
- **Sensitivity, not A2: the same run with the UI culture `en`** (`bind/sens-en/`; a launcher sets the culture and calls the
  unchanged harness; with `ja-JP` it reproduces run1 byte for byte). **45 of 56 certified, kept 0**; 58 steps pass. The 11
  failing: the binder's 8 announced starts, UC-052 by construction, UC-202 machine-dependent, UC-194 (an `expect` of
  `"unknown"`, which the binder prompt keeps and the harness does not take). **The frame-rate scenarios UC-109, 110, 111 and
  113 are certified.** Kept is still 0: of 97 ambiguous states, 70 differ in a command's availability whose guard
  (`CanUndo`, `CanSplit`, …) the state does not carry, 19 in `TogglePlay`'s transition with `Playing` not stated. The
  upstream's states are coarser than the authority's availability (OBS-20261030-07's bin).

## 4. A3 — MoviePad-Remake's repairs, again

Two fresh classifiers on S2, S4 and S5 (`classify/verdicts-1.json`, `-2.json`); **they agree on all four**:

| Item | Verdict | MoviePad-Remake `22e2213` |
|---|---|---|
| D01 error order | **after** | before |
| D02 acceptance audio measure | **absent** | before |
| D03 keyframe lookup window | **before** | before |
| D06 silent-source copy eligibility | **after** | before |

Both noted for D01 that stage A orders the checks as after does but describes ffmpeg's absence as an unhandled process
exception, not a named result; and for D03 that the scenarios cannot tell the two windows apart (UC-173's keyframes give the
same answer under both). Descriptive.

## 5. A4 — cost

27 agents (`a4/agents.json`): S1 4, S2 5 (one set aside), S3 4, S4 4, S5 4 plus two helpers its first auditor started itself,
A2 2 binders, A3 2 classifiers; 1,783 tool uses in all. Wall time from a step's first agent to its last: S1 6.4 h (including
the wait for the user's ruling), S2 2.1 h (including the repair and the restart), S3 1.1 h, S4 1.5 h, S5 1.2 h, A2 0.5 h, A3 4
minutes; stage A from the first author to S5's freeze about 12.5 hours. Operator interventions besides relays: the two
instrument repairs (departures 2 and 4), the two rulings asked of the user, stray working files moved into their agents'
folders (S4), one set-aside folder renamed (S2). MoviePad-Remake's upstream took 6 hours and 4 commits with no model and no
screens; not a like-for-like comparison.

## 6. Limits

- **Unaudited text in four of the five artefacts.** Each cut-off froze the author's answers to the last round with no audit
  (S1, S2, S4, S5). S3 converged, but its round-3 answers, also unread, emptied `shows` on 30 elements. A1's numbers do not
  move between S4's last audited draft and the frozen file; the other artefacts were not compared this way.
- **S1's exposure** to the leaked tools (departure 2) stands; S1 was not redone.
- **The harness gives every agent this repository's `CLAUDE.md` and the user's memory index**, which name MoviePad-Remake and the
  experiment ids (no frame-rate word); older than this run.
- **A2 ran on this machine's culture.** The sensitivity shows the culture accounts for 29 of the 40 scenarios that fail on
  `ja-JP`, not for kept = 0.
- The operator wrote the prompts and the bindings' folder and runs the counts, and knows the answer (section 11).

## 7. The reading left to the user

Section 9, as fixed, reads the frame-rate row as broken at L1, so stage B is not proposed. By hand, the frame rate does reach
checked states through the derived attributes its settable value feeds, and its scenarios execute on the authority once the
culture is English. The fixed reading was written for one attribute per value; the model made one value into six attributes.
Whether to keep the fixed reading or to amend it is the user's, on one of two options:

- **A — keep section 9 as fixed.** The frame-rate row is broken at L1; stage B is not proposed on this evidence; the
  decomposition of one value into a settable attribute and derived ones is recorded as a limit of A1's row definition. Cost:
  "the link that broke" names a break that did not happen — the value is displayed and stated, through its derived attributes.
- **B — a departure: read the frame-rate row through the derived attributes its settable value feeds.** L1 (the preset
  buttons, the summary), L2 (53 states), L3 (the `SetFps` steps) and L4 (5 of 6 `SetFps` steps) then hold, A2 ran, so stage B
  earns a proposal (its design and start still the user's). Cost: the fixed reading is changed after the data were seen, which
  is what fixing it beforehand exists to prevent.
