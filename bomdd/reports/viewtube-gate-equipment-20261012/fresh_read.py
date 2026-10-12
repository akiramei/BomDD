"""Is the first read of freshly written files slow on this machine?

The gate's validators ran 34-44 s on the first read of a fresh tree and 7-12 s on a re-read. This
copies the 5,195-file record surface (260 MB) into a new temporary directory and times reading every
file three times: right after writing, again, and again. Nothing is written to ViewTube."""
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
VT = Path(r"C:\Users\akira\source\repos\ViewTube")
sys.path.insert(0, str(VT / "bomdd" / "tools"))
import validate_machinery_claims as gate  # noqa: E402

policy = gate.load_policy(VT)
surface = gate.record_surface(VT, policy)
with tempfile.TemporaryDirectory(prefix="fresh-read-") as temp:
    target = Path(temp)
    started = time.perf_counter()
    copies = []
    for path in surface:
        destination = target / path.relative_to(VT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        copies.append(destination)
    print(f"wrote {len(copies)} files in {time.perf_counter() - started:.1f}s")
    for attempt in range(1, 4):
        started = time.perf_counter()
        total = sum(len(open(path, "rb").read()) for path in copies)
        print(f"read pass {attempt}: {time.perf_counter() - started:.2f}s ({total / 1e6:.0f} MB)")
started = time.perf_counter()
total = sum(len(open(path, "rb").read()) for path in surface)
print(f"read of the same files in the ViewTube working tree: {time.perf_counter() - started:.2f}s")
