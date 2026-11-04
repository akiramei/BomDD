# Change Order — ECO-123 (bomdd-job's gauges: the job view reads an English closure heading, and the dwell selftest catches a version key that does not follow the parse rule and a cache that keeps rewritten-away blobs)

> Ruling: user, 2026-11-04, "1 本で起票する" — the answer to "見つけた計器の欠陥 2 件を、1 本の ECO として起票しますか？" after ECO-122's
> closure, which recorded both findings (ECO-122 order section 5): the nested `--selftest` misses two broken copies of the dwell cache,
> and the job view reports verified ECOs with an English `Closure` heading as `LEDGER_INCONSISTENT`.
>
> Each part below is labelled **stop** (refuses), **measure** (a number produced and compared) or **none** (text only), as the standing
> caveat of 2026-10-29 asks. **Filing only.** Manufacture waits for the user's start instruction (ECO-106). Records are English-primary.
> Both defects lower the evidential value of a pass, not of a product: the selftest's green said less than its arms' names, and the
> job view's check of a closed order was blind to every English closure (the 2026-09-29 rule: a measured false negative is closed first,
> not left until it does harm).

## Equipment

- Filing: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- Producer: EQ-004.
- Independent inspection: none planned (one tool's regular expression and selftest arms; the manufacturer's calibration only, as
  ECO-120 and ECO-122). The user may name one at the start instruction.

## 0. Measurement (basis of the filing)

**The selftest's blind spots** (ECO-122's `bomdd/reports/eco-122-dwell-cache/manufacture/mutants_selftest.txt`). The four broken copies of
ECO-122, run through the tool's own `--selftest`: M2 (a cached parse failure read back as an empty snapshot) red; M4 (a write failure
raised) `UNMEASURABLE`; **M1 (the version key without the parse functions' source) and M3 (every blob ever seen kept in the cache file)
green**. The selftest's version-key arm edits the key written in the file, so it shows that another key is a miss but not that the key
follows the source; and it has no amend arm. Only ECO-122's `v23.py`, which nobody reruns, holds the two properties.

**The closure heading** (`bomdd/reports/eco-123-job-gauge/heading_survey.py`, `heading_survey.txt`, at `825d9a1`). `CLOSE_HEAD_RE`
(`method/tools/bomdd-job.py:91`) requires `クローズ` right after the section number and `verified` on the same line. Of the 122 register
entries with an order, the closure rule alone gives 71 entries a stop other than `NONE`, all `verified`:
- **12 closed under an English heading** since records became English-primary (2026-10-12): ECO-105 to ECO-111, ECO-116 to ECO-118,
  ECO-120 and ECO-121, each `## N. Closure (…verified…)`. ECO-112 to ECO-115 and ECO-122 wrote `## N. クローズ (closure, …verified…)` and
  read `NONE`.
- **59 closed before the convention** that the rule encodes (ECO-055, the first order closed as `## 6. クローズ(…・verified)`): 30 orders
  have no closure heading (ECO-001 to ECO-020, ECO-022 to ECO-029, ECO-033, ECO-034), 27 have `## 6. クローズ` without `verified`, and two
  write it inside another title (ECO-056 `## 10. CI 実測(r3)とクローズ(…・verified)`, ECO-057 likewise).

With `(?:クローズ|Closure)` in place of `クローズ`, the 12 read `NONE`, the 59 stay as they are, and the rule matches no other heading
(the 12 headings it adds are exactly the 12 closures).

**Why nobody saw it.** `bomdd-job.py --all` lists only entries that are not verified. The rule also runs the other way — an order with a
closure heading while the register is not `verified` is `LEDGER_INCONSISTENT` (the ECO-055 measurement, F0) — and for an English order
that direction is blind: a closure written before the register moved would read `NONE`. `bomdd-run.py` refuses to launch on any stop other
than `NONE` (R1), so the 12 would also be refused there; they are verified and not launched.

## 1. Change request (frozen at filing)

**P1 — the closure heading in English (measure).** `CLOSE_HEAD_RE` accepts `Closure` as well as `クローズ` after the section number; the rest
of the rule is unchanged (a heading of level 2 to 6, a section number, `verified` on the same line, fences removed first). Both directions
of the check apply to both words.

**P2 — selftest arms (measure).**
- **Job view** (in the existing job selftest): an English closure heading with `verified` and the register `verified` → `NONE`; the same
  heading with the register `implemented` → `LEDGER_INCONSISTENT`; `## N. Closure` without `verified` is not a closure; an English
  closure heading inside a fence is ignored.
- **Dwell cache** (in `_dwell_cache_arms()`): **the version key follows the parse rule** — the selftest writes a copy of its own file with
  one line of `_dwell_snapshot` changed, imports it, and runs it on the cache the original wrote: a miss with `version key differs`;
  **an amend drops the rewritten-away blob** — after `git commit --amend` with other content, the cache file holds no blob that is not in
  the history, and the result equals no cache.

**P3 — the header note (none).** Limit (1) of the header names both heading words.

**Not chosen:**
- **Rewrite the 12 closed orders' headings to `クローズ`.** A closed record is not edited to suit a tool; the tool reads the language the
  records are written in (the 2026-10-12 ruling).
- **Accept a closure heading without `verified`, or any heading that mentions closure** (the 59). The word is what the rule reads as the
  record of the verdict; a heading written before acceptance would then count, and the reverse direction would turn on headings of open
  ECOs. The 59 stay `LEDGER_INCONSISTENT` in the job view, declared in section 2.
- **A cut-off by ECO number** for the 59: a transcribed boundary in the tool, for entries that are never launched.
- **Match the word case-insensitively or in any language:** no other form was measured (`closure` in lower case occurs only inside the
  parentheses of `クローズ (closure, …)`).
- **Run `bomdd-job.py --selftest` in CI:** the user chose ECO-122 without it; it stays a declared limit here.

## 2. No-impact prediction (before manufacture; frozen)

- **Diff:** `method/tools/bomdd-job.py` (the regular expression, the selftest arms, the header note); this order, the register,
  `bomdd/reports/eco-123-job-gauge/`.
- **Verdicts:** the job view of ECO-105 to ECO-111, ECO-116 to ECO-118, ECO-120 and ECO-121 changes from `LEDGER_INCONSISTENT` to `NONE`;
  every other entry's job record is byte-identical. `--all`, `--dwell` and the dwell cache's key are unchanged (P2 does not touch
  `_dwell_snapshot` or `_dwell_items`). `bomdd-run.py` decides the same, apart from no longer refusing the 12. Every self-conformance check
  gives the same line on the same tree.
- **Products:** none changed. MoviePad-Remake's kit copy of `bomdd-job.py` is not updated (it already differs: sha256 `1a0e8173…` against
  `fe2961aa…` since ECO-120); a kit re-pin is a distribution question.

