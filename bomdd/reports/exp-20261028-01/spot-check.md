# EXP-20261028-01 spot-check (three ECOs read by hand against baseline.py's output)

Chosen to cover the three record dialects: BomDD ECO-115 (English, six inspection rounds, six converge loops),
ViewTube ECO-VT-270 (review file, known defects, a receiving run), BomDD ECO-098 (Japanese `eco(NNN):` dialect).
Each metric: the script's value, what the record says (file and line or commit), and agree / disagree. Disagreements
were fixed in the script and the script re-run; what could not be fixed is listed as residual.

## BomDD ECO-115 (`bomdd/60-change-order-eco-115.md`)

| metric | script | record | result |
|---|---|---|---|
| 1 R8 rounds | 6: R7, R3, R1, R2, R2, A0 | §15 line 690: "r1 REJECT 7 → r2 REJECT 3 → r3 REJECT 1 → r4 REJECT 2 → r5 REJECT 2 → r6 ACCEPT", 15 findings | agree after D1 (first run: 5 rounds, r1 missing, because "loop 4 round 2" in a bold lead of §4 opened round 2) |
| 2 converge | 26→10 ; 10→5 ; 5→5 ; 8→4 ; 9→6 ; 9→3, cutoff | receipt loops 1-6, each "判定: 未収束 (round 軌跡: ...)"; adopted by the user's cut-off rulings (lines 3-15) | agree |
| 3 fix commits | 6 (35961c3, 2aa2d7d, 7eddaba, 11982a4, 460dc6b, 47b4df7); rework 5 | `git log`: `fix(eco-115)` manufacture + five repairs after r1-r5 | agree |
| 4 rulings | 7 distinct strings ("ECO-115を起票して", "ECO-115 を製造して", "ECO-115 をクローズして", "A", "2:A", "1:A 2:A 3:A", "only ruling-layer gaps") | by occasion about 15: "A" split, "A" extension, "2:A" narrowing, "1:A 2:A 3:A", "2:A" redesign, "A" loop 4 cut-off, "A" staged plan, "A" loop 5, "A" loop 6, filing, manufacture, "A" r3, "A" r4, "A" r5, closure | agree with the rule (distinct strings); **the rule undercounts by about half here** — one string "A" stands for nine occasions. Golden n/a: agree (method repository) |
| 5 known defects | unknown:NO_KD_STATEMENT | §15/§16: "15 findings, all resolved"; limits L1-L9 declared; no known defect named | agree with the rule (no statement); a reader would say 0 |
| 6 escapes | 0 | no later record attributes a defect to ECO-115 (ECO-116 distributes it) | agree |
| 7 elapsed | 7.0 h | filing `db16fa3` 10-26 06:39 → `ef1506a` 13:40 | agree |
| 8 receiving | n/a | not a receiving ECO | agree |

## ViewTube ECO-VT-270 (`bomdd/eco/ECO-VT-270.md`, `ECO-VT-270-independent-review.md`, register entry)

