#!/usr/bin/env python3
"""ECO-089 延長 1 周(裁定 2:B): 連鎖所見の帰属(契約 5)が実装できるかを、既存の検査出力で実測する。

候補規則(検査器は変えず、出力への後処理だけ): 未解決の参照先の族に**定義ノードが 1 件も無い**なら
「測定不能の連鎖」、1 件以上あるなら「違反(RED)」と帰属する。入力は graph.json と diagnostics.json。
  C-b  (全ファミリー) : graph.json の resolved=false の全参照を対象にする(粗い版)。
  C-b' (厳格ファミリー): diagnostics.json の R-003 のうち severity=error の所見だけを対象にする。
                         R-003 の severity は id-grammar の族ごとの厳格度(strict は error)で決まるので、
                         定義サイトが機械可読な族だけに自動的に絞られる。

測ること:
  (1) arms(measure-arms.py の変異 8 種+変種 2 種・2 土台)で、連鎖が「測定不能の連鎖」に、既知の違反が「違反」に分かれるか。
  (2) 実在リポ(コーパス)で、規則を当てたとき「測定不能の連鎖」へ回る参照の数と族を出す。
      実在リポには、定義サイトが散文の族・別リポの族・ID でない語が混ざるため、粗い版が誤帰属を出すかを見る。
測らないこと: 帰属の正しさの最終判定(コーパスの列挙は人が読む)・検査器への実装可能性そのもの。

使い方: python cascade-attribution.py --plm <BomDD-Plm> --repos <実在リポのパス>... [--out <md>]
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

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("measure_arms", os.path.join(HERE, "measure-arms.py"))
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)

FAMILY_RE = re.compile(r"^([A-Za-z]+[0-9]*)-")


def family_of(id_):
    m = FAMILY_RE.match(id_ or "")
    return m.group(1) if m else None


def run_lint_json(cli, target, gate, outdir, timeout=240):
    try:
        p = subprocess.run(["node", cli, target, "--gate", gate, "--format", "json", "--out", outdir],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "timeout"
    gp = os.path.join(outdir, "graph.json")
    dp = os.path.join(outdir, "diagnostics.json")
    if not (os.path.exists(gp) and os.path.exists(dp)):
        return p.returncode, "graph/diagnostics なし(exit %d)" % p.returncode
    with open(gp, encoding="utf-8") as f:
        g = json.load(f)
    with open(dp, encoding="utf-8") as f:
        d = json.load(f)
    return p.returncode, (g, d)


def classify(defs, fam_items):
    """fam_items: {族: [対象 ID...]} → (測定不能の連鎖件数, 違反件数, 族ごとの行)。"""
    mf = red = 0
    rows = []
    for fam, ids in sorted(fam_items.items(), key=lambda kv: str(kv[0])):
        dcount = defs.get(fam, 0)
        cls = "測定不能の連鎖" if dcount == 0 else "違反"
        if dcount == 0:
            mf += len(ids)
        else:
            red += len(ids)
        rows.append((fam, dcount, len(ids), cls, sorted(set(ids))))
    return mf, red, rows


def literal_defs(repo_dir, ids):
    """測定不能の連鎖へ回った参照 ID のうち、repo の bomdd/ 配下に `id: <ID>` の字面で定義が存在するものを数える。
    存在する= 定義はあるのに検査器の定義サイトが読めていない(契約上の測定不能が妥当)・存在しない= 本当に未定義かもしれない(曖昧)。"""
    texts = []
    base = os.path.join(repo_dir, "bomdd")
    for dp, dn, fn in os.walk(base):
        dn[:] = [d for d in dn if d not in {".git", "node_modules", "reports"}]
        for x in fn:
            if x.endswith((".yaml", ".yml", ".md", ".json")):
                try:
                    with open(os.path.join(dp, x), encoding="utf-8", errors="replace") as f:
                        texts.append(f.read())
                except OSError:
                    pass
    blob = "\n".join(texts)
    has = set()
    for i in ids:
        if re.search(r"\bid:\s*[\"']?" + re.escape(i) + r"[\"']?(\s|,|\}|$)", blob, re.M):
            has.add(i)
    return has


def attribute(graph, diag):
    defs = {}
    for n in graph.get("nodes", []):
        defs[n.get("family")] = defs.get(n.get("family"), 0) + 1
    # 粗い版(全ファミリー): resolved=false の全参照
    all_items = {}
    total_all = 0
    for e in graph.get("edges", []):
        if e.get("resolved") is False:
            total_all += 1
            all_items.setdefault(family_of(e.get("to")), []).append(e.get("to"))
    mf_a, red_a, rows_a = classify(defs, all_items)
    # 厳格版: R-003 の severity=error の所見だけ
    strict_items = {}
    total_s = 0
    for f in diag.get("findings", []):
        if f.get("rule") == "R-003" and f.get("severity") == "error" and not f.get("suppressed"):
            total_s += 1
            strict_items.setdefault(family_of(f.get("targetId")), []).append(f.get("targetId"))
    mf_s, red_s, rows_s = classify(defs, strict_items)
    return dict(all=dict(total=total_all, mf=mf_a, red=red_a, rows=rows_a),
                strict=dict(total=total_s, mf=mf_s, red=red_s, rows=rows_s))


def arms_part(cli, plm):
    arch_self = ma.sh(["git", "-C", plm, "archive", "HEAD"], binary=True)
    arch_min = ma.sh(["git", "-C", plm, "archive", "HEAD", ma.MINIMAL_PATH], binary=True)
    bases = [("plm-self", arch_self.stdout, ""), ("minimal", arch_min.stdout, ma.MINIMAL_PATH)]
    work = tempfile.mkdtemp(prefix="eco089c-")
    res = []
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
                    return None
                out = os.path.join(work, "out-%s-%s" % (bname, arm["id"]))
                code, r = run_lint_json(cli, root, "acceptance", out)
                if isinstance(r, tuple):
                    res.append((bname, arm, code, attribute(*r), None))
                else:
                    res.append((bname, arm, code, None, r))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return res


def corpus_part(cli, repos):
    rows = []
    work = tempfile.mkdtemp(prefix="eco089k-")
    try:
        for r in repos:
            name = os.path.basename(os.path.abspath(r))
            ws = os.path.join(r, "bomdd-workspace.yaml")
            target = ws if os.path.exists(ws) else r
            out = os.path.join(work, "out-" + name)
            code, res = run_lint_json(cli, target, "acceptance", out)
            if isinstance(res, tuple):
                rows.append((name, os.path.basename(target), code, attribute(*res), None, r))
            else:
                rows.append((name, os.path.basename(target), code, None, res, r))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return rows


def reading(exp, v):
    if exp == "MEASUREMENT_FAILURE":
        if v["total"] == 0:
            return "対象 0 件 — 捕まらない"
        return "全て測定不能の連鎖へ" if v["red"] == 0 else "**一部が違反へ誤帰属**"
    if exp == "RED":
        if v["total"] == 0:
            return "該当参照なし(別規則で RED)"
        return "違反へ" if (v["red"] >= 1 and v["mf"] == 0) else "**違反を測定不能へ誤帰属**"
    return "未解決なし" if v["total"] == 0 else "**緑の土台に未解決**"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plm", required=True)
    ap.add_argument("--repos", nargs="*", default=[])
    ap.add_argument("--out", default=os.path.join(HERE, "cascade-attribution.md"))
    a = ap.parse_args()
    plm = os.path.abspath(a.plm)
    cli = os.path.join(plm, "packages", "cli", "dist", "main.js")
    head = ma.sh(["git", "-C", plm, "rev-parse", "--short", "HEAD"]).stdout.strip()

    arms = arms_part(cli, plm)
    if arms is None:
        return 2
    corpus = corpus_part(cli, [os.path.abspath(r) for r in a.repos]) if a.repos else []

    L = []
    L.append("# ECO-089 延長 1 周 — 連鎖所見の帰属(契約 5)が実装できるかの実測")
    L.append("")
    L.append(f"- 測定日: {date.today().isoformat()}・計器= BomDD-Plm `{head}` の bomdd-lint(受入ゲート・graph.json と diagnostics.json を入力)")
    L.append("- 規則: 未解決の参照先の族に定義ノードが 1 件も無い → 「測定不能の連鎖」/ 1 件以上ある → 「違反」。検査器は変えず、出力への後処理だけ。")
    L.append("  C-b= graph.json の未解決参照すべて(粗い版)/ C-b'= R-003 の severity=error の所見だけ(厳格ファミリーに自動で絞られる)。")
    L.append("- 限界: 族は参照先 ID の先頭節で判定(id-grammar を読まない近似)。arms は私の設計した変異。コーパスの帰属の正しさは人が読んで判定する(自動判定ではない)。")
    L.append("")
    L.append("## (1) arms: 連鎖は測定不能へ・本物の違反は違反へ分かれるか")
    L.append("")
    L.append("| 土台 | arm | 期待 | C-b 未解決 | C-b 測定不能へ | C-b 違反へ | C-b 読み | C-b' 対象(R-003 error) | C-b' 測定不能へ | C-b' 違反へ | C-b' 読み |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for bname, arm, code, att, err in arms:
        if att is None:
            L.append(f"| {bname} | {arm['id']} | {arm['expect']} | — | — | — | 測定不能: {err} | — | — | — | — |")
            continue
        x, s = att["all"], att["strict"]
        L.append(f"| {bname} | {arm['id']} | {arm['expect']} | {x['total']} | {x['mf']} | {x['red']} | {reading(arm['expect'], x)} | {s['total']} | {s['mf']} | {s['red']} | {reading(arm['expect'], s)} |")
    L.append("")
    L.append("## (2) 実在リポ(コーパス): 規則を当てたとき測定不能の連鎖へ回る参照")
    L.append("")
    if not corpus:
        L.append("(実在リポの指定なし)")
    else:
        L.append("| リポ | 入力 | exit | C-b 未解決 | C-b 測定不能へ | C-b 違反へ | C-b' 対象(R-003 error) | C-b' 測定不能へ | C-b' 違反へ | C-b' で測定不能へ回る族(定義数・件数・例) |")
        L.append("|---|---|---|---|---|---|---|---|---|---|")
        for name, tgt, code, att, err, rp in corpus:
            if att is None:
                L.append(f"| {name} | {tgt} | {code} | — | — | — | — | — | — | 測定不能: {err} |")
                continue
            x, s = att["all"], att["strict"]
            mfam = [f"{fam}(定義 {d}・{n} 件・例 {', '.join(ex[:3])})" for fam, d, n, cls, ex in s["rows"] if cls == "測定不能の連鎖"]
            L.append(f"| {name} | {tgt} | {code} | {x['total']} | {x['mf']} | {x['red']} | {s['total']} | {s['mf']} | {s['red']} | {'; '.join(mfam) if mfam else '—'} |")
        L.append("")
        L.append("### 粗い版(C-b)で測定不能へ回る族の数(誤帰属の目安)")
        L.append("")
        L.append("| リポ | 測定不能へ回る族の数(定義 0・未解決あり) | うち C-b' でも回る族の数 |")
        L.append("|---|---|---|")
        for name, tgt, code, att, err, rp in corpus:
            if att is None:
                continue
            fa = [r for r in att["all"]["rows"] if r[3] == "測定不能の連鎖"]
            fs = [r for r in att["strict"]["rows"] if r[3] == "測定不能の連鎖"]
            L.append(f"| {name} | {len(fa)} | {len(fs)} |")
        L.append("")
        L.append("### C-b' で測定不能へ回った参照 ID の内訳(族が判定できたか・定義が字面で存在するか)")
        L.append("")
        L.append("族が判定できない(先頭節が ID 族の形でない語)は、この規則では帰属を決められない(「帰属不明」)。族が判定できたものは、bomdd/ 配下に `id: <ID>` の字面の定義があるかを数える:")
        L.append("あれば「定義はあるのに検査器の定義サイトが読めていない」= 測定不能の帰属が妥当。無ければ「本当に未定義かもしれない」= 違反か測定不能か曖昧。")
        L.append("")
        L.append("| リポ | 測定不能へ回った参照(ID の異なり数) | 帰属不明(族が判定できない) | 族あり | うち字面の定義あり(帰属が妥当) | うち字面の定義なし(曖昧) | 定義なしの族(件数) |")
        L.append("|---|---|---|---|---|---|---|")
        for name, tgt, code, att, err, rp in corpus:
            if att is None:
                continue
            ids_known = []
            ids_none = []
            for fam, d, n, cls, ex in att["strict"]["rows"]:
                if cls != "測定不能の連鎖":
                    continue
                (ids_none if fam is None else ids_known).extend(ex)
            ids_known = sorted(set(ids_known))
            ids_none = sorted(set(ids_none))
            has = literal_defs(rp, ids_known) if ids_known else set()
            nodef = [i for i in ids_known if i not in has]
            fam_n = {}
            for i in nodef:
                fam_n[family_of(i)] = fam_n.get(family_of(i), 0) + 1
            fam_txt = ", ".join(f"{k}({v})" for k, v in sorted(fam_n.items(), key=lambda kv: -kv[1])) or "—"
            L.append(f"| {name} | {len(ids_known) + len(ids_none)} | {len(ids_none)} | {len(ids_known)} | {len(has)} | {len(nodef)} | {fam_txt} |")
    L.append("")
    L.append("読み方: (1) は規則が原理的に区別できるかの確認。(2) は実在リポで、定義サイトが散文の族・別リポの族・ID でない語まで「測定不能」と読む誤帰属が出るかの目安。")
    L.append("C-b' で測定不能へ回る族は、定義サイトが本当に読めていない(構文エラー・必須成果物の欠落)のか、方言・別リポの族なのかを人が確かめる。")
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(L) + "\n")
    print("結果:", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
