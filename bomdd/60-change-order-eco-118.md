# Change Order — ECO-118 (the G3 structure check A1 and the part-standard coverage check C1 become a kit tool, run at G3 and on every ECO that changes 30/32/33)

> Ruling: user, 2026-10-29, "1:A 2:A", on the two decisions of EXP-20261029-01 (`bomdd/reports/exp-20261029-01/results.md`):
> - 1 = whether A1 (rules 1-6) and C1 become a kit tool now or wait for OBS-20261029-02's second instance: **A** (now). This order;
> - 2 = whether MoviePad-Remake's A1 violations get a product ECO: **A** (yes). Filed in that repository as its ECO-006; not part of this order.
>
> **Filing only.** Manufacture waits for the user's start instruction (ECO-106: the start-wait after filing is unchanged).
> Distribution to the products is a separate ECO (the ECO-108 → ECO-109 form). The three copies of an authority recorded as
> OBS-20261029-03 are not part of this order (the user's message: a structural problem of their own).
> Records are English-primary.

## Equipment

- Filing: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- Producer: EQ-004.
- Independent inspection: one R8 round is planned before acceptance (a new instrument; the memory of ECO-148: the receiving tool broke twice on real files that four design rounds had not used). The user may change this at the start instruction.

## 0. Measurement (basis of the filing)

The experiment's record is `bomdd/reports/exp-20261029-01/` (definitions fixed before counting, the classifiers' outputs, `results.md`).

- **A1 and C1 are written, not run.** Playbook §4.6 (G3) says the orchestrating AI re-checks §4.5's C1 and the A1 structure resolution (rules 1-7) before the dry run, reading the E-BOM, M-BOM and Control Plan only. No tool in `method/tools/` or `method/templates/` implements either (grep for `part_standard`, `ruled_ref`, `part_standard_refs`, 2026-10-29: hits only in templates' comments and in the playbook).
- **The first mechanical run** (`bomdd/reports/exp-20261029-01/a1_check.py`, 115 lines, rules 1-6, reads with `git show`, always exits 0):
  - MoviePad-Remake `d3683d6`: rules 1, 2, 3, 6 — 0 failures; **rule 4 — 6; rule 5 — 6**;
  - MoviePad-Remake `64912a4` (the first M-BOM, whose commit says "A1 structure checked" and names four checks): 13 and 14.
  - These passed three G3 rounds, five ECOs and two R8 rounds.
