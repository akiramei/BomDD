# R8 round 4 — ECO-119 round-4 fix (9f586b8; round 3 at 1cd891b)

**Inspector.** A fresh-context Agent (`claude-opus-5-5`) worked from the brief `r8-119-round4-brief`. The round was narrowed to
R8-3-01..08 and the parts changed for them. The brief added safety rules: `git -C <absolute path>` only, and no `cd` in compound
commands.

At the end, the inspector reported that BomDD `git status --short` was empty and HEAD was `9f586b8`, that MoviePad-Remake was clean,
that out/ had been restored and that its temp folder had been removed.

R8 ECO-119 round 4: **REJECT** — 4 material, 3 minor.

## Findings

- **R8-4-01 (material).** A narrowing window still escapes the replay if the entry is restored with a different spelling.
  - Restoring `bomdd/adr` as `bomdd/adr/`, or as the broader `bomdd`, leaves the window commit unreported.
  - Cause: `held_at` and `values_for` compare entry strings, while `ruled_paths_touched` matches by path coverage.
  - Fix: decide "held" per touched path, by coverage.
- **R8-4-02 (material).** An entry held only on a side branch that was merged with `-s ours` turns a later hooked commit into a
  permanent red once main adds the entry.
  - Cause: `held_at` counts any ancestor version, including the side branch's.
  - This contradicts 4F, §4.5 and the docstring: "an extended entry does not judge earlier commits".
  - The report text "第 1 層を通らなかった" is also wrong for that commit.
  - Fix: compute "held" along the base's first-parent line.
- **R8-4-03 (material).** The fast path is not exact when HEAD has no profile file. Removing the profile, then restoring it in one
  commit together with a ruled change, is accepted by the first layer. Without the fast path that commit would be refused. The
  replay reports it, so the result stays inside the declared removal-window limit, but 4F's "the result is the same" is false.
  - Fix: take the fast path only when HEAD's profile has the field, or correct the claim.
- **R8-4-04 (material; pre-existing, in a changed part).** A file entry written with a trailing slash (`bomdd/20-spec.md/`) passes
  `validate_profile`, and the first layer judges it. As a literal pathspec, though, it matches directories only, so the replay lists
  no commit for it and a `--no-verify` change is never reported. The same is true at `00f3ae2` and `1cd891b`.
  - The replay's filter does not share the one decision (git's matcher, not `ruled_paths_touched`).
  - Fix: strip the slash, or list candidates without a pathspec and filter them with `ruled_paths_touched`.
- R8-4-05 (minor). If an entry is narrowed away for good and re-added later, every commit in the gap that touched it becomes a
  permanent red. A window cannot be told apart from a permanent narrowing. Not declared.
- R8-4-06 (minor). Of four mutants, each removing one round-4 part:
  - removing the entry filter fails only N23z3b;
  - removing the held-at union fails only N23z4;
  - `nearest` without the fallback fails 0 arms;
  - no `--literal-pathspecs` fails 0 arms (harmless as far as the inspector could tell).
  - So R8-3-06's mechanism has no arm of its own.
- R8-4-07 (minor). At 152 profile versions:
  - non-ruled commit: 2.4 s / 2.1 s (round 3: 12.5 s; round 2: 2.2 s);
  - ruled commit: 14.4 s;
  - merge: 16.2 s;
  - validate: 12.9 s, about 7 times round 2's.
  - Not declared; the blob reads were not batched.

## Answers (summary)

- **Q1.**
  - R8-3-01, 03, 04, 05 and 08: closed.
  - R8-3-02: closed only for an exact-string restore (R8-4-01).
  - R8-3-06: closed in the replay. Its mechanism is untested, and the fast path bypasses it (R8-4-03, 06).
  - R8-3-07: closed for the reported case (R8-4-07).
- **Q2.**
  - New holes: R8-4-01 and 04.
  - New false reports and permanent reds: R8-4-02 and 05.
  - Found sound:
    - `nearest` with a field changed on a second parent;
    - the trailer name;
    - glob characters in both layers;
    - an entry removed for good and never re-added.
- **Q3.** Parity breaks: R8-4-02 (outside the declared windows) and R8-4-03 (inside one). No other.
- **Q4.**
  - Selftest: 99 PASS.
  - Known-bad runs: `1cd891b`, `00f3ae2` and `--letter` all as expected.
  - V1: PASS.
  - `out/v2.txt` and `out/v3.txt` were read.
- **Q5.** The records are true except for the fast-path claim, "extended entries do not judge earlier commits", the narrowing claim
  without the spelling caveat, and "the replay's filter shares the one decision". R8-4-05 and 07 are not declared.
