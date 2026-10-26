# Change Order — ECO-116 (distribution of ECO-115 to the existing products: each product's receiving side decides from the records alone whether a delivered individual enters Phase 5)

> Instruction: user, 2026-10-26, "ECO-115 の配布 ECO を起票して" (file ECO-115's distribution ECO), after ECO-115 was verified (`ef1506a`).
> **Filing only.** Which products, and in what order, is a separate manufacture ruling (the pattern of ECO-075, ECO-081, ECO-107 and ECO-109),
> together with the human items of §1 B.
> **TimetableAdv is not a target**: it stays deferred as in ECO-109 (the user's deferral of 2026-10-13); not read. When it restarts, its
> distribution covers ECO-106, ECO-108 and ECO-115 together (EXP-20261013-01's resume condition, extended by this order).
> Cut-off ruling: user, 2026-10-26, "A" after loop 1 ended unconverged (23→6→2; material 11→1→0): **adopt the design with round 3's two
> minor findings repaired, and file it.** The repairs were not reviewed by a further round; the verdict under the converge rule stays
> unconverged (receipt, loop 1).
> Records are English-primary.

## Equipment

- Filing: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- producer: EQ-004
- Converge round reviewer: a fresh context of the same model (context independence), read-only.
- Independent inspection: decided at the manufacture ruling. In each product, its own review rule (R8 or its equivalent) applies to its own change.

## 0. Survey (basis of the filing; `bomdd/reports/eco-116-advance-decision-distribution/survey.txt`, read at BomDD `ef1506a`)

ECO-115 changed the method's text and templates only (ECO-115 M1): playbook §1 (one line), §4.4's new item "前進の判定", §6.1 (one line), the
per-ID-table item's `on_fail` sentence; `33-control-plan.yaml`, `50-as-built.yaml`, `40-work-order.md`; `improvements.md`. A product decides by it
only after its own BOM, records and procedure are within the decision's inputs (ECO-115 L5: "in both products every decision is `input-defect`
until distribution migrates them"). `survey.py` applies ECO-115's I3a structure and I2 checks (the rehearsal code the closure verified) to each
product's M-BOM and Control Plan at its HEAD, and reads its work order and newest As-Built entry:

- **ViewPrism2** (`504921a`, tree clean): **26 defects** (control-plan-fix 19, bom-fix 7) — `approver` outside I2 on 17 named rows (`maintainer`
  12, absent 3, `automated+maintainer` 1, `factory self-acceptance(最終確認は maintainer)` 1), 6 units with empty `acceptance_refs`, no
  `check_mapping`, no `mbom.assembly`, one `on_fail` with the key `dependency-update` (value `human-approval`); 44 units, 65 rows, 50 named. The
  work order has no valued frozen-revision line. **Its `50-as-built.yaml` is a legacy mapping, not the template's entry list** (`as_built:` holds the
  loop V1-V4 records; `survey.py` reports "no entry" for that reason), last changed at ECO-072 (`9097799`): ECO deliveries are not recorded there.
  ECO deliveries go through `eco-fix` and `eco-accept` (`.claude/skills/`) with the manufacturing AI in the same session; `eco-fix` 3.1 runs
  `bomdd/cp_results.py`, a per-row classifier the user ruled is **not a decision** (ECO-143, ruling A; ECO-115 B3); its stored results name no
  measured unit (B3). ViewPrism2's ECOs routinely change its own Control Plan or M-BOM in their fix commits (for example ECO-143 `391588d`,
  ECO-145 `491d2c1`).
- **ViewTube** (`a6314a87`; its untracked `product/` is not touched): **11 defects** (control-plan-fix 10, bom-fix 1) — `approver` outside I2 on 9
  named rows (`user` 5, and four free-text forms such as `automated + user for visible interaction` and `user after self-golden and fresh-context
  review`), no `check_mapping`, no `mbom.assembly`; 12 units, 41 rows, 28 named. Its Control Plan parses at HEAD (ECO-VT-268). Its CP values are
  written by generator tools (`bomdd/tools/build_phase3.py:340`, `build_loop2.py`), so a hand migration is undone by a regeneration unless the
  generators change too; 32/33/34/40 and the change-management files are `protected_paths` (`process-transplant-policy.yaml`). The work order has no
  valued frozen-revision line; the newest As-Built entry (`AB-capa-vt-001-release-gate`) has none of `frozen_commit`, `delivered`, `work_ref`, refs
  in I2's form, decision records. Release work orders select one Acceptance route with at most one canonical full-suite execution
  (`bomdd/process/change-management.md:18`); `AGENTS.md` rules 11-13 keep inspection, disposition and recovery steps that are not independently
  qualified with the user ("stabilize before automating"). Adding a check is under the user's standing gate freeze (ruling "C" on ECO-VT-176).
  Change-impact records are YAML and exist for UI changes only (`AGENTS.md` rule 10). Whether its evidence names the measured unit is not
  measured (ECO-115 L5).
- **MoviePad-Remake** (`b2e19a0`, local only; the experiment product of EXP-20261024-01): **0 defects** — its Control Plan carries
  `check_mapping` as ECO-115's pilot; the work order's line names `bom-v5`; the newest As-Built entry has `frozen_commit`, `delivered` and refs in
  I2's form, but no `work_ref` and no decision records; its comparator stamps the measured unit (`MEASURED_ON`). Two rows (`CP-BUILD-001`,
  `CP-SELF-ACCEPTANCE-001`) have no check in the evidence yet (decided: `inspect.py` writes them, carried to delivery 3). Its canonical method is
  the vendored `bomdd-kit/` (`CLAUDE.md`, `AGENTS.md`: a frozen snapshot versioned by `bomdd.lock`), which predates ECO-115. Its `ROUTE-INSPECT`
  runs the fixed oracle's runner. BomDD keeps the whole repository as a bundle that is remade when BomDD's records cite new commits
  (`bomdd/reports/exp-20261024-01/README.md`).

