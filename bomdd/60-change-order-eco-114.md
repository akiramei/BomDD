# Change Order — ECO-114 (the part standard: each unit's provides and requires in the BOM, external promises in the ruling layer, the Phase 3 order and owners, and assembly resolution)

> Ruling: user, 2026-10-24, "A" on filing and designing this change, after the evaluation of an external discussion (M-BOM / Control Plan,
> 部品契約, 自動車会社の E-BOM→M-BOM の役割). The user's statements this ECO answers (in substance):
> - A work instruction is issued from the M-BOM; the agent works and returns a completion report. **What counts as a pass needs a criterion.**
> - Without a part standard (interfaces and the like), **nothing guarantees the part can be used by the next process.**
> - Between E-BOM and M-BOM / Control Plan, someone does part and interface design and the check that the parts can be manufactured; **without the
>   parts and their assembly the Control Plan cannot be made.**
> - Condition of "A": the design must show that the result of a work instruction derived from the M-BOM **is judged against the M-BOM's criteria**, and
>   that **the Control Plan decides from that result, deterministically, whether the process may advance.**
>
> Split ruling: user, 2026-10-24, "A" after the first design loop ended unconverged at its limit (26→8→8; material 20→3→4). **This ECO keeps the part
> standard, the Phase 3 order and owners, and assembly (resolution and the list of rows that measure the units together). The advance decision moved to
> ECO-115 (designed separately; not filed with this ECO)**, which reads this ECO's `mbom.assembly`; manufacture goes 114 then 115. Both ECOs converge by the default rule,
> with rounds counted afresh because the scope changed (as in ECO-112/113).
>
> Extension ruling: user, 2026-10-24, "A" after loop 2 ended unconverged (18→12; material 7→3) with ECO-115's (26→10): extend both loops, with the
> common cause removed first — the rules are run as rehearsal scripts on the real ViewPrism2 and ViewTube data before the next round, so where they meet
> existing data shows up by execution, not one review round at a time (receipt, loop 3). Limit 3 rounds.
>
> Cut-off ruling: user, 2026-10-24, "1:A" after loop 3 ended unconverged (8→3; material 1→0): **adopt the design with round 2's three minor findings
> repaired, and file it.** The repairs were not reviewed by a further round; the verdict under the converge rule stays unconverged (receipt, loop 3).
>
> Premise the design uses (stated so the user can object): "the M-BOM's criteria" for a unit are its part standard (P1) and the Control Plan rows in its
> `acceptance_refs`. The M-BOM carries the standard; for a promise another design part or a user outside the product relies on, the canonical text stays in
> the ruling layer (E-BOM) and the M-BOM refers to it by ID (P2). This follows the user's standing ruling "E = the place of human rulings, M / CP = the
> place of the AI's judgement" (ECO-097) and playbook §4.5's rule that the derived layer does not hold ruling-layer content in its own words (ECO-098,
> ECO-100).
>
> Records are English-primary. Manufacture waits for the user after the design converges.

## Equipment

- Filing and design: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- producer: EQ-004
- inspector: EQ-002
- Converge round reviewer: a fresh context of the same model (context independence), read-only, resumed each round; loop 2 has a new context.
- Independent inspection: EQ-002 (Codex), because the change redefines what the method's BOM states and who derives it (precedent: ECO-098).

## 0. Basis (measured; `bomdd/reports/eco-114-part-standard/`)

`measure.py` writes `measurements.txt` and `shapes.py` writes `shapes.txt` (git `show`, read-only; ViewPrism2 at `504921a`, ViewTube's E-BOM and M-BOM at
`c214dec0` and its control plan at `fc35bf1d`, the templates from this repository); sha256 in that folder's `README.md`.

- **B1 — no step and no owner for part and interface design; the Control Plan is made before the M-BOM.** `method/prompts/phase3-design.md:6-20`:
  1 E-BOM, 2 FMEA, 3 K-BOM, **4 Control Plan**, **5 M-BOM**. The roles table gives Phase 0-3 to "設計者(ユーザー+設計AI)"
  (`method/bomdd-playbook-v1.md:832`); §4.5 gives M-BOM / Control Plan / Routing to the orchestrating AI (`:344-345`). No step names part or interface
  design. G3 asks a fresh AI whether it can start from the package (`phase3-design.md:22-26`); it does not ask whether a unit can be accepted alone or
  whether the parts connect.
- **B2 — the part standard has a slot but no standard.** `method/templates/32-mbom.yaml:28` `interface_contract: <key>: <value>` (free form, in the
  derived layer). `30-ebom.yaml` and `20-spec.md` contain none of provides / requires / signature (count 0).
  - ViewPrism2: 38 of 44 units have an interface_contract, with 147 distinct keys; 3 units have a `signature` key; no `provides`/`requires` key. Five E
    items have a key `interface_contracts` (count in `measurements.txt`); reading 30-ebom at `504921a`, they hold prose ownership notes.
  - ViewTube: 12 of 12 units have an interface_contract with 4 distinct keys — `errors`, `async`, `nullability` on all 12 (coding conventions) and
    `required_action_bindings` on 3; no signature, provides or requires.
  - ViewPrism2's spec states some boundaries itself (e.g. `OC-1`, `OC-4`, `OC-6` in `20-spec.md:712-717`, cited by the unit signatures).
- **B3 — no Control Plan row verifies a part standard.** The template has no field linking a row to an interface; "interface" occurs 0 times in either
  product's control plan at the revisions measured.