**Declared at filing — what this will not do:**
- **The 59 pre-convention orders still read `LEDGER_INCONSISTENT`** in the job view.
- **CI does not run `bomdd-job.py --selftest`**, so the new arms run when someone runs them.
- **The selftest's copy arm reads the tool's own file:** a run from a frozen or zipped build without the source reports the cache as off
  (ECO-122 P1), and the arm reports itself as not run, not passed.

## 3. Acceptance (conditions; frozen at filing)

required_gates: [V1, V2, V3, V4]

**Gated:** V1-V4.

- **V1 — the job view on this register.** For every register entry, `bomdd-job.py <ID> --json` from the filing tree's tool and from the
  changed tool: byte-identical for every entry except the 12 named in section 0, and for those 12 the only difference is `stop_type`
  (`LEDGER_INCONSISTENT` → `NONE`). The 59 are unchanged.
- **V2 — the new arms run and pass.** `bomdd-job.py --selftest` exits 0 and its lines name the four heading arms and the two cache arms of
  section 1 P2.
- **V3 — the arms can fail** (copies of the changed tool, run from a temporary directory; only the named selftest line is read):
  - ECO-122's M1 and M3 each turn the dwell selftest `FAILED`, naming the version-key arm and the amend arm; M2 and M4 are still not
    `PASS`;
  - a copy with the old `CLOSE_HEAD_RE` turns the job selftest `FAILED`, naming an English-heading arm.
- **V4 — nothing else moves.**
  - `--all --json` and `--all`: byte-identical from the filing tree's tool and the changed tool.
  - `--dwell` on BomDD's and ViewTube's registers in-process at one fixed `now`, no cache: text and JSON byte-identical between the two
    tools; and `_dwell_cache_key()` equal between them.
  - `bomdd-run.py --selftest` exits 0; self-conformance exits 0, observed before each commit of this ECO; CI is green for each pushed
    commit (read by the full SHA).

Conditions are frozen at filing; results go to the closing section.

## 4. Manufacture and the measurements before commit (2026-11-04, the user's "起票どおり製造")

**Start.** Baseline the filing commit `a968c51` (CI run 41769003840 success); the tree clean apart from ECO-119's untracked R8 report,
which this ECO does not touch.

**What was changed** (`method/tools/bomdd-job.py` only):
- `CLOSE_HEAD_RE`: `(?:クローズ|Closure)` in place of `クローズ`; nothing else in the rule.
- Header limit (1): both words, and the 59 pre-convention orders declared.
- Job selftest (`_selftest_body`): four English-heading arms (ECO-906 to ECO-909), projected from entries built in place, so the fixture
  register and every later arm that counts its entries are untouched; the PASS line names them.