## 1. Change request (frozen at filing; carried out per product at manufacture)

For each target product, one product-side ECO in that repository, under its own change management, records, gates and language.

### A. What each product ECO carries (from ECO-115; each item cites its clause)

1. **The BOM within the decision's inputs: every check of I2 and I3a** — both files parse; unit and row IDs unique; every unit with a non-empty
   `acceptance_refs`; `mbom.assembly.acceptance_refs` present (empty only with `assembly_reason`); at least one row named; every named row present
   and not `retired`; `approver`, `on_fail`, `status` and `check_mapping` within I2. Migration decides about the BOM, not names (L5), under L5's
   two rules, quoted: **"ViewTube's reviewer or inspector approvals are not `approver` values under I2; at migration they belong to independent
   inspection"**, and **a row the factory's self-acceptance carried ("CP-L1-SMOKE") is given an automated part the receiving side runs** (or
   loses its automated part). The choices are the derived layer's: the orchestrating AI decides and records each changed row and unit with its
   reason (ECO-106).
2. **Instruments name the unit they measured (I4, D1 test 1; L3).** Each instrument writing evidence for a counted row writes the `identity` its
   format's `check_mapping` declares. Until it does, every counted row it measures is `unmeasurable` and the decision holds; the product ECO says
   which instruments change and which rows wait.
3. **The records (I1, I2, I4, D4, D5).** Each delivery's As-Built entry, in the template's entry-list form, carries `work_ref`, `frozen_commit`,
   `delivered`, the three refs in I2's form, the decision records (`source: decision`, with D4's `result`), `advance_decision` with D5's
   `sequence`, `routes_done` and `row_changes`. The work order carries the frozen-revision line and, where wanted, the bounds line, with the
   line's literal key as written in I2 (a machine key) at the start of a line, in a Markdown file.
