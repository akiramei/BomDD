"""Diagnostic input for the harness (operator's reading of A2's failures, not A2): for every scenario whose step fails with
"in-state X does not hold", one zero-step scenario with the same setup, and one singleton state per predicate key of X.
The harness's k=0 point then lists which singletons hold, i.e. which keys of X fail on the authority.

    python mk_diag.py <harness-scenarios.json> <certify.json> <out.json>
"""
import json
import re
import sys

scen = json.load(open(sys.argv[1], encoding="utf-8"))
cert = json.load(open(sys.argv[2], encoding="utf-8"))
states = {s["id"]: s for s in scen["states"]}
byid = {s["id"]: s for s in scen["scenarios"]}
out_states, out_scen = [], []
for r in cert["steps"]:
    m = re.match(r"in-state (\S+) does not hold", r.get("Reason") or "")
    if not m:
        continue
    st = m.group(1)
    sid = r["Scenario"]
    for i, (k, v) in enumerate(states[st]["predicate"].items()):
        out_states.append({"id": f"D|{sid}|{st}|{k}", "name": k, "predicate": {k: v}})
    s = byid[sid]
    out_scen.append({"id": f"D|{sid}|{r['Index']}", "title": s["title"], "goal": s["goal"], "flow": s["flow"],
                     "setup": s.get("setup") or [], "steps": [],
                     "_note": f"replays the {r['Index']} steps before the failing one is not done; only Index 0 is exact"})
json.dump({"states": out_states, "scenarios": out_scen}, open(sys.argv[3], "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
print(len(out_states), "singleton states,", len(out_scen), "scenarios;",
      sum(1 for r in cert["steps"] if (r.get("Reason") or "").startswith("in-state") and r["Index"] != 0), "fail at Index > 0")
