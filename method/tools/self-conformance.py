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
                      弁別できない)。ECO-034= `not-required` は**根拠つき**
                      (reason+decided-by)なら受理し、根拠なしは却下。有効な免除の
                      件数と宣言者を判定行へ出す(沈黙する免除を作らない)
  C17 calibrate-receipt: calibrate 未実施(trigger ①)の ECO の正典化を阻止(ECO-043)。
                      アンカー= register の verified 昇格(受入節の執筆でなく状態遷移)。
                      適用= ECO-041 以降(A-1)。verified エントリの order に較正 receipt
                      または根拠つき免除(reason+decided-by・フェンス内無効・件数と宣言者を
                      表示)を要求。限界= receipt の構造的存在のみ / trigger ②③④ は被覆外
                      (① gate が最後の防波堤)/ 天然対照は shallow CI で実行不能につき
                      常設化しない(受入時ローカル実測)
  C18 pre-push-witness: 観測前 push の機械遮断(ECO-046)— 全検査 PASS 時に検査対象 tree の
                      witness を .git 配下へ記録し、bomdd/hooks/pre-push が push 対象 tree と
                      突合。C18 は設置検収(hooksPath+hook 実在)。CI は push しない環境に
                      つき NA 宣言。限界= うっかり型の遮断まで(意図的回避は信頼境界外・
                      最終層は CI)

検査(--dotnet tier — 任意):
  C9 loop-suites    : loops/expected-results.yaml の期待結果 manifest と実測を突合 —
                      expected_failed は「失敗しなければならない」(実験証拠の保存検査)・
                      それ以外は全合格(リグレッション検出)。ECO-039: failure identity
                      (kind/expected/actual)の構造化突合を主判定に(substring は補助・
                      parse 不能は FAIL で fallback しない)+母集団の双方向突合
                      (Test SDK 参照 csproj ⇔ manifest)+陽性対照 5 腕を毎回実測。
                      限界宣言は c9 コード先頭(Exe harness 母集団外・意味論同一性の
                      非証明・SDK/環境差の再現性未測定)

欠測・実行不能は「問題なし」ではない: 検査対象が見つからない/実行できない場合も FAIL。
exit 0 = 全検査合格 / exit 1 = 不適合あり / exit 2 = ゲート自身が実行不能。

環境前提の宣言(ECO-040 較正掃引 ③ の還元):
  - 検査は自分の前提を自分で満たす(git identity は内在化 — ECO-020・_git_env)。
  - CI の checkout は shallow(depth 1)であり、履歴・ステージングに依存する検査は
    ここには置けない(実測: ECO-033 C-1→C-1c)。履歴依存の検査を追加する場合は
    fetch-depth の裁定を先に行うこと。
  - ローカルと CI の Python/PyYAML/SDK 版の一致は前提としない — 現在両環境緑の観測は
    あるが、版間の判定同値性は**未較正**(ECO-040 B1・修理しない裁定 4)。
  - 環境個体(python/PyYAML/os/runner/dotnet-sdk)は [env] 行へ刻印する — 目的は
    ドリフトの防止でなく観測可能化(pin はしない)。沈黙的ドリフトの非発生は unknown
    (理由コード= 観測手段なし。刻印により事後突合のみ可能)。
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
    # ECO-045: 辞書なしは「昇格判定保留」へ挙動変更されたため空辞書を明示 — C6 の測定目的
    # (rejected の根拠検査)を保留ノイズから分離する(検査意図の保存)
    "36-ui-dictionary.yaml": "actions: {}\n",
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
# ECO-039: signature(substring)の弁別力欠陥の是正 — failure identity の構造化突合(a-3)+
# 母集団の双方向突合(b-2)+検出力の限界宣言(ECO-033 様式の遡及)。
#
# 検出力の限界(宣言 — 実施した検査が測っていない次元):
#   (1) Exe 型 acceptance harness(loop-02.5 / loop-05 / equip-02)は母集団外 — loops/ は
#       不可逆観測データであり実行環境依存(ffmpeg・API 起動)の意図的境界。
#   (2) failure identity は trx Message 表層の構造化(kind+Expected/Actual)であり、失敗理由の
#       意味論的同一性の完全な証明ではない(同 kind・同値で意味の異なる失敗は弁別外)。
#   (3) SDK/環境差の再現性(別環境・別実行主体での判定安定性)は測っていない。SDK 個体は
#       結果に刻印されない(環境ドリフトは identity 不一致= FAIL 側に倒れることのみ保証)。

def _c9_parse_failure(msg: str):
    """trx Message から failure identity(kind/expected/actual)を構造化する。
    識別できない形式は None — 呼び出し側で FAIL(旧 substring への silent fallback はしない)。"""
    lines = [ln.strip() for ln in (msg or "").splitlines() if ln.strip()]
    if not lines:
        return None
    ident = {"kind": lines[0], "expected": None, "actual": None}
    for ln in lines[1:]:
        if ln.startswith("Expected:"):
            ident["expected"] = ln[len("Expected:"):].strip()
        elif ln.startswith("Actual:"):
            ident["actual"] = ln[len("Actual:"):].strip()
        elif ln.startswith("Not found:"):
            ident["expected"] = ln[len("Not found:"):].strip().strip('"')
    if ident["expected"] is None:  # kind だけでは identity にならない(曖昧形式は不成立)
        return None
    return ident


def _c9_identity_match(want: dict, got) -> tuple[bool, str]:
    """manifest 宣言(want)と実測(got)の identity 突合。want の actual: null は
    kind 固有の不在の明示宣言(Assert.Contains 型 — Message に Actual が存在しない)。"""
    if got is None:
        return False, "識別不能な失敗形式(構造化 parse 不能 — substring へ fallback しない)"
    for k in ("kind", "expected", "actual"):
        wv = want.get(k)
        if wv is None:
            continue
        if str(wv) != str(got.get(k) or ""):
            return False, f"{k} 不一致(期待 {wv!r} / 実測 {got.get(k)!r})"
    return True, ""


