# Change Order — ECO-120 (progress: the stall of each open ECO is measured from the register's history, its reason is read from a fixed vocabulary, a paused repository is declared once, and uncommitted work's age is shown)

> Ruling: user, 2026-11-04, "A: 進捗の ECO を起票" — option A of the answer after the dwell count: file items 1-3 of its table as a
> BomDD ECO (distribution separate), with the count as the basis. The items:
> - 1 = days in the current status, derived from the register's git history, listed above a threshold; and the reason for the wait as a
>   field with a fixed vocabulary;
> - 2 = a pause of the whole repository, declared with its reason and the condition to resume;
> - 3 = uncommitted work that has gone stale, found at the start of work.
>
> **One departure from that table, disclosed for the start instruction:** item 3 was labelled **stop** there. It is filed as a **measure**
> (section 1, P4, and "Not chosen"): every stall of this kind that was measured happened outside the one entry point that could refuse
> (`bomdd-run.py`), and a commit-time stop cannot see work that was never committed. If the user wants the stop, it is a narrow addition to
> `bomdd-run.py` and can be named at the start instruction.
>
> Each part below is labelled **stop** (refuses), **measure** (a number produced and compared) or **none** (text only), as the standing
> caveat of 2026-10-29 asks. **Filing only.** Manufacture waits for the user's start instruction (ECO-106). Distribution to the products is a
> separate ECO (the ECO-108 → ECO-109 form). Records are English-primary.

## Equipment

