# ECO-VT-228 - independent fresh-context review

One round so far, by a reviewer started with no context from the manufacturer's session. The reviewer wrote nothing in the
repository; everything it executed ran in a scratch copy (`git archive HEAD` plus the working-tree `SqliteCatalogStore.cs`). Marking
in the reviewer's report: **[RAN]** = a command was run and its output quoted; **[REASONED]** = read from the files only. The report is
summarised here by the manufacturer.

## Round 1 - 2026-10-06 - PASS WITH FINDINGS (no blocking, no major)

Reviewed state: HEAD `b3ba0c6c` with the uncommitted repair written by the first `impl228.py` (one file,
`src/ViewTube.Infrastructure/Persistence/SqliteCatalogStore.cs`), and the four acceptance cases of
`test/ViewTube.Acceptance/RestoredLegacyRestrictionTests.cs` as committed at `b3ba0c6c`.

### Mutants, in the reviewer's scratch copy [RAN]

| mutant | control | restored-and-read | restored-saved-restarted | restored-restarted |
|---|---|---|---|---|
| the repair | green | green | green | green |
| m1: the conversion removed from the list | RED | RED | RED | RED |
| m2: the list in the start only, the restore back to its three bare calls | green | RED | RED | green |
| m3: the restore's commit dropped | green | RED | RED | green |
| m4 (extra): the opt-out column step removed from the list | green | green | green | green |
| m7 (extra): a throw injected after the settings table, on the restore's connection only | green | RED | RED | RED |

m2 is the product before the repair and gives the same two reds as `tests-before.txt`. m4 SURVIVED the four cases (finding F5).

### The reviewer's own probe, with the repair [RAN]

- A. A backup with no opt-out column, no policy table, no settings table and legacy restrictions: restored (`Restored=True`), all
  three present afterwards, 0 legacy rows, and the same store reads the views converted, the collections and the settings with no
  start.
- B. The same file with one `Restriction` that is the JSON number 3 (a value the product never writes): the restore returns
  `ReplacementFailed` with the safety copy; the live file is the restored one WITHOUT the column and the two tables; in the same
  session reading the collections throws `no such column: refresh_opt_out` and reading the settings throws
  `no such table: app_settings`; the next start throws the conversion's exception too. Under m2 (before the repair) the same file
  restored as `Restored=True` with the column and the tables present, and then failed the next start the same way.
- m7 on A (a transient failure): `ReplacementFailed`, nothing of the list kept (the added column rolled back), and the next start
  applies the whole list and converts.
- D. A backup with the three indexes and the library identity row removed passes validation; after the restore
  `GetLibraryIdentity` throws `LibraryIdentityMissing` until the next start, which repairs both. Only a hand-edited file can lack
  them (both predate schema 4).

### Findings

- **R228a-F1, MINOR [RAN].** The restore's note said "the next start applies the list again". That holds for a transient failure
  only; a restriction the conversion cannot read fails the start as well (probe B), as it did before the repair.
- **R228a-F2, MINOR [RAN].** A behaviour shift nothing recorded: when a later step fails, the earlier additive steps are now rolled
  back too, and the file is already replaced, so the running session reads a catalogue without the opt-out column and the settings
  table (probe B, m7). Before, the three autocommit statements kept whatever had succeeded. The shell does not reload on the failure
  and its status does not say to restart.
- **R228a-F3, MINOR [RAN, git].** "one omission made three times" and "left one out four times" are stronger than the record: the
  ECO-VT-166 line and the ECO-VT-168 line first appear in those ECOs' own fix commits (`8fd76917`, `d1cc6ff0`). Only ECO-VT-170's
  (found by a review) and the conversion of ECO-VT-212 are recorded omissions.
