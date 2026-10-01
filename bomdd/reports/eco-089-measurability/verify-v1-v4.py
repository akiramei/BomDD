#!/usr/bin/env python3
"""ECO-089 製造後の受入 V1・V4 の測定。判定器ではなく観測の記録 — 結果は order のクローズ節の観測行へ写す。

V1: ref-edges.draft.yaml を YAML 解析し、契約の各キーを読む(文字列 grep でなく構造を読む)。
V4: 改訂後の ref-edges を --schema で直指定した現行実装(BomDD-Plm の bomdd-lint)の出力が、同梱スキーマ(ref-v0.11)の出力と
    同一であること — 規則文言・新節だけでは検査器の挙動が変わらないことの確認。比較は diagnostics.json から refSchema(版の表記)
    を除いた内容と終了コード。標本は measure-arms.py の arms(2 土台)を実行時に組み、両ゲートで当てる。

使い方: python verify-v1-v4.py --plm <BomDD-Plm> [--edges <ref-edges.draft.yaml>] [--out <md>]
終了コード: 0= V1・V4 とも観測どおり / 1= 不一致 / 2= 測定不能
"""
import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("measure_arms", os.path.join(HERE, "measure-arms.py"))
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
STATES = ["PASS", "RED", "MEASUREMENT_FAILURE", "NOT_APPLICABLE"]
CAUSES = ["unreadable-input", "selector-miss", "empty-required-source", "tool-failure"]
DECLARED = ["R-011", "R-012", "R-014", "R-050"]
V4_ARMS = ["A1-clean", "A2-rename-mbom-key", "A6-empty-mbom", "A7-dangling-ref", "A8-ab-fail-row",
           "A1b-clean-unreferenced", "A9-rename-mbom-key-unreferenced"]


def v1(edges_path):
    obs = []
    with open(edges_path, encoding="utf-8") as f:
        e = yaml.safe_load(f)

    def chk(name, ok, detail=""):
        obs.append((name, bool(ok), detail))

    chk("edges_version が ref-v0.12", e.get("edges_version") == "ref-v0.12", str(e.get("edges_version")))
    m = e.get("measurability")
    chk("measurability 節がある", isinstance(m, dict))
    m = m if isinstance(m, dict) else {}
    chk("4 状態", [s.get("id") for s in m.get("states", [])] == STATES, str([s.get("id") for s in m.get("states", [])]))
    chk("原因の閉語彙 4 つ", [s.get("id") for s in m.get("failure_causes", [])] == CAUSES)
    for k in ("pass_rule", "zero_target_rule", "boundary_rule", "output_rule"):
        chk(f"{k} がある", isinstance(m.get(k), str) and len(m.get(k)) > 20)
    ud = m.get("upstream_declarations", [])
    chk("上流宣言の対象が R-011・R-012・R-014・R-050", [d.get("rule") for d in ud] == DECLARED, str([d.get("rule") for d in ud]))
    chk("各上流宣言が reads・expectation_source・on_empty を持つ",
        all(all(isinstance(d.get(k), str) and d.get(k) for k in ("reads", "expectation_source", "on_empty")) for d in ud))
    dids = [d.get("id") for d in m.get("deferred", [])]
    chk("deferred に cascade-attribution と exit-code-value", dids == ["cascade-attribution", "exit-code-value"], str(dids))
    rules = {r.get("id"): r for r in e.get("lint_rules", [])}
    chk("lint_rules が 19 規則", len([i for i in rules if i.startswith("R-")]) == 19, str(len(rules)))
    r50 = rules.get("R-050", {})
    chk("R-050 の gate=acceptance・severity=error が不変", r50.get("gate") == "acceptance" and r50.get("severity") == "error")
    rt = r50.get("rule", "")
    chk("R-050 (d) が上流の宣言を参照", "ref-v0.12" in rt and "upstream_declarations" in rt)
    note = r50.get("note", "")
    chk("R-050 note の『所見なし』の定義(抑止・支持すること・支持しないこと)が不変",
        all(w in note for w in ("抑止", "支持すること", "支持しないこと")))
    for rid in ("R-011", "R-012", "R-014"):
        chk(f"{rid} の note が measurability を参照", "measurability.upstream_declarations" in str(rules.get(rid, {}).get("note", "")))
    return obs


