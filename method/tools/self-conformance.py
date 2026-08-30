#!/usr/bin/env python3
"""self-conformance — 方法論リポ(BomDD)全体の自己適合ゲート(harness ECO-006)

外部レビュー所見6(2026-07-10)「リポジトリ全体の自己適合ゲートがない — テンプレート構文、
初期化後の動作、ツール異常系、既知の実験結果を一括検証する入口がない」への回答。
所見1〜5 の是正(ECO-001〜005)を恒久回帰として収載する。

検査(fast tier — 既定):
  C1 yaml-parse     : method/ 全 YAML+bomdd/ 実台帳が厳格パース — 構文成功に加え重複キー
                      (沈黙上書き=情報損失)を FAIL・陽性対照を常設(ECO-001/012 恒久回帰)
  C2 json-parse     : method/ 配下の *.json が全数パース
  C3 register       : ハーネス台帳が厳格パースし、verified エントリは diff_audit.head で窓が
                      閉じ、verification が実記録(非空・既知プレースホルダでない)(ECO-012 案3)
  C4 scaffold       : bomdd-init が一時ディレクトリへ scaffold でき、生成物に方法論リポの
                      絶対パスが漏れない(bomdd.lock の origin_path=来歴のみ許容)+
                      lock がパースし kit の files 数が manifest と一致(ECO-004 恒久回帰)+
                      生成物 YAML の厳格パース(ECO-012 — 生成物も保存正本)
  C5 fail-closed    : stage0-survey / impact-retrospective が存在しないリポに exit 2(ECO-002/003)
  C6 gate-mutation  : ui-cad-gate が「理由なし rejected」を落とし(exit≠0)、
                      「根拠+決定者つき rejected」を通す(exit 0)— 対検査(ECO-005 恒久回帰)
  C7 readme-drift   : README の「スキル N 本」表記が bomdd-init.SKILLS の実数と一致
  C8 root-hygiene   : リポ直下にパス破損の化石(名前に ':' を含む等)がない
  C10 schema-drift  : 参照スキーマの派生同期 — 正本(id-grammar/ref-edges)と派生(JSON Schema)
                      の ID 層機械突合+二方言被覆+テンプレ空振り検査・陽性対照常設(ECO-014)
  C11 process-core  : scaffold 上で工程設備(hooks+validator+qualification runner)が稼働する —
                      IQ/OQ 合格+変異(hooksPath 無効化)を IQ-03 が検出(ECO-015。git 必須)
                      C11b= 非既定構成 profile(register/initial/trailers/protected を既定と変更)
                      でも全対照 PASS(ECO-024 — 導出化の全面適用を測る)
  C12 entry-refs    : **自リポ入口**(AGENTS.md)の相対 markdown リンク全数が実在(ECO-025 —
                      製品リポ側は IQ-08 が担うが生成器自身は対象定義の外だった。不在も FAIL)
  C13 link-integrity: method corpus のリンク実在 — 二文脈検査(ECO-026)。(a) リポ文脈=
                      リポ直下 *.md+method/**/*.md(templates/ 除外— 参照文脈が設置先のため)
                      (b) 設置先文脈= scaffold した一時製品リポの全 md(bomdd-kit/ 除く)。
                      対象欠落チャレンジ+壊れリンク陽性対照を毎回実測
  C14 kit-freshness : kit-freshness 治具の対照実測(ECO-026)— 合成 origin+合成 kit で
                      FRESH/STALE/TAMPERED/UNKNOWN/入力不正の全分岐を発動実測し、
                      実 scaffold での最初の正常後続取引(FRESH)を一巡(git 必須)
  C15 deprecated-refs: deprecated 参照の掃討 lint(ECO-027)— `> **deprecated` を宣言正本とし、
                      basename を含む行が同一行に deprecated 語を持たなければ現役誘導として
                      FAIL。証拠台帳(improvements/FINDINGS)は除外・陽性対照を毎回実測
  C16 converge-receipt: converge 未実施の裁定候補 artifact が正典化されるのを阻止する
                      (ECO-033 Phase 1)。対象= cutoff 以降の ECO order+improvements.md 節
                      (A-1)。判定= 構造マーカー 5 種(裁定要求・gate 1・裁定対象・
                      よる自動 required ∪ 明示宣言、ただし
                      **宣言は緩める方向に使えない**(not-required 宣言は hard-positive 実在時に
                      却下=FAIL。B-1 の非対称設計)。境界= cutoff 全数走査(C-1c — staged 差分は
                      CI で計算不能〔shallow clone〕なため意味論から外し判定の正本を全数走査へ)。
                      fixture 5 種を毎回実測(F2 正常系を含む — 無いと「常に FAIL する Gate」と
                      弁別できない)

検査(--dotnet tier — 任意):
  C9 loop-suites    : loops/expected-results.yaml の期待結果 manifest と実測を突合 —
                      expected_failed は「失敗しなければならない」(実験証拠の保存検査)・
                      それ以外は全合格(リグレッション検出)

欠測・実行不能は「問題なし」ではない: 検査対象が見つからない/実行できない場合も FAIL。
exit 0 = 全検査合格 / exit 1 = 不適合あり / exit 2 = ゲート自身が実行不能。
"""
from __future__ import annotations

import argparse
import copy
import json
import os
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


# --- 厳格 YAML ローダー(ECO-012) ----------------------------------------------------
# PyYAML の既定は重複キーを後勝ちで沈黙上書きする — 保存正本の情報損失が「構文 PASS」で
# 素通りした実害が ECO-011(summary の別 ECO への誤帰属・5 日潜伏)。検査は「パースできる」
# でなく「情報が保存される」を張る。
class _DupKeyError(yaml.YAMLError):
    pass


class _StrictLoader(yaml.SafeLoader):
    pass


def _strict_mapping(loader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=True)
        if key in seen:
            raise _DupKeyError(f"重複キー '{key}'(line {key_node.start_mark.line + 1})")
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


_StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _strict_mapping)


def strict_yaml_load(text: str):
    """重複キーを _DupKeyError にする safe_load(情報損失の遮断)"""
    return yaml.load(text, Loader=_StrictLoader)


# ECO-012 案3: verified の verification 欄が取り得ない既知プレースホルダ(部分一致でなく列挙管理)
_KNOWN_PLACEHOLDERS = {"(製造前 — 未実施)", "(製造前)", "(未実施)", "(未検証)"}


