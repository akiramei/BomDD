# EXP-20261030-03 — definitions (fixed before any table is derived or any check is run)

Fixed 2026-10-30. A change after this point is a departure (section 11).

## 1. The question

The aim (the user, 2026-10-30): **make the design verifiable** — a step beyond review, which depends on the reviewer. EXP-20261030-01's
follow-up found that the recorded upstream defects sat at granularities no check had an input for, and EXP-20261030-02 measured a
reader on six of them (no claim). The proposal accepted with the user's "起票する": write the design as an **operation table** — each
operation with its entity, kind, counterpart, owning surface and availability per state, tied to the mock's action names and to the
requirement it comes from — so that checks on it are deterministic.

On ViewTube's three items of EXP-20261030-02 (D1, D2, D3), each with a pre-fix and a post-fix state: **does a deterministic check fire
on the defect before its fix and stay silent after it?**

The text side is still read: the requirements and spec cite no mock action and 2-3 UI ids in all six states (measured with
`git show`, 2026-10-30), so mapping their sentences to operations is reading. The step measured here over EXP-20261030-02 is that the
reading's output is a structured table and the checks on it are deterministic — not that reading is gone.

This is a measurement. It changes no method text, template, tool or product.

## 2. Items and states

| item | source | pre (ViewTube) | post | the defect, as the table must carry it |
|---|---|---|---|---|
| D1 (VT-002) | ECO-VT-035 | `ad8c37c` | `6f24075f` | batch tag assignment has no unassign counterpart |
| D2 (VT-003) | ECO-VT-040 | `2060849` | `b9f629d6` | the batch tag action is absent in an ordinary-browse state that offers batch selection |
| D3 (VT-024) | ECO-VT-226 | `05e2d905` | `1cd3e7a5` | the manual-collection entity has no create operation |

Controls checked before filing (`git show`, 2026-10-30; the OBS-20261030-04 lesson applied):
- D1 post's mock has `BatchUnassignTag`; pre's has none.
- D2 post's text adds the requirement (the batch action in every result mode with batch selection: ordinary collection, search/filter,
  saved hierarchy all and unclassified) and its mock adds the `browse=ordinary` capture. D2 pre's text already states batch selection
  in collection and filter results (REQ text "Filter, collection, view, path or mode change intersects the batch set").
- D3 post's mock has `CreateManualCollection` and `OpenManualCollectionCreate`; pre's has neither.
- **D1 post and D2 pre are the same input**: requirements, spec, both notes and the mock are the same blobs (`videos-cad.md` exists in
  neither). Their two derivations measure the derivation's variation on one input (reported, section 8).

## 3. Packages

`packages.py <staging-dir>` builds T01-T06 (D1 pre, D1 post, D2 pre, D2 post, D3 pre, D3 post) with `git show` (never a working tree)
into a staging folder outside every repository; `manifest.json` lists each file with its source and SHA-256. Each package: `ruled/`
(`bomdd/10-requirements.yaml`, `bomdd/20-spec.md`), `notes/` (`bomdd/ui/design-intent.md`, `bomdd/ui/unresolved-questions.md`,
`bomdd/ui/videos-cad.md` where it exists), `mock/viewtube-v1.html`, `actions.txt` and `prompt.md`.

