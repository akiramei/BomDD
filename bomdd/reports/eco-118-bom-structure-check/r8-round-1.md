# R8 round 1 — ECO-118 manufacture (f8b4891)

Inspector: a fresh-context Agent (`claude-opus-5-5`), brief `r8-118-brief` (six questions: rules vs text, the stop's bypasses,
section 4 vs out/, the receipt, the P1 finding, an open question). Read-only; its temp folders removed. Its final message, verbatim:

---

R8 ECO-118 round 1: REJECT

Two material findings and eleven minor ones. Material #1: E12 can be bypassed with a plain `git commit --amend`. Material #2: entries that share an id are silently dropped, so a failing BOM can read as PASS. Re-running the evidence matched what was committed: v1, v2, v3 and v8 came out identical. v7 differed only in temp roots, `utc` and its summary line (R8-1-03). out/ was restored with `git checkout`, and BomDD's `git status` is clean. CI for f8b4891: `self-conformance` success (`gh run list --commit <full sha>`).

## Findings

**R8-1-01 (material): `git commit --amend` gets a failing BOM into an acceptance commit, and E12 never runs.**
- Mechanism:
  - `_load_pair` (process-validator.py:789-790) compares HEAD's register with the index's register.
  - When the acceptance commit is amended, HEAD already says `applied`. So `accept_transitions` (:685) returns `[]` and `check_structure` (:720) never runs the tool.
  - Replay does not recompute either (D10).
- Evidence: a throwaway bomdd-init product, path containing spaces, hooks active.
  - Accepted ECO-901 with the tool's `good` fixture: allowed, "構造検査 PASS".
  - Staged the `fail` fixture and ran `git commit --amend --no-edit`: exit 0, no [E12].
  - HEAD^ register shows `staged`, HEAD shows `applied`, so HEAD is the acceptance commit.
  - `bom-structure-check.py --rev HEAD` on that commit: exit 1, "verdict: FAIL - 1 finding(s)".
- Not declared: D10 and the playbook's 止めないもの name only `--no-verify`; 1A names only removing the field or the hook. E05 uses the same detector, but replay's E06 backs it up; nothing backs up E12.
- Fix (one of):
  - Also fire E12 when the commit message carries the accept trailer. `--amend --no-edit` keeps it, and `check_commit_msg` already parses it.
  - Or recompute E12 in replay for acceptance commits (there are few). This also covers `--no-verify`, rebase and cherry-pick.
  - Add an amend arm to V8 / N22 either way.
  - At minimum, declare amend, rebase and cherry-pick among the routes the stop does not cover, with the user's acknowledgement.

