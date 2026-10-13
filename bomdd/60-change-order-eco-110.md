# Change Order — ECO-110 (repair of ECO-108's product-kit text: the defects ViewPrism2 ECO-147's review found in the merged copy are also in the template)

> Ruling: user, 2026-10-13, "A". The question asked was whether to accept ViewPrism2 ECO-147 with its two known defects. A = accept it, repair the methodology template first (this ECO), then distribute to ViewTube; B = accept and do ViewTube first; C = hold ECO-147.
> Converge ruling: the text did not converge in 3 rounds (11→5→2). The user ruled "B" (file now, recording that the round-3 repairs are unreviewed).
> Records are English-primary. The template text stays in Japanese, like the text around it.
> **Filing and manufacture are in one commit** (documents only; the pattern of ECO-076, ECO-104, ECO-106 and ECO-108). Verified is recorded in a later commit, after self-conformance and the CI conclusion have been observed.

## Equipment

- Filing and manufacture: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- Producer: EQ-004.
- Converge round reviewer: a fresh context of the same model (context independence).
- Independent inspection: none planned (documents only; manufacturer's calibration only; no inspector row).

## 0. Basis

ViewPrism2 ECO-147 (applied `504921a`) merged ECO-108's text into ViewPrism2's own copies, and its independent review ran 2 rounds. Of the findings, these are also in the template at baseline `070d46e` (the findings are listed by their ViewPrism2 numbers in ECO-147 §8):

- **F4.** eco-accept 4.5 does the separate filing (`/eco-file`, its own commit) before step 5's accept commit. By then step 2 has already edited the register, so the filing commit carries an uncommitted applied transition without its trailer. `/eco-file` also ends at its own stop, so the accept is never committed.
- **F5.** R4's limit default and R7 are not reconciled. At an ECO limit with an R7 copy error left, R4 says to go to the next stop (golden), and R7 forbids golden.
- **F6.** The R7-exception repair (after the last review) has no return path. Machine acceptance can be skipped before the fix commit.
- **F8.** Three gaps in eco-accept:
  - the precondition does not say that accepted known defects are not findings;
  - step 2 has no place for them on the golden n/a path;
  - step 6 asks for a destination for known inaccuracies and unconfirmable findings that no step produces.
- **N1** (carried as a known defect in ViewPrism2, which has a Codex second opinion inside a round). In the template's terms: a parallel review result that arrives after repair has started has no stated round.
- **N2** (carried in ViewPrism2):
  - the wording: R4's limit stop reads against R8's "上限到達で工程は止まらない", which is about the review count;
  - the status: neither says whether a green diff with an R7 copy error left gets a fix commit and the register note "golden 待ち".

## 1. Change request (documents only)

1. **`change-management.md` R4.** When the R7 side-by-side is unfinished, or a copy error remains, at a limit, R7 wins:
   - no golden;
   - no fix commit; the status note is not "golden 待ち" and the register is not implemented;
   - the record of the fix is written, and the status note and the record say 「上限到達・golden 不可(R7)」;
   - the stop word is `NORMATIVE_RULING`. The human decides extension or closure, and what happens to the diff.
2. **`change-management.md` R8:**
   - the R7-exception repair (a copy error found at or after the last review) goes through eco-fix 1 to 3.5 and skips 3.6;
   - one review round is on one diff. The round's reviews, parallel ones included, are recorded when it starts, and repair waits for their results;
   - an uncollectable review is `MISSING` (not a pass) and closes the round;
   - a round with no collected result is not counted: it is redone, or else `MISSING` is shown at the stop and the claim reads "R8 未レビュー";
   - a late result belongs to its round and is handled at the next point where findings are handled. After the last round it is a known defect; after application it goes through R3;
   - each round's diff is recorded: a commit, or `git write-tree` after staging;
   - the last bullet names the review-count bound, distinct from R4's ECO limit;
   - the exclusive sentence names both bounds.
3. **`skills/eco-fix.md`:**
   - the description and step 2 carry the R7 stop at the limit: step 4 is done with the stop line as status note, and step 5 is not;
   - 3.5 cross-refers to the R7-exception path;
   - 3.6 records the round's reviews and their diff, and names `MISSING`;
   - the stop section lists known defects from either bound and `MISSING`, and asks the human to name the known defects accepted.
4. **`skills/eco-accept.md`:**
   - the precondition: known defects (R4 and R8) that the human named and accepted are not findings; unnamed ones are not accepted;
   - step 2: on the n/a path the content goes only in the n/a brackets;
   - step 3: 「分離起票予定」 is listed in the closure;
   - 4.5 (R4 and R8): the cheat-log entry goes in the accept commit, and a separate filing comes after step 5; its stop does not interrupt;
   - step 6: a wider trigger, and a destination for each kind.

**Not changed:**
- ECO-108's design (layers, 2 reviews, known defects at golden, converge's limit exception);
- R4's gates;
- the playbook;
- products' copies. ViewPrism2's ECO-147 already carries F4 to F8; its N1 and N2 are recorded in its cheat log. ViewTube receives the repaired text through ECO-109.

