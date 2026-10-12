# Change Order — ECO-105 (self-conformance C11: run C11b beside C11's own qualification runs; same checks, same output)

> Ruling: user, 2026-10-12, "1". The question asked was which ECO to file after measuring an 11 min 43 s BomDD record commit:
> - 1 = parallel C11 runs (a) plus the manufacturer's procedure change (b);
> - 2 = also skip C11 and the CI .NET job for record-only commits (c);
> - 3 = no ECO, (b) only.
>
> (b), running the CI wait in the background, is a working rule of the manufacturer and is not part of this ECO. The record-only skip (c) was not chosen.
> Records are English-primary from 2026-10-12 (the user's ruling under ViewTube ECO-VT-253).

## Equipment

- Filing and manufacture: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- Producer: EQ-004.
- Independent inspection: none (manufacturer's calibration only; no inspector row).

## 0. Measurement (basis of the filing)

**The record commit.** One BomDD record commit (e35c73d, one markdown file) took 11 min 43 s from the self-conformance run to the CI conclusion:
- local `self-conformance.py`: about 5.6 min;
- commit, push and a 15 s wait: about 0.5 min;
- the CI wait: about 5.9 min.

**The local run.** Profiled by check (`bomdd/reports/eco-105-c11-parallel/sc-profile-output.txt`): 337.9 s, of which C11 took 330.6 s.
- C11 runs `process-qualification.py` three times: a full run on the default scaffold (167.1 s), an `--mode iq --runs 1` run (short), and C11b's full run on the adapted scaffold (156.2 s).
- One full run measured 160.6 s: 134 hooked `git commit`s (120.9 s), 1,194 `git rev-parse`, and 613 Python processes (`pq-profile-output.txt`).

**CI** (run 38258045785):
- `fast (ubuntu-latest)` 61 s;
- `fast (windows-latest)` 215 s, of which self-conformance took 215 s;
- `dotnet` 351 s, of which `self-conformance.py --dotnet` took 328 s.

**Why C11b can run beside C11.** C11b (`c11b_adapted_profile`) builds its own scaffold, `AdaptSmoke`, in C11's temporary directory, and qualifies it with the runner script of C11's `ProcCoreSmoke` scaffold. It writes only:
- `AdaptSmoke/`;
- `q-adapt.json`;
- the runner's own `mkdtemp` sandboxes.

C11 writes only:
- `ProcCoreSmoke/`, where it also unsets `core.hooksPath` before its IQ-only run;
- `q1.json` and `q2.json`;
- its runner's own sandboxes.

Neither reads what the other writes. The runner script is only executed, never written.

**Prototype measured** in a throwaway clone at e35c73d (`compare-output.txt`). The original and the changed self-conformance gave the same exit code and the same 25 check lines. The time fell from 336.5 s to 188.3 s. Both exited 1 there, on C18, because the clone has no `core.hooksPath`; that is the same in both and is environment, not the change.

## 1. Change request (frozen; one tool)

In `method/tools/self-conformance.py`:
- `c11_process_core` starts `c11b_adapted_profile` on one worker thread as soon as C11's scaffold and runner exist.
- It then runs its own two qualification runs as before.
- It reports C11, then waits for C11b and reports C11b's results in the order C11b produced them.
- `c11b_adapted_profile` takes a `report` callable, defaulting to `check`, so that its results are collected and printed by the main thread after C11's line.
- An exception in C11b is raised from `future.result()` at the point where the sequential call used to raise it.
- The worker is shut down before the temporary directory is cleaned.

**Not changed:**
- `process-qualification.py`, which is distributed to product repositories (its two determinism runs stay sequential inside it);
- the C11/C11b checks themselves;
- CI;
- the skip for record-only commits (not chosen).

## 2. No-impact prediction (before manufacture; frozen)

The diff is `method/tools/self-conformance.py` (C11/C11b only), this order, the register, and `bomdd/reports/eco-105-c11-parallel/`.
- No change to templates, hooks or `.github`.
- The check lines and exit code are unchanged for every input (V1, V2).
- Local self-conformance time falls by about the duration of C11b (est 150 s).
- The CI Windows and .NET jobs should fall by a similar share. The Linux job is already 61 s.

## 3. Acceptance

- **V1**: condition = on the real repository and on the clone, the original and the changed self-conformance give the same exit code and the same check lines (temporary paths and the `[env]` line aside).
- **V2**: condition = on the failing side, with C11's and C11b's subprocess calls replaced by a fake, the original and the changed `c11_process_core` give the same printed lines, the same FAILURES and the same exception in each of these scenarios: all pass, C11's init fails, C11b's init fails, C11b's qualification fails, both fail, C11b raises. Two broken versions (not waiting for C11b; not reporting its results) must be told apart.
- **V3**: condition = self-conformance exits 0 (observed before commit), and CI is green.
- **V4**: condition = local self-conformance time measured before and after on the same machine.
- **V5** (not a closing condition): CI job times on the next run.

## /preflight receipt (start path: manual — the user's "1" read as the start artifact)

- **Classification**: application of a decided change (user "1").
- **Baseline `e35c73d`**: **confirmed** (git status clean, HEAD matches).
- **Next number 105**: **confirmed** (the last register entry and the last order are ECO-104).
- **Current text of `c11_process_core` and `c11b_adapted_profile`**: **confirmed** (read).
- **No ECO in progress on `method/tools/self-conformance.py`**: **confirmed** (every register entry is verified, apart from one implemented entry that does not touch it).
- **Start decision**: **PROCEED**, override 0.

## 4. Manufacture and the measurements before commit (2026-10-12)

**What was changed** in `method/tools/self-conformance.py` (20 lines added, 6 changed), all in C11/C11b:
- one import (`concurrent.futures.ThreadPoolExecutor`);
- in `c11_process_core`, a worker started after the runner path is known, results collected and reported after C11's line, and the worker shut down before `_cleanup_tmp`;
- in `c11b_adapted_profile`, a `report` parameter defaulting to `check`, and its four `check("C11b", ...)` calls made through it.

**Evidence** is in `bomdd/reports/eco-105-c11-parallel/` (README.md lists each file).

- **V2 result**: PASS.
  - `equiv105.py`: 6 of 6 scenarios the same (`equiv-output.txt`): all pass, C11 init fails, C11b init fails, C11b qualification fails, both fail, and C11b raises (the same `RuntimeError`).
  - The two broken versions, not waiting for C11b and not reporting its results, are both told apart (`equiv-mutants-output.txt`).
- **V1, the clone part**: PASS. The prototype gave the same exit code and the same 25 check lines in a throwaway clone: 336.5 s → 188.3 s.
- **V1, the real-repository part, V3 and V4**: recorded in section 5, after the changed self-conformance has run on this tree.

## 5. Closure (2026-10-12, verified, manufacturer's calibration only)

- **Window.** Baseline `e35c73d` → filing `c82b852` → manufacture `d188b5a` (diff_audit.head; **the window is closed**; the acceptance commit holds records only). Inside the window there are only the allowed paths:
  - `method/tools/self-conformance.py`;
  - this order and the register;
  - `bomdd/reports/eco-105-c11-parallel/`.
- **Acceptance results:**
  - **V1 result: PASS.**
    - Clone: the same exit code and the same 25 check lines (§4).
    - This tree: the changed self-conformance exited 0 with the same check ids and verdicts as the original's run at c82b852. That was compared on the `[Cn] PASS|FAIL` lines; the counts inside the lines move with the files this ECO adds.
  - **V2 result: PASS** (§4).
  - **V3 result: PASS.** Self-conformance exit 0 was observed before each commit (filing 387 s; manufacture 196 s). CI for the filing, run 38265471169, was **success**; CI for the manufacture, run 38266304834, was **success**.
  - **V4 result.** The local self-conformance went from **387 s to 196 s** (wall time, this machine, one run each).
- **V5** (not a closing condition): CI job times on the manufacture commit against the run measured before (38258045785).

  | Job | Total before | Total after | Self-conformance before | Self-conformance after |
  |---|---:|---:|---:|---:|
  | fast (ubuntu-latest) | 71 s | 32 s | 61 s | 24 s |
  | fast (windows-latest) | 242 s | 182 s | 215 s | 155 s |
  | dotnet | 351 s | 247 s | 328 s | 227 s |

  The wait for a CI conclusion is set by the dotnet job, so it went from 351 s to 247 s. One run each, on hosted runners whose load is not controlled.

### 較正 receipt (/calibrate self-application - trigger ①: verified promotion; receipt_author_role = producer; one tool changed)

- **The claim (one sentence).** C11b runs beside C11's own qualification runs, and self-conformance prints the same check lines, keeps the same FAILURES and exit code, and raises the same exception as before, in less time.
- **査定した主張と判定** (the claims assessed and their verdicts; measurement × evidence):
  - "Same lines, FAILURES and exception on the failing side": **observed / eligible**. Six scenarios with a fake for the subprocesses, and two broken versions told apart, so the comparison can go red.
  - "Same exit code and check lines on the passing side": **observed / conditionally eligible**. One run each, in a clone and on this tree. Not measured: the real subprocesses failing, which is covered by the fake only.
  - "C11b reads nothing C11's runs write": **read / conditionally eligible**. Argued from the code (separate scaffolds, separate JSON files, the runner's own mkdtemp sandboxes). Not measured: a hidden shared resource such as a global git config.
  - "Faster": **observed / eligible** for this machine and CI, one run each.
- **検出した計器欠陥と帰属** (instrument defects found, and attribution): 0.
  - The manufacturer's tooling made two incidents in this session: a line-ending normaliser rewrote CRLF files in the working tree. Both were caught before commit, the files were restored, and the tool now refuses directories.
- **宣言した検出力の限界** (declared limits of detection):
  - The ordering and exception equivalence rests on the fake.
  - Contention between the two qualification runs could make a timing-sensitive control flaky. None was seen in 4 runs (clone and real, before and after), and the process-core controls have no wall-clock waits that I found.
  - The self-assessment is blind to the manufacturer's own wrong premises (playbook §9); this receipt was written by the manufacturer.
- **Battery, row by row:**
  - **Q1 asked.** The check lines are unchanged; no check text claims more.
  - **Q2 asked.** Known-bad: the two mutants and the failing scenarios. Known-good: the original's output. The labels come from the original code, independent of the change.
  - **Q3 asked.** Six scenarios, one per way C11/C11b can end.
  - **Q4 NA.** No declared input.
  - **Q5 asked.** CI success observed for both commits, and the clone's C18 failure identified as environment.
  - **Q6 asked.** Each commit came after an observed exit 0. The pre-push witness was not tripped, because no file was added after the check.
  - **Q7 NA.** No standing instrument was added.
  - **Q8 NA.** No preventive gate was added.
  - **Q9 asked.** Both versions ran on the same tree and the same clone.
  - **Q10 asked.** The limits above.
  - **Q11 NA.** No input class needs to be separated.
- **What this closure does not support:**
  - the record-only skip (not chosen);
  - running process-qualification's determinism runs in parallel (template, not changed);
  - any product repository.
