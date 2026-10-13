# How often the AI stopped to ask the human for a ruling (2026-10-13, read-only)

**Purpose.** Count how often the AI asked the human for a ruling on something that closes inside the M-BOM or the Control Plan, using past session transcripts. Before guessing at causes (such as the AI avoiding responsibility), look at which procedure and which stop point each ask came from. Also look at whether the two model families (Claude and GPT) differ.

## The instrument (the same for both sources)

A turn-ending AI message (the last AI text before the human's next input) that contains 裁定待ち, 裁定が必要, 裁定をお願い, 裁定してください or gate①.
- Messages that only say there is nothing waiting for a ruling (裁定待ちはありません and the like) are excluded.
- Messages with the same text are counted once.

| Source | Products | Models (as recorded) | Period | Count |
|---|---|---|---|---|
| Claude Code transcripts | ViewTube 106, ViewPrism2 62, TimetableAdv 8 | claude-opus-5 99, claude-fable-5 47, claude-opus-4-8 23, claude-opus-5-5 5, claude-fable-5-1 2 | 2026-07-13 to 09-25 | 176 |
| Codex transcripts | TimetableAdv | gpt-6-astra 104 (high 95, medium 9), gpt-6.1-sol 20 | 2026-09-05 to 10-05 | 124 |

**A correction.** The first pass selected the Claude side by the `[DECIDE]` header, which was introduced on 09-11. That is a different instrument from the Codex side, and it dropped everything before 09-11. This version uses the same instrument on both sides. The classification of the 76 `[DECIDE]` messages, most of them from BomDD's method sessions, is kept in the appendix.

## How the messages were classified

**The classifiers.** Two classifiers, Claude Opus and Claude Sonnet, classified each message without seeing each other's results. They were not told the hypothesis. They were given the rule, playbook §4.5, and asked to apply it: from the derived side, only three kinds go back to the human (a new feature, a new promise, something not derivable).

**The classes:**
- **E**: CAD, requirements, specification, E-BOM, K-BOM.
- **M**: M-BOM, CP, Routing; how to make or inspect; the scope and order of manufacture; the choice of a fix option.
- **G**: acceptance.
- **P**: process, equipment, method.
- **W**: progress of work, including whether to start.
- **N**: asks for no ruling.

**What counts as a claim.** A number is claimed only where both classifiers agree. They agreed on the class for 151 of 176 Claude messages and 91 of 124 Codex messages.

## Results

**These numbers are a baseline from before the rule.** §4.5's rule came in with ECO-097 to ECO-102 (2026-10-05 and 06): the derived layer is not approved item by item, and only the three kinds go back to the human.
- The Claude data ends on 09-25 and the GPT data on 10-05.
- So "the AI could have decided" is the rule applied after the fact. It is not a count of violations.
- The question is therefore not whether the AI ignored the rule. It is whether the rule was wired into the procedures `eco-file`, `eco-fix` and `converge`. It was not (see below).

| | Claude (176) | GPT (124) |
|---|---|---|
| E side, rightly returned to the human (both classifiers: E, and the AI could not decide) | 30 (17%) | 61 (49%) |
| **M/W stops the AI could have decided** (both classifiers: could decide, and M or W) | **32 (18%)** | **28 (23%)** |
| of which **start-waits** (the design is settled; may manufacturing start?) | 19: stops on "裁定(gate①)は不要です。/eco-fix で着手できます" | 21: ECO-046's per-scene 着手裁定 |
| of which **derived-layer choices asked as rulings** | 7 (see below) | 7 (see below) |
| of which other progress checks | 6: whether to file; whether to add a small correction to a record | 0 |

**The 7 derived-layer asks on the Claude side:**
- a fix option asked as gate① (ViewPrism2 ECO-095, and the scope of a maintenance ECO, ECO-141);
- how to cut the scope of a repair;
- which mutants to run;
- the scope of the change surface.

**The 7 derived-layer asks on the GPT side:**
- how to repair its own master;
- the order of manufacture and inspection;
- observation plans (2 of them include an inspection budget);
- how to repair its own mapping table.

**What the two families share and where they differ:**
- **The shape is the same in both families.** Most avoidable stops are start-waits. Derived-layer choices were asked as rulings 7 times in each family.
- **The wording differs.** Claude says "no ruling is needed" and then stops, because the stop point of the `eco-file` procedure says so. GPT calls the same start-wait a 着手裁定 ("start ruling"). To the human, the latter looks like a ruling being asked on an M-side matter (inference).
- **The E-side share differs (17% against 49%).** This cannot be separated from the product (a game with many undefined CAD points) or from the period.
- **The human almost never rejected the recommendation:**
  - Claude, 32 stops: took it 23, rejected 1, unreadable 8;
  - GPT, 28 stops: took it 24, rejected 0, unreadable 4.

### After the rule (2026-10-06 to 10-12, Claude, 27 `[DECIDE]` messages)

From 09-11 the `[DECIDE]` header is mandatory in Claude sessions, so for this period the header is the right instrument. The two Claude measurements complement each other by period. Most of these 27 messages are ViewTube work (ECO-VT-250 to 255) done from BomDD sessions.

- **M asks.** Both classifiers called 0 of them M; one classifier alone called 2 M (how to repair rewrite D in ECO-VT-250).
- **What they are.** Mostly P (whether to file a repair to a validator, hook or qualification tool) and G (6 asks whether to set applied).
- **One repeated ask.** The same equipment repair's filing was asked three times running on 10-12, and the human pushed back. The AI itself had written that the data was enough for the repair. This is none of the three kinds. But the messages did not say whether ViewTube requires human approval for an inspection change, and the classifiers could not decide (unclear or no).

### What can and cannot be said about the models

- **Can be said.** No difference between families is visible in the share of avoidable stops (18% and 23%) or in their make-up (start-waits dominate in both).
- **Cannot be said.** Whether there is a family difference at all.
  - The model overlaps completely with the product, the period, the harness (Claude Code or Codex) and the copy of the procedures. GPT is TimetableAdv only, and gpt-6.1-sol covers only the scene-wiring period from 09-30.
  - Inside the Claude family the products also differ: ViewPrism2 21 of 62, ViewTube 10 of 106. ViewPrism2's stops come from a period with many `eco-file` start-waits, which again overlaps with the procedure.

## The procedures behind the stops (checked in the files)

1. **`eco-file` stops even when the AI has confirmed an implementation deviation.** It says "裁定は不要です。/eco-fix eco-NNN で是正に着手できます" and **stops** (template `method/templates/product-profile/skills/eco-file.md:35-37`; the ViewPrism2 and TimetableAdv copies are the same).
   - This is where the 19 Claude start-waits come from.
   - The exit for a problem that closes on the M side is not written at all; `:24` does not separate E-BOM from M-BOM.
2. **TimetableAdv's ECO-046 per-scene start ruling.** On 2026-09-20, ECO-046 switched to a policy of no longer making per-part rulings a routine step, and introduced a per-scene start ruling (`TimetableAdv/bomdd/60-change-order-eco-046.md:1223-1231`; `:1005` says 場面単位の着手裁定と成果物goldenは維持し).
   - This is where the 21 GPT start-waits come from.
   - Whether the human asked for a ruling per scene, or the AI introduced it, was not traced.
3. **The product change-management rule R4 names no layer.** R4 calls the human gate 裁定 "設計判断・選択肢選び" (`method/templates/product-profile/change-management.md:36`; TimetableAdv's copy is the same).
   - What the 7 + 7 derived-layer asks cite: gate① (2 on the Claude side), R3 (1 to 3, by classifier), R8 (1), `converge` with `eco-fix` (3 on the GPT side), `converge` (2), or nothing.
   - Step 2 of `eco-fix`, 是正の裁定, does not say who chooses. Step 6 of `converge` says to ask the points that need human judgement, with no layer named.
4. **ViewTube's diagnosis classes lump the layers together.** The class `requirements_bom_control` covers requirements, BOM and CP in one (`ViewTube/bomdd/process/process-transplant-policy.yaml:101-106`; 46 entries in the register).

## Limits

- **The splits inside the core are mine.** I split them by matching phrases, by ID range and, for the rest, by reading: start-waits 19, M side 7 and other 6; start rulings 21 and M side 7. The agreement of the two classifiers covers only the totals, 32 and 28. The classifiers split M/W on C129.
- **The model names are as recorded.** The user knows the models as GPT-5.6 Sol and 6 Astra; the transcripts record gpt-6.1-sol and gpt-6-astra. The version of Sol differs between the two.
- **"Could have decided" is the rule applied, not an independent judgement.** It was judged from the facts in each message only; the product records were not traced.
- **Counting scope and order as M is this measurement's reading.** §4.5's own text covers the content of the M-BOM, CP and Routing. The start-waits fall into M/W because of this reading.
- **Avoidable is measured against §4.5's rule.** Keeping the start command with the human is itself a matter of how much to delegate, and the human may decide it.
- **Not counted:**
  - asks without the instrument's words;
  - Codex messages in ViewTube (28) and ViewPrism2 (1), which were not classified;
  - BomDD's method sessions.

## Appendix: the 76 `[DECIDE]` messages (Claude, 2026-09-14 to 10-12, mostly BomDD method sessions)

- The classifiers agreed on the class for 65 of 76.
- Both classifiers called 0 of them M.
- Most were P (37 to 42), W (19) or G (12 to 13).
- Both classifiers judged 5 of them as decisions the AI could have made: whether to start a read-only measurement, whether to wait for other work to finish, and a split that rule R3 already decides.

## Where the evidence is

The extraction scripts and the classification results (JSON Lines) are in this session's scratch area. They are not copied into the repository, because they contain transcript text.

The follow-up is ECO-106 (`bomdd/60-change-order-eco-106.md`). It wires the rule into R4, `eco-fix` step 2 and `converge` step 6, and keeps the start-wait (user ruling A).
