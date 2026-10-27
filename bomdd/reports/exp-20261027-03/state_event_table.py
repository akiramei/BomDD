#!/usr/bin/env python3
"""EXP-20261027-03, side measurement 1: ViewTube's delivery lifecycle as a state x event table, and its undefined cells.

  python bomdd/reports/exp-20261027-03/state_event_table.py > bomdd/reports/exp-20261027-03/state-event-table.md

The cells below are the measurement: one reading of the prose, made by hand and written down here so that it can be
re-read and disputed cell by cell. The script only renders them and counts them; it reads no repository.

The prose read (ViewTube, read-only, at 33a2581efac99998f680c51ed0dc4362186c60a4, ECO-VT-270 applied):
- `bomdd/process/change-management.md` section 4 (lifecycle and commits) and section 6 (deliveries and the advance
  decision), with R3/R4 where section 6 points to them, and AGENTS.md rule 12's six options;
- `.agents/skills/eco-receive/SKILL.md` (section 6 item 7 names it as the receiving procedure; its exit table and
  preconditions are part of the receiving step).
Section 6 at 33a2581e is the text of bf095249, the only ECO-VT-270 commit to the file; the real commits replayed the
scripts R8 round 2 reviewed (the review file, line 12), so it is the text KD-270-2 to 8 are defects of. Other skills
(eco-file, eco-fix, eco-accept, cad-mock) are not part of the prose read; they are used only to place the known defects.

Classes:
- D   defined: the prose says whether the event is allowed in the state and what follows (a state, an action, or a refusal).
- KL  forbidden by the prose and stated as unenforced (section 6 item 6's known limit); what follows a violation is not said.
- C   defined, but another rule of the same prose gives a different answer for the same cell.
- U   undefined: the event can occur in the state and the prose does not say whether it is allowed or what follows.
      Flags: `caught` = a later check the prose names (item 9 at accept) would stop the result; `borderline` = a
      closed-world reading of the prose's order (only the listed transitions are allowed) would answer the cell.
- I   impossible: the event cannot occur in the state (no delivery, no lock, no stop, already decided, ...).
- N   not applicable: a commit naming an applied or superseded ECO; section 4 ends the lifecycle there.
"""
import sys

STATES = [
    ("S1", "filed (staged, no issue)"),
    ("S2", "issued, lock open, no delivery after the newest issue"),
    ("S3", "delivered, not received"),
    ("S4a", "received: advances"),
    ("S4b", "received: holds, every non-passing row violation"),
    ("S4c", "received: holds with unmeasurable or no-check, or a launcher failure"),
    ("S4d", "received: input-defect"),
    ("S5", "receipt failed after its run (exit 5): no entry, run spent, evidence kept untracked"),
    ("S6", "held (the user chose hold; the lock stays)"),
    ("S7", "bound-reached (stopped for the user)"),
    ("S8", "implemented (records-only implemented fix)"),
    ("S9", "applied"),
    ("S10", "superseded"),
]

EVENTS = [
    ("bom", "bom (M-BOM or Control Plan)"),
    ("issue", "issue (the first)"),
    ("reissue", "re-issue"),
    ("fix", "fix changing a product path"),
    ("emptyfix", "empty fix"),
    ("implfix", "records-only implemented fix [added: reaches S8]"),
    ("ownprobe", "own probe/cad commit to a product path [added]"),
    ("rx0", "receive exit 0 (entry written)"),
    ("rx3", "receive exit 3 (already decided)"),
    ("rx4", "receive exit 4 (no delivery)"),
    ("rx26", "receive exit 2 or 6 (usage, linked worktree)"),
    ("rx5b", "receive exit 5 before the run"),
    ("rx5a", "receive exit 5 after the run"),
    ("rx7", "receive exit 7 (application running)"),
    ("r12cont", "rule 12: continue"),
    ("r12retest", "rule 12: exact retest"),
    ("r12hold", "rule 12: hold"),
    ("r12rework", "rule 12: rework"),
    ("r12abort", "rule 12: abort"),
    ("r12cond", "rule 12: conditional acceptance"),
    ("release", "the user releases the lock (item 6) [added]"),
    ("accept", "accept"),
    ("oprod", "other ECO commits: product path"),
    ("obom", "other ECO commits: M-BOM or Control Plan"),
    ("ocad", "other ECO commits: CAD (bomdd/ui/mock/)"),
    ("onamed", "other ECO commits, named by a rule 12 decision"),
    ("orec", "other ECO commits: records only"),
]
# The task's list plus three columns: the implemented fix (the task lists `implemented` as a state, and nothing else reaches
# it), the ECO's own probe/cad commits (item 4's sequence holds both kinds; added after reading KD-270-3, so its cells are
# marked as prompted by a known defect), and the user's release of the lock (item 6 names it as a way the lock ends).
PROMPTED_BY_KD = {"ownprobe"}