## 2. No-impact prediction (before manufacture; frozen)

- **The diff:** the three template files (29 insertions, 11 deletions by git), this order, the register and `method/improvements.md`.
- **Not touched:** tools, hooks, `.github`, the playbook and `.claude/skills` (none of the three files has a copy there).

## 3. Acceptance (conditions; frozen at filing)

- **V1**: condition = phrase counts at baseline `070d46e` 0 → 1:
  - R4 "「上限到達・golden 不可(R7)」と書いて止まる";
  - R8 "3.6 だけを通らない" and "結果を 1 つも回収できなかった回は見直しに数えない";
  - eco-fix "手順 1〜3.5 を通し、3.6 だけを通らない(R8)" and "受け入れる既知の欠陥は、人に名前を挙げてもらう";
  - eco-accept "名前を挙げなかったものは受け入れていない", "分離起票にするものは手順 5 の後に /eco-file で行う" and "既知の不正確とプローブで確かめられない所見は ECO の実施記録".
- **V2**: condition = no hunks outside these places:
  - R4 and R8;
  - eco-fix: the description, steps 2, 3.5 and 3.6, and the stop section;
  - eco-accept: the precondition and steps 2, 3, 4.5 and 6.

  The two skills' frontmatter parses.
- **V3**: condition = self-conformance exits 0 (observed before commit), and CI is green.
- **V4**: condition = manufacturer's calibration only.
- **V5** (not a closing condition): ViewTube's merge under ECO-109 uses the repaired text, and its independent review does not find these defects again.

## 4. Manufacture and the measurements before commit (2026-10-13, filing and manufacture in one commit)

**What was changed** (29 insertions, 11 deletions; 15 hunks, all at the V2 places):
- `change-management.md`: R4 and R8;
- `skills/eco-fix.md`: the description, steps 2, 3.5 and 3.6, and the stop section;
- `skills/eco-accept.md`: the precondition and steps 2, 3, 4.5 and 6.

**V1 result: PASS.** All eight phrases count 0 at `070d46e` and 1 in the tree (a count script reading the baseline with `git show`, the same phrases as §3; the round-3 reviewer counted them independently with `grep -oF`).

**V2 result: PASS.**
- The hunks are at the places named in §3 only.
- The two skills' frontmatter parses (name and description).

**V3** is recorded at closure, after observation.

## 収束 receipt (converge self-application)

- **判定: 未収束** (round 軌跡: 11→5→2; material 3→2→0).
  - The limit of 3 rounds was reached without two consecutive rounds of zero, and the user ruled "B": file now, with the round-3 repairs unreviewed.
  - The text is not reported as converged.
- **起動経路**: 自発 (rule text for process equipment is design synthesis). The unconverged design stopped for a ruling before filing.
- **Round reviewer**: one fresh context of the same model, resumed for each round; read-only.
- **DoD** (fixed before the draft):
  - ✔ D1 every rule has an event that always occurs: the limit, each review round, the stop, and each accept.
  - ✔ D2 every target exists (§0, with ViewPrism2 ECO-147 §8 as the source of the findings).
  - ✔ D3 one source per rule: R4 for the limit stop and R8 for rounds. eco-fix and eco-accept point to them.
  - ✔ D4 no conflict found in round 3 with R3 to R8, converge step 5, the operator-layer vocabulary or factory-delegate's range, except the two items repaired after it.
  - ✘ D5 the round-3 repairs are unreviewed (user ruling B).
  - ✔ D6 within ruling A: the template only; ECO-108's design kept.
