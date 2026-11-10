# Change Order — ECO-125 (self-conformance in two tiers: a quick run for the work in between, and the full run before a push, which stays where it is)

> Ruling: user, 2026-11-10, "A" — the answer to "この形で ECO の起票に進むか". The thread behind it: a record of one file waited
> 21 minutes for the full check; the user asked whether running everything every time is required or forced by missing impact
> information, recalled an earlier proposal ("作業A, B, C, コミットという場合、A,B,Cはスコープを絞って、コミット前に全件検査、
> みたいな濃淡"), and set the requirement: 「コミットは一例であり、プッシュでも構いません。全件とそれ以外に分けられることが
> 重要です。」
>
> Each part is labelled **stop**, **measure** or **none** (the standing caveat of 2026-10-29). **Filing only.** Manufacture waits for
> the user's start instruction (ECO-106), which also answers the two points of section 1, "For the start instruction". Records are
> English-primary.

## Equipment

- Filing: requested/resolved `claude-fable-5-2`, Claude Code (Claude Agent SDK, desktop app), provenance **self-reported**.
- Producer: not named at filing — the filing model has no entry in `bomdd/70-equipment.yaml`. Named at the start instruction.
- producer: EQ-006
- Independent inspection: none planned (a mode that runs fewer of the same checks and writes no witness; the manufacturer's
  calibration only). The user may name one.

## 0. Measurement (basis of the filing)

- **Today's full run** (this machine, 2026-11-10, tree of `ae5fdb2` plus an unfiled order): total 1,264.7 s; C11 with C11b
  1,253.3 s; the other eighteen checks together 11.4 s (the run's own `[time]` line).
- **How C11 grew**: 201.7 s of 209.7 s on 2026-10-28 (`bomdd/reports/eco-117-self-conformance-cost/survey.md` §1, 27 OQ controls);
  262.8 s after ECO-118; 703.8 s at 70 controls, 940.6 s at 82 controls during ECO-119 (its order, lines 405 and 621); 105
  controls now.
- **What can turn C11 red** (the survey's §3 table): `method/templates/process-core/**`, `bomdd-init.py`, the AGENTS.md template
  and the kit link targets it points into, and the machine's git, Python and OS behaviour. A record commit (`bomdd/**`,
  `method/improvements.md`) touches none of the files.
- **Where the full run is enforced today**: the pre-push hook compares the pushed tree with the PASS witness the full run writes
  (ECO-046, C18). Nothing runs at a commit.
- **What exists for running less**: `--c9-only` (CI's dotnet job, ECO-117), which writes no witness and leaves an existing one.
  No local mode runs less than everything.
- **What is written about it**: OBS-20261106-04, "iterations run the touched arms, and the full suite and the inspection run
  once at the end" — `watch 1/3`, machine face なし. On 2026-11-10 the producer of this filing ran the full check twice on work
  that had no commit yet; no narrower run was there to choose.
- **Declined before, and not reopened here**: skipping C11 when its inputs did not change, with no full run left at the end
  (ECO-105's option 2, 2026-10-12; the survey's J2, 2026-10-29).

## 1. Change request (frozen at filing)

**P1 — the quick tier (measure).** `python method/tools/self-conformance.py --quick` runs every check of the fast tier except
C11 (with C11b), in the same order and by the same functions, and prints each check's line as the full run does. Then:
- one line names what was not run: `[quick] not run: C11 (process-core qualification) — the full run decides before a push`;
- one line says whether C11's file inputs differ from the upstream branch (`git diff --name-only @{u}` plus the working tree and
  untracked files, against the survey's list): `[quick] C11 inputs changed: yes (<n> paths) | no | not determined — <reason>`. It
  is a notice; it changes no verdict and runs nothing;
- **it writes no witness and leaves an existing one byte-identical** (as `--c9-only` does);
- the last line is `self-conformance (quick) passed — C11 を除く検査が合格(全検査ではない・witness なし)` or
  `self-conformance (quick) FAILED — <n> 件の不適合(全検査ではない)`; exit 0 or 1.
`--quick` cannot be combined with `--dotnet` or `--c9-only`.

**P2 — the full tier (stop; unchanged).** The run with no option is as it is today, writes the witness, and is what the pre-push
hook requires. No line of it, of the hook or of CI changes.

**P3 — the entry text (none).** `AGENTS.md` discipline 2 gains one sentence: the single entry has two tiers — `--quick` during
the work, the full run before a push; a quick pass is not a pass for discipline 4.

**For the start instruction (the user's points):**
- **The design is not converged in the form** (converge receipt: 4 → 4 → 0 at the limit of three rounds). Building it as filed is
  the user's cut-off; the other answers are another round or sending the design back.
- **The producer's equipment entry**: if this model manufactures, `bomdd/70-equipment.yaml` needs an entry for
  `claude-fable-5-2`, whose `account_lineage` is the user's declaration.

**Not chosen:**
- **A per-check selection from the changed files** (the survey's whole table as a map): every check but C11 costs 11 s together,
  so selecting among them saves nothing and adds a map that can be wrong.
- **Running C11 inside the quick tier when its inputs changed:** the quick tier would then take 21 minutes on exactly the work
  that iterates on process-core; the notice says so and the worker chooses the full run.
- **The full run at every commit** (a pre-commit hook): the user's requirement is two tiers, with the full one before a push,
  where the stop already is.
- **Skipping the full run when C11's inputs did not change** (J2): declined twice; not this ECO.
- **Making C11 itself faster** (the runner's sandboxes side by side, the survey's S1; a review of the 105 controls): a different
  change, on the template and its distribution; it stays open and this ECO does not depend on it.

## 2. No-impact prediction (before manufacture; frozen)

- **Diff:** `method/tools/self-conformance.py` (the `--quick` mode, about 30 lines), `AGENTS.md` (one sentence), this order, the
  register, `bomdd/reports/eco-125-two-tiers/`; `bomdd/70-equipment.yaml` only if the start instruction names a new entry.
- **Verdicts:** the full run prints the same lines and writes the same witness on the same tree; `--dotnet` and `--c9-only` are
  unchanged; the pre-push hook and the CI workflow are not in the diff.
- **Products:** none changed; the kit does not carry `self-conformance.py`.

**Declared at filing — what this will not do:**
- **The full run still takes 21 minutes**, once per push instead of once per check of the work.
- **A defect only C11 can see is found at the full run**, later than today when the worker ran the full check at every step.
- **The quick tier is a choice, not a stop.** Nothing makes a session use it, or run the full check before trying to push; the
  hook refuses the push.
- **The notice reads files only.** A change of the machine's git or Python is not in it; the full run and CI see those.
- **CI is unchanged**: every push still runs everything on three jobs.

## 3. Acceptance (conditions; frozen at filing)

required_gates: [V1, V2, V3, V4, V5]

**Gated:** V1-V5.

- **V1 — the quick tier is the full tier without C11.** On one tree: every `[Cn]` line of the quick run is byte-identical to
  the same line of the full run; no `[C11]` line is in the quick run; the two `[quick]` lines and the closing line are as P1
  says.
- **V2 — no witness from the quick tier.** With no witness present, a quick pass leaves none and the pre-push hook refuses a
  push of that tree; with a witness present, a quick pass and a quick failure both leave it byte-identical (sha256 before and
  after).
- **V3 — it fails when a check fails, and the notice tells.** On a scratch copy: a register that does not parse makes the quick
  run exit 1 with the `(quick) FAILED` line; a changed file under `method/templates/process-core/` makes the notice `yes`; a
  record-only change makes it `no`; no upstream makes it `not determined`. Known-bad: a copy whose quick mode writes the witness
  turns V2 red, and a copy whose quick mode drops another check turns V1 red; the unchanged copy passes both.
- **V4 — time.** The quick run finishes within 60 s on this machine (three runs); the full run's `[time]` line shows no check
  slower than before by more than the run-to-run spread of two runs.
- **V5 — nothing else moves; the gate.** The full run's output and witness on the filing tree's tool and the changed tool are
  identical apart from the `[time]` line; `--c9-only` unchanged; the diff is inside `allowed_paths`; the full self-conformance
  exits 0 before each push of this ECO; CI is green for each pushed commit (read by the full SHA).

Conditions are frozen at filing; results go to the closing section.

## /preflight receipt (start path: manual — the user's "A" read as the start artifact)

- **Classification**: filing of a decided change (filing only).
- **Baseline `ae5fdb2`**: **confirmed** (HEAD). The working tree also holds another session's uncommitted record
  (`method/improvements.md`, `bomdd/reports/count-survey-20261110/`); this filing does not touch them and commits only its own
  files.
- **Next number 125**: **confirmed** (the last register entry and the last order are ECO-124; an order of this number was
  written and removed uncommitted earlier the same day for a different, withdrawn change — nothing of it is in the history).
- **The modes that exist**: **confirmed** (`--dotnet`, `--c9-only`; `main()` read).
- **C11's inputs and the earlier rulings**: **confirmed** (the survey's §3 and §7 J2; ECO-117's order, "J2 was already declined").
- **No ECO in progress on the same files**: **confirmed** (the one open entry, ECO-079, touches three other files).
- **The producer's equipment**: **missing** — put to the start instruction.
- **Start decision**: **PROCEED_WITH_LIMITS** (filing only).

## Converge receipt (the two tiers; 起動経路: self-triggered at filing)

- 判定: 未収束 (round 軌跡: 4 → 4 → 0; the limit of three rounds reached with one round at zero). The ruling asked for is in
  section 1, "For the start instruction". The rounds are the producer's own.
- DoD (written before the draft of section 1):
  - ✔ D1 two tiers that can be told apart by name, by output and by what they leave behind;
  - ✔ D2 the full tier and its stop are unchanged, and the quick tier cannot stand in for it;
  - ✔ D3 no map or condition whose error lets a failure through unseen — an error only delays it to the full run;
  - ✔ D4 what the quick tier did not run is on its output every time;
  - ✔ D5 the two declined proposals are not reopened by a side door;
  - ✔ D6 each part labelled stop, measure or none; limits and size written.
- round 1 (4): (a) a per-check map from changed files → one rule, "all but C11", since the rest costs 11 s; (b) a quick pass
  mistaken for the pass a push needs → no witness, and its own closing line; (c) C11's inputs outside the repository cannot be
  seen by any file rule → the quick tier claims nothing about C11, and the full run and CI stay; (d) the full run at every
  commit → not what was asked; the stop stays at the push.
- round 2 (4 new): (e) a worker changing process-core would want to know the quick tier is not enough → the notice line; (f) a
  notice that guesses when it cannot tell → `not determined`, never `no`; (g) a quick failure removing a good witness of another
  tree → the witness is left as it is, as `--c9-only` does; (h) AGENTS discipline 2 says "single entry" → one entry, two tiers,
  one sentence.
- round 3 (0 new): D1-D6 against sections 1-3, and the failure types A①-⑧ (⑥: the quick tier's not running C11 is said on its
  output and is not a permission; ⑦: the per-check map, C11-in-quick, the commit hook, J2 and the speed-up are listed as not
  chosen).
- 未収束事項: the form itself. No open finding is known. Whether sessions will use the quick tier is a prediction, not verified
  here; it is measured after application by how often a record-only push is preceded by more than one full run.

## 4. Manufacture (2026-11-10, on the user's "A: 着手する")

The start instruction also answered section 1's two points: the design is built as filed (the cut-off of a design not
converged in the form), and the producer's equipment entry is made with `account_lineage: akiramei@anthropic` (EQ-006).

**What was made** (`0ed8b12`).
- `method/tools/self-conformance.py`: `--quick`, mutually exclusive with `--dotnet` and `--c9-only`; C11 dropped from the same
  list of checks; the two `[quick]` lines, a `[witness]` line and the closing line of P1; `_quick_c11_inputs_notice()`.
- `AGENTS.md` discipline 2: one sentence on the two tiers.
- `bomdd/70-equipment.yaml`: EQ-006 (`claude-fable-5-2`); this order's Equipment section names it.

**A departure from P1, the producer's choice (derived layer).** P1 said the notice compares "against the survey's list". The
list's last item — the AGENTS template's link targets in the kit — cannot be named by a path rule, so the notice counts every
path under `method/` other than `method/improvements.md` as a changed input (the kit is a copy of `method/`). It errs toward
`yes`: changing this tool itself gives `yes`. It still changes no verdict and runs nothing.

**Results** (evidence in `bomdd/reports/eco-125-two-tiers/`; measured in a detached worktree of `0ed8b12` outside the
repository, removed afterwards):
- **V1 PASS** (`v1-v5.txt`, `quick.txt`, `full-changed-tool.txt`): the quick run's 21 `[Cn]` lines are byte-identical to the
  full run's 23 without its two C11 lines; the quick run has no C11 line.
- **V2 PASS** (`v2-v4.txt`): with no witness, a quick pass leaves none and `bomdd/hooks/pre-push`, run with that tree's ref on
  its input, exits 1; with a witness present, a quick pass and a quick failure both leave its sha256 unchanged.
- **V3 PASS** (`v2-v4.txt`): a register that does not parse → exit 1 with `self-conformance (quick) FAILED`; the notice is `no`
  on a clean tree, `yes (1 paths under method/)` with a new file under `method/templates/process-core/`, `no` with a
  record-only change and with a change to `method/improvements.md` alone, `not determined` with no upstream. Known-bad: the
  copy whose quick mode writes the witness left a witness (caught by V2's condition); the copy that also drops C3 lost the
  `[C3]` line (caught by comparing the check ids). The unchanged tool passes both.
- **V4 PASS**: three quick runs 11.9, 11.3 and 13.1 s in the worktree (9.7 s in the main tree). The full run by the changed
  tool took 1,232.2 s and by the filing tree's tool 1,332.6 s, C11 1,221.9 and 1,321.4 s; no other check differs by more than
  0.3 s. One run each, so the spread of two runs that V4 names was not measured; the changed tool is the faster of the two.
- **V5 PASS, with two parts not measured** (`v1-v5.txt`, `full-filing-tool.txt`): on the same worktree the full run's `[Cn]`
  lines, and every other line but `[time]` and `[env]`, are identical by the changed tool and by the filing tree's tool
  (`92fc3cb`, written over the tool file for its run — so its tree differs by that one file, and the two witnesses name
  different trees; both carry `PASS`). The commits are inside `allowed_paths` (`git diff --name-only ae5fdb2 HEAD`).
  **Not measured:** `--c9-only` was not run (it needs the .NET build in the working tree; its branch is untouched but for the
  suffix of the `[time]` line, read from the diff); and no commit of this ECO has been pushed, so the full run in the main
  tree before a push and CI's conclusion are still owed.

**Seen while manufacturing.** The filing commit and the manufacture commit were each checked with the seventeen checks other
than C11 (24.0 s by calling the functions, then 9.7 s by `--quick`) instead of the full run — the mode's first use, on its own
ECO. The two full runs V5 needed took 43 minutes together.

**Declared.** The notice is broader than P1 wrote. `--c9-only` and CI are not measured. Whether sessions use the quick tier is
not shown by any of this.

## 5. クローズ (closure, 2026-11-10, verified with known limits on the user's "A: 受け入れる", manufacturer's calibration only)

- **The ruling.** Shown V1-V5's results and the two parts of V5 not measured (`--c9-only` not run; nothing pushed, so the
  full run before a push and CI are owed), and the notice's departure from P1, the user answered **"A: 受け入れる"**. This is a
  closure with those parts unmeasured, by the human's ruling; it is not a pass of them.
- **Window.** Baseline `ae5fdb2` → filing `92fc3cb` → manufacture `0ed8b12` → record `b2ab175` (diff_audit.head; **the window
  is closed**; the closure commit holds records only: this order and the register).
  - Inside the window (`git diff --name-only ae5fdb2 b2ab175`, 12 paths): the tool, AGENTS.md, the equipment ledger, this
    order, the register and 7 files under `bomdd/reports/eco-125-two-tiers/`. **No path outside `allowed_paths`.**
  - The committed tool is the one measured: `method/tools/self-conformance.py` is unchanged from `0ed8b12`, the commit the
    worktree of V1-V5 was made from, to `b2ab175`.
- **Acceptance results:**
  - **V1 result: PASS** (section 4).
  - **V2 result: PASS** (section 4).
  - **V3 result: PASS** (section 4).
  - **V4 result: PASS** (section 4; one full run by each tool, so the run-to-run spread V4 names was not measured).
  - **V5 result: PASS for what was run; two parts not measured** (section 4) — closed over by the ruling above. No commit of
    this ECO was preceded by the full run in the main tree: each was checked by the checks other than C11, and the full run
    was made twice in the worktree at `0ed8b12`. Nothing is pushed; the full run before the push and CI's conclusion are read
    then, and a red there reopens this ECO.

### 較正 receipt (/calibrate self-application - trigger ①: verified promotion; receipt_author_role = producer; one tool changed)

- **The claim (one sentence).** `self-conformance.py --quick` gives the same verdict lines as the full run for every check but
  C11, in about ten seconds, cannot stand in for the full run at a push, and leaves the full run as it was.
- **査定した主張と判定** (the claims assessed and their verdicts; measurement × evidence):
  - "Quick is the full run without C11" (V1): **observed / eligible** — one tree, both runs, line by line.
  - "A quick pass cannot push" (V2): **observed / eligible** — the real hook run on that tree with no witness, exit 1; the
    witness's sha256 before and after a pass and a failure.
  - "Quick fails when a check fails" (V3): **observed / eligible for one check** (a broken register, C3); the other sixteen
    are covered only by V1's identity of lines on a passing tree.
  - "The notice tells" (V3): **observed / eligible** for five cases on files; it reads no machine state.
  - "The full run is unchanged" (V5): **observed / eligible** for the verdict lines on one tree; **not observed** for
    `--c9-only`, for the push and for CI.
  - "About ten seconds" (V4): **observed / eligible** — four runs on this machine, 9.7 to 13.1 s.
- **検出した計器欠陥と帰属** (instrument defects found, and attribution):
  - `verify125.py` stopped at its first line of output on this machine's console encoding (cp932); attributed to the script,
    repaired (stdout set to UTF-8) before any result was read. No measurement had been taken by the failed run.
  - No defect found in the tool.
- **宣言した検出力の限界** (declared limits of detection):
  - The comparison of the two tools ran on a tree that differs by the tool file itself, so the two witnesses name different
    trees; only their result lines were compared.
  - One passing tree: that quick and full agree on a failing tree is shown for C3 alone.
  - `--c9-only`, the push and CI are not measured. The spread of the full run's time is not measured.
  - Whether a session uses the quick tier, and whether a defect only C11 sees now reaches a push more often, are not measured;
    the second is the cost this ECO accepts.
  - The self-assessment is blind to the manufacturer's own wrong premises (playbook §9); this receipt was written by the
    manufacturer, with no independent inspection.
- **Battery, row by row:**
  - **Q1 asked.** The mode's closing line says "全検査ではない・witness なし"; the notice's `yes` is worded "paths under
    method/", which is what the code counts.
  - **Q2 asked.** Known-good: the unchanged tool; known-bad: the copy that writes the witness and the copy that drops C3,
    each made by a stated one-line change before its run.
  - **Q3 asked.** The two known-bad copies fall on different conditions (V2's and V1's); the notice's five cases fall
    separately.
  - **Q4 asked.** The runs are on the repository's real tree in a worktree, not on a fixture.
  - **Q5 asked.** `--c9-only`, the push and CI are recorded as not measured, not as PASS.
  - **Q6 asked.** Each commit came after an observed exit 0 of the checks other than C11; none after the full run in the
    main tree — said in V5's result.
  - **Q7 asked.** The quick mode prints what it did not run on every run; a silent quick run would be seen by the missing
    `[quick]` lines, which V1's script reads.
  - **Q8 NA.** No preventive gate is added.
  - **Q9 asked.** The worktree was made from `0ed8b12` and the tool is unchanged since; the filing tree's tool was read from
    `92fc3cb` by `git show`.
  - **Q10 asked.** The limits above.
  - **Q11 asked.** The notice's cases keep the classes apart (process-core, records under `bomdd/`, `method/improvements.md`,
    no upstream); a path under `method/` that is not a C11 input is counted `yes` — the stated over-count.
- **What this closure does not support:**
  - that `--c9-only`, a push or CI behave as before;
  - that the full run is faster (it is not changed: 1,232 s);
  - that sessions will use the quick tier.
