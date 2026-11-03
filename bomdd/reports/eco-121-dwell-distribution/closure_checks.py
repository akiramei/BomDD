"""ECO-121 V1 and V4 at each product's applied commit, read from git (no working tree).

  python -X utf8 closure_checks.py [<repos-root>]     exit 0 = every V1 count rises from 0 and every path is classified

V1: per file, the number of lines containing `waiting_on` at the product ECO's base and at its applied commit (0 -> at least 1);
change-management also names `paused`, `resume_when` and `bomdd-job.py --dwell`.
V4: every path changed between base and applied, with the class of section 2's product side it falls in. A path in no class is
printed as OUTSIDE and fails the run.
"""
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[4])
PRODUCTS = {
    "ViewPrism2": {
        "base": "82c362e", "applied": "9bdbe91",
        "cm": "bomdd/change-management.md",
        "skills": [".claude/skills/eco-file/SKILL.md", ".claude/skills/eco-fix/SKILL.md", ".claude/skills/eco-accept/SKILL.md"],
        "classes": {
            "register": ["bomdd/60-change-register.yaml"],
            "change-management": ["bomdd/change-management.md"],
            "eco-file/eco-fix/eco-accept": [".claude/skills/eco-file/", ".claude/skills/eco-fix/", ".claude/skills/eco-accept/"],
            "its own ECO records": ["bomdd/60-change-order-eco-149.md", "bomdd/51-cheat-log.md"],
        },
    },
    "ViewTube": {
        "base": "62d2b3e4", "applied": "42936d96",
        "cm": "bomdd/process/change-management.md",
        "skills": [".agents/skills/eco-file/SKILL.md", ".agents/skills/eco-fix/SKILL.md", ".agents/skills/eco-accept/SKILL.md"],
        "classes": {
            "register": ["bomdd/process/change-register.yaml"],
            "change-management": ["bomdd/process/change-management.md"],
            "eco-file/eco-fix/eco-accept": [".agents/skills/eco-file/", ".agents/skills/eco-fix/", ".agents/skills/eco-accept/"],
            "its own ECO records": ["bomdd/eco/ECO-VT-273", "bomdd/process/change-impact/ECO-VT-273.yaml",
                                    "test-results/eco-vt-273-", "bomdd/51-cheat-log.md",
                                    "bomdd/process/release-workflow-policy.yaml"],
        },
    },
}


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8").stdout


def count(repo, rev, path, word):
    return sum(word in line for line in git(repo, "show", f"{rev}:{path}").splitlines())


ok = True
for name, p in PRODUCTS.items():
    repo = root / name
    print(f"== {name}  base {p['base']}  applied {p['applied']}")
    for path in [p["cm"], *p["skills"]]:
        a, b = count(repo, p["base"], path, "waiting_on"), count(repo, p["applied"], path, "waiting_on")
        good = a == 0 and b >= 1
        ok &= good
        print(f"V1 {'PASS' if good else 'FAIL'}  waiting_on {a} -> {b}  {path}")
    for word in ("paused", "resume_when", "bomdd-job.py --dwell"):
        n = count(repo, p["applied"], p["cm"], word)
        ok &= n >= 1
        print(f"V1 {'PASS' if n >= 1 else 'FAIL'}  change-management names {word!r} ({n} lines)")
    for path in git(repo, "diff", "--name-only", p["base"], p["applied"]).split():
        cls = next((c for c, prefixes in p["classes"].items() if any(path.startswith(x) for x in prefixes)), None)
        ok &= cls is not None
        print(f"V4 {cls or 'OUTSIDE'}  {path}")
print("ALL PASS" if ok else "FAILED")
sys.exit(0 if ok else 1)
