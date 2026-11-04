# Change Order — ECO-122 (progress: the dwell view reuses each register blob's parse result, so a repeated run reads only the commits it has not seen)

> Ruling: user, 2026-11-04, "Aを採用します" — option A of the answer to "ViewTube 39.7 秒というのはかなり長いです": keep the history as
> the authority and reuse the result of parsing each register blob, held in a cache that is derived and can be thrown away. Asked
> before the ruling and answered in the same exchange: writing each status's date into the register instead ("台帳に登録されていれば…")
> was not chosen (see "Not chosen").
>
> Each part below is labelled **stop** (refuses), **measure** (a number produced and compared) or **none** (text only), as the standing
> caveat of 2026-10-29 asks. **Filing only.** Manufacture waits for the user's start instruction (ECO-106). Records are English-primary.
> No distribution ECO is needed: the products run BomDD's tool by `--register PATH` (ECO-121); nothing in a product changes.

## Equipment

- Filing: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- Producer: EQ-004.
- Independent inspection: none planned (a cache under a read-only view whose output must not change; the manufacturer's calibration
  only, as ECO-120). The user may name one at the start instruction.

## 0. Measurement (basis of the filing)

The scripts and their outputs are in `bomdd/reports/eco-122-dwell-cache/` (README.md lists each file). ViewTube's register
(`bomdd/process/change-register.yaml`) at `42936d96`, 1,732 commits, on the user's machine.

