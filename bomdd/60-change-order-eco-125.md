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