- **B4 — the BOM's structure is not 1:1** (`shapes.txt`):
  - units by `ebom_refs` count 0 / 1 / 2+: ViewPrism2 6 / 29 / 9 (the six with none are harness, oracle, infrastructure and one UI unit); ViewTube 0 / 6 / 6;
    the 32 template's own `M-ACCEPTANCE-HARNESS-001` has none.
  - E items by realizing-unit count 0 / 1 / 2+: ViewPrism2 1 / 36 / 7 (`E-WORKSPACE-042` realized by none; `E-DOMAIN-001` by `M-SLN-000` and
    `M-CORE-001`); ViewTube 10 / 22 / 0 (the ten `E-DESIGN-*` items).
  - E-item connections: ViewPrism2 101 `depends_on` edges and 31 `graph_edges` consumer edges (19 in both); ViewTube 20 and 47 (none in both). A
    `graph_edges` holder is the part its consumers use; its `owner` may be another item (ViewTube's ten `E-DESIGN-*` items hold `owner:
    E-DESIGN-SYSTEM-001`). M-BOM `depends_on`: ViewPrism2 0 units, ViewTube 2 (`M-VIEW-PACK-001` on 8 units, `M-DEMO-CURATOR-001` on 3).
  - units with empty `acceptance_refs`: ViewPrism2 6, ViewTube 0; Control Plan rows named by 0 / 1 / 2+ units: ViewPrism2 15 / 41 / 9, ViewTube 13 / 4 / 24.
  - neither M-BOM has a key besides `manufacturing_units`.
- **B5 — assembly inspection was deferred on measurement.** `method/gap-analysis-v1.md:47-51`: no "unit green, assembly diverges" defect was recorded in
  ViewPrism2's 34 ECOs (scale-01), and the end-to-end oracle and golden were not broken at that scale. That says nothing about a part being usable when it
  is accepted alone.
- **B6 — the method defines the unit as acceptable alone.** `method/bomdd-playbook-v1.md:116`: "独立に再製造・交換でき、単独で受入できる最小単位".
  Accepting a unit alone, and replacing it, needs a standard checked when the unit is accepted (B2, B3 show there is none).

## 1. Change request — the rule register

The IDs below are this order's record. The method text states each rule in the canonical place named by the map at the end of this section; the places
the map lists as copies repeat it for their reader and must match the canonical text (V1 checks the match).

### P — the part standard

- **P1 (shape).** A unit with a part standard has `part_standard` with two lists, `provides` and `requires`; for it, `part_standard` replaces
  `interface_contract` (which stays, unchanged, on units without a standard — M1).
  - Entry IDs are unique within the unit across both lists: `PS-<UNIT>-Pnn` for `provides`, `PS-<UNIT>-Rnn` for `requires` (checked with A1).
  - A `provides` entry has `id`, `kind` (`api` | `data` | `event` | `file` | `process`) and either `ruled_ref: IF-…` (P2) or `statement`: the boundary
    (symbol and signature, schema, event, file format, command line) and its results, errors and side effects there, by reference to spec §2 / §3 IDs
    where they exist. An entry with `ruled_ref` may add `form`: the concrete symbol, signature or schema that realizes the ruled promise, when the
    ruling states it abstractly (e.g. `OC-1`); `form` is a manufacturing decision (§4.5 ③), the promise stays the ruled text.
  - A `requires` entry has `id` and `target`: a `provides` entry ID of another unit (`PS-<UNIT>-Pnn`), an `IF-` ID, `procurement:<package>`, or
    `platform:<name>`.
  - A display ruled as a display contract stays in the unit's `display_contract.refs` (`32-mbom.yaml:30-34`) and is not repeated as an entry.
  - Coding conventions shared across units (error style, nullability, async) are not entries; they move to `manufacturing_decisions`, or to the K-BOM
    through the human (§4.5 ②). The errors a `provides` entry states are that boundary's own.
- **P2 (external promises in the ruling layer).** An **external promise** is a boundary of one E item that another E item, or a user outside the product,
  relies on. Its canonical text is an `IF-<ITEM>-NN` entry in the providing item's `interfaces.provides`, with two fields: `refs`, the spec §2 / §3 IDs
  that state the boundary or its behaviour (e.g. `OC-1`), and `boundary`, only for what those IDs do not state (e.g. the types a behaviour is stated
  over) — never restating what a referenced ID states.
  - The consuming item's `interfaces.requires` names the `IF-` ID, and the providing item is connected to it in the E-BOM: the consumer's `depends_on`
    names the provider, or the provider (the `graph_edges` holder) lists the consumer in `graph_edges.consumers`.
  - A display already ruled as a display contract is not repeated as an `IF-` entry. An E item that no unit realizes (B4: design-system parts, whose
    contracts are the Design System BOM (35) and the standard parts ledger, §4.7) carries no `IF-`.
  - Which boundaries are external is the human's ruling with the E-BOM release; the derived layer does not add, drop or reword an `IF-` (P3).
- **P3 (adding or changing a promise).** An external promise found to be needed or wrong after the E-BOM release (at M-BOM derivation, in manufacture,
  in acceptance) is §4.5's "new promise" and goes back to the human. A factory that cannot meet one reports a blocker (`40-work-order.md:63-64`); it does
  not change the promise.
- **P4 (what stays derived).** A boundary between units that is not an external promise is a manufacturing decision (§4.5 ③), stated in the M-BOM as a
  `provides` entry with `statement`. A unit with no `ebom_refs` (harness, oracle, infrastructure, one UI unit — B4) provides only such entries and
  realizes no `IF-`; it may require any entry (a harness uses the units it verifies), but once it requires an `IF-` or an E-item unit's `PS-` entry,
  directly or through other units with no `ebom_refs`, no E-item unit may require its `PS-` entries (it cannot relay a boundary between E items — A1 4).
  P4's extension: this extends §4.5's four classes to the part standard, and settles for new units the item §4.5 lists as unmeasured
  on interface contracts (`method/bomdd-playbook-v1.md:360-361`).

### O — Phase 3 order and owners

- **O1 (order and owners).** Phase 3 becomes:
  1. E-BOM, with the part split and the external promises (P2) — drafted by the design AI, ruled by the human with the E-BOM's release;
  2. FMEA and the silence sweep — as today; an FMEA row gains `ebom_ref` (the E item it is written against, `32-mbom.yaml:88-93`), and its `unit` and
     `targeted_by` are filled at steps 4 and 5;
  3. K-BOM — as today;
  4. M-BOM — units, their part standards (P1, P4) and `mbom.assembly` (A2) — by the orchestrating AI;
  5. Control Plan — by the orchestrating AI, completing each unit's `acceptance_refs` and `mbom.assembly.acceptance_refs`; the fixed oracle and the
     exploratory probes stay with the designer side as today (§4.4:138, `phase3-design.md:13`);
  6. Routing and work order — by the orchestrating AI;
  then G3. The Control Plan is still made before manufacture (oracle first, §4.4).
- **O2 (manufacturability).** At step 4 the orchestrating AI checks that each unit's entries are complete (P1) and that A1 holds; at step 5, that C1
  holds. Where either cannot hold without adding or changing an external promise, P3 applies; where a derived entry (P4) cannot be measured, the
  orchestrating AI revises that entry.
- **O3 (G3).** Before G3's dry run, the orchestrating AI re-checks A1 and C1; G3's question to the fresh AI gains: "Can each unit be accepted alone from
  its part standard and the Control Plan rows in its `acceptance_refs`?"
- **O4 (the roles table).** §9's designer row becomes "設計者(ユーザー+設計AI): Phase 0–2, Phase 3 steps 1–3 and the fixed oracle and probes, Phase 5
  裁定", and a row "統括 AI: derives the M-BOM, Control Plan and Routing whenever they are derived (Phase 3 steps 4–6, and re-derivation in an ECO)" is
  added with the same 見てよいもの / 見てはならないもの as the designer row (it is on the designer side).

### C — the Control Plan

- **C1 (rows verify the standard).** A row lists in `part_standard_refs` the `provides` entries it measures some part of; it lists none it does not
  measure. Every `provides` entry is listed by at least one row in the providing unit's `acceptance_refs`. What a listing row does not measure of an entry
  goes to that row's `known_limits`, naming the entry's ID (§4.5 ④). An entry no row can measure is, for an `IF-`, a P3 return, and for a derived entry,
  O2's revision. Every ID in a `part_standard_refs` names an existing `provides` entry (checked with A1).

### A — assembly

- **A1 (structural resolution).** Read from the E-BOM, the M-BOM and the Control Plan only, by the orchestrating AI (O2, O3); a failure means the BOM is
  incomplete and G3 does not pass. Clauses 1, 3, 4 and 6 apply to units that have a `part_standard`; clause 2 to every `IF-`; clauses 5 and 7 to every
  E-BOM `interfaces.requires` (5 only where some unit realizing the consumer has a `part_standard`). A unit without a standard and an item without
  `interfaces` give no failure (the lazy rule).
  1. every `requires` target resolves: a `PS-…-Pnn` to that entry; an `IF-` to the one unit realizing it (clause 2), and only for a unit with no
     `ebom_refs` or one of whose E items provides or requires that `IF-`; `procurement:<package>` to a top-level `procurement` entry of the M-BOM;
     `platform:<name>` is accepted as written; any other target fails;
  2. every `IF-` is realized by exactly one unit — a unit whose `ebom_refs` include the providing item and which carries a `provides` entry with that
     `ruled_ref`;
  3. every `ruled_ref` names an `IF-` of one of its unit's E items;
  4. a `PS-` target is allowed only when the two units share an E item, or the provider has no `ebom_refs`; an E-item unit may not take a `PS-`
     target of a unit with no `ebom_refs` that requires an `IF-` or an E-item unit's `PS-` entry, directly or through other units with no `ebom_refs`
     (P4: no relay);
  5. some unit realizing the consuming item has a `requires` with that `IF-` as target, unless one unit realizes both items;
  6. a unit's `depends_on`, when the list is non-empty, equals the set of units its `requires` resolve to;
  7. the `IF-` exists, and its provider is connected to the consumer as P2 states.
  A `requires` naming a unit that has no `part_standard` yet: the same change gives that unit the `provides` entries it is required for (the lazy rule
  does not cover a consumed entry — M1).
- **A2 (rows that measure the units together).** `mbom.assembly.acceptance_refs` lists the Control Plan rows that measure several units together —
  end-to-end harness rows and golden rows (depth G) whose subject is the units' behaviour together — chosen by the orchestrating AI at Phase 3 step 5
  (a derived-layer choice, recorded in the list). A row may also stay in units' `acceptance_refs`; it is one row wherever it is named (ECO-115 D2). An
  empty list needs `assembly_reason`.
  The automated parts are run by the receiving side (the orchestrating AI at receipt of a delivery, ECO-115 D0); the human parts stay Phase 5's. The fixed
  oracle (41) is not a Control Plan row and stays Phase 5's, with the designer side. A1 does not replace any of them.

### M — manufacture

- **M1 (scope).** Text and templates only: `method/bomdd-playbook-v1.md` (§4.1, §4.5 including `:342`'s field list, §4.6, §9's roles table),
  `method/templates/30-ebom.yaml` (`interfaces`), `32-mbom.yaml` (`part_standard`, `mbom.assembly`, the FMEA `ebom_ref` field and comment, the
  four-class comment `:37-40`),
  `33-control-plan.yaml` (`part_standard_refs`), `method/prompts/phase3-design.md`, `method/improvements.md`. No tool under `method/tools/`. Distribution to
  the products is a separate ECO. Existing BOMs are not migrated here: a unit gets its standard with the next change that touches it (§4.5's lazy rule),
  except a unit whose entries that change consumes (A1). The rehearsal script of V2 is evidence under `bomdd/reports/eco-114-*/`, like `measure.py`; the
  method does not ship it.

### Where each rule is stated (the map V1 checks)

| Rules | Canonical place | Copies (must match) | Fields that refer to it |
|---|---|---|---|
| P1, P3, P4, C1, A2 | playbook §4.5, new item "部品規格" | `32-mbom.yaml:37-40` comment (P4's extension sentence only) | `32-mbom.yaml` `part_standard`, `mbom.assembly`; `33-control-plan.yaml` `part_standard_refs` (comments naming §4.5) |
| P2 | playbook §4.1, new item "外向きの約束" | — | `30-ebom.yaml` `interfaces` (comment naming §4.1) |
| O1, O2, O4 | playbook §4.6, new item "Phase 3 の順序と担当" | `phase3-design.md` steps; §9's roles table | `32-mbom.yaml` FMEA comment (O1 step 2) |
| O3, A1 | playbook §4.6, G3 | `phase3-design.md` G3 | — |

### Declared limits

- **L1 (A1, A2).** A resolved `requires` says the entry exists, not that the two sides behave together; integration stays with the assembly rows and Phase
  5 (B5).
- **L2 (C1).** C1 says each `provides` entry is listed by a row that measures some part of it; it does not say the row tests the entry's whole meaning (as
  §4.4:175's mapping limit). Whether a row measures an entry is a judgement of meaning, made by the orchestrating AI at step 5 and checked by the
  independent inspection's reading; the BOM files show mechanically only that listed IDs exist and that each entry is listed by a row of its unit (user
  ruling "2:A" on inspection r1's IA-04, 2026-10-24).
- **L3 (P2, A1).** Reliance is read from the BOM (`interfaces`, `depends_on`, `graph_edges.consumers`, `requires`); a consumer the BOM does not name (code
  that calls a unit without a `requires`) is not seen, and an E-BOM connection with no `IF-` is not flagged. A1 4's grain is the E item: two units
  sharing one item may use each other's derived entries even when a provider's entry belongs to its other item (ViewPrism2: 7 items are realized by
  two or more units).
- **L4 (scale).** Designed from two products' BOMs; rehearsed on four ViewPrism2 units (V2); the cost of writing standards for every unit is not measured,
  and units without a standard stay as they are until touched (M1).
- **L6 (V1).** The English rule register and the Japanese method text cannot be compared mechanically; V1's checker watches a named list of clauses
  (each with a removal that fails its rule), and the completeness of the text against §1 beyond that list is the independent inspection's reading
  (user ruling "C" on inspection r2's IA-05, 2026-10-24).
- **L5 (copies outside M1).** `interface_contract` is also named in `method/contracts/plm-ready-contract.md:76`, `method/product-schema-candidates.md:70`,
  `method/schemas/draft/id-grammar.draft.yaml:33` and `method/gap-analysis-v1.md:49`; they are not changed here and describe units without a standard.

### Not changed

- The ruling-layer / derived-layer split and its return paths (§4.5), the fixed oracle and its owner and freeze, the factory's self-acceptance,
  independent inspection, the advance decision (ECO-115), and every tool.

## 2. No-impact prediction (before manufacture; frozen at filing)

Changed: the files in M1, this order, the register and `bomdd/reports/eco-114-*/`. Untouched: `method/tools/`, `method/schemas/`, `method/contracts/`,
`method/templates/product-profile/`, `method/templates/process-core/`, `.claude/skills/`, hooks, `.github/`, `40-work-order.md`, `50-as-built.yaml`, the
other templates and prompts, and both product repositories.

## 3. Acceptance (conditions; frozen at filing)

required_gates: [V1, V2, inspection]

**Gated:** V1, V2, and V3 as the gate `inspection`. **Checked at closure:** V4 (self-conformance and CI).

- **V1 — the text.** For each row of §1's map: the rule appears once in its canonical place; each copy says the same; each listed field carries a comment
  naming the canonical place. The templates carry P1's fields (`part_standard`, `provides` with `form`, `requires` with `target`), `interfaces` with
  `IF-` IDs and their `refs` and `boundary`, `mbom.assembly` with `assembly_reason`, the FMEA row's `ebom_ref`, and `part_standard_refs`; the prompt carries O1's order and owners and O3; §9's table carries O4.
  "Says the same" is checked clause by clause: each rule's clauses (§1) are present in the canonical text, and each copy holds its canonical text's
  clauses; removing one clause from the canonical text or from a copy fails V1 for that rule (r1's IA-03). The clause list is named evidence, not a
  derivation of §1: whether the method text says everything §1 says beyond the list is the independent inspection's reading (user ruling "C" on r2's
  IA-05; L6).
- **V2 — the standard and its checks on real units (rehearsal; evidence only, read-only on ViewPrism2).** Copies of ViewPrism2's E-BOM and M-BOM entries for
  `E-DOMAIN-001`, `E-EVAL-002` and `E-GRAPH-003` and the units `M-SLN-000`, `M-CORE-001`, `M-EVAL-002` and `M-GRAPH-003`, with their Control Plan rows,
  get part standards, `interfaces` and an `mbom.assembly` written to the new templates under the report folder (the domain types as an `IF-` of
  `E-DOMAIN-001` realized by `M-CORE-001`; `M-EVAL-002`'s evaluation as an `IF-` of `E-EVAL-002` required by `E-GRAPH-003`, with its signature as
  `form`). A script there applies A1 and C1's reference part (each `provides` entry listed by a row in its unit's `acceptance_refs`; every listed ID an
  existing entry — whether the row measures the entry is not checked by the script, L2; amended by the user's ruling "2:A" on r1's IA-04) and prints,
  for each failure, the clause and the entry. The design evidence of loop 3
  (`rehearse_part.py`, `rehearsal-bom.yaml`, `run_rehearsal.py`, `rehearsal.txt`) is this rehearsal's first run; V2 re-runs it on the manufactured
  templates' field names.
  - Both products' real BOMs as they are (no unit has a standard): no failure (A1's scope; the lazy rule).
  - The unchanged rehearsal BOM: no failure; run twice, identical output.
  - Allowed changes, each giving no failure: a harness unit with no `ebom_refs` requiring an E-item unit's `PS-` entry; a provider connected only
    through `graph_edges.consumers`; one unit realizing both the providing and the consuming item (A1 5's exemption); a `procurement:` target with its
    entry.
  - Known-bad inputs, each changing one thing, each with its own clause among the failures reported (other clauses that follow from the change may also
    be reported, and are listed): a `provides` entry listed by no row (C1); listed only by a row outside the unit's `acceptance_refs` (C1); a
    `part_standard_refs` naming no entry (C1); two entries of one unit with one ID (P1); a `requires` target naming no entry, and one naming a `requires`
    entry (A1 1); a `procurement:` target with no entry (A1 1); an `IF-` required by a unit none of whose E items provides or requires it (A1 1); an `IF-`
    that nothing requires, realized by no unit, and by two units (A1 2); a `ruled_ref` naming no `IF-`, and one carried by a unit with no `ebom_refs`
    (A1 3); `M-GRAPH-003` requiring a `PS-` entry of `M-EVAL-002` (A1 4); an E-item unit requiring a `PS-` entry of a harness that takes an E-item unit's
    `PS-`, of one that takes an `IF-`, and of one that takes them through a second such unit (A1 4, relay); `E-GRAPH-003`'s `interfaces.requires` with no unit `requires` (A1 5); `M-GRAPH-003`'s `depends_on`
    naming a unit it does not require (A1 6); an `interfaces.requires` whose provider is not connected (A1 7).
- **V3 — independent inspection** (EQ-002): the text against §1, and V2's evidence.
- **V4 — self-conformance exit 0 before each commit; CI success on each pushed tip.**

## 4. Manufacture (2026-10-24, user "1:A": manufacture now)

**Inputs fixed** (sha256 prefixes of the files at the filing commit `25bea38`, `git show 25bea38:<path>`): `method/bomdd-playbook-v1.md` `eb52d1200143`,
`method/templates/30-ebom.yaml` `b203de2c40f2`, `32-mbom.yaml` `9d5a58b4466f`, `33-control-plan.yaml` `838ee238911e`, `method/prompts/phase3-design.md`
`efbfbb76e75f`; the design: this order at `25bea38`. ECO-115's held draft (committed as a record in `afabdb1`) is not mixed in: no rule of it is in this diff.

**What changed, by rule:**
- playbook §4.1 — new item "外向きの約束" (P2); §4.5 — the M-BOM line names `part_standard`, `:361`'s unmeasured item points at the new item, and the new
  item "部品規格" (P1, P3, P4 with its extension, C1, A2, their limits); §4.6 — new item "Phase 3 の順序と担当" (O1, O2) before G3, and G3's question and
  "A1 構造の解決" (O3, A1's seven clauses and scope); §9's roles table (O4).
- `30-ebom.yaml` — `interfaces` (`provides` with `IF-`, `refs`, `boundary`; `requires`) and a checklist line; `32-mbom.yaml` — `part_standard` (provides
  with `ruled_ref`/`statement` and `form`; requires with `target`) in place of `interface_contract` for a unit that has it, `mbom.assembly`
  (`acceptance_refs`, `assembly_reason`), the FMEA row's `ebom_ref`, the `depends_on` comment, and the copy of P4's extension in the four-class comment;
  `33-control-plan.yaml` — `part_standard_refs`.
- `method/prompts/phase3-design.md` — the six steps in O1's order with owners (a copy of §4.6, pointing at it), and G3 running A1 and C1 first with the
  unit-alone question.
- `method/improvements.md` — the 2026-10-24 section with EXP-20261024-01 (the MoviePad re-manufacture trial) and OBS-20261024-01 (ViewTube's Control
  Plan unparsable since `cfd00433`).

**Acceptance measured before the manufacture commit** (evidence: `bomdd/reports/eco-114-part-standard/manufacture/`):
- **V1 — PASS.** `check_v1_v2.py`: each canonical place once (4 headings), §4.5's five rule labels, A1's seven clauses, G3's question, §9's split, the
  prompt's step order equal to §4.6's, its owners and G3, 32's copy of P4's extension, and every listed template field with its place comment. Positive
  control: the same script on the filing tree `25bea38` gives V1 FAIL (27 of 29 checks fail).
- **V2 — PASS (re-run on the manufactured field names).** The templates parse and carry every path the rehearsal reads (V2-fields PASS; FAIL on the
  control tree); `run_rehearsal.py` re-run gives output byte-identical to the filing's `rehearsal.txt`: both real BOMs no failure, 4 allowed changes no
  failure, 19 known-bad changes each reporting its own clause.
- **Instrument defects found and corrected before the outputs above** (`check_v1_v2.py`): the step-order check matched a "3. K-BOM" elsewhere in the
  playbook; on the control tree it stopped with a traceback instead of reporting FAIL. Attribution: this ECO's own instrument.
- **V3 (inspection) and V4 (CI on this commit)** follow.

## 5. Independent inspection r1 (2026-10-24, EQ-002, range 境界探索) — REJECT IA-01, IA-02, IA-03, IA-04

- **Launched through the operator entry** on `286d02c` (CI 40042223303 success; witness tree `9f383581e1fd`, gate self-conformance):
  `bomdd-run.py ECO-114 --cell "codex exec -s workspace-write -m gpt-5.6-sol -C … -o …/inspection-r1.md - < %BOMDD_BRIEF%" --brief <brief outside the
  worktree> --executor EQ-002 --report bomdd/reports/eco-114-part-standard/inspection-r1.md --range 境界探索`. Brief `c615d8bda30b…` (stored; committed copy
  `bomdd/reports/eco-114-part-standard/inspection-brief-r1.md`, same sha256); report `inspection-r1.md` (`b49d9b942f26…`); the ledger's cell record binds
  it (`REJECT`, `journal_end: committed`, run `20261023T235859.690037Z`).
- **Items:** scope FAIL, each rule against the text FAIL, the rules against the rest of the method **PASS** (no contradiction with §4.4-§4.7, the package
  and the oracle's owner, the existing template fields, or the measured BOM shapes), acceptance evidence FAIL, records FAIL. The rehearsal reproduced
  byte-identically; all 12 README sha256 values match the committed bytes; the basis figures sampled match.
- **IA-01 — blocking — the audited window holds another change.** `git diff 25bea38..286d02c` includes the 12 files of ECO-115's record commit `afabdb1`
  (between the filing and the manufacture), outside ECO-114's `allowed_paths`; §4's "not mixed in" is true of the manufacture commit, not of the window
  the brief named. Reproduced by the producer (`git diff --name-only 25bea38..286d02c`: 12 paths under `bomdd/reports/eco-115-advance-decision/`). This
  is OBS-20261018-02's class (a third case after ECO-112 and ECO-113, each settled by the user's exception ruling for that ECO).
- **IA-02 — blocking — O4 is not in its canonical place.** The map names §4.6 "Phase 3 の順序と担当" as O4's canonical place with §9 as a copy, but §4.6
  only points at the roles table; the split by layer and the same may-see / must-not-see live only in §9.
- **IA-03 — blocking — V1's checker does not compare rule substance.** `check_v1_v2.py` checks headings, labels, selected substrings, step numbers and
  field names, not each rule's clauses against §1 or each copy against its canonical text; it passes despite IA-02, and its positive control (the filing
  tree) shows only that absent text fails. Attribution: this ECO's instrument.
- **IA-04 — blocking — the rehearsal does not implement C1's "measures".** `rehearse_part.py` checks that each `provides` ID is listed by a row in the
  unit's `acceptance_refs` and that listed IDs exist; it never reads what a row measures or its `known_limits`, so an unrelated row citing an entry
  passes. The evidence supports reference integrity, not C1 as written.
- **Not repaired yet.** IA-02 (the text) and IA-03 (the instrument) can be repaired inside the filed design. IA-01 needs a ruling on the diff window (as
  for ECO-112 and ECO-113), and IA-04 a ruling on C1 or on what V2 claims — both are the user's (a window exception; a rule or acceptance change).

## 6. Repair after inspection r1 (2026-10-24, user ruling "1:A 2:A")

**Rulings:** 1:A — IA-01 is settled for ECO-114 only, by ECO-113's method: the change set is ECO-114's commits, `afabdb1` (ECO-115's held draft) excluded
with its reason (OBS-20261018-02's third case; a general rule is a separate question). 2:A — C1 stays as written; whether a row measures an entry is
the orchestrating AI's judgement at step 5 and the inspection's reading, declared in L2 and in §4.5's limits; V2 claims only C1's reference part (the
acceptance text amended by this ruling).

**What changed, by finding:**
- IA-02 — playbook §4.6 "Phase 3 の順序と担当" now states O4 (the roles by layer, the orchestrating AI's may-see / must-not-see equal to the designer's);
  §9's row says it is the copy.
- IA-03 — `check_v1_v2.py` checks each rule's clauses (64, taken from §1) in the canonical text and in each copy, §9's two rows' equal columns, and the
  prompt's step order; `--mutations` removes each clause in turn: 64 of 64 caught (`manufacture/v1-mutations.txt`); V1 on the repaired tree PASS, on the
  filing tree FAIL. V1's text in §3 says how "says the same" is checked.
- IA-04 — §4.5's limits and this order's L2 state that "measures" is judged, not checked mechanically; V2 says what the script checks (2:A).
- IA-01 — `bomdd/reports/eco-114-part-standard/diff-window/`: `be96698..5bc708a` PASS (3 ECO-114 commits, 26 paths, all allowed; `afabdb1` before the
  manufacture, touching none of ECO-114's records or input files); positive control `--control-include afabdb1` FAIL (C4, C5). Measured again at
  closure. `method/improvements.md`: OBS-20261018-02's third case (watch 3/3; the worklist marks it due for promotion review — the user's stop point).
- Not changed: P1-P4, O1-O3, C1's rule text, A1, A2, the templates and the prompt.

## 7. Independent inspection r2 (2026-10-24, EQ-002, range 是正確認+回帰) — REJECT IA-05

- **Launched through the operator entry** on `faffcf9` (CI 40049535617 success; witness tree `92c40251340b`, gate self-conformance). Brief
  `26cb1c95a3dd…` (stored; committed copy `bomdd/reports/eco-114-part-standard/inspection-brief-r2.md`); report `inspection-r2.md` (`1af6f9b5d190…`);
  the ledger's cell record binds it (`REJECT`, `journal_end: committed`, run `20261024T012627.392469Z`).
- **Items:** IA-01 under 1:A PASS (the window on ECO-114's commits passes C1-C5; the control fails); IA-02 PASS (§4.6 states O4; §9 a matching copy);
  IA-04 under 2:A PASS; regression PASS (only §6's areas changed; all 18 README sha256 match; the rehearsal byte-identical). IA-03 FAIL through IA-05.
- **IA-05 — blocking — V1's clause list does not cover every clause of §1.** The 64 listed clauses pass and each removal fails its rule, but the list
  leaves clauses out (the inspector names some in P1, P2, O1, O2, O3, C1, A1, A2); an in-memory probe removing O3's "re-check A1 and C1 before G3" from
  the canonical text still gave V1 PASS. The finding is about the checker's coverage: the inspector reports no clause missing from the method text.
- **Not repaired yet.** Two ways, the second an acceptance change: extend the list to the clauses named (a later round may name more — a prose
  equivalence between the English order and the Japanese method text cannot be derived mechanically); or keep the list as named evidence and declare,
  as for C1's "measures" (2:A), that the completeness of the text against §1 is the inspection's reading. The user rules.

## 8. Repair after inspection r2 (2026-10-24, user ruling "C")

- **Ruling "C":** extend V1's clause list to the clauses r2 named, and declare that completeness beyond the list is the inspection's reading (V1's text
  and L6 — an acceptance change by the ruling).
- **What changed:** `check_v1_v2.py` gained 32 clauses (P1 3, P2 1, O1 4, O2 3, O3 2 — the canonical pre-G3 re-check and its copy in the prompt — C1 3,
  A1 11, A2 5); V1 on the tree PASS; `--mutations` 96 of 96 caught (r2's in-memory probe, removing O3's pre-G3 re-check, is now among them); the filing
  tree still fails. The order's V1 and L6. No method text changed.

## 9. Independent inspection r3 (2026-10-24, EQ-002, range 是正確認+回帰) — ACCEPT

- **Launched through the operator entry** on `c221153` (CI 40051091651 success; witness tree `21815ac3bdbb`, gate self-conformance). Brief
  `e424f389fd25…` (stored; committed copy `bomdd/reports/eco-114-part-standard/inspection-brief-r3.md`); report `inspection-r3.md` (`750811b68f5c…`);
  the ledger's cell record binds it (`ACCEPT`, `journal_end: committed`, run `20261024T014646.688736Z`).
- **All three items PASS; findings: none.** IA-05 under "C" (the 32 clauses r2 named added; 96 of 96 removals caught; the filing tree fails; V1's text
  and L6 carry the ruling). The method text read against §1 by the inspector: P1-P4, O1-O4, C1, A1 with its scope and lazy rule, and A2 stated in their
  canonical places, the copies matching, no omission or contradiction. Regression: only §8's files changed; the diff window `be96698..c221153` PASS and
  its control FAIL; the rehearsal byte-identical; 18 README sha256 match.

## 10. クローズ (closure, 2026-10-24, verified)

The acceptance commit after `5ac2145` holds records only (this section, the register entry, the diff-window evidence). Results by acceptance item:

- **V1 — PASS (the text).** `check_v1_v2.py` on the final tree: 96 named clauses present in their canonical places and copies, §9's rows, the prompt's
  order, the template fields with their place comments; `--mutations` 96 of 96 caught; the filing tree `25bea38` fails. Completeness beyond the list was
  read by the inspector in r3 (no omission or contradiction) — user ruling "C".
- **V2 — PASS (the standard on real units).** The rehearsal re-run on the manufactured field names is byte-identical to the filing's: both products'
  real BOMs give no failure, 4 allowed changes none, 19 known-bad changes each their own clause; V2 claims A1 and C1's reference part only (user ruling
  "2:A"; whether a row measures an entry is judged, L2).
- **V3 — PASS (the gate `inspection`).** EQ-002: r1 境界探索 REJECT IA-01 to IA-04 (§5) → repair under "1:A 2:A" (§6) → r2 是正確認+回帰 REJECT IA-05
  (§7) → repair under "C" (§8) → r3 是正確認+回帰 **ACCEPT** (§9), read as the gate `inspection` from the ledger's last cell record with a report.
- **V4 — PASS:** self-conformance exit 0 before each commit (the pre-push witness admits a push only after a PASS); CI success on the tip of every push:
  `25bea38` 40036248353, `afabdb1` 40041426012 (ECO-115's record, in the window), `286d02c` 40042223303, `5bc708a` 40043205542, `faffcf9` 40049535617,
  `45fcc66` 40050285583, `c221153` 40051091651, `5ac2145` 40051850314. This commit's run is observed after push.
- **The diff window, under the exception ruling (1:A on r1's IA-01):** `bomdd/reports/eco-114-part-standard/diff-window/diff-window.md`
  (`4bfaf0cfd528`): `be96698..5ac2145` PASS, 7 ECO-114 commits, 35 paths, all inside the register's `allowed_paths`; `afabdb1` excluded with its reason,
  before the manufacture, touching none of ECO-114's records or input files. Positive control (`control-include-afabdb1-final.md`, `ce6c2351274a`): FAIL.
- **The promotion decision** (bomdd-run under ECO-112's G3, dry, on the tree of this closure): **ADVANCE OK** (decision
  `20261024T020546.994337Z`, tree `e5c5b01bded8`): `required_gates` = `matched_gates` = [V1, V2, inspection] — V1 and V2 from the witness gates
  (`check_v1_v2.py` and the rehearsal re-run on that tree), `inspection` derived from the ledger (r3, ACCEPT, 是正確認+回帰, inspector EQ-002 required by
  this order's equipment line); three stored briefs, each with its committed copy (`brief_copies` 3). The equipment line `inspector: EQ-002` was added
  with this closure: without it the first dry run read the inspection as not required (R11), although the gate still matched by name.
- **The `{sha256, path}` pairs of ECO-114's stored briefs (ECO-112 B4):**
  - `c615d8bda30b859c88a3153cf690b0547a23605c0023d3b0f9fbdb220b7b3685` — `bomdd/reports/eco-114-part-standard/inspection-brief-r1.md` (r1)
  - `26cb1c95a3dd0a7449257804406143141a125f376d43017bb0cf27f57971867d` — `bomdd/reports/eco-114-part-standard/inspection-brief-r2.md` (r2)
  - `e424f389fd250eed15019788fdf21a9715480850e0df3ae07b5a370c5481c63f` — `bomdd/reports/eco-114-part-standard/inspection-brief-r3.md` (r3)
- **Declared limits that stay:** L1-L6 as in §1; the design was adopted unconverged by the user's cut-off ruling (receipt, loop 3). Not done here and
  recorded elsewhere: distribution to the products (a separate ECO); the MoviePad re-manufacture trial (EXP-20261024-01); ViewTube's unparsable Control
  Plan (OBS-20261024-01); OBS-20261018-02 at 3/3, due for its promotion review (the user's stop point); ECO-115 held unconverged (record `afabdb1`).

### 較正 receipt (/calibrate self-application - trigger ①: verified promotion; receipt_author_role = producer)

- **The claim (one sentence).** The method now states each unit's part standard (provides with ruled or derived boundaries, requires with targets),
  external promises once in the E-BOM, the Phase 3 order with owners by layer, and assembly resolution checked from the BOM files at G3, and the evidence
  shows the text says so and the resolution rules can be applied as written to real BOMs.
- **査定した主張と判定** (claims assessed; measurement × evidence):
  - "The text states the rules in their canonical places and the copies match": **observed / conditionally eligible** — 96 named clauses with a
    removal each (96/96 caught) and a control; completeness beyond the list rests on the inspector's reading (r3), not on the instrument (L6).
  - "A1 and C1's reference part apply as written to real BOMs": **observed / eligible** for the shapes in `shapes.txt` — both real BOMs (no failure,
    the lazy scope), 4 allowed and 19 known-bad one-change cases on four ViewPrism2 units, byte-identical across filing, manufacture and r3.
  - "A row measures the entries it lists" (C1): **unknown — not mechanically measurable (by ruling 2:A)**; no qualification given; it is the
    orchestrating AI's judgement and the inspection's reading (L2).
  - "The part standard makes a part usable by the next process in a real product": **unknown — not run** (no product has used it; EXP-20261024-01).
- **検出した計器欠陥と帰属** (instrument defects found): 4, all in this ECO's own `check_v1_v2.py`: (1) a step-order match outside §4.6; (2) a traceback
  instead of FAIL on the control tree (both before the manufacture commit); (3) labels and selected tokens instead of clauses, passing while O4 was
  missing from its canonical place (r1 IA-03, found by the inspector); (4) a clause list not covering §1 (r2 IA-05, found by the inspector), and in its
  repair a clause whose bare form occurred twice was missed by the first mutation run. Attribution: the producer's instrument; (3) and (4) were found
  only by the independent inspection after the producer's checks had passed.
- **宣言した検出力の限界:** the English register and the Japanese text cannot be compared mechanically (L6); "measures" is judged (L2); the rehearsal
  covers four units of one product and both products' legacy BOMs only under the lazy scope; no product ECO has exercised the rules; the
  self-assessment is the producer's own, the inspections r1-r3 and the converge reviewers are the outside checks.
- **Battery, row by row:**
  - **Q1 asked.** The checker's docstring and README against its code (r1 found the overclaim; repaired).
  - **Q2 asked.** Known-bad / known-good in pairs: 96 clause removals; the filing tree as control; 19 known-bad and 4 allowed rehearsal cases; the diff
    window's control.
  - **Q3 asked.** Each clause fails alone (one removal per clause); each A1 clause has its own case.
  - **Q4 asked.** The rehearsal reads the products' real BOMs and a rehearsal BOM written from real entries; no declared-only fixture.
  - **Q5 asked.** A missing heading or path is FAIL, not a crash (repaired); "measures" is recorded as unknown, not as a pass.
  - **Q6 asked.** Each commit after self-conformance exit 0; each inspection launched after CI success; each report read before its record.
  - **Q7 asked.** Positive controls for the checker (the filing tree, the mutations), the rehearsal (known-bad cases) and the diff window.
  - **Q8 NA.** No preventive gate is added by this ECO (A1 runs at G3 by the orchestrating AI; no mechanical gate).
  - **Q9 asked.** The evidence READMEs' sha256 against the committed bytes (r1-r3 checked 18 each).
  - **Q10 asked.** The limits above and L1-L6.
  - **Q11 asked.** The rehearsal's real BOMs (legacy, no standard) and the rehearsal BOM (with standards) are measured as separate classes.
- **What this closure does not support:** a product effect (no distribution is filed); that the rules are right for products other than the two
  measured; ECO-115's advance decision.

## 収束 receipt (converge self-application)

### Loop 1 (before the split; the part standard and the advance decision together)

- **判定: 未収束** (round 軌跡: 26→8→8; material 20→3→4). Limit of 3 rounds reached. No filing commit; round-3 findings not repaired. User ruling "A":
  split the advance decision to ECO-115, remove its common cause first, continue the rest here with rounds counted afresh.
- **起動経路**: 自発 (design synthesis after the user's "A").
- **Round 1 — 26 findings (20 material); Round 2 — 8 (3 material); Round 3 — 8 (4 material), unrepaired.** The details are in ECO-115's receipt (not filed with this ECO), which
  carries the advance-decision findings with their dispositions; R3-6 (O1 stated in three places) stayed here and is met by the map's canonical place and
  checked copies.
- **Correction (loop 2):** loop 1's receipt said rounds 2 and 3 found no material defect in P, O or A. The round-2 and round-3 prompts asked for new
  findings and pointed the reviewer at the repaired advance-decision rules; P, O and A were not re-read. A fresh reviewer in loop 2 round 1 found 7 material
  defects there. "No finding" in those rounds meant "not asked", not "sound".

### Loop 2 (after the split; user "A"; rounds counted afresh)

- **判定: 未収束** (round 軌跡: 18→12; material 7→3). Round 2 had new findings, so two consecutive zero rounds could not come within the limit of 3;
  round 3 was not run. At the end of loop 2 there was no filing commit and the round-2 findings were unrepaired; loop 3 repairs them.
- **DoD (fixed before round 1 of this loop):**
  - D1 the user's condition (i), part side: the unit's criteria are stated in the BOM (its part standard and its rows), and each step from the E-BOM to the
    unit's rows is a rule in §1 with an owner.
  - D3 who designs parts and interfaces and who checks manufacturability is named, with the Phase 3 order.
  - D4 an external promise has one canonical text, in the ruling layer; the M-BOM refers by ID.
  - D5 each rule has one canonical place; copies are named and checked.
  - D6 every basis claim (§0) names its measurement or file and line.
  - D7 each acceptance observation fails for its own rule's reason (a known-bad input per rule it shows).
  - D8 no new tool or mechanism beyond M1's text and templates; limits declared against the rule they limit.
  - (D2, the user's condition (ii), is ECO-115's DoD.)
- **Round 1 — 18 findings (7 material).** An `IF-` not tied to its realization (L2R1-1); "external" undefined for units with 0 or several E items, self
  consumption, unrealized items and cross-item `PS-` references (L2R1-2); no `requires` target field (L2R1-3); the lazy rule against A1 (L2R1-4); the fixed
  oracle's owner changed silently (L2R1-5); V2's unit not runnable alone (L2R1-6); assembly rows undefined between the two ECOs (L2R1-7); minor L2R1-8 to
  L2R1-18.
  - Common cause: the rules were written against the template's 1:1 picture of E items and units, and the BOM's real shapes were not enumerated. Before
    repair, `shapes.py` enumerated every shape in both products and the templates (B4); each rule now states what it does for each shape that exists:
    units with no E item (P4, A1 4), units realizing several items and items realized by several or none (A1 2, 5), connections in `depends_on` or
    `graph_edges` (P2, L3), self consumption (A1 5), unit `depends_on` (A1 6). Repairs in place: the `requires` target (P1), consumed legacy units (A1, M1),
    the fixed oracle back with the designer (O1 5), V2's unit set (V2), `mbom.assembly` defined here and read by ECO-115 (A2), and L2R1-8 to L2R1-18
    (header, C1 and `known_limits`, §9 (O4), §4.5's extension (map), the copies outside M1 (L5), who runs A1 at G3 (O3), the FMEA keys (O1 2), spec
    references in `IF-` (P2), conventions (P1), the basis wording (B2, B4)).
- **Round 2 (full re-read) — 12 new findings (3 material), unrepaired.** 9 of round 1's 18 repaired outright, 9 repaired with a new problem (counted once
  below). Material: L2R2-1 A2 says golden is not a Control Plan row, but depth-G rows are rows (ViewPrism2 CP-UI-G*, ViewTube 7), and whether app-level
  golden rows go in `assembly` is open; L2R2-2 A1 6 fails on legacy units with `depends_on` and no standard (ViewTube `M-VIEW-PACK-001`,
  `M-DEMO-CURATOR-001`), so G3 fails everywhere; L2R2-3 when the spec states a boundary abstractly (ViewPrism2 `OC-1`), the concrete signature has no place
  under P1/P2. Minor: L2R2-4 A1 4's allowances; L2R2-5 an `IF-` consumer unchecked in reverse; L2R2-6 V2's clauses fire together; L2R2-7 `graph_edges`
  owner differing from its holder (and shapes.py's label); L2R2-8 design-system items realized outside the M-BOM; L2R2-9 the map's "fifth sentence";
  L2R2-10 FMEA has no E-item key; L2R2-11 O4's row by step instead of by layer; L2R2-12 "receiving side" and the UI unit.
- **Where the findings come from:** the new rules meet what already exists — golden rows, legacy units, a spec that states boundaries abstractly, the
  design-system parts — and each such meeting was found by reading, one round at a time.
- **DoD at round 2:** ✔ D3, D5, D6, D7, D8; ✘ D1 (L2R2-1, L2R2-3), D4 (L2R2-3).
- **未収束事項 at the end of loop 2:** L2R2-1 to L2R2-12 (repaired in loop 3, below).

### Loop 3 (extension; user "A", 2026-10-24; the common cause removed first; limit 3 rounds)

- **判定: 未収束** (round 軌跡: 8→3; material 1→0). Round 2's three findings are minor, but they are new findings, so two consecutive zero rounds cannot
  come within the limit; round 3 was not run. User ruling "1:A": cut-off adoption with round 2's findings repaired (below); filed; manufacture waits for
  the user.
- **DoD:** unchanged from loop 2.
- **Common cause removed first — the rules run on real data.** `rehearse_part.py` applies C1 and A1 as written; `run_rehearsal.py` runs it on both
  products' real BOMs and on `rehearsal-bom.yaml` (ViewPrism2's three items and four units in the new shape) with one change per case — 13 in its
  first run, 23 at filing (4 allowed, 19 known-bad), besides the 3 baseline runs (`rehearsal.txt`):
  - X1: both real BOMs as they are give no failure — the clauses' scope (units with a standard, items with `interfaces`) keeps the legacy BOMs passing,
    which also means A1 and C1 say nothing about them until their units are touched (L4).
  - X2: `E-DOMAIN-001` is realized by two units but its `IF-` by one (`M-CORE-001`): clause 2 counts the units that carry the `ruled_ref`, not every
    realizer of the item — the rule is stated that way.
  - X3: three cases report more clauses than their own (a missing target also breaks clauses 5 and 6; a removed `requires` also breaks clause 6) — V2 now
    asks for the own clause among those reported and lists the rest.
  - X4: the abstract `OC-1` and the concrete signature both have a place (P1 `form`); the relay through a unit with no `ebom_refs` fails (A1 4).
- **Loop 2 round 2 repairs:** L2R2-1 A2 (golden rows are Control Plan rows; only the fixed oracle is not); L2R2-2 A1's scope; L2R2-3 P1 `form`; L2R2-4 P4
  and A1 4, L3; L2R2-5 A1 1 and 7; L2R2-6 V2's rule; L2R2-7 B4, P2 and `shapes.py`'s label (re-run; new sha256); L2R2-8 P2 (unrealized items carry no
  `IF-`); L2R2-9 the map; L2R2-10 O1 2 and M1 (`ebom_ref`); L2R2-11 O4 by layer; L2R2-12 A2 ("receiving side"), P4 (the UI unit).
- **Round 1 (full re-read) — 8 new findings (1 material).** L3R1-1 P4 / A1 4 forbade a harness with no `ebom_refs` from requiring the units it verifies
  (ViewPrism2 `M-HARNESS-015`); minor L3R1-2 an `IF-` relay through such a unit; L3R1-3 the `IF-` entry's fields and the rehearsal BOM's own entries;
  L3R1-4 branches and shapes not exercised (`graph_edges`, A1 5's exemption, A1 1's last branch, a resolving `procurement:`, a `ruled_ref` on a unit
  with no refs) and `procurement`'s place in the rehearsal BOM; L3R1-5 checks the script made that §1 did not state; L3R1-6 A1 6's "where present";
  L3R1-7 which rows go to `assembly`; L3R1-8 a stale receipt sentence.
  - Repairs: P4 and A1 4 forbid the relay, not the use (L3R1-1, L3R1-2); P2 names the `IF-` fields `refs` and `boundary` (L3R1-3); P1 and C1 state the
    two checks the script makes, A1 1 says `platform:` is accepted as written and `procurement` is top-level (L3R1-5); A1 6 reads a non-empty list
    (L3R1-6); A2 makes the `assembly` choice the orchestrating AI's, recorded, with a row allowed in both places (L3R1-7); the receipt (L3R1-8). The
    rehearsal gained 4 allowed and 6 known-bad cases (L3R1-4): all 22 changes and the 3 baseline runs gave their expected outcome, both real BOMs still
    none.
- **Round 2 (full re-read) — 3 new findings (0 material), unrepaired.** All 8 of round 1 repaired. L3R2-1 a relay through two units with no `ebom_refs`
  is not caught (P4 states it as a guarantee); L3R2-2 V1's field list lacks `form`, `refs`, `boundary` and the FMEA `ebom_ref`; L3R2-3 the receipt's case
  counts (25 = 22 changes plus 3 baseline runs; the README says 4 allowed and 18 known-bad).
- **DoD at round 2:** ✔ D1, D3, D4, D5, D6, D7, D8 (the reviewer's reading; the three minor findings sit under D7 and D8).
- **User ruling "1:A" (cut-off adoption), 2026-10-24.** Repaired before filing, not re-reviewed: L3R2-1 P4 and A1 4 say "directly or through other units
  with no `ebom_refs`", the script follows the chain, and a relay-chain case was added (A1 4 reported); L3R2-2 V1 lists `form`, `refs`, `boundary` and
  the FMEA `ebom_ref`; L3R2-3 the counts are stated once (23 changes: 4 allowed, 19 known-bad; 3 baseline runs). The rehearsal re-run gives every case
  its expected outcome and both real BOMs none (`rehearsal.txt`, sha256 in the README).
- **未収束事項:** none open; the verdict stays **未収束** under the converge rule (adopted by the user's cut-off ruling).

(Rounds below.)