- Dwell selftest (`_dwell_cache_arms`, now also given the fixture's `git` and a list for arms not run): **key-follows-source** writes a copy
  of the tool's own file with the line `data = yaml.load(blob, Loader=_dwell_loader())` given a trailing comment, imports it, and runs it on
  the cache the original wrote (expects hits 0, `version key differs`, write ok, result unchanged); when the source cannot be read, the arm
  is named as not run on the PASS line; **amend** rewrites the cache with the original key, appends a line to the register, amends the last
  commit, and expects parsed 1, the result unchanged, a rewritten-away blob in the file before and none outside the history after.

**Departures:** none from section 1. One choice of the manufacturer: the English-heading arms project entries directly instead of adding
rows to the shared fixture register (recorded above).

**Evidence** is in `bomdd/reports/eco-123-job-gauge/manufacture/` (README.md of the folder above lists each file). Every run used the
same tool file (sha256 `dfb4e5dc0de32c2c…`, printed by `v14.py` and checked again before the commit); the filing tree's tool is
`fe2961aa7129df76…` (`git archive a968c51 method`).

- **V1 result: PASS** (`v14.py`, `v14.txt`): of the register's 123 entries, 111 give byte-identical `--json`; the 12 that differ are
  exactly ECO-105 to ECO-111, ECO-116 to ECO-118, ECO-120 and ECO-121, each in `stop_type` only, `LEDGER_INCONSISTENT` → `NONE`. The 59
  pre-convention entries are among the identical.
- **V2 result: PASS** (same run): `bomdd-job.py --selftest` exit 0; its lines name the four English-heading arms and the two new cache arms
  (6 of 6). The dwell selftest now runs 8 cache arms.
- **V3 result: PASS** (`mutants123.py`, `mutants123.txt`; copies run from a temporary directory):
  - unchanged copy: dwell selftest PASS, no `ECO-123` failure in the job selftest (control);
  - M1: dwell selftest FAILED on `cache key-follows-source` (hits 8, no miss); M3: FAILED on `cache amend` (one blob outside the history
    kept); M2: FAILED (also on `cache amend`); M4: `UNMEASURABLE` — neither PASS;
  - the old `CLOSE_HEAD_RE`: the job selftest names `ECO-123 英語 Closure+verified 台帳= NONE` and the reverse-direction arm.
- **V4 result: PASS** (`v14.txt`): `--all --json` (13,526 bytes) and `--all` (9,199) byte-identical; `--dwell` on BomDD (3 open) and
  ViewTube (173 open) in-process at a fixed `now`, no cache, text and JSON byte-identical between the tools; `_dwell_cache_key()` equal;
  `bomdd-run.py --selftest` exit 0. The self-conformance and CI parts are recorded at closure.

**Not done here:** the commit's self-conformance and CI (V4), the closure.

## /preflight receipt (start path: manual — the user's "1 本で起票する" read as the start artifact)

- **Classification**: filing of a decided change (the user's choice to file both findings as one ECO; filing only).
- **Baseline `825d9a1`**: **confirmed** (HEAD, ECO-122 verified; the tree clean apart from this filing's files and ECO-119's untracked R8
  report `bomdd/reports/eco-119-ruled-layer/r8-round-1.md`, which this filing does not touch).
- **Next number 123**: **confirmed** (the last register entry and the last order are ECO-122).
- **The two findings**: **confirmed** (ECO-122 order section 5; `mutants_selftest.txt`; `heading_survey.txt` rerun at `825d9a1`).
- **Consumers of the closure rule**: **confirmed** (`CLOSE_HEAD_RE` is used once, `project()` at `bomdd-job.py:490`; `bomdd-run.py` reads
  the job's `stop_type` (R1); `bomdd-witness.py` and `self-conformance.py` import the tool but do not read the closure rule).
- **No ECO in progress on the same files**: **confirmed** (open: ECO-079 — `method/acceptance-evidence.md`, two product-profile files;
  ECO-119 — `method/templates/process-core/`, the change-order template, playbook §4.5/§7, `bomdd-init.py`, `self-conformance.py`).
- **Start decision**: **PROCEED_WITH_LIMITS** (filing only; manufacture waits for the start instruction).

## Converge receipt (the two gauge repairs; 起動経路: self-triggered at filing, DoD fixed first)

- 判定: 収束 (round 1 = 6 findings, round 2 = 2 new, round 3 = 0 new).
- DoD:
  - ✔ D1 the job view's closure check reads the closures the records actually contain, in both directions;
  - ✔ D2 no heading that is not a closure becomes one, and no record is rewritten;
  - ✔ D3 the selftest catches M1 and M3, and still catches M2 and M4;
  - ✔ D4 only the 12 job records change; every other output stays byte-identical;
  - ✔ D5 each part labelled stop, measure or none, and the limits declared.
- round 1 (6): (a) rewrite the 12 headings instead → a closed record is not edited to suit a tool, "Not chosen"; (b) the 59 look like the
  same defect → they are not: their orders do not record `verified` in a closure heading (survey classes), kept and declared; (c) a
  looser rule (any heading mentioning closure) → would turn on open ECOs' headings in the reverse direction, not chosen; (d) the version-key
  arm cannot change its own source at run time → a copy of its own file with one line changed, imported, as `v23.py` does; (e) the amend
  arm needs a history rewrite → `git commit --amend` in the fixture; (f) the kit copy in MoviePad-Remake → not updated, already differs,
  declared.
- round 2 (2 new): (g) does the cache key move with P2 → no, P2 does not touch the hashed functions; V4 compares the keys; (h) the
  selftest's copy arm without the source file → reported as not run, declared.
- round 3 (0 new): the parts checked against D1-D5 and against the survey's numbers.
- 未収束事項: none in the form. Declared outside it (section 2): the 59 pre-convention orders, CI not running the selftest, the copy arm
  needing the source.