AGENT = ["bom", "reissue", "fix", "emptyfix", "implfix", "ownprobe"]
RECEIVE = ["rx0", "rx3", "rx4", "rx26", "rx5b", "rx5a", "rx7"]
R12 = ["r12cont", "r12retest", "r12hold", "r12rework", "r12abort", "r12cond"]
OTHER = ["oprod", "obom", "ocad", "onamed", "orec"]

GAPS = {
    "G1": ("a receipt that failed after its run keeps an entry-less evidence folder; the prose gives the next receipt of the "
           "same entry no rule for it", "R270-2-01 (KD-270-1)", "filled at 44bd91d0 (ECO-VT-271: exit 8 refuses the receipt "
           "while the folder exists; the folder must leave first, the user decides)"),
    "G2": ("an all-violation hold whose violation the ECO's diff did not cause: item 8.5 sends it to a product fix in this "
           "ECO, R3 forbids that", "R270-2-05 (KD-270-5)", None),
    "G3": ("accept when the sweep reports a finding on an earlier applied ECO: item 9 requires 0, eco-accept says record it "
           "in the cheat log, and the instrument cannot acknowledge it", "R270-2-02 (KD-270-2)", None),
    "G4": ("the ECO's own probe or cad commit to a product path after its delivery: not a delivery (item 3), not addressed; "
           "item 9's diff stops this ECO's accept, the sweep does not see it for others", "R270-2-03 (KD-270-3)", None),
    "G5": ("the records-only implemented fix before an advancing receipt: item 4 orders it after `advances`, nothing says "
           "what an early one does; item 9 stops the accept", None, None),
    "G6": ("how long a rule 12 permission for a named other ECO lasts once the stop that granted it is left (re-delivery, "
           "a new receipt, implemented)", None, None),
    "G7": ("the lock released by the user's disposition without ending the ECO (item 6): no state for an issued ECO whose "
           "lock is closed; whether its later commits need a re-issue first (the issue is what writes `open`) is not said",
           None, None),
    "G8": ("continuing past a bound: R4 stops the work at a bound and keeps the choice with the user, but nothing says "
           "whether continue, exact retest or rework raises the bound (a re-issue with a new bounds line?) or the next "
           "decision is bound-reached again", None, None),
    "G9": ("an empty fix outside its two named uses (exact retest, a route carried by a bom or re-issue): after `advances` "
           "it makes a new delivery and a new canonical run, and the newest entry governs item 9; on an all-violation hold "
           "it is the agent taking the user's exact retest", None, None),
    "G10": ("re-opening an implemented ECO: item 4 sends a later finding back to manufacture, section 4 has no transition "
            "from implemented back to staged; item 9 stops the accept", None, None),
}

# cells: state -> event -> (class, note, gap, flags). flags: "caught", "borderline", "r1:<finding>" (defined because
# R8 round 1 found it; the pre-repair text exists only in the deleted scratch clone, so this is read from the finding)
C = {s: {} for s, _ in STATES}


def put(state, events, cls, note, gap=None, flags=()):
    for e in ([events] if isinstance(events, str) else events):
        assert e not in C[state], (state, e)
        C[state][e] = (cls, note, gap, tuple(flags))


LOCKED = ["S2", "S3", "S4a", "S4b", "S4c", "S4d", "S5", "S6", "S7", "S8"]
STOPS = ["S4c", "S4d", "S5", "S6", "S7"]
DECIDED = ["S4a", "S4b", "S4c", "S4d", "S6", "S7"]

# ---- S1 filed
put("S1", "bom", "D", "item 4: a bom before the issue")
put("S1", "issue", "D", "item 4: the issue writes the work order and opens the lock -> S2")
put("S1", "reissue", "I", "no issue yet")
put("S1", "fix", "D", "item 4: product-path commits before the issue are allowed and measured with the delivered tree; "
                      "item 3: not a delivery (no issue)")
