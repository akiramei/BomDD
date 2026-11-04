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

## 4. Manufacture and the measurements before commit (2026-10-29, the user's "ECO-119を製造")

**Start.** Baseline `42a6158` (ECO-118 verified; CI success, run 40882182448); the tree clean. Start check (/preflight, manual): the order's
sections 1-3 read; ECO-118, which shares `process-validator.py`, its profile and its qualification, is verified (the manufacture order of
section 1 holds); no other ECO in progress on the affected files → PROCEED. Producer EQ-004 (`claude-opus-5-5`, self-reported).

**What was changed** (`git diff --stat 42a6158`, the evidence folder apart):
- `method/templates/process-core/tools/process-validator.py`: E13 in the docstring and REASONS; `ruled_layer` and `trailers.ruling` in
  `validate_profile`; the pure core `ruled_layer_issues` (shared by both layers) with `ruled_paths_touched`, `sources_read_section`,
  `citation_counts`; the first layer `check_ruled_layer` (commit-msg mode) with `since_applies` and `staged_paths_no_renames`; the second
  layer in `scan_history` (T4); 13 selftest arms.
- `method/templates/process-core/process-profile.yaml`: the commented `ruled_layer` block and the `trailers.ruling` note.
- `method/templates/process-core/tools/process-qualification.py`: N23a-o and their docstring lines.
- `method/templates/60-change-order.md`: the `Sources read` section (after section 1), pointing to §4.5's authority order.
- `method/bomdd-playbook-v1.md`: §4.5's enforcement bracket names E13 and its count (T5); §7's design-release sentence names the field.
- `bomdd-init.py` unchanged (the scaffold renders the template; the field stays commented).

**Derived-layer choices** (decided and reported, ECO-106):
- D1 — **the first commit is never after the release**: no HEAD → no E13. Without it a scaffold's first commit, which carries the
  template BOM, would be refused when the field is set and `since` does not resolve yet.
- D2 — **`since` unresolvable**: the first layer refuses only a commit touching a ruled path (it cannot tell whether the release has
  passed); the second layer stops with exit 2 (measurement impossible), as it does for `history_replay_since`.
- D3 — **the trailer is read after removing the editor's comment lines** (`strip_commit_comments` with git's comment candidates and the
  configured characters — ECO-118's R8-2-01 and R8-3-01 lessons applied from the start).
- D4 — **the order** is read from the index first, then HEAD (first layer); in the replay, as it stood at that commit.
- D5 — **`Sources read`** is a markdown heading containing the words, to the next heading of the same or a higher level; a citation is
  `<path>:<line>` or `<path>:<line>-<line>` with a path boundary (`xbomdd/20-spec.md:3` does not count as `bomdd/20-spec.md`).
- D6 — **several ids named**: one that meets every requirement suffices; each failing id's reason is printed.
- D7 — **merges.** The replay counts only a merge's conflict resolutions (`diff-tree --cc`); the branch's own commits are judged
  themselves. The first layer reads the staged diff against HEAD, so a merge bringing ruled changes needs a trailer naming an open ECO
  even when the branch's commits had one (fail-closed; the cost is a trailer on such a merge).
- D8 — **the replay's boundary is `--ancestry-path since..HEAD`** — only descendants of `since`, the first layer's "since is HEAD or an
  ancestor". Found by V1's first run: without it the replay reported three commits made before the release on the main line and merged
  in after it (V1's set-up puts the release tag on a side branch). Kept as V1's known-bad KB2.
- D9 — **the qualification's arms always run** (the sandbox's profile gets `ruled_layer`), unlike E12's, which run only where the
  installed profile has its field: the template leaves `ruled_layer` commented, so a field-gated arm would never run in C11.
- D10 — `trailers.ruling` is optional (the default name is in the code); written, it must be non-empty and differ from fix/accept.
- D11 — V1's product removes `structure_check` in its profile commit (E12 off), so that only E13 is measured: the copied E-BOM sits
  beside the template M-BOM and Control Plan.
- D12 — **an amend** that keeps a ruled change already in HEAD is not seen by the first layer (the staged diff against HEAD does not
  show it); the replay (T4) judges the stored commit. Declared, with `--no-verify`.

**Evidence:** `bomdd/reports/eco-119-ruled-layer/` — `verify119.py` (V1), `verify119_v2v3.py` (V2, V3), outputs in `out/`. MoviePad-Remake
read with git only. `bom-v4` is the tag on `ca9319d`; `5dde98c` (named in section 0) is the G3-pass record right after it; both give the
same six ruled-layer commits after them (`git rev-list --count <x>..HEAD -- <the ruled paths>` = 6 each).

