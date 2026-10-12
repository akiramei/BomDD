"""Time copy_registered_evidence with each parent directory copied once, on HEAD's register.

Same inputs as evidence_copy_count.py. Copies into a temporary directory and deletes it; nothing is
written to ViewTube. The measured gate spent 1,066-1,247 s per harness run in this function."""
import subprocess
import sys
import tempfile
import time
import shutil
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8")
VT = Path(r"C:\Users\akira\source\repos\ViewTube")
sys.path.insert(0, str(VT / "bomdd" / "tools"))
import selftest_ui_manufacturing as harness  # noqa: E402

register = yaml.safe_load(subprocess.run(["git", "-C", str(VT), "show", "HEAD:bomdd/process/change-register.yaml"],
                                         check=True, capture_output=True).stdout.decode("utf-8"))
original_copytree = shutil.copytree
seen = set()
calls = {"made": 0, "skipped": 0}


def copy_once(source, destination, *args, **kwargs):
    if args:  # shutil's own recursion into a subdirectory: pass through unchanged
        return original_copytree(source, destination, *args, **kwargs)
    key = Path(source).resolve()
    if key in seen:
        calls["skipped"] += 1
        return destination
    seen.add(key)
    calls["made"] += 1
    return original_copytree(source, destination, **kwargs)


harness.shutil.copytree = copy_once
with tempfile.TemporaryDirectory(prefix="dedupe-") as temp:
    clone = Path(temp)
    started = time.perf_counter()
    unavailable = harness.copy_registered_evidence(clone, register, source_root=VT)
    elapsed = time.perf_counter() - started
print(f"copy_registered_evidence with each directory copied once: {elapsed:.1f}s "
      f"({calls['made']} copies made, {calls['skipped']} repeats skipped, {len(unavailable)} unavailable)")