# --- C1/C2 テンプレ・スキーマ・実台帳の構文+情報保存 ---------------------------------
def c1_yaml() -> None:
    # 陽性対照(常設): 厳格ローダー自身が重複キーを検出できることを毎回確認してから走査する
    # (検出器が壊れたまま全 PASS するのを遮断 — control-plan「検査の対照3種」)
    try:
        strict_yaml_load("a: 1\na: 2\n")
        check("C1", False, "陽性対照が失敗 — 厳格ローダーが重複キーを検出しない")
        return
    except _DupKeyError:
        pass
    files = (sorted((ROOT / "method").rglob("*.yaml")) + sorted((ROOT / "method").rglob("*.yml"))
             + sorted((ROOT / "bomdd").rglob("*.yaml")))  # ECO-012: 実台帳も保存正本
    bad = []
    for f in files:
        try:
            strict_yaml_load(f.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            bad.append(f"{f.relative_to(ROOT)}: {str(e).splitlines()[0]}")
    check("C1", bool(files) and not bad,
          f"YAML {len(files)} 件厳格パース(重複キー検出・陽性対照込み)"
          + (f" — 失敗: {bad}" if bad else ""))


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
        reg = strict_yaml_load(reg_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        check("C3", False, f"台帳がパース不能/情報損失: {e}")
        return
    problems = []
    for c in reg.get("changes") or []:
        if c.get("status") != "verified":
            continue
        cid = c.get("id", "?")
        # ECO-012 案3: verified の明示的な状態契約 — 窓閉鎖・verification 実記録を一体で検査
        if not (c.get("diff_audit") or {}).get("head"):
            problems.append(f"{cid}: diff 窓が開いている(head 未設定)")
        v = (c.get("verification") or "").strip()
        if not v:
            problems.append(f"{cid}: verification が空")
        elif v in _KNOWN_PLACEHOLDERS:
            problems.append(f"{cid}: verification が製造前プレースホルダのまま")
    check("C3", not problems,
          "台帳厳格パース+verified の状態契約(窓閉鎖・verification 実記録)"
          + (f" — {problems}" if problems else "(全 verified 適合)"))


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
        lock = strict_yaml_load((prod / "bomdd.lock").read_text(encoding="utf-8"))["bomdd_lock"]
        manifest = json.loads((prod / lock["kit"]["manifest"]).read_text(encoding="utf-8"))
        count_ok = lock["kit"]["files"] == len(manifest["files"])
        # ECO-012: 生成物も保存正本 — scaffold の全 YAML を厳格パース(重複キー=情報損失を遮断)
        gen_bad = []
        for f in list(prod.rglob("*.yaml")) + list(prod.rglob("*.yml")):
            try:
                strict_yaml_load(f.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                gen_bad.append(f"{f.relative_to(prod)}: {str(e).splitlines()[0]}")
        # ECO-010: ハーネス中立入口 — AGENTS.md の存在+参照する SKILL.md の全実在
        agents = prod / "AGENTS.md"
        agents_ok, agents_msg = False, "AGENTS.md がない"
        if agents.is_file():
            text = agents.read_text(encoding="utf-8")
            refs = re.findall(r"\.claude/skills/([\w-]+)/SKILL\.md", text)
            missing = [s for s in refs if not (prod / ".claude" / "skills" / s / "SKILL.md").is_file()]
            agents_ok = bool(refs) and not missing
            agents_msg = f"AGENTS.md 参照スキル {len(refs)} 件" + (f" — 実在しない: {missing}" if missing
                         else "" if refs else " — スキル参照ゼロ(ポインタ空)")
        check("C4", not leaks and count_ok and agents_ok and not gen_bad,
              f"scaffold 煙試験(絶対パス漏れ {len(leaks)} 件・lock/manifest 整合 {count_ok}・{agents_msg}・"
              f"生成 YAML 厳格パース{'失敗: ' + str(gen_bad[:3]) if gen_bad else ' 全数'})"
              + (f" — 漏れ: {leaks[:3]}" if leaks else ""))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- C11 process-core 適格性(ECO-015・環境依存の除去は ECO-020) ----------------------
def _c11_env() -> dict:
    """検査は自分の前提を自分で満たす(ECO-020)。

    C11 は bomdd-init の git 経路(init/config/add/初回 commit)を通すため、実行環境に
    git の identity が必要になる。これを ambient な設定へ委ねると、**開発機では緑・CI では赤**
    という環境差が生まれる(実測: C11 導入〔ECO-015〕から 11 コミット・約 2 日・5 ECO を跨いで
    CI が赤のまま潜伏 — ローカル self-conformance の全 PASS だけを見ていたため)。
    identity を検査側の固定値で与え、前提を検査に内在させる。
    """
    env = dict(os.environ)
    env.setdefault("GIT_AUTHOR_NAME", "bomdd-selfconf")
    env.setdefault("GIT_AUTHOR_EMAIL", "selfconf@bomdd.invalid")
    env.setdefault("GIT_COMMITTER_NAME", "bomdd-selfconf")
    env.setdefault("GIT_COMMITTER_EMAIL", "selfconf@bomdd.invalid")
    return env
def c11_process_core() -> None:
    probe = run(["git", "--version"])
    if probe.returncode != 0:
        check("C11", False, "git が実行できない(工程設備の検査対象が実行不能 — 欠測は FAIL)")
        return
    tmp = Path(tempfile.mkdtemp(prefix="bomdd-selfconf-c11-"))
    try:
        p = run([sys.executable, str(ROOT / "method" / "tools" / "bomdd-init.py"),
                 "ProcCoreSmoke", "--dir", str(tmp), "--no-gui", "--no-qualify"],
                env=_c11_env())
        prod = tmp / "ProcCoreSmoke"
        if p.returncode != 0:
            check("C11", False, f"bomdd-init が失敗 (exit {p.returncode}): {p.stderr.strip()[:120]}")
            return
        runner = prod / "bomdd" / "tools" / "process-qualification.py"
        # scaffold の初回 commit が hook 有効のまま成立していること(bomdd-init 経路の実測)
        head_ok = run(["git", "-C", str(prod), "rev-parse", "HEAD"]).returncode == 0
        # ECO-017 REV-11: 2 回決定性を C11 でも回帰固定(--runs 既定 2)+構造化 JSON 判定
        j1 = tmp / "q1.json"
        q = run([sys.executable, str(runner), "--root", str(prod), "--json", str(j1)])
        ok1, det_ok = q.returncode == 0, False
        try:
            r1 = json.loads(j1.read_text(encoding="utf-8"))
            det_ok = r1.get("runs_identical") is True and r1.get("disposition") == "PASS"
        except (OSError, json.JSONDecodeError):
            ok1 = False
        # 変異: hooksPath 無効化 → 構造化結果で IQ-03 自身の pass==false を確認(文字列一致の廃止)
        run(["git", "-C", str(prod), "config", "--unset", "core.hooksPath"])
        j2 = tmp / "q2.json"
        q2 = run([sys.executable, str(runner), "--root", str(prod), "--mode", "iq", "--runs", "1",
                  "--json", str(j2)])
        ok2 = False
        try:
            r2 = json.loads(j2.read_text(encoding="utf-8"))
            iq3 = [r for r in r2.get("iq", []) if r.get("control") == "IQ-03"]
            ok2 = q2.returncode != 0 and bool(iq3) and iq3[0].get("pass") is False
        except (OSError, json.JSONDecodeError):
            pass
        check("C11", head_ok and ok1 and det_ok and ok2,
              f"process-core 適格性(初回 commit hook 有効={head_ok}・IQ/OQ PASS={ok1}・"
              f"2 回決定性={det_ok}・変異〔hooksPath 無効〕IQ-03 pass=false 構造判定={ok2})"
              + ("" if ok1 else f" — {q.stdout.strip().splitlines()[-1:] or q.stderr.strip()[:120]}"))
        c11b_adapted_profile(tmp, runner)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def c11b_adapted_profile(tmp: Path, runner: Path) -> None:
    """C11b(ECO-024 IA-04・裁定 4)— **非既定構成の対照 1 本**。
    差分注入点(register パス・initial 状態名・trailer 名・保護パス)をすべて既定と変えた
    profile で全対照が PASS するか。既定一致構成だけの検査は、adapt された実運用リポで
    初めて誤 FAIL/素通りを起こす(ECO-021 は保護パスのみ導出化し、他の可変点が残った)。"""
    p = run([sys.executable, str(ROOT / "method" / "tools" / "bomdd-init.py"),
             "AdaptSmoke", "--dir", str(tmp), "--no-gui", "--no-qualify"], env=_c11_env())
    prod = tmp / "AdaptSmoke"
    if p.returncode != 0:
        check("C11b", False, f"bomdd-init が失敗 (exit {p.returncode}): {p.stderr.strip()[:120]}")
        return
    prof_path = prod / "bomdd" / "process-profile.yaml"
    try:
        prof = yaml.safe_load(prof_path.read_text(encoding="utf-8"))
        old_reg = prof["register"]
        prof["register"] = "meta/custom-register.yaml"
        prof["initial"] = "queued"
        prof["states"] = ["queued", "applied"]
        prof["open_states"] = ["queued"]
        prof["trailers"] = dict(prof["trailers"], fix="X-Fix", accept="X-Accept")
        prof["protected_paths"] = ["app/"]
        prof_path.write_text(yaml.safe_dump(prof, allow_unicode=True, sort_keys=False),
                             encoding="utf-8", newline="\n")
        (prod / "meta").mkdir(parents=True, exist_ok=True)
        (prod / "meta" / "custom-register.yaml").write_text("changes: []\n",
                                                            encoding="utf-8", newline="\n")
        (prod / old_reg).unlink(missing_ok=True)
        # 入口の参照も adapt に追随させる(IQ-08 は移動後の空ポインタを正しく FAIL にする —
        # ここは「台帳を動かすなら入口も直す」という実運用の手当てを fixture で再現している)
        agents = prod / "AGENTS.md"
        if agents.is_file():
            agents.write_text(agents.read_text(encoding="utf-8").replace(old_reg, prof["register"]),
                              encoding="utf-8", newline="\n")
        (prod / "app").mkdir(parents=True, exist_ok=True)
        (prod / "app" / ".keep").write_text("", encoding="utf-8", newline="\n")
    except (OSError, KeyError, yaml.YAMLError) as e:
        check("C11b", False, f"adapt profile を構成できない: {type(e).__name__}: {e}")
        return
    for args in (["add", "-A"], ["commit", "-q", "--no-verify", "-m", "adapt: non-default profile"]):
        r = run(["git", "-C", str(prod), *args], env=_c11_env())
        if r.returncode != 0:
            check("C11b", False, f"adapt commit が失敗: {r.stderr.strip()[:120]}")
            return
    j = tmp / "q-adapt.json"
    q = run([sys.executable, str(runner), "--root", str(prod), "--json", str(j)])
    ok, det, failed = q.returncode == 0, False, []
    try:
        r = json.loads(j.read_text(encoding="utf-8"))
        det = r.get("runs_identical") is True and r.get("disposition") == "PASS"
        failed = [c.get("control") for c in r.get("iq", []) + r.get("oq", []) if not c.get("pass")]
    except (OSError, json.JSONDecodeError):
        ok = False
    check("C11b", ok and det and not failed,
          f"非既定構成 profile の全対照(register/initial/trailers/protected を既定と変更)— "
          f"PASS={ok}・2 回決定性={det}" + (f"・不合格 {failed}" if failed else ""))


# --- C5 fail-closed 陽性対照(ECO-002/003・由来検査は ECO-008) -----------------------
def c5_fail_closed() -> None:
    ghost = str(ROOT / "no-such-repo-selfconf")
    for cid, tool in [("C5a", "stage0-survey.py"), ("C5b", "impact-retrospective.py")]:
        tool_path = ROOT / "method" / "tools" / tool
        # ECO-008: 対象欠落チャレンジ — tool 自体の消失は「測定不能」でなく検査器の前提破綻。
        # Python の script-not-found も exit 2 を返すため、存在検査なしでは偽 PASS になる。
        if not tool_path.is_file():
            check(cid, False, f"{tool} が存在しない(検査対象の消失 — exit code 検査以前の FAIL)")
            continue
        p = run([sys.executable, str(tool_path), "--repo", ghost])
        # ECO-008: exit 2 の由来を die() の stderr マーカーで確認(Python-not-found 等と区別)
        from_die = "測定不能:" in (p.stderr or "")
        check(cid, p.returncode == 2 and from_die,
              f"{tool} 存在しないリポ → exit {p.returncode}・測定不能マーカー={from_die}(期待 2+マーカー)")


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


# --- C12 自リポ入口の参照実在(ECO-025) ----------------------------------------------
def c12_entry_refs() -> None:
    """本リポ自身の入口(AGENTS.md)の相対 markdown リンク全数が実在するか。

    ECO-023 は製品リポ側の同じ穴を IQ-08 で塞いだが、**生成器自身のリポは対象定義の外**に
    あったため被覆されていなかった(OBS-20260727-12: 適用対象を「製品リポ」と定義した瞬間、
    自リポが対象外になり、穴が対象集合の中でなく**定義の中**に隠れる)。C4(scaffold 煙試験)は
    bomdd-init の生成物を見る検査であり、自リポの入口は生成物ではないため別検査として置く。
    AGENTS.md 不在も FAIL(入口の欠落そのものが本 ECO の症状)。
    """
    entry = ROOT / "AGENTS.md"
    if not entry.is_file():
        check("C12", False, "AGENTS.md がない(自リポの入口不在 — ECO-025 の症状)")
        return
    links = re.findall(r"\]\(([^)]+)\)", entry.read_text(encoding="utf-8"))
    rels = [l.split("#")[0] for l in links
            if not l.startswith(("http://", "https://", "#")) and l.split("#")[0]]
    missing = sorted({l for l in rels if not (ROOT / l).exists()})
    check("C12", not missing,
          f"自リポ入口(AGENTS.md)の相対リンク {len(rels)} 件すべて実在" if not missing
          else f"参照不在 {len(missing)} 件: {missing[:5]}")


# --- C13 リンク実在の二文脈検査(ECO-026) --------------------------------------------
def _md_links_missing(files: list[Path], base: Path,
                      tracked: set[str] | None = None) -> tuple[int, list[str]]:
    """相対 markdown リンクを各ファイルの所在文脈で解決し、(総数, 不在リスト) を返す。

    除外: http(s)/mailto/アンカーのみ/`{{` プレースホルダ(render 前のテンプレ変数)。
    tracked を渡すと存在判定は **git 追跡集合**(合意された内容)に対して行う —
    ambient worktree を判定入力にすると、未追跡の生成物・隣接リポの存在で
    **ローカル PASS / クリーン checkout FAIL** の環境差が生まれる(ECO-026 CI 赤の実測。
    「規則は合意された地点で読む」OBS-20260727-04 の検査版)。base の外へ解決される
    リンク(隣接リポ等)は検証不能につき対象外(総数にも数えない — 宣言済み限界)。
    """
    total, missing = 0, []
    for p in files:
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for m in re.finditer(r"\]\(([^)\s]+)\)", text):
            t = m.group(1)
            if t.startswith(("http://", "https://", "mailto:", "#")) or "{{" in t:
                continue
            target = t.split("#")[0]
            if not target:
                continue
            resolved = (p.parent / target).resolve()
            try:
                rel = resolved.relative_to(base.resolve()).as_posix()
            except ValueError:
                continue  # base 外(隣接リポ等)= 検証不能・対象外(宣言済み限界)
            total += 1
            if tracked is not None:
                ok = rel in tracked or any(x.startswith(rel + "/") for x in tracked)
            else:
                ok = resolved.exists()
            if not ok:
                missing.append(f"{p.relative_to(base).as_posix()}: {t}")
    return total, missing


def c13_link_integrity() -> None:
    """method corpus のリンク実在 — 二文脈検査(ECO-026)。

    境界の裁定(OBS-20260727-05: 値と併せて面ごとの端点と選択理由を記録する):
    (a) リポ文脈: リポ直下 *.md + method/**/*.md。**method/templates/ は全体を除外** —
        テンプレの参照文脈は設置先(製品リポ)であり、リポ文脈で解決すると誤検出になる
        (起票時実測: product-profile 15 件)。除外分の設置形は (b) が全数検証する。
    (b) 設置先文脈: bomdd-init で scaffold した一時製品リポ内の全 .md(bomdd-kit/ を除く)を
        設置先で解決 — IQ-08(入口 AGENTS.md のみ)の全 md への拡張。
    既知限界(宣言+掃射手段の紐づけ): ①bomdd-kit/ 内部は method/ の凍結写しで非規範
    (検査対象にしない)②scaffold が設置しないテンプレ(ui-mock-extraction/ 等)のリンクは
    自動検査外 — 設置経路へ載った時点で (b) が自動被覆する。
    対照: 対象欠落チャレンジ(列挙 0・リンク 0 → FAIL)+壊れリンク陽性対照を毎回実測。
    """
    templates = ROOT / "method" / "templates"
    repo_files = sorted(ROOT.glob("*.md")) + \
        [p for p in sorted((ROOT / "method").rglob("*.md")) if templates not in p.parents]
    # リポ文脈の存在判定は追跡集合(git ls-files)— worktree の未追跡生成物で局所 PASS しない
    ls = run(["git", "-C", str(ROOT), "ls-files"])
    if ls.returncode != 0:
        check("C13", False, "git ls-files が実行できない(追跡集合が取得不能 — 欠測は FAIL)")
        return
    tracked = set(ls.stdout.split())
    total_a, miss_a = _md_links_missing(repo_files, ROOT, tracked=tracked)
    tmp = Path(tempfile.mkdtemp(prefix="bomdd-selfconf-c13-"))
    try:
        # 陽性対照: 壊れリンクを検出できることを毎回実測(検出器の生死判定)
        pos = tmp / "pos.md"
        pos.write_text("[x](no-such-file.md)", encoding="utf-8")
        _, pos_miss = _md_links_missing([pos], tmp)
        pos_ok = len(pos_miss) == 1
        p = run([sys.executable, str(ROOT / "method" / "tools" / "bomdd-init.py"),
                 "LinkCtxSmoke", "--dir", str(tmp), "--no-gui", "--no-git"])
        if p.returncode != 0:
            check("C13", False, f"bomdd-init が失敗 (exit {p.returncode}): {p.stderr.strip()[:120]}")
            return
        prod = tmp / "LinkCtxSmoke"
        inst_files = [f for f in sorted(prod.rglob("*.md")) if "bomdd-kit" not in f.parts]
        total_b, miss_b = _md_links_missing(inst_files, prod)
        ok = (bool(repo_files) and total_a > 0 and not miss_a and pos_ok
              and bool(inst_files) and total_b > 0 and not miss_b)
        check("C13", ok,
              f"リンク実在の二文脈検査(リポ文脈 {len(repo_files)} files/{total_a} links 不在 "
              f"{len(miss_a)}・設置先文脈 {len(inst_files)} files/{total_b} links 不在 "
              f"{len(miss_b)}・陽性対照 {pos_ok})"
              + (f" — リポ文脈: {miss_a[:5]}" if miss_a else "")
              + (f" — 設置先: {miss_b[:5]}" if miss_b else ""))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- C14 kit-freshness 治具の対照実測(ECO-026) ---------------------------------------
def c14_kit_freshness() -> None:
    """kit-freshness の 4 値+入力不正の全分岐を発動実測してから正本とする(ECO-026)。

    control-plan「安全装置の較正は真の故障モードでの発動実測」+「正本化前検査 (d):
    強制規則・ゲートの導入は最初の正常後続取引を First Article に含める」の適用 —
    合成 origin(2 commit)+合成 kit で全分岐を実測し、実 scaffold(bomdd-init)での
    最初の正常後続取引(FRESH)も一巡する。
    """
    if run(["git", "--version"]).returncode != 0:
        check("C14", False, "git が実行できない(工程設備の検査対象が実行不能 — 欠測は FAIL)")
        return
    tool = ROOT / "method" / "tools" / "kit-freshness.py"
    tmp = Path(tempfile.mkdtemp(prefix="bomdd-selfconf-c14-"))
    try:
        env = _c11_env()
        origin = tmp / "origin"
        origin.mkdir()
        run(["git", "-C", str(origin), "init", "-q"], env=env)
        (origin / "a.txt").write_text("v1", encoding="utf-8")
        run(["git", "-C", str(origin), "add", "-A"], env=env)
        run(["git", "-C", str(origin), "commit", "-qm", "c1"], env=env)
        c1 = run(["git", "-C", str(origin), "rev-parse", "HEAD"], env=env).stdout.strip()
        (origin / "a.txt").write_text("v2", encoding="utf-8")
        run(["git", "-C", str(origin), "add", "-A"], env=env)
        run(["git", "-C", str(origin), "commit", "-qm", "c2"], env=env)
        c2 = run(["git", "-C", str(origin), "rev-parse", "HEAD"], env=env).stdout.strip()

        import hashlib as _h
        prod = tmp / "prod"
        kit = prod / "bomdd-kit"
        kit.mkdir(parents=True)
        (kit / "f.md").write_text("kit file", encoding="utf-8")
        manifest = {"files": {"f.md": _h.sha256(b"kit file").hexdigest()}}
        mpath = kit / "kit-manifest.json"
        mpath.write_text(json.dumps(manifest), encoding="utf-8", newline="\n")
        msha = _h.sha256(mpath.read_bytes()).hexdigest()

        def write_lock(commit: str, origin_path: str) -> None:
            (prod / "bomdd.lock").write_text(
                "bomdd_lock:\n  method:\n"
                f"    origin_path: \"{origin_path}\"\n    commit: \"{commit}\"\n"
                "  kit:\n    root: bomdd-kit\n    manifest: bomdd-kit/kit-manifest.json\n"
                f"    manifest_sha256: \"{msha}\"\n", encoding="utf-8", newline="\n")

        def fresh() -> subprocess.CompletedProcess:
            return run([sys.executable, str(tool), "--root", str(prod)])

        results: list[tuple[str, bool]] = []
        write_lock(c2, origin.as_posix())
        p = fresh()
        results.append(("FRESH", p.returncode == 0 and "FRESH" in p.stdout))
        write_lock(c1, origin.as_posix())
        p = fresh()
        results.append(("STALE", p.returncode == 0 and "STALE" in p.stdout
                        and "behind=1" in p.stdout))
        write_lock(c2, (tmp / "nowhere").as_posix())
        p = fresh()
        results.append(("UNKNOWN", p.returncode == 3 and "ORIGIN_MISSING" in p.stdout))
        write_lock(c2, origin.as_posix())
        (kit / "f.md").write_text("hacked", encoding="utf-8")
        p = fresh()
        results.append(("TAMPERED", p.returncode == 1 and "TAMPERED" in p.stdout))
        (kit / "f.md").write_text("kit file", encoding="utf-8")
        (kit / "extra.md").write_text("x", encoding="utf-8")
        p = fresh()
        results.append(("EXTRA", p.returncode == 1 and "extra:extra.md" in p.stdout))
        (kit / "extra.md").unlink()
        (prod / "bomdd.lock").unlink()
        p = fresh()
        results.append(("INPUT", p.returncode == 2 and "LOCK_MISSING" in p.stdout))
        # 最初の正常後続取引: 実 scaffold へ実行して FRESH/STALE(判定成功)を一巡
        pr = run([sys.executable, str(ROOT / "method" / "tools" / "bomdd-init.py"),
                  "FreshSmoke", "--dir", str(tmp), "--no-gui", "--no-git"])
        p = run([sys.executable, str(tool), "--root", str(tmp / "FreshSmoke")])
        results.append(("REAL", pr.returncode == 0 and p.returncode == 0))
        bad = [name for name, ok in results if not ok]
        check("C14", not bad,
              "kit-freshness 対照実測(FRESH/STALE/UNKNOWN/TAMPERED/余剰/入力不正/実 scaffold "
              f"= {len(results) - len(bad)}/{len(results)})" + (f" — 失敗: {bad}" if bad else ""))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- C15 deprecated 参照の掃討 lint(ECO-027) -----------------------------------------
_DEP_MARKER_RE = re.compile(r"^>\s*\*\*deprecated", re.M)


def _dep_naive_refs(files: list[Path], base: Path,
                    deprecated: list[Path]) -> list[str]:
    """deprecated ファイルの basename を含む行のうち、同一行に deprecated 語が無いもの
    (=現役誘導とみなす)を列挙する。宣言ファイル自身は除外。"""
    names = {d.name: d for d in deprecated}
    naive = []
    for p in files:
        if p in names.values():
            continue
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(lines, 1):
            for name in names:
                if name in line and "deprecated" not in line.lower():
                    naive.append(f"{p.relative_to(base).as_posix()}:{i}: {name}")
    return naive


def c15_deprecated_refs() -> None:
    """「正典を差し替えても誘導が旧を指し続ける」の機械掃討(ECO-027・T0-15 昇格裁定)。

    宣言正本= 当該ファイル自身の行 `> **deprecated`(実在標本 method/prompts/
    ui-mock-to-ui-bom.md:3 の既存様式をそのまま規約化 — 実在標本較正・ECO-006 教訓 6)。
    判定= deprecated ファイルの basename を含む行は、同一行に `deprecated` の語を含む場合のみ
    「承知の参照」として許容。含まない行は現役誘導として FAIL。
    境界(値と端点の記録 — OBS-20260727-05): 走査対象= リポ直下 *.md+method/**/*.md。
    **証拠台帳(method/improvements.md・FINDINGS.md)は除外** — 過去状態の記述が本文の
    証拠正本であり、履歴記述を現役誘導と誤検出するため。bomdd/ 台帳(同じく履歴)・
    .claude/skills(ハーネス面 — 必要が実測されてから拡張)も対象外。
    既知限界: basename の行内一致のため同名別ファイルで誤検出しうる(現状 deprecated 1 件・
    衝突なし)。宣言 0 件= 適用対象なしの明示記録つき PASS(任意対象)・corpus 列挙 0= FAIL。
    陽性対照(毎回実測)= 合成 corpus で naive 検出+knowing 許容の両方向。
    """
    ledgers = {ROOT / "method" / "improvements.md", ROOT / "FINDINGS.md"}
    files = [p for p in sorted(ROOT.glob("*.md")) + sorted((ROOT / "method").rglob("*.md"))
             if p not in ledgers]
    if not files:
        check("C15", False, "md corpus の列挙が 0 件(対象欠落 — FAIL)")
        return
    deprecated = [p for p in files
                  if _DEP_MARKER_RE.search(p.read_text(encoding="utf-8", errors="replace"))]
    naive = _dep_naive_refs(files, ROOT, deprecated) if deprecated else []
    # 陽性対照: 合成 corpus で「naive を検出する/knowing を許容する」の両方向を毎回実測
    tmp = Path(tempfile.mkdtemp(prefix="bomdd-selfconf-c15-"))
    try:
        dep = tmp / "old-thing.md"
        dep.write_text("> **deprecated**: 旧方式\n", encoding="utf-8")
        (tmp / "naive.md").write_text("手順は old-thing.md を使う\n", encoding="utf-8")
        (tmp / "knowing.md").write_text("old-thing.md は deprecated(参照回避)\n",
                                        encoding="utf-8")
        syn = _dep_naive_refs([tmp / "naive.md", tmp / "knowing.md"], tmp, [dep])
        pos_ok = syn == ["naive.md:1: old-thing.md"]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ok = pos_ok and not naive
    label = (f"deprecated 宣言 {len(deprecated)} 件" if deprecated
             else "deprecated 宣言 0 件(適用対象なし — 明示記録)")
    check("C15", ok,
          f"deprecated 参照の掃討({label}・naive 参照 {len(naive)} 件・陽性対照 {pos_ok})"
          + (f" — 現役誘導: {naive[:5]}" if naive else ""))


# --- C10 参照スキーマの派生同期(ECO-014) --------------------------------------------
# README §2「id-grammar/ref-edges が正本・JSON Schema は導出」の宣言を機械検査で裏付ける。
# 実害= uiId の domain が正本追加(ref-v0.3(c))から 13 日未同期でも検出されなかった(ECO-013)。
def _c10_id_drifts(fams: list, ids: dict) -> list[str]:
    """ID 層の正本↔派生 機械突合。乖離メッセージのリストを返す(空=同期)"""
    drifts = []
    by_prefix = {f["prefix"]: f for f in fams}
    # family_pattern を持つ家族は pattern の文字列一致
    for prefix, key in (("ui-id", "uiId"), ("S", "oracleCaseId"), ("M0", "migrationCaseId")):
        gp = (by_prefix.get(prefix) or {}).get("family_pattern")
        sp = (ids.get(key) or {}).get("pattern")
        if gp != sp:
            drifts.append(f"{key}: 正本 family_pattern と派生 pattern が不一致")
    # tmpUiPartNo: TMP-UI-* 接頭辞集合の一致
    gset = {p.replace("TMP-UI-", "") for p in by_prefix if p.startswith("TMP-UI-")}
    m = re.search(r"TMP-UI-\((.*?)\)", (ids.get("tmpUiPartNo") or {}).get("pattern") or "")
    if not m or gset != set(m.group(1).split("|")):
        drifts.append("tmpUiPartNo: TMP-UI 接頭辞集合が不一致")
    # anyKnownId: 単純 prefix 家族(family_pattern なし)の全被覆
    simple = {p for p, f in by_prefix.items() if "family_pattern" not in f and p != "ui-id"}
    m = re.search(r"\^\((.*?)\)", (ids.get("anyKnownId") or {}).get("pattern") or "")
    aset = set(m.group(1).split("|")) if m else set()
    missing = {p for p in simple
               if p not in aset and not (p.startswith("TMP-UI") and "TMP-UI" in aset)}
    if missing:
        drifts.append(f"anyKnownId: 未被覆 prefix {sorted(missing)}")
    # 単純 prefix の個別 def 被覆(^P- または alternation 内)
    pats = [v.get("pattern", "") for v in ids.values()]
    unc = [p for p in sorted(simple) if not p.startswith("TMP-UI")
           and not any(f"^{p}-" in pat or f"({p}|" in pat or f"|{p}|" in pat or f"|{p})" in pat
                       for pat in pats)]
    if unc:
        drifts.append(f"個別 def 未被覆: {unc}")
    return drifts


def _c10_selector_roots(edges: dict, file_key: str) -> set:
    """ref-edges の指定 file 節から、セレクタ起点キー(alternation 展開済み)を集める"""
    art = next((a for a in edges.get("artifacts") or [] if a.get("file") == file_key), {})
    roots = set()
    for section in ("defines", "refs"):
        for e in art.get(section) or []:
            head = (e.get("selector") or "").split("[")[0].split(".")[0]
            if head.startswith("("):
                roots |= set(head.strip("()").split("|"))
            elif head and head != "*":
                roots.add(head)
    return roots


def _c10_structural_drifts(edges: dict, schema: dict, tmpl_dir: Path) -> list[str]:
    """構造層の三者突合: テンプレ実在キー ↔ ref-edges セレクタ起点 ↔ Schema properties(二方言被覆)"""
    drifts = []
    ir_roots = _c10_selector_roots(edges, "bomdd/ui/**/ui-ir.json")
    tm_roots = _c10_selector_roots(edges, "bomdd/ui/**/ui-trace-map.json")
    defs = schema.get("$defs") or {}
    ir_props = set((defs.get("uiIrFile") or {}).get("properties") or {})
    tm_props = set((defs.get("uiTraceMapFile") or {}).get("properties") or {})
    # 両方言の被覆ピン(ref-v0.9 回帰ガード — 片方言の「掃除」で検査が再沈黙するのを遮断)
    for k in ("components", "occurrences", "componentCandidates", "componentOccurrences"):
        if k not in ir_roots:
            drifts.append(f"ref-edges ui-ir セレクタ起点に {k} がない(方言被覆の破れ)")
        if k not in ir_props:
            drifts.append(f"Schema uiIrFile に {k} がない(方言被覆の破れ)")
    for k in ("entries", "mappings"):
        if k not in tm_roots:
            drifts.append(f"ref-edges trace-map セレクタ起点に {k} がない(方言被覆の破れ)")
        if k not in tm_props:
            drifts.append(f"Schema uiTraceMapFile に {k} がない(方言被覆の破れ)")
    # テンプレ実在キーの空振り検査(テンプレが持つ宣言対象キーはセレクタに被覆される)
    ir_t = json.loads((tmpl_dir / "ui-ir.json").read_text(encoding="utf-8"))
    missed = [k for k in ir_t if k in ir_props and k not in ir_roots]
    if missed:
        drifts.append(f"ui-ir テンプレのキーがセレクタ空振り: {missed}")
    tm_t = json.loads((tmpl_dir / "ui-trace-map.json").read_text(encoding="utf-8"))
    missed = [k for k in ("entries", "mappings") if k in tm_t and k not in tm_roots]
    if missed:
        drifts.append(f"ui-trace-map テンプレのキーがセレクタ空振り: {missed}")
    return drifts


def c10_schema_drift() -> None:
    draft = ROOT / "method" / "schemas" / "draft"
    tmpl = ROOT / "method" / "templates" / "ui-mock-extraction"
    try:
        fams = strict_yaml_load((draft / "id-grammar.draft.yaml").read_text(encoding="utf-8"))["families"]
        edges = strict_yaml_load((draft / "ref-edges.draft.yaml").read_text(encoding="utf-8"))
        schema = json.loads((draft / "bomdd-ref.draft.schema.json").read_text(encoding="utf-8"))
    except (OSError, KeyError, TypeError, yaml.YAMLError, json.JSONDecodeError) as e:
        check("C10", False, f"正本/派生の読込不能(欠測は「問題なし」ではない): {e}")
        return
    ids = (schema.get("$defs") or {}).get("id") or {}
    # 陽性対照(常設・環境非依存): 検出器自身が乖離に反応することを毎回確認してから突合する
    mut_ids = {k: dict(v) for k, v in ids.items()}
    mut_ids["uiId"] = {"pattern": (ids.get("uiId") or {}).get("pattern", "").replace("|domain", "")}
    mut_edges = copy.deepcopy(edges)
    for a in mut_edges.get("artifacts") or []:
        if a.get("file") == "bomdd/ui/**/ui-trace-map.json":
            a["refs"] = [e for e in a.get("refs") or []
                         if not (e.get("selector") or "").startswith("mappings")]
    if not _c10_id_drifts(fams, mut_ids) or not _c10_structural_drifts(mut_edges, schema, tmpl):
        check("C10", False, "陽性対照が失敗 — 乖離検出器(ID 層/構造層)が反応しない")
        return
    bad = _c10_id_drifts(fams, ids) + _c10_structural_drifts(edges, schema, tmpl)
    check("C10", not bad,
          "参照スキーマの派生同期(ID 層突合+二方言被覆+テンプレ空振り・陽性対照込み)"
          + (f" — {bad}" if bad else ""))


# --- C9 loop スイート vs 期待結果 manifest(--dotnet) --------------------------------
def c9_dotnet() -> None:
    manifest_path = ROOT / "loops" / "expected-results.yaml"
    if not manifest_path.exists():
        check("C9", False, f"期待結果 manifest がない: {manifest_path}")
        return
    doc = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    suites = (doc or {}).get("suites") or []  # 空ファイル(doc=None)もクラッシュでなく下の FAIL へ
    # ECO-008: 空/欠落 suites の vacuous pass 遮断 — C9 は対象必須の検査(control-plan「検査の対照3種」)
    if not suites:
        check("C9", False, f"manifest に suites がない/空: {manifest_path}(vacuous pass を遮断)")
        return
    for suite in suites:
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


# --- C16 converge receipt ゲート(ECO-033 Phase 1) -------------------------------------
# 目的: **converge 未実施の対象 artifact が正典化されるのを阻止し、非起動を観測可能にする**。
# 「人間への未収束提示を防ぐ」ことは目的ではない(それは Phase 2 = presentation Gate)。
#
# 検出力の限界(宣言 — 未了項目リストではなく「実施した検査が測っていない次元」):
#   (1) receipt の**構造的存在**しか測らない。「本当に敵対自問したか」「実測で裏取りしたか」は
#       測っていない。目的は converge 工程が**完全に素通りする故障**の検出に限定する。
#   (2) hard-positive は高精度・低再現で設計してある。マーカーを一切使わない裁定候補は自動
#       required にならない — その被覆は書き手の `converge: required` 宣言に依存する
#       (残余の fail-open)。
#   (3) artifact に落ちない提示(チャットのみで終わる裁定)は原理的に被覆外(Phase 2 の対象)。
CONVERGE_CUTOFF = "2026-08-30"   # ECO-033 gate 1 裁定(C-1c)。これ以前の節・order は対象外

# 明示宣言(HTML コメント — 描画に出ず機械可読。前例= worklist-legacy-audit-cutoff)
CONVERGE_DECL_RE = re.compile(r"<!--\s*converge:\s*(required|not-required)\s*-->")

# hard-positive= 「人間へ未解決の選択を出している」ことの高精度マーカー
# 語彙は**実リポの実測**で決めた(製造時 R5 probe — ECO-033 §8)。`残ゲート` だけでは
# `gate 1`(本リポで 18/32 order が使う確立した裁定要求マーカー)を持つ 14 件を取り逃がした
# = 弁別力はあるが被覆が無い状態(playbook §4.4)。
CONVERGE_HARD_POSITIVES = (
    ("adjudication-request", re.compile(r"裁定を(お願い|求め)")),
    ("adjudication-gate",    re.compile(r"gate\s*\u2460")),
    ("adjudication-target",  re.compile(r"裁定対象")),
    ("open-gate",            re.compile(r"残ゲート")),
    ("recommended-option",   re.compile(r"[(\uff08]推奨[)\uff09]|推奨[:\uff1a]")),
)
# 選択肢の列挙は hard-positive から**外した**(製造時 R5 probe の実測 — ECO-033 §8)。
# 素の `[A-Z]-\d+` は ID の部分文字列(ECO-034 -> O-034 / RSC-CP-CLOSURE-001 -> E-001)を
# 拾い、実リポで 36 ラベル中 29 件が誤検出だった(部分文字列ゲートで意味を測る欠陥 —
# ViewTube NF-10 R9 と同型。playbook §4.4「検査文はコードが測る以上を主張しない」)。
# 加えて候補ラベルは「提案」と「完了裁定の記録」の双方に現れ、両者を弁別できない —
# 本ゲートの対象は**未解決の選択を人間へ出している** artifact であり、過去の裁定の記録では
# ない。再現力の低下は書き手の `converge: required` 宣言で補う(下記 限界宣言 (2))。

# receipt= 現行契約の 3 項(周回数と各周の新規指摘件数 / 検証した主張と実測結果 / 未収束事項)
CONVERGE_RECEIPT_RE = re.compile(r"(収束\s*receipt|/?converge\s*receipt)", re.I)
CONVERGE_ROUNDS_RE = re.compile(r"周回|round\s*\d")
CONVERGE_UNRESOLVED_RE = re.compile(r"未収束")


def converge_classify(text: str) -> dict:
    """1 artifact を分類する。返り値= required / reasons / declared / conflict / receipt。"""
    reasons = []
    for name, rx in CONVERGE_HARD_POSITIVES:
        if rx.search(text):
            reasons.append(name)
    dm = CONVERGE_DECL_RE.search(text)
    declared = dm.group(1) if dm else None

    # B-1 非対称設計: required への引き上げは常に有効 / not-required への引き下げは
    # hard-positive が 1 つでも実在するなら却下する(宣言で検査を弱められない)
    conflict = bool(declared == "not-required" and reasons)
    required = bool(reasons) or declared == "required"

    receipt = bool(CONVERGE_RECEIPT_RE.search(text)
                   and CONVERGE_ROUNDS_RE.search(text)
                   and CONVERGE_UNRESOLVED_RE.search(text))
    return {"required": required, "reasons": reasons, "declared": declared,
            "conflict": conflict, "receipt": receipt}


def converge_verdict(text: str) -> tuple[bool, str]:
    """(ok, 理由)。conflict は receipt の有無によらず FAIL(宣言による引き下げの却下)。"""
    c = converge_classify(text)
    if c["conflict"]:
        return False, f"not-required 宣言だが hard-positive 実在: {','.join(c['reasons'])}"
    if c["required"] and not c["receipt"]:
        why = ",".join(c["reasons"]) or "declared:required"
        return False, f"converge-required({why})だが収束 receipt がない"
    return True, "ok"


_CONVERGE_FIXTURES = (
    # (id, 期待 ok, 説明, 本文)
    ("F1", False, "required + receipt なし",
     "## 残ゲート\n人間は候補 A-1 か候補 A-2 を指定する。\n"),
    ("F2", True, "required + receipt あり(正常系)",
     "## 残ゲート\n候補 A-1 / 候補 A-2 から選ぶ。\n"
     "## /converge receipt\n- 周回: round 1 = 2 件 / round 2 = 0 件\n- 未収束事項: なし\n"),
    ("F3", True, "not-required + receipt なし",
     "## 記録\n台帳の status を filed から applied へ遷移させた。差分は 1 行。\n"),
    ("F4", False, "mixed-task 陽性(事実照会で始まり裁定候補を生成)",
     "## 出典の確認\n3 例の出典を読み、内容を突き合わせた。\n"
     "## 判定\n案 A(推奨)/ 案 B / 案 C のいずれかで裁定をお願いします。\n"),
    ("F5", False, "hard-positive 実在 かつ not-required 宣言",
     "<!-- converge: not-required -->\n## 残ゲート\n候補 B-1(推奨)/ 候補 B-2。\n"),
)


def c16_converge_receipt() -> None:
    # (1) 較正 — fixture 5 種を毎回実測(予防ゲートの陽性対照。OBS-20260828-05)
    fx_bad = []
    for fid, want_ok, desc, body in _CONVERGE_FIXTURES:
        got_ok, why = converge_verdict(body)
        if got_ok != want_ok:
            fx_bad.append(f"{fid}({desc}) 期待={'PASS' if want_ok else 'FAIL'}"
                          f" 実測={'PASS' if got_ok else 'FAIL'} [{why}]")
    if fx_bad:
        check("C16", False, "fixture 較正が不成立(計器を先に疑う): " + " / ".join(fx_bad))
        return

    # (2) 対象集合 — A-1 x C-1c(cutoff 以降の全数走査。staged は使わない)
    reg = ROOT / "bomdd" / "60-change-register.yaml"
    if not reg.is_file():
        check("C16", False, "台帳が見つからない(対象集合が決定不能 — 欠測は FAIL)")
        return
    try:
        data = strict_yaml_load(reg.read_text(encoding="utf-8"))
    except Exception as e:                                     # noqa: BLE001
        check("C16", False, f"台帳がパースできない(対象集合が決定不能): {e}")
        return

    targets = []
    for ent in (data or {}).get("changes", []) or []:
        if str(ent.get("date", "")) < CONVERGE_CUTOFF:
            continue
        ref = ent.get("order_ref")
        if not ref:
            check("C16", False,
                  f"{ent.get('id')}: cutoff 以降だが order_ref がない(検査対象が特定不能)")
            return
        po = ROOT / ref
        if not po.is_file():
            check("C16", False, f"{ent.get('id')}: order_ref の実体がない({ref} — 欠測は FAIL)")
            return
        targets.append((str(ent.get("id")), po))

    imp = ROOT / "method" / "improvements.md"
    if not imp.is_file():
        check("C16", False, "method/improvements.md が見つからない(欠測は FAIL)")
        return
    sec_id, sec_buf, sections = None, [], []
    for line in imp.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+(\d{4}-\d{2}-\d{2})\s+(.*)$", line)
        if m:
            if sec_id:
                sections.append((sec_id, "\n".join(sec_buf)))
            sec_id, sec_buf = f"improvements.md #{m.group(1)} {m.group(2)[:36]}", []
            if m.group(1) < CONVERGE_CUTOFF:
                sec_id = None
            continue
        if sec_id is not None:
            sec_buf.append(line)
    if sec_id:
        sections.append((sec_id, "\n".join(sec_buf)))

    problems = []
    for name, po in targets:
        ok, why = converge_verdict(po.read_text(encoding="utf-8"))
        if not ok:
            problems.append(f"{name}: {why}")
    for name, body in sections:
        ok, why = converge_verdict(body)
        if not ok:
            problems.append(f"{name}: {why}")

    n = len(targets) + len(sections)
    check("C16", not problems,
          f"converge receipt ゲート(cutoff {CONVERGE_CUTOFF} 以降 {n} 件"
          f"・fixture 5/5 較正成立)"
          + (" — " + " / ".join(problems) if problems else ""))


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
    c10_schema_drift()
    c11_process_core()
    c12_entry_refs()
    c13_link_integrity()
    c14_kit_freshness()
    c15_deprecated_refs()
    c16_converge_receipt()
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
