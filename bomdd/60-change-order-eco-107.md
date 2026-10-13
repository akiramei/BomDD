# Change Order — ECO-107 (distribution of ECO-106 to the existing products: TimetableAdv, ViewPrism2 and ViewTube carry its wording on who decides derived-layer choices) — filed only

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
