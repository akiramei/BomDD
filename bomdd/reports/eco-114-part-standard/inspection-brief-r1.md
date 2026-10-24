# Independent inspection brief r1 — BomDD ECO-114 (the part standard: provides and requires, external promises in the E-BOM, the Phase 3 order and owners, assembly resolution) — inspector EQ-002

- **Role: inspector.** EQ-002 (Codex CLI). Responsibility: judge whether the manufactured method text and templates implement the order's rules, and
  whether the acceptance evidence shows what the order claims. Range of this round: **境界探索** (boundary exploration — where the rules can be read wrongly,
  contradict the rest of the method, or are stronger in the record than in the text).
- **Target:** BomDD commit `286d02c944ed7429e0f899a70342cbed518e81ad` (the manufacture commit). Report `git rev-parse HEAD` at start and at end (they must be
  equal; otherwise UNMEASURABLE).
- **The design was adopted by the user's cut-off ruling ("1:A") while unconverged under the converge rule** (the order's header and receipt). Its rules are
  the object of this inspection as manufactured; a finding that the text departs from the order, or that a rule cannot be applied as written, is in range.
- **You are running inside the operator entry** (`bomdd-run.py ECO-114 …`); do not run `bomdd-run.py ECO-114 …` yourself.
- **Observable prohibitions:** no file in the repository created, changed or deleted (`git status --short` unchanged at the end, apart from the report the
  harness writes), no commit, no network, nothing written under `.git/`. You MAY run, with `python -B` and output to a temp directory outside the
  repository: `bomdd/reports/eco-114-part-standard/manufacture/check_v1_v2.py <tmp>/out.txt` (from the repository root),
  `bomdd/reports/eco-114-part-standard/run_rehearsal.py ../../../../ViewPrism2 ../../../../ViewTube <tmp>/out.txt` (from that folder; it reads the two
  product repositories read-only with `git show`), and small throwaway probes of your own outside the repository.
- **Read:** the order `bomdd/60-change-order-eco-114.md` (§0 basis, §1 rule register P/O/C/A/M and the map, declared limits, §2, §3 acceptance, §4
  manufacture); the register entry ECO-114 in `bomdd/60-change-register.yaml`; the diff `git diff 25bea38b41060a04f9f4c0b9563462f01d73e2d3..286d02c944ed7429e0f899a70342cbed518e81ad`;
  `method/bomdd-playbook-v1.md` §4.1, §4.4 (for the mapping limit), §4.5, §4.6, §9; `method/templates/30-ebom.yaml`, `32-mbom.yaml`, `33-control-plan.yaml`;
  `method/prompts/phase3-design.md`; the evidence `bomdd/reports/eco-114-part-standard/` (README, rehearsal scripts and outputs, `manufacture/`).
- **Report path:** do not write the report yourself; your final message is saved by the harness. Its first non-empty line (after an optional
  `[INFORM / COMPLETE]`) starts with `ACCEPT`, `REJECT` (followed by the finding IDs) or `UNMEASURABLE <reason>`.

## What to check (each item: PASS / FAIL with evidence; a FAIL is blocking or non-blocking)

1. **Scope.** `git diff --stat 25bea38b41060a04f9f4c0b9563462f01d73e2d3..286d02c944ed7429e0f899a70342cbed518e81ad` stays inside the register entry's
   `diff_audit.allowed_paths`; nothing under `method/tools/`, `method/schemas/`, `method/contracts/`, `method/templates/product-profile/`,
   `method/templates/process-core/`, `.claude/`, `.github/`, `40-work-order.md` or `50-as-built.yaml` changed.
2. **Each rule against the text.** For P1-P4, O1-O4, C1, A1 (all seven clauses and the scope sentence) and A2: the manufactured text says what the order's
   §1 says, in the canonical place the order's map names, once; the copies the map names (the prompt's steps and G3, §9's table, 32's four-class comment)
   say the same. Report every place where the text is weaker, stronger or different.
3. **The rules against the rest of the method.** Contradictions with §4.4 (the per-ID table, `known_limits`, oracle-first), §4.5's four classes and its
   return paths, §4.6's package definition and G3, §4.7, the 30/32/33 templates' existing fields and checklists (e.g. `interface_contract` kept for units
   without a standard; `display_contract`; `depends_on`; `graph_edges`), and the fixed oracle's owner. A rule that cannot be applied as written to a shape
   the basis lists (`shapes.txt`) is in range.
4. **The acceptance evidence.** V1: does `check_v1_v2.py` check what V1 says (and fail for its own reason on the control)? V2: re-run the rehearsal; does
   `rehearse_part.py` do what A1 and C1 say, case by case; does a case pass for a reason other than its rule? The basis figures (§0) against
   `measurements.txt` / `shapes.txt`.
5. **Records.** §4 of the order and the register entry against the diff and the evidence (sha256 in the READMEs against the committed bytes).

## Report format

First line as above. Then one line per item 1-5 (PASS / FAIL), then findings with IDs `IA-01`, … (blocking / non-blocking, location, evidence with
file:line or the command you ran, a one-line direction), a section "Out of range observations" (not counted in the verdict), and a section "Not examined"
(what you did not check). State the reasoning effort you ran at if you know it.
