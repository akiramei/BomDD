# R8 round 5 — ECO-119 round-5 fix (4eba600; round 4 at 9f586b8)

**Inspector.** A fresh-context Agent (`claude-opus-5-5`) worked from the brief `r8-119-round5-brief`, with the full scope of round 5
(the design of order 4H and the fix of 4I). Its sandboxes were throwaway products from `bomdd-init.py` in its own temp folder, each
with the round-5 validator, `ruled_layer {since: HEAD, paths: [bomdd/20-spec.md, bomdd/adr]}`, ECO-950 open and an order citing
`20-spec.md:1-2` and `adr/ADR-1.md:1`.

At the end, the inspector reported that BomDD `git status --short` was empty and HEAD was
`4eba6009d28e1ccfafffadfeb0d1be5d0ab18aed`, that MoviePad-Remake was clean (only read), that `out/` had been restored with
`git checkout --` and that its temp folder had been removed. Six qualification sandboxes from its OQ runs remain under the user's
temp folder (`bomdd-oq-*`, about 3.7 MB each), because the qualification does not delete its own and its sweep of the shared temp
folder was refused.

R8 ECO-119 round 5: **REJECT** — 4 material, 4 minor. All round-4 findings are closed (R8-4-05 and 07 with declared limits).

## Findings

- **R8-5-01 (material). The replay can be blinded by a crafted path.**
  - Cause: `diff_tree_paths` splits git's output on `\x01`, which can also occur inside a path.
  - A path `a\x01<SHA>` turns the rest of a commit's path list into a fake chunk for `<SHA>`. If `<SHA>` is a commit in the range
    for which git printed nothing (an empty diff), the guard `sha in out` does not fire and the following paths are credited to it.
  - Reproduction: an empty commit C2 carrying a ruling; a `--no-verify` commit C (made with `mktree`/`commit-tree`) that changes the
    spec without a trailer and adds the root file `a\x01<C2>`. `diff_tree_paths` returned `{C: ['a'], C2: ['bomdd/20-spec.md']}`;
    validate exit 0 (control without the odd path: exit 1, E13 history:C). The same with C2 = a `-s ours` merge with a ruling.
  - Inverse: a path `z\x01<40 zeros>` makes validate exit 2 for good; it recovers only by moving `since` past that commit.
  - Suggested fix: framing a path cannot imitate (`diff-tree --stdin -r --raw -z --no-renames`, parsed by position), and an arm with
    a `\x01` path made with plumbing.
- **R8-5-02 (material). The first layer reads the order from HEAD when the commit deletes it.**
  - Cause: `order_text_of` tries `:ref`, then falls back to `HEAD:ref`; the replay reads the commit's own tree. Present in round 4.
  - A ruled spec change plus `git rm` of the order, hooked: exit 0; validate exit 1 ("指示書 … が無い"). The same when the order is
    moved and `order_ref` updated in the same commit.
  - The hooked commit stays red for good. This contradicts playbook §4.5 and the docstring ("the same judgment").
  - Suggested fix: read `:ref` only. No arm exercises this read (mutant `order-head`: 0 arms FAIL).
- **R8-5-03 (material). A merge drops the field when the first parent has no profile file.**
  - Cause: `main()` returns "profile なし — 素通し" before E13 when HEAD and the working tree both lack the profile, so the merge
    field check never runs.
  - Branch b removes the profile under an open ECO (E08, hooked); main moves on; on b, `git merge -s ours main` is accepted and the
    result has no profile; after main fast-forwards to b, an untrailered spec change is accepted and validate says "profile なし".
    Control: b removes only the field, then the same merge is refused.
  - This deviates from ruling B of round 3, and 4H's "a merge whose result lacks the field is refused whenever some parent has it"
    is false here.
  - Suggested fix: during a merge, run the git-only field check before the no-profile exit, or load a parent's profile.
- **R8-5-04 (material). The index's field is parsed with a looser loader than HEAD's.**
  - Cause: `index_ruled_layer` and `ruled_layer_of` use `yaml.safe_load`; HEAD's profile is read with `strict_load`.
  - A second `since:` key in the index's `ruled_layer`, hooked with an open ECO: exit 0. Every later commit is refused
    ("重複キー 'since'"), validate exits 2, and a hooked restoring commit is refused too; only `--no-verify` recovers.
  - 4H's "a malformed field in the index … refuses the commit" is false for this form. A duplicate key anywhere in a staged profile
    bricks the same way; that general form is older than ECO-119.
  - Suggested fix: `strict_load` in both; better, `validate_profile` on the whole index profile whenever it is staged. No arm
    exercises the index parse failure (mutant `index-lenient`: 0 arms FAIL).
