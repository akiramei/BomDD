# EXP-20261030-01 — results

Counted by `compare.py` (exit 0) from the six classifier files; numbers below are copied from `summary.json`, which is the
record. Definitions: `definitions.md` (fixed at `16cbeda`; departure D1, the Codex model, before any item was written).

## 1. Counts

| | ViewTube | ViewPrism2 | MoviePad-Remake |
|---|---|---|---|
| candidates | 42 | 56 | 25 |
| screening agreement | 37/42 | 48/56 | 25/25 |
| IN for C-A / C-B | 22 / 21 | 27 / 21 | 20 / 20 |
| IN for both | 19 | 20 | 20 |
| structural (K1 or K2) for both | 7 (36.8 %) | 3 (15.0 %) | 1 (5.0 %) |
| structural for either | 11 (57.9 %) | 12 (60.0 %) | 4 (20.0 %) |
| structural split (one yes, one no) | 4 | 9 (> 1/3 of 20) | 3 |
| K1 for both | 0 | 0 | 0 |

Per classifier, over its own IN items: K1 0 everywhere (both classifiers, all three products). OUT reasons are mostly
`feature` (ViewTube 16 / 18, ViewPrism2 11 / 16) and, in ViewPrism2, `impl` (17 / 17). 33 items differ between the classifiers
(screen or classes); all are listed in `summary.json` → `disagreements`. Every one of the 246 entries carries a non-empty
`reason` and `read` (counted after `compare.py`, which checks the vocabulary only).

## 2. Reading (section 6, as fixed)

1. **Rule 2: trial.** ViewTube's S(both) is 36.8 % ≥ 25 % and its split (4 of 19) is within a third, so a robustness extraction
   for G2 earns a prospective trial (seeded defects in a use case, a G2/G3-only control arm, detection per class).
2. **Rule 3: the connection rules do not pay here.** K1 is 0 for both classifiers in all three products — no recorded upstream
   defect would have surfaced as a Boundary / Control / Entity connection violation.
3. **Rule 4: ViewPrism2 gives no claim** (structural split 9 of 20); its 15.0 % is not read.
4. MoviePad-Remake (reported separately, not representative): 1 of 20 structural for both; its G2 topics are values, orders,
   tolerances, formats (N).
5. Upper bound (section 7): every count assumes the best case — no invented element, every gap raised as a question.

## 3. What the structural items are (descriptive — not part of the reading)

ViewTube's seven structural-for-both items: VT-002, VT-003, VT-012, VT-015, VT-017, VT-024, VT-025.
- Three (VT-002, VT-003, VT-024) are also K3 for both: a mock / UI-CAD comparison (which exists without a robustness model, as
  UI-IR) names them too.
- Four are K2 without K3 for both: VT-012 (a destination stated two ways across requirements, spec and CAD), VT-015 and VT-017
  (what an open view on another tab does after an action on this one — saving HOME, selecting another View), VT-025 (an import
  destination written only in the M-BOM). Two of the four are **effects across surfaces** that no single screen's mock shows.

ViewPrism2's three structural-for-both items (VP-024, VP-043, VP-055) are all K3 for both.

So of everything both classifiers called structural in the two general products (10 items), 6 are also named by a mock
difference for both, and 4 (all ViewTube) are named only by the source / alternative-flow rule. Whether that residue is worth a
model is what the trial would measure; this section is not a reading.

## 4. Where the classifiers part

C-B (Codex) calls K2 more often on display omissions and missing operations (ViewPrism2 VP-001 to VP-004, VP-030, VP-039); C-A
(Claude) calls those N ("no ruled text implies it" / "a state rule"). The split is about how far "the model would have to ask"
reaches — the definition's "names this defect" did not fix it for ViewPrism2. A trial needs that line drawn by the seeded defect
itself (known in advance), not by a reader's judgement.

## 5. Limits

As `definitions.md` §7: found defects only; counterfactual judged by AI readers; best case; one snapshot. In addition: the
ViewTube reading rests on 7 items, and on one of the two general products only.
