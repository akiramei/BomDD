# ECO-115 — repairs after independent inspection r2 (REJECT IA-08 to IA-10)

Run 2026-10-26 from the BomDD root. All files are LF; sha256 of the committed bytes.

| File | What | sha256 |
|---|---|---|
| `v1-v2.txt` | `../manufacture/check_v1_v2.py` on the repaired tree: PASS 120/120 (the same bytes as after r1's repairs: the report prints counts) | `0a586111b33237fdf2b627475a71523c3fda183dc20b00d156975e8d79f9bc30` |
| `control-on-r1-repair-tree.txt` | the same script on the tree of r1's repairs (`2aa2d7d`, these repairs stashed): FAIL 119/120 — I2's domain clause | `73ae716d71eee2a748fa7608ee7dcfae24b98d619580325a4424b9c0a85f5508` |
| `redfirst-decision.txt` | the repaired `run_rehearsal_v2.py` against `2aa2d7d`'s `rehearse_decision_v2.py`: exit 1, 3 MISSED (the IA-09 arm that expects the ref defects beside the bounds one; 1000; 5,000 digits) | `98e7393fbc25c94674f3b4e00e3b51f1da52f25df71f371dcc82cbde9d8f8f4c` |
| `redfirst_domain.py` | runs the domain control of `../repair-r4/redfirst_all.py` (the shared parser's domain opened in a scratch copy); exit 0 only on the signature: the D5 rehearsal stops on Z3 with `ValueError` | `63d5088e69a5be87f7567cd690e7108ede0ca303f8103c90a71ff49be4ccda38` |
| `redfirst-domain.txt` | its output: exit 1, `ValueError` on Z3's 5,000-digit line (the inspector's probe) | `0db1525e01cef55bc17b0c2ffe9ba2505f82de8104baa903aca73f5b0bd89791` |

What each repair is (the order's section 8 has the account):
- IA-08 — the order's L7 now gives the evidenced scale (two MoviePad-Remake deliveries), as the playbook's limits already did.
- IA-09 — `rehearse_decision_v2.py` checks the bounds line on its own, before the frozen-revision branch (r1's repair had chained it in, so a
  malformed line hid the ref, ancestry and binding checks); two arms on a malformed line with swapped refs, each expecting one of the reasons.
- IA-10 — the bounds values are closed at 1 to 999 (no leading zero) in the order's I2, the playbook, the work order template and both rehearsals;
  arms at 999, 1000 and 5,000 digits, and Z3 in `rehearse_sequence.py`.

Command for the red-first decision run: a scratch folder with `2aa2d7d`'s `rehearse_decision_v2.py`, the repaired `run_rehearsal_v2.py` and
`vp2-cp-results.xml.gz`, then `python -B run_rehearsal_v2.py <ViewPrism2> <out>`. For the domain:
`python -B repair-r2/redfirst_domain.py <scratch>` (from `bomdd/reports/eco-115-advance-decision/`).

Since inspection r4 (IA-13): r3 moved the bounds parser into `rehearse_decision_v2.py`, which this helper's first form neither copied nor patched, and it accepted any child failure; it now runs the self-verifying control of `../repair-r4/redfirst_all.py`. That script also re-runs the decision run above, staged with every file it imports, and checks it against its expected misses.
