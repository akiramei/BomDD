"""ECO-126 — the three GU7 repairs made after the inspector's last round: does the self-test fail when each is removed?

usage: gu7_mutants.py <BomDD root> <scratch dir>
Copies ui-cad-gate.py under other names in the scratch folder, disables one check in each copy, runs its --selftest.
Exits 1 if a mutant's self-test stays green, or does not name the arm of the disabled check.
"""
import subprocess
import sys
from pathlib import Path

root, scratch = Path(sys.argv[1]), Path(sys.argv[2])
src = (root / "method" / "tools" / "ui-cad-gate.py").read_text(encoding="utf-8")
scratch.mkdir(parents=True, exist_ok=True)
MUT = [
    ("IB-01 an empty member of the list", "        if len(targets) != len(members):", "        if False:", "IB-01"),
    ("IB-02 a ruling naming itself", '            if cid == str(r.get("id")):', "            if False:", "IB-02"),
    ("ruled, but not by the user", '        if r.get("status") == "ruled" and r.get("decided_by") != "user":', "        if False:",
     "裁定したのが人でない"),
]
bad = []
base = subprocess.run([sys.executable, str(root / "method" / "tools" / "ui-cad-gate.py"), "--selftest"], capture_output=True,
                      text=True, encoding="utf-8", errors="replace")
print(("PASS " if base.returncode == 0 else "FAIL ") + f"the unchanged tool's self-test — exit {base.returncode}")
if base.returncode != 0:
    bad.append("base")
for label, old, new, arm in MUT:
    if src.count(old) != 1:
        print(f"FAIL {label}: the line to disable is not found exactly once ({src.count(old)})")
        bad.append(label)
        continue
    m = scratch / ("gate-mutant-" + arm.encode("ascii", "ignore").decode() + f"-{len(bad)}{MUT.index((label, old, new, arm))}.py")
    m.write_text(src.replace(old, new), encoding="utf-8", newline="\n")
    r = subprocess.run([sys.executable, str(m), "--selftest"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    named = [seg for seg in r.stdout.split(" / ") if arm in seg]
    ok = r.returncode == 1 and len(named) == 1 and r.stdout.count("known-") == 1
    print(("PASS " if ok else "FAIL ") + f"{label} disabled: self-test exit {r.returncode}, failing arms {r.stdout.count('known-')}, names its arm {bool(named)}")
    if not ok:
        bad.append(label)
print("GU7 mutants:", "FAILED " + str(bad) if bad else "each disabled check turns exactly its own arm red")
sys.exit(1 if bad else 0)
