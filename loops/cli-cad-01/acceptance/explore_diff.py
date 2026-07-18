# 探索差分(受入の第 2 層 — 合否に使わない): 原品/再製品の出力を同一入力行列で採取し
# unified diff を吐く。分類(P1〜P3・帰属)は観測者が手で行う。
import difflib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIG = Path("C:/Users/akira/source/repos/BomDD/method/tools/worklist.py")
REPRO = HERE / "factory" / "worklist.py"
FIX = HERE / "inspector" / "kit" / "fixtures"
OUT = Path("C:/Users/akira/source/repos/BomDD/loops/cli-cad-01/acceptance/exploratory")
OUT.mkdir(parents=True, exist_ok=True)

CASES = {
    "f1": [str(FIX / "f1-normal.md")],
    "f1-full": [str(FIX / "f1-normal.md"), "--full"],
    "f2": [str(FIX / "f2-warnings.md")],
    "f3": [str(FIX / "f3-empty.md")],
    "f4": [str(FIX / "f4-no-marker.md")],
    "f5": [str(FIX / "f5-unaudited.md")],
    "show-hit": ["show", "EXP-20260601-01", str(FIX / "f1-normal.md")],
    "show-origin": ["show", "EXP-20260702-04", str(FIX / "f1-normal.md")],
    "show-miss": ["show", "EXP-NOPE-99", str(FIX / "f1-normal.md")],
    "show-noid": ["show"],
    "missing": [str(FIX / "does-not-exist.md")],
}


def run(script, args):
    p = subprocess.run([sys.executable, str(script)] + args,
                       capture_output=True, text=True, encoding="utf-8")
    return p


total_diff_lines = {}
for name, args in CASES.items():
    a, b = run(ORIG, args), run(REPRO, args)
    (OUT / f"{name}.orig.txt").write_text(a.stdout, encoding="utf-8")
    (OUT / f"{name}.repro.txt").write_text(b.stdout, encoding="utf-8")
    # elapsed_ms は未規定(U4)— 差分ノイズ除去のため正規化して比較
    def norm(s):
        return "\n".join(
            ("elapsed_ms: <U4>" if ln.startswith("elapsed_ms:") else ln.rstrip())
            for ln in s.splitlines())
    d = list(difflib.unified_diff(norm(a.stdout).splitlines(),
                                  norm(b.stdout).splitlines(),
                                  fromfile=f"orig/{name}", tofile=f"repro/{name}",
                                  lineterm=""))
    (OUT / f"{name}.diff").write_text("\n".join(d), encoding="utf-8")
    n = sum(1 for ln in d if ln[:1] in "+-" and ln[:3] not in ("+++", "---"))
    total_diff_lines[name] = (n, a.returncode, b.returncode,
                              len(a.stderr), len(b.stderr))

print(f"{'case':<14}{'difflines':>10}{'exit o/r':>10}{'stderr o/r':>12}")
for name, (n, ro, rr, so, sr) in total_diff_lines.items():
    print(f"{name:<14}{n:>10}{f'{ro}/{rr}':>10}{f'{so}/{sr}':>12}")
