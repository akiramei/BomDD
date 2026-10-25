# Change Order — ECO-115 (the advance decision: the receiving side measures the delivered individual per Control Plan row and decides from the records alone whether it may enter Phase 5)

> **Status: not filed — a held design draft, kept as a record.** User ruling "1:A 2:A 3:A", 2026-10-24: D3 is reverted to the ruling "2:A" (a hold is
> lifted only by a new delivery), and the design stays **unconverged** and on hold. It is to be tried on real per-delivery records in a re-manufacture of
> MoviePad by the full BomDD procedure (the user's AGREE, same day), and redesigned from that result. Nothing in this draft is in the method; it has no
> register entry, and the ECO number is reserved for it.
>
> **Redesign (user "2:A", 2026-10-24, after EXP-20261024-01's first trial):** the rules below are edited in place from MoviePad-Remake delivery 1's
> real records (B5); what changed and why is loop 4 of the receipt. Loop 4 ended unconverged (8→4); the user's "A" adopted it by cut-off with
> round 2's findings repaired. Still not filed: next it is checked on MoviePad-Remake's second delivery, and filing follows that.

> Ruling: user, 2026-10-24, "A" (split) after [ECO-114](../../60-change-order-eco-114.md)'s first design loop ended unconverged at its limit (26→8→8;
> material 20→3→4). Every material finding of rounds 2 and 3 was in the advance decision, and each was a case where the decision read a Control Plan
> field that today is free form, missing or bound to an occasion. This ECO carries the user's condition (ii) of ECO-114's "A":
> - **the Control Plan decides from the result of a work instruction, deterministically, whether the process may advance.**
>
> The common cause is removed first: **the decision's place in the process and its inputs with their values are fixed (I) before its rules (D)**, and
> anything outside them is a defect of the input, decided before any row. Rounds are counted afresh (scope changed, as in ECO-112/113); default rule.
> This ECO reads ECO-114's `mbom.assembly.acceptance_refs` (ECO-114 A2), and both change `33-control-plan.yaml`, so manufacture goes 114 then 115.
>
> Extension ruling: user, 2026-10-24, "A" after loop 1 ended unconverged (26→10; material 14→5) with ECO-114's loop 2 (18→12): extend both loops, with
> the common cause removed first — the rules are run as a rehearsal script on ViewPrism2's real data before the next round, so where they meet existing
> data and records shows up by execution (receipt, loop 2). Limit 3 rounds.
>
> Narrowing ruling: user, 2026-10-24, "2:A" after loop 2 ended unconverged (10→5; material 5→3, all where the decision met the change-management
> records around it): **the decision only decides whether the delivered individual enters Phase 5.** A hold is lifted only by a new delivery decided
> afresh; the known-defect acceptance stays outside the decision, as it is; the frozen revision is read from one field of the work order. Then extend
> (receipt, loop 3; limit 3 rounds).
>
> Records are English-primary. Manufacture waits for the user after the design converges.

## Equipment

- Filing and design: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- producer: EQ-004
- Converge round reviewer: a fresh context of the same model (context independence), read-only, resumed each round.
- Independent inspection: EQ-002 (Codex), because the change redefines what the method's acceptance decides (precedent: ECO-098).

## 0. Basis (measured; `bomdd/reports/eco-115-advance-decision/` and `bomdd/reports/eco-114-part-standard/`)

The files, their sha256 and the commands are in each folder's `README.md`. Method line numbers are at BomDD `ab87e48` (after ECO-114's
manufacture). ViewPrism2 at `504921a`; ViewTube at `fc35bf1d`, its newest control plan
revision that parses.

- **B1 — the completion report is a prose list; per-row records exist only in the As-Built.** `method/templates/40-work-order.md:69-74` (artifacts,
  self-acceptance log, cheat report, changed artifacts, provenance material). `50-as-built.yaml:32-40` holds per-CP records (`result: pass | fail |
  blocked | not-run` at `:37`) with the rule that each entry re-measures every CP of every unit's `acceptance_refs` on its own individual, regression
  included (ECO-088, `:32-34`). R-050 reads that `result` in the newest As-Built entry and passes only when every unit/CP pair has a `pass` row and no row
  is other than `pass` (`method/schemas/draft/ref-edges.draft.yaml:516-548`); its gate is acceptance.
- **B2 — the observations are the designer side's, and self-acceptance is not a pass.** Playbook §4.4 "製造より先に、設計者側で観測一式を作り凍結する"
  (`method/bomdd-playbook-v1.md:145`); §5.1 "自己受入緑≠合格" (`:482`). Phase 5 is the designer side's oracle pass/fail, variance, attribution and
  convergence (`:33`, §6.1 `:508-513`); the fixed oracle is designer-only (`41-fixed-oracle.yaml:4`).
- **B3 — a deterministic per-row classifier exists in one product, declared not to be a decision.** ViewPrism2 `bomdd/cp_results.py` (ECO-143) gives
  each row 違反 / 合格 / 測定不能 from the test results by trait, and splits rows without tests into 未実行(人の承認で検査) / 未実行(検査なし) by `depth`; a
  missing, unreadable or empty results file is a run-level 測定不能 with no row decided (`:18`). Its docstring says it is **not a decision** (ECO-143 gate ①
  ruling A). Its output names the results file by sha256 and its configuration and finish time, **not the commit or build measured**. The stored results
  finished 2026-10-13T21:06+09:00; `504921a` was committed 2026-10-13T21:15+09:00 — they were measured before that commit, on a tree no record names
  (`run_rehearsal.py` docstring). Playbook §4.4 keeps its per-ID table as input to the approver (`:176-183`).
