"""ECO-126 V5 — the text, and what the diff touches.

usage: v5_text.py <BomDD root> <filing commit>
Compares the working tree with the filing commit. Exits 1 if any expectation fails.
"""
import subprocess
import sys
from pathlib import Path

import yaml

root, filing = Path(sys.argv[1]), sys.argv[2]
bad = []
# uncommitted records of the same session that are not this ECO's and are never staged with it
NOT_THIS_ECO = ("method/improvements.md", "bomdd/reports/count-survey-20261110/")


def git(*a):
    return subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def expect(label, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + label + (" — " + detail if detail else ""))
    if not ok:
        bad.append(label)


def added_removed(path):
    add, rem = [], []
    for line in git("diff", "--unified=0", filing, "--", path).splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            add.append(line[1:])
        elif line.startswith("-") and not line.startswith("---"):
            rem.append(line[1:])
    return add, rem


P = "method/templates/product-profile/"

# eco-fix: steps 1-3.6 untouched; the only change is the pointer in the stop section
add, rem = added_removed(P + "skills/eco-fix.md")
body = (root / P / "skills/eco-fix.md").read_text(encoding="utf-8")
old = git("show", f"{filing}:{P}skills/eco-fix.md")
steps_new = body.split("## 手順", 1)[1].split("## 停止点", 1)[0]
steps_old = old.split("## 手順", 1)[1].split("## 停止点", 1)[0]
expect("eco-fix: the steps section (steps 1-5) is identical character for character (line ends normalised to LF)",
       steps_new.replace("\r\n", "\n") == steps_old.replace("\r\n", "\n") and len(steps_new) > 2000, f"{len(steps_new)} chars")
expect("eco-fix: the diff is the pointer only (no line removed)",
       not rem and len([a for a in add if a.strip()]) == 1 and "/eco-turn" in "".join(add), f"+{len(add)} -{len(rem)}")

for name in ("skills/eco-accept.md", "skills/eco-file.md"):
    add, rem = added_removed(P + name)
    expect(f"{name}: one line added, none removed", not rem and len(add) == 1 and "§3.5" in add[0], f"+{len(add)} -{len(rem)}")
add, rem = added_removed(P + "skills/bomdd-next.md")
expect("bomdd-next: one line changed, the old text kept inside it",
       len(add) == 1 and len(rem) == 1 and rem[0].rstrip(" |") in add[0], f"+{len(add)} -{len(rem)}")

# change-management: nothing removed; R3 / R4 / R6 gain only the clauses the rulings decided
add, rem = added_removed(P + "change-management.md")
expect("change-management: no line removed", not rem, f"+{len(add)} -{len(rem)}")
cm_old = git("show", f"{filing}:{P}change-management.md")
cm_new = (root / P / "change-management.md").read_text(encoding="utf-8")
sec2_old = cm_old.split("## 2. 共通規律", 1)[1].split("## 3. シナリオ別経路", 1)[0].splitlines()
sec2_new = cm_new.split("## 2. 共通規律", 1)[1].split("## 3. シナリオ別経路", 1)[0].splitlines()
extra = [l for l in sec2_new if l not in sec2_old]
expect("section 2 (R1-R8): every old line is still there, in order", [l for l in sec2_new if l in sec2_old] == sec2_old)
expect("section 2: five lines added, each carrying a marker word of the RP1 clause (R4) or the RP4 clauses (R3, R6) — a count and keywords, not a reading",
       len(extra) == 5 and all("§3.5" in l or "種類" in l or "確認項目(合否)" in l or "例外の外" in l for l in extra),
       f"{len(extra)} added lines")
expect("the route section exists once", cm_new.count("### 3.5 周で回す変更") == 1 and "先に伺う 5 つ" in cm_new)

# what the diff touches
changed = [l.split("\t")[-1] for l in git("diff", "--name-only", filing).splitlines() if l.strip()]
untracked = [l for l in git("ls-files", "--others", "--exclude-standard").splitlines() if l.strip()]
mine = [p for p in changed + untracked if not p.startswith(NOT_THIS_ECO)]
reg = yaml.safe_load((root / "bomdd/60-change-register.yaml").read_text(encoding="utf-8"))
entries = reg["changes"] if isinstance(reg, dict) and "changes" in reg else next(v for v in reg.values() if isinstance(v, list))
allowed = next(e for e in entries if e.get("id") == "ECO-126")["diff_audit"]["allowed_paths"]
outside = [p for p in mine if not any(p == a or (a.endswith("/") and p.startswith(a)) for a in allowed)]
expect("every changed or new path of this ECO is inside allowed_paths", not outside, f"{len(mine)} paths; outside: {outside}")
expect("nothing under method/templates/process-core/ changed",
       not [p for p in changed + untracked if p.startswith("method/templates/process-core/")])
expect("method/bomdd-playbook-v1.md unchanged", "method/bomdd-playbook-v1.md" not in changed)
print("paths of this ECO:", ", ".join(sorted(mine)))
left = [p for p in changed + untracked if p.startswith(NOT_THIS_ECO)]
print(f"left out (not this ECO's, never staged with it): {len(left)} paths under {', '.join(NOT_THIS_ECO)}")

print("V5:", "FAILED " + str(bad) if bad else "all as expected")
sys.exit(1 if bad else 0)
