# EXP-20261030-02 — definitions (fixed before any inspector runs)

Fixed 2026-10-30. A change after this point is a departure (section 9).

## 1. The question

EXP-20261030-01's follow-up found that six recorded upstream defects were named, in the records, only by people reading the text
and the mock together, and that no deterministic check on today's inputs names them. The user's "A" (2026-10-30): **measure the
reader.** On the six as known-bad inputs, does an isolated AI inspector name the defect before its fix, and stay silent on it after?

This is a measurement. It changes no method text, template, tool or product.

## 2. The six, their states and their hit criteria

Each item has a **pre** state (the inputs as they stood before the fix) and a **post** state (just after the fix — one change apart,
not the products' current HEAD). The criterion is what the inspector's report must name; it is fixed here, before any report exists.

| item | source | pre (product / UI repo) | post | hit criterion — the report names… |
|---|---|---|---|---|
| D1 (VT-002) | ViewTube ECO-VT-035 | `ad8c37c` | `6f24075f` (golden approved) | that batch tag assignment has no way to **remove** (unassign) a tag, **or** no surface where the tag / value is chosen and the assigned / mixed state shown, behind the assign action |
| D2 (VT-003) | ViewTube ECO-VT-040 | `2060849` | `b9f629d6` (golden approved) | that the batch tag action is **not available in ordinary browsing** although selection is offered there (available only in the hierarchy layout) |
| D3 (VT-024) | ViewTube ECO-VT-226 | `05e2d905` | `1cd3e7a5` (golden approved) | that there is **no operation to create (and name) a manual collection** |
| D4 (VP-024) | ViewPrism2 ECO-052 | VP2 `19c436f` / ViewPrismUI `7ffd423` | VP2 `bd573d6` / ViewPrismUI `7ffd423` | that the requirement's **pre-merge preview of the merged tags and the "files are not deleted" notice** are absent from the organize tray (or that the text and the tray disagree on them) |
| D5 (VP-043) | ViewPrism2 ECO-119 | VP2 `872d33c` / ViewPrismUI `2c31176` | VP2 `403756a` / ViewPrismUI `c9b5667` | that the CAD text cites a **docked tag-assign operation / area** the mock does not have (or that it contradicts the immediate row-click assignment) |
| D6 (VP-055) | ViewPrism2 ECO-140 | VP2 `6866b2f` / ViewPrismUI `5556df2` | VP2 `58354ed` / ViewPrismUI `3a1bb37` | that **relink is assigned to two owners** — the text hands it to the repair flow while the review mock relinks itself |

D4 was fixed on the text side (the user's ruling b: the requirement amended to the existing UI); its post state differs from pre in
the requirements only.

## 3. Packages

Built by `packages.py` from the commits above with `git show` (never a working tree), into a staging folder outside every
repository; `manifest.json` (committed) lists each file with its SHA-256.

- **Notes** (the §17 "designer notes"): ViewTube `bomdd/ui/design-intent.md`, `bomdd/ui/unresolved-questions.md`, and
  `bomdd/ui/videos-cad.md` where it exists; ViewPrism2 the CAD screen documents in ViewPrismUI `docs/screens/` that the item's order
  names (D4: `image_tab.md`, `work_tab.md`; D5: `image_tab.md`, `work_tab.md`; D6: `pending_review.md`, and `integrity_review.md`
  where it exists).
- **Mock**: ViewTube `bomdd/ui/mock/viewtube-v1.html`. ViewPrismUI's mocks under `資料/`: a `.dc.html` as stored; a standalone bundle is
  reduced to its authored page — the `__bundler/template` block decoded — with the runtime and fonts dropped (stated in the
  manifest). D4: `画像タブ/ViewPrism2 画像タブ.dc.html`, `画像タブ/ViewPrism2 整理マージ (standalone).html`, `作業タブ/ViewPrism2 作業タブ.html`;
  D5: `画像タブ/ViewPrism2 画像タブ.dc.html`; D6: every file under `未裁定の画像/`, and under `要確認の画像/` where it exists.
- **Ruled text** (arm B only): the product's `bomdd/10-requirements.yaml` and `bomdd/20-spec.md` at the state's product commit.
- No raw IR, no DOM snapshots: §17's typical package has them, but ViewTube's committed raw IR drifts from its mock (the follow-up of
  EXP-20261030-01) and ViewPrism2 has none; the inspector reads the mock source. A departure from §17's package, declared here.
- The screens are chosen by the designer from the order — a hint of **where**, not of **what**. Stated as a limit.

## 4. Arms (two instruments)

- **Arm A — §17 as it exists.** The prompt `method/prompts/ui-mock-coverage.md` verbatim from "あなたは UI モックの受入検査官である"
  to the end, with the package listed as the input (notes + mock).
- **Arm B — a text–mock reader derived from §17.** The same prompt with two changes, and only these: the input restriction admits the
  requirements and the specification as part of the package; layer 1 gains one line — "要求・仕様とモック(注記・DOM)の間の矛盾と、
  要求・仕様が求めるのにモックに無いもの、モックにあるのに要求・仕様が述べないものも列挙する". Arm B's numbers are not §17's.
- **In scope by design** (a miss outside it is not the instrument failing): Arm A — D1, D2, D3, D5, D6 (D4's requirement is not in
  its input). Arm B — all six.

## 5. Runs and staging (bounding the cost)

- Inspector: a fresh-context Claude agent per package, given only the staged folder's path and the prompt; it writes `report.md`
  into that folder. One package per agent (an agent never sees two states of the same screen).
- **Stage 1**: pre state, both arms — 12 runs.
- **Stage 2**: post state, only for (item, arm) pairs judged hit or partial in stage 1. A hit whose control did not run is reported
  as "hit, specificity unmeasured" — never as specific.
- Each stage is watched by a file-appearance monitor with a 30-minute bound; a run with no report at the bound is a **no-report**,
  counted as a miss and listed (never retried silently).

## 6. Judge

Codex (`--model gpt-5.6-sol`, as EXP-20261030-01 D1), given per report: the item's hit criterion and the report text only — not the
arm, the state or the item's source. Reports are relabelled `R01…` in a shuffled order (`judge-map.json`, written before judging,
committed after). Verdict per report: **hit** (names that thing at that granularity), **partial** (names the area or asks the
question without naming the thing), **miss**, with the quoted line(s) it relies on. On a post report, hit or partial = **false alarm**
(the defect is fixed there).

## 7. Reading (fixed now)

Per arm, over its in-scope items, hits (and partials) in stage 1, false alarms in stage 2.

1. **Arm B** (the text–mock reader): ≥ 4 of 6 hit with ≤ 1 false alarm → a reader-based text–mock comparison is worth wiring as a
   **measured** input of G2 (its receipt counted, not trusted); ≤ 2 of 6 hit → reading does not reach these either, and the residue
   stays with acceptance; otherwise → no claim.
2. **Arm A** (§17 as it exists): ≥ 4 of 5 hit with ≤ 1 false alarm → §17, applied as written, would have named them — not applying it
   is the gap; ≤ 1 of 5 → §17 as written does not reach this class; otherwise no claim. Reference only (not a threshold): the one
   prior §17 measurement, MoviePad 2026-07-05, hit + partial 69 %.
3. Partials are reported beside hits and enter no threshold.
4. Six items, one run each: no rate is claimed beyond these six; a single run per package measures one draw of a non-deterministic
   reader.

## 8. Limits

- The screens were chosen from the order (section 3). The packages omit what the readers of the time also had (captures, rulings
  ledgers, other screens).
- The inspector reads mock source, not rendered states.
- Post states for D1-D3 are the golden-approved commits, which may carry other changes of the same ECO.
- The judge is one AI; its verdicts and quoted lines are kept for re-reading.

## 9. Departures

(none yet)
