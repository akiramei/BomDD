# Change Order — ECO-126 (a change turned in rounds: the kit gets a route in which manufacture is repeated until the user's acceptance, with what the AI decided on its own counted and stopped where it touched something already confirmed)

> Ruling: user, 2026-11-17, "A: 作る作業に入る" — the answer to "仕組みを作る作業(BomDD への起票と設計)に入ってよいですか".
> The requirement, in the user's words (2026-11-17): 「ミクロループで製造が正しく収束し、マクロループで合格するまで製造が繰り返される、
> また、ループ毎に改善される、という仕組み」. Restated by the producer and not corrected: "in a product built with BomDD, for
> each change, manufacture repairs itself until the checks pass, and is repeated until the user, having used the result, says it
> passes; over successive changes the same stumble stops recurring."
> What was wrong before this filing, in the user's words: 「あなたの作業が終わった＝改善が出来ると認識していました。」 Everything up
> to here was investigation (counts, two trial runs); nothing in the kit or in a product's procedure had changed.
>
> Each part is labelled **stop**, **measure** or **none** (the standing caveat of 2026-10-29). **Filing only.** Manufacture waits for
> the user's start instruction (ECO-106), which also answers section 1, "For the start instruction". Records are English-primary.

## Equipment

- Filing: requested/resolved `claude-fable-5-2`, Claude Code (Claude Agent SDK, desktop app), provenance **self-reported**.
- producer: EQ-006
- inspector: EQ-002
- Independent inspection: **owed for GU7 by equipment of another lineage, read-only** — `ui-cad-gate.py` has been through an
  independent inspection before (ECO-045), and a new check is a change of its inspection semantics (playbook §3, the
  high-risk jig rule, line 340). The inspector is named at the start instruction. For the rest of the diff: one review in a
  fresh context of the same equipment before the acceptance request (context independence). Three instruments are new or
  changed, so a calibrate receipt is owed at verification (activation-map `instrument-change`).

## 0. Measurement (basis of the filing)

