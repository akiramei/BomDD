"""R-050 が所見ありになる実リポで、赤の中身を分ける(読み取りのみ)。

対象 CP = M unit の acceptance_refs の CP。現行の規則は「最新エントリ」だけを見る。
分類(CP ごと・排他):
  latest_pass     最新エントリに合格行がある(現行規則でも緑)
  latest_nonpass  最新エントリに行はあるが合格でない
  earlier_pass    最新エントリに行はないが、それより前のエントリの最後の行が合格(増分記録なら緑になりうる)
  earlier_nonpass 最新エントリに行はなく、前のエントリの最後の行が合格でない
  never           どのエントリにも行がない
"""
import io
import sys
from collections import Counter
from pathlib import Path

import yaml

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path("C:/Users/akira/source/repos")


def load(p):
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


print("| リポ | 対象 CP | 最新で合格 | 最新に行あり・合格でない | 前のエントリの合格が最後 | 前のエントリの不合格が最後 | どこにも行なし | エントリ数 |")
print("|---|---|---|---|---|---|---|---|")
for r in sys.argv[1:]:
    b = ROOT / r / "bomdd"
    ab = load(b / "50-as-built.yaml")
    mb = load(b / "32-mbom.yaml")
    a = (ab or {}).get("as_built")
    if not isinstance(a, list) or not a:
        print(f"| {r} | 測定不能(文書形または記録なし) | - | - | - | - | - | - |")
        continue
    cps = set()
    for u in (((mb or {}).get("mbom") or {}).get("manufacturing_units") or []):
        cps.update((u or {}).get("acceptance_refs") or [])
    last_rows = {}   # cp -> (entry index, result) 最後に行が出たもの
    for i, e in enumerate(a):
        for row in (e or {}).get("test_evidence_refs") or []:
            if isinstance(row, dict) and isinstance(row.get("cp_ref"), str):
                last_rows[row["cp_ref"]] = (i, row.get("result"))
    n = len(a) - 1
    c = Counter()
    for cp in cps:
        if cp not in last_rows:
            c["never"] += 1
        else:
            i, res = last_rows[cp]
            if i == n:
                c["latest_pass" if res == "pass" else "latest_nonpass"] += 1
            else:
                c["earlier_pass" if res == "pass" else "earlier_nonpass"] += 1
    print(f"| {r} | {len(cps)} | {c['latest_pass']} | {c['latest_nonpass']} | {c['earlier_pass']} | {c['earlier_nonpass']} | {c['never']} | {len(a)} |")
