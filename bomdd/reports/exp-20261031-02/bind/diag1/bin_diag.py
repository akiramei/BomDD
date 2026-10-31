"""Bin the A2 in-state failures by the predicate keys that fail at the start (operator's reading, after the counts).

    python bin_diag.py <diag.json> <diag certify.json> <MainWindowViewModel.cs> <out.json>
A key is "localized" when its view-model property is an expression of the Localizer (`L[` or `L.Format(`).
"""
import collections
import json
import re
import sys

dg = json.load(open(sys.argv[1], encoding="utf-8"))
cert = json.load(open(sys.argv[2], encoding="utf-8"))
src = open(sys.argv[3], encoding="utf-8").read()
localized = set(re.findall(r"public string (\w+)\s*=>[^;]*\bL(?:\[|\.Format\()", src))
pred = {s["id"]: s["predicate"] for s in dg["states"]}
keys = collections.defaultdict(list)
for sid in pred:
    _, scen, st, k = sid.split("|")
    keys[scen].append(sid)
rows = []
for p in cert["points"]:
    scen = p["Scenario"].split("|")[1]
    hold = set(p["States"])
    fail = [x.split("|")[3] for x in keys[scen] if x not in hold]
    loc = [k for k in fail if k in localized]
    other = [k for k in fail if k not in localized]
    kind = "localized only" if loc and not other else "other only" if other and not loc else "both"
    rows.append({"scenario": scen, "state": keys[scen][0].split("|")[2], "keys": len(keys[scen]),
                 "failing_localized": loc, "failing_other": other, "kind": kind})
out = {"localized_properties": sorted(localized), "rows": rows,
       "count": dict(collections.Counter(r["kind"] for r in rows))}
json.dump(out, open(sys.argv[4], "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print(out["count"])
for r in rows:
    print(r["scenario"], r["kind"], r["failing_other"])