put("S1", "emptyfix", "D", "item 3: not a delivery before an issue")
put("S1", "implfix", "U", "a delivery ECO turned implemented before any issue", "G5", ["caught"])
put("S1", "ownprobe", "D", "item 4: CAD and probes before the issue")
put("S1", RECEIVE, "D", "eco-receive preconditions refuse (no delivery, no lock); run anyway, exit 4")
put("S1", R12, "I", "no stop")
put("S1", "release", "I", "no lock")
put("S1", "accept", "D", "item 9 refuses a delivery ECO with no deciding entry")
put("S1", OTHER, "I", "this ECO holds no lock")

# ---- S2 issued, locked
put("S2", "bom", "D", "item 4: a BOM change during the work goes through a bom and a re-issue before the delivery")
put("S2", "issue", "I", "already issued (a second issue is a re-issue)")
put("S2", "reissue", "D", "item 4 and the route table -> S2 with a new frozen revision")
put("S2", "fix", "D", "item 3: the delivery -> S3")
put("S2", "emptyfix", "D", "item 3 and item 10: an empty fix after the issue delivers the tree -> S3")
put("S2", "implfix", "U", "implemented with no delivery", "G5", ["caught"])
put("S2", "ownprobe", "D", "item 4: probes and manufacture after the issue")
put("S2", RECEIVE, "D", "eco-receive preconditions refuse (no delivery); run anyway, exit 4")
put("S2", R12, "I", "no stop")
put("S2", "release", "I", "no stop")
put("S2", "accept", "D", "item 9 refuses (no deciding entry)")

# ---- S3 delivered
put("S3", "bom", "D", "item 4: a finding after the delivery goes back to manufacture; bom and re-issue before the new delivery")
put("S3", "issue", "I", "already issued")
put("S3", "reissue", "D", "item 3: no delivery after the newest issue -> S2")
put("S3", "fix", "D", "item 4: a new delivery with R7 and R8 repeated -> S3 (the earlier delivery is never decided)")
put("S3", "emptyfix", "D", "item 3: a new delivery of the same tree -> S3")
put("S3", "implfix", "U", "implemented before the receipt", "G5", ["caught"])
put("S3", "ownprobe", "U", "after the delivery", "G4", ["caught"])
put("S3", "rx0", "D", "item 7 -> S4a/S4b/S4c/S4d/S7 by the result")
put("S3", "rx3", "I", "not decided")
put("S3", "rx4", "I", "the delivery exists")
put("S3", "rx26", "D", "eco-receive: nothing written, report and stop")
put("S3", "rx5b", "D", "eco-receive: no entry, nothing run, the next step is the user's (rule 12)")
put("S3", "rx5a", "D", "item 7 and eco-receive: run and logs retained, no entry -> S5", flags=["r1:R270-1-03"])
put("S3", "rx7", "D", "eco-receive: ask the user to close the application, then receive")
put("S3", R12, "I", "no stop")
put("S3", "release", "I", "no stop")
put("S3", "accept", "D", "item 9 refuses (no deciding entry)")

# ---- S4a advances
put("S4a", "bom", "D", "item 4: a finding after the delivery goes back to manufacture (bom, re-issue, new delivery)")
put("S4a", "issue", "I", "already issued")
put("S4a", "reissue", "D", "item 4: as for bom -> S2")
put("S4a", "fix", "D", "item 4: a new delivery, R7 and R8 repeated -> S3")
put("S4a", "emptyfix", "U", "an exact retest of an advancing delivery", "G9")
put("S4a", "implfix", "D", "item 4: after R9 and the swap -> S8")
put("S4a", "ownprobe", "U", "after the delivery", "G4", ["caught"])
put("S4a", "release", "I", "no stop")
put("S4a", R12, "I", "no stop")
put("S4a", "accept", "D", "section 4: lifecycle enforcement, implemented comes first")

# ---- S4b all-violation hold
put("S4b", "bom", "D", "item 4's general rule (bom, re-issue, new delivery); item 8.3 for a ruling-layer candidate")
put("S4b", "issue", "I", "already issued")
put("S4b", "reissue", "D", "as for bom")
put("S4b", "fix", "C", "item 8.5: product-fix re-delivery without the user; R3 forbids it when the violation is not the "
                       "ECO's", "G2")
put("S4b", "emptyfix", "U", "the agent's own exact retest", "G9", ["borderline"])
put("S4b", "implfix", "U", "implemented on a hold", "G5", ["caught"])
put("S4b", "ownprobe", "D", "item 8.5: the factory's probe for the held violation comes first (R5)", flags=["r1:R270-1-05"])
put("S4b", R12, "D", "item 8.5: a probe that does not fail sends the hold to item 8.2 (rule 12's options; row S4c)",
    flags=["r1:R270-1-05"])
