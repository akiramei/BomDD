#!/usr/bin/env python3
"""ECO-115's diff window at closure: every commit from the register's diff_audit.baseline to the head is ECO-115's, and every path any of them
changed is inside the register entry's diff_audit.allowed_paths. Read only.

  python -B diff_window.py <BomDD root> <baseline> <head> [--control-drop <allowed path>]

A commit is ECO-115's when its subject starts with file(eco-115), fix(eco-115), record(eco-115) or accept(eco-115); any other commit in the window
fails the check (no exception ruling applies to this ECO). --control-drop removes one allowed path, as a positive control that must FAIL.
Prints a Markdown report; exit 0 on PASS, 1 on FAIL.
"""
import subprocess
import sys

import yaml

sys.stdout.reconfigure(encoding="utf-8", newline="\n")  # a report line must never stop on the console encoding (cp932)
root, base, head = sys.argv[1:4]
drop = sys.argv[sys.argv.index("--control-drop") + 1] if "--control-drop" in sys.argv else None


def git(*args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, encoding="utf-8", check=True).stdout


reg = yaml.safe_load(git("show", f"{head}:bomdd/60-change-register.yaml"))
entry = next(e for e in reg["changes"] if e["id"] == "ECO-115")
allowed = [p for p in entry["diff_audit"]["allowed_paths"] if p != drop]
commits = git("rev-list", "--reverse", f"{base}..{head}").split()
lines = [f"# ECO-115 diff window — `{base}..{head}`{' (control: ' + drop + ' dropped)' if drop else ''}", "",
         f"Allowed paths (register at `{head[:7]}`{', one dropped' if drop else ''}): " + ", ".join(f"`{p}`" for p in allowed), "",
         "| # | commit | ECO-115's | paths | outside the allowed paths |", "|---|---|---|---|---|"]
fails = []
for n, c in enumerate(commits, 1):
    subject = git("log", "-1", "--format=%s", c).strip()
    own = subject.startswith(("file(eco-115)", "fix(eco-115)", "record(eco-115)", "accept(eco-115)"))
    paths = [p for p in git("diff-tree", "--no-commit-id", "--name-only", "-r", c).split("\n") if p]
    outside = [p for p in paths if not any(p == a or (a.endswith("/") and p.startswith(a)) for a in allowed)]
    if not own:
        fails.append(f"`{c[:7]}` is not ECO-115's: {subject[:80]}")
    fails += [f"`{c[:7]}` changed `{p}`, outside the allowed paths" for p in outside]
    lines.append(f"| {n} | `{c[:7]}` | {'yes' if own else 'NO'} | {len(paths)} | {', '.join(outside) or 'none'} |")
total = sorted({p for c in commits for p in git("diff-tree", "--no-commit-id", "--name-only", "-r", c).split("\n") if p})
lines += ["", f"{len(commits)} commits, {len(total)} distinct paths.", "", "## Result", ""]
lines += [f"- {f}" for f in fails] or ["- none outside; every commit ECO-115's"]
lines += ["", f"**{'PASS' if not fails else 'FAIL'}**"]
print("\n".join(lines))
sys.exit(0 if not fails else 1)
