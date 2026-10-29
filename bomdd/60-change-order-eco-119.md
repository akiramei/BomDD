# Change Order — ECO-119 (the ruled layer becomes protected after the design release: a commit changing it is refused unless it names an open ECO whose order cites the sources read)

> Ruling: user, 2026-10-29, "1:A 2:A 3:A" on the three points of the authority order (lesson-promote stage 2, at review):
> - 1 = adopt the authority-order text in playbook §4.5: **A** (woven in the same commit as this filing);
> - 2 = file an ECO for the stop that protects the ruled layer, with the presence check of the sources read: **A**. This order;
> - 3 = make /lesson-promote admit body text only with a stop or a measure: **A** (applied in the same commit; not part of this order).
>
> The standing caveat of the same day (`method/improvements.md`, 2026-10-29 "After MoviePad-Remake ECO-006"): a rule nothing stops or
> measures is a wish. Each part below is labelled **stop** (refuses), **measure** (a number produced and compared) or **none** (text only).
>
> **Filing only.** Manufacture waits for the user's start instruction (ECO-106). Distribution to the products is a separate ECO (the
> ECO-108 → ECO-109 form). Records are English-primary.

## Equipment

- Filing: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- Producer: EQ-004.
- Independent inspection: one R8 round is planned before acceptance (a new stop in process-core; ECO-118 has the same plan). The user may change this at the start instruction.

## 0. Measurement (basis of the filing)

**What happened (MoviePad-Remake ECO-006, `bomdd/60-change-order-eco-006.md` §6 in that repository).** The designer framed two items as
"the E-BOM and the code disagree" and recommended matching the code — options that would have rewritten the ruled layer to the code's
shape. Read against the requirements, the specification, the ruled E-BOM and ADR-004, the E-BOM was right in both; the defect was in the
derived layer. Nothing stopped the proposal except the user's hold. No commit carried it, so there is no commit to point to; the failure is
the proposal, and it is the case this stop is for.

**What the equipment does today.** process-core's validator protects `protected_paths` (`src/`, `test/`, `tests/`) with E01 (an open ECO
at HEAD) and its own files with E08. The ruled layer — `bomdd/10-requirements.yaml`, `bomdd/20-spec.md`, `bomdd/30-ebom.yaml`,
`bomdd/31-kbom.yaml`, the ADRs — is not protected by anything: any commit may change it.

**The ruled layer's history in the one forward-built product** (MoviePad-Remake; design release = `bom-v4`, the tag at which G3 passed,
`5dde98c` on the user's "A"). Every commit after `bom-v4` that touches the ruled layer, with the ECO states in the register at its parent
(read with `git show <commit>^:bomdd/60-change-register.yaml`, 2026-10-29):

| commit | touches | open ECO at the parent | what it is |
|---|---|---|---|
| `0b50020` | `20-spec.md` (INV-008 row, trace rows), `30-ebom.yaml` (E-EXPORT-001 `acceptance_refs`) | none (ECO-001..003 applied) | a Control Plan row split carried into the ruled files' references, outside any ECO |
| `b06a5bf` | `20-spec.md` | none (ECO-003 filed in this same commit) | ECO-003's filing commit, with the spec correction |
| `ec6e549` | `31-kbom.yaml` | ECO-003 staged | ECO-003's K-BOM line made true |
| `f4861e8` | `reports/adr/ADR-002.md`, `ADR-006.md` (new) | none (ECO-005 filed in this same commit) | ECO-005's filing commit, with the human ruling's ADR |
| `31273e7` | `20-spec.md`, `30-ebom.yaml`, `31-kbom.yaml` | ECO-005 staged | ECO-005's BOM line (the human E-BOM ruling carried down) |
| `79f1791` | `reports/adr/ADR-003.md` | ECO-005 staged | ECO-005's R8 repair, a note on ADR-003 |

`bbce170` and `0522643` (G3 rounds 1 and 2) changed the specification before `bom-v4` — Phase 3 work, which the stop must not refuse.
None of the six carries a trailer (none was asked for). This table is where the acceptance arms below come from.

## 1. Change request (frozen at filing)

