"""ECO-126 closure — the diff window, read from git objects only (the working tree is not read).

usage: window126.py <BomDD root> <baseline> <head> [--drop PATH]

For every commit in <baseline>..<head>: its subject must name eco-126, and every path it touches must be inside
`diff_audit.allowed_paths` of ECO-126 as the register reads at <head>. `--drop PATH` removes one allowed path before the
check (the control: the run must then fail on the commits that touch it).
Prints one line per commit and a summary; exits 1 if any commit fails, 2 if the window cannot be read.
"""
import subprocess
import sys
from pathlib import Path

import yaml

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

args = sys.argv[1:]
drop = None
if "--drop" in args:
    i = args.index("--drop")
    drop = args[i + 1]
    del args[i:i + 2]
if len(args) != 3:
    print(__doc__)
    sys.exit(2)
root, baseline, head = Path(args[0]), args[1], args[2]


def git(*a):
    p = subprocess.run(["git", "-C", str(root), "-c", "core.quotepath=false", *a],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        print(f"UNREADABLE git {' '.join(a)}: {p.stderr.strip()[:200]}")
        sys.exit(2)
    return p.stdout


reg = yaml.safe_load(git("show", f"{head}:bomdd/60-change-register.yaml"))
entry = [c for c in reg["changes"] if c.get("id") == "ECO-126"]
if len(entry) != 1:
    print(f"UNREADABLE register: {len(entry)} entries with id ECO-126")
    sys.exit(2)
allowed = list(entry[0]["diff_audit"]["allowed_paths"])
if drop is not None:
    if drop not in allowed:
        print(f"UNREADABLE --drop {drop}: not in allowed_paths")
        sys.exit(2)
    allowed.remove(drop)


def inside(path):
    return any(path == a or (a.endswith("/") and path.startswith(a)) for a in allowed)


commits = git("rev-list", "--reverse", f"{baseline}..{head}").split()
if not commits:
    print("UNREADABLE window: no commit between baseline and head")
    sys.exit(2)
print(f"window {baseline}..{head}: {len(commits)} commits; allowed_paths {len(allowed)}"
      + (f" (control: `{drop}` dropped)" if drop else ""))
bad = 0
for c in commits:
    subject = git("log", "-1", "--format=%s", c).strip()
    paths = [p for p in git("diff-tree", "--no-commit-id", "--name-only", "-r", c).splitlines() if p]
    out = [p for p in paths if not inside(p)]
    named = "(eco-126)" in subject.lower()
    ok = named and not out and bool(paths)
    bad += 0 if ok else 1
    print(("PASS " if ok else "FAIL ") + f"{c[:7]} paths {len(paths)} outside {len(out)} names eco-126: {'yes' if named else 'no'}"
          + ("" if not out else " — " + ", ".join(out[:5]) + (" …" if len(out) > 5 else "")))
whole = [p for p in git("diff", "--name-only", baseline, head).splitlines() if p]
whole_out = [p for p in whole if not inside(p)]
print(f"whole window: {len(whole)} paths, outside {len(whole_out)}")
verdict = bad == 0 and not whole_out
print("WINDOW: " + ("PASS" if verdict else f"FAIL ({bad} commits; {len(whole_out)} paths outside)"))
sys.exit(0 if verdict else 1)
