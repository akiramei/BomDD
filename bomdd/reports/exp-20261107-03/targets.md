# EXP-20261107-03 — the sealed list: MoviePad's frame-rate behaviour (evaluator side, never given to a writer)

Fixed 2026-11-07 before any writer starts, read from MoviePad `126eae9` by `git show`. Paths are in that commit. "Source" is
the opened clip's frame rate, "output" the output frame rate. Class: **a** = in the user docs (`docs/QUICKSTART.md` /
`.ja.md` §4.6), **b** = on screen but not in the docs, **c** = in the code only. **Run** = executable on the harness's sample
(a 30 fps constant-rate clip with no file path); the others are scored from documents only.

| id | the authority's behaviour | class | run | evidence |
|---|---|---|---|---|
| T01 | The source rate is read when a clip is opened: `avg_frame_rate`, else `r_frame_rate`, else 30 | c | no | `Services/MediaProbe.cs` 92-98 |
| T02 | The source is variable-rate (VFR) when both rates are valid and differ by more than max(0.1, 0.5 % of the larger) | c | no | `Services/MediaProbe.cs` 97 |
| T03 | The output rate starts at the source rate (on opening a clip, and with the sample at start) | c | yes | `ViewModels/MainWindowViewModel.cs` 63, 536 |
| T04 | Output frame rate presets Source / 24 / 30 / 60 / 120; Source sets the output to the source rate, a number to that number | a | yes | QUICKSTART §4.6; `Views/InspectorView.axaml` 88-101; `MainWindowViewModel.cs` 850-857 |
| T05 | A preset is shown active: Source when \|output − source\| < 0.05; a number when the output's text (`0.##`) equals its label — so on a 30 fps source Source and 30 are active together; on 29.97 only Source | b | yes | `InspectorView.axaml` 92-101; `MainWindowViewModel.cs` 459-460; `Models/TimeMath.cs` 47-52 |
| T06 | The Source preset's tooltip reads "Same as source (30 fps)" (the source rate, `0.##`) | b | yes | `Resources/Strings.resx` `Inspector_FpsSourceTip`; `MainWindowViewModel.cs` 441-443 |
| T07 | A hint is shown when output > source + 0.05: a rate above the source duplicates frames and does not improve quality | b | yes | `InspectorView.axaml` 103-104; `MainWindowViewModel.cs` 461; `Strings.resx` `Inspector_FpsUpsampleHint` |
| T08 | The clip information shows the source rate as "30 fps" (label "Frame rate") | b | yes | `InspectorView.axaml` 259-260; `MainWindowViewModel.cs` 441 |
| T09 | The export dialog shows the output rate as "<output> fps" | b | yes | `Views/ExportDialogView.axaml` 112-113 |
| T10 | Setting the output rate marks the document unsaved and records no undo step | c | yes | `MainWindowViewModel.cs` 850-857 |
| T11 | Split, boundary moves and trim moves snap to the source frame grid, round(t × source) / source (30 when the rate is not positive) | c | yes | `Models/DocumentState.cs` 119-164; `TimeMath.cs` 20-24 |
| T12 | A frame step moves by one source frame, (round(playhead × source) ± 1) / source, kept inside the trim | c | yes | `MainWindowViewModel.cs` 640-644 |
| T13 | Timecodes (M:SS:FF) take the frame field from the source rate | c | yes | `TimeMath.cs` 36-44; `MainWindowViewModel.cs` 335-352 |
| T14 | Export resamples to a constant rate at the output rate when any region's speed is changed, the output differs from the source by more than 0.05, or the source is VFR | c | no | `Services/FfmpegExporter.cs` 261-264, 472-474 |
| T15 | Fast lossless copy is offered only when, among other conditions, the output rate equals the source (within 0.05); changing the output rate therefore hides the fast-copy option in the export dialog; a VFR source alone does not disqualify it | b | no | `FfmpegExporter.cs` 473-482; `MainWindowViewModel.cs` 214-224; `ExportDialogView.axaml` 83 |
| T16 | With a VFR source and fast copy on, a note says the timestamps are kept and VFR is not converted to a constant rate | b | no | `MainWindowViewModel.cs` 231-234; `ExportDialogView.axaml` 90; `Strings.resx` `Export_CopyVfrNote` |

Counts: class a 1, b 7, c 8; run 11 (T03-T13), not run 5. T15 is not run because the sample has no file path, which makes fast
copy ineligible regardless of the rate.
