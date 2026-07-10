#!/usr/bin/env python3
"""self-conformance — 方法論リポ(BomDD)全体の自己適合ゲート(harness ECO-006)

外部レビュー所見6(2026-07-10)「リポジトリ全体の自己適合ゲートがない — テンプレート構文、
初期化後の動作、ツール異常系、既知の実験結果を一括検証する入口がない」への回答。
所見1〜5 の是正(ECO-001〜005)を恒久回帰として収載する。

検査(fast tier — 既定):
  C1 yaml-parse     : method/templates/**/*.yaml が PyYAML で全数パース(ECO-001 恒久回帰)
  C2 json-parse     : method/ 配下の *.json が全数パース
  C3 register       : ハーネス台帳がパースし、verified エントリは diff_audit.head で窓が閉じている
  C4 scaffold       : bomdd-init が一時ディレクトリへ scaffold でき、生成物に方法論リポの
                      絶対パスが漏れない(bomdd.lock の origin_path=来歴のみ許容)+
                      lock がパースし kit の files 数が manifest と一致(ECO-004 恒久回帰)
  C5 fail-closed    : stage0-survey / impact-retrospective が存在しないリポに exit 2(ECO-002/003)
  C6 gate-mutation  : ui-cad-gate が「理由なし rejected」を落とし(exit≠0)、
                      「根拠+決定者つき rejected」を通す(exit 0)— 対検査(ECO-005 恒久回帰)
  C7 readme-drift   : README の「スキル N 本」表記が bomdd-init.SKILLS の実数と一致
  C8 root-hygiene   : リポ直下にパス破損の化石(名前に ':' を含む等)がない

検査(--dotnet tier — 任意):
  C9 loop-suites    : loops/expected-results.yaml の期待結果 manifest と実測を突合 —
                      expected_failed は「失敗しなければならない」(実験証拠の保存検査)・
                      それ以外は全合格(リグレッション検出)

欠測・実行不能は「問題なし」ではない: 検査対象が見つからない/実行できない場合も FAIL。
exit 0 = 全検査合格 / exit 1 = 不適合あり / exit 2 = ゲート自身が実行不能。
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("[self-conformance] 測定不能: PyYAML が必要です", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
FAILURES: list[str] = []


def check(cid: str, ok: bool, msg: str) -> None:
    print(f"[{cid}] {'PASS' if ok else 'FAIL'} {msg}")
    if not ok:
        FAILURES.append(f"{cid}: {msg}")


def run(args: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", **kw)


# --- C1/C2 テンプレ・スキーマの構文 -------------------------------------------------
def c1_yaml() -> None:
    files = sorted((ROOT / "method").rglob("*.yaml")) + sorted((ROOT / "method").rglob("*.yml"))
    bad = []
    for f in files:
        try:
            yaml.safe_load(f.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            bad.append(f"{f.relative_to(ROOT)}: {str(e).splitlines()[0]}")
    check("C1", bool(files) and not bad,
          f"YAML {len(files)} 件パース" + (f" — 失敗: {bad}" if bad else ""))


def c2_json() -> None:
    files = sorted((ROOT / "method").rglob("*.json"))
    bad = []
    for f in files:
        try:
            json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            bad.append(f"{f.relative_to(ROOT)}: {e}")
    check("C2", bool(files) and not bad,
          f"JSON {len(files)} 件パース" + (f" — 失敗: {bad}" if bad else ""))


# --- C3 ハーネス台帳の規律 ----------------------------------------------------------
def c3_register() -> None:
    reg_path = ROOT / "bomdd" / "60-change-register.yaml"
    if not reg_path.exists():
        check("C3", False, f"ハーネス台帳がない: {reg_path}")
        return
    try:
        reg = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        check("C3", False, f"台帳がパース不能: {e}")
        return
    open_windows = [c["id"] for c in reg.get("changes") or []
                    if c.get("status") == "verified"
                    and not (c.get("diff_audit") or {}).get("head")]
    check("C3", not open_windows,
          "台帳パース+verified の diff 窓" + (f" — head 未設定: {open_windows}" if open_windows else "(全て閉じている)"))


# --- C4 scaffold 煙試験(ECO-004) ---------------------------------------------------
def c4_scaffold() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="bomdd-selfconf-"))
    try:
        p = run([sys.executable, str(ROOT / "method" / "tools" / "bomdd-init.py"),
                 "SelfConfSmoke", "--dir", str(tmp), "--no-gui", "--no-git"])
        prod = tmp / "SelfConfSmoke"
        if p.returncode != 0:
            check("C4", False, f"bomdd-init が失敗 (exit {p.returncode}): {p.stderr.strip()[:120]}")
            return
        leaks = []
        needle = str(ROOT).replace("\\", "/")
        for f in prod.rglob("*"):
            if not f.is_file() or "bomdd-kit" in f.parts or f.name == "bomdd.lock":
                continue
            try:
                text = f.read_text(encoding="utf-8").replace("\\", "/")
            except (UnicodeDecodeError, OSError):
                continue
            if needle in text:
                leaks.append(str(f.relative_to(prod)))
        lock = yaml.safe_load((prod / "bomdd.lock").read_text(encoding="utf-8"))["bomdd_lock"]
        manifest = json.loads((prod / lock["kit"]["manifest"]).read_text(encoding="utf-8"))
        count_ok = lock["kit"]["files"] == len(manifest["files"])
        check("C4", not leaks and count_ok,
              f"scaffold 煙試験(絶対パス漏れ {len(leaks)} 件・lock/manifest 整合 {count_ok})"
              + (f" — 漏れ: {leaks[:3]}" if leaks else ""))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- C5 fail-closed 陽性対照(ECO-002/003) ------------------------------------------
def c5_fail_closed() -> None:
    ghost = str(ROOT / "no-such-repo-selfconf")
    for cid, tool in [("C5a", "stage0-survey.py"), ("C5b", "impact-retrospective.py")]:
        p = run([sys.executable, str(ROOT / "method" / "tools" / tool), "--repo", ghost])
        check(cid, p.returncode == 2,
              f"{tool} 存在しないリポ → exit {p.returncode}(期待 2・測定不能で停止)")


# --- C6 ui-cad-gate 対検査(ECO-005) ------------------------------------------------
_FIXTURE_COMMON = {
    "ui-ir.json": '{"actions": [{"uiId": "action.selfconf.one"}], "inputs": []}',
    "ui-bom.json": '{"items": []}',
    "ui-trace-map.json": '{"mappings": []}',
}
_REJECTED_BARE = """rulings:
  - id: UQ-SELFCONF-1
    status: rejected
    target: {ui_ids: ["action.selfconf.one"]}
    question: 理由なし黙殺(通ってはならない)
