"""Where does a long harness process spend time in its own Python (no child running)?

For each process over 1000 s, list the gaps of 10 s or more between the end of one subprocess.run
call and the start of the next (or the process start / exit), with the calls on either side."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(__file__).resolve().parent / "out"
records = [json.loads(line) for line in (OUT / "timer-log.jsonl").read_text(encoding="utf-8").splitlines() if line]
t0 = min(record["t"] for record in records)
procs = {}
order = []
for record in sorted(records, key=lambda item: item["t"]):
    pid = record["pid"]
    if record["event"] == "start":
        procs[pid] = {"argv": record["argv"], "start": record["t"], "end": None, "runs": []}
        order.append(procs[pid])
    elif record["event"] == "run" and pid in procs:
        procs[pid]["runs"].append(record)
    elif record["event"] == "exit" and pid in procs:
        procs[pid]["end"] = record["t"]


def label(run):
    return " ".join(str(item).replace("\\", "/").split("/")[-1] for item in run["argv"][:4]) if run else "-"


for proc in order:
    if not proc["end"] or proc["end"] - proc["start"] < 1000:
        continue
    runs = sorted(proc["runs"], key=lambda item: item["t"])
    print(f"\n{proc['start'] - t0:8.1f}s +{proc['end'] - proc['start']:7.1f}s  {label({'argv': proc['argv']})}")
    previous_end, previous = proc["start"], None
    own_total = 0.0
    for run in runs + [None]:
        start = run["t"] if run else proc["end"]
        gap = start - previous_end
        own_total += max(gap, 0)
        if gap >= 10:
            print(f"    gap {gap:7.1f}s at {previous_end - t0:8.1f}s  after [{label(previous)}]  before [{label(run)}]")
        if run:
            previous_end, previous = max(previous_end, run["t"] + run["dt"]), run
    print(f"    own time total {own_total:.1f}s")
