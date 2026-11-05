# R8 round 6 — ECO-119 round-6 fix (9328477; round 5 at 4eba600, the design at 70921c3)

**Inspector.** A fresh-context Agent (`claude-opus-5-5`) worked from the brief `r8-119-round6-brief`, narrowed to R8-5-01..08 and the
code changed for them (`70921c3..9328477`). Its sandboxes were minimal products from a `bomdd-init.py` scaffold of this tree, with
the round-6 validator and hooks and `structure_check` removed. Each had ECO-950 open with an order citing `20-spec.md:1-2` and
`adr/ADR-1.md:1`, and `ruled_layer {since: HEAD, paths: [bomdd/20-spec.md, bomdd/adr]}`. The hooks ran through
`core.hooksPath=bomdd/hooks`.

At the end, the inspector reported:
- BomDD `git status --short` was empty and HEAD was `93284775f2b4326e3604b42b5357a019b49d837b`;
- MoviePad-Remake was only read and was clean (HEAD `a2ca41e`);
- `out/` was restored after every run;
- its temp folder, including the qualification's and mutants' sandboxes, was removed.

R8 ECO-119 round 6: **REJECT** — 1 material, 5 minor. R8-5-01..06 are closed, R8-5-07 is closed for its six named mechanisms, and
R8-5-08 is closed with a declared limit. Two of the closures carry a new consequence or variant (R8-6-01, R8-6-03).

## Findings

- **R8-6-01 (material). The new `since` rule can leave a product with no way forward except `--no-verify`.**
  - Cause: round 6 refuses every commit whose index field holds an entry with an off-line or unresolvable `since`. That includes
    entries the commit only carries over unchanged from HEAD. The fix of such an entry is a profile change, which E08 allows only
    when an ECO is open at HEAD. Filing that ECO is itself a commit that carries the entry, so E13 refuses it.
  - Reproduction (all hooked):
    1. On a branch: an entry with `since` = the branch's commit, then its ECO accepted.
    2. Rebase onto main (no hooks run), then fast-forward main.
    3. validate exits 2 (declared).
    4. Filing a new ECO is refused by E13 ("系列に無い"), and so is any unrelated commit.
    5. Re-pointing `since` is refused by E08 (no open ECO), alone or together with the filing.
  - New in round 6: with round 5's validator, the ECO can be filed and the `since` then fixed.
  - Other ways into the state: `git cherry-pick` of the entry commit; a shallow clone that does not reach `since` (an unrelated
    hooked commit is refused, "解決できない").
  - False or incomplete records: 4K's "so the forward fix of an off-line since passes"; playbook §4.5's "squash や rebase の後は
    書き直す"; the template's "その commit は止まる" (after a rebase or cherry-pick it is the next commit that is stopped).
  - Suggested fix: check `since` only for index entries not in HEAD's field (entries the commit adds or changes). This still refuses
    the squash commit (N23v2), the commit that writes an unresolvable `since` (N23n) and a merge that brings an off-line entry in. Add
    an arm: the off-line state reached by a rebase with no open ECO, where filing an ECO and then the fix both pass. Name
    cherry-pick in the template and §4.5.
