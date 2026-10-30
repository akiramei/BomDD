"""EXP-03 sensitivity (after the verdict, descriptive): the same checks with owner_surfaces null read as [] (no row dropped).
Usage: python -I exp03_sensitivity.py <exp-folder> <staging>"""
import json
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
import checks  # noqa: E402

stage = Path(sys.argv[2])
results = {}
for pkg in checks.PACKAGES:
    acts = [a for a in (stage / pkg / "actions.txt").read_text(encoding="utf-8").splitlines() if a]
    t = json.loads((stage / pkg / "table.json").read_text(encoding="utf-8"))
    for o in t["operations"]:
        if o.get("owner_surfaces") is None:
            o["owner_surfaces"] = []
    table, dropped = checks.validate(t)
    results[pkg] = {"M": {"flags": checks.layer_m(acts)}, "T": {"flags": checks.layer_t(table, acts)}}
    print(pkg, "dropped", dropped)
s = checks.tally(results)
for item, r in s["T"].items():
    print("T", item, "caught", r["caught"], "pre", len(r["pre_matching"]), "post", len(r["post_matching"]))
    for st in ("pre", "post"):
        for f in r[st + "_matching"]:
            print("   ", st, f["check"], f["text"][:140])
print(s["reading_T"], s["post_stop_flags"])
