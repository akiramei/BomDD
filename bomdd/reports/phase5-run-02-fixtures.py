# Phase 5 run-02 治具生成(設計= phase5-run-02-design.md・commit 後の clean tree で実行する)
#   python bomdd/reports/phase5-run-02-fixtures.py <self-conformance ログの座標(例: scratchpad/selfconf-36.log task xxx)>
# 生成先: .git/bomdd-witness/phase5-run02/r1〜r8.json(作業木外)。正解表(decision/CODE)を検証器で確認して exit 0/1。
import json
import shutil
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
wdir = root / ".git" / "bomdd-witness"
out = wdir / "phase5-run02"
tool = root / "method" / "tools" / "bomdd-witness.py"
KW = dict(cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace")


def run(*args):
    return subprocess.run(list(args), **KW)


src_coord = sys.argv[1] if len(sys.argv) > 1 else None
if not src_coord:
    print("usage: <self-conformance ログの座標>")
    sys.exit(2)
st = run("git", "status", "--porcelain").stdout
if st.strip():
    print("worktree not clean:\n" + st)
    sys.exit(2)
if out.exists():
    shutil.rmtree(out)
out.mkdir(parents=True)

# r1: 現 tree の実 witness(produce・作業木外へ)
r = run(sys.executable, str(tool), "produce", "--eco", "ECO-066", "--gate", f"self-conformance=0:{src_coord}",
        "--out", str(out / "r1.json"), "--producer", "claude-fable-5-1 / Claude Code (self-reported)")
print(r.stdout.strip())
assert r.returncode == 0, r.stdout
good = json.loads((out / "r1.json").read_text(encoding="utf-8"))
tree = good["tree"]
w65 = json.loads((wdir / "ECO-065.json").read_text(encoding="utf-8"))
assert w65["tree"] != tree
real_gate = dict(good["gates"][0])


def base(eco, **kw):
    d = dict(good, witness=f"WIT-{eco}", eco=eco, gates=[dict(real_gate)])
    d.update(kw)
    return d


fx = {
    "r2": dict(w65),
    "r3": dict(good),
    "r4": base("ECO-063", gates=[dict(real_gate), {"name": "kit-freshness", "exit": 1, "source": "scratchpad/kitfresh-4.log"}], verdict="PASS"),
    "r5": base("ECO-064", gates=[], status="PASS"),
    "r6": base("ECO-065", tree=tree[:-4] + ("0000" if tree[-4:] != "0000" else "1111"), verified_by="self-conformance PASS"),
    "r7": base("ECO-055", stop_type="LEDGER_INCONSISTENT"),
    "r8": base("ECO-063"),
}
for k, v in fx.items():
    (out / f"{k}.json").write_text(json.dumps(v, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

jobs = {"r1": "ECO-066", "r2": "ECO-065", "r3": "ECO-062", "r4": "ECO-063", "r5": "ECO-064", "r6": "ECO-065", "r7": "ECO-055", "r8": "ECO-063"}
expect = {"r1": (0, "OK"), "r2": (1, "TREE_MISMATCH"), "r3": (1, "IDENTITY_MISMATCH"), "r4": (1, "GATE_FAIL"),
          "r5": (1, "GATES_MISSING"), "r6": (1, "TREE_MISMATCH"), "r7": (1, "STOP_TYPE"), "r8": (0, "OK")}
ok = True
for k, eco in jobs.items():
    r = run(sys.executable, str(tool), "verify", str(out / f"{k}.json"), "--eco", eco)
    line = r.stdout.strip().splitlines()[0] if r.stdout.strip() else ""
    code = line.split(":", 1)[0].split()[1].split("(")[0] if line else "?"
    good_ = (r.returncode, code) == expect[k] and (k != "r6" or "最初の差分位置 36" in line)
    ok &= good_
    print(f"{k} {eco} exit={r.returncode} code={code} expect={expect[k]} {'OK' if good_ else 'MISMATCH'} :: {line[:110]}")
r = run(sys.executable, str(tool), "verify", str(out / "r3.json"))
print(f"r3 without --eco: exit={r.returncode} :: {r.stdout.strip()[:80]}")
ok &= r.returncode == 2
print("ground truth", "OK" if ok else "MISMATCH")
sys.exit(0 if ok else 1)
