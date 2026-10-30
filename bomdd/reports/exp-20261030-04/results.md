# EXP-20261030-04 — results (stage 1)

Run 2026-10-30 on the user's "走らせる", by `definitions.md` as filed in `bc3dff8` (departures D1-D9 in section 13).
Authority: MoviePad `126eae9`, read by `git archive` into a staging folder outside every repository; nothing was written into
MoviePad or MoviePad-Remake. One side effect outside the staging folder happened (section 6).

## 1. The run, in the order of section 8

1. **Harness.** `harness/` (net10.0 console, ProjectReference to the archived `MoviePad.csproj`) — selftest PASS, 20 checks
   reported one by one, each with a firing case and a silent twin (extraction X1-X7, step checks C1-C8, mock generation G1-G2,
   ambiguity A1). `walk.py selftest` PASS, 11 checks, including "labels and order are not read".
2. **Real slice end to end.** `bindings.json` on the real archive (45 command bindings, 44 action ids, 0 unknown, 3 overlays, 24
   code-behind lines outside extraction — D6); a hand-written scenario certified (`slice/`); its mock walked with 0 flags; one
   mutant per class: a, c, d, e caught; b fell outside the slice's coverage (its two values were not used by the slice).
3. **Scenario writer** (one fresh Claude agent, `writer/prompt.md`): 21:13:25 to 21:24:23, about 11 minutes of a 60-minute bound.
   It wrote 22 scenarios (15 main, 7 alternate), 49 steps (4 with `"harness": "no"`), 28 states. Isolation (`isolation.py` over
   its transcript): 3 flags, all a `cd` into the staging root followed by reads of `writer/`, `authority/` and `bindings.json`
   only (all three given). Sealed inputs (`sealed-inputs.json`: archive, `bindings.json`, the built `Harness.dll`, the prompt):
   0 of 455 files changed after the writer.
4. **Certify and freeze.** All 22 certified on `new MainWindowViewModel()`; 0 ambiguous states; 0 dropped for failure or
   ambiguity. Frozen as `run/scenarios-frozen.json`, SHA-256 `ce0d305c3b592d1a63ff2687c9be756e3499a061f75dffc40d7481b86b05e5be`
   (`run/freeze.json`); the frozen file re-certifies to the same `certify.json`. Mock generated from the authority on the visited
   states: 27 sections, 859 elements (`run/mock.html`). **Clean control: W1-W3 = 0**; W4 = 730.
   (`writer/mockdata.json` differs from `run/mockdata.json` in 46 values, all `SwitchLanguage` gotos: the writer's own runs
   executed it. Certification ran on the harness rebuilt for D8, not the sealed build; D8 records both hashes.)
5. **Seeder** (one fresh Claude agent, `seeder/prompt.md`, never shown the scenarios): 21:26:05 to 21:28:02, about 2 minutes of a
   30-minute bound; isolation 0 flags; `seeder/mock.html` byte-identical to `run/mock.html` after it ran. 31 mutants, all one
   change from the clean mock by the mechanical check (D5). Stored as line edits (`run/mutant-edits.json`, D9).
6. **Walk** on all 31 (`run/flags.json`).

## 2. Verdict by the fixed reading (`definitions.md` section 9)

| class | n | inside | caught inside | outside | caught outside |
|---|---|---|---|---|---|
| a missing / disabled in one state | 5 | 3 | 3 | 2 | 0 |
| b value merged | 5 | 2 | 2 | 3 | 0 |
| c one of a pair removed | 5 | 5 | 5 | 0 | — |
| d moved to another surface | 5 | 5 | 5 | 0 | — |
| e wrong transition | 5 | 5 | 5 | 0 | — |
| f equivalent (control) | 6 | 0 | — | 6 | 0 false alarms |

**Inside coverage every a-e mutant was caught (20 of 20) and f gave 0 false alarms → by reading 9.1, "with a correct upstream,
every miss of the walk is attributable to coverage"; stage 2 earns a run. Its design and its start are the user's.**

