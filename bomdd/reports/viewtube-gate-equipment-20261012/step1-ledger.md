# Step 1 ledger: every gate process, kept or excluded, and what excluding costs (2026-10-12)

**Method (user, 2026-10-12)**:
- Step 1. Exclude the processes whose effect is doubtful, and record what each exclusion gives up.
- Also record the processes judged necessary. That a step is needed is a fact; whether it is done the most efficient way is a separate question.
- Then, as the next task, look for another way to make up for each excluded effect.

**Status of this ledger**: nothing here is applied yet. ViewTube code changes need the user's approval and an ECO.

**Times** come from the reproduced equipment commit (`README.md`, 6,815 s), plus `dedupe-copy-timing-output.txt`.

## A. Proposed for exclusion (effect doubtful)

| ID | Process | Time in the measured commit | Why its effect is doubtful | What excluding it gives up | Ways to make up for it (next step) |
|---|---|---:|---|---|---|
| E1 | Nested UI-manufacturing qualification runs, past their first failure | about 14 min (849 s, excluding the evidence copy) | **What the outer control needs**: the lifecycle control only needs the nested run's exit code. The candidate it qualifies carries a validator that always says PASS, so the 34 mutation cases fail within about 15 s (L2 reached its lifecycle part at 15.3 s). **Why the rest cannot matter**: the harness returns 1 whenever any failure exists (`selftest_ui_manufacturing.py:1417-1421`). So the 24-49 minutes after that point cannot change the exit code. | The failure list a nested run would print is cut short. Nobody reads it, because the outer harness captures it and checks only the exit code. Also, the vacuous control in D1 no longer runs. | **The mechanism**: the outer harness passes a stop-at-first-failure flag only in the environment of its own fixture commits. **Real gate runs** keep the full output. **Why the flag is safe**: it acts only when a failure already exists, so it can only end a failing run sooner, never turn a failure into a pass. |
| E2 | Capture-plan sweep when the only sweep trigger staged is `bomdd/hooks/pre-commit` | 5.2 min (313 s) | **What a plan reads**: no capture plan reads the hook. The product, harness, fixtures and root build inputs a plan reads are unchanged from HEAD in such a commit. **What a hook edit can break**: only whether the hook still runs the sweep, and launching the app 23 times is not needed to check that. **Not yet read**: why ECO-VT-182/184 listed the hook as a path "that can strand a plan". | A hook edit that breaks the sweep block itself (wrong pattern, wrong invocation, ignored exit status) is not exercised in that commit. A sweep that silently stops running would not be noticed until someone looked. | **Static check**: the hook still holds the sweep block and the runner invocation. This is a token check, which the UI-manufacturing harness already does for its own block. **Selection-logic test**: run the hook's sweep-selection logic against fixed sample staged lists, which takes seconds. **Fallback**: keep the full sweep for a hook edit that touches the sweep block's own lines. |

## B. Replaced, not excluded (same result, less work)

| ID | Process | Time | Replacement | Why the result is the same |
|---|---|---:|---|---|
| R1 | `copy_registered_evidence`: one `copytree` of the whole parent directory per registered file (3,050 calls, 129.5 GB) | 4,696 s (78.3 min) over the 4 harness runs | Copy each distinct parent directory once (389 calls, 1.79 GB). Measured: 42.1 s per run. | **What every repeated call does**: it copies an unchanged source over the same destination, with `dirs_exist_ok=True`. **The checks**: the per-file path-escape and existence checks stay per file. The symlink walk of a directory gives the same answer every time, because the source does not change during the loop. |

## C. Defect found while classifying (not a speed item)

**D1. The staged-equipment-bypass control passes without testing anything in the nested L2 run.**
- **Why**: L2's fixture is copied from a candidate that already holds the always-PASS validator. So "stage the weakened validator" changes nothing, and git ends with "nothing to commit" (rc=1) after running the hook. The harness counts that rc=1 as a rejection.
- **Evidence**: L2's commit took 31.8 s with no nested run. A small repository showed that git runs pre-commit and then returns rc=1 on an empty commit (`PRE-COMMIT-RAN` then rc 1). Both agree with the code.
- **Limit**: the nested output itself was not captured, so this is an inference.
- **Effect on the real gate**: none. L2 is a run that fails anyway.
- **Fix to consider**: a control that expects a rejection should check that something was staged, and should check the rejection reason, not only rc≠0.

## D. Kept as necessary, with the efficiency question still open

