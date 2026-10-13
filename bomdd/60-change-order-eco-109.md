# Change Order — ECO-109 (distribution of ECO-108 to the existing products: ViewPrism2 and ViewTube carry the default dispositions for limits and for independent-review findings)

> Instruction: user, 2026-10-13, "ECO-108 の配布の ECO を起票して" (file ECO-108's distribution ECO), after ECO-108 was verified.
> **Filing only.** Which products, and in what order, is a separate manufacture ruling (the pattern of ECO-075, ECO-081 and ECO-107).
> **TimetableAdv is not a target.** The user deferred it on 2026-10-13: the project is paused for model compute, with no restart date. When it restarts, its distribution covers ECO-106 and ECO-108 together; see EXP-20261013-01's resume condition.
> Records are English-primary (from 2026-10-12).

## Equipment

- Filing: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- Producer: EQ-004.
- Independent inspection: decided at the manufacture ruling. In each product, its own R8 applies to its own change.

## 0. Survey (basis of the filing; read at BomDD `21df6ed`)

ECO-108 changed the product-profile templates only:
- R4, R5 and R8 of `change-management.md`;
- `skills/eco-fix.md` steps 1, 2 and 3.6 and the stop section;
- `skills/eco-accept.md` steps 2, 4.5 and 6.

The products carry their own diverged copies, so the clauses have to be merged into each, as in ECO-107.

**ViewPrism2** (run by Claude; tree clean; HEAD `d8735ff`, 2026-10-13):
- **R4 limit.** `bomdd/change-management.md:38` has ECO-106's sentence ("ECO で決めた上限(時間・回数)を超える場合だけ"), with no default disposition when a limit is reached.
- **R8.** `bomdd/change-management.md:53-60` is ViewPrism2's R8 "セルフレビュー(出荷前レビュー)". It says "**未処置のスコープ内所見 0 になるまで golden に出さない**", with no bound and no layers. The same rule is restated at `:108` (scenario 3.3).
- **eco-fix.**
  - Step 2 (`.claude/skills/eco-fix/SKILL.md:31-32`) sends an exceeded limit to "延長の裁定".
  - Step 3.7 (`:58-66`) says "未処置のスコープ内所見 0 になるまで停止点に進まない".
  - The stop section (`:76-86`) lists nothing carried.
- **eco-accept.** Step 7 (`.claude/skills/eco-accept/SKILL.md:45`) re-lists scope-out items only.
- **R7.** R7 (`:44-45`) and eco-fix 3.5 hold "転写漏れ 0 になるまで golden に出さない". ECO-108's exception (R7 copy errors are repaired, not carried) applies here.

**ViewTube** (run by Claude from BomDD sessions and by Codex; tree clean; HEAD `dcf5c178`, pushed):
- **R8.** `bomdd/process/change-management.md:118-122` reads: "Open in-scope findings block golden and return to R5". There is no bound and no layers.
- **The R4 limit sentence** (`:81`, "when it would exceed a limit set in the ECO") has no default disposition.
- **eco-fix and eco-accept.**
  - `.agents/skills/eco-fix/SKILL.md:55-57` step 7 reads: "Resolve all in-scope findings before continuing".
  - `.agents/skills/eco-accept/SKILL.md:18` makes "zero open in-scope findings" a precondition of acceptance.
  - `AGENTS.md` rule 7 requires the review before golden.
- **Where the measured bound comes from.** ViewTube is the source of ECO-108's evidence. Its stop conditions were declared per ECO by the user's ruling, for example `change-impact/ECO-VT-182.yaml:583-594` ("停止条件を置いて進めて"): the second R8 round is the last, a blocking finding there narrows the claim, and material and minor findings are carried. They are not a standing rule, so each long review needed a new ruling. The distribution makes them standing.
- **Weight axis.** ViewTube's reviews classify findings by weight (blocking, material, minor). ECO-108's layers (substance, evidence, record) are a different axis, and the merge has to say how the two meet.
- **Constraints.** R9 (change-impact closure) and the ECO-VT-176 freeze on adding gates: the distribution adds no gate. Records are in English, and the eco-file step 4 rule is in place (ECO-VT-258).

## 1. Change request (frozen at filing; carried out per product at manufacture)

For each target product, one product-side ECO in that repository, under its own change management, records, gates and language:

1. **Limit default (R4 or its equivalent).**
   - Reaching a limit set in the charter or an ECO does not stop the work to ask for an extension.
   - The confirmed part is presented as a candidate for acceptance, the rest is recorded as known defects and known inaccuracies, the claim is narrowed, and this is reported at the next stop.
   - A diff that is not all green is not committed as a fix.
   - converge's own round limit stays a point where the work stops for a decision.
2. **Independent review (R8 or its equivalent).**
   - Layered default dispositions for in-scope findings:
     - substance → R5 repair; an unconfirmable finding is listed at the stop;
     - evidence → accepted if readable, otherwise `UNKNOWN`;
     - record → a known inaccuracy, except an overstated claim (narrow it) or a record that turns a check red (correct it).
   - At most 2 reviews. Equipment-independent inspection carries the 2.
   - Substance findings left at the last review are shown at golden as known defects, with the claim narrowed.
   - R7 copy errors are repaired, not carried.
   - Departures from the default are decided by the human at the next stop; until then the default applies.
   - The count restarts after a golden failure.
3. **eco-fix.**
   - Step 2: the limit default replaces the extension ruling.
   - The review step follows R8.
   - The stop lists what is carried: known defects, unconfirmed findings, known inaccuracies, `UNKNOWN` evidence, any unreviewed R7 repair and its side-by-side, and a last-round REJECT.
   - Step 1 defers R8 findings' probes to R8.
4. **eco-accept.**
   - Accepted known defects are written into the approval record.
   - They then take R3's two choices after acceptance.
   - They are re-listed with their destination.
   - ViewTube: the precondition "zero open in-scope findings" is reconciled with carried known defects.
5. **ViewTube's weight axis.** The merge states how blocking, material and minor map onto the layers and the bound. The manufacture decides how; ECO-VT-182's measured rule is the reference.

**Not changed:**
- product code, tests, BOM files, fixed oracles and CAD;
- the start-wait after filing;
- BomDD templates (done in ECO-108);
- TimetableAdv (deferred).

The per-product merge is design work. converge is applied at manufacture, per product, and its receipt goes into that product's ECO.

## 2. No-impact prediction (before manufacture; frozen)

- **BomDD side:** this order and the register at filing. At closure: the closure record, and a line in `method/improvements.md` against EXP-20260828-03 (the window opened in each product).
- **Product side:** per product, its change-management rules (R4, R5, R7 and R8 or their equivalents), eco-fix and eco-accept, and the product's own ECO records.
- **Untouched:** product code, tests, BOM files, fixed oracles, CAD and hooks. ViewTube validators are not touched; the gate freeze holds.

## 3. Acceptance (conditions; frozen at filing)

- **V1**: condition = in each target product, its ECO is applied under its own lifecycle, and its rules, eco-fix and eco-accept carry the clauses of section 1 (grep, per file, 0 → 1 for the new clauses and 1 → 0 for "until in-scope findings are 0").
- **V2**: condition = the product's own gates pass for each product commit, and that product's CI, where it has one, is green. For BomDD's own commits, self-conformance exits 0 and CI is green.
- **V3**: condition = each product's ECO records how its own conflicting text was reconciled. That covers ViewPrism2's scenario 3.3 line, R7's exception, ViewTube's eco-accept precondition and its weight axis. The independent review in each product attacks those points.
- **V4**: condition = EXP-20260828-03's window is opened in each target product (the start commit recorded in improvements.md).
- **V5** (not a closing condition): EXP-20260828-03 ② and ③ in each product's next review series.

## /preflight receipt (start path: manual — the user's instruction read as the start artifact)

- **Classification**: filing of a distribution ECO (survey; no product change at filing).
- **Baseline `21df6ed`**: **confirmed** (HEAD; the tree is clean).
- **Next number 109**: **confirmed** (the last register entry and the last order are ECO-108).
- **The product texts listed in section 0**: **confirmed** (read at ViewPrism2 `d8735ff` and ViewTube `dcf5c178`; both trees clean).
- **TimetableAdv**: **out of scope** by the user's deferral (2026-10-13); not read.
- **Start decision**: **PROCEED_WITH_LIMITS** (filing only; manufacture waits for the ruling on products and order).

## 4. Manufacture (2026-10-13; manufacture ruling "A": both products, ViewPrism2 first)

**ViewPrism2 ECO-147** (applied `504921a`):
- filed `f697a82`, fix `b63897a`, pushed;
- mechanical acceptance 4 points green;
- independent review: round 1 FAIL (9 findings, repaired), round 2 PASS with 2 minor carried as known defects (N1, N2), accepted by the maintainer and recorded in its cheat log;
- six findings were also in the template, which led to ECO-110 (the user's "A": repair the template before ViewTube).

**ViewTube ECO-VT-260** (applied `9074b831`):
- filed `831ae8cb`, probe `694352e2`, fix `1453401c`, pushed;
- R8 ran under the rule it writes: round 1 FAIL (2 blocking, 6 material, 4 minor; repaired), round 2 FAIL with one blocking record finding corrected and three minor substance findings carried as KD-260-1 to 3, named and accepted by the user (CHEAT-D10-028);
- the validator's "open findings must be 0" is met by a register convention: only undisposed findings count, and carried known defects are listed by id;
- two findings are also in the template (the narrow substance definition, R260-F2; partial naming at golden, KD-260-3), which lead to ECO-111 (the user's "A").

## 5. Closure (2026-10-13, verified for ViewPrism2 and ViewTube)

**Window.** Baseline `21df6ed` → filing `070d46e` (diff_audit.head; the acceptance commit holds records only). Inside the window there are only the order and the register.

**Acceptance results:**
- **V1: PASS** for both targets.
  - Each product ECO is applied under its own lifecycle.
  - Its rules, eco-fix and eco-accept carry the clauses: ViewPrism2's count script showed 6 new phrases 0 → 1 and 3 old ones 1 → 0; ViewTube's probe showed RED 14/14 → GREEN 14/14.
  - The "until in-scope findings are 0" rule is gone in both.
- **V2: PASS.** Each product commit passed its own gates:
  - ViewPrism2: validate_bom, and the lifecycle self-test after acceptance;
  - ViewTube: the commit gate, the release-workflow validator and self-test, and the X1 replay at acceptance (REPLAY_CLEAN).

  Neither product has CI. BomDD's commits had self-conformance exit 0 and CI success.
- **V3: PASS.** Each product ECO records how its conflicting text was reconciled, and its own independent review attacked those points:
  - ViewPrism2: scenario 3.3, R7's exception, the Codex second opinion, no equipment tier;
  - ViewTube: the eco-accept precondition, the weight axis, the validator's zero rule, the stabilization carve-out, rule 7.
- **V4: PASS.** EXP-20260828-03's windows are open from ViewPrism2 `b63897a` and ViewTube `1453401c` (recorded in improvements.md).
- **V5** (not a closing condition): EXP-20260828-03 ② and ③ in each product's next review series.

Register: `filed → verified`; head frozen. Manufacturer's calibration only on the BomDD side.

### 較正 receipt (/calibrate self-application - trigger ①: verified promotion; receipt_author_role = producer; records only on the BomDD side)

- **The claim (one sentence).** ECO-108's default dispositions are in ViewPrism2's and ViewTube's process documents. Both changes were accepted by their users with their known defects named. Each product's own gates passed.
- **査定した主張と判定** (the claims assessed and their verdicts; measurement × evidence):
  - "The clauses are in the two products": **observed / eligible**. ViewPrism2's count script (0 → 1, 1 → 0) and ViewTube's probe (RED → GREEN, with controls) can each fail on their own.
  - "Both are applied on the user's acceptance": **observed / eligible**. Register status and accept commits with parsed trailers (`504921a`, `9074b831`).
  - "The product gates passed": **observed / eligible**. The gates ran at each commit; ViewPrism2's 4 points ran twice, on the first and the final text.
  - "The bound reduces record-layer corrections in products": **not claimed; unknown** (EXP-20260828-03).
- **検出した計器欠陥と帰属** (instrument defects found, and attribution): ViewTube's `validate_process.py` enforces "open findings = 0". It is not a defect of the instrument, but it forced earlier relabelling. The register convention resolves the conflict without changing the instrument.
- **宣言した検出力の限界** (declared limits of detection):
  - The counts and the probe show the text is there, not that it is acted on.
  - Both products' reviews were context independence of the same model family.
  - Known defects are carried in both products. They are named, not resolved.
  - The self-assessment is blind to the manufacturer's own wrong premises (playbook §9).
- **Battery, row by row:**
  - **Q1 asked.** The counts are mechanical; the verdicts are the manufacturer's.
  - **Q2 asked.** Known-bad: each product's baseline. Known-good: after.
  - **Q3 asked.** Per phrase and per check.
  - **Q4 NA.**
  - **Q5 asked.** BomDD CI observed; the products have no CI and their gates ran.
  - **Q6 asked.** Every commit came after an observed passing check.
  - **Q7 NA.**
  - **Q8 NA.**
  - **Q9 asked.** The same script or probe was used before and after.
  - **Q10 asked.** The limits above.
  - **Q11 asked.** The products differ, so the results are reported per product.
- **What this closure does not support:**
  - any effect on review rounds (EXP-20260828-03);
  - the carried known defects;
  - TimetableAdv (deferred).

