# Change Order — ECO-124 (progress: the dwell view is shown at the start of every Claude Code session in a BomDD repository, as a short summary that separates what just stalled from the old backlog, and what to decide about it is written down)

> Ruling: user, 2026-11-04, "起票に進む" — the answer to "進捗の表示を工程に結線する ECO(hook と判断の規則)の起票に進みますか？" after
> ECO-123's closure. The thread behind it: "工程管理と進捗管理の改善は、仕組みの問題です" (the method, not each product's backlog); "必ず実行する
> ならHookにできますが、問題はありますか？" (answered then: a hook gives "see", and still needs a short output, speed, a visible "could not
> measure" and a rule for "decide"); ECO-122 made the view fast enough to run at every session start.
>
> Each part below is labelled **stop** (refuses), **measure** (a number produced and compared) or **none** (text only), as the standing
> caveat of 2026-10-29 asks. **Filing only.** Manufacture waits for the user's start instruction (ECO-106), and **the start instruction
> also answers two points that are the user's** (section 1, "For the start instruction"): the rule for what to decide, and the edit to the
> user-level Claude Code settings. Records are English-primary.

## Equipment

- Filing: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- Producer: EQ-004.
- Independent inspection: none planned (a read-only summary and a hook that prints it; the manufacturer's calibration only). The user may
  name one at the start instruction.

## 0. Measurement (basis of the filing)

**What exists** (read 2026-11-04): no repository has a Claude Code hook (`.claude/settings.json` absent in BomDD, ViewTube and ViewPrism2);
the user-level `~/.claude/settings.json` has one `PreToolUse` hook (the heredoc stop). Every repository has git hooks under `bomdd/hooks/`
(`core.hooksPath`); BomDD's is the pre-push witness. Nothing runs `bomdd-job.py --dwell`: not a hook, not `bomdd-run.py`, not CI.

**What a session-start summary would show** (`bomdd/reports/eco-124-dwell-wiring/survey.py`, `survey.txt`; warm cache, wall clock of the
command line):

| Repository | full text | warm run | open | over 14 d | unexplained | crossed 14 d in the last 7 days, unexplained |
|---|---:|---:|---:|---:|---:|---|
| BomDD | 6 lines | 0.81 s | 2 | 1 | 1 | 0 |
| ViewTube | 180 lines | 1.14 s | 173 | 173 | 170 | 1 (ECO-VT-267) |
| ViewPrism2 | 31 lines | 0.37 s | 24 | 24 | 17 | 0 |
| BomDD-Plm | 5 lines | 0.30 s | 0 | 0 | 0 | 0 |
| MoviePad-Remake | 5 lines | 0.51 s | 0 | 0 | 0 | 0 |
| TimetableAdv (out of scope by the user's ruling; shown for size) | 82 lines | 1.00 s | 77 | 77 | 77 | 0 |

**What it shows.** The view is fast enough for every session start (≤ 1.2 s warm; the first run on a machine ≈ 40 s on ViewTube, ECO-122).
But the full text is the backlog: in ViewTube 170 of 173 lines would be the same old entries at every session start, which teaches a
reader to skip them; the one entry that stalled this week (ECO-VT-267) is one line among them. A summary has to put **what just crossed
the threshold** apart from **the backlog**, and the two need different decisions: the first is a decision due now; the second is a triage
done once.

## 1. Change request (frozen at filing)

**P1 — a short form of the view (measure).** `bomdd-job.py --dwell --brief` prints at most 8 lines (ids capped at 10 per line, then
"+N more"):
1. `dwell: <register> — open N, over <T> d M` (or `dwell: not measured — <reason>`, and nothing else);
2. `DECIDE: crossed <T> d in the last 7 days with no reason: K — <id> <status> <days> d, …` (only when K > 0): open entries with no
   `waiting_on`, not under `paused`, whose days are in (T, T + 7] — derived each run, no state kept;
3. `backlog: unexplained X · <reason> Y · …` (open entries over the threshold that crossed it more than 7 days ago, by reason);
4. `paused: <days> d — <reason> / resume when: <condition>` (only when paused);
5. `uncommitted: dirty D, oldest E d (lower bound), register differs from HEAD: yes|no`;
6. `warnings: W — run bomdd-job --dwell for the lines` (only when W > 0).
It uses the same `dwell()` result as the full view (cache as ECO-122); exit 0; the full view and `--json` are unchanged.

**P2 — shown at every session start (measure: a summary produced at each start).** `method/tools/dwell-session-hook.py`, versioned in
BomDD, is a Claude Code `SessionStart` hook:
- It reads the hook's input (JSON on standard input; its `cwd`, else the process's), finds the git top level, and looks for a register at
  `bomdd/60-change-register.yaml` or `bomdd/process/change-register.yaml`. None: it prints nothing and exits 0 (any other repository is
  untouched).
- Found: it runs P1 with BomDD's own tool (located next to the script) under a time bound (75 s; ViewTube's first run ≈ 40 s) and prints
  the brief, which Claude Code adds to the session's context. Any failure or the bound reached prints one line,
  `dwell: not measured — <reason>`, and exits 0 — never silence, never a blocked session.
