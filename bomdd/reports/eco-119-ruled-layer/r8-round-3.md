# R8 round 3 — ECO-119 round-3 fix (1cd891b; round 2 at 00f3ae2)

**Inspector.** A fresh-context Agent (`claude-opus-5-5`) working from the brief `r8-119-round3-brief`. The round was narrowed to the
round-3 changes and the seven round-2 findings, with rulings 1:A (narrowed by B), 2:A and 3:A stated. Below is a summary of its
final message, with its findings and verdicts as it gave them.

R8 ECO-119 round 3: **REJECT** — 2 material, 6 minor. Ruling 3:A made this round the last, so the work stops for the user.

## Breach of the read-only rule (disclosed by the inspector, checked by the session)

- A `cd` into a sandbox failed: its glob matched both the folder and its `.gitconfig`. The rest of that command ran in BomDD.
- It made two local commits on `main`, `9eb1e0e n2` and `a8b3079 n3`, each adding a file under `bomdd/`. Neither was pushed.
- No commit hook ran: BomDD's hooks folder holds only `pre-push`.
- The inspector undid them with `git reset -q --mixed 1cd891b` and deleted the two files.
- Checked by the session afterwards: HEAD and `origin/main` are both `1cd891b`, `git status --short` is empty, and neither file exists.
  The reflog keeps the two entries and the reset.

## Findings

- **R8-3-01 (material).** The replay's path filter takes the union of every profile version's `paths` without checking the entries,
  and passes them to `rev-list -- <paths>` as git pathspecs.
  - Only `values_at` checks entries with `repo_rel_path_ok`.
  - A side-branch commit that adds `:(exclude)bomdd` to `paths` passes E08 when an ECO is open. Merged into main with `-s ours`, it is
    allowed by ruling B.
  - From then on the replay reports no E13 in the whole history, earlier `--no-verify` changes included.
  - A `../outside` entry makes validate exit 2 on every run.
  - Fix: keep only entries that pass `repo_rel_path_ok`, and/or use `--literal-pathspecs`; add an arm.
- **R8-3-02 (material).** A narrowing window escapes the replay, while a removal window does not.
  - Narrow `paths` (E08), make a ruled change without a trailer, then restore `paths`: the replay does not report the change, because
    the values come from the base parent's profile (R8-2-05's fix).
  - Fix: judge an entry when the base parent's `paths` hold it, or when HEAD's `paths` hold it and some version at or before the base
    parent held it.
- R8-3-03 (minor). Ruling B's merge refusal exists only in the first layer. The playbook's and the docstring's "the replay detects the
  same" read as if it were repeated. Changing the field with `--no-verify` (merge or not) is not declared.
- R8-3-04 (minor). B's cost is not declared. Two branches that each extend `paths` cannot be merged with the union of their entries;
  the workaround is to take one parent's field, then add the other in a separate commit.
- R8-3-05 (minor). The declared residual is narrower than what the code allows. A branch that drops the field in its own commit can
  also be merged straight into main. Fix: word the residual generally.
- R8-3-06 (minor). In a removal window `values_at` falls back to HEAD's values. A file created in the window, under an entry added when
  the field is restored, becomes a permanent red. Fix: fall back to the nearest ancestor's well-formed field.
- R8-3-07 (minor). Every hooked commit walks every profile version, even when it touches no ruled path. With 152 profile versions a
  non-ruled commit took 18.2 s and 14.4 s, against 2.7 s on `00f3ae2`. Real products today have 0 or 1 versions.
  - Fix: for a non-merge commit, compute `touched` first; batch the blob reads.
- R8-3-08 (minor). N23u tells round 2 from round 3 only by its expected text: on `00f3ae2` the merge is refused by E05 (no accept
  trailer). Fix: add the accept trailer to N23u.
- Out of scope (noted): E01's octopus gap, as declared.

## Answers (summary)

- **Q1.**
  - R8-2-01: closed with a declared limit, but the limit is wider than declared (R8-3-03, 05).
  - R8-2-02: closed for removal; narrowing is open (R8-3-02).
  - R8-2-03: closed; the choice not to exit 2 closes the fail-open.
  - R8-2-04: closed for E13, in both directions.
  - R8-2-05: closed for extension. Round 3 introduced R8-3-01, 02 and 06.
  - R8-2-06, R8-2-07: closed.
- **Q2.** New holes: R8-3-01 and 02. New permanent reds or unmeasurable states: R8-3-01's `..` variant and R8-3-06. B does not reopen
  R8-2-01 through `-s ours`, `--no-commit`, `-X ours` or an octopus.
- **Q3.** The first layer matches B's text and 2:A's text. The gaps are the undescribed costs and limits.
- **Q4.**
  - Selftest: 99 PASS.
  - `verify119_r3kb.py 00f3ae2` and `--letter` both behave as recorded.
  - V1: PASS.
  - `out/v2.txt` and `out/v3.txt` were read, not rerun.
  - No arm covers R8-3-01, 02 or 06.
- **Q5.** The records are true except as listed in R8-3-02 to 05 and 08.
