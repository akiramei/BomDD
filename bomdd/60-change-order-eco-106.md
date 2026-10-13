# Change Order — ECO-106 (who decides derived-layer choices: product change-management R4, eco-fix step 2, converge step 6 and the two product entry lines — the AI decides, records and reports; the start-wait after filing is unchanged)

> Ruling: user, 2026-10-13, "A". The question asked was whether to keep the stop after filing, where the AI waits for an explicit `/eco-fix` (40 of the 60 avoidable stops measured were such start-waits):
> - A = keep the start-wait; fix only the type where the AI asks for a ruling on a derived-layer choice (the fix option, the order, the plan, how to repair its own output): eco-fix's "是正の裁定" is chosen and recorded by the AI, and converge presents derived-layer designs as a decision and a report;
> - B = A, and also go on from filing to fixing without a stop when the diagnosis is implementation or derived layer.
>
> In both, the measurement is recorded (`bomdd/reports/escalation-asks-20261013/summary.md`).
> Records are English-primary from 2026-10-12 (the user's ruling under ViewTube ECO-VT-253). The skill and template text stays in Japanese, like the text around it.
> Second ruling: user, 2026-10-13, "A" to the converge stop at the 3-round limit (A = extend one round and add one sentence to R4 on R3 scope cuts; B = adopt the draft as it was; C = send back to the two named skills only). The extension was offered with the condition "if round 4 finds something new, ask again"; round 4 found nothing, so the design goes ahead under that ruling, still formally unconverged (see the receipt).
> **Filing and manufacture are in one commit** (documents only, the pattern of ECO-076 and ECO-104). Verified is recorded in a later commit, after self-conformance and the CI conclusion have been observed.

## Equipment

- Filing and manufacture: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- Producer: EQ-004.
- Independent inspection: none planned (documents only; manufacturer's calibration only; no inspector row).

## 0. Measurement (basis of the filing)

From `bomdd/reports/escalation-asks-20261013/summary.md` (read-only; two classifiers, Claude Opus and Claude Sonnet, blind to each other and to the hypothesis):

- **The instrument.** Turn-ending AI messages that wait on or ask for a ruling, in product-repository sessions: Claude Code 176 (ViewTube, ViewPrism2, TimetableAdv; 2026-07-13 to 09-25) and Codex 124 (TimetableAdv; gpt-6-astra and gpt-6.1-sol; 2026-09-05 to 10-05).
- **Avoidable stops** (both classifiers: the AI could have decided under playbook §4.5, and the subject is a derived-layer choice or the progress of work): Claude 32 of 176, Codex 28 of 124.
  - Start-waits (the design is settled; may manufacturing start?): Claude 19 (eco-file's "裁定は不要です。/eco-fix … で着手できます"), Codex 21 (ECO-046's per-scene "着手裁定"). **Kept** by the ruling.
  - **Derived-layer choices asked as rulings: Claude 7, Codex 7.** This ECO is about these.
- **What the 14 stops cited.**
  - Claude (the two classifiers differ): gate① 2 in both (ViewPrism2 ECO-095 and ECO-141, a fix option asked as gate①); R8 1 in both; R3 (whether to fold a repair into the ECO or file it apart) 1 or 3; none 3 or 0; preflight 0 or 1.
  - Codex: eco-fix with converge 3, converge 2, none 2.
- **The model families show the same shape** (18% and 23% avoidable; start-waits dominate; 7 and 7 derived-layer asks). Model, product, period and harness overlap completely, so no difference between models is claimed either way.
- **These are a baseline from before the rule.** §4.5's rule, that the derived layer is not approved item by item, came with ECO-097 to ECO-102 (2026-10-05/06). The stops were not violations of it; the rule was never wired into the procedures.

**Where the procedures route derived-layer choices to the human** (read at baseline `41efd00`):

- `method/templates/product-profile/change-management.md:36` R4: the human gate "裁定" is "設計判断・選択肢選び", with no layer named. TimetableAdv's copy is the same; ViewPrism2's says "方針・要求・候補の裁定 — 選択肢から選ぶ".
- `method/templates/product-profile/skills/eco-fix.md:25` step 2 "是正の裁定: ECO 本文 §4 の案から選ぶ" does not say who chooses.
- `method/templates/product-profile/skills/converge.md:73` step 6 "人間の判断が要る点を質問として明示する", with no layer named. Its self-start contract (`:17`) names "裁定候補" as the first kind of design synthesis.
- `method/templates/product-profile/AGENTS.product.md:31` "裁定(gate① — 選択肢から選ぶ)" and `CLAUDE.product.md:55` "裁定(選択肢から選ぶ)".

**converge is frozen** (2026-09-02, `method/improvements.md:6297`), and the condition for reopening it is a failure mechanism observed in real operation. The 7 Codex stops that cite converge or eco-fix, and its step 6 asking for rulings with no layer named, are that observation.

## 1. Change request (documents only)

1. `change-management.md` R4: "裁定" becomes the design decisions of the 裁定層 (CAD, requirements, specification, E-BOM, K-BOM) and the choice among them. Derived-layer choices (the fix option, the order and plan of manufacture and inspection, how to repair its own output) are AI work, decided, recorded and reported as a decision at the next stop; objections are taken there. The scope cut (record a separate problem, or file it apart) is R3's choice of two, made by the AI; mixing it into the current ECO is forbidden by R3, so only wanting to mix it is asked. They go back to the human only when the 裁定層 would have to change, when they are one of the three kinds §4.5 returns (new feature, new promise, underivable), or when a limit set in the charter or an ECO (time, count) would be exceeded.
2. `skills/eco-fix.md` step 2: the manufacturer chooses among the §4 options, writes the chosen and rejected options and the reason into the step-4 record, and reports the decision at the stop (golden). Only in R4's return cases does it stop without touching code: back to `/eco-file` for a 裁定層 problem, or a ruling on extending the limit.
3. `skills/converge.md` step 6 and its copy `.claude/skills/converge/SKILL.md`: a product's derived-layer design synthesis, once converged, is recorded as a decision and presented as a report, not as ruling candidates. In a product, the points that need the human are the 裁定層, §4.5's three kinds, non-convergence (step 5) and extending a limit.
4. `AGENTS.product.md:31` and `CLAUDE.product.md:55`: one qualifier each, pointing to R4.

**Not changed:**
- the start-wait after filing (eco-file's stop and the explicit-command rule in `AGENTS.product.md`): the user's ruling A;
- TimetableAdv's per-scene "着手裁定": the same question in product form, answered by A;
- `method/tools/bomdd-init.py:507` and `method/onboarding/example-session-log.md:22` ("裁定(選択肢から選ぶ)"): both address the human, for whom "choose among the options that reach you" stays true;
- the handoff contract: the candidate OBS-20261011-02 ① (reword §2.1 Q1 to name where authority lies) is not the lever the data shows, because the stops cite procedures, not the handoff tree;
- product copies: distribution is a separate ECO;
- no mechanical check (the discussion's traceability or coverage gate): not in A. R6 still stops any change to a fixed oracle row;
- the playbook.

## 2. No-impact prediction (before manufacture; frozen)

- The diff is the five template files and the converge copy (16 lines added, 5 changed; git counts 21 insertions, 5 deletions), this order, the register, `method/improvements.md` and `bomdd/reports/escalation-asks-20261013/`.
- No change to tools, hooks, `.github` or the playbook. BomDD's own self-application is unaffected, because its designs are method and process equipment, which the human rules on.
- The converge copy differs from the canonical file only by placeholder resolution: 3 hunks, the 2 known ones plus the new line's `{{METHOD}}`.
- Products see nothing until distribution.

## 3. Acceptance (conditions; frozen at filing)

- **V1**: condition = grep counts at baseline `41efd00` and after manufacture:
  - R4 has "導出層(M-BOM・Control Plan・Routing)の選択も AI の作業" (0 → 1) and "R3 の二択から AI が選ぶ" (0 → 1);
  - eco-fix has "是正の裁定(製造者が決める・R4)" (0 → 1);
  - converge, canonical and copy, has "導出層の選択を裁定候補の形で人に出さない" (0 → 1 each);
  - each of the two entry lines has "change-management.md R4" (0 → 1).
- **V2**: condition = no other hunks in the five templates; the converge copy's diff from canonical is placeholder-only (3 hunks); the frontmatter of the two skills parses.
- **V3**: condition = self-conformance exits 0 (observed before commit), and CI is green.
- **V4**: condition = manufacturer's calibration only.
- **V5** (not a closing condition): after distribution, the next 20 ruling stops in that product count derived-layer choices asked as rulings (baseline 7/176 Claude, 7/124 Codex).

## /preflight receipt (start path: manual — the user's "A" read as the start artifact)

- **Classification**: application of a decided change (user "A"), with design of the rule text.
- **Baseline `41efd00`**: **confirmed** (HEAD; the tree held only the untracked report).
- **Next number 106**: **confirmed** (the last register entry and the last order are ECO-105).
- **Current text** of R4, eco-fix step 2, converge step 6 and the two entry lines: **confirmed** (read).
- **No ECO in progress on these files**: **confirmed** (every register entry from ECO-100 on is verified).
- **Start decision**: **PROCEED_WITH_LIMITS** (the rule text is design synthesis; converge applied below).

## 4. Manufacture and the measurements before commit (2026-10-13, filing and manufacture in one commit)

**What was changed** (16 lines added, 5 changed):
- `change-management.md` R4: the gate line qualified, and four lines added (derived-layer choices, R3's scope cut, the return cases);
- `skills/eco-fix.md` step 2: the heading and the chooser, and three lines added (record and report; the return cases);
- `skills/converge.md` step 6 and the copy: four lines each;
- `AGENTS.product.md:31` and `CLAUDE.product.md:55`: one qualifier each.

**V1 result: PASS.** Every phrase counted 0 at `41efd00` and 1 after manufacture:
- R4 has both phrases;
- eco-fix has its phrase;
- converge has its phrase, in both the canonical file and the copy;
- each of the two entry lines has its phrase.

**V2 result: PASS.**
- **No other hunks.** Hunks against the baseline: R4 2, eco-fix 2, each other file 1, all at the places listed above.
- **The copy differs only by placeholder resolution.** The converge copy differs from the canonical file in 3 hunks: the copy notice and header, the new line's `{{METHOD}}` resolved, and the table A note. The first and last are the known ones (ECO-075).
- **The frontmatter parses** for `eco-fix`, `converge` and the copy (name and description).

**Worklist:** EXP-20261013-01 is listed, with 0 validation warnings.

**V3** is recorded at closure, after observation.

## 収束 receipt (converge self-application)

- **判定: 未収束** (round 軌跡: 2→1→2→0). The limit of 3 rounds was reached without two consecutive rounds of zero; the user ruled "A" (extend one round, ask again only if it finds something); round 4 found nothing. One round of zero is not two, so this is not reported as converged; the design goes ahead under the ruling.
- **起動経路**: 自発 (rule text for process equipment is design synthesis under converge's self-start contract). In a self-started arc, the unconverged design stops for a ruling before filing or canonisation.
- **DoD** (fixed before the draft):
  - ✔ D1 every rule has an event that always occurs (eco-fix step 2 runs in every fix; converge step 6 in every presentation; R4 is read through both);
  - ✔ D2 every target exists (file:line above);
  - ✔ D3 one source per rule (R4 holds the product rule; eco-fix points to R4; converge points to §4.5; the three kinds are named next to the reference for the reader);
  - ✔ D4 no conflict with golden (still a stop), converge's non-convergence and extension rules, handoff (a decision report is INFORM), ECO-097's two approval points, R3, R6 or R8;
  - ✔ D5 impact listed by line (two items were found late: round 2, the human-facing lines; round 3, kit freshness for distribution; both now listed);
  - ✔ D6 within ruling A (the start-wait is kept).
- **周回** (each round's new findings):
  - **Round 1, 2.** (a) converge's list of human points read as complete in BomDD's own method work too: limited to "製品で". (b) Weakening inspection: R6 already stops changes to fixed oracle rows; noted, no text.
  - **Round 2, 1.** `bomdd-init.py:507` and the onboarding example also say "裁定(選択肢から選ぶ)". Decided: not changed, because they address the human.
  - **Round 3, 2.** (c) Products' frozen kits may predate §4.5's three kinds, which R4 and converge now point to. Distribution must carry a kit at ECO-098 or later. Noted, no text. (d) R3 scope cuts (whether to fold a repair into this ECO or file it apart) were asked as rulings in 1 to 3 of the Claude stops (by classifier). The draft does not name them, although R3 already decides "file apart" and only an exception to R3 needs the human.
  - **Round 4 (extension, user "A"), 0.** Added to R4: the scope cut is R3's choice of two, made by the AI; only mixing into the current ECO is asked. Checked against R3 ("二択のみ"), eco-file's and eco-fix's R3 sections, eco-accept's R3 references and ViewTube's practice of asking for an R3 exception (ECO-VT-253): no conflict.
- **Claims checked** (key points): R4, eco-fix step 2, converge step 6 and the entry lines read at `41efd00`; TimetableAdv's R4 identical and ViewPrism2's different (grep); no tool or test pins the edited text apart from `bomdd-init.py:507` (grep over .py, .yaml and .json); converge's freeze and its reopening condition at `method/improvements.md:6297`.
- **未収束事項**:
  1. (c) the kit-version requirement for distribution: the distribution ECO must carry a kit at ECO-098 or later.
  2. Formal: one round of zero, not two. A further gap of the kind found late in rounds 2 and 3 (lines elsewhere that repeat the old wording) is possible; the grep for the old wording over .md, .py, .yaml and .json found none beyond those listed.


## 5. Closure (2026-10-13, verified, manufacturer's calibration only)

- **Window.** Baseline `41efd00` → filing and manufacture `44c0332` (diff_audit.head; **the window is closed**; the acceptance commit holds records only). Inside the window there are only the 10 allowed paths (`git diff --name-only 41efd00 44c0332`).
- **Acceptance results:**
  - **V1 result: PASS** (§4).
  - **V2 result: PASS** (§4).
  - **V3 result: PASS.** Self-conformance exited 0, observed before the commit (all checks, C16 and C17 included). The push went through the pre-push witness. CI run 38327279338 was **success** (fast ubuntu, fast windows, dotnet).
  - **V4 result.** Manufacturer's calibration only; no independent inspection. Register: `implemented → verified`; head frozen.
- **V5** (not a closing condition): EXP-20261013-01, after distribution to a product.
- **Recorded honestly.**
  - A commit attempt hung on a stray `cat` reading standard input and was stopped. Nothing was committed by it; the commit was then made from a message file, on the tree self-conformance had checked.
  - The converge verdict stays 未収束 (2→1→2→0). The design went ahead under the user's extension ruling, not under a claim of convergence.

### 較正 receipt (/calibrate self-application - trigger ①: verified promotion; receipt_author_role = producer; documents only)

- **The claim (one sentence).** The product templates now say that derived-layer choices and R3's scope cut are decided, recorded and reported by the AI, with the human asked only for the ruling layer, section 4.5's three kinds, an exceeded limit or mixing into the current ECO; and the rest of each file and the copy relation are unchanged.
- **査定した主張と判定** (the claims assessed and their verdicts; measurement × evidence):
  - "The new phrases are in R4, eco-fix, converge (canonical and copy) and the two entry lines": **observed / eligible**. Grep counts 0 at the baseline (known-bad side) and 1 after, for 7 phrases, each able to fail on its own.
  - "No other text changed; the copy differs by placeholder resolution only": **observed / eligible**. Hunk counts against the baseline, and a line diff of copy against canonical (3 hunks, 2 of them known from ECO-075).
  - "The new text does not conflict with R3, R6, R8, golden, converge's non-convergence and extension rules, handoff or ECO-097's approval points": **read / conditionally eligible**. Read by the manufacturer only, over converge rounds 1 to 4. Not measured: a reader other than the manufacturer.
  - "The 14 derived-layer asks came from procedures that name no layer": **read / conditionally eligible**. The cited rules come from two blind classifiers; the link from wording to behaviour is inferred, not tested.
  - "The change removes derived-layer asks": **not claimed; unknown** (EXP-20261013-01, after distribution).
- **検出した計器欠陥と帰属** (instrument defects found, and attribution): 0.
  - The hung commit attempt was the manufacturer's command (a stray `cat`), not an instrument.
  - The earlier instrument mismatch in the measurement (the `[DECIDE]` header on one side and keywords on the other) was the manufacturer's, found and corrected before filing (report, "A correction").
- **宣言した検出力の限界** (declared limits of detection):
  - The grep shows the text is there, not that a product AI will act on it.
  - Misclassification in the other direction, an E-side matter decided alone, is caught only by golden or by a user correction; no mechanical check was added (ruling A).
  - The products' copies are unchanged until distribution.
  - The self-assessment is blind to the manufacturer's own wrong premises (playbook §9); this receipt was written by the manufacturer.
- **Battery, row by row:**
  - **Q1 asked.** The grep only counts; the verdict sentences are the manufacturer's.
  - **Q2 asked.** Known-bad: the baseline counts (0). Known-good: after manufacture. The labels were fixed at filing, before the counts were taken.
  - **Q3 asked.** 7 phrases counted one by one.
  - **Q4 NA.** No declared input.
  - **Q5 asked.** CI success observed for the commit.
  - **Q6 asked.** The commit came after an observed exit 0, and the push went through the witness.
  - **Q7 NA.** No standing instrument was added.
  - **Q8 NA.** No preventive gate was added.
  - **Q9 asked.** Baseline and after were counted by the same script on the same tree.
  - **Q10 asked.** The limits above.
  - **Q11 NA.** No input class needs to be separated.
- **What this closure does not support:**
  - any effect on products (EXP-20261013-01);
  - the distribution (a separate ECO, which needs a kit at ECO-098 or later);
  - the start-wait, which is unchanged;
  - TimetableAdv's per-scene start ruling.
