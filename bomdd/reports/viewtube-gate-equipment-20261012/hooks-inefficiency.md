# Inefficiencies inside the necessary gate processes (2026-10-12)

**Request**: user, 2026-10-12. Investigate what the commit hooks run. A necessary process can still be doing its work inefficiently.

**Method**:
- Code was read and the existing timing data from `README.md` was used. Nothing ran the gate end to end again, and nothing in ViewTube was changed.
- Two subagents read the tools:
  - A: validate_process and its sub-validators, plus validate_change_impact.
  - B: the hooks, the change-impact and UI-golden harnesses, the sweep, and the UI-manufacturing lifecycle.
- Their scripts are in `subagent-scripts/`.
- I measured items 0 and 1, and spot-checked item 2.

All items keep the verdict unless they are marked as a ruling item. **Measured** means run on this machine on 2026-10-12. **Est** means an estimate.

## 0. Environment: the first read of a freshly written file is about 80 times slower (measured)

**What was measured** (`fresh_read.py` → `fresh-read-output.txt`): the 5,195-file, 260 MB record surface was copied into a new temporary directory and read three times.

| Read | Time |
|---|---:|
| Pass 1 | 34.6 s |
| Pass 2 | 0.43 s |
| Pass 3 | 0.54 s |
| The same files in ViewTube's working tree | 1.6 s |

**Why it matters**: the gate writes fresh trees again and again (index copies, fixtures, evidence copies). This explains the validators' "34-44 s on a first read, 7-12 s on a re-read".

**Likely cause** (inference): Windows Defender real-time protection is on (`Get-MpComputerStatus`: RealTimeProtectionEnabled, OnAccessProtectionEnabled = True). On-access scanning of new files is the probable cause. It was not proved by switching protection off.

**Who decides**: the security setting is the user's decision. Agents do not change it.

## 1. validate_machinery_claims: necessary and efficient once the cache is warm (measured)

`machinery_claims_profile.py` → `machinery-claims-profile-output.txt`, `surface_sizes.py` → `surface-sizes-output.txt`:
- **Work**: 13 claims × 5,195 files. Reading and normalising takes 3.2 s, the 67,535 substring searches take 1.0 s, and the whole run takes 8-13 s warm.
- **Make-up of the surface**: 90% is JSON (3,300 files, 235 MB), and 2 of the 47 claim hits are in JSON. The scope therefore cannot be narrowed without changing the verdict. Its cold-cache cost is item 0.

## 2. validate_process and its sub-validators (subagent A; the register-parse times were spot-checked)

**The scale**: validate_process ran **22 times** in the measured equipment commit, 878 s in total, most of them inside fixture commits. Each saving below is per run.

| # | Inefficiency | Measured | Fix (verdict unchanged) |
|---|---|---|---|
| 2.1 | The register (3.0 MB) is parsed 5-6 times per run with the pure-Python loader | **Spot-checked**: SafeLoader 1.67 s and CSafeLoader 0.15 s, equal result (`yaml-loader-check-output.txt`). Subagent: 233/234 bomdd YAML files parse equal; the other one fails under both loaders. | Use `getattr(yaml, "CSafeLoader", yaml.SafeLoader)`. Est 8-9 s per run. **Caveat**: the libyaml error text differs, so for a malformed register the VALIDATOR_UNAVAILABLE message text changes. The exit code and the finding code do not. |
| 2.2 | `validate_record_language.entry_text` rescans the whole register with a regex for each entry (`:110-120`) | 5.48 s, against 0.021 s for one pass that builds an id→slice index; identical output | Build the index once. Est 3.7 s per run. |
| 2.3 | `validate_process.history_has` runs `_trailer_values` over all 1,115 messages for each lookup (`:432-468`), 129,706 `findall` calls | 3.22 s, against 0.033 s when the values per key are computed once; identical | Compute the values per key once. Est 3 s per run. |
| 2.4 | The 5-6 sub-validators run one after another (`validate_process.py:1513-1564`), although they are independent | Typical run: children 22.9 s, longest child 7.8 s | Start them together; print the results in the current order and stop at the first failure, as now. Est 15 s wall time per run. **Risk**: CPU contention. |
| 2.5 | `--commit-msg` mode: one `git show` per staged file (`:866-868`) | 0.5-0.8 s | One `cat-file --batch`. |

## 3. validate_change_impact (subagents A and B)

**What it does now** (`validate_change_impact.py:86,103`): one `git show :path` per read and one `git cat-file -e` per existence check.
- In one run, 343 spawns take 11.2 of 15.0 s, and 88 of them are repeats. For example, the same `cat-file -e :bomdd/eco/ECO-VT-064-independent-review.md` runs 40 times.
- About 199 manifest reads are thrown away unread (`:386-392`).
- **Across the commit**: 16 runs, 1,857 git spawns, 62.7 s.

