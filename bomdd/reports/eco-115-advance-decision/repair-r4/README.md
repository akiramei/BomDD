# ECO-115 — the common cause removed and the repairs after independent inspection r4 (REJECT IA-12, IA-13), under the user's "A"

Run 2026-10-26 from the BomDD root. All files are LF; sha256 of the committed bytes.

| File | What | sha256 |
|---|---|---|
| `redfirst_all.py` | (repaired after inspection r5, IA-14: exact misses, staged identity, stderr, two negative set-ups — `../repair-r5/`; `redfirst-all.txt` below is its first output) every red-first control of the repairs (r1, r2 and r3's decision runs against the code each repair replaced; the C5 and the domain controls), each staged in a new scratch folder with every file it imports and passing only on its own expected failure signature; exit 0 only when all show it | `96d5152d3480331387bd391604048cc1705c4982253616de956c60f2ca0acbda` |
| `redfirst-all.txt` | its output: 5 of 5 controls show their signature | `5b072373c2bc6a1598afb6d0bddf6a9ec844af59b12dea86ff000feb8e955202` |
| `v1-v2.txt` | `../manufacture/check_v1_v2.py` on the repaired tree: PASS 123/123 | `0276a8d3ffd22b648f07717db062355c6b2242549ebb283e690fecbdffde7034` |
| `control-on-r3-repair-tree.txt` | the same script on the tree of r3's repair (`11982a4`, these changes stashed): FAIL 121/123 — the template and the order's §1 do not carry the playbook's sentence | `a0ba8bd79f3d83544904359e214f251bf19dcdf225d5f20f0c3555d68b0d40b7` |

**The common cause.** The bounds line's rule had been written in five places (the order's §1, the playbook, the work order template, two scripts),
and r2 to r4 found three times that a repair left one behind. Now: the playbook's I2 sentence is the one statement of the rule; the work order
template and the order's §1 carry it verbatim; V1 reads the sentence from the playbook and checks that both copies hold it; the two scripts share
one parser (since r3) and agree on 84 lines (`run_rehearsal_v2.py`).

**IA-12** — the template now holds the sentence, "without leading zeros" included, and V1 checks it (above).

**IA-13** — the earlier helpers (`../repair-r1/redfirst_c5.py`, `../repair-r2/redfirst_domain.py`) run the controls of `redfirst_all.py`; the
decision runs are re-run by it too. `run_rehearsal_v2.py`'s agreement check reports "not measurable" and fails, instead of crashing, when it runs
against an older rehearsal without the shared reader, so a control on old code finishes and shows its misses. A defect of `redfirst_all.py` found
before its output: it cut arm names at their first colon, so the r2 control missed an arm whose name holds one.

Command: `python -B repair-r4/redfirst_all.py ../../../../ViewPrism2 <scratch>` (from `bomdd/reports/eco-115-advance-decision/`).