**T1 — the profile field (none; opt-in).** `method/templates/process-core/process-profile.yaml` gets one commented field:

```yaml
# ruled_layer:
#   since: <commit-ish>          # the design release (§7): the tag at which G3 passed
#   paths: [bomdd/10-requirements.yaml, bomdd/20-spec.md, bomdd/30-ebom.yaml, bomdd/31-kbom.yaml, <the product's ADR directory>]
```

Absent = no E13, so an installed product's behaviour does not change until its distribution ECO (or the product's own ECO) sets it;
setting it is a profile change and goes through E08. `paths` entries are files or directory prefixes (a trailing `/`). The scaffold
(`bomdd-init.py`) writes the field commented only; the product sets it at its design release (Phases 1-3 write these files before any
ECO exists).

**T2 — the stop: E13 `ruled-layer-change-without-ruling` (stop).** In process-validator's commit-msg mode, where E05 already reads the
message:
- **When it applies.** The profile has `ruled_layer`, `since` resolves to a commit, `since` is HEAD or an ancestor of HEAD, and the staged
  paths (`git diff --cached --name-only`, so deletions count; a rename counts by its new and its old path — the check reads
  `--no-renames`) include a `ruled_layer.paths` entry.
- **What it requires.** The message carries the trailer `BomDD-ECO-Ruling: <id>` (the name in the profile's `trailers.ruling`, default
  `BomDD-ECO-Ruling`), at least one, and for at least one named id:
  1. the id is an entry of the **HEAD** register (not the staged one) in an `open_states` state — so the ECO is filed in an earlier commit
     than the change (E01's rule, REV-10: "起票 commit が先・同一 commit 起票は不可");
  2. that entry's order (`order_ref`, or `bomdd/60-change-order-<id in lower case>.md` when the entry has none) exists at HEAD or in the
     index and has a section headed `Sources read` (T3).
- **Refused** when any requirement fails, and **refused** when `since` does not resolve or the register or the order does not parse
  (fail-closed once the field is set; unmeasurable is not a pass). The refusal names the ruled paths touched and the failed requirement.
- **Not checked:** commits before `since`; commits that touch no ruled path; the content of the change.

**T3 — the sources read (measure: a count compared with the touched files).** The named ECO's `Sources read` section must cite **each
ruled file the commit touches** at least once in the form `<path>:<line>` or `<path>:<line>-<line>` (path as in `ruled_layer.paths`, or
a file under a listed directory). Counted by the validator from the order's text: for every touched ruled file, the number of citations
in that section; any count of 0 refuses, naming the file. The section may cite anything else (the authority order of §4.5 says to read
the higher sources too); only the touched files are counted. `method/templates/60-change-order.md` gets the section with one line of
guidance pointing to §4.5's authority order.

**T4 — the history version (stop in the second layer).** E13 joins the history replay as E01 did (ECO-019): a commit after `since` that
touched a ruled path without a qualifying trailer — made with `--no-verify` or before the hook was installed — is reported by the
validator's full mode (`history:<sha>`), and in CI where the product runs it. For T3 the replay reads the order as it stood at that
commit.

**T5 — the text (none, pointing to the stop).** Playbook §4.5's authority-order paragraph (woven at filing) gets its enforcement bracket
changed from "ECO-119, filed" to the check id at acceptance; §7's design release gets one clause: set `ruled_layer.since` to the release
tag. The process-core qualification (`process-qualification.py`) gets V2's arms nested in its existing run (no new top-level group), as
ECO-118 T3 decided for E12.

**Decided at filing (the filer's derived-layer choices, recorded and reported per ECO-106).**
- **A trailer naming an ECO, not E01's "any open ECO".** The failure is an unattributed rewrite of the ruled layer; a commit that names
  the ECO ties the change to a filed decision and to its sources. E01's form would pass `0b50020`'s pattern whenever any unrelated ECO
  happened to be open.
- **File-first, as E01.** `b06a5bf` and `f4861e8` filed an ECO and changed the ruled layer in one commit; under E13 both are refused and
  the change moves to the next commit. Cost: one commit per ECO that carries a ruling. Gain: the filing (and its `Sources read`) exists
  before the change, which is the order the authority rule asks for.
- **File level, no field-level exclusion.** `0b50020` changed only references (E-BOM `acceptance_refs`, spec trace rows naming Control
  Plan rows). It is refused: excluding fields would make the stop's reach depend on a list of "harmless" keys, and §4.5 lists E-BOM
  `acceptance_refs` (an E → derived reference) as unmeasured. Consequence: a Control Plan row split that renames a row id cited by the
  ruled files needs an ECO. That this reference lives in the ruled files at all is OBS-20261029-03's question (copies of an authority),
  not this order's.
- **E13's number.** E12 is ECO-118's (filed, amended, not manufactured).

**Manufacture order.** ECO-118 and ECO-119 both change `process-validator.py`, its profile template and its qualification. ECO-119 is
manufactured after ECO-118 is verified, unless the user orders otherwise at the start instruction.

**Not changed:** the products (distribution is a separate ECO); E01, E05, E08 and every other check; the hooks' shape; the content of any
ruled file; ViewTube's gate freeze (a new gate there needs the user's exception).

## 2. No-impact prediction (before manufacture; frozen)

- **Diff:** `method/templates/process-core/tools/process-validator.py` (E13, its REASONS entry, the commit-msg and history paths),
  `method/templates/process-core/process-profile.yaml` (the commented field, `trailers.ruling`), `method/templates/process-core/tools/process-qualification.py`
  and its fixtures (V2's arms), `method/templates/60-change-order.md` (the section), `method/bomdd-playbook-v1.md` (§4.5 bracket, §7 one
  clause), `method/tools/bomdd-init.py` only if the scaffold writes the profile outside the template; this order, the register,
  `bomdd/reports/eco-119-ruled-layer/`.
- **Verdicts:** every existing validator check gives the same result on the same commit when `ruled_layer` is absent (V3). Every existing
  self-conformance check gives the same line on the same tree; C11's qualification gains arms.
- **Products:** none changed by this ECO. A product's kit-freshness reads STALE against BomDD's HEAD until it is re-locked, as for any
  kit change.

**Declared at filing — what the stop will not tell:**
- **Who ruled.** The trailer and the `Sources read` section are written by whoever commits. E13 stops the unattributed and careless edit;
  it does not show that a human ruled (the same class as E05's accept trailer and E11's trust boundary).
- **Whether the sources were read, or read in the right order.** T3 counts citations of the touched files; the higher sources and the
  quality of the reading are not measured (the C16/C17 class: presence, not quality).
- **Whether the change is right.** E13 does not read the change.
- **Before the design release** nothing is checked, and a product that never sets the field is never checked.
- The committer can remove the field, move `since` forward, or remove the hook — each a profile or equipment change that E08 records in
  the diff (the trust boundary of the profile's known limits).

## 3. Acceptance (conditions; frozen at filing)

required_gates: [V1, V2, V3, V4, V5]

**Gated:** V1-V5. **Not a closing condition:** V6.

- **V1 — real history, replayed in a throwaway product.** In a product made by `bomdd-init.py` with process-core, the field set
  (`since` = a commit standing for `bom-v4`, `paths` = the four files and `bomdd/reports/adr/`), each row of section 0's table is
  committed with that commit's ruled files copied from MoviePad-Remake and the register state of its parent recreated:
  - `0b50020`'s change, no trailer, no open ECO → **refused**, E13 names `20-spec.md` and `30-ebom.yaml`;
  - `b06a5bf`'s change in the commit that files ECO-003 (trailer `BomDD-ECO-Ruling: ECO-003`) → **refused** (not open at HEAD);
  - the same change in the next commit, ECO-003 staged at HEAD, its order citing `bomdd/20-spec.md:<line>` → **allowed**;
  - `f4861e8`'s ADR change in ECO-005's filing commit → **refused**; in the next commit with the trailer and a citation of each of
    `ADR-002.md` and `ADR-006.md` → **allowed**;
  - `31273e7`'s change with the trailer and an order citing `20-spec.md` and `30-ebom.yaml` but not `31-kbom.yaml` → **refused**, E13
    names `31-kbom.yaml` with count 0; with all three cited → **allowed**;
  - `bbce170`'s spec change committed before `since` → **allowed** (Phase 3 is not checked).
- **V2 — the arms in the qualification.** Nested in process-qualification's run, each shown with its verdict line:
  - no trailer → refused; a trailer naming an id absent from the register → refused; naming an applied (closed) ECO → refused;
  - the order missing, or without a `Sources read` section → refused;
  - a ruled file deleted, and a ruled file renamed out of a ruled path, without a trailer → refused;
  - `since` that does not resolve → refused; the profile without `ruled_layer` → no E13 (the `0b50020` arm passes);
  - a commit touching no ruled path → no E13;
  - the history version: the `0b50020` arm committed with `--no-verify` → reported by the full mode as `history:<sha>` E13;
  - **known-bad of the gate itself:** a validator with E13's refusal disabled lets the `0b50020` arm through — shown, then restored.
- **V3 — nothing else moves.** The qualification's existing arms give the same verdicts as before the change (the run's line counts
  compared before and after); E13 never fires in a product without the field.
- **V4 — the text.** §4.5's bracket names E13 as the stop and T3 as the measure; §7 names the field; the template has the
  `Sources read` section pointing to §4.5 without copying the authority order.
- **V5 — the gate.** self-conformance exits 0, observed before each commit of this ECO; CI green for each pushed commit.
- **V6 (not a closing condition).** When a product sets the field in its distribution ECO: E13's full mode on that product's history after
  its release, the count of commits it reports, each read. For MoviePad-Remake section 0 predicts all 6 (none carries a trailer);
  3 of them would be refused even with one (`0b50020`: no open ECO; `b06a5bf`, `f4861e8`: filed in the same commit).

Conditions are frozen at filing; results go to the closing section.

## /preflight receipt (start path: manual — the user's "1:A 2:A 3:A" read as the start artifact)

- **Classification**: filing of a decided change (the user's ruling, item 2; filing only).
- **Baseline `9cc108b`**: **confirmed** (HEAD, the commit recording ECO-118's amendment and the item-1 plan; tree clean before this filing).
- **Next number 119**: **confirmed** (the last register entry and the last order are ECO-118; no `60-change-order-eco-119.md`).
- **process-core's E01, E05, E08 and the commit-msg mode**: **confirmed** by reading `process-validator.py` (`check_protected`,
  `check_equipment`, the trailer reading) at `9cc108b`.
- **No check already protecting the ruled layer**: **confirmed** (`protected_paths: [src/, test/, tests/]`; `CORE_PROTECTED` lists the
  equipment only).
- **ECO in progress on the same files**: **ECO-118** (filed, amended; changes `process-validator.py`, the profile and the
  qualification) — answered by the manufacture order in section 1.
- **Start decision**: **PROCEED_WITH_LIMITS** (filing only; manufacture waits for the start instruction and for ECO-118).

## Converge receipt (the stop's form; start path: self-triggered at filing, DoD fixed first)

- DoD: the stop refuses an unattributed change to the ruled layer after the release; it does not refuse Phase 3; it ties the change to a
  filed ECO and to that ECO's citation of the touched files; it changes no installed product until that product opts in; it is not
  silently bypassed.
- Round 1 (5 findings): (a) E01's "any open ECO" passes an unrelated ECO → a trailer naming the ECO; (b) a trailer alone names any
  filed id → the named ECO must be open at HEAD and its order must cite the touched files; (c) a same-commit filing makes the decision and
  the change one commit → file-first, refusing `b06a5bf`'s and `f4861e8`'s pattern; (d) `--no-verify` skips the hook → the history
  version (T4); (e) a deletion or a rename out of a ruled path escapes a name-only diff → `--no-renames`, both paths counted.
- Round 2 (1 new finding): the reference-only change of `0b50020` — refuse it or exclude fields? Excluding makes the reach depend on a list
  of harmless keys → refuse at file level and record the cost (section 1).
- Round 3 (0 new findings): the answers checked against the DoD and the six commits of section 0.
- 未収束事項: none in the form. Outside it and declared (section 2): who ruled, whether the sources were read, the trust boundary.
