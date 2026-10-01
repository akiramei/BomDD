#!/usr/bin/env python3
"""ECO-089 既知不良サンプル(arms)の較正測定 — 現行の bomdd-lint に「測定できなかった」を作って当てる。

土台は 2 種(どちらも BomDD-Plm の HEAD から git archive で複製。対象リポには書き込まない):
  plm-self : BomDD-Plm 自身の bomdd/(自己ホスト・error 0 の緑・他ファイルからの参照が多い)
  minimal  : 固定オラクルの clean fixture(M unit 1・CP 1)+合格行 1 本の 50-as-built(参照が最小)
各 arm は土台へ 1 つだけ変異を入れる。期待(契約後の判定)は実装の前に本ファイルで固定する。
現行実装の出力は期待と突き合わせるだけで、期待の導出には使わない(是正前の個体に是正後の期待を当てる=
ECO-085 と同じ較正の型)。

土台が両ゲートで exit 0 でなければ「測定不能」として中止する(緑でない土台の上の測定は弁別にならない)。

使い方: python measure-arms.py --plm <BomDD-Plm のパス> [--cli <main.js>] [--out <結果 md>]
"""
import argparse
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import date

GATES = ["always", "acceptance"]
FINDING_RE = re.compile(r"^(error|warn|info) (\S+)")
MINIMAL_PATH = "oracle/fixtures/clean/repo"
MINIMAL_AB = (
    "as_built:\n"
    "  - id: AB-min-factory-01\n"
    "    lifecycle_state: as-built\n"
    "    test_evidence_refs:\n"
    "      - { evidence_id: TE-min-001, cp_ref: CP-CORE-001, result: pass }\n"
)

# 期待(契約後の判定)。PASS / RED / MEASUREMENT_FAILURE のいずれか。
# expect_by_gate= 規則のゲートが実行ゲートより後なら適用されないため、ゲートごとに期待が変わる arm。
ARMS = [
    dict(id="A1-clean", expect="PASS", fault="変異なし(土台)"),
    dict(id="A2-rename-mbom-key", expect="MEASUREMENT_FAILURE",
         fault="32-mbom の manufacturing_units を process_units へ改名(キー空振り)"),
    dict(id="A3-rename-cp-key", expect="MEASUREMENT_FAILURE",
         fault="33-control-plan の characteristics を checks へ改名(キー空振り)"),
    dict(id="A4-broken-mbom-yaml", expect="MEASUREMENT_FAILURE",
         fault="32-mbom.yaml の末尾へ YAML 構文エラーを 1 行足す(読めない入力)"),
    dict(id="A5-broken-cp-yaml", expect="MEASUREMENT_FAILURE",
         fault="33-control-plan.yaml の末尾へ YAML 構文エラーを 1 行足す(読めない入力)"),
    dict(id="A6-empty-mbom", expect="MEASUREMENT_FAILURE",
         fault="32-mbom.yaml を空文書にする(対象 0 件・上流の 30-ebom は実現を要する品目を持つ)"),
    dict(id="A7-dangling-ref", expect="RED",
         fault="32-mbom の ebom_refs の 1 件を存在しない ID へ(既知の違反)"),
    dict(id="A8-ab-fail-row", expect="RED", expect_by_gate={"always": "PASS", "acceptance": "RED"},
         fault="50-as-built の最後の result: pass を result: fail へ(既知の違反・R-050 は acceptance ゲートの規則)"),
    # 参照の無い構成: M ID を他ファイルが参照しないとき、キー空振りが連鎖所見(R-003)を出さずに済むかを測る。
    dict(id="A1b-clean-unreferenced", expect="PASS", only_base="minimal",
         fault="33 の verifies から M ID の参照を外した変種(M ID を他ファイルが参照しない構成・変異なし)"),
    dict(id="A9-rename-mbom-key-unreferenced", expect="MEASUREMENT_FAILURE", only_base="minimal",
         baseline_arm="A1b-clean-unreferenced",
         fault="A1b の 32-mbom の manufacturing_units を process_units へ改名(M ID の被参照なし)"),
]


def sh(cmd, cwd=None, binary=False):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=not binary,
                          **({} if binary else dict(encoding="utf-8", errors="replace")))


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def extract(blob, root):
    with tarfile.open(fileobj=io.BytesIO(blob)) as t:
        try:
            t.extractall(root, filter="data")
        except TypeError:  # Python < 3.12
            t.extractall(root)


