# R8 round 7 — ECO-119 round-7 fix (a021984; round 6 at 9328477, the design at 93053f8)

**Inspector.** A fresh-context Agent (`claude-opus-5-5`) worked from the brief `r8-119-round7-brief`, narrowed to R8-6-01..06 and
the code changed for them (`9328477..a021984`). Its sandboxes were copies of a `bomdd-init.py` scaffold of this tree, with
`structure_check` removed and the hooks through `core.hooksPath=bomdd/hooks`. Each had ECO-950 open, its order citing the spec,
ADR-1, the E-BOM and the requirements as `path:line`, and `ruled_layer {since: <setup commit>, paths: [bomdd/20-spec.md, bomdd/adr]}`.

At the end, the inspector reported:
- BomDD `git status --short` was empty and HEAD was `a021984a5a3e2cf7b2f094f37b85cd95453d5f8c`;
- MoviePad-Remake was only read and was clean (HEAD `a2ca41e`);
- `out/` was restored after V1 (one SHA changed); one brief run rewrote `out/r5kb-since-all.txt` byte-identically;
- its temp folder, including the qualification's sandboxes, was removed. Eight `bomdd-oq-*` folders in `%TEMP%` were there
  before its runs and were left alone.

R8 ECO-119 round 7: **ACCEPT** — 0 material, 3 minor. R8-6-01..06 are closed; R8-6-02 has a remaining variant (R8-7-01).

The inspector notes that R8-7-01 is a wrong record, which the brief's literal rule ("a false claim in the records") would class
material. It rated it minor as round 6 rated R8-6-02 and R8-6-04, and left the class to the user.

## Findings

- **R8-7-01 (minor; material under the literal rule).** In a product with the validator removed, a merge whose other parent still
  has the profile is refused ("validator または実行可能な python が見つからない").
  - This holds in either direction, and whether or not that branch's profile has `ruled_layer`. So it also hits products that
    never opted into E13. Round 5's hook let these merges through.
  - The recorded remedy "先にその枝で欄を外す" does not work there. After the field is removed on the old branch (hooked, passes),
    the merge hits a modify/delete conflict on the profile. `git rm` and `git commit --no-edit` is still refused. With the
    validator restored on main, the same resolution passes.
  - Wrong or incomplete records: commit-msg's comment ("profile を撤去し validator も外した製品の merge を止めない" and "先にその枝で
    欄を外す"), playbook §4.5's remedy, and order 4N and 4O.
  - Suggested fix: the remedy becomes "remove the profile on that branch first (E08 under its ECO), or keep the validator until
    such branches are merged". Declare that, with the validator removed, a merge of any branch that still has the profile is
    refused. Do not grep the profile for `ruled_layer` in the hook: flow-style YAML or a quoted key would get past it.
- **R8-7-02 (minor).** The recorded forward fix for an off-line `since` narrows the replay, and it is the wrong fix for a shallow
  clone.
  - (a) Rebase. N23rb and the records re-point `since` to HEAD, which drops every commit between the rebased entry commit and
    HEAD from the replay. Measured: a `--no-verify` change to `bomdd/30-ebom.yaml` in the rebase state, then a hooked ECO filing.
    With `since` at HEAD, validate exits 0 and never reports the change. With `since` at the rebased copy of the entry's commit,
    validate exits 1 and reports it.
  - (b) Shallow clone. There `since` is only missing from the local history, not off the line. Rewriting it moves the boundary
    for the full repository too; the right fix is to deepen the clone (`git fetch --unshallow`). The template and §4.5 say
    "ECO を起票して since を書き直す" for shallow clones, and the "解決できない" message gives no hint.
  - Suggested fix: "re-point to the rebased or cherry-picked copy of the commit the entry named"; for a shallow clone, "deepen the
    clone; do not rewrite `since`", with that hint in the "解決できない" message.
- **R8-7-03 (minor).** Two round-7 mechanisms have no arm.
  - The inspector's mutant `i1`: `merge_parent_has_profile` reads only the first `MERGE_HEAD` line (octopus parents 2 and later
    ignored). It fails 0 of 54 arms.
  - The inspector's mutant `i2`: at a merge, the `since` check skips every entry (an entry brought in from another parent goes
    unchecked). It fails 0 of 54 arms.
  - Both mechanisms work in the code. An octopus `-s ours` into a profile-less HEAD, with the profile only on `MERGE_HEAD` line 2,
    is refused ("ruled_layer を落とす"). A merge whose result carries the second parent's off-line entry is refused
    ("どの親の系列に無い").
  - Suggested fix: one arm for each; optionally keep `i1` and `i2` as mutants.

## Answers to the brief's questions

- **Q1, round 6's closure.**
  - R8-6-01 closed. Rebase (all hooked): validate exit 2 ("系列に無い"); an unrelated commit and an ECO filing exit 0; a ruled
    change under the entry is refused; re-pointing `since` exits 0, then validate exits 0. Cherry-pick: the same. Shallow clone
    (`--depth 2`): validate exit 2 ("解決できない"); unrelated commit and filing exit 0; a ruled change is refused.
  - R8-6-02 (a) closed (the x7 merge exits 0). (b) declared, but its remedy is wrong with the validator removed (R8-7-01).
  - R8-6-03 closed with a declared limit. R8-6-04 closed (validate exits 0 with no E13 for both working-tree probes). R8-6-05
    closed. R8-6-06 closed.
- **Q2, holes.** None beyond the declared limits. An entry's effect is exactly its `(path, since)`, so skipping carried-over
  pairs is safe. Probes: string form to `{path, since}` with the same pairs; the field's `since` moved off the line while every
  entry keeps its own (the value is then unused; adding a string entry is refused); merges into a profile-less HEAD in a linked
  worktree and as an octopus (refused); a `MERGE_HEAD` commit whose profile has a duplicate key (exit 2); a merge bringing in an
  off-line entry (refused); a first parent carrying one (touches refused). Outside the stop: R8-7-02(a).
- **Q3, false refusals.** R8-7-01, with a forward way. Removing pre-commit's index clause loses nothing: on the same index,
  pre-commit and commit-msg modes report the same E01 and E03.
- **Q4, layer parity.** No new mismatch, apart from R8-7-02(a).
- **Q5, evidence.** Selftest 105 PASS. `since-all`, `hook-merge-any` and `wt-replay` each fail exactly their arms. The
  inspector's `skip-by-path` fails N23v; `i1` and `i2` fail none (R8-7-03). V1 PASS. V2 and V3 read from `out/`. Its first runs
  of long-named mutants also failed N23rb with "Filename too long" in `git rebase` under its deep TMP path; a control without
  mutation passed and short-named reruns passed, so that was its setup. N23rb is the arm that breaks first when TMP is deep.
- **Q6, records.** True: 4N/4O, the register comment, the docstrings, the template and pre-commit comments, and the mutant
  table. Wrong or incomplete: R8-7-01 and R8-7-02.

## The inspector's verdict

ACCEPT: no material findings. R8-7-01..03 should be fixed or declared at closure. R8-7-01 is the one to recheck under a strict
reading of the records-claim rule.
