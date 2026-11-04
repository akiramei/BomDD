# R8 round 1 — ECO-119 manufacture (3d16181, baseline 42a6158)

Inspector: a fresh-context Agent (`claude-opus-5-5`), brief `r8-119-brief` (six questions, ECO-118's hook lessons named). Read-only;
its throwaway product (release tag on main, a branch forked before it) and temp folders removed; out/ restored. Summary of its final
message (findings and verdicts as it gave them):

R8 ECO-119 round 1: REJECT — 3 material, 8 minor.

- **R8-1-01 (material)** — a branch forked before the release and merged after it escapes both layers with `--no-verify`: the replay's
  `--ancestry-path` drops the branch's commits (not descendants of since) and `diff-tree --cc` is empty for a clean merge; `-X theirs`
  can even replace ruled content silently. D7's "the branch's own commits are judged themselves" is false for such a branch. D8 came
  from V1/N23's side-branch release topology; KB2 shows only that the flag suppresses reports. Fix: judge a merge by its first-parent
  diff (what the first layer sees) with the combined parent registers; reconsider `--ancestry-path`; an arm with the tag on main.
- **R8-1-02 (material)** — the replay's `diff-tree` lacks `-z`, so git quotes non-ASCII paths (`ADR-日本.md`) and `ruled_paths_touched`
  misses them: a `--no-verify` commit escapes; the first layer (with `-z`) refuses. Fix: `-z`; an arm.
- **R8-1-03 (material)** — `since` as a tag can be moved (`git tag -f`) with no diff: moved forward, the replay stops reporting; moved off
  HEAD's line, both layers stop silently. Section 2 and the profile comment ("moving since is a profile change E08 records") are false
  for the tag form §7 recommends. Fix: require a full commit SHA, or treat a since not on HEAD's line as unmeasurable (exit 2) and
  correct section 2 (a ruling).
- R8-1-04 (minor) — the first layer and the replay read the message differently: `-m x -m "BomDD-ECO-Ruling: ECO-901" -m "# note"`
  passes the hook (the comment-candidate strip makes the trailer final) but git stores `# note` (cleanup=whitespace for `-m`) and the
  replay reports it — red history with no forward fix. For E12 stripping more only fires more; for E13 it can pass what T2 refuses.
- R8-1-05 (minor) — the change-order template's example `bomdd/20-spec.md:120-134` counts as a citation: an untouched template satisfies
  T3 for the spec. Fix: a placeholder the regex ignores.
- R8-1-06 (minor) — `paths` entries that never match (a directory without `/`, a backslash) pass `validate_profile`: a silent disable.
- R8-1-07 (minor) — N23 hard-codes the trailer name (ECO-024's rule); with `trailers.ruling` set, D6 (one valid id suffices) conflicts
  with E07 (an unknown id in a trailer is reported).
- R8-1-08 (minor) — an amend of an ECO's filing commit adding a ruled change with that ECO's trailer passes the hook (HEAD's register has
  it open); the replay catches it. Declare with D12.
- R8-1-09 (minor) — D7's cost is understated: a merge of a post-release branch whose ECO was filed, used and applied there is refused,
  and naming that ECO is refused too ("open でない"); only an unrelated open ECO passes.
- R8-1-10 (minor) — `since` = the release tag makes the replay judge commits made before the field existed (V6 predicts 6 permanent
  reds for MoviePad-Remake, no forward fix). E01 uses the field's introduction as its cutoff. A ruling for the distribution ECO, or the
  later of since and the introduction.
- R8-1-11 (minor) — evidence notes: V2's frozen "known-bad of the gate itself" is in V1, not in N23 (relocation unrecorded); N23m's
  `"sneaked" not in` check is vacuous; `order_ref` is not sanitised (`/Sources read` became a commit-message search; fails closed).

Answers: T1-T3 as written apart from R8-1-04/05/06; T4 not met for merges (R8-1-01). D1, D2, D4, D5, D9, D10, D11 match; D3, D6+D10, D7,
D8, D12 need a ruling or correction. Hook-refused as stated: `commit -a`, `--only`, `commit -- path`, rename into the ADR directory,
case-only rename, deletion, a trailer in a non-final paragraph; replay-caught: cherry-pick, a rebase putting the change before its
filing, a fast-forward of a post-release `--no-verify` commit; a conflict resolution in a merge caught (`--cc`). Evidence re-runs: V1
the same apart from regenerated shas; V2/V3 byte-identical; CI on 3d16181 success (run 40891374976).
