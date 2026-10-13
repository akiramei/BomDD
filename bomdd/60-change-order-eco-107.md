# Change Order — ECO-107 (distribution of ECO-106 to the existing products: TimetableAdv, ViewPrism2 and ViewTube carry its wording on who decides derived-layer choices) — verified for ViewPrism2 and ViewTube; TimetableAdv deferred

> Instruction: user, 2026-10-13, "配布のECOを起票して" (file the distribution ECO), after ECO-106 was verified.
> **Filing only.** Which products, and in what order, is a separate manufacture ruling (the pattern of ECO-075 and ECO-081).
> Records are English-primary from 2026-10-12 (the user's ruling under ViewTube ECO-VT-253).

## Equipment

- Filing: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- Producer: EQ-004.
- Independent inspection: decided at the manufacture ruling.

## 0. Survey (basis of the filing; read at BomDD `207f56d`)

ECO-106 changed the product-profile templates only: R4 of `change-management.md`, `skills/eco-fix.md` step 2, `skills/converge.md` step 6, and the gate lines of `AGENTS.product.md` and `CLAUDE.product.md`. The existing products carry their own copies, which have diverged from the templates. A copy cannot be overwritten; the new clauses have to be merged into it.

**TimetableAdv** (run by Codex, gpt-6-astra and gpt-6.1-sol; the most derived-layer asks measured, 7 of 124):
- `bomdd/change-management.md` R4 has the same text as the template before ECO-106 ("設計判断・選択肢選び"); 41 lines differ from that template in the whole file.
- `.claude/skills/eco-fix/SKILL.md` differs in 40 lines and `.claude/skills/converge/SKILL.md` in 45 lines.
- `AGENTS.md:41` and `CLAUDE.md:65` have the old gate wording ("選択肢から選ぶ").
- **The kit is too old.** It has a frozen kit, `bomdd-kit/` (`bomdd.lock`: "original kit provenance + explicit three-file overlay; not a full upgrade", ECO113). The kit's playbook section 4.5 does not have the ruling-layer/derived-layer text that R4 points to.
- **Work is in progress in the tree.** The working tree has many modified acceptance artifacts (ECO-046 scene wiring by Codex; last commit 2026-09-28). A product ECO there cannot start until that work is committed, or unless the user directs otherwise.

**ViewPrism2** (run by Claude):
- `bomdd/change-management.md` has its own R4 ("gate 1 = 裁定(方針・要求・候補の裁定 — 選択肢から選ぶ)"); 310 lines differ from the template.
- `.claude/skills/eco-fix/SKILL.md` differs in 84 lines. There is no converge copy.
- `AGENTS.md:37` has the same gate wording as R4; `CLAUDE.md:16` names the two gates.
- No kit. The method is referenced as `../BomDD` (`AGENTS.md:49`, `CLAUDE.md:5`), so section 4.5 is reachable.
- The tree is clean; the last commit is 2026-10-05.
- The two derived-layer choices asked as gate 1 that were measured (ECO-095, ECO-141) are from here.

**ViewTube** (run by Claude from BomDD sessions and by Codex):
- No `change-management.md`. `AGENTS.md:81-86` defines the human gates: "decision gate — chooses requirements, design, or treatment". "Treatment" (the fix) is put in the human gate.
- Its own skills are in `.agents/skills/` (eco-fix among them). There is no converge copy.
- Records are in English.
- The tree is clean; the last commit is 2026-10-13. Its commit gate takes about 30 s to minutes.

## 1. Change request (frozen at filing; carried out per product at manufacture)

For each target product, one product-side ECO in that repository, under its own change management, records, gates and language:

1. **The gate rule.** Narrow the decision gate to the ruling layer (CAD, requirements, specification, E-BOM, K-BOM) and add ECO-106's sentences:
   - derived-layer choices (the fix option, the order and plan of manufacture and inspection, repairing its own output) and R3's scope cut are decided and recorded by the AI, and reported at the next stop;
   - they go back to the human only for a change to the ruling layer, section 4.5's three kinds, an exceeded limit, or mixing a separate problem into the current ECO.

   Where:
   - TimetableAdv: R4, `AGENTS.md:41` and `CLAUDE.md:65`;
   - ViewPrism2: R4, `AGENTS.md:37` and `CLAUDE.md:16`;
   - ViewTube: `AGENTS.md:85`.
2. **eco-fix.** Merge ECO-106's step 2 (the manufacturer chooses, records the rejected options and the reason, and reports at the stop) into the product's own eco-fix. The product's own additions are kept.
3. **converge.** Merge ECO-106's step 6 where a copy exists (TimetableAdv).
4. **Section 4.5 reachable.** TimetableAdv's kit needs the playbook at ECO-098 or later. The overlay or upgrade is decided at manufacture; the lock records what was done.
5. **EXP-20261013-01.** The counting window opens in each product from its application commit.

**Not changed:**
- the start-wait after filing (ECO-106, ruling A);
- TimetableAdv's per-scene start ruling;
- product code and tests;
- the CAD repositories;
- BomDD templates (already done in ECO-106).

The per-product merge is design work. converge is applied at manufacture, per product, and its receipt goes into that product's ECO.

## 2. No-impact prediction (before manufacture; frozen)

- **BomDD side:** this order and the register at filing; at closure, the closure record and a line in `method/improvements.md` against EXP-20261013-01.
- **Product side:** per product, the gate lines, eco-fix (and converge in TimetableAdv), the product's own ECO records and, in TimetableAdv, the kit files and the lock.
- **Untouched:** product code, tests, BOM files, fixed oracles and CAD.

## 3. Acceptance (conditions; frozen at filing)

- **V1**: condition = in each target product, its ECO is applied under its own lifecycle, and its gate lines and eco-fix (and converge) carry the clauses (grep, 0 → 1, per file).
- **V2**: condition = section 4.5's ruling-layer/derived-layer text is reachable from each target product: in TimetableAdv the kit's playbook has it (grep) and the lock names the update; in ViewPrism2 and ViewTube through `../BomDD`.
- **V3**: condition = the product's own gates pass for each product commit, and that product's CI, where it has one, is green. For BomDD's own commits, self-conformance exits 0 and CI is green.
- **V4**: condition = the window of EXP-20261013-01 is opened in each target product (the start commit recorded in improvements.md).
- **V5** (not a closing condition): EXP-20261013-01's result.

## /preflight receipt (start path: manual — the user's instruction read as the start artifact)

- **Classification**: filing of a distribution ECO (survey; no product change at filing).
- **Baseline `207f56d`**: **confirmed** (HEAD; the tree is clean).
- **Next number 107**: **confirmed** (the last register entry and the last order are ECO-106).
- **The product copies and gate lines listed in section 0**: **confirmed** (read and diffed against the template at `41efd00`).
- **TimetableAdv's working tree**: **contradicted** for starting work there now (dirty, ECO-046 in progress). This limits the manufacture order, not the filing.
- **Start decision**: **PROCEED_WITH_LIMITS** (filing only; TimetableAdv waits).

## 4. Manufacture (2026-10-13; manufacture ruling "A": ViewPrism2 and ViewTube now, TimetableAdv after its ECO-046 work is committed)

**ViewPrism2 ECO-146** (`implemented`; golden n/a waits for the maintainer):
- filed `d20ad6d`, fix `c0f6237`, pushed;
- R4, `AGENTS.md:37`, `CLAUDE.md:16` and eco-fix step 2 carry the clauses (V1: 5 phrases 0 → 1);
- mechanical acceptance: build 0/0, Tests 977/977, Oracle 109 + skip 4, validate_bom 0-0;
- the CP-row table is unchanged from ECO-145;
- R8 not applicable (documents only).

**ViewTube ECO-VT-256** (`implemented`; acceptance waits for the user):
- filed `cad7be9b`, probe `05db9c3a`, fix `405ae3ca`, pushed.
- AGENTS.md item 1, R4 and eco-fix step 3 carry the clauses (probe: 5 of 5 RED → GREEN).
- **Rulings on the way:**
  - the user approved moving AGENTS.md's ownership from ECO-VT-065 to ECO-VT-256 ("A"). The ECO-VT-061 → ECO-VT-065 handoff was annulled and kept, in the ECO-VT-172 form;
  - the release-workflow self-test was rebuilt so that its handoff arms do not borrow that record, and a positive control was added.
  - The write was refused twice by the harness's automatic permission check ("audit tampering"). It went ahead after the user switched to manual approval.
- **Independent review R8, round 1: PASS.**
  - 0 blocking findings;
  - 4 material, repaired: the carve-outs for rule 11, the stabilization-first section, security treatment, and the ruling record;
  - F5 recorded as CHEAT-D10-027: five single-condition mutants of the ownership validator survive the self-test before and after alike.
- **Machine acceptance:**
  - the first supervised run had 12 failures in MCP and demo-curation tests while ViewTube.App and ViewTube.Mcp were running; asked under rule 12;
  - the exact retest the user chose was refused at preparation (the route is for invalid executions); asked again;
  - the user-authorized second full run, with both programs closed: 1268 / 1267 / 0 failed / 1 known skip, exit 9. This is the known form.
- **The new R4 applied to its own manufacture.** The order, the form of the self-test change and R3's cut were decided by the agent and recorded (ECO-VT-256 section 8f).

**TimetableAdv:** not started; its tree still holds ECO-046's uncommitted work.

**Acceptance so far:**
- **V1:** clauses present in both products (grep 0 → 1); the applied state waits for the user's acceptance of ECO-146 and ECO-VT-256.
- **V2:** section 4.5 is reachable through `../BomDD` in both products; TimetableAdv's kit is not yet updated.
- **V3:** each product commit passed its own gates; BomDD's own commits pass self-conformance and CI.
- **V4:** the windows of EXP-20261013-01 are open from ViewPrism2 `c0f6237` and ViewTube `405ae3ca` (recorded in `method/improvements.md`).

## 5. Product acceptance (2026-10-13; the user's answer "A": accept both)

- ViewPrism2 ECO-146 **applied** at `d8735ff` (golden n/a accepted).
- ViewTube ECO-VT-256 **applied** at `5971cef8`:
  - the four ownership rows went back to active declarers, with AGENTS.md to ECO-VT-061 (the ECO-VT-172 shape), and the cheat-log row was retired;
  - the X1 replay was REPLAY_CLEAN over the interval from `7b79469a`;
  - the validator and its self-test passed after the commit.
- **V1: met for ViewPrism2 and ViewTube.**
- **What remains for closure:**
  - TimetableAdv: a product ECO after its ECO-046 work is committed, with its kit at ECO-098 or later (V2);
  - V4 for TimetableAdv.

  ECO-107 stays `implemented` until then.

## 6. Closure (2026-10-13, verified for ViewPrism2 and ViewTube; TimetableAdv deferred)

**TimetableAdv deferred.** The user, 2026-10-13, verbatim: 「TimetableAdvは現在、ChatGPTのモデルの計算リソースの問題でプロジェクトが中断しています。再開の予定が立っていないので今回は見送ります。」 TimetableAdv is taken out of this ECO's targets.
- Its distribution, a product ECO plus a kit at ECO-098 or later, is recorded under EXP-20261013-01 with its resume condition: the project restarts.
- At that point a new distribution ECO is filed. This one is not reopened.

**Window.** Baseline `207f56d` → `cc765b3` (diff_audit.head; **the window is closed**; the acceptance commit holds records only). Inside the window there are only the allowed paths: this order, the register and `method/improvements.md`.

**Acceptance results:**
- **V1 result: PASS** for both targets.
  - ViewPrism2 ECO-146 applied at `d8735ff`; ViewTube ECO-VT-256 applied at `5971cef8`.
  - The clauses are present: grep 0 → 1, 5 phrases in ViewPrism2; in ViewTube, its probe's 5 boundary sentences.
- **V2 result: PASS** for both targets. Section 4.5's ruling-layer and derived-layer text is reachable through `../BomDD`, which both products name as their method. TimetableAdv's kit is not applicable now (deferred).
- **V3 result: PASS.**
  - Each product commit passed its own gates: ViewPrism2's pre-commit validate_bom; ViewTube's commit gate, R8, and the X1 replay at acceptance.
  - BomDD's commits had self-conformance exit 0 before each commit and CI success: filing run 38329450347; records runs 38338181380 and 38340487026.
- **V4 result: PASS** for both targets. EXP-20261013-01's windows are open from `c0f6237` (ViewPrism2) and `405ae3ca` (ViewTube).
- **V5** (not a closing condition): EXP-20261013-01's result.

Register: `implemented → verified`; head frozen. Manufacturer's calibration only on the BomDD side. ViewTube's own record carries its independent review.

### 較正 receipt (/calibrate self-application - trigger ①: verified promotion; receipt_author_role = producer; records only on the BomDD side)

- **The claim (one sentence).** ECO-106's wording on who decides derived-layer choices is in ViewPrism2's and ViewTube's process documents, both changes accepted by the user, and each product's own gates passed. TimetableAdv is deferred by the user.
- **査定した主張と判定** (the claims assessed and their verdicts; measurement × evidence):
  - "The clauses are in the two products": **observed / eligible**. Grep counts 0 at each product's baseline and 1 after. ViewTube's probe went RED before and GREEN after, with 2 controls that can fail.
  - "Both are applied on the user's acceptance": **observed / eligible**. The register status and the accept commits with parsed trailers (`d8735ff`, `5971cef8`); the user's answer "A" is recorded in each product.
  - "The product gates passed": **observed / conditionally eligible**.
    - ViewPrism2's 4-point mechanical acceptance was run once.
    - ViewTube's first supervised run failed 12 tests while its programs were running; the second run, with them closed, was in the known form.
    - Not measured: the cause of the first run's failures.
  - "The rule reduces derived-layer asks": **not claimed; unknown** (EXP-20261013-01).
- **検出した計器欠陥と帰属** (instrument defects found, and attribution): 0 on the BomDD side. ViewTube: five single-condition mutants of the ownership validator survive its self-test, before and after this work alike (CHEAT-D10-027). This is a pre-existing weakness of the product's instrument, recorded, not repaired here.
- **宣言した検出力の限界** (declared limits of detection):
  - The grep shows the text is there, not that an agent acts on it.
  - The products' copies were edited by the manufacturer of the template; ViewTube's change was reviewed in a fresh context of the same model family, which is context independence, not equipment independence.
  - TimetableAdv, the only GPT-run product, is not covered, so EXP-20261013-01 can no longer compare model families.
  - The self-assessment is blind to the manufacturer's own wrong premises (playbook §9); this receipt was written by the manufacturer.
- **Battery, row by row:**
  - **Q1 asked.** The counts are mechanical; the verdict sentences are the manufacturer's.
  - **Q2 asked.** Known-bad: each product's baseline. Known-good: after the fix. The labels were fixed in each order before manufacture.
  - **Q3 asked.** Each phrase is counted on its own, per product.
  - **Q4 NA.** No declared input.
  - **Q5 asked.** CI success observed for the BomDD commits. The product repositories have no CI; their commit gates ran.
  - **Q6 asked.** Every commit came after an observed passing check. One ViewTube commit attempt was refused by its gate (ownership); the record was corrected and the commit retried.
  - **Q7 NA.** No standing instrument was added on the BomDD side.
  - **Q8 NA.** No preventive gate was added.
  - **Q9 asked.** The same phrase lists were used before and after.
  - **Q10 asked.** The limits above.
  - **Q11 asked.** The two products differ in harness and gates, so the results are reported per product, not pooled.
- **What this closure does not support:**
  - TimetableAdv (deferred);
  - any effect on asks (EXP-20261013-01);
  - a comparison of model families, now not possible without TimetableAdv.

