# self-conformance cost survey (2026-10-28, investigation only, no code changed)

Requested by session local_e03f7e27 (user akiramei): where does `method/tools/self-conformance.py` spend its time, is anything redundant, does each check run at the right point (local / commit / pre-push / CI), and could it run less often. Detection power is not traded for speed.

Baseline: BomDD `main` at `cbb71c1`, clean tree. Machine: the user's Windows 11 desktop, 8 logical CPUs, Python 3.12.

## 1. Answer in one paragraph

**C11/C11b take 201.7 s of the 209.7 s local run (96 %); every other check together takes about 8 s.** Nothing other than C11 is worth an ECO for speed. Inside C11, almost all of the time is git commits through the process-core hooks in the qualification runner's 23 disposable sandboxes, run twice for the determinism check and twice again for C11b. The sandboxes do not depend on each other, so building them side by side (with the two determinism passes kept one after the other) is the one remaining change that keeps every verdict. But the work is CPU-bound: measured on this machine, it brings C11 from about 200 s to about 145 s (the local run from about 210 s to about 155 s), not further. The runner is a distributed template, so that is a template ECO plus a distribution ECO, not a self-conformance-only change like ECO-105. Going below that needs less work, which means fewer runs or skipped runs, and those change what is detected (§7). Each commit through the process-core hooks costs about 1.2 s on Windows, and that is the cost underneath everything. The pre-push hook runs no checks; it only compares a tree hash, so it duplicates nothing. The real duplication is in CI: the `dotnet` job reruns the whole fast tier on the same Windows image that the `fast (windows-latest)` job already ran.

## 2. How it was measured (cheapest first)

1. **Reading the code.** Each check's input files and subprocess count were read, without running anything.
2. **The ECO-105 profiler**, copied unchanged from `bomdd/reports/eco-105-c11-parallel/sc_profile.py`. It times each check in the order `main()` runs them, plus the subprocesses each check starts. One run: total 209.7 s, 0 failures, exit 0. It does not write the witness.
3. **Timing one IQ pass and one OQ pass by sandbox** on a fresh scaffold (`pq_sandbox_timing.py`, imports the runner and wraps `Sandbox`; see §5).
4. **N whole OQ passes at once** (N = 4, 8) on one fresh scaffold (`pq_concurrency.py`), as a proxy for how far running them side by side can go on this machine.
5. **The CI job and step times** of the last three runs (`gh run view --json jobs`).
6. **Not measured:**
   - C9's own duration. It was estimated from CI job differences; running `--dotnet` locally would build into the shared working tree.
   - The CI runners' core count.
   - Any prototype of the proposed changes.

**Where the files are:** the scripts and raw outputs are in `self-conformance-cost-evidence/` next to this note. They can be copied to `bomdd/reports/` if the user wants this survey kept in the repository. The BomDD working tree was not changed (`git status` clean after the runs).

## 3. Per-check table

Local time is from the one profiler run on `cbb71c1`. "Runs where" means: **L** = local manual run (the single entry point, AGENTS rule 2; writes the PASS witness); **U** = CI `fast (ubuntu-latest)`; **W** = CI `fast (windows-latest)`; **D** = CI `dotnet` (Windows, `--dotnet`). The pre-push hook runs no check; it compares the pushed tree with the witness. Frequency today: 66 commits and 61 CI runs since 2026-10-20, so nearly every commit is run locally once and pushed alone.