put("S4b", "release", "I", "no user stop on item 8.5's main branch (the probe branch is row S4c)")
put("S4b", "accept", "D", "item 9 refuses (the newest entry holds)")

# ---- the rule 12 stops, the hold and the bound
for s in ("S4c", "S4d"):
    put(s, AGENT, "D", "item 8.2: rule 12's stop, execute only the authorised next action")
    put(s, "issue", "I", "already issued")
    put(s, ["r12cont", "r12retest", "r12hold", "r12rework", "r12abort"], "D",
        "item 8 rule 12's options (AGENTS.md rule 12 lists them for every stop)")
    put(s, "r12cond", "D", "3:B: ECO-VT-270's own deliveries only; for every later ECO a new delivery decided afresh")
    put(s, "accept", "D", "item 9 refuses (no advancing entry)")
put("S4c", "release", "U", "item 6 names the user's disposition of a hold that releases the lock", "G7")
put("S4d", "release", "U", "item 6 names a hold or a bound-reached, not an input-defect", "G7", ["borderline"])

put("S5", AGENT, "D", "eco-receive: what happens next is the user's (rule 12)")
put("S5", "issue", "I", "already issued")
put("S5", ["rx0", "rx5a"], "U", "the user-authorised rerun: same entry id, the kept folder already there", "G1")
put("S5", "rx3", "I", "not decided (no entry)")
put("S5", "rx4", "I", "the delivery exists")
put("S5", ["rx26", "rx5b", "rx7"], "D", "eco-receive's exit table, as in S3")
put("S5", ["r12cont", "r12retest", "r12rework"], "U", "each leads to a new receipt of the same entry", "G1")
put("S5", ["r12hold", "r12abort"], "D", "rule 12: the lock stays / superseded")
put("S5", "r12cond", "D", "no entry to admit; refused for every later ECO (3:B)")
put("S5", "release", "U", "item 6 names a hold or a bound-reached, not a failed receipt", "G7", ["borderline"])
put("S5", "accept", "D", "item 9 refuses (no entry)")

put("S6", AGENT, "D", "rule 12 hold: the work waits")
put("S6", "issue", "I", "already issued")
put("S6", R12, "D", "item 6: the user's later disposition of the hold")
put("S6", "release", "U", "item 6 names it; the resulting state is not described", "G7")
put("S6", "accept", "D", "item 9 refuses")

put("S7", AGENT, "D", "item 8.1 and R4: stop for the user")
put("S7", "issue", "I", "already issued")
put("S7", ["r12cont", "r12retest", "r12rework"], "U", "what the next decision does at the bound", "G8")
put("S7", ["r12hold", "r12abort"], "D", "the lock stays / superseded (item 6)")
put("S7", "r12cond", "D", "R4: a held individual is not presented as an acceptance candidate")
put("S7", "release", "U", "item 6 names it; the resulting state is not described", "G7")
put("S7", "accept", "D", "item 9 refuses; R4")

for s in DECIDED:
    put(s, "rx0", "I", "already decided (exit 3 first)")
    put(s, "rx3", "D", "eco-receive: nothing written, report and stop")
    put(s, "rx4", "I", "the delivery exists")
    put(s, "rx26", "D", "eco-receive: nothing written, report and stop")
    put(s, ["rx5b", "rx5a", "rx7"], "I", "the decided check comes before the application check and the run")

# ---- S8 implemented
put("S8", ["bom", "reissue", "fix", "emptyfix"], "U", "a finding after implemented", "G10", ["caught"])
put("S8", "issue", "I", "already issued")
put("S8", "implfix", "I", "already implemented")
put("S8", "ownprobe", "U", "after the delivery", "G4", ["caught"])
put("S8", RECEIVE, "D", "eco-receive preconditions refuse (the register is not staged)")
put("S8", R12, "I", "no stop")
put("S8", "release", "I", "no stop")
put("S8", "accept", "C", "item 9's report-0 against eco-accept's cheat-log record", "G3")

# ---- closed
for s in ("S9", "S10"):
    put(s, AGENT + ["issue"], "N", "a commit naming a closed ECO")
    put(s, RECEIVE, "D", "eco-receive preconditions refuse (the register is not staged, no lock)")
    put(s, R12, "I", "no stop")
    put(s, "release", "I", "no lock")
    put(s, "accept", "I", "closed")
    put(s, OTHER, "I", "the lock has ended")

