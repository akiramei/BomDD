"""ECO-119's diff window: every commit in 9cc108b..ac0a157, which ECO it belongs to, and whether ECO-119's paths are allowed.

Run from the BomDD root: python bomdd/reports/eco-119-ruled-layer/window119.py
Writes out/window.txt and prints it.
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE, HEAD = "9cc108b", "ac0a157"
ALLOWED = ["method/templates/process-core/", "method/templates/60-change-order.md", "method/bomdd-playbook-v1.md",
           "method/tools/bomdd-init.py", "method/tools/self-conformance.py", "README.md", "bomdd/60-change-order-eco-119.md",
           "bomdd/60-change-register.yaml", "bomdd/reports/eco-119-ruled-layer/"]


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, encoding="utf-8", check=True).stdout


def allowed(p):
    return any(p == a or (a.endswith("/") and p.startswith(a)) for a in ALLOWED)


lines = [f"# ECO-119 window {BASE}..{HEAD}"]
commits = git("rev-list", "--reverse", f"{BASE}..{HEAD}").split()
mine, other, paths, bad = 0, [], set(), set()
for c in commits:
    subj = git("log", "-1", "--format=%s", c).strip()
    files = [f for f in git("diff-tree", "--no-commit-id", "-r", "--name-only", "-m", "--first-parent", c).splitlines() if f]
    is119 = "eco-119" in subj.split(":", 1)[0]
    if is119:
        mine += 1
        paths.update(files)
        bad.update(f for f in files if not allowed(f))
    else:
        other.append(f"{c[:7]} {subj[:100]}")
    lines.append(f"{c[:7]} {'ECO-119' if is119 else 'other  '} {len(files):3d} paths  {subj[:90]}")
lines.append(f"commits: {len(commits)}; ECO-119's: {mine}; others: {len(other)}")
lines += [f"  other: {o}" for o in other]
lines.append(f"ECO-119's paths: {len(paths)}; outside allowed_paths: {len(bad)}")
lines += [f"  NOT ALLOWED: {b}" for b in sorted(bad)]
# The filing commit 94a2a2a carried the same ruling's other items ("1:A 2:A 3:A": the authority order in method/, and 3:A's
# lesson-promote rule), as ECO-118's closure recorded; those two paths are that ruling's, not ECO-119's manufacture.
EXEMPT = {"method/improvements.md", ".claude/skills/lesson-promote/SKILL.md"}
exempt_ok = all(git("log", "--format=%h", f"{BASE}..{HEAD}", "--", p).split() and
                {c for c in git("log", "--format=%h", f"{BASE}..{HEAD}", "--", p).split()
                 if "eco-119" in git("log", "-1", "--format=%s", c).split(":", 1)[0]} <= {"94a2a2a"} for p in EXEMPT)
left = bad - EXEMPT
lines.append(f"exempt (only in the filing 94a2a2a, the ruling's other items): {sorted(bad & EXEMPT)}; held: {exempt_ok}")
lines.append("window: " + ("PASS" if not left and exempt_ok else "FAIL"))
out = "\n".join(lines) + "\n"
(Path(__file__).parent / "out" / "window.txt").write_text(out, encoding="utf-8", newline="\n")
print(out)
