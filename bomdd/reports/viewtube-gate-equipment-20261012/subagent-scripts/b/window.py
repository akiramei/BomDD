import json, sys
T0 = 1791787992.795
LOG = r"C:\Users\akira\source\repos\BomDD\bomdd\reports\viewtube-gate-equipment-20261012\out\timer-log.jsonl"
lo, hi = float(sys.argv[1]), float(sys.argv[2])
minrun = float(sys.argv[3]) if len(sys.argv) > 3 else 0.3
starts = {}
rows = []
for line in open(LOG, encoding="utf-8"):
    e = json.loads(line)
    t = e["t"] - T0
    if e["event"] == "start":
        starts[e["pid"]] = (t, e["argv"], e.get("cwd", ""))
    elif e["event"] == "exit":
        s = starts.get(e["pid"])
        if s and lo <= s[0] <= hi:
            rows.append((s[0], "PY", t - s[0], " ".join(s[1])[:140], s[2][-60:], e["pid"], e.get("ppid")))
    elif e["event"] == "run":
        st = t - e["dt"]
        if lo <= st <= hi and e["dt"] >= minrun:
            rows.append((st, "RUN", e["dt"], " ".join(e["argv"])[:160], e.get("cwd", "")[-60:], e["pid"], e.get("ppid")))
rows.sort()
for r in rows:
    print(f"{r[0]:9.1f} {r[1]:3} {r[2]:7.2f}s pid={r[5]} {r[3]}  [{r[4]}]")
