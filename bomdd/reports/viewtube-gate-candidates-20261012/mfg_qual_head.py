"""Run the UI-manufacturing equipment qualification exactly as the pre-commit hook would, against an
UNCHANGED hook (HEAD), in a throwaway clone. If it fails 49/51 here too, the failure predates any hook
change."""
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
VT = Path(r"C:\Users\akira\source\repos\ViewTube")
base = Path(tempfile.mkdtemp(prefix="mfgq-"))
clone = base / "clone"
try:
    subprocess.run(["git", "clone", "-q", "--shared", "-c", "core.autocrlf=false", str(VT), str(clone)], check=True)
    head = subprocess.run(["git", "-C", str(clone), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    print("clone at", head, "(hook unchanged)")
    tmp = base / "tree"
    tmp.mkdir()
    subprocess.run(["git", "-C", str(clone), "checkout-index", "--all", f"--prefix={tmp.as_posix()}/"], check=True)
    trusted = base / "trusted_selftest.py"
    trusted.write_bytes(subprocess.run(["git", "-C", str(clone), "show", "HEAD:bomdd/tools/selftest_ui_manufacturing.py"],
                                       capture_output=True, check=True).stdout)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["VIEWTUBE_UI_MFG_CANDIDATE_ROOT"] = str(tmp)
    t0 = time.perf_counter()
    done = subprocess.run([sys.executable, str(trusted)], cwd=tmp, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    print(f"rc={done.returncode} in {time.perf_counter() - t0:.0f}s")
    lines = (done.stdout + done.stderr).splitlines()
    for line in lines:
        if "FAIL" in line or "self-test" in line or "RECORD_LANGUAGE" in line:
            print("  " + line[:220])
finally:
    shutil.rmtree(base, ignore_errors=True)
