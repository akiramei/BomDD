# EXP-20261030-04 — definitions (fixed before any scenario is written, any mock is generated or any check is run)

Fixed 2026-10-30. A change after this point is a departure (section 12).

## 1. The question

The user (2026-10-30), after EXP-20261030-01/-02/-03: with an imperfect upstream, a failed check cannot be told apart — is the
upstream (use cases, requirements) wrong, or the checking mechanism? With an upstream known to be correct, a failure can be
attributed. A remake has an authority product, so a correct upstream can be written and checked against it. The user chose
MoviePad-Remake's authority as the subject, the experiment folder as the place (not the product's scope), and machine
certification of the scenarios ("B: 機械で確かめる").

**Stage 1 (this experiment):** given use case scenarios certified by execution on the authority (MoviePad `126eae9`) and a mock
generated from the authority that every scenario walks cleanly, does a deterministic walk of the scenarios over the mock catch
structural defects seeded into the mock, and stay silent on the clean mock and on equivalent changes? A miss is reported **inside**
or **outside** the scenarios' coverage (section 7): inside belongs to the mechanism, outside to the upstream's completeness.

Stage 2 (not filed): the same seeded mock with an ordinary upstream (an AI draft from the requirements), to measure the upstream's
share. It is worth running only if stage 1 shows the mechanism sound inside coverage.

This is a measurement. It changes no method text, template, tool or product. Nothing is written into MoviePad or MoviePad-Remake;
the authority is read by `git archive` / `git show` of `126eae9` into a staging folder outside every repository.

## 2. What "correct" means here — and what it does not

- **Correct** = every step of every frozen scenario executes on the authority's view model as written (section 4). Checkable.
- **Complete** is not claimed: no check says the scenarios contain every use the authority supports. The coverage measure
  (section 7) reports how much they touch; misses outside it are the upstream's, by definition.
- "Correct" is relative to the authority, defects included: what the authority does is taken as right.
- What the harness can execute is the view model and the views' bindings (section 4), not rendering, layout or I/O.

## 3. Scenario schema (`scenarios.json`)

```
{"states": [{"id", "name", "predicate": {<VM property path>: <value>, ...}}],
 "scenarios": [{"id", "title", "goal", "flow": "main"|"alternate", "setup": [<setup op>],
                "steps": [{"in": <state id>, "action": <action id>, "surface": <view name>, "expect": <state id>}]}]}
```
- An **action id** = the bound command's name without `Command`, plus `:<CommandParameter>` when the binding has one
  (`ApplySpeedPreset:2`, `SelectFormat:Mp4`). The same ids are used by the mock (section 5).
- `surface` = the view file that holds the control (`ToolbarView`, `InspectorView`, …; `MainWindow` for its own bindings).
- A **state** is a named predicate over view-model properties (equality on bool, enum, int, string, or `null` / `not-null`).
  States are the writer's; the harness checks them, it does not invent them.
- `setup` ops (the only way to reach a start point the commands cannot): set a public settable VM property (`Playhead`,
  `UseExternalPlayback`, `State` via a named `DocumentState` method). Listed per scenario and counted.
- Steps whose command opens a file dialog or runs an external process (`Open`, `ConfirmExport`, `InstallFfmpeg` and any other the
  harness finds needing `StorageProvider`, ffmpeg or VLC) are written with `"harness": "no"`: the walk over the mock still checks
  them; their certification is by the binding only (section 4) and they are counted apart.

## 4. Certification on the authority (the harness; machine, not reading)

`harness/` — a .NET console program (not a test project) built in the staging folder against an archive of `126eae9`
(`MoviePad.csproj` referenced as a project). It does two things:

1. **Binding extraction.** Parses `Views/*.axaml` as XML. For every element with `Command="{Binding XCommand}"`: action id,
   surface, `CommandParameter`, and the `IsVisible` / `IsEnabled` binding paths of the element and of its ancestors within the file
   (and, for a `UserControl` placed in `MainWindow.axaml`, of the placing element). A binding through a converter other than
   `EqualsConverter` / `!` negation, or a path the harness cannot resolve on the VM, makes that action's availability **unknown**;
   unknown actions are listed and excluded from the mock (counted). Output: `bindings.json`.