`actions.txt` = every distinct `data-ui-action="…"` value in the mock, extracted by regex, minus template literals (values containing
`$` or `{`) and the drawing tool (`PreviewCad*` — the mock's own state switcher, not a product operation). This list is mechanical.
Built at filing (manifest.json): 43, 50, 50, 50, 117 and 126 actions; T02 and T03 have the same files (same SHA-256); T05 and T06
are 0.75 and 0.84 MB (by then ViewTube had a CAD notes file and a 0.37-0.44 MB mock). On the built `actions.txt`,
`BatchUnassignTag` is absent from T01 only and `CreateManualCollection` present in T06 only (the controls of section 2 again).

## 4. Layer M — mock only, no AI (the cheapest instrument)

`checks.py run` applies it to each package's `actions.txt`. Each action name is split into CamelCase tokens. Its **verb** is the first token
in `VERBS`; its **object** is the other tokens, minus `FILLER`, joined.

- `PAIRS` (each direction): Assign↔Unassign, Create↔Delete, Create↔Remove, Add↔Remove, Archive↔Restore, Archive↔Unarchive,
  Register↔Unregister. `VERBS` = the words in `PAIRS`.
- `FILLER` = Batch, Request, Confirm, Open, Start, Cancel, Close, Validate, Toggle.
- Navigation verbs (Open, Close, Navigate, Select, Show) are not paired: they are filler or not verbs here.
- **M1 (stop)**: an action whose verb has partners flags when no other action has a partner verb and an object that contains, or is
  contained in, its object.

The lexicon is **in-sample**: it was written after seeing `BatchAssignTag` / `BatchUnassignTag` and `RequestCollectionDelete` /
`CreateManualCollection`. D2 is outside layer M by design: its defect is per state, and layer M has no states.

## 5. Layer T — an AI-derived operation table, deterministic checks

### 5.1 Derivation

One fresh Claude agent per package, given only its folder and `prompt.md`. Not told the item, the state, the defects or the checks.
Told to **transcribe** what the inputs say into the schema — not to judge, fix or review — and to write `null` / `not_drawn` where the
inputs say nothing. It returns the table as one fenced `json` block. The harness refuses subagent report files
(EXP-20261030-02 D1); the table is therefore **taken by script from the agent's stored transcript** — the content of its refused
`Write` of `table.json` if there is one, else the last `json` block of its hand-back (`extract_tables.py`, which also prints the
derivation time and any path touched outside the package). Nothing is retyped. A package whose output is not JSON with the three
lists is a **no-table**, counted as a miss and listed. A row failing its fields (section 5.2) is dropped and the count reported.

### 5.2 Schema

```
{"states": [{"id", "name", "source": "mock"|"text"|"both", "selection_possible": true|false|null, "evidence"}],
 "entities": [{"id", "name", "evidence"}],
 "operations": [{"id", "label", "entity", "kind", "mock_action", "text_refs", "owner_surfaces", "counterpart", "availability"}]}
```
- `kind` ∈ create, delete, assign, unassign, add, remove, archive, restore, update, navigate, view, other.
- `mock_action` = a name from `actions.txt`, or `null` when the mock does not draw the operation.
- `text_refs` = the REQ ids / spec sections that require or presuppose it.
- `owner_surfaces` = the surfaces where it is performed.
- `counterpart` = the id of the operation that undoes it, or `null`. The prompt states that the mock's action names and labels are
  input, so an undo relation readable from them counts as stated (fixed before filing: otherwise a literal reading of "null when the
  text says nothing" would set every counterpart null and T3 would fire on both members of a drawn pair, a false alarm on post that
  measures the prompt, not the table).
- `availability` = {state id: enabled | disabled | absent | not_drawn}.
- The states are the union of the states the mock draws (its capture parameters and screens) and the states the text names.

### 5.3 Checks (`checks.py run`, on each package's `table.json`)

| check | label | fires when |
|---|---|---|
| T1 coverage | measure | an action in `actions.txt` is no operation's `mock_action` (derivation completeness, not a defect) |
| T2 text-only operation | stop | `text_refs` non-empty and `mock_action` null or not in `actions.txt` |
| T3 missing counterpart | stop | `kind` ∈ {create, delete, assign, unassign, add, remove, archive, restore} and `counterpart` is null, unknown, or an operation whose `mock_action` is null / not in `actions.txt` |
| T4 entity without creation | stop | an entity has an operation but no operation of `kind` create or add whose `mock_action` is in `actions.txt` |
| T5 availability asymmetry | stop | an operation is `enabled` in one state with `selection_possible` true and `absent` / `not_drawn` (or no entry) in another state with `selection_possible` true |
| T6 several owners | measure | `kind` ∉ {navigate, view} and more than one `owner_surfaces` (the D6 class; no ViewTube item) |

Free text in the table (`evidence`, `label`) is read by no check, except for the matching in section 6.

## 6. Matching a flag to the item (fixed now; no designer reading)

A flag's text = its operation's `id`, `label`, `mock_action` and its entity's `name`, joined (T4: the entity's `id` and `name`;
layer M: the action name). A flag
**matches** the item when:
- **D1**: from M1, T2 or T3, and the text matches `(?i)assign|付与|付け|外す` **and** `(?i)tag|タグ`.
- **D2**: from T5, and the text matches `(?i)tag|タグ`.
- **D3**: from M1, T2, T3 or T4, and the text matches `(?i)manual|手動` **and** `(?i)collection|コレクション`.
  (Layer M's D3: the object matches `(?i)collection`.)

**Caught** = at least one matching flag on the pre package **and** none on the post package. There is no partial: a flag is binary
(the OBS-20261030-03 correction). A matching flag on post = a **false alarm**.

## 7. Reading (fixed now)

1. **Layer T** over D1-D3:
   - ≥ 2 of 3 caught → an operation table is worth a **prospective trial as a G2 stop in ViewTube** (its design and start are the
     user's). This is qualified by the noise:
     - stop flags (T2-T5) on every post package ≤ 25 → "usable as a stop";
     - more than 25 on any post package → "catches, but the stop needs an exception-ruling step of that size".
     - 25 = about one sitting of table rows to rule; chosen, not derived.
   - 1 of 3 → no claim.
   - 0 of 3 → the table form does not reach these on these inputs.
2. **Layer M** over D1, D3: caught count and flags per package, **descriptive only** — the lexicon is in-sample.
3. Three items, one derivation each: no rate is claimed.

## 8. Also reported (descriptive)

- T1 coverage per package.
- Flags per check per package.
- The time of each derivation.
- **Reproducibility**: T02 and T03 (the same input) compared — operations by `mock_action`, the counts per check and the flag sets
  (Jaccard on `(check, operation mock_action or id)`).
- Whether D1's matching flag is silent on T03 as well as on T02, and D2's fires on T02 as well as on T03 (the same input under two
  labels): any disagreement is the derivation's variation, stated as such.

## 9. Limits

- **In-sample.** The checks, the lexicon and the matching patterns were written knowing these three defects. A hold-out exists and is
  not run here: EXP-20261030-01's other ViewTube structural items.
- One derivation per state. The derivation is a reader of the text, and non-deterministic.
- No human ruling of the table. Real use has one, which could add or remove rows.
- The mock is read as source: action names include those inside template strings, and nothing is rendered.
- The noise bound (25) is chosen, not derived.

## 10. Files and the run (when the user starts it)

- `packages.py <staging>` → T01-T06 and `manifest.json` (committed at filing).
- `checks.py selftest` — synthetic cases only: each check fires on a planted defect and is silent on its fixed twin (PASS at filing).
- The run: six derivers (section 5.1), then `extract_tables.py <staging> agents.json <subagents-dir>`, then `checks.py run <staging>`
  → `flags.json` and the tally. Layer M was not run before filing.
- Results go to `results.md`; the staging folder is deleted after the commit that records them.

## 11. Departures

(none yet)
