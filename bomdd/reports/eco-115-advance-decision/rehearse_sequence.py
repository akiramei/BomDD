#!/usr/bin/env python3
"""D5 as the draft states it (loop 6, round 1 repaired): a work's decisions over time — convergence, and whether the process is in control.

  python rehearse_sequence.py [<output file>]

Design evidence, not shipped. Loop 6 removed loop 5's two common causes: a row's history is a ledger of explicit states (A), and the
bounds and their disposition are bound to the playbook's loop rules in one place (B).

A work's decisions come with the work's bounds as issued first ({"holds": n, "decisions": m}); a decision of the work is
  {"result":   advances | holds | input-defect,
   "measured": false for an input defect, and for a hold whose every counted row is unmeasurable by D1 test 1,
   "bounds":   the bounds line of the work order this delivery was made under (absent = as first issued),
   "rows":     {row: state} for every counted row — pass | violation | unmeasurable | no-check | nothing-measured (an input
               defect measured no row; a test-1 hold gives each row unmeasurable, with its own cause),
   "causes":   [[kind, key, route, category], ...] — kind "row" (key "<row>:<category>") or "input" (key "<route>:<message>",
               category "input"), by the decision's result, never by the key's spelling,
   "routes_done": absent (the record has no such field: "unrecorded"), or the cause keys whose route is recorded done since the
               decision where the cause last appeared,
   "row_changes": {"removed": {row: routing cause key}, "added": {row: routing cause key}, "renamed": {old: [[new, ...], routing key]}}}.
The expected outcome of every arm is fixed below, before the arms are run; the script exits 1 if any arm differs.

The ledger: per row, its states over the work's decisions, carried through renames. Observed: pass, violation. Not observed, with its
reason: unmeasurable, no-check, nothing-measured.
  C1 persists     a row is a violation and its last observed state was a violation; or it is unmeasurable or no-check as at its last
                  state other than nothing-measured; or an input cause is in this decision and the previous one. With routes_done:
                  "route done, cause not removed" / "route not done" / "unrecorded".
  C2 returns      a row is a violation after a violation and then a pass; or it is unmeasurable or no-check after that same state and
                  then another (nothing-measured skipped); or an input cause absent in a later decision is back.
  C3 regression   a row whose observed states are all pass (at least one) is a violation now.
  C4 own parts    this decision and the previous one each have a cause whose category is not violation (unmeasurable, no-check, an
                  input defect) — by category, so an on_fail route override does not move it.
  C5 row set      a row removed or renamed with no routing cause (control-plan-fix or bom-fix) of the previous decision on that row (a
                  row cause of it, or an input cause naming it); a row added with no such cause of the previous decision at all; a row
                  removed or renamed whose open violation or unmeasurable (last state other than nothing-measured) is not the cause that
                  routed it.
  C6 bounds       a delivery's work order carries a bounds line different from the work's first issue (the first issue's bounds still
                  apply; it is a signal, not a cause of the decision, so D2 is unchanged).
  (Loop 6 cut-off repairs: C6 replaces the "input cause" of round 1; C5's clause narrowed; nothing-measured skipped in C1/C2's
  not-observed comparison.)
Ruling-layer candidate: rows X != Y and decisions i < j < k: X violation and Y pass at i, X pass and Y violation at j, X violation and
Y pass at k (one fixed, the other broken, then back).
"""
import sys

ROUTING = ("control-plan-fix", "bom-fix")
NOT_PRODUCT = {"unmeasurable", "no-check", "input"}
CAT_ROUTE = {"violation": "product-fix", "unmeasurable": "instrument-recovery", "no-check": "control-plan-fix"}


def reading(d, key):
    if "routes_done" not in d:
        return "unrecorded"
    return "route done, cause not removed" if key in d["routes_done"] else "route not done"


