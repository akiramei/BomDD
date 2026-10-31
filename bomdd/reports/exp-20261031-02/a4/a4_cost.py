"""A4: wall time and tool uses of every agent whose first prompt names an exp07 staging folder.

    python a4_cost.py <subagents dir> <out.json>
Wall time = last minus first timestamp of the transcript (an author's transcript spans its answers to every round, idle
waits included). Helpers an agent started itself are listed with their parent.
"""
import datetime
import json
import pathlib
import re
import sys

d = pathlib.Path(sys.argv[1])
rows = []
for t in sorted(d.glob("agent-*.jsonl")):
    lines = [json.loads(x) for x in t.open(encoding="utf-8")]
    first = next((o for o in lines if o.get("message", {}).get("role") == "user"), None)
    if first is None:
        continue
    c = first["message"]["content"]
    text = c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)
    m = re.search(r"exp07[\\/]+([\w-]+)", text)
    if not m:
        continue
    ts = [o["timestamp"] for o in lines if o.get("timestamp")]
    p = lambda s: datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
    tools = sum(1 for o in lines if o.get("message", {}).get("role") == "assistant"
                and isinstance(o["message"].get("content"), list)
                for x in o["message"]["content"] if x.get("type") == "tool_use")
    meta = t.with_suffix(".meta.json")
    meta = json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else {}
    rows.append({"agent": t.stem[6:], "folder": m.group(1), "description": meta.get("description"),
                 "parent": meta.get("parentAgentId"), "start": ts[0], "end": ts[-1],
                 "wall_s": round((p(ts[-1]) - p(ts[0])).total_seconds()), "tool_uses": tools})
rows.sort(key=lambda r: r["start"])
json.dump({"agents": rows}, open(sys.argv[2], "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
for r in rows:
    print(r["start"][:19], r["folder"], r["wall_s"], r["tool_uses"], r["parent"] or "")
print(len(rows), "agents")