- **V1 — PASS** (`out/v1.txt`), the six commits in their real order (b06a5bf, ec6e549, 0b50020, f4861e8, 31273e7, 79f1791) with each
  parent's register recreated: `bbce170` before `since` → allowed; `b06a5bf` in ECO-003's filing commit → refused ("ECO-003 は親の台帳に
  無い"), filed first then changed → allowed; `ec6e549` (extra) → allowed; `0b50020` with no open ECO → refused, naming `20-spec.md` and
  `30-ebom.yaml`; `f4861e8` in ECO-005's filing commit → refused, in the next commit citing both ADRs → allowed; `31273e7` with
  `31-kbom.yaml` uncited → refused ("引用数 0: 31-kbom.yaml"), all three cited → allowed; `79f1791` with `--no-verify` → the full mode
  reports exactly one E13 (`history:`), no other violation. Known-bad: `check_ruled_layer` disabled → `0b50020` gets through (undone);
  the replay without `--ancestry-path` → 4 E13 lines instead of 1.
- **V2 — PASS** (`out/v2.txt`): a fresh scaffold of this tree, the qualification with `--runs 2` (as C11): disposition PASS, the two
  runs identical, 62 controls; the 15 N23 arms each as stated — before the release not checked (N23a); refused with E13: no trailer,
  an id not in the register, a closed ECO, no order, no `Sources read`, an uncited file (count 0), a deletion, a rename out of a ruled
  path, an unresolvable `since` (N23b-i, n); allowed: an open ECO whose order cites the file, with `-m` and through an editor's comment
  block (N23j, k); no E13 on a commit touching no ruled path (N23l) or without the field (N23o); `--no-verify` reported by the replay as
  exactly one history E13 (N23m — the pre-release branch not counted).
- **V3 — PASS** (`out/v3.txt`): a scaffold of `42a6158` (before) and of this tree (after): the 47 controls present in both have the same
  verdict and the same detail; only the 15 N23 controls are new; nothing only before; no E13 in the before run.
- **V4 — the text**: §4.5's bracket names E13 as the stop and its citation count as the measure, and what it does not stop; §7 names
  `ruled_layer.since`; the template's `Sources read` section points to §4.5 without copying the authority order.
- **V5**: the first self-conformance run on the changed tree failed C11b (the non-default profile: other register path, initial state,
  trailers, protected paths): N23's set-up wrote the initial state as `staged` instead of deriving it from the installed profile (the
  ECO-024 rule the other arms follow). Fixed (`SPEC["initial"]`); the second run exit 0, C11 and C11b 62 controls each. V2's `out/`
  comes from the default profile, which the fix does not change. CI after the push: at closure.
- **V6** (not a closing condition): when a product sets the field.

**Not done here:** the commit's CI, the R8 round, the closure.

**CI on `3d16181`:** success (run 40891374976).

## 4A. R8 round 1 and the rulings on it (2026-10-29 → 2026-11-04)

**R8 round 1: REJECT**, with 3 material and 8 minor findings. The summary is in `bomdd/reports/eco-119-ruled-layer/r8-round-1.md`.
**Rulings:** user, 2026-11-04, "1:A 2:A 3:A 4:A 5:A" on the five points put to them:
1. **Merges.** A merge is judged by its diff from the first parent (the view the first layer has), and its base is the combined register
   of its parents. Cost, as stated in the question: a merge that brings ruled changes needs a trailer naming an ECO that is open there,
   so the ECO is applied after the merge. Option B was rejected: it would accept a merge whose branch commits were each ruled.
2. **`since` form.** `since` is a full commit SHA; the tag goes in a comment.
3. **The replay's start.** The replay starts at the later of `since` and the commit that introduced the field.
4. **Message parity.** A commit is refused when the trailer read with the comment lines removed differs from the trailer read from the
   raw message.
5. **Rounds.** Fix, then R8 round 2. Round 2 is the last: a REJECT stops for the user.

The minor findings (R8-1-02, 05, 06, 07, 08, 11) are fixed without a ruling. With the user's go-ahead came a request to check, before
continuing, that the many commits since the manufacture leave this work valid.

