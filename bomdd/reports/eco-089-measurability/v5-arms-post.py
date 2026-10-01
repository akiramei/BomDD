#!/usr/bin/env python3
"""BomDD ECO-089 の V5: measure-arms.py の arms(期待は実装の前に ARMS に固定済み)を、実装後の bomdd-lint に当てる。

判定(arm × ゲートごと):
  期待= MEASUREMENT_FAILURE: exit が 0 でなく、適用ゲート内に outcome= MEASUREMENT_FAILURE の所見か measurement の項目が 1 件以上
  期待= RED:                 exit 1 で、適用ゲート内に outcome= RED の所見が 1 件以上
  期待= PASS:                exit 0
連鎖の R-003 が違反として残ることは V5 では問わない(ECO-089 裁定 2:C)。ARMS の期待は書き換えない — 不一致はそのまま記録する。

使い方: python v5-arms-post.py --plm <BomDD-Plm> [--out <md>]
"""
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("measure_arms", os.path.join(HERE, "measure-arms.py"))
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)

LADDER = {"always": 0, "G1": 1, "G3": 2, "freeze": 3, "acceptance": 4}


def applied(entry_gate, run_gate):
    return LADDER.get(entry_gate, 0) <= LADDER.get(run_gate, 0)


def judge(expect, code, diag, gate):
    fs = [f for f in diag["findings"] if applied(f.get("gate", "always"), gate)]
    mf = [f for f in fs if f.get("outcome") == "MEASUREMENT_FAILURE"]
    red = [f for f in fs if f.get("outcome") == "RED"]
    meas = [m for m in diag.get("measurement", []) if applied(m["gate"], gate)]
    if expect == "MEASUREMENT_FAILURE":
        ok = code != 0 and (len(mf) + len(meas)) > 0
    elif expect == "RED":
        ok = code == 1 and len(red) > 0
    else:
        ok = code == 0
    return ok, len(mf), len(red), len(meas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plm", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "v5-arms-post.md"))
    a = ap.parse_args()
    plm = os.path.abspath(a.plm)
    cli = os.path.join(plm, "packages", "cli", "dist", "main.js")
    head = ma.sh(["git", "-C", plm, "rev-parse", "--short", "HEAD"]).stdout.strip()
    dirty = ma.sh(["git", "-C", plm, "status", "--porcelain"]).stdout.strip()
    # 土台は HEAD の archive(既存 fixture)。計器は作業木の dist(未コミットの実装を測るときは dirty と記録する)。
    arch_self = ma.sh(["git", "-C", plm, "archive", "HEAD"], binary=True)
    arch_min = ma.sh(["git", "-C", plm, "archive", "HEAD", ma.MINIMAL_PATH], binary=True)
    bases = [("plm-self", arch_self.stdout, ""), ("minimal", arch_min.stdout, ma.MINIMAL_PATH)]
    work = tempfile.mkdtemp(prefix="eco089v5-")
    rows = []
    try:
        for bname, blob, sub in bases:
            for arm in ma.ARMS:
                if arm.get("only_base") and arm["only_base"] != bname:
                    continue
                top = os.path.join(work, bname, arm["id"])
                os.makedirs(top)
                ma.extract(blob, top)
                root = os.path.join(top, *sub.split("/")) if sub else top
                if bname == "minimal":
                    ma.write(os.path.join(root, "bomdd", "50-as-built.yaml"), ma.MINIMAL_AB)
                if not ma.mutate(arm["id"], root):
                    print("測定不能: 変異アンカー無し", bname, arm["id"], file=sys.stderr)
                    return 2
                for g in ma.GATES:
                    out = os.path.join(work, f"o-{bname}-{arm['id']}-{g}")
                    p = subprocess.run(["node", cli, root, "--gate", g, "--format", "json", "--out", out],
                                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
                    try:
                        diag = json.loads(p.stdout)
                    except json.JSONDecodeError:
                        rows.append((bname, arm["id"], g, "?", p.returncode, False, "-", "-", "-", "json なし(測定不能)"))
                        continue
                    exp = arm.get("expect_by_gate", {}).get(g, arm["expect"])
                    ok, nmf, nred, nmeas = judge(exp, p.returncode, diag, g)
                    rows.append((bname, arm["id"], g, exp, p.returncode, ok, nmf, nred, nmeas, diag.get("schemaVersion")))
    finally:
        shutil.rmtree(work, ignore_errors=True)

    L = ["# BomDD ECO-089 V5 — arms を実装後の bomdd-lint に当てた結果", ""]
    L.append(f"- 測定日: {date.today().isoformat()}・計器= BomDD-Plm `{head}` の作業木の dist({'clean' if not dirty else 'dirty= 未コミットの実装を含む'})")
    L.append("- 期待は measure-arms.py の ARMS(実装の前に固定)から読み、書き換えていない。")
    L.append("")
    L.append("| 土台 | arm | ゲート | 期待 | exit | 判定 | 測定不能の所見 | RED の所見 | measurement | 版 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        L.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {'一致' if r[5] else '**不一致**'} | {r[6]} | {r[7]} | {r[8]} | {r[9]} |")
    n_ok = sum(1 for r in rows if r[5])
    L.append("")
    L.append(f"集計: {n_ok}/{len(rows)} 組が期待と一致。")
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(L) + "\n")
    print("結果:", a.out, f"{n_ok}/{len(rows)}")
    for r in rows:
        if not r[5]:
            print("不一致:", r)
    return 0 if n_ok == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