- **C1 on MoviePad-Remake `d3683d6`** (a 30-line reading aid in the filer's scratch space, not kept): 11 `provides` items, 0 `part_standard_refs` naming a missing item, 0 `provides` items not named by a row in their unit's `acceptance_refs`.
- **What the run does not show.** Rules 1, 2, 3 and 6 and both C1 checks found nothing on the only product with part standards, so there is **no positive control for them** yet: a tool that never fails them would have given the same output. The script's rule 4 checks the direct case only (a `PS-` of a unit with E items); the relay case of §4.5 P4 (through a unit without `ebom_refs`) is not implemented. Rule 7 is not implemented.
- **Population in the other products** (grep `part_standard:` in `bomdd/32-mbom.yaml`, 2026-10-29): ViewPrism2 0, ViewTube 0, TimetableAdv 0; MoviePad-Remake 8 of 8 units. By §4.6's lazy rule, a product without part standards fails nothing — which an instrument must report as "nothing to check", not as a pass (playbook §4.4; the type-④ lesson of ECO-054/060).

## 1. Change request (frozen at filing)

**T1 — a kit tool `method/tools/bom-structure-check.py`.** It ships in every kit by `bomdd-init.py`'s copy of `method/tools/` (no change to the copier).
- **Reads** `bomdd/30-ebom.yaml`, `bomdd/32-mbom.yaml` and `bomdd/33-control-plan.yaml` from a product root given by `--root` (default `.`), from the working tree; `--rev <commit>` reads the same three files with `git show` instead. Strict YAML (duplicate keys refused). Nothing else is read (§4.6: "E-BOM, M-BOM and Control Plan only").
- **Applies** §4.6's A1 rules 1-6 to the units and items each rule names (rules 1, 3, 4, 6 to units with `part_standard`; rule 2 to every `IF-`; rule 5 to every E-BOM `interfaces.requires` whose consumer is realised by a unit with `part_standard`), leaving out retired E items (`lineage.superseded_by`) and `mbom.retired_units`. Rule 4 includes the relay case of §4.5 P4. Also the id form of §4.5 P1 (`PS-<UNIT>-Pnn` / `-Rnn`, unique within the unit).
- **Applies** §4.5's C1 machine part: every `part_standard_refs` id names an existing `provides` item; every `provides` item is named by at least one row listed in its unit's `acceptance_refs`. Whether a row *measures* the item stays a judgment (§4.5 limit) and is not claimed.
- **Prints** one line per finding (`[A1-<rule>]` / `[C1-<a|b>]` / `[P1-id]`, the unit or item, the target, why), then one population line — units with `part_standard`, `IF-` count, E `requires` checked, `provides` items, Control Plan rows read — and one verdict line:
  - `PASS` = every rule ran on a non-empty population and found nothing;
  - `FAIL` = at least one finding;
  - `NOT-APPLICABLE` = no unit has `part_standard` and no E `requires` falls under rule 5 (the lazy rule; it says what was not checked);
  - `UNMEASURABLE` = a file missing, unparsable, or of an unknown shape.
- **Exit codes**: 0 PASS, 1 FAIL, 2 UNMEASURABLE, 3 NOT-APPLICABLE (so a caller cannot read "nothing to check" as a pass by the exit code alone).
- **`--selftest`**: built-in fixtures, each run through the same functions: one known-good BOM, and for each of rules 1-6, the relay case of rule 4, the P1 id form and C1 a and b, at least one mutated copy that must give exactly that finding; plus the empty-population case (exit 3) and a broken file (exit 2). The selftest prints its arm count and fails if any arm differs.
- **Not implemented, declared in the tool's docstring and output:** rule 7 (a provider connected to its consumer as §4.1 says is a reading of meaning); whether a row measures an item; any check on code.

**T2 — where it runs (text).**
- Playbook §4.6, the G3 paragraph: the orchestrating AI runs `bomdd-kit/method/tools/bom-structure-check.py` before the dry run and records its verdict line in the G3 record; a `FAIL` or `UNMEASURABLE` stops G3 as a failed A1 does today; `NOT-APPLICABLE` is recorded as such.
- Playbook §4.6 (the same paragraph): on every ECO that changes `30-ebom.yaml`, `32-mbom.yaml` or `33-control-plan.yaml`, the tool runs on the ECO's last BOM commit before the work order is issued (or before the ECO is accepted, when no work order is issued), and its verdict line goes in the change order.
- Playbook §4.5, the limit paragraph: one clause naming the tool as the machine part of A1 and C1, and that it does not claim rule 7 or a row's measuring.
- Templates: `method/templates/60-change-order.md` gets one line for the verdict when the ECO changes 30/32/33; `method/templates/34-routing.yaml`'s ROUTE-ECO comment gets one line pointing to §4.6.

**Not changed:**
- any existing tool's verdicts (self-conformance gets one check only if T3 is taken at manufacture — see below; no other tool changes);
- the products (distribution is a separate ECO; ViewTube's gate freeze needs the user's exception for any new gate there);
- rule 7 and C1's judgment part;
- OBS-20261029-03's copies.

**T3 (manufacturer's choice at manufacture, recorded and reported per ECO-106):** whether self-conformance gets a check that runs `bom-structure-check.py --selftest` (as C14 runs kit-freshness's). The filer's expectation is yes — a kit tool whose selftest is not run on every push can rot unseen (ECO-096, the same shape) — but the choice and its reason go in §4.

## 2. No-impact prediction (before manufacture; frozen)

- **Diff:** `method/tools/bom-structure-check.py` (new), `method/bomdd-playbook-v1.md` (§4.5 one clause, §4.6 the G3 paragraph), `method/templates/60-change-order.md` (one line), `method/templates/34-routing.yaml` (one comment line), and, if T3 is taken, `method/tools/self-conformance.py` (one check and its docstring line) and `README.md` only if a count it states changes; this order, the register and `bomdd/reports/eco-118-*/`.
- **Verdicts:** every existing self-conformance check gives the same line on the same tree. The kit gains one file, so a product's kit-freshness against BomDD's HEAD reads STALE until that product is re-locked — as for any kit change; its locked kit is untouched.
- **Products:** none changed by this ECO.

**Declared at filing — what the tool will not tell:**
- A `PASS` says the BOM files' structure resolves; it does not say the code honours it (a unit calling another without a `requires` is invisible — §4.5 limit), nor that a row measures what it names.
- On products without part standards it says `NOT-APPLICABLE`, not `PASS`, until a change gives a unit a part standard.

## 3. Acceptance (conditions; frozen at filing)

required_gates: [V1, V2, V3, V4, V5, V7, V8]

**Gated:** V1-V5, and V7, V8 (added by section 1A, 2026-10-29). **Not a closing condition:** V6.

- **V1 — known-bad on real files.**
  - Condition: on MoviePad-Remake `d3683d6` (`--rev`), the tool exits 1 and its A1 findings are rule 4 × 6 and rule 5 × 6, the same unit/target pairs as `a1_check.py`'s output in the experiment, and nothing for rules 1, 2, 3, 6. On `64912a4`, rule 4 × 13 and rule 5 × 14 (or, if the relay case adds findings, each extra one listed and read against P4 in §4).
  - Control: the comparison is shown red on a copy of the expected list with one pair altered.
- **V2 — positive controls for every rule.**
  - Condition: `--selftest` passes, with at least one mutated arm per rule 1-6, the relay case, P1's id form and C1 a and b, each giving exactly its finding, the known-good arm giving `PASS`, the empty arm exit 3 and the broken arm exit 2.
  - Known-bad of the selftest itself: a version with one rule's function disabled (returning no finding) makes the selftest fail — shown for each rule.
- **V3 — the other products, read as they are.**
  - Condition: on ViewPrism2, ViewTube and TimetableAdv at their HEADs (read only, nothing written there), the tool exits 3 (`NOT-APPLICABLE`) with the population line naming 0 units with `part_standard`, or exits 1 with findings each read in §4 — and never exits 0 on an empty population.
- **V4 — the text.**
  - Condition: §4.6 names the tool, its run points (G3; an ECO changing 30/32/33) and what `FAIL`, `UNMEASURABLE` and `NOT-APPLICABLE` do; §4.5's limit names what it does not claim; the two template lines exist and refer to §4.6 without copying the rules.
- **V5 — the gate.**
  - Condition: self-conformance exits 0, observed before each commit of this ECO; CI green for each pushed commit; if T3 is taken, its check's line appears in the CI logs.
- **V6 (not a closing condition).** After MoviePad-Remake's ECO-006 is applied: the tool on its new BOM commit exits 0 — the first known-good real file. Recorded when it happens, in this order or in the distribution ECO.

Conditions are frozen at filing; results go to the closing section.

## 1A. Amendment before manufacture (2026-10-29, the user's "2:A"; supersedes section 1 where they differ)

> Ruling: user, 2026-10-29, "1:A 2:A 3:A" on three decisions taken before new work; 2 = add to ECO-118, before its manufacture, the
> evidence definition (the version checked, the rules applied, the checker's version, the result, the time, recorded by machine) and a
> condition that the step cannot complete without it: **A**. With it, verbatim: "ただし、AIへのプロンプトは、努力目標やお願いに近く、工業的に
> 見ると守られることを祈るようなものです。Hookなど外部で止める、数値化して機械的に判断する、ようなことをしないと、文書だけ膨らんでやっている感
> を出すだけになりかねません。"
> Why: the first M-BOM's commit said "A1 structure checked" and named four checks, not the rules that failed 13 and 14 times there
> (EXP-20261029-01); the filed T2 asked only for "the verdict line" in a record, written by hand. Still not part of this ECO: the
> ruled-layer protection and the authority order (the same ruling's item 1, at review), distribution to the products.

Each addition is labelled by what enforces it: **stop** (refuses), **measure** (a number produced and compared), **none** (text only).

**T1 addition — `--index` (measure).** The tool also reads the three files from the git index (`git show :<path>`), so a commit hook can
check what is being committed rather than the working tree. Exactly one of the working tree (default), `--rev <commit>`, `--index`.

**T4 — a receipt written by the tool itself (measure; no hand-written field).** `--receipt <path>` writes one JSON file on every verdict,
UNMEASURABLE included when the run gets that far:
- `schema`: `bom-structure-receipt/1`;
- `source`: `worktree` | `index` | `rev`, and for `rev` the commit and tree ids (40-hex) resolved by git;
- `inputs`: for each of the three files, its path and the SHA-256 of the bytes read (for `index` and `rev`, the blob as git stores it);
- `tool`: the SHA-256 of the tool's own file and its `RULE_SET` constant (the rules it applies, named by playbook section and rule
  number, e.g. `A1:1-6;A1-4:relay;P1:id;C1:a,b` — the constant changes when the rules implemented change);
- `counts`: findings per rule id, and the population counts of the population line;
- `verdict` and `exit_code`; `utc`: the time the run ended (ISO 8601, `Z`).
The text output is unchanged; the receipt is an extra file. Where a product keeps it (beside the G3 record, in the change order's
evidence) is the product's; T2's records cite the receipt path, not a copied verdict.

**T5 — the stop: process-core's validator re-checks the BOM at the applied transition (stop).**
- A new check `E12 structure-check-failed-at-acceptance` in `method/templates/process-core/tools/process-validator.py`, in the commit-msg
  mode where it already finds the applied transitions (E05): when the staged register moves any ECO to the profile's acceptance state, the
  validator runs the tool with `--index` and **does not read any receipt** (it recomputes).
  - exit 0 (PASS) or 3 (NOT-APPLICABLE) → allowed; the commit's output names the verdict and the population line;
  - exit 1 (FAIL) → refused, the findings printed;
  - exit 2 (UNMEASURABLE), the tool missing, or the tool not runnable → refused (unmeasurable is not a pass).
- Enabled by one profile field `structure_check: <repo-relative path of the tool>` (the scaffold writes
  `bomdd-kit/method/tools/bom-structure-check.py`). A profile without the field has no E12, so an installed product's behaviour does not
  change until its distribution ECO sets the field (E08 governs that profile change). Fail-closed once set.
- Not at every commit: an ECO may commit its BOM changes in steps that are inconsistent in between (MoviePad-Remake ECO-006's `41a5b18`
  carried 2 failures by design while two items waited for a ruling). The stop is where the change is accepted.
- Declared consequence for the distribution ECO (not decided here): a product that sets the field must have the tool in its kit, so the
  field and a kit re-lock go together; ViewTube's gate freeze needs the user's exception for any new gate there.
- **The playbook text (none → stop):** §4.6's sentence of T2 that the verdict is recorded becomes: the tool's receipt is cited; the stop
  at acceptance is E12 where the profile enables it; G3 remains a reading step whose record cites a receipt (no stop at G3: G3 runs
  before process-core's ECOs exist).

**T3 decided by this amendment (no longer the manufacturer's choice):** self-conformance runs the tool's `--selftest` (one check), and
C11's qualification gets the E12 arms of V8 nested in the existing qualification run (no new top-level control group).

**Scope widened** (paths): `method/templates/process-core/tools/process-validator.py`, `method/templates/process-core/process-profile.yaml`
(the field and its comment), `method/tools/bomdd-init.py` only if the scaffold writes the profile field outside the template, the
process-core qualification (`method/templates/process-core/tools/process-qualification.py` and its fixtures) for V8, and
`method/improvements.md` (this ruling's records are written there while the window is open). Not widened: the products, the hooks' shape,
any other validator check.

**Conditions added (frozen with this amendment):**
- **V7 — the receipt is machine-made and true.**
  - Condition: `--rev d3683d6` on MoviePad-Remake writes a receipt whose commit and tree equal `git rev-parse`, whose three input hashes
    equal the blobs' SHA-256, whose tool hash equals the tool file's, whose counts give A1-4 6 and A1-5 6, and whose verdict is FAIL with
    exit code 1; the same for `--index` on a checkout of `3ba3d00` (PASS, 0). Every field is present on the four verdicts (the selftest's
    arms included).
  - Known-bad: a receipt with one input hash altered is told apart by a re-hash (the check script shown red).
- **V8 — the stop refuses and allows as stated** (in a throwaway product made by `bomdd-init.py` with process-core and the field set; the
  three BOM files copied from MoviePad-Remake's history):
  - an applied-transition commit with `d3683d6`'s three files staged → refused, E12, the findings printed;
  - the same with `3ba3d00`'s files → allowed;
  - a template BOM with no `part_standard` → allowed, NOT-APPLICABLE named in the output;
  - a non-applied commit (a staged-state entry, the register untouched) with `41a5b18`'s files → allowed (the stop is not per commit);
  - the tool removed, or a staged 32-mbom.yaml that does not parse → refused (exit 2 / missing is not a pass);
  - the profile without the field → no E12 on the `d3683d6` commit (installed products unchanged).
  - Known-bad of the gate itself: a validator with E12's refusal disabled lets the first arm through — shown, then restored.

The required gates (amended): V1-V5, V7, V8; the machine copy in the register changed with this section.

**Converge receipt (gate placement only; start path: self-triggered at the amendment, DoD fixed first).**
- DoD: the stop refuses an accepted BOM that fails A1/C1 or cannot be measured; it does not refuse an intermediate commit; it changes no
  installed product until that product opts in; it does not trust a hand- or tool-written file.
- Round 1 (4 findings): (a) a receipt-checking gate trusts a file the committer can write → recompute instead; (b) pre-commit on every
  BOM change refuses ECO-006's legitimate intermediate commit → only at the applied transition; (c) "tool missing" passing would make an
  un-relocked product silently ungated → fail-closed once the field is set, no field = no E12; (d) the working tree may differ from what
  is committed → `--index`.
- Round 2 (0 new findings): the four answers checked against the DoD and against ECO-006's history (d3683d6 refused, 41a5b18 not stopped
  as an intermediate commit, 3ba3d00 allowed).
- 未収束事項: none in the placement. Outside it and declared: the committer can remove the field or the hook (the trust boundary of E11);
  NOT-APPLICABLE passes the stop by design (the lazy rule), so a product without part standards is not checked by it.

## /preflight receipt (start path: manual — the user's "1:A 2:A" read as the start artifact)

- **Classification**: filing of a decided change (the user's ruling on the experiment's decision 1; filing only).
- **Baseline `a3b3cc1`**: **confirmed** (HEAD, the commit recording the ruling and OBS-20261029-03; the tree clean apart from this filing's files).
- **Next number 118**: **confirmed** (the last register entry and the last order are ECO-117; no `60-change-order-eco-118.md`).
- **A1 and C1 text at `a3b3cc1`**: **confirmed** (playbook §4.5 "部品規格" and §4.6 G3 read).
- **No tool already implementing A1 or C1**: **confirmed by grep** (section 0).
- **No ECO in progress on the playbook §4.5/§4.6 or the two templates**: **confirmed** (every register entry is verified apart from ECO-079, implemented, which touches neither).
- **Start decision**: **PROCEED_WITH_LIMITS** (filing only; manufacture waits for the start instruction).

No converge loop was run. The change and its scope were decided by the user's ruling; the details in section 1 (the tool's name, its four verdicts and exit codes, the selftest's arms, T3 left to manufacture) are the filer's derived-layer choices, recorded here and reported (ECO-106).