- **B4 — the Control Plan fields a decision would read are free form or absent today** (`cp-fields.txt`, `inputs-outside-i2.txt`, ECO-114's `shapes.txt`):
  - ViewPrism2 (65 rows): `approver` `automated` 40, `maintainer` 13, none 8, `automated+maintainer` 3, `factory self-acceptance(最終確認は maintainer)` 1;
    `on_fail` 2 (one with an extra key `dependency-update: human-approval`); `when` 2 (both the scalar `acceptance`). 50 rows are named by some unit, of which
    18 fall outside I2 (`approver` 17, `on_fail` 1); 15 rows are named by no unit; 6 of 44 units have no `acceptance_refs`; the M-BOM has no key besides
    `manufacturing_units`; the Control Plan header has `depth_ladder`, `part_kind_gates`.
  - ViewTube (41 rows at `fc35bf1d`): `approver` `automated` 22, `user` 8, none 2, and 9 distinct prose values (four name an independent reviewer or
    inspector); `on_fail` 0; `when` 0. 28 rows are named by some unit, of which 9 fall outside I2 (`approver`); 13 named by no unit.
  - ViewTube's control plan at HEAD does not parse as YAML; it stopped at `cfd00433` (ECO-114 report `measurements.txt`).
    (Repaired since by ViewTube ECO-VT-268, applied `a6314a87`; this order's counts stay at `fc35bf1d`.)
- **B5 — the first per-delivery records (MoviePad-Remake, EXP-20261024-01 delivery 1; `rehearsal-moviepad.txt`).** The work order issued at `7824ba9`
  names the frozen revision as the tag `` `bom-v4` `` (written as Markdown code; the template says neither tag nor commit); `bom-v4` is `ca9319d`; the
  delivery is `f30d771`, whose M-BOM and Control Plan are byte-equal to `bom-v4`'s. The As-Built entry (`50-as-built.yaml` at `e1d71b3`) has
  `work_order_ref` as `<path>@7824ba9` (short), `mbom_ref` and `control_plan_ref` at the tag, no field holding the delivered commit, and one
  `test_evidence_refs` entry naming `compare.txt`; **`compare.txt` does not name the commit or tree it measured** (the trial's M1 link L4). 13 rows
  are counted; `CP-BUILD-001` and `CP-SELF-ACCEPTANCE-001` have no check in `compare.txt` (measured only by the factory's self-acceptance — the
  product's As-Built note said otherwise and was corrected, `5540a38`); `CP-HARNESS-SELFTEST-001` is named by no unit.

## 1. Change request — the rule register

The IDs below are this order's record. Every rule's canonical place is the new playbook §4.4 item "前進の判定"; the templates carry the fields with a comment
naming that item, and §4.4:178's sentence on `on_fail` refers to it instead of listing values.

### I — the decision's place and inputs (fixed before the rules)

- **I0 (place).** The decision sits between Phase 4 and Phase 5: at receipt of a delivery, before the designer side runs the fixed oracle and golden.
  It decides whether the delivered individual **enters Phase 5**. It decides the automated part of the Control Plan only; human judgement (golden, the
  human part of a row, the acceptance) stays in Phase 5, where its records are written (D4). §1's flow and §6.1 gain one line each naming it (M1).
- **I1 (exactly these inputs).** The decision reads the M-BOM and the Control Plan **at the revision frozen for the work**: the revision named by the
  work order's one line `- 対象 BOM tag/commit: <revision>` (`40-work-order.md:5`), which the orchestrating AI writes before manufacture (Phase 3 step
  6) as a tag or a commit. At receipt the receiving side resolves it to a commit and records that as the As-Built entry's `frozen_commit`; the decision
  reads the BOM at `frozen_commit` (a tag can move later; the commit it named at receipt cannot — B5's `bom-v4`). The work order is read **as issued** —
  at the commit the entry's `work_order_ref` names (`50-as-built.yaml:11`), never from the delivered tree, which carries its own copy — and the M-BOM
  and the Control Plan at `frozen_commit`, at the paths of the entry's `mbom_ref` and `control_plan_ref`; the delivery's copies are compared, not read
  (I3a). That line is the only part of the work order D0–D4 read; D5 also reads the bounds line `- 前進の判定の上限: holds <n>, decisions <m>`
  of the work's first issue (absent = the defaults of D5) and of this delivery's work order, and the work's earlier As-Built entries (those with
  the same `work_ref`: their decisions, `routes_done` and `row_changes`). It then reads:
  1. the M-BOM: every unit's `acceptance_refs`, and `mbom.assembly.acceptance_refs` with `assembly_reason` (ECO-114 A2);
  2. the Control Plan: its header `check_mapping`, and for each row named in 1: `id`, `status`, `approver`, `on_fail`;
  3. the As-Built entry the receiving side creates at receipt for this delivery: its `frozen_commit`, `work_order_ref`, `mbom_ref` and
     `control_plan_ref` (`50-as-built.yaml:11, :12, :14`), its `delivered` identity, its decision records (`test_evidence_refs` entries with
     `source: decision`, I4), and the evidence files they name — including the measured unit each evidence file names (`check_mapping`'s `identity`);
  4. the delivery's copies of the M-BOM and the Control Plan at the frozen revision's paths;
  5. git: the commits above and their ancestry, in the repository that holds the delivery (D requires git — L8).
  Nothing else enters: not the rest of the work order, the factory's report or self-acceptance, not `when`, `depth`, `verifies`, `characteristic`, `oracle`,
  `evidence_output_ref`, the work order's or Routing's copies of `acceptance_refs`. Every named row is counted at every delivery (ECO-088's
  re-measurement); `when` keeps its meaning for other occasions and is not read here.
- **I2 (closed values).**
  - `approver`: `automated` | `human:<role>` | `automated+human:<role>`.
  - `on_fail`: absent, or a map whose keys are among `red`, `unmeasurable` and whose values are among `product-fix`, `instrument-recovery`,
    `control-plan-fix`.
  - `status`: absent or `retired`.
  - `check_mapping`: a map from an evidence format name to `{row_key, outcomes, identity}` — `row_key` names how a check names its row: for the
    `xunit-v3` format, the trait whose value is the row (ViewPrism2: `cp`); for the `line` format, a regular expression with the named groups
    `outcome` and `row`, and every line it matches whole is a check (MoviePad-Remake's comparator: `(?P<outcome>[A-Z]+) (?P<row>\S+)(?: .*)?`);
    a check that names no row is a check no row owns. `outcomes` maps each of the format's outcome terms to one of
    `passed`, `failed`, `skipped`, `not-run`, and `identity` is a regular expression with the named groups `commit` and `tree` that finds, in an
    evidence file of that format, the unit the instrument measured (for example a line `MEASURED_ON <commit> <tree>` the instrument writes as it runs).
  - `delivered`: `{commit, tree}`, both 40-hex.
  - the frozen-revision line: a tag or a commit ID, written plainly or as Markdown code (the backticks are not part of it); `frozen_commit`: a
    40-hex commit ID; `work_order_ref`, `mbom_ref`, `control_plan_ref`: `<path>@<40-hex commit>`.
- **I3a (input check before running anything).** git is available (L8); the entry's `delivered` is within I2 and its `tree` is the tree of its
  `commit`; the entry's `work_order_ref` is within I2 and names a commit other than the delivered one; the entry
  has `frozen_commit`; the work order read at `work_order_ref` has exactly one frozen-revision line, and its value resolves to `frozen_commit`; the
  entry's `mbom_ref` and `control_plan_ref` name `frozen_commit`; `frozen_commit` is the work order's commit or an ancestor of it (the freeze
  precedes the issue), and the M-BOM and the Control Plan at the work order's commit are byte-equal to those at `frozen_commit` (no BOM change
  between the freeze and the issue, so a tag moved back to an older BOM is caught); the work order's commit is an ancestor of the delivered commit
  (with the clauses above, this makes `frozen_commit` an ancestor of the delivered commit and not the delivered commit — not checked again);
  the M-BOM and the Control Plan at `frozen_commit` parse; the delivery's copies of both are byte-equal to
  them, and a delivery without a copy at that path differs (a factory does not change its own acceptance — B2; all three products keep their BOM in
  the delivered repository);
  unit IDs and row IDs are unique; every unit has a non-empty `acceptance_refs`;
  `mbom.assembly.acceptance_refs` is present (empty only with `assembly_reason`); at least one row is named; every named row exists and is not `retired`;
  every value of I1 1-2 is within I2. Any failure makes the decision `input-defect`, listing each failure with its route (D2); nothing is run.
- **I3b (input check after the records).** Every counted row (D0) has exactly one decision record, and no decision
  record names a row that is not counted; every decision record has `cp_ref`, `evidence_path`, `evidence_sha256`, `format` and `observed_at`, with a
  `format` that `check_mapping` names. Any failure makes the decision `input-defect`, listing each failure; no row category is
  computed.
- **I4 (records).** The decision's records are the As-Built entry's `test_evidence_refs` entries with `source: decision`, one per counted row, with I3b's
  fields and, written after D2, `result` (D4). The unit an instrument ran on is read from its evidence (`identity`), not written into the record. Several rows may name the same evidence
  file. An instrument that produced no evidence still gets its record, naming the file it should have written, with `evidence_sha256: none` (D1 test 1
  then routes to instrument-recovery). Phase 5 adds its own entries (`source: phase5`) for the human parts. Each delivery has its own As-Built entry and
  is decided once (D3).

### D — the decision

- **D0 (who, in what order).** The orchestrating AI, in a context other than the factory's (playbook §9), at receipt: creates the As-Built entry and fixes
  `delivered`; applies I3a; takes the **counted rows** — every named row whose `approver` includes `automated`, with its automated part only; runs their
  instruments on `delivered`; writes the decision records (I4); applies I3b, D1 and D2; writes `advance_decision` into the entry: the result, for each
  counted row its category and the D1 test that decided it, and the rows not decided — human-only rows, the human part of mixed rows, and rows named by no
  unit and not in `assembly`.
- **D1 (row category; the first that holds).**
  1. `unmeasurable` (evidence) — the row's evidence file cannot be read, it holds no check at all, it holds a check whose outcome term is not in
     `check_mapping`'s outcomes for its format, its sha256 differs from the record, its format's `identity` finds in it no measured unit, more
     than one, or one other than `delivered`, or it holds a check whose outcome maps to `failed` and which no counted row owns (no row, or a row
     that is not counted) — the instrument reports a failure the decision cannot place, so no row it measured is taken as passed;
  2. `violation` — the evidence holds at least one check for the row (by `row_key`) whose outcome maps to `failed`;
  3. `unmeasurable` (skipped) — the evidence holds checks for the row and all map to `skipped` or `not-run`;
  4. `no-check` — the evidence holds no check for the row;
  5. `pass` — at least one check for the row maps to `passed`, and none to `failed`.
- **D2 (the result).** `input-defect` (I3a, I3b); otherwise `advances` when every counted row is `pass` — or, with no counted row, when every named row
  has a human part (all of it is decided in Phase 5); otherwise `holds`. A hold lists each non-`pass` counted row with its category and route: the row's
  `on_fail` value for `red` (when `violation`) or `unmeasurable` (when `unmeasurable`) where present; otherwise `violation` → product-fix,
  `unmeasurable` → instrument-recovery, `no-check` → control-plan-fix. An `input-defect` routes to the file that failed: control-plan-fix (Control Plan),
  bom-fix (M-BOM), work-order-fix (the frozen-revision line), record-fix (the As-Built entry), or product-fix (a delivery whose copies differ from the
  frozen revision). A row named by several units is one row, decided once. A row made `unmeasurable` by a failure no counted row owns (D1 test 1)
  routes to control-plan-fix whatever its `on_fail`: the failure is not the row's, and the fix is to give the failing check an owner row, after
  which a new delivery decides it as that row's `violation`.
- **D3 (what follows).** `advances`: the individual enters Phase 5, and the designer side runs it. `holds` or `input-defect`: the individual does not
  enter Phase 5 through D. Its routes are done and the result is a **new delivery** — a new commit and tree with its own As-Built entry and, where a
  Control Plan or M-BOM was fixed, a work order naming the new frozen revision — decided afresh. This holds for every route, including record-fix,
  work-order-fix and instrument-recovery, which change nothing the factory made: by the user's ruling "2:A" the same delivery is not decided again (L6).
  D has no other way past a hold. Whether a
  human may still take a held individual into Phase 5 (for example through the known-defect acceptance of ECO-108 / ECO-111, which works at golden and
  at the acceptance request) is outside D and is decided per product at distribution, together with whether D is enforced mechanically (ViewPrism2's
  ECO-143 ruling A is that product's). §4.4's per-ID table stays the approver's input (`:176-183`).
- **D4 (the As-Built's `result`).** The canonical category is in `advance_decision`. Each decision record's `result` (R-050's field) is derived from it in
  the existing vocabulary: `pass` → `pass`, `violation` → `fail`, `unmeasurable` → `blocked`, `no-check` → `not-run`. Phase 5's entries carry the human
  part's `pass` or `fail` as today. R-050 and ECO-088 are read at acceptance, after Phase 5: a human-only pair has its `pass` row only once Phase 5 has
  written it (`rehearsal-real.txt`: on ViewPrism2's migrated copy, 22 of 73 unit/CP pairs, 12 rows), and an entry whose decision held keeps its non-`pass`
  rows, which R-050 (b) reports at acceptance unless a product's named suppression is used.
- **D5 (a work's decisions over time — loop 6, 2026-10-26).** D decides one delivery; a work can be held and redelivered several times. A **work** is
  named by `work_ref` — the ECO or work order that started it — which every As-Built entry of the work carries; a process ECO that a control review
  files (below) continues the same work and keeps its `work_ref`, so a review does not start a new history or new bounds. At every decision after a
  work's first, the orchestrating AI reads the work's **ledger** (I1: the work's earlier As-Built entries) and writes two separate readings into
  `advance_decision.sequence` — **convergence** (is this work reaching `advances`?) and **control** (is the process that made and judged these
  deliveries working as designed?). They have different inputs and different consequences, and **counts are inputs to convergence only**.
  - **The ledger** (from records D already writes, plus three fields). Per counted row, its state at each decision of the work: **observed** —
    `pass`, `violation`; or **not observed**, with the reason — `unmeasurable`, `no-check`, or `nothing-measured` (an input defect measured no
    row). A hold whose every counted row is `unmeasurable` by D1 test 1 gives each row `unmeasurable` with its own cause, as D2 lists it, and is
    marked as having **measured no row**. Per decision, D2's causes, each with its kind — **row** (`<row>:<category>`) or **input**
    (`<route>:<message>`), following the decision's result, not the key's spelling — and its category (`violation`, `unmeasurable`, `no-check`,
    or `input`); an input cause may name the row it concerns (for example "a named row is retired"). The three fields: **`work_ref`** (above); **`routes_done`** — for each cause, the ref showing its route done since the decision
    where the cause last appeared (D3 requires it; the record makes it checkable); and **`row_changes`** — the rows the frozen Control Plan or
    M-BOM `removed`, `added` or `renamed` since the previous decision, each with the cause that routed it. A renamed row carries its states to
    the new rows, so splitting or renaming a row does not clear its history.
  - **Convergence.** `converged` when the newest decision advances; otherwise `open`; `bound-reached` when either bound is reached: **holds** —
    the work's holds that measured rows (default 3, the design loops' bound), and **decisions** — all its decisions, input defects included
    (default 5), so a loop that never measures a row is bounded too. The bounds are read from the **work's first issue** (the work order's
    bounds line, I1; absent = the defaults); a re-issue whose bounds line differs is control signal C6 (below), not a cause of the decision
    (D2 is unchanged), and the first issue's bounds still apply — a bound is not raised from inside the work. The playbook's loop rules apply here and only here,
    with one declared departure. §8.5 (`method/bomdd-playbook-v1.md:879-881`) asks for the default disposition to be declared in advance and
    names it: record the confirmed facts and the known inaccuracies, and accept. **D5 declares a different default — stop without advancing —**
    because D cannot accept a held individual (D3; the user's ruling "2:A": a hold is lifted only by a new delivery decided afresh): no further
    delivery is requested, the held individual stays out of Phase 5, and the open causes and the control reading are recorded and reported. What
    follows from the departure: unlike §8.5's default, the work stays stopped until someone disposes of it, which is §13's pending human
    disposition (`:1195-1198`), entered with the current state, the evidence still owed and the technical risk. A human may dispose (for example
    a new work with its own bounds, or the known-defect acceptance of ECO-108 / ECO-111, which is outside D). The bound is a fact about
    convergence: a work in control and one that is not reach it the same way, and the report carries the control reading, not the count, as the
    account of the process.
  - **Control**, from the ledger, never from a count:
    - **C1 persists** (owner: the route's owner — the factory for product-fix, the designer for instrument-recovery, the orchestrating AI for
      control-plan-fix, bom-fix and work-order-fix, the receiving side for record-fix) — a row is a `violation` and its last observed state was a
      `violation` (not-observed states in between do not break it); or a row is `unmeasurable` or `no-check` as at its last state other than
      `nothing-measured` (a decision that measured nothing does not break it either); or an input cause is in this decision and the previous one. Read with `routes_done`: *route done, cause not removed* (the fix did not work),
      *route not done* (D3 was not followed), or *unrecorded* (the entry has no `routes_done`, as in records written before this field).
    - **C2 returns** (owner: as C1) — a row is a `violation` after a `violation` and then a `pass`; or it is `unmeasurable` or `no-check` after
      that same state and then another, `nothing-measured` skipped (an instrument failure back after a repair); or an input cause that was absent
      in a later decision is back.
    - **C3 regression** (owner: the factory, whose self-acceptance did not catch it) — a row whose observed states are all `pass` is a
      `violation` now. Every counted row is measured at every delivery (I1, ECO-088), so a later violation on a row that once passed is always
      C2 or C3.
    - **C4 own parts fail twice** (owner: the orchestrating AI) — this decision and the previous one each have a cause whose **category** is not
      `violation` (`unmeasurable`, `no-check`, an input defect): records, instruments, the Control Plan or the work order keep failing, not the
      product. It reads the category, not the route, so a row whose `on_fail` routes a violation elsewhere still counts as the product's.
    - **C5 row set** (owner: the orchestrating AI) — a row `removed` or `renamed` with no control-plan-fix or bom-fix cause of the previous
      decision on that row (the row's own cause, or an input cause naming it); a row `added` with no such cause in the previous decision at all;
      or a row removed or renamed whose open `violation` or `unmeasurable` (its last state other than `nothing-measured`) is not the cause that
      routed the change — an open cause taken out of the counted set, or moved under a new name, under another row's route. A row changed under
      its own cause (a `no-check` row losing its automated part, a row split or renamed to fix its own finding) is a routine route, not a signal.
    - **C6 bounds changed** (owner: the orchestrating AI) — a delivery's work order carries a bounds line different from the work's first issue.
      The first issue's bounds still apply; the signal reports the attempt even when the delivery advances.
    No signal: `in-control`, however many holds the work has had (a hold with several causes that the next delivery clears; a row whose state
    changes from not observed to a product violation, as when an instrument repaired lets the product's own failure show). Any signal:
    `signals`.
  - **What follows.** `in-control` and below both bounds: D3 as written. `signals`: no further redelivery is asked for on the same causes; the
    orchestrating AI opens a **control review** — for each signal, which record, instrument, Control Plan row, route or work order failed, and
    why, with the signal's owner — and fixes what lies in the product's derived layer (a process ECO in the product, continuing the work: the
    Control Plan, an instrument, the routing, the work order), recording the decision and reporting it; a new delivery follows and is decided
    afresh. What lies in the method (a template, this rule) is filed as a method ECO or an OBS in `method/improvements.md`, not fixed and reported
    (AGENTS.md rule 1). The review is the AI's within the existing authority and does not by itself reach the human. At a bound the declared
    default applies, whatever the control reading.
  - **To the human — a judgement is asked only for a gap in the ruling layer** that the review finds and no existing rule resolves, which maps
    onto §4.5's three kinds: **a new promise** — two rows that alternate in order (one violated and the other passing, then the reverse, then
    back: marked mechanically as a candidate) because their promises cannot both hold, a contradiction in the requirements, the spec, the E-BOM
    or the K-BOM (OBS-20260922-01: a contradiction shows only as satisfying one promise breaking another), whose resolution changes a promise; or
    a product-fix the factory reports it cannot make without changing a promise — which reaches the review through the work order's blocker
    report (§4.5 P3, `40-work-order.md`), not through D's inputs; **a new function** — a fix that needs behaviour no requirement states;
    **underivable** — a row the derived layer cannot write from the ruling layer. The AI presents the decisions and causes that show it and the
    judgement needed. Whether a marked candidate is a contradiction is the review's finding, not the mark's. The only other thing that reaches the
    human is the bound's pending disposition above, under the existing loop rule.

### M — manufacture

- **M1 (scope).** Text and templates only: `method/bomdd-playbook-v1.md` §1 (one line), §4.4 (new item "前進の判定"; `:178` refers to it), §6.1 (one
  line; and D5 in §4.4's new item), `method/templates/33-control-plan.yaml` (I2's values on `approver`, `on_fail`, `status`; header `check_mapping` with `identity`; the `when`
  comment `:30` rewritten to say that `when` names further occasions on which a row is measured and does not take a named row out of the advance
  decision), `50-as-built.yaml` (`frozen_commit`, `delivered`, `source`, `format`, `advance_decision` with D5's `sequence`, `work_ref`,
  `routes_done`, `row_changes`, I4's record fields,
  D4's derivation, and comments on `work_order_ref`, `mbom_ref`, `control_plan_ref` giving I2's form), `40-work-order.md` (a comment on the
  frozen-revision line: a tag or a commit, resolved at receipt into the As-Built's `frozen_commit`, read by the decision as issued; and D5's
  optional bounds line with its defaults and the declared default disposition),
  `method/improvements.md`. No tool
  under `method/tools/`; R-050 and ECO-088's rule are unchanged (D4 keeps their vocabulary). Distribution to the products is a separate ECO; there,
  existing Control Plans and M-BOMs must be brought within I2/I3a before D runs (not lazy). The rehearsal scripts are evidence under
  `bomdd/reports/eco-115-*/`; the method does not ship them.

### Declared limits

- **L1 (D1, mapping).** D1 reads which checks `row_key` assigns to a row and what `outcomes` says a term means; it checks neither (a mapping `Error →
  passed` is within I2). A row whose checks partly skip passes when one passed and none failed (as §4.4:183's limit), and a filtered run that drops a
  row's checks gives `no-check` (route control-plan-fix) where the instrument is at fault. The other way, D1 test 1 is strict: one failed check no
  counted row owns — a test without the row trait, a row named by no unit, or a line such as compare.py's own "FAIL spec-checks.json missing …"
  (MoviePad-Remake `compare.py:211-213`) — makes every counted row citing that file `unmeasurable`, including rows whose own checks passed; a passed
  check no row owns is ignored. Such rows route to control-plan-fix (D2), not to instrument-recovery.
- **L2 (D2, coverage).** D counts rows, not ruled IDs: a ruled ID (REQ / INV) with no counted row can sit under an advancing individual. Coverage stays with
  the per-ID table (§4.4:176-183) and the spec §3 rule that each INV names its row or a reason (ECO-086). Rows named by no unit and not in `assembly` are
  listed and not decided (ViewPrism2 15, ViewTube 13).
- **L3 (I4, D0, D1, who writes).** The measured unit is now read from the evidence (`identity`) rather than from a field the receiving side writes, so
  an evidence file that names no unit or another one is caught (B3, B5: neither ViewPrism2's stored results nor MoviePad-Remake's `compare.txt` names
  one — both hold today). What remains: the stamp is written by the instrument itself, and nothing proves it ran on the tree it names; `evidence_sha256`
  catches later edits only. D is applied by the receiving AI without a tool until a product ships one; only the rehearsal checks the rules can be
  applied as written. On the freeze, D now proves that `frozen_commit` precedes or equals the work order's issue commit, that both are in the
  delivered commit's history and are not the delivered commit, that `delivered.tree` is that commit's tree, and that the delivery carries the frozen
  revision's M-BOM and Control Plan byte for byte, and that the BOM did not change between the freeze and the issue — so a tag moved after the
  issue, or moved back to an older BOM, is caught (I3a). A tag moved back to a commit with the same BOM bytes passes, and decides the same. It does not prove that the work order was issued
  before the factory started, nor that the factory read nothing else: a factory's own commits made after the issue are also ancestors of the delivered
  commit (in MoviePad-Remake the designer committed the factory's work in one commit, so the question did not arise).
- **L4 (I0, human part).** Rows or row parts with a human approver are not decided by D; an individual can enter Phase 5 with them open, and they are decided
  there. The template rule that a depth-G row has a human approver (`33-control-plan.yaml:43, :111`) is not checked by D (`depth` is not an input).
- **L5 (I2, I3a, migration).** Today 18 of ViewPrism2's 50 named rows and 9 of ViewTube's 28 fall outside I2, 6 ViewPrism2 units have no `acceptance_refs`,
  neither M-BOM has `assembly`, neither Control Plan has `check_mapping`, and ViewTube's control plan at HEAD does not parse (B4); in both products every
  decision is `input-defect` until distribution migrates them (`rehearsal-real.txt` R0: 26 defects on ViewPrism2). Migration makes decisions about the
  BOM, not renames: an absent `approver` given a value (the rehearsal assumed `automated` for 8 rows), a unit with no `acceptance_refs` given rows or
  removed (the rehearsal dropped 6, among them `M-ORACLE-030`), and a row the factory's self-acceptance carried (`CP-L1-SMOKE`) given an automated part
  the receiving side runs. ViewTube's reviewer or inspector approvals are not
  `approver` values under I2; at migration they belong to independent inspection. The freeze inputs are missing too (`freeze-inputs.txt`): neither
  product's work order has the frozen-revision line, ViewPrism2's As-Built has no `work_order_ref`, `mbom_ref` or `control_plan_ref` (ViewTube's has some),
  and both deliver through ECOs that do not issue a work order per delivery — distribution must say where the issued work order of an ECO delivery is.
  The rehearsal's real-data runs construct them (the frozen revision and the work order's issue both `f697a82`, ECO-147's filing; the delivery
  `504921a`; the M-BOM and Control Plan blobs are equal at both, asserted by the script; v1 froze `504921a` itself and loop 4's first draft
  `b63897a`, each after the issue, which v2's I3a refuses). MoviePad-Remake, made by the current templates, gives `input-defect` with 3 defects
  (no `check_mapping`, no `frozen_commit`, a short `work_order_ref`), and neither ViewPrism2's stored results nor MoviePad-Remake's `compare.txt` names a measured unit (ViewTube's evidence not measured), so the
  first delivery after migration holds on every counted row until the instruments stamp their runs (B5, `rehearsal-moviepad.txt` M0, M1a).
  For MoviePad-Remake's two `no-check` rows, control-plan-fix means a product decision at migration: the receiving side's instrument also builds and
  runs the tests and writes checks for those rows, or the rows lose their automated part (they are the factory's self-acceptance, which B2 says is not
  a pass). Since MoviePad-Remake `b2e19a0` (2026-10-26) that product's Control Plan carries `check_mapping` as a pilot ahead of the template, equal
  to the calibration's mapping (I3a on its M-BOM and Control Plan: no defect), and its chain checker reads `delivered.commit`. Deliveries 1 and 2 were
  frozen before it, so its first effect is delivery 3. For the two rows it took the first way: inspect.py is to write their checks, carried to delivery 3.
  The distribution ECO is unchanged.
- **L6 (D3, a hold; the user's ruling "2:A").** D gives a held individual no way into Phase 5 other than a new delivery, even when the route changed nothing
  the factory made (a record-fix of the receiving side's own typo costs a redelivery — the ruling's accepted cost). A product that accepts known defects today (ViewPrism2
  ECO-147) must decide at distribution how that acceptance meets D's hold; until then, D's hold and the known-defect acceptance are two separate facts.
- **L7 (scale).** Designed from two products' Control Plans; rehearsed on ViewPrism2's real BOM and stored results, on MoviePad-Remake's first
  per-delivery records (one delivery), and on synthetic inputs (V2).
- **L8 (I1, I2, git).** D requires git: `delivered` is `{commit, tree}` and the freeze is checked by commit and ancestry. The non-git form
  (`{content_sha256}`) is removed — it could never pass a commit-only freeze (L3E2-4). A product that does not deliver through git has no advance
  decision until a form for it is designed. A receiving side without git gets `input-defect` (route record-fix: the receipt is redone where git is),
  never a decision with the freeze checks skipped; the other I3a checks still run and are listed with it.
- **L9 (D5, what the control reading sees).** It sees causes as D2 names them, so two different faults with the same row and category are one
  cause, and one fault reported under two rows is two. It does not see a route done badly but in time (a fix that hides the check rather than
  the fault passes as converged — the fixed oracle's detection power, not D5, bounds that), nor the cost of the redeliveries. `routes_done` is
  written by whoever did the route; D5 reads that it is recorded, not that the fix is real. `row_changes` and `work_ref` are the orchestrating
  AI's statements: a wrong rename hides a persistence (C1), and a failing row renamed or removed under its own cause is a routine route by
  C5's rule — if the new row then passes, nothing in D5 tells a real fix from a check redefined away (the fixed oracle and the independent
  inspection bound that, not D5); an undeclared change shows as C5
  only when the counted rows differ (a row swapped for another of the same name is not seen), and a delivery filed under a new `work_ref` instead
  of the work's own starts a fresh ledger and fresh bounds — nothing checks that the link was kept. An added row is accepted on any routing
  cause of the previous decision (an added row has no earlier name to be on). C1 fires on the first persistence, so a fix that needs two attempts
  opens a review; the review may find the process in control and continue. The bounds (3 holds, 5 decisions) are defaults taken from the design
  loops, not measured on deliveries. The declared default at a bound (stop) departs from §8.5's (accept), so a bound leaves the product stopped
  until a human disposes of it. Rehearsed on synthetic histories and on one product's two deliveries (`rehearsal-sequence.txt`); no work has yet
  been held more than twice, R2's first decision rests on an assumed stamp (M1b), and both real records predate `routes_done` (read
  *unrecorded*).

### Not changed

- The factory's self-acceptance and its stop rule, the fixed oracle and golden (Phase 5), the known-defect acceptance, §4.4's per-ID table, R-050,
  ECO-088's re-measurement rule, independent inspection, the operator layer (`bomdd-run`, whose promotion decision is about this repository's ECOs), the
  work order's fields (one of them is now read, I1), and every tool.

## 2. No-impact prediction (before manufacture; frozen at filing)

Changed: the files in M1, this order, the register and `bomdd/reports/eco-115-*/`. Untouched: `method/tools/`, `method/schemas/`,
`method/templates/product-profile/`, `method/templates/process-core/`, `.claude/skills/`, hooks, `.github/`, `30-ebom.yaml`, `32-mbom.yaml` (ECO-114's),
`method/prompts/`, the other templates, and both product repositories.

## 3. Acceptance (conditions; frozen at filing)

- **V1 — the text.** Playbook §4.4 "前進の判定" states I0-I4 and D0-D4 once; §1 and §6.1 carry one line each naming it; `:178` refers to it; each
  template field of M1 carries a comment naming it; I2's values appear in the template comments exactly as in I2.
- **V2 — the decision reads only its inputs (rehearsal; evidence only, read-only on ViewPrism2 and MoviePad-Remake).** The rehearsal script under the report folder applies
  I3a, I3b, D1, D2 and D4 and prints, for each row, the category and the deciding test; the design evidence of loop 4 (`rehearse_decision_v2.py`,
  `run_rehearsal_v2.py`, `rehearsal-v2.txt`, `run_moviepad.py`, `rehearsal-moviepad.txt`) is its latest run (loops 2-3: the v1 files), and V2 re-runs it
  on the manufactured templates' field names.
  - Real data as it is: ViewPrism2's M-BOM and Control Plan at `504921a` give `input-defect` (I3a), listing each row and unit outside I2/I3a;
    MoviePad-Remake's delivery 1 records give `input-defect` with their 3 defects (B5).
  - Real data migrated: a copy with the edits listed in the output. On the stored results as they are, which name no measured unit, every counted row
    is `unmeasurable` by test 1 and the individual holds (ViewPrism2 38 rows; MoviePad-Remake 13 rows). On ViewPrism2's tests run on a clean copy of
    its HEAD made outside that repository, stamped by the run, the outcome is predicted from the stored results: `holds`, with `CP-STARTUP-028` and the
    two rows whose absent `approver` was migrated to `automated` as `no-check`, and the other counted rows `pass` by test 5. On MoviePad-Remake's
    comparator re-run on `f30d771` with its stamp, the outcome is predicted from `compare.txt` (`rehearsal-moviepad.txt` M1b, the stamp ASSUMED):
    `holds`, with `CP-BUILD-001` and `CP-SELF-ACCEPTANCE-001` `no-check` and the other 11 counted rows `pass`; `CP-HARNESS-SELFTEST-001` is listed as
    named by no unit (L2). Each run twice, byte-identical.
  - Known-bad freezes on MoviePad-Remake's real records (`rehearsal-moviepad.txt` M2), each `input-defect` with its own reason among those it lists:
    `frozen_commit` set to the delivered commit (which necessarily also follows the issue and differs from what the line resolves to); the work order
    read at a commit after the delivery, with its text there (not an ancestor); `frozen_commit` recorded as `bom-v3` while the line names `bom-v4`;
    `delivered.tree` not the delivered commit's tree; `bom-v4` moved back to `bom-v3`'s commit with `bom-v3`'s BOM delivered (the line, `frozen_commit`,
    the refs and the copies all agreeing — the BOM at the issue commit differs).
  - Known-bad evidence lines on the same records (M3, D1): a `FAIL` line for one row gives that row `violation` (test 2); an `ERROR` line gives
    `unmeasurable` (test 1, an unmapped term); compare.py's own `FAIL spec-checks.json missing …` line gives every counted row `unmeasurable`
    (test 1, a failure no counted row owns).
  - Known-bad inputs on a synthetic M-BOM, Control Plan and evidence, each changing only that input (every evidence edit recomputes the record's sha256
    unless the case is the sha256), each giving its own outcome and naming its deciding test:
    - I3a: the Control Plan unparsable; the M-BOM unparsable; the delivery's Control Plan differing from the frozen revision, its M-BOM differing, and
      a delivery without its Control Plan; the work order without a frozen-revision line, with two, and with a tag that cannot be resolved; the
      entry's `mbom_ref` and its `control_plan_ref` each naming another revision; no `work_order_ref`; a `work_order_ref` naming the delivered
      commit; no `frozen_commit`; a frozen revision that is the delivered commit, with the line and both refs agreeing (caught by freeze ≤ issue,
      which implies it — a multi-reason case); a duplicate unit ID; a
      duplicate row ID; a unit with empty `acceptance_refs`; `assembly` absent; `assembly` empty without `assembly_reason`; no row named (the units and the
      assembly list emptied together — the one way to name no row); a named row missing; a named row retired; an `approver` of `maintainer` and one
      absent; an
      `on_fail` with the key `dependency-update` and one with the value `human-approval`; a `status` of `draft`; `check_mapping` absent; an `outcomes`
      value outside the four; a format without `identity`; an `identity` without the group `tree`; a `line` format whose `row_key` lacks the group
      `outcome`; git unavailable, alone and with a row `approver` outside I2 (both listed); no `delivered`; a malformed `delivered`; a
      `delivered.tree` that is not its commit's tree; `frozen_commit` on another line of history (multi-reason, as above); the freeze after the issue
      (the line's tag moved to a later commit); a tag moved back to a commit with an older BOM, and the same with the same BOM (advances); the work
      order's commit outside the delivered history.
      With git (a stub history in the synthetic runs), a tag in backticks that resolves to `frozen_commit` advances.
    - I3b: a counted row with no decision record; two decision records for one row; a record without
      `evidence_sha256`; a record whose `format` `check_mapping` does not name; a decision record for a row that is not counted.
    - D1: an unreadable evidence file; no evidence file (`evidence_sha256: none`); a changed sha256; evidence naming another measured unit, none, and
      two; an evidence file with no checks; a check with an unmapped outcome term; a failed check with no row trait, and one of a row named by no
      unit (each makes every counted row `unmeasurable`, route control-plan-fix); a failed check (test 2); all checks of a row skipped (test 3); no check for a row (test 4).
    - D0/D2: a `human:<role>` row is listed, not decided, and the individual advances; an `automated+human:<role>` row is decided by its automated part;
      an `assembly` row with a failed check holds; every named row `human:<role>` advances with all listed; a row named by two units with one failed check
      is one `violation`; a `source: phase5` record is not read.
  - Inputs outside I1: a factory "PASS" added to the delivery, the self-acceptance log changed, the rest of the work order changed, a row's `when`,
    `depth`, `verifies` or `characteristic` changed — each leaves the output byte-identical.
  - D5 (`rehearse_sequence.py`, expectations fixed in the script before its arms run): a hold with several causes that the next delivery clears,
    and a row whose cause changes kind, are `in-control`; two works with the same number of holds read differently by their causes (the count
    does not decide); three holds on a fixed row set with no signal are `bound-reached` and `in-control`; six input defects reach the decisions
    bound; a re-issue that raises the bound is C6 and the first issue's bound is reached, also when its delivery advances, and one that keeps it
    is not a signal; C1 (route done / not done), C2, C3, C4, C5 and C6 each turn red alone on an arm made for it; a not-observed state between two
    violations of a row does not hide the persistence, nor does a decision that measured nothing between two unmeasurable states, and such a
    decision makes no return or regression and does not count to the holds bound; an instrument failure over every row read twice running is C1
    and C4, and back after a repair is C2; an `on_fail` override of a violation's route does not make C4; a renamed row carries its states; an
    open violation removed under another row's cause is C5, and a row changed with no routing cause on it is C5, while a `no-check` row removed or
    renamed under its own cause, a failing row renamed under its own cause, a passing row removed by a cause on it or by an input cause naming it,
    and a row added by a routing cause are not; two rows that fail and are fixed together, a second row that stays broken, and
    a receiving-side defect's return are not candidates, and only rows alternating in order and back are; MoviePad-Remake's two deliveries give
    C1 (*unrecorded*) and C4 as written and as migrated. Run twice, byte-identical.
- **V3 — independent inspection** (EQ-002): the text against §1, and V2's evidence.
- **V4 — self-conformance exit 0 before each commit; CI success on each pushed tip.**

## 収束 receipt (converge self-application)

### Loop 1 (after the split from ECO-114)

- **判定: 未収束** (round 軌跡: 26→10; material 14→5). Round 2 had new findings, so two consecutive zero rounds could not come within the limit of 3;
  round 3 was not run. User ruling "A": extend, with the common cause removed first.
- **起動経路**: user ruling "A" (split from ECO-114), 2026-10-24.
- **DoD (fixed before round 1; unchanged in loop 2):**
  - D2 the user's condition (ii): the decision is a function of I1's inputs only; a missing record or an unmeasured row never counts as a pass; V2 can
    show it with known-bad inputs.
  - D2a every value of every I1 field is either within I2 or an `input-defect`, decided before any row.
  - D2b every counted row gets exactly one category, and every non-`pass` outcome has a route.
  - D5 each rule has one canonical place.
  - D6 every basis claim (§0) names its measurement or file and line.
  - D7 each acceptance observation fails for its own rule's reason (a known-bad input per branch it shows).
  - D8 no new tool or mechanism beyond M1's text and templates; limits declared against the rule they limit.
- **Carried from ECO-114 loop 1:** R1-6 to R1-15, R1-18, R1-24 to R1-26, R2-1 to R2-5, R2-8, R3-1 to R3-5, R3-7, R3-8; their dispositions were in loop
  1's text (D0, I0, D1, I2, D2, I3a, D3, L2, I4/D4, V2, L3, I1).
- **Round 1 — 26 findings (14 material).** Fail-open paths through an `occasion` outside I2, zero counted rows, a single occasion, and regression rows;
  free-form `check_mapping`, outcome terms and `approval.by`; the decision's place against Phase 5; human rows at receipt; an uncompletable route; work-order
  defects; branch reasons; L5; R-050's vocabulary; minor E1-15 to E1-26. Grouped by cause (place, free inputs, outcomes without a route) and repaired.
- **Round 2 — 10 new findings (5 material).** E2-1 a malformed `delivered`; E2-2 zero counted rows with no route, all-human Control Plans never reaching
  Phase 5; E2-3 attempts and undecided rows against R-050 / ECO-088; E2-4 D3's held individual; E2-5 V2's real-data prediction against the basis; minor E2-6
  `check_mapping` per format, E2-7 README sha256, E2-8 the work order's form, E2-9 rows named by no unit, E2-10 the outcome mapping's meaning; E1-25's
  docstring and E1-6's partial run left from round 1.
- **Where the findings come from:** round 2's material findings are all where D meets what already exists around it — the As-Built record and R-050 /
  ECO-088, Phase 5 and the known-defect acceptance, the real Control Plan the rehearsal would run on — each found by reading, one at a time.

### Loop 2 (extension; user "A", 2026-10-24; the common cause removed first; limit 3 rounds)

- **判定: 未収束** (round 軌跡: 10→5; material 5→3). Round 2 had new findings, so two consecutive zero rounds cannot come within the limit; round 3 was
  not run. **No filing commit and no manufacture** until the user rules; round 2's findings are **not repaired**.

- **Common cause removed first — the rules run on real data.** `rehearse_decision.py` applies I3a, I3b, D1, D2 and D4 as written; `run_rehearsal.py`
  runs it on ViewPrism2's M-BOM and Control Plan at `504921a` and on a migrated copy with the stored results, and R-050 (a)/(b) on the records it writes
  (`rehearsal-real.txt`):
  - Y1: as it is, `input-defect` with 26 defects (bom-fix 7, control-plan-fix 19) — L5 is measured, not estimated.
  - Y2: the stored results were measured before `504921a` was committed; honestly recorded, every counted row is `unmeasurable` by test 1 — the decision
    cannot advance an individual on results whose individual no record names (B3, L3), which V2's real-data case now says.
  - Y3: with `measured_on` assumed (design evidence only), 35 rows pass and 3 are `no-check` (`CP-STARTUP-028`, and two rows whose absent `approver` was
    migrated to `automated`) — V2's real-data prediction is `holds`, and the migration of an absent `approver` is a decision about the row (L5).
  - Y4: R-050 on the decision's records: 12 human-only pairs have no `pass` row before Phase 5, and a hold leaves 3 non-`pass` rows — D4 states when R-050
    is read (after Phase 5) and what a hold leaves.
  - Y5: run twice, byte-identical.
- **Loop 1 round 2 repairs:** E2-1 I3b (`delivered` within I2) and V2; E2-2 D2 (no counted row advances when every named row has a human part); E2-3 I4
  (decision records replaced, history kept; Phase 5's own entries) and D4; E2-4 D3 (the known-defect path stated); E2-5 V2 (prediction `holds`, edits
  listed); E2-6 I2 (`check_mapping` per format) and I4 (`format`); E2-7 the README; E2-8 the work order is no longer an input (I1: `when` and `occasions`
  dropped — every named row is counted, as ECO-088 already requires); E2-9 D0 and L2; E2-10 L1; E1-25 the script's docstring (re-run; new sha256); E1-6 L1.
- **Round 1 (full re-read) — 10 new findings (5 material).** L2E1-1 the M-BOM and Control Plan revision the decision reads is not pinned, so a delivery
  can change its own acceptance; L2E1-2 I3b required `result`, which D4 writes afterwards; L2E1-3 the script did not implement I3a's parse check; L2E1-4
  an M-BOM naming no row advanced vacuously; L2E1-5 counting every row contradicts the `when` comment the order kept; minor L2E1-6 most branches never
  executed and the docstring overstated it, L2E1-7 "pairs" were rows, L2E1-8 I3b's edges (records for uncounted rows, an instrument with no output),
  L2E1-9 `attempt` in the script and the ruling's field, L2E1-10 migration choices undeclared.
  - Common cause: the design evidence ran only the real data, whose 977 checks all pass, so most branches had never run — the reviewer found by reading
    what execution would have shown. Removed before repair: `run_rehearsal.py` now runs 41 synthetic one-change cases, one per branch of I3a, I3b, D1, D0
    and D2 with its expected outcome, and 5 inputs outside I1 that must leave the output byte-identical; `rehearse_decision.py` takes the files as text
    and parses them inside I3a. All 46 give their expected outcome (`rehearsal-real.txt`).
  - Repairs: L2E1-1 I1 (the frozen revision) and I3a (the delivery's copies compared; route product-fix); L2E1-2 I3b's field list and I4 (`result`
    after D2); L2E1-3 the script; L2E1-4 I3a (at least one row named); L2E1-5 M1 (the `when` comment rewritten) and "Not changed"; L2E1-6 the script and
    this receipt; L2E1-7 D4 (22 of 73 pairs, 12 rows; `r050()` counts pairs); L2E1-8 I3b and I4; L2E1-9 the script and M1 (`known_defect_ruling`);
    L2E1-10 L5.
- **Round 2 (full re-read) — 5 new findings (3 material), unrepaired.** Eight of round 1's ten repaired; L2E1-1 with a new problem; L2E1-6 with a residue.
  Material: L2E2-1 `control-plan-fix` / `bom-fix` cannot complete "on the same `delivered`" (the frozen revision either stays and the fix is never read,
  or moves and the delivery's copy differs); L2E2-2 the frozen revision's source is not an input — the receiving side writes `mbom_ref` /
  `control_plan_ref` in the entry it creates, so the freeze check can be made trivially equal; L2E2-3 the known-defect acceptance D3 and D4 cite works at
  golden on review findings and does not touch R-050 (b), so "existing" and "as today" do not hold. Minor: L2E2-4 rehearsal gaps (the second-attempt
  case cannot fail; no-evidence-file, missing-copy and differing-M-BOM cases; the self-acceptance-log input; a two-input case); L2E2-5 what "equal" and
  "where it carries them" mean.
- **Where the findings come from:** all three material findings are where the decision meets the change-management records around it — the freeze made
  before manufacture, a fix followed by a new attempt, the known-defect acceptance — not the decision's own rules (the 41 synthetic cases and the real
  data reproduce; script and §1 agree).
- **DoD at round 2:** ✔ D5, D6; ✘ D2 (L2E2-2), D2a (L2E2-2, L2E2-5), D2b (L2E2-1), D7 (L2E2-4), D8 (L2E2-3).
- **未収束事項 at the end of loop 2:** L2E2-1 to L2E2-5 (repaired in loop 3, below).

### Loop 3 (user "2:A", 2026-10-24: narrow, then extend; limit 3 rounds)

- **判定: 未収束** (round 軌跡: 5→5; material 2→4). Round 2 had new findings, so two consecutive zero rounds cannot come within the limit; round 3 was
  not run. **No filing commit and no manufacture** until the user rules; round 2's findings are **not repaired**.
- **Correction (producer's error):** D3 as written after round 1 lets record-fix, work-order-fix and instrument-recovery lead to a new decision on the
  same delivery. That **contradicts the user's ruling "2:A"** (a hold is lifted only by a new delivery decided afresh), whose stated cost was that the
  same delivery cannot be decided again. Round 1's L3E1-2 was that accepted cost and should have been answered as a limit declared by the ruling; the
  producer instead implemented the reviewer's direction. Round 2's L3E2-1, L3E2-2, L3E2-5 and half of L3E2-3 exist only because of that split.
- **DoD:** unchanged.
- **Narrowing (the common cause removed):** the decision only decides whether the delivered individual enters Phase 5 (D3). L2E2-1 → there is no second
  decision on the same delivery; every route ends in a new delivery decided afresh (I4, D3), so `advance_decision_history` is gone. L2E2-3 → the
  known-defect acceptance is outside D and unchanged; how it meets D's hold is a product's decision at distribution (D3, L6); D4 says R-050 (b) reports a
  held entry's rows. L2E2-2 → the frozen revision is read from the work order's one line (I1), and I3a checks the entry's references and the delivery's
  copies against it; the write time stays a limit (L3).
- **Minor repairs:** L2E2-4 cases added (no evidence file with `evidence_sha256: none`; a delivery without its Control Plan; a differing M-BOM; the work
  order without its line; the entry naming another revision; the self-acceptance log as an input outside I1), the second-attempt case removed with the
  rule, the no-row case stated as two changes made together; L2E2-5 I3a says byte-equal and that a missing copy differs.
- **Rehearsal re-run:** 45 synthetic cases and 6 inputs outside I1 all give their expected outcome; the real data as before (`rehearsal-real.txt`).
- **Round 1 (full re-read) — 5 new findings (2 material).** L3E1-1 which copy of the work order is read was not named, and both products keep it in the
  delivered repository, so a factory could rewrite the line and its Control Plan together; a tag can also move; L3E1-2 routes that change nothing in the
  delivered tree (record-fix, work-order-fix, instrument-recovery) could not complete under "a new delivery"; minor L3E1-3 the products lack the freeze
  inputs (unmeasured), L3E1-4 the paths of the copies, L3E1-5 cases missing (two lines, `mbom_ref`, a tag, the rest of the work order).
  - Repairs: L3E1-1 I1 reads the work order as issued at `work_order_ref`, never from the delivered tree; I2 requires commit IDs; I3a checks that
    `work_order_ref` is not the delivered commit; L3 states what remains (that the issue commit precedes the factory's work). L3E1-2 D3 splits the routes:
    a new delivery after product-fix, control-plan-fix or bom-fix; a new decision on the same delivery after the three that change nothing in it (I4,
    `advance_decision_history` back for that case). L3E1-3 measured (`measure_freeze.py`, `freeze-inputs.txt`) and added to L5. L3E1-4 I1 (the entry's
    paths). L3E1-5 cases added. Rehearsal: 51 cases and 7 inputs outside I1 all as expected; the real data unchanged.
- **Round 2 (full re-read) — 5 new findings (4 material), unrepaired.** L3E1-3 to L3E1-5 repaired; L3E1-1 and L3E1-2 with new problems. Material: L3E2-1
  D3's same-delivery routes contradict the "2:A" ruling and L6 (the correction above); L3E2-2 instrument-recovery changes the delivered tree when the
  instruments are in it (ViewPrism2's tests are); L3E2-3 a frozen revision equal to the delivered commit passes I3a, a same-delivery work-order-fix could
  write one, and the rehearsal's real-data construction (frozen `504921a`, the work order "issued" at its parent) is such a case — a parent cannot name
  its child; L3E2-4 the non-git `delivered` form can never pass I3a's commit-only freeze. Minor: L3E2-5 the same-delivery case cannot fail.
- **Where the findings come from:** with the ruling restored, what remains is the freeze's provenance (L3E2-3's frozen ≠ delivered check, L3E2-4's dead
  non-git form); every loop since the split has found its material defects at the boundary where the decision proves the BOM it reads was not the
  factory's own (L2E1-1, L2E2-2, L3E1-1, L3E2-3), and neither product carries the inputs that boundary needs (`freeze-inputs.txt`).
- **DoD at round 2:** ✔ D5, D6; ✘ D2 (L3E2-2, L3E2-3), D2a (L3E2-3, L3E2-4), D2b (L3E2-2), D7 (L3E2-5), D8 (L3E2-1).
- **未収束事項:** L3E2-1 to L3E2-5 (unrepaired).
- **User ruling "1:A 2:A 3:A", 2026-10-24.** 2:A — D3, I4, L6, M1 and V2 are reverted to the ruling "2:A" (every route ends in a new delivery; the
  same-delivery case is removed from the rehearsal, which re-runs with every case as expected). That removes L3E2-1, L3E2-2, L3E2-5 and the same-delivery
  half of L3E2-3. Not repaired, left for the redesign: the check that the frozen commit is not the delivered one (L3E2-3), the non-git `delivered` form
  (L3E2-4). 3:A — the design is held unconverged and kept as this record; its trial is the MoviePad re-manufacture, whose real per-delivery records
  (issued work orders, frozen revisions, As-Built references) neither product has today (`freeze-inputs.txt`).

### Loop 4 (redesign; user "2:A", 2026-10-24, after EXP-20261024-01's first trial; rounds counted afresh; limit 3 rounds)

- **判定: 未収束** (round 軌跡: 8→4; material 6→1). Round 2 had new findings, so two consecutive zero rounds cannot come within the limit; round 3
  was not run. **No filing and no manufacture** until the user rules; round 2's findings are **not repaired**.
- **起動経路**: user ruling "2:A" (redesign ECO-115 from the trial), 2026-10-24.
- **DoD:** unchanged (D2, D2a, D2b, D5-D8).
- **Common cause removed first — real per-delivery records at the freeze boundary.** Every loop since the split found its material defects where D
  proves the BOM it reads was not the factory's own, and no product had the records that boundary needs. MoviePad-Remake delivery 1 is the first set
  (B5); the v2 rehearsal (`rehearse_decision_v2.py`) runs on it read-only (`run_moviepad.py`, `rehearsal-moviepad.txt`) before any round:
  - X1: the records as the current templates left them are `input-defect` with 3 defects — the decision's inputs are not written by today's templates.
  - X2: the work order names a tag in Markdown code; v1 required a 40-hex commit and could not read it. The line may name a tag; the receiving side
    records the commit it resolved to (`frozen_commit`), and I3a checks the line still resolves to it (I1, I2, I3a).
  - X3: `compare.txt` names no measured unit (the trial's L4 break); v1 trusted a `measured_on` the receiving side writes. Each format declares an
    `identity` and D1 test 1 reads the unit from the evidence (I2, I4, D1, L3). The cost, measured: the evidence of both products measured (ViewPrism2, MoviePad-Remake) names none today, so
    every counted row holds until instruments stamp their runs (L5).
  - X4: L3E2-3 (a frozen commit equal to the delivered one) is checked without git, and the ancestry of `frozen_commit` and the issue commit with git
    (I3a); v1's own real-data construction was such a case and is rebuilt at `504921a`'s parent (L5; the BOM blobs are equal at both commits) —
    round 1 found that rebuild still followed the issue (L4E1-3); it is now at `f697a82`.
  - X5: L3E2-4 (the non-git `delivered` form) is removed and D declared git-only (L8).
  - X6: the redesigned decision on the real records holds on exactly `CP-BUILD-001` and `CP-SELF-ACCEPTANCE-001` (`no-check`), which the product's
    As-Built said were judged by the comparator — a false record found by running D, corrected in the product (`5540a38`, `0066d2b`).
  - Not in this ECO (R3; recorded separately): the work order's route lacks the ECO step the product's change management requires; a sandboxed factory
    cannot commit; the register template's state words differ from the process profile; the As-Built's hash should be of the committed blob.
  - Rehearsal: 63 synthetic cases and inputs outside I1 all as expected (`rehearsal-v2.txt`); the real data of both products, each run twice,
    byte-identical.
- **Round 1 (full re-read, fresh context) — 8 new findings (6 material), repaired.** Checked against the standing rulings first: none argues against
  "2:A", English records or no new tool. By cause:
  - Freeze and identity boundary (L4E1-3, -4, -5, -7): the freeze was not required to precede the issue, so a tag moved during manufacture passed, and
    loop 4's own ViewPrism2 rebuild at `b63897a` followed its issue at `f697a82`; `delivered.tree` was never checked against its commit; without git
    the script skipped ancestry while the text has no git-less mode, and every synthetic case ran without git; `delivered` was checked in I3b after
    I3a had read it. Repairs: I3a (freeze ≤ issue; `delivered` and its tree checked first; git required), L3, L8; the synthetic driver runs on a stub
    history; ViewPrism2's construction at `f697a82` (freeze = issue).
  - The `line` format and failures no row owns (L4E1-1, -2): an unmapped term was skipped, not unmeasurable, and the grammar was hard-coded; a failed
    check owned by no counted row was dropped — compare.py's own "spec-checks.json missing" line would have advanced. Repairs: I2 (`row_key` for the
    line format is a regular expression with `outcome` and `row`), D1 test 1 (a failure no counted row owns), L1 (the strictness declared).
  - Records (L4E1-6, -8): method line numbers were stale after ECO-114's manufacture (re-cited at `ab87e48`, which §0 now pins); V2 filed a D1 case
    under freezes, MoviePad's freeze-at-delivered case cannot be isolated (its reasons are now listed), the later-work-order case passed the issued
    text, and MoviePad's double run was not printed. Repairs: V2 (M2 and M3), `run_moviepad.py`.
  - Rehearsal after repair: 65 synthetic cases and 7 inputs outside I1 all as expected; ViewPrism2's real data unchanged in outcome (R0 26 defects;
    R1a 38 `unmeasurable`; R1b 35 `pass`, 3 `no-check`); MoviePad-Remake M2 4/4 and M3 3/3; each run twice, byte-identical.
- **Round 2 (full re-read, same reviewer resumed) — 4 new findings (1 material), unrepaired.** All 8 of round 1 repaired (the reviewer re-ran both
  rehearsals byte-identical and spot-checked the re-pinned citations).
  - Material: L4E2-1 a tag moved **back** passes I3a — on MoviePad-Remake's real git, `bom-v4` resolved to `bom-v3`'s commit with `frozen_commit`,
    refs and delivered copies all `bom-v3`'s gives `holds` on the same two rows as the honest delivery, no `input-defect`: the factory chose its own
    older acceptance and D cannot tell; L3's "a tag moved after the issue is caught" holds only forward. Direction offered: the M-BOM and Control Plan
    at the issue commit byte-equal to those at `frozen_commit` (at `7824ba9` they equal `bom-v4`'s, `f6664def` / `6905a0ab`; `bom-v3`'s M-BOM is
    `2305d2a2`), or require the line to name a commit.
  - Minor: L4E2-2 two I3a clauses (frozen ≠ delivered; frozen an ancestor of delivered) are now implied by freeze ≤ issue < delivered, so their cases
    cannot fail for their own reason (D5, D7); L4E2-3 with git missing, I3a returns early and does not list the other defects; L4E2-4 a failure no
    counted row owns routes to instrument-recovery by default, though the failing check is usually a product, delivery or orphan-row failure (L1 states
    the strictness, not its route).
- **Where the findings come from:** L4E2-1 is again the freeze boundary — where D proves the BOM it reads was not the factory's own — now from the side
  of a tag moved back; the rest are consequences of round 1's repairs. The material count fell 6→1 and every finding came with a cheap direction.
- **DoD at round 2:** ✔ D2a, D2b, D6; ✘ D2 (L4E2-1), D5 and D7 (L4E2-2), D8 (L4E2-4's route undeclared against its rule).
- **未収束事項:** L4E2-1 to L4E2-4 (unrepaired).
- **User ruling "A", 2026-10-24: cut-off adoption.** Round 2's four findings are repaired by the directions offered, with no further reading round;
  the design phase closes **unconverged by reading** and is checked next on real data — MoviePad-Remake's second delivery (EXP-20261024-01: redesign
  and calibration are separate steps). Not filed; filing follows that calibration.
  - L4E2-1: I3a — the M-BOM and Control Plan at the issue commit byte-equal to those at `frozen_commit` (the `show` callback); L3. Cases: synthetic
    (a tag moved back with an older BOM → `input-defect`; with the same BOM → `advances`) and real (`bom-v4` moved back to `bom-v3`'s commit with
    `bom-v3`'s BOM delivered → `input-defect`, `rehearsal-moviepad.txt` M2).
  - L4E2-2: I3a's two implied clauses removed from the text and the script; their cases relabelled multi-reason, caught by freeze ≤ issue.
  - L4E2-3: with git missing, the git-dependent checks are skipped and the rest still listed (L8); case with an `approver` outside I2 alongside.
  - L4E2-4: D2 and L1 — a failure no counted row owns routes to control-plan-fix; the two synthetic cases check the route.
  - Rehearsal: 68 synthetic cases and 7 inputs outside I1 all as expected; ViewPrism2's real data unchanged in outcome; MoviePad-Remake M2 5/5,
    M3 3/3; each run twice, byte-identical. The repairs were not re-read by a reviewer (the ruling's accepted cost); their check is the next delivery.

### Calibration on real records (MoviePad-Remake delivery 2, 2026-10-25; the user's "A" on the staged plan)

- **Records written by the revised procedure, nothing constructed** (`run_moviepad_d2.py`, `rehearsal-moviepad-d2.txt`): the work order
  issued at `d39a86a` names `bom-v5`; the As-Built entry has `frozen_commit` `085d207`, the refs at it, `delivered` `bd55362` / `df20276`;
  the comparator's output names that commit and tree on its first line.
- **N0, as written: `input-defect` for one reason** — the Control Plan has no `check_mapping` (a field this order adds to the template; not
  yet distributed). Every freeze and identity check of I3a passed on real values (delivery 1 needed every chain field constructed).
- **N1, with only `check_mapping` and the decision records added:** `holds` — `CP-BUILD-001` and `CP-SELF-ACCEPTANCE-001` are `no-check`
  (no designer-side check exists for them, as on delivery 1), the other 11 counted rows `pass` by test 5 from the stamped evidence;
  run twice, byte-identical.
- **N2, three known-bad inputs on N1, each for its own reason:** another unit's stamped evidence → test 1 "measured another unit";
  `delivered.tree` altered → `input-defect` (record-fix); `frozen_commit` recorded as `bom-v4` → `input-defect` (the BOM changed between the
  freeze and the issue; the line resolves to another commit).
- **What this shows and does not:** the I-rules and D1's identity test work on real per-delivery records, and the only blocker left is a
  template field. It does not show the decision on a delivery that should hold or fail for a product reason (delivery 2 passes every
  oracle check), on a second product, or on records written by anyone but this designer. The two `no-check` rows are a standing
  property of this product's Control Plan (factory self-acceptance only), to be decided at distribution (L5).

### Loop 5 (D5: a work's decisions over time; the user's instruction of 2026-10-26; rounds counted afresh; limit 3 rounds)

- **判定: 未収束** (round 軌跡: 9→6; material 5→4). Round 2 had new findings, so two consecutive zero rounds cannot come within the limit; round 3
  was not run. **Round 2's findings are not repaired**; D5 stays in the held draft until the ruling on how to go on.
- **起動経路:** the user's instruction (2026-10-26): "ECO-115の差し戻し上限や上申条件も、既存の権限の範囲で設計・検証してください。ただし、工程の
  収束性と工程管理の正常性は区別してください。差し戻し回数だけを管理状態の判断根拠にしないこと。既存の規則では解決できない裁定層の欠落が明ら
  かになった場合のみ、その根拠と必要な判断事項を提示してください。"
- **DoD** (fixed before the design): (a) convergence and control are separate readings with separate inputs, and the hold count alone never changes
  the control state; (b) each control signal has an event anchor, an owner, an arm that turns it red alone and arms where it stays green; (c) every
  outcome has a route within existing authority, and the human is reached only by a named ruling-layer condition with its basis; (d) the rules apply
  to MoviePad-Remake's real records (deliveries 1 → 2) as written; (e) the convergence bound triggers a review, never an escalation by itself.
  **(e) was revised in round 1** because it contradicted the playbook's existing loop rule (`method/bomdd-playbook-v1.md:1195-1198`: a fix,
  recovery or review loop has a bound frozen in advance and, at it, goes to pending human disposition): now "the bound is frozen in advance and its
  disposition follows that rule; the control reading is attached and the count does not decide it". **(c) has the same conflict** (R2-04) and is
  not yet revised.
- **Round 1** (a fresh context of the same model, read-only; 9 findings, material 5: R1-01 the bound had no frozen disposition and conflicted with
  the loop rule; R1-02 decisions that measured nothing were read as observations; R1-04 C2 was never red alone; R1-06 a row rename hid a
  persistence and H3 relied on that blind spot; R1-09 no owner per signal; minor 4: R1-03 the candidate counted route keys and ignored order,
  R1-05 C1 could not tell a route not done from a fix that failed, R1-07 method fixes were "fixed and reported", R1-08 not mapped onto §4.5).
  Repaired: the history inputs (`measured`, `routes_done`, `row_map`), C1–C5 with owners, the bound and its disposition, the §4.5 mapping, method
  fixes filed as an ECO or an OBS.
- **Round 2** (the same reviewer, resumed; 6 new, material 4): R2-01 an `unmeasurable` or `no-check` between two violations of a row silences C1
  (V→U→V reads in-control); R2-02 a work whose decisions are all input defects has no bound (six in a row stay `open`); R2-03 any
  control-plan-fix lets a fix drop a failing row from the counted set without a signal; R2-04 DoD (c) contradicts "besides the loop rule's
  disposition" in D5; minor: R2-05 the loop rule is in §13 (`:1194-1198`), not §8 as D5 says, and §8.5 (`:878`) asks for a default disposition
  declared in advance, which D5 does not declare; R2-06 `routes_done` is defined on the previous decision, not on the last measured one through
  `row_map`, and the script tells input causes by a "CP-" prefix.
- **The common causes** (for the ruling): (A) D5 keeps a row's history as "the last decision that measured it", so what counts as an observation of
  a row, and what may leave the counted set, are implicit — R2-01, R2-03, R2-06 (and R1-02, R1-06 before them); a per-row ledger with
  explicit states (observed pass / observed violation / not observed with its reason / removed with its route) would remove them together.
  (B) D5 binds itself to the existing loop rules piecemeal — R2-02, R2-04, R2-05 (and R1-01): one bound on all of a work's decisions, a default
  disposition declared at the work's issue (§8.5), the citation to §13, and DoD (c) read together with the loop rule.
- **Evidence and its honesty:** `rehearse_sequence.py`, `rehearsal-sequence.txt` (18/18 as expected, byte-identical on two runs). Its first runs did
  not match: 8/11 on the first version (three arms described histories impossible when every counted row is measured at every delivery; their
  inputs were rewritten, expectations unchanged), 14/18 on the round-1 version (three of the producer's expectation or arm errors — H11's bound
  count, H12's C4, H14's missing row — and one rule gap, an input-defect cause in two decisions running not read as C1).
- **Verified claims:** the loop rule's text (`bomdd-playbook-v1.md:1195-1198`, in §13 — D5's "§8" is wrong, R2-05); the real decisions R1/R2 are
  `rehearsal-moviepad.txt` M0/M1b and `rehearsal-moviepad-d2.txt` N0/N1; D3's "a new delivery decided afresh" and the user's ruling "2:A" are
  unchanged by D5.
- **未収束事項:** R2-01 … R2-06, and whether the user's "only ruling-layer gaps" is read together with the existing loop rule (the bound's
  disposition reaches the human) — the reading taken in this draft.

### Loop 6 (extension; the user's "A", 2026-10-26; the common causes removed first; rounds counted afresh; limit 3 rounds)

- **判定: 未収束** (round 軌跡: 9→3; material 4→2). Round 2 had new findings, so two consecutive zero rounds cannot come within the limit; round 3
  was not run.
- **起動経路:** the user's "A" on loop 5's non-convergence (extend, the common causes removed first).
- **Ruling (user "A", 2026-10-26): adopted by cut-off with round 2's findings repaired.** The repairs follow the reviewer's directions and are
  checked by the rehearsal only — not by another review round: L6R2-01 → a changed bounds line is control signal C6, not a cause of the
  decision (D2 unchanged), with arm Y5 (a raised bound whose delivery advances is reported); L6R2-02 → C5 narrowed to a row changed with no
  routing cause on it (the row's own cause or an input cause naming it) or to an open `violation` / `unmeasurable` moved under another row's
  cause, on the last state other than `nothing-measured`, with green arms Y1, Y2, Y3 and X4 (a failing row renamed under its own cause, now
  green; the limit it leaves is declared in L9); L6R2-03 → `nothing-measured` is skipped in C1/C2's not-observed comparison, arm Y4. The
  rehearsal has 38 arms, 38/38 on the first run, byte-identical on two runs. **D5 is adopted unconverged:** what the repairs changed is checked
  next by ECO-115's independent inspection (V3, EQ-002) at filing.

- **Common causes removed before the first round:** (A) a row's history is a ledger of explicit states (observed `pass` / `violation`; not
  observed with its reason; `row_changes` for removed, added and renamed rows with their routing cause) — answers R2-01, R2-03, R2-06; (B) the
  bounds and their disposition bound to the loop rules in one place — two bounds frozen at issue (holds that measured rows, default 3; all
  decisions, default 5), the default disposition declared at issue (§8.5, `:879-881`: stop without advancing, record and report), §13's pending
  human disposition (`:1195-1198`) as the state at the bound, the report as information — answers R2-02, R2-04, R2-05. I1 now names the work
  order's bounds line as D5's one further input.
- **DoD:** (a), (b), (d) unchanged. **(c) revised** (R2-04, the same conflict as (e)): "every outcome has a route within existing authority; a
  judgement is asked of the human only for a ruling-layer gap (§4.5's three kinds) with its basis; at a bound, the disposition declared at issue
  applies and is reported as information". **(e)** as revised in loop 5.
- **Rehearsal:** `rehearse_sequence.py` rewritten on the ledger; 25 arms (loop 5's 18, the round-2 histories T1–T4, and T5–T7 for C5's and
  C1's edges), expectations fixed in the script; 25/25 on the first run, byte-identical on two runs.
- **Round 1** (a fresh context of the same model, read-only; 9 findings, material 4): L6R1-01 §8.5 names its own default disposition (accept),
  so D5's "stop" is a departure the draft did not declare; L6R1-02 a re-issue could raise the bound unchecked; L6R1-03 which deliveries belong
  to a work was undefined, so a review's process ECO could reset the ledger and the bounds; L6R1-04 an instrument failure over every row read
  as `nothing-measured` hid its persistence and return; minor: L6R1-05 C5's "on the row" was in the text but not in the script, and T5's label
  overstated it; L6R1-06 C4 read the route, so an `on_fail` override moved a product violation into C4; L6R1-07 a failing row renamed and then
  passing was silent; L6R1-08 "route not done" on records that predate `routes_done`; L6R1-09 the candidate did not require the second row back.
  Repaired: the departure from §8.5 declared with "2:A" as its reason and its consequence (the product stays stopped until disposed of);
  bounds from the first issue, a differing bounds line an input cause; `work_ref`, read in I1, continued by a review's process ECO; a test-1
  hold gives each row `unmeasurable` with its cause, and C1/C2 read the not-observed states; C4 by category; C5 on the row, with renames of a
  failing row; a third reading, *unrecorded*; the candidate requires the second row back. 33 arms (X1, X1c, X3–X6, H7b, H13b added); the first
  run gave 32/33 — X5's expectation was the producer's error (C4 needs both decisions' causes outside the product); X5 was extended to three
  decisions so that it shows the first issue's bound being reached; 33/33, byte-identical on two runs.
- **Round 2** (the same reviewer, resumed; round 1's nine resolved; 3 new, material 2): L6R2-01 the re-issue's changed bounds line is called
  "an input cause of that decision", but D2 makes input defects only from I3a/I3b, so whether it changes the decision is undefined — and the
  script adds it only to the ledger, so a re-issue that raises the bound and then advances is silent; L6R2-02 C5's "removed or renamed while
  not pass" fires on routine routes — a `no-check` row losing its automated part under its own cause (MoviePad-Remake's two rows, L5), the same
  row renamed into one with checks, a row removed after an input defect naming it (input causes are never "on a row", and the clause reads the
  last state, not the last observed one); no green arm covers these; minor: L6R2-03 a row `unmeasurable` before and after an input defect
  reads as C2 (returned) though nothing was repaired — `nothing-measured` breaks the not-observed comparison. Directions given: make a changed
  bounds line a control signal (or an I3a check with its route) with an arm where the delivery advances; limit C5's clause to an open
  `violation` or `unmeasurable` moved without its own cause, on the last observed state, with input causes naming a row counted as on it, and
  green arms for the three routine cases; skip `nothing-measured` in the not-observed comparison.
- **DoD status after round 2** (the reviewer's): (a) holds; (b) not met until L6R2-02 (C5 lacks green arms for routine routes); (c) holds;
  (d) holds; (e) met apart from L6R2-01.
- **未収束事項:** L6R2-01, L6R2-02, L6R2-03.
