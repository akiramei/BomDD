# EXP-20261107-04 — results

Run 2026-11-07 on the user's "1", by `definitions.md` as filed in `dddd454` (departure D1 in its section 7). BehaviorForge was
not used (the experiment stopped at the pilot). Nothing was written outside this folder and the pilot's scratch folder.

## 1. The pilot

One fresh general-purpose writer with `prompts/control.md` and `REQ-QC-001.md` only (folder outside every repository, file
hash `15d6ec7a…` unchanged after); 203 s, 4 tool calls (Glob 2, Read 1, Write 2); the isolation tool flagged nothing; it
consulted the advisor once (D1). Frozen: `run-P1/review.md` (sha256 `441e9617…`, 24,449 bytes) — 20 cross-section findings
(A-1..A-20), 14 vague expressions (B), a section on section 13 (C), 27 questions (D).

## 2. Scored against the sealed key (not blind; a go / no-go)

| id | detected | where (`run-P1/review.md`) |
|---|---|---|
| X01 cancel has no state | yes | A-1: §3.2 の「取消」に対応する状態がない |
| X02 state after send-back | yes | A-1: 差し戻した後にどの状態へ戻るのか…決まっていない |
| X03 correction after approval → approval again | yes | A-5: 承認をやり直すのか(状態が戻るのか) |
| X04 re-test as new request or child | yes | A-7 |
| X05 deputy who performed the test | yes | A-4: 代理者が本人(試験実施者)になる場合に §6.2 の禁止が効くのか |
| X06 administrator's correction of approved data | yes | A-5 first point |
| X07 deletion recorded but not defined | yes | A-6 |
| X08 承認済 → 完了 | yes | A-1: 「承認済」と「完了」の違い…誰が何をするとその状態に移るのか |
| X09 change after start and entered results | yes (lenient) | A-14: 既に入った結果はどうなるのか (said of a change of item; "after start" implied by entered results) |
| X10 cancelled request in the duplicate check | yes | A-12: 取消済みの依頼を重複判定の対象に含めるか |
| X11 re-acquisition after manual entry | yes | A-10: 再取得したとき、前の値を上書きするのか、両方残すのか |
| X12 correction during review vs send-back | **no** | not found |

**11 of 12 detected (10 without the lenient X09).** Both are at or above the stop rule's 10.

## 3. Verdict by the fixed stop rule

**The comparison has no room; the experiment stops at the pilot.** A neutral reviewer without the kit found the cross-section
holes of this specification nearly all, so two kit writers could not show a direction over two such reviewers on this key.

## 4. Read after the verdict (descriptive)

- **The pilot went past the key.** Of its 20 cross-section findings, at least nine name holes the key does not hold, for
  example: the unit of state (request or test item, A-2), who receives a request before assignment (A-3), raw versus rounded
  values for judgement (A-9), the source of lot numbers when the link fails (A-11), the reading scope against hand-over and load
  balancing (A-13), the reference date for "delayed" (A-16), what the requester may see of results (A-17), migrated data as an
  official record (A-18), section 1.3's scope against the body (A-19). The key was the smaller list, so it limited, rather than
  inflated, what could be seen.
- **It separated findings from questions** (27 questions, each tied to a finding) and **flagged section 13's deferrals that
  are design inputs** — the two practices the kit's recent revision adds — without being asked to.
- With EXP-20261107-01..03 and the lab's BF-GAP-01, this is the fifth time the reviewer or writer without the kit reached the
  ceiling of the measure; here the measure was the kit author's stated aim (finding where a human-style specification is weak).

## 5. Limits

- The key was written by one reader of the same model family; holes that reader does not see are not in it.
- One specification of unknown authorship; one pilot run; scored by me, not blind.
- D1: the advisor's one consultation is part of the pilot's result.
- The stop says nothing about a specification whose holes a neutral reviewer misses; it says this one is not such a
  specification for the current model.

## 6. Files

`definitions.md`, `key.md`, `input/REQ-QC-001.md`, `prompts/control.md`, `run-P1/review.md`. The pilot's scratch folder
(`exp-20261107-04/P1` in the session's scratchpad, about 36 KB) is deleted on the user's word.
