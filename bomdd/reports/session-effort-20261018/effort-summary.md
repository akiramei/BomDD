# ECO-112 / ECO-113 session — effort measurement (observed, 2026-10-18 11:48 → 23:59 JST)

Instruments: `session_effort.py` (this folder; partition of the transcript by what ends each idle gap) → `effort.md`; `git log`/`git diff --numstat`
on `3a9de06..5ddd428`; the orders' receipts for review rounds. The repository's `time-decomposition.py` was run first: it counts every wait that
ends with a system notification as HUMAN (its declared limit), 9:04 — not usable for this session.

## 1. Wall clock (12:11)

| state | time | share |
|---|---|---|
| AI active (inside a turn) | 3:05 | 25% |
| waiting for background work, AI idle | 2:11 | 18% |
| — of which checks / CI / cells (task notification) | 1:54 | 16% |
| — of which the reviewer subagent (peer report) | 0:17 | 2% |
| waiting for the human | 6:56 | 57% |
| — of which two long gaps (14:48→18:18, 18:42→19:43) | 4:30 | 37% |

AI active 3:05 = foreground tools 0:48 (Bash 0:21, Edit 0:14 over 162 edits, Agent 0:11, SendMessage 0:01) + model time ≈ 2:17.

## 2. By segment (between the user's 13 messages)

| # | JST | what | AI active | BG wait |
|---|---|---|---|---|
| 1 | 11:48 | proposal evaluated | 0:06 | 0:00 |
| 2-7 | 12:22-18:18 | design loops (ECO-112 L1-L5, ECO-113 L1-L4), 6 rulings | 1:04 | 0:48 |
| 8 | 19:43 | ECO-112 manufacture + V3 run 1 + r1; ECO-113 loop 5 | 0:42 | 0:09 |
| 9 | 20:52 | amendment loop A; ECO-113 record fix and filing | 0:20 | 0:05 |
| 10-11 | 21:17-22:44 | amendment loop A2, repair, V3 run 2, r2 | 0:34 | 0:24 |
| 12 | 22:52 | exception ruling, r3, closure | 0:15 | 0:46 |

## 3. Background compute (runs overlap each other and AI-active time)

| class | runs | total | each |
|---|---|---|---|
| V3 instrument | 3 (1 discarded: `python -I` hid PyYAML; 1 FAIL; 1 PASS) | 2:11 | 21-57 min |
| self-conformance | 12 (2 at closure: the first failed C17, the calibrate receipt) | 0:46 | 3.2-4.7 min |
| CI wait | 7 | 0:30 | ~4 min |
| independent inspection cell (Codex) | 3 (r1 REJECT 2, r2 REJECT 1, r3 ACCEPT) | 0:25 | 4-11 min |
| rule mutations | 3 (+2 foreground) | 0:17 (+0:05) | 3.5-7 min |

## 4. Design review and inspection

| | loops | rounds | findings (material) | converged by the default rule |
|---|---|---|---|---|
| ECO-112 | 7 (L1-L5, A, A2) | 23 | 63 (28) | L5 and A2, each only with a user-approved 4th round |
| ECO-113 | 5 | 15 | 50 (16) | none (filed by an exception ruling) |
| total | 12 | 38 | 113 (44) | |

Inspection: 3 rounds, 3 blocking findings: IA-01, IA-02 rooted in the converged design; IA-03 in the inspection brief's range.
User rulings asked: 12 (each a DECIDE of 1,500-4,000 characters; 22,610 characters in all).

## 5. Output

| kind | lines added | files |
|---|---|---|
| tools code (`bomdd-run.py`, `bomdd-job.py`) | 595 (+608/-46 with templates) | 2 |
| orders (ECO-112 648 lines, ECO-113 496) | 1,144 | 2 |
| instruments and probes (py) | 1,279 | 16 |
| reports, briefs (md, txt) | 756 | 27 |
| evidence JSON | 12,015 | 3 |

Commits 11 (file 2, design 1, fix 2, record 5, accept 1); every push's tip CI success.

## 6. Tokens (lower bounds)

| scope | API calls | cache read | cache write | output |
|---|---|---|---|---|
| main session | 515 | 230.3 M | 2.3 M | ≥ 611 k |
| reviewer subagents (3) | 131 | 25.4 M | 3.6 M | ≥ 45 k |

Cache read per main-session call ≈ 447 k tokens (the conversation's context is re-read on every call; one compaction at 21:16).

## Limits

- The state partition is by what ended a gap; human reading time and background work overlap HUMAN_WAIT.
- Output tokens are lower bounds: some transcript records do not hold a call's final usage (the third reviewer shows 3-16 output tokens on calls
  that returned long reports). Codex cells' own tokens are not in this transcript.
- "Model time" lumps generation, thinking and harness overhead; Edit's 0:14 may include permission checks.
- Segment labels are mine, from the order's records; the boundaries are the user's messages.