| metric | script | record | result |
|---|---|---|---|
| 1 R8 rounds | 2: R15, R8 | review line 24 "Verdict: REJECT" with R270-1-01..15; line 336 "Verdict: REJECT", R270-2-01..08 | agree |
| 2 converge | 15→7→5, cutoff | §7 line 8: "Judgement: not converged (round trajectory 15 → 7 → 5 ...) The user adopted it ... with "1:A"" | agree after D10 (first run: 15→7, a partial chain on the round 2 line) |
| 3 fix commits | 3 (bf095249, 10f3df09, b69aa2ed); rework 2 | `fix(eco-vt-270)`: equipment and process text, the delivery, `implemented` | agree with the rule; **rework 2 is not rework** — ViewTube's `fix(` marks steps (noted in definitions) |
| 4 rulings | 5 ("1:A 2:A 3:A", "B", "ECO-VT-270 の設計に進んでください", "1:A 2:a", "3:A") | 4 rulings: "1:A 2:A 3:A" (line 11), "B" (line 12), the design instruction (line 228), "1:A 2:a" (line 286); "3:A" at line 282 refers to point 3 of the first | **disagree (residual)**: first run gave 8; D9 removed three non-rulings ("rework: bind or narrow the row", ECO-VT-269's "2:a", "the one canonical full-suite run"); the "3:A" reference cannot be told from ECO-115's separate "2:A" by local text, so it stays. Golden n/a ("No golden (`ui_change: false`)"): agree |
| 5 known defects | 8 (KD-270-1..8) | §9: KD-270-1 to 8 named and accepted | agree |
| 6 escapes | 0 | ECO-VT-271 is filed for KD-270-1, a known defect carried, not an escape; R270-2-01 "which the repair of R270-1-03 introduced" is inside the ECO, before acceptance | agree |
| 7 elapsed | 1.7 h | `a1784b46` 10-27 22:31 → `33a2581e` 10-28 00:11 | agree |
| 8 receiving | 1 run, AB-ECO-VT-270-1 at 2026-10-27 22:50:03 +09:00 | `50-as-built.yaml` line 245 (`work_ref: ECO-VT-270`); `receive(eco-vt-270)` `82cabfe9` | agree |

## BomDD ECO-098 (`bomdd/60-change-order-eco-098.md`, Japanese dialect)

| metric | script | record | result |
|---|---|---|---|
| 1 R8 rounds | 3: R1, R1, A0 | §6.1 "REJECT IA-01"; §6.2 "REJECT IA-01 / IA-02" (a procedure error of the receiving side); §6.3 "ACCEPT", "所見なし" | agree (r2's IA-01 is a repeat, so 1 new) |
| 2 converge | 3→0→0, converged | line 56 "判定: 収束(round 軌跡: 3→0→0)" | agree |
| 3 fix commits | 2 (8d84edb 製造, ad9d836 是正); rework 1 | `eco(098): 製造 —`, `eco(098): 独立検査 r1 REJECT IA-01 の是正` | agree |
| 4 rulings | 1 ("A") | line 3 "user 2026-10-05 DECIDE「A」", line 50 the same ruling | agree; golden n/a agree |
| 5 known defects | unknown:NO_KD_STATEMENT | none named | agree with the rule |
| 6 escapes | 1 (ECO-100) | ECO-100 line 153: "ECO-098 の記載の誤り 1 件(本 ECO の対象)" — the rule ECO-098 wrote did not fit the second product | agree after the fix (first run: 0 — D6 had no correction wording; `の記載の誤り` / `を訂正` / `corrects` added, then a false positive in ECO-096 "ECO-092 r1 IA-03 の訂正後の文言" removed by requiring the correction word right after the id) |
| 7 elapsed | 0.6 h | `cf1852f` 10-05 11:13 → `a9063ff` 11:48 | agree |
| 8 receiving | n/a | | agree |

## Other disagreements seen while checking (outside the three, fixed)

- MoviePad-Remake ECO-004 known defects: 3 → 4 after D8 (accept commit `e45f4fa`: "four low known defects"; §6: R8-2-01 to R8-2-04).
- ViewPrism2 ECO-147 known defects: 3 → 2 after D8b (VP147-F1 was the repaired round-1 finding; known defects VP147-N1, N2).
- BomDD ECO-093 and ECO-094 R8 rounds: 1 (ACCEPT) → 0 (none_declared). The commit-subject fallback read
  `eco(091/093/094): ECO-091 独立検査 r1 ACCEPT ...`, which is ECO-091's round; a subject naming several ECOs is no
  longer read for rounds (ECO-089's single-ECO subjects still give its r1 REJECT, r2 ACCEPT).

## Residual (not fixed)

1. Rulings: distinct strings undercount repeated answers (ECO-115: 7 against about 15 occasions) and keep references
   to part of an answer (ECO-VT-270: "3:A"). Use the rulings column as an ordinal signal, not a count of occasions.
2. ViewTube fix-commit counts include step markers (`implemented`, the delivery), so `rework_fixes` overstates rework
   there; compare ViewTube with itself only.
3. Escape recall is not measured: the narrowed rule found 3 escapes in 92 ECOs (ECO-098, ECO-VT-220, ECO-VT-232),
   with ECO-VT-232 cited by two records. An escape written in other words is missed.
4. BomDD ECOs that record a product's trial or distribution are credited with the product's outcomes because their
   records report them: ECO-116's 2 R8 rounds (21, 8 findings) are ViewPrism2 ECO-148's (lines 194-195) and its 8
   known defects ViewTube ECO-VT-270's (line 231); ECO-107's round is ViewTube ECO-VT-256's R8 (line 103); ECO-110's
   "two known defects" are ViewPrism2 ECO-147's (line 3); ECO-097's round is the meaning inspection of ViewPrism2
   ECO-145 (line 146, "r1 **REJECT IA-01** → 是正 → r2 **ACCEPT**", of which only r1 is read: one marker per line).
   For the method repository, read the R8 and known-defect columns as "recorded in the ECO", not "of the ECO".
