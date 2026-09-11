import json
import shutil
import subprocess
import sys
from pathlib import Path

root = Path(r"C:\Users\akira\source\repos\BomDD")
wdir = root / ".git" / "bomdd-witness"
out = wdir / "phase5"
if out.exists():
    shutil.rmtree(out)
out.mkdir(parents=True)

cur = subprocess.run(["git", "-C", str(root), "write-tree"], capture_output=True, text=True)
# write-tree on the real index equals worktree tree only when clean; assert clean first
st = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True).stdout
assert st.strip() == "", "worktree not clean"
tree = cur.stdout.strip()
w65 = json.loads((wdir / "ECO-065.json").read_text(encoding="utf-8"))
w64 = json.loads((wdir / "ECO-064.json").read_text(encoding="utf-8"))
assert w65["tree"] == tree, (w65["tree"], tree)
assert w64["tree"] != tree
head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
real_gate = dict(w65["gates"][0])  # self-conformance exit 0, real source (selfconf-27 on this tree)
producer = w65["producer"]


def base(eco, **kw):
    d = {"witness": f"WIT-{eco}", "eco": eco, "tree": tree, "tree_definition": w65["tree_definition"],
         "head": head, "gates": [dict(real_gate)], "stop_type": "NONE", "producer": producer,
         "produced_at": "2026-09-11"}
    d.update(kw)
    return d


fx = {}
fx["r1"] = dict(w65)                                           # known-good (real copy)
fx["r2"] = dict(w64)                                           # stale tree (real copy)
fx["r3"] = dict(w65)                                           # identity mismatch: job=ECO-062, witness eco=ECO-065
fx["r4"] = base("ECO-063", gates=[dict(real_gate), {"name": "kit-freshness", "exit": 1, "source": "scratchpad/kitfresh-3.log"}],
                verdict="PASS")                                # FAIL 混入 + decoy
fx["r5"] = base("ECO-062", gates=[], status="PASS")            # 欠測 + decoy
t6 = tree[:-4] + ("0000" if tree[-4:] != "0000" else "1111")
fx["r6"] = base("ECO-064", tree=t6, verified_by="self-conformance PASS")   # hash 改変 + decoy
fx["r7"] = base("ECO-055", stop_type="LEDGER_INCONSISTENT")    # ruling required
fx["r8"] = base("ECO-063")                                     # known-good (fabricated but valid)

for k, v in fx.items():
    (out / f"{k}.json").write_text(json.dumps(v, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

# ground-truth check with the verifier (with job identity binding)
jobs = {"r1": "ECO-065", "r2": "ECO-064", "r3": "ECO-062", "r4": "ECO-063", "r5": "ECO-062", "r6": "ECO-064", "r7": "ECO-055", "r8": "ECO-063"}
expect = {"r1": 0, "r2": 1, "r3": 1, "r4": 1, "r5": 1, "r6": 1, "r7": 1, "r8": 0}
ok = True
for k, eco in jobs.items():
    r = subprocess.run([sys.executable, "method/tools/bomdd-witness.py", "verify", str(out / f"{k}.json"), "--eco", eco],
                       cwd=root, capture_output=True, text=True, encoding="utf-8")
    flag = "OK" if r.returncode == expect[k] else "MISMATCH"
    if flag != "OK":
        ok = False
    print(f"{k} {eco} exit={r.returncode} expect={expect[k]} {flag} :: {r.stdout.strip()}")
# r3 without --eco would ADVANCE (the trap) — record
r = subprocess.run([sys.executable, "method/tools/bomdd-witness.py", "verify", str(out / "r3.json")],
                   cwd=root, capture_output=True, text=True, encoding="utf-8")
print(f"r3 without --eco: exit={r.returncode} :: {r.stdout.strip()}")
print("ground truth", "OK" if ok else "MISMATCH")
sys.exit(0 if ok else 1)