4. **The freeze precedes the delivery (I3a).** The M-BOM and Control Plan at the issue commit equal those at `frozen_commit`, and the delivery's
   copies equal them; so an ECO's own changes to its BOM are committed at or before the frozen revision and the issue, apart from the factory's
   delivery commit. The product ECO records how its ECOs keep this.
5. **The receiving step (I0, D0).** Before golden and before the designer side runs the fixed oracle, the orchestrating AI, in a context other
   than the factory's, creates the As-Built entry, applies I3a, runs the counted rows' instruments on `delivered` (the factory's own runs are not
   a pass, B2), writes the decision records and
   `advance_decision`, and reads the work's sequence (D5: convergence, control, the control review). The product ECO names the step and how its
   receiving context is kept apart from the manufacturing one where the same AI manufactures.
6. **D5's default at a bound (D5; §8.5's declared departure).** At a bound the work stops without advancing and enters §13's pending human
   disposition, which departs from the products' limit default (ECO-108: accept with known defects; ViewPrism2 ECO-147, ViewTube ECO-VT-260). The
   product ECO records how the two meet.

### B. Points known at filing, per product, and who decides them at manufacture

| Product | Point | Who decides |
|---|---|---|
| ViewPrism2 | the As-Built moves from the legacy mapping to per-delivery entries (A3) | the AI, recorded (proposed: new entries below the legacy records, the legacy mapping kept) |
| ViewPrism2 | where the issued work order of an ECO delivery is (L5, left open by ECO-115; A3) | the AI, recorded (proposed: a per-ECO Markdown work order issued at a commit after the ECO's own BOM changes, which may be later than its filing, named by `work_order_ref`) |
| ViewPrism2 | the receiving step's place (A5) | the AI, recorded (proposed: between `eco-fix` and golden, in a fresh context) |
| ViewPrism2 | whether the decision is enforced mechanically, given the user's ECO-143 ruling A (`cp_results.py` is not a decision; ECO-115 D3) | **the human** |
| ViewPrism2 | how the known-defect acceptance meets the decision's hold, which only a new delivery lifts (ECO-115 D3, L6, the user's "2:A") | **the human** |
| ViewTube | whether and how the decision runs under `AGENTS.md` rules 11-13 and the stabilization section — the counted rows' instruments, `unmeasurable` routed to recovery, any extra execution (A5) | **the human** |
| ViewTube | any mechanical enforcement (a new check under the gate freeze, ruling "C" on ECO-VT-176) | **the human** (the exception ruling) |
| ViewTube | how the known-defect acceptance meets the decision's hold | **the human** |
| ViewTube | the migration against the generator tools and the protected paths (A1) | the AI, recorded (the generators' inputs change with the files, or the ECO records why not) |
| ViewTube | the work order's home for ECO deliveries that are not releases (A3, A5; change-impact YAML cannot carry the line, rule 10) | the AI, recorded |
| MoviePad-Remake | the vendored `bomdd-kit/` (its canonical method) predates ECO-115: re-lock it to BomDD at or after `ef1506a`, or record an exception that cites BomDD's playbook — the experiment's method version | **the human** |
| MoviePad-Remake | the receiving step's order inside `ROUTE-INSPECT`, before the fixed oracle's reading (A5) | the AI, recorded |
| MoviePad-Remake | whether the decision is enforced mechanically | the AI, recorded (no user ruling stands against it) |
| all | D5's stop default against the product's limit default (A6) | the AI records the reconciliation; where it changes text the user approved (ECO-147, ECO-VT-260), **the human** |

**Not changed:** product code, tests, fixed oracles, CAD and hooks (except an instrument's stamp under A2, which is a product ECO's own change);
BomDD's method text and templates (done in ECO-115); TimetableAdv (deferred).

The per-product migration is design work. converge is applied at manufacture, per product, and its receipt goes into that product's ECO (as in
ECO-109). This filing's own receipt is below: it covers the filing's design (what each product ECO carries and who decides what), not any
product's migration.

## 2. No-impact prediction (before manufacture; frozen)

