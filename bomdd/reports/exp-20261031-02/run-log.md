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
- Repair committed as `cbcbf99` (the blobs of the two blind tools and `prepare.py` equal the hashes above). The leaked draft was
  written with CRLF and `.gitattributes` stores LF: its blob is `7264b920…`, which equals `3af0158b…`'s bytes with CRLF
  turned to LF (no lone CR).
- Fresh S2 author started 2026-10-31T12:20:23+09:00 with the watcher.
- Fresh author done in 654 s (29 tool calls): 21 entities, 179 attributes (83 with `set_by`, 96 derived), 29 relations,
  73 operation names (2 setting nothing), 9 questions, 5 attributes with an unknown initial; form OK with the blind tool.
  Draft `28440b94…` (kept as `s2/draft-r1.json`). Isolation: no read outside its folder; the same one-off write as the first
  author (`../reqs-dump.txt` in `exp07/`, deleted by itself, then `work/`). Its transcript has no trace of the tools' measured
  words. (The full tool, run by the operator only: form OK; its frame-rate rule selects six `OutputSettings` attributes, of
  which A1 counts only those with `set_by` — read at the measurement.)
- **A channel found while checking that transcript, older than this run:** the harness gives every subagent the repository's
  `CLAUDE.md` and the user's memory index (`MEMORY.md`). The index names `MoviePad-Remake` (3 times) and this series'
  experiment ids, and none of fps, frame rate, `SetFps` or 出力設定. Every agent of EXP-20261030-04, -05 and EXP-20261031-01
  had it too; none of their records name it. It does not name what A1 singles out; recorded as a limit, not repaired (the
  harness, not the folders, supplies it).
- Audit round 1: folder `exp07/s2-audit-r1` (prompt `ecee6464…`, draft `28440b94…`, blind tools, authority tree `bfef702c…`);
  auditor started 2026-10-31T12:32:07+09:00 with the watcher.
