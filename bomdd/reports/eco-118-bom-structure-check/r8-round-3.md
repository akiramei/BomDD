# R8 round 3 — ECO-118 (8461c7f, diff against 94a2a2a) — the last round by the user's "1:A 2:A"

Inspector: a third fresh-context Agent (`claude-opus-5-5`), the same brief plus questions 7 (rounds 1-2 closed?) and 8 (regressions,
including E12 in 14 hook contexts); told the ruling's scope (R8-2-01 inside E12's path only). Read-only; its temp folders removed.
Summary of its final message (findings and verdicts as it gave them):

R8 ECO-118 round 3: REJECT — 1 material, 2 minor.

- **R8-3-01 (material)** — E12 misses the accept trailer when git comments with another character than the one E12 strips: (a)
  `core.commentChar=auto` with a body line starting with `#` (git chose `;`; E12 stripped the real `#42…` line and kept git's `;`
  block, so no trailer was found) and (b) `core.commentString=';'` (git 2.47.1 honours it; the last key set wins, so reading
  commentChar alone is wrong even when both are set). In both an editor `--amend` let a failing BOM into an acceptance commit; HEAD's
  BOM exits 1 and `validate` exits 0. Neither key is set on this machine. No arm covers the config read (`commit_comment_char`
  replaced by `return "#"` leaves the selftest all PASS). Fix inside E12's path: read the last of core.commentChar/commentString as git
  does; under `auto` strip lines starting with any of git's candidates (`#;@!$%^&|:`) — over-stripping only removes lines and cannot
  hide a trailer — or refuse and ask for an explicit character; arms for each configuration and for the config read. Or declare it.
- R8-3-02 (minor) — A1-2's population counts every IF-, including those its lazy rule skips, so a BOM where nothing was checked can
  read PASS (one unit with empty lists, the IF- items in units without part standards) and `not_exercised` misstates A1-2. Narrower
  than R8-2-02; no BOM that breaks a rule passes; the stop is unaffected (E12 allows 0 and 3 alike). The playbook's NOT-APPLICABLE
  parenthetical was not widened with the tool's. Fix: count after the lazy skip; an arm; widen the text.
- R8-3-03 (minor) — the working tree's `git_blob` through `git hash-object --path` (R8-2-05) has no selftest control; its only
  control is V7's CRLF arm, run at closure. Fix: an arm, or declare V7 as the control. (Also noted: when `hash-object` fails the
  field silently falls back to the raw bytes' id.)

Hook contexts (14): refused with E12 — editor amend, `--amend --no-edit`, `--amend -m` with the trailer, `-a --amend`, `--amend --only`,
`-v --amend` (scissors and diff), `commit.verbose=true`, `core.commentChar=;` (file and `-c`), multi-character `//`, `auto` without a
`#` line, `--cleanup=scissors`; let through — R8-3-01 (a) and (b). A legitimate editor amend and a first `-m` acceptance with the good
BOM allowed.

Rounds 1-2: every finding closed by the code (each checked by a case) or by the text, except R8-2-01, still open for R8-3-01's two
configurations; R8-1-06 and R8-1-07's first half properly left to the closure. Regressions: none — 26 targets (MoviePad-Remake's 21
commits touching 30/32/33 and HEAD, ViewPrism2, ViewTube, TimetableAdv at HEAD, the kit templates) under the tools at f8b4891, ea2ac97
and 8461c7f give identical exit codes and findings. CI on 8461c7f success (run 40869894655; C19 36/36, C11/C11b 45 controls on both
runners). Evidence re-runs identical apart from `utc` and temp paths.
