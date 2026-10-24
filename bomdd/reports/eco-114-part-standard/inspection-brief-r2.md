# Independent inspection brief r2 — BomDD ECO-114 (the part standard) — inspector EQ-002

- **Role: inspector.** EQ-002 (Codex CLI). Range of this round: **是正確認+回帰** (repair confirmation and regression) — whether r1's four findings are
  repaired as the order's §6 says, under the user's rulings, and whether the repair broke anything r1 found sound. New boundary exploration is out of
  range: anything new goes to "Out of range observations" and does not decide the verdict unless it is a regression.
- **Target:** BomDD commit `faffcf9d21d20f9755d881c68ff82d4815466507` (the repair). Report `git rev-parse HEAD` at start and at end (equal, otherwise
  UNMEASURABLE).
- **The user's rulings on r1 (order §6):** 1:A — IA-01 settled for ECO-114 only: the change set is ECO-114's commits, `afabdb1` (ECO-115's held draft,
  a record commit) excluded with its reason, ECO-113's method. 2:A — C1's rule text stays; whether a row measures an entry is a judgement (the
  orchestrating AI's at step 5, the inspection's reading), declared as a limit; V2 claims only C1's reference part. Do not re-raise what a ruling settled;
  check that the record and the text carry the ruling.
- **You are running inside the operator entry** (`bomdd-run.py ECO-114 …`); do not run `bomdd-run.py ECO-114 …` yourself.
- **Observable prohibitions:** no file in the repository created, changed or deleted (apart from the report the harness writes), no commit, no network,
  nothing written under `.git/`. You MAY run with `python -B`, output to a temp directory outside the repository:
  `bomdd/reports/eco-114-part-standard/manufacture/check_v1_v2.py <tmp>/v.txt` and `… --mutations <tmp>/m.txt` (from the repository root);
  `bomdd/reports/eco-114-part-standard/diff-window/diff_window.py . be96698 faffcf9d21d20f9755d881c68ff82d4815466507` and the same with
  `--control-include afabdb1` (from the root; prints Markdown); `bomdd/reports/eco-114-part-standard/run_rehearsal.py ../../../../ViewPrism2
  ../../../../ViewTube <tmp>/r.txt` (from that folder; read-only `git show` on the two product repositories — if git refuses them as of dubious
  ownership, process-local `GIT_CONFIG_*` safe-directory values are fine, as you did in r1); small throwaway probes outside the repository.
- **Read:** your r1 report `bomdd/reports/eco-114-part-standard/inspection-r1.md`; the order `bomdd/60-change-order-eco-114.md` (§1, §3, §5, §6); the
  register entry ECO-114; `git diff 5bc708a905a7fcc2bb809f5c47046fe2075e417c..faffcf9d21d20f9755d881c68ff82d4815466507`; `method/bomdd-playbook-v1.md`
  §4.5 (the limits of "部品規格"), §4.6 ("Phase 3 の順序と担当" and G3), §9; the evidence folders `manufacture/` and `diff-window/` with their READMEs.
- **Report path:** do not write the report yourself; your final message is saved by the harness. Its first non-empty line (after an optional
  `[INFORM / COMPLETE]`) starts with `ACCEPT`, `REJECT` (followed by the finding IDs) or `UNMEASURABLE <reason>`.

## What to check (each item: PASS / FAIL with evidence)

1. **IA-01 repaired under 1:A.** The diff window on ECO-114's commits `be96698..faffcf9` passes (its five checks), the positive control fails; the
   excluded commit is only `afabdb1`, before the manufacture, touching none of ECO-114's records or input files; §6 and the diff-window README say so.
2. **IA-02 repaired.** §4.6 "Phase 3 の順序と担当" states O4 completely (the roles by layer; the orchestrating AI's may-see / must-not-see equal to the
   designer's) and §9 is a matching copy.
3. **IA-03 repaired.** `check_v1_v2.py` compares each rule's clauses against the order's §1 and each copy against its canonical text; its clause list
   covers P1-P4, O1-O4, C1, A1 (scope and seven clauses) and A2; `--mutations` shows each clause's removal failing its own rule; the control tree fails.
   Report any clause of §1 the list leaves out.
4. **IA-04 under 2:A.** §4.5's limits and the order's L2 declare that "measures" is judged, not checked; V2's text claims only C1's reference part; the
   rehearsal does not claim more.
5. **Regression.** The repair changed only what §6 lists (the diff); r1's PASS items (the rules against the rest of the method; the basis figures; the
   READMEs' sha256 against the committed bytes) still hold; the rehearsal output is unchanged (byte-identical to `rehearsal.txt`).

## Report format

First line as above. Then one line per item 1-5 (PASS / FAIL), findings with IDs `IA-05`, … (blocking / non-blocking, location, evidence, a one-line
direction), "Out of range observations" (not counted), and "Not examined".
