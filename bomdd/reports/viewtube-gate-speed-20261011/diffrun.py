"""Differential run: original validator vs in-memory patched validator, same tree, same args.
Compares stdout byte-for-byte and the exit code, and reports wall time of each."""
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
VT = Path(r"C:\Users\akira\source\repos\ViewTube")
S = Path(__file__).resolve().parent
CASES = [
    ("record_consistency", "bomdd/tools/validate_record_consistency.py", ["--mode", "active", "--json"]),
    ("machinery_claims", "bomdd/tools/validate_machinery_claims.py", ["--json", "--root", str(VT)]),
]


def run(cmd):
    s = time.perf_counter()
    p = subprocess.run(cmd, cwd=VT, capture_output=True)
    return p, time.perf_counter() - s


for name, rel, args in CASES:
    if len(sys.argv) > 1 and name not in sys.argv[1:]:
        continue
    orig, t0 = run([sys.executable, rel, *args])
    new, t1 = run([sys.executable, str(S / "patchrun.py"), str(VT / rel), str(S / "patches.py"), name, "--", *args])
    same = orig.stdout == new.stdout and orig.returncode == new.returncode
    print(f"{name}: original rc={orig.returncode} {t0:6.1f}s | patched rc={new.returncode} {t1:6.1f}s | "
          f"stdout identical={orig.stdout == new.stdout} ({len(orig.stdout)} bytes) | verdict {'SAME' if same else 'DIFFERENT'}")
    if new.stderr.strip():
        print("  patched stderr:", new.stderr.decode('utf-8', 'replace')[:300])