def _c9_selftest() -> list[str]:
    """計器の陽性対照(合成・毎回実測)。known-bad= 旧 substring なら一致するが
    identity が異なる別理由失敗(ECO-039 gate 裁定 2)。不成立なら本走査を行わない。"""
    bad = []
    want_eq = {"kind": "Assert.Equal() Failure: Values differ", "expected": "1", "actual": "0"}
    m_true = "Assert.Equal() Failure: Values differ\nExpected: 1\nActual:   0"
    m_other = "Assert.Equal() Failure: Values differ\nExpected: 1\nActual:   3"
    m_junk = "System.InvalidOperationException: boom"
    ok, _ = _c9_identity_match(want_eq, _c9_parse_failure(m_true))
    if not ok:
        bad.append("正腕: 真の期待赤を受理できない")
    if "Expected: 1" not in m_other:
        bad.append("known-bad の前提不成立(旧 substring が一致する合成になっていない)")
    ok, _ = _c9_identity_match(want_eq, _c9_parse_failure(m_other))
    if ok:
        bad.append("known-bad: 別理由失敗(Actual 相違)を受理 — 旧 substring と弁別できていない")
    ok, _ = _c9_identity_match(want_eq, _c9_parse_failure(m_junk))
    if ok:
        bad.append("parse 不能形式を受理した(silent fallback)")
    want_ct = {"kind": "Assert.Contains() Failure: Sub-string not found",
               "expected": "[cv]null[vout]", "actual": None}
    m_ct = 'Assert.Contains() Failure: Sub-string not found\nString:    "xx"\nNot found: "[cv]null[vout]"'
    ok, _ = _c9_identity_match(want_ct, _c9_parse_failure(m_ct))
    if not ok:
        bad.append("正腕: Contains 型の期待赤を受理できない")
    # ECO-054: 空結果 guard の腕(型④)— ラベルの根拠= 独立検査官 S1/S3 の実測(0/0 合格の PASS)
    ok_e, _, _ = _c9_suite_verdict({"project": "x", "total": 0, "expected_failed": []}, {}, {})
    if ok_e:
        bad.append("known-bad: total 0+空結果を PASS にした(空結果の合格化)")
    ok_e, _, _ = _c9_suite_verdict({"project": "x", "total": 2, "expected_failed": []}, {}, {})
    if ok_e:
        bad.append("known-bad: total 2 だが結果 0 件を PASS にした(結果欠測の合格化)")
    ok_g, _, _ = _c9_suite_verdict({"project": "x", "total": 2, "expected_failed": []},
                                   {"A": "Passed", "B": "Passed"}, {})
    if not ok_g:
        bad.append("正腕: 正常 suite(2/2 合格)を受理できない")
    return bad


