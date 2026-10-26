# ECO-115 — repair after independent inspection r3 (REJECT IA-11), under the user's "A" (one more round)

Run 2026-10-26 from the BomDD root. All files are LF; sha256 of the committed bytes.

| File | What | sha256 |
|---|---|---|
| `v1-v2.txt` | `../manufacture/check_v1_v2.py` on the repaired tree: PASS 120/120 | `da1ffddc877f67c6e57ee88f24dcbe1d517d3981ffdc1d585e996eba4e51f9c6` |
| `control-on-r2-repair-tree.txt` | the same script on the tree of r2's repairs (`7eddaba`, this repair stashed): FAIL 119/120 — I2's line-end clause | `b548c848448f722e276ccad7cabfa888ebbdefd94a8bb0b2ce7b76e2e56393c0` |
| `redfirst-both.txt` | the repaired `run_rehearsal_v2.py` against `7eddaba`'s `rehearse_decision_v2.py` and `rehearse_sequence.py`: exit 1 — the no-break-space and ideographic-space arms MISSED, and I3a and D5 disagree on the line-end probes (the inspector's finding) | `bf70f0ae45f793c6d882db6904515a242304b8bd6d85e62111fd82a25c671cbd` |

The repair: one function reads the bounds line — `rehearse_decision_v2.parse_bounds`, which I3a's check uses and `rehearse_sequence.py` imports for
D5 — so the two cannot disagree. Trailing ASCII spaces and tabs are not part of the line (as for the frozen-revision line); any other character,
other whitespace included, puts it outside I2. The text says the same in the order's I2, the playbook's I2 and the work order template.
Arms: four in `run_rehearsal_v2.py` (spaces and a tab accepted; a no-break space and an ideographic space refused) and an agreement check over 84
lines (seven value pairs × twelve line ends: none, spaces, a tab, a no-break space, an ideographic space, an em space, CR, VT, FF, a letter) that D5
reads a line I3a accepts as written and keeps the defaults for one I3a refuses; Z4 and Z5 in `rehearse_sequence.py`.

Command for the red-first run: a scratch folder with `7eddaba`'s `rehearse_decision_v2.py` and `rehearse_sequence.py`, the repaired
`run_rehearsal_v2.py` and `vp2-cp-results.xml.gz`, then `python -B run_rehearsal_v2.py <ViewPrism2> <out>`.
