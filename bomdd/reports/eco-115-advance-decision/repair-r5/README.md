# ECO-115 — repairs after independent inspection r5 (REJECT IA-14, IA-15), under the user's "A" (a narrowed r6)

Run 2026-10-26 from the BomDD root. All files are LF; sha256 of the committed bytes.

| File | What | sha256 |
|---|---|---|
| `v1-v2.txt` | `../manufacture/check_v1_v2.py` (repaired) on the repaired tree: PASS 144/144 — 11 I2 checks (the playbook yields every vocabulary; five vocabularies × two copies) and 10 mutations of the copies, each caught | `b7f595b754484d8cd8424f24cee693a0f8cbe58b94983cf2e08293b46dcf8af8` |
| `control-on-r4-repair-tree.txt` | the same script on the tree of r4's repairs (`460dc6b`): PASS 144/144 — the same bytes, because IA-15 changed the check, not the text (the copies were already equal); the discriminating evidence is the mutations and the probe below | `b7f595b754484d8cd8424f24cee693a0f8cbe58b94983cf2e08293b46dcf8af8` |
| `ia15-probe-r4-check.txt` | the inspector's IA-15 probe repeated: a scratch copy of the method files whose template `approver` comment gains `\| maintainer`, checked by `460dc6b`'s `check_v1_v2.py`: PASS 123/123 (the miss) — the same bytes as `../repair-r4/v1-v2.txt`, since that check prints counts only | `0276a8d3ffd22b648f07717db062355c6b2242549ebb283e690fecbdffde7034` |
| `ia15-probe-repaired-check.txt` | the same mutated copy checked by the repaired script: FAIL 141/144 — the template's approver set differs from the playbook's (and two mutation checks report that their text is no longer there, which is true of the mutated copy) | `179a639b22da79a30bf00f87f501794a4458eebc6633aa58bbc9c7b478564afd` |
| `redfirst-all.txt` | `../repair-r4/redfirst_all.py` (repaired): 5 of 5 controls show their own failure, each with its staged files proved to be the named revision's and the exact set of misses; 2 of 2 wrong set-ups refused (the inspector's IA-14 probe — `35961c3` staged for the r2 control — and the C5 control without the shared parser) | `fe18487bed7854b6f02d50c1997d5f29cc279783b74e19728f3e77076c145c28` |

**IA-15.** I2's closed values (`approver`, `on_fail` keys and values, `status`, `outcomes`) are read from the playbook's I2 sentences; the order's
§1 and the template (its comments, and the `on_fail` keys of its first row) must hold exactly those sets — an added or a removed value fails.
Ten mutations (a value added or removed in each vocabulary of the template; two in the order) are each caught.

**IA-14.** Each decision control declares the exact set of arms its revision's code misses (that revision's own finding's arms and those added for
every later finding) and requires equality, checks with git's object ids that the staged rehearsals are that revision's blobs and the driver the
current tree's, and requires an empty stderr; the C5 and domain controls check identity before their mutation. The two wrong set-ups are kept as
permanent negative checks of the runner.

Command: `python -B repair-r4/redfirst_all.py ../../../../ViewPrism2 <scratch>` (from `bomdd/reports/eco-115-advance-decision/`).
