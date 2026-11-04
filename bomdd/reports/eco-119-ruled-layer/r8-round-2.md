# R8 round 2 — ECO-119 round-2 fix (00f3ae2, round 1 at 3d16181)

**Inspector.** A fresh-context Agent (`claude-opus-5-5`) working from the brief `r8-119-round2-brief`: six questions, with the five
rulings stated. It was read-only on BomDD. Its throwaway products and temp folder were removed and out/ was restored; `git status`
was clean at 00f3ae2. Below is a summary of its final message, with its findings and verdicts as it gave them.

R8 ECO-119 round 2: **REJECT** — 3 material, 4 minor. Ruling 5:A made this round the last, so the work stops for the user.

## Findings

- **R8-2-01 (material).** A merge into a branch forked before the field can drop the field without an ECO and without a bypass flag.
  After a fast-forward, HEAD's profile has no field, so both layers are off.
  - Reproduced with `-s ours`, and with `--no-commit` followed by restoring the old profile.
  - Cause: E08 compares the staged paths with HEAD only. Round 2 reads MERGE_HEAD's field only to judge the ruled-path diff.
  - The following become false: the profile comment (「削除は本ファイルの変更= E08 を通る」), section 2's limit, and 4A's "now true".
  - Fix: diff the equipment against every merge parent, or have E13 refuse a merge whose result drops the field its boundary parent
    had. Otherwise correct the three texts.
- **R8-2-02 (material).** The replay judges by parent (a commit is judged only when its parent's profile has the field). This differs
  from ruling 3:A's text ("the later of `since` and the field's introduction") wherever the field was removed and later re-added. A
  ruled change in that window is reported by neither layer, and 4A does not record the difference.
  - Fix: a cutoff like E01's `replay_cutoff` (the oldest commit on HEAD's line that has the field), or a ruling that accepts the
    per-parent reading as a limit.
- **R8-2-03 (material).** When the profile does not parse, or is empty, `has_field` counts it as "no field". A `--no-verify` ruled
  change right after it escapes the replay (fail-open). Fix: judge the commit, or exit 2; add an arm.
- R8-2-04 (minor). In an octopus merge, the first layer combines HEAD with the first MERGE_HEAD line only (`parent_registers`); the
  replay combines all parents. Both directions were reproduced. E01 has the same gap.
- R8-2-05 (minor). The replay judges all history with HEAD's `paths` and trailer name. Extending `paths` turns commits the hook
  accepted into permanent reds. Fix: read the values from the boundary parent's profile, or declare the limit.
- R8-2-06 (minor), gaps in the records:
  - (a) cherry-pick, revert and rebase run no commit-msg hook, and only `--no-verify` and amend are declared;
  - (b) the commit that introduces the field can carry a ruled change that is not judged;
  - (c) ruling 1:A's cost applies in both directions, and B's outcome is reachable for branches forked after the field: a sync merge
    of main into the branch, then a fast-forward, with each branch commit still judged;
  - (d) nits: 4B's wording about the refusal text, and the `_oq_ruled_layer` docstring's "N23a〜x".
- R8-2-07 (minor). `repo_rel_path_ok` accepts `:`. An `order_ref` of `0:bomdd/...` reads as index stage 0 in the first layer and is
  missing in the replay: a parity break that ends in a permanent red. Fix: refuse `:`.

## Answers

- **Q1.** R8-1-01..11 are all closed. R8-1-08 and R8-1-09 are closed with declared limits. For R8-1-03 the "E08 records it" claim
  fails through a merge (R8-2-01); for R8-1-10, see R8-2-02.
- **Q2.** The message parity holds: `core.commentChar` (`;`, `auto`, `%`), `-F -e`, `-v -e` and `-F --cleanup=verbatim` all behaved as
  stated. Parity breaks in R8-2-04, 05 and 07. Cherry-pick, revert and rebase are caught by the replay.
- **Q3.** 1:A is implemented faithfully: the second rule only adds refusals. B's outcome is reachable through topology (R8-2-06c). 3:A
  differs from its text in removal windows (R8-2-02). 2:A and 4:A are implemented as ruled.
- **Q4.** New holes: R8-2-01, 03 and 07. A new source of permanent reds: R8-2-05.
- **Q5.**
  - V1 rerun: PASS. V2/V3 rerun in full: PASS, byte-identical to out/. Selftest: 98 PASS.
  - N23 discriminates. In mutants of the installed validator, each mutation failed its arm: `-z` dropped → N23m; first parent only →
    N23s; parity check removed → N23k and N23q; field gate always true → N23m; merges not candidates → N23m.
  - No arm covers an octopus merge, a dropped field, a profile that does not parse, or a removal window.
- **Q6.**
  - True: T1 (`since`, `paths`), the T2 parity check, D3, D6, D8, D12, D13 (apart from `:`), D14, D15 and 4B's counts.
  - Not true or incomplete: the boundary and "now true" (R8-2-01), 3:A's text (R8-2-02), the octopus register (R8-2-04), D7's cost
    (R8-2-06c), the declared bypasses (R8-2-06a, b), and 4B's wording.
