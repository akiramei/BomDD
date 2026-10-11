"""Run validate_process.py --commit-msg MSG in REPO once; save stdout/stderr; print exit, seconds, sha256.

usage: python runvp.py REPO MSGFILE OUTPREFIX [--quiet] [--hashseed N]
"""
import hashlib
import os
import subprocess
import sys
import time

repo, msg, out = sys.argv[1], sys.argv[2], sys.argv[3]
extra = []
env = dict(os.environ)
args = sys.argv[4:]
if "--quiet" in args:
    extra.append("--quiet")
if "--hashseed" in args:
    env["PYTHONHASHSEED"] = args[args.index("--hashseed") + 1]
start = time.perf_counter()
p = subprocess.run([sys.executable, "bomdd/tools/validate_process.py", "--commit-msg", msg, *extra],
                   cwd=repo, capture_output=True, env=env)
elapsed = time.perf_counter() - start
open(out + ".stdout", "wb").write(p.stdout)
open(out + ".stderr", "wb").write(p.stderr)
print(f"{os.path.basename(out)}: exit={p.returncode} seconds={elapsed:.1f} "
      f"stdout_sha256={hashlib.sha256(p.stdout).hexdigest()[:16]} stdout_lines={p.stdout.count(b'\n')} "
      f"stderr_bytes={len(p.stderr)}")
