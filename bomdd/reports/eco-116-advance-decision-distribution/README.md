# ECO-116 survey — where each product stands against ECO-115's advance decision (read-only)

Run 2026-10-26 from the BomDD root for the filing of [ECO-116](../../60-change-order-eco-116.md). Nothing in any product repository was written.
All files are LF; sha256 of the committed bytes.

| File | What | sha256 |
|---|---|---|
| `survey.py` | per product at its HEAD (`git show`): ECO-115's I3a structure and I2 checks on the M-BOM and Control Plan (`../eco-115-advance-decision/rehearse_decision_v2.py`, the rules as verified), counted by route; the work order's frozen-revision and bounds lines; the newest As-Built entry's decision fields; vendored method templates. Frozen at filing as V1's instrument; `--work-order <product>=<path>` reads the work order where the product ECO keeps it (converge round 1, L1R1-01), and a key that names no surveyed product exits with an error (round 3, L1R3-02) | `b3360642687a286c1a6bb8d1afdf9e4b9ee398736c858b8c1b9e45065fbd61af` |
| `survey.txt` | its output at filing: ViewPrism2 `504921a` 26 defects, ViewTube `a6314a87` 11, MoviePad-Remake `b2e19a0` 0 | `1112ea9ecb9f1d2719fe98672122bd3ac101555fb7f1022cb382597e4eab2986` |

Command: `python -B bomdd/reports/eco-116-advance-decision-distribution/survey.py . <output> ../ViewPrism2 ../ViewTube ../MoviePad-Remake`
(set `PYTHONIOENCODING=utf-8` on a Windows console). A defect of the script found before its output: it stopped on a unit without
`acceptance_refs` (ViewPrism2 has six), which is a defect to count, not a crash; it now reads the field as empty.
