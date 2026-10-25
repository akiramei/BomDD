# Independent inspection brief r2 — BomDD ECO-115 (the advance decision) — inspector EQ-002

- **Role: inspector.** EQ-002 (Codex CLI). Responsibility: judge whether the repairs after inspection r1 resolve its findings, and whether the
  repairs broke anything. Range of this round: **是正確認+回帰** (repair confirmation and regression).
- **Target:** BomDD commit `2aa2d7df9ec902f1c295f455c82ef78b3da6bb7a` (the repair commit). Report `git rev-parse HEAD` at start and at end (they must
  be equal; otherwise UNMEASURABLE).
- **What r1 found:** `bomdd/reports/eco-115-advance-decision/inspection-r1.md` — REJECT IA-01 to IA-07. The order's §5 records it and §6 the repairs,
  including one rule the design lacked (IA-02: the bounds line's domain in I2, its check in I3a, D5's defaults for a malformed first line), designed
  within the existing authority and carried in both the order's §1 and the playbook. The review loop is bounded at r3.
- **The order's §1 is in English; the playbook item is in Japanese**, with identifiers and values verbatim.
- **You are running inside the operator entry** (`bomdd-run.py ECO-115 …`); do not run `bomdd-run.py ECO-115 …` yourself.
- **Observable prohibitions:** no file in the repository created, changed or deleted (`git status --short` unchanged at the end, apart from the report the
  harness writes), no commit, no network, nothing written under `.git/`, nothing written in `../ViewPrism2` or `../MoviePad-Remake`. You MAY run, with
  `python -B` and every output in a temp directory outside the repository:
  `bomdd/reports/eco-115-advance-decision/manufacture/check_v1_v2.py . ../ViewPrism2 ../MoviePad-Remake <tmp>` (from the repository root), from
  `bomdd/reports/eco-115-advance-decision/`: `run_rehearsal_v2.py ../../../../ViewPrism2 <tmp>/out.txt`, `run_moviepad.py ../../../../MoviePad-Remake
  <tmp>/out.txt`, `run_moviepad_d2.py ../../../../MoviePad-Remake <tmp>/out.txt`, `rehearse_sequence.py <tmp>/out.txt`, and
  `repair-r1/redfirst_c5.py` as its README says (its scratch copy outside the repository), plus small throwaway probes of your own outside the
  repository. Set `PYTHONIOENCODING=utf-8` on a Windows console; if git refuses a repository's ownership, use process-local settings only (as in r1).
- **Read:** r1's report; the order `bomdd/60-change-order-eco-115.md` (§1, §3, §5, §6); the register entry ECO-115; the diff
  `git diff 35961c32d916c71ecd10a9124df5fee9574a7e0a..2aa2d7df9ec902f1c295f455c82ef78b3da6bb7a`; `method/bomdd-playbook-v1.md` §4.4's item
  "前進の判定" and §6.1; `method/templates/40-work-order.md`; the evidence `bomdd/reports/eco-115-advance-decision/` (README, the rehearsal scripts and
  outputs, `manufacture/`, `repair-r1/`).
- **Report path:** do not write the report yourself; your final message is saved by the harness. Its first non-empty line (after an optional
  `[INFORM / COMPLETE]`) starts with `ACCEPT`, `REJECT` (followed by the finding IDs) or `UNMEASURABLE <reason>`.

## What to check (each item: PASS / FAIL with evidence; a FAIL is blocking or non-blocking)

1. **Each r1 finding resolved.** For IA-01 to IA-07: does the repair do what the finding's direction asks, in the text and in the rehearsal, and does
   its arm fail for the finding's own reason when the repair is taken away (the red-first evidence in `repair-r1/`, or your own probe — re-run your r1
   probes)? IA-02: is the new rule stated the same in §1 and in the playbook, and is it deterministic for every malformed shape?
2. **Regression.** Only the repair's files changed (`git diff --stat` of the range above, inside the register entry's `diff_audit.allowed_paths`);
   the rest of the manufactured text and templates unchanged; the four rehearsals re-run byte-identical to their stored outputs and exit 0; the real-data
   results (ViewPrism2 R0/R1, MoviePad-Remake M0/M1, N0/N1) unchanged from r1's target apart from what §6 lists; V1/V2 PASS and its control on
   `35961c3` fails for the repaired clauses.
3. **Records.** §5 and §6 of the order, the register entry and the READMEs (sha256 against the committed bytes) against the diff and the evidence.

## Report format

First line as above. Then one line per item 1-3 (PASS / FAIL), then findings with IDs `IA-08`, … (blocking / non-blocking, location, evidence with
file:line or the command you ran, a one-line direction), a section "Out of range observations" (not counted in the verdict), and a section "Not examined"
(what you did not check). State the reasoning effort you ran at if you know it.
