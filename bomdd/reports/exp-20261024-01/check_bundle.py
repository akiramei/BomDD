#!/usr/bin/env python3
"""Every MoviePad-Remake commit that BomDD's records name is in the kept bundle (README.md in this folder).

  python bomdd/reports/exp-20261024-01/check_bundle.py <scratch directory>

Clones MoviePad-Remake.bundle (next to this script) into a new folder under <scratch directory>, collects every 7- to 40-digit hex
token on the lines of method/improvements.md, FINDINGS.md and method/bomdd-playbook-v1.md that name MoviePad-Remake (and on
the lines after such a line up to the next blank line), and resolves each as a commit in the clone. A token that resolves is a
cited commit; one that does not is listed (most are sha256 prefixes or other repositories' commits — read the list). Run from
the BomDD repository root. Exit 1 if the bundle does not verify or no cited commit is found.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE / "MoviePad-Remake.bundle"
HEX = re.compile(r"(?<![0-9a-fA-F])[0-9a-f]{7,40}(?![0-9a-fA-F])")
sys.stdout.reconfigure(encoding="utf-8")


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")


if git("bundle", "verify", str(BUNDLE)).returncode != 0:
    sys.exit("the bundle does not verify")
# a new folder each run: git's pack files are read-only on Windows, so an earlier clone is not removed here
clone = Path(tempfile.mkdtemp(prefix="bundle-check-", dir=Path(sys.argv[1]).resolve()))
git("clone", "-q", "--mirror", str(BUNDLE), str(clone))
tokens = {}
for doc in ("method/improvements.md", "FINDINGS.md", "method/bomdd-playbook-v1.md"):
    inside = False
    for n, line in enumerate(Path(doc).read_text(encoding="utf-8").splitlines(), 1):
        if "MoviePad-Remake" in line:
            inside = True
        elif not line.strip():
            inside = False
        if inside:
            for t in HEX.findall(line):
                tokens.setdefault(t, f"{doc}:{n}")
found, other = [], []
for t, where in sorted(tokens.items()):
    (found if git("cat-file", "-e", f"{t}^{{commit}}", cwd=clone).returncode == 0 else other).append((t, where))
print(f"bundle verifies; commits in the clone: {len(git('rev-list', '--all', cwd=clone).stdout.split())}")
print(f"hex tokens near 'MoviePad-Remake' in the records: {len(tokens)}; commits found in the bundle: {len(found)}; not commits there: {len(other)}")
for t, where in other:
    print(f"  not a commit in the bundle: {t} ({where})")
sys.exit(0 if found else 1)
