"""ECO-118 closure: the diff window. Lists the paths each ECO-118 commit touched, checks them against the register's
allowed_paths, and lists the one commit in the range that belongs to another ECO (ECO-119's filing). Read only.

usage: python window118.py   (from the BomDD root; writes out/window.txt)
"""
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "out"
ECO118 = ["3a71807", "9cc108b", "f8b4891", "ea2ac97", "8461c7f", "9724877", "d355f62", "dcebc2e"]
OTHER = {"94a2a2a": "ECO-119's filing (its own order and register entry)"}


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, encoding="utf-8", check=True).stdout


def main():
    reg = yaml.safe_load((ROOT / "bomdd/60-change-register.yaml").read_text(encoding="utf-8"))
    entry = next(c for c in reg["changes"] if c.get("id") == "ECO-118")
    allowed = entry["diff_audit"]["allowed_paths"]
    lines = ["# ECO-118 diff window", f"allowed_paths: {allowed}"]
    rng = git("rev-list", "--reverse", "a3b3cc1..dcebc2e").split()
    lines.append(f"commits in a3b3cc1..dcebc2e: {len(rng)}")
    union = set()
    for sha in rng:
        short = sha[:7]
        paths = [p for p in git("show", "--name-only", "--format=", sha).splitlines() if p]
        if short in OTHER:
            lines.append(f"  {short} NOT ECO-118 - {OTHER[short]}: {paths}")
            continue
        assert short in ECO118, f"unexpected commit {short}"
        union |= set(paths)
        lines.append(f"  {short} ECO-118: {len(paths)} paths")
    outside = sorted(p for p in union if not any(p == a or (a.endswith("/") and p.startswith(a)) for a in allowed))
    lines.append(f"paths touched by ECO-118's commits: {len(union)}")
    lines += [f"  {p}" for p in sorted(union) if not p.startswith("bomdd/reports/eco-118-bom-structure-check/")]
    lines.append(f"  + {sum(1 for p in union if p.startswith('bomdd/reports/eco-118-bom-structure-check/'))} under bomdd/reports/eco-118-bom-structure-check/")
    lines.append(f"outside allowed_paths: {outside or 'none'}")
    OUT.mkdir(exist_ok=True)
    (OUT / "window.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    return 0 if not outside else 1


if __name__ == "__main__":
    sys.exit(main())