- **BomDD side:** this order, the register and `bomdd/reports/eco-116-*/` at filing, and a note on EXP-20261013-01 in `method/improvements.md`
  that TimetableAdv's resume scope includes ECO-115. At closure: the closure record, a re-run of `survey.py`, a line
  in `method/improvements.md` (a record of the products reached; EXP-20261026-03 reads from their deliveries), and MoviePad-Remake's bundle remade in
  `bomdd/reports/exp-20261024-01/` when MoviePad-Remake's ECO adds commits BomDD's records cite.
- **Product side:** per product, its Control Plan and M-BOM (A1), the instruments that stamp evidence (A2), its As-Built and work orders (A3), its
  routing or change-management (A4, A5, A6), its generators where they write the BOM (ViewTube), its vendored kit where the human so rules
  (MoviePad-Remake), and the product ECO's own records.
- **Untouched:** product code and tests apart from A2's stamp, fixed oracles, CAD, hooks; ViewTube's validators (the gate freeze) unless the user's
  exception ruling says otherwise; ViewTube's untracked `product/`; nothing is pushed in ViewTube by this ECO without the user's word.

## 3. Acceptance (conditions; frozen at filing)

required_gates: [V1, V2, V3]

**Gated:** V1, V2, V3. **Not a closing condition:** V4.

- **V1 — the inputs.** For each target product, after its ECO is applied, `survey.py` (frozen in
  `bomdd/reports/eco-116-advance-decision-distribution/`, with `--work-order <product>=<path>` naming the home the product ECO chose) reports
  **0** I3a/I2 defects and a valued frozen-revision line. Known-good / known-bad at filing: MoviePad-Remake (0 defects, a valued line) against
  ViewPrism2 and ViewTube (26 and 11, no valued line).
- **V2 — the gates.** The product's own gates pass for each product commit, and its CI, where it has one, is green; BomDD's own commits pass
  self-conformance and CI.
- **V3 — the decisions recorded and attacked.** Each product ECO records A1-A6 for its product (each changed row and unit with its reason; the
  stamped instruments; the records' and the work order's form; how the freeze precedes the delivery; the receiving step and its context; D5's
  default against the limit default) and the human's rulings on its §1 B items, quoted; the product's own independent review (R8 or its
  equivalent) attacks those points, as in ECO-109.
