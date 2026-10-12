import json, sys, collections
LOG = r"C:\Users\akira\source\repos\BomDD\bomdd\reports\viewtube-gate-equipment-20261012\out\timer-log.jsonl"
needle = sys.argv[1]
pid = None
c = collections.Counter(); t = collections.defaultdict(float)
for line in open(LOG, encoding="utf-8"):
    e = json.loads(line)
    if e["event"] == "start" and pid is None and any(needle in a for a in e["argv"]):
        pid = e["pid"]
    if pid is not None and e["event"] == "run" and e["pid"] == pid:
        k = " ".join(e["argv"])
        c[k] += 1; t[k] += e["dt"]
calls = sum(c.values()); distinct = len(c)
dup_calls = sum(n - 1 for n in c.values())
dup_time = sum(t[k] * (c[k] - 1) / c[k] for k in c)
print(f"calls={calls} distinct={distinct} repeat_calls={dup_calls} repeat_time~{dup_time:.2f}s total={sum(t.values()):.2f}s")
hist = collections.Counter(c.values())
print("multiplicity histogram", sorted(hist.items()))
for k, n in c.most_common(8):
    print(n, k[:150])
