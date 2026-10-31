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
- Committed `39e0974` (self-conformance restarted once: the operator wrote `build_packages.py` into this folder while it ran,
  moved it out, and ran the check again on the tree that was committed).

## Step 3 — the transcriptions (definitions section 4.3)

- `build_packages.py` built `exp08/t1` and `exp08/t2`, 7 files each, identical: `prompt.md` `a7cede9d…`, `form.md`
  `96b22ac0…`, `form_check.py` `768d3b58…`, `rule.md` `ad6c8250…`, `slots.json` `54d50990…`, `s2/domain-model.json`
  `b758d626…`, `s3/screens.json` `f46ef7cb…` (the frozen S2 and S3 of EXP-20261031-02).
- Both started 2026-10-31T23:26:30+09:00 (fresh Claude agents, general-purpose; prompt: read the folder's `prompt.md` and work
  only in the folder). t2 finished about 23:29 (16 tool uses by its transcript, 144 s); t1 about 23:29 (14 by its transcript,
  13 by its own count, 182 s). Neither near section 10's limits.
- **Isolation** (`../exp-20261030-04/isolation.py` on each agent's transcript under the session's `subagents/`): t1 Bash 10,
  Write 4, **0 flags**; t2 Bash 10, Read 4, Write 2, **0 flags**. The first run of the tool was given the agent's task output
  file instead of its transcript and counted 0 tool calls; that run is not used (a measure that reads nothing passes).
- **Departure 1** (definitions section 12): counting the measured side's words in the transcripts found them only in the
  harness's context lines (the working directory, the status and the recent commit subjects naming the cases count, the
  requirement ids and "the nine mutants"), none in a tool call. Both specimens kept.
- Frozen: **N2a** = t1's `n2.json` (`86e031f4…`, 8 notes), **N2b** = t2's (`7e56e0b1…`, 10 notes); `form_check.py` OK on both,
  all five buttons defined. t1 left `work/` (`gather.py` `f42820d9…`, `q.txt` `770144c5…`, `s2_dump.txt` = a copy of the S2
  file) in its folder; not used.
- The two representations differ before any check (A2 reads them in full): N2a compares the output text with each preset
  directly and wraps the tooltip in a derived value; N2b goes through `activeFpsPreset` (one value, `'none'` when no digit
  matches) and wraps the tooltip in the slot. Both write the rounding of 「小数 2 桁まで」 as `num(x, 2)` and note that S2 states
  no rounding for it.