- **R8-5-05 (minor). A profile restored in the index only is not judged by the first layer.**
  - Same root as R8-5-03: `load_profile` falls back to the working tree, not the index.
  - Profile removed under an ECO, then restored with `git restore --staged --source=<rev>` (the working tree still lacks it), plus an
    untrailered spec change: exit 0; the replay reports it. Within the declared limit, but 4H's "the commit that adds or restores an
    entry is judged under it" (N23z9) is false for this flow. When HEAD lacks a profile, the trailer name, register path and open
    states also come from the working tree.
- **R8-5-06 (minor). The recorded practice plus the recorded remedy leaves `since` off main's line.**
  - An entry added on a feature branch with `since` = the feature's HEAD, then squash-merged into main (the remedy 4H names): main's
    validate exits 2 ("since … が HEAD の系列に無い"), which stops every check; a properly ruled change is refused as unmeasurable.
    An E08 commit re-pointing `since` recovers.
  - Related: an index `since` that is well-formed but unresolvable, in a commit touching no ruled path, is accepted; validate then
    exits 2.
  - Suggested fix: declare it (template comment and 4H), or refuse at commit an index `since` that does not resolve or is not HEAD or
    an ancestor (of some parent, for a merge).
- **R8-5-07 (minor). New mechanisms that no arm exercises.** Mutants run as a full OQ with the 44 N23 arms:
  `order-head` (order read from `HEAD:` only), `index-lenient` (an unparsable index profile taken as "no field") and `frame-trust`
  (`diff_tree_paths` without its want/duplicate guard) each fail 0 arms. The replay's guard "since の後の親が無い" cannot be reached.
- **R8-5-08 (minor). Timing is only partly declared.** 4I gives the direction (cost grows with commits after `since`) but no figure,
  and leaves out the order read (one `git show` per named ECO per touched commit). Measured: 300 commits after `since` (150 ruled),
  validate 20.5 s / 21.5 s with E13, 0.9 s without; under load 13.7 s at 100 commits and 48.9 s at 300. Not a regression from round
  4. Suggested: declare the figure, or batch the reads (`git cat-file --batch`).

## Answers to the brief's questions

- **Q1, round 4's closure.** R8-4-01, 02 and 04 closed; 03 closed with residual R8-5-05; 05 and 07 closed with declared limits; 06
  closed for the seven listed mutants, the remaining gaps being R8-5-07.
- **Q2, holes.** R8-5-01 and R8-5-03. Found sound otherwise: octopus merges, `-s ours` merges with the field, merges whose first
  parent is before `since`, criss-cross, rebase and cherry-pick (judged by the replay), renames and deletions, duplicate and
  overlapping entries with different sinces, `since` equal to HEAD, the index's field differing from HEAD's, empty diffs, non-ASCII
  paths. By induction over the base chain, the replay sees every ruled-file change between `since` and HEAD; framing is its only gap.
- **Q3, false refusals and permanent reds.** R8-5-02 (recovered only by moving `since`), R8-5-04 (only `--no-verify`), R8-5-06
  (recoverable with an E08 commit).
- **Q4, layer parity.** R8-5-02 and R8-5-05 (the first layer accepts, the replay reports). No case of the reverse found.
- **Q5, evidence.** Selftest 102 PASS. Mutants `strict`, `no-index` and `first-parent` re-run: each fails exactly its expected arms,
  identical to the committed `out/` files apart from SHAs. V1 PASS (KB2: 5 E13). `out/v2.txt` and `out/v3.txt` read, not rerun.
- **Q6, records.** False: §4.5 and the docstring "同じ判定" (R8-5-02); the three 4H sentences named in R8-5-03, 04 and 05. Missing
  from the declared consequences: R8-5-06. Timing: acceptable in direction only (R8-5-08). Everything else checked is true of the code
  (the 4I counts, the register comment, the template comment's rules, the fast path being exact).

## The inspector's note on causes

R8-5-03 and R8-5-05 share one cause (the no-profile exit reads the working tree, not git); R8-5-02 and R8-5-04 are one-line fixes.
