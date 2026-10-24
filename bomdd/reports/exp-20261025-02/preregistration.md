# EXP-20261025-02 — pre-registration (written before any scan of the delivery)

Question (`method/improvements.md`, EXP-20261025-02): does the code of MoviePad-Remake delivery 1 (`f30d771`) have cross-unit dependencies that
the part standards (`bomdd/32-mbom.yaml` at `f30d771`, equal to `bom-v4`) do not declare? Read-only on the product; everything is read with
`git show` / `git ls-tree` at `f30d771`.

## Fixed before results

1. **File → unit.** Measured before writing this (`git show f30d771:bomdd/32-mbom.yaml`): `artifact.path` cannot map files to units — M-EXPORT-CLOCK-001,
   M-EXPORT-COPY-001 and M-EXPORT-001 share `src/MoviePad.Core/Export`; M-MEDIA-TOOLS-001 and M-PROBE-001 share `src/MoviePad.Core/Media`;
   M-DOCUMENT-001's `src/MoviePad.Core/Editing` contains M-HISTORY-001's `History.cs`. The entry's "by `artifact`" is therefore replaced by:
   each unit's `planned_output_artifact_ref`, split on commas; an entry without a `/` is a file name in the folder of the unit's first entry;
   an entry that is a folder owns every file under it. A delivered `.cs` file owned by no unit is reported **unowned**; by two, **ambiguous**.
   This ambiguity of `artifact` is itself a finding of the run (reported, not repaired).
2. **What a dependency is.** For each `.cs` file: comments (`//`, `/* */`) and string literals (regular, verbatim, interpolated text parts) are
   blanked, then every identifier token is looked up among the type names declared (`class`, `record`, `struct`, `interface`, `enum`, `delegate`)
   in other units' files. A unit A depends on B when any file of A has such a token for a type declared only in B. A type name declared in two
   units is reported **ambiguous** and not attributed.
3. **What is declared.** A declares B when one of A's `part_standard.requires` targets an id in B's `part_standard.provides`. `depends_on` is
   reported beside it (ECO-114's A1 already requires it to equal the resolved requires).
4. **Verdicts per pair (A, B):** referenced and declared → `declared-used`; referenced, not declared → **`undeclared`** (the measure);
   declared, not referenced → `declared-unused`, reported as information, **not** a defect (ECO-114 does not forbid declaring a use the code
   happens not to make; decided now, before reading).
5. **Scope of the verdict.** The production units (`src/`) carry the reading. The self-acceptance unit (`test/`, M-SELF-ACCEPTANCE-001, which
   requires only M-SOLUTION-001) is scanned and reported apart: its tests exercise every unit, so its references are expected, and whether a test
   unit must declare them is a separate question (ECO-114 does not say). M-SOLUTION-001 owns no `.cs` file.
6. **Calibration first (known labels, independent of the scanner):**
   - **Synthetic fixture** (built by the calibration script): three units — A references B (declared) and C (not declared); B declares C but does
     not reference it; C's type name also appears in A only inside a comment, a string literal and a verbatim string. Expected exactly: A→B
     `declared-used`, A→C `undeclared`, B→C `declared-unused`, no other pair, and the comment and string mentions not counted.
   - **Real copy, one undeclared reference added:** the delivery's `History.cs` (M-HISTORY-001, requires none) with one added line using
     `TimeMath.MinLen` (M-DOCUMENT-001). Expected: M-HISTORY-001 → M-DOCUMENT-001 `undeclared`, and otherwise the same as the unaltered run.
   The scanner is used on the delivery only if both arms give exactly their expected output.
7. **Reading.** Zero `undeclared` among production units → ECO-114's declarations held on this delivery (one product, one delivery). Any → A1/C1's
   limit is measured on a real delivery; whether a check belongs in the part standard is a separate decision. No gate is added by this EXP.

## Limits declared now

- Type names only: a dependency through an extension method called without its type name, through reflection, or through a string (a file path,
  a process name) is not seen. A shared name in different namespaces is reported ambiguous rather than resolved.
- One C# project, one delivery, one product.
