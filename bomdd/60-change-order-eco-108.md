# Change Order — ECO-108 (default dispositions in the product kit: R4's limit and R8's review get playbook §8.5's default disposition and layered findings; eco-fix and eco-accept follow)

> Ruling: user, 2026-10-13, "A". The question asked was whether to file the one evidence-backed part of an outside proposal now (A) or wait for a second positive example (B).
> - The proposal: borrow manufacturing's "stop institutions" — concession, tolerance, measurement-system analysis, change classes.
> - The analysis: most of these already exist in playbook §8.5, but the product kit carries none of them. R8 still says "never proceed until in-scope findings are 0".
> - A = put §8.5's default dispositions into the kit now (distribution is a separate ECO); B = record only.
>
> The proposal's other items (a list of established conditions, a standing reviewer repeatability check, process characteristics, procurement classes, moving lessons to a process FMEA, Hold/Witness/Review) are held as lenses, not filed. They have no observed trigger, and the proposal itself says not to make them a desk round.
> Converge rulings: the text did not converge in 3 rounds (16→7→3). The user ruled "A" (extend one round; ask again if it finds something). Round 4 found 2 minor items, which were repaired, and the user ruled "B" (file now, recording that the round-4 repairs are unreviewed).
> Records are English-primary (from 2026-10-12). The template text stays in Japanese, like the text around it.
> **Filing and manufacture are in one commit** (documents only; the pattern of ECO-076, ECO-104 and ECO-106). Verified is recorded in a later commit, after self-conformance and the CI conclusion have been observed.

## Equipment

