#!/usr/bin/env python3
"""D5 as the draft states it (loop 5, round 1 repaired): a work's decisions over time — convergence, and whether the process is in control.

  python rehearse_sequence.py [<output file>]

Design evidence, not shipped. A decision of a work is
  {"result": advances | holds | input-defect,
   "measured": false when it measured no row (an input defect, or every counted row unmeasurable by D1 test 1),
   "rows": {row: category} for every counted row (pass | violation | unmeasurable | no-check), empty when measured is false,
   "causes": [[key, route], ...] (D2's list; key "<row>:<category>" for a held row, "<route>:<message>" for an input defect),
   "routes_done": [keys of the previous decision's causes whose route is recorded done before this delivery, with its ref],
   "row_map": {old row: [new rows]} when the frozen Control Plan or M-BOM renamed rows since the previous decision}.
The expected outcome of every arm is fixed below, before the arms are run; the script exits 1 if any arm differs. Run twice, the
output is byte-identical.

Readings (the draft's D5):
  convergence — converged | open | bound-reached; the bound counts the work's holds that measured rows (input defects measured
                nothing and are the receiving side's), default 3, frozen at the work's issue; at the bound playbook §8 applies
                (no new step; pending human disposition with the state, the evidence still owed and the risk; the control reading
                attached).
  control     — from causes and row observations, never from the count:
    C1 persists     a cause is in this decision and was in the last decision that measured its row (row renames mapped), or an
                    input-defect cause is in this decision and the previous one; split by whether its route was recorded done:
                    "route done, cause not removed" / "route not done"
    C2 returns      a row had this cause in an earlier measured decision, passed in a later one, and has it again
                    (input-defect causes: absent in a later decision, back now)
    C3 regression   a row never non-pass earlier in the work, passed earlier, is a violation now
    C4 own routes   this decision and the previous one each have a cause routed other than product-fix
    C5 unrouted set the counted rows changed since the last measured decision, with no row_map and no control-plan-fix or
                    bom-fix cause in the previous decision
  ruling-layer candidate — rows X != Y and measured decisions i < j < k: X a violation at i, X pass and Y a violation at j, X a
                violation at k (one fixed, the other broken, then back). Marked only; whether it is a contradiction is the review's.
"""
import sys

BOUND = 3
OWN = {"control-plan-fix", "instrument-recovery", "record-fix", "work-order-fix", "bom-fix"}
NONPASS = {"violation", "unmeasurable", "no-check"}


def read_sequence(decisions):
    signals = []
    hist = []  # measured decisions: (index, rows dict after mapping to current names)
    input_causes_seen, input_causes_absent = set(), set()
    prev = None
    for i, d in enumerate(decisions, 1):
        rows = dict(d.get("rows", {}))
        rmap = d.get("row_map", {})
        if rmap:  # carry earlier observations to the new row names
            hist = [(j, {new: cat for old, cat in r.items() for new in rmap.get(old, [old])}) for j, r in hist]
        causes = {k for k, _ in d["causes"]}
        if d.get("measured", True):
            for row, cat in sorted(rows.items()):
                if cat not in NONPASS:
                    continue
                key = f"{row}:{cat}"
                last = next((r for _, r in reversed(hist) if row in r), None)
                if last is not None and last[row] == cat:
                    done = key in d.get("routes_done", [])
                    signals.append(("C1", i, f"{key} ({'route done, cause not removed' if done else 'route not done'})"))
                earlier = [r.get(row) for _, r in hist]
                if cat in earlier and "pass" in earlier[earlier.index(cat) + 1:] and (last is None or last[row] != cat):
                    signals.append(("C2", i, key))
                if cat == "violation" and "pass" in earlier and not any(c in NONPASS for c in earlier):
                    signals.append(("C3", i, row))
            if hist and set(rows) != set(hist[-1][1]) and not rmap and not (
                    prev and any(r in ("control-plan-fix", "bom-fix") for _, r in prev["causes"])):
                signals.append(("C5", i, f"rows {sorted(set(rows) ^ set(hist[-1][1]))}"))
            hist.append((i, rows))
        for k in sorted(c for c in causes if not c.split(":")[0].startswith("CP-")):
            if k in input_causes_absent:
                signals.append(("C2", i, k))
            elif prev is not None and k in {c for c, _ in prev["causes"]}:  # an input defect in two decisions running
                done = k in d.get("routes_done", [])
                signals.append(("C1", i, f"{k} ({'route done, cause not removed' if done else 'route not done'})"))
        cur_input = {c for c in causes if not c.split(":")[0].startswith("CP-")}
        input_causes_absent = (input_causes_absent | (input_causes_seen - cur_input)) - cur_input
        input_causes_seen |= cur_input
        if prev is not None and any(r in OWN for _, r in d["causes"]) and any(r in OWN for _, r in prev["causes"]):
            signals.append(("C4", i, ",".join(sorted({r for _, r in d["causes"] if r in OWN}))))
        prev = d
    candidate = False
    for a in range(len(hist)):
        for b in range(a + 1, len(hist)):
            for c in range(b + 1, len(hist)):
                ra, rb, rc = hist[a][1], hist[b][1], hist[c][1]
                for x in ra:
                    if ra[x] == "violation" and rb.get(x) == "pass" and rc.get(x) == "violation" and any(
                            y != x and rb.get(y) == "violation" and ra.get(y) == "pass" for y in rb):
                        candidate = True
    holds_measured = sum(1 for d in decisions if d["result"] == "holds" and d.get("measured", True))
    if decisions[-1]["result"] == "advances":
        convergence = "converged"
    elif holds_measured >= BOUND:
        convergence = "bound-reached"
    else:
        convergence = "open"
    return {"convergence": convergence, "holds_measured": holds_measured,
            "control": "signals" if signals else "in-control", "signals": signals, "ruling_layer_candidate": candidate}


