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

## What the experiment did not test

- **Refusal on a save failure:** only a missing target was tried. A target containing CR, a failed write to the store and other failures were not.
- **Linking reports to requests:** one session, three reports. No timeout, resent report or reviewer ended mid-review occurred, so the cases
  where the order rule ("the agent's next report after the request") becomes ambiguous were not observed.
- **Control by a hook in general:** the experiment shows one function — saving the named targets at a review's start and refusing the start —
  for this harness. It does not show that other workflow control can be moved into hooks.

## Design premises for an ECO (user AGREE, 2026-10-19 — premises only, not a filing or an implementation approval)

1. **Scope:** the guarantee covers the targets named in the request, as they were at the review's start. Files the reviewer reads on its own
   are not captured completely, and the design does not try to.
2. **A second hash at the report:** at the report, the named targets are hashed again and the result is recorded as `MATCH`, `CHANGED` or
   `UNKNOWN`. It compares the start and the end only; it does not show that the target was unchanged throughout the review. It is an
   observation: no rule refuses or stops a review on `CHANGED`. In the 38 measured rounds, no order was edited while its reviewer ran
   (0/38; the same matcher finds 80 and 68 edits to the two orders over the whole session — `during_review.py`, `during-review.txt`).
3. **Claims:** the record states what the experiment tested and what it did not (the section above), and claims no more than was measured.
4. **Reuse first:** existing mechanisms are reused; a new state or identifier (for example a review run id) is added only when its need is shown.

## Files

`review_snapshot_hook.py` (the temporary hook), `settings-used.json` (the settings it ran under), `ledger.jsonl` (every hook invocation),
`check_reports.py` and `check-reports.txt` (report hashes against the reviewers' transcripts; stored files against their names), `stored/` (the
three stored versions, named by sha256), `during_review.py` and `during-review.txt` (order edits made while each reviewer ran, from
`bomdd/reports/review-origin-20261018/primary/edits.jsonl` and `versions.json`; run from the repository root with that folder as the argument).
