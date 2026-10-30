"""EXP-03 after the verdict: why each item missed (descriptive)."""
import json
import re
import sys
from pathlib import Path

S = Path(sys.argv[1])


def load(p):
    return json.loads((S / p / "table.json").read_text(encoding="utf-8"))


def ops(t, pat):
    return [o for o in t["operations"] if re.search(pat, " ".join(str(o.get(k)) for k in ("id", "label", "mock_action")))]


print("== D1: detail-pane tag ops (pre T01, post T02) and the mock")
for p in ("T01", "T02"):
    t = load(p)
    for o in ops(t, r"(?i)tag|タグ"):
        if o["kind"] in ("assign", "unassign"):
            print(p, o["id"], o["kind"], o.get("mock_action"), "cp=", o.get("counterpart"), "refs=", o["text_refs"][:3],
                  "owners=", o.get("owner_surfaces"))
    mock = (S / p / "mock" / "viewtube-v1.html").read_text(encoding="utf-8")
    print(p, "mock data-ui-action with Tag:", sorted(set(re.findall(r'data-ui-action="([^"]*Tag[^"]*)"', mock))))
print("== D2: states with selection_possible, and the batch tag op's availability (T03 pre, T04 post)")
for p in ("T03", "T04"):
    t = load(p)
    sel = {s["id"]: s["name"] for s in t["states"] if s.get("selection_possible") is True}
    print(p, "states", len(t["states"]), "selection_possible true:", len(sel),
          "null:", sum(s.get("selection_possible") is None for s in t["states"]))
    ordinary = [(s["id"], s["name"], s.get("selection_possible")) for s in t["states"]
                if re.search(r"(?i)ordinary|通常|browse", s["name"] + " " + str(s.get("evidence")))]
    print("   ordinary/browse states:", ordinary[:6])
    for o in ops(t, r"BatchAssignTag"):
        print("  ", o["id"], {k: v for k, v in o["availability"].items() if k in sel or k in [x[0] for x in ordinary]})
print("== D3: collection entities and create ops (T05 pre, T06 post)")
for p in ("T05", "T06"):
    t = load(p)
    for e in t["entities"]:
        if re.search(r"(?i)collection|コレクション", e["name"] + e["id"]):
            mine = [o for o in t["operations"] if o.get("entity") in (e["id"], e["name"])]
            print(p, e["id"], e["name"], "ops", len(mine),
                  "creates:", [(o["id"], o.get("mock_action")) for o in mine if o["kind"] in ("create", "add")])
    for o in ops(t, r"(?i)manual|手動"):
        if o["kind"] in ("create", "add"):
            print("   manual create/add:", o["id"], o.get("mock_action"), o.get("entity"), o["text_refs"][:3])
