# EXP-20261030-01 — definitions (fixed before classifying)

Fixed 2026-10-30, before either classifier read an item. A change after this point is a departure, recorded in section 8 with
both readings.

## 1. The question

An outside proposal (the user's paste, 2026-10-30) asks to verify the upstream layer — use cases, specification, domain model —
by robustness analysis (ICONIX): an AI maps each use-case step to Boundary / Control / Entity objects, and a deterministic checker
tests the connection rules, step coverage, screen consistency and the source of every element. Before building anything (the
user's "A"): **of the upstream defects already recorded in three products, how many would such a check have named before
manufacture, and by which kind of check?**

This is a measurement. It changes no method text, template, tool or product.

## 2. Sample

Mechanical selection by `items.py` at pinned commits (in `items.json`); 123 candidates. Screening (section 3) is the
classifiers'.

1. **ViewTube** (`bomdd/process/change-register.yaml`): every entry with `diagnosis_layer` `ui_cad` or
   `requirements_bom_control` and status `applied` or `implemented` — 42. The layer field says where the change was diagnosed,
   not that the old text was defective; feature extensions are expected among them and are screened out.
2. **ViewPrism2** (`bomdd/60-change-register.yaml`, no layer field): every entry whose free-text `type` matches the upstream words
   in `items.py` (`VP2_UPSTREAM`) and does not begin with a feature, process or equipment word (`VP2_EXCLUDE`) — 56.
3. **MoviePad-Remake**: its six change register entries, and the 19 topics of its G2 audit (`20-spec.md` at `22e2213`, Gate
   record, rounds 1-3). The audit's finding texts are not kept in the repository, and the spec's first commit (`bb79898`) already
   carries every round's fix, so the text before a fix is not kept either: a topic is a heading only, and the classifier judges
   the gap from the topic and the clause that now covers it. MoviePad-Remake is a
   computation-heavy product and not representative of a general application (ViewPrism2 and ViewTube are); it is reported
   separately and does not enter the reading of section 6.

## 3. Screening (per item, first)

**IN** when the item's records say that a statement of the **ruled layer** — requirements (10), specification (20), E-BOM (30),
K-BOM (31), the UI-CAD or mock, an ADR — was **missing, wrong, ambiguous, or contradicted another ruled statement**, and the
change corrected or ruled it. For a G2 topic: the audit found the spec text missing, wrong or ambiguous on that topic.

**OUT** (name which) when it is:
- `impl` — an implementation deviation with the ruled layer sound;
- `derived` — a defect of the M-BOM, Control Plan, routing, fixed oracle, inspection or process equipment only;
- `feature` — a new or changed requirement where the old text correctly stated what was then wanted;
- `process` — method, tooling or records only;
- `unclear` — the records do not let the classifier tell (say what is missing).

## 4. Catch classes (per IN item)

Suppose that **before manufacture** an AI built a robustness model from the ruled layer **as it stood before the fix** (the
mock or UI-CAD included where one existed), mapping each step or behaviour clause to Boundary, Control and Entity objects, with
every element citing its source (a step, clause, mock element or term), and that **every element it needed but could not source
was emitted as a question** (the best case for the proposal). The rules: an Actor talks only to a Boundary; a Boundary talks to
an Actor or a Control, never to an Entity; a Control talks to Boundaries, Entities and other Controls; Entities do not talk to
each other.

Count a class only when the violation, difference or question it produces **names this defect** — not when it is merely near it.
Write every class that holds (a set), or N, or U.

| Class | Holds when |
|---|---|
| **K1** — connection rule | A faithful model of the defective text would be forced into a connection-rule violation, and the violation points at the defect. |
| **K2** — source / coverage | Modelling the text would need an element, a step's handler, an alternative flow or its destination that the text does not state or states two ways, so a question would be raised, and the question names the defect. |
| **K3** — mock difference | The mock or UI-CAD's set of operations or displayed elements differs from the model's boundary operations, and the difference is the defect. (Needs a mock; this check also exists without a robustness model, as UI-IR.) |
| **N** — none | None of the above would name it — for example a value, rule, order, tolerance, rounding or computation; visual layout or wording; a requirement that no text implies. |
| **U** — cannot tell | The records do not let the classifier decide. Say what is missing. |

Per IN item also write the **defect kind**: `missing`, `wrong`, `ambiguous` or `contradictory`.

## 5. Classifiers

- Two classifiers, blind to each other and to the designer's expectation: **C-A**, a fresh-context Claude agent; **C-B**, Codex (a
  different model — the independence of equipment as well as of context, kit R8). Each runs as three instances, one per product,
  with the same brief, to bound what one context must hold. Each gets this file, `items.md` and read access to the three product
  repositories at the pinned commits — not BomDD's `method/improvements.md` or the other classifier's files — and writes
  `classifier-<a|b>-<product>.json`: per item `screen`, `out_reason`, `classes`, `kind`, a one-line `reason`, and `read` (the
  file and section read).
- The designer (this session, which proposed the reading and so holds an expectation) classifies nothing; `compare.py` counts.
- No adjudicated "true" class is claimed; both classifiers' counts are reported, with every disagreement listed.

## 6. Reading (fixed now)

Over items IN for both classifiers, per product; **structural** = K1 or K2.

1. **Structural share** S(both) = items structural for both / items IN for both; S(either) reported beside it.
2. If S(both) ≥ 25 % in ViewTube or ViewPrism2 → a robustness extraction for G2 earns a **prospective trial** (seeded defects in a
   use case, a control arm of today's G2/G3 only, detection per class). If S(either) ≤ 10 % in both → **not useful for these
   products**: the lever is the comparison with an independent input (K3, the mock; examples a human writes) and checks of meaning;
   no trial is proposed. Otherwise → **no claim**; counts reported by class. (The thresholds are chosen now, not derived.)
3. K1 is reported on its own: if K1 is 0 or 1 for both classifiers across the two products, **the connection rules do not pay
   here**, whatever K2 shows.
4. A product where the classifiers disagree on structural / not structural for more than a third of the items IN for both gives
   **no claim** for that product.
5. Screening agreement is reported (IN/OUT per item); it bounds how far the counts can be read.

## 7. Limits (stated before counting)

- Only defects that were found and recorded are in the denominator; a class that every gate missed and nobody recorded is
  absent.
- "Would have named it" is a counterfactual judged by AI readers from records.
- The supposition in section 4 is the best case (no fabricated element, every gap raised as a question); the counts are an
  **upper bound** on what the proposal would catch. A low upper bound reads strongly; a high one only earns a trial.
- MoviePad-Remake's G2 items are headings, not findings.
- One snapshot per product; no rate is claimed outside these three products.

## 8. Departures

- D1 (before any classifier wrote an item, 2026-10-30): C-B's first runs failed at the first turn — Codex's configured default
  model `gpt-6.1-sol` is refused for this account (`model_not_found`). C-B runs with `--model gpt-5.6-sol`, the model the earlier
  BomDD Codex runs used; the Codex configuration is unchanged. Section 5 is otherwise as fixed.
