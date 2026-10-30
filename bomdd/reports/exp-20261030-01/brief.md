# EXP-20261030-01 — classifier brief (the same text for every instance; `{PRODUCT}`, `{PREFIX}` and `{LETTER}` filled per run)

You are one classifier in a measurement. Work alone. Read only what is named here.

**Read first, in full**: `C:/Users/akira/source/repos/BomDD/bomdd/reports/exp-20261030-01/definitions.md` (the rules you apply)
and the rows of `items.md` in the same folder whose id begins with `{PREFIX}-` (your items, product `{PRODUCT}`).

**Do not read**: `C:/Users/akira/source/repos/BomDD/method/improvements.md`, any `classifier-*.json` in that folder, or any file
in that folder other than `definitions.md` and `items.md`.

**For each of your items**: open its `order` (relative to `C:/Users/akira/source/repos/`) and, where needed, the ruled-layer files
it names in the same product repository (`bomdd/10-requirements.yaml`, `20-spec.md`, `30-ebom.yaml`, `31-kbom.yaml`, the UI-CAD /
mock, ADRs). The repositories' working trees equal the pinned commits in `items.md` for every file you need; do not modify any
repository. Apply section 3 (screen) and, if IN, section 4 (classes and kind). Judge the ruled layer **as it stood before the
fix** — the order usually says what was missing or wrong. Count a class only when it would **name this defect**.

**Write** `C:/Users/akira/source/repos/BomDD/bomdd/reports/exp-20261030-01/classifier-{LETTER}-{PRODUCT}.json` (UTF-8), exactly:

```json
{"classifier": "{LETTER}", "product": "{PRODUCT}", "items": [
  {"id": "{PREFIX}-001", "screen": "IN", "out_reason": null, "classes": ["K2"], "kind": "missing",
   "reason": "one line: what the defect was and why this class names it (or why none does)",
   "read": "file and section read"}
]}
```

- `screen`: `IN` or `OUT`. `out_reason`: null when IN; else one of `impl`, `derived`, `feature`, `process`, `unclear`.
- `classes` when IN: any of `K1`, `K2`, `K3` (a set, in that order), or `["N"]`, or `["U"]`; `[]` when OUT.
- `kind` when IN: `missing`, `wrong`, `ambiguous` or `contradictory`; null when OUT.
- One entry per item, every item of your prefix, in id order. No other file.

When done, reply with only: the path written, the number of items, and counts of IN / OUT and of K1, K2, K3, N, U.