Two changes of one product (MoviePad) were turned in rounds under trial rules written outside the kit: ECO-005 (four rounds on a
copy, then taken into the product) and ECO-006 (two rounds in the product). The trial rules are
`bomdd/reports/count-survey-20261110/loop-trial/LOOP-TRIAL-SPEC.md` (not converged; adopted by the user's "始める") and its copy
in the product. The counts below are in `bomdd/reports/count-survey-20261110/loop-trial/eco-005-stage-count/` and
`.../eco-006/stage-count/` (uncommitted at this filing; whether they are committed is the user's word).

- **The inner loop's return from red was taken rarely, and not inside the rounds.** Inside the rounds: repairs 0, 0, 0, 0 in
  the trial (`turns.tsv`) and both rounds of ECO-006 passed their exit checks at the first run; in the trial's second round one
  red seen once in a full run was patched without being reproduced (J36). Outside the rounds, ECO-005's import went from red to
  green twice (the required-case check: FAIL → the cases registered → PASS; the fold after the layout loss: a probe red on three
  missing names → manufactured → green). Where a check and the build disagreed in ECO-006, the check or the sentence moved
  (the prediction T1-P7 was narrowed after the result; the maker rewrote one of its own tests).
- **The outer loop did repeat.** The user's reactions per round: 3, 2, 1, 0 (ECO-005's trial), and one difference then a pass
  (ECO-006). One of the seven was classified by the user ("好みの問題だった"); the other six carry only the producer's classes.
- **Every event whose cause the records tie down lands on the stage that writes what the loop converges to** — the producer's
  own provisional decisions or sentences: R1 (S14), R6 (F4), the layout loss found by the juxtaposition (addendum R8), H3 (R20),
  and the false prediction T1-P7. None lands on a reader's or a maker's item.
- **Listing a decision before use did not prevent the reaction.** R1, R6 and H3 were all in the hand-over text before the user
  used the build. The one the user said could have been settled beforehand is H3, and only as a choice between two roles
  (2026-11-16).
- **Findings were lost at the producer's triage, not at the reader.** For H3, three items had pointed at it; one was handed to
  the user as a report, two were filed under "nothing for the owner to do"; the check item's sentence said the opposite.
- **Three stumbles, counted one by one**: a decision touching something the user had already confirmed was raised as its own
  ruling only after manufacture — twice, both in ECO-006, although its trial rule said before (ECO-005 had raised its one such
  case before, as a blocking entry); nobody could tell which build had run — three times (the trial's third round, ECO-005's
  golden, ECO-006's measurement build); the reply offered had no place to name the reports being accepted — once (ECO-006).
- **What the current kit already allows** (read at `38c482b`): a golden failure returns to step 1 of the same change
  (`skills/eco-fix.md:70`); R4's "two gates" are two kinds, with no limit on how often (`change-management.md:36`); R8's fresh
  read and the naming of known defects exist. **What has no form**: a round used freely with no verdict asked; a reaction that
  is "it passes, but I would change this"; details the user never spoke of, decided by the AI and built — the text says a
  ruling comes first, while the gate stops only `blocking` + `open` (GU3) and an `action` item with no ruled ruling (GU4)
  (`method/tools/ui-cad-gate.py:301-318`; ECO-006 was manufactured with an open, non-blocking bundle and the gate passed).
- **A probe of the proposed check on real ledgers** (read-only, `git show`): before ECO-006's manufacture (`d5dab41`) the open
  bundle UQ-0030 (`screen.main`) overlapped 10 rulings decided by the user, among them UQ-0027 — the earlier bundle that holds
  the two items ECO-006 went on to touch. Before ECO-005's import (`a56afe6`) the bundle UQ-0027 overlapped 9.
- **The lifecycle validator binds transitions, not the number of commits while a change is open** (E01-E13 read in
  `method/templates/process-core/tools/process-validator.py`); candidate commits that leave the status as it is carry no
  trailer rule. E13 (`ruled_layer`, optional) asks a ruling trailer for commits that touch the product's ruled-layer paths —
  read only as far as the rule list; its behaviour on a round's addendum commit is **not verified** (gate V4).

## 1. Change request (frozen at filing)

**L1 — the route (none: text and entry).** `method/templates/product-profile/change-management.md` gains §3.5 "a change turned
in rounds (candidate)": when it applies (the user names it at gate ①, for a change whose fit is judged by use); the stages
(direction → filing with the round limit, the cost frame and the "must never happen" list → rounds → the user's "good" →
confirmation items → acceptance); the complete list of conditions under which a round stops for the human. **Each round's
manufacture is `/eco-fix` steps 1-3.6 as they are** (probe first, machine acceptance, juxtaposition, the fresh read and its
limits) — the route adds no second way to manufacture. The stop of a round is L2.

**L2 — the stop of a round: skill `eco-turn` (none for the text; measured by L5).** New
`method/templates/product-profile/skills/eco-turn.md`, added to `bomdd-init.SKILLS`. It holds: what a hand-over gives (the
build through L6's launcher, how to tell it is this build, what changed in at most five lines, what the machine did and did not
check, the index of decisions); **the reply form with kinds** — passes / passes but I would change something / fails (the aim
is not met) — and a place to name accepted reports in the same reply; the routing of a reaction (a decision changed → the
drawing gets a revision line and the ledger a ruling; a new want → the requirement table with the words; a symptom → a check
from the written sentences: reproduced → repair, not reproduced → an unresolved report, outside → recorded); the conditions
before confirmation items and the conditions of acceptance; the return path. `eco-fix`, `eco-accept`, `eco-file` and
`bomdd-next` each gain one pointer line and are otherwise unchanged.

**L3 — provisional decisions in the rulings ledger (stop).**
- `method/templates/37-ui-rulings.yaml`: a `type: provisional-bundle` entry (open, `blocking: false`) carries
  `confirmed_checked: [{id, touches: yes|no, why}]`; a decision that touches a confirmed ruling is its own entry with
  `touches: <id>`.
- `method/tools/ui-cad-gate.py` **GU7**: for each open provisional bundle, (a) every `ruled` entry with `decided_by: user`
  whose `target.ui_ids` intersect the bundle's must be in `confirmed_checked` with a non-empty `why`; (b) each `touches: yes`
  must have its own entry naming that id. Entries of other types are not read by GU7. **How (b) depends on RP2**: if what
  touches a confirmed ruling is asked first (the recommended answer), that entry must be `blocking: true` while it is open, so
  GU3 holds manufacture until the user rules; if RP2 is answered the other way, (b) accepts a non-blocking entry and the
  decision is made by use, as in ECO-006.
- The rule text (`method/ui-ir-ui-bom.md` §13 and the gate table — lines 323-330, 390 and 401 found by search, the sections
  not yet read; the ledger template's discipline list; §3.5): a provisional bundle may not be the only ruling behind a ui-bom
  `action` item — adding an operable part is never provisional (GU4 already stops it).

**L4 — a read before manufacture that ends in questions (measure; candidate).** In §3.5: before a round's manufacture, a fresh
context reads the round's drawing addendum, the user's words and the list of the user's rulings — not the code, not the
producer's doubts — and returns rows of three kinds: two sentences that cannot both hold / an addition not in the user's words
that has more than one possible role / something that touches a confirmed ruling. The producer disposes of every row:
`asked` (as a choice between two roles; the ruling's id) / `fixed` (the drawing line) / `not asked` (the reason). The rows and
dispositions go to L5's record.

**L5 — the record of rounds and its count (measure).** A sidecar per looped change, `bomdd/loops/eco-NNN.yaml` in the product:
per round the set (commit, jig, sha256 of the named files), the hand-over time, the reply verbatim, L6's log summary; every
decision and finding with its source (producer / maker / reader), disposition and later outcome; every reaction with its kind,
**who assigned the kind** (the user / the producer's reading), its class, what it lands on, and whether that was listed before
use; repairs, checks replaced, re-asks. New `method/tools/loop-count.py`: prints the stage tables (the producer's own decisions
included), the kinds, where causes land, and the repair count; `--check` exits 1 when a reaction has no kind or class, a round
has no set, or an accepted report has no naming reply. `eco-accept` puts its output into the closing section.

**L6 — which build ran (measure).** New `method/tools/handover-stamp.py`: `stamp` writes a manifest (label, sha256 of the named
files) and a launcher beside the build that appends one line (time, label, the main file's sha256 at that moment) to a log and
starts the program; `check` reads the log against the manifest: how many launches, of which set, any mismatch. A start that
bypasses the launcher leaves no line; `check` then says "not launched through the launcher — unknown".

**L7 — the three recurrences, one instrument each.** Touching a confirmed ruling → GU7 (stop). Which build ran → L6
(measure). No place to name → the reply form (none) with L5's `kind_by` and re-ask counts (measure).

**For the start instruction (the user's points).** The recommended set is the first answer of each.
- **RP1 — is a round's free use a third human gate?** *Recommended: no — it is the second kind (the human uses the real thing)
  asked in a second form; R4 stays "two kinds".* Otherwise: R4 is rewritten to three.
- **RP2 — what may the AI decide and build without asking?** *Recommended: everything except five things asked first —
  what cannot be undone (the user's data, a stored format, what leaves the product); what use cannot reveal; an added operable
  part; what touches a ruling the user already confirmed; an addition not in the user's words that has more than one role
  (asked as a choice between two roles).* The first two were in the trial rules of both changes; the third is today's GU4; the
  last two come from ECO-006 and were approved so far only as a trial for the next MoviePad change.
- **RP3 — the kinds of a reply.** *Recommended: the three of L2.* Two are the user's own distinction of 2026-11-16; the middle
  one is the producer's.
- **RP4 — inside a looped change, may a new want join the same change, and may a check written in this change for a
  provisional decision be replaced when the user's reaction changes that decision?** *Recommended: yes to both, on these
  terms: only on a recorded reaction; replaced by the producer, never by the maker; before manufacture, with the red measured;
  rows that existed before this change are never replaced.* Otherwise R3 and R6 apply unchanged and the round stops to ask
  each time.
- **RP5 — the design is not converged in the form** (converge receipt: 9 → 2 → 1 at the limit of three rounds). Building it as
  filed is the user's cut-off; the other answers are another round, or sending the design back.

**Order of manufacture, and what goes first at a limit (the producer's choice; derived layer).** L3 with GU7 → L5 → L1 and L2
→ L4 → L6. If the limit set at the start instruction is reached, L6 is dropped first and then L4; the claim is narrowed to
what was built (R4's default), and the dropped part is named in the closing section.

**Not chosen:**
- **Only widening `eco-fix`'s stop** (no route, no skill): the three missing forms would sit inside the skill that is the inner
  loop, and nothing would count them.
- **A stop in the lifecycle validator** (refuse `applied` without L5's record): `process-core` is what C11 qualifies (105
  controls, about 21 minutes); the first version measures, and a stop there needs a measured miss first.
- **Detecting "touches a confirmed item" by meaning**: closed (the semantic sensor is not a gatekeeper, 2026-09-18). GU7 forces
  the list by the overlap of ids; it does not judge the answers.
- **Asking the user every provisional decision before manufacture**: the list is an index, not a set of questions; the user
  does not know the answer before use (2026-11-12). Only RP2's five are asked.
- **A playbook section**: the route is a product-profile part of the kit; the method text changes only through
  `/lesson-promote` after use.
- **Re-kitting a product**: MoviePad is pinned to the kit of 2026-07-27 and keeps the trial rules; no product is changed here.

## 2. No-impact prediction (before manufacture; frozen)

- **Diff:** the paths of `allowed_paths` in the register entry and nothing else. Nothing under
  `method/templates/process-core/`; nothing in `method/bomdd-playbook-v1.md`; no product repository.
- **Verdicts:** `ui-cad-gate.py` gives the same verdict as the filing tree's on every ledger that has no `provisional-bundle`
  entry (GU1-GU6 unchanged). The full self-conformance prints the same lines apart from the new arms and the skill count.
- **Skills:** `eco-fix` steps 1-3.6, `eco-accept` and `eco-file` behave as before for a change that is not looped; each gains
  one pointer line.

**Declared at filing — what this will not do:**
- **It does not show that the loop helps.** That is known only after a product built with this kit turns a change through it.
- **The inner loop gets no new mechanism.** It is bound to the existing steps, and its repair count becomes visible.
- **GU7 stops the omission, not a wrong "no".** The answers in `confirmed_checked` are the producer's; a bundle typed as
  something else is not read.
- **L4 is a candidate resting on one statement of the user and against one counter-example** (ECO-005's trial had a read before
  manufacture; its findings went to an index and the reaction still came).
- **L5 and L6 measure; nothing refuses a hand-over without them.** A reply given through a one-word button still cannot carry
  names — the form is text.
- **Products without a UI rulings ledger are not covered.**
- **Parts are added and none is removed.** The removal rule is in section 3, "Not gated".

## 3. Acceptance (conditions; frozen at filing)

required_gates: [V1, V2, V3, V4, V5, V6]

**Gated:** V1-V6.

- **V1 — GU7.** Known-bad: a bundle with no list; an overlapping user ruling missing from the list; `touches: yes` with no
  entry of its own — each red for that reason. Known-good: the same ledger completed. On MoviePad's ledger at `d5dab41`
  retyped as a bundle (a scratch copy): red, naming the 10 overlapping rulings; with the list filled and two single entries:
  green. On ledgers with no bundle (MoviePad HEAD; ViewTube HEAD, read-only): the verdict equals the filing tree's gate. The
  arms are in `--selftest` and in C6.
- **V2 — the count.** ECO-006 transcribed into L5's form reproduces the count of 2026-11-17 in the survey folder
  (`eco-006/stage-count/findings.tsv`, sha256 `67861a09…a4dc8315`: rows by source and disposition, 65 rows and 51 subjects;
  the one difference lands on a producer's decision that was listed before use). Known-bad: a reaction
  with no kind, a round with no set, an accepted report with no naming reply — `--check` exits 1 for each; the complete record
  exits 0.
- **V3 — the launcher.** On a harmless program in a scratch folder: a launch writes one line with the manifest's hash; a
  changed file is reported as a mismatch; a start that bypasses the launcher is reported as unknown, not as a pass.
- **V4 — the route on a scaffolded product.** `bomdd-init` into a temporary GUI product: the kit holds `eco-turn`, §3.5 and
  the template's type; the commit sequence of a two-round looped change (filing, the addendum with a bundle, the gate, two
  candidate commits that leave the status, L5's record file written at each hand-over and reply, acceptance with its trailer)
  passes the installed hooks and validator, also with
  `ruled_layer` enabled; C13 resolves the new skill's links; C7's count matches.
- **V5 — the text.** `eco-fix` steps 1-3.6 are byte-identical apart from the pointer line; R3, R4 and R6 differ only as RP1
  and RP4 were answered; the diff under `method/templates/process-core/` is empty.
- **V6 — nothing else moves; the gate.** The diff is inside `allowed_paths`; the full self-conformance exits 0 before each
  push of this ECO; CI is green for each pushed commit (read by the full SHA); no product repository has a change.

**Not gated — measured after application** (a tracking item is filed at verification): on the first three looped changes of
products carrying this kit — reactions by kind and by who assigned it, where tied causes land, GU7 reds, launcher mismatches,
L4 rows asked, repairs. **A part with no hit in three changes is put to the user for removal.**

Conditions are frozen at filing; results go to the closing section.

## /preflight receipt (start path: manual — the user's "A: 作る作業に入る" read as the start artifact)

- **Classification**: filing of a change the user asked to be built (filing and design; manufacture not started).
- **Baseline `38c482b`**: **confirmed** (HEAD). The working tree also holds this session's uncommitted records
  (`method/improvements.md`, `bomdd/reports/count-survey-20261110/`); this filing commits only its own two files.
- **Next number 126**: **confirmed** (the last register entry and the last order are ECO-125).
- **The kit parts named in section 0**: **confirmed** by reading (`change-management.md` R1-R8 and §3, `skills/eco-fix.md`,
  `skills/eco-accept.md`, `skills/eco-file.md` 25-45, `37-ui-rulings.yaml` 1-60, `ui-cad-gate.py` 270-340 and its options,
  `bomdd-init.py` SKILLS, the validator's rule list).
- **Not read**: `skills/bomdd-next.md`, `skills/handoff.md`, the body of the validator's E13, `method/ui-ir-ui-bom.md` beyond
  the lines a search for `ruled` returned — **unknown**, covered by V4 and V5 rather than by reading.
- **No ECO in progress on the same files**: **contradicted** — ECO-079 (`implemented`, its window open from `7e060c92`)
  names `skills/eco-accept.md` and `change-management.md`, two of this ECO's sixteen files. This ECO adds §3.5, the clauses
  RP1 and RP4 decide, and one pointer line in `eco-accept`; it does not touch the acceptance-evidence text ECO-079 wrote. The
  two windows will interleave on those two files and are read apart by commit, not by head.
- **Closed series**: **confirmed** not reopened as to the semantic sensor as gatekeeper, a role decider, enforcement by
  harness permission, ViewTube's gates and `process-core`. **L4 stands on the ground of the closed reader measurements**
  (EXP-20261030-01/02, closed without a conclusion; reopening condition "an upstream defect a reader could have named reaches
  manufacture"). That ECO-006 meets the condition is the producer's reading after the fact (about 16 of 22 findings), not a
  measurement.
- **The producer's equipment**: **confirmed** (EQ-006).
- **Start decision**: **PROCEED_WITH_LIMITS** (filing only; the design is not converged — RP5).

## Converge receipt (the route for a change turned in rounds; 起動経路: self-triggered at filing)

- 判定: 未収束 (round 軌跡: 9 → 2 → 1; the limit of three rounds reached, no round at zero). The ruling asked for is RP5 in
  section 1. The rounds are the producer's own. No manufacture and no change to the kit until the ruling.
- DoD (written before the draft of section 1):
  - ✔ D1 each rule hangs on an event that must happen, or is labelled none;
  - ✘ D2 each rule names a site that was read — true for the kit parts of section 0; **not for `method/ui-ir-ui-bom.md`**
    (lines found by search, sections unread) nor for `bomdd-next` and `handoff`;
  - ✔ D3 each new check has a planned input that turns it red for its own reason (V1-V3);
  - ✔ D4 each new record has an owner and a time of update (L5: the producer, at each hand-over and each reply; GU7's list is
    recomputed against the ledger at every gate run, so a later user ruling turns a stale list red);
  - ✔ D5 one source: the route refers to `eco-fix`'s steps and does not restate them;
  - ✔ D6 impact by file (the register's `allowed_paths`), products none;
  - ✔ D7 each part labelled, with what it does not do;
  - ✔ D8 what changes the human's part is put to the user (RP1-RP4), not decided here;
  - ✔ D9 closed series not reopened; `process-core` untouched;
  - ✘ D10 each of the three parts of the requirement has a stop or a measure — **the inner loop has no new stop**: it is bound
    to the existing ones, and gets one measure (L5's repair count, with reds patched without reproduction counted apart).
    Stated in section 2.
- round 1 (9): (a) the touched items of ECO-006 sat inside a closed bundle, not in rulings of their own → the list is per
  overlapping ruling with a `why`, and the limit is declared; (b) per-round commits against the lifecycle validator → the rule
  list read, V4 added; (c) a new skill moves C7's count and the product entry tables → listed; (d) the sidecar has no stop →
  `--check` and the declared limit; (e) the pre-manufacture reader could be handed the producer's doubts → the brief is named;
  (f) the launcher can be bypassed → "unknown", declared; (g) nothing removes a part → the removal rule; (h) R3 and R6 forbid
  what the trials did → RP4; (i) a product with no UI ledger → declared out.
- round 2 (2 new): (j) ledgers in the field have open non-blocking entries of other types, and a product re-kitted later must
  not turn red → GU7 reads typed bundles only, the evasion declared; (m) "passes but I would change this" may be left as it is
  by the user → the routing has that outcome.
- round 3 (1 new): (n) E13 — a round's addendum commit on a product that enabled `ruled_layer` → not verified by reading;
  V4 runs it.
- Common cause of 5 of the 12 findings (b, c, i, j, n): machinery the route's commits pass through that was not read before
  the draft. The parts still unread are named in the preflight receipt; V4 is the measure for them.
- 未収束事項: the form (no zero round); E13's behaviour on a round's commits; whether L4's rows become questions the user can
  answer. Failure types A①-⑧ checked: ① the validator claim is limited to the rule list and marked; ③ R3/R4/R6 quoted from
  the current text, not from the trial copy; ⑥ GU7 not reading other types is declared and is not a permission; ⑦ five
  alternatives listed; ⑧ this receipt.

## 4. Manufacture (2026-11-17, on the user's "A: この形で着手する")

**The start instruction.** The question put to the user was "ECO-126 を、推しの組のまま、詰め切れていない設計で作り始めてよいですか"; the
answer was "A: この形で着手する". It carries: the recommended answers to **RP1-RP4**; **RP5**, building a design not converged in
the form (9 → 2 → 1) as the user's cut-off; and the inspector of another lineage, named in the question as Codex (EQ-002,
`gpt-5.6-sol`). No limit of time or rounds was named; the producer kept the default of two rounds for each kind of review.

**Where it is first used (the user's word of 2026-11-17, before the start):** 「MoviePadで続けても良いし、ViewTubeと比較して好ましい方を
選んでも良いです。」 The producer compared the two by reading (ViewTube read-only) and chose **MoviePad first, ViewTube second**:
ViewTube does not consume this kit (no `bomdd.lock`; its own procedure, skills and gates; its ledger fails this gate's GU4 on its
own status words), adding a check there needs the user's exception each time (its gate freeze), and its register holds 172
changes not closed; MoviePad takes the parts as built and has two looped changes to compare with, but its kit is 659 commits
behind (`kit-freshness.py`: STALE) and must be replaced first — a MoviePad change of its own, not part of this ECO. **No product
carries this kit yet.**

**What was made** (`da797b7`, against `59b96bb`: 16 files, +1269 -17; nothing under `method/templates/process-core/`).
- **L1** `product-profile/change-management.md`: §3.5 (the route), the clauses of R3, R4 and R6, the scenario row, the commit
  note, the skill row.
- **L2** `product-profile/skills/eco-turn.md` (new), listed in `bomdd-init.SKILLS` (14 skills; README's two counts follow);
  one line each in `eco-fix`, `eco-accept`, `eco-file`, `bomdd-next`, and in the product entry templates (`AGENTS.product.md`,
  `CLAUDE.product.md`).
- **L3** `templates/37-ui-rulings.yaml` (discipline 9, examples 4 and 5); `ui-ir-ui-bom.md` (§13.1 and §15); `tools/ui-cad-gate.py`
  GU7 with 16 self-test arms of its own (19 in all); self-conformance C6c, C6d, C6e.
- **L4** the read before manufacture: in §3.5, with its rows in the record (`kind: preread`).
- **L5** `tools/loop-count.py` (new; the record's format is its header) with 23 self-test arms. **L6** `tools/handover-stamp.py`
  (new) with 11. Both run in self-conformance as C20a and C20b.

**Departures from section 1 (the producer's choices unless marked; section 1 is frozen and not rewritten).**
- The field of a single entry is **`touches_confirmed`**, not `touches: <id>` (the bundle's rows already use `touches`).
- **GU7 does more than (a) and (b)**, after the inspections: the target of `touches_confirmed` must be a ruling decided by the
  user, not itself, with no empty member; while open the entry must be `blocking: true` as a boolean; once ruled it must be ruled
  by the user; one row per ruling; ids are compared as strings; a single entry already ruled by the user is listed like any other
  overlapping ruling (no exemption).
- **The route uses `eco-fix` steps 1-5, not 1-3.6**: the implementation record and the commit of each round are steps 4 and 5;
  only the stop differs (the first review's finding 18).
- **Two rules were added to the route because V4 found them**: a round's commit that changes a ruled-layer file needs the ruling
  trailer and a citation in the order's Sources read (E13); a product with three states needs the `implemented` transition
  before the confirmation items.
- **The launcher's log line carries a stamp id, not the label** (the label stays in the manifest: the launcher scripts are kept
  to ASCII). The started program is stamped too. File names are limited to letters, digits and `. _ - /`.
- **`loop-count --check` checks more than L5's three conditions** (the record's shape, vocabularies, rounds, replies) and, as
  declared in its header, less than its whole format (KD-03). The class `left_as_is` and `limits.budget` were added.
- **Delivered though section 1 did not name them, all inside `allowed_paths`**: the lines in the two product entry templates,
  README's counts, the scenario row, the commit note, the skill row, C20 and C6c-e. The line in `eco-file.md` carries a rule
  (what gate ① asks), not only a pointer.
- **Nothing was dropped at a limit**: L4 and L6 were built.

**The independent inspection of GU7 (EQ-002, another lineage; read-only on a scratch copy).** Two rounds, **both REJECT**.
Round 1: eight findings (IA-01 to IA-08), each reproduced as an arm that was red on the unrepaired tool, then repaired. Round 2
(the last): seven closed, IA-08 not closed, two new (IB-01, introduced by the round-1 repair; IB-02). **After the last round the
producer repaired IB-01, IB-02 and one finding of the fresh-context review, against the default** (which is to leave them as
known defects), on the user's standing instruction of 2026-09-29 that a measured false negative of a gauge is closed first.
**The inspector has not seen that repair** (UR-1 to UR-3). Briefs, reports and the disposition:
`bomdd/reports/eco-126-loop-route/inspection/`.

**How the inspector was started (a departure).** Earlier inspections of this repository were started through `bomdd-run.py`,
which also decides the promotion; here `codex exec -s workspace-write -m gpt-5.6-sol` was started directly on a scratch folder
holding copies of the old and the new tool, the diff and the template, with the brief on standard input and the report as its
last message. No promotion was decided by a tool. A closure of this ECO with the inspector's last verdict at REJECT has no
precedent in this register; the nearest are closures with declared limits on the user's ruling (ECO-119, ECO-125).

**The review in a fresh context of the same equipment (the rest of the diff).** Two rounds. Round 1: 42 findings — 11 on the
two new tools (false passes of `--check` and of the launcher check, tracebacks), 14 on text against tools and text against
text, 11 on the verification scripts, 3 on the record, 3 out of scope. The substance was repaired (both tools were largely
rewritten; the skill and §3.5 were corrected). Round 2 (the last): of round 1's findings 28 closed; 7 not closed; 16 new
(11 substance, 4 evidence, 1 record). **Nothing of substance was repaired after round 2**; four statements that said more than
the tools do were narrowed, and the rest is the list of known defects below. Both rounds, condensed, with every disposition:
`inspection/review-r1-findings.md`, `inspection/review-r2-report.md`.

**Mistakes of the producer during manufacture (declared).**
- V3's first run left a window open: the test program was a script, which `start` keeps open; the run was stopped, the stray
  processes (those naming the scratch folder) were ended, and the test program was made to exit by itself.
- V5's first expectation counted seven added lines in section 2 where there are five; the count in the script was corrected
  after reading the five lines — the text was not changed to fit.
- Both subagents reported that files changed under them while they read: the producer repaired GU7 and the route's text while
  the first review and the first V4 run were in progress. The later rounds ran on a tree that was not edited meanwhile.
- The first full self-conformance run measured the tree before the GU7 repair; the second measured the tree before the last
  four narrowed statements (text and comments). Only the quick tier was run after them.

## 5. Results before the acceptance request (2026-11-17; status `implemented`, not closed)

**Acceptance (the frozen gates of section 3).**
- **V1 result: PASS.** `v1_gu7.py` (9 checks): on MoviePad's ledger at `d5dab41` and at `9d46268` and on ViewTube's at
  `b714c546` the changed gate's output equals the filing tree's (no bundle); the ledger at `d5dab41` retyped as a bundle is red
  on GU7 alone and names the 10 overlapping rulings; with the list filled it is red for the missing single entry, then held by
  GU3 while the two single entries are open and blocking, red when they are not blocking, red when they are ruled but not
  listed, green when ruled and listed. Self-test 19 arms; C6c-e. **A departure in the check itself**: every run declares GU6 as
  not applicable (`--na`), because the current gate withholds its verdict on MoviePad's ledger without it — MoviePad's kit of
  July does not have that rule.
- **V2 result: PASS.** `v2_count.py` (11 checks): ECO-006 transcribed (65 rows, 51 subjects) gives the stage tables of the
  count of 2026-11-17; four mutations of the real record each make `--check` exit 1 with one gap. **Limit**: the rounds, the
  three reactions and the four reports are entered by hand in the script; the lines about them show that the tool reports what
  was entered.
- **V3 result: PASS.** `v3_launcher.py` (5 checks): `launch.cmd` really starts a program and logs one line with the stamp's
  hash; a changed file is a mismatch; a start that bypasses the launcher is "unknown", exit 3; `launch.sh` under Git's `sh`
  starts and logs, and reports a mismatch. A POSIX system was not used.
- **V4 result: PASS on the last tree** (`v4_route.py`, 69 checks, three scaffolds bound to one kit manifest, `409aa6c5b721`). **Its first run
  failed one step**: with `ruled_layer` enabled, a round's commit that changed the requirements file as the route was then
  worded was refused by E13. The route's text was repaired (above) and the script now drives the route as worded, with the
  refusals as controls. Variant C (three states) was added after the review. The script was written by a subagent and run by
  the producer; the producer has not read it through (a search finds no check whose verdict is a constant true; the five
  constant-false ones are its failure branches; the first review found one PASS line that does not depend on the exit code it
  prints). Not run: IQ/OQ on these scaffolds (C11 runs it on
  its own), a return to a round after `implemented` (KD-09), branches and merges, a populated BOM at acceptance.
- **V5 result: PASS.** `v5_text.py` (12 checks): `eco-fix`'s steps are identical character for character; nothing is removed
  from `change-management.md`; section 2 gains five lines; every path of this ECO is inside `allowed_paths`; nothing under
  `process-core`; the playbook unchanged.
- **V6 result: PASS for what was run; two parts owed.** The full self-conformance exited 0 twice on this machine (28 result
  lines each, C11 and C11b included; `full-self-conformance-run2.txt`), the second time before the last four narrowed
  statements; the quick tier exited 0 after them (`quick-self-conformance-final.txt`). **Nothing is pushed**: the full run on the
  committed tree before the push, and CI's conclusion, are owed, and a red there reopens this ECO.

**Known defects and unreviewed repairs (the user names what is accepted; the list with sources is
`inspection/review-r2-report.md`).**
- **KD-01** `loop-count`: a record that is not UTF-8 ends in a traceback (exit 1) instead of `[input]` (exit 2).
- **KD-02** `handover-stamp check`: a malformed manifest or a log that is a directory ends in a traceback with exit 1, the code
  for "another build ran".
- **KD-03** `loop-count --check` does not check six rules its format names; a round with a reply and no reaction row passes.
- **KD-04** `loop-count`: unquoted values that YAML retypes are reported as missing.
- **KD-05** `eco-turn`: the instruction for the launcher check's exit 3 does not fit the record's fields.
- **KD-06** the words for an item's kind, disposition and outcome are explained nowhere in the kit.
- **KD-07** the status note "golden 待ち" is set one step late. **KD-08** two entry texts say less than the route.
- **KD-09** three states: returning from the confirmation items to a round needs `implemented` in `open_states` (read, not run).
- **KD-10** the self-tests of the two new tools cover part of their checks (22 of 47 and 13 of 25 of the reviewer's mutants).
- **KD-11** V4's labels use the names R3 / R4 for what the skill now calls A3 / A4.
- **UR-1 to UR-3** the three GU7 repairs made after the inspector's last round, not seen by the inspector. The producer's own
  check: with each disabled in a copy, the self-test turns exactly its own arm red (`gu7-mutants-output.txt`).

**Out of scope, found on the way (not changed).** `method/onboarding/working-with-ai.md` lists the entry skills without
`/eco-turn` (not in `allowed_paths`). The scaffold puts its ledger at `bomdd/37-ui-rulings.yaml`, where `--ui-dir bomdd/ui` does
not look. GU3 and GU4 do not look at who ruled. ECO-079's window is still open on two of this ECO's files.

**Not shown by any of this.** That the loop helps; that the read before manufacture ends in questions a user can answer; that
sessions use the record and the launcher. These are measured on the first three looped changes of products carrying this kit
(section 3, "Not gated"), and there is no such product yet.

### 較正 receipt (/calibrate self-application - trigger ③: instruments changed; receipt_author_role = producer; three instruments)

- **The claims (one sentence each).** (1) GU7 fails a ledger whose open provisional bundle omits an overlapping ruling decided by
  the user, or leaves a touched one without a blocking entry ruled by the user, and changes nothing for a ledger with no bundle
  and no `touches_confirmed` field. (2) `loop-count` reports the stage tables of a record and its `--check` exits 1 on the gaps
  its header lists. (3) `handover-stamp check` tells a launch of the stamped build from a launch of another, and from no launch.
- **査定した主張と判定** (measurement × evidence):
  - (1) the omission is stopped: **observed / eligible** — 15 known-bad arms, each red for its own reason with no other gate
    red; MoviePad's real ledger retyped (10 rulings named); the inspector's 18 ledgers of round 2 and its seven mutated copies;
    the producer's three mutated copies for the last repairs.
  - (1) no effect without a bundle: **observed / eligible** — output identical on three real ledgers and on the inspector's 14
    cases; **conditionally**, since identity was measured with GU6 declared not applicable.
  - (1) as accepted by an independent inspector: **not eligible** — both verdicts are REJECT, and the last repair is unseen.
  - (2) the stage tables: **observed / eligible for one record** (ECO-006, against the table it was transcribed from).
  - (2) `--check` on gaps: **observed / conditionally eligible** — 22 known-bad arms and four mutations of the real record; the
    reviewer's mutants show 25 of 47 removed checks leave the self-test green, and six rules of the format are not checked.
  - (3): **observed / conditionally eligible** — real starts on Windows and under Git's `sh`; 10 known-bad arms; 12 of 25
    mutants survive the self-test, among them the mismatch dropped from the exit condition (the tool itself returns 1 there).
- **検出した計器欠陥と帰属** (instrument defects found, and attribution): GU7 — IA-01 to IA-08, IB-01, IB-02 and one more
  (the producer's logic; repaired). `loop-count` — review findings 1-4 and 10 (repaired), N1, N3, N4 (left: KD-01, KD-03, KD-04).
  `handover-stamp` — review findings 5-9 and 11 (repaired), N2 (left: KD-02). The verification scripts — V5's wrong count and
  V3's test program (the producer's; corrected before a result was used). No defect is attributed to a product.
- **宣言した検出力の限界** (declared limits of detection): GU7 judges the omission, not the truth of "does not touch"; overlap is
  equality of ids; an untyped bundle is not read. The count shows what was written, not whether it is right. The launcher sees
  only starts through itself. No POSIX system, no product, no user took part. The self-assessment is blind to the producer's
  own wrong premises; the two reviews and the inspection found 68 things the producer had not (10, 42 and 16).
- **Battery, row by row:**
  - **Q1 asked.** Four statements said more than the code measures and were narrowed (the route's sentence on `--check`,
    `ui-ir-ui-bom.md` on when GU7 applies, the skill on exit 0, V5's label); the headers of the two tools list what is not checked.
  - **Q2 asked.** Known-bad and known-good arms in pairs for all three; the labels come from the stated rule, the inspector's
    fixtures and MoviePad's ledger, not from the tools' own output.
  - **Q3 asked.** Each GU7 arm must be red on GU7 alone with its own words; for the two new tools the reviewer's mutants show
    that not every clause falls separately (KD-10).
  - **Q4 asked.** V1 runs on product ledgers read from their repositories; V2 on a record transcribed from a real change; the
    hand-entered part of V2 is declared.
  - **Q5 asked.** The push, CI, a POSIX system and a third inspection are recorded as not measured; the withheld verdict of the
    gate on MoviePad's ledger without `--na` is recorded, not counted as a pass.
  - **Q6 asked.** Each repair followed an observed red; the commit follows observed exits of the quick tier and of V1-V5.
  - **Q7 asked.** C6c-e and C20a-b run the arms on every self-conformance; a tool that is missing is a FAIL there.
  - **Q8 asked.** GU7 is a preventive gate: its way out is the list itself (`touches: no` with a reason), which is counted in the
    ledger; there is no exemption switch.
  - **Q9 asked.** V1 names the commits it read; V4 prints the kit manifest of its scaffolds (the last run: see its output).
  - **Q10 asked.** The limits above and the known defects.
  - **Q11 asked.** GU7 was measured on separate classes: ledgers with no bundle, with a bundle, with single entries open, ruled
    by the user, ruled by another, with malformed fields; the two new tools on well-formed records, records with gaps and
    malformed input, and for the last class the answer is only partly sound (KD-01, KD-02).

## 6. Scoped repair on the user's "B" (2026-11-17; status stays `implemented`, not closed)

**The instruction.** To the acceptance request of section 5 the user answered "B", limited to four items, in these words:

> B。ただし、今回は次の範囲に限定してください。
> 1. GU7 の最後の修正3件について、修正確認と回帰に範囲を絞った独立検査を、通常の結果回収経路で1回行ってください。
> 2. KD-02・03 と、手順どおりに記録・受入できない KD-05〜08 を直してください。KD-10 は、その修正と主要な誤合格を検出する自己テストを補ってください。全変異への対応までは求めません。
> 3. V2 の照合に必要な固定データを証拠に含め、リポジトリから再現できるようにしてください。V4 は、検査対象の終了コードが適切に合否へ反映されていることを確認してください。
> 4. 3状態の製品で周へ戻る経路は、実測するか、今回の適用範囲から明示的に外してください。
>
> 追加確認は、修正箇所と対応する回帰に絞った1回とします。新しい重大な所見が出た場合は、勝手に修正を続けず、残った危険と適用できる範囲を報告してください。
> 最終版の必要な検査結果をそろえて、残る欠陥の受入を改めて提示してください。CI 未確認は未確認として扱い、検証済みの完了には含めないでください。製品への導入は、その後の判断にします。

Not in the list, and therefore left as they were: KD-01, KD-04, the labels of KD-11. Sections 1 to 5 are not rewritten; where
this section says something different, this section is the later one.

**/preflight (continuation; start artifact = the instruction above).** Baseline `acc7c05` **confirmed** (HEAD, nothing pushed;
the working tree also holds `method/improvements.md` and `bomdd/reports/count-survey-20261110/`, not this ECO's, never staged
with it). ECO-126 `implemented` in the register, job stop type NONE: **confirmed** (`bomdd-job.py ECO-126`). Every file to be
changed is in `allowed_paths`: **confirmed**. No ECO in progress on the same files: **contradicted, as at the filing** —
ECO-079's window is open on `change-management.md`; this return changes one sentence there, in the part this ECO added. The
reviewer's mutant lists of round 2: **confirmed** present outside the repository (a temp folder the reviewer left). Start
decision: **PROCEED_WITH_LIMITS** (the four items; one confirmation after; nothing repaired after it).

### 6.1 Item 1 — the three GU7 repairs seen by the inspector: ACCEPT

- **Launched through the operator entry**, before any file of this return was changed: `self-conformance.py --quick` exit 0 →
  `bomdd-witness.py produce --eco ECO-126 --gate self-conformance-quick=0:<log>` (tree `ec6d9fc66939`) →
  `bomdd-run.py ECO-126 --cell "codex exec --skip-git-repo-check -s workspace-write -m gpt-5.6-sol -C <scratch copy> -o
  <repo>/bomdd/reports/eco-126-loop-route/inspection/gu7-inspection-r3-report.md - < %BOMDD_BRIEF%" --executor EQ-002 --brief
  <brief outside the worktree> --report bomdd/reports/eco-126-loop-route/inspection/gu7-inspection-r3-report.md --range
  是正確認+回帰`. First line `ADVANCE ECO-126 OK → next · launching`; `cell exit 0`; `report ACCEPT sha256:0b6f32c24a75 (EQ-002)`.
  The ledger's cell record (run `20261117T113220.557065Z`, `journal_end: committed`) binds the report (`0b6f32c2…879fff73`,
  2738 bytes) with verdict `ACCEPT` and range `是正確認+回帰`. Brief `16bbd2d2…0d44fa27` (stored; committed copy
  `inspection/gu7-inspection-r3-brief.md`, same sha256).
- **Two differences from the earlier launches of this register, declared**: the witness's gate is the quick tier (C11 not
  run), and the tree was not pushed (earlier inspections were launched on a pushed commit with CI's conclusion read). The
  inspector worked on a scratch copy holding the tool as round 2 saw it, the tool now, the tool before the change, the two
  diffs, the template in both states, both earlier reports and the earlier fixtures.
- **What was inspected**: `new/ui-cad-gate.py` sha256 `8f7e25ca…f70b9902a` — the bytes of `HEAD:method/tools/ui-cad-gate.py`
  at `acc7c05`. The fix commit of this return does not touch that file or the template (git blob `1048de05…`, unchanged).
- **The verdict's content**: C1 (an empty member, IB-01), C2 (a ruling naming itself, IB-02) and C3 (ruled, not by the user)
  each **closed**, each on round 2's ledger and on variations the inspector wrote; IA-08 **closed**; IA-01 to IA-07 hold; no
  false fail on five classes of valid ledgers; no false pass in the same path; no traceback in a 40-case sweep; the
  no-bundle output identical on 6 cases; each of the three arms turns red when its check is removed (the inspector's own
  three mutants). **New findings in range: none.**
- **Out of range, from the inspector (not repaired, not counted)**: a ledger whose ruling id is the number `0` is failed by
  GU4, which reads `0` as a missing id; GU7 passes it. It predates this ECO.
- **What this changes in section 5**: UR-1 to UR-3 are no longer unreviewed. The verdict of record for GU7 is now ACCEPT in
  the range "correction confirmation and regression"; rounds 1 and 2 remain REJECT in the record, each answered by a repair.

### 6.2 Item 2 — the repairs, and the self-tests

Each new arm for a repaired check was run on the unrepaired tool first and was red there (13 arms of `loop-count`, 3 of
`handover-stamp`); the arms added only for coverage were green on the unrepaired tool, as they should be.

- **KD-02** `handover-stamp.py`: a manifest whose `main` / `program` is not a string is `[input]`, exit 2; a log that
  cannot be read (a directory) is `[input]`, exit 2; any other exception leaves through `[internal]`, exit 2. Exit 1 now
  means only what the header says. The header's exit 2 line says "cannot measure".
- **KD-03** `loop-count.py --check` now reports as gaps: a round with a reply and no reaction row; a duplicate report id; an
  item whose `round` is missing or not a round; missing `limits.rounds` or `limits.budget`; a missing `jig` field; a reply
  with no `launches` field; `matching` greater than `count`. As input errors (exit 2): `limits.rounds` not an integer of 1
  or more; `launches.count` / `matching` missing or not integers. **A consequence for records**: `limits.budget` and
  `set.jig` are required. Declared as still not checked (the header): the vocabulary of `outcome`, the contents of
  `subject` / `about`, a round with no reply and no `launches`.
- **KD-05** `eco-turn.md`: the record line is copied as printed for exit 0, 1 and 3 (`{count: 0, matching: 0}` for exit 3);
  on exit 3 and exit 1 the build used is asked of the user and counted in `reasks`; no word is added to `class`; exit 2 is
  named (`launches: unknown`, handled as exit 3). `loop-count`'s self-test feeds both record lines to `--check`.
- **KD-06** the header of `loop-count.py` explains each word of `kind`, `disposition` and `outcome` (the meanings are those
  the count of 2026-11-17 used; `fixed` and `record_fixed` are told apart as before and after manufacture);
  `eco-turn.md` maps the confirmation items and its two lists to `to_user_check`, `to_user_report`, `no_action`.
- **KD-07** `eco-turn.md`: the status note becomes "golden 待ち" when the confirmation items are handed over (the end of its
  section 4), and goes back to "周 N 候補・利用待ち" on a return to a round.
- **KD-08** `CLAUDE.product.md` names both stops of the skill; `eco-file.md` names what gate ① approves (the words, the
  acceptance criteria, the list of what must not happen, the limit of rounds, the budget) apart from what is asked first.
- **KD-10** arms: `loop-count` 23 → 54, `handover-stamp` 11 → 26. `mutants_tools.py` runs the reviewer's own lists of
  round 2 again, and the producer's mutants for the checks added here (`mutants-tools-output.txt`):
  `loop-count` — the reviewer's 47: **47 killed** (22 before); the 10 for the added checks: 10 killed. `handover-stamp` —
  the reviewer's 25: **24 killed** (13 before); the 3 for the added checks: 3 killed. The one survivor is the `..` test of
  the file-name check: the name pattern already refuses every name that test refuses, so removing it changes no result.
  The headers of both tools carry these numbers in place of the old ones, and say that nothing is claimed for a check
  that is in no list. **What the numbers are not**: the committed output was measured on the two tools before the header
  lines that carry these numbers were written (comment lines only; no code line differs); the reviewer of 6.6 reproduced
  six of its entries on the committed bytes with the same results, and found that 22 of 35 mutants of its own, outside
  these lists, survive (R3-07). A second run of the whole check on the committed bytes was started after the confirmation:
  its first list (the reviewer's 47 for `loop-count`) ended with 47 killed; the producer then stopped the run, so that
  nothing would be writing into the repository at the acceptance stop. The other three lists were not measured again on
  the committed bytes, and the committed output file is the first run's.

### 6.3 Item 3 — V2 from the repository; V4's exit codes

- **V2**: the table is `v2/findings.tsv`, a byte copy (5882 bytes, 65 rows, sha256 `67861a09…a4dc8315`) of the count's
  table, whose folder is not committed. `v2_count.py` takes no argument, reads that file, and stops if its sha256 differs.
  The record now carries the budget MoviePad's order names. One mutation of the script was narrowed: a round with no `set`
  at all now has two gaps (the set and the jig field), so the mutation keeps the jig field. Five mutations for the new rules
  were added. **17 checks, all as expected** (`v2-output.txt`). The limit of section 5 stands: the rounds, three reactions
  and four reports are entered by hand in the script.
- **V4, read through by the producer** (679 lines before this return). Tool calls and where their exit codes go: the
  scaffold, the two installed self-tests, every commit and every `validate`, the gate (twice), `loop-count --check` on the
  final record — into the line's verdict. **One was not**: `loop-count --check` on the round-1 record printed its exit code
  in a line whose verdict was the commit's. It is now a check of its own (`*.d.rec1.count`). One exit code stays in a
  NOTE by design (`bom-structure-check --index` before the acceptance commit; the hook's verdict is the commit's line).
- **Known-bad controls added**: the round-1 record with `handed_at` removed must make the count exit 1 with that one gap;
  the ledger with the bundle's list left out must make the gate exit 1 on GU7.
- **`v4_sabotage.py`** replaces one installed tool by a stub with a constant exit code and expects `v4_route.py` to go red
  on the checks that read that tool: the count always failing, never failing, the gate always failing, never failing —
  **4 of 4 red on the expected checks, baseline green** (`v4-sabotage-output.txt`). **Its first run showed nothing**: the
  stub was written once after the scaffold and the route's own `git reset --hard` restored the tracked kit file, so two
  cases stayed green for the wrong reason; the stub is now written before every call.
- **Found by reading, corrected in the script**: the synthetic ledger closed the bundle with `decided_by: producer`, not
  `user` as the skill's A3 words it; the record lacked the fields the count now requires.

### 6.4 Item 4 — three states: the return to a round is measured

`v4_route.py` variant C now returns to a round after the `implemented` transition: a candidate commit on a protected path
with the ECO in `implemented` and `open_states: [staged, implemented]` passes both layers (`C.back`), its record commit
passes (`C.back.rec`), and the acceptance from `implemented` to `applied` follows (`C.e`). The line `C.back.status` cannot
fail once the transition has passed and is **not** counted as a measurement (R3-06, found by the confirmation of 6.6);
the edit of the status note back to "周 N 候補・利用待ち" under `implemented` is driven by no commit of V4. Variant D is
the control: the same profile with
`open_states: [staged]` — the same commit is refused by E01 (`D.back.ctl`). The two texts that said "read, not run"
(`eco-turn.md` section 4, `change-management.md` section 4) now say what was measured — `eco-turn.md` says "both", which
is more than the paragraph above (R3-06; not repaired). KD-09 is closed as a defect of the
record; the limit it names stays a rule of the route: a three-state product can return to a round only with `implemented`
in `open_states`.

### 6.5 The results on the fix commit `12cc2be`

- **V1 result: PASS** — 9 checks, run again; the gate's bytes are those of section 5 (`v1-output.txt`).
- **V2 result: PASS** — 17 checks, from the repository alone (`v2-output.txt`).
- **V3 result: PASS** — 5 checks, run again on Windows and under Git's `sh`; a POSIX system was not used (`v3-output.txt`).
- **V4 result: PASS** — 88 checks on four scaffolds bound to one kit manifest, `df914814e7bb` (`v4-output.txt`); the run was
  made on the working tree that was then committed as `12cc2be` with no file of this ECO under `method/` changed in between
  (the reviewer of 6.6 compared the kit hashes in the output with the committed files: equal for the files it lists). The
  kit the scaffolds copied also held the uncommitted `method/improvements.md`, which is not this ECO's and which CI will not
  see. `v4_sabotage.py`: baseline green, 4 of 4 red.
- **V5 result: PASS** — 12 checks (`v5-output.txt`).
- **V6 result: PASS for what was run; CI not confirmed.** The full self-conformance with HEAD at `12cc2be`:
  **exit 0, 28 result lines**, C11 and C11b included, 961.7 s (`full-self-conformance-12cc2be.txt`). The working tree was
  that commit plus the two uncommitted paths that are not this ECO's (`method/improvements.md`, which lies under `method/`
  and so inside what C11 copies, and the survey folder) — not the bare commit CI would check out. The quick tier exited 0
  on the tree of this record commit (C11 is not run by it; this commit changes the order, the register and files under
  `bomdd/reports/` only). **Nothing is pushed. CI has not run on any commit of this ECO**, and the POSIX launcher has run
  nowhere but under Git's `sh`. By the user's instruction this is recorded as not confirmed and is part of no statement that
  the ECO is verified. `required_gates` names V6, so a promotion to `verified` through `bomdd-run` is not attempted.

### 6.6 The one confirmation after the repair

One reading in a fresh context of the producer's equipment (not another lineage), read-only, on `12cc2be` against `acc7c05`,
range "the repaired places and the regressions those repairs could cause"; brief and report with every disposition:
`inspection/review-r3-brief.md`, `inspection/review-r3-report.md`. It was run through the session's subagent call, not through
`bomdd-run`, so that the ledger's last cell record stays the GU7 inspection of 6.1.

- **Verdict: SERIOUS FINDING — one, by the letter of the brief's definition** (a wrong exit code of a tool). **R3-01**:
  `loop-count --check` exits 0 for an item whose `round` is written `true`, `yes` or `1.0` when round 1 exists (the check
  compares with Python equality). The reviewer rates its practical weight low and writes that under the reading "input a
  session would realistically write" its verdict would be "no new serious finding". Not a regression: before this return the
  field was not checked at all. **Reproduced by the producer. Not repaired**, as instructed.
- **Items**: KD-02, KD-05, KD-07, KD-08, KD-09, V2 and V4 **closed**; KD-03, KD-06 and KD-10 **partly** (R3-01; R3-02 and
  R3-05; R3-07). No traceback on any input tried (72 + 59 hand-made cases, 2106 structural mutations); no regression found in
  either tool (0 loosened against `acc7c05`, 177 tightened, all in the six rule areas); V2 reproduced from a `git archive`
  export.
- **Seven minor findings, none repaired**: R3-02 a rule the repair added ("reports にも 1 行") is neither checked nor declared
  unchecked (reproduced); R3-03 the skill's exit-2 bullet names a broken trace, which is exit 1 (reproduced); R3-04 the
  exit-1 bullet does not say to write the reply and a reaction row (it fails closed); R3-05 no word for a finding repaired in
  the product after manufacture, and the self-test's own good record uses `fixed` against the header's meaning; R3-06
  `C.back.status` cannot fail, so "both measured" in `eco-turn.md` says more than was measured, and the status-note edit under
  `implemented` is driven by no commit of V4; R3-07 four parts of the added checks are not held by the self-tests, and 22 of
  the reviewer's own 35 mutants outside the lists survive; R3-08 a count in a docstring.
- **The remaining risk, and the scope that can be used (the producer's statement, for the user's decision).**
  - `loop-count --check` exit 0 can be read as "the record has no gap the header names" **only for records whose item and
    reaction rounds are written as plain integers**; it does not show that every `to_user_report` item has a row in
    `reports`, nor anything about the vocabulary of `outcome`, nor is it defined for a record that is not UTF-8. The stage
    tables do not group by an item's round, so R3-01 does not change a count; it lets one wrong field through.
  - `handover-stamp check`: the exit codes are as its header says on every input tried; measured on Windows and under Git's
    `sh` only.
  - `eco-turn.md` carries two phrases that say more than is true (the exit-2 bullet's "跡が壊れている"; "両方を…実測") and
    one missing sentence (exit 1). A session that follows the exit codes acts on the safe side in each.
  - The three-state return: the validator accepts the candidate commit with the ECO in `implemented` when `implemented` is in
    `open_states`, and refuses it otherwise — that much is measured. That the status note can be edited back under
    `implemented` is not.
  - GU7: accepted by the independent inspector within the range of round 3. No round has explored the boundary of the tool
    as it now stands.
  - **Nothing here supports use in a product yet**: no product carries this kit, and CI has not run.

### 6.7 What remains (for the acceptance request)

The user names what is accepted. Nothing in this list was repaired after the confirmation.

- **From the confirmation**: **R3-01** (serious by the letter; a known false pass of `--check`), **R3-02 to R3-08** (minor),
  and its seven out-of-range observations (`inspection/review-r3-report.md`).
- **Not in the user's list for this return, unchanged**: **KD-01** (`loop-count`: a record that is not UTF-8 ends in a
  traceback, exit 1), **KD-04** (unquoted values that YAML retypes are reported as missing — it fails closed), **KD-11**
  (V4's labels say R3 / R4 for A3 / A4; its other half, the exit code, is closed in 6.3).
- **Closed in this return**: KD-02, KD-05, KD-07, KD-08, KD-09; UR-1 to UR-3 (seen by the inspector: ACCEPT). **Closed in
  part**: KD-03 (R3-01 remains), KD-06 (R3-02, R3-05 remain), KD-10 (the lists' mutants are killed; R3-07 remains).
- **Out of range, from the inspector**: GU4 reads a ruling id that is the number `0` as missing (predates this ECO).
- **Standing from section 5**: the hand-entered part of V2; no POSIX system; no product; no user took part; the out-of-scope
  items listed there; "not shown by any of this".
- **Not confirmed**: CI; the push; the full self-conformance on this record commit (the quick tier only).

### 較正 receipt — addendum (/calibrate, trigger ③: `loop-count`, `handover-stamp` and the script of V4 changed; receipt_author_role = producer)

- **Written in two steps**: the judgements below were drafted before the confirmation of 6.6 returned and were corrected
  after it; the corrections are marked "after 6.6".
- **The claims (one sentence each).** (2') `loop-count --check` exits 1 on the gaps its header's format names, except
  the three things the header lists as not checked — **after 6.6: and except two more that the header does not list** (an
  item's or a reaction's `round` written as a bool or a float that equals a round number, R3-01; a `to_user_report` item
  with no row in `reports`, R3-02). (3') `handover-stamp check` returns 1 only for a launch of another build,
  a changed file or a broken log line, and 2 for anything it cannot measure. (4) `v4_route.py`'s PASS lines depend on the
  exit codes of the tools they report.
- **査定した主張と判定**:
  - (2'): **observed / eligible for the classes armed** — 49 known-bad arms, each with its own words and, for gaps, its own
    count; 13 of them red on the unrepaired tool; the real ECO-006 record and nine mutations of it; 57 of 57 mutants of
    the two lists killed. Not eligible beyond that: the three declared exclusions, a record that is not UTF-8 (KD-01),
    retyped values (KD-04). **After 6.6: not eligible for the two undeclared false passes (R3-01, R3-02), and the arms do not
    hold four parts of the added checks (R3-07); of the reviewer's 18 own mutants of this tool, 11 survive.**
  - (3'): **observed / conditionally eligible** — 25 known-bad arms, 3 red on the unrepaired tool; 27 of 28 mutants killed,
    the survivor equivalent; the catch-all is exercised by replacing `check` inside the self-test, not by a real fault. The
    POSIX launcher is run by V3 under Git's `sh` only. **After 6.6: 59 more inputs from the reviewer, exit codes as the
    header says; of its 17 own mutants, 11 survive (three likely equivalent, by its reading); the arm `program: 7` does not
    exercise the repair (R3-07).**
  - (4): **observed / eligible for the two tools the route calls** — four stubs with constant exit codes each turn the
    script red on the expected checks. Not shown for the validator and the hooks (their controls are the refusal lines).
  - GU7 as accepted by an independent inspector: **eligible within the range of round 3** (the three repairs and their
    regressions). Rounds 1 and 2 were boundary exploration and correction confirmation; no round has explored the boundary
    of the tool as it now stands.
- **検出した計器欠陥と帰属**: **after 6.6, left as they are** — `loop-count`'s round check compares with equality and so
  takes `true` / `1.0` for round 1 (R3-01; the producer's logic, written in this return); a rule this return added to the
  header is not checked and not declared (R3-02; the producer's); V4's line `C.back.status` cannot fail (R3-06; the
  producer's). Repaired or corrected before a result was used: the unchecked exit code in V4 (the producer's script, written by a subagent; found by the first
  review, repaired here); the sabotage control that showed nothing on its first run (the producer's; repaired before a
  result was used); V2's mutation that assumed one gap (the producer's script; narrowed); the synthetic ledger's
  `decided_by` (the producer's script). No defect is attributed to a product or to the inspector.
- **宣言した検出力の限界**: as in section 5, and: the new arms were written by the producer after reading the reviewer's
  lists, so they answer those lists; the confirmation of 6.6 is one reading by the producer's own equipment.
- **Battery (only the rows whose answer changed since section 5).** Q1: two header statements were replaced by measured
  ones; the route's sentence about `--check` still holds (it points to the header). Q3: for `loop-count` each removed check
  in the lists now turns the self-test red; for `handover-stamp` all but the equivalent one. Q5: CI, the push, a POSIX
  system and a boundary exploration of the final GU7 are recorded as not measured. Q9: V4 prints the kit manifest of its
  four scaffolds. Q11: malformed input of the two tools is now a class of its own with one exit code (2), except KD-01.