**Fix**: one `git cat-file --batch` and `--batch-check` process plus a per-run memo, which is what `validate_record_citations` already does. Est 62.7 s → under 5 s per commit. The index does not change during a run, so the bytes read are the same.

**Caveat**: if the unread manifests are skipped instead of batched, then outside `--prospective-index` mode an invalid-UTF-8 manifest on an unchanged entry would no longer fail. The hook uses prospective mode, but batching the reads (instead of skipping them) avoids the question.

## 4. Whole-index copies the harnesses do not need (subagent B)

**The size of a copy**: the index holds 11,805 files and 1,462 MB, of which `test-results/` is 1,267 MB.

**What the harnesses read**: the change-impact and UI-golden harnesses read only under `bomdd/hooks`, `bomdd/process` and `bomdd/tools`, and neither mentions `test-results`. This contradicts the hook comment (pre-commit L324-326, "the trusted harness reads it widely"), which is the reason the equipment branch copies everything.

**Fix**: narrow these copies the ECO-VT-253 way:
- pre-commit L332 (change-impact equipment branch)
- pre-commit L388 (UI-golden)
- commit-msg L48

Est about 70 s → about 5 s. A file left out of the copy makes the harness fail closed.

**What stays**: L470 (UI-manufacturing) keeps the whole copy. Its harness reads `test-results` and writes the inspector build into the copy.

**Not in the measured 313 s**: `reproduce.py` ran the hooks without `GIT_INDEX_FILE`, so in a real commit `sweep-capture-plans.py:73` makes another whole-index copy, est +17-19 s. The plans do not read `test-results` either. This is a limit of the reproduction.

## 5. Harnesses (subagent B)

| # | Item | Measured | Fix / status |
|---|---|---|---|
| 5.1 | `selftest_change_impact` runs 3 times per equipment commit: directly, inside the pre-commit reachability probe, inside the commit-msg probe | 33.4 + 31.7 + 34.4 s | Any saving in it counts three times. |
| 5.2 | `selftest_change_impact` calls `git rev-parse --local-env-vars` 126 times; the output is a list fixed inside git | 3.2 s per run | Cache it once per run. Est 9 s per commit. |
| 5.3 | **Ruling item**: UI-golden's pre-commit reachability probe stages a mutation that also matches the change-impact equipment pattern, so it nests a full `selftest_change_impact` (31.7 s of its 53.4 s) | measured | Probing with a mutation that is only in the UI-golden pattern would save est 66 s per commit. **This changes what the probe exercises**, so it is not verdict-identical and needs a ruling. |
| 5.4 | The UI-manufacturing fixture's `--no-verify` baseline commit takes 34-35 s in each of the 4 runs | measured | The likely cause is git's automatic gc inside the commit. **Inference**: a scratch repository of 8,000 files took 12.9 s to commit by default and 0.38 s with `gc.auto=0` (n=1). **Fix**: `git config gc.auto 0` in the fixture, est 30 s per harness run. Only object storage changes. |
| 5.5 | The fixture's `git add -A` takes 40-48 s per run | measured | `core.looseCompression=0` gave est 30-55% faster (n=1, noisy). Most of the cost disappears with R1 anyway, since the fixture is mostly copied evidence. |
| 5.6 | The inspector is restored and built from cold in each harness run (4 × 3-9 s) | 23 s total | Reusing the binary would change what is qualified, so this is flagged and not proposed. |
| 5.7 | The capture sweep runs 23 plans one after another (294 s); none share files, ports, windows or app data | read in the code | They could run in parallel. Est 90-120 s at 4 wide. **Risk**: the plans have wall-clock waits (`Task.Delay(3000)` and settle loops), so contention could give a false red, though never a false green. Adopt only after showing that the manifests and captures are byte-identical to a sequential run. |

## 6. Already necessary and efficient (checked)

- validate_materialisation_divergence
- the batch calls in validate_line_ending_flip
- record_consistency's census
- the single trailer-history read in validate_process
- probe protocol (0.7-1.2 s)
- the small validators: release-workflow, run-evidence, citations, MCP host
- the 5 real-hook scenarios inside selftest_change_impact
- the commit-msg reachability probe
- the narrowed change-impact copy on ordinary commits

## 7. How the items combine (estimate)

The validate_process items (2.x) pay off per run. E1 removes the nested qualification runs, which hold most of the 22 runs, so 2.x and E1 overlap.

| Commit kind | Now | Estimate after the changes |
|---|---:|---|
| Equipment commit | 113.6 min | about 18 min after R1, E1 and E2 (`step1-ledger.md`), then roughly 10 min with items 2-5 |
| Ordinary record commit | 69 s | mostly validate_process twice, roughly 30 s with 2.1-2.4 |

All of these figures are estimates. Item 0, the first read of fresh files, sits on top of every figure, and only the user can change it.