def mutate(arm_id, root):
    mb = os.path.join(root, "bomdd", "32-mbom.yaml")
    cp = os.path.join(root, "bomdd", "33-control-plan.yaml")
    ab = os.path.join(root, "bomdd", "50-as-built.yaml")
    if arm_id in ("A1b-clean-unreferenced", "A9-rename-mbom-key-unreferenced"):
        s = read(cp)
        if "verifies: [E-CORE-001, M-CORE-001]" not in s:
            return False
        write(cp, s.replace("verifies: [E-CORE-001, M-CORE-001]", "verifies: [E-CORE-001]"))
        if arm_id == "A9-rename-mbom-key-unreferenced":
            m = read(mb)
            write(mb, m.replace("  manufacturing_units:", "  process_units:"))
            return m.count("  manufacturing_units:") == 1
        return True
    if arm_id == "A1-clean":
        return True
    if arm_id == "A2-rename-mbom-key":
        s = read(mb)
        n = s.count("  manufacturing_units:")
        write(mb, s.replace("  manufacturing_units:", "  process_units:"))
        return n == 1
    if arm_id == "A3-rename-cp-key":
        s = read(cp)
        n = s.count("  characteristics:")
        write(cp, s.replace("  characteristics:", "  checks:"))
        return n == 1
    if arm_id == "A4-broken-mbom-yaml":
        write(mb, read(mb).rstrip("\n") + "\nbroken: [unclosed\n")
        return True
    if arm_id == "A5-broken-cp-yaml":
        write(cp, read(cp).rstrip("\n") + "\nbroken: [unclosed\n")
        return True
    if arm_id == "A6-empty-mbom":
        write(mb, "")
        return True
    if arm_id == "A7-dangling-ref":
        s = read(mb)
        m = re.search(r"ebom_refs: \[(E-[A-Z0-9-]+)", s)
        if not m:
            return False
        write(mb, s[: m.start(1)] + "E-NOPE-999" + s[m.end(1):])
        return True
    if arm_id == "A8-ab-fail-row":
        s = read(ab)
        i = s.rfind("result: pass")
        if i < 0:
            return False
        write(ab, s[:i] + "result: fail" + s[i + len("result: pass"):])
        return True
    raise ValueError(arm_id)


def lint(cli, root, gate, outdir):
    p = sh(["node", cli, root, "--gate", gate, "--fail-on", "error", "--out", outdir])
    counts = {}
    for line in p.stdout.splitlines():
        m = FINDING_RE.match(line)
        if m:
            k = f"{m.group(1)} {m.group(2)}"
            counts[k] = counts.get(k, 0) + 1
    return p.returncode, counts


def delta(base, cur):
    parts = []
    for k in sorted(set(base) | set(cur)):
        d = cur.get(k, 0) - base.get(k, 0)
        if d:
            parts.append(f"{k} {d:+d}")
    return ", ".join(parts) if parts else "差なし"


def err_delta(base, cur):
    return sum(v for k, v in cur.items() if k.startswith("error ")) - sum(v for k, v in base.items() if k.startswith("error "))