- **R228a-F4, MINOR [REASONED].** The new method was put inside an existing stack of doc comments, so three `<summary>` blocks
  attached to it and `AddAppSettingsTableAsync` lost the one it had. (The misplacement of ECO-VT-168's summary predates this diff.)
- **R228a-F5, MINOR [RAN].** m4 survives the four cases, and no test names `refresh_opt_out`. The list is now the only place a
  restored schema-4 file gets that step, and no case guards it.
- **R228a-F6, MINOR, out of scope [REASONED].** Another opener without the list: `src/ViewTube.DemoCurator/Program.cs:190-220`
  constructs a `SqliteCatalogStore` on a copy of the installed catalogue and previews and applies a View Pack with no
  `InitializeAsync`, then installs the result. A catalogue last opened by a build from before ECO-VT-212 would be read with its
  restrictions dropped. Whether the apply rewrites existing legacy views was not traced.
- R228a-F7, INFO [RAN]: what the start applies and the restore still does not - the three indexes, the library identity row,
  `PRAGMA journal_mode=WAL` (the main DDL block). Only a hand-edited schema-4 file can lack them (probe D). "ONE LIST" covers the
  steps after the version migrations, not the main block.
- R228a-F8, INFO [RAN]: the conversion's `LIKE '%"Restriction"%'` filter also matches a view NAMED `Restriction`; it is skipped
  harmlessly but re-read at every start, and case 2's count of legacy rows would be a false red for such a catalogue.
- R228a-F9, INFO [RAN]: the restored-restarted case is green before the repair and under m2; it guards "converted once", not the
  defect.
- R228a-F10, INFO [RAN]: a legacy restriction whose tag is missing converts to no condition and no dropped restriction, with nothing
  reported. ECO-VT-212's rule, the same at the start and at the restore.
- R228a-F11, INFO [REASONED]: "the conversion comes last" is a convention - it reads views and tags only, so any order passes. The
  start's second `CREATE TABLE IF NOT EXISTS app_settings` is a no-op.
- R228a-F12, INFO [RAN]: the body and the M-BOM were not yet updated when the review read them (the manifest lists both as required).
- R228a-F13, INFO [REASONED]: the restore's transaction uses the default isolation level; `WriteAsync` names Serializable. Same effect.

### What the reviewer verified as correct

- [RAN] 4 of 4 green with the repair in an independent build, 0 warnings, 0 errors. `src` is unchanged between `7781b33d`,
  `b908a46c`, `8337bf5f` and HEAD, so the ECO's reading, the probe and `tests-before.txt` describe the same product code.
- [RAN] The manifest's sentences match `probe-before.txt` and `tests-before.txt`.
- [REASONED, with RAN support] The new transaction is sound: the restore's connection is private-cache and unpooled with a busy
  timeout; the three former statements already took the write lock, so there is no new lock class; the measured shared-cache
  deadlock concerned shared-cache table locks, which this connection does not use; the transaction is disposed before the connection
  and rolls back (m3, m7). No run hung.
- [REASONED] `CarryNodeRestrictionsAsync` has two call paths, both through the list. The MCP host calls `InitializeAsync`; the app
  has one store and its restore goes through `RestoreAsync` then `LoadLocalAsync`.
- [RAN] The 12 failures of the whole-project run are the environment's, not the repair's: with the user's application running,
  `McpSurfaceTests` fails 10 of 24 with `ApplicationIsRunning` (`src/ViewTube.Mcp/CatalogTools.cs:142`) and
  `DemoCurationAcceptanceTests` 2 of 5, one with `ViewTubeProcessIsRunning` (`DemoCurationApplier.EnsureViewTubeStopped`) and one
  with a hash mismatch consistent with the same cause but not proven by its own message. The same counts in the reviewer's scratch
  build.

### Not verified by the reviewer

- A legacy view in the music scope or a collection scope through the restore (the conversion's SELECT has no scope filter).
- The whole acceptance suite under any mutant, or under the repair; `whole-project.txt` was read, not reproduced.
- The screen after a restore; all checks were at the store.
- Concurrency of the new transaction against live readers in the running application (reasoned only).
- A real backup produced by a build from before ECO-VT-212; every arranged file was made by the current build and then edited.

### Disposition (the manufacturer, 2026-10-06)

- **F1, F3, F4: repaired** in the revised `impl228.py` (re-applied from the committed file). The restore's note now says a transient
  failure is repaired by the next start and an unreadable restriction fails the start as before; the history is worded as the record
  has it; the list is placed after its additive steps, so the older doc comments are where they were.
- **F2: recorded, no code change.** The restore's note and the M-BOM line say what a failed list leaves. One transaction is the form
  ruled (B); keeping the earlier steps on a failure would be a second form. It is put to the user with the acceptance request.
- **F5: repaired.** A fifth case, `ECO_VT_228_a_restored_backup_from_before_every_step_gets_the_whole_list` (the reviewer's probe
  A): RED without the repair (`tests-before-r1.txt`, 3 of 5 red), RED under m4 run by the manufacturer in the repository's working
  tree and then reverted (`mutant-m4.txt`, 1 of 5 red), green with the repair (`tests-after-r1.txt`, 5 of 5).
- **F6: out of scope (R3).** Not repaired here. Put to the user as a separate ECO.
- **F7: the list's summary now says** it covers the steps after the version migrations only and that the main block is not applied
  by a restore. F8 to F11 and F13: recorded; no change. F12: done in the commit that carries the repair.
