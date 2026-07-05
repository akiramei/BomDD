#!/usr/bin/env python3
"""ui-mock-inspect — モック受入検査のワークフロー治具(ui-ir-ui-bom.md §17/§17.1 の編成・強制層)。

プロンプト(正典: method/prompts/ui-mock-refmodel.md / ui-mock-coverage.md)が判断を、
本治具が規律(隔離ステージング・工程順序・予算・台帳記入・来歴)を担う。
検査内容の質と裁定は機械化しない — 機械化するのは凍結済み規律だけである。

サブコマンド:
    init        モックパッケージの manifest 化(sha256)+隔離ステージング生成
    skip        refmodel 段のスキップ(理由必須。スキップも来歴)
    emit-prompt 正典プロンプト+ステージング一覧から検査プロンプトを合成(版数を来歴記録)
    check       検査報告書のスキーマ/予算 lint。exit 0=合格 / 1=違反 / 2=使い方誤り
    hearing     ①〜④回答を 37 台帳へ原子的に記入(ruling+status+decided_at をセットで)
    gate-cad    CAD 工程(/bomdd-ui-cad)の起動条件検査
    status      状態機械の現在地
    --selftest  違反フィクスチャを含む自己検査

隔離の限界(正直な線引き): ステージングは検査エージェントの入力からリポへのパスを排除し
バーを大幅に上げるが、エージェントの探索を技術的に不可能にはしない(サンドボックス非依存)。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # hearing 以外は不要

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
CANON = {"refmodel": "ui-mock-refmodel.md", "lint": "ui-mock-coverage.md"}
STATE_NAME = "inspection-state.json"
BUDGET = {"refmodel": 15, "lint": 20}
COST_RANK = {"high": 3, "medium": 2, "low": 1}
CLS = {1: "intentional-non-adoption", 2: "oversight", 3: "out-of-scope", 4: "deferred"}
CLS_NEG = {
    1: "採用する(参照モデル準拠)— 本裁定により否定",
    2: "現モックのままで十分 — 本裁定により否定(モック改訂へ)",
    3: "製品スコープに含める — 本裁定により否定",
    4: "現フェーズで実装する — 本裁定により否定(後フェーズへ)",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state_path(workdir: Path) -> Path:
    return workdir / STATE_NAME


def load_state(workdir: Path) -> dict:
    p = state_path(workdir)
    if not p.is_file():
        sys.exit(f"[err] {p} がありません。先に init を実行してください(exit 2)")
    return json.loads(p.read_text(encoding="utf-8"))


def save_state(workdir: Path, st: dict) -> None:
    state_path(workdir).write_text(
        json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- init
def cmd_init(args) -> int:
    workdir = Path(args.dir)
    workdir.mkdir(parents=True, exist_ok=True)
    if state_path(workdir).exists() and not args.force:
        sys.exit(f"[err] {state_path(workdir)} は既にあります(--force で作り直し)(exit 2)")
    staging = workdir / "staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    files = []
    for i, m in enumerate(args.mock, 1):
        src = Path(m)
        if not src.is_file():
            sys.exit(f"[err] モックファイルがありません: {src}(exit 2)")
        dst = staging / f"{i:02d}-{src.name}"
        shutil.copy2(src, dst)
        files.append({"origin": str(src), "staged": str(dst), "sha256": sha256(src)})
    st = {
        "created": date.today().isoformat(),
        "manifest": {"files": files},
        "stages": {
            "refmodel": {"status": "pending"},
            "lint": {"status": "pending"},
            "cad": {"status": "locked"},
        },
    }
    save_state(workdir, st)
    print(f"[ok] manifest {len(files)} files / staging: {staging}")
    return 0


# ---------------------------------------------------------------- skip
def cmd_skip(args) -> int:
    if args.stage != "refmodel":
        sys.exit("[err] スキップ可能なのは refmodel だけです(lint は必須)(exit 2)")
    if not args.reason.strip():
        sys.exit("[err] --reason は必須です(スキップも来歴)(exit 2)")
    workdir = Path(args.dir)
    st = load_state(workdir)
    st["stages"]["refmodel"] = {
        "status": "skipped", "reason": args.reason, "decided_at": date.today().isoformat()}
    save_state(workdir, st)
    print(f"[ok] refmodel を skipped として記録: {args.reason}")
    return 0


# ---------------------------------------------------------------- emit-prompt
def canonical_body(stage: str) -> tuple[str, str, str]:
    src = PROMPTS_DIR / CANON[stage]
    if not src.is_file():
        sys.exit(f"[err] 正典プロンプトがありません: {src}(exit 2)")
    text = src.read_text(encoding="utf-8")
    if "\n---\n" not in text:
        sys.exit(f"[err] 正典プロンプトに区切り(---)がありません: {src}(exit 2)")
    body = text.split("\n---\n", 1)[1]
    return body, str(src), hashlib.sha256(text.encode("utf-8")).hexdigest()


def cmd_emit(args) -> int:
    workdir = Path(args.dir)
    st = load_state(workdir)
    if args.stage == "lint" and st["stages"]["refmodel"]["status"] not in ("done", "skipped"):
        sys.exit("[err] 工程順序違反: lint の前に refmodel を done か skipped にしてください"
                 "(スキップは skip --stage refmodel --reason)(exit 1)")
    body, src, digest = canonical_body(args.stage)
    lines = [
        f"# 検査プロンプト(合成: ui-mock-inspect emit-prompt / stage={args.stage})",
        f"# 正典: {src}",
        f"# 正典 sha256: {digest}",
        "",
        "## 厳格な入力制限(本案件の具体化 — 違反は検査を無効にする)",
        "",
        "読んでよいファイルは次のステージング済みファイルのみ:",
        "",
    ]
    for i, f in enumerate(st["manifest"]["files"], 1):
        lines.append(f"{i}. {f['staged']}(元: {Path(f['origin']).name}, sha256={f['sha256'][:12]}…)")
    lines += [
        "",
        "上記以外のファイル・ディレクトリ(リポジトリ本体・実装コード・台帳類・git 履歴・その他一切)を"
        "読むこと・検索することを禁止する。Glob/Grep も使わない。",
        "",
        "---",
        body,
    ]
    out = Path(args.out) if args.out else workdir / f"prompt-{args.stage}.md"
    out.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    st["stages"][args.stage].update({"prompt": str(out), "prompt_canon_sha256": digest})
    save_state(workdir, st)
    print(f"[ok] {out} を合成しました(正典 {Path(src).name} / sha256 {digest[:12]}…)")
    return 0


# ---------------------------------------------------------------- check
def find_sections(text: str) -> list[tuple[str, int, int]]:
    heads = list(re.finditer(r"(?m)^#{2,3}[^\n]*", text))
    out = []
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        out.append((h.group(0), h.end(), end))
    return out


def section_block(text: str, name: str) -> str | None:
    for head, start, end in find_sections(text):
        if name in head:
            return text[start:end]
    return None


def split_numbered(block: str) -> list[tuple[int, str]]:
    marks = list(re.finditer(r"(?m)^(?:\*\*(\d+)\.|(\d+)\.\s)", block))
    items = []
    for i, m in enumerate(marks):
        num = int(m.group(1) or m.group(2))
        end = marks[i + 1].start() if i + 1 < len(marks) else len(block)
        items.append((num, block[m.start():end]))
    return items


COST_RE = re.compile(r"(?:【\s*|手戻りコスト[::]?\s*\**\s*)(high|medium|low)")


def check_report(stage: str, text: str, forbidden: list[str]) -> tuple[list[str], list[str]]:
    """returns (violations, warnings)"""
    v, w = [], []
    if stage == "refmodel":
        secs, item_sec, needs_mark = ["段A", "段B", "段C", "段D"], "段D", "①"
    else:
        secs, item_sec, needs_mark = ["層1", "層2", "層3", "層4"], "層3", None
    for s in secs:
        if section_block(text, s) is None:
            v.append(f"必須セクションが無い: {s}")
    block = section_block(text, item_sec)
    items = split_numbered(block) if block else []
    if block is not None and not items:
        v.append(f"{item_sec} に番号付き項目が見つからない")
    if len(items) > BUDGET[stage]:
        v.append(f"予算超過: {item_sec} が {len(items)} 件(上限 {BUDGET[stage]})")
    prev = 4
    for num, body in items:
        m = COST_RE.search(body)
        if not m:
            v.append(f"{item_sec} #{num}: 手戻りコスト(high/medium/low)が無い")
            continue
        rank = COST_RANK[m.group(1)]
        if rank > prev:
            v.append(f"{item_sec} #{num}: コスト順序違反({m.group(1)} が前項より高い — 降順必須)")
        prev = rank
        if needs_mark and needs_mark not in body:
            v.append(f"{item_sec} #{num}: ヒアリング分類(①〜④)の形になっていない")
    if stage == "refmodel":
        dan_a = section_block(text, "段A") or ""
        if re.search(r"\*\*Q4", dan_a):
            v.append("段A: 較正質問が 3 問を超えている(Q4 を検出)")
        if not re.search(r"除外|含めていない", text):
            w.append("範囲規律の除外リストが見当たらない(範囲宣言を推奨)")
    else:
        rep = section_block(text, "層4") or ""
        if len(split_numbered(rep)) < 10:
            w.append("層4 復唱文が 10 文未満(密度を確認)")
        if "検査サマリ" not in text:
            w.append("検査サマリが無い")
    for pat in forbidden:
        m = re.search(pat, text)
        if m:
            v.append(f"禁止パターン検出(隔離違反の疑い): {pat!r} → {m.group(0)!r}")
    return v, w


def cmd_check(args) -> int:
    text = Path(args.report).read_text(encoding="utf-8")
    v, w = check_report(args.stage, text, args.forbidden or [])
    for x in w:
        print(f"[warn] {x}")
    for x in v:
        print(f"[NG]   {x}")
    if v:
        print(f"[fail] {args.stage}: 違反 {len(v)} 件(exit 1)")
        return 1
    print(f"[pass] {args.stage}: 違反 0(警告 {len(w)})")
    if args.standalone:
        return 0
    workdir = Path(args.dir)
    st = load_state(workdir)
    if args.stage == "lint" and st["stages"]["refmodel"]["status"] not in ("done", "skipped"):
        print("[NG]   工程順序違反: refmodel が未決着のまま lint を確定できない(exit 1)")
        return 1
    st["stages"][args.stage].update({
        "status": "done", "report": str(Path(args.report)),
        "report_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "checked_at": date.today().isoformat()})
    if (st["stages"]["lint"]["status"] == "done"
            and st["stages"]["refmodel"]["status"] in ("done", "skipped")):
        st["stages"]["cad"]["status"] = "unlocked"
        print("[ok]  CAD 工程を解錠しました(/bomdd-ui-cad が実行可能)")
    save_state(workdir, st)
    return 0


# ---------------------------------------------------------------- hearing
def cmd_hearing(args) -> int:
    if yaml is None:
        sys.exit("[err] hearing には PyYAML が必要です: pip install pyyaml(exit 2)")
    answers = (yaml.safe_load(Path(args.answers).read_text(encoding="utf-8")) or {}).get("answers", [])
    if not answers:
        sys.exit("[err] answers が空です(exit 2)")
    for a in answers:
        c = a.get("classification")
        if c not in (1, 2, 3, 4):
            sys.exit(f"[err] classification は 1〜4: {a}(exit 2)")
        if c == 1 and not str(a.get("note", "")).strip():
            sys.exit(f"[err] ①意図的な非採用には note(理由)が必須: {a.get('gap')}(exit 2)")
    rul_path = Path(args.rulings)
    text = rul_path.read_text(encoding="utf-8")
    doc = yaml.safe_load(text) or {}
    existing = doc.get("rulings") or []
    n0 = len(existing)
    max_id = 0
    for m in re.finditer(r"UQ-(\d+)", text):
        max_id = max(max_id, int(m.group(1)))
    im = re.search(r"(?m)^(\s*)- id:", text)
    indent = im.group(1) if im else "  "
    today = date.today().isoformat()
    recs = []
    for a in answers:
        max_id += 1
        note = str(a.get("note", "")).strip()
        recs.append("\n".join([
            f"{indent}- id: UQ-{max_id:04d}",
            f"{indent}  status: ruled",
            f"{indent}  type: scope-gap",
            f"{indent}  blocking: false",
            f"{indent}  source: mock-inspect hearing",
            f"{indent}  target:",
            f"{indent}    surface_label: {json.dumps(str(a['gap']), ensure_ascii=False)}",
            f"{indent}  question: >",
            f"{indent}    参照概念モデル gap「{a['gap']}」はモックに無い。意図的な非採用か、検討漏れか、スコープ外か、フェーズ計画か。",
            f"{indent}  options: [intentional-non-adoption, oversight, out-of-scope, deferred]",
            f"{indent}  ruling: {CLS[a['classification']]}",
            f"{indent}  negative_rulings:",
            f"{indent}    - option: {json.dumps(CLS_NEG[a['classification']], ensure_ascii=False)}",
            f"{indent}  decided_by: human-hearing",
            f"{indent}  decided_at: \"{today}\"",
        ] + ([f"{indent}  note: {json.dumps(note, ensure_ascii=False)}"] if note else [])))
    new_text = text.rstrip("\n") + "\n" + "\n".join(recs) + "\n"
    doc2 = yaml.safe_load(new_text)
    n1 = len(doc2.get("rulings") or [])
    if n1 != n0 + len(answers):
        sys.exit(f"[err] 追記後の台帳が壊れています(件数 {n0}→{n1}, 期待 {n0 + len(answers)})。"
                 f"ファイルは変更していません(exit 1)")
    rul_path.write_text(new_text, encoding="utf-8", newline="\n")
    print(f"[ok] 台帳へ {len(answers)} 件を原子記入({n0}→{n1}件・UQ-{max_id:04d} まで)")
    if any(a["classification"] == 2 for a in answers):
        print("[flow] ②検討漏れ あり → モック改訂へ戻ってください(1 に戻る)")
        return 3
    return 0


# ---------------------------------------------------------------- gate-cad / status
def cmd_gate_cad(args) -> int:
    st = load_state(Path(args.dir))
    if st["stages"]["cad"]["status"] == "unlocked":
        print("[pass] CAD 工程は解錠済み(lint 合格+refmodel 決着)")
        return 0
    missing = []
    if st["stages"]["refmodel"]["status"] not in ("done", "skipped"):
        missing.append("refmodel が未決着(/bomdd-refmodel を実行するか skip --reason)")
    if st["stages"]["lint"]["status"] != "done":
        missing.append("lint が未合格(/bomdd-mock-lint を実行)")
    for m in missing:
        print(f"[NG]   {m}")
    print("[fail] CAD 工程は施錠中(exit 1)")
    return 1


def cmd_status(args) -> int:
    st = load_state(Path(args.dir))
    print(f"manifest: {len(st['manifest']['files'])} files({st['created']})")
    for k in ("refmodel", "lint", "cad"):
        s = st["stages"][k]
        extra = " / ".join(f"{a}={b}" for a, b in s.items() if a != "status")
        print(f"  {k:9s}: {s['status']}" + (f"({extra})" if extra else ""))
    return 0


# ---------------------------------------------------------------- selftest
VALID_REF = """## 段A: 製品クラス較正
- **Q1**: 拡張しますか?
- **Q2**: 永続化しますか?
## 段B: 参照概念モデル
| B1 | コア | x | y |
## 段C: カバレッジ写像
- B1: 一式
## 段D: gap 一覧
**1. B8 進捗** — 状態: 完全に無い
- 質問: ①意図 ②漏れ ③スコープ外 ④フェーズ のどれですか?
- 手戻りコスト: **high** — 状態設計に波及
**2. B14 About** — 状態: 痕跡のみ
- 質問: ①/②/③/④ のどれですか?
- 手戻りコスト: **low** — 独立表示物
除外: マルチトラック(範囲規律)
"""

VALID_LINT = """## 層1: 内部矛盾検査
なし
## 層2: カバレッジ写像
一式
## 層3: 隣接未カバー質問
1. **出力先**【high — 意味論に波及】
2. **国際化**【low — 見た目】
## 層4: 復唱文
""" + "\n".join(f"{i}. 文{i}。" for i in range(1, 13)) + """
検査サマリ: 矛盾0・質問2
"""


def selftest() -> int:
    import tempfile
    ok = [0]

    def t(name, cond):
        ok[0] += 0 if cond else 1
        print(f"  {'ok' if cond else 'NG'}: {name}")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        m1 = tmp / "mock.html"; m1.write_text("<html/>", encoding="utf-8")
        m2 = tmp / "notes.md"; m2.write_text("# notes", encoding="utf-8")
        wd = tmp / "insp"

        class A: pass
        a = A(); a.dir = str(wd); a.mock = [str(m1), str(m2)]; a.force = False
        t("init", cmd_init(a) == 0 and (wd / "staging" / "01-mock.html").is_file())

        a2 = A(); a2.dir = str(wd); a2.stage = "lint"; a2.out = None
        try:
            cmd_emit(a2); t("emit lint before refmodel → 拒否", False)
        except SystemExit:
            t("emit lint before refmodel → 拒否", True)

        a3 = A(); a3.dir = str(wd); a3.stage = "refmodel"; a3.reason = "製品2画面目(参照モデル裁定済み)"
        t("skip refmodel(理由付き)", cmd_skip(a3) == 0)
        t("emit lint after skip", cmd_emit(a2) == 0
          and "厳格な入力制限" in (wd / "prompt-lint.md").read_text(encoding="utf-8"))

        # check: lint
        rep = wd / "lint-report.md"; rep.write_text(VALID_LINT, encoding="utf-8")
        a4 = A(); a4.dir = str(wd); a4.stage = "lint"; a4.report = str(rep)
        a4.forbidden = []; a4.standalone = False
        t("check lint valid → pass+CAD解錠", cmd_check(a4) == 0)
        a5 = A(); a5.dir = str(wd)
        t("gate-cad unlocked", cmd_gate_cad(a5) == 0)

        bad = VALID_LINT.replace("## 層3: 隣接未カバー質問\n",
                                 "## 層3: 隣接未カバー質問\n" +
                                 "\n".join(f"{i}. **q{i}**【high — x】" for i in range(1, 22)) + "\n")
        rep2 = wd / "bad21.md"; rep2.write_text(bad, encoding="utf-8")
        a4b = A(); a4b.dir = str(wd); a4b.stage = "lint"; a4b.report = str(rep2)
        a4b.forbidden = []; a4b.standalone = True
        t("check lint 予算超過(21+2問)→ fail", cmd_check(a4b) == 1)
        rep3 = wd / "nol4.md"; rep3.write_text(VALID_LINT.replace("## 層4: 復唱文", "## 層X"), encoding="utf-8")
        a4c = A(); a4c.dir = str(wd); a4c.stage = "lint"; a4c.report = str(rep3)
        a4c.forbidden = []; a4c.standalone = True
        t("check lint 層4欠落 → fail", cmd_check(a4c) == 1)
        a4d = A(); a4d.dir = str(wd); a4d.stage = "lint"; a4d.report = str(rep)
        a4d.forbidden = [r"ViewModels/"]; a4d.standalone = True
        t("forbidden 不検出 → pass", cmd_check(a4d) == 0)
        repf = wd / "contam.md"; repf.write_text(VALID_LINT + "\n根拠: ViewModels/Main.cs", encoding="utf-8")
        a4e = A(); a4e.dir = str(wd); a4e.stage = "lint"; a4e.report = str(repf)
        a4e.forbidden = [r"ViewModels/"]; a4e.standalone = True
        t("forbidden 検出(隔離違反疑い)→ fail", cmd_check(a4e) == 1)

        # check: refmodel
        wr = tmp / "insp2"
        ar = A(); ar.dir = str(wr); ar.mock = [str(m1)]; ar.force = False
        cmd_init(ar)
        ae = A(); ae.dir = str(wr); ae.stage = "refmodel"; ae.out = None
        t("emit refmodel", cmd_emit(ae) == 0)
        rr = wr / "ref.md"; rr.write_text(VALID_REF, encoding="utf-8")
        ac = A(); ac.dir = str(wr); ac.stage = "refmodel"; ac.report = str(rr)
        ac.forbidden = []; ac.standalone = False
        t("check refmodel valid → pass", cmd_check(ac) == 0)
        many = VALID_REF + "\n".join(
            f"**{i}. B{i} x**\n- 質問: ① のどれ?\n- 手戻りコスト: **low** — x" for i in range(3, 18))
        r16 = wr / "r16.md"; r16.write_text(many, encoding="utf-8")
        ac2 = A(); ac2.dir = str(wr); ac2.stage = "refmodel"; ac2.report = str(r16)
        ac2.forbidden = []; ac2.standalone = True
        t("check refmodel 予算超過(17 gap)→ fail", cmd_check(ac2) == 1)
        nomark = VALID_REF.replace("①意図 ②漏れ ③スコープ外 ④フェーズ のどれですか?", "どうしますか?")
        rn = wr / "nomark.md"; rn.write_text(nomark, encoding="utf-8")
        ac3 = A(); ac3.dir = str(wr); ac3.stage = "refmodel"; ac3.report = str(rn)
        ac3.forbidden = []; ac3.standalone = True
        t("check refmodel ①欠落 → fail", cmd_check(ac3) == 1)
        disorder = VALID_REF.replace("**high** — 状態設計に波及", "**low** — x").replace(
            "**low** — 独立表示物", "**high** — y")
        rd = wr / "disorder.md"; rd.write_text(disorder, encoding="utf-8")
        ac4 = A(); ac4.dir = str(wr); ac4.stage = "refmodel"; ac4.report = str(rd)
        ac4.forbidden = []; ac4.standalone = True
        t("check refmodel コスト順序違反 → fail", cmd_check(ac4) == 1)

        # hearing
        if yaml is not None:
            led = tmp / "37.yaml"
            led.write_text("version: 1\nrulings:\n  - id: UQ-0001\n    status: ruled\n",
                           encoding="utf-8")
            ans = tmp / "ans.yaml"
            ans.write_text(
                "answers:\n"
                "  - gap: B11 空状態\n    classification: 2\n"
                "  - gap: B15 a11y\n    classification: 3\n    note: 対象外\n",
                encoding="utf-8")
            ah = A(); ah.answers = str(ans); ah.rulings = str(led)
            rc = cmd_hearing(ah)
            doc = yaml.safe_load(led.read_text(encoding="utf-8"))
            t("hearing 追記(2件・②あり→exit 3)", rc == 3 and len(doc["rulings"]) == 3
              and doc["rulings"][1]["ruling"] == "oversight"
              and doc["rulings"][1]["negative_rulings"])
            bad_ans = tmp / "bad.yaml"
            bad_ans.write_text("answers:\n  - gap: X\n    classification: 1\n", encoding="utf-8")
            ab = A(); ab.answers = str(bad_ans); ab.rulings = str(led)
            try:
                cmd_hearing(ab); t("hearing ①理由なし → 拒否", False)
            except SystemExit:
                t("hearing ①理由なし → 拒否", True)
        else:
            print("  skip: hearing(PyYAML なし)")

    print(f"[selftest] {'PASS' if ok[0] == 0 else f'FAIL({ok[0]})'}")
    return 0 if ok[0] == 0 else 1


# ---------------------------------------------------------------- main
def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    if "--selftest" in sys.argv:
        return selftest()
    ap = argparse.ArgumentParser(description="モック受入検査ワークフロー治具(§17)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("--dir", required=True)
    p.add_argument("--mock", nargs="+", required=True); p.add_argument("--force", action="store_true")
    p = sub.add_parser("skip"); p.add_argument("--dir", required=True)
    p.add_argument("--stage", required=True); p.add_argument("--reason", required=True)
    p = sub.add_parser("emit-prompt"); p.add_argument("--dir", required=True)
    p.add_argument("--stage", required=True, choices=["refmodel", "lint"])
    p.add_argument("--out", default=None)
    p = sub.add_parser("check"); p.add_argument("--dir", default=".")
    p.add_argument("--stage", required=True, choices=["refmodel", "lint"])
    p.add_argument("--report", required=True)
    p.add_argument("--forbidden", action="append", default=[])
    p.add_argument("--standalone", action="store_true",
                   help="状態を更新せず報告書だけ検査(遡及検証用)")
    p = sub.add_parser("hearing"); p.add_argument("--answers", required=True)
    p.add_argument("--rulings", required=True)
    p = sub.add_parser("gate-cad"); p.add_argument("--dir", required=True)
    p = sub.add_parser("status"); p.add_argument("--dir", required=True)
    args = ap.parse_args()
    return {"init": cmd_init, "skip": cmd_skip, "emit-prompt": cmd_emit, "check": cmd_check,
            "hearing": cmd_hearing, "gate-cad": cmd_gate_cad, "status": cmd_status}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
