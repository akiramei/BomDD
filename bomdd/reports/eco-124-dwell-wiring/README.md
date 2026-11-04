# ECO-124 filing evidence — the dwell view wired to the session start

- `survey.py` — for each repository's register: the full text view's line count, a warm command-line run's wall clock, and from
  `--json` the counts a session-start summary would show (open, over 14 days, unexplained, crossed 14 days in the last 7 days with no
  reason, paused, warnings, dirty paths). Read-only on the repositories; uses the user's dwell cache as the command line does.
  Run: `python -X utf8 survey.py C:/Users/akira/source/repos` (2026-11-04, heads of that day).
- `survey.txt` — its output (LF). TimetableAdv is out of scope by the user's ruling and is listed for size only.

What it is used for: order section 0 (the full view is the backlog; a summary has to put what just crossed the threshold apart from it).
Manufacture evidence goes to `manufacture/` when the start instruction is given.