def H(result, rows=None, causes=None, done=(), measured=True, row_map=None):
    rows = rows or {}
    if causes is None:  # D2's causes from the rows
        causes = [(f"{r}:{c}", {"violation": "product-fix", "unmeasurable": "instrument-recovery", "no-check": "control-plan-fix"}[c])
                  for r, c in sorted(rows.items()) if c in NONPASS]
    return {"result": result, "rows": rows, "causes": [list(c) for c in causes], "routes_done": list(done), "measured": measured,
            "row_map": row_map or {}}


P, V, U, N = "pass", "violation", "unmeasurable", "no-check"
TYPO = [("record-fix:the entry has no frozen_commit", "record-fix")]
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
     "bound-reached", "in-control", [], False, "DoD (e): the bound is reached with no control signal (§8 disposition)"),
    ("H4 the same cause twice, route recorded done", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("holds", {"CP-A": V, "CP-B": P}, done=["CP-A:violation"])],
     "open", "signals", ["C1"], False, "DoD (b): C1 red, 'route done, cause not removed'"),
    ("H4b the same cause twice, route not recorded done", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("holds", {"CP-A": V, "CP-B": P})],
     "open", "signals", ["C1"], False, "DoD (b): C1 red, 'route not done' (D3 not followed)"),
    ("H5 a fixed cause returns on its row", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("holds", {"CP-A": P, "CP-B": U}, done=["CP-A:violation"]),
        H("holds", {"CP-A": V, "CP-B": P}, done=["CP-B:unmeasurable"])],
     "bound-reached", "signals", ["C2"], False, "DoD (b): C2 alone (the row had failed, passed, fails again)"),
    ("H6 a row that never failed breaks", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("holds", {"CP-A": P, "CP-B": V}, done=["CP-A:violation"])],
     "open", "signals", ["C3"], False, "DoD (b): C3 alone"),
    ("H7 two rows alternate in order", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("holds", {"CP-A": P, "CP-B": V}, done=["CP-A:violation"]),
        H("holds", {"CP-A": V, "CP-B": P}, done=["CP-B:violation"])],
     "bound-reached", "signals", ["C2", "C3"], True, "DoD (c): the pattern that may be a contradiction between two promises"),
    ("H8 the process's own parts fail twice", [
        H("input-defect", measured=False, causes=TYPO),
        H("holds", {"CP-A": N, "CP-B": P})],
     "open", "signals", ["C4"], False, "DoD (b): C4 alone"),
    ("H9 one own-route decision, then product causes", [
        H("input-defect", measured=False, causes=TYPO),
        H("holds", {"CP-A": V, "CP-B": P}),
        H("advances", {"CP-A": P, "CP-B": P}, done=["CP-A:violation"])],
     "converged", "in-control", [], False, "DoD (b): C4 green on one own-route decision; the input defect is not counted to the bound"),
    ("H10 an input defect between two violations of a row", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("input-defect", measured=False, causes=TYPO),
        H("holds", {"CP-A": V, "CP-B": P}, done=["CP-A:violation"])],
     "open", "signals", ["C1"], False, "R1-02: a decision that measured nothing is not an observation (C1, not C2)"),
    ("H11 an all-unmeasurable decision (a failure no row owns) between", [
        H("holds", {"CP-A": V, "CP-B": P, "CP-C": P}),
        H("holds", measured=False, causes=[("CP-A:unmeasurable", "control-plan-fix"), ("CP-B:unmeasurable", "control-plan-fix"),
                                           ("CP-C:unmeasurable", "control-plan-fix")]),
        H("holds", {"CP-A": V, "CP-B": P, "CP-C": P}, done=["CP-A:violation"])],
     "open", "signals", ["C1"], False, "R1-02: no C3 on B or C, no candidate; the all-unmeasurable hold measured no row, so it is not counted to the bound"),
    ("H12 a row renamed by a Control Plan change, still failing", [
        H("holds", {"CP-A": V, "CP-B": P}, causes=[("CP-A:violation", "product-fix"), ("CP-A:violation", "control-plan-fix")]),
        H("holds", {"CP-A1": V, "CP-A2": P, "CP-B": P}, done=["CP-A1:violation"], row_map={"CP-A": ["CP-A1", "CP-A2"]})],
     "open", "signals", ["C1"], False, "R1-06: causes mapped through row_map (C1 on CP-A1)"),
    ("H13 the counted rows changed with nothing routed", [
        H("holds", {"CP-A": V, "CP-B": P}),
        H("holds", {"CP-A": P, "CP-B": P, "CP-E": V}, done=["CP-A:violation"])],
     "open", "signals", ["C5"], False, "R1-06: an unrouted change to the row set (C5 alone)"),
    ("H14 two rows fail together and are fixed together, twice", [
        H("holds", {"CP-A": V, "CP-B": V, "CP-C": P}),
        H("holds", {"CP-A": P, "CP-B": P, "CP-C": U}, done=["CP-A:violation", "CP-B:violation"]),
        H("holds", {"CP-A": V, "CP-B": V, "CP-C": P}, done=["CP-C:unmeasurable"])],
     "bound-reached", "signals", ["C2"], False, "R1-03: no alternation, so no candidate"),
    ("H15 the same receiving-side defect twice around a hold", [
        H("input-defect", measured=False, causes=TYPO),
        H("holds", {"CP-A": V, "CP-B": P}),
        H("input-defect", measured=False, causes=TYPO)],
     "open", "signals", ["C2"], False, "R1-03: route keys are not rows (no candidate); the defect's return is C2"),
]


