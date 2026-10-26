# Independent inspection brief r4 — BomDD ECO-115 (the advance decision) — inspector EQ-002

- **Role: inspector.** EQ-002 (Codex CLI). Responsibility: judge whether the repair after inspection r3 resolves its finding, and whether the
  repairs broke anything. Range of this round: **是正確認+回帰** (repair confirmation and regression).
- **Target:** BomDD commit `11982a45097fa6418b04eb6df32a689be0ed78d0` (the commit repairing r3). Report `git rev-parse HEAD` at start and at end (they must
  be equal; otherwise UNMEASURABLE).
- **What r1 to r3 found:** `inspection-r1.md` (REJECT IA-01 to IA-07; §5, repairs §6), `inspection-r2.md` (REJECT IA-08 to IA-10; §7, repairs
  §8) and `inspection-r3.md` (REJECT IA-11 — I3a and D5 read a bounds line's trailing whitespace differently; §9), all under
  `bomdd/reports/eco-115-advance-decision/`. r3 reached the review loop's bound; **the user extended it by this one round ("A", §10)**, and if this
  round is not ACCEPT the ECO goes to the human's disposition, so report every blocking defect you find.
- **The order's §1 is in English; the playbook item is in Japanese**, with identifiers and values verbatim.
- **You are running inside the operator entry** (`bomdd-run.py ECO-115 …`); do not run `bomdd-run.py ECO-115 …` yourself.
- **Observable prohibitions:** no file in the repository created, changed or deleted (`git status --short` unchanged at the end, apart from the report the
  harness writes), no commit, no network, nothing written under `.git/`, nothing written in `../ViewPrism2` or `../MoviePad-Remake`. You MAY run, with
  `python -B` and every output in a temp directory outside the repository:
  `bomdd/reports/eco-115-advance-decision/manufacture/check_v1_v2.py . ../ViewPrism2 ../MoviePad-Remake <tmp>` (from the repository root), from
  `bomdd/reports/eco-115-advance-decision/`: `run_rehearsal_v2.py ../../../../ViewPrism2 <tmp>/out.txt`, `run_moviepad.py ../../../../MoviePad-Remake
  <tmp>/out.txt`, `run_moviepad_d2.py ../../../../MoviePad-Remake <tmp>/out.txt`, `rehearse_sequence.py <tmp>/out.txt`, and
  `repair-r1/redfirst_c5.py` and `repair-r2/redfirst_domain.py` as their READMEs say, and the red-first set-up in `repair-r3/README.md` (scratch copies outside the repository), plus small throwaway probes of your own outside the
  repository. Set `PYTHONIOENCODING=utf-8` on a Windows console; if git refuses a repository's ownership, use process-local settings only (as in r1).
- **Read:** r1's, r2's and r3's reports; the order `bomdd/60-change-order-eco-115.md` (§1, §3, §5 to §10); the register entry ECO-115; the diff
  `git diff 7eddaba48d486b17bb6943d0d88e8eb3ef60df24..11982a45097fa6418b04eb6df32a689be0ed78d0` (and `35961c32d916c71ecd10a9124df5fee9574a7e0a..11982a45097fa6418b04eb6df32a689be0ed78d0` for all the repairs); `method/bomdd-playbook-v1.md` §4.4's item
  "前進の判定" and §6.1; `method/templates/40-work-order.md`; the evidence `bomdd/reports/eco-115-advance-decision/` (README, the rehearsal scripts and
  outputs, `manufacture/`, `repair-r1/`, `repair-r2/`, `repair-r3/`).
- **Report path:** do not write the report yourself; your final message is saved by the harness. Its first non-empty line (after an optional
  `[INFORM / COMPLETE]`) starts with `ACCEPT`, `REJECT` (followed by the finding IDs) or `UNMEASURABLE <reason>`.

## What to check (each item: PASS / FAIL with evidence; a FAIL is blocking or non-blocking)

1. **The finding resolved.** For IA-11 (and IA-02 and IA-10, which it kept open): do I3a and D5 now read every bounds line the same way, in the
   text and in the rehearsals; does the arm fail for the finding's own reason when the repair is taken away (`repair-r3/`, or your own probe — re-run
   your r3 probe, including whitespace and other characters at the line's end); is the bounds rule stated the same in §1, the playbook and the
   template, and fully determined (form, values and the line's end)?
2. **Regression.** Only the repair's files changed (`git diff --stat` of the range above, inside the register entry's `diff_audit.allowed_paths`);
   the rest of the manufactured text and templates unchanged; the four rehearsals re-run byte-identical to their stored outputs and exit 0; the real-data
   results unchanged from r3's target; IA-01 to IA-10 still resolved; V1/V2 PASS and its control on `7eddaba` fails for the repaired clause.
3. **Records.** §9 and §10 of the order, the register entry and the READMEs (sha256 against the committed bytes) against the diff and the evidence.

## Report format

First line as above. Then one line per item 1-3 (PASS / FAIL), then findings with IDs `IA-12`, … (blocking / non-blocking, location, evidence with
file:line or the command you ran, a one-line direction), a section "Out of range observations" (not counted in the verdict), and a section "Not examined"
(what you did not check). State the reasoning effort you ran at if you know it.