**/preflight receipt (start path: the user's request, "このまま継続して問題ないか事前に確認して", 2026-11-04)**
- **Classification:** continuation. This is an implemented ECO that is being fixed under rulings. The authority for it is this order,
  its register entry and the R8 report.
- **Baseline `2e94683` — confirmed.** HEAD equals `origin/main`. CI success on it (run 41827828764). The tree is clean apart from the R8
  report, which is untracked.
- **Commits after `3d16181`: 59, none in this ECO's scope — confirmed.**
  - The 59 are ECO-120..124 and EXP-20261030-01 .. EXP-20261031-03.
  - `git diff --quiet 3d16181 HEAD` is empty for every path this ECO changes: `method/templates/process-core/`,
    `method/tools/bom-structure-check.py`, `method/tools/self-conformance.py`, `method/templates/60-change-order.md`,
    `method/templates/34-routing.yaml`, this order and the evidence folder.
  - Three files overlap. In `method/bomdd-playbook-v1.md`, ECO-120/124 add to §8 only; this ECO changes §4.5 and §7. `AGENTS.md` and
    the register template get comments about the dwell view. `bomdd/60-change-register.yaml` gets other ECOs' entries; this ECO's
    entry is unchanged since `3d16181`.
- **Current state — confirmed.** The register reads `implemented`. The dwell view (ECO-120) shows this ECO open for 5.9 days with no
  reason recorded. It is not on a DECIDE line: under ECO-124 that line is for items past 14 days.
- **Unresolved items — confirmed** from the R8 report: R8-1-01..11.
- **Other writers — confirmed none.** No other Claude Code session is running in this repository (the app's session list, 2026-11-04).
- **Acceptance target — confirmed.** V1-V5 (section 3), with the conditions changed by the rulings recorded below.
- **Discovered — the closure's diff window.** The window from this ECO's baseline to its fix contains the 59 foreign commits. The window
  check counts only this ECO's commits. Each other commit in the range is shown as belonging to its own ECO or EXP, read from its
  subject. Its paths are not counted against this ECO's `allowed_paths`.
- **Start decision: PROCEED.** Overrides: none.

**Frozen conditions changed by the rulings** (the changes are recorded here; sections 1-3 keep their frozen text):
- **T1, `since`** (ruling 2:A). `since` is the release commit's full SHA (40 or 64 lowercase hex), and the tag goes in a comment.
  `validate_profile` refuses any other form, so a tag name, a short SHA, `HEAD` or upper case make the profile invalid (exit 2).
  Section 2's "moving `since` is a profile change E08 records" is now true: the SHA cannot move without a diff of the profile. In the
  tag form it was false (R8-1-03).
- **T1, `paths`** (R8-1-06). An entry matches the path itself or anything under it, with or without a trailing `/`. This replaces "a
  trailing `/` marks a directory": `bomdd/adr` written without the slash used to match nothing. Backslashes, `.`, `..`, empty segments,
  leading or trailing spaces, absolute paths and drive letters make the profile invalid. In full mode, an entry that matches no file at
  HEAD is printed as a warning; it is measured, not stopped, because a product may create its ADR folder later.
- **T2/T4, the boundary** (rulings 1:A and 3:A; both layers read it the same way, in the class `RuledBoundary`).
  - A parent is **after the boundary** when `since` is that parent or one of its ancestors, and that parent's profile has
    `ruled_layer`.
  - A commit is judged by its diff from its **first parent**, when the first parent is after the boundary. Otherwise it is judged by
    its diff from the first parent, in parent order, that is after the boundary. When no parent is after the boundary, the commit is
    not judged.
  - The base is the parents' combined register (REV-13, as E01 has it).
  - The second rule exists for one form: `main` is merged into a branch forked before the field, and `main` is then fast-forwarded.
    The first parent is the old branch, so a first-parent-only rule would skip the change the branch brings in. For every other merge
    the base is the first parent, as ruled.
  - In that form HEAD's profile has no field. The first layer then takes the field from the other parent's profile. NEW-02's "HEAD's
    profile governs" is not weakened by this, since the addition can only add a refusal.
  - The replay's candidates are the descendants of `since` (`--ancestry-path`): non-merges that touch a ruled path, and every merge
    (the path-limited listing's merge simplification is not relied on). Paths are read with `-z` (R8-1-02).
  - `since` not on HEAD's line is refused in the first layer and gives exit 2 in the replay. This covers the case where `since` has
    moved off the line (R8-1-03).
- **T2, message parity** (ruling 4:A). The trailer is read twice, from the message as the hook receives it and with the comment lines
  removed. When the two readings differ, the commit is refused, and the refusal says to use `-m` or `-F <file>` with no `#` line after
  the trailer.
  - Two forms are refused: an editor's comment block (git stores the stripped text, the hook receives it raw) and an `-m "# note"`
    paragraph after the trailer (git keeps it).
  - A commit that passes the hook therefore reads the same in the replay, whatever cleanup mode git applies.

**Earlier derived choices of section 4 that are replaced:**
- **D3** — the comment-stripped reading is kept, and the parity check is added (above).
- **D6** — every id the trailer names must exist in the parent register; then one id that is open and whose order cites the touched
  files suffices. The full mode's E07 reads the ruling trailer whenever `ruled_layer` is set, whether or not `trailers.ruling` names
  it (R8-1-07). Before this, the two disagreed when the name was set.
- **D7** — replaced by the boundary above. A merge of a branch that changed the ruled layer needs a trailer naming an ECO that is open
  in the combined register, so that ECO is applied after the merge. This is ruling 1:A's stated cost, and R8-1-09's account of it is
  accepted as written: a branch whose ECO was filed, used and applied on the branch cannot be merged under that ECO's name.
- **D8** — the `--ancestry-path` boundary is kept for the candidates. Its round-1 justification depended on V1's side-branch release
  and no longer applies: V1 and N23 now put the release on main.
- **D12** — extended (R8-1-08). An amend of an ECO's filing commit that adds a ruled change under that ECO's trailer passes the first
  layer, because HEAD's register already has the ECO open. The replay judges the stored commit and reports it. Declared with
  `--no-verify`.

**New derived choices (decided and reported, ECO-106):**
- D13 — `order_ref` must be a repository-relative path in the `paths` form. Otherwise the reason is "order_ref がリポ相対のパスでない"
  (R8-1-11: `/Sources read` used to be read as git's `<rev>:/<text>` search).
- D14 — the change-order template's example uses `<line>`, which the count does not match. An untouched template therefore cites
  nothing (R8-1-05).
- D15 — the qualification's trailer name comes from the installed profile (`trailers.ruling`, else the default), as ECO-024 requires
  (R8-1-07).

## 4B. Round 2 — the fix and the measurements before commit (2026-11-04)

**What was changed** (from `3d16181`):
- `process-validator.py`:
  - `validate_profile`: `since` must be a full SHA; `paths` entries must have the `repo_rel_path_ok` form.
  - Shared functions: `ruled_paths_touched` matches a path or anything under it; `order_ref_of` checks `order_ref` (D13);
    `ruled_layer_issues` requires every named id to exist (D6).
  - New: `trailer_parity_issue` (ruling 4:A), `merge_heads`, `RuledBoundary`, `ruled_profile_of_merge`, `staged_paths_from`.
  - The first layer `check_ruled_layer` now takes the raw and the stripped message.
  - The replay is rewritten on the boundary, with `-z`. In full mode, E07 reads the ruling trailer, and a `paths` entry that
    matches nothing is printed as a warning.
  - Selftest: 98 arms, all PASS.
- `process-qualification.py`: N23 is rebuilt. The release is on main and the field is added later as a SHA. There are 23 controls
  (N23a-w). N23m compares the exact set of commits the replay reports with the expected set. The round-1 check,
  `"sneaked" not in`, could never fail (R8-1-11).
- `process-profile.yaml`: the comment gives the SHA form and says the replay starts after the field. Round 1's "moving `since` is a
  profile change" is now true.
- `60-change-order.md`: the example cites with `<line>` (D14).
- The playbook: §4.5's bracket says SHA, from the field's commit, merges by the first parent with the ECO applied after the merge,
  and `-m`/`-F`. §7's clause says the tag's commit SHA, with the tag in a comment.
- Evidence: `verify119.py` (V1) puts the release on main, adds the field in a later commit, and gets two new arms (below).

**Evidence notes (R8-1-11):**
- V2's frozen "known-bad of the gate itself" (section 3) has been carried by V1 since round 1: `check_ruled_layer` disabled → the
  `0b50020` arm gets through. Round 1 did not record this move from N23 to V1, and it is recorded here. The qualification has no arm
  that edits its own installed validator.
- V1's KB2 changes meaning. In round 1 it removed `--ancestry-path`, which mattered only because V1 put the release on a side branch.
  It now removes the field gate (`has_field` returns True): the change made after the release and before the field is then reported
  too.

**V1 — PASS** (`out/v1.txt`; the six commits of section 0 in their real order):
- Unchanged from round 1: every arm's verdict, and the history E13 for `79f1791` as the only E13.
- New arm: a ruled change after the release and before the field is allowed (ruling 3:A).
- New KB2: without the field gate, the replay reports 2 E13.
- The refusals now read "名指す ID はすべて台帳に実在すること" where round 1 read "親の台帳に無い" (D6).

**V2 — PASS** (`out/v2.txt`; a fresh scaffold of this tree, the qualification with `--runs 2`; disposition PASS, the two runs
identical, 70 controls):
- The 23 N23 controls, each with its verdict line.
- Allowed (no E13):
  - before the release, and after the release but before the field (N23a, p);
  - an open ECO whose order cites the file (N23j);
  - a commit touching no ruled path (N23l);
  - no field (N23o).
- Refused with E13:
  - no trailer; an id not in the register, also next to one that qualifies (N23b, c, c2);
  - a closed ECO; no order; no `Sources read` section; a file cited 0 times; a deletion; a rename out of a ruled path (N23d-i);
  - an editor's comment block, and an `-m "# note"` paragraph after the trailer (N23k, q — ruling 4:A);
  - merges (ruling 1:A): a branch forked before the release (N23r); `main` merged into a branch without the field (N23s); a
    post-release branch, refused without a trailer and allowed with an open ECO's trailer (N23t);
  - `since` that does not resolve, and `since` off HEAD's line (N23n, v).
- Reported by the replay as exactly the expected set of commits (N23m): a `--no-verify` change, a non-ASCII path, a pre-release
  branch's merge, and a fast-forward to a merge of `main` into a branch without the field. The commit before the field and the
  correctly ruled commits are not reported.
- Exit 2 for a `since` written as a tag name (N23w).
- **The first run had one FAIL, N23v.** That arm set `since` to the `early` branch's tip, which N23m had already merged into main, so
  the commit was on HEAD's line and the arm could not fail. The arm now uses a commit that exists only on a side branch. The validator
  did not change.
- The script's expected count went from 15 to 23. The second run reported "V2: FAIL" only because it still expected 15. The verdict
  line comes from the third run.

**V3 — PASS** (`out/v3.txt`): a scaffold of `42a6158` (before the ECO, as in round 1) and of this tree (after). The 47 controls present in
both have the same verdict and the same detail. Only the 23 N23 controls are new; no control is only in "before"; there is no E13 in
the before run.

**V5:**
- self-conformance exit 0 on the tree with the N23v fix: C11 and C11b 70 controls each, both runs identical, 703.8 s. The order and
  the evidence files were changed after that run.
- Final run before the commit: exit 0, C11 and C11b 70 controls each, 533.8 s. The commit `00f3ae2` was pushed; its CI succeeded
  (run 41843989344).

## 4C. R8 round 2 and the rulings on it (2026-11-04 → 2026-11-05)

**R8 round 2: REJECT**, with 3 material and 4 minor findings. The summary is in `bomdd/reports/eco-119-ruled-layer/r8-round-2.md`.
All of round 1's findings are closed, or closed with a declared limit. Under ruling 5:A the work stopped for the user.

**Rulings:** user, 2026-11-05, "推奨どおり", on the three points put to them, i.e. "1:A 2:A 3:A".
1. **The field dropped through a merge** (R8-2-01). E13 itself refuses a merge whose result drops or changes the field held by the
   parent it judges from. E08 is not changed. Dropping the field with `--no-verify` is not stopped, and this is declared.
2. **The boundary** (R8-2-02). As ruled in 3:A, the replay judges from the later of `since` and the first appearance of the field.
   A ruled change made between a removal of the field and its re-addition is therefore reported by the replay. The first layer
   cannot judge such a change, because HEAD's profile then has no field; this is declared.
3. **Rounds.** Fix, then run round 3 narrowed to the fixed parts and the seven findings. Round 3 is the last: a REJECT stops for the
   user.

**Premises stated with the question and fixed without a ruling:**
- R8-2-03: a parent profile that does not parse.
- R8-2-04: the register of an octopus merge.
- R8-2-05: the values read from the parent the commit is judged from.
- R8-2-06: the gaps in the records.
- R8-2-07: `:` in a path.
- Declared, not changed: cherry-pick, revert and rebase run no commit-msg hook (the replay judges them). After the field, a branch can
  reach main without a merge trailer by a sync merge followed by a fast-forward, and each of its commits is still judged.

## 4D. Round 3 — the fix and the measurements before commit (2026-11-05)

**What was changed** (from `00f3ae2`):
- `process-validator.py`:
  - **R8-2-01 (ruling 1:A, narrowed by ruling B below).** In a merge, the first layer refuses when the index's `ruled_layer`
    differs from the field of every parent after the boundary ("merge の結果が ruled_layer を落とす/変える — 結果の欄が、境界の
    後にあるどの親 … の欄とも違う"). A merge that keeps the field of one of those parents is allowed. The field itself is changed in
    a commit of its own, which goes through E08. E08 is unchanged.
  - **R8-2-02 (ruling 2:A).** `RuledBoundary` now takes the heads it reads from. A parent is after the boundary when `since` is that
    parent or one of its ancestors, and that parent or one of its ancestors has a profile with the field. The first commit with the
    field is found by `rev-list --full-history -- <profile>`, and its descendants by `--ancestry-path`. A commit made while the
    field was removed therefore stays after the boundary. The replay judges it. The first layer cannot, because HEAD's profile then
    has no field (declared).
  - **R8-2-03.** A profile that does not parse, or is empty, is not counted as a first appearance of the field. It does not end the
    boundary either: if the field appeared earlier, the commits after the broken profile are judged.
  - **R8-2-04.** In a merge, E13 combines the registers of every parent: HEAD and every line of MERGE_HEAD. This is the same base as
    the replay's. E01's `parent_registers` is not changed (below).
  - **R8-2-05.** The `paths` and the trailer name are read from the profile of the parent the commit is judged from. If that profile's
    field is not well formed, the caller's values are used. Both layers do this. The replay's path filter is the union of every
    profile version's `paths`, so a commit touching only an entry that was later removed is still listed.
  - **R8-2-07.** `repo_rel_path_ok` refuses `:`. This covers `paths` and `order_ref`.
  - The E13 docstring now declares what the layers do not stop:
    - cherry-pick, revert and rebase, which the replay catches;
    - the commit that adds the field, whose own ruled change is not judged, as E01's installation commit is not;
    - dropping the field with `--no-verify`, after which both layers are off.
  - Selftest: 99 arms, all PASS. New arms: `:` in `paths` and in `order_ref`.
- `process-qualification.py`: eight arms, 31 N23 controls in all.
  - N23x: `main` merged with `-s ours` into a branch forked before the field. Refused with "ruled_layer を落とす".
  - N23x2 (ruling B): the trunk changes the field in its own commit, then is merged into a working branch. Allowed.
  - N23x3 (ruling B): a branch changes the field in its own commit, then is merged into the trunk. Allowed.
  - N23x4 (ruling B): a merge whose resolution writes a field held by neither parent. Refused with "ruled_layer を変える".
  - These three run on a `trunk` branch cut from main, so main's line, which the later arms replay, is unchanged.
  - N23u: an octopus merge naming an ECO that is applied on its third parent. Refused with "open でない".
  - N23y: the field removed, a ruled change, the field restored. The replay reports the change.
  - N23z: a profile that does not parse, then a `--no-verify` ruled change. The replay reports it.
  - N23z2: `paths` extended in a commit that also creates a file under the new entry. Neither layer reports it. The only new
    reports are N23y's and N23z's.
  - The docstrings now say "N23a〜z2", 31 arms (R8-2-06d).
- The playbook, §4.5's E13 sentence:
  - the merge's base is the combined register of every parent;
  - the field itself is changed in a commit of its own (a merge whose result holds a field that no parent after the boundary
    holds is refused);
  - the replay judges a removal window, and catches cherry-pick, revert and rebase;
  - 止めないもの adds the field's own commit and dropping the field with `--no-verify`.
- Evidence:
  - `verify119.py`: KB2 now patches `after_boundary` to `after_since` (`has_field` no longer exists). Its meaning is unchanged: the
    replay without the field gate.
  - `verify119_v2v3.py` expects 31 N23 controls.
  - New: `verify119_r3kb.py`, with `out/r3kb.txt` (against `00f3ae2`) and `out/r3kb-letter.txt` (`--letter`).

**Ruling on the round-3 draft:** user, 2026-11-05, "B: 範囲を絞る".
- The draft implemented ruling 1:A's text: refuse a merge whose result differs from the base parent's field. A throwaway product
  showed that this also refused two merges that follow the error's own advice:
  - the trunk changes the field in its own commit and is merged into a working branch;
  - a branch changes the field in its own commit and is merged into the trunk.
- This cost had not been shown with the round-2 question, so it was put back to the user before round 3.
- Ruling B: refuse only when the result's field differs from the field of every parent after the boundary.
- The attacks of R8-2-01 stay refused:
  - `-s ours` into a branch forked before the field (N23x);
  - `--no-commit`, then the old profile restored (the same test);
  - a resolution that writes a field no parent holds (N23x4).
- Residual, declared: a branch drops the field in its own commit, main is merged into that branch, and main fast-forwards to it.
  The drop itself is an equipment change, which E08 controls.

**The choice made for R8-2-03.** R8 offered two fixes: judge the commit, or exit 2 (unmeasurable). The fix takes the first. Exit 2
would leave a product permanently red once a broken profile sits in its history, because history cannot be rewritten. Judging the
following commits closes the fail-open just as well. The user is told of this choice with this round.

**Declared limits (records only — R8-2-06):**
- (a) Cherry-pick, revert and rebase run no commit-msg hook. The replay judges what they produce.
- (b) The commit that adds the field is not judged for a ruled change it carries.
- (c) Ruling 1:A's cost applies in both directions:
  - a merge cannot launder an unruled change into main;
  - a merge without a trailer is refused even when each branch commit was ruled.
  For a branch forked after the field, a sync merge of main into the branch followed by a fast-forward reaches B's outcome, and each
  branch commit is still judged by the first layer when made and by the replay.
- E01's octopus gap is not closed: its `parent_registers` combines HEAD with the first MERGE_HEAD line only. It is outside ECO-119's
  scope, so it is left as a candidate for a separate ECO.
- R8-2-06(d): 4B says the refusals "now read 名指す ID はすべて台帳に実在すること". That is the text when a named id is missing. For a
  closed ECO the refusal still reads "open でない" (N23d, N23u).

**Known-bad of the new arms:**
- `out/r3kb.txt`: this tree's qualification, run against the round-2 validator (`00f3ae2`), FAILs exactly N23u, N23x, N23x4, N23y,
  N23z and N23z2. The other 25 N23 controls PASS, including N23x2 and N23x3, which round 2 also allowed. So each refusing or
  reporting arm tests something round 2 did not do.
- `out/r3kb-letter.txt`: this tree's validator with ruling B's test put back to 1:A's text. Exactly N23x2 and N23x3 FAIL. So the two
  allowing arms detect the over-refusal that ruling B removed.

**V1 — PASS** (`out/v1.txt`): every arm has the same verdict as in round 2. KB "check_ruled_layer disabled" lets the `0b50020` arm
through. KB2 (no field gate) reports 2 E13.

**V2 — PASS** (`out/v2.txt`; a fresh scaffold of this tree, `--runs 2`): disposition PASS, the two runs identical, 78 controls. All 31
N23 controls PASS.

**V3 — PASS** (`out/v3.txt`; before = a scaffold of `42a6158`): the 47 controls present in both runs have the same verdict and detail.
Only the 31 N23 controls are new. No control is only in "before", and the before run has no E13.

A V2/V3 run started before ruling B was stopped part-way, and its leftover temporary folder was removed. The lines above come from
the run made after B.

**V5:** self-conformance exit 0 on the tree of `1cd891b` (C11 and C11b 78 controls each, both runs identical, 770.8 s). The commit
`1cd891b` was pushed; its CI succeeded (run 41874648644).

## 4E. R8 round 3 (2026-11-05)

**R8 round 3: REJECT**, with 2 material and 6 minor findings. The summary is in `bomdd/reports/eco-119-ruled-layer/r8-round-3.md`.
Under ruling 3:A this was the last round, so the work stopped for the user.
- The two material findings are R8-3-01 (unchecked entries in the replay's path filter) and R8-3-02 (a narrowing window).
- Both come from round 3's change to which `paths` a commit is judged with.
- The inspector broke the read-only rule once and undid it; this is disclosed in the report. BomDD was left at `1cd891b`, clean.

**Ruling:** user, 2026-11-05, "A: 一本化+第4回". Remove the common cause, then run a round 4 narrowed to round 3's eight findings and
the parts changed for them.

**The common cause.** R8-3-01, 02 and 06 come from one place. Round 3 decided which `paths` a commit is judged with in three different
ways:
- the replay's path filter took the union of every version's entries, unchecked;
- the judgment took the base parent's entries;
- in a removal window, the judgment fell back to HEAD's entries.

## 4F. Round 4 — the fix and the measurements before commit (2026-11-05)

**What was changed** (from `1cd891b`):
- `process-validator.py`, `RuledBoundary`:
  - `entries_at(rev)` keeps only the entries that pass `repo_rel_path_ok`. `:(exclude)…`, `..` and `:` entries are dropped. A version
    with no such entry counts as having no well-formed field.
  - `values_for(base, HEAD's profile)` is the only place that decides the `paths` and the trailer name. Both layers use it.
    - The `paths` are the base parent's entries, together with HEAD's entries that some version at or before the base parent held.
    - If the base parent has no well-formed field, its entries come from the nearest well-formed version on the first-parent line.
    - The trailer name comes from that same version, or from HEAD if there is none.
    - Effects:
      - a narrowing window is judged by the replay, as a removal window is (R8-3-02);
      - a removal window is judged with the field as it was before the removal (R8-3-06);
      - an extended entry does not judge commits made before the extension (R8-2-05 kept).
  - `held_at(entry)` is the set of commits whose own profile, or an ancestor's, held the entry. It is computed like the field's
    boundary.
  - `paths_ever()` holds well-formed entries only. The replay passes them to git with `--literal-pathspecs` (R8-3-01).
  - `values_at` is removed.
- `check_ruled_layer`:
  - Fast path (R8-3-07). For a non-merge commit that touches none of HEAD's ruled paths, it returns before the boundary walk. The
    result is the same, because for a non-merge commit `values_for(HEAD)` is HEAD's entries, which `validate_profile` has already
    checked.
  - Merges still take the full path.
- The E13 docstring and playbook §4.5 (R8-3-03, 04, 05):
  - the merge field refusal is first-layer only, and the replay does not repeat it;
  - changing or dropping the field with `--no-verify` is not stopped, merge or not;
  - the first layer does not judge a removal or narrowing window, which the replay judges;
  - a merge that keeps the field of a parent whose own commit dropped or changed it is allowed, in either direction;
  - B's cost: two branches that each extended `paths` cannot be merged with the union; merge with one side's field, then add the
    other's entries in a commit of its own.
- `process-qualification.py`: N23u's octopus merge now carries the accept trailer (R8-3-08). Four arms are added, 35 N23 controls in
  all. Each new arm is judged by its own validate run, so a failing arm (an exit 2, say) cannot hide another arm's result.
  - N23z4 (R8-3-02): `paths` narrowed, a spec change without a trailer, `paths` restored. The replay reports exactly that commit.
  - N23z5 (R8-3-06): the field removed, a file created under an entry added later, the field restored with that entry. No new
    report.
  - N23z3 (R8-3-01): a side branch adds `:(exclude)bomdd` and is merged into main with `-s ours`; there is a `--no-verify` change
    before and after. Both are reported, and no earlier report disappears.
  - N23z3b: the same with `../outside`. Not unmeasurable (no exit 2), and both changes are reported.
- Evidence:
  - `verify119.py` KB2 now removes both field gates: `after_boundary` and `values_for`'s "held at or before the base parent".
  - `verify119_r3kb.py` takes `00f3ae2`, `1cd891b` or `--letter`, each with its own expected set.
  - `verify119_v2v3.py` expects 35 N23 controls.

**Known-bad of the new arms:**
- `out/r4kb.txt` (against round 3's `1cd891b`): exactly N23z3, N23z3b, N23z4 and N23z5 FAIL. Each fails in its own validate run:
  - N23z4: the narrowing-window commit is not reported;
  - N23z5: the window commit is reported (a permanent red);
  - N23z3: every earlier report disappears (`:(exclude)`);
  - N23z3b: exit 2 (`../outside`).
- `out/r3kb.txt` (against round 2's `00f3ae2`): exactly N23u, N23x, N23x4, N23y, N23z and N23z2 FAIL.
  - N23u now fails by passing (exit 0), not by a different reason text. With the accept trailer, E05 no longer refuses it (R8-3-08).
  - N23x still tells round 2 from round 3 only by its reason text: round 2 also refuses that merge with E13, for a missing trailer
    on the diff from main. This is declared, not changed.
- `out/r3kb-letter.txt` (1:A's letter in place of B): exactly N23x2 and N23x3 FAIL.

**V1 — PASS** (`out/v1.txt`). The first rerun failed KB2 with 1 E13, because KB2 removed only `after_boundary`, and `values_for` also
gives no paths before the field. KB2 now removes both. Its second rerun gave 0 E13: the replacement had put a comment in the middle of
a line, so the patched validator did not compile. That was fixed in the script. The third rerun is the recorded PASS: 2 E13.

**V2 — PASS** (`out/v2.txt`): disposition PASS, the two runs identical, 82 controls; all 35 N23 controls PASS.

**V3 — PASS** (`out/v3.txt`; before = `42a6158`): the 47 controls in both runs have the same verdict and detail. Only the 35 N23
controls are new.

The known-bad runs and V2/V3 were made before the last edits to the E13 docstring, and those edits change comments only. The selftest
(99 PASS) and self-conformance's C11 ran on the final tree.

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
