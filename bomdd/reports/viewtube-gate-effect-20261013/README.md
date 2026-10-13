# ViewTube gate effect after ECO-VT-254 and 255, read in the ECO-VT-258 window (2026-10-13)

**Request**: the user asked (2026-10-13) whether the effect of the ViewTube gate speed-ups can be confirmed in the ECO-VT-258 work, then asked for this record. It adds a third reading to EXP-20261011-01 (recovered 2026-10-12, `../viewtube-gate-effect-20261012/`). It does not reopen that EXP.

## 1. Window and instrument

- **Window**: 2026-10-13T06:49:33Z to 07:20:00Z.
  - It begins right after ECO-VT-257's record commit `58dd179c` and ends after ECO-VT-258's acceptance `dcf5c178`.
  - The work was ECO-VT-258: a filing workflow text change, documents only, with no product code, tests, build, supervised suite or capture sweep.
  - The work ran in this methodology session, together with one fresh-context reviewer subagent.
- **Instrument**: the same `../viewtube-inspection-cost-20261010/measure.py` as the earlier readings, with the same classes → `measure-output.txt`.
  - measure.py has no end time, so `window_copy.py` first copies the session transcript lines inside the window into a temporary tree. That tree keeps measure.py's main/subagent split.
  - Q4 (acceptance runs) filters by day, not by time, so its three runs are from earlier the same day and are not part of this window.
- **`validate_process.py` alone**: timed three times in a row in ViewTube's working tree at `dcf5c178`.

## 2. Results

| Measure | Before (2026-10-07 to 10) | After ECO-VT-250 (ECO-VT-252 window) | This window (ECO-VT-258) |
|---|---:|---:|---:|
| One commit, hooks included | mean 161 s | mean 79 s | 35, 36, 41 and 57 s (mean about 42 s) |
| `validate_process.py` once | 109.8 s | 25.2 s | 13.9 and 14.4 s warm; 51.2 s on the first, cold run |
| Gate refusals | — | 2 (the same kinds as before) | 1 (materialisation divergence) |

- **The 57 s commit** also ran `validate_process.py` (about 14 s) inside the same tool call, so the commit itself was about 44 s.
- **Every commit staged the register.** None matched the capture-sweep pattern (Q2b).
- **Cross-check**: ECO-VT-255 profiled a register-staged record commit's gate at 29.6 s in a clone. In real work, with the other git steps of each call included, the commits here took 35 to 44 s, which is consistent.
- **The one refusal** was correct. The manufacturer's evidence files had CRLF line endings, and the gate's materialisation check caught them. This kind of check predates the speed-ups, and nothing suggests a verdict changed.

## 3. Limits

- **The kind of work differs between windows.** This one had no sweep, build or suite, and only four ViewTube commits. Compare the per-commit seconds, not the window totals.
- **The wait share (EXP-20261011-01 ②) is not meaningful here.** Gate waits are 64% of 8.5 minutes of tool waits, but there were almost no other tool waits, so the denominator is small.
- **Seconds are tool-call elapsed times.** They include any other command run in the same call.
