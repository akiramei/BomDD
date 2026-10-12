import json, sys, collections
LOG = r"C:\Users\akira\source\repos\BomDD\bomdd\reports\viewtube-gate-equipment-20261012\out\timer-log.jsonl"
needle = sys.argv[1]
starts = {}
pids = set()
total = 0.0; n = 0
child = collections.defaultdict(float); childn = collections.Counter()
for line in open(LOG, encoding="utf-8"):
    e = json.loads(line)
    if e["event"] == "start" and any(needle in a for a in e["argv"]):
        starts[e["pid"]] = e["t"]; pids.add(e["pid"])
    elif e["event"] == "exit" and e["pid"] in starts:
        total += e["t"] - starts.pop(e["pid"]); n += 1
    elif e["event"] == "run" and e["pid"] in pids:
        k = " ".join(e["argv"][:2]); child[k] += e["dt"]; childn[k] += 1
print(f"{needle}: {n} processes, {total:.1f}s wall")
for k, v in sorted(child.items(), key=lambda kv: -kv[1])[:6]:
    print(f"   {v:7.1f}s x{childn[k]:5d} {k}")