def read_current(expect, code):
    """現行出力の読み。期待と突き合わせる(導出には使わない)。"""
    if expect == "PASS":
        return "一致" if code == 0 else "**不一致**(PASS のはずが exit %d)" % code
    if expect == "RED":
        return "一致" if code == 1 else "**不一致**(違反を通した)"
    if code == 0:
        return "**FALSE-PASS**(測定不能が無音で緑)"
    if code == 1:
        return "混在(測定不能が違反と同じ error)"
    return "ツール失敗(exit 2・別経路)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plm", required=True)
    ap.add_argument("--cli", default=None)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "arms-pre.md"))
    a = ap.parse_args()
    plm = os.path.abspath(a.plm)
    cli = os.path.abspath(a.cli) if a.cli else os.path.join(plm, "packages", "cli", "dist", "main.js")

    head = sh(["git", "-C", plm, "rev-parse", "HEAD"]).stdout.strip()
    dirty = sh(["git", "-C", plm, "status", "--porcelain"]).stdout.strip()
    ev = os.path.join(plm, "packages", "core", "dist", "rules", "evaluate.js")
    ev_sha = hashlib.sha256(open(ev, "rb").read()).hexdigest()[:12] if os.path.exists(ev) else "(なし)"
    node_v = sh(["node", "--version"]).stdout.strip()
    arch_self = sh(["git", "-C", plm, "archive", "HEAD"], binary=True)
    arch_min = sh(["git", "-C", plm, "archive", "HEAD", MINIMAL_PATH], binary=True)
    if arch_self.returncode != 0 or arch_min.returncode != 0:
        print("測定不能: git archive 失敗", file=sys.stderr)
        return 2

    bases = [("plm-self", arch_self.stdout, ""), ("minimal", arch_min.stdout, MINIMAL_PATH)]
    work = tempfile.mkdtemp(prefix="eco089-")
    allres = {}
    try:
        for bname, blob, sub in bases:
            results = []
            base_row = None
            by_id = {}
            for arm in ARMS:
                if arm.get("only_base") and arm["only_base"] != bname:
                    continue
                top = os.path.join(work, bname, arm["id"])
                os.makedirs(top)
                extract(blob, top)
                root = os.path.join(top, *sub.split("/")) if sub else top
                if bname == "minimal":
                    write(os.path.join(root, "bomdd", "50-as-built.yaml"), MINIMAL_AB)
                if not mutate(arm["id"], root):
                    print(f"測定不能: {bname}/{arm['id']} の変異アンカーが土台に無い", file=sys.stderr)
                    return 2
                gates = {}
                for g in GATES:
                    out = os.path.join(work, f"out-{bname}-{arm['id']}-{g}")
                    gates[g] = lint(cli, root, g, out)
                row = dict(arm=arm, gates=gates)
                results.append(row)
                by_id[arm["id"]] = row
                if arm["id"] in ("A1-clean", "A1b-clean-unreferenced"):
                    if arm["id"] == "A1-clean":
                        base_row = row
                    for g in GATES:
                        if gates[g][0] != 0:
                            print(f"測定不能: 土台 {arm['id']}@{bname} が {g} ゲートで exit {gates[g][0]}(緑でない土台は弁別にならない)", file=sys.stderr)
                            return 2
            allres[bname] = (base_row, results, by_id)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    L = []
    L.append("# ECO-089 較正測定 — 現行 bomdd-lint に「測定できなかった」を当てた結果(是正前)")
    L.append("")
    L.append(f"- 測定日: {date.today().isoformat()}")
    L.append(f"- 土台の出所: BomDD-Plm `{head[:7]}`(git archive HEAD)・作業木: {'clean' if not dirty else 'dirty(' + str(len(dirty.splitlines())) + ' 行)'}。変異前(A1)は 2 土台とも両ゲート exit 0 を確認済み")
    L.append(f"- 計器: `{os.path.relpath(cli, plm).replace(os.sep, '/')}`・evaluate.js sha256 先頭 12= `{ev_sha}`・node {node_v}")
    L.append("- 期待は本スクリプトの ARMS に実装の前に固定(契約後の判定)。現行出力は期待と突き合わせるだけで、期待の導出に使っていない。")
    L.append("- 母集団の限界: 土台 2 種・変異 8 種(minimal のみ変種 2 本を追加)・各 1 回。変異の分布は私の設計であり、実在の事故の分布ではない。「差分」は土台(A1)に対する所見の増減。")
    L.append("")
    summary = {}
    for bname, (base_row, results, by_id) in allres.items():
        L.append(f"## 土台 {bname}")
        L.append("")
        L.append("| arm | 壊したもの | ゲート | 期待(契約後) | 現行の exit | 現行の読み | error の増分 | 所見の差分 |")
        L.append("|---|---|---|---|---|---|---|---|")
        for row in results:
            arm = row["arm"]
            for g in GATES:
                code, counts = row["gates"][g]
                exp = arm.get("expect_by_gate", {}).get(g, arm["expect"])
                bsrc = by_id[arm["baseline_arm"]] if arm.get("baseline_arm") else base_row
                bc = bsrc["gates"][g][1]
                r = read_current(exp, code)
                L.append(f"| {arm['id']} | {arm['fault']} | {g} | {exp} | {code} | {r} | {err_delta(bc, counts):+d} | {delta(bc, counts)} |")
                if arm["expect"] == "MEASUREMENT_FAILURE":
                    s = summary.setdefault((bname, g), dict(n=0, falsepass=0, mixed=0, toolfail=0, err=[]))
                    s["n"] += 1
                    s["falsepass" if code == 0 else ("mixed" if code == 1 else "toolfail")] += 1
                    s["err"].append(err_delta(bc, counts))
        L.append("")
    L.append("## 集計(期待= MEASUREMENT_FAILURE の arm。plm-self は 5 件・minimal は 6 件〔A9 を含む〕)")
    L.append("")
    L.append("| 土台 | ゲート | 無音で緑(FALSE-PASS) | 違反と混在(exit 1) | ツール失敗(exit 2) | 混在した arm の error 増分 |")
    L.append("|---|---|---|---|---|---|")
    for (bname, g), s in summary.items():
        L.append(f"| {bname} | {g} | {s['falsepass']}/{s['n']} | {s['mixed']}/{s['n']} | {s['toolfail']}/{s['n']} | {', '.join('%+d' % e for e in s['err'])} |")
    L.append("")
    L.append("読み方: 契約が成立していれば、MEASUREMENT_FAILURE の arm は PASS とも RED とも区別できる出力になる。")
    L.append("「無音で緑」は測れていないことを合格と区別できない状態、「違反と混在」は不良を見つけたのか測れなかったのかが出力から分からない状態。")
    write(a.out, "\n".join(L) + "\n")
    print(f"結果: {a.out}")
    for k, s in summary.items():
        print(k, s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
