# EXP-20261031-03 — results

Written 2026-10-31 after every measure ran. Read by `definitions.md` section 9. Every number below is in `run-log.md` and in
`outputs/` (`run_all.py`).

## 1. The reading

**Within the range of section 3, a design in this form is judged by the frozen checker against the authority without review:
a direct and a derived representation pass, and the named defects fail with a counterexample.** By section 9: N1, N2a and N2b
PASS; all 18 mutants (M1–M9 on N1, M1′–M9′ on N2a, none NA) FAIL with their named case and slot among their counterexamples;
no mutant's base fails at its named case and slot (all informative); no UNKNOWN in A1. Nothing more is claimed (section 2):
not that authors write this form, not that the form covers other attributes, not that unnamed defects are caught, nothing
about EXP-20261031-02's counts.

## 2. What ran

| step | what | outcome |
|---|---|---|
| 1 | driver against MoviePad `126eae9` (`LoadClip`, `SetFpsCommand`, cultures `en` ×3); cross-check from S1's REQ-020 / 070 / 077 | 78 cases; **624 values, 0 differences**; `settings.json` unchanged |
| 2 | `form.md`, `form_check.py`, `check.py` (selftest 29 of 29; four deliberate breaks each turn their fixture red), N1, M1–M9 | frozen `39e0974` |
| 3 | two fresh transcribers on EXP-20261031-02's frozen S2 / S3 | N2a (8 notes), N2b (10 notes), isolation 0 flags each; departure 1 |
| 4 | M1′–M9′ on N2a | frozen `cb1b28d` |
| 5 | `run_all.py` | below |

## 3. A1 — verdicts (52 judged cases × 8 slots)

| specimen | verdict | counterexamples | cases failing | slots differing | named case → slot hit |
|---|---|---|---|---|---|
| N1 | PASS | 0 | | | |
| N2a | PASS | 0 | | | |
| N2b | PASS | 0 | | | |
| M1 / M1′ 60 keeps the value | FAIL / FAIL | 38 / 38 | 10 / 10 | V1–V7 | (25, none, 60) V1 ✓ / ✓ |
| M2 / M2′ Source keeps the value | FAIL / FAIL | 28 / 28 | 8 / 8 | V1–V7 | (25, 60, Source) V1 ✓ / ✓ |
| M3 / M3′ text one press late | FAIL / FAIL | 40 / 40 | 40 / 40 | V1 | (25, 24, 60) V1 ✓ / ✓ |
| M4 / M4′ text shows the source rate | FAIL / FAIL | 40 / 40 | 40 / 40 | V1 | (25, none, 24) V1 ✓ / ✓ |
| M5 / M5′ 120 not defined | FAIL / FAIL | 18 / 18 undefined | 18 / 18 | — | (25, none, 120) ✓ / ✓ |
| M6 / M6′ Source = 30 | FAIL / FAIL | 30 / 30 | 10 / 10 | V1, V2, V4, V7 | (25, 60, Source) V1 ✓ / ✓ |
| M7 / M7′ Source selected on equality | FAIL / FAIL | 5 / 5 | 5 / 5 | V2 | (29.97, none, 30) V2 ✓ / ✓ |
| M8 / M8′ note without margin | FAIL / FAIL | 5 / 5 | 5 / 5 | V7 | (29.97, none, 30) V7 ✓ / ✓ |
| M9 / M9′ whole-number text | FAIL / FAIL | 6 / 12 | 6 / 6 | V1 / V1, V4 | (29.97, opened) V1 ✓ / ✓ |

**Checked by hand, after the counts, that the checker compared and did not pass by default:** M5's 18 are exactly the cases
that press 120 (9 per rate); M7's and M8's 5 are the 29.97 cases whose last press is 30; M9's 6 are the 29.97 cases whose output
stays at the source rate (opened, or Source last); M9′ adds V4 there because N2a's 30-selection reads the same rounded text.
M3 / M4 fail in the 40 cases whose last press changes the output away from the value they show.

## 4. A2 — the two transcriptions

Same `state` and `buttons` (one variable `outputFps`, opened at `src`; Source → `src`, a number → that number). They differ in
`derived` and `observe`: N2a compares the output text with each preset in the slots and builds the tooltip as a derived value;
N2b keeps S2's `activeFpsPreset` (one value, `'none'` when no digit matches) and wraps S2's `fpsSourceTip` (= the clip's text)
in the slot. Both PASS. Both wrote 「小数 2 桁まで」 as `num(x, 2)` and noted that S2 states no rounding for it (no case value is
a midpoint, so the choice is not exercised). Both left out what no slot observes ("unsaved even when the value is the same")
and the overlay / banner conditions, and noted it.

## 5. A3 — the source-rate control (not judged)

On the 26 cases at source rate 30: N1, M6 and M6′ all PASS. "Source sets a constant 30" cannot be told apart at 30 fps — the
reason the judged rates are 25 and 29.97 (amendment 1).

## 6. A4 — cost

Run from the user's "A: 既定で始める" (after `565609e`, 22:56) to step 5 (about 23:46): about 50 minutes, including a
self-conformance gate before each of four commits (not timed apart). Two agents: t1 13 tool uses (its own count; 14 by its
transcript), 182 s; t2 16, 144 s. The operator wrote the driver, the cross-check, the form, both checkers, N1 and the 18
mutants.

## 7. Limits

- **The operator knows the answer** (definitions section 11): it read the authority's frame-rate code and S2 / S3's entries
  before filing, and fixed the transcription rule "the displayed form follows the text" knowing that S2's `fpsSourceTip` is
  `派生: Clip.fpsText` while the tooltip reads "Same as source (… fps)". **Without that rule, a transcription of the `派生:`
  expression alone would show "25 fps" for V8 and differ in all 52 cases on V8 (derived from the slot, not run)** — an inconsistency inside S2 between the
  expression and its own description, resolved by the rule, not found by the checker.
- **The representations differ less than "direct" and "derived" suggest.** All three keep one variable for the output rate;
  what differs is the path from it to the slots (derived names, a one-value preset, where the tooltip is wrapped). That path is
  what broke EXP-20261031-02's A1, and it is what passed here; a design that splits the state itself differently is not tested.
- **Departure 1**: the transcribers' context named the cases count, the requirement ids and that nine mutants exist (commit
  subjects), not their content; neither read outside its folder.
- The mutants are the operator's named defects; detection of unnamed ones is not measured. 18 of 18 is descriptive.
- The views are not run (their bindings are transcribed from the `.axaml`); the clip is a `ClipInfo` object; one attribute
  family of one product; two transcribers.
