# Independent inspection brief r1 — BomDD ECO-115 (the advance decision: the receiving side decides from the records alone whether a delivered individual enters Phase 5, and reads a work's decisions over time) — inspector EQ-002

- **Role: inspector.** EQ-002 (Codex CLI). Responsibility: judge whether the manufactured method text and templates implement the order's rules, and
  whether the acceptance evidence shows what the order claims. Range of this round: **境界探索** (boundary exploration — where the rules can be read wrongly,
  contradict the rest of the method, or are stronger in the record than in the text).
- **Target:** BomDD commit `35961c32d916c71ecd10a9124df5fee9574a7e0a` (the manufacture commit). Report `git rev-parse HEAD` at start and at end (they must
  be equal; otherwise UNMEASURABLE).
- **The design was adopted by the user's cut-off rulings while unconverged under the converge rule** (the order's header and receipt, loops 1-6). Its
  rules are the object of this inspection as manufactured; a finding that the text departs from the order, or that a rule cannot be applied as written,
  is in range. **The repairs made after loop 4 round 2 and loop 6 round 2 (the receipt) were checked by the rehearsals only and have had no review; this
  inspection is their first.**
- **The order's §1 is in English; the playbook item is in Japanese** (the playbook's language), with identifiers and values verbatim. Read the Japanese
  text against §1 clause by clause.
- **You are running inside the operator entry** (`bomdd-run.py ECO-115 …`); do not run `bomdd-run.py ECO-115 …` yourself.
- **Observable prohibitions:** no file in the repository created, changed or deleted (`git status --short` unchanged at the end, apart from the report the
  harness writes), no commit, no network, nothing written under `.git/`, nothing written in `../ViewPrism2` or `../MoviePad-Remake`. You MAY run, with
  `python -B` and every output in a temp directory outside the repository:
  `bomdd/reports/eco-115-advance-decision/manufacture/check_v1_v2.py . ../ViewPrism2 ../MoviePad-Remake <tmp>` (from the repository root; it re-runs the
  four rehearsals below into `<tmp>`), and from `bomdd/reports/eco-115-advance-decision/`: `run_rehearsal_v2.py ../../../../ViewPrism2 <tmp>/out.txt`,
  `run_moviepad.py ../../../../MoviePad-Remake <tmp>/out.txt`, `run_moviepad_d2.py ../../../../MoviePad-Remake <tmp>/out.txt`,
  `rehearse_sequence.py <tmp>/out.txt` (the product repositories are read with `git show` only), and small throwaway probes of your own outside the
  repository. Set `PYTHONIOENCODING=utf-8` on a Windows console.
- **Read:** the order `bomdd/60-change-order-eco-115.md` (§0 basis, §1 rule register I/D/M, declared limits L1-L9, §2, §3 acceptance, §4 manufacture,
  the receipt for the loop 4 and loop 6 repairs); the register entry ECO-115 in `bomdd/60-change-register.yaml`; the diff
  `git diff 37e0fd9d7ba1c091d0e641961f063196893a898e..35961c32d916c71ecd10a9124df5fee9574a7e0a`; `method/bomdd-playbook-v1.md` §1, §4.4 (the new item
  "前進の判定" and the per-ID-table item before it), §4.5 (the three kinds returned to the human, P3), §6.1, §8.5, §13; `method/templates/33-control-plan.yaml`,
  `50-as-built.yaml`, `40-work-order.md`, `32-mbom.yaml` (ECO-114's `mbom.assembly`); the evidence `bomdd/reports/eco-115-advance-decision/` (README,
  rehearsal scripts and outputs, `manufacture/`).
- **Report path:** do not write the report yourself; your final message is saved by the harness. Its first non-empty line (after an optional
  `[INFORM / COMPLETE]`) starts with `ACCEPT`, `REJECT` (followed by the finding IDs) or `UNMEASURABLE <reason>`.

## What to check (each item: PASS / FAIL with evidence; a FAIL is blocking or non-blocking)

1. **Scope.** `git diff --stat 37e0fd9d7ba1c091d0e641961f063196893a898e..35961c32d916c71ecd10a9124df5fee9574a7e0a` stays inside the register entry's
   `diff_audit.allowed_paths`; nothing under `method/tools/`, `method/schemas/`, `method/templates/product-profile/`, `method/templates/process-core/`,
   `.claude/`, `.github/`, `method/prompts/`, `30-ebom.yaml` or `32-mbom.yaml` changed.
2. **Each rule against the text.** For I0, I1, I2, I3a, I3b, I4, D0, D1, D2, D3, D4 and D5 (the ledger and its three fields, convergence with the two bounds
   and the declared departure from §8.5, C1-C6 with their owners, what follows, what reaches the human) and the limits bullet against L1-L9: the
   manufactured text says what the order's §1 says, once, in the new §4.4 item; the one-line references (§1's flow, §6.1, the per-ID-table item's
   `on_fail` sentence) and the template comments say the same. Report every place where the text is weaker, stronger or different.
3. **The rules against the rest of the method.** Contradictions with §4.4 (the per-ID table as the approver's input), §4.5's three kinds and P3, §6.1,
   §8.5 (its default disposition) and §13 (pending human disposition), R-050 and ECO-088's re-measurement (the As-Built checklist), the known-defect
   acceptance (ECO-108 / ECO-111), and the templates' existing fields and checklists. A rule that cannot be applied as written to the real records the
   basis and the rehearsals read (ViewPrism2, MoviePad-Remake deliveries 1 and 2) is in range.
4. **The acceptance evidence.** V1: does `check_v1_v2.py` check what V1 says, and does it fail for its own reason on the filing tree (its README states
   what its clause check does not measure)? V2: re-run; do the rehearsal scripts (`rehearse_decision_v2.py`, `rehearse_sequence.py`) do what I3a, I3b,
   D1, D2, D4 and D5 say, arm by arm; does an arm pass for a reason other than its rule; are D5's arm expectations fixed before the arms run?
5. **Records.** §4 of the order and the register entry against the diff and the evidence (sha256 in the READMEs against the committed bytes).

## Report format

First line as above. Then one line per item 1-5 (PASS / FAIL), then findings with IDs `IA-01`, … (blocking / non-blocking, location, evidence with
file:line or the command you ran, a one-line direction), a section "Out of range observations" (not counted in the verdict), and a section "Not examined"
(what you did not check). State the reasoning effort you ran at if you know it.