- Audit round 1 done in 596 s (45 tool calls): 12 findings, blocker 0 / material 6 / minor 6 (`s2/audit-r1.json`,
  `ff2628bd…`); the draft in its folder unchanged (`28440b94…`). Isolation: no read or write outside its folder (one flag,
  `d:\`, is the text `id:\|` of a grep pattern). Relayed 2026-10-31T12:42:26+09:00 as the file (same hash in the author
  folder), in the words of S1's round-1 relay.
- Author answered round 1 in 317 s: 12 fixed (`s2/answers-r1.json`, `3e0489ef…`); 23 entities, 196 attributes (88 with
  `set_by`), 32 relations, 11 questions; form OK. Draft `e9c620b5…` (`s2/draft-r2.json`). It added a top-level
  `operation_definitions` (all 81 operations: trigger, argument, effect, history entries) outside section 6's form and asked
  the operator whether that place is right; **not answered** (the operator does not rule on content) — the author also put
  it in `questions`, where the next auditor sees it. Isolation: unchanged (the earlier one-off write only).
- Audit round 2 (fresh auditor, revised draft only): folder `exp07/s2-audit-r2`, started 2026-10-31T12:48:13+09:00.
- Audit round 2 done in 923 s (48 tool calls): 10 findings, blocker 0 / material 1 / minor 9 (`s2/audit-r2.json`,
  `7ab801d8…`); draft in its folder unchanged. The material one: the export's content (the span left after trim and
  exclusion, the copy's real start, the progress denominator, REQ-085's totals and runs, REQ-086's path) is not in the model.
  Isolation: no read or write outside its folder (two `d:\` flags, the grep pattern `id:\|` again); no trace of the tools'
  measured words. Relayed 2026-10-31T13:04:00+09:00 as the file, in the words of S1's round-2 relay.
- Author answered round 2 in 223 s: 10 fixed (`s2/answers-r2.json`, `f36b266a…`); 25 entities (ExportRun, OutputFile added),
  217 attributes (92 with `set_by`), 36 relations, 13 questions; form OK. Draft `880a7e5b…` (`s2/draft-r3.json`). It removed
  one attribute (`PreviewPlayer.seekRetryCount`) and wrote its rule into an operation's definition instead.
- Audit round 3 (the last of the budget; fresh auditor, revised draft only): folder `exp07/s2-audit-r3`, started
  2026-10-31T13:08:17+09:00.
- Audit round 3 done in 775 s (46 tool calls): 8 findings, blocker 0 / **material 3** / minor 5 (`s2/audit-r3.json`,
  `eac4e8e6…`); draft in its folder unchanged (`880a7e5b…`). The three: what "resolve the selection again" does after a
  document change and after a playhead move (F-1); the internal timer drives playback whenever the external player is not
  playing, not only for the sample (F-2); the keyframe lookup returns 0 first when the trim start is 0 or less, before the
  online-only test (F-3; round 1's F-12 named the same function). Isolation: none outside (the `d:\` flag is the grep pattern
  again); no trace of the measured words. Not relayed.
- **Stop (definitions sections 4 and 10): S2 unconverged at the 3-round budget.** Blocker / material per round: 0 / 6,
  0 / 1, 0 / 3 (all findings 12, 10, 8). The draft at the stop is `s2/draft-r3.json` (`880a7e5b…`); not frozen. As in S1, each
  round's material findings are source behaviour the model does not yet state (here: selection rules, the timer's condition,
  a keyframe branch). Returned to the user 2026-10-31T13:21:42+09:00.
- **The user's ruling: "B: 以後も打ち切り"** (definitions section 12, departure 3) — S2 cut off as S1 was, and S3–S5 cut off at
  the budget without returning unless a blocker is open. Round 3 relayed 2026-10-31T13:57:09+09:00 as the file
  (`eac4e8e6…`, same hash in the author folder) in the words of round 2; the cut-off not told to the author.
- Author answered round 3 in 130 s: 8 fixed (`s2/answers-r3.json`, `171c77b7…`); counts and names unchanged (25 entities,
  217 attributes, 92 with `set_by`, 13 questions); form OK. Isolation unchanged.
- **S2 frozen** 2026-10-31T13:59:42+09:00 as `s2/domain-model.json` (`b758d626…`), the author folder's file copied unchanged
  (departure 3).

## Step 4 — S3 screens

- Author folder `exp07/s3-author` (`prepare.py author S3`): prompt `640a7490…`, requirements `24964b9d…`, model `b758d626…`,
  blind tools (`a6ae177f…`, `313cb523…`), authority tree `bfef702c…` (246 files). Author started 2026-10-31T13:59:42+09:00 with
  the watcher (the S2 freeze is committed while it runs; the frozen bytes are those hashed here).
- S2 freeze committed as `2d44f1f`. The model was written with CRLF: its blob is `ab7b91b6…`, the LF form of `b758d626…`.
- Author done in 586 s (43 tool calls): 10 screens, 171 elements, 4 `model_gaps`; form OK. Draft `3a4d692d…`
  (`s3/draft-r1.json`). Keyboard shortcuts are 13 `command` elements on the main screen; one element per operation (a control
  with several operations is split). Isolation: no read outside; the same one-off write as the S2 authors
  (`../model-summary.txt`), not left in `exp07/`. No trace of the measured words.
- Audit round 1: folder `exp07/s3-audit-r1` (draft `3a4d692d…`, blind tools, authority tree `bfef702c…`, 247 files); auditor
  started 2026-10-31T14:09:56+09:00 with the watcher.
- Audit round 1 done in 942 s (46 tool calls): 11 findings, blocker 0 / material 1 / minor 10 (`s3/audit-r1.json`,
  `0a29f87f…`); draft unchanged. The material one: the S key runs Split without the toolbar's `canSplit` test (the two use
  different tests near a boundary). Isolation: no flag; no trace of the measured words. Relayed 2026-10-31T14:26:03+09:00 as
  the file (same hash in the author folder).
- Author answered round 1 in 239 s: 11 fixed (`s3/answers-r1.json`, `751b490c…`); 10 screens, 171 elements, 5 `model_gaps`;
  form OK. Draft `6810d5ff…` (`s3/draft-r2.json`). Isolation: one more flag, `../10-requirements.yaml` from inside
  `authority/` (the folder's own file).
- Audit round 2 (fresh auditor, revised draft only): folder `exp07/s3-audit-r2`, started 2026-10-31T14:30:21+09:00.
- Audit round 2 done in 867 s (44 tool calls): 7 findings, blocker 0 / material 1 / minor 6 (`s3/audit-r2.json`,
  `24ee4c70…`); draft unchanged. The material one: the timeline's region label is placed against the drawing range's left
  edge, not the visible left edge (REQ-048). Isolation: one write outside (`../s3r2-summary.txt`, moved into its folder by
  itself), then one `ls ..`, which showed the other folders' **names** (no file in them was opened; the set-aside S2 folder's
  name ended in "leaked"). That folder is renamed `exp07/s2-author-0` so later agents do not see the word; no trace of the
  measured words. Relayed 2026-10-31T14:45:23+09:00 as the file.
- Author answered round 2 in 131 s: 7 fixed (`s3/answers-r2.json`, `89c77b7e…`); 12 screens (the two OS file dialogs added),
  174 elements, 7 `model_gaps`; form OK. Draft `bf151891…` (`s3/draft-r3.json`). Isolation: one more flag of the same kind
  (`../domain-model.json` from inside `authority/`).
- Audit round 3 (the last of the budget): folder `exp07/s3-audit-r3`, started 2026-10-31T14:48:16+09:00.
- Audit round 3 done in 997 s (57 tool calls): 7 findings, **blocker 0 / material 0** / minor 7 (`s3/audit-r3.json`,
  `80a4d5e6…`); draft unchanged. **S3 converged at round 3** (definitions section 4). Among the minors, F-6: the 16 event and
  startup operations have no element, so a change they cause (export progress, the keyframe's lead text, the first frame)
  cannot be written as a scenario step under section 6's form. Isolation: none outside (three relative paths from inside
  `authority/`). **One `Artifact` publish call** — the auditor tried to edit its own `audit.json` through it; the tool refused
  (only `.html` pages publish) and nothing was published; it then used `Edit`. No trace of the measured words. Relayed
  2026-10-31T15:05:37+09:00 as the file; the author answers every finding before the freeze (section 4).
- Author answered round 3 in 144 s: 7 fixed (`s3/answers-r3.json`, `6d3664b8…`); 12 screens, 175 elements, 8 `model_gaps`;
  form OK. **Unaudited changes in these answers that bear on A1's L1:** to make `shows` mean only what a part itself displays
  (F-3), the author set `shows: []` on 30 elements (title bar buttons and drag area, the 8 resize edges, the timeline's press,
  move, release, hover and leave elements and zoom buttons, the width / height focus and commit elements) and added one
  display element (`EL-TM-CURSOR`); it also added a `model_gaps` entry naming the 16 event and startup operations no part
  invokes, with two ways a scenario could handle them, choosing neither (F-6).
- **S3 frozen** 2026-10-31T15:08:47+09:00 as `s3/screens.json` (`f46ef7cb…`), converged at round 3, with the round-3 answers.

## Step 5 — S4 scenarios

- Author folder `exp07/s4-author` (`prepare.py author S4`): prompt `a892359d…`, requirements `24964b9d…`, model `b758d626…`,
  screens `f46ef7cb…`, blind tools, authority tree `bfef702c…` (247 files). Author started 2026-10-31T15:08:47+09:00 with the
  watcher.
- S3 record committed as `97e5ad4` (the screens blob equals `f46ef7cb…`).
- Author done in 1116 s (38 tool calls): 182 states, 128 scenarios (57 main, 71 alternate), 173 steps, 3 with `expect`
  `"unknown"`, 12 questions; form OK. 77 of 95 requirements cited; the 18 not cited are those no element and visible value can
  confirm (startup language, settings, the ffmpeg search, generation and caches, the exported file's content, appearance, the
  environment variables). Its rule for events: the `expect` of an asynchronous operation is the state when its synchronous
  part ends, and a state that exists only after an event is placed directly as an `in`; so export success, ffmpeg failure,
  download success and the thumbnails' arrival are in no step. It defined test fixtures (`talk.mp4` 60 s, 1280×720, 25 fps
  and others). Draft `ec33fb82…` (`s4/draft-r1.json`). Isolation: one one-off write outside (`../s4-reqs.txt`, not left in
  `exp07/`); one read of `~/.claude/projects/…/tool-results/bxu31tyd6.txt`, which is the harness's saved copy of its own
  long command output (its own tool result names that path). No trace of the measured words.
- Audit round 1: folder `exp07/s4-audit-r1` (draft `ec33fb82…`, 248 files); auditor started 2026-10-31T15:27:52+09:00.
- Audit round 1 done in 810 s (44 tool calls): 9 findings, **blocker 1** / material 3 / minor 5 (`s4/audit-r1.json`,
  `d7492688…`); draft unchanged. The blocker: UC-010's first step presses the track at x = 340, which is on a boundary, so the
  original starts a boundary drag, not a seek. Material: the zoom states leave `scrollOffset` unknown although the source
  decides it; 18 requirements uncited; a split behind the export dialog does not clear the cached keyframe. Isolation: one
  flag, `d:\s*`, a grep pattern; no trace of the measured words. Relayed 2026-10-31T15:41:55+09:00 as the file.
- Author answered round 1 in 234 s: 8 fixed, 1 question (F-3, the uncited requirements: checked at the unit / L2 / L3 levels
  their acceptance hints name, or may a state list attributes no screen shows — asked of a ruling; **not answered by the
  operator**, it stays in `questions`) (`s4/answers-r1.json`, `6ad91249…`). 188 states, 135 scenarios, 177 steps, 1 with
  `expect` `"unknown"`; 16 requirements uncited. Draft `968aa1bf…` (`s4/draft-r2.json`); form OK.
- Audit round 2 (fresh auditor, revised draft only): folder `exp07/s4-audit-r2`, started 2026-10-31T15:46:10+09:00.
- Audit round 2 done in 1052 s (64 tool calls): 6 findings, blocker 0 / material 3 / minor 3 (`s4/audit-r2.json`); draft
  unchanged. Material: the copy toggle on `talk.mp4` sets the copy start to 0.0 at once (not null); following the playhead on
  play start is synchronous, so REQ-046 can be a step; REQ-013 and REQ-094 can be written by fixing startup conditions, as
  REQ-010 was. **Isolation: it worked from `exp07/` and wrote 8 working files there** (dumps of the draft's states, screens
  and scenarios, a resx dump, 4 small scripts) and left them; no command names another step's folder. The operator moved them
  into `exp07/s4-audit-r2/stray-from-exp07/` so later agents do not find them. No trace of the measured words. Relayed
  2026-10-31T16:04:07+09:00 as the file.
- Author answered round 2 in 212 s: 6 fixed (`s4/answers-r2.json`, `c2c6b0a2…`); 207 states, 144 scenarios, 190 steps; 13
  requirements uncited (REQ-009, 051–055, 084–088, 092, 093); form OK. Draft `9f2d6c65…` (`s4/draft-r3.json`).
- Audit round 3 (the last of the budget): folder `exp07/s4-audit-r3`, started 2026-10-31T16:08:21+09:00.
- Audit round 3 done in 1053 s (51 tool calls): 6 findings, blocker 0 / **material 2** / minor 4 (`s4/audit-r3.json`,
  `540beda3…`); draft unchanged. The two: a title-bar press under the export dialog or About lands on the dialog's backdrop
  and closes it (UC-166, UC-203 expect nothing to happen). Isolation: none outside (relative paths from inside `authority/`);
  no trace of the measured words.
- **S4 unconverged at the budget** (blocker / material 1 / 3, 0 / 3, 0 / 2; all findings 9, 6, 6) with no blocker open, so
  **cut off under departure 3** without returning to the user. Round 3 relayed 2026-10-31T16:26:22+09:00 as the file.
- Author answered round 3 in 551 s: 6 fixed (`s4/answers-r3.json`, `79663eba…`), **not re-audited**. The two title-bar
  scenarios now press the dialogs' backdrops (UC-166, UC-203); REQ-009's visible part is cited by four scenarios. The answers
  also **added 7 scenarios no auditor has read** (UC-019 the ← key, UC-039, UC-077, UC-086 the volume slider's margin,
  UC-087, UC-112, UC-113; UC-113 sets the frame rate to 120 and then 30 fps) and changed 9 (UC-035 gains a 2x preset after
  the split; UC-103, 130, 131, 163, 166, 167, 180, 203), against the last audited `s4/draft-r3.json`. 221
  states, 151 scenarios, 206 steps, 13 questions; 12 requirements uncited (REQ-051–055, 084–088, 092, 093); form OK.
- Isolation of the author over the whole step: 16 flags, all its own one-off files — `../els.txt` written from
  `s4-author/` (it landed in `exp07/`; the operator moved it into `exp07/s4-author/stray-from-exp07/`), and `../q.txt`,
  `../chk.txt`, `../scenarios.json` from `s4-author/work/` (inside its own folder); one read of the harness's saved copy of
  its own output. No command names another step's folder; no trace of the measured words.
- **S4 frozen 2026-10-31T16:36:06+09:00** as `s4/scenarios.json` (`ef416e68…`), the author folder's file copied unchanged.

## Step 6 — S5 spec

- Author folder `exp07/s5-author` (`prepare.py author S5`): prompt `e2b63827…`, requirements `24964b9d…`, model `b758d626…`,
  screens `f46ef7cb…`, scenarios `ef416e68…`, template `45cc7a6b…`, blind tools, authority tree `bfef702c…`. Author started
  2026-10-31T16:37:54+09:00 with the watcher.
