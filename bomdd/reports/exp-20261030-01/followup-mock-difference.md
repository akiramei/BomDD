# EXP-20261030-01 — follow-up: can the mock difference be a deterministic stop? (the user's "C", 2026-10-30)

The user's "C" asked to make the comparison of the ruled text with the mock a stop in G2 first. Before designing it, the six items
that both classifiers counted as named by a mock difference (K3) were read for what the stop would have to compare. Read-only; no
product changed. Investigation by a fresh-context agent (its report is model output); the facts marked ✓ were re-measured by the
designer (`spot.py` here, run from `C:/Users/akira/source/repos` on 2026-10-30 at the pins of `items.json`; the ViewPrismUI count
by `find`/`grep` over its HTML files).

## 1. The six, by what a check would have to compare

| item | defect (the order) | direction | granularity | an id-existence + "every surface REQ cites ≥ 1 id" check |
|---|---|---|---|---|
| VT-002 ECO-VT-035 | REQ-024/025 require assign and unassign; the mock had only `action.selection.tag`, no assignment surface, no unassign, no mixed state | text → mock | operation present, its result surface and states missing | no (the id exists) |
| VT-003 ECO-VT-040 | batch checkboxes in ordinary browsing, the assign action only in the hierarchy layout; the text silent on modes | inside the mock | present, missing in one mode | no (no mode × action set exists) |
| VT-024 ECO-VT-226 | REQ-010 presumes user-made manual collections; no create action among `action.collection.*` | text → mock | whole operation missing | no (REQ-010 is cited by 11 actions) |
| VP-024 ECO-052 | REQ-067 / G-9 require a pre-merge preview and a notice; the tray CAD and mock have neither | text → mock | display element missing | partly (only if each G-9 line must cite an element id) |
| VP-043 ECO-119 | CAD prose (image_tab.md:107) names a docked assign operation the mock lacks | CAD prose → mock | a region that does not exist | only if every operation the prose names must cite an id |
| VP-055 ECO-140 | prose hands relink to repair; the v2 mock relinks in the review screen | two statements | role / ownership | no |

So the deterministic form catches **0 of 6 fully and 2 partly**, and both partial catches need the text to cite element ids line by
line. The classifiers' K3 assumed a reader who sees that the text implies an operation, a state, a mode or an owner; no id set
carries those.

## 2. What the inputs are today

- Ruled text citing UI ids: ViewTube 10/20/30 = 0 / 3 / 0 ui ids; ViewPrism2 0 / 0 / 0 (it cites CAD by file and line, 42 / 11 / 21).
- ViewTube's mock → text link: `ui-ir.json` actions' `requirementRefs` — ✓ 130 actions cite 28 REQs (of 87); written by
  `bomdd/ui/build_ui_cad.py`, read by no validator.
- ViewTube's raw IR is stale: ✓ the mock carries 449 distinct `data-ui-id`, 232 of them absent from `ui-ir.raw.json`
  (`action.collection.create-manual` among them — the very fix of ECO-VT-226); ✓ raw IR last committed `fcd9ba08` 2026-08-04, the
  mock `416a97e4` 2026-10-11.
- ViewPrism2's mocks (in ViewPrismUI): ✓ 21 HTML files, 0 with `data-ui-id`; its `bomdd/ui/` frozen 2026-07-01 (its README).
- `method/tools/ui-cad-gate.py` (GU1-GU6, GU6 = id drift between mock and raw IR): ✓ referenced by neither product's `bomdd/`.

## 3. Reading (not fixed in advance — a design input, no claim)

- A deterministic stop on the text–mock comparison has no input to compare until the ruled text cites UI element ids at the
  granularity of the defects (operation, state, mode, owner) — which is a typed model of the UI written into the ruled layer, the
  thing the robustness proposal itself would add. The cheap form available today (ids exist, each surface REQ cites one) would not
  have stopped the six.
- What named them in the records was reading: a human golden, an R3 finding, a maintainer's comparison. The method already has a
  reader-based form for this — §17 mock acceptance inspection (internal contradictions, adjacent questions; measured once on
  MoviePad, 69 %, "unspecified contract" 5/6) — not applied in either product.
- Separately, the precondition every mock check needs — a raw IR that matches the mock — fails in ViewTube today, and the method's
  gate for it (GU6) runs in no product.
- EXP-20261030-01's descriptive line "6 of the 10 are also named by a mock difference (UI-IR exists without a robustness model)"
  is narrowed accordingly: named by a **reader** comparing text and mock; not by any check that exists or could run on today's inputs.