**Where the 40 seconds go.** ECO-120's `--dwell` parses the whole register at every commit that touched it, on every run:
1,732 blobs, 3,026 MB in total, the largest 3.8 MB. libyaml's C loader reads the newest blob at 27 MB/s, which puts the parse alone at
about 113 s serial (the prototype's serial read below took 189.6 s); ECO-120 deals the commits out to 8 workers, which gives the
measured 30-43 s (ECO-120 V6) and 34.1 s and 39.5 s today (`tool-baseline.txt`). Everything else is small (`costs.py`, `costs.txt`,
three runs each):

| Stage | Time |
|---|---:|
| `git log` of the register's history | 0.09-0.20 s |
| blob ids of all 1,732 commits (`cat-file --batch-check`) | 0.09 s |
| uncommitted-work scan (`git status -uall`, ECO-120 P4) | 0.08 s |
| loading every blob's snapshot from one JSON file (8.8 MB) | 0.08-0.10 s |

**What a reuse gives** (`prototype.py`, `prototype.txt`; serial, one JSON file per blob, the tool's own `_dwell_snapshot`):
cold (empty cache) 189.6 s, 1,732 parsed; warm (the same cache)
4.04 s, 0 parsed, of which 3.89 s is reading the 1,732 per-blob files; the warm snapshots equal the cold ones. The per-blob files are
13 MB on disk; merged into one file they are 8.8 MB and load in 0.08-0.10 s (above). A warm run in the proposed form is therefore
about half a second of git and file reading plus the forward pass over 1,732 snapshots and the interpreter's start.

**Why the same blobs are parsed again.** A register blob is named by the hash of its content; its parse result cannot change while the
parse rule does not. ViewTube's register gained 12 commits in the last week: a run after a week parses 12 blobs, not 1,732.

**What the tools do today.** `bomdd-job.py --dwell` keeps nothing between runs. Nothing else calls it (`bomdd-run.py` does not; CI runs
self-conformance, `worklist.py --selftest` and `bomdd-witness.py --selftest`, not `bomdd-job.py`).

## 1. Change request (frozen at filing)

**P1 — reuse the parse of each blob (measure).** In `method/tools/bomdd-job.py`, the dwell history read gets a cache:
- **Key: the blob id.** The read lists the history as today, then takes each commit's register blob id (`cat-file --batch-check`). A
  blob whose snapshot is in the cache is not read or parsed; only the others go to `cat-file --batch` and `_dwell_snapshot`.
- **What is kept per blob:** exactly what the read returns today — the snapshot (`{id: (status, waiting_on)}`), the `paused` string, and
  the legacy-shape flag; for a blob that does not parse, the exception's type name (so its warning is printed on every run, cached or
  not). A commit without a register blob is not cached (it costs nothing to see).
- **Version key, derived, not written:** the cache file carries a hash over the source of `_dwell_snapshot` and `_dwell_items`, the
  loader's class name and `yaml.__version__`. A cache with another key is a miss (every blob parsed, the file rewritten). Changing the
  parse rule therefore invalidates the cache without anyone remembering to.
- **One file per register:** a JSON file named by a hash of the repository's git common directory and the register's path. Written
  after the run with **only the blobs this run used** (hits and new parses), so blobs of a rewritten history are dropped and the file is
  bounded by the live history. Written to a temporary file in the same directory and renamed into place.
- **Faults are misses, never verdicts:** a missing, unreadable, unparsable or wrongly shaped cache file is a miss. A failure to write is
  reported (below) and changes nothing else. The view still exits 0 (principle 4).
- **Parallelism counts the misses:** the existing rule (8 workers from 64 commits) is applied to the blobs that must be parsed. A run
  where every blob is a hit starts no worker.
- **Output:** standard output (text and `--json`) is unchanged. One line goes to standard error:
  `dwell cache: hits N, parsed M, file <path>` (or `off`, or `write failed: <reason>`, or `read: miss (<reason>)` before it).
- **`--no-cache`:** neither reads nor writes the cache.

**P2 — where the cache lives (measure: V4 checks it).** Outside every work tree and every repository: under the user's cache
directory — `%LOCALAPPDATA%\bomdd\dwell-cache\` on Windows, `$XDG_CACHE_HOME/bomdd/dwell-cache/` or `~/.cache/bomdd/dwell-cache/`
elsewhere; `BOMDD_DWELL_CACHE_DIR` overrides it. `dwell()` called from Python (the selftest, `bomdd-run.py`'s imports, report scripts)
uses no cache unless it is given a directory; only the command line turns it on by default.

**P3 — selftest arms (measure).** `_dwell_selftest()` gains arms with a temporary cache directory: a cold run, a warm run and
`--no-cache` give the same result; a new commit is the only blob parsed; a corrupt cache and a cache with another version key are misses;
a commit that does not parse is warned on the warm run too.

**P4 — the header note (none).** The tool's header note (8) gains one sentence: the cache is derived from the history and can be deleted.

**Not chosen:**
- **Write each status's date into the register** (the user's question before the ruling). Fast to read, but the value is written by
  whoever commits (the view would count what it cannot verify, as ECO-121's reviews found three times with `waiting_on`), it is a
  transcribed value of what the history already holds (playbook §13), it needs a stop to stay true (in ViewTube a new check needs the
  user's exception under the gate freeze, ECO-VT-176), and 272 + 148 + 119 entries would need a backfill derived from the history anyway.
- **Find status lines with a regular expression instead of parsing YAML:** faster on every run, but it is a second parser that must agree
  with the YAML loader on every shape the registers have held (ECO-120 found one legacy shape by running); ECO-VT-255 showed that "same
  verdict on the real files" does not prove "same parser".
- **Read only the diffs (`git log -p`):** a whole-file re-indent or a moved entry (ECO-120 V2 b, c) would need its own rules; the
  equivalence would rest on diff heuristics.
- **The cache inside each repository's git directory:** it would go away with the repository and be shared by its worktrees, but it
  writes into the products' `.git`; the user's cache directory touches no repository.
- **A hand-maintained version number:** a rule that works only if someone remembers it (2026-10-29); the source hash is derived.
- **A checksum over the cache's content:** a corrupt file already fails to parse; a well-formed wrong entry is a declared limit with
  `--no-cache` as the remedy, not a reason for more machinery.

## 2. No-impact prediction (before manufacture; frozen)

- **Diff:** `method/tools/bomdd-job.py` (the cache in the dwell read, `--no-cache`, the selftest arms, the header note); this order, the
  register, `bomdd/reports/eco-122-dwell-cache/`.
- **Verdicts:** for the same register and the same moment, `--dwell` prints the same standard output (text and `--json`) with a cold
  cache, a warm cache and `--no-cache`, and the same as ECO-120's tool. Every other `bomdd-job.py` mode prints the same output;
  `bomdd-run.py` decides the same; every self-conformance check gives the same line on the same tree.
- **Products:** none changed. No file in any work tree or git directory is written.

**Declared at filing — what this will not do:**
- **The first run on a machine stays as slow as today** (about 30-43 s on ViewTube), and so does the first run after the parse rule
  changes. The time figures are one machine's.
- **A well-formed but wrong cache entry is believed.** A content-addressed cache cannot tell; `--no-cache` gives the history's answer.
  V3 shows this, it does not claim to catch it.
- **The view now writes** — one file per register, outside every repository (P2). Until now `--dwell` wrote nothing.
- **CI does not run `bomdd-job.py --selftest`** (ECO-120's declared limit), so the cache arms run when someone runs them. Adding that
  selftest to CI is a `.github/` change outside this ECO's paths; the user may name it at the start instruction.
- **Speed does not wire the view into any step.** Nothing starts `--dwell` at the beginning or end of a session; that is a separate
  question (the hook and the rule for what to decide from the view).

## 3. Acceptance (conditions; frozen at filing)

required_gates: [V1, V2, V3, V4, V5]

**Gated:** V1-V5.

`now` below is one fixed moment passed to `dwell()` in-process, so `days` cannot change between the runs compared; the text form is
`render_dwell()` of the result and the JSON form is the command's own serialisation of it.

- **V1 — same answer, five real registers.**
  - Condition: for BomDD, ViewTube, ViewPrism2, BomDD-Plm and MoviePad-Remake at heads recorded in the evidence (TimetableAdv excluded by
    the user's ruling of 2026-11-04), four results are byte-identical in text and in JSON: ECO-120's tool (the `bomdd-job.py` of
    `9e926be`), the new tool without a cache, the new tool with an empty cache (cold), and the new tool again with that cache (warm).
  - The warm run parses 0 blobs; the cold run parses every blob.
- **V2 — growth and rewriting** (a throwaway repository):
  - after a warm run, one new commit: the next run parses 1 blob and hits the rest; the result equals `--no-cache`;
  - the last commit amended: afterwards the cache file holds no blob that is not in the history; the result equals `--no-cache`.
- **V3 — a faulty cache** (the same repository):
  - (a) the cache file truncated, or not JSON: a miss, every blob parsed, the result equals `--no-cache`, the file rewritten;
  - (b) a cache written under another version key (a copy of the tool with one line of `_dwell_snapshot`'s source changed): a miss;
  - (c) the cache directory not writable: the result equals `--no-cache`, standard error says the write failed, exit 0;
  - (d) a commit whose register does not parse: the same warning on the cold and the warm run;
  - (e) the declared limit, shown: a well-formed entry with a changed status is believed (the result differs from `--no-cache`), and
    `--no-cache` gives the history's answer.
  - Known-bad of the instrument (copies of the changed tool, each must turn an arm red): M1 the version key without the source hash
    (b); M2 a cached parse failure dropped on a hit (d); M3 every blob ever seen kept in the file (V2's amend arm); M4 a write failure
    raised (c).
- **V4 — nothing else moves.**
  - `bomdd-job.py --all --json`, `bomdd-job.py ECO-119 --json` and `bomdd-job.py --all` on this repository: byte-identical output from
    the filing tree's tool and the changed tool.
  - `bomdd-job.py --selftest` (dwell and cache arms nested) and `bomdd-run.py --selftest` exit 0.
  - `git status --porcelain=v1 -uall` of each of V1's five repositories, and a listing of each one's git directory (excluding git's own
    `index` and `logs`), are identical before and after a cold run of the command line with the default cache directory.
- **V5 — time and the gate.**
  - ViewTube's register at its recorded head, on the user's machine, by the command line (wall clock, three runs each): the warm run
    within 5 s, the cold run within 60 s (ECO-120 V6's limit; the cache write included). The times are recorded.
  - self-conformance exits 0, observed before each commit of this ECO; CI is green for each pushed commit (read by the full SHA).

Conditions are frozen at filing; results go to the closing section.

## 4. Manufacture and the measurements before commit (2026-11-04, the user's "A: 起票どおり製造")

**Start.** The user chose option A: the filed form, with no CI wiring. Baseline the filing commit `d06472a` (CI run 41760147971
success); the tree clean apart from ECO-119's untracked R8 report, which this ECO does not touch.

**What was changed** (`method/tools/bomdd-job.py` only):
- `_dwell_read_history()` takes `cache_dir` and `stats`. With no `cache_dir` it reads as ECO-120 did. With one it lists each commit's
  register blob id (`cat-file --batch-check`), takes the blobs found in the cache, and sends only the others (each distinct blob once) to
  `_dwell_parse()`, which applies ECO-120's worker rule to that count; then rewrites the cache file with the blobs used, when anything
  changed.
- `_dwell_chunk()` accepts a bare blob id; `_dwell_parse()` is ECO-120's worker split, moved out unchanged.
- `_dwell_cache_key()` (sha256 over `inspect.getsource` of `_dwell_snapshot` and `_dwell_items`, the loader's module and class, and
  `yaml.__version__`; `None`, so no cache, when the source cannot be read), `dwell_cache_dir_default()`, `_dwell_cache_path()` (sha256 of the
  git common directory and the register's path, 24 hex digits), `_dwell_cache_load()` (any fault a miss with its reason, every field's
  shape checked), `_dwell_cache_save()` (temporary file in the same directory, `os.replace`; an `OSError` returned as text).
- `dwell()` takes `cache_dir` and `stats` (defaults: none). `dwell_main()` passes `dwell_cache_dir_default()` unless `--no-cache`, and
  writes the cache lines to standard error (`_dwell_cache_lines()`, `_dwell_cache_report()`); `--no-cache` is a known option.
- The selftest: `_dwell_cache_arms()` nested in `_dwell_selftest()` on fixture (a) (it holds an unparsable commit and two repeated
  contents): cold, warm (the warning kept), a file cut in half, another version key, a cache path that is a file, one new commit.
- Header note (8) and the usage line.

**Departures** (each recorded; none changes a frozen condition):
1. **Distinct blobs are parsed once.** A register that returns to an earlier content (fixture (a)'s A → B → A) has the same blob at two
   commits; the cold run parses it once. `hits` counts commits, `parsed` counts blobs. The first selftest run expected `parsed` = commits
   and failed (5 != 7); the arm now derives the distinct count from git and fails if the fixture has no repeat. The five real registers
   have no repeat (V1: distinct = commits).
2. **"Not writable" realised as a cache path that is a file.** On Windows a read-only directory still accepts new files, so V3 (c) and the
   selftest point the cache directory at a regular file; the read then reports `absent` and the write `FileExistsError`.
3. **The write is skipped when nothing changed** (every blob a hit, the same set as the file, no miss): a warm run writes nothing. V3's
   arms read `write=None` on a warm run and `ok` after a change.

**Evidence** is in `bomdd/reports/eco-122-dwell-cache/manufacture/` (README.md of the folder above lists each file). Every run below
used the same tool file (sha256 `fe2961aa7129df76…`, printed by `v1.py` and checked again before the commit).

- **V1 result: PASS** (`v1.py`, `v1.txt`; `now` fixed at 2026-11-04T12:00Z). For BomDD @ `d06472a`, ViewTube @ `42936d96`, ViewPrism2 @
  `9bdbe91`, BomDD-Plm @ `0d98371` and MoviePad-Remake @ `a2ca41e`, ECO-120's tool, the new tool without a cache, cold and warm are
  byte-identical in text and in JSON (open entries 3, 173, 24, 0, 0); the cold run parsed every distinct blob (355, 1,732, 440, 19, 21)
  and the warm run 0. A one-byte alteration is told apart.
- **V2 result: PASS** (`v23.py`, `v23.txt`): one new commit parsed 1 and hit 5 of 6; after an amend the cache holds 0 blobs outside the
  history (the amended-away blob dropped); both equal the result without a cache.
- **V3 result: PASS** (same run): (a) a file cut in half and a file that is not JSON: miss `not JSON`, 5 blobs parsed, the file rewritten
  and loadable, result unchanged; (b) the copy with one changed line of `_dwell_snapshot`: another key, miss `version key differs`;
  (c) a cache path that is a file: result unchanged, `write failed: FileExistsError` in-process and on standard error, exit 0;
  (d) the unparsable commit warned identically cold and warm; (e) a well-formed entry changed to `applied` is believed (ECO-001 drops
  out of the open list) and without a cache ECO-001 is open — the declared limit shown.
  - **Known-bad** (`mutants.py`, `mutants.txt`): M1 (key without the source) turned V3b red; M2 (a cached failure read back as an empty
    snapshot) V3d (and V2's two arms); M3 (every blob ever seen kept) V2 amend; M4 (a write failure raised) V3c — **4 of 4**.
- **V4 result: PASS** (`v45.py`, `v45.txt`): `--all --json` (13,503 bytes), `ECO-119 --json` (4,896) and `--all` (9,166) byte-identical from
  9e926be's tool (`git archive`, so no worktree in BomDD's git directory) and the changed tool; `bomdd-job.py --selftest` exit 0 (with the
  cache arms) and `bomdd-run.py --selftest` exit 0; for each of the five repositories `git status` and the git directory listing (370,
  1,963, 298, 648, 1,410 files) are the same before and after a cold command-line run with the default cache directory, and the cache file
  lies under `%LOCALAPPDATA%\bomdd\dwell-cache\`, outside every repository.
- **V5, time: PASS** (same run, ViewTube @ `42936d96`, 1,732 commits, the user's machine, wall clock of the command line): cold 37.26,
  37.41 and 40.22 s (limit 60); warm 0.83, 0.71 and 0.70 s (limit 5). The cache file is 8.0 MB. The self-conformance and CI parts of V5 are
  recorded at closure.

**Not done here:** the commit's self-conformance and CI (V5), the closure.

## /preflight receipt (start path: manual — the user's "Aを採用します" read as the start artifact)

- **Classification**: filing of a decided change (the user's choice of option A; filing only).
- **Baseline `9e926be`**: **confirmed** (HEAD; the tree clean apart from this filing's files and ECO-119's untracked R8 report
  `bomdd/reports/eco-119-ruled-layer/r8-round-1.md`, which this filing does not touch).
- **Next number 122**: **confirmed** (the last register entry and the last order are ECO-121; no `60-change-order-eco-122.md` before
  this file).
- **The dwell read (`_dwell_read_history`, `_dwell_chunk`, `_dwell_snapshot`, `_dwell_runs`, `dwell()`, `dwell_main()`)**: **confirmed**
  (read at `9e926be`, lines 1105-1380).
- **No other caller of `dwell()`**: **confirmed** (`bomdd-run.py` and `.github/workflows/` have no `dwell` or `bomdd-job`).
- **No ECO in progress on the same files**: **confirmed** (open: ECO-079 — `method/acceptance-evidence.md`, two product-profile files;
  ECO-119 — `method/templates/process-core/`, the change-order template, playbook §4.5/§7, `bomdd-init.py`, `self-conformance.py`; neither
  touches `bomdd-job.py`).
- **The five registers**: **confirmed** (BomDD 354 commits, ViewTube 1,732, ViewPrism2 440, BomDD-Plm 19, MoviePad-Remake 21; ViewTube's
  at `bomdd/process/change-register.yaml`).
- **Start decision**: **PROCEED_WITH_LIMITS** (filing only; manufacture waits for the start instruction).

## Converge receipt (the cache's form; 起動経路: self-triggered at filing, DoD fixed first)

- 判定: 収束 (round 1 = 8 findings, round 2 = 3 new, round 3 = 0 new).
- DoD:
  - ✔ D1 the history stays the authority: every cached value is derivable from it and the cache can be deleted;
  - ✔ D2 the view's standard output does not change with the cache, cold, warm or off;
  - ✔ D3 a repeated run on the largest register is bounded by the commits it has not seen;
  - ✔ D4 a faulty cache is a miss, never a verdict, and a parse failure still warns;
  - ✔ D5 no product file, work tree or git directory is written;
  - ✔ D6 no existing mode, decision or self-conformance line changes;
  - ✔ D7 each part labelled stop, measure or none, and the limits declared.
- round 1 (8): (a) a stats line on standard output breaks D2 → standard error only; (b) `now` not fixed makes "identical" depend on
  luck → the comparison in-process at one moment; (c) a hand-bumped version is a prayer → a hash over the parse functions' source;
  (d) "CI exercises the cold path" is not true (CI runs no `bomdd-job.py`) → declared, the CI wiring offered at the start instruction;
  (e) one file per blob is 1,732 opens (3.9 s) → one file per register (0.08-0.10 s); (f) the file grows with every rewrite → write only the
  blobs used; (g) on Windows a worker pool costs process starts even with nothing to parse → workers from the misses, none on a full hit;
  (h) a parse failure cached silently would hide its warning → the type name cached, the warning derived on every run.
- round 2 (3 new): (i) where the cache lives: a product's `.git` versus the user's cache directory → the latter, recorded in "Not
  chosen"; (j) a well-formed wrong entry → declared and shown in V3 (e), no checksum machinery; (k) concurrent runs → content-addressed
  entries and a rename into place: either writer's file is a valid cache.
- round 3 (0 new): the parts checked against D1-D7 and against section 0's numbers.
- 未収束事項: none in the form. Declared outside it (section 2): the first run's time, a well-formed wrong entry, the new write, CI not
  running the selftest, and that nothing starts the view.
