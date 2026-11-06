# EXP-20261107-01 — definitions (fixed before any writer starts or any example is executed)

Fixed 2026-11-07. A change after this point is a departure (section 11).

## 1. The question

The user built BehaviorForge (`C:/Users/akira/source/repos/BehaviorForge`, a document-and-template kit, no executable parts)
after feedback that the re-implementations of MoviePad, ViewTube and ViewPrism2 had software CAD and mocks but a weak domain
model and weak verification. My reading of the kit (2026-11-07, in conversation) was: useful as a reading discipline, not yet an
answer to the feedback, and not measured. The user chose "A: 実機能で試す" — try the kit as it is on one real feature with
history and enablement, and measure against the authority.

**The question:** given the same sources and the same deliverables, do fresh AI writers who use BehaviorForge write an upstream
for MoviePad's undo / redo that (1) holds better when its concrete examples are executed on the authority, and (2) treats the
authority's facts better — fewer unfounded completions of what the sources leave open, as many of what the sources do say —
than fresh writers given the same task without the kit?

This is a measurement. It changes no method text, no kit file and no product. MoviePad and MoviePad-Remake are read by
`git show` only; BehaviorForge is read and copied, never written (it has no commits; its 18 files are hashed, section 3).

## 2. The feature and the authority's facts (fixed now, from the code)

Feature: undo / redo of document edits in MoviePad (`126eae9`), with the buttons' availability and what is shown after each
press. Read from `Services/History.cs`, `ViewModels/MainWindowViewModel.cs` (`CommitEdit`, `Undo`, `Redo`, `Split`,
`SetTrimIn`, `SetTrimOut`, `ApplySpeedPreset`, `ApplyVolumePreset`, `Scale`, `SetFps`, `LoadClip`) and
`Models/DocumentState.cs` (`ResolveSelection`).

Each fact is classed **D** (determined by the sources given to the writers: the authority's `README.md` / `README.ja.md` and
MoviePad-Remake's `bomdd/10-requirements.yaml` at `a2ca41e`, by statement or by a direct derivation) or **N** (not determined
by them). The class is fixed here, before any output exists; it is what turns a wrong assertion into an unfounded completion.

| id | the authority's behaviour | class | basis in the sources (D) or why open (N) |
|---|---|---|---|
| F1 | Undo is available when at least one step is recorded; Redo when at least one step has been undone | D | REQ-012 "every edit can be undone and redone" (availability derived) |
| F2 | A new edit after an undo clears the redo steps (Redo unavailable) | D | REQ-012 |
| F3 | Undo of a split, merge, speed or volume preset, Set In / Set Out restores the regions and trim of before; Redo re-applies | D | REQ-012, README "snapshots of the immutable document" |
| F4 | Beyond 50 steps the oldest is dropped | D | REQ-012, README |
| F5 | The selected region after any edit, undo or redo is the region under the playhead (so a split selects the later part) | D | REQ-003 rationale "which region is at the playhead decides the target of every per-region edit", README "the region under the playhead becomes the edit target" |
| F6 | Output size and output frame rate changes are not undone by Undo and record no step | N | REQ-012 "every edit" does not say whether output settings are edits; README says history is of the document but not what the document holds |
| F7 | Undo and Redo do not move the playhead | N | not stated |
| F8 | A speed or volume preset equal to the current value still records a step (Undo becomes available, nothing visible changes) | N | not stated |
| F9 | Set In / Set Out that changes nothing records no step | N | not stated |
| F10 | The unsaved status stays after undoing back to the start | N | not stated (and screens are outside the requirements' scope) |
| F11 | Opening a clip clears the history | N | not stated (scored from the documents only; `Open` is not executed) |

## 3. What every writer is given (applied by `prepare.py package`)

A folder per writer, outside every repository, under the session's scratchpad:

- `sources/README.md`, `sources/README.ja.md` (MoviePad `126eae9`), `sources/10-requirements.yaml` (MoviePad-Remake `a2ca41e`).
- `cad/actions.json` — the 45 rows of EXP-20261030-05 (`../exp-20261030-05/writer/actions.json`, reused by hash): id, the
  screen it is on, the button's label. This is the screen CAD's element list.
- `cad/observations.json` — 19 named observations a user can read on the screen (section 5), each with a one-line meaning
  in Japanese. Their view-model paths are not given.
- `cad/start-screen.json` — the 19 values the harness reads at the start (section 6), as an observed screen: the sample clip
  loaded, the ffmpeg prompt dismissed, the playhead at 20 s.
- `check_examples.py` — checks the form of `examples.json` (ids, names, types, sizes), never its values.
- **Arm K only:** `kit/` — the 18 files of BehaviorForge as they are on disk 2026-11-07 (hashed into `package-sha256.txt`).

Not given to any writer: the code, the tests, the harness, the facts of section 2, earlier experiments' scenarios or mocks.

## 4. Arms and writers

- **K (kit):** the prompt is the kit's own `prompts/start.md` text with its fields filled (target: MoviePad re-implementation,
  undo / redo; sources: the folder; permitted work: analysis and documents; not permitted: code, other folders), followed by
  the common section.
