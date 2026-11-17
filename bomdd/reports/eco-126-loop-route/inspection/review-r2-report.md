# ECO-126 — the fresh-context review, round 2 (the last; 2026-11-17): results, condensed, and what was done

Another fresh context of the producer's equipment. Its task was correction confirmation and regression on the repaired tree.
The numbering is the reviewer's. Nothing of substance was repaired after this round (two rounds are the limit); statements
that said more than the tools do were narrowed, and the rest is listed as known defects (KD) for the user to accept or send back.

## Round 1's findings

- **Closed** (the reviewer ran or read each): 1-9, 12-24, 28-31, 34, 35.
- **Not closed**: 10 (a record that is not UTF-8 still ends in a traceback → KD-01), 11 (`"main": []` in the manifest → KD-02),
  26/27 (one self-test arm of `handover-stamp` survives the removal of what it names → KD-10), 33 (one label of V5 said "only"
  for a count plus keywords → the label was reworded), 36 (no full self-conformance output in the folder → copied in:
  `../full-self-conformance-run2.txt`), 39 (the text said `--check` exits 1 on every gap the format names → narrowed, KD-03).
- **Recorded, not repairs**: 25, 32, 37, 38 (the order's section 4), 40, 41. **Not checked**: 42.

## New findings and their disposition

| # | Layer | Finding | Disposition |
|---|---|---|---|
| N1 | substance | `loop-count`: a record that is not UTF-8 → traceback, exit 1 (the header says 2) | **KD-01**; declared in the tool's header |
| N2 | substance | `handover-stamp check`: a manifest whose `main` / `program` is not a string, or a log that is a directory → traceback, exit 1 (the code the skill reads as "another build ran") | **KD-02**; declared in the tool's header |
| N3 | substance | `loop-count --check` does not check: a reply with no reaction row; duplicate report ids; `jig`; missing or non-numeric `limits` / `budget`; the contents of `launches`; an item's `round` | **KD-03**; the list is now in the tool's header, and the route's sentence about `--check` is narrowed |
| N4 | substance | `loop-count`: a value YAML retypes (an unquoted timestamp, `words: no`) is reported as missing | **KD-04** (it fails closed); a note on quoting is in the header |
| N5 | substance | `eco-turn`: on exit 3 the skill says to add "どの版かは不明" to the class, which is a closed list; `launches: unknown` against the record line `{count: 0, matching: 0}`; exit 2 is not mentioned | **KD-05** |
| N6 | substance | the words for an item's kind, disposition and outcome are listed without meaning; the skill's two lists and the confirmation items are not mapped to them | **KD-06** |
| N7 | substance | `ui-ir-ui-bom.md`: "not applied to a ledger with no bundle" is not what the gate does | narrowed in the text: "no bundle and no `touches_confirmed` field" |
| N8 | substance (low) | the status note becomes "golden 待ち" after the reply, not at the stop where golden is awaited | **KD-07** |
| N9 | substance (low) | `CLAUDE.product.md` names one stop of the skill; `eco-file.md` says gate ① asks "only" and omits the acceptance criteria | **KD-08** |
| N10 | substance | `handover-stamp`: names made of the stated characters are refused when a segment starts with `.` or holds `\` | the start-of-segment rule is now stated in the header |
| N11 | substance (low) | `eco-turn`: "exit 0 — the handed build ran" does not carry the tool's limits | narrowed in the text |
| E1 | evidence | `loop-count --selftest`: 22 of the reviewer's 47 mutants are killed (25 survive: several checks added in the repair, item checks, shape checks, parts of the tally, the `[over]` line) | **KD-10**; the numbers are in the tool's header |
| E2 | evidence | `handover-stamp --selftest`: 13 of 25 mutants are killed (survivors include: mismatch dropped from the exit condition, the record line's `matching`, four clauses of the manifest check) | **KD-10**; the numbers are in the tool's header |
| E3 | evidence | no full self-conformance output in the folder | copied in |
| E4 | evidence (low) | V5's path count predated ten files | V5 re-run at the end |
| R1 | record | V4's labels say "eco-turn R3 / R4"; the skill now calls them A3 / A4 | **KD-11** (left) |

## Known defects, in one list (for the acceptance request)

- **KD-01** `loop-count`: a record that is not UTF-8 ends in a traceback with exit 1 instead of `[input]`, exit 2.
- **KD-02** `handover-stamp check`: a malformed manifest (`main` / `program` not a string) or a log that is a directory ends in a
  traceback with exit 1, the same code as "another build ran".
- **KD-03** `loop-count --check` does not check six rules its format names (listed in the tool's header). In particular a round
  with a reply and no reaction row passes, so a bare "合格" can be left out of the count of kinds.
- **KD-04** `loop-count`: unquoted values that YAML retypes are reported as missing.
- **KD-05** `eco-turn`, exit 3 of the launcher check: the instruction does not fit the record's fields.
- **KD-06** the vocabulary of an item's kind, disposition and outcome is not explained anywhere in the kit.
- **KD-07** the status note "golden 待ち" is set one step late.
- **KD-08** two entry texts say less than the route (`CLAUDE.product.md`, `eco-file.md`).
- **KD-09** (from V4) a product with three states can return from the confirmation items to a round only if `implemented` is in
  `open_states`; read from the validator, not run.
- **KD-10** the self-tests of `loop-count` and `handover-stamp` cover part of their checks (22 of 47 and 13 of 25 mutants killed).
- **KD-11** V4's labels use the old names R3 / R4; one of its PASS lines does not depend on the exit code it prints.
- **UR-1 to UR-3** (not defects — repairs the inspector has not seen): the three GU7 repairs made after the independent
  inspector's last round (`gu7-after-r2.md`).