- Filing and manufacture: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- Producer: EQ-004.
- Converge round reviewer: a fresh context of the same model (context independence, not equipment independence).
- Independent inspection: none planned (documents only; manufacturer's calibration only; no inspector row).

## 0. Basis

**What §8.5 already holds** (`method/bomdd-playbook-v1.md:787-816`):
- reviews have a bound, frozen before they start;
- a budget with a default disposition when it is reached: accept what is confirmed, record the known inaccuracies, and stop and report without tidying, rolling back or extending (80点受入);
- findings are split into 実体, 証拠 and 記録, each with a default disposition frozen in advance (candidate, N=1);
- the forms §8.5 declined: a three-field schema and validator enforcement (line 815).

**The measurement** (`method/improvements.md`, EXP-20260828-03):
- **Observation 2** (ViewTube ECO-VT-162, 8 review rounds). No default was declared, and the record-layer findings sent to correction were 9 of 9 through round 7. This is the failure §8.5 describes, measured a second time.
- **Observation 3** (ViewTube ECO-VT-178 to 211, with a control). Stop conditions were declared on ECO-VT-182, 184 and 190 and inherited by the products: "the 2nd round is the last; blocking findings at the last round are not repaired, the claim is narrowed; material and minor are carried".
  - Record-layer findings sent to correction: 17% (5/29) in final rounds under the default, against 79% (49/62) in other rounds.
  - Playbook §8.5 also records the counter-example. The one extension the user allowed as an exception re-broke two inputs that had been right, and the repair was withdrawn.

**The gap** (read at baseline `40379d1`):
- `method/templates/product-profile/` holds no "既定処分", "80 点", "記録層" or "停止条件" (grep).
- R4 names "charter・ECO で決めた上限" only as a reason to go back to the human, with no default when it is reached.
- R8 (`change-management.md:55-56`) and eco-fix 3.6 (`skills/eco-fix.md:40-41`) say "未処置のスコープ内所見が 0 になるまで停止点へ進まない", with no bound and no layers. This is the rule under which ViewTube ECO-VT-184 ran 13 rounds.
- eco-fix step 2 (`:29-30`) sends an exceeded limit to "延長の裁定".
- ViewPrism2's copy (`bomdd/change-management.md:38`) has the same limit sentence and no default.

## 1. Change request (documents only)

1. `change-management.md` R4: one sentence on the default disposition when a limit set in the charter or an ECO is reached. converge's round limit is excluded and stays a ruling point (converge step 5).
   - Do not stop to ask for an extension.
   - Present the confirmed part as a candidate for acceptance; record the rest as known defects and known inaccuracies; narrow the ECO's claim to that range; report it at the next stop.
   - Do not tidy or roll back. A diff that is not all green is not made a fix commit. Whether to go on past the limit is the human's, after the report.
2. `change-management.md` R8: the "until 0" sentence is replaced. In-scope findings get **layered default dispositions**:
   - **実体** (product artifacts: the source of code, tests and probes, and their behaviour) → R5 repair. A finding whose probe does not fail is recorded with its probe and listed at the stop. Sending the work back to R2 is kept for the probe of the ECO's own symptom.
   - **証拠** (results and observations: test results, captures, side-by-sides) → accepted if readable, otherwise `UNKNOWN` and not a basis for passing. Readable evidence that shows a failure or a skip goes to 実体.
   - **記録** (everything else: the ECO text, ledgers, reports, and so on) → recorded as known inaccuracies, not corrected. Two exceptions:
     - a record that states a claim or a result more broadly than it is gets the claim narrowed;
     - one that turns a machine check red is corrected.
3. `change-management.md` R8: **at most 2 reviews**. This is the binding that worked in section 8.5's measurement, "the 2nd is the last".
   - Round 1 ends the review if it finds no 実体 findings.
   - 実体 findings left at the last review are not repaired. They are shown at the stop as known defects, with the claim narrowed. The human decides at golden (or at the acceptance request). Accepted known defects then take R3's two choices.
   - Exception: an R7 copy error (転写漏れ) is not carried. It is repaired and checked by R7's side-by-side, with no third review.
   - Departures from the default are decided by the human at the next stop; until then the default applies. Departures are more than 2 reviews, or correcting a record outside the exceptions.
   - A repair coming back from a golden failure or a returned acceptance request counts from round 1.
   - Reaching the bound does not stop the process (stop word `NONE`); it goes on to the existing stop.
   - When equipment independence is required, that inspection carries the 2 reviews. Round 1 is boundary search and round 2 is fix-confirmation plus regression (factory-delegate's range). Round 2 runs even if round 1 finds no 実体 findings. A REJECT in the last round is shown at the stop like known defects.
   - Only the bound and unconfirmable findings let a 実体 finding reach the stop.
4. R5: probes for R8 findings follow R8.
5. `skills/eco-fix.md`:
   - step 1 defers R8 findings' probes to R8;
   - step 2: on reaching a charter or ECO limit, R4's default disposition applies, not an extension ruling;
   - step 3.6 follows R8 (round 1 ends the review except for equipment-independent inspection) and points to it; the record lists layer and review count;
   - the stop section lists the following apart from the pass criteria, with the narrowed claim: known defects, unconfirmed findings, known inaccuracies, `UNKNOWN` evidence, and any repair made without review after the last review (the R7 exception) together with its side-by-side, and a REJECT in the last round of equipment-independent inspection;
   - a known defect the human does not accept becomes a GF-*, and the R8 count restarts.
6. `skills/eco-accept.md`:
   - step 2 writes accepted known defects into the approval record;
   - a new step 4.5 gives accepted known defects their R3 disposition: a cheat-log record goes in the accept commit, a separate filing is its own commit;
   - step 6 re-lists findings carried by R8's bound, each with its R3 destination (a cheat-log record or the separate ECO's number).

**Not changed:**
- R4's human gates: no new gate. Known defects reach the human through the existing golden or acceptance request.
- The start-wait after filing.
- `factory-delegate.md`'s round rules: the receiver already owns the cut-off of inspection rounds.
- `operator-layer.md`'s stop vocabulary: reaching R8's bound leads to the existing golden stop.
- The playbook: §8.5 keeps its candidate status and its own text.
- Products' copies: distribution is a separate ECO.
- No mechanical check: §8.5 line 815 declines validator enforcement.

## 2. No-impact prediction (before manufacture; frozen)

- The diff is the three template files (39 insertions, 8 deletions by git), this order, the register and `method/improvements.md`.
- No change to tools, hooks, `.github`, the playbook or the `.claude/skills` copies. None of the three files has a copy there.
- BomDD's own self-application is unaffected; it does not use the product kit's R8.
- Products see nothing until distribution.

## 3. Acceptance (conditions; frozen at filing)

- **V1**: condition = phrase counts at baseline `40379d1` and after manufacture, by `eco108_count.py` (the script is quoted in §4):
  - new phrases 0 → 1:
    - R4 "上限に達したときの既定の処置";
    - R8 "**見直しは 2 回まで**" and the record-layer clause;
    - eco-fix "延長を求めて止まらず R4 の既定の処置", "R8 の層ごとの既定の処置" and "縮めた主張の範囲を明示する";
    - eco-accept "R8 の上限で持ち越した所見";
  - old phrases 1 → 0:
    - R8's "未処置のスコープ内所見が 0 になるまで停止点へ進まない";
    - eco-fix's "上限の超過は延長の裁定を求める" and "未処置のスコープ内所見 0 になるまで停止点に進まない".
- **V2**: condition = no hunks outside R4, R5, R8, eco-fix steps 1, 2 and 3.6 and the stop section, and eco-accept steps 2, 4.5 and 6. The two skills' frontmatter parses. A grep over templates, `.claude/skills`, tools and onboarding finds no remaining statement of the old rules.
- **V3**: condition = self-conformance exits 0 (observed before commit), and CI is green.
- **V4**: condition = manufacturer's calibration only.
- **V5** (not a closing condition): after distribution, EXP-20260828-03's ② and ③ in the product's next review series (record-layer findings sent to correction; repair lines).

## 4. Manufacture and the measurements before commit (2026-10-13, filing and manufacture in one commit)

**What was changed** (39 insertions, 8 deletions):
- `change-management.md`: R4 gained 3 lines, R5 gained 1, and R8's "until 0" sentence became 16 lines with the layers and the bound.
- `skills/eco-fix.md`: steps 1, 2 and 3.6, and the stop section.
- `skills/eco-accept.md`: steps 2, 4.5 (new) and 6.

The text was repaired over four converge rounds (receipt below). Round-by-round repair scripts are kept in the manufacturer's scratchpad and are not records.

**V1 result: PASS.** `eco108_count.py` reads the baseline with `git show 40379d1:<path>` and the working tree with the same strings:
- rows 1, 2, 3, 5, 6, 7 and 10 (new phrases): baseline 0 → now 1;
- rows 4, 8 and 9 (old phrases): baseline 1 → now 0.

The script (verbatim strings):

```
change-management.md  上限に達したときの既定の処置
change-management.md  **見直しは 2 回まで**
change-management.md  **記録**(それ以外 — ECO 本文・台帳・報告の記述など)= 既知の不正確として記録し、是正しない
change-management.md  未処置のスコープ内所見が 0 になるまで停止点へ進まない
skills/eco-fix.md     延長を求めて止まらず R4 の既定の処置
skills/eco-fix.md     R8 の層ごとの既定の処置
skills/eco-fix.md     縮めた主張の範囲を明示する
skills/eco-fix.md     上限の超過は延長の裁定を求める
skills/eco-fix.md     未処置のスコープ内所見 0 になるまで停止点に進まない
skills/eco-accept.md  R8 の上限で持ち越した所見
```

The record-layer phrase (row 3) was reworded in round 1, before filing. The row was updated with it, and its baseline is 0 either way.

**V2 result: PASS.**
- Hunks against the baseline: change-management at 44 (R4), 49 (R5) and 59 (R8); eco-accept at 30 (step 2), 35 (4.5) and 38 (step 6); eco-fix at 22 (step 1), 30 (step 2), 41 (3.6) and 56 (stop).
- The frontmatter of eco-fix and eco-accept parses (name and description).
- A grep for "未処置のスコープ内所見", "延長の裁定を求める" and "上限の超過" over `method/templates`, `.claude/skills`, `method/onboarding` and `method/tools` returns 0. The round reviewer's wider grep found the old phrases only in orders, reports and `improvements.md` history.

**V3** is recorded at closure, after observation.

## 収束 receipt (converge self-application)

- **判定: 未収束** (round 軌跡: 16→7→3→2; material findings 6→1→0→0).
  - The limit of 3 rounds was reached without two consecutive rounds of zero, and the user ruled "A" (extend one round; ask again if it finds something).
  - Round 4 found 2 minor items, so the user was asked again and ruled "B" (file now, recording that the round-4 repairs are unreviewed).
  - The text is not reported as converged.
- **起動経路**: 自発. Rule text for process equipment is design synthesis under converge's self-start contract; the unconverged design stopped for a ruling before filing, twice.
- **Round reviewer**: one fresh context of the same model, resumed for each round. This is context independence, not equipment independence. It was read-only and edited nothing.
- **DoD** (fixed before the draft):
  - ✔ D1 every rule has an event that always occurs: R8 runs on every protected-path fix, the limit default on every limit reached, eco-accept 4.5 on every golden acceptance with known defects.
  - ✔ D2 every target exists (file:line in §0 and §4).
  - ✔ D3 one source per rule: R8 holds the rule; eco-fix 3.6 and the stop section point to it; R4 holds the limit default.
  - ✔ D4 no conflict with R3, R4's gates and ECO-106's text, R5, R6, R7, golden, eco-accept, converge step 5, operator-layer's vocabulary, factory-delegate's range or handoff. Each was found in rounds 1 to 4 and resolved, except the items below.
  - ✘ D5 the round-4 repairs (eco-fix 3.6's exception, eco-accept 4.5) are unreviewed.
  - ✔ D6 within ruling A of 2026-10-13: the kit only; distribution apart; no mechanical check.
- **周回** (each round's new findings):
  - **Round 1, 16** (6 material).
    - R4's default would override converge's limit.
    - R7 and R8 bound the same finding differently.
    - An AI-written "before the review" exception let the AI lift its own bound, against section 8.5.
    - An overstated claim could pass as a record inaccuracy.
    - A finding disproved by its probe had no disposition.
    - 10 minor: layer overlap, no catch-all, 1 round against 2 reviews, count wording, the limit stated twice, partial work at a time limit, stop vocabulary, factory-delegate rounds, the human's decision on a known defect, the R3 destination unchecked.
  - **Round 2, 7.**
    - 1 material: equipment-independent rounds were exempt from the bound.
    - 4 minor: an unreviewed R7 repair undisclosed; "人が決める" read as a new stop; list nesting; eco-fix drift.
    - 2 partial: R5 and step 1 still sent every non-failing probe to R2; the stop vocabulary.
  - **Round 3, 3 minor.**
    - The bold sentence contradicted the probe carve-out.
    - Equipment-independent inspection could not reach ACCEPT.
    - A defect filed apart could come back as a golden failure.
  - **Round 4 (extension), 2 minor.**
    - eco-fix 3.6 lacked the equipment-independent exception and the last-round REJECT.
    - eco-accept had no step making the R3 choice.
- **Claims checked** (key points):
  - section 8.5 at `method/bomdd-playbook-v1.md:787-816`;
  - EXP-20260828-03 observations 2 and 3 at `method/improvements.md:4422-4443`;
  - the kit grep for 8.5's terms (0);
  - ViewPrism2's limit sentence (`bomdd/change-management.md:38`);
  - converge step 5's limit rule;
  - operator-layer's `NONE` and `CONVERGENCE_LIMIT`;
  - factory-delegate's range rule (`:125-128`);
  - no tool pins the replaced text (grep over `method/tools`, `bomdd/hooks`, `.github`).
- **未収束事項**:
  1. The round-4 repairs are unreviewed (user ruling B).
  2. The text grew from a one-sentence change to 39 lines. Each round's findings were interactions with neighbouring rules, so further ones of that kind are possible. The distribution ECO compares the text with each product's own copy, which is a second reading.
  3. §8.5 stays candidate (N=1 positive, one product). The kit now carries a candidate rule, by the user's ruling A.