def _c9_suite_verdict(suite: dict, results: dict, messages: dict):
    """1 suite の判定(ECO-054 で純関数化 — 空結果の guard を持ち、selftest で腕を立てる)。
    返り値= (ok, 要約, detail)。**空結果(results 0 件)または total 0 は FAIL**(型④: 測定不能は
    合格ではない — 独立検査官 S1/S3 が 0/0 合格の PASS を実測)。"""
    expected_failed, signatures, identities = set(), {}, {}
    for e in suite.get("expected_failed") or []:
        if isinstance(e, dict):
            expected_failed.add(e["test"])
            if e.get("signature"):
                signatures[e["test"]] = e["signature"]
            if e.get("identity"):
                identities[e["test"]] = e["identity"]
        else:
            expected_failed.add(e)
    total = suite.get("total")
    if not results or not total:
        return False, f"結果 {len(results)} 件・total {total!r}", " 空結果は合格ではない(測定不能の合格化= 型④・ECO-054)"
    failed = {n for n, o in results.items() if o != "Passed"}
    total_ok = len(results) == total
    set_ok = failed == expected_failed
    wrong_reason = []
    for n, want in identities.items():
        if n in failed:
            ok_id, why = _c9_identity_match(want, _c9_parse_failure(messages.get(n, "")))
            if not ok_id:
                wrong_reason.append(f"{n}: {why}")
    wrong_reason += [f"{n}: signature 不一致" for n, sig in signatures.items()
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
        detail += f" 期待理由と異なる失敗: {sorted(wrong_reason)}"
    summary = (f"{len(results) - len(failed)}/{len(results)} 合格・"
               f"期待赤 {len(expected_failed)} 件一致={set_ok}・"
               f"identity 突合 {len(identities)} 件・signature 補助 {len(signatures)} 件")
    return (total_ok and set_ok and not wrong_reason), summary, detail


def _c9_population() -> set[str]:
    """loops/ 配下の dotnet test 対象(Test SDK/xunit 参照 csproj)の機械列挙(ECO-039 b-2)。
    Exe 型 console harness は参照述語により自然に母集団外(限界宣言 (1))。"""
    found = set()
    for csp in sorted((ROOT / "loops").rglob("*.csproj")):
        text = csp.read_text(encoding="utf-8", errors="replace")
        if "Microsoft.NET.Test.Sdk" in text or "xunit" in text.lower():
            found.add(csp.parent.relative_to(ROOT).as_posix())
    return found


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
    # ECO-039: 計器較正(陽性対照)が不成立なら本走査を行わない — 計器を先に疑う
    st = _c9_selftest()
    if st:
        check("C9", False, f"計器較正不成立(陽性対照): {st}")
        return
    check("C9", True, "計器較正(陽性対照 8 腕: 正腕 3・known-bad〔substring 一致×identity 相違・空結果×2〕・parse 不能・前提検査)")
    # ECO-039 b-2: 母集団の双方向突合 — 未記載 project と不存在/対象外化 entry の双方を FAIL
    found = _c9_population()
    declared = {s["project"] for s in suites}
    unlisted = sorted(found - declared)
    ghost = sorted(declared - found)
    pop_ok = not unlisted and not ghost
    pop_detail = (f" manifest 未記載の test project: {unlisted}" if unlisted else "") + \
                 (f" 不存在/対象外化した manifest entry: {ghost}" if ghost else "")
    check("C9", pop_ok, f"母集団突合(Test SDK/xunit 参照 csproj {len(found)} 件 ⇔ manifest {len(declared)} 件・双方向){pop_detail}")
    for suite in suites:
        proj = suite["project"]
        # 文字列(旧形)/ mapping+signature(ECO-007)/ +identity(構造化 — ECO-039)の三形は
        # _c9_suite_verdict が受ける(ECO-054 で純関数化)
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
            ok_s, summary, detail = _c9_suite_verdict(suite, results, messages)
            check("C9", ok_s, f"{proj}: {summary}{detail}")
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
#   (4) ECO-053: receipt 検出は C17 と**共通関数**(fence 除去〔backtick / tilde・未閉鎖は EOF
#       まで〕→ 見出し → 本体)。**ECO-053 以降の order** は本体ラベル 5 つ(判定〔収束|未収束〕・
#       起動経路・round/周回・未収束事項・DoD ✔/✘)の存在を要求し、**遺産**(ECO-033〜052 の
#       order と improvements.md の節)は fence 除去後のトークン共起で測る(歴史は書き換えない)。
#       **ラベルの存在≠敵対自問の実施**(限界 (1) は維持)。契機= converge 評価(2026-09-02)で
#       ECO-049 前の C17 と同型の use/mention 穴 6 変種+未閉鎖 fence+インデント免除+
#       「round 軌跡」様式の偽陽性を実測 — C17(ECO-051)の修理を親へ還流。ラベル検索は
#       **見出し行を含む**(ECO-036 様式は「起動経路」を見出しに書く — 受入で本 order 自身が
#       遮断された偽陽性の是正)。否定見出しに全ラベルを揃えた病的 receipt は構造的には receipt で
#       あり通過する — 意味は測らない(C17 限界 (5) と同じ)。
#   (5) hard-positive(裁定語)は**フェンス内でも読む**(意図された非対称 — 過剰検出は出口が
#       あるので安全側・過剰免除は fail-open)。本 ECO はこの非対称を変更していない。
CONVERGE_CUTOFF = "2026-08-30"   # ECO-033 gate 1 裁定(C-1c)。これ以前の節・order は対象外

# 明示宣言(HTML コメント — 描画に出ず機械可読。前例= worklist-legacy-audit-cutoff)
# ECO-034: `not-required` は**根拠つきなら受理**する。根拠= reason と decided-by の 2 点で、
# 片方でも空なら却下(FAIL)。前例= ui-cad-gate GU4(ECO-005)「rejected は却下根拠と決定者を
# 必須にする — 来歴なしの黙殺を通さない」。B-1 の非対称性は「宣言で緩められない」から
# 「**根拠なしには緩められない**」へ精密化される(`required` への引き上げは無条件で有効)。
# ECO-053: 宣言は**行頭**でのみ有効(インデントされたコード例・引用内の宣言を実宣言と数えない —
# C17 F11 と同型の実測)。
CONVERGE_DECL_RE = re.compile(
    r"^<!--\s*converge:\s*(required|not-required)"
    r"(?:[\s;|]+reason:\s*(.*?))?"
    r"(?:[\s;|]+decided-by:\s*(.*?))?\s*-->", re.S | re.M)

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

# receipt= 現行契約(ECO-036 様式): 判定 / 起動経路 / 周回と各周の新規指摘件数 / 検証した主張 /
# 未収束事項。ECO-053 で「見出し+本体ラベル」検出へ(共通関数 — C17 と共用)。
CONVERGE_RECEIPT_RE = re.compile(r"(収束\s*receipt|/?converge\s*receipt)", re.I)
CONVERGE_RECEIPT_HEAD_RE = re.compile(
    r"^[ \t]{0,3}(#{2,6})[ \t]+([^\n]*?(?:収束\s*receipt|/?converge\s*receipt)\b[^\n]*)$", re.I | re.M)
CONVERGE_ROUNDS_RE = re.compile(r"周回|round\s*(\d|軌跡)")   # ECO-053: 「round 軌跡」様式を受理
CONVERGE_UNRESOLVED_RE = re.compile(r"未収束")
C16_BODY_MIN = 53   # ECO-053 以降の order は本体ラベル 5 つを要求(遺産はトークン共起)
_C16_LABELS = (
    ("判定(収束|未収束)", re.compile(r"判定[^\n]{0,12}(収束|未収束)")),
    ("起動経路", re.compile(r"起動経路")),
    ("round/周回", CONVERGE_ROUNDS_RE),
    ("未収束事項", CONVERGE_UNRESOLVED_RE),
    ("DoD ✔/✘", re.compile(r"DoD[\s\S]{0,400}?[✔✘]")),
)


# ECO-053: fence 除去と receipt 本体抽出の**共通関数**(C16 / C17 が共用 — 正本を 1 つにする)。
# backtick と tilde の両方・未閉鎖 fence は EOF まで除去(C17 ECO-051 の正規表現を昇格)。
_FENCE_ALL_RE = re.compile(r"^[ \t]{0,3}(```|~~~)[^\n]*\n.*?(?:^[ \t]{0,3}\1[ \t]*$|\Z)", re.S | re.M)


def _strip_fences_all(text: str) -> str:
    return _FENCE_ALL_RE.sub("", text)


def _receipt_bodies(unfenced: str, heading_re, include_heading: bool = False) -> list:
    """receipt 見出しの直後から同レベル以上の次見出しまでを本体として返す(該当見出しごと)。
    include_heading=True で見出し行の文言を本体に含める(ECO-036 様式は「起動経路」を見出しに
    書く — ECO-053 受入で本 order 自身が遮断された偽陽性の是正。見出し行は receipt の一部)。"""
    out = []
    for m in heading_re.finditer(unfenced):
        lvl = len(m.group(1))
        nxt = re.compile(rf"^[ \t]{{0,3}}#{{2,{lvl}}}[ \t]", re.M).search(unfenced, m.end())
        body = unfenced[m.end(): nxt.start() if nxt else len(unfenced)]
        out.append((m.group(2) + "\n" + body) if include_heading else body)
    return out


# ECO-034 製造中の実測: 宣言構文を**説明する**文書(本 ECO の order 自身)の
# コードフェンス内テンプレートが実際の宣言として解釈され、`by <誰が宣言したか>` という
# プレースホルダで自己免除が成立した。**免除を granting する文はフェンス内では読まない**。
# hard-positive は逆に**フェンス内でも読む**(非対称) — 過剰検出は出口があるので安全側だが、
# 過剰免除は fail-open で出口を要さないため。倒れる方向を揃えている。
# ECO-053: フェンス除去は共通関数 _strip_fences_all へ(旧 _FENCE_RE は閉じ fence を要求し
# 未閉鎖 fence を除去できなかった — 実測)。
def _strip_fences(text: str) -> str:
    return _strip_fences_all(text)


def _c16_receipt_present(text: str, eco_no: int = 0) -> bool:
    """ECO-053: fence 除去後に判定。eco_no >= C16_BODY_MIN は見出し+本体ラベル 5 つ、
    それ未満(遺産 order・improvements 節= 0)はトークン共起(フェンス穴だけ塞ぐ)。"""
    unf = _strip_fences_all(text)
    if eco_no >= C16_BODY_MIN:
        for body in _receipt_bodies(unf, CONVERGE_RECEIPT_HEAD_RE, include_heading=True):
            if all(rx.search(body) for _, rx in _C16_LABELS):
                return True
        return False
    return bool(CONVERGE_RECEIPT_RE.search(unf) and CONVERGE_ROUNDS_RE.search(unf)
                and CONVERGE_UNRESOLVED_RE.search(unf))


def converge_classify(text: str, eco_no: int = 0) -> dict:
    """1 artifact を分類する。返り値= required / reasons / declared / conflict / receipt。"""
    reasons = []
    for name, rx in CONVERGE_HARD_POSITIVES:
        if rx.search(text):
            reasons.append(name)
    dm = CONVERGE_DECL_RE.search(_strip_fences(text))
    declared = dm.group(1) if dm else None
    decl_reason = (dm.group(2) or "").strip() if dm else ""
    decl_by = (dm.group(3) or "").strip() if dm else ""
    grounded = bool(decl_reason and decl_by)

    # B-1 非対称設計(ECO-034 で精密化): required への引き上げは無条件で有効。
    # not-required への引き下げは **根拠(reason + decided-by)が揃うときだけ**受理し、
    # 根拠なしなら hard-positive 実在時に却下する。
    conflict = bool(declared == "not-required" and reasons and not grounded)
    exempted = bool(declared == "not-required" and reasons and grounded)
    required = (bool(reasons) and not exempted) or declared == "required"

    receipt = _c16_receipt_present(text, eco_no)
    return {"required": required, "reasons": reasons, "declared": declared,
            "conflict": conflict, "receipt": receipt, "exempted": exempted,
            "decl_reason": decl_reason, "decl_by": decl_by}


def converge_verdict(text: str, eco_no: int = 0) -> tuple[bool, str]:
    """(ok, 理由)。conflict は receipt の有無によらず FAIL(宣言による引き下げの却下)。"""
    c = converge_classify(text, eco_no)
    if c["conflict"]:
        miss = " / ".join(x for x, v in (("reason", c["decl_reason"]),
                                         ("decided-by", c["decl_by"])) if not v)
        return False, (f"根拠なき not-required 宣言(欠落: {miss})だが hard-positive 実在: "
                       f"{','.join(c['reasons'])}")
    if c["required"] and not c["receipt"]:
        why = ",".join(c["reasons"]) or "declared:required"
        if eco_no >= C16_BODY_MIN:
            return False, (f"converge-required({why})だが収束 receipt の見出し+本体ラベル"
                           "(判定/起動経路/round/未収束事項/DoD ✔✘)が揃っていない — 平文の言及・"
                           "フェンス内の様式例は receipt ではない")
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
    ("F5", False, "hard-positive 実在 かつ 根拠なし not-required 宣言",
     "<!-- converge: not-required -->\n## 残ゲート\n候補 B-1(推奨)/ 候補 B-2。\n"),
    # ECO-034: 根拠つき not-required の受理と、根拠の欠落・空欄の却下
    ("F6", False, "not-required + reason のみ(decided-by なし)",
     "<!-- converge: not-required reason: 記帳のみ -->\n## 残ゲート\n候補 B-1(推奨)。\n"),
    ("F7", True, "not-required + reason + decided-by(根拠つき受理)",
     "<!-- converge: not-required reason: 記帳のみ・裁定候補なし decided-by: maintainer -->\n"
     "## 残ゲート\n候補 B-1(推奨)/ 候補 B-2。\n"),
    ("F8", False, "not-required + 空の reason(欄の存在でなく中身を測る)",
     "<!-- converge: not-required reason:  decided-by: maintainer -->\n"
     "## 残ゲート\n候補 B-1(推奨)。\n"),
    ("F9", False, "コードフェンス内の宣言は免除を与えない(構文を説明する文書の自己免除を防ぐ)",
     "宣言の書式は次のとおり。\n\n```\n"
     "<!-- converge: not-required reason: <なぜ対象外か> decided-by: <誰が宣言したか> -->\n"
     "```\n\n## 残ゲート\n候補 B-1(推奨)。\n"),
    # ECO-053 追加 — use/mention・fence・様式の known-bad / known-good(ラベルの根拠= converge 評価時の
    # 実測。C17 の独立検査官変種〔ECO-051〕と同型)。第 5 要素= eco_no(0= 遺産規則・53= 新規則)。
    ("F10", False, "フェンス内の様式例は receipt ではない(遺産規則でも)",
     "## 残ゲート\n候補 A-1(推奨)。\n```\n## /converge receipt\n- round 1\n- 未収束事項: なし\n```\n", 0),
    ("F11", False, "未閉鎖 fence 内の様式例は receipt ではない",
     "## 残ゲート\n候補 A-1(推奨)。\n```\n## /converge receipt\n- round 1\n- 未収束事項: なし\n", 0),
    ("F12", False, "チルダ fence 内(新規則)",
     "## 残ゲート\n候補 A-1(推奨)。\n~~~\n## 収束 receipt\n- 判定: 収束 / 起動経路: 自発 / round 1 / 未収束事項: なし / DoD ✔\n~~~\n", 53),
    ("F13", False, "平文の言及(省略宣言)は receipt ではない(新規則)",
     "## 残ゲート\n候補 A-1(推奨)。\n収束 receipt は今回省略した。round 1 は未実施・未収束のまま。\n", 53),
    ("F14", False, "見出しはあるが判定・DoD のない receipt(ECO-036/053 様式違反)",
     "## 残ゲート\n候補 A-1(推奨)。\n## /converge receipt\n- round 1 = 2 件\n- 未収束事項: なし\n", 53),
    ("F15", False, "インデントされたコード例内の免除宣言は無効",
     "    <!-- converge: not-required reason: example decided-by: nobody -->\n## 残ゲート\n候補 B-1(推奨)。\n", 0),
    ("F16", True, "「round 軌跡」様式だけの正当 receipt を遮断しない(偽陽性の除去・遺産規則)",
     "## 残ゲート\n候補 A-1(推奨)。\n## /converge receipt\n- 判定: 収束(round 軌跡: 2→0→0)\n- 未収束事項: なし\n", 0),
    ("F17", True, "5 ラベル完備の receipt(known-good・新規則)",
     "## 残ゲート\n候補 A-1(推奨)。\n## /converge receipt\n- 判定: 収束(round 軌跡: 2→0→0)\n"
     "- 起動経路: 自発\n- 未収束事項: なし\n- DoD: アンカー ✔ / 実装先 ✔\n", 53),
)


