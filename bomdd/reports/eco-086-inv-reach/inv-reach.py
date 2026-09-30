"""仕様が採番した INV-* が、M-BOM・Control Plan・固定オラクルの文面にどこまで届いているかを数える(読み取りのみ)。

届き方の定義(機械的な字面の一致のみ — 意味は読まない):
  spec   = 20-spec.md で表の先頭列に現れる INV-NNN(定義)
  mbom   = 32-mbom.yaml のどこかに INV-NNN が現れる
  cp     = 33-control-plan.yaml のどこかに INV-NNN が現れる
  oracle = 41-fixed-oracle.yaml のどこかに INV-NNN が現れる
"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path("C:/Users/akira/source/repos")
INV = re.compile(r"\bINV-\d{3}\b")
DEF = re.compile(r"^\|\s*(INV-\d{3})\s*\|", re.M)


def ids(p, defs=False):
    if not p.is_file():
        return None
    t = p.read_text(encoding="utf-8", errors="replace")
    return set(DEF.findall(t)) if defs else set(INV.findall(t))


print("| リポ | 仕様の INV | M-BOM に届く | 検査計画に届く | 固定オラクルに届く | どの層にも届かない |")
print("|---|---|---|---|---|---|")
for r in sys.argv[1:]:
    b = ROOT / r / "bomdd"
    spec = ids(b / "20-spec.md", defs=True)
    if not spec:
        print(f"| {r} | 定義なし | - | - | - | - |")
        continue
    m, c, o = ids(b / "32-mbom.yaml"), ids(b / "33-control-plan.yaml"), ids(b / "41-fixed-oracle.yaml")
    f = lambda s: "ファイルなし" if s is None else str(len(spec & s))  # noqa: E731
    none = spec - (m or set()) - (c or set()) - (o or set())
    print(f"| {r} | {len(spec)} | {f(m)} | {f(c)} | {f(o)} | {len(none)} |")