def real_moviepad():
    """MoviePad-Remake deliveries 1 and 2: rehearsal-moviepad.txt (M0, M1b) and rehearsal-moviepad-d2.txt (N0, N1)."""
    cm = ("control-plan-fix:check_mapping absent or outside I2", "control-plan-fix")
    d1_written = H("input-defect", measured=False, causes=[cm, ("record-fix:delivered None missing or outside I2", "record-fix"),
                                                           ("record-fix:the entry has no frozen_commit", "record-fix"),
                                                           ("record-fix:the entry has no work_order_ref", "record-fix")])
    d2_written = H("input-defect", measured=False, causes=[cm])
    passing = ["CP-ASSEMBLY-EXPORT-001", "CP-DOCUMENT-001", "CP-EDIT-001", "CP-EXPORT-001", "CP-EXPORT-CLOCK-001", "CP-EXPORT-COPY-001",
               "CP-EXPORT-VFR-001", "CP-HISTORY-001", "CP-MEDIA-TOOLS-001", "CP-OUTPUT-SETTINGS-001", "CP-PROBE-001"]
    rows = {**{r: P for r in passing}, "CP-BUILD-001": N, "CP-SELF-ACCEPTANCE-001": N}
    return [
        ("R1 MoviePad-Remake 1 -> 2, records as written", [d1_written, d2_written], "open", "signals", ["C1", "C4"], False,
         "DoD (d): the check_mapping defect persists with its route not done, and the process's own routes repeat — the template lacks the field"),
        ("R2 MoviePad-Remake 1 -> 2, migrated (decision 1 on M1b's ASSUMED stamp; decision 2 on N1, stamped)",
         [H("holds", dict(rows)), H("holds", dict(rows))], "open", "signals", ["C1", "C4"], False,
         "DoD (d): the two no-check rows persist with their route not done, and own routes repeat"),
    ]


def main():
    lines, bad = [], 0
    for name, decisions, conv, ctrl, sigs, cand, what in ARMS + real_moviepad():
        r = read_sequence(decisions)
        got = sorted({s[0] for s in r["signals"]})
        ok = r["convergence"] == conv and r["control"] == ctrl and got == sorted(sigs) and r["ruling_layer_candidate"] == cand
        bad += not ok
        lines.append(f"{'OK ' if ok else 'BAD'} {name}: convergence {r['convergence']} (expected {conv}); control {r['control']} "
                     f"{got} (expected {ctrl} {sorted(sigs)}); candidate {r['ruling_layer_candidate']} (expected {cand}); "
                     f"holds that measured rows {r['holds_measured']} — {what}")
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