def read_sequence(bounds, decisions):
    signals, ledger = [], {}
    input_seen, input_absent = set(), set()
    prev = None
    for i, d in enumerate(decisions, 1):
        causes = [list(c) for c in d["causes"]]
        if "bounds" in d and d["bounds"] != bounds:  # loop 6 cut-off repair (L6R2-01): a control signal, not a cause of the decision
            signals.append(("C6", i, f"bounds {d['bounds']} differ from the work's first issue {bounds}"))
        ch = d.get("row_changes", {})
        prev_causes = (prev or {}).get("causes", [])
        # a routing cause is "on" a row when it is that row's cause, or an input cause that names the row (its fifth element)
        on_row = {}
        for c in prev_causes:
            if c[2] in ROUTING:
                row = c[1].split(":")[0] if c[0] == "row" else (c[4] if len(c) > 4 else None)
                if row:
                    on_row.setdefault(row, set()).add(c[1])
        any_routing = any(c[2] in ROUTING for c in prev_causes)

        def moved(row, hist, verb):
            if row not in on_row:
                signals.append(("C5", i, f"{row} {verb} with no routing cause on it"))
                return
            # loop 6 cut-off repair (L6R2-02): an open violation or unmeasurable, on the last observed (or not-observed) state that is
            # not nothing-measured, moved under a cause that is not its own
            states = [s for s in hist if s != "nothing-measured"]
            last = states[-1] if states else None
            if last in ("violation", "unmeasurable") and f"{row}:{last}" not in on_row[row]:
                signals.append(("C5", i, f"{row} {verb} with its open {last} under another cause"))

        for old, (news, _via) in sorted(ch.get("renamed", {}).items()):
            hist = ledger.pop(old, [])
            for n in news:
                ledger[n] = list(hist)
            moved(old, hist, "renamed")
        for row in sorted(ch.get("removed", {})):
            moved(row, ledger.pop(row, []), "removed")
        for row in sorted(ch.get("added", {})):
            if not any_routing:
                signals.append(("C5", i, f"{row} added with no routing cause in the previous decision"))
        for row, state in sorted(d.get("rows", {}).items()):
            hist = ledger.setdefault(row, [])
            observed = [s for s in hist if s in ("pass", "violation")]
            key = f"{row}:{state}"
            if state == "violation":
                if observed and observed[-1] == "violation":
                    signals.append(("C1", i, f"{key} ({reading(d, key)})"))
                elif "violation" in observed and "pass" in observed[observed.index("violation"):]:
                    signals.append(("C2", i, key))
                elif observed and all(s == "pass" for s in observed):
                    signals.append(("C3", i, row))
            elif state in ("unmeasurable", "no-check"):
                seen = [s for s in hist if s != "nothing-measured"]  # loop 6 cut-off repair (L6R2-03)
                if seen and seen[-1] == state:
                    signals.append(("C1", i, f"{key} ({reading(d, key)})"))
                elif state in seen and any(s != state for s in seen[seen.index(state):]):
                    signals.append(("C2", i, key))
            hist.append(state)
        cur_input = {c[1] for c in causes if c[0] == "input"}
        prev_input = {c[1] for c in prev_causes if c[0] == "input"}
        for k in sorted(cur_input):
            if k in input_absent:
                signals.append(("C2", i, k))
            elif k in prev_input:
                signals.append(("C1", i, f"{k} ({reading(d, k)})"))
        input_absent = (input_absent | (input_seen - cur_input)) - cur_input
        input_seen |= cur_input
        if prev is not None and any(c[3] in NOT_PRODUCT for c in causes) and any(c[3] in NOT_PRODUCT for c in prev_causes):
            signals.append(("C4", i, ",".join(sorted({c[3] for c in causes if c[3] in NOT_PRODUCT}))))
        d = {**d, "causes": causes}
        prev = d
    candidate = False
    rs = [d.get("rows", {}) for d in decisions]
    for a in range(len(rs)):
        for b in range(a + 1, len(rs)):
            for c in range(b + 1, len(rs)):
                for x in rs[a]:
                    for y in rs[b]:
                        if y != x and (rs[a][x], rs[a].get(y), rs[b].get(x), rs[b][y], rs[c].get(x), rs[c].get(y)) == (
                                "violation", "pass", "pass", "violation", "violation", "pass"):
                            candidate = True
    holds = sum(1 for d in decisions if d["result"] == "holds" and d.get("measured", True))
    if decisions[-1]["result"] == "advances":
        convergence = "converged"
    elif holds >= bounds["holds"] or len(decisions) >= bounds["decisions"]:
        convergence = "bound-reached"
    else:
        convergence = "open"
    return {"convergence": convergence, "holds_measured": holds, "decisions": len(decisions),
            "control": "signals" if signals else "in-control", "signals": signals, "ruling_layer_candidate": candidate}