def run(cli, target, gate, outdir, schema_dir=None):
    cmd = ["node", cli, target, "--gate", gate, "--format", "json", "--out", outdir]
    if schema_dir:
        cmd += ["--schema", schema_dir]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240)
    dp = os.path.join(outdir, "diagnostics.json")
    if not os.path.exists(dp):
        return p.returncode, None
    with open(dp, encoding="utf-8") as f:
        d = json.load(f)
    d.pop("refSchema", None)
    return p.returncode, d


def v4(plm, cli, edges_path):
    bundled = os.path.join(plm, "schemas", "ref-v0")
    work = tempfile.mkdtemp(prefix="eco089v4-")
    rows = []
    posrow = None
    try:
        variant = os.path.join(work, "schema-variant")
        shutil.copytree(bundled, variant)
        shutil.copyfile(edges_path, os.path.join(variant, "ref-edges.draft.yaml"))
        control = os.path.join(work, "schema-control")
        shutil.copytree(bundled, control)
        # 陽性対照: 差が検出できる比較でなければ V4 の「同一」は弁別にならない。
        #   pos(gate)= R-012 の gate を G3→always に変えた変種 — 実装が schema から読む項目(所見の gate 属性)なので差が出るはず。
        #   pos(severity)= R-012 の severity を error→warn に変えた変種 — 参考(実装が schema の severity を読まないなら差は出ない)。
        pos = os.path.join(work, "schema-pos")
        shutil.copytree(bundled, pos)
        ptxt = ma.read(os.path.join(pos, "ref-edges.draft.yaml"))
        ptxt2 = re.sub(r"(- id: R-012\n(?:    .*\n)*?    gate: )G3", r"\1always", ptxt, count=1)
        if ptxt2 == ptxt:
            return None
        ma.write(os.path.join(pos, "ref-edges.draft.yaml"), ptxt2)
        pos_sev = os.path.join(work, "schema-pos-sev")
        shutil.copytree(bundled, pos_sev)
        stxt2 = re.sub(r"(- id: R-012\n(?:    .*\n)*?    severity: )error", r"\1warn", ptxt, count=1)
        if stxt2 == ptxt:
            return None
        ma.write(os.path.join(pos_sev, "ref-edges.draft.yaml"), stxt2)
        arch_self = ma.sh(["git", "-C", plm, "archive", "HEAD"], binary=True)
        arch_min = ma.sh(["git", "-C", plm, "archive", "HEAD", ma.MINIMAL_PATH], binary=True)
        bases = [("plm-self", arch_self.stdout, ""), ("minimal", arch_min.stdout, ma.MINIMAL_PATH)]
        for bname, blob, sub in bases:
            for arm in ma.ARMS:
                if arm["id"] not in V4_ARMS:
                    continue
                if arm.get("only_base") and arm["only_base"] != bname:
                    continue
                top = os.path.join(work, bname, arm["id"])
                os.makedirs(top)
                ma.extract(blob, top)
                root = os.path.join(top, *sub.split("/")) if sub else top
                if bname == "minimal":
                    ma.write(os.path.join(root, "bomdd", "50-as-built.yaml"), ma.MINIMAL_AB)
                if not ma.mutate(arm["id"], root):
                    return None
                for g in ma.GATES:
                    res = {}
                    for label, sd in (("bundled", None), ("control", control), ("variant", variant)):
                        out = os.path.join(work, f"o-{bname}-{arm['id']}-{g}-{label}")
                        res[label] = run(cli, root, g, out, sd)
                    same_ctrl = res["bundled"] == res["control"] and res["bundled"][1] is not None
                    same_var = res["bundled"] == res["variant"] and res["bundled"][1] is not None
                    rows.append((bname, arm["id"], g, res["bundled"][0], same_ctrl, same_var))
                    if bname == "minimal" and arm["id"] == "A2-rename-mbom-key" and g == "acceptance":
                        out = os.path.join(work, "o-pos")
                        pres = run(cli, root, g, out, pos)
                        out2 = os.path.join(work, "o-pos-sev")
                        sres = run(cli, root, g, out2, pos_sev)
                        posrow = (pres != res["bundled"] and pres[1] is not None, res["bundled"][0], pres[0],
                                  sres != res["bundled"] and sres[1] is not None, sres[0])
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return rows, posrow


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plm", required=True)
    ap.add_argument("--edges", default=os.path.join(REPO, "method", "schemas", "draft", "ref-edges.draft.yaml"))
    ap.add_argument("--out", default=os.path.join(HERE, "verify-v1-v4.md"))
    a = ap.parse_args()
    plm = os.path.abspath(a.plm)
    cli = os.path.join(plm, "packages", "cli", "dist", "main.js")
    head = ma.sh(["git", "-C", plm, "rev-parse", "--short", "HEAD"]).stdout.strip()
    dirty = ma.sh(["git", "-C", plm, "status", "--porcelain"]).stdout.strip()

    o1 = v1(a.edges)
    r4_all = v4(plm, cli, a.edges)
    if r4_all is None:
        print("測定不能: V4 の変異アンカーまたは陽性対照の差し替えが成立しない", file=sys.stderr)
        return 2
    r4, posrow = r4_all
    if posrow is None:
        print("測定不能: 陽性対照の arm が実行されなかった", file=sys.stderr)
        return 2

    L = []
    L.append("# ECO-089 製造後の受入 V1・V4 の観測")
    L.append("")
    L.append(f"- 測定日: {date.today().isoformat()}・対象= `{os.path.relpath(a.edges, REPO).replace(os.sep, '/')}`")
    L.append(f"- V4 の計器= BomDD-Plm `{head}`({'clean' if not dirty else 'dirty'})の bomdd-lint。同梱スキーマ= ref-v0.11(`schemas/ref-v0`)・比較は diagnostics.json から refSchema(版の表記)を除いた内容と終了コード。")
    L.append("")
    L.append("## V1(スキーマ本体の構造を YAML 解析で読む)")
    L.append("")
    L.append("| 観測項目 | 結果 | 詳細 |")
    L.append("|---|---|---|")
    for name, ok, detail in o1:
        L.append(f"| {name} | {'一致' if ok else '**不一致**'} | {detail} |")
    L.append("")
    L.append("## V4(改訂後スキーマの直指定で、現行実装の出力が同梱スキーマの出力と同一か)")
    L.append("")
    L.append("制御= 同梱スキーマの複製を --schema で指定した出力が、既定の同梱と同一であること(比較手順そのものの健全性)。")
    L.append("")
    L.append("| 土台 | arm | ゲート | exit | 制御(同梱の複製)が同一 | 改訂後スキーマが同一 |")
    L.append("|---|---|---|---|---|---|")
    for bname, arm, g, code, c, v in r4:
        L.append(f"| {bname} | {arm} | {g} | {code} | {'同一' if c else '**差あり**'} | {'同一' if v else '**差あり**'} |")
    L.append("")
    L.append(f"陽性対照(比較が差を検出できること)= R-012 の gate を G3→always に変えた変種を minimal の A2(acceptance)へ当てると、出力が{'**差あり**(検出できた)' if posrow[0] else '同一(**比較が差を検出できない**)'}(exit {posrow[1]}→{posrow[2]})。")
    L.append(f"参考(副次の観測)= 同じ手順で R-012 の severity を error→warn に変えた変種は、出力が{'差あり' if posrow[3] else '**同一**'}(exit {posrow[1]}→{posrow[4]})"
             + ("" if posrow[3] else " — この規則・この arm では実装は schema の severity を読まず、所見の severity を自身で持つ(他の規則は未確認)。severity の変更では比較の感度を測れない"))
    L.append("")
    ok1 = all(ok for _, ok, _ in o1)
    ok4 = all(c and v for _, _, _, _, c, v in r4) and len(r4) > 0 and posrow[0]
    L.append(f"集計: V1 {sum(1 for _, ok, _ in o1 if ok)}/{len(o1)} 項目一致・V4 {sum(1 for r in r4 if r[4] and r[5])}/{len(r4)} 組同一(標本 {len(r4)} 組)。")
    L.append("限界: V4 の標本は私の設計した arms(2 土台)で、実在リポの全数ではない。比較は diagnostics.json の内容と終了コードまで(text 出力・sarif は見ていない)。")
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(L) + "\n")
    print("結果:", a.out, "V1", ok1, "V4", ok4)
    return 0 if (ok1 and ok4) else 1


if __name__ == "__main__":
    sys.exit(main())