- **V4 (not a closing condition).** The product's next delivery is decided through the receiving step, its As-Built entry carries A3's fields and its
  `advance_decision` is recorded; EXP-20261026-03 (D5's bounds on real works) reads from it.

## /preflight receipt (start path: manual — the user's instruction read as the start artifact)

- **Classification**: filing of a distribution ECO (survey; no product change at filing).
- **Baseline `ef1506a`**: **confirmed** (HEAD; the tree clean apart from this filing's files).
- **Next number 116**: **confirmed** (the last register entry and the last order are ECO-115).
- **The product states in section 0**: **confirmed** (`survey.py` at ViewPrism2 `504921a`, ViewTube `a6314a87`, MoviePad-Remake `b2e19a0`, read
  with `git show` only; the reviewer of round 1 re-ran it byte-identical and read the cited files).
- **TimetableAdv**: **out of scope** by the deferral of ECO-109; not read.
- **Start decision**: **PROCEED_WITH_LIMITS** (filing only; manufacture waits for the ruling on products, order and §1 B's human items).

## 収束 receipt (converge self-application)

### Loop 1 (filing design; the user's instruction of 2026-10-26; limit 3 rounds)

- **判定: 未収束** (round 軌跡: 23→6→2; material 11→1→0). Round 3 had new findings, so two consecutive zero rounds could not come within the
  limit of 3. **Ruling (user "A", 2026-10-26): cut-off adoption with round 3's two minor findings repaired**, then filing.
- **起動経路:** self-conformance C16 found the order needs a converge receipt (it carries ruling points: the manufacture ruling and §1 B's human
  items); the design was then put through the converge loop rather than reworded.
- **DoD (fixed before round 1):** (a) every clause of §1 traces to a clause of ECO-115 and adds no rule beyond it, except where ECO-115 left a
  point open (then a proposal decided per product); (b) every number and fact in §0 reproduces from `survey.txt` or the cited file:line/commit;
  (c) points that are the human's (ruling layer, user rulings, gate freezes) are separated from derived-layer choices, and the filing decides none
  of the human's; (d) standing constraints kept (ViewTube not pushed, its `product/` untouched, its gate freeze, TimetableAdv deferred);
  (e) each acceptance condition is measurable with an instrument that exists, and V1's instrument has a known-good / known-bad pair; (f) for each
  product the receiving step and the home of the frozen-revision line are named or flagged as decided at manufacture.
- **Round 1** (a fresh context of the same model, read-only; 23 findings, material 11). Material: V1 could not see a work-order home other than
  `40-work-order.md` (L1R1-01); V1's As-Built half had no known-good and could only be met by a decided delivery (02); ViewPrism2's As-Built is a
  legacy mapping, not "no entry" (03); a frozen revision at the filing commit makes every ECO that changes its own BOM an input defect (04);
  ViewTube's rules 11-13 were decided against in clause 5 (05); MoviePad-Remake's bundle refresh was not provided for (06); MoviePad-Remake's kit is
  its canonical method, not a record (07); D5 (ledger fields, control review, the stop default against the products' limit default) was not
  distributed (08); L5's two migration rules were not quoted (09); "outside the factory's context" is unworkable where the same AI manufactures
  (10); ViewTube's change-impact YAML cannot carry the line (11). Minor 12-23: an unsourced TimetableAdv figure, "on a clean tree" not in
  ECO-115, I3a's list incomplete, placements stated as facts, a MoviePad-Remake enforcement item, M1's list incomplete, V3 without an instrument,
  `affected_refs` and the improvements line, the gate freeze's source, ViewTube's generators and protected paths, the receiving step's order in
  `ROUTE-INSPECT`, TimetableAdv's resume scope.
- **Common cause removed before round 2:** the filing prescribed per-product mechanics that are manufacture decisions, and listed only the defects
  found instead of ECO-115's obligations. §1 is now A (the complete obligations, each citing ECO-115) and B (each point known at filing, per
  product, with who decides it). V1 is the I3a/I2 count and the frozen-revision line (with `--work-order` for the chosen home); the As-Built fields
  moved to V4.
- **Round 2** (the same reviewer, resumed): all 23 of round 1 resolved; **6 new, material 1** — L1R2-01 A5's "runs or reads" went beyond D0,
  which has the receiving side run the instruments (the factory's runs are not a pass, B2); minor: L1R2-02 the ViewPrism2 work-order proposal
  at the filing commit would force its post-filing BOM changes before the freeze (A4); L1R2-03 the register's no-impact text not revised with
  §2; L1R2-04 this receipt claimed the repairs before round 2 had confirmed them; L1R2-05 `survey.py` used an f-string form that needs Python
  3.12; L1R2-06 TimetableAdv's resume scope was extended only here, not on EXP-20261013-01. All six repaired before round 3.
- **Round 3** (the same reviewer, resumed; the last under the limit): all six of round 2 resolved; **2 new, both minor** — L1R3-01 the
  EXP-20261013-01 note widens the resume scope to ECO-115 but keeps the kit floor at ECO-098 (ECO-115's templates exist from `ef1506a`);
  L1R3-02 a mistyped `--work-order` key falls back silently to `bomdd/40-work-order.md` and can pass V1 on a stale line. Repaired under the
  ruling, not reviewed: the EXP-20261013-01 note now sets the kit at BomDD `ef1506a` or later; `survey.py` exits 1 on a key that names no
  surveyed product (checked: a mistyped key exits 1; the survey's output on the three products is byte-identical).
- **未収束事項:** none open in the text; the two round-3 repairs are unreviewed.
