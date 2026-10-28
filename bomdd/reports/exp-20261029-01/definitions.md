# EXP-20261029-01 — definitions (fixed before classifying)

Fixed 2026-10-29, before either classifier read an item for its class. A change after this point is a departure, recorded in
section 7 with both readings.

## 1. The question

An outside proposal (the user's paste, 2026-10-29) asks to move parts of design synthesis from generative AI to deterministic
generators and to grow that part over time. Before building any generator: **of the decisions the orchestrating AI wrote in a
derived layer (M-BOM, Control Plan, Routing), how many could a program reproduce from the ruled layer — today, with one more
rule, or only with one more field in the input — and where did the recorded defects fall?**

This is a measurement. It changes no method text, template, tool or product.

## 2. Sample and items

- Product: MoviePad-Remake at `d3683d6` (ECO-005 applied). Its derived layer was derived forward from a ruled layer before any
  code existed (EXP-20261024-01), and its M-BOM states its manufacturing decisions item by item.
- Items: `items.py` lists one item per decision written in `bomdd/32-mbom.yaml`, `33-control-plan.yaml` and `34-routing.yaml`
  at that commit — 120 items in 13 kinds. Item = the value as a whole (for example a unit's `depends_on` with its `requires`, a
  Control Plan row's method fields together); a value is not split further.
- Ruled input (what a program may read): `10-requirements.yaml`, `20-spec.md`, `30-ebom.yaml`, `31-kbom.yaml`,
  `bomdd/reports/adr/`, at the same commit. Written rules (what a program may apply): the BomDD playbook and templates as
  distributed to the product (MoviePad-Remake `bomdd-kit/`, at the same commit), and rules written in the product's ruled layer or its process files
  (`process-profile.yaml`, `bomdd/reports/exp-20261024-01/test-plan/test-plan.md`).
- Derived-layer text that the item itself cites (another M-BOM unit, another Control Plan row) is input only when it is itself
  an item classified R or C (a chain of mechanical steps stays mechanical).

## 3. Class of an item (one per item)

Apply in order; the first that holds is the class.

| Class | Holds when |
|---|---|
| **R** — rule today | A written rule (section 2), applied to the ruled input as it stands, gives this value (or a value equal up to order and wording that carries no decision). A program could be written today. |
| **C** — one more rule | No written rule gives it, but it follows from the ruled input by a pattern that could be stated as a rule whose conditions the ruled input already carries, and stating it decides no new design question (it records a practice the layer already follows consistently — for example a copy, a union, the same value in every row of a kind). |
| **C+** — one more field | It would follow by a rule as in C only if the ruled input carried a field it does not carry now. Name the field (for example "a typed signature for IF-…", "a test event per requirement"). |
| **J** — judgment | More than one reasonable value exists on the ruled input, and choosing among them rests on a trade-off, on knowledge outside the ruled input, or on taste; a rule that fixed it would decide a design question for future cases. |
| **U** — cannot tell | The record does not let the classifier decide between the classes above. Say what is missing. |

Mixed values: an item whose value has a mechanical part and a judged part takes the class of its judged part (the least
mechanical class in the order R < C < C+ < J), and the note names the mechanical part.

## 4. Second axis — is it checked

For each item, independent of its class: is there a written rule that **checks** the value (not produces it)?
`machine` (a tool in the product or the method runs it), `prose` (written, applied by reading — for example playbook §4.6's
A1 structure resolution and §4.5's C1, which no tool implements), or `none`.

## 5. Defects

After both classifications are fixed: findings recorded in MoviePad-Remake's change orders, reviews and delivery records that
name a derived-layer item (a unit, a provides item, a decision, a Control Plan row or a routing step) and led to a change of
it. Each finding is mapped to the item(s) it changed and their class. Found by searching those records for the item ids and the
three file names; a finding that names no item is counted separately as unmapped.

## 6. Classifiers and reading

- Classifier 1: the designer (this session). Classifier 2: a fresh-context agent given this file, `items.md` and the product
  repository only, not classifier 1's classes. Both write a class, the check axis and a one-line reason per item.
- Agreement is reported per kind and overall (exact class match). The table of results gives both classifiers' counts; no
  adjudicated "true" class is claimed. Disagreements are listed.
- Reading fixed now:
  1. The **island candidate** under current inputs is R + C; C+ items list the fields the input would need (the proposal's
     intermediate model, as fields of the existing ruled layer).
  2. A kind is a **generator candidate** only when most of its items are R or C for both classifiers **and** recorded
     defects fell on that kind. If defects fall mainly on J items, or on R/C items that a written check already covers, the
     result supports checking before generating and no generator ECO is proposed from it.
  3. A kind where the classifiers disagree on more than a third of its items gives no claim for that kind.
  4. One product, one designer, one forward run: no rate is claimed beyond this product.

## 7. Departures

- D1 (before counting): the DECIDE of 2026-10-29 named ViewTube ECO-VT-269/270, ViewPrism2 ECO-148 and MoviePad-Remake
  ECO-004/005 as the sample. On reading, the ViewTube and ViewPrism2 ECOs install the method kit (the advance decision) and do
  not derive a product's M-BOM or Control Plan, and those products' M-BOMs were derived in reverse from existing code with no
  `manufacturing_decisions` field (ViewTube 0, ViewPrism2 1 unit). The sample is therefore MoviePad-Remake's whole derived
  layer, which ECO-004 and ECO-005 last changed.