- **R8-6-02 (minor). The hook change's consequences in a disabled repo are incomplete.**
  - (a) In a repo with no profile in any commit, the validator file removed and the hooks kept, every merge is refused ("validator
    または実行可能な python が見つからない"). Round 5's commit-msg hook allowed it. 4L declares only "needs python with PyYAML".
  - (b) After main removes the profile (the hooks' own "無効化" path), merging a branch from before the removal is refused
    ("ruled_layer を落とす"). This follows ruling B but is not declared. Removing the field on that branch first avoids it.
  - Suggested fix: start the validator on a merge only if some merge parent has the profile (`git cat-file -e <parent>:…` for HEAD
    and each MERGE_HEAD line), and declare (b) in 4L, §4.5 and the hook text.
- **R8-6-03 (minor). An undeclared variant of R8-5-03: the hooks removed together with the profile.** A branch removes the profile,
  both hooks and the tools under an open ECO; a merge with main then goes through either way, and after a fast-forward both layers
  stop. Older than ECO-119 (the hooks are tracked files, ECO-015), and the same end state is reachable by an approved removal (E08),
  so it is a limit, not a bypass. It falsifies 4K's "A merge whose result has no profile, while some parent's profile has the
  field, is refused". Suggested fix: declare it in 4K/4L and §4.5's 止めないもの.
- **R8-6-04 (minor). Validate mode still takes the field from the working tree.** 4K says so, but the docstring ("作業ツリーと
  `HEAD:` への縮退は E13 の入力にしない"), §4.5 and the register comment ("every E13 input read from git") overclaim. Measured: with
  no profile at HEAD, an untracked working-tree profile with an unresolvable `since` makes validate exit 2; an untracked
  working-tree field makes validate report a hooked commit the first layer accepted. Suggested fix: run the E13 replay only when HEAD
  has the profile, or reword the three records.
- **R8-6-05 (minor). One round-6 mechanism is exercised by no arm.** "A parent's profile that does not parse is unmeasurable": the
  inspector's mutant `parent-lenient` fails 0 of 50 arms. Its other mutants are covered: `hook-no-merge-head` fails N23x6 only,
  `since-head-only` fails N23s only. The hooks' known-bad named in 4L (the first full run) has no evidence file in `out/`; the
  pre-commit index clause is covered by no arm (it adds nothing for E13). Suggested fix: an arm with a merge parent whose profile
  has a duplicate key (expect exit 2); keep the hooks' known-bad as an `out/` file or as hook mutants.
- **R8-6-06 (minor).** The register comment cites "order sections 4J/4K" for round 6; the manufacture is in 4L.

## Answers to the brief's questions

- **Q1, round 5's closure.**
  - R8-5-01 closed: the `a\x01<C2>` path is reported; the inverse `z\x01<40 zeros>` is reported instead of exit 2.
  - R8-5-02 closed: A1 and A2 refused, and with `--no-verify` the replay reports A2.
  - R8-5-03 closed for the reproduction: `-s ours` and plain merges refused, and so is a modify/delete conflict concluded with
    `git commit`. The variant is R8-6-03.
  - R8-5-04 closed: duplicate keys in the field and elsewhere refused (exit 2), also in a product without the field; the next commit
    is not bricked.
  - R8-5-05 closed.
  - R8-5-06 closed for both forms, with the new consequence R8-6-01.
  - R8-5-07 closed for the six named mechanisms; the remainder is R8-6-05.
  - R8-5-08 closed with a declared limit.
- **Q2, holes.** None beyond R8-6-03. In the hook modes no E13 input is read from the working tree in a way that changes the judgment.
  The order read has no `HEAD:` fallback, profiles are parsed strictly and paths are framed by position. The hooks start the
  validator for index-only profiles, merges with no profile at HEAD and conflicted merges concluded with `git commit`.
- **Q3, false refusals.** R8-6-01, including the shallow-clone form. Whole validation of the index's profile refuses nothing the
  validator would otherwise accept. The hook change refuses every merge in a profile-less repo without the validator (R8-6-02a).
- **Q4, layer parity.** The order read and the index profile agree between the layers. First layer accepts and replay reports: only
  through validate's working-tree read (R8-6-04). The other direction: R8-6-01.
- **Q5, evidence.**
  - Selftest: 105 PASS.
  - Mutants name-only, wt-profile, exit-first and since-touched-only re-run: each fails exactly its arms, matching `out/` apart from
    one SHA.
  - V1: PASS (KB2: 5 E13).
  - V2 and V3: read from `out/`.
  - The inspector's own mutants: see R8-6-05.
- **Q6, records.**
  - True: 4L's counts (50 arms, 13 mutants, 105 selftest) and the template's squash rule.
  - False: R8-6-01, R8-6-03 and R8-6-04.
  - Incomplete: R8-6-02, cherry-pick and shallow clones (R8-6-01), and R8-6-06.

## The inspector's verdict

REJECT. R8-6-01 is a permanent red that round 6 introduced, and the records claim the opposite. The single-point fix is to check
`since` only for the entries the commit adds or changes, with one arm.
