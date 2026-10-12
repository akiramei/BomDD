"""Profile one full process-qualification run as C11 runs it: scaffold with bomdd-init, then the runner with
the timing probe on PYTHONPATH. Summarises git and Python process counts and seconds."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\akira\source\repos\BomDD")
SITE = ROOT / "bomdd/reports/viewtube-gate-equipment-20261012/site"
tmp = Path(tempfile.mkdtemp(prefix="pq-profile-"))
env = dict(os.environ, GIT_AUTHOR_NAME="x", GIT_AUTHOR_EMAIL="x@x.invalid", GIT_COMMITTER_NAME="x",
           GIT_COMMITTER_EMAIL="x@x.invalid")
try:
    subprocess.run([sys.executable, str(ROOT / "method/tools/bomdd-init.py"), "ProcCoreSmoke", "--dir", str(tmp),
                    "--no-gui", "--no-qualify"], env=env, check=True, capture_output=True)
    prod = tmp / "ProcCoreSmoke"
    log = tmp / "log.jsonl"
    env2 = dict(os.environ, PYTHONPATH=str(SITE), GATE_TIMER_LOG=str(log))
    started = time.time()
    run = subprocess.run([sys.executable, str(prod / "bomdd/tools/process-qualification.py"), "--root", str(prod),
                          "--json", str(tmp / "q.json")], env=env2, capture_output=True, text=True, encoding="utf-8")
    total = time.time() - started
    records = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]
    runner = [r for r in records if r["event"] == "run"]
    starts = [r for r in records if r["event"] == "start"]
    by = defaultdict(lambda: [0, 0.0])
    for r in runner:
        argv = r["argv"]
        key = Path(argv[0]).name.lower().replace(".exe", "")
        if key == "git":
            sub = next((a for a in argv[1:] if not a.startswith("-") and a not in ("-C",) and "\\" not in a and "/" not in a), "?")
            key = "git " + sub
        else:
            key = key + " " + Path(argv[1]).name if len(argv) > 1 else key
        by[key][0] += 1
        by[key][1] += r["dt"]
    print(f"process-qualification rc={run.returncode} total {total:.1f} s; python processes started {len(starts)}")
    hook_validators = [r for r in starts if any("process-validator" in a for a in r["argv"])]
    print(f"python process-validator processes (from hooks and direct): {len(hook_validators)}")
    for key, (count, seconds) in sorted(by.items(), key=lambda kv: -kv[1][1])[:12]:
        print(f"  {seconds:7.1f} s  x{count:<4} {key}")
    durations = []
    open_ = {}
    for r in sorted(records, key=lambda x: x["t"]):
        if r["event"] == "start":
            open_[r["pid"]] = r
        elif r["event"] == "exit" and r["pid"] in open_:
            s = open_.pop(r["pid"])
            durations.append((r["t"] - s["t"], " ".join(Path(a).name for a in s["argv"][:3])))
    validators = [d for d, name in durations if "process-validator" in name]
    if validators:
        print(f"process-validator runs: {len(validators)}, total {sum(validators):.1f} s, mean {sum(validators)/len(validators):.2f} s")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
