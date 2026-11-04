"""ECO-122 filing basis: how long a warm run of the dwell view's history read would take if each blob's snapshot were reused.

  python -X utf8 prototype.py <register path> <cache dir>

Read-only on the repository. It uses bomdd-job.py's own _dwell_snapshot on each blob (so a snapshot is the tool's), and stores one JSON
file per blob id in <cache dir> (outside any work tree). It prints, for a cold run (empty cache) and a warm run (the same cache):
the blobs parsed, the blobs reused, and the seconds for each stage. It also checks that the warm snapshots equal the cold ones.
A prototype for sizing, not the design: no parallelism, no versioned key, no atomic write.
"""
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

reg = Path(sys.argv[1]).resolve()
cache = Path(sys.argv[2])
cache.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location("bj", Path(__file__).resolve().parents[3] / "method/tools/bomdd-job.py")
bj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bj)

top = subprocess.check_output(["git", "-C", str(reg.parent), "rev-parse", "--show-toplevel"], text=True).strip()
rel = reg.relative_to(Path(top).resolve()).as_posix()


def run(label):
    t0 = time.perf_counter()
    log = subprocess.check_output(["git", "-C", top, "log", "--reverse", "--format=%H", "--", rel], text=True).split()
    t1 = time.perf_counter()
    check = subprocess.run(["git", "-C", top, "cat-file", "--batch-check"], input="".join(f"{h}:{rel}\n" for h in log),
                           capture_output=True, text=True).stdout.splitlines()
    blobs = [l.split()[0] if " blob " in l else None for l in check]
    t2 = time.perf_counter()
    snaps, parsed, reused = [], 0, 0
    p = subprocess.Popen(["git", "-C", top, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for b in blobs:
        if b is None:
            snaps.append(None)
            continue
        f = cache / f"{b}.json"
        if f.exists():
            snaps.append(json.loads(f.read_text(encoding="utf-8")))
            reused += 1
            continue
        p.stdin.write(f"{b}\n".encode())
        p.stdin.flush()
        size = int(p.stdout.readline().split()[2])
        blob = p.stdout.read(size)
        p.stdout.read(1)
        snap, paused, legacy = bj._dwell_snapshot(blob)
        s = {"snap": {k: list(v) for k, v in snap.items()}, "paused": paused, "legacy": legacy}
        f.write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
        snaps.append(s)
        parsed += 1
    p.stdin.close()
    p.wait()
    t3 = time.perf_counter()
    print(f"{label}: commits {len(log)}, parsed {parsed}, reused {reused}; git log {t1 - t0:.2f} s, batch-check {t2 - t1:.2f} s, "
          f"snapshots {t3 - t2:.2f} s, total {t3 - t0:.2f} s")
    return snaps


cold = run("cold")
warm = run("warm")
print("warm equals cold:", cold == warm)
