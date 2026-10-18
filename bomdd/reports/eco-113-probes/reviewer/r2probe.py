import os, sys, time, subprocess, json

D = os.path.dirname(os.path.abspath(__file__))
L = os.path.join(D, "ledger_r2.jsonl")

if len(sys.argv) > 1 and sys.argv[1] == "appender":
    tag = sys.argv[2]
    for i in range(3000):
        with open(L, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"t": tag, "i": i, "pad": "x" * 200}) + "\n")
    sys.exit(0)

print(sys.version)
# 1. concurrent append atomicity (same as write_ledger)
if os.path.exists(L): os.remove(L)
ps = [subprocess.Popen([sys.executable, __file__, "appender", t]) for t in ("A", "B", "C")]
for p in ps: p.wait()
lines = open(L, "rb").read().split(b"\n")[:-1]
bad = 0
for ln in lines:
    try: json.loads(ln)
    except Exception: bad += 1
print("append: expected", 9000, "lines", len(lines), "unparsable", bad)

# 2. shell=True kill leaves grandchild?
marker = os.path.join(D, "gc_alive.txt")
if os.path.exists(marker): os.remove(marker)
code = "import time,pathlib,os; [ (pathlib.Path(r'%s').write_text(str(i)), time.sleep(0.2)) for i in range(40) ]" % marker
p = subprocess.Popen(f'"{sys.executable}" -c "{code}"', shell=True)
time.sleep(1.5)
p.kill(); p.wait()
v1 = open(marker).read() if os.path.exists(marker) else None
time.sleep(1.5)
v2 = open(marker).read() if os.path.exists(marker) else None
print("after killing shell pid", p.pid, ": marker", v1, "->", v2, "(grandchild alive if increased)")
