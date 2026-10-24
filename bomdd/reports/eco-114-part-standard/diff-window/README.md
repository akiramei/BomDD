# ECO-114 diff window under the exception ruling (user "1:A" on inspection r1's IA-01, 2026-10-24)

ECO-114's window `be96698..` (the register's `diff_audit.baseline`) holds ECO-115's held-draft record commit `afabdb1` between ECO-114's filing
`25bea38` and its manufacture `286d02c`. By the user's ruling the change set is ECO-114's commits only, with `afabdb1` excluded and its reason recorded
— ECO-113's method (`bomdd/reports/eco-113-briefs/diff-window/`). OBS-20261018-02's third case.

| File | What | sha256 |
|---|---|---|
| `diff_window.py` | ECO-113's tool with ECO-114's constants (tag, own records, the one record commit, the manufacture's input files at `25bea38`) | `2362c285a118dcf381cb234581d308957b0cc940a82aa94d59829cd819d16e47` |
| `diff-window-to-r1.md` | `python -B diff_window.py . be96698 5bc708a` — PASS (3 ECO-114 commits, 26 paths, all allowed; `afabdb1` excluded, before the manufacture, touching none of ECO-114's records or inputs) | `927362f54259e1f411337a9835cbe462d724b44f76eec5fb5d2414d6033545ab` |
| `control-include-afabdb1.md` | the same with `--control-include afabdb1` (the commit counted as ECO-114's on purpose) — FAIL on C4 and C5, the positive control | `0be77fa7cc94de19f98384aee53f36f6fd2072b15671eb7ed99b2db41c28d8f7` |

The window is measured again at closure on the final head.