def c16_converge_receipt() -> None:
    # (1) 較正 — fixture 5 種を毎回実測(予防ゲートの陽性対照。OBS-20260828-05)
    fx_bad = []
    for fx in _CONVERGE_FIXTURES:
        fid, want_ok, desc, body = fx[:4]
        eco = fx[4] if len(fx) > 4 else 0
        got_ok, why = converge_verdict(body, eco)
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
        mno = re.match(r"ECO-(\d+)$", str(ent.get("id") or ""))
        targets.append((str(ent.get("id")), po, int(mno.group(1)) if mno else 0))

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

    problems, exempt = [], []
    for name, body, eco in ([(n_, po.read_text(encoding="utf-8"), e_) for n_, po, e_ in targets]
                            + [(n_, b_, 0) for n_, b_ in sections]):
        c = converge_classify(body, eco)
        if c["exempted"]:
            exempt.append(f"{name}(by {c['decl_by']})")
        ok, why = converge_verdict(body, eco)
        if not ok:
            problems.append(f"{name}: {why}")

    # ECO-034: **沈黙する免除を作らない** — 根拠つき not-required は fail-open を再導入しうる
    # ため、有効な免除の件数と宣言者を毎回の判定行へ出す(増加が観測できる形にする)。
    n = len(targets) + len(sections)
    check("C16", not problems,
          f"converge receipt ゲート(cutoff {CONVERGE_CUTOFF} 以降 {n} 件"
          f"〔本体ラベル要求= ECO-0{C16_BODY_MIN} 以降〕・fixture {len(_CONVERGE_FIXTURES)}/{len(_CONVERGE_FIXTURES)} 較正成立"
          f"・根拠つき免除 {len(exempt)} 件"
          + ("[" + " / ".join(exempt) + "]" if exempt else "") + ")"
          + (" — " + " / ".join(problems) if problems else ""))


