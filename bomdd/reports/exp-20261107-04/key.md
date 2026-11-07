# EXP-20261107-04 — the sealed key (cross-section holes in REQ-QC-001)

Written 2026-11-07 from `input/REQ-QC-001.md` alone, before any writer starts; given to no writer. Each item is a scene whose
result the spec does not determine, or where two statements of the spec conflict, and which shows only when two or more
sections are read together. Items the spec itself lists as undecided in section 13 are left out (for example the final
judgement on a re-test), and so are the plain vague words ("適切に", "必要に応じて", "柔軟に"), which any reviewer finds.

**Counts as detected** when a finding names the scene (the operation and the state, role or data it meets) and says that its
result is undetermined or conflicting, in any words. Section numbers are not required. A general remark ("状態遷移が未定義",
"権限が曖昧") does not count for an item unless it names that item's scene; the column "must say" is the minimum.

| id | scene | sections read together | must say |
|---|---|---|---|
| X01 | Cancelling a request, in particular one already under test | 3.2 (cancel allowed, also when testing has progressed; "取消済み" requests), 4.1 (the state list has no cancelled state) | the state a cancelled request takes, or that cancellation is not in the state list |
| X02 | A result sent back by the reviewer | 6.1 (差し戻す), 4.1 (差戻し only as "必要となる") | which state a sent-back request returns to (or what happens next to it) |
| X03 | Correcting a result after approval | 5.3 (after approval, correction by the responsible person's judgement), 6.2 (approved = official record; approver recorded), 4.1 | whether a corrected approved result leaves 承認済 / needs approval again |
| X04 | Registering a re-test | 6.3 (re-test linked to the original result), 3.3 (duplicate prevention, re-test allowed as an exception), 3.1 (requests are registered by the manufacturing staff) | whether a re-test is a new request (who registers it, duplicate warning) or a child of the original |
| X05 | A deputy approves while the responsible person is absent, and the deputy performed the test | 2.2 (approval must not stall when the responsible person is absent), 6.2 (self-approval not allowed; small departments flexible) | the conflict or undetermined case between deputy approval and the self-approval ban |
| X06 | The administrator corrects data of an approved result | 2.2 (administrator may correct data as needed), 5.3 (approved results not changed in principle; correction by the responsible person), 8.2 (prevent tampering) | that the administrator's data correction conflicts with, or is not bounded by, the approval / tampering rules |
| X07 | Deleting a test result | 8.1 (history records 削除 of results), 3.2 / 5.3 (only cancel and correct are defined) | that deletion is recorded but no deletion operation (who, when, what) is defined |
| X08 | Moving from 承認済 to 完了 | 4.1 (both states listed), 6.2 / 6.3 (approval is the official record; final judgement later) | the condition, actor or meaning of 完了 as distinct from 承認済 |
| X09 | Changing a request after testing has started, e.g. adding a test item | 3.1 (items may be added or changed), 3.2 (change after start needs a procedure), 4.1 | what happens to the progress state (or to entered results) when items change after the start |
| X10 | Registering the same lot again after the earlier request was cancelled | 3.2 (cancelled requests hidden from normal lists), 3.3 (duplicate prevention by lot) | whether a cancelled request counts in the duplicate check |
| X11 | Re-acquiring a device result after it was entered by hand | 9.2 (re-acquire after a failure; manual entry allowed), 5.3 / 8.1 (correction and history) | which value stands, or whether the re-acquisition is a correction |
| X12 | The tester finds an input error while the result is under review | 5.3 (registered results may be corrected), 6.1 (reviewer sends back), 4.1 (確認中) | whether the tester may correct during review or a send-back is required |

Twelve items. The key's limits: written by one reader of the same model family as the writers, so a hole that reader does not
see is not here; no owner's intent is available, so an item is "undetermined by the text", not "wrong".
