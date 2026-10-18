"""For each reviewed round: edits by the main session to that round's order while the reviewer was running (request_ts < edit ts < report_ts)."""
import json
import sys
from pathlib import Path

base = Path(sys.argv[1])
versions = json.loads((base / "versions.json").read_text(encoding="utf-8"))
edits = [json.loads(l) for l in (base / "primary/edits.jsonl").open(encoding="utf-8")]


def writes(e, name):
    if (e.get("result") or {}).get("is_error"):
        return False
    fp = (e.get("file_path") or "").replace("\\", "/")
    p = e.get("payload") or ""
    return fp.endswith(name) or (e["tool"] == "Bash" and name in p and ("sed -i" in p or ">" in p))


# control: the same matcher over the whole session, with no time window, must find the orders' edits
for d in sorted({v["document"] for v in versions}):
    print(f"control: writes to order {d} in the whole session:", sum(writes(e, f"60-change-order-eco-{d}.md") for e in edits))
hit_rounds = 0
for v in versions:
    name = f"60-change-order-eco-{v['document']}.md"
    lo, hi = v["request_ts"], v.get("report_ts") or "9999"
    hits = [(e["ts"], e["tool"], e["seq"]) for e in edits if lo < e["ts"] < hi and writes(e, name)]
    if hits:
        hit_rounds += 1
    print(v["eco"], v["round"], v["request_ts"], v.get("report_ts"), "edits during review:", len(hits), hits[:3])
print("rounds:", len(versions), "| rounds with the order edited while its reviewer ran:", hit_rounds)