# ---- other ECOs during this ECO's lock
for s in LOCKED:
    put(s, ["oprod", "obom", "ocad"], "KL", "item 6: forbidden; nothing refuses it")
    put(s, "orec", "D", "item 6 holds product paths and the M-BOM/Control Plan only; eco-file may file")
for s in STOPS:
    put(s, "onamed", "D", "item 6: a user's rule 12 decision may let a named other ECO commit")
for s in ("S2", "S3", "S4a", "S4b", "S8"):
    put(s, "onamed", "U", "a permission granted at an earlier stop, used after leaving it", "G6", ["borderline"])

# ---- where the reviews' findings and the known defects fall
FINDINGS = [
    ("R270-1-01", "audit --eco on an old-route ECO", "not a cell", "the cutover (item 10) keeps old-route ECOs outside this lifecycle"),
    ("R270-1-02", "the sweep run by no procedure, blind to bypasses", "not a cell", "the accept cell was defined; the defect was the instrument and the procedure behind item 9"),
    ("R270-1-03", "a failure after the run deleted the evidence", "S3 x receive exit 5 after the run", "defined at 33a2581e because the review found it"),
    ("R270-1-04", "the human part's inspection had no owner", "not a cell", "what a golden inspects, not a transition"),
    ("R270-1-05", "no step when the probe does not fail", "S4b x own probe, S4b x rule 12", "defined at 33a2581e because the review found it"),
    ("R270-1-06", "skipped bound tests pass a row", "not a cell", "D1's reading of a row"),
    ("R270-1-07", "class-level bindings, removal and rename", "not a cell", "the binding, not the lifecycle"),
    ("R270-1-08", "SortModel binding outside the tolerance", "not a cell", "a binding"),
    ("R270-1-09", "route evidence ignored the instrument's repair", "not a cell", "the instrument's reading of a defined route"),
    ("R270-1-10", "item 11's text against the code", "not a cell", "bound arithmetic"),
    ("R270-1-11", "eco-fix's lock precondition broader than item 6", "named other-ECO column, stop states (D)", "the prose's cell was right; a skill did not carry it"),
    ("R270-1-12", "counts, stale records", "not a cell", "record"),
    ("R270-1-13", "3:B's reading attributed to the user", "not a cell", "record"),
    ("R270-1-14", "the instrument not R1-protected", "not a cell", "record (protection of a file)"),
    ("R270-1-15", "the rehearsal receipt is not V4", "not a cell", "evidence"),
    ("R270-2-01", "a retry after a failed receipt loses its evidence (KD-270-1)", "G1: S5 x 5 cells", "undefined, found"),
    ("R270-2-02", "an audit finding cannot be acknowledged (KD-270-2)", "G3: S8 x accept", "conflict, found"),
    ("R270-2-03", "the sweep misses later probe/cad commits and unnamed commits (KD-270-3)", "G4: S3/S4a/S8 x own probe/cad", "undefined, found (the part about commits naming no ECO is not a cell: attribution by subject)"),
    ("R270-2-04", "cad-mock does not read the lock (KD-270-4)", "S2-S8 x other ECO CAD (KL)", "the prose's cell is KL; the skill that does CAD work does not read it"),
    ("R270-2-05", "no route for a violation the ECO did not cause (KD-270-5)", "G2: S4b x fix", "conflict, found"),
    ("R270-2-06", "D5's declared inputs passed by no procedure (KD-270-6)", "not a cell", "the inputs of a decision, not a transition"),
    ("R270-2-07", "probe subject 55 vs 54, garbled claim", "not a cell", "record"),
    ("R270-2-08", "two bindings below their row's tolerance (KD-270-7)", "not a cell", "a binding"),
    ("KD-270-8", "eco-file lacks item 6's rule 12 exception (R270-1-11, partly)", "named other-ECO column, stop states (D)", "the prose's cell is defined; eco-file does not carry it"),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    for s, _ in STATES:
        missing = [e for e, _ in EVENTS if e not in C[s]]
        assert not missing, (s, missing)
    out = ["# EXP-20261027-03 - ViewTube's delivery lifecycle as a state x event table", "",
           "Generated by `bomdd/reports/exp-20261027-03/state_event_table.py` (the cells are written there, with the prose "
           "read and the classes in its docstring). ViewTube at `33a2581efac99998f680c51ed0dc4362186c60a4` (ECO-VT-270 "
           "applied), read-only; the delta at `44bd91d0` (ECO-VT-271 applied) is listed under the gaps.", ""]
    out += ["## States", ""] + [f"- **{s}** {d}" for s, d in STATES] + ["", "## Events", ""]
    out += [f"- **{e}** {d}" for e, d in EVENTS] + [""]

    def mark(cell):
        cls, _, gap, flags = cell
        t = cls if not gap else f"{cls}:{gap}"
        if "caught" in flags:
            t += "*"
        if "borderline" in flags:
            t += "?"
        if any(f.startswith("r1:") for f in flags):
            t += "^"
        return t

    out += ["## The table", "", "`*` caught later by item 9; `?` borderline; `^` defined because R8 round 1 found it.", ""]
    out.append("| state | " + " | ".join(e for e, _ in EVENTS) + " |")
    out.append("|---|" + "---|" * len(EVENTS))
    for s, _ in STATES:
        out.append(f"| {s} | " + " | ".join(mark(C[s][e]) for e, _ in EVENTS) + " |")
    out.append("")

    cells = [(s, e, C[s][e]) for s, _ in STATES for e, _ in EVENTS]
    counts = {}
    for _, _, (cls, *_r) in cells:
        counts[cls] = counts.get(cls, 0) + 1
    u = [(s, e, c) for s, e, c in cells if c[0] == "U"]
    u_caught = [x for x in u if "caught" in x[2][3]]
    u_border = [x for x in u if "borderline" in x[2][3]]
    u_strict = [x for x in u if "borderline" not in x[2][3]]
    u_prompted = [x for x in u if x[1] in PROMPTED_BY_KD]
    possible = len(cells) - counts.get("I", 0) - counts.get("N", 0)
    out += ["## Counts", "",
            f"- cells: {len(cells)} ({len(STATES)} states x {len(EVENTS)} events); impossible {counts.get('I', 0)}, "
            f"not applicable {counts.get('N', 0)}; possible {possible}",
            f"- defined {counts.get('D', 0)}, known limit {counts.get('KL', 0)}, conflict {counts.get('C', 0)}, "
            f"**undefined {counts.get('U', 0)}** ({counts.get('U', 0) / possible:.1%} of the possible cells)",
            f"- undefined, strict (borderline cells excluded): {len(u_strict)}; borderline {len(u_border)}",
            f"- undefined and caught later by item 9: {len(u_caught)}; not caught: {len(u) - len(u_caught)}",
            f"- undefined cells in the column added after reading KD-270-3 (own probe/cad): {len(u_prompted)}",
            f"- defined because R8 round 1 found them: "
            f"{sum(1 for _, _, c in cells if any(f.startswith('r1:') for f in c[3]))}", ""]

    out += ["## Gaps (undefined and conflict cells grouped by the missing rule)", "",
            "| gap | cells | class | found by | the missing rule | at 44bd91d0 |", "|---|---|---|---|---|---|"]
    found_cells = notfound_cells = 0
    found_gaps = notfound_gaps = 0
    for g, (what, found, later) in GAPS.items():
        mine = [(s, e, c) for s, e, c in cells if c[2] == g]
        classes = "/".join(sorted({c[0] for _, _, c in mine}))
        where = ", ".join(f"{s}x{e}" for s, e, _ in mine)
        out.append(f"| {g} | {len(mine)} ({where}) | {classes} | {found or 'no review'} | {what} | {later or 'unchanged'} |")
        if found:
            found_cells += len(mine)
            found_gaps += 1
        else:
            notfound_cells += len(mine)
            notfound_gaps += 1
    out += ["", f"- gaps a review found: {found_gaps} ({found_cells} cells); gaps no review found: {notfound_gaps} "
            f"({notfound_cells} cells)", ""]

    out += ["## Where R8's findings and the known defects fall", "",
            "| finding | what | cell | reading |", "|---|---|---|---|"]
    for f in FINDINGS:
        out.append("| " + " | ".join(f) + " |")
    cellish = [f for f in FINDINGS if f[2] != "not a cell"]
    out += ["", f"- findings listed: {len(FINDINGS)} (R8 rounds 1 and 2: 23, plus KD-270-8's own line); on a cell: {len(cellish)}; "
            f"not a cell: {len(FINDINGS) - len(cellish)}", ""]

    out += ["## Every non-defined cell", "", "| state | event | class | gap | flags | note |", "|---|---|---|---|---|---|"]
    for s, e, (cls, note, gap, flags) in cells:
        if cls in ("U", "C", "KL"):
            out.append(f"| {s} | {e} | {cls} | {gap or ''} | {' '.join(flags)} | {note} |")
    out.append("")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
