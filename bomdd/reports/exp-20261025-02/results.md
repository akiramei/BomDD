# EXP-20261025-02 — results: no undeclared cross-unit dependency in MoviePad-Remake delivery 1's production units

Run 2026-10-25 on MoviePad-Remake `f30d771` (read-only, `git show`), after `preregistration.md` (`9f31cdd`, amended before the scan). Output:
`results.txt`; command in `README.md`.

## Calibration (before the delivery was read)

- Arm 1, synthetic fixture with known labels: exactly the expected pairs (A→B `declared-used`, A→C `undeclared`, B→C `declared-unused`); A→C found
  only through the reference inside an interpolation hole; the type names in a comment, a string, a verbatim string and an interpolated string's
  text did not count (no A→D pair).
- Arm 2, the delivery with one undeclared reference added to `History.cs`: the only difference from the unaltered scan is M-HISTORY-001 →
  M-DOCUMENT-001 `undeclared`.

## Result

- **Production units (`src/`): 13 cross-unit dependencies, all declared (`declared-used` 13); `undeclared` 0; `declared-unused` 0.** Every
  `requires` in the part standards that names another unit is used by the code, and the code uses no other unit. Read as pre-registered:
  ECO-114's declarations held on this delivery (one product, one delivery).
- Self-acceptance unit (`test/`, reported apart): references all 8 production units, declares none of them (its only `requires` is
  M-SOLUTION-001, which owns no `.cs` file, so that pair is `declared-unused`).
- Mapping: every delivered `src/` and `test/` file has exactly one owner; no type name is declared in two units; every unit's `depends_on` equals
  its resolved `requires`. One unowned file: `tools/harness-runner/Runner.cs` — the designer's instrument, which no M unit is meant to own.
- Run twice, byte-identical.

## Findings beside the measure

1. **`artifact.path` does not identify a unit's files.** Five of the ten units share a folder with another unit (the three Export units, the two
   Media units), and M-HISTORY-001's file is inside M-DOCUMENT-001's folder. Ownership was recoverable only from `planned_output_artifact_ref`,
   whose short form (a bare file name read against the folder of the first entry) is a convention of this product's M-BOM, not a rule of the
   template. A tool reading `artifact` alone would mis-assign files.
2. **The self-acceptance unit uses every unit and declares none.** ECO-114's rule that a consuming unit names what it uses is silent on a test
   unit; whether it should declare them, or is exempt by kind, is not decided anywhere.

## Limits

Type names only (an extension method called without its type, reflection and string-based lookups are not seen); a type declared in two units would
not be attributed (none here); raw string literals are not handled (none here); one C# project, one delivery, one product. The result says the
declarations matched the code, not that the declared interfaces behave together (ECO-114 L1).