# --- C17 calibrate receipt ゲート(ECO-043・ECO-049・ECO-051) ---------------------------
# 目的: **calibrate 未実施(trigger ①)の ECO が正典化されるのを阻止し、非起動を観測可能に
# する**。アンカーは「受入節を書くこと」でなく「register 上で status: verified へ昇格した
# 状態遷移」(gate 裁定 4)。適用範囲= ECO-041 以降(gate 裁定 A-1 — missed-trigger debt
# repayment 済みの 2 件が最初の適用個体)。
#
# 検出力の限界(宣言 — 実施した検査が測っていない次元):
#   (1) 較正 receipt の**構造的存在**しか測らない — ECO-041〜050 は「見出し」、ECO-051 以降は
#       「見出し+本体の必須項目ラベル(主張と判定 / 計器欠陥 / 検出力の限界 / battery 行別記録
#       asked)」の存在まで。**ラベルが存在することと battery を本当に当てたことは別**であり、
#       中身の実質(判定の正しさ・行別記録の真正さ)は依然として被覆外。
#       経緯: ECO-049 で use/mention を弁別(backtick fence・見出し語句)。**盲検感度試験
#       (bomdd/reports/calibrate-blind-sensitivity-01.md)で独立検査官が 6 変種の通過を実測**
#       (チルダ fence・インデントコード例・見出し内の否定・空白なし・`#` 過多・receiptless)→
#       ECO-051 で見出し規則の厳密化+本体ラベル要求+対象/fixture 空集合の FAIL 化+`verified`
#       厳密一致+register 欠落の構造化 FAIL。**修理は当方の設計した変種にしか効かない**という
#       第 6 掃引の教訓を、独立検査官の変種を fixture へ恒久化することで補う。
#   (2) trigger ②(緑の引用)・③(検査器新設 — OBS-20260901-04 watch)・④(インシデント後)は
#       被覆外 — 本 gate は trigger ① の**最後の防波堤**(gate 裁定 5)。
#   (3) artifact に落ちない査定は被覆外。
#   (4) 天然対照(返済前 blob)は shallow clone の CI で実行不能のため**常設化しない** —
#       受入時のローカル実測のみ(環境前提の宣言= 履歴依存を常設検査に置かない)。
#   (5) 見出し内の否定文に本体ラベルまで揃えた病的 receipt(「## 較正 receipt は省略した」+
#       4 項目)は構造的には receipt であり通過する — 意味は測らない(型⑧の残余・宣言)。
#   (6) 集約レベルの guard(対象 0 件・fixture 0 本・register 欠落)は受入時のプローブで較正し、
#       恒久 fixture は verdict レベル(F1〜F18)のみ。

