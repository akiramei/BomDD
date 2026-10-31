# EXP-20261031-03 — run log

Started 2026-10-31 on the user's "A: 既定で始める": the defaults of definitions section 3 accepted as proposed. Staging root
`<scratchpad>/exp08/`; disk free before the run 174 GB.

## Step 1 — the expected table (definitions sections 6 and 8)

- The driver's I/O read before it ran (`126eae9`): the constructor (`ViewModels/MainWindowViewModel.cs:55–64`) sets fields from
  `Models/Sample.cs`; `LoadClip` (526–545) sets state in memory, stops playback (597–603) and cancels jobs; `SetFps` (850–857)
  sets `OutFps` and `Edited`; `Localizer.SetCulture` (`Services/Localizer.cs`) sets the culture only. The one write of
  `settings.json` in the view model is `SwitchLanguage` (931–939), which the driver does not call.
- `run_driver.py`: `git archive` of `126eae9` (tar `a63a1d25…`) into `exp08/authority`, `driver/` built next to it
  (`Driver.dll` `9bcd9415…`, 0 warnings, 0 errors), run once: 78 cases, cultures `en` / `en` / `en` (current, UI, the
  Localizer's). `settings.json` mtime 1793363047314949700 ns before and after (unchanged). Output `expected.json`
  (`cfdce7ae…` on disk) and `driver-run.json`.
- By hand, before the cross-check, against section 5's named cases: (25, opened) "25 fps", Source selected, tooltip "Same as
  source (25 fps)"; (29.97, none, 30) "30 fps" with **Source and 30 both selected** and no note; (25, none, 120) "120 fps", the
  note shown; (25, 60, Source) "25 fps".
- **Cross-check** (`req070.py`, from S1's REQ-020 / 070 / 077 as written): **624 values compared, 0 differences**; cultures
  checked `en` ×3 (`req070-check.json`). Step 1 passes; the stop of section 10 does not apply.