- Filing: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- Producer: EQ-004.
- Independent inspection: none planned (a read-only view; the manufacturer's calibration only, as ECO-117). The user may name one at the
  start instruction.

## 0. Measurement (basis of the filing)

The scripts, their outputs and each repository's HEAD are in `bomdd/reports/eco-120-progress-dwell/` (README.md lists each file).
For each of six registers, every commit that touched the register was read and each ECO's status changes recorded with the committer
date; 0 parse failures in all six. Ages are as of 2026-11-04.

| Repository (register commits) | ECO | open | open > 30 days | past dwell before leaving `staged` / `implemented`: median, max |
|---|---:|---:|---:|---|
| ViewTube (1,728) | 272 | 173 | 168 | 0.2 d, 9.1 d / 0.1 d, 9.0 d |
| TimetableAdv (601) | 117 | 77 | 77 | 0.3 d, 9.7 d / — |
| ViewPrism2 (437) | 148 | 24 | 24 | 0.0 d, 22.4 d / 0.0 d, 1.1 d |
| BomDD (347) | 119 | 2 | 1 (ECO-079, `implemented`, 49 d) | `filed` 0.0 d, 33.7 d / 0.0 d, 4.8 d |
| BomDD-Plm (19), MoviePad-Remake (21) | 15 | 0 | — | — |

**What it shows:**
- **Moving work is fast; stopped work stays.** Of the 628 closed spans in `staged`/`implemented`/`filed` across the six, all but five
  left within 10 days (the five: BomDD ECO-016 to ECO-019 in `filed`, 33.0-33.7 d; ViewPrism2 ECO-065 in `staged`, 22.4 d). Almost every
  open ECO is past 30 days. A fixed threshold between the two separates most of them; the default of 14 days would also have listed
  those five while they waited.
- **The status does not say why, and sometimes not what.** TimetableAdv: 62 of its 78 `staged` entries carry
  `implementation_started: True` — the status is behind the work. ViewTube: 76 of its 116 `staged` entries say "waiting for a human's
  golden" in keys like `blocks_application_golden_added_2026_10_08_eco_vt_239` — a different key name each time, so no tool can count
  them.
- **Some stalls are not in the history at all.** TimetableAdv's last commit is 2026-09-28; its register holds 665 uncommitted lines
  (ECO-118 filed only in the working tree, mtime 2026-10-05); 2,191 paths are dirty. In BomDD, ECO-119's first R8 report
  (`bomdd/reports/eco-119-ruled-layer/r8-round-1.md`) is untracked.

**What the tools do today.** `bomdd-job.py --all` lists the ECOs that are not verified, with no age. `bomdd-run.py` decides at launch
(`RUN_IN_FLIGHT(ENTRY_ALIVE)` sees a live run only when the next launch is tried). The register template has one `date` (the filing).
`time-decomposition.py` and 52-metrics' `timing` measure a session after the fact. Nothing compares the current state against the past.

## 1. Change request (frozen at filing)

**P1 — the dwell view (measure).** `method/tools/bomdd-job.py` gets a mode `--dwell` (with the existing `--register PATH` and `--json`,
and `--stale-days N`, default 14):
- It reads the register **at HEAD** (committed), not the working tree. For each entry whose status is not terminal (`verified`,
  `applied`, `rejected`, `superseded`, `withdrawn`, `cancelled`, `closed`), it derives the commit at which the entry's current status
  began: the latest commit at which the entry has that status while the commit before it on the register's history has another status
  or no such entry. Days in the status = now − that commit's committer date. Nothing is written by hand (playbook §13).
- The derivation must equal a full read of the register at every commit (section 0's `dwell.py`) — V1 and V2 hold it to that.
  A faster method (for example `git blame` on the status line, checked against the parent) is the manufacturer's choice, provided it
  passes V1, V2 and V6.
- A commit whose register does not parse is named in a warning, not skipped silently; the entry is derived from the commits that parse.
- Output, summary first: open entries counted by reason (P2; "none" when there is no reason) × age (≤7, 8-30, 31-90, >90 days); then
  the entries over the threshold **without** a reason ("unexplained"), oldest first; then those with a reason, grouped by reason; then the
  past dwell of each status from closed spans (n, median, max); then P3 and P4.
- Exit 0 always (read-only, as the tool's principle 4); `--selftest` exits 1 on a failure. It adds no field to the job records and does
  not change a `stop_type`.

**P2 — the reason for the wait (measure).** An optional entry field `waiting_on`, one of:
`start-instruction` (filed; the start instruction is awaited — ECO-106) · `human-ruling` (a decision from the user) ·
`human-acceptance` (a golden, an acceptance or an approval by a human) · `independent-inspection` (an R8 round or another inspector) ·
`eco:<ID>` (blocked by another ECO) · `external` (outside the repository: CI, another repository, a vendor).
- When it began is derived (the commit at which the field took its current value), not written.
- In the view: an invalid value, or `waiting_on` on a terminal entry, is a warning line. Neither changes a `stop_type` or the exit code.
- `method/templates/60-change-register.yaml`: one commented line with the vocabulary.

**P3 — the repository's pause (measure).** An optional top-level block in the register: `paused: {reason: <text>, resume_when: <text>}`.
- When it began is derived (the commit at which `paused` appeared).
- In the view, the pause comes first (its age, reason and condition to resume), and the open entries are reported as one group under it,
  not as "unexplained". A pause without `reason` or `resume_when` is a warning.
- `method/templates/60-change-register.yaml`: a commented block.

**P4 — uncommitted work's age (measure).** The view also reports, for the repository that holds the register: the count of dirty paths
(tracked changes and untracked files, ignored files excluded), the oldest modification time among them as days, and whether the register
itself differs from HEAD. The age is a **lower bound**: a later touch of a file makes the work look newer, never older.

**P5 — the text (none; it points to P1-P4).** One paragraph in `method/bomdd-playbook-v1.md` §8 (Phase 7): what the dwell view measures,
the `waiting_on` vocabulary, the pause, that the view is not a gate, and its limits (section 2).

**Not chosen:**
- **A gate on age in self-conformance.** The same tree would turn red with the calendar alone, which breaks a verdict's repeatability
  (C11 checks that the gate's verdicts repeat); and a red CI on an unrelated commit points at the wrong change.
- **A stop in `bomdd-run.py` on a stale dirty tree** (the table's item 3 as "stop"): its reach is the narrow launch path, and none of the
  stalls of section 0 went through it. Recorded for the start instruction.
- **A `since` field written by hand** for the status, the reason or the pause: a transcribed value (§13), derivable from the history.
- **A threshold from each repository's past maximum:** one closed long stall would raise the bar for every later one (BomDD's 49-day
  ECO-079, once closed, would hide a 40-day stall).

## 2. No-impact prediction (before manufacture; frozen)

- **Diff:** `method/tools/bomdd-job.py` (the `--dwell` mode, its arguments and its selftest arms), `method/templates/60-change-register.yaml`
  (comments only), `method/bomdd-playbook-v1.md` (§8, one paragraph); this order, the register, `bomdd/reports/eco-120-progress-dwell/`.
- **Verdicts:** every existing mode of `bomdd-job.py` prints the same output for the same input; `bomdd-run.py` (which imports
  `bomdd-job.py`) decides the same; every self-conformance check gives the same line on the same tree.
- **Products:** none changed. Their registers can be read today with `--register PATH`; they gain `waiting_on` and `paused` only through
  the distribution ECO (whether their validators accept the new keys is checked there).

**Declared at filing — what the view will not tell:**
- **Whether a status is right.** A status that is behind the work (TimetableAdv's 62) shows as a long dwell, which is the signal, but the
  view does not read the work.
- **Whether a reason is true.** `waiting_on` is written by whoever commits; the view counts it, it does not verify it.
- **Anything at all unless someone runs it.** It is a view, not a gate; nothing here starts it at the beginning of a session.
- **How long uncommitted work has really sat:** the age is a lower bound (P4).
- **A stall in a terminal status** (for example an `applied` in BomDD that waits for `verified`): terminal statuses are not listed. In
  section 0, none of BomDD's 17 `applied` spans lasted more than a day.

## 3. Acceptance (conditions; frozen at filing)

required_gates: [V1, V2, V3, V4, V5, V6]

**Gated:** V1-V6. **Not a closing condition:** V7.

- **V1 — real registers.**
  - Condition: for every open entry of the six registers at the heads in `heads.txt`, the commit `--dwell --json` gives as the start of
    the current status is the commit at which section 0's `dwell.py` records that status's last change (compared by commit, not by days).
  - Run on: the six repositories at the recorded heads (read-only).
- **V2 — mutated histories** (a throwaway repository; each arm is the known-bad of one shortcut):
  - (a) a status A → B → A: the start is the second A;
  - (b) a commit that re-indents the whole register without changing a status: no start moves;
  - (c) a commit that moves an entry to another place in the file: its start does not move;
  - (d) a commit whose register does not parse: named in a warning; the starts are derived from the other commits;
  - (e) a status changed in the working tree only: not counted; the register reported as differing from HEAD.
  - Known-bad of the instrument: a version that takes "the last commit that touched the status line" moves (b) and (c) — shown, then
    restored.
- **V3 — reasons and the pause.**
  - Each `waiting_on` value is reported in its own group; an invalid value and `waiting_on` on a terminal entry are warnings, and the job
    records and their `stop_type` are unchanged.
  - An entry shaped like ECO-079 (`implemented` for 49 days, no reason) is listed as unexplained; an entry 3 days old is not listed over
    the threshold; `--stale-days 2` lists it.
  - `paused` with both fields: its open entries reported as one group, none as unexplained; without `resume_when`: a warning.
- **V4 — uncommitted work.** A throwaway repository with a tracked file changed and its mtime set 30 days back, and an untracked file set
  10 days back: dirty 2, oldest 30 days (± 1). The same repository clean: dirty 0 and no age. The register changed and uncommitted:
  "differs from HEAD".
- **V5 — nothing else moves.**
  - `bomdd-job.py --all --json` and `bomdd-job.py ECO-119 --json` on this repository: byte-identical output from the filing tree's tool
    and the changed tool.
  - `bomdd-job.py --selftest` (with the `--dwell` arms nested) and `bomdd-run.py --selftest` pass.
- **V6 — time and the gate.**
  - `--dwell` on ViewTube's register at `62d2b3e4` finishes within 60 s on the user's machine (the measured time is recorded).
  - self-conformance exits 0, observed before each commit of this ECO; CI is green for each pushed commit.
- **V7 (not a closing condition).** The view on the six registers: the counts by reason and age, and the uncommitted-work lines, recorded
  (every product reads "none" for the reason until its distribution ECO).

Conditions are frozen at filing; results go to the closing section.

## 4. Manufacture and the measurements before commit (2026-11-04, the user's "測る形で製造する")

**Start.** The user chose the filed form (measure; no stop in `bomdd-run.py`). Baseline the filing commit `32e2bdd` (CI run 41675481205
success); the tree clean before the change apart from ECO-119's untracked R8 report, which this ECO does not touch.

**What was changed** (`git diff --stat` against `32e2bdd`: 3 files, 503 insertions, 1 deletion before this record):
- `method/tools/bomdd-job.py`:
  - header note (8) and the usage line;
  - `--dwell` is dispatched in `main()` **before** `select()`, so no existing mode passes through new code;
  - `dwell()`: the register's history read with one `git cat-file --batch` per worker (8 workers on 64 commits or more, the commits dealt
    out in turn; serial below that); a forward pass with section 0's rule (only commits that parse are compared, each against the last
    value seen); P2's `waiting_on` and P3's `paused` take their start from the same pass; P4 from `git status --porcelain=v1 -z -uall`;
  - `render_dwell()` (summary first), `dwell_main()` (arguments; every error is one `MISSING_INPUT` line, or `{"error"}` with `--json`;
    exit 0);
  - `_dwell_selftest()` nested in `--selftest` (git fixtures with commit dates set; the existing arms are untouched), and
    `_set_times_back()` for the fixtures.
- `method/templates/60-change-register.yaml`: the commented `waiting_on` line (the vocabulary) and the commented `paused` block.
- `method/bomdd-playbook-v1.md` §8: one paragraph after step 6 (the measure, the vocabulary, the pause, "not a gate", the limits).

**Departures found by running on the real registers** (each recorded, none changes a frozen condition):
1. **Legacy register shape (found by V1).** The first run read 33 of ViewPrism2's commits as unreadable: its register before 2026-07-03
   keeps the entries under `change_orders:`, not `changes:`. Section 0's full read takes the first list whose first item has an `id`; the
   tool now does the same when `changes` is absent and counts those commits as `legacy_shape_commits` (ViewPrism2: 33), not as
   warnings. V1 was rerun after this.
2. **The age of uncommitted work (found by V7).** Section 1 P4 says "the oldest modification time". On TimetableAdv that gave
   2,991.9 days: untracked NuGet DLLs under `artifacts/acceptance/eco-042/` keep their 2018 modification times but were created on
   2026-09-02. The modification time alone is not the lower bound the same paragraph declares. The tool now takes, per file, the newer
   of the modification time and the creation time (`st_birthtime`, else `st_ctime`); TimetableAdv now reads 66.5 days (2026-08-29).
   V4's arm sets both times back on Windows (`SetFileTime`) so its frozen condition (30 days) is tested as written; an added arm (a
   file with only its modification time 3,000 days back) holds the age at most 31 days. On an OS where the creation time cannot be set,
   the 30-day arm is reported as not run, not passed.
3. **The rule at a gap.** Section 1 P1 says "the commit before it has another status or no such entry". Implemented as section 0's
   rule, which V1 compares against: a commit where the entry is absent is skipped, not counted as a change. No register of the six has
   such a gap among its open entries (V1: 0 differences).
4. **Counting dirty paths.** `-uall` counts each file inside an untracked directory: TimetableAdv reads 12,186 dirty paths where
   `git status` shows 2,191 entries. Kept (section 1 says "untracked files").
5. **Speed.** The first V1 run gave ViewTube 48.2 s and 57.9 s with the commits split into consecutive blocks (later registers are
   larger, so the last worker carried most of the work); dealt out in turn, 30-43 s (below).

**Evidence** is in `bomdd/reports/eco-120-progress-dwell/` (README.md lists each file).

- **V1 result: PASS** (`v1/results.txt`, `v1/<repo>.dwell.json`; `v1_compare.py`). Every open entry of the six registers at the heads
  of `heads.txt` has the same start commit as the full read: ViewTube 173/173, TimetableAdv 77/77, ViewPrism2 24/24, BomDD 2/2 (plus
  ECO-120, filed after the reference), BomDD-Plm and MoviePad-Remake 0 open; 0 parse failures.
- **V2 result: PASS** (the dwell selftest, `v5/bomdd-job-selftest.txt`): (a) A → B → A gives the second A; (b) a whole-file re-indent
  and (c) moving ECO-002 behind two other entries move no start; (d) the unparsable commit is named in a warning and the starts come
  from the other commits; (e) a working-tree-only status change is not counted and the register is reported as differing from HEAD.
  Known-bad: "the last commit that touched the status line" (`git blame -L` at the re-indent and at the move) returns the re-indent
  commit and the move commit, not the first commit — the arms tell it apart. A first version of arm (c) moved one of only two entries,
  and git's diff kept ECO-002's lines in place, so the shortcut was not fooled; the fixture has three entries since.
- **V3 result: PASS** (same run): the six vocabulary values each form their own group (besides "none" and the invalid value's own); an invalid value and a value
  left on a `verified` entry are warnings; `project()` gives the same job record with and without `waiting_on`; the ECO-079-shaped
  entry (49.0 days, no reason) is the one unexplained entry; a 3-day entry is not over 14 and is over 2; `paused` with both fields groups
  every open entry under it with no warning; without `resume_when` it is warned.
- **V4 result: PASS** (same run; the 30-day arm ran, creation times set back): dirty 3 with the oldest at 30 days and the 3,000-day
  modification-time file not raising it; clean: dirty 0 and no age; the register changed and uncommitted: "differs from HEAD".
- **V5 result: PASS** (`v5/`): `--all --json`, `ECO-119 --json` and `--all` (text) from the filing tree's tool and from the changed tool
  on the same tree are byte-identical (`cmp`; a copy with one altered byte is told apart). `bomdd-job.py --selftest` exit 0 (both lines
  PASS); `bomdd-run.py --selftest` exit 0 (`v5/bomdd-run-selftest.txt`).
- **The dwell arms against broken copies** (`mutants.py`, `mutants-results.txt`; not a condition, a check of the arms): M1 the start
  taken at the first entry into the status, M2 an unparsable commit skipped silently, M3 untracked files not counted, M4 an invalid
  reason not warned, M5 a pause that does not group, M6 the age from the modification time only — **6 of 6 turn the dwell selftest red**.
  (The copies run from a temporary directory, so the existing arms also fail there for want of the activation map; only the dwell line
  is read.)
- **V6, time: PASS** — ViewTube's register at `62d2b3e4`, 1,728 commits, on the user's machine: 30.2 s and 30.4 s (the two V1 runs of
  the final split), 43.1 s and 33.0 s (two runs of the same split by hand). The self-conformance and CI parts of V6 are recorded at
  closure.
- **V7** (not a closing condition; `v7/<repo>.txt`): every product reads "none" for every open entry (no register has `waiting_on`
  yet). Open and over 14 days: ViewTube 173 (8-30 d 5, 31-90 d 129, >90 d 39), TimetableAdv 77, ViewPrism2 24 (all >90 d), BomDD 1
  (ECO-079). Uncommitted: TimetableAdv 12,186 paths, oldest 66.5 days (lower bound), its register differs from HEAD; ViewTube 4 paths,
  21.0 days; ViewPrism2, BomDD-Plm and MoviePad-Remake clean; BomDD's own lines are this manufacture's files.

**Not done here:** the commit's self-conformance and CI (V6), the closure.

## /preflight receipt (start path: manual — the user's "A: 進捗の ECO を起票" read as the start artifact)

- **Classification**: filing of a decided change (the user's choice of option A; filing only).
- **Baseline `3f718b5`**: **confirmed** (HEAD; the tree clean apart from this filing's files and ECO-119's untracked R8 report, which this
  filing does not touch).
- **Next number 120**: **confirmed** (the last register entry and the last order are ECO-119; no `60-change-order-eco-120.md`).
- **`bomdd-job.py`'s modes, `select()`, `load_register()` and principle 4 (exit 0)**: **confirmed** (read at `3f718b5`;
  `--selftest` PASS at `3f718b5`).
- **No ECO in progress on the same files**: **confirmed** (open: ECO-079 — `method/acceptance-evidence.md`, two product-profile files;
  ECO-119 — `method/templates/process-core/`, the change-order template, playbook §4.5/§7, `bomdd-init.py`, `self-conformance.py`. Both
  touch the playbook only ECO-119, in §4.5 and §7, not §8.)
- **The six registers' shapes**: **confirmed** (`changes:` list in all six; ViewTube's at `bomdd/process/change-register.yaml`).
- **Start decision**: **PROCEED_WITH_LIMITS** (filing only; manufacture waits for the start instruction).

## Converge receipt (the view's form; 起動経路: self-triggered at filing, DoD fixed first)

- 判定: 収束 (round 1 = 9 findings, round 2 = 3 new, round 3 = 0 new).
- DoD:
  - ✔ D1 each open ECO's time in its current status is shown, derived from the history, not written;
  - ✔ D2 the reason for a wait is read from a fixed vocabulary, and its absence is shown as such;
  - ✔ D3 a paused repository is declared once and its ECOs are not each reported as unexplained;
  - ✔ D4 uncommitted work's age is shown;
  - ✔ D5 no existing output or decision changes (`bomdd-job` modes, `bomdd-run`, self-conformance);
  - ✔ D6 usable on the largest register in bounded time;
  - ✔ D7 each part labelled stop, measure or none.
- round 1 (9): (a) an age gate in CI turns red with the calendar → a view, not a gate; (b) a hand-written `since` → derived from the
  history; (c) a status behind the work → shown as dwell, declared as not read; (d) a whole-file re-indent or a moved entry would mislead a
  line-based method → V2 (b)(c) and the known-bad; (e) threshold fixed or adaptive → fixed 14 days from section 0, overridable; (f) other
  registers' paths and shapes → `--register`, checked on all six; (g) 173 entries are not readable as a list → summary by reason × age
  first; (h) an invalid reason blocking `bomdd-run` → warnings only, no `stop_type`; (i) mtime is reset by later touches → stated as a
  lower bound.
- round 2 (3 new): (j) a pause that never ends → its age and its condition to resume are shown, a missing condition warned; (k) terminal
  statuses differ by repository (`verified` here, `applied` in the products) → one terminal set, the `applied`-waits-for-`verified`
  blind spot declared; (l) uncommitted register changes are invisible to a history read → the register compared with HEAD (P4).
- round 3 (0 new): the parts checked against D1-D7 and against section 0's three findings.
- 未収束事項: none in the form. Declared outside it (section 2): whether a status or a reason is true; that nothing starts the view; the
  lower bound; terminal-status stalls. The departure from the table's item 3 (stop → measure) is for the user at the start instruction.
