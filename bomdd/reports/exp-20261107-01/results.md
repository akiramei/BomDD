# EXP-20261107-01 — results

Run 2026-11-07 on the user's "A: 実機能で試す", by `definitions.md` as filed in `f9b34f8` (departures D1-D3 in its section 11).
Nothing was written into MoviePad, MoviePad-Remake or BehaviorForge.

## 1. The run, in the order of section 10

1. Filed `f9b34f8` (self-conformance PASS before it).
2. Authority `126eae9` archived; the observing harness built (0 warnings); the copied `harness selftest` PASS.
3. `compare.py selftest` PASS (17 cases).
4. Real slice (`slice/`): 31 asserted, exactly the three planted outcomes (a wrong value placed F3, a press of an unavailable
   Redo, the output frame rate expected undone placed F6); `CanUndo` / `CanRedo` agreed with the bindings' availability on
   every step. The slice also confirmed F7, F8 and F10 by execution. `start-screen.json` came from the same harness.
5. Four writers started together at 01:11:26; run durations K1 677 s, K2 558 s, C1 526 s, C2 492 s (D3). Isolation 0 flags for
   all four; all 68 packaged files unchanged after. C1 wrote and ran a script in its folder against the prompt (D1).
6. Frozen (`run-<W>/freeze.json`); observed on the authority; compared; the scorer package rebuilt once before the scorer
   started (D2); a fresh scorer, labels shuffled, key hashed `184a7479…` before it started and matched when opened.
   `%LOCALAPPDATA%\MoviePad\settings.json` unchanged (2026-10-30 21:24:07) before and after every harness run.

## 2. Verdict by the fixed reading (section 8)

| writer | examples | asserted | fail on the authority | `unresolved` | R2: N facts wrong | R3: D facts correct | questions (answered by the sources) |
|---|---|---|---|---|---|---|---|
| K1 | 15 | 245 | **0** | 27 | **0** | 5 | 4 (1) |
| K2 | 14 | 220 | **0** | 39 | **0** | 4 | 5 (1) |
| C1 | 13 | 280 | **0** | 64 | **0** | 4 | 11 (1) |
| C2 | 12 | 243 | **0** | 38 | **0** | 4 | 9 (1) |

No example pressed an unavailable button or raised. The 0 is not made of copies of the start screen: of the 988, 120 are at
the start (k = 0); 868 follow a press, and 483 follow a press of Undo or Redo directly (K1 123, K2 109, C1 124, C2 127).

- **R1: no claim** — every writer's fail share is 0 (988 asserted values, 0 contradicted by the authority).
- **R2: no claim** — no writer stated an open fact (F6-F11) wrongly.
- **R3: no claim** — K 5 and 4, C 4 and 4 overlap.

**On this feature, under this setup, the kit's effect is not visible in any of the three readings.** All four writers, with or
without the kit, asserted only what held and left open what the sources leave open.

Per-fact verdicts (scorer, `scoring/scores.json`):

| | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K1 | correct | correct | correct | correct | correct | open | open | open | open | open | absent |
| K2 | correct | correct | correct | correct | wrong | open | open | open | absent | open | absent |
| C1 | correct | correct | correct | correct | wrong | open | correct | open | open | open | open |
| C2 | correct | correct | correct | correct | open | open | correct | open | open | open | open |

## 3. Read after the verdict (descriptive, not readings)

- **Why the control held is not measured; two explanations fit.** (a) The common section did it: both arms read only the
  sources, had an observed start screen and an observation list (a CAD), and a machine form with `unresolved` as a field —
  which carries the kit's central idea (say what you do not know) into the control by construction (section 9). (b) This
  model writes this way regardless of scaffolding. The trial separates neither; a control without the `unresolved` field
  and the observed start screen would.
  The writers' `unresolved` entries fall mostly on the facts the code turns on (the selection after a split, `unsaved`, the
  output settings after Undo — most frequent names: K1 `selected_start`/`selected_end` 8 each, K2 `unsaved` 11, C1 `unsaved`
  42, C2 `output_length` 13), and where they did not mark a value they left it unasserted. Whether the control would still hold without that field is not measured here.
- **The documents committed where the examples hedged — prose against machine form.** K2 and C1 (one per arm) state as
  their design that the selection is kept by region id; the authority resolves it to the region under the playhead. Their
  examples left the selection after a split `unresolved`, so the authority could not contradict them there. The one place
  the "say what you do not know" idea had a machine form (`unresolved`, executed) is where all four complied; in the prose,
  where it was only a rule, two of four committed wrongly — the user's standing principle that rules need a stop or a
  measure, observed in the data. Both took the rule from MoviePad-Remake's REQ-004 counterexample 3 ("undo resolves the
  selection to the wrong region"), and K1 named it a conflict with REQ-003's rationale (CF-01): **the conflict is in the
  remake's own requirements**, not in the authority's manual.
  **My class D for F5 (fixed before the run) is contestable**: the sources say "the region under the playhead" in two places
  and imply "by id" in one. The class is kept as filed; R3 would not change direction either way (K1 is the only `correct`).
- **Questions: the kit's writers asked fewer** (4 and 5 against 11 and 9), each arm with one question the sources answer (the
  selection one, by the scorer's reading of REQ-003 and README line 18). Not a reading; two writers per arm.
- **The kit's writers recorded their own verification as NOT_RUN** (K1, K2 reports and documents), as the kit asks; the
  control's reports said the form check passed and the values were not checked. Both are true; neither wrote a false claim
  of execution.
- **The feature had no trap the writers fell into.** Every fact the authority implements beyond the sources (F6-F11) was
  either treated as open or, for F7 in C1 and C2, stated as the authority does it; none was stated otherwise. The trial therefore could not show a difference in unfounded
  completion: there was none to prevent.

## 4. Limits (in addition to `definitions.md` section 9)

- A ceiling: 0 fails in all four writers leaves R1 with no room.
- The control is not "no discipline": the common section is itself scaffolding.
- One feature, one model, two writers per arm; no rate.
- Self-reported times are unreliable (C2 "約 30 分" against 492 s measured).
- Aside (not this experiment): self-conformance's C11 took 1205 s at the filing, against about 330 s measured on 2026-10-12.

## 5. Files

`definitions.md`, `prepare.py`, `check_examples.py`, `compare.py`, `freeze.py`, `tally.py`, `harness/`, `prompts/`
(`head-k.md`, `head-c.md`, `common.md`, `scorer.md`), `slice/`, `writer/package-sha256.txt`, `run-K1/` … `run-C2/` (frozen
documents and `examples.json`, `freeze.json`, `runs.json`, `observed.json`, `compared.json`), `scoring/` (`scores.json`,
`scorer-key.json`), `scorer-key-sha256.txt`, `tally.json`. The `freeze.json` hashes are of the bytes as the writers left
them; C1's `examples.json` was written with CRLF and git stores it with LF, so its committed blob differs from its frozen
hash by line endings only (the harness read the CRLF file; JSON parsing is unaffected). The staging folder (about 1.5 GB, mostly the authority archive and
the harness build) is outside every repository and deleted on the user's word.