- **C (control):** a neutral prompt — "organise the requirements, write a domain model and the behaviour of undo / redo, and
  list what you would ask the product's owner" — followed by the same common section. It carries none of the kit's rules.
- **Common section (identical bytes in both):** the folder boundary; the deliverables (documents under `out/`, plus
  `examples.json`); the examples schema (section 5); which actions examples may use; that the start screen is observed; 45
  minutes; a short final report.
- Two writers per arm (K1, K2, C1, C2), fresh Claude agents (general-purpose, the session's default model) started together,
  each given only its own folder. Bound 45 minutes; liveness by the newest file's modification time in the folder every 10
  minutes; a writer past the bound is stopped and its files are frozen as they are.

## 5. The examples (`examples.json`) — the machine form both arms add

```
{"examples": [{"id": "EX-01", "title": "...", "basis": "<where in the sources>",
               "steps": [{"action": null | "<action id>", "expect": {"<observation>": <value>}, "unresolved": ["<observation>"]}]}]}
```
- `steps[0].action` is `null` (the start screen) or an action; each later step presses one action. A step's `expect` is what
  the screen shows after it; `unresolved` names observations the writer does not assert there because the sources do not
  settle them. An observation in neither is not asserted.
- Allowed actions (the executable subset): `Undo`, `Redo`, `Split`, `DeleteSelectedBoundary`, `SetTrimIn`, `SetTrimOut`,
  `ApplySpeedPreset:*`, `ApplyVolumePreset:*`, `Scale:*`, `SetFps:*`, `ToStart`, `ToEnd`, `StepBack`, `StepForward`.
  Excluded and said so: `Open`, `ConfirmExport`, `InstallFfmpeg`, `SwitchLanguage:*` (files, external processes, the user's
  settings), `TogglePlay` (a timer), dialogs and zoom (not part of the feature).
- **A press is a press of an enabled button.** To say a button is unavailable, assert its `*_enabled` observation as false;
  never press it. Pressing an unavailable button is counted as the example's error (section 7).
- Observations (19): `undo_enabled`, `redo_enabled`, `split_enabled`, `merge_enabled`, `trim_in_enabled`, `trim_out_enabled`,
  `region_count`, `trim_start`, `trim_end`, `output_length`, `playhead`, `selected_start`, `selected_end`, `selected_speed`,
  `selected_volume_percent`, `out_fps`, `out_width`, `out_height`, `unsaved`. Booleans as `true`/`false`, numbers in seconds,
  percent or pixels with at most 3 decimals. Regions are referred to only through the selected one (there is no index).
- 3-30 examples, 1-15 steps each. `check_examples.py` rejects other forms; a writer may run it any number of times.

## 6. The observing harness (`harness/`, a copy of EXP-20261030-04's with one added command)

`harness observe <bindings.json> <runs.json> <out.json>`: for each run, a fresh view model (the factory and the
`SwitchLanguage` exclusion of EXP-20261030-04's `certify`), the setup `ShowFfmpegSetup = false`, `Playhead = 20`; then for each
step the availability of its action by the real bindings (`Certifier.Avail`) — if not `enabled`, the run stops there and the
remaining steps are not run — then the press, then the 19 values read by property path (`Convert.ToString`, invariant).
The mapping from observation to path is fixed in `prepare.py` and given to no writer:
`CanUndo`, `CanRedo`, `CanSplit`, `CanDeleteBoundary`, `CanSetTrimIn`, `CanSetTrimOut`, `RegionCount`, `TrimStart`, `TrimEnd`,
`OutputLength`, `Playhead`, `SelectedRegion.Start`, `SelectedRegion.End`, `SelectedRegion.Speed`, `VolumeText`, `OutFps`, `OutW`,
`OutH`, `Edited`.

Bindings: `../exp-20261030-04/bindings.json`, extracted from the authority (reused by hash, SHA-256 `dfc7fe8c…`). The authority is a
`git archive` of `126eae9` in the staging folder; the harness is built there (`build_harness.py` of EXP-20261030-04). No
command is executed that writes outside the process: the allowed actions were read for I/O (none writes a file), and
`%LOCALAPPDATA%\MoviePad\settings.json`'s modification time is recorded before and after (2026-10-30 21:24 at filing).

## 7. Comparison (`compare.py`, deterministic) and scoring

Per assertion (example, step, observation, value): **hold** (numbers within 0.0005, booleans equal), **fail**, or **not run**
(an earlier step pressed an unavailable button or raised). Per example: **pressed-unavailable** if a press was refused.
Each fail is placed against section 2's facts by `compare.py`'s `place` from the presses up to that step (last = the
step's own press): `undo_enabled` / `redo_enabled` — `redo_enabled` after a document edit with an Undo before it → F2, last a
`Scale` / `SetFps` → F6, last a speed or volume preset → F8, last Set In / Set Out → F9, otherwise F1 (at the start → other);
`out_*` after Undo / Redo → F6; `playhead` after Undo / Redo → F7; `unsaved` after Undo / Redo → F10; `selected_*` → F5;
`region_count` / `trim_*` / `output_length` after Undo / Redo → F3; anything else → **other**, listed one by one. The placement
is a pointer for reading, not a reading itself.

Document scoring (F1-F11, by a fresh scorer agent): the four writers' `out/` documents and `examples.json`, labelled W1-W4 by
a shuffle whose key is hashed before the scorer starts and opened after. For each writer and fact: **correct** (states the
authority's behaviour), **wrong** (states another behaviour as fact), **open** (marks it undetermined or asks it as a
question), **absent**. The scorer is given section 2's table and the writers' files only, quotes the line it relies on, and is
not told the arms. Also from the documents: the number of questions to the owner, and how many of them the given sources
already answer (scorer, with the line).

## 8. Reading (fixed now)

Per writer, never pooled; two writers per arm, so no rate is claimed.

- **R1 (examples on the authority):** the fail count and the fail share of asserted values, per writer. If both K writers are
  below both C writers on the fail share (non-overlapping) → "on this feature the kit's writers asserted less that the
  authority contradicts"; the reverse → the reverse; overlap → no claim, descriptive.
- **R2 (unfounded completion):** the number of N facts (F6-F11) scored **wrong**, per writer, read the same way.
- **R3 (what the sources say):** the number of D facts (F1-F5) scored **correct**, per writer, read the same way.
- Reported as measures (no reading): asserted values, `unresolved` uses, pressed-unavailable examples, fails by fact, questions
  and how many the sources answer, time per writer.

None of R1-R3 decides "useful" alone; what follows is the user's. Nothing is filed by the result.

## 9. Limits

- One feature, one product, four writers, one model; the facts of section 2 are my reading of the code (the harness executes
  the code, so R1 does not depend on them; R2 and R3 do).
- The machine form (section 5) is added to both arms — a departure from "the kit as it is", symmetric by construction. The
  kit's own documents are scored, not executed.
- The observation list is a CAD written for this trial; it names output size, frame rate and the unsaved status, which hints
  that they could be observed (both arms).
- The arm is visible in the documents' vocabulary; the scorer's blindness is by label only.
- Examples see the region model only through the selected region and the frame-step playhead; histories longer than a few
  steps are expensive to write, so F4 is scored from the documents only in practice.

## 10. Order (each step's output committed or hashed before the next starts)

1. Commit this file, `prepare.py`, `check_examples.py`, `compare.py` and `harness/`.
2. `prepare.py package` into the staging folder; `git archive` the authority; build the harness; `harness selftest` (the
   copied selftest) PASS.
3. `compare.py selftest`: hold / fail / not run / pressed-unavailable and the fact placement, a planted case and a silent twin
   each, on synthetic observations.
4. **One real slice:** a hand-written `examples.json` with the real vocabulary — one deliberately wrong value, one press of an
   unavailable button, one F6 case — through `check_examples.py`, the harness and `compare.py`; exactly the planted outcomes, the
   F6 fail placed at F6, and `undo_enabled` agreeing with `Avail("Undo")` on every step (the harness records both).
   `start-screen.json` is written from the same harness run.
5. Four writers together (section 4). Isolation by `../exp-20261030-04/isolation.py` over each transcript
   (`<session>/subagents/agent-*.jsonl`); each package's hashes checked after.
6. Freeze each `examples.json` and `out/` (SHA-256); observe; compare; the scorer; open the shuffle key; tally; `results.md`.

## 11. Departures

- **D1 — C1 wrote and ran code in its folder (the writer's own report).** Against "コードは書きません", C1 wrote a Python
  script at its folder's top level to generate `examples.json`, ran it once, moved it to `out/` and deleted it before
  finishing. Isolation over its transcript: 0 flags (it stayed in its folder); its frozen files are the four documents and
  `examples.json`. Kept in the run; read as a fact about the control prompt's hold on the boundary, not a reading.
- **D2 — the scorer package first carried the run's results (found before the scorer started).** `freeze.py scorer` copied
  every file under `run-<W>/`, which by then also held `runs.json`, `observed.json` and `compared.json` (all-hold results).
  The package and its key were deleted unread and rebuilt from the files listed in each `freeze.json` only (the hash checked);
  the key hashed in `scorer-key-sha256.txt` is the rebuilt one.
- **D3 — time.** Measured by the agents' run durations (`usage.duration_ms`): K1 677 s, K2 558 s, C1 526 s, C2 492 s; all
  inside the bound. C2's report said "約 30 分"; the measure is the duration, not the report.
