# Independent inspection brief r6 — BomDD ECO-115 (the advance decision) — inspector EQ-002

- **Role: inspector.** EQ-002 (Codex CLI). Responsibility: judge whether the repairs after inspection r5 resolve IA-14 and IA-15, and whether
  anything already accepted regressed. Range of this round: **是正確認+回帰** (repair confirmation and regression), **narrowed by the user's ruling**:
  confirm IA-14 and IA-15, and check the regression of the whole. Do not open new lines of search for further classes of defect beyond these; a
  blocking defect you meet while confirming or checking regression is still reported.
- **Target:** BomDD commit `47b4df7637157392705a498fd2687e426f5474f0` (the commit repairing r5). Report `git rev-parse HEAD` at start and at end (they must be equal;
  otherwise UNMEASURABLE).
- **History:** `bomdd/reports/eco-115-advance-decision/inspection-r1.md` to `inspection-r5.md` (findings IA-01 to IA-15); the order records each
  round and its repairs in §5 to §14. r5 reached the bound extended to it; the user ruled "A" (§14): repair IA-14 and IA-15, then this round with
  its range narrowed. If it is not ACCEPT, the ECO goes to the human's disposition.
- **The order's §1 is in English; the playbook item is in Japanese**, with identifiers and values verbatim.
- **You are running inside the operator entry** (`bomdd-run.py ECO-115 …`); do not run `bomdd-run.py ECO-115 …` yourself.
- **Observable prohibitions:** no file in the repository created, changed or deleted (`git status --short` unchanged at the end, apart from the report the
  harness writes), no commit, no network, nothing written under `.git/`, nothing written in `../ViewPrism2` or `../MoviePad-Remake`. You MAY run, with
  `python -B` and every output in a temp directory outside the repository:
  `bomdd/reports/eco-115-advance-decision/manufacture/check_v1_v2.py . ../ViewPrism2 ../MoviePad-Remake <tmp>` (from the repository root), from
  `bomdd/reports/eco-115-advance-decision/`: `run_rehearsal_v2.py ../../../../ViewPrism2 <tmp>/out.txt`, `run_moviepad.py ../../../../MoviePad-Remake
  <tmp>/out.txt`, `run_moviepad_d2.py ../../../../MoviePad-Remake <tmp>/out.txt`, `rehearse_sequence.py <tmp>/out.txt`, and
  `repair-r4/redfirst_all.py ../../../../ViewPrism2 <tmp>`, plus small throwaway probes of your own outside the repository (a scratch copy of files
  you mutate). Set `PYTHONIOENCODING=utf-8` on a Windows console; if git refuses a repository's ownership, use process-local settings only.
- **Read:** r5's report; the order `bomdd/60-change-order-eco-115.md` (§1, §3, §13, §14); the register entry ECO-115; the diff
  `git diff 50ce8d43cc391fb0eb0c0dd910e6d2eda1024d9f..47b4df7637157392705a498fd2687e426f5474f0`; the evidence `bomdd/reports/eco-115-advance-decision/` (README, `manufacture/`,
  `repair-r4/`, `repair-r5/`).
- **Report path:** do not write the report yourself; your final message is saved by the harness. Its first non-empty line (after an optional
  `[INFORM / COMPLETE]`) starts with `ACCEPT`, `REJECT` (followed by the finding IDs) or `UNMEASURABLE <reason>`.

## What to check (each item: PASS / FAIL with evidence; a FAIL is blocking or non-blocking)

1. **IA-14 and IA-15 resolved.** IA-14: does each red-first control pass only for its own revision, exact misses and clean stderr, and refuse a wrong
   set-up (re-run your r5 probe)? IA-15: are I2's closed values read from the playbook and every copy (the order's §1, the template) compared as an exact
   set, so that an added or a removed value fails (re-run your r5 probe)?
2. **Regression.** Only the repair's files changed (`git diff --stat` of the range above, inside the register entry's `diff_audit.allowed_paths`); the
   method text and templates unchanged in this range; the four rehearsals re-run byte-identical and exit 0; IA-01 to IA-13 still resolved; V1/V2 PASS.
3. **Records.** §14 of the order, the register entry and the READMEs (sha256 against the committed bytes) against the diff and the evidence.

## Report format

First line as above. Then one line per item 1-3 (PASS / FAIL), then findings with IDs `IA-16`, … (blocking / non-blocking, location, evidence with
file:line or the command you ran, a one-line direction), a section "Out of range observations" (not counted in the verdict), and a section "Not examined"
(what you did not check). State the reasoning effort you ran at if you know it.
