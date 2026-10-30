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
