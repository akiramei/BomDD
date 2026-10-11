"""Profile ViewTube's pre-commit hook stage by stage in a throwaway clone (nothing written to ViewTube).

Stages a typical record commit (the ECO body and the register touched), runs bomdd/hooks/pre-commit
under `bash -x` with a timestamped PS4, and sums the time between traced lines per hook block. Then
times commit-msg's second validate_process run (made when the register is staged)."""
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import OrderedDict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
VT = Path(r"C:\Users\akira\source\repos\ViewTube")
base = Path(tempfile.mkdtemp(prefix="hookprof-"))
clone = base / "clone"
try:
    subprocess.run(["git", "clone", "-q", "--shared", "-c", "core.autocrlf=false", str(VT), str(clone)], check=True)
    head = subprocess.run(["git", "-C", str(clone), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    print(f"clone at {head}")
    body = clone / "bomdd/eco/ECO-VT-252.md"
    body.write_bytes(body.read_bytes() + b"\nprofile line\n")
    reg = clone / "bomdd/process/change-register.yaml"
    reg.write_bytes(reg.read_bytes() + b"# profile\n")
    subprocess.run(["git", "-C", str(clone), "add", "bomdd/eco/ECO-VT-252.md", "bomdd/process/change-register.yaml"], check=True)
    env = {"PS4": "+ $(date +%s.%N) ", "PATH": __import__("os").environ["PATH"]}
    import os
    env = {**os.environ, "PS4": "+ ${EPOCHREALTIME} "}
    warm0 = time.perf_counter()
    subprocess.run(["bash", "bomdd/hooks/pre-commit"], cwd=clone, capture_output=True)  # warm the cache
    print(f"first (cold) pre-commit run: {time.perf_counter() - warm0:.1f}s")
    started = time.perf_counter()
    done = subprocess.run(["bash", "-x", "bomdd/hooks/pre-commit"], cwd=clone, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=env)
    total = time.perf_counter() - started
    print(f"pre-commit rc={done.returncode} total {total:.1f}s")
    trace = [line for line in done.stderr.splitlines() if re.match(r"^\++ \d+\.\d+ ", line)]
    stamps = [(float(line.split()[1]), " ".join(line.split()[2:])[:110]) for line in trace]
    costs = []
    for (t0, cmd), (t1, _) in zip(stamps, stamps[1:]):
        costs.append((t1 - t0, cmd))
    for dt, cmd in sorted(costs, reverse=True)[:12]:
        print(f"  {dt:6.1f}s  {cmd}")
    msg = base / "msg.txt"
    msg.write_text("record\n\nprofile\n", encoding="utf-8")
    started = time.perf_counter()
    subprocess.run([sys.executable, "bomdd/tools/validate_process.py", "--commit-msg", str(msg), "--quiet"],
                   cwd=clone, capture_output=True)
    print(f"commit-msg's validate_process --commit-msg: {time.perf_counter() - started:.1f}s")
finally:
    shutil.rmtree(base, ignore_errors=True)