| ID | Process | Time | Why it is needed | Open efficiency question |
|---|---|---:|---|---|
| N1 | Lifecycle control: real commits in a fixture through the real hooks (outer run) | 808 s (13.5 min) | It is the only end-to-end check that the installed hooks reject a missing trailer and weakened staged equipment. | Each fixture commit runs the whole hook, including `validate_process.py` (25-70 s each). Does each control need the whole hook, or only the block it tests? |
| N2 | `validate_process.py`, first read of a fresh tree | 34-44 s per first read, about 8 first reads in the commit | It is the process-integrity gate. | `validate_machinery_claims.py` reads every file under `bomdd/`, `test-results/`, `.agents/` and `tools/`. A first read of a fresh tree takes 34-44 s, and a re-read takes 7-12 s. Can a fixture or a copy share what the first read learned, without changing what is read? |
| N3 | Whole-index copies | 91.5 s (4 copies with their removals) | Each qualification must read the exact prospective index. | Four consumers each write their own copy of the same index. Could one read-only copy serve all four? That needs a check that none writes into its copy. |
| N4 | UI-golden qualification in both hooks | 178 s | It is reciprocal protection. When one hook is edited, the other still runs the check, and this commit edited pre-commit. | When neither hook is edited but golden equipment is staged, the two runs see the same input. Note that the hooks run from the working tree, so "not staged" is not "unchanged". |
| N5 | `validate_process.py` in both hooks | 144 s | Shown on 2026-10-12 (`../viewtube-gate-candidates-20261012/` §2) that the second run cannot be skipped without a fingerprint that is too broad. | None new. |
| N6 | `git add -A` of the whole fixture | 169 s (4 runs) | The fixture must be a repository. | Most of the fixture is the copied evidence. Could less evidence be copied? It must cover what `validate_process.py` requires (the precondition check). |
| N7 | Inspector `dotnet restore` + `build` | 23 s (4 runs) | The harness needs the inspector. | The same project is built 4 times. |
| N8 | Capture-plan sweep for product, harness, fixture or runner changes | 5.2 min when it runs | It is the only check that the plans still run to their end. | The 23 plans run one after another. Could they run in parallel? That needs a check that they do not interfere. |
| N9 | Change-impact trusted harness, UI-golden harness, mutation cases, small validators, probe protocol | about 4 min together | These are equipment qualification and process checks. | Not examined further. |

## E. Flagged for a decision, not proposed here

**The product-UI / expectation coupling** (pre-commit L226-256) costs 0.1 s, but its effect is partly doubtful by its own comment:
- it "will raise where nothing is wrong";
- a whitespace edit clears it;
- it "checks that a document moved, never that the move was correct".

Its cost is friction when it blocks, and that friction was not measured. Whether it belongs in A is the user's call.

## F. Not yet examined

- **BomDD's own record path**: about 6.5-7 min of `self-conformance.py` and 5-6 min of CI per BomDD commit (2026-10-12). Records are now batched to one commit per task.
- **The waits outside the gate**: 59.7% of the 2026-10-11 window (`../viewtube-gate-effect-20261012/`).

## Expected effect if A and B are applied (estimate, from the measured parts)

| Change | Equipment commit time |
|---|---:|
| Measured | 113.6 min |
| + R1 | about 38 min |
| + E1 | about 23 min |
| + E2, for a hook-only commit | about 18 min |

## G. Closure: ViewTube ECO-VT-254 applied (2026-10-12)

**The user's ruling** (verbatim): "1です。また、Aは変えません。Windows Defenderに疑いのもたれないように大量のアクセスや複数回の連続実行をやめればよいはず。B.は変えます。変わることが問題ではなく、変えた後に目的を達成できるかです。"

**What landed, with ViewTube's commits:**
- the filing `5d1053bc`;
- the probe `c7f5dc25`, which was RED on 8 of 8 cases;
- the declaration `a42e06b0`;
- the repair `945d86ac`;
- implemented `4029fc47`;
- applied `7b79469a` (the user's answer "1").

**What applied:**
- **R1.** Each evidence directory is copied once.
- **E1.** The nested qualification stops at its first failure, by a flag the harness sets only for its own fixture commits.
- **C1-C3.** `test-results/` is left out of three index copies.
- **G1.** The fixture runs with `gc.auto 0`.
- **L1.** git is asked once.
- **B1.** The reachability probe's mutation moved to commit-msg. This is the user's ruling B: the probe is still valid on the real hooks, invalid when their UI-golden block is switched off, and starts 0 change-impact processes where it used to start 64.

**What did not apply:**
- **E2 was withdrawn after R8 round 1.** ECO-VT-184's applied claim and CP-CAPTURE-PLANS-RUN-001 both name the hook as a sweep trigger, so E2 needs an ECO of its own that changes those records.
- **The expectation coupling (section E) was not ruled on.**

**Measured effect:**
- The repair commit's gate took **2,373 s (39.6 min)**, against 6,815 s (113.6 min) for the same kind of commit before. The estimate had been about 45 minutes.
- That gate still ran HEAD's old harness. Later equipment commits run the repaired one, which took 756.5 s end to end on a shared machine. With the sweep and UI-golden, an equipment commit is estimated at about 20-25 minutes; that has not been measured on a real commit.
- The ordinary record commits of this ECO took 57-79 s.

**Elapsed time and its causes:**
- The ECO took 2 h 45 min from filing to implemented, against the 1.5-2 h estimate given to the user.
- The difference came from two R8 rounds (round 1 REJECT), the manufacturer's own tooling incident (a line-ending normaliser run over `test-results/` in the working clone), and two repair defects found by the evidence (B1's newline and the sentinel's machinery claim).

**Open:**
- E2, as its own ECO.
- The validator inefficiencies (`hooks-inefficiency.md` sections 2-3).
- Running the sweep's plans in parallel.
- D1, the nested control that passes on "nothing to commit".
- The commit-msg UI-golden exit-status gap that round 1 found (it predates this ECO).
