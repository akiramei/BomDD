# ECO-VT-231 - independent fresh-context review

One round, by a reviewer started with no context from the manufacturer's session, read-only (no file written, nothing staged, no
build or test run; the read-only probe was re-run). **[RAN]** = a command was run and its output quoted; **[REASONED]** = read from the
files only. Summarised here by the manufacturer; the clause table is the faithfulness evidence the ECO's section 4 asks for.

## Round 1 - 2026-10-06 - PASS WITH FINDINGS (no blocking, no major)

Reviewed state: HEAD `5d9aca23`, the uncommitted diff written by the first `req231.py` (REQ-032 statement +4 and rationale +5,
the specification's mirror paragraph +2), against the M-BOM's two lines (M-INFRA-PERSISTENCE-001: the ECO-VT-212 line at `:353`, the
ECO-VT-228 line at `:355` onward) and the code of `SqliteCatalogStore.cs` (InitializeAsync `:148`, RestoreAsync `:2192-2208`,
ApplyStepsAfterVersionMigrationsAsync `:2300-2309`, CarryNodeRestrictionsAsync `:2325` onward).

### Clause table

| clause | vs the M-BOM | the code bears it (by reading) |
|---|---|---|
| a backup taken before this form existed is converted when it is restored | SAME (ECO-VT-228 line: "It is converted by the restore") | yes: the restore opens a transaction on the connection that replaced the file, calls the list, commits, and only then returns Restored = true |
| its stored restrictions are carried by the same rule | SAME (ECO-VT-212 line: FromLegacyRestriction with the tag's type) | yes: the same CarryNodeRestrictionsAsync on both paths |
| by the restore itself, not at the next start | SAME (ECO-VT-228 line) | yes: inside RestoreAsync before it returns; the shell only reloads afterwards |
| a view read or saved after the restore keeps what [the rule gives them] | SAME in substance (the M-BOM states the negated measured defect; CP-BACKUP-001 states the positive) | yes: cases 2 and 3 of RestoredLegacyRestrictionTests; the unreadable numeric is dropped and reported by the rule (F5) |
| a later start finds nothing left to convert | SAME (ECO-VT-212 line: "a second open finds nothing") | yes: Carry removes Restriction from every node and rewrites the row |
| the Japanese paragraph's five clauses | SAME as the five above | as above |
| the rationale's five facts | checked against ECO-VT-227 §2, §4, §9 and ECO-VT-228 | correct |

ABSENT, rightly: "not a schema version bump" (the user's ruling), the list, the transaction, the known limit of a failed step
(R228a-F2). "by the restore itself, not at the next start" is user-observable behaviour, not manufacturing detail.

### Findings

- **R231a-F1, MINOR [RAN].** The body said the ECO-VT-228 line starts at `:356`; it starts at `:355`.
- **R231a-F2, MINOR [RAN].** The body quoted ECO-VT-227's D4 inexactly, dropping 「の最初の起動で」 - the very timing the new clause
  reverses. The diff itself is honest ("as the M-BOM says it after that repair").
- **R231a-F3, MINOR [RAN].** The specification's 「（ECO-VT-228、ECO-VT-231で書き戻し）」 reads as two write-backs; ECO-VT-228's
  commits touched no specification file - it is the repair that made the sentence true.
- **R231a-F4, MINOR [RAN].** The ruling holds for the statement (nothing about a schema version), but the rationale stated the
  excluded manufacturing fact as a presupposition ("not a schema version bump stays in the M-BOM"), so a search for it on REQ-032 hits.
- **R231a-F5, MINOR [REASONED].** "keeps what they meant" is literally false for the unreadable numeric restriction (dropped and
  reported, by the rule); it rides on "by the same rule", the shape of REQ-032's own headline, so SAME in substance.
- **R231a-F6, MINOR [RAN].** REQ-032 is the right owner (the rule, the five cases and CP-BACKUP-001 cite it), but REQ-064 and the
  specification's backup bullet say nothing about work done after the replacement; a reader of the backup requirement alone cannot
  find that a restore converts. No other specification section needs the sentence.
- R231a-F7, INFO: the known limit of a failed step (R228a-F2) is outside the success path the requirement promises; the limit lives in
  the M-BOM and CP-BACKUP-001 (the user's ruling 2-a). R231a-F8, INFO: a schema-<4 backup is refused by validation, so the clause is
  vacuous, not false, for it; the clause makes no restorability promise (R227a-F2's trap avoided). R231a-F9, INFO: the probe proves the
  presence of two fixed phrases that `req231.py` writes, so its GREEN was guaranteed by construction; its two controls are
  unmeasurability guards; probe-before's RED was independently reproduced at `4b51151b`.
- **R231a-F10, INFO, out of scope [RAN].** REQ-064's "failure leaves the active catalog byte-for-byte unchanged" does not hold for the
  ReplacementFailed path (validation passed, the file replaced, a post-replacement step threw). Pre-existing, from before ECO-VT-228.

### What the reviewer verified

- [RAN] `git diff --check` clean; no CR in either file; `yaml.safe_load` of the requirements with the new folded text; the diff is
  exactly the hunks described; `41-fixed-oracle.yaml` untouched.
- [RAN] The body's section 2 facts: `:353`, `:967`, `:276`; "backup" 0 hits in REQ-032 at HEAD; 「バックアップ」「復元」 0 hits in the
  mirror paragraph at HEAD; REQ-064 says validation and integrity only; the five acceptance cases as described.
- [RAN] The rationale's dates, ECO numbers and rulings against ECO-VT-227 and ECO-VT-228; the code paths; the added English lines
  within the block's existing width.

### Not verified by the reviewer

- Nothing built or executed; the five acceptance cases are taken from ECO-VT-228's record, not re-run.
- Whether the shell's reload after a restore reads views exactly as the tests do (the screen itself, unmeasured in ECO-VT-228 too).

### Disposition (the manufacturer, 2026-10-06)

- **F1, F2: the body corrected** (`record231.py`).
- **F3, F4, F5, F6: the revised `req231.py`** (re-applied from `5d9aca23`): the specification's attribution names ECO-VT-228 as the
  repair; the rationale says "the manufacturing side of D4 (how the conversion is versioned) stays in the M-BOM"; "keeps what the rule
  gives them" / 「規則が与える条件を保ち」; REQ-064 and the specification's backup bullet each gain one clause pointing to REQ-032.
  No further review round was held for these: they replace words and add references without adding content from the M-BOM.
- **F7, F8, F9: recorded.** **F10: carried to the user** with the acceptance request (a separate ECO or not).