| Check | Local time | Inputs that can turn it red | Origin | Runs where | Proposal | Why |
|---|---:|---|---|---|---|---|
| C1 yaml-parse | 0.5 s | `method/**/*.y{a,}ml`, `bomdd/**/*.yaml` | ECO-001/012 | L U W D | keep | cheap; inputs include every record commit |
| C2 json-parse | 0.0 s | `method/**/*.json` | ECO-001/006 | L U W D | keep | cheap |
| C3 register | 0.2 s | `bomdd/60-change-register.yaml` | ECO-006/012 | L U W D | keep | cheap; record commits touch it |
| C4 scaffold | 1.3 s | all of `method/**` (the kit is a copy of `method/`; the lock's file count is checked against the manifest), `bomdd-init.py` | ECO-004/010/012 | L U W D | keep | 1 s; see note on shared scaffolds (§6, R4) |
| C5 fail-closed | 0.2 s | `method/tools/stage0-survey.py`, `impact-retrospective.py` | ECO-002/003/008 | L U W D | keep | cheap |
| C6 gate-mutation | 0.2 s | `method/tools/ui-cad-gate.py` | ECO-005 | L U W D | keep | cheap |
| C7 readme-drift | 0.0 s | `README.md`, `bomdd-init.py` (SKILLS) | ECO-006 | L U W D | keep | cheap |
| C8 root-hygiene | 0.0 s | names at the repository root | ECO-006 | L U W D | keep | cheap |
| C10 schema-drift | 0.0 s | `method/schemas/draft/*`, `method/templates/ui-mock-extraction/` | ECO-014 | L U W D | keep | cheap |
| **C11 + C11b** process-core | **201.7 s** (two runner processes of about 194 s each, side by side since ECO-105) | `method/templates/process-core/**` (hooks, validator, runner, profile); `bomdd-init.py`; the AGENTS.md template and the kit link targets it points into (IQ-08); the git, Python and OS behaviour of the machine | ECO-015/017/020/024/060/105 | L U W D | **make faster without changing the verdict** (§6, S1) | 96 % of the local run; the only lever that matters |
| C12 entry-refs | 0.0 s | `AGENTS.md` and its link targets | ECO-025 | L U W D | keep | cheap |
| C13 link-integrity | 1.3 s | root `*.md`, `method/**/*.md`, the tracked-file set, the scaffold's `*.md` | ECO-026 | L U W D | keep | 1 s |
| C14 kit-freshness | 2.7 s | `method/tools/kit-freshness.py`, `bomdd-init.py`, the cleanup helper | ECO-026/065 | L U W D | keep | 3 s |
| C15 deprecated-refs | 0.1 s | root `*.md`, `method/**/*.md` | ECO-027 | L U W D | keep | cheap |
| C16 converge-receipt | 0.3 s | register, cited orders, `method/improvements.md` | ECO-033/034 | L U W D | keep | cheap; record commits touch these |
| C17 calibrate-receipt | 0.2 s | register, cited orders | ECO-043/051 | L U W D | keep | cheap |
| C18 pre-push-witness | 0.9 s | witness helper; `core.hooksPath`; `bomdd/hooks/pre-push` | ECO-046/092 | L (U W D: calibration arm only, install check NA) | keep | 1 s |
| witness write | 0.13 s | the working tree at the end of the run | ECO-046/092 | L | keep | negligible; see §8 |
| C9 loop-suites | not run locally; about 7–39 s in CI by difference | `loops/**`, `loops/expected-results.yaml`, the .NET SDK (`10.0.x`, floating) | ECO-006/039 | D only | keep in D | SDK drift is caught only because it runs every push |
| `worklist.py --selftest` | about 1 s (CI) | `method/tools/worklist.py` | — | U W | keep | cheap |
| `bomdd-witness.py --selftest` | 10–13 s on W, 1 s on U | `method/tools/bomdd-witness.py` | ECO-096 | U W | keep | small |

## 4. CI today (last three runs)

| Run (commit) | U: self-conformance / job | W: self-conformance / job | D: `--dotnet` / job | Wait for the conclusion |
|---|---|---|---|---|
| 40701637554 (cbb71c1) | 35 s / 45 s | 184 s / 219 s | 191 s / 241 s | 241 s |
| 40590058612 (5716680) | 34 s / 44 s | 159 s / 189 s | 198 s / 246 s | 246 s |
| 40589149810 (f791496) | 30 s / 39 s | 189 s / 223 s | 201 s / 246 s | 246 s |

- The wait for the CI conclusion is the slowest job, which is D.
- D is setup-dotnet (24–30 s) + the full fast tier on Windows + C9.
- The fast tier is the same code on the same image (`win25-vs2026`, Python 3.12.10, PyYAML 6.0.3) in W and D. So **the Windows fast tier runs twice per push**, and the second run decides nothing new.
- On Linux the whole fast tier takes 30–35 s. The Windows cost is process start-up: the 134 hooked `git commit`s of one runner process cost about 0.9 s each (ECO-105 `pq_profile.py`).
- `worklist.py --selftest` and `bomdd-witness.py --selftest` run only in CI (U, W), never in the local run that writes the witness. A red there is found only after push. This is recorded as a fact; adding them locally would cost about 10 s on Windows, and that is the user's call.
- CI prints the log at exit (stdout to a pipe is block-buffered), so per-check times cannot be read from CI logs. This is why C9 was estimated by difference.

## 5. Inside C11

**What C11 runs:**
- C11 makes 2 scaffolds (`ProcCoreSmoke`, and `AdaptSmoke` for C11b).
- It runs `process-qualification.py` 3 times:
  - a full run on the default scaffold;
  - an IQ-only run on the same scaffold with `core.hooksPath` unset;
  - a full run on the adapted scaffold (C11b, on a second thread since ECO-105).
- A full run is the IQ pass plus the OQ pass, done `--runs 2` times (the determinism check, REV-11).
- So one self-conformance run does **4 OQ passes**, two at a time.

**One OQ pass, measured alone** (`pq_sandbox_timing.py`, fresh scaffold, nothing else running):
- **IQ pass:** 0.8 s (8 controls).
- **OQ pass:** 84.5 s (27 controls, all pass), across **23 sandboxes** of 2.2–6.6 s each.
- **Setting up a sandbox** (`git init`, 4 `git config`, 2 `rev-parse` and a first commit through the hooks): about 1.5 s. The 3 sandboxes that install the hooks later set up in 0.3 s. So **one commit through the hooks costs about 1.2 s on this machine**, against about 0.1–0.2 s without them.
- **The rest of each sandbox:** 1–3 more commits and 0–2 `validate` runs.
- **Where the time goes:** the hooks start `sh`, which starts the Python validator. On Windows, that process start-up is the cost. On Linux the same suite takes about 30 s in CI.

**Why a full run takes about 194 s:** 2 × (0.8 + 84.5) s is about 170 s alone. With C11b running beside it, each runner process took about 194 s in the profile, so the two compete for CPU by about 15 %.

**Are the sandboxes independent?** Read from the code:
- Each sandbox has its own directory under the pass's own `mkdtemp` base.
- Each has its own global git config file (`GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM`).
- They copy the scaffold's assets and only read them.
- The module global `SPEC` is set once, before the first sandbox, and only read afterwards.
- The validator's selftest uses its own `TemporaryDirectory`.
- No sandbox reads another's results.

Two things would need care in a parallel version:
1. Results must be collected in the original order, because the determinism check compares the canonical JSON of the two runs.
2. `die()` calls `sys.exit(2)`. In a worker thread that raises `SystemExit` in the thread, and its effect on the main thread has to be proved, as ECO-105 did for C11b's exception.

ECO-105's receipt left "a hidden shared resource such as a global git config" unmeasured. The per-sandbox `GIT_CONFIG_GLOBAL` answers that for the sandboxes. It does not answer it for the scaffold's own `git init`, which runs once, before any sandbox.

## 6. Candidates that keep every verdict

**S1. Run the qualification runner's sandboxes side by side** (template: `method/templates/process-core/tools/process-qualification.py`).

- **The change, recommended form:** `run_oq` builds its 23 sandboxes on a small worker pool (2–4 wide), and returns the results in the original order.
  - The two determinism passes stay one after the other, as REV-11/ECO-015 defined them ("the same input, run twice, gives the same verdicts and reasons").
  - With C11 and C11b already side by side, a pool of 2 or more reaches the 4 streams where this machine saturates (below).
- **Not recommended: running the two `--runs` passes side by side.**
  - It is simpler and has the same ceiling.
  - But the second pass would no longer run after the first, so "the first pass left state that changed the second" would no longer be sampled; interference between concurrent passes would be sampled instead.
  - The comparison stays the same, but the class of failure it can see shifts. Under "no trading detection for speed" this form would have to be declared as a change, so it is left out.
- **What stays the same:**
  - every control and its verdict;
  - the determinism check, still `--runs 2`, still comparing the same canonical JSON;
  - C11 and C11b themselves, which are not changed.
- **Effect, measured as a proxy** (`pq_concurrency.py`: N whole OQ passes at once on threads, own bases, one fresh scaffold; all passed, results identical):

  | OQ passes at once | Wall time | Per pass |
  |---:|---:|---:|
  | 1 | 84.5 s | 84.5 s |
  | 4 | 141.9 s | 35.5 s |
  | 8 | 252.4 s | 31.6 s |

  - The work is CPU-bound process start-up, and this machine saturates at about 4 streams.
  - C11 + C11b need 4 OQ passes. Today they run as 2 streams of 2 passes (about 194 s each). All 4 at once took **about 142 s**.
  - So the ceiling of S1 is roughly **C11 from about 200 s to about 145 s, and the local run from about 210 s to about 155 s (−25 to −30 %)**. It is not a several-fold gain.
  - This is a proxy, not the change itself; the real figure needs a prototype measured in the shape of ECO-105's V4.
  - CI Windows runners have fewer cores than this machine (not measured here), so their gain may be smaller.
- **Products get the same gain.** The runner is installed in product repositories, and `bomdd-init` runs it at scaffold time unless `--no-qualify` is given, so their qualification gets faster too.
- **Cost of the change:**
  - It is a template change, so it needs a template ECO in this repository, with an equivalence proof in the shape of ECO-105's V2: the same output and exit code with failure scenarios faked, and broken versions (wrong order, a lost result, a lost `die`) told apart.
  - Distribution to the three products is a separate ECO in the shape of ECO-116, or it is left until each product next refreshes its kit.
  - The runner's "version pair" note matters: only the runner changes, and the validator it qualifies does not.
- **Risk:** contention could make a timing-sensitive control flaky.
  - **Measured:** 4 and 8 whole OQ passes at once all passed, and their results were identical (`identical=True`), one sample each.
  - ECO-105 found no wall-clock waits in the controls.
  - A flaky control would show as a determinism FAIL, not be hidden.

**S2. Stop running the fast tier twice on Windows in CI** (workflow, plus a flag in self-conformance).
- Give `self-conformance.py` a way to run C9 alone (for example `--dotnet-only`), and use it in D. W keeps running C1–C18 on Windows.
- Every check still runs on Windows every push, on the same image, so no verdict is lost.
- Effect: D shrinks to about setup + C9 (estimate 70–90 s). The critical path moves to W, so the wait for the conclusion falls by roughly 20–60 s per push (from 241–246 s to 189–223 s in the three runs above). Windows runner time falls by about 160–200 s per push.
- What changes: D no longer sees the fast tier with the .NET SDK installed. No check other than C9 reads dotnet, so this is a difference in environment, not in what is checked.
- Workflow-only alternative: drop W and move the two selftests into D. The verdicts stay the same, but the wait does not fall, because D stays the slowest job.
- If S1 is done, the gain from S2 becomes smaller, because both W and D get faster.

**S3. Make CI per-check times observable** (not a speed change).
- Flush after each check line, or run `python -u`.
- This turns the CI log into a per-check profile. Without it, the C9 figure above is only an estimate, and the next tuning decision is again blind.

**R4. Small redundancies, listed but not worth an ECO on their own:**
- Five `bomdd-init` scaffolds per run (C4, C11, C11b, C13, C14). The three without git (C4, C13, C14) could share one; that saves about 2 s.
- C11's IQ-only mutation run on the real scaffold repeats what OQ control N6 measures in a sandbox (unset `core.hooksPath` → IQ-03 fails). It also checks the runner's exit code and JSON in `iq` mode, so it is not a pure duplicate. It costs a few seconds. Keep it.

## 7. Candidates that change what is detected (not recommended without a ruling)

**J1. Cut the determinism runs from 2 to 1** (in C11, C11b or both).
- Halves C11's work.
- REV-11 forbids `--runs 1` for a full run because a single run cannot show nondeterminism. C11b's second run is the only check of determinism under a non-default profile.
- Since C11 and C11b run side by side, cutting only C11b's runs does not shorten the wall time.
- Detection lost: nondeterministic controls. Not recommended.

**J2. Skip C11/C11b when no input of theirs changed** (the frequency question; a file-based or hash-based skip).
- This is ECO-105's option 2, which the user **did not choose** on 2026-10-12. Two things are new since then:
  - **(i) The input map above.** A record-only commit (`bomdd/**`, `FINDINGS.md`) touches none of C11's file inputs. But C4 and C13 depend on all of `method/**`, so a skip has to be per check, not one rule.
  - **(ii) The witness constraint.** The PASS witness records "this tree passed everything" (ECO-046). A partial run cannot write that witness without changing what the pre-push gate attests. It would have to become something like "this tree passed, and C11 was carried over from tree X with the same inputs".
- C11's inputs also include things outside the repository: the machine's git and Python versions, and its global git config, which the scaffold's `git init` reads. A hash of files cannot see those, so a skip opens a channel for missed failures.
- CI would still run the full suite on every push. But that moves the observation to the layer that went unobserved for 11 commits and about 2 days (ECO-020).
- Detection lost: machine drift between runs; any input missed by the map. Not recommended unless S1 is rejected and the time still matters.

**J3. Run C11 only in CI (move it out of the local run).**
- Same costs as J2, without even an input check. Not recommended.

**J4. Run once per push instead of once per commit.**
- The witness already makes this enough for the push gate.
- But ECO closures record "exit 0 observed before each commit", and nearly every commit is pushed alone today (66 commits, 61 CI runs since 2026-10-20). So this saves little, and it leaves intermediate commits unobserved. Not proposed.

## 8. Side observation (not speed): the witness is computed after the checks

`_write_selfconf_witness` computes the tree at the end of the run, from the working tree as it is then. The checks read the working tree while they run, which takes about 3.5 minutes. If a file changes during the run (for example, another session sharing the folder edits it), the witness can record a tree whose changed file was never checked. Computing the tree at the start, and refusing to write the witness if the tree at the end differs, would close this. It is a possible missed failure, not a speed issue. It is recorded here for the user to decide whether it should be an OBS.

## 9. Ruling point (for the user)

Which, if any, to take to an ECO:

| Option | What | Effect | Verdicts | Cost |
|---|---|---|---|---|
| **A** (recommended) | S2 + S3: the CI `dotnet` job runs C9 only, and CI prints per-check times | CI wait −20 to −60 s per push; about 3 min less Windows runner time per push; per-check times visible in CI | unchanged | one ECO: self-conformance flag + workflow |
| **B** | A, plus S1: the runner builds its sandboxes on a small worker pool (determinism passes stay sequential) | also local run about 210 → 155 s, CI Windows somewhat faster; products' qualification faster | unchanged, with an ECO-105-style equivalence proof | template ECO + distribution ECO, to three products |
| **C** | none | — | — | — |

- Options that change verdicts (J1 to J4) are not offered.
- J2, the skip by inputs, is the only one that would cut the record-commit loop to near zero locally. It was declined on 2026-10-12. It stays declined unless the user reopens it with the witness question (§7, J2) answered.
- Separately: should §8 (the witness is computed after the checks) be recorded as an OBS?
