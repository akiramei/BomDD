# Independent inspection brief r3 — BomDD ECO-114 (the part standard) — inspector EQ-002

- **Role: inspector.** EQ-002 (Codex CLI). Range of this round: **是正確認+回帰** — whether r2's finding IA-05 is settled as the order's §8 says, under
  the user's ruling, and whether the repair broke anything. Anything new goes to "Out of range observations" and does not decide the verdict unless it is
  a regression.
- **Target:** BomDD commit `c2211537b8468aea3e6f203ebe48634c2f7a33c4`. Report `git rev-parse HEAD` at start and at end (equal, otherwise UNMEASURABLE).
- **The user's ruling on r2 (order §8), "C":** extend V1's clause list to the clauses r2 named, and declare that the completeness of the method text
  against §1 beyond the list is the independent inspection's reading (V1's text, L6). Do not re-raise that the list is not a derivation of §1 — the
  ruling settled it. Check that the clauses r2 named are now in the list (or say which are not), that each removal fails its rule, and that V1's text
  and L6 carry the ruling. Then read the method text against §1 yourself — that reading is now part of the gate — and report any clause of §1 the method
  text does not state (a defect of the text, not of the list).
- **You are running inside the operator entry** (`bomdd-run.py ECO-114 …`); do not run `bomdd-run.py ECO-114 …` yourself.
- **Observable prohibitions:** no file in the repository created, changed or deleted (apart from the report the harness writes), no commit, no network,
  nothing written under `.git/`. You MAY run with `python -B`, output to a temp directory outside the repository:
  `bomdd/reports/eco-114-part-standard/manufacture/check_v1_v2.py <tmp>/v.txt` and `… --mutations <tmp>/m.txt` (from the repository root);
  `bomdd/reports/eco-114-part-standard/diff-window/diff_window.py . be96698 c2211537b8468aea3e6f203ebe48634c2f7a33c4` and the same with
  `--control-include afabdb1`; `bomdd/reports/eco-114-part-standard/run_rehearsal.py ../../../../ViewPrism2 ../../../../ViewTube <tmp>/r.txt` (from
  that folder; process-local `GIT_CONFIG_*` safe-directory values are fine); small throwaway probes outside the repository.
- **Read:** your r2 report `bomdd/reports/eco-114-part-standard/inspection-r2.md`; the order `bomdd/60-change-order-eco-114.md` (§1, §3, §7, §8 and the
  limits); `git diff 45fcc6608baa6bfb51c1a6202a38e5cdb2c082b2..c2211537b8468aea3e6f203ebe48634c2f7a33c4`; `method/bomdd-playbook-v1.md` §4.1, §4.5, §4.6,
  §9; the templates 30/32/33 and `method/prompts/phase3-design.md`; the evidence folders with their READMEs.
- **Report path:** do not write the report yourself; your final message is saved by the harness. Its first non-empty line (after an optional
  `[INFORM / COMPLETE]`) starts with `ACCEPT`, `REJECT` (followed by the finding IDs) or `UNMEASURABLE <reason>`.

## What to check (each item: PASS / FAIL with evidence)

1. **IA-05 under "C".** The clauses r2 named are in `check_v1_v2.py`'s list; `--mutations` catches every listed clause; V1 PASS on the tree and FAIL on the
   filing tree `25bea38`; the order's V1 text and L6 state the ruling.
2. **The method text against §1 (your reading).** Every clause of §1 (P1-P4, O1-O4, C1, A1 with its scope, A2) is stated in its canonical place and the
   copies match. Report omissions or contradictions of the text.
3. **Regression.** The repair changed only §8's areas (the diff); the diff window `be96698..c221153` passes and its control fails; the rehearsal output
   is unchanged; the READMEs' sha256 match the committed bytes.

## Report format

First line as above. Then one line per item 1-3 (PASS / FAIL), findings with IDs `IA-06`, … (blocking / non-blocking, location, evidence, a one-line
direction), "Out of range observations" (not counted), and "Not examined".
