# OBS-20261019-01 — feasibility of saving each review's target with a hook (experiment, 2026-10-19)

**What this is:** a feasibility check approved by the user (2026-10-19, "A"), **not an adoption of the hook method** — that is decided separately.
A temporary hook in the uncommitted local settings (`.claude/settings.local.json`, absent before) ran `review_snapshot_hook.py` from the session's
scratch folder; it stored each named review target with bomdd-run's `store_brief` (ECO-112 B2, unchanged) in a separate store bucket. Nothing
permanent was added: after the runs the settings file was removed, the bucket was removed (its three files are copied to `stored/`), and the
repository's tracked files were never changed.

## Results by the user's conditions

| # | condition | result | evidence (`ledger.jsonl`, `check-reports.txt`) |
|---|---|---|---|
| 1 | the temporary hook stays uncommitted and local, and is removed after the experiment | **met** | `.claude/settings.local.json` created for the runs, removed after; `settings-used.json` is its copy |
| 2 | it fires on the first review and on a follow-up to the same reviewer | **met** | PreToolUse fired for `Agent` (launch) and for `SendMessage` (follow-up to the same agent id) |
| 3 | the named files are saved at the start and their content matches by SHA-256 | **met** | 3 files stored; each re-hashes to its name; the in-repository target (`7da7633c…`) equals ECO-112's order at HEAD; the outside target was changed between rounds and both versions are kept (`7326ece9…`, `fda2e1a8…`) |
| 4 | at the end, the review result can be linked to the saved version | **met, with a rule** | request → agent: `tool_use_id` of the launch and the agent id in PostToolUse's response (foreground: at completion; background: 0.3 s after launch); follow-up → agent: `to`. Report: its sha256 logged at the reviewer's report call, with the agent id; all 3 equal the reports in the reviewers' own transcripts. A round's report is the agent's next report after the request (order). SubagentStop's last message was empty here (the report goes through a tool) |
| 5 | a failure to save refuses the review's start | **met** | a missing target blocked the launch (`Agent`) and the follow-up (`SendMessage`), exit 2 with the reason; no reviewer ran |
| 6 | the same works for a file outside the repository | **met** | the scratch-folder target was stored like the in-repository one |
| 7 | files the reviewer reads during the review: their content at read time | **partly** | a `Read` inside the reviewer is seen with the reviewer's id and the whole file is stored just before the read (2 rounds: same sha256 as the start snapshot). A read through `Bash` (`head`, `sed`, `git diff`…) is logged as the command only — which files it read, and their content, is **not** captured; `Grep`/`Glob` were not hooked |
| 8 | after the experiment the hook is removed and the settings are as before | **met** | `.claude/` holds the same entries as before (`skills/`, `worktrees/`); a launch that the hook had blocked now runs, and the ledger did not grow (18 lines) |

## Constraints found (for the adoption decision)

- **The targets must be named in the request** (here: `REVIEW-TARGET: <path>` lines). The hook sees only the request text.
- **`store_brief` refuses a file containing CR** (`BRIEF_NOT_LF`, by its code; not exercised here): a CRLF target would block the review.
- **Reads through the shell are outside the guarantee.** In the 38 rounds measured in `bomdd/reports/review-origin-20261018/`, reviewers read the
  orders mostly through `Bash`; a guarantee for "what the reviewer read" would need the reviewer to use `Read`, or a different capture.
- **The store is clone-local** (`<git-common-dir>/bomdd-run/briefs/<bucket>/`), as ECO-112's L4: lasting beyond the clone needs the files committed.
- **The hook's scope is every subagent of the project** while it is configured: each `Read` inside any subagent stores the whole file.
- The settings change was picked up within seconds by the running session (the documented file watcher); no restart was needed.

## Files

`review_snapshot_hook.py` (the temporary hook), `settings-used.json` (the settings it ran under), `ledger.jsonl` (every hook invocation),
`check_reports.py` and `check-reports.txt` (report hashes against the reviewers' transcripts; stored files against their names), `stored/` (the
three stored versions, named by sha256).
