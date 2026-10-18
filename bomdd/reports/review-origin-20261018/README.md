# Review-finding origin — ECO-112 / ECO-113 design reviews (measured 2026-10-19)

**Purpose (user ruling 2026-10-19 "A"):** keep the primary records of the 38 design-review rounds, which existed only in this session's own
records, and make a baseline that a third party can re-measure. It is a measurement, not a full classification: what the records cannot
show is UNKNOWN. The converge procedure is not changed and the instruments here were not independently reviewed (the user's conditions).

**Result:** [`summary.md`](summary.md); one record per finding in [`findings.jsonl`](findings.jsonl).

| origin time of the text a finding points at | findings |
|---|---|
| INITIAL — in the ECO's first reviewed version (by a quote: 8; reported in the ECO's first round: 23) | 31 |
| LATER — first appeared in a later reviewed version (the round is named) | 42 |
| UNKNOWN — no quote, a paraphrase, or quotes that disagree | 40 |
| total (equal, round by round, to the receipts' counts) | 113 |

The cause axis is kept apart: it is copied only from what the record says (the reviewer's tag or the order's "Classes in this loop" line),
so 88 of the 113 causes are UNKNOWN. Origin time is the quoted **text's** time, not the defect's cause: for example AR3-1's sentence ("the set
of briefs launched…") is in every version from L2R1, and became a defect only when the amendment added a rollback.

## What is here

| path | what it is |
|---|---|
| `primary/reviews.jsonl` | every request record of the three reviewer subagents (41, of which 3 are harness reminders) and every report they handed back (38), with source line |
| `primary/edits.jsonl` | every file-writing call of the main session (582): Write content, Edit old/new strings, shell commands, tool-result error flag |
| `primary/file-history.json`, `primary/file-history/` | Claude Code's checkpoint copies of the two orders (20): full content at a snapshot |
| `primary/shell-replays/` | the result of re-running each shell write of an order on a temporary copy (index, results, the ones that could not be re-run) |
| `primary/sources.json` | sha256 and size of each transcript as read (the main session's transcript kept growing after the read) |
| `anchors/` | the git versions of the two orders (10 commits) |
| `baseline/` | the repository files at `3a9de06` (quotes found there are cited code, not design text) and the final orders (for the recorded classes) |
| `round_map.json` | which report is which loop and round, with the receipts' per-round counts |
| `versions/`, `versions.json` | the order as each of the 38 rounds reviewed it, with sha256 and how it was rebuilt |
| `control-drop-edit-38.txt` | positive control of the rebuild |

## How it was measured, and how to re-measure

1. `extract_primary.py <session.jsonl> <subagents dir> primary <file-history dir>` — needs the transcripts (this machine only). Its outputs are kept.
2. `make_anchors.py <repo> anchors` — needs the repository.
3. `rebuild_versions.py .` — rebuilds every reviewed version from anchors (Write, checkpoint, git commit) by replaying the Edits that succeeded and
   the stored shell replays; a replay is accepted only if it equals the next anchor, otherwise the versions in between are UNKNOWN. The shell
   replays were made once with `--emulate-shell` on this machine (it re-runs the order-writing part of each command on a temporary copy; commands
   that a hook blocked are skipped). **Result: 38/38 reviewed versions known**, each an anchor or confirmed by the next one.
4. `measure_origin.py .` — reads only the files above; same inputs, same outputs.

Steps 3-4 run from this folder alone. Checks run once (not an independent review):
- the per-round finding counts equal the receipts' counts in all 38 rounds;
- positive control: leaving out one Edit (`--drop-edit 38`) turns the two affected rounds UNKNOWN; without it, 38/38;
- two runs gave the same `versions.json`, `findings.jsonl` and `summary.md` (same sha256);
- four findings re-checked against every reviewed version by a separate script (A1R1-1, AR3-1, L4R1-1 of ECO-113, R2-1): all agree.

## Limits

- The time measured is the quoted text's; a defect in old text caused by a later change elsewhere reads as the old text's time.
- A finding with no quote (17) or with only paraphrased quotes (22) is UNKNOWN unless it was reported in the ECO's first round.
- A quote can match an unrelated passage with the same words (minimum 15 characters after normalisation).
- ECO-113's first version was written from ECO-112's pre-split draft; for ECO-113, text carried over reads INITIAL.
- The shell replays depend on this machine's scratch files at the time of the run; a third party uses the stored results, and their correctness
  rests on the anchor check, not on re-running them.

The way to make this measurable from the repository alone next time (an immutable copy and sha256 of each reviewed version) is recorded
separately as OBS-20261019-01 in `method/improvements.md`.
