# ECO-VT-227 - independent fresh-context review

Two rounds, each by a reviewer started with no context from the manufacturer's session, read-only (no file written, nothing staged,
no build or test run). Marking in the reviewers' reports: **[RAN]** = a command was run and its output quoted; **[REASONED]** = read
from the files only. The reports are summarised here by the manufacturer; the rulings they led to are on the register entry.

## Round 1 - 2026-10-05 - FAIL (one blocking)

Reviewed state: HEAD `7781b33d`, the uncommitted diff written by the first `req227.py` (D1 to D4: `bomdd/10-requirements.yaml` +12,
`bomdd/20-spec.md` +6).

- **R227a-F1, BLOCKING [REASONED; greps RAN].** The D4 sentence ("its stored restrictions are converted by the same rule when the
  restored catalogue is opened") is faithful to the M-BOM (`bomdd/32-mbom.yaml`, M-INFRA-PERSISTENCE-001: "a restored backup is
  converted on its open") but the code does not do it on the in-app restore path. `CarryNodeRestrictionsAsync` has one call site,
  `SqliteCatalogStore.cs:150` (inside `InitializeAsync`). `RestoreAsync` (`:2125` on) does not re-run `InitializeAsync` - its own
  notes say so (`:2162` on) - and applies three later additive steps by hand, not this conversion. After a restore the shell calls
  `LoadLocalAsync` (`ShellViewModel.cs:8214`). By reading: until the next start the restored views are read without their
  conditions and without a warning, and a view saved in that session loses the restriction for good. No test covers restore followed
  by conversion. Not executed.
- **R227a-F2, MAJOR.** "stays restorable" is broader than the M-BOM, which only says the conversion is not a schema version bump.
  Restore refuses any backup whose schema version is not 4.
- **R227a-F3, MAJOR.** The Japanese paragraph of `bomdd/20-spec.md` that mirrors REQ-032 was not updated for D3: a reader of the
  specification alone would predict that a pack with an unreadable numeric restriction is imported with a warning.
- **R227a-F4, MINOR.** In the D2 sentence "unless a target Collection is forced", "forced" is undefined in the specification. In the
  code it means a target Collection is given AND global definitions are not allowed (`SqliteCatalogStore.cs:2605`); the definition
  then becomes local to that Collection. The sentence is the same as the M-BOM's.
- **R227a-F5, MINOR.** The ECO body did not yet record the ruling.
- **R227a-F6, MINOR.** Rationale wording: "stood only in the M-BOM" (also in code comments, a test summary and ECO-VT-212's review),
  "on purpose as built" (no ruling; only a code comment gives the reason), "refused before anything is changed" (not said of this
  case in the M-BOM).
- R227a-F7, INFO: the D1 sentence's last half restates by instance the general rule one line above (the precedent is the
  `music-scope-v1` sentence). R227a-F8, INFO: an untracked acceptance-run directory is not part of this ECO.
- Clause table: D1, D2 and D3 are the SAME as the M-BOM clause by clause. Code agreement by reading: D1, D2 (with F4's meaning of
  "forced") and D3 agree; D4 does not (F1).

**Manufacturer's own check after round 1 (read-only):** `SqliteCatalogStore.cs:2162-2185` and `ShellViewModel.cs:8196-8216` read, and
the single call site confirmed by `git grep`. Agrees with F1 by reading. Not executed.

**Disposition.**
- F1 and F2: the user took D4 out of this ECO and had the restore path filed separately (「A 復元経路の ECO も起票して」, 2026-10-05).
  ECO-VT-228 is filed (`33e16ff9`). The D4 sentence is not written; the probe's D4 row is removed and the removal is recorded in
  `probe227.py`.
- F3: repaired - the Japanese paragraph now carries D3.
- F4: left as it stands. The user's ruling was to write D1 to D3 back as they stand, and a more specific sentence would say more than
  the M-BOM. The more specific wording goes to the user (round 2, finding 1).
- F5: repaired in the commit that carries the diff (the body's sections 4, 8 and 9).
- F6: repaired - the rationale names the four files searched, and no longer says "on purpose" or "before anything is changed".

## Round 2 (the last) - 2026-10-05 - PASS WITH FINDINGS (no blocking, no major)

Reviewed state: HEAD `33e16ff9`, the uncommitted diff written by the revised `req227.py` (D1 to D3: `bomdd/10-requirements.yaml` +10,
`bomdd/20-spec.md` +9), the revised `probe227.py`, and the new `probe-before-r2.txt` and `probe-after.txt`.

- Round-1 dispositions: F1 and F2 resolved by removal ([RAN] no added line carries "backup", "restorable" or 「バックアップ」); F3
  resolved; F4 left as stated; F6 resolved, each rationale sentence checked ("built under ECO-VT-212": [RAN]
  `git log -S"ViewPackLegacyRestrictionUnreadable" -- src` gives the single commit `d75a1b65`).
- Clause table: every added clause - D1 (three clauses, specification item 8), D2 (item 3), D3 (three clauses in REQ-032 and the
  Japanese paragraph) - is the SAME as the M-BOM. None is stronger, weaker or absent. D5 is not written.
- Code agreement by reading, nothing executed: D1 `SqliteCatalogStore.cs:1125-1126`, `ViewPackContracts.cs:165-170`,
  `ViewPackJsonTransfer.cs:116`, `:123`, `:144-145`; D2 `SqliteCatalogStore.cs:2605-2608`, `:2623-2628`; D3
  `ViewPackJsonTransfer.cs:57`, `:105-127`, `Views.cs:200-216`. An edge was checked: a legacy node whose tag the pack does not carry
  is refused by `ViewPackMissingTag`, so no path imports a view with a numeric condition silently gone.
- [RAN] The diff is exactly the script's output (`req227.py` on a scratch copy of HEAD gives files byte-identical to the working
  tree). The probe gives exit 1 and `probe-before-r2.txt` on HEAD's files, exit 0 and `probe-after.txt` on the working tree. YAML
  loads; `git diff --check` is clean; `bomdd/32-mbom.yaml`, `src/`, `test/` and `bomdd/41-fixed-oracle.yaml` are untouched.

Findings:

1. **R227b-F1, MINOR (round 1's F4, undispositioned).** "forced" is undefined, and the body's section 2 paraphrased D2 as "when a
   target collection is specified, it is placed there", which the code contradicts when global definitions are allowed. Suggested,
   if the user wants it closed: "...unless the import forces a target Collection (a target Collection is given and global definitions
   are not allowed)". That says more than the M-BOM, so it needs the user's disposition.
2. **R227b-F2, MINOR.** The body's section 2 said the search words gave 0 hits in the four files and listed `refuses the pack`; that
   phrase has one hit, `20-spec.md:1022`, which is the `music-scope-v1` sentence and not D3. The conclusion stands; the count was
   wrong as written.
3. R227b-F3, INFO: the pack refusal is stated twice inside the D3 clause (the capitalised lead, then the "but" half). Redundant, not
   contradictory.
4. R227b-F4, INFO: the probe's GREEN establishes only that three phrases are present; a sentence saying the opposite would also be
   GREEN. Faithfulness rests on the clause table, not on the probe.
5. R227b-F5, INFO (on ECO-VT-228's body): nothing in it is contradicted by the code read. Two remarks: its title states "not
   converted until the next start" as fact while the body says it is an unexecuted reading; and a start of the MCP server
   (`CatalogTools.cs:59`) also runs `InitializeAsync`, so the gap may close without an application restart - relevant to the design
   of the failing probe.

**Disposition.**
- R227b-F1: the body's paraphrase is corrected (section 2, D2). The specification sentence was first left as the M-BOM's wording, as
  ruled, and the more specific wording was put to the user. The user ruled for it (「承認・1 は B」, 2026-10-05) and `forced227.py`
  wrote it: a target Collection is forced when the import is given one and global definitions are not allowed, and the definitions
  then become local to that Collection. The sentence now says more than the M-BOM's line, on that ruling. It was read against
  `DesiredCollection` and `DesiredScope` by the manufacturer; no third review round was held for it.
- R227b-F2: corrected in the body.
- R227b-F3, F4: recorded; no change.
- R227b-F5: outside this ECO. It is for ECO-VT-228's first step (the failing probe) and is recorded here so that it is not lost.

## Not verified by either round

- Any runtime behaviour: no build, test or product run. All code agreement is by reading.
- The behaviour of reader builds from before `node-condition-v1` (inferred from the date the refusal was introduced, `909b713d`).
- The provenance of D2 beyond the M-BOM line and a code comment: ECO-VT-195's body supports the main clause; the "unless forced"
  branch was not found in it.
- Other M-BOM units.