- `--check` reports whether `~/.claude/settings.json` holds a `SessionStart` entry that runs this script (installed / not installed /
  settings unreadable), so the installation can be measured.
- **Installed once per machine, in the user-level settings** (`~/.claude/settings.json`, one `SessionStart` entry with a timeout of 90 s),
  so every BomDD repository on the machine is covered with no change to any product. The edit is shown before and after and made only on
  the user's go-ahead (see below).

**P3 — what to decide (none: text; its effect measured by P1's line 2).** In `method/bomdd-playbook-v1.md` §8 (after ECO-120's
paragraph) and one line in `AGENTS.md`:
- **Due now** — an entry on the brief's `DECIDE` line is put to the human in the session's first handoff (a DECIDE), with the options:
  resume it; record why it waits (`waiting_on`, written by the step that stops it — OBS-20261104-01 point 1); pause the repository
  (`paused`); or withdraw / supersede it (a human ruling). The AI does not choose among the last three by itself.
- **Backlog** — not asked at every session; a triage the human schedules, per repository, using the full view.
- **Measure** — an entry decided leaves line 2 (it gets a reason, a pause, or another status); an entry not decided leaves line 2 after
  7 days into the backlog. A later re-measure (as ECO-121 V5) counts entries that entered the backlog unexplained after this ECO's
  application.

**P4 — the manual entry (none).** `AGENTS.md` names `python <BomDD>/method/tools/bomdd-job.py --dwell --brief [--register PATH]` as the
command for a session the hook does not reach (another harness, or a machine without the hook).

**For the start instruction (the user's points):**
- **The rule of P3** as written, or another cadence (for example: put the `DECIDE` line to the human only in a session's last handoff, or
  only when K > 0 for 2 days).
- **The user-level settings edit of P2** — `~/.claude/settings.json` gains one `SessionStart` entry. It is persistent configuration
  outside any repository; it is made at manufacture only with the user's go-ahead, and can be removed with one line.

**Not chosen:**
- **A hook in each repository's `.claude/settings.json`:** every product would need a distribution ECO (ViewTube's under its gate
  freeze), and the entry would carry a machine path to BomDD's tool in a checked-in file.
- **A git hook** (post-checkout, pre-commit): harness-independent, but git has no "session start"; a commit-time print would repeat at every
  commit and would not reach a session that only reads.
- **`bomdd-run.py` prints the summary at launch:** its path is the factory launch, which the operator session already starts after seeing
  the summary; a factory (Codex) does not decide progress.
