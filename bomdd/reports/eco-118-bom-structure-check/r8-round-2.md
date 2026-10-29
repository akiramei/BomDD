# R8 round 2 — ECO-118 (ea2ac97, diff against 94a2a2a)

Inspector: a fresh-context Agent (`claude-opus-5-5`, not round 1's), the same brief plus questions 7 (round 1's findings closed by
the code?) and 8 (regressions). Read-only; its temp folders removed. Summary of its final message (the full text is in the session
transcript; findings and verdicts below are as it gave them):

R8 ECO-118 round 2: REJECT — 2 material, 6 minor.

- **R8-2-01 (material)** — a plain `git commit --amend` (editor) lets a failing BOM into an acceptance commit: the commit-msg hook reads
  the message before git strips its `#` comment lines, so `parse_trailers` sees the comment block as the final paragraph and finds no
  trailer; `structure_targets` returns []; git then stores a valid trailer; `validate` exit 0 (no E06). Only amends that open no
  editor (`--no-edit`, `-m`, `-F`, `-C`) are closed; the playbook line and the docstring claim more. The same parse makes E05 refuse a
  first acceptance written in an editor (pre-existing, not this ECO's). Fix: strip comments before reading trailers in E12's path
  (`git stripspace --strip-comments` honouring core.commentChar and the scissors line, or `git interpret-trailers --parse`); an
  editor-amend arm in V8 and N22; changing `parse_trailers` itself would change E04/E05 (out of the amendment's scope) — keep it local
  or get a ruling, and record E05's editor defect.
- **R8-2-02 (material)** — `part_standard: {}` on every unit gives PASS, exit 0, with all nine rules not exercised (round 1's tool
  gave NOT-APPLICABLE): the R8-1-05 fix accepts an empty mapping as a part standard and D6 then yields PASS. §4.5 P1 says a standard
  has the two lists. Fix: both `provides` and `requires` present, else UNMEASURABLE; and/or PASS needs at least one rule exercised,
  else NOT-APPLICABLE; a selftest arm. No real unit is affected (every real part-standard unit carries both keys).
- R8-2-03 (minor) — an amend that drops or changes the trailer (`-m` without it, a lower-case key) is not stopped by E05 or E12 (HEAD
  already applied); `validate` then reports E06. Not declared; name it in the playbook's 止めないもの.
- R8-2-04 (minor) — E-BOM `interfaces` ignores unknown keys (`require:` hides an A1-5 finding). Close it to provides/requires; an arm.
- R8-2-05 (minor) — on a CRLF working copy (`core.autocrlf=true`) the receipt's working-tree `git_blob` differs from HEAD's blob for an
  unchanged file; use `git hash-object --path`. `RULE_SET` was not bumped although A1-1 and A1-2 changed behaviour.
- R8-2-06 (minor) — the `_ids` string-id check has no selftest arm (disabled, the selftest still passes).
- R8-2-07 (minor) — section 4's "two placeholder rows skipped" at 64912a4 is out of date (now `cp_rows=4 placeholders_skipped=0`,
  findings unchanged).
- R8-2-08 (minor, declared) — E12 also refuses a non-acceptance commit carrying an accept trailer for an already applied ECO; never seen
  in the products' history (MoviePad-Remake 6, TimetableAdv 38 trailer commits).

Round 1's findings: closed by the code — R8-1-02, 03, 09, 10, 11, 12, 13 and R8-1-07's second half (each checked by a case; R8-1-04 by
40,144 type substitutions, 0 non-Unmeasurable exceptions); partly closed — R8-1-01 (R8-2-01, 03), R8-1-04 (R8-2-06), R8-1-05
(R8-2-02), R8-1-08 (R8-2-05); left to the closure, properly — R8-1-06 and R8-1-07's first half (now a real decision, R8-2-02).

Regressions: none on real BOMs — 25 targets (MoviePad-Remake's 22 commits touching 30/32/33 plus HEAD, ViewPrism2, ViewTube, TimetableAdv
at HEAD) give identical exit codes and findings under f8b4891's and ea2ac97's tool; only 64912a4's population line differs. The kit
templates still read NOT-APPLICABLE. Evidence re-runs identical apart from `utc` and temp roots; CI on ea2ac97 success (run
40861146368, C19 32/32, C11/C11b 44 controls on ubuntu and windows).