By reading 9.4 this is **a qualification of the instrument, not evidence that the mechanism works in real use**: the scenarios
and the mock share action ids, state ids and surfaces, so inside detection was expected by construction, and it came out as
expected — W1 caught a, b, c inside; W2 caught d; W3 caught e; nothing read labels or order.

Per mutant (stop flags on the mutant, 0 on the clean mock):

| mutant | class | what (seeder's words, shortened) | inside | flags |
|---|---|---|---|---|
| M01 | e | ST-02 Undo goto ST-03 → ST-01 | yes | W3 |
| M02 | a | ST-02 Undo disabled | yes | W1 |
| M03 | b | ApplySpeedPreset:1.5 removed | no | — |
| M04 | c | Redo removed | yes | W1 ×2 |
| M05 | d | Undo to TitleBarView | yes | W2 ×7 |
| M07 | a | ST-21 SetTrimOut removed | no | — |
| M08 | e | ST-13 ShowExportDialog goto ST-17 → ST-18 | yes | W3 |
| M09 | b | ApplyVolumePreset:150 removed | no | — |
| M10 | c | DeleteSelectedBoundary removed | yes | W1 ×2 |
| M11 | d | Split to TimelineView | yes | W2 ×3 |
| M13 | a | ST-13 ShowExportDialog disabled | yes | W1 |
| M14 | e | ST-17 CloseExport goto ST-13 → ST-16 | yes | W3 |
| M15 | b | SetFps:60 removed | yes | W1 |
| M16 | c | CloseAbout removed | yes | W1 |
| M17 | d | TogglePlay to ToolbarView | yes | W2 ×4 |
| M19 | a | ST-22 DeleteSelectedBoundary removed | yes | W1 |
| M20 | e | ST-13 TogglePlay goto ST-19 → ST-20 | yes | W3 ×3 |
| M21 | b | Scale:0.75 removed | yes | W1 |
| M22 | c | CloseExport removed | yes | W1 |
| M23 | d | OpenAbout to ToolbarView | yes | W2 |
| M25 | a | ST-15 Redo disabled | no | — |
| M26 | e | ST-06 SetTrimOut goto ST-12 → ST-06 | yes | W3 |
| M27 | b | SwitchLanguage:en removed | no | — |
| M28 | c | ZoomOut removed | yes | W1 |
| M29 | d | SetTrimIn to TimelineView | yes | W2 |
| f: M06, M12, M18, M24, M30, M31 | f | two labels, two reorders, two added disabled buttons | no | — |

## 3. Outside coverage and coverage (readings 9.2, 9.3)

- **Coverage.** (state, action) pairs: **44 of 774** enabled pairs in the clean mock are used by some step (5.7%). Actions:
  **32 of 44** (72.7%). The unused 12: speed 0.25 / 1.5 / 3 / 4, volume 50 / 150, FPS 24 / 30 / 120, `CancelExport`,
  `SwitchLanguage:en` / `:ja`. The pair ratio is small by structure: the toolbar's actions are enabled in almost every state and
  a scenario uses each in a few.
- **Outside, 5 of 25 a-e mutants (the upstream's share for this scenario set):** M03, M09 (speed 1.5, volume 150 — values no
  scenario used), M27 (`SwitchLanguage:en` — the writer left language out after naming the settings write, so this miss is a
  harness limit, D8, not only the writer's choice), M07 (SetTrimOut in ST-21) and M25 (Redo in ST-15) — pairs no step used.
- **W4 on the outside mutants gave nothing:** `new_w4` is empty for every mutant. W4 lists enabled elements no step uses; a
  removal or a disable takes an element away and cannot add one, so W4 cannot point at these misses by its definition. It is
  uninformative here, not silent by chance.

## 4. Also reported (section 10) and read after the verdict (descriptive, not readings)

- **The upstream's reach: 20 of 25 freely chosen structural defects fell inside a certified scenario set that uses 5.7% of the
  pairs.** Split by how a class spreads:
  - action-level classes (b, c, d change an action in every state): inside when any step uses the action. c and d: 10 of 10
    (22 of the 23 actions without a value are used). b: 2 of 5, near the share of value actions used (10 of 21).
  - pair-level classes (a, e change one state): 8 of 10 inside, against 5.7% if pairs were chosen evenly. The seeder put a and
    e on salient pairs (Undo after a split, the export dialog, play, trim) — the same pairs a scenario writer reaches first. The
    seeder even chose the same pair twice (ST-02 Undo for M01 and M02; ST-13 ShowExportDialog for M08 and M13).
  So 20 of 25 is not a property of the scenarios alone: it is a property of these scenarios **against this seeder**, and the two
  agents' shared sense of what matters makes it high. A rate for real defects is not claimed.
- Bindings 45 / unknown 0; states declared 28, sections generated 27: ST-28 is only the `expect` of two `Open` steps marked
  `"harness": "no"` (UC-20, UC-21; `Open` is asynchronous), so the harness never reaches it. The 4 not-executed steps are those
  two, `ConfirmExport` (UC-12) and `InstallFfmpeg` (UC-19); the walk still checks W1 and W2 on them, and their transitions are
  not checked. Setup ops per scenario 1-2 (`run/freeze.json`).

## 5. Limits (in addition to `definitions.md` section 11)

- **Correlation between seeder and writer** (section 4): both are Claude agents choosing what a user would do or what a
  designer would get wrong; inside rates for pair-level classes depend on it.
- **W4 is uninformative for removals** (section 3): reverse coverage cannot point at what is missing.
- **M27 is a harness limit:** with `SwitchLanguage` not executed (D8) the writer avoided it.
- The f control exercises labels, order and added disabled buttons only; a walk that read enabled-but-unused elements would not
  be tested by it.
- **Corrected 2026-10-30 after stage 2 (EXP-20261030-05 `results.md` section 3):** `definitions.md` section 5 says the clean mock
  is "the authority's availability, ownership and transitions on the visited states". For transitions that holds only on the
  **paths** stage 1 took: Undo and Redo from ST-02, ST-03, ST-04, ST-05 and ST-08 depend on the undo history, which the state
  predicates do not carry, and stage 2's writers reached those states by other edits where the authority's Undo / Redo go
  elsewhere (the harness then reports the five states ambiguous). Stage 1's own scenarios are consistent with the mock (0
  ambiguous over its visits), so its verdict and placements are unchanged; what changes is the reach of "the mock is the
  authority's".
- Stage 1 removes, on purpose, the two things that fail in real work: wrong scenarios (stage 2) and the binding between scenario
  words and a designer's mock (not filed).

## 6. A side effect on the user's machine (D8)

`SwitchLanguage` calls `AppSettings.Save()`, which wrote the user's real `%LOCALAPPDATA%\MoviePad\settings.json` during the D7
probe, the slice's mock generation and the writer's certify runs. The file's last write was 21:24:07 with content
`{"language": "ja"}`; **its content before the run was not recorded and is unknown**. The harness was changed before the
experimenter's certification so that `SwitchLanguage` is never executed, and the file's modification time stayed unchanged
across that certification. If MoviePad's language setting was something else, it needs to be set back by the user.

## 7. Files

`definitions.md`; `harness/` (source); `build_harness.py`, `seal_inputs.py`, `isolation.py`, `freeze.py`, `gen_mock.py`,
`walk.py`, `record_mutants.py`; `bindings.json`, `sealed-inputs.json`; `slice/`; `writer/` (prompt, the writer's own
`gen.py` / `derive.py` / `states_assign.json`, start time); `seeder/` (prompt, `mutants.json`, start time); `run/`
(`scenarios-written.json`, `certify.json`, `freeze.json`, `scenarios-frozen.json`, `mockdata.json`, `mock.html`,
`mutant-edits.json`, `flags.json`). The staging folder (archive 758 MB, build output 744 MB) is deleted on the user's word.
The hashes cited here are of files written with LF (`run/scenarios-frozen.json`, `run/mock.html`) or are held inside a file
(`mutant-edits.json`, `sealed-inputs.json`). The harness and the writer's scripts wrote the other JSON and Python copies with CRLF;
the repository's `.gitattributes` (`eol=lf`) stores them with LF, so their committed bytes differ from the staging copies by line
endings only, and `seal_inputs.py check` cannot be reproduced from the committed `bindings.json`.
