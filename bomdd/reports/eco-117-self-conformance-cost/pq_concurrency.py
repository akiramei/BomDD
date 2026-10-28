"""Throughput of process-qualification's OQ pass on this machine when N passes run at once (threads, each pass
sequential inside, each with its own sandbox base). A proxy for how far sandbox-level parallelism could go.
Read-only towards the BomDD repository; everything lives in a temp dir that is removed."""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
ROOT = Path(r"C:\Users\akira\source\repos\BomDD")
env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t.invalid",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t.invalid")


def _rw(func, path, exc):
    os.chmod(path, 0o700)
    func(path)


tmp = Path(tempfile.mkdtemp(prefix="pq-conc-"))
try:
    p = subprocess.run([sys.executable, str(ROOT / "method/tools/bomdd-init.py"), "ProcCoreSmoke",
                        "--dir", str(tmp), "--no-gui", "--no-qualify"], capture_output=True, text=True,
                       encoding="utf-8", env=env, timeout=300)
    prod = tmp / "ProcCoreSmoke"
    spec = importlib.util.spec_from_file_location("pq", prod / "bomdd/tools/process-qualification.py")
    pq = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pq)
    for n in (int(a) for a in sys.argv[1:]):
        bases = []
        for i in range(n):
            b = tmp / f"oq-{n}-{i}"
            b.mkdir()
            bases.append(b)
        s = time.perf_counter()
        with ThreadPoolExecutor(max_workers=n) as ex:
            results = list(ex.map(lambda b: pq.run_oq(prod, b), bases))
        wall = time.perf_counter() - s
        ok = all(all(r["pass"] for r in res) for res in results)
        same = len({pq.canonical([], res) for res in results}) == 1
        print(f"{n} OQ passes at once: wall {wall:.1f} s, per pass {wall / n:.1f} s, all pass={ok}, identical={same}")
finally:
    shutil.rmtree(tmp, onexc=_rw)
    print(f"temp removed: {not tmp.exists()}")
