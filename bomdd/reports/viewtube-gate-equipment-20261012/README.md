# ViewTube gate: where the 111 minutes of an equipment commit go (2026-10-12)

**Request**: user, 2026-10-12, "111分の内訳の測定を進めて" (measure the breakdown of the 111 minutes). This follows the user's ruling of the same day: accept the 111 minutes for ECO-VT-253, and improve the waiting from the next ECO onward, starting with a measurement. This record only measures. Nothing in ViewTube was changed, and no fix is proposed as decided.

This is the first record written after the ruling that records are English-primary. No Japanese translation is stored.

## 1. What was measured, and how

**The subject** is the gate of ViewTube's repair commit `e912e5d8` (ECO-VT-253). On 2026-10-12 it took 111 minutes, and its per-stage time was not recorded (`../viewtube-gate-candidates-20261012/README.md` §2.5).

**The reproduction** (`reproduce.py`) ran in a throwaway clone (`git clone --shared -c core.autocrlf=false`):
- It checked out the parent `5fd5394e` and staged the `e912e5d8` tree over it, which is the state the real `git commit` saw.
- Before running, it asserted three things: the staged name-status equals `git diff 5fd5394e e912e5d8`, the index tree equals `e912e5d8^{tree}`, and the UI-manufacturing harness has the qualified sha256 `983075a6…`. That last one is the condition for the hook's one-time ECO-VT-253 branch (`out/setup.txt`).
- It ran the hooks directly, as `hook_profile.py` did on 2026-10-12. ViewTube sets `core.hooksPath=bomdd/hooks`, so git runs these same files with nothing in between.
  - `bash -x bomdd/hooks/pre-commit` ran with a timestamped, line-numbered `PS4`.
  - `bash -x bomdd/hooks/commit-msg` ran with `e912e5d8`'s own message.

**Inside the Python processes**, `site/sitecustomize.py` was put on `PYTHONPATH` for the hook run:
- Every Python process the hook starts, including the nested ones inside harness fixtures, logged its start, each `subprocess.run` call (`check_output` goes through it) and its exit to `out/timer-log.jsonl`.
- Every write is wrapped so it cannot change a verdict.
- Both hooks returned 0, as on the day.

**The bytes are unchanged**: the hook and tools at `e912e5d8` are byte-identical to ViewTube HEAD `769bb27a` (`git diff --stat e912e5d8 HEAD -- bomdd/hooks bomdd/tools` is empty). The candidate harness that the one-time branch ran is the harness that HEAD now holds. So a future commit that stages the hook or UI-manufacturing equipment will run the same stages.

**Scripts and outputs:**
- `analyze.py` → `analysis-output.txt`: per hook block, plus what each process over 5 s waited on.
- `nesting.py` → `nesting-output.txt`: how processes nest in time.
- `gaps.py` → `gaps-output.txt`: in-process time with no child running.
- `evidence_copy_count.py` → `evidence-copy-count-output.txt`: what one function copies.

## 2. Result

**Total: 6,815 s (113.6 min)**, made up of pre-commit 6,653.8 s and commit-msg 161.5 s. The day's commit took 111 min, so this run is 2.3% longer.

| Stage | Seconds | Share |
|---|---:|---:|
| **UI-manufacturing equipment qualification** (pre-commit L458-695) | **6,099.0** | **89.5%** |
| - harness run, own Python time copying evidence (4 harness runs, see 2.1) | 4,748 | 69.7% |
| - fixture commits' hooks, outside the nested harness runs | 808 | 11.9% |
| - fixture precondition `validate_process.py` (4 runs) | 253 | 3.7% |
| - fixture `git add -A` (4 runs) | 169 | 2.5% |
| - `validate_ui_manufacturing.py` x38 per run, `dotnet restore`/`build` | 93 | 1.4% |
| - whole-index copy 18.8, bootstrap check 3.5, `rm -rf` 2.5 | 24.8 | 0.4% |
| Capture-plan sweep (harness build 17.6 s, 23 plans 9-34 s each) | 313.2 | 4.6% |
| UI-golden equipment qualification, twice | 178 | 2.6% |
| - pre-commit: copy 16.7, harness 67.8, rm 3.6 | 88.7 | |
| - commit-msg: copy 22.3, harness 64.1, rm 2.6 | 89.0 | |
| `validate_process.py`, twice | 144.3 | 2.1% |
| - pre-commit (synthetic message) | 73.7 | |
| - commit-msg | 70.6 | |
| Change impact (whole copy 19.1, trusted harness 33.5, validator 15.0, rm 5.9) | 73.8 | 1.1% |
| Everything else (small validators, decisions, probe protocol, selftest) | about 7 | 0.1% |

The four whole-index copies are three in pre-commit and one in commit-msg. With their removals they total 91.5 s (1.3%).

### 2.1 Inside the UI-manufacturing qualification: the harness runs itself three more times

**The harness's lifecycle control** (`lifecycle_hook_controls`, `selftest_ui_manufacturing.py:716`) does five things:
1. Copies the candidate tree into a fixture.
2. Sets `core.hooksPath=bomdd/hooks` there.
3. Makes real `git commit`s.
4. Two of those commits stage UI-manufacturing equipment ("stage weakened inspection equipment", "stage weakened validator and selftest").
5. The fixture's real pre-commit can then run the UI-manufacturing qualification again, with the fixture's committed harness, which builds its own lifecycle fixture.