**R8-1-02 (material): duplicate ids are silently dropped (the last entry wins), so a failing BOM reads as PASS (exit 0) and E12 would allow it.**
- Where: `items[it["id"]] =` (bom-structure-check.py:204), `units[u["id"]] =` (:221), `rows[r["id"]] =` (:232).
- Rules 1, 2, 5 and C1-a/b are written over "every" requires / IF- / provides / row. The earlier entry is never checked, and this choice is not declared anywhere.
- Constructed cases (the selftest's `good` fixture, mutated):
  - A first `M-A-001` whose requires target `PS-NOWHERE-P01` and whose provides id is `PS-WRONG-FORM`, followed by the good `M-A-001`: PASS, exit 0.
  - A first `CP-A-001` naming `PS-M-A-001-P99` (a C1-a finding), followed by the good row: PASS.
  - A duplicate `E-B-001` whose second copy drops `requires IF-A-01`, which hides an A1-5 finding: PASS.
- None of the four products has duplicate E-item, unit or row ids today (I parsed each HEAD), so this is constructed. No other kit tool checks unit-id uniqueness (only this tool and impact-retrospective.py read `manufacturing_units`).
- Fix: a duplicate id in `items`, `manufacturing_units` or `characteristics` is UNMEASURABLE (or a finding), plus a selftest arm. This is the same class as T1's "strict YAML, duplicate keys refused".

**R8-1-03 (minor): `out/v7.txt` was not produced by the committed `verify118.py`.**
- The committed file ends `V7: PASS (the literal 3ba3d00 arm is reported above and judged in the order)`.
- The committed script now writes `V7: every arm but one as expected; the literal 3ba3d00 --index arm NOT MET ...`.
- My re-run changed only that line, the temp `root` paths and `utc`; the tool sha256 in the receipts is unchanged. Section 4's wording matches the stricter line.
- Fix: regenerate out/v7.txt at closure.

**R8-1-04 (minor): values of the wrong type crash the tool.**
- What happens: a Python traceback with exit 1 (the FAIL code) and no receipt. E12 then prints "BOM の構造検査が FAIL" with zero findings.
- Cases:
  - An E-BOM `provides` entry without `id`: `sorted()` at :300 raises "TypeError: '<' not supported between NoneType and str".
  - `ebom_refs: [{id: ...}]`: "unhashable type: 'dict'".
  - `part_standard_refs: [{...}]`: the same TypeError.
- This is fail-closed, but T1 says an unknown shape is UNMEASURABLE (exit 2), and T4 says a receipt is written on every verdict.
- Fix: type-check ids and refs in `build_model`, raising `Unmeasurable`.

**R8-1-05 (minor): the shape of `part_standard` is read loosely.**
- `if ps:` (:215) treats `part_standard: {}` (or any falsy value) as "no part standard". With every unit set that way, the result is NOT-APPLICABLE (exit 3), which E12 allows.
- Unknown keys are ignored. A mistyped `provide:` holding an item with id `BAD-ID` makes that item vanish from P1, C1-b, A1-2 and A1-3, and the BOM reads PASS (constructed).
- P1's "two lists" form is not claimed by the tool (only the id form), but T1's "unknown shape → UNMEASURABLE" covers this.
- Fix: a present `part_standard` must be a mapping whose keys are only `provides` and `requires`; otherwise UNMEASURABLE.

**R8-1-06 (minor): D3 narrows the literal text of §4.6 rule 4.**
- The text forbids an E-item unit from targeting the PS- of a unit without `ebom_refs` that requires any IF-, or any PS- of an E-item unit. It has no boundary qualifier.
- `_relay_crossing` (:321-350) flags only crossings relative to the requirer. Two constructed cases PASS where the literal text fails:
  - M-JIG requires IF-A-01, which M-A's own item provides.
  - M-JIG requires PS-M-A-001-P01, a cycle back to the requirer.
- D3 matches P4's stated reason ("E 品目の間の境界を中継しない") and the §4.5 granularity limit.
- Fix: no code change. Align the §4.6 rule 4 wording ("…を越えて"), or have the closure rule on it, since the playbook text is the contract.

**R8-1-07 (minor): D6 changes the frozen PASS definition, and the receipt cannot show what it left out.**
- T1 (frozen): PASS = "every rule ran on a non-empty population". D6: PASS = no finding and at least one part-standard unit, with the unexercised rules named.
- This is declared, but it is a change to a frozen definition and needs the closure's ruling.
- `not_exercised` is printed on the population line (:501-502) but is not in the receipt (:524-539). T4 says the receipt carries the population line's counts, so a PASS receipt cannot show which rules had empty populations.
- Fix: add `not_exercised` to the receipt, and record the ruling.

**R8-1-08 (minor): receipts read from the working tree or the index carry no version identity.**
- The `source` field is just `{"kind": "worktree"}` or `{"kind": "index"}`. The inputs carry SHA-256 values, not git blob ids, so such a receipt cannot be tied back to a commit.
- §4.6 says the receipt records 読んだ版. G3 runs before process-core, so a G3 record will often cite a receipt made from the working tree.
- Fix: record HEAD, a dirty flag and the git blob ids, or have §4.6 say "run with `--rev` on the BOM commit".
- Also: `RULE_SET` is a hand-maintained constant with no tie to `RULES`; the tool hash covers it. `utc` is inherently unverifiable.

**R8-1-09 (minor): rule 2 is applied to every E-BOM `provides` id, whatever its prefix.**
- Code: `rule_2` iterates `e_provides` (:300). The text says "すべての `IF-`".
- Constructed: a provides id `OC-1` gives `[A1-2] OC-1 -> -: realised by 0 units`.
- All real provides ids are IF- (MoviePad-Remake 10 of 10; the other products have 0) and it is fail-closed.
- Fix: filter on `IF-`.

**R8-1-10 (minor): a unit can require its own provides item.**
- P1 says a requires target is "別の単位の provides の ID", but `_resolve` (:265-267) accepts the unit's own PS-.
- Constructed: M-JIG requires PS-M-JIG-001-P01, and the BOM reads PASS.
- Fix: refuse self-targets under A1-1, or declare the choice.

**R8-1-11 (minor): D1 skips any id containing `<NAME>`, even among real units.**
- Constructed: a unit `M-<NAME>-009` carrying failures among real units reads PASS, shown only as `placeholders_skipped=1`.
- Fix (one of):
  - Skip placeholders only when every unit is a placeholder, or when the BOM is the unchanged template.
  - Or make a non-zero `placeholders_skipped` alongside real part-standard units a finding.

**R8-1-12 (minor): the selftest count is padded.**
- The `exit-codes` arm (:674) compares a constant with itself. The `fail` arm duplicates `a1-4-direct`. So "23/23" includes two arms that test nothing new; C19 only requires a count above 0.
- The real exit-code mapping is exercised by V7's fixture runs.
- Fix: drop the tautological arm, or make it run `main()`.

**R8-1-13 (minor): `verify118.py` leaves temp repositories behind.**
- `shutil.rmtree(tmp, ignore_errors=True)` cannot remove git's read-only objects on Windows. This is the fail-silent pattern self-conformance's cleanup comment already describes.
- The manufacturer's runs left `%TEMP%\eco118-v7-67qgdbhv` (the root named in the committed receipts) and `%TEMP%\eco118-v7-jsn6q19x`. My re-run left a third, which I removed. I did not touch theirs.
- Fix: use the `onerror` chmod handler that verify118_v8.py already has, and report anything it cannot remove.

## Answers per question

**Q1 (rules versus code):**
- Rule 1: matches the text, including the IF- side condition, `procurement:` against top-level `procurement[].package` (D7) and `platform:` as written.
- Rule 2: matches the text plus D2's lazy reading, except R8-1-09.
- Rule 3: provided-by reading.
- Rule 4: direct case plus relay (see R8-1-06).
- Rule 5: matches; D4's `ebom_refs` exception matches "1 つの単位が両方の品目を実現する".
- Rule 6: matches; D5 matches "解決する単位の集合".
- P1 id form `^PS-<unit>-[PR]\d{2}$` and uniqueness across both lists: matches, except R8-1-10.
- C1-a/b: match.
- D1–D12:
  - D2, D4, D5, D7, D8, D9, D11, D12 are consistent with the text.
  - D3 narrows a rule (R8-1-06). D6 changes a frozen definition (R8-1-07). D1 is broader than needed (R8-1-11).
  - D10 leaves the amend gap (R8-1-01).
- Gaps not declared anywhere: R8-1-02, R8-1-04, R8-1-05.

**Q2 (can E12 pass a failing BOM or refuse a valid one?):**
- Lets one through: by amend (R8-1-01) and by duplicate ids (R8-1-02).
- Correct in every other hook case I ran in a product whose path contains spaces (fail fixture = the tool's own A1-4 case):
  - `git commit -- <paths>` (the `--only` temporary index): refused, [A1-4] shown.
  - `git commit -a` with the failing BOM only in the working tree: refused.
  - Failing BOM in the index, good one in the working tree: refused. The tool inherits `GIT_INDEX_FILE` and reads the commit's own index.
- Exit codes: crashes exit 1 and are refused (R8-1-04). The profile field is read from HEAD. The 300 s timeout refuses.
- Process-validator `--mode selftest`: "all PASS".
- Refusals of an arguably valid acceptance: E12 fires on every applied transition, including ECOs that never touch 30/32/33. That is what 1A ordered, but its consequence is not declared (see Q6).

**Q3 (is section 4 backed by out/, and do the known-bad arms test what they claim?):**
- Each "PASS" or "as expected" in section 4 is backed by its out/ file, except R8-1-03.
- 64912a4's "two placeholder rows skipped" checks out: CP-<NAME>-001 and CP-<NAME>-DISPLAY-001 skipped, cp_rows=2.
- I read each mutated arm's construction. Every one isolates its rule (a1-1-ps-missing also gives A1-6, as declared).
- V2's disabled-rule copies each go red on that rule's arms.
- V8's known-bad disables `check_structure` in the working-tree validator and lets arm 1 through.
- The SC run-1 file shows C11 and C11b with 43 controls and C19 at 23/23.

**Q4 (is the receipt machine-made and true?):**
- Every field is written by `write_receipt`. Hashes re-verify against the git blobs; the tool hash matches the committed tool.
- Weaknesses are R8-1-07 (no `not_exercised`), R8-1-08 (no version identity outside `--rev`; `RULE_SET` hand-kept; `utc` unverifiable) and R8-1-04 (no receipt on a crash).

**Q5 (the P1 finding in MoviePad-Remake at 3ba3d00):**
- The tool is right. M-EXPORT-001 provides `PS-M-EXPORT-CLOCK-001-P01` and `PS-M-EXPORT-COPY-001-P01`, but P1 requires `PS-<UNIT>-Pnn`. Nothing in the playbook exempts kept ids; §8's lineage text asks for active references to be re-attributed.
- Confirmed at HEAD `a2ca41e`: exit 1, P1-id=2.
- The derived copy is honest: exactly those two ids changed, in 6 lines.
  - 32-mbom: the two provides ids, plus the two `retired_units.moved` narrative strings. These now say "PS-M-EXPORT-001-P03 … under the same ids", which contradicts itself but does not affect the tool.
  - 33-control-plan: two `part_standard_refs`.
  - 30-ebom is untouched. P03/P04 were not already used, and nothing longer shares those ids as a prefix.

**Q6 (what else I would not trust):**
- After distribution, MoviePad-Remake, the only product with part standards, fails at HEAD. E12 would then refuse every acceptance there, including code-only ECOs. The process's "applied with known defects" route (`known_defects`, KD-…) has no way through E12 except dropping the field (E08) or `--no-verify`. The distribution ECO should declare this or provide a route.
- E12 runs the working-tree copy of the tool (process-validator.py:708), so an unstaged edit runs. This is the same trust class as the validator itself, but it is not declared.
- Rules 1, 2, 3, 6 and C1-a still have no positive control on a real file (already declared).

Nothing was modified, committed or pushed in any repository. My temp product, my case folders and my scratch scripts are removed.