def H(result, rows=None, causes=None, done=(), changes=None, measured=True, recorded=True, bounds=None, route=None):
    rows = rows or {}
    if causes is None:
        causes = [["row", f"{r}:{s}", (route or CAT_ROUTE)[s], s] for r, s in sorted(rows.items()) if s in CAT_ROUTE]
    d = {"result": result, "rows": rows, "causes": causes, "row_changes": changes or {}, "measured": measured}
    if recorded:
        d["routes_done"] = list(done)
    if bounds is not None:
        d["bounds"] = bounds
    return d


def NM(rows, inputs, recorded=True):  # an input defect: no row measured
    return H("input-defect", {r: "nothing-measured" for r in rows}, causes=[["input", k, r, "input"] for k, r in inputs],
             measured=False, recorded=recorded)


def T1ALL(rows, route="instrument-recovery"):  # a hold whose every row is unmeasurable by D1 test 1
    return H("holds", {r: "unmeasurable" for r in rows}, causes=[["row", f"{r}:unmeasurable", route, "unmeasurable"] for r in rows],
             measured=False)


P, V, U, N = "pass", "violation", "unmeasurable", "no-check"
B = {"holds": 3, "decisions": 5}
TYPO = [("record-fix:the entry has no frozen_commit", "record-fix")]
WO = [("work-order-fix:the frozen-revision line resolves to another commit", "work-order-fix")]
AB = ["CP-A", "CP-B"]
ARMS = [
    # (name, decisions, expected convergence, expected control, expected signals, expected candidate, what it controls)
    ("H1 several causes at once, all fixed, advances", [
        H("holds", {"CP-A": V, "CP-B": V, "CP-C": P}),
        H("advances", {"CP-A": P, "CP-B": P, "CP-C": P}, done=["CP-A:violation", "CP-B:violation"])],
     "converged", "in-control", [], False, "DoD (a): one hold with several causes, no signal"),
    ("H2 two holds, the row's cause changes kind (instrument repaired, then the product fixed)", [
        H("holds", {"CP-A": U, "CP-B": V, "CP-C": P}),
        H("holds", {"CP-A": V, "CP-B": P, "CP-C": P}, done=["CP-A:unmeasurable", "CP-B:violation"]),
        H("advances", {"CP-A": P, "CP-B": P, "CP-C": P}, done=["CP-A:violation"])],
     "converged", "in-control", [], False, "DoD (a): the same two holds as H4, read differently by their causes"),
    ("H3 three holds on a fixed row set, each revealing a different cause on the row, no signal", [
        H("holds", {"CP-A": U, "CP-B": V}),
        H("holds", {"CP-A": V, "CP-B": P}, done=["CP-A:unmeasurable", "CP-B:violation"]),
        H("holds", {"CP-A": N, "CP-B": P}, done=["CP-A:violation"])],
     "bound-reached", "in-control", [], False, "DoD (e): the holds bound is reached with no control signal"),
    ("H4 the same violation twice, route recorded done", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("holds", {"CP-A": V, "CP-B": P}, done=["CP-A:violation"])],
     "open", "signals", ["C1"], False, "DoD (b): C1 alone, 'route done, cause not removed'"),
    ("H4b the same violation twice, route not recorded done", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("holds", {"CP-A": V, "CP-B": P})],
     "open", "signals", ["C1"], False, "DoD (b): C1 alone, 'route not done'"),
    ("H5 a fixed cause returns on its row", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("holds", {"CP-A": P, "CP-B": U}, done=["CP-A:violation"]),
        H("holds", {"CP-A": V, "CP-B": P}, done=["CP-B:unmeasurable"])],
     "bound-reached", "signals", ["C2"], False, "DoD (b): C2 alone"),
    ("H6 a row that never failed breaks", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("holds", {"CP-A": P, "CP-B": V}, done=["CP-A:violation"])],
     "open", "signals", ["C3"], False, "DoD (b): C3 alone"),
    ("H7 two rows alternate in order", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("holds", {"CP-A": P, "CP-B": V}, done=["CP-A:violation"]),
        H("holds", {"CP-A": V, "CP-B": P}, done=["CP-B:violation"])],
     "bound-reached", "signals", ["C2", "C3"], True, "DoD (c): the pattern that may be a contradiction between two promises"),
    ("H7b two rows, the second stays broken", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("holds", {"CP-A": P, "CP-B": V}, done=["CP-A:violation"]),
        H("holds", {"CP-A": V, "CP-B": V}, done=["CP-B:violation"])],
     "bound-reached", "signals", ["C1", "C2", "C3"], False, "L6R1-09: not 'then back', so no candidate"),
    ("H8 the process's own parts fail twice", [
        NM(AB, TYPO),
        H("holds", {"CP-A": N, "CP-B": P})],
     "open", "signals", ["C4"], False, "DoD (b): C4 alone"),
    ("H9 one own-part decision, then product causes", [
        NM(AB, TYPO),
        H("holds", {"CP-A": V, "CP-B": P}),
        H("advances", {"CP-A": P, "CP-B": P}, done=["CP-A:violation"])],
     "converged", "in-control", [], False, "DoD (b): C4 green; the input defect is not counted to the holds bound"),
    ("H10 an input defect between two violations of a row", [
        H("holds", {"CP-A": V, "CP-B": P}),
        NM(AB, TYPO),
        H("holds", {"CP-A": V, "CP-B": P}, done=["CP-A:violation"])],
     "open", "signals", ["C1"], False, "a decision that measured nothing is not an observation"),
    ("H11 a test-1 hold (a failure no row owns) between", [
        H("holds", {"CP-A": V, "CP-B": P, "CP-C": P}),
        T1ALL(["CP-A", "CP-B", "CP-C"], route="control-plan-fix"),
        H("holds", {"CP-A": V, "CP-B": P, "CP-C": P}, done=["CP-A:violation"])],
     "open", "signals", ["C1"], False, "no C3 on B or C, no candidate; the test-1 hold is not counted to the holds bound"),
    ("H12 a failing row split by a routed Control Plan change, still failing", [
        H("holds", {"CP-A": V, "CP-B": P}, causes=[["row", "CP-A:violation", "control-plan-fix", "violation"]]),
        H("holds", {"CP-A1": V, "CP-A2": P, "CP-B": P}, done=["CP-A:violation"],
          changes={"renamed": {"CP-A": [["CP-A1", "CP-A2"], "CP-A:violation"]}})],
     "open", "signals", ["C1"], False, "states carried through a rename under the row's own cause (C1 on CP-A1; no C5)"),
    ("H13 a row added with nothing routed", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("holds", {"CP-A": P, "CP-B": P, "CP-E": V}, done=["CP-A:violation"], changes={"added": {"CP-E": None}})],
     "open", "signals", ["C5"], False, "C5 alone: an unrouted addition"),
    ("H13b a row added by a routing cause", [
        H("holds", {"CP-A": P, "CP-B": N}),
        H("advances", {"CP-A": P, "CP-B": P, "CP-E": P}, done=["CP-B:no-check"], changes={"added": {"CP-E": "CP-B:no-check"}})],
     "converged", "in-control", [], False, "C5 green: an addition routed by the previous decision's control-plan-fix"),
    ("H14 two rows fail together and are fixed together, twice", [
        H("holds", {"CP-A": V, "CP-B": V, "CP-C": P}),
        H("holds", {"CP-A": P, "CP-B": P, "CP-C": U}, done=["CP-A:violation", "CP-B:violation"]),
        H("holds", {"CP-A": V, "CP-B": V, "CP-C": P}, done=["CP-C:unmeasurable"])],
     "bound-reached", "signals", ["C2"], False, "no alternation, so no candidate"),
    ("H15 the same receiving-side defect twice around a hold", [
        NM(AB, TYPO),
        H("holds", {"CP-A": V, "CP-B": P}),
        NM(AB, TYPO)],
     "open", "signals", ["C2"], False, "route keys are not rows (no candidate); the defect's return is C2"),
    ("T1 a violation, the row unmeasurable, the violation again", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("holds", {"CP-A": U, "CP-B": P}, done=["CP-A:violation"]),
        H("holds", {"CP-A": V, "CP-B": P}, done=["CP-A:unmeasurable"])],
     "bound-reached", "signals", ["C1"], False, "a not-observed state does not hide the persistence"),
    ("T2 a violation, a test-1 failure hiding two rows, the violation again", [
        H("holds", {"CP-A": V, "CP-B": P, "CP-C": P}),
        H("holds", {"CP-A": U, "CP-B": U, "CP-C": P}, causes=[["row", "CP-A:unmeasurable", "control-plan-fix", "unmeasurable"],
                                                              ["row", "CP-B:unmeasurable", "control-plan-fix", "unmeasurable"]]),
        H("holds", {"CP-A": V, "CP-B": P, "CP-C": P}, done=["CP-A:violation"])],
     "bound-reached", "signals", ["C1"], False, "the same with an unowned failure on two rows"),
    ("T3 six input defects, alternating record-fix and work-order-fix", [
        NM(AB, TYPO), NM(AB, WO), NM(AB, TYPO), NM(AB, WO), NM(AB, TYPO), NM(AB, WO)],
     "bound-reached", "signals", ["C2", "C4"], False, "the decisions bound stops a loop that never measures a row"),
    ("T4 a control-plan-fix that also drops the failing row", [
        H("holds", {"CP-A": V, "CP-B": N}),
        H("advances", {"CP-B": P}, done=["CP-B:no-check"], changes={"removed": {"CP-A": "CP-B:no-check"}})],
     "converged", "signals", ["C5"], False, "an open cause taken out of the counted set, under a cause not on it"),
    ("T5 a passing row removed with no cause on it in the previous decision", [
        H("holds", {"CP-A": P, "CP-B": N}),
        H("advances", {"CP-B": P}, done=["CP-B:no-check"], changes={"removed": {"CP-A": "CP-B:no-check"}})],
     "converged", "signals", ["C5"], False, "L6R1-05: the removing cause must be on the row (CP-B:no-check is not)"),
    ("T6 a passing row removed by a routing cause on it", [
        H("holds", {"CP-A": P, "CP-B": V}, causes=[["row", "CP-B:violation", "product-fix", "violation"],
                                                   ["row", "CP-A:retire", "control-plan-fix", "retire"]]),
        H("advances", {"CP-B": P}, done=["CP-B:violation", "CP-A:retire"], changes={"removed": {"CP-A": "CP-A:retire"}})],
     "converged", "in-control", [], False, "C5 green"),
    ("T7 an instrument not repaired (one row unmeasurable twice)", [
        H("holds", {"CP-A": U, "CP-B": P}),
        H("holds", {"CP-A": U, "CP-B": P})],
     "open", "signals", ["C1", "C4"], False, "C1 on a not-observed state repeated, with C4"),
    ("X1 every row unmeasurable (stamp missing), repaired, a violation, unmeasurable again", [
        T1ALL(AB),
        H("holds", {"CP-A": V, "CP-B": P}, done=["CP-A:unmeasurable", "CP-B:unmeasurable"]),
        T1ALL(AB)],
     "open", "signals", ["C2"], False, "L6R1-04: an instrument failure's return is C2"),
    ("X1c every row unmeasurable twice running", [T1ALL(AB), T1ALL(AB)],
     "open", "signals", ["C1", "C4"], False, "L6R1-04: C1 with the instrument's owner, and C4"),
    ("X3 on_fail routes a violation to control-plan-fix, twice", [
        H("holds", {"CP-A": V, "CP-B": P}, route={"violation": "control-plan-fix"}),
        H("holds", {"CP-A": V, "CP-B": P}, route={"violation": "control-plan-fix"})],
     "open", "signals", ["C1"], False, "L6R1-06: C4 reads the category, so an on_fail override does not make it fire"),
    ("X4 a failing row renamed under its own routed cause, and passing", [
        H("holds", {"CP-A": V, "CP-B": P}, causes=[["row", "CP-A:violation", "control-plan-fix", "violation"]]),
        H("advances", {"CP-A1": P, "CP-B": P}, done=["CP-A:violation"], changes={"renamed": {"CP-A": [["CP-A1"], "CP-A:violation"]}})],
     "converged", "in-control", [], False,
     "L6R2-02 (cut-off repair): a rename under the row's own cause is a routine route; that it may hide a violation is declared in L9"),
    ("X5 re-issues raise the bound", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("holds", {"CP-A": P, "CP-B": N}, done=["CP-A:violation"], bounds={"holds": 6, "decisions": 8}),
        H("holds", {"CP-A": P, "CP-B": P}, done=["CP-B:no-check"], bounds={"holds": 6, "decisions": 8})],
     "bound-reached", "signals", ["C6"], False,
     "L6R1-02, L6R2-01: the first issue's bound (3) is reached although the re-issues say 6; each changed bounds line is C6"),
    ("Y5 a re-issue raises the bound and its delivery advances", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("advances", {"CP-A": P, "CP-B": P}, done=["CP-A:violation"], bounds={"holds": 9, "decisions": 9})],
     "converged", "signals", ["C6"], False, "L6R2-01: the raised bound is reported even when the work converges"),
    ("Y1 a no-check row loses its automated part under its own cause", [
        H("holds", {"CP-A": P, "CP-B": N}),
        H("advances", {"CP-A": P}, done=["CP-B:no-check"], changes={"removed": {"CP-B": "CP-B:no-check"}})],
     "converged", "in-control", [], False, "L6R2-02: C5 green on a routine control-plan-fix (MoviePad-Remake's two rows, L5)"),
    ("Y2 a no-check row renamed into a row with checks under its own cause", [
        H("holds", {"CP-A": P, "CP-B": N}),
        H("advances", {"CP-A": P, "CP-B2": P}, done=["CP-B:no-check"], changes={"renamed": {"CP-B": [["CP-B2"], "CP-B:no-check"]}})],
     "converged", "in-control", [], False, "L6R2-02: C5 green"),
    ("Y3 a passing row removed after an input defect that names it", [
        H("holds", {"CP-A": P, "CP-B": V}),
        H("input-defect", {"CP-A": "nothing-measured", "CP-B": "nothing-measured"}, measured=False,
          causes=[["input", "control-plan-fix:a named row is retired", "control-plan-fix", "input", "CP-A"]]),
        H("advances", {"CP-B": P}, done=["CP-B:violation", "control-plan-fix:a named row is retired"],
          changes={"removed": {"CP-A": "control-plan-fix:a named row is retired"}})],
     "converged", "in-control", [], False, "L6R2-02: an input cause naming the row routes its removal; the last observed state is pass"),
    ("Y4 an instrument broken before and after an input defect", [
        H("holds", {"CP-A": U, "CP-B": P}),
        NM(AB, TYPO),
        H("holds", {"CP-A": U, "CP-B": P})],
     "open", "signals", ["C1", "C4"], False, "L6R2-03: a persistence across a decision that measured nothing (C1, not C2)"),
    ("X6 a re-issue keeps the bound", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("advances", {"CP-A": P, "CP-B": P}, done=["CP-A:violation"], bounds=dict(B))],
     "converged", "in-control", [], False, "the same bounds line in a re-issue is not a cause"),
]