Of the four such equipment commits made by L1 and L2, three started a nested harness run. The fourth, L2's "stage weakened inspection equipment", was rejected in 31.8 s with no nested run. Why it took a different path was not examined.

**Measured nesting** (`nesting-output.txt`):

| Run | Started inside | Seconds |
|---|---|---:|
| L1 (the gate's) | pre-commit L670 | 6,073.3 |
| L2 | L1's "stage weakened inspection equipment" commit (2,998.6 s) | 2,934.7 |
| L3 | L2's "stage weakened validator and selftest" commit (1,538.7 s) | 1,473.2 |
| L3' | L1's "stage weakened validator and selftest" commit (1,532.7 s) | 1,437.3 |

**How the nesting stops:** in L3 and L3', the lifecycle positive-control commit was rejected (rc=1, 29-33 s). On that path the harness returns before its two equipment commits, so the nesting went no deeper.

**The nested runs total 4,372 s.** Without them, L1 alone would be about 1,701 s.

### 2.2 The single largest cost: the evidence copy, about 98 copies of all of `test-results/` per harness run

**Where the time sits:** each of the four harness runs spent 1,066-1,247 s in its own Python with no child process running (`gaps-output.txt`). Each run spent it in one stretch, between `git config core.excludesFile` and `git add -A`. That stretch is `selftest_ui_manufacturing.py:752-772`: read the register, `copy_registered_evidence`, then rewrite one register entry.

**What the copy does:** `copy_registered_evidence` (`:654-713`) handles each registered evidence file under `test-results/` like this:
- It walks the file's whole parent directory with `rglob` to look for symlinks.
- It then copies that whole parent with `shutil.copytree(..., dirs_exist_ok=True)`.

So a directory holding n registered files is copied n times.

**Counted on HEAD's register** (`evidence-copy-count-output.txt`, read-only):

| Measure | Value |
|---|---|
| Registered evidence files under `test-results/` present | 3,050 |
| Distinct parent directories | 389 |
| `copytree` calls (one per present file) | 3,050 |
| Files written by those calls | 1,078,279 (129.5 GB) |
| Files written if each directory were copied once | 16,366 (1.79 GB) |

**The dominant term:** 98 registered files sit directly in `test-results/`. For each of them the parent is `test-results/` itself (9,743 files, 1.28 GB). One copy of it took 15.7 s, and the same copy over itself took 14.0 s. 98 × 14-16 s ≈ 1,370-1,540 s, which matches the measured 1,066-1,247 s per run in size.

The working tree and the index agree here: 9,714 tracked files and 1.27 GB under `test-results/`, against 9,743 files and 1.28 GB on disk. So the count applies to the index copy that the gate's harness reads.

**Across the four harness runs this stretch is 4,748 s, 69.7% of the whole commit.**

## 3. What this means for the next ECO (candidates to prove, not decisions)

The user's rule holds: speed is not traded for correctness. Each candidate below needs a proof that the verdict is unchanged before it is proposed as a fix.

1. **Copy each evidence directory once** (2.2). The bytes in the fixture would be the same: `copytree` with `dirs_exist_ok=True` of the same source writes the same files each time. The symlink walk would also run once per directory. The saving to prove is up to about 4,500 s per equipment commit. This is the same shape as OBS-20261011-01 (repeated processing of the same input), in the same product, so that observation stays at 1/3.
2. **The recursion** (2.1). It costs 4,372 s. Whether the nested runs carry meaning that the controls depend on was **not examined** here. Two things are open:
   - Each nested rejection was observed only as an exit code. Whether each control that expects a rejection is rejected for the reason its name gives is unknown.
   - L3 and L3' stop because their positive-control commit is rejected.

   This is a correctness question before it is a speed question.
3. **UI-golden qualification runs in both hooks** (178 s). It is deliberate per the commit-msg hook's comment ("Reciprocal protection").
4. **The whole-index copies**: four of them, 91.5 s with their removals.
5. **`validate_process.py` in both hooks**: 144 s. Here it was 70-74 s, not the 25 s measured warm on 2026-10-11, mostly because of `validate_machinery_claims.py`. Its first read of a freshly written tree took 34-44 s: the gate's pre-commit run at t=2 s, and each fixture's precondition run. Re-reads of the same tree took 7-12 s: the `--commit-msg` runs inside each fixture. The gate's commit-msg run (41.5 s) came after 1.8 hours of copying, so its cache state is unknown. Candidate (a) of `../viewtube-gate-candidates-20261012/` (skip the second run) was already judged not recommended.

## 4. Limits

- **One run on one machine.** Other load on the machine was not controlled. The total agrees with the day's 111 min to within 2.3%, but individual stages can move. In particular `validate_machinery_claims.py` took 7-44 s across runs, depending on cache state.
- **The timing probe adds a small cost.** Each Python start opens and appends to a file. 6,686 records were written, and their cost was not separated out.
- **Python processes only.** The probe sees Python processes and the `subprocess.run` calls they make. Time inside git, bash and dotnet is attributed to the Python call that started them. A process the hook starts outside Python appears only in the bash trace.
- **The 2.2 cause is inferred, not timed directly.** It rests on the count, one timed copy, the location of the gap, and the agreement in size. The function itself was not timed in isolation.
- **Only the equipment-commit path was measured.** The "other" waits outside the gate (59.7% of the 2026-10-11 window, `../viewtube-gate-effect-20261012/`) were not measured here.
