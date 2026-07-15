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
