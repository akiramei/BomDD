# r050-survey — 実リポの製造記録(50-as-built.yaml)に現行の受入ゲートを当てた実測(ECO-085・読み取りのみ)
#
# 目的: 規則を変える前に、実在の製造記録が現行規則でどう判定されているかを数える(影響予測の基準線)。
# 出すのは件数だけ — 製品リポの CP ID や本文は出力しない。
#
# 使い方:
#   python r050-survey.py --plm <BomDD-Plm のパス> --root <リポ群の親ディレクトリ> <リポ名>...
#
# 終了コード: 常に 0(測定のみ)。読めないリポは「測定不能」と書く。
# 検出力の限界(宣言):
#   (1) 「最新エントリ」は as_built リストの末尾(現行実装と同じ定義)。
#   (2) 合否値の語彙は記録にある文字列をそのまま数える(意味は解釈しない)。
#   (3) workspace 構成では測らない(リポ単体で CLI を起動する)。

import argparse
import io
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import yaml

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def load(p: Path):
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")), None
    except Exception as e:  # noqa: BLE001
        return None, type(e).__name__


def head(repo: Path) -> str:
    p = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True)
    return p.stdout.strip() or "unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plm", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("repos", nargs="+")
    a = ap.parse_args()
    cli = Path(a.plm) / "packages" / "cli" / "dist" / "main.js"

    print(f"CLI の個体: BomDD-Plm HEAD {head(Path(a.plm))}・ゲート= acceptance・リポ単体")
    print()
    print("| リポ(HEAD) | 方言 | エントリ数 | 最新エントリの証拠行(合否値の内訳) | 全エントリの合否値の内訳 "
          "| M unit の受入 CP | 最新に行がない CP | 最新に合格行がない CP | 現行 R-050 所見 | exit |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for name in a.repos:
        repo = Path(a.root) / name
        abf = repo / "bomdd" / "50-as-built.yaml"
        if not abf.is_file():
            print(f"| {name}({head(repo)}) | 製造記録なし | - | - | - | - | - | - | - | - |")
            continue
        doc, err = load(abf)
        with tempfile.TemporaryDirectory(prefix="r050-survey-") as td:
            p = subprocess.run(["node", str(cli), str(repo), "--gate", "acceptance", "--format", "json", "--out", td],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
        try:
            n050 = sum(1 for f in json.loads(p.stdout).get("findings", []) if f.get("rule") == "R-050")
        except json.JSONDecodeError:
            n050 = "測定不能"
        if err:
            print(f"| {name}({head(repo)}) | 読込不能({err}) | - | - | - | - | - | - | {n050} | {p.returncode} |")
            continue
        ab = (doc or {}).get("as_built")
        if not isinstance(ab, list):
            print(f"| {name}({head(repo)}) | 文書形(mapping) | - | - | - | - | - | - | {n050} | {p.returncode} |")
            continue
        last = ab[-1] if ab else {}
        rows = [r for r in (last or {}).get("test_evidence_refs") or [] if isinstance(r, dict)]
        allrows = [r for e in ab for r in (e or {}).get("test_evidence_refs") or [] if isinstance(r, dict)]
        cnt = lambda rs: dict(Counter(str(r.get("result", "<欄なし>")) for r in rs))  # noqa: E731
        cps = set()
        md, _ = load(repo / "bomdd" / "32-mbom.yaml")
        for u in (((md or {}).get("mbom") or {}).get("manufacturing_units") or []):
            cps.update((u or {}).get("acceptance_refs") or [])
        covered = {r.get("cp_ref") for r in rows}
        passed = {r.get("cp_ref") for r in rows if r.get("result") == "pass"}
        print(f"| {name}({head(repo)}) | リスト形 | {len(ab)} | {len(rows)} {cnt(rows)} | {cnt(allrows)} "
              f"| {len(cps)} | {len(cps - covered)} | {len(cps - passed)} | {n050} | {p.returncode} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