- **The full view at session start:** 180 lines in ViewTube, almost all backlog (section 0).
- **A stop** (refuse to start, or refuse a commit, while an entry is due): the decision is the human's, and a stop would block unrelated
  work on the calendar alone (ECO-120's reason against an age gate).
- **Keeping state to show "new since the last session":** a stored value; "crossed in the last 7 days" is derived from the history.

## 2. No-impact prediction (before manufacture; frozen)

- **Diff:** `method/tools/bomdd-job.py` (`--brief` and its selftest arms), `method/tools/dwell-session-hook.py` (new, with `--selftest` and
  `--check`), `method/bomdd-playbook-v1.md` (§8, one paragraph), `AGENTS.md` (one line); this order, the register,
  `bomdd/reports/eco-124-dwell-wiring/`. Outside the repository: one entry in `~/.claude/settings.json`, only on the user's go-ahead.
- **Verdicts:** every existing `bomdd-job.py` mode (the full `--dwell`, `--json`, job views, `--all`) prints the same output;
  `bomdd-run.py` decides the same; every self-conformance check gives the same line on the same tree.
- **Products:** none changed. A session started in any BomDD repository on this machine receives the brief once the hook is installed.

**Declared at filing — what this will not do:**
- **Only Claude Code sessions on a machine with the hook see it.** A Codex session operating directly, or another machine, does not; the
  manual entry (P4) is text.
- **The decide rule is text.** Nothing stops a session from not asking; its effect is measured afterwards by line 2 and the re-measure.
- **The first session start on a machine waits for the cold read** (≈ 40 s on ViewTube); the bound turns a longer wait into "not
  measured".
- **The brief is as of the last `SessionStart` event.** Claude Code fires it on startup, resume, `/clear` and compaction; the brief
  is re-run on the sources the entry's `matcher` admits (chosen at manufacture and recorded in V4), and not between them.
- **The backlog is not reduced by this ECO** (ViewTube 170, ViewPrism2 17, BomDD 1 unexplained); its triage is the human's, scheduled
  separately.
- Section 2 of ECO-120 still holds: the view does not tell whether a status or a reason is true.

## 3. Acceptance (conditions; frozen at filing)

required_gates: [V1, V2, V3, V4, V5, V6]

**Gated:** V1-V6.

- **V1 — the brief agrees with the full view.** On BomDD, ViewTube, ViewPrism2, BomDD-Plm and MoviePad-Remake (TimetableAdv excluded by
  the user's ruling), at one fixed `now` in-process: every count and id on the brief equals what is derived from `dwell()`'s result by the
  rules of P1; at most 8 lines.
- **V2 — the brief's rules** (selftest arms on a fixture): entries at 14.5, 21.0 and 21.5 days with no reason are on line 2, line 2 and
  line 3 respectively; an entry at 15 days with a reason is not on line 2; under `paused`, nothing is on line 2; more than 10 ids end in
  "+N more"; a register that cannot be measured gives the one `not measured` line.
- **V3 — the hook script** (`dwell-session-hook.py --selftest`): no register → no output, exit 0; a register → the brief, exit 0; the tool
  failing → one `dwell: not measured — …` line, exit 0; the bound reached (set small in the arm) → `not measured — time bound`, exit 0;
  input without `cwd` → the process's directory. Known-bad: a copy that swallows the failure silently turns the failure arm red.
- **V4 — installed and reported.** With the user's go-ahead, `~/.claude/settings.json` gains one `SessionStart` entry (before and after
  recorded, the existing `PreToolUse` entry unchanged); `--check` reports `installed`, and on a copy of the settings without the entry
  reports `not installed`.
- **V5 — seen in a real session.** A new Claude Code session started in BomDD and one in ViewTube each quote the brief they received at
  start (the line 1 of each matches V1's for that repository at that time).
- **V6 — nothing else moves; time; the gate.**
  - `--dwell` (full, text and JSON at a fixed `now`), `--all --json`, `--all`: byte-identical from the filing tree's tool and the changed
    tool; `bomdd-job.py --selftest` and `bomdd-run.py --selftest` exit 0.
  - The hook on ViewTube with a warm cache finishes within 3 s (wall clock, three runs).
  - Self-conformance exits 0, observed before each commit of this ECO; CI is green for each pushed commit (read by the full SHA).

Conditions are frozen at filing; results go to the closing section.

## 4. Manufacture (2026-11-04, on the user's "1:A 2:A 3:A")

The user's ruling at the start instruction: **1:A** the rule of P3 as written; **2:A** the user-level settings edit approved (the
entry shown in the ruling request); **3:A** manufacture as filed.

**What was made.**
- `method/tools/bomdd-job.py` (sha256 `3d290fc20aa44423…`): `render_brief()` and `brief_not_measured()`; `--brief` in `dwell_main`
  (with `--json` = argument error); header usage line and note (9); dwell selftest arms for the brief. The brief is 3-7 lines: header,
  `DECIDE` (only when due), a `rule:` line naming the decide rule (only with `DECIDE` — added so that a session reading the brief has the
  rule beside the entries; still within P1's 8 lines), `backlog`, `paused` (only when paused), `uncommitted`, `warnings` (only when any).
- `method/tools/dwell-session-hook.py` (new, sha256 `5e46cce424679f2e…`): hook mode, `--check [--settings PATH]` (exit 0 installed / 1
  not / 2 unreadable), `--selftest`. On a time bound the child is stopped with its process tree (`taskkill /T` on Windows, the process
  group elsewhere).
- `method/bomdd-playbook-v1.md` §8: one paragraph after ECO-120's (display and decide rule, measured by the DECIDE line, limits).
- `AGENTS.md`: a short section "進捗の表示と判断(ECO-124)" before 正本の所在 (the hook, the manual command, the rule in one sentence).
- Outside the repository: `~/.claude/settings.json` gained the one `SessionStart` entry (V4).

**Results** (evidence in `bomdd/reports/eco-124-dwell-wiring/manufacture/`, README there):
- **V1 PASS** (`v1.txt`): five registers at now = 2026-11-04T12:00Z, the brief's header, `DECIDE` ids, backlog counts, paused,
  uncommitted and warnings equal an independent derivation from the same `dwell()` result; 3-5 lines each. ViewTube: `DECIDE` =
  ECO-VT-267 (staged 15.0 d), backlog unexplained 169 · eco:ECO-VT-081 2 · eco:ECO-VT-095 1.
- **V2 PASS**: `bomdd-job.py --selftest` exit 0; the dwell PASS line names the ECO-124 arms (14.5 and 21.0 d on `DECIDE`, 21.5 d /
  with a reason / 3 d not; backlog counts by reason; paused = no `DECIDE`; cap 10 + "+2 more"; two one-line not-measured cases).
  Known-bad (`mutants124.txt`): window end excluded, reason ignored, no cap, not-measured silent — 4 of 4 FAILED; the unchanged copy
  passes.
- **V3 PASS**: `dwell-session-hook.py --selftest` exit 0 (no register / not git = silent; both register places, from a subfolder =
  brief; the tool's own not-measured line; a crashing tool and unexpected output = one hook line; bound 1.5 s with a grandchild = one
  line within the bound; input without cwd, empty, not JSON, a missing folder, a non-string = the process's folder; `--check` 4 cases).
  Known-bad: tool failure swallowed, time bound swallowed, unexpected output passed through, input cwd ignored — 4 of 4 FAILED; the
  unchanged copy passes.
- **V4 PASS** (`v4.txt`): before 5,017 bytes with hooks [PreToolUse], after 5,337 bytes with [PreToolUse, SessionStart]; every other key
  and the PreToolUse entry unchanged (parsed JSON); `--check` reports installed (exit 0), and not installed (exit 1) on the copy of the
  settings before the edit.
- **V5 FAIL — the BomDD arm; the ViewTube arm PASS** (measured 2026-11-04 after the terminal CLI was signed in again; the first runs
  at manufacture could not start a session — "OAuth session expired"). Headless sessions (`claude -p`, CLI 2.1.207, its default model
  `claude-opus-4-8[1m]`, no tools, the desktop app's environment variables removed):
  - `v5.txt` (the frozen V5 run): ViewTube quoted the brief — line 1 equal to the hand-run line 1, and the `DECIDE` (ECO-VT-267) and
    `backlog` lines; BomDD replied `NONE`.
  - `v5rep.txt`: three more runs in BomDD all `NONE`; two more in ViewTube both quoted. Total BomDD 0/4, ViewTube 3/3.
  - **The hook's text reached the BomDD sessions.** Every BomDD run's stream shows the hook's `dwell:` output (`--include-hook-events`),
    and the session transcript holds it as a `hook_success` attachment placed before the user's prompt — the same place as in ViewTube's.
    Asked differently (`v5probe.txt`), a BomDD session first answered `NO` / `NOT FOUND` and then corrected itself and copied the three
    lines exactly. So the failing arm is the session's first answer, not the tool, the hook or the harness's delivery.
  - Discriminators (`v5disc.txt`): a third repository, ViewPrism2 (24 open, no `DECIDE` line), also replied `NONE` — so this is not
    BomDD's context alone; the one repository that quoted is the one whose brief carries a `DECIDE` line. Not separated: whether the
    `DECIDE` line or something else in ViewTube's context makes the difference (one repository on each side). The desktop app's model
    (`claude-opus-5-5`) could not be run headless — CLI 2.1.207 refuses it ("version 2.1.280 or newer is required"); updating the CLI
    was not done (it changes the user's install).
  - Also seen (`v5-compact-observation.txt`): in this manufacturing session (desktop app, Opus 5.5) the hook fired on compaction and its
    three lines were the hand-run BomDD brief's — the session did take it in. One observation, source `compact`, not the V5 arm.
  - What this means for the ECO's purpose: the rule ("put the `DECIDE` entries to the human in the first handoff") depends on the session
    noticing the brief. Where a `DECIDE` line was present it was quoted 3/3; a brief without one was missed 5/5 when asked to quote it.
    V5's own instrument (one prompt, one answer) also showed that a single answer can deny text the session holds.
- **V6 PASS** (`v6.txt`): against the filing tree's tool (97cb6c1, run from a detached worktree so it reads its own activation map —
  a first run with a copy in the scratchpad differed in required_skills only, for that reason): `--dwell` text and JSON identical on the
  five registers at a fixed now (no cache, serial); `--all --json`, `--all`, `ECO-119 --json`, `ECO-124 --json` byte-identical;
  `bomdd-job`, `bomdd-run` and `dwell-session-hook` selftests exit 0; the hook on ViewTube warm 0.89, 0.83, 0.74 s (< 3 s).
  Self-conformance and CI: observed at the manufacture commit (below the commit, in the closure).

**Found while making.** The measurement scripts that load the tool start the dwell read's worker processes, which under Windows' spawn
import the calling script again — both scripts needed a main guard (and the mutant copies a folder on `sys.path`). Not a tool defect;
recorded so the next measurement does not lose time to it.

## /preflight receipt (start path: manual — the user's "起票に進む" read as the start artifact)

- **Classification**: filing of a decided change (the user's choice to file the wiring and the decide rule; filing only).
- **Baseline `7b648df`**: **confirmed** (HEAD, ECO-123 verified; the tree clean apart from this filing's files and ECO-119's untracked R8
  report, which this filing does not touch).
- **Next number 124**: **confirmed** (the last register entry and the last order are ECO-123; no `60-change-order-eco-124.md`).
- **The hooks that exist**: **confirmed** (section 0: no repository Claude hook; the user-level `PreToolUse` heredoc hook; git hooks under
  `bomdd/hooks/` in every repository).
- **The view's speed and size**: **confirmed** (`survey.txt` at the heads of 2026-11-04).
- **No ECO in progress on the same files**: **confirmed** for `bomdd-job.py` and the new script; **overlap noted** for
  `method/bomdd-playbook-v1.md` and `AGENTS.md`: ECO-119 (filed, not started) touches the playbook's §4.5 and §7, this ECO §8 only; ECO-119
  does not touch `AGENTS.md`.
- **Start decision**: **PROCEED_WITH_LIMITS** (filing only; manufacture waits for the start instruction, which also answers the two points
  of section 1).

## Converge receipt (the wiring and the decide rule; 起動経路: self-triggered at filing, DoD fixed first)

- 判定: 収束 (round 1 = 8 findings, round 2 = 3 new, round 3 = 0 new). The reviewer advisor was unavailable at filing (overloaded); the
  rounds are the producer's own.
- DoD:
  - ✔ D1 the view is seen without anyone remembering to run it, in every BomDD repository on the machine;
  - ✔ D2 what just stalled is told apart from the backlog, in a few lines;
  - ✔ D3 a failure is visible ("not measured"), never silence, never a blocked session;
  - ✔ D4 what to decide, by whom, and how its effect is measured, is written; the parts that are the user's are put to the user;
  - ✔ D5 no product file and no existing output changes;
  - ✔ D6 each part labelled stop, measure or none, and the limits declared.
- round 1 (8): (a) the full view at session start is 180 lines of backlog → a brief with a `DECIDE` line apart from the backlog; (b) "new
  since last session" needs stored state → "crossed in the last 7 days", derived; (c) a hook per repository needs product distributions
  and a machine path in checked-in files → one user-level entry calling a versioned script; (d) Codex and other harnesses have no Claude
  hook → declared, the manual entry in `AGENTS.md`; (e) a cold first run (≈ 40 s) at session start → a 75 s bound inside a 90 s hook
  timeout, "not measured" beyond it; (f) the hook failing silently would look like "nothing stalled" → one `not measured` line on every
  failure; (g) a stop on due decisions would block on the calendar → a text rule, measured by line 2; (h) the decide rule and the settings
  edit are the user's → put to the start instruction.
- round 2 (3 new): (i) the AI choosing withdraw or supersede by itself → only the human (P3); (j) installation not observable → `--check`
  and V4; (k) the hook's text reaching the session is a harness behaviour, not a test → V5 observes it in real sessions.
- round 3 (0 new): the parts checked against D1-D6 and against section 0's numbers.
- 未収束事項: none in the form. Declared outside it (section 2): other harnesses and machines, the decide rule as text, the cold first
  start, the brief's age within a session, the backlog itself. For the user at the start instruction: the rule of P3 and the settings edit.
