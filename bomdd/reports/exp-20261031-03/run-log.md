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
- Committed `1411500`. `expected.json` is CRLF on disk (`cfdce7ae…`, the hash in `driver-run.json`); its LF blob is
  `e3fd04aa…`.

## Step 2 — the form, the checkers, N1 and M1–M9 (frozen before the checker runs on any specimen)

- `form.md` (`96b22ac0…`): the parts, the expressions, the slots and the type probe; each rule names the fixture that pins it.
- `form_check.py` (`768d3b58…`): the form's parser and evaluator, no case and no expected value; `check.py` (`eb05a7a2…`)
  imports it and adds the judging and the selftest. **Selftest 29 of 29** (F1–F24, F11 in six parts).
- Whether the fixtures can go red (`mutate_checker.py`, `b739415d…`): the checker broken four ways in memory, each time the
  selftest exits 1 with the fixture of that rule red — `num` rounding half to even (F2), buttons assigned one by one (F12),
  no slot type check (F8), an undefined button made an error (F3).
- `make_specimens.py` (`12a41467…`) writes `specimens/`: N1 (`17012ca7…`) and M1–M9 (each with its meaning, named case, slot,
  expected and mutant value in `meta`; `M1` `4279c795…`, `M2` `03e5965a…`, `M3` `8875e3fa…`, `M4` `963d18db…`, `M5`
  `e8c9fd75…`, `M6` `56d0655c…`, `M7` `931c25bb…`, `M8` `de276090…`, `M9` `44493d63…`, all LF). `form_check.py` on each: OK
  (M5: the 120 button not defined). **No specimen has been run by `check.py`.**
- Step 3's package files written now and committed with this step, before any transcriber starts: `transcriber/prompt.md`
  (`a7cede9d…`, Japanese), `rule.md` (`ad6c8250…`, definitions section 4.3's rule verbatim), `slots.json` (`54d50990…`).
  `form.md` and `rule.md` name no experiment id and no definitions section.
