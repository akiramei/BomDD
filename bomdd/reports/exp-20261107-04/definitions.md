# EXP-20261107-04 — definitions (fixed before any writer starts)

Fixed 2026-11-07, on the user's "1" (start with the pilot). A change after this point is a departure (section 7).

## 1. The question

BehaviorForge's author aims to use the kit as a checker of human-written upstream documents: to find where a specification is
weak, so that a weak upstream does not flow into the next process. EXP-20261107-01..03 compared *writing*; the lab's BF-GAP-01
(BehaviorModelLab `comparison_plans/spec_gap_review_v1/execution-02`) compared the kit's review step on six three-sentence
cases and reached a ceiling (4 of 4 holes in every run, with and without the scene-first step). The user supplied a longer
specification with ambiguities (`input/REQ-QC-001.md`, pasted 2026-11-07; its authorship is not checked).

**The question:** on REQ-QC-001, does a fresh reviewer given BehaviorForge find more of the holes that show only when sections
are read together than a fresh reviewer given a neutral request, without more unsupported findings?

This is a measurement. No method text, kit file or product changes. BehaviorForge is read and copied, never written.

## 2. The key

`key.md`: twelve cross-section holes X01-X12, each with the sections read together and the minimum a finding must say. Section
13's listed undecided items and the plain vague words are left out (any reviewer finds them). The key is given to no writer.

## 3. The pilot (a go / no-go, not a reading)

- One fresh writer (general-purpose agent, the session's default model) with `prompts/control.md` and the specification only,
  in a folder outside every repository; reading and writing its `out/` only; 30 minutes.
- Scored by me against `key.md`, item by item, with the quoted line for each item counted as detected. Not blind; it decides only
  whether a comparison has room.
- **Stop rule (fixed now):** if the pilot detects **10 or more of the 12**, the comparison has no room to show a direction with
  two writers per arm, and the experiment stops there with that result. If it detects 9 or fewer, the main run follows.

## 4. The main run (only if the pilot leaves room)

- **K:** BehaviorForge's `prompts/review.md` as on disk when packaged (hashed), its fields filled — target and version:
  REQ-QC-001 0.9; sources and the candidate under review: `REQ-QC-001.md` itself; common contract: `kit/docs/artifact-contract.md`;
  range: the whole document — followed by the boundary and delivery sections of `prompts/control.md`; the kit folder given.
- **C:** `prompts/control.md` unchanged.
- Two fresh writers per arm, started together; the pilot writer is not one of them.
- A fresh scorer with `key.md` and the four `out/` folders under shuffled labels (key hashed before it starts) marks each item
  detected / not, with a quote; and counts findings it judges unsupported by the text, and findings that give a concrete scene
  and at least two candidate results (answerable by the owner).
- **Readings** (per writer, never pooled, a direction only when the arms do not overlap): **R1** items detected (of 12);
  **R2** unsupported findings. Reported, not read: answerable findings, total findings, questions, time.

## 5. Limits

- The key is written by one reader of the same model family as the writers: a hole that reader cannot see is not in the key,
  so detection reads high. No owner's intent is available; an item is "undetermined by the text", not "wrong".
- One specification; its authorship is not checked.
- Two writers per arm in the main run, one model; no rate.
- BF-GAP-01's B arm added two things at once (the scene-first step and "record findings whether or not a question is needed");
  the kit's current `prompts/review.md` carries both, so K here tests the kit as distributed, not the step alone.

## 6. Order

1. File this folder with the ledger entry (commit; the push follows with the result).
2. The pilot; isolation by `../exp-20261030-04/isolation.py`; freeze its `out/`; score; the stop rule.
3. If it continues: package K and C, hash, four writers, freeze, scorer, readings, `results.md`.

## 7. Departures

(none yet)