def real_moviepad():
    """MoviePad-Remake deliveries 1 and 2: rehearsal-moviepad.txt (M0, M1b) and rehearsal-moviepad-d2.txt (N0, N1). Neither record has
    a routes_done field (it did not exist), so persistences read "unrecorded"."""
    passing = ["CP-ASSEMBLY-EXPORT-001", "CP-DOCUMENT-001", "CP-EDIT-001", "CP-EXPORT-001", "CP-EXPORT-CLOCK-001", "CP-EXPORT-COPY-001",
               "CP-EXPORT-VFR-001", "CP-HISTORY-001", "CP-MEDIA-TOOLS-001", "CP-OUTPUT-SETTINGS-001", "CP-PROBE-001"]
    allrows = passing + ["CP-BUILD-001", "CP-SELF-ACCEPTANCE-001"]
    cm = ("control-plan-fix:check_mapping absent or outside I2", "control-plan-fix")
    d1 = NM(allrows, [cm, ("record-fix:delivered None missing or outside I2", "record-fix"),
                      ("record-fix:the entry has no frozen_commit", "record-fix"), ("record-fix:the entry has no work_order_ref", "record-fix")],
            recorded=False)
    d2 = NM(allrows, [cm], recorded=False)
    rows = {**{r: P for r in passing}, "CP-BUILD-001": N, "CP-SELF-ACCEPTANCE-001": N}
    return [
        ("R1 MoviePad-Remake 1 -> 2, records as written", [d1, d2], "open", "signals", ["C1", "C4"], False,
         "DoD (d): the check_mapping defect persists (unrecorded) and the process's own parts fail twice — the template lacks the field"),
        ("R2 MoviePad-Remake 1 -> 2, migrated (decision 1 on M1b's ASSUMED stamp; decision 2 on N1, stamped)",
         [H("holds", dict(rows), recorded=False), H("holds", dict(rows), recorded=False)], "open", "signals", ["C1", "C4"], False,
         "DoD (d): the two no-check rows persist (unrecorded) and own parts fail twice"),
    ]


def main():
    lines, bad = [], 0
    for name, decisions, conv, ctrl, sigs, cand, what in ARMS + real_moviepad():
        r = read_sequence(B, decisions)
        got = sorted({s[0] for s in r["signals"]})
        ok = r["convergence"] == conv and r["control"] == ctrl and got == sorted(sigs) and r["ruling_layer_candidate"] == cand
        bad += not ok
        lines.append(f"{'OK ' if ok else 'BAD'} {name}: convergence {r['convergence']} (expected {conv}); control {r['control']} "
                     f"{got} (expected {ctrl} {sorted(sigs)}); candidate {r['ruling_layer_candidate']} (expected {cand}); "
                     f"holds that measured rows {r['holds_measured']}, decisions {r['decisions']} — {what}")
        for s in r["signals"]:
            lines.append(f"      {s[0]} at decision {s[1]}: {s[2]}")
    n = len(ARMS) + 2
    lines.append(f"arms: {n}; as expected: {n - bad}")
    text = "\n".join(lines) + "\n"
    sys.stdout.reconfigure(encoding="utf-8")
    print(text, end="")
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
