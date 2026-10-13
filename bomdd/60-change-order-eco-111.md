# Change Order — ECO-111 (naming known defects at golden: IDs, what counts as naming, one recorded re-ask on zero or partial naming)

> Ruling: user, 2026-10-13, "A" on ViewTube ECO-VT-260. Accept it with KD-260-1 to 3 named, and repair the template for the two points found there that are also in the template:
> - R260-F2, the narrow substance definition;
> - KD-260-3's second half, partial naming at golden.
>
> Narrowing ruling: user, 2026-10-13, "B". Converge round 1 showed that the substance redefinition would need a redesign of R8:
> - its trigger;
> - a route to R4 for ruling-layer findings;
> - probes for text;
> - playbook §8.5.
>
> The ECO is narrowed to the naming of known defects; the substance redefinition is withdrawn and recorded.
>
> Converge ruling: the text did not converge in 3 rounds (10→4→2). The user ruled "B": file now, recording that the round-3 repairs are unreviewed.
> Records are English-primary. The template text stays in Japanese.
> **Filing and manufacture are in one commit** (documents only). Verified is recorded in a later commit, after self-conformance and the CI conclusion have been observed.

## Equipment

- Filing and manufacture: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- Producer: EQ-004.
- Converge round reviewer: a fresh context of the same model (context independence).
- Independent inspection: none planned (documents only; manufacturer's calibration only).

## 0. Basis

ViewTube ECO-VT-260's acceptance (`9074b831`) carried KD-260-3. Its second half is that when the human names some known defects at golden and is silent on others, the eco-accept precondition blocks with no route. The template (ECO-110) has the same rule, "名前を挙げなかったものは受け入れていない", and no route either (read at baseline `eac8c1a`).

## 1. Change request (documents only)

1. **`skills/eco-fix.md`, the stop section:**
   - known defects are listed with IDs;
   - an answer that points to a presented option (one that lists the IDs), by symbol or by word, names those IDs; an answer without IDs that points to no presented option (a free-text "全部OK") names nothing;
   - zero or partial naming gets one re-ask, listing the remaining known defects by ID. This happens once per golden answer, at this stop, and the question and answer are written into the record of the fix;
   - anything still unnamed is treated as not accepted (GF-*).
2. **`skills/eco-accept.md`, the precondition:** on zero or partial naming, it reads the re-ask record. If the re-ask was made, unnamed known defects are GF-*. If not, it does the re-ask as eco-fix's stop says.

**Not changed (withdrawn by ruling B, recorded in improvements.md with a reopening condition):**
- the substance definition and R8's trigger (round-1 findings F1 to F6);
- widening naming to `MISSING`, unconfirmable findings and the last-round REJECT (F8; the widening opened new gaps, N1 and N2, in round 2);
- the effect on EXP-20260828-03's layer ratios (F10).

## 2. No-impact prediction (before manufacture; frozen)

- **The diff:** the two skill files (6 insertions, 1 deletion), this order, the register and `method/improvements.md`.
- **Not touched:** change-management.md, tools, hooks, `.github`, the playbook and `.claude/skills`.

## 3. Acceptance (conditions; frozen at filing)

- **V1**: condition = phrase counts at baseline `eac8c1a` 0 → 1:
  - eco-fix "提示した選択肢(ID を列挙したもの)を指す答え" and "golden の 1 回の返事につき一度";
  - eco-accept "問い直しの記録を見る".
- **V2**: condition = hunks only in eco-fix's stop section and eco-accept's precondition; the frontmatter of both parses; change-management.md is unchanged.
- **V3**: condition = self-conformance exits 0 (observed before commit), and CI is green.
- **V4**: condition = manufacturer's calibration only.

## 4. Manufacture and the measurements before commit (2026-10-13)

**V1 result: PASS.** All three phrases count 0 at `eac8c1a` and 1 in the tree.

**V2 result: PASS.**
- 2 hunks, at eco-fix's stop and eco-accept's precondition.
- Both skills' frontmatter parses.
- `git diff -- method/templates/product-profile/change-management.md` is empty.

**V3** is recorded at closure.

## 収束 receipt (converge self-application)

- **判定: 未収束** (round 軌跡: 10→4→2; material 6→2→0).
  - The limit of 3 rounds was reached without two consecutive rounds of zero, and the user ruled "B": file now, with the round-3 repairs unreviewed.
  - Between rounds 1 and 2, the user narrowed the scope (ruling "B").
- **起動経路**: 自発 (rule text for process equipment). The design stopped for a ruling twice, once on scope and once at the limit.
- **Round reviewer**: one fresh context of the same model, resumed each round; read-only.
- **DoD** (fixed before the draft):
  - ✔ D1 the event always occurs: every golden answer that lists known defects;
  - ✔ D2 targets exist (eco-fix's stop, eco-accept's precondition);
  - ✔ D3 one source per rule: eco-fix's stop holds the re-ask, and eco-accept reads its record;
  - ✘ D4 the rounds 1 and 2 conflict findings were resolved by withdrawal, not repair; the round-3 repairs are unreviewed;
  - ✔ D5 within the narrowing ruling B.
- **周回** (each round's new findings):
  - **Round 1, 10 (6 material).**
    - The substance redefinition: R8's trigger leaves it inert for document-only ECOs (F1); "台帳" is ambiguous (F2); omissions are not covered (F3); ruling-layer findings go to R5 against R4 and R2 (F4); no probe form exists for text (F5); it conflicts with playbook §8.5 (F6). All withdrawn by ruling B.
    - Naming: zero names were not re-asked in eco-accept (F7); other stop items are accepted by silence (F8); what counts as naming was undefined (F9).
    - The open EXP windows (F10).
  - **Round 2, 4 (2 material).** The F8 widening opened N1 (eco-accept does not record or dispose the newly named kinds) and N2 (no GF route for them). N3 was the missing IDs, and N4 was the REJECT against its findings. The F8 widening was withdrawn, so N1, N2 and N4 became moot.
  - **Round 3, 2 minor.** M1: "全部" as a valid option choice against the example. M2: the re-ask could happen once per skill. Both were repaired; they are unreviewed.
- **Claims checked:**
  - ViewTube CHEAT-D10-028's KD-260-3;
  - the template's eco-fix stop and eco-accept precondition at `eac8c1a`;
  - R8's trigger (`src/`, `test/`), the basis of F1.
- **未収束事項**:
  1. The round-3 repairs are unreviewed (ruling B).
  2. F1 to F6, F8 and F10 are recorded, not resolved.

## 5. Closure (2026-10-13, verified, manufacturer's calibration only)

- **Window.** Baseline `eac8c1a` → filing and manufacture `fbc73b2` (diff_audit.head; **the window is closed**). Inside the window there are only the 5 allowed paths.
- **Acceptance results:**
  - **V1 result: PASS** (§4).
  - **V2 result: PASS** (§4).
  - **V3 result: PASS.** Self-conformance exited 0, observed before the commit. CI run 38417529182 was **success**.
  - **V4 result.** Manufacturer's calibration only.
- **Recorded honestly.**
  - The converge verdict stays 未収束 (10→4→2). The round-3 repairs are unreviewed (ruling B).
  - The substance definition, R8's trigger and naming beyond known defects are held in improvements.md with their reopening conditions.

### 較正 receipt (/calibrate self-application - trigger ①: verified promotion; receipt_author_role = producer; documents only)

- **The claim (one sentence).** At golden, known defects are listed with IDs. An answer that points to a listing option names them. Zero or partial naming gets one recorded re-ask, and anything still unnamed is GF-*. eco-accept reads the re-ask record.
- **査定した主張と判定** (the claims assessed and their verdicts; measurement × evidence):
  - "The phrases are present": **observed / eligible**. Three phrases count 0 at the baseline and 1 after.
  - "Nothing else changed": **observed / eligible**. 2 hunks; change-management.md is unchanged.
  - "The naming rule closes KD-260-3's route gap": **read / conditionally eligible**. The round-3 reviewer judged N1, N2 and N4 moot and found 2 minor defects, which were repaired and are unreviewed.
- **検出した計器欠陥と帰属** (instrument defects found, and attribution): 0.
- **宣言した検出力の限界** (declared limits of detection):
  - The counts show the text is there, not that it is acted on.
  - The items other than known defects (`MISSING`, unconfirmable findings, REJECT) are still accepted by silence; this is a recorded limit.
  - The self-assessment is blind to the manufacturer's own wrong premises. The withdrawn substance redefinition began from one such premise, about the scope of R8's trigger.
- **Battery, row by row:**
  - **Q1 asked.** The counts are mechanical; the verdicts are the manufacturer's.
  - **Q2 asked.** Known-bad: the baseline via `git show`.
  - **Q3 asked.** 3 phrases.
  - **Q4 NA.**
  - **Q5 asked.** CI success.
  - **Q6 asked.** The commit came after exit 0.
  - **Q7 NA.**
  - **Q8 NA.**
  - **Q9 asked.** The same counts were taken before and after.
  - **Q10 asked.** The limits above.
  - **Q11 NA.**
- **What this closure does not support:**
  - the held items;
  - any product effect (no distribution is filed; ViewTube's own text already routes partial naming as KD-260-3).

