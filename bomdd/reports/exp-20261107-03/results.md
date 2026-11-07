# EXP-20261107-03 — results

Run 2026-11-07 on the user's "A: 始める", by `definitions.md` as filed in `44d51de` (departures D1-D5 in its section 11 and
below). Nothing was written into MoviePad or BehaviorForge.

## 1. The run, in the order of section 10

1. Filed `44d51de` (self-conformance PASS, CI success).
2. `check_examples.py` accepted a hand-made good file and rejected a bad one with all six planted errors (`slice/`). Packaged:
   139 files of the original (313 BomDD management files left out), 18 of the kit; 600 hashed files
   (`writer-package-sha256.txt`); `verify` OK before and after the writers.
3. Four writers started together at 10:13:49; durations (first to last transcript entry) K1 523 s, K2 765 s, C1 641 s,
   C2 548 s — all well inside the 75-minute bound. Isolation: no writer read or wrote outside its folder; the tool's flags were
   relative paths inside the folder (K1, K2), K1's empty folder created and removed at once (D2), and C2 reading the harness's
   saved copy of its own command output. Two writers ran inline Python inside their folders (D4).
   `%LOCALAPPDATA%\MoviePad\settings.json` unchanged (2026-10-30 21:24:07).
4. Frozen (`run-<W>/freeze.json`; no writer left other files). A fresh scorer, labels shuffled (seed 20261107), key hashed
   `f20b3303…` before it started and matched when opened (W1 = C1, W2 = K1, W3 = K2, W4 = C2).

## 2. Verdict by the fixed reading (section 7)

| writer | correct (of 16) | wrong | open | absent | correct by class a / b / c | questions (answered by the original) | examples / steps / values |
|---|---|---|---|---|---|---|---|
| K1 | **16** | **0** | 0 | 0 | 1 / 7 / 8 | 1 (0) | 14 / 34 / 77 |
| K2 | **15** | **0** | 0 | 1 (T02) | 1 / 7 / 7 | 3 (0) | 11 / 34 / 66 |
| C1 | **16** | **0** | 0 | 0 | 1 / 7 / 8 | 11 (1) | 12 / 29 / 105 |
| C2 | **15** | **0** | 0 | 1 (T16) | 1 / 6 / 8 | 16 (0) | 12 / 25 / 73 |

- **R1: no claim** — K 16 and 15, C 16 and 15 overlap.
- **R2: no claim** — no writer stated a result that differs from the original.

**On this feature, from the original alone, every writer with or without the kit extracted 15 or 16 of the 16 behaviours
and stated none wrongly.** The kit's effect is not visible. As fixed in section 7, this is a valid result and no second topic is
searched for.

## 3. Read after the verdict (descriptive, not readings)

- **The skeleton was not lost on the correct path here.** Every writer found the behaviours that are in the code only (class c,
  7 or 8 of 8) and on screen only (6 or 7 of 7), not only the one in the quick start (class a). EXP-20261030-05's loss of the
  frame-rate step happened on a state list without a frame-rate state; reading the original, no writer lost it. This run
  names the feature in the task (section 9), so it says nothing about a whole-app skeleton.
- **Questions: the kit's writers asked far fewer** (1 and 3 against 11 and 16), as in EXP-20261107-01 (4, 5 against 11, 9).
  The scorer counted one question in all four as answered by the original (C1's, on the clip information panel). The kit's
  writers stated the original's behaviour and asked only about intent; most of the control's questions were also about intent
  or keep-or-change. Not a reading; two writers per arm.
- **Writers found two things the sealed list did not hold.** (1) All four noticed that the clip information panel showing the
  source rate is visible only when no region is selected, which in practice does not happen after a clip is opened — recorded
  as D3, a gap in my list, not in the writers. (2) K1 and C2 found an inconsistency inside the original: on a 29.97 fps source,
  pressing "30" sets the output to 30, yet the 0.05 tolerance treats it as unchanged — K1: a copy export keeps 29.97 and a
  re-encode gives 30 (`run-K1/out/04-review-and-questions.md` Q-01); C2: the copy check sees no change while the nominal rate
  is built from 30/1 (`run-C2/out/04-owner-questions.md` Q8); both put it to the owner. K2 copies the tolerance as a design
  choice and C1 mentions 29.97 without stating the inconsistency. Neither was scored (not on the list).
- **The kit's writers marked their checks `NOT_RUN`** in their documents (K1 3 files, K2 6); no control document uses the mark.
  No writer claimed an execution (none was permitted).
- **The kit's example: K1 says it did not read it** (`run-K1/out/01-input-index.md` 15: the example is fictional and was
  neither read nor used); K2's documents do not mention it.

## 4. Departures found during the run (added to `definitions.md` section 11)

- D1 the scorer was given the product tree for the question count; D2 K1's empty folder outside; D3 T08 has no visibility
  condition; D4 inline Python in K2's and C2's folders.
- **D5 — the scorer wrote four reading dumps outside its folder** (`w2.txt`, `w3.txt`, `w4.txt` in the session's scratchpad
  and `ex234.txt` next to the scorer folder) and read W3's and W4's `examples.json` (K2's and C2's) only through a dump it
  calls garbled. Its item verdicts rest mainly on the documents; a wrong value that only an example of K2 or C2 states could have
  been missed. The dumps were deleted after the scores were copied.

## 5. Limits (in addition to `definitions.md` section 9)

- A ceiling again: 15-16 of 16 in every writer leaves R1 and R2 no room.
- One scorer; its own hesitations are listed in its report (T01 for K2 could be `absent`; T16 for K1 given by resource key
  only; a looser rule for "answered by the original" would give about 4 each to C1 and C2 and 0 to K1 and K2).
- The execution pass (section 8) has not been run; no example value has been checked on the authority.
- Two writers per arm, one feature, one model; no rate.

## 6. Files

`definitions.md`, `targets.md`, `prepare.py`, `check_examples.py`, `freeze.py`, `tally.py`, `prompts/` (`head-k.md`,
`head-c.md`, `common.md`, `scorer.md`), `slice/` (the checker's good and bad files), `writer-package-sha256.txt`,
`run-K1/` … `run-C2/` (frozen documents, `examples.json`, `freeze.json`), `scoring/` (`scores.json`, `scorer-key.json`),
`scorer-key-sha256.txt`, `tally.json`. The staging folder (about 22 MB, outside every repository) is deleted on the user's word.
