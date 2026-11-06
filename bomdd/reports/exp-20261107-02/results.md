# EXP-20261107-02 — results

Run 2026-11-07 on the user's "A: 素の対照を足す", by `definitions.md` as filed in `f40c4c8` (departure D1 in its section 8).
Nothing was written into MoviePad, MoviePad-Remake or BehaviorForge.

## 1. The run, in the order of section 5

1. Filed `f40c4c8`.
2. Packaged into EXP-20261107-01's staging folder (`package-sha256-02.txt`); `verify` OK before and after the writers. D1 found
   after packaging, before the writers started.
3. Slice: the bare checker accepts C2's examples with their `unresolved` entries removed and rejects them with the entries
   (OK 12 / 3 errors on the first steps; done at filing).
4. Writers B1 and B2 started together at 02:31:52; run durations (first to last transcript entry) B1 511 s, B2 408 s.
   Isolation 0 flags for both.
5. Frozen (`run-B*/freeze.json`); observed on the authority with EXP-20261107-01's harness build; compared. A fresh scorer,
   labels W1 / W2 by a seeded shuffle, the key hashed `9a78f906…` before it started and matched when opened (W1 = B2,
   W2 = B1); the scorer's isolation 0 flags. `%LOCALAPPDATA%\MoviePad\settings.json` unchanged (2026-10-30 21:24:07).

## 2. Verdict by the fixed reading (section 4)

| writer | examples | asserted | fail on the authority | R2′: N facts wrong | D facts correct | questions (answered by the sources) |
|---|---|---|---|---|---|---|
| B1 | 15 | 210 | **0** | **0** | 4 | 9 (1) |
| B2 | 15 | 246 | **0** | **0** | 4 | 9 (2) |
| *C1 (EXP-20261107-01)* | 13 | 280 | 0 | 0 | 4 | 11 (1) |
| *C2 (EXP-20261107-01)* | 12 | 243 | 0 | 0 | 4 | 9 (1) |

No example pressed an unavailable button or raised. Of the 456 values, 17 are at the start (k = 0); 439 follow a press and
254 follow a press of Undo or Redo directly (B1 102, B2 152).

- **R1′: both 0 → "the field did not carry it here; explanation (b) or the remaining scaffolding".**
- **R2′: both 0 → the same reading.**

**Removing the `unresolved` field and its sentence did not make the writers assert what the authority contradicts, nor state
an open fact wrongly.** On this feature the field is not what kept the control careful. What remains is the model itself or
the scaffolding that stayed (sources only, the observed start screen, the observation list); this run does not separate those.

Per-fact verdicts (scorer, `scoring/scores.json`):

| | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | correct | correct | correct | correct | open | open | correct | open | open | open | open |
| B2 | correct | correct | correct | correct | open | open | open | open | absent | open | open |

## 3. Read after the verdict (descriptive, not readings)

- **Without the field the writers stayed silent where the others had written `unresolved`.** The four writers of
  EXP-20261107-01 put 27-64 `unresolved` entries in their examples; B1 and B2 could not. They asserted fewer values per step
  (B1 4.2, B2 3.8 against C1 5.1, C2 5.9; K1 3.6, K2 4.9) and **no selection value after a Split** (B 0 and 0 against K1 8,
  K2 2, C1 2, C2 13 — all of those held). The place where the sources conflict (F5) was left out of the machine form rather
  than marked. Section 6's limit applies as written: what was removed is the invitation, not the possibility of omission.
- **Both documents describe the selection as kept by region id** (B2 commits, B1 "と読める"), the mechanism K2 and C1 stated
  in EXP-20261107-01. Neither states a result that differs from the authority, and both put the split case to the owner (B2's
  Q-05, B1's Q-01), so the scorer marked F5 `open` for both. **The two scorers drew this line differently**: EXP-20261107-01's
  marked K2 and C1 `wrong` for the same kind of statement. F5's verdicts are therefore not comparable across the two runs.
  F5 is a D fact, so R2′ (N facts) is unaffected; under the stricter line B1 and B2 would both be F5 `wrong`, D correct 4
  either way.
- **Questions: 9 and 9**, close to the control's 11 and 9 (the kit's writers asked 4 and 5). One and two answered by the
  sources by the scorer's rule (the selection after a split from REQ-003; B2's Q-09 from REQ-012).
- **The feature still had no trap the writers fell into.** As in EXP-20261107-01, the facts the authority implements beyond the
  sources were treated as open or, for F7 in B1, stated as the authority does it.

## 4. Limits (in addition to `definitions.md` section 6)

- A ceiling again: 0 fails in both writers, as in all four before.
- One variable removed; the observed start screen and the observation list stay, so "the model alone" is not shown.
- Two writers, one feature, one model; the comparison is against a run made the same night by a different scorer.

## 5. Files

`definitions.md`, `prepare.py`, `check_examples.py`, `freeze.py`, `tally.py`, `prompts/common-bare.md`,
`package-sha256-02.txt`, `run-B1/`, `run-B2/` (frozen documents and `examples.json`, `freeze.json`, `runs.json`,
`observed.json`, `compared.json`), `scoring/` (`scores.json`, `scorer-key.json`), `scorer-key-sha256.txt`, `tally.json`.
The staging folder (EXP-20261107-01's, about 1.5 GB) is outside every repository and deleted on the user's word.
