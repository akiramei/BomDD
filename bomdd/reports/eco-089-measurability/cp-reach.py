#!/usr/bin/env python3
"""ECO-089 基準線の空白 1 点: Control Plan の特性 ID が、テスト/実装コードへ字面で届く率。

定義: 各リポの bomdd/33-control-plan.yaml の特性 ID(`id: CP-...` の字面)を母集団とし、
bomdd/ 以外のソースファイル(拡張子を限定)に ID が**字面で 1 回以上現れる**ものを「届く」とする。

測るのは字面の一致だけ — 届いた = その CP が実際に検査されている、ではない
(命名規約・ID を持たないテスト名・golden の承認記録は拾えない)。届かない = 検査されていない、でもない。
ECO-086 の INV 到達率と同じ型の測定で、「CP が検査コードへ結ばれているか」の下限の目安を与えるだけ。

加えて、bomdd-lint が実際に使う選択子(control_plan.characteristics のリスト)で何件拾えるかを併記する。
字面で拾った定義数と食い違うリポは、Control Plan の書き方(方言)が lint の想定と違う= 選択子の空振り。

測定不能は 0% に丸めない: YAML 解析不可・走査対象のソースが 0 ファイルは、その旨を状態列に残す。
使い方: python cp-reach.py <リポのパス>... [--out <md>]
"""
import argparse
import os
import re
import subprocess
import sys
from datetime import date

SRC_EXT = {".cs", ".fs", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".py", ".xaml", ".java", ".go", ".rs", ".vb", ".kt"}
SKIP_DIRS = {".git", "node_modules", "bin", "obj", "dist", "bomdd", "bomdd-kit"}
CP_DEF = re.compile(r"\bid:\s*[\"']?(CP-[A-Za-z0-9][A-Za-z0-9._-]*)")
CP_TOKEN = re.compile(r"CP-[A-Za-z0-9][A-Za-z0-9._-]*")
MAX_BYTES = 2_000_000


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def list_files(repo):
    g = sh(["git", "-C", repo, "ls-files"])
    if g.returncode == 0 and g.stdout.strip():
        return [f for f in g.stdout.splitlines() if not f.startswith(("bomdd/", "bomdd-kit/"))], "git ls-files"
    files = []
    for dp, dn, fn in os.walk(repo):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for x in fn:
            files.append(os.path.relpath(os.path.join(dp, x), repo).replace(os.sep, "/"))
    return files, "ディレクトリ走査(git 追跡なし)"


def lint_selector_count(cp_path):
    """bomdd-lint の選択子 control_plan.characteristics(リスト)で拾える件数。解析不可は None。"""
    try:
        import yaml
        with open(cp_path, encoding="utf-8") as f:
            doc = yaml.safe_load(f)
    except Exception:
        return None, "解析不可"
    cp = doc.get("control_plan") if isinstance(doc, dict) else None
    ch = cp.get("characteristics") if isinstance(cp, dict) else None
    if isinstance(ch, list):
        return len(ch), "解析可"
    return 0, "解析可(characteristics リストなし)"


def measure(repo):
    name = os.path.basename(os.path.abspath(repo))
    cp = os.path.join(repo, "bomdd", "33-control-plan.yaml")
    row = dict(repo=name, head="", dirty="", defined=None, reached=None, status="",
               yaml="", selector=None, scanned=0, files_from="")
    if not os.path.exists(cp):
        row["status"] = "対象外(33-control-plan.yaml なし)"
        return row
    row["head"] = sh(["git", "-C", repo, "rev-parse", "--short", "HEAD"]).stdout.strip() or "(git なし)"
    dirty = sh(["git", "-C", repo, "status", "--porcelain"]).stdout.strip()
    row["dirty"] = "clean" if not dirty else f"dirty({len(dirty.splitlines())})"
    ids = set()
    with open(cp, encoding="utf-8", errors="replace") as f:
        for line in f:
            ids.update(CP_DEF.findall(line))
    ids = sorted(ids)
    row["selector"], row["yaml"] = lint_selector_count(cp)
    if not ids:
        row["status"] = "測定不能(特性 ID が字面で 1 件も拾えない)"
        return row
    files, row["files_from"] = list_files(repo)
    seen = set()
    for rel in files:
        if os.path.splitext(rel)[1].lower() not in SRC_EXT:
            continue
        p = os.path.join(repo, rel)
        try:
            if os.path.getsize(p) > MAX_BYTES:
                continue
            with open(p, encoding="utf-8", errors="replace") as f:
                seen.update(CP_TOKEN.findall(f.read()))
        except OSError:
            continue
        row["scanned"] += 1
    row["defined"] = len(ids)
    if row["scanned"] == 0:
        row["status"] = "測定不能(走査対象のソースが 0 ファイル — 届く率を出さない)"
        return row
    row["reached"] = len([i for i in ids if i in seen])
    row["status"] = "測定済み(字面)"
    if row["selector"] is not None and row["selector"] != row["defined"]:
        row["status"] += f"・**母集団不一致**(字面 {row['defined']} ≠ 選択子 {row['selector']} — 率は字面で拾えた CP- 接頭辞の部分集合にしか当てはまらない)"
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repos", nargs="+")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "cp-reach.md"))
    a = ap.parse_args()
    rows = [measure(r) for r in a.repos]
    L = []
    L.append("# ECO-089 基準線 — Control Plan の特性 ID がコードへ字面で届く率")
    L.append("")
    L.append(f"- 測定日: {date.today().isoformat()}")
    L.append("- 母集団= 各リポ bomdd/33-control-plan.yaml に `id: CP-...` の字面で現れる異なる ID。届く= bomdd/ 以外のソースファイル(拡張子を限定)に字面で現れる。")
    L.append("- **限界**: 字面一致のみ。届く≠検査されている(ID を書かないテスト・golden の承認記録・命名規約は拾えない)。届かない≠検査されていない。")
    L.append("  ID を持たない慣行のリポは過小に、コメントに ID を貼るだけの慣行は過大に出る。1 リポ 1 時点・各 1 回。作業木が dirty のリポは未コミットの変更を含む。")
    L.append("- 「lint の選択子で拾える数」= bomdd-lint が読む control_plan.characteristics のリストの件数。字面の定義数と大きく食い違えば、その Control Plan の書き方は lint の想定と違う。")
    L.append("")
    L.append("| リポ | HEAD | 作業木 | 33 の解析 | 字面の CP 定義数 | lint の選択子で拾える数 | コードへ届く | 届く率 | 状態 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        sel = "—" if r["selector"] is None else str(r["selector"])
        if r["defined"] is None:
            L.append(f"| {r['repo']} | {r['head']} | {r['dirty']} | {r['yaml'] or '—'} | — | {sel} | — | — | {r['status']} |")
        elif r["reached"] is None:
            L.append(f"| {r['repo']} | {r['head']} | {r['dirty']} | {r['yaml']} | {r['defined']} | {sel} | — | — | {r['status']} |")
        else:
            pct = f"{100 * r['reached'] / r['defined']:.0f}%"
            L.append(f"| {r['repo']} | {r['head']} | {r['dirty']} | {r['yaml']} | {r['defined']} | {sel} | {r['reached']} | {pct} | {r['status']}(走査 {r['scanned']} ファイル・{r['files_from']}) |")
    L.append("")
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(L) + "\n")
    print(f"結果: {a.out}")
    for r in rows:
        print(r["repo"], r["status"], r["defined"], r["selector"], r["reached"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
