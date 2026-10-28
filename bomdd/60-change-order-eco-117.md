# Change Order — ECO-117 (CI: the dotnet job runs C9 only, and self-conformance prints each check's time; same checks, same verdicts)

> Ruling: user, 2026-10-29, "1:A 2:a — CI の dotnet ジョブを C9 だけにする+CI で検査ごとの時間を出す ECO を起票。§8(witness が検査後に計算される件)は OBS として記帳。"
> It answers the ruling point of the cost survey (`bomdd/reports/eco-117-self-conformance-cost/survey.md` §9):
> - 1 = which candidate to take to an ECO: A (S2 + S3), B (A plus S1, the runner's sandboxes side by side), C (none). **A** was chosen;
> - 2 = whether the survey's §8 (the witness tree is computed after the checks) is recorded as an OBS: **a** (yes). It is recorded as
>   OBS-20261029-01 in `method/improvements.md`; it is not part of this ECO.
>
> **Filing only.** Manufacture waits for the user's start instruction (ECO-106: the start-wait after filing is unchanged).
> S1 (a template ECO plus a distribution ECO) and the verdict-changing candidates J1-J4 were not chosen; J2 was already declined on 2026-10-12 (ECO-105).
> Records are English-primary.

## Equipment

- Filing: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- Producer: EQ-004.
- Independent inspection: none planned (manufacturer's calibration only, as ECO-105). The user may name one at the start instruction.

## 0. Measurement (basis of the filing)

The survey and its scripts and raw outputs are in `bomdd/reports/eco-117-self-conformance-cost/` (README.md lists each file). Baseline: BomDD `cbb71c1`, clean tree, the user's Windows 11 machine.

**The local run** (`sc-profile-now.txt`, the ECO-105 profiler unchanged): 209.7 s, 0 failures. C11 + C11b took 201.7 s (96 %); every other check took under 3 s (C14 2.7 s, C4 1.3 s, C13 1.3 s, C18 0.9 s, the rest under 0.5 s).

**CI, the last three runs** (`gh run view --json jobs`; survey §4):

| Run (commit) | fast (ubuntu): self-conformance / job | fast (windows): self-conformance / job | dotnet: `--dotnet` / job | Wait for the conclusion |
|---|---|---|---|---|
| 40701637554 (cbb71c1) | 35 s / 45 s | 184 s / 219 s | 191 s / 241 s | 241 s |
| 40590058612 (5716680) | 34 s / 44 s | 159 s / 189 s | 198 s / 246 s | 246 s |
| 40589149810 (f791496) | 30 s / 39 s | 189 s / 223 s | 201 s / 246 s | 246 s |

- The wait for the CI conclusion is set by the slowest job, `dotnet`.
- `dotnet` runs `self-conformance.py --dotnet`: the whole fast tier (C1-C18) and then C9, on the same Windows image, Python and PyYAML as `fast (windows-latest)` (`win25-vs2026`, Python 3.12.10, PyYAML 6.0.3 in the `[env]` lines). **The Windows fast tier runs twice per push**; the second run adds no check.
- C9's own time is not in any log: CI prints the self-conformance output at exit (stdout to a pipe is block-buffered), so the times above are per step, and C9 (about 7-39 s) is an estimate by difference.

**Read, not run: no fast-tier check uses the .NET SDK.** In `method/tools/self-conformance.py`, `dotnet` is called only by C9 and by the `[env]` imprint when `--dotnet` is given. `bomdd-init.py` and the process-core tools (`method/templates/process-core/tools/`, `hooks/`) do not call it (grep, 2026-10-29). So the fast tier in the `dotnet` job differs from the one in `fast (windows-latest)` only in that the SDK of `setup-dotnet` is on the PATH, which no fast check reads.

**ECO-006 ruling (c)** fixed the CI layout as "fast = ubuntu + windows / dotnet = windows, net10.0". It does not say that the `dotnet` job reruns the fast tier. This ECO keeps both jobs, their names, their runners and the SDK version.

## 1. Change request (frozen at filing; one tool and one workflow)

**S2 — the `dotnet` job runs C9 only.**
- `method/tools/self-conformance.py` gets a flag `--c9-only`, mutually exclusive with `--dotnet` (argparse; given together → exit 2).
- With `--c9-only`, `main()` prints the header and the `[env]` line as with `--dotnet` (the SDK imprinted), runs `c9_dotnet()` only, and prints the `[cleanup]` line.
- With `--c9-only`, the PASS witness is **neither written nor removed**. The witness attests that the fast tier passed on a tree (ECO-046; the header's C18 note (2)), and a C9-only run does not run the fast tier. The run prints one `[witness]` line saying so.
- With `--c9-only`, the last line does not say that every check passed. It says that C9 alone passed (or failed), and that this is not the full gate. The exit code follows the existing rule (0 = the checks run all passed, 1 = a FAIL, 2 = the gate could not run).
- `.github/workflows/self-conformance.yml`: the `dotnet` job's step becomes `python method/tools/self-conformance.py --c9-only`. Its checkout, `setup-python`, `setup-dotnet` (`10.0.x`) and `pip install pyyaml` steps stay. The `fast` matrix (ubuntu, windows) is unchanged and keeps running C1-C18, `worklist.py --selftest` and `bomdd-witness.py --selftest`.

**S3 — each check's time is printed.**
- In `main()`, the wall time of each check function is measured, and **one** `[time]` line is printed after the checks and before the `[cleanup]` line: each check id with its seconds, in the order run, and the total. C11's entry covers C11b, which runs inside it (ECO-105).
- It is printed on PASS and on FAIL, in every mode (default, `--dotnet`, `--c9-only`).
- `main()` makes stdout line-buffered for its own run, so the CI log shows each line when it is printed. This is done inside `main()`, not at import, because `bomdd-job.py` imports the module to read its regular expressions.
- **The `[Cn] PASS|FAIL` lines are not changed.** The time goes on its own line, so the check lines stay comparable between runs and versions (ECO-105 V1).

**Text kept in step:** the docstring's tier description (the `--dotnet` and `--c9-only` modes, and the `[time]` line), and the workflow's header comment (what the `dotnet` job runs, and why: this order).

**Not changed:**
- any check, its inputs, its verdicts or its line text;
- `--dotnet` locally, which still runs the fast tier and then C9 and writes the witness on PASS as before;
- `process-qualification.py` and every template (S1 was not chosen);
- the hooks, the witness logic and the pre-push hook (OBS-20261029-01 is recorded, not repaired here);
- the `fast` job.

## 2. No-impact prediction (before manufacture; frozen)

- **Diff:** `method/tools/self-conformance.py` (`main()`, the argument parser, the docstring), `.github/workflows/self-conformance.yml` (the `dotnet` step and the header comment), this order, the register and `bomdd/reports/eco-117-*/`.
- **Verdicts:** for every input, the default and `--dotnet` modes print the same check lines and give the same exit code as before, plus one `[time]` line. `--c9-only` prints the same C9 lines as `--dotnet` does on the same tree.
- **The witness:** written only by the default and `--dotnet` modes on PASS, as before.
- **CI:** the `dotnet` job falls to about setup + C9 (estimate 70-90 s). The slowest job becomes `fast (windows-latest)`, so the wait for the conclusion falls by roughly 20-60 s per push (241-246 s → 189-223 s in the runs above). Windows runner time falls by about 160-200 s per push.
- **Local:** unchanged apart from the `[time]` line (the default mode runs the same checks).

**Declared at filing — what a push no longer gets (not a verdict change, a smaller sample):**
- **One Windows sample of the fast tier per push, not two.** Today `fast (windows-latest)` and `dotnet` run the fast tier on two separate runners. A check that fails only sometimes had two chances per push to show on Windows; after this ECO it has one. A deterministic verdict is the same either way. C11 keeps its own determinism check (`--runs 2`), which is unchanged.
- **The fast tier no longer runs with the .NET SDK on the PATH.** No fast check reads it (section 0, read), so this is a difference in environment, not in what is checked.

## 3. Acceptance (conditions; frozen at filing)

required_gates: [V1, V2, V3, V4]

**Gated:** V1, V2, V3, V4. **Not a closing condition:** V5.

- **V1 — the default and `--dotnet` modes are unchanged.**
  - Condition: on the same tree, the original and the changed self-conformance give the same exit code and the same `[Cn] PASS|FAIL` lines (temporary paths and the `[env]` line aside). The changed one prints exactly one more line, `[time]`, which names every check run.
  - Run on: this repository in the default mode, and a throwaway clone in `--dotnet` mode.
  - Control: the comparator is shown red on a copy of the output with one check line altered.
- **V2 — `--c9-only` runs C9 alone and never touches the witness.**
  - Condition (a): on the same tree, its `[C9]` lines are the same as those of a `--dotnet` run, and no other `[Cn]` line is printed.
  - Condition (b): with no witness before, there is none after; with a witness before, it is byte-identical after. Checked on a PASS and on a FAIL.
  - Condition (c): a failing C9 (a clone whose `loops/expected-results.yaml` has no suites) exits 1 in both `--dotnet` and `--c9-only` modes, with the same `[C9]` lines.
  - Condition (d): `--c9-only --dotnet` exits 2.
  - Known-bad: a version that writes the witness in `--c9-only` mode, and a version that also runs the fast tier in `--c9-only` mode, are each told apart by (a) or (b).
- **V3 — CI.**
  - Condition: on the manufacture commit, the `dotnet` job's log shows only `[C9]` check lines and the job passes; both `fast` jobs pass; all three self-conformance logs carry the `[time]` line.
- **V4 — the gate before each commit.**
  - Condition: self-conformance exits 0, observed before each commit of this ECO; CI is green for each pushed commit.
- **V5 (not a closing condition).**
  - The wait for the CI conclusion and the job times on the manufacture commit, against the three runs in section 0.
  - C9's measured time from the `[time]` line, replacing the estimate.

## /preflight receipt (start path: manual — the user's "1:A 2:a" read as the start artifact)

- **Classification**: filing of a decided change (the user's ruling on the survey; filing only).
- **Baseline `cbb71c1`**: **confirmed** (HEAD; the tree clean apart from this filing's files).
- **Next number 117**: **confirmed** (the last register entry and the last order are ECO-116; no `60-change-order-eco-117.md`).
- **Current text of `main()`, `env_imprint()`, `c9_dotnet()`, `_write_selfconf_witness()` and the workflow**: **confirmed** (read at `cbb71c1`).
- **No ECO in progress on `method/tools/self-conformance.py` or `.github/`**: **confirmed** (every register entry is verified apart from ECO-079, implemented, which touches neither).
- **No fast-tier use of `dotnet`**: **confirmed by reading** (section 0); not confirmed by running the fast tier without the SDK.
- **Start decision**: **PROCEED_WITH_LIMITS** (filing only; manufacture waits for the start instruction).

No converge loop was run. The change and its scope were decided by the user's ruling on the survey; the details in section 1 (the flag's name, where the time line goes, the witness left untouched) are the manufacturer's derived-layer choices, recorded here and reported (ECO-106).
