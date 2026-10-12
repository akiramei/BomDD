import json, sys, collections
T0 = 1791787992.795
LOG = r"C:\Users\akira\source\repos\BomDD\bomdd\reports\viewtube-gate-equipment-20261012\out\timer-log.jsonl"
needle = sys.argv[1]
nargs = int(sys.argv[2]) if len(sys.argv) > 2 else 3
pid = None
runs = []
for line in open(LOG, encoding="utf-8"):
    e = json.loads(line)
    if e["event"] == "start" and pid is None and any(needle in a for a in e["argv"]):
        pid = e["pid"]
        print("pid", pid, "start", e["t"] - T0, e["argv"], e.get("cwd"))
    if pid is not None and e["event"] == "run" and e["pid"] == pid:
        runs.append(e)
groups = collections.Counter()
times = collections.defaultdict(float)
for r in runs:
    a = r["argv"]
    key = " ".join(x for x in a[:nargs])
    groups[key] += 1
    times[key] += r["dt"]
for k, n in sorted(groups.items(), key=lambda kv: -times[kv[0]])[:40]:
    print(f"{times[k]:7.2f}s x{n:4d}  {k[:200]}")