C17_SCOPE_MIN = 41  # ECO-041 以降(A-1)
C17_BODY_MIN = 51   # ECO-051 以降: 見出しに加え receipt 本体の必須項目ラベル+行別記録を要求
# ECO-051: 見出し行は「3 空白以内・# 2〜6 個+空白必須・receipt は語境界」— 「##較正」「#######」
# 「receiptless」を排除(独立検査官の実測変種)。
C17_RECEIPT_RE = re.compile(
    r"^[ \t]{0,3}(#{2,6})[ \t]+([^\n]*?(?:較正\s*receipt|calibrate\s*receipt)\b[^\n]*)$", re.I | re.M)
# ECO-051: 免除宣言は**行頭**でのみ有効 — 4 空白のコード例・引用内の宣言を実宣言と数えない。
C17_DECL_RE = re.compile(
    r"^<!--\s*calibrate:\s*not-required\s+reason:\s*(?P<reason>[^>]*?)\s+decided-by:\s*(?P<by>[^>]*?)\s*-->",
    re.M)
# ECO-051: ``` と ~~~ の両方・未閉鎖 fence は EOF まで除去(ECO-049 は backtick のみだった)。
_C17_FENCE_RE = _FENCE_ALL_RE   # ECO-053: 共通関数へ(C16 と正本を 1 つにする)
# ECO-051: receipt 本体の必須項目(calibrate.md「較正 receipt」節の 3 項目+ECO-052 の行別記録)。
_C17_LABELS = (
    ("主張と判定", re.compile(r"査定した主張|主張と判定")),
    ("計器欠陥", re.compile(r"計器欠陥")),
    ("検出力の限界", re.compile(r"検出力の限界|限界")),
    ("行別記録(asked)", re.compile(r"\basked\b", re.I)),
)


def _c17_receipt_bodies(unfenced: str):
    """ECO-053: 共通関数 _receipt_bodies へ委譲(挙動保存 — F1〜F18 で回帰確認)。"""
    return _receipt_bodies(unfenced, C17_RECEIPT_RE)


def c17_verdict(status: str, text: str, eco_no: int = 0):
    """(ok, 理由, exempt_by)。status が厳密に verified のもののみ対象。免除はフェンス外・行頭の
    根拠つき宣言のみ受理(reason+decided-by の 2 点必須 — ECO-034 様式)。eco_no >= C17_BODY_MIN
    は receipt 本体の必須項目ラベルまで要求する(ECO-051)。"""
    if str(status).strip() != "verified":
        return True, "", None
    unfenced = _C17_FENCE_RE.sub("", text)
    bodies = _c17_receipt_bodies(unfenced)
    if bodies:
        if eco_no < C17_BODY_MIN:
            return True, "", None
        for b in bodies:
            if all(rx.search(b) for _, rx in _C17_LABELS):
                return True, "", None
        missing = [k for k, rx in _C17_LABELS if not any(rx.search(b) for b in bodies)]
        return False, (f"較正 receipt の見出しはあるが本体の必須項目が欠落({missing})"
                       " — 見出しだけの receipt は receipt ではない"), None
    m = C17_DECL_RE.search(unfenced)
    if m and m.group("reason").strip() and m.group("by").strip():
        return True, "", m.group("by").strip()
    if m:
        miss = [k for k in ("reason", "by") if not m.group(k).strip()]
        return False, f"免除宣言の根拠欠落({miss})", None
    return False, ("verified だが較正 receipt の**見出し**がない(calibrate trigger ① 非起動)"
                   " — 平文の言及・フェンス内の様式例・インデントされたコード例は receipt ではない。"
                   "`### 較正 receipt` 節(本体: 主張と判定 / 計器欠陥 / 検出力の限界 / 行別 asked)を"
                   "書くか、行頭で根拠つき免除を宣言する"), None


