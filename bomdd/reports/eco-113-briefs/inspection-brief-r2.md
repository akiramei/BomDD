# Independent inspection brief r2 — BomDD ECO-113 (the run journal read in order; invalid records JOURNAL_CORRUPT) — inspector EQ-002

- **Role: inspector.** EQ-002 (Codex CLI). Responsibility: judge whether the repair implements the amended rules and whether the acceptance evidence
  shows what the order claims. Range of this round: **是正確認+回帰** (correction confirmation and regression): are r1's IA-01 and IA-02 repaired,
  and did the repair break anything r1 passed?
- **Target:** BomDD commit `fcd9fd70977da709cd4152e9f66b98bf0e23ea3c` (the repair commit). Report `git rev-parse HEAD` at start and at end (they must be equal; otherwise UNMEASURABLE).
- **You are running inside the entry you inspect** (as in r1): your process tree is in a kill-on-close Job Object named
  `Local\BomDD-run-ECO-113-<run_id>`, and the entry holds `<git-common-dir>/bomdd-run/ECO-113.lock` until you end. Do not stop or release that run,
  and do not run `bomdd-run.py ECO-113 …` against the real repository (it reads `ENTRY_ALIVE`, by design).
- **Observable prohibitions:** no file in the repository created, changed or deleted (`git status --short` empty at the end), no commit, no network,
  nothing written under the repository's `.git/bomdd-run/` or `.git/bomdd-witness/`. You MAY run, with `python -B`: `method/tools/bomdd-run.py
  --selftest` (about 80 seconds), `method/tools/bomdd-job.py --selftest`, `method/tools/bomdd-witness.py --selftest`, the rule-mutation script
  `bomdd/reports/eco-113-manufacture/rule_mutations.py <repo>/method/tools <a temp dir> [case …]` (one selftest per case; the A4 cases are
  `A4i-not-object A4ii-run-id A4iii-order A4iv-integer A4iv-position A4iv-boundary A4iv-digest`), the diff-window check
  `bomdd/reports/eco-113-briefs/diff-window/diff_window.py <repo> f2d91d4 fcd9fd70977da709cd4152e9f66b98bf0e23ea3c` (and with `--control-include 597e842`, which must fail), and small
  throwaway probes of your own in a temp directory outside the repository. Run the selftests one at a time (OBS-20261018-03).
- **Read:** the order `bomdd/60-change-order-eco-113.md` — the amendment ruling and extension paragraphs at the top, §1 J1, J2, R3, A3, A4, L11, §3
  V4(f), V4(q) and the coverage line, §5 (r1), §6 (the repair), the receipts "Amendment loop A" and "Amendment loop A2"; r1's report
  `bomdd/reports/eco-113-briefs/inspection-r1.md`; the diff `git diff 9163625..fcd9fd70977da709cd4152e9f66b98bf0e23ea3c` (the amendment `860097d` and the repair); in
  `method/tools/bomdd-run.py` the functions `_quarantine_fault`, `journal_read`, `open_runs`, `judge`, `_recover`, and the selftest block after
  `V4(f)/(q)(ECO-113 修正 1:A)`; the evidence `bomdd/reports/eco-113-manufacture/repair/`.
- **The change set under the exception ruling (user "2:a"):** ECO-113's commits only; the other commits in the register's window (`f2d91d4..`) are
  excluded with their reasons by `diff_window.py` (ECO-112's commits — manufactured first by ECO-112 M1 — and three record commits). Judge the
  exclusion by its record, not by applying the window literally.
- **Report path:** do not write the report yourself; your final message is saved by the harness. Its first non-empty line (after an optional
  `[INFORM / COMPLETE]`) starts with `ACCEPT`, `REJECT` (followed by the finding IDs) or `UNMEASURABLE <reason>`.

## What to check (each item: PASS / FAIL with evidence; a FAIL is blocking or non-blocking)

1. **IA-01 repaired.** The journal is read in order per J1: a closing record closes only an earlier `start` of its id; a closing record for a closed run
   closes nothing; a second `start` for an open id and a closing record with no earlier `start` are invalid (A4 (iii)); a reused id after close opens a
   new run. Re-run r1's probes and the sequences you think most likely to break it.
2. **IA-02 repaired.** A4 (i), (ii), (iv): non-objects, non-string or empty `run_id` on `start`/`end`/`abort`/`release`, and quarantines whose offset is
   not an integer, past their own position, not at a line boundary, or whose digest (the corrupt lines before `offset`, each with its `\n`) does not
   match, are `JOURNAL_CORRUPT` and exclude nothing; a valid quarantine (R3's own) excludes, in order; L11's statement of what is and is not detected.
3. **The amended text against the code.** J1, J2's sentence, A3, A4, R3, L11 as amended; the S4 `JOURNAL_CORRUPT` row (unchanged; `corrupt_offset` per A4).
4. **The acceptance evidence.** V4(f)'s observations and its mutation requirement (one mutation per A4 clause, each caught on its own arm), V4(q)'s reuse,
   as recorded in §6 and `bomdd/reports/eco-113-manufacture/repair/`.
5. **Regression.** Everything r1 passed (X, W, R, S, O, T, V1-V5 and their arms) still holds: the three selftests exit 0, the earlier 20 ECO-113 and
   ECO-112's 9 rule mutations are still caught (re-run whichever you doubt), and `bomdd-witness.py` is unchanged (`git diff 2271102..fcd9fd70977da709cd4152e9f66b98bf0e23ea3c --
   method/tools/bomdd-witness.py` empty).
6. **Scope under the exception ruling.** `diff_window.py` PASS on `f2d91d4..fcd9fd70977da709cd4152e9f66b98bf0e23ea3c` and its positive control FAIL; the excluded commits and their reasons;
   ECO-113's change set inside §2's paths.
7. **Records.** The order's §5, §6, the two amendment receipts and the register entry claim nothing that the code or the evidence does not show.

## Report format (your final message, in full)

```
[INFORM / COMPLETE]

ACCEPT            ← or REJECT IA-03, … / UNMEASURABLE <reason>

- inspector: EQ-002 / Codex CLI / <model>
- HEAD at start / at end: <sha> / <sha>
- commits: 0 / files changed: 0
- selftests run: bomdd-run <first line>, bomdd-job <first line>, bomdd-witness <first line>

## Items
| # | item | verdict | evidence (file:line, command and the key output) |

## Findings (IA-03, …)
- each: blocking / non-blocking, where, what is wrong, a suggested repair

## Not checked (limits)
```
