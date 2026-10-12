"""What makes up the 260 MB record surface validate_machinery_claims.py reads (ViewTube HEAD, read-only)."""
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
VT = Path(r"C:\Users\akira\source\repos\ViewTube")
sys.path.insert(0, str(VT / "bomdd" / "tools"))
import validate_machinery_claims as gate  # noqa: E402

policy = gate.load_policy(VT)
surface = gate.record_surface(VT, policy)
tracked = set(subprocess.run(["git", "-C", str(VT), "ls-files"], capture_output=True, text=True,
                             encoding="utf-8").stdout.splitlines())
by_suffix = defaultdict(lambda: [0, 0])
untracked = [0, 0]
big = []
for path in surface:
    size = path.stat().st_size
    by_suffix[path.suffix][0] += 1
    by_suffix[path.suffix][1] += size
    relative = path.relative_to(VT).as_posix()
    if relative not in tracked:
        untracked[0] += 1
        untracked[1] += size
    big.append((size, relative))
for suffix, (count, size) in sorted(by_suffix.items(), key=lambda item: -item[1][1]):
    print(f"{suffix:6} {count:5} files {size / 1e6:8.1f} MB")
print(f"untracked (not in git): {untracked[0]} files {untracked[1] / 1e6:.1f} MB")
big.sort(reverse=True)
print(f"largest 20 files hold {sum(size for size, _ in big[:20]) / 1e6:.1f} MB:")
for size, relative in big[:10]:
    print(f"  {size / 1e6:7.1f} MB  {relative}")
over_1mb = [item for item in big if item[0] > 1e6]
print(f"files over 1 MB: {len(over_1mb)} holding {sum(size for size, _ in over_1mb) / 1e6:.1f} MB")