_C17_FIXTURES = [
    # (name, want_ok, desc, status, text, eco_no)
    ("F1", True, "verified + receipt(旧 scope)",
     "verified", "## 追記: 事後較正 receipt\n- 査定した主張と判定…\n", 41),
    ("F2", False, "verified + receipt なし",
     "verified", "## 受入\n- V1 PASS\n", 41),
    ("F3", True, "filed + なし(verified のみ対象)",
     "filed", "## 受入\n- 検討中\n", 41),
    ("F4", True, "verified + 根拠つき免除(宣言者表示)",
     "verified", "<!-- calibrate: not-required reason: 事務的クローズのみ decided-by: maintainer -->\n", 41),
    ("F5", False, "フェンス内の免除宣言は無効(過剰免除の遮断)",
     "verified", "```\n<!-- calibrate: not-required reason: x decided-by: y -->\n```\n", 41),
    ("F6", False, "空の reason は却下(欄の存在でなく中身)",
     "verified", "<!-- calibrate: not-required reason:  decided-by: maintainer -->\n", 41),
    # ECO-049 追加 — use/mention 弁別の known-bad / known-good 腕。
    ("F7", False, "backtick フェンス内の様式例は receipt ではない(known-bad)",
     "verified", "```\n### 較正 receipt(様式の例)\n- 査定した主張と判定…\n```\n", 41),
    ("F8", False, "平文の言及・否定文は receipt ではない(known-bad)",
     "verified", "## 受入\n- V1 PASS\n\n較正 receipt は今回省略した。\n", 41),
    ("F9", True, "見出しとして存在する receipt(known-good・旧 scope)",
     "verified", "### 較正 receipt(trigger ①)\n- 査定した主張と判定…\n", 41),
    # ECO-051 追加 — 盲検感度試験で**独立検査官(Codex・検体 S4/S5)が実測した変種**を known-bad 腕へ
    # 恒久化(ラベルの根拠= 修理前 revision で通過・当方 HEAD で 6/6 再現)。当方設計の変種だけを
    # 測っていた ECO-049 の Q3 型過大判定への対処。
    ("F10", False, "チルダ fence 内の見出しは receipt ではない(独立検査官 S4-1)",
     "verified", "~~~\n### 較正 receipt\n- 査定した主張と判定 / 計器欠陥 / 検出力の限界 / asked\n~~~\n", 51),
    ("F11", False, "インデントされたコード例内の免除宣言は無効(独立検査官 S4-2)",
     "verified", "    <!-- calibrate: not-required reason: example decided-by: nobody -->\n", 51),
    ("F12", False, "見出し内の否定+本体なし(独立検査官 S4-3a)",
     "verified", "## 較正 receipt は省略した\n", 51),
    ("F13", False, "`##較正`(空白なし)は見出しではない(独立検査官 S4-3b)",
     "verified", "##較正 receipt\n- 査定した主張と判定 / 計器欠陥 / 検出力の限界 / asked\n", 51),
    ("F14", False, "`#` 7 個は見出しではない(独立検査官 S4-3c)",
     "verified", "####### calibrate receipt\n- 査定した主張と判定 / 計器欠陥 / 検出力の限界 / asked\n", 51),
    ("F15", False, "receiptless は receipt ではない(独立検査官 S4-3d)",
     "verified", "## calibrate receiptless notes\n- 査定した主張と判定 / 計器欠陥 / 検出力の限界 / asked\n", 51),
    ("F16", False, "見出しのみ・本体空は新 scope では receipt ではない(旧 P4 境界の縮小)",
     "verified", "### 較正 receipt\n\n## 次の節\n", 51),
    ("F17", True, "見出し+本体 4 項目(known-good・新 scope)",
     "verified", "### 較正 receipt(trigger ①)\n- 査定した主張と判定: …\n- 検出した計器欠陥: なし\n"
                 "- 検出力の限界: …\n| Q1 | asked | … |\n", 51),
    ("F18", True, "status 'verifiedness' は対象外(厳密一致 — 独立検査官 S4-4 の偽陽性)",
     "verifiedness", "## 受入\n", 51),
]


def c17_calibrate_receipt() -> None:
    if not _C17_FIXTURES:
        check("C17", False, "fixture 0 本 — 陽性対照の空集合は較正成立ではない(測定不能は合格ではない)")
        return
    bad = []
    for name, want_ok, desc, st, txt, eco in _C17_FIXTURES:
        ok, _, _ = c17_verdict(st, txt, eco)
        if ok != want_ok:
            bad.append(f"{name}({desc})")
    if bad:
        check("C17", False, f"fixture 較正不成立(計器を先に疑う): {bad}")
        return
    reg_path = ROOT / "bomdd" / "60-change-register.yaml"
    try:
        reg = strict_yaml_load(reg_path.read_text(encoding="utf-8"))
    except Exception as e:  # ECO-051: 欠落・解析不能は例外でなく構造化 FAIL
        check("C17", False, f"register を読めない({type(e).__name__}: {str(e)[:80]}) — 測定不能は合格ではない")
        return
    changes = reg.get("changes") if isinstance(reg, dict) else None
    if not isinstance(changes, list):
        check("C17", False, "register の changes が list でない — 測定不能は合格ではない")
        return
    problems, exempt, n = [], [], 0
    for ent in changes:
        if not isinstance(ent, dict):
            problems.append(f"changes に mapping でない要素({type(ent).__name__})")
            continue
        m = re.match(r"ECO-(\d+)$", str(ent.get("id") or ""))
        if not m or int(m.group(1)) < C17_SCOPE_MIN:
            continue
        if str(ent.get("status") or "").strip() != "verified":
            continue
        n += 1
        ref = ent.get("order_ref")
        po = ROOT / str(ref) if ref else None
        if not po or not po.is_file():
            problems.append(f"{ent.get('id')}: order_ref の実体がない({ref} — 欠測は FAIL)")
            continue
        ok, why, by = c17_verdict("verified", po.read_text(encoding="utf-8"), int(m.group(1)))
        if by:
            exempt.append(f"{ent.get('id')}(by {by})")
        if not ok:
            problems.append(f"{ent.get('id')}: {why}")
    if n == 0:  # ECO-051: 対象 0 件は PASS ではない(空集合の合格化= 型④)
        problems.append(f"適用対象 0 件(ECO-0{C17_SCOPE_MIN} 以降の verified が無い — 空集合は合格ではない)")
    check("C17", not problems,
          f"calibrate receipt ゲート(trigger ①= verified 昇格・適用 ECO-0{C17_SCOPE_MIN} 以降 {n} 件"
          f"〔本体ラベル要求= ECO-0{C17_BODY_MIN} 以降〕・fixture {len(_C17_FIXTURES)}/{len(_C17_FIXTURES)} 較正成立"
          f"・根拠つき免除 {len(exempt)} 件"
          + ("[" + " / ".join(exempt) + "]" if exempt else "") + ")"
          + (" — " + " / ".join(problems) if problems else ""))


