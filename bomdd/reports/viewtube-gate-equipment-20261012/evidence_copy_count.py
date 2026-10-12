"""Count what copy_registered_evidence (selftest_ui_manufacturing.py) copies, without copying.

The four harness runs each spent 1,066-1,247 s in their own Python between `git config
core.excludesFile` and `git add -A` - the stretch that reads the register, calls
copy_registered_evidence and rewrites one register entry. This reads ViewTube's committed register
(HEAD, through git show) and its working tree, uses the harness's own registered_evidence_paths, and
counts, for every registered evidence file under the evidence root, the directory it copies
(the file's whole parent, dirs_exist_ok=True) and the rglob it walks first.
Nothing is written."""
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8")
VT = Path(r"C:\Users\akira\source\repos\ViewTube")
sys.path.insert(0, str(VT / "bomdd" / "tools"))
os.environ.pop("VIEWTUBE_UI_MFG_CANDIDATE_ROOT", None)
import selftest_ui_manufacturing as harness  # noqa: E402  (module top level only defines names)

register = yaml.safe_load(subprocess.run(["git", "-C", str(VT), "show", "HEAD:bomdd/process/change-register.yaml"],
                                         check=True, capture_output=True).stdout.decode("utf-8"))
paths = harness.registered_evidence_paths(register)
prefix = f"{harness.EVIDENCE_ROOT_NAME}/"
under_root = [value for value in paths if value.startswith(prefix)]
present = [value for value in under_root if (VT / value).is_file()]
parents = Counter(str(Path(value).parent).replace("\\", "/") for value in present)


def tree_size(directory):
    files = 0
    size = 0
    for item in directory.rglob("*"):
        if item.is_file():
            files += 1
            size += item.stat().st_size
    return files, size


per_parent = {parent: tree_size(VT / parent) for parent in parents}
copies_files = sum(per_parent[parent][0] * count for parent, count in parents.items())
copies_bytes = sum(per_parent[parent][1] * count for parent, count in parents.items())
once_files = sum(files for files, _ in per_parent.values())
once_bytes = sum(size for _, size in per_parent.values())
print(f"evidence root: {harness.EVIDENCE_ROOT_NAME}")
print(f"registered evidence paths: {len(paths)}; under the evidence root: {len(under_root)}; present as files: {len(present)}")
print(f"distinct parent directories copied: {len(parents)}")
print(f"copytree calls (one per present file): {sum(parents.values())}")
print(f"files written across those calls: {copies_files:,} ({copies_bytes / 1e9:.2f} GB)")
print(f"files if each directory were copied once: {once_files:,} ({once_bytes / 1e9:.2f} GB)")
print("directories copied most often (times copied, files, MB):")
for parent, count in parents.most_common(8):
    files, size = per_parent[parent]
    print(f"  x{count:<4} {files:6,} files {size / 1e6:9.1f} MB  {parent}")

# Time one representative directory copy, to relate the counts to the measured seconds.
import shutil  # noqa: E402
import tempfile  # noqa: E402

parent, count = parents.most_common(1)[0]
with tempfile.TemporaryDirectory(prefix="evcopy-") as temp:
    started = time.perf_counter()
    shutil.copytree(VT / parent, Path(temp) / "x", dirs_exist_ok=True)
    first = time.perf_counter() - started
    started = time.perf_counter()
    shutil.copytree(VT / parent, Path(temp) / "x", dirs_exist_ok=True)
    again = time.perf_counter() - started
print(f"one copy of the most-copied directory: {first:.2f}s; the same copy over itself: {again:.2f}s")
