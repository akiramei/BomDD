"""Run the original and the ECO-105 self-conformance on the same BomDD clone, one after the other; compare exit codes
and the check lines (the [env] line and temp paths aside), and report the seconds."""
import re
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
clone, original = Path(sys.argv[1]), Path(sys.argv[2])
patched = clone / "method/tools/self-conformance.py"
saved = patched.read_bytes()
results = {}
try:
    for tag, source in (("original", original.read_bytes()), ("ECO-105", saved)):
        patched.write_bytes(source)
        started = time.time()
        done = subprocess.run([sys.executable, str(patched)], cwd=clone, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        elapsed = time.time() - started
        lines = [re.sub(r"[A-Za-z]:\\[^\s)]*|/tmp/\S*", "<path>", line) for line in done.stdout.splitlines()
                 if not line.startswith("[env]") and not line.startswith("self-conformance: ")]
        results[tag] = (done.returncode, lines, elapsed)
        print(f"{tag}: exit {done.returncode}, {elapsed:.1f} s, {len(lines)} lines", flush=True)
finally:
    patched.write_bytes(saved)
same = results["original"][:2] == results["ECO-105"][:2]
print(f"same exit code and check lines: {same}")
if not same:
    import difflib
    print("\n".join(difflib.unified_diff(results["original"][1], results["ECO-105"][1], lineterm="", n=0)))