- **周回** (each round's new findings):
  - **Round 1, 11 (3 material).**
    - The R7 stop at the limit was not in eco-fix.
    - The R8-only scoping left R4's known defects with no accept path.
    - A review that never returns had no rule.
    - 8 minor: the separate filing not recorded, step 6's trigger, silence about a known defect, the n/a slot written twice, no stop word or end state, an unfinished side-by-side, the exception's scope, and the diff id.
  - **Round 2, 5 (2 material).**
    - A round with no collected review ended R8 unreviewed.
    - The order's V1 and V2 no longer matched the text.
    - 3 minor: the timing of a late result, step 4's record dropped in the R7 stop, and the stop section not asking for names.
  - **Round 3, 2 minor.**
    - eco-fix 3.6 lacked the "not counted" rule.
    - The late-result rule disagreed with R7's exception.
  - **Repairs after round 3:** both minor items were repaired; they are unreviewed.
- **Claims checked:**
  - ViewPrism2 ECO-147 §8 and its cheat-log entry for N1 and N2;
  - operator-layer's `NORMATIVE_RULING`, `NONE` and `INSPECTION_MISSING`;
  - factory-delegate's lifecycle;
  - that no tool pins the changed text (as for ECO-108).
- **未収束事項**:
  1. The round-3 repairs are unreviewed (ruling B). ViewTube's review under ECO-109 reads this text next (V5).
  2. Each round found interactions with neighbouring rules. ECO-108 showed the same pattern, so more of that kind are possible.

## 5. Closure (2026-10-13, verified, manufacturer's calibration only)

- **Window.** Baseline `070d46e` → filing and manufacture `f7e860e` (diff_audit.head; **the window is closed**; the acceptance commit holds records only). Inside the window there are only the 6 allowed paths.
- **Acceptance results:**
  - **V1 result: PASS** (§4).
  - **V2 result: PASS** (§4).
  - **V3 result: PASS.** Self-conformance exited 0, observed before the commit. The push went through the pre-push witness. CI run 38404046432 was **success**.
  - **V4 result.** Manufacturer's calibration only; no inspector row. The round reviewer was context independence only.
- **V5** (not a closing condition): ViewTube's merge under ECO-109.
- **Recorded honestly.** The converge verdict stays 未収束 (11→5→2). The round-3 repairs are unreviewed, by the user's ruling B.

### 較正 receipt (/calibrate self-application - trigger ①: verified promotion; receipt_author_role = producer; documents only)

- **The claim (one sentence).** The product kit's R4, R8, eco-fix and eco-accept no longer carry the six defects ViewPrism2 ECO-147's review found in ECO-108's text. Those defects were:
  - the limit stop against R7;
  - the R7-exception return path;
  - late or missing review results;
  - the separate filing's order;
  - the n/a slot;
  - the destinations.
- **査定した主張と判定** (the claims assessed and their verdicts; measurement × evidence):
  - "The new phrases are in the four places": **observed / eligible**. Eight phrases count 0 at the baseline and 1 after. The manufacturer and the round reviewer counted them independently.
  - "No other text changed": **observed / eligible**. 15 hunks, all at the V2 places.
  - "The repaired text is consistent with its neighbouring rules": **read / conditionally eligible**.
    - Three rounds by a fresh-context reviewer found 18 items and resolved them.
    - Not measured: the two round-3 repairs, which are unreviewed. Not measured either: a reader of other equipment.
  - "Products no longer meet these defects": **not claimed; unknown**. The first evidence is V5, ViewTube's merge.
- **検出した計器欠陥と帰属** (instrument defects found, and attribution): 0.
- **宣言した検出力の限界** (declared limits of detection):
  - The counts show the text is there, not that it is acted on.
  - Interaction findings kept coming in every round.
  - The self-assessment is blind to the manufacturer's own wrong premises (playbook §9).
- **Battery, row by row:**
  - **Q1 asked.** The counts are mechanical; the verdicts are the manufacturer's.
  - **Q2 asked.** Known-bad is the baseline via `git show`; known-good is after.
  - **Q3 asked.** 8 phrases counted one by one.
  - **Q4 NA.** No declared input.
  - **Q5 asked.** CI success observed.
  - **Q6 asked.** The commit came after exit 0; the push went through the witness.
  - **Q7 NA.** No standing instrument was added.
  - **Q8 NA.** No preventive gate was added.
  - **Q9 asked.** The same script counted the baseline and after, in one run.
  - **Q10 asked.** The limits above.
  - **Q11 NA.** No input class needs to be separated.
- **What this closure does not support:**
  - any product effect (V5);
  - the unreviewed round-3 repairs;
  - ECO-108's own effect (EXP-20260828-03).

