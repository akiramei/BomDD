"""Show how the long Python processes nest in time: the UI-manufacturing harness commits inside its
lifecycle fixture, and that commit runs the fixture's own hooks, which can start the harness again.

For every process over 20 s: offset from the first record, duration, depth by time containment, and
for each `git commit` it made, the commit message (argv) and seconds."""
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
        proc = {"argv": record["argv"], "cwd": record.get("cwd", ""), "start": record["t"], "end": None, "runs": []}
        procs[pid] = proc
        order.append(proc)
    elif record["event"] == "run" and pid in procs:
        procs[pid]["runs"].append(record)
    elif record["event"] == "exit" and pid in procs:
        procs[pid]["end"] = record["t"]

long = [proc for proc in order if proc["end"] and proc["end"] - proc["start"] >= 20]
for proc in long:
    depth = sum(1 for other in long if other is not proc and other["start"] <= proc["start"] and other["end"] >= proc["end"])
    name = " ".join(item.replace("\\", "/").split("/")[-1] for item in proc["argv"][:3])
    print(f"{'  ' * depth}{proc['start'] - t0:8.1f}s +{proc['end'] - proc['start']:7.1f}s  {name}  [cwd {proc['cwd'][-60:]}]")
    for run in proc["runs"]:
        argv = run["argv"]
        if len(argv) > 1 and argv[0].lower().endswith(("git", "git.exe")) and "commit" in argv:
            at = argv.index("-m") + 1 if "-m" in argv else len(argv)
            message = argv[at] if at < len(argv) else "?"
            print(f"{'  ' * depth}    commit {run['dt']:7.1f}s rc={run['rc']}  {message[:60]}")
