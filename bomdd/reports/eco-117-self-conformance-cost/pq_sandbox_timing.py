"""Time one IQ pass and one OQ pass of process-qualification, by sandbox, on a fresh scaffold.
Read-only towards the BomDD repository: the scaffold and the sandboxes live under a temp dir that is removed."""
import importlib.util
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
env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t.invalid",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t.invalid")
tmp = Path(tempfile.mkdtemp(prefix="pq-timing-"))
try:
    t0 = time.perf_counter()
    p = subprocess.run([sys.executable, str(ROOT / "method/tools/bomdd-init.py"), "ProcCoreSmoke",
                        "--dir", str(tmp), "--no-gui", "--no-qualify"], capture_output=True, text=True,
                       encoding="utf-8", env=env, timeout=300)
    print(f"scaffold rc={p.returncode} {time.perf_counter() - t0:.1f} s")
    prod = tmp / "ProcCoreSmoke"
    runner = prod / "bomdd/tools/process-qualification.py"
    spec = importlib.util.spec_from_file_location("pq", runner)
    pq = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pq)

    per = defaultdict(lambda: [0.0, 0, 0, 0.0])  # seconds, commits, validates, init seconds
    current = {"name": "(none)"}
    real_init, real_commit, real_validate = pq.Sandbox.__init__, pq.Sandbox.commit, pq.Sandbox.validate

    def init(self, source_root, base, name, *a, **k):
        current["name"] = name
        s = time.perf_counter()
        real_init(self, source_root, base, name, *a, **k)
        per[name][3] += time.perf_counter() - s

    def commit(self, *a, **k):
        per[self.root.name][1] += 1
        return real_commit(self, *a, **k)

    def validate(self):
        per[self.root.name][2] += 1
        return real_validate(self)

    pq.Sandbox.__init__, pq.Sandbox.commit, pq.Sandbox.validate = init, commit, validate
    # wall time per sandbox = time from its creation to the next sandbox's creation (run_oq is sequential)
    marks = []
    orig_init = pq.Sandbox.__init__

    def marked(self, *a, **k):
        marks.append((time.perf_counter(), a[2] if len(a) > 2 else k.get("name")))
        orig_init(self, *a, **k)

    pq.Sandbox.__init__ = marked
    s = time.perf_counter()
    iq = pq.run_iq(prod)
    t_iq = time.perf_counter() - s
    base = tmp / "oq"
    base.mkdir()
    s = time.perf_counter()
    oq = pq.run_oq(prod, base)
    end = time.perf_counter()
    t_oq = end - s
    print(f"IQ pass {t_iq:.1f} s ({len(iq)} controls, all pass={all(r['pass'] for r in iq)}); "
          f"OQ pass {t_oq:.1f} s ({len(oq)} controls, all pass={all(r['pass'] for r in oq)})")
    print(f"OQ-00 + setup before first sandbox: {marks[0][0] - s:.1f} s")
    for i, (t, name) in enumerate(marks):
        nxt = marks[i + 1][0] if i + 1 < len(marks) else end
        sec, nc, nv, ini = per[name]
        print(f"  {name:6} {nxt - t:6.1f} s  (init {ini:4.1f} s; extra commits {nc - 1}; validates {nv})")
    print(f"sandboxes {len(marks)}; max {max((marks[i + 1][0] if i + 1 < len(marks) else end) - t for i, (t, _) in enumerate(marks)):.1f} s")
finally:
    def _rw(func, path, exc):
        os.chmod(path, 0o700)
        func(path)
    shutil.rmtree(tmp, onexc=_rw)
    print(f"temp removed: {not tmp.exists()}")
