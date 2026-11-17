# ECO-126 — GU7 after the independent inspector's last round (2026-11-17)

The inspector of another lineage (EQ-002, `gpt-5.6-sol`, `codex exec -s workspace-write` inside a scratch copy; briefs and reports
are beside this file) inspected the new check twice. **Both verdicts are REJECT.**

| Round | Verdict | Findings | What the producer did |
|---|---|---|---|
| 1 | REJECT | IA-01 to IA-08 (six false passes, one false fail, one self-test arm that embedded a false pass) | each reproduced as a self-test arm that was red on the unrepaired tool (7 arms), then repaired |
| 2 (the last) | REJECT | IA-01 to IA-07 closed; IA-08 not closed through IB-01; IB-01 (an empty member of a `touches_confirmed` list is dropped silently — introduced by the round-1 repair), IB-02 (a human ruling may name itself in `touches_confirmed`) | see below |

## What was done after the last round — and what that means

Two rounds are the limit for an independent inspection (the second is "correction confirmation and regression"). The default
for findings left by the last round is to **not** repair them and to show them at the stop as known defects.

**The producer departed from that default**: IB-01, IB-02 and one finding of the fresh-context review (a `touches_confirmed`
entry in status `ruled` whose `decided_by` is not `user` passed GU7) were repaired, each after an arm showed it red on the tool
the inspector saw (3 arms; the inspector's two ledgers are in `r2-ledgers/` and now exit 1 for the stated reason).

- **Why**: all three are measured false passes of a gate. The user's standing instruction of 2026-09-29 is that a measured
  false negative of a gauge is closed first, not left until it does harm.
- **What it costs**: the inspector has not seen this last repair. Round 2's own IB-01 was a defect introduced by the round-1
  repair, so an unseen repair can introduce another. The verdict of record stays **REJECT (round 2)**.
- **What the user decides at the stop**: accept GU7 as it stands with this repair uninspected, or have the inspector look a third
  time (a round beyond the limit is the user's to grant).

## State of the tool now

`python method/tools/ui-cad-gate.py --selftest`: 19 arms (15 known-bad, 4 known-good), exit 0. self-conformance C6c, C6d and
C6e run GU7's arms on every run. The inspector's own mutation check in round 2 (seven copies, each with one repair removed; every
copy's self-test failed and named the arm) covers the round-1 repairs. For the last three repairs the producer ran the same
kind of check itself (`../gu7_mutants.py`, output `../gu7-mutants-output.txt`): with each check disabled in a copy, the
self-test exits 1 and exactly its own arm is red. That is the producer's check, not the inspector's.
