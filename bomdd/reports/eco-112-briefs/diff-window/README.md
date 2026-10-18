# ECO-112 diff window under the exception ruling (order §8)

The user's ruling (2026-10-18, "A"): ECO-112's V6 and its independent inspections count only the commits attributed to ECO-112; ECO-113's filing
commit `3c7781c` is not part of ECO-112's manufacture. This is an exception for ECO-112, not a general rule (the general question is OBS-20261018-02).

| file | what it is |
|---|---|
| `diff_window.py` | the check: attribution by the commit subject's `(eco-NNN)` tag; C1-C5 (header of the script) |
| `diff-window.md` | its run on `3a9de06..436f0c6` (the window up to the r2 record): **PASS** |
| `control-include-3c7781c.md` | the positive control: the same run with `3c7781c` counted as ECO-112 on purpose: **FAIL** (C4 names its paths) |

Run: `python -B diff_window.py <repo> <baseline> <head> [--control-include <sha>]`. At closure V6 is re-run on the final head (the user's condition 5).