# --- C18 pre-push witness(ECO-046) ---------------------------------------------------
# 目的: **観測前 push(検査結果を観測せず push する強制経路の故障)を機械遮断する** —
# AGENTS 規律 4「非 0 なら push しない」の機械化。由来= 同一設備・同一規則の 2 再演
# (ECO-024 / ECO-045)+ ECO-025 §7 が予約した「機械的強制の要否は測定で判断」の発火。
#
# 構成: 全検査 PASS 時に検査対象 tree の witness を .git 配下へ記録(_write_selfconf_witness)。
# bomdd/hooks/pre-push が push 対象 commit の tree と突合し、不一致・witness 不在を遮断する。
#
# 検出力の限界(宣言):
#   (1) 到達目標は「うっかり型の素通り遮断」まで — witness 改竄・hook 除去・hooksPath 解除の
#       意図的回避は信頼境界外(ECO-018 残余の限界と同じ整理)。押し戻しの最終層は CI。
#   (2) witness は fast tier の PASS に束縛(規律 2 の単一入口)— --dotnet 層は CI が毎 push 担保。
#   (3) witness の tree は「追跡対象+追加可能ファイルの worktree 内容」(一時 index への add -A)
#       — 未追跡の非 ignore ファイルが残っていると commit tree と不一致になり遮断される
#       (意図された厳密さ: 検査していない内容の push を通さない)。
#   (4) CI(GITHUB_ACTIONS)は push しない環境のため適用対象外= NA を宣言して PASS
#       (ECO-045 の NA 思想 — SKIP と PASS を同義にしない)。
#   (5) 突合対象は refs/heads/* のみ — 歴史タグ等(push.followTags の同送を含む)は当時の
#       検査対象であり witness は現 tree のみを覆うため対象外(タグ単独 push は被覆外)。

def _write_selfconf_witness() -> None:
    """全検査 PASS 時に検査対象 tree の witness を書く(ECO-046)。防御用であり検査結果に
    影響させない — git 外・書込不能なら黙って省略(pre-push 側が witness 不在を遮断する)。"""
    try:
        gd = run(["git", "-C", str(ROOT), "rev-parse", "--git-dir"])
        if gd.returncode != 0:
            return
        git_dir = Path(gd.stdout.strip())
        if not git_dir.is_absolute():
            git_dir = ROOT / git_dir
        with tempfile.TemporaryDirectory() as td:
            tmp_index = Path(td) / "index"
            src_index = git_dir / "index"
            if src_index.exists():
                shutil.copy2(src_index, tmp_index)
            env = os.environ.copy()
            env["GIT_INDEX_FILE"] = str(tmp_index)
            run(["git", "-C", str(ROOT), "add", "-A"], env=env)
            wt = run(["git", "-C", str(ROOT), "write-tree"], env=env)
            if wt.returncode != 0:
                return
            tree = wt.stdout.strip()
        # newline="\n" 明示 — Windows の改行変換で CRLF になると hook 側の比較に \r が混入する
        # (W2 緑腕の較正が本 push 前に捕捉した欠陥・ECO-046 §4)
        (git_dir / "bomdd-selfconf-witness").write_text(
            f"{tree}\nPASS\n", encoding="ascii", newline="\n")
    except OSError:
        pass


def c18_prepush_witness() -> None:
    if os.environ.get("GITHUB_ACTIONS") == "true":
        check("C18", True, "pre-push witness(NA — CI は push しない環境・適用対象外の宣言)")
        return
    hp = run(["git", "-C", str(ROOT), "config", "core.hooksPath"])
    got = (hp.stdout or "").strip()
    ok_path = hp.returncode == 0 and got == "bomdd/hooks"
    hook = ROOT / "bomdd" / "hooks" / "pre-push"
    ok_hook = hook.is_file() and "bomdd-selfconf-witness" in hook.read_text(encoding="utf-8")
    check("C18", ok_path and ok_hook,
          f"pre-push witness 設置(hooksPath={got or '未設定'}・hook 実在+witness 突合={ok_hook})"
          + ("" if ok_path and ok_hook else " — `git config core.hooksPath bomdd/hooks` で設置(ECO-046)"))


# --- 環境個体の刻印(ECO-040 Y) ------------------------------------------------------
def env_imprint(dotnet: bool) -> str:
    """今回の判定に関係する環境個体を証拠へ刻印する(ECO-040 Y・§4.4 道具の個体参照)。
    目的はドリフトの**防止**ではなく**観測可能化** — pin はしない(gate 裁定 2)。
    沈黙的ドリフトの非発生は依然 unknown(観測手段= 本刻印の事後突合のみ)。"""
    import platform
    parts = [f"python {platform.python_version()}",
             f"PyYAML {yaml.__version__}",
             f"os {platform.system()}-{platform.release()}"]
    image_os, image_ver = os.environ.get("ImageOS"), os.environ.get("ImageVersion")
    parts.append(f"runner {image_os}/{image_ver}" if image_os else "runner local")
    if dotnet:
        try:
            p = run(["dotnet", "--version"])
            parts.append(f"dotnet-sdk {p.stdout.strip()}" if p.returncode == 0
                         else "dotnet-sdk 測定不能")
        except OSError:
            parts.append("dotnet-sdk 測定不能")
    return "・".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description="BomDD リポ全体の自己適合ゲート")
    ap.add_argument("--dotnet", action="store_true",
                    help="loop .NET スイートを期待結果 manifest と突合(C9)")
    a = ap.parse_args()

    print(f"self-conformance: {ROOT}")
    print(f"[env] {env_imprint(a.dotnet)}")
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
    c17_calibrate_receipt()
    c18_prepush_witness()
    if a.dotnet:
        c9_dotnet()

    print()
    if FAILURES:
        print(f"self-conformance FAILED — {len(FAILURES)} 件の不適合")
        return 1
    _write_selfconf_witness()  # ECO-046: PASS の観測可能な証跡 — pre-push が突合する
    print("self-conformance passed — 全検査合格")
    return 0


if __name__ == "__main__":
    sys.exit(main())
