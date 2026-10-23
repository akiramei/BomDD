# ECO-113 diff window under the exception ruling (order, amendment ruling "2:a")

The user's ruling (2026-10-24, "2:a"): V8's diff window is ruled for ECO-113 as an exception, by ECO-112's method (ECO-112 order §8): the commits in
the register's window (`diff_audit.baseline` `f2d91d4`) that are not ECO-113's are excluded with their reasons, non-interference is checked by diff, and
ECO-113's change set is enumerated in full as inspection r2's target. This is an exception for ECO-113, not a general rule; its second case is recorded
in OBS-20261018-02 (`method/improvements.md`).

| file | what it is |
|---|---|
| `diff_window.py` | the check: attribution by the commit subject's `(eco-NNN)` tag and a named list of three untagged record commits; C1-C5 (header of the script) |
| `diff-window.md` | its run on the final window (written at closure) |
| `control-include-597e842.md` | the positive control: the same run with the record commit `597e842` counted as ECO-113 on purpose: **FAIL** (C3 and C4 name it) |

Why ECO-112's method needed one change: ECO-112's excluded commit was a filing that touched none of ECO-112's tools; here the excluded ECO-112 commits
change the same tools ECO-113 changes (`bomdd-run.py`, `bomdd-job.py`, `operator-layer.md`), because ECO-112 was manufactured first by its rule M1. So
C3 checks that every excluded commit precedes ECO-113's manufacture and that the tools at that point equal the inputs the order's §4 names; ECO-112's
changes are ECO-113's input, not part of its change.

Run: `python -B diff_window.py <repo> <baseline> <head> [--control-include <sha>]`.
