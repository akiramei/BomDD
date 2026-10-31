# EXP-20261031-03 — definitions (fixed before any prompt is written, any agent is started or any folder is built)

Fixed 2026-10-31. A change after this point is a departure (section 12). Each fact (a count, a requirement id, a file, a step)
is written once, in the section named for it; other sections refer to it.

## 1. The question, and where it comes from

EXP-20261031-02 (closed 2026-10-31 on the user's "A: §9 のまま") read the frame-rate row as broken at L1: its model states the
rate as one settable value (`outputFps`) and five derived attributes, and its screens and states carry only the derived ones.
A1 required the settable attribute's own id on a screen and in a state, so a design that keeps the meaning but changes the
representation broke the row. A reader's comment on its results (2026-10-31) added that A1 counts references, not whether a
wrong rule is told from a right one (its results section 6). Its results section 7 named, as one thing missing, "a row
definition fixed beforehand that follows a settable value into the derived attributes it feeds". The reader proposed a narrow
experiment; the user chose "A: 起票する" (2026-10-31) on it with three amendments, marked where they apply (sections 2 and 3).

**Given a design written in a machine-evaluable form, can a frozen checker evaluate what the design predicts the screen shows
after each operation, and so pass designs that are right in different representations and fail designs that are wrong in
meaning — over a fixed, finite range of the output frame rate, with no review?**

A measurement of a checker, not of authors. It changes no method text, template, tool or product. Nothing is written into
MoviePad or MoviePad-Remake; EXP-20261031-02's records stay as they are.

## 2. What success would say, and what it would not (amendment 3)

On success: **within the range of section 3, a design in this form is judged by the frozen checker against the authority without
review: a direct and a derived representation pass, and the named defects fail with a counterexample.** Not said: that authors
write this form; that the form covers other attributes; that defects nobody named are caught (the mutants are the operator's);
anything about EXP-20261031-02's counts.

## 3. Fixed items (proposed defaults; the user's at the start) — the one place for counts and ids

| item | proposed default | why / what it trades |
|---|---|---|
| authority | MoviePad **`126eae9`**, built from a `git archive` copy in the scratchpad (as EXP-20261031-02) | the source the S2 specimen was written from |
| range | the output frame rate only: the five presets and what they make visible (the slots below). Undo, playback, export, the `Edited` flag and rendering are out | narrow on purpose; without `Edited` the form needs no document state |
| source rates (amendment 1) | judged: **25** and **29.97** fps. Control (A3, not judged): **30** | at 30, Source and the 30 preset coincide, so "Source sets a constant 30" cannot be told apart; at 29.97 the 30 preset and Source are both selected (0.03 < 0.05) and the 0.05 margins and the two-decimal text are exercised |
| cases | per source rate **26**: the clip as opened (no press), and first press ∈ {none, 24, 30, 60, 120} × second press ∈ {Source, 24, 30, 60, 120}. A case is written (rate, first, second). **Judged: 52** (two rates); **control: 26** (rate 30); **78 in the expected table** | generated from this table, not from a specimen, so a specimen that drops an operation does not shrink the cases; "first press none" leaves the output at the source rate |
| slots | 8 per case — **V1** the export summary's frame-rate text (string); **V2–V6** the Source / 24 / 30 / 60 / 120 preset shown selected (boolean); **V7** the duplicate-frames note shown (boolean); **V8** Source's tooltip text (string). Judged values: 52 × 8 = **416**; expected table: 78 × 8 = **624** | the screen's values, not the model's; the representation inside a design is free |
| requirements for the cross-check | S1 (EXP-20261031-02, frozen) **REQ-070** (presets, selection, note, tooltip), **REQ-077** (the summary's 「{表記} fps」), **REQ-020** (the output rate on opening = the source's) | the authority is the truth; the cross-check catches a driver that misreads it |
| culture (the lesson of EXP-20261031-02) | the driver sets `CurrentUICulture` and `CurrentCulture` to `en` and writes both into its output; the run checks them before reading any value | V8 is localized (`Strings.resx` "Same as source ({0})"); the number format is invariant (`Models/TimeMath.cs:50`), but the premise is a checked condition, not prose |
| specimens (amendment 2) | **N1** direct (the operator's). **N2a**, **N2b**: EXP-20261031-02's frozen S2 model and S3 screens transcribed into the form, each by one fresh agent (section 4.3). **Mutants**: the nine meanings of section 5 on N1 (M1–M9) and on N2a (M1′–M9′) | the derived representation is the real one that broke A1, not one the checker's author imagined |
| place | this folder for the records; staging in the session scratchpad (`exp08/`), deleted on the user's word | |

## 4. The form, the verdicts, and the transcription

### 4.1 The form (structure fixed here; meaning fixed in `form.md`)

A specimen is one JSON file with four parts: `state` (variables, each with its value when a clip of source rate `src` is
opened); `buttons` (one entry per preset button `Source`, `24`, `30`, `60`, `120`, each giving the new values of variables — **a
button with no entry is "not defined"**); `derived` (named values computed from others, no cycles); `observe` (one expression
per slot). Expressions are a subset of Python expression syntax evaluated through `ast`, with no access to anything but the
specimen's own names and a fixed list of functions.

**Everything else about the meaning** — the exact syntax and functions, what each part may refer to, when a button's
expressions are evaluated, number formatting — is written in `form.md` at run step 2 and **frozen with the checker, each rule
pinned by a selftest fixture of `check.py` that fails if the rule is not as written.** `form.md` is not revised after step 2;
a rule found wanting later is a departure.

### 4.2 Verdicts (fixed now, so that a form error is never counted as a detection)

- **FAIL** — the specimen is well formed under `form.md` and on some judged case either a slot's value differs from the
  authority's (*value* counterexample) or a case presses a button the specimen leaves "not defined" (*undefined*
  counterexample). Every counterexample is listed with its case, slot, expected and predicted value.
- **UNKNOWN** — anything `form.md` makes an error: a parse error, an unresolved name, a cycle, a slot of the wrong type, an
  evaluation error. Not a detection and not a pass; it never removes a case or a specimen from a count.
- **PASS** — neither, on every judged case.

### 4.3 The transcription

**The rule** (written verbatim into the transcribers' `rule.md`): 「各スロットについて、`slots.json` がそのスロットに挙げる S3 の部品と、
その部品の `shows` が挙げる S2 の属性を使う。`派生:` の式は書かれたとおりに写す。画面に出る形(「{表記} fps」や
"Same as source ({fps} fps)" のような囲み、選択表示になる条件)を S2 の説明や S3 の部品の文が述べているときは、表示の形はその文に
従う。ボタンは S2 の `SetFps` の効果から書く。文を読んで決めた箇所は、すべて `notes` に挙げる。」

**The package — each transcriber's folder holds exactly these, and nothing else:** `prompt.md`; `form.md`; `form_check.py` (`check.py`'s
own form stage, the same code, with no case and no expected value — so a typo does not cost the transcription, and what passes
it is well formed for `check.py`); `rule.md`; `slots.json` (per slot: id, type, the S3 element of section 5, and what of the
element is observed — its text, shown selected, shown at all, or its tooltip); `s2/domain-model.json` and
`s3/screens.json` (EXP-20261031-02's frozen files, hashes recorded). Its output: `n2.json` with a `notes` field.

**Isolation:** `../exp-20261030-04/isolation.py` on both transcripts. A read outside the folder is reported per agent; a read of
the authority, the requirements, or any file of this experiment outside its folder sets that specimen aside (missing, not
replaced silently).

## 5. Slots against the authority and S3, and the mutants

| slot | authority (`126eae9`) | S3 element |
|---|---|---|
| V1 | `OutFpsText`, `StringFormat '{}{0} fps'` (`Views/ExportDialogView.axaml:113`) | `EL-EX-SUMMARY-FPS` |
| V2 | `Classes.active="{Binding FpsSourceActive}"` (`Views/InspectorView.axaml:92`) | `EL-INS-FPS-SOURCE` |
| V3–V6 | `OutFpsText` through `EqualsConverter` (ordinal) with `24` / `30` / `60` / `120` (`InspectorView.axaml:94–101`, `Converters/EqualsConverter.cs:12–17`) | `EL-INS-FPS-24`, `-30`, `-60`, `-120` |
| V7 | `IsVisible="{Binding FpsUpsampling}"` (`InspectorView.axaml:103`) | `EL-INS-FPS-NOTE` |
| V8 | `ToolTip.Tip="{Binding FpsSourceTip}"` (`InspectorView.axaml:93`) | `EL-INS-FPS-SOURCE` |

The view model (`ViewModels/MainWindowViewModel.cs`): `SetFps` 850–857; `OutFpsText`, `FpsSourceActive`, `FpsUpsampling`
459–461; `FpsText`, `FpsSourceTip` 441–443; `LoadClip` 526, which sets `OutFps = clip.Fps` (536).

**The nine meanings.** Each mutant changes one meaning of its base and names one case and slot where it must differ (checked by
hand against the rules above while filing); it is fixed in its file before the checker runs on its base.

| id | meaning | named case → slot (expected / mutant) |
|---|---|---|
| M1 | the 60 button keeps the previous value | (25, none, 60) → V1 ("60 fps" / "25 fps") |
| M2 | Source keeps the previous value | (25, 60, Source) → V1 ("25 fps" / "60 fps") |
| M3 | the summary text shows the value before the last press | (25, 24, 60) → V1 ("60 fps" / "24 fps") |
| M4 | the summary text shows the source rate | (25, none, 24) → V1 ("24 fps" / "25 fps") |
| M5 | the 120 button is not defined | (25, none, 120) → undefined |
| M6 | Source sets a constant 30 | (25, 60, Source) → V1 ("25 fps" / "30 fps") |
| M7 | Source shown selected only on exact equality | (29.97, none, 30) → V2 (true / false) |
| M8 | the note shown when the output exceeds the source, no margin | (29.97, none, 30) → V7 (false / true) |
| M9 | the text rounded to whole numbers | (29.97, opened) → V1 ("29.97 fps" / "30 fps") |

On N2a each meaning is written in N2a's own representation; one with no counterpart there is recorded NA with the reason. If
N2a is missing (section 4.3), M1′–M9′ are written on N2b; if both are missing, there are no M′.

## 6. The driver and the cross-check

A C# console driver (`driver/`), built against the authority archive, sets the cultures of section 3, and for each case of the
expected table: `new MainWindowViewModel()`; `LoadClip(Sample.Clip with { Fps = rate }, Sample.Doc)`; the presses through
`SetFpsCommand.Execute`; then reads the view model values of section 5 and applies the slot bindings written there (string
format, ordinal comparison). The views are not run. Output: `expected.json` (the expected table of section 3) with the cultures,
the commit and the build hash. Before it runs, its I/O is read (what the constructor and `LoadClip` touch), and MoviePad's
`settings.json` mtime is recorded before and after.

Cross-check: `req070.py` (the operator's) computes the expected table from the requirements of section 3 as written, without the
authority; it must equal `expected.json` on every value.

## 7. Measures

- **A1 — verdicts.** For N1, N2a, N2b and every mutant on the judged cases: the verdict, every counterexample, and for each
  mutant whether its named case and slot are among them.
- **A2 — the transcriptions.** N2a against N2b, part by part: where they differ, whether their verdicts differ, and each one's
  `notes`.
- **A3 — the source-rate control (descriptive, not judged).** N1, M6 and M6′ on the control cases; expected: all three pass
  there, which is amendment 1's reason.
- **A4 — cost.** Agents, tool uses, wall time; the operator's build and writing time.

## 8. Order of the run (each step before the next)

1. Archive the authority; build the driver; read its I/O; run it (mtime before / after); run `req070.py`. Commit `driver/`,
   `expected.json`, `req070.py` and its output.
2. Write `form.md`, `form_check.py`, `check.py` with its selftest (fixtures for `form.md`'s rules, not the mutants), N1 and
   M1–M9. Commit — frozen.
3. Build the two packages of section 4.3 and write `prompt.md`; commit; start both transcribers; isolation check; commit N2a
   and N2b — frozen.
4. Write M1′–M9′ on N2a. Commit — frozen.
5. Run `check.py` for A1 and A3. Commit the outputs.
6. Write `results.md`, read by section 9.

## 9. Reading (fixed now)

- **The checker judges designs in this form on this range** — when all of: N1 PASS; N2a and N2b PASS; every mutant that is not
  NA FAILs with its named case and slot among its counterexamples; no UNKNOWN in A1. Reported as section 2's sentence and no
  more.
- A mutant whose base already fails at the mutant's named case and slot is **not informative** (its FAIL may be the base's),
  reported as such.
- **Representation not shown** — N1 and its mutants hold, but N2a or N2b does not PASS or is missing (a missing specimen is
  reported as missing, with no reading of its own). Each counterexample is read by hand
  against S2 / S3's text: where the text says what the specimen predicted, **a defect of S2 / S3 found by the checker**; where the
  transcription departs from the text, **the transcription's**. No claim of representation tolerance either way.
- **Detection not shown** — a mutant PASSes, or FAILs without its named case and slot: that meaning is reported as not caught,
  with the slots that did differ.
- **No claim** — N1 does not PASS, or any UNKNOWN in A1: the checker or the form is the failure; nothing is said about designs.
- k of n mutants is descriptive; there is no baseline.

## 10. Stops

- The driver does not build, writes MoviePad's `settings.json`, or the cross-check differs on any value → stop, return to the
  user.
- A transcriber silent 30 minutes or running past 60 → stop it; its specimen is missing, not replaced silently.
- Budget: one day from step 1. Running past it returns to the user.

## 11. Limits (declared now)

- **The operator knows the answer.** It wrote this file after reading the authority's frame-rate code and S2 / S3's frame-rate
  entries, to check that the cases can be made and the specimens transcribed. It knows that S2's `fpsSourceTip` is
  `派生: Clip.fpsText` while S3's element text gives "Same as source ({fps} fps)"; the rule "the displayed form follows the text"
  was fixed knowing this.
- The form, `form.md`, the checkers, the driver, the cross-check, N1 and all mutants are the operator's. The mutants are named
  defects; detection of unnamed ones is not measured.
- The views are not run; their bindings are transcribed by hand from the lines of section 5.
- N2a and N2b are transcriptions of S2 / S3, not S2 / S3 themselves; two transcribers, no rate.
- One attribute family of one product; the clip is a `ClipInfo` object, not decoded media.
- The harness gives every agent this repository's `CLAUDE.md` and the user's memory index (as EXP-20261031-02).

## 12. Departures

None yet.

## 13. Convergence receipt (filing)

- **Verdict: not converged; filed on the user's "A: 打ち切って起票" (2026-10-31).** Started by the operator itself (`/converge`).
- First loop: new findings per round 5 → 2 → 1 (limit 3); extended on the user's "B: 延長する": 7 → 3. Grouped by cause — facts
  written in several places, the transcribers' package spread over sections, the form's meaning fixed in prose — and removed on
  the user's "C: 原因を除いて再開" (each fact in one place; the package as one file list; the meaning moved to `form.md` pinned by
  selftest fixtures). Second loop: 2 → 0 → 1 (limit 3); cut off.
- Claims checked against the authority while filing: the lines of section 5; `Models/Sample.cs` (`Clip` at 30 fps, `Doc`);
  `ClipInfo` a positional record (`Models/ClipInfo.cs:14`); `TimeMath.FormatSpeed` invariant `"0.##"`; `30 − 29.97 < 0.05` and
  `30 > 29.97 + 0.05` false; S1's REQ-070, REQ-077, REQ-020; S2's six frame-rate attributes and `SetFps`; S3's nine elements.
- Unaudited: the last round's change (a missing transcription, section 5 and section 9).