"""
_REJECTED_REASONED = """rulings:
  - id: UQ-SELFCONF-1
    status: rejected
    target: {ui_ids: ["action.selfconf.one"]}
    question: 根拠つき却下(通らねばならない)
    negative_rulings: [{option: adopt, why: 装飾要素のため採用しない}]
    evidence: ["self-conformance fixture"]
    decided_by: user
"""


def c6_gate_mutation() -> None:
    gate = ROOT / "method" / "tools" / "ui-cad-gate.py"
    for cid, rulings, expect_fail, label in [
            ("C6a", _REJECTED_BARE, True, "理由なし rejected を遮断"),
            ("C6b", _REJECTED_REASONED, False, "根拠つき rejected を通す")]:
        tmp = Path(tempfile.mkdtemp(prefix="bomdd-selfconf-gu-"))
        try:
            for name, body in _FIXTURE_COMMON.items():
                (tmp / name).write_text(body, encoding="utf-8")
            (tmp / "37-ui-rulings.yaml").write_text(rulings, encoding="utf-8")
            p = run([sys.executable, str(gate), "--ui-dir", str(tmp)])
            ok = (p.returncode != 0) if expect_fail else (p.returncode == 0)
            check(cid, ok, f"{label}(exit {p.returncode})")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# --- C7 README の陳腐化(スキル本数) ------------------------------------------------
def c7_readme() -> None:
    init_src = (ROOT / "method" / "tools" / "bomdd-init.py").read_text(encoding="utf-8")
    m = re.search(r"^SKILLS\s*=\s*\[(.*?)\]", init_src, re.S | re.M)
    actual = len(re.findall(r'"[^"]+"', m.group(1))) if m else None
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    claims = [int(n) for n in re.findall(r"スキル\s*(\d+)\s*本", readme)]
    ok = actual is not None and all(c == actual for c in claims)
    check("C7", ok, f"README のスキル本数表記 {claims} = SKILLS 実数 {actual}")


# --- C8 リポ直下の衛生 ---------------------------------------------------------------
def c8_hygiene() -> None:
    # ':' の私用領域代替(U+F03A)・全角(U+FF1A)は Windows のパス破損化石の典型
    fossils = [e.name for e in ROOT.iterdir()
               if any(c in e.name for c in (":", "", "："))
               or re.search(r"Users\w+repos", e.name)]
    check("C8", not fossils, "リポ直下にパス破損の化石なし" + (f" — {fossils}" if fossils else ""))


# --- C9 loop スイート vs 期待結果 manifest(--dotnet) --------------------------------
def c9_dotnet() -> None:
    manifest_path = ROOT / "loops" / "expected-results.yaml"
    if not manifest_path.exists():
        check("C9", False, f"期待結果 manifest がない: {manifest_path}")
        return
    doc = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    for suite in doc.get("suites") or []:
        proj = suite["project"]
        # 文字列(旧形)と mapping(test/class/signature — playbook §13・ECO-007)の両形を受ける
        expected_failed, signatures = set(), {}
        for e in suite.get("expected_failed") or []:
            if isinstance(e, dict):
                expected_failed.add(e["test"])
                if e.get("signature"):
                    signatures[e["test"]] = e["signature"]
            else:
                expected_failed.add(e)
        tmp = Path(tempfile.mkdtemp(prefix="bomdd-selfconf-trx-"))
        try:
            p = run(["dotnet", "test", str(ROOT / proj), "--nologo",
                     "--logger", "trx;LogFileName=out.trx", "--results-directory", str(tmp)],
                    env=None)
            trx = tmp / "out.trx"
            if not trx.exists():
                check("C9", False, f"{proj}: trx が生成されない (dotnet exit {p.returncode})")
                continue
            ns = "{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}"
            root = ET.parse(trx).getroot()
            results, messages = {}, {}
            for r in root.iter(f"{ns}UnitTestResult"):
                name = r.get("testName")
                results[name] = r.get("outcome")
                msg = r.find(f".//{ns}Message")
                if msg is not None and msg.text:
                    messages[name] = msg.text
            failed = {n for n, o in results.items() if o != "Passed"}
            total_ok = len(results) == suite.get("total")
            set_ok = failed == expected_failed
            # 期待理由と異なる失敗の検査(signature 突合)
            wrong_reason = [n for n, sig in signatures.items()
                            if n in failed and sig not in messages.get(n, "")]
            detail = ""
            if not set_ok:
                healed = expected_failed - failed
                regressed = failed - expected_failed
                if healed:
                    detail += f" 期待赤が直っている(実験証拠の破壊?): {sorted(healed)}"
                if regressed:
                    detail += f" リグレッション: {sorted(regressed)}"
            if wrong_reason:
                detail += f" 期待理由と異なる失敗(signature 不一致): {sorted(wrong_reason)}"
            check("C9", total_ok and set_ok and not wrong_reason,
                  f"{proj}: {len(results) - len(failed)}/{len(results)} 合格・"
                  f"期待赤 {len(expected_failed)} 件一致={set_ok}・signature 突合 {len(signatures)} 件{detail}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="BomDD リポ全体の自己適合ゲート")
    ap.add_argument("--dotnet", action="store_true",
                    help="loop .NET スイートを期待結果 manifest と突合(C9)")
    a = ap.parse_args()

    print(f"self-conformance: {ROOT}")
    c1_yaml()
    c2_json()
    c3_register()
    c4_scaffold()
    c5_fail_closed()
    c6_gate_mutation()
    c7_readme()
    c8_hygiene()
    if a.dotnet:
        c9_dotnet()

    print()
    if FAILURES:
        print(f"self-conformance FAILED — {len(FAILURES)} 件の不適合")
        return 1
    print("self-conformance passed — 全検査合格")
    return 0


if __name__ == "__main__":
    sys.exit(main())
