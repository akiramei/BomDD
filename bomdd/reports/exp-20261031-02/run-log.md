# EXP-20261031-02 — run log (stage A; started 2026-10-31 on the user's "A: 既定で始める")

The defaults of definitions section 3 were accepted as proposed.

## Step 1 — prompts and tools (before any agent)

- `check_upstream.py selftest`: PASS (23 cases: known-good forms, one broken fixture per form rule, the four links on two
  attributes, the totals, and an `"unknown"` value that does not check).
- `check_model.py` is EXP-20261031-01's, copied unchanged (`check_upstream.py` imports it).
- `prepare.py prompt-check`: PASS for all 12 prompts (positive control: the excluded pattern matches "output fps",
  "フレームレート", "SetFps", "出力設定", "MoviePad-Remake", "実験", "frame rate").
- **How the prompts phrase section 3's scope:** "the whole application, every screen named, except the preview's video rendering
  and playback timing (what the preview shows as values is in)". MoviePad-Remake's REQ scope plus every screen covers every
  function the screens offer, so the two are read as the same scope; recorded here because the words differ.
- **The authority archive** (`prepare.py authority`) is MoviePad `126eae9` by `git archive` without `bomdd-kit/`, `.claude/`,
  `.github/`, `AGENTS.md`, `CLAUDE.md` and `bomdd.lock`: the method kit and the agent-instruction files are not the product's
  manual, records, source or behaviour (section 3's list), and they tell an agent to read elsewhere. 245 files in the S1 folder
  including the tools, prompt and template.
- Staging root: `<scratchpad>/exp07/`; disk free before the run 168 GB.

## Step 2 — S1 requirements

- Author folder `exp07/s1-author` (built at step 1 from the committed files): prompt `db05b885…`, template `9f6a5361…`,
  `check_upstream.py` `207fc7e5…`, `check_model.py` `506d04d6…`, authority tree `bfef702c…` (245 files in the folder).
- Author started 2026-10-31T05:19:43+09:00; liveness watcher (60 min bound, 30 min silent) started with it.
- Author done in 893 s (41 tool calls): 91 requirements (REQ-001..091; must 83, should 6, could 2; core 82, surface 9; 19
  unresolved questions, 4 blocker; 1 needs-refinement, REQ-091 visual tolerance). Draft `7fbc8d89…`. The author kept two working
  files (`gen_reqs.py`, the YAML's generator; `resx-dump.txt`).
- Audit round 1: folder `exp07/s1-audit-r1` (prompt `2a94b78e…`, draft `7fbc8d89…`, authority tree `bfef702c…`); auditor started
  2026-10-31T05:34:53+09:00 with the watcher.
- Audit round 1 done in 1082 s (54 tool calls): 20 findings, blocker 0 / material 10 / minor 10 (`s1/audit-r1.json`,
  `2396c9d9…`). Relayed 2026-10-31T05:53:15+09:00 as the file itself (`audit-r1.json` placed in the author folder, same hash), the author asked to
  answer each in `answers-r1.json`.
- Author answered in 466 s: 20 fixed, 0 rejected, 0 question (`s1/answers-r1.json`); 94 requirements (REQ-092..094 added at
  the end); draft `0a6a9bfd…`.
- Audit round 2 (a fresh auditor, the revised draft only; no earlier findings given): folder `exp07/s1-audit-r2`, started 2026-10-31T06:01:20+09:00.
- Audit round 2 done: 16 findings, blocker 0 / material 3 / minor 13 (`s1/audit-r2.json`). Relayed 2026-10-31T06:19:04+09:00 as the file.
- Author answered round 2: 16 fixed (`s1/answers-r2.json`); 94 requirements; two blocker questions now open (REQ-058, REQ-060:
  whether pressing the speed or volume slider records an undo step depends on the running app, not the source).
- Audit round 3 (the last of the budget; fresh auditor, revised draft only): folder `exp07/s1-audit-r3`, started 2026-10-31T06:26:42+09:00.
- Audit round 3 done in 656 s: 16 findings, **blocker 1** / material 7 / minor 8 (`s1/audit-r3.json`, `b882e40b…`). The blocker
  is the author's own round-2 question (REQ-058 / REQ-060: does pressing the speed or volume slider record an undo step — the
  source cannot settle it, the running app can). Not relayed.
- **Stop (definitions sections 4 and 10): S1 unconverged at the 3-round budget.** Blocker / material per round: 0 / 10, 0 / 3,
  1 / 7 (all findings 20, 16, 16). The draft at the stop is `s1/draft-after-r2.yaml` (`efb48461…`, 94 requirements); not frozen.
  Of round 3's eight blocker or material findings, six name a requirement the author changed in round 2 (an id overlap, not a
  reading of cause); REQ-048 (the timeline's drawing) is named in all three rounds. Returned to the user 2026-10-31T06:38:43+09:00: cut off, extend or
  stop.
- **The user's ruling: "A: 打ち切って進む"** — the author answers round 3 with no re-audit, S1 is frozen, and the slider
  question (REQ-058 / REQ-060) goes on to the next stages as an open question. Round 3 relayed 2026-10-31T11:35:06+09:00 as the
  file (`audit-r3.json`, `b882e40b…`, same hash in the author folder) in the same words as round 2; the cut-off was not told to
  the author, so its treatment of round 3 is the same as of rounds 1 and 2.
- Author answered round 3 in about 640 s (45 tool calls): 16 fixed, 0 rejected, 0 question (`s1/answers-r3.json`,
  `4ecedc4e…`); 26 requirements changed and REQ-095 added (the overlays cover the whole window). 95 requirements (must 86,
  should 6, could 3); 18 unresolved questions, all minor, none blocker.
- **How the round-3 blocker was carried:** the author did not leave it as a blocker. REQ-058 / REQ-060 now state a behaviour —
  dragging the thumb or pressing the track records nothing, so the next undo also reverts the operation recorded before; only
  a press on the transparent margin records — and name as their source "Avalonia 12.0.0's default pointer handling", which the
  author says it did not read (the framework's source is outside the folder). The question stays open as
  `UQ-REQ-058-001` (minor), to be checked at L2 against the running app. The same form (a library default not read, an open
  minor question) carries REQ-083 / REQ-014 (an exception in the export command ends the application). Neither was audited.
- **S1 frozen** 2026-10-31T11:46:07+09:00 as `s1/10-requirements.yaml` (`24964b9d…`), the author folder's file copied
  unchanged (definitions section 12, departure 1). Committed as `535486e` (the blob's hash equals the frozen file's).

## Step 3 — S2 domain model

- Author folder `exp07/s2-author` (`prepare.py author S2`): prompt `3bc40d44…`, requirements `24964b9d…`, `check_upstream.py`
  `207fc7e5…`, `check_model.py` `506d04d6…`, authority tree `bfef702c…` (245 files). Author started with the watcher.
- Author done in 777 s (33 tool calls): 22 entities, 109 attributes (70 with `set_by`), 63 operations, 12 questions; form OK.
  **Its report said it had read the checker's frame-rate rule** and reworded three attribute descriptions
  (`EditSession.edited`, `History.undo_depth`, `ExportSession.copy_cut_start`) and dropped a quoted note so that the rule
  selects `OutputSettings.fps` alone. Its transcript has the rule or the `output_frame_rate` count in 8 tool results.
  Isolation: no read outside its folder; one write outside it (`../reqs_brief.txt`, in `exp07/`), deleted by the author itself
  and rewritten under `work/`.
- **Stopped and repaired (definitions section 12, departure 2).** What each agent saw (tool results containing any of
  `EXP-2026`, `chain count`, `frame_rate`, `SetFps`, `FPS = re`, `output_frame_rate`): the S1 author and the round-3 auditor saw
  the tools' source (the docstring naming this experiment, `chain`, `frame_rate`); the round-1 and round-2 auditors also saw
  `check_model.py`'s `FPS` rule (`head` of the file); the S2 author all of these and the printed count. No S1 finding or answer
  singles out the output frame rate as examined (its mentions are the frame grid, the source rate and `OutFps` not re-running
  the copy start). S1 stays as frozen; the exposure is a limit of S1.
- The leaked draft: `s2/draft-leaked.json` (`3af0158b…`; its generator `work/build_model.py` `d4a7983b…` stays in
  `exp07/s2-author-leaked/`). Not audited, not used.
- Blind tools: `blind/check_model.py` `313cb523…`, `blind/check_upstream.py` `a6ae177f…` (selftests PASS);
  `equiv_blind.py` `b5b22809…`: 27 of 27 cases equal, every broken arm caught; negative control (a blind copy without the
  `set_by` list check) FAIL as it should. `prepare.py` `817818bd…` copies the blind pair; `prompt-check` PASS for the 12
  prompts and the 2 blind tools (positive control: the full tools match `EXP-2026`, `SetFps`, `chain`, `fps`, `frame rate`, …).
- Carried for the fresh author to raise, not told to it: the first author noted that `Region` is plural, so `Region.speed` in a
  `shows` list does not say which region (a section 6 form question; decided only if a fresh author or auditor raises it).
- Fresh author folder `exp07/s2-author` (rebuilt): prompt `3bc40d44…`, requirements `24964b9d…`, `check_upstream.py`
  `a6ae177f…`, `check_model.py` `313cb523…`, authority tree `bfef702c…` (245 files); 0 matches of `fps`, `frame rate`, `chain`
  or `EXP-2026` in its tools.
