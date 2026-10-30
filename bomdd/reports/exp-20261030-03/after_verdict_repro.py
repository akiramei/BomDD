"""EXP-03 section 8: T02 vs T03 (same input) - flags keyed by mock action only, and each item's matching on the other label;
plus D2's entry control availability."""
import json
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
import checks  # noqa: E402

d = json.loads((Path(sys.argv[1]) / "flags.json").read_text(encoding="utf-8"))
f2, f3 = d["packages"]["T02"]["T"]["flags"], d["packages"]["T03"]["T"]["flags"]
acts = set((Path(sys.argv[2]) / "T02" / "actions.txt").read_text(encoding="utf-8").split())
k2 = {(f["check"], f["key"]) for f in f2 if f["key"] in acts}
k3 = {(f["check"], f["key"]) for f in f3 if f["key"] in acts}
print("flags keyed by a mock action: T02", len(k2), "T03", len(k3), "shared", len(k2 & k3), "jaccard", checks.jaccard(k2, k3))
for c in ("T1", "T2", "T3", "T4", "T5", "T6"):
    print(" ", c, "T02", sum(f["check"] == c for f in f2), "T03", sum(f["check"] == c for f in f3))
print("D1 matching on T03 (same input as D1 post):", [(f["check"], f["key"]) for f in checks.item_flags("D1", "T", f3)])
print("D2 matching on T02 (same input as D2 pre):", [(f["check"], f["key"]) for f in checks.item_flags("D2", "T", f2)])
for p in ("T03", "T04"):
    t = json.loads((Path(sys.argv[2]) / p / "table.json").read_text(encoding="utf-8"))
    sel = [s["id"] for s in t["states"] if s.get("selection_possible") is True]
    for o in t["operations"]:
        if o.get("mock_action") in ("OpenTagAssignment", "BatchAssignTag", "BatchUnassignTag"):
            print(p, o["id"], o["mock_action"], {s: o["availability"].get(s) for s in sel})
