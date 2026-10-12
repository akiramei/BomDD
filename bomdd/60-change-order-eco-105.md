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
