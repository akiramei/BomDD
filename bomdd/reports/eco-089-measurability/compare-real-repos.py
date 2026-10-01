#!/usr/bin/env python3
"""BomDD-Plm ECO-009 の変更前後の突合(実在リポ)。

run:     指定した CLI で各リポ(workspace があればそれ)を always / acceptance の 2 ゲートで実行し、
         diagnostics.json を <out>/<label>/<repo>-<gate>.json に保存する(対象リポには書き込まない)。
compare: 2 つのラベルの保存結果を比べる。比較の単位は所見の (rule, severity, gate, file, line, targetId, message) と終了コード。
         `outcome`(区分)と `measurement` 節・stats.outcomes・schemaVersion は新しい版で足した欄なので比較から外し、別に件数を出す。

使い方:
  python compare-real-repos.py run --cli <main.js> --label old --out <dir> <repo>...
  python compare-real-repos.py compare --out <dir> --a old --b new
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter

GATES = ["always", "acceptance"]


def run(args):
    os.makedirs(os.path.join(args.out, args.label), exist_ok=True)
    for r in args.repos:
        name = os.path.basename(os.path.abspath(r))
        ws = os.path.join(r, "bomdd-workspace.yaml")
        target = ws if os.path.exists(ws) else r
        for g in GATES:
            tmp = tempfile.mkdtemp(prefix="eco009cmp-")
            p = subprocess.run(["node", args.cli, target, "--gate", g, "--format", "json", "--out", tmp],
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
            try:
                diag = json.loads(p.stdout)
            except json.JSONDecodeError:
                diag = None
            rec = {"repo": name, "gate": g, "exit": p.returncode, "diag": diag}
            with open(os.path.join(args.out, args.label, f"{name}-{g}.json"), "w", encoding="utf-8") as f:
                json.dump(rec, f, ensure_ascii=False)
    return 0


def key(f):
    return (f.get("rule"), f.get("severity"), f.get("gate"), f.get("file"), f.get("line"), f.get("targetId"), f.get("message"))


def compare(args):
    da = os.path.join(args.out, args.a)
    db = os.path.join(args.out, args.b)
    rows = []
    for fn in sorted(os.listdir(da)):
        pa, pb = os.path.join(da, fn), os.path.join(db, fn)
        if not os.path.exists(pb):
            rows.append((fn, "比較先なし", "", "", ""))
            continue
        a = json.load(open(pa, encoding="utf-8"))
        b = json.load(open(pb, encoding="utf-8"))
        if a["diag"] is None or b["diag"] is None:
            rows.append((fn, f"exit {a['exit']}→{b['exit']}", "測定不能(json なし)", "", ""))
            continue
        ca = Counter(key(f) for f in a["diag"]["findings"])
        cb = Counter(key(f) for f in b["diag"]["findings"])
        only_a = ca - cb
        only_b = cb - ca
        diff_rules = Counter([k[0] + ":" + k[1] for k in (only_a + only_b).elements()])
        same = "同一" if not only_a and not only_b else f"差 {sum(only_a.values())} 件消失 / {sum(only_b.values())} 件出現({dict(diff_rules)})"
        oc = Counter(f.get("outcome", "-") for f in b["diag"]["findings"])
        meas = b["diag"].get("measurement", [])
        mtxt = "; ".join(sorted({f"{m.get('rule', '')}/{m.get('family', '')}/{m['cause']}@{m['gate']}" for m in meas})) or "—"
        rows.append((fn, f"exit {a['exit']}→{b['exit']}", same, dict(oc), mtxt))
    print("| リポ-ゲート | exit 旧→新 | 区分以外の所見 | 新の区分の件数 | 新の measurement |")
    print("|---|---|---|---|---|")
    for r in rows:
        print("| " + " | ".join(str(x) for x in r) + " |")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cli", required=True)
    r.add_argument("--label", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("repos", nargs="+")
    c = sub.add_parser("compare")
    c.add_argument("--out", required=True)
    c.add_argument("--a", required=True)
    c.add_argument("--b", required=True)
    a = ap.parse_args()
    return run(a) if a.cmd == "run" else compare(a)


if __name__ == "__main__":
    sys.exit(main())