2. **Scenario execution.** For each scenario: a fresh `new MainWindowViewModel()` (the sample document loaded, as in the
   authority's own tests), the `setup` ops, then per step: (i) the `in` predicate holds; (ii) the action is **available** —
   every visibility and enabledness path of its binding evaluates true and the command's `CanExecute(parameter)` is true;
   (iii) its surface equals the step's `surface`; (iv) the command executes (skipped for `"harness": "no"`, which then must have
   (i)-(iii) and ends the scenario's executed part); (v) the `expect` predicate holds. Output: `certify.json`, pass/fail per step.

A scenario is **certified** when every executed step passes. The scenario writer may run the harness while writing (section 8).
After the writer stops, the harness is run once more by the experimenter on the final file; failing scenarios are dropped and
counted, and the remaining file is frozen (SHA-256 in `freeze.json`). Values that depend on the machine (`FfmpegLocator.Available`,
the UI culture) are recorded in `certify.json`.

## 5. The mock (generated, not drawn)

`gen_mock.py` writes `mock.html` from the frozen scenarios and the harness:
- one `<section data-ui-state="<state id>">` per state the frozen scenarios visit, its representative being the first view-model
  instance at which that state holds during certification;
- in it, one element per extracted action available or present in that instance: `data-ui-action`, `data-ui-surface`,
  `data-ui-enabled` (`true`/`false`; not present when invisible), and `data-ui-goto` = the state id that holds after executing it
  from the representative (computed by the harness on a clone of the instance; `"unknown"` when no declared state holds or the
  command is `"harness": "no"`), plus its label from the resource strings.

So the clean mock is the authority's availability, ownership and transitions on the visited states, by construction. States the
scenarios never visit are not in the mock — a limit of stage 1 (section 11).

## 6. Seeded defects (a fresh agent that never sees the scenarios)

One fresh Claude agent, given only `mock.html`, `bindings.json` and the class list below, writes **31 mutants** — one change
each, a copy of `mock.html` per mutant plus a `mutants.json` row (`id`, `class`, what was changed). It chooses the targets.

| class | change | count | the recorded defect it stands for |
|---|---|---|---|
| a | an action absent from, or disabled in, one state where it is present and enabled | 5 | D2 (ECO-VT-040) |
| b | two parameter values of one action merged into one (one value's element removed everywhere) | 5 | D3's kind merge (ECO-VT-226) |
| c | one member of an undo pair removed everywhere (Undo/Redo, Split/DeleteSelectedBoundary, a toggle's other state, …) | 5 | D1 (ECO-VT-035) |
| d | an action moved to a different surface | 5 | ViewPrism2 ECO-140 (ownership) |
| e | an action's `data-ui-goto` changed to another existing state | 5 | a wrong transition |
| f | equivalent: a label's text changed, elements reordered, an extra disabled element with a new action id added | 6 | control — must be silent on the stop checks |

## 7. Checks (`walk.py`, deterministic) and coverage

| check | label | fires when |
|---|---|---|
| W1 walk | stop | a step's `in` state has no section, or its action has no element in that section, or the element is `data-ui-enabled="false"` |
| W2 surface | stop | the element's `data-ui-surface` differs from the step's `surface` |
| W3 transition | stop | the element's `data-ui-goto` differs from the step's `expect` (not checked when either is `"unknown"`) |
| W4 reverse coverage | measure | an enabled element in the mock that no step uses |

**Coverage** = the (state, action) pairs present and enabled in the clean mock that some frozen step uses, over all such pairs;
also the extracted actions used by some step, over all extracted actions with known availability. A mutant is **inside** coverage
when the element it changes (for `b`, `c`: any element it removes) is a pair some step uses; otherwise **outside**.

A mutant is **caught** when W1-W3 fire on it and not on the clean mock. For `f`, any W1-W3 flag is a **false alarm**.

## 8. Order (each step's output is committed or hashed before the next starts)

1. Build the harness; its selftest (synthetic axaml and a stub view model) covers every extraction rule and every step check,
   each with a firing case and a silent twin, and is reported check by check (the EXP-20261030-03 correction).
2. **One real slice end to end first** (the 2026-10-30 lesson, `run-new-instrument-on-real-files`): `bindings.json` on the real
   archive, one hand-written two-step scenario certified, a mock generated from it, the walk run on it (0 flags), one mutant of
   each class a-e caught. Only then the writer starts.
3. Scenario writer: one fresh Claude agent, given the archive (read-only), the authority's `README.md` / `README.ja.md`, the schema
   and the harness command. Told to write what a user does with the application — main flows and alternate flows (undo, cancel,
   retry, another way in) — not to aim at passing, and not told about mutants, classes or checks. Bound 60 minutes, liveness by
   the output file's modification time every 10 minutes.
4. Certify and freeze (section 4). Generate the mock (section 5). Run W1-W4 on the clean mock: **W1-W3 must be 0** (the clean
   control, checked before any mutant exists; OBS-20261030-04's lesson). Not 0 → a defect of the harness or generator, fixed and
   recorded as a departure before going on.
5. Seeder (section 6), bound 30 minutes. Its mutants are checked mechanically to be one change each from the clean mock.
6. Run W1-W4 on every mutant. Tally.

## 9. Reading (fixed now)

1. **Inside coverage, classes a-e**: caught / inside, per class.
   - Every inside mutant caught and **f** gives 0 false alarms → "with a correct upstream, every miss of the walk is attributable
     to coverage" — stage 2 earns a run (its design and start are the user's).
   - Any inside mutant missed → the mechanism has a gap at that class, named from the mutant (not a claim about upstreams); stage 2
     waits for that gap to be closed.
   - Any **f** false alarm → the mechanism reads something not structural; named.
2. **Outside coverage**: counted per class and reported as the upstream's share for this scenario set; W4 on each is reported.
3. **Coverage** (both ratios) is reported as the upstream's completeness measure.
4. **Expected by construction**, since the scenarios and the mock share action ids, state ids and surfaces: W1 catches inside
   `a`, `b` and `c`; W2 inside `d`; W3 inside `e`; `f` is silent unless the walk reads labels or order. Reading 1 is therefore a
   qualification of the instrument (an inside miss means an implementation defect), not evidence that the mechanism works in
   real use. What stage 1 measures that is not fixed by construction: **coverage**, and **how many of a seeder's freely chosen
   defects fall inside a correct, certified scenario set** — the upstream's reach. In real work two more things can fail, which
   stage 1 removes on purpose: the scenarios can be wrong (stage 2), and the binding between scenario words and a designer's mock
   is not given (a later stage; not filed).

## 10. Also reported (descriptive)

Bindings extracted / unknown; states declared / visited; scenarios written / certified / dropped; steps with `"harness": "no"`;
setup ops per scenario; the time of each agent run; per mutant the flags by check.

## 11. Limits

- Stage 1 measures the mechanism's upper bound with a correct upstream; it says nothing yet about ordinary upstreams.
- The mock is generated from the authority, sharing the scenarios' action ids: the binding between upstream and design is given,
  which in real work it is not (a designer's mock has its own names). The mock covers only visited states.
- Seeded defects only. MoviePad-Remake's own recorded defects are mostly values, orders, tolerances and formats (EXP-20261030-01:
  1 of 20 structural), so they do not exercise this mechanism.
- MoviePad is a small single-document editor; ViewTube's mode x selection x kind combinations are mostly absent. Transfer to a
  product of that size is a separate question.
- The harness executes the view model and bindings only; layout, rendering, keyboard shortcuts and I/O are outside it.
- One scenario writer, one seeder: no rate is claimed.

## 12. Files and the run (when the user starts it)

- Committed at filing: this file. At the run: `harness/` (source), `gen_mock.py`, `walk.py`, `bindings.json`, `scenarios.json`,
  `certify.json`, `freeze.json`, `mock.html`, `mutants.json` and the mutant files, `flags.json`, `results.md`.
- The staging folder (the archive, the build output) is outside every repository and deleted after the recording commit on the
  user's word.
- Departures are recorded here, below, with the reason and when.

## 13. Departures

Recorded 2026-10-30 while building the instruments, before the scenario writer started (the slice of section 8 step 2 had run).

- **D1 — `data-ui-goto` is a set.** Declared states may overlap, so the harness writes the space-separated set of declared
  states that hold after the action (`unknown` when none holds, `-` on a disabled element). W3 fires when the step's `expect` is
  not in the set.
- **D2 — a state must be an availability class.** Section 5 took the first instance of a state as its representative; that is
  only sound if every visit to the state shows the same availability and the same transitions. The harness reports a state as
  **ambiguous** when its availability vector (every known action: enabled / disabled / absent), or the states reached by an
  executed action from it, differ between visits. The writer sees the report and may refine the predicates. After the writer
  stops, scenarios visiting an ambiguous state are dropped, repeated until stable, and counted (`dropped_for_ambiguity`).
- **D3 — modal overlays.** The axaml has three full-cover overlays (`Background="{StaticResource ScrimBrush}"`: export dialog,
  About, ffmpeg setup). While one is visible only the topmost one's controls are available (document order in `MainWindow`).
  Without this rule the toolbar would count as usable behind an open dialog.
- **D4 — binding variables recorded.** `certify.json` lists, at each point of each scenario, the value of every view-model path
  the bindings read (15 paths), so that states can be written exactly.
- **D5 — one-change check for class f** compares labels and element order (a label-only change is otherwise invisible to the
  structural diff). The walk itself still reads no label and no order (`walk.py selftest`, "labels and order are not read").
- **D6 — what extraction found** (facts, not a change): 45 command bindings, 44 action ids, 0 unknown, 3 overlays; 24 code-behind
  lines act without a `Command` binding (format selection, exclude / mute / pitch / aspect toggles, width and height entry,
  keyboard shortcuts) and are outside the extraction, as section 4 fixed. Machine values: `FfmpegLocator.Available` = True,
  UI culture ja-JP; labels come from the default (English) resources.
- **D7 — culture reset per view model.** `SwitchLanguage` sets a static singleton (`Localizer.Instance`) and
  `CultureInfo.CurrentUICulture`, which would carry into every later scenario and replay. The harness resets the culture to the
  run's starting one before each fresh view model. A probe through playback, both dialogs, a trim, a speed preset, a scale preset
  and a language switch certified without exception (`TogglePlay` starts its timer without a running dispatcher; no tick fires).
- **D8 — a side effect outside the staging folder, found after the writer stopped; `SwitchLanguage` no longer executed.**
  `SwitchLanguage` calls `AppSettings.Save()`, which writes `%LOCALAPPDATA%\MoviePad\settings.json` — the user's real MoviePad
  settings. The harness executed it in the D7 probe, in the slice's mock generation and in every certify run of the writer (mock
  generation executes each enabled action once per state to compute `data-ui-goto`). The file's last write was 21:24:07
  (content `{"language": "ja"}`); its content before the run was not recorded and is unknown. The writer's report named the write;
  the harness was then changed, before the experimenter's certification, to treat `SwitchLanguage` as not executed (like the
  async commands: a step needs `"harness": "no"`, its goto is `unknown`), and the file's modification time was checked unchanged
  across that certification. No frozen scenario uses `SwitchLanguage`. Sealed inputs were unchanged by the writer (455 files).
  The certification, the mock and the walk therefore ran on a rebuilt `Harness.dll` (21:25:38, SHA-256
  `adc602fede37b3b16b68ebab405e06abd14447996c8b60bfc6f14494dcbd5be6`), not the sealed one (`4d37f7a3…`); the source change is
  the `NoExecuteCommands` line for `SwitchLanguage` in the committed `harness/Program.cs`, and `seal_inputs.py check` after the
  run reports that file as the only one of 455 differing. Its effect, checked leaf by leaf: the writer's `mockdata.json` and the
  run's differ in 46 values, all `SwitchLanguage:en` / `:ja` gotos (the state itself → `unknown`); the writer's `certify.json`
  is byte-identical to the run's (no frozen step executes `SwitchLanguage`).
- **D9 — mutants stored as line edits (recorded after the walk, before the recording commit).** Section 12 named the mutant
  files; the 31 copies are 3.6 MB, so `run/mutant-edits.json` holds each mutant as line edits against `run/mock.html` with the
  file's SHA-256, and `record_mutants.py verify` rebuilds all 31 byte for byte (0 mismatches against the seeder's files before
  the staging folder is deleted). The walk ran on the seeder's files, not on the rebuilt ones.
