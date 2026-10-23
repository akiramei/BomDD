"""ECO-115 basis: whether the two products carry the inputs the decision's freeze check reads (the work order's frozen-revision line, the As-Built
entry's references), read-only.

Usage: python measure_freeze.py <ViewPrism2 repo> <ViewTube repo> <out file>
Reads bomdd/40-work-order.md and bomdd/50-as-built.yaml at each repo's HEAD with `git show`, and whether they are tracked (git ls-files).
"""
import re
import subprocess
import sys


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, encoding="utf-8")


def survey(out, name, repo):
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    out.append(f"== {name} at {head}")
    for path in ("bomdd/40-work-order.md", "bomdd/50-as-built.yaml"):
        tracked = bool(git(repo, "ls-files", path).stdout.strip())
        text = git(repo, "show", f"HEAD:{path}").stdout if tracked else ""
        out.append(f"  {path}: tracked {tracked}; last changed {git(repo, 'log', '-1', '--format=%h %cs', '--', path).stdout.strip() or '-'}")
        if path.endswith("40-work-order.md"):
            lines = re.findall(r"^- 対象 BOM tag/commit:.*$", text, re.MULTILINE)
            out.append(f"    frozen-revision lines '- 対象 BOM tag/commit:': {len(lines)} {lines[:2]}")
        else:
            out.append(f"    entries with mbom_ref: {len(re.findall(r'^\s+mbom_ref:', text, re.MULTILINE))}; with control_plan_ref: "
                       f"{len(re.findall(r'^\s+control_plan_ref:', text, re.MULTILINE))}; with work_order_ref: "
                       f"{len(re.findall(r'^\s+work_order_ref:', text, re.MULTILINE))}")


def main():
    vp2, vt, path = sys.argv[1:4]
    out = []
    survey(out, "ViewPrism2", vp2)
    survey(out, "ViewTube", vt)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
