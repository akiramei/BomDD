# bomdd-job — register + ECO order から job ビューを生成する read-only 射影(ECO-062 第 1 弾)
#
# 目的: 運転員(人・Bot・スクリプトを問わない)が BomDD を理解せずに工程を運ぶための
# 機械可読ビュー。**正本ではない**(register / order が正本・本ツールは導出のみ・書き戻さない)。
# 由来: ECO-062 §1-1(job は生成される射影・手書きしない)・§5 Phase 2 手動リハーサル
# (導出可 4 欄 / 出所なし 6 欄 F1〜F6 / 状態不整合 F0)。
#
# 原則(v0 で凍結):
#  1. 全欄が `source` 座標を持つ — register のキー / order の見出し / "none"(出所なし)。
#     散文からの手写し(転写値)はしない: 出所のない欄は null + source "none" で出す(F1/F3/F4/F6)。
#  2. 状態の正本は register。order のクローズ節と register.status が矛盾したら修復せず
#     停止種別 LEDGER_INCONSISTENT を出す(F0・ECO-055 の実測)。
#  3. 停止語彙は job 側の固定値(F5・ECO-062 §0.5 の 5 種+⑥台帳不整合)。台帳から導出できるのは
#     NONE / LEDGER_INCONSISTENT / MISSING_INPUT のみ — 他は receipt 由来で本ツールの被覆外と明示する。
#  4. 終了コードは常に 0(読み取り専用・判定器ではない)。--selftest のみ失敗時に exit 1。
#  5. 報告経路は明示 UTF-8(実行環境の既定符号化に依存させない — §13)。
#
# 使い方:
#   python bomdd-job.py ECO-062 [--register PATH] [--json]
#   python bomdd-job.py --all [--register PATH]      # verified 以外の全 ECO
#   python bomdd-job.py --selftest
#
# 検出力の限界(宣言):
#   (1) クローズ節の検出は見出し形状(「## N. クローズ」+ verified 語)のみ — 本文の意味は読まない。
#   (2) forbidden / expected_outputs / independent_inspection / required_capability は register/order に
#       構造欄がないため常に null(F2/F3/F4/F6)。
#   (3) 受入の PASS/FAIL は導出しない(witness の担当・bomdd-witness.py)。
#   (4) ECO-064(F1): required_skills は activation-map(templates/product-profile/skills/activation-map.yaml・
#       参照付き対応表)から台帳側の機械アンカーだけで導出し、skills_observed は order の receipt 見出し
#       (C16/C17 の正規表現を import・preflight は job 側)から導出、skills_missing= 差(**情報欄**・停止語彙
#       不変・gate 化しない)。map 不在 / import 不能 / order 不在は unknown(合格ではない)。契約の**意味**は
#       測らない — map の source は所在参照のみで、契約が変われば所在が腐る(selftest は実在まで)。
#       認識依存のトリガー(calibrate ②④)は機械化しない。

import io
import json
import re
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

STOP_VOCABULARY = (
    "NONE",                  # 進行可
    "NORMATIVE_RULING",      # ① 規範判断が要る(gate ①・converge 裁定点)→ 人
    "VERIFICATION_FAIL",     # ② 検査赤(stop/report)→ 工場へ差し戻し
    "BOM_CONTRADICTION",     # ③ BOM 自己矛盾(blocked)→ 設計者
    "CONVERGENCE_LIMIT",     # ④ 未収束の上限到達 → 裁定点(再実行ではない)
    "PREFLIGHT_HOLD",        # ⑤ 開始条件不成立 → 工程判定
    "LEDGER_INCONSISTENT",   # ⑥ 台帳不整合(register と order の状態矛盾)→ 台帳の所有者
    "MISSING_INPUT",         # 欠測(order 不在・register 不能)— 測定不能は合格ではない
)
DERIVABLE_FROM_LEDGER = ("NONE", "LEDGER_INCONSISTENT", "MISSING_INPUT")

CLOSE_HEAD_RE = re.compile(r"^[ \t]{0,3}#{2,6}[ \t]+\d+\.[ \t]*クローズ[^\n]*verified", re.M)
FENCE_RE = re.compile(r"^[ \t]{0,3}(```|~~~)[^\n]*\n.*?(?:^[ \t]{0,3}\1[ \t]*$|\Z)", re.S | re.M)

# --- ECO-064(F1): activation-map と receipt 突合 -------------------------------------------
# 対応表の正本= method/templates/product-profile/skills/activation-map.yaml(契約の所在参照のみ・転写しない)。
# converge 要否(C16 hard-positive)と receipt 見出しの正規表現は self-conformance.py から import(正本 1 つ)。
# preflight receipt の見出し(ECO-042 様式)は C 検査が未整備のため job 側で検出する。
TOOLS_DIR = Path(__file__).resolve().parent
MAP_PATH = TOOLS_DIR.parent / "templates" / "product-profile" / "skills" / "activation-map.yaml"
PREFLIGHT_RECEIPT_RE = re.compile(r"^[ \t]{0,3}#{2,6}[ \t]+[^\n]*?/?preflight\s*receipt\b", re.I | re.M)


def _load_selfconf():
    """self-conformance.py の正規表現を import する(失敗= None・呼び側は unknown にする)。"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("bomdd_selfconf", TOOLS_DIR / "self-conformance.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return {"hard": mod.CONVERGE_HARD_POSITIVES, "converge": mod.CONVERGE_RECEIPT_HEAD_RE,
                "calibrate": mod.C17_RECEIPT_RE, "strip": mod._strip_fences_all}
    except Exception:  # noqa: BLE001 — import 不能は測定不能として上位で unknown にする
        return None


ANCHOR_KINDS = ("always", "ledger-status", "affected-refs-glob", "order-hard-positive")


def _is_str_list(v) -> bool:
    return isinstance(v, list) and all(isinstance(s, str) and s.strip() for s in v)


def validate_map(classes, base: Path) -> list:
    """IA-01/IA-04(r1): class の形状(型)と source の参照実在(ファイル+`#` 以降の literal 断片)を検査し、問題を列挙する。
    .md の断片は見出し行(# で始まる行)に含まれること・.py その他は本文に含まれることを要求する。意味の一致は測らない。"""
    problems = []
    if not isinstance(classes, list) or not classes:
        return ["classes 配列なし"]
    seen = set()
    for i, cls in enumerate(classes):
        if not isinstance(cls, dict):
            problems.append(f"class[{i}] が object でない")
            continue
        cid = cls.get("id")
        tag = f"class {cid!r}" if isinstance(cid, str) else f"class[{i}]"
        if not isinstance(cid, str) or not cid.strip():
            problems.append(f"{tag}: id が空")
        elif cid in seen:
            problems.append(f"{tag}: id 重複")
        seen.add(cid)
        if not _is_str_list(cls.get("required_skills")) or not cls.get("required_skills"):
            problems.append(f"{tag}: required_skills が非空の文字列配列でない")
        else:
            for s in cls["required_skills"]:
                if not (base / "method" / "templates" / "product-profile" / "skills" / f"{s}.md").exists():
                    problems.append(f"{tag}: スキル {s} が skills/ に実在しない")
        kind = cls.get("anchor_kind")
        if kind not in ANCHOR_KINDS:
            problems.append(f"{tag}: anchor_kind 不正 {kind!r}")
        if kind == "ledger-status" and not _is_str_list(cls.get("statuses")):
            problems.append(f"{tag}: statuses が文字列配列でない")
        if kind == "affected-refs-glob" and not _is_str_list(cls.get("instrument_paths")):
            problems.append(f"{tag}: instrument_paths が文字列配列でない")
        if not isinstance(cls.get("anchor"), str) or not cls["anchor"].strip():
            problems.append(f"{tag}: anchor が空")
        src = cls.get("source")
        if not isinstance(src, str) or not src.strip():
            problems.append(f"{tag}: source が空")
            continue
        for part in src.split(";"):
            part = part.strip()
            if not part:
                continue
            fp, _, frag = part.partition("#")
            fpath = base / fp.strip()
            if not fpath.is_file():
                problems.append(f"{tag}: source {fp.strip()} が実在しない")
                continue
            frag = frag.strip()
            if not frag:
                problems.append(f"{tag}: source {fp.strip()} に # 断片がない")
                continue
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace")
            except OSError:
                problems.append(f"{tag}: source {fp.strip()} を読めない")
                continue
            if fpath.suffix == ".md":
                ok = any(line.lstrip().startswith("#") and frag in line for line in text.splitlines())
            else:
                ok = frag in text
            if not ok:
                problems.append(f"{tag}: source 断片 '{frag}' が {fp.strip()} に実在しない")
    return problems


def load_map(path: Path = MAP_PATH, base: Path | None = None):
    """activation-map を読み validate する。(classes, None) / (None, 理由)。不正な map は使わない(fail-closed・unknown 側)。"""
    if yaml is None:
        return None, "PyYAML 不在"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        return None, f"activation-map 読取不能: {e}"
    classes = (data or {}).get("classes") if isinstance(data, dict) else None
    if not isinstance(classes, list) or not classes:
        return None, "activation-map 形状不正(classes 配列なし)"
    if base is None:
        base = path.resolve().parents[4] if len(path.resolve().parents) > 4 else path.resolve().parent
    problems = validate_map(classes, base)
    if problems:
        return None, "activation-map 不正(MAP_INVALID): " + " / ".join(problems[:5]) + (" …" if len(problems) > 5 else "")
    return classes, None


def _glob_match(ref: str, pattern: str) -> bool:
    """IA-02(r1): 区切りを跨がない glob。`*` は 1 階層内・`**` は複数階層。`\\` は `/` へ正規化(OS 非依存)。"""
    r = ref.replace("\\", "/")
    p = pattern.replace("\\", "/")
    out = ""
    i = 0
    while i < len(p):
        c = p[i]
        if c == "*":
            if i + 1 < len(p) and p[i + 1] == "*":
                out += ".*"
                i += 2
                continue
            out += "[^/]*"
        elif c == "?":
            out += "[^/]"
        else:
            out += re.escape(c)
        i += 1
    return re.fullmatch(out, r) is not None


def _class_matches(cls: dict, entry: dict, order_text: str | None, sc) -> bool | None:
    """anchor_kind ごとの機械判定。None= 判定不能(unknown)。"""
    kind = cls.get("anchor_kind")
    if kind == "always":
        return True
    if kind == "ledger-status":
        statuses = cls.get("statuses")
        if not _is_str_list(statuses):  # IA-01: 型不正は判定不能(validate_map が先に弾くが防御的に)
            return None
        return str(entry.get("status")) in statuses
    if kind == "affected-refs-glob":
        pats = cls.get("instrument_paths")
        if not _is_str_list(pats):
            return None
        refs_raw = entry.get("affected_refs")
        refs = [str(r) for r in refs_raw] if isinstance(refs_raw, list) else []
        return any(_glob_match(r, p) for r in refs for p in pats)  # IA-02: 区切りを跨がない
    if kind == "order-hard-positive":
        if order_text is None or sc is None:
            return None
        text = sc["strip"](order_text)
        return any(rx.search(text) for _, rx in sc["hard"])
    return None


def observed_skills(order_text: str | None, sc) -> list | None:
    """order の receipt 見出しから起動済みスキルを導出(fence 除去後)。None= 判定不能。"""
    if order_text is None or sc is None:
        return None
    text = sc["strip"](order_text)
    out = []
    if PREFLIGHT_RECEIPT_RE.search(text):
        out.append("preflight")
    if sc["converge"].search(text):
        out.append("converge")
    if sc["calibrate"].search(text):
        out.append("calibrate")
    return out


def _field(value, source):
    return {"value": value, "source": source}


def load_register(path: Path):
    if yaml is None:
        return None, "PyYAML 不在"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        return None, f"register 読取不能: {e}"
    if not isinstance(data, dict) or not isinstance(data.get("changes"), list):
        return None, "register 形状不正(changes 配列なし)"
    return data["changes"], None


def project(entry: dict, root: Path, register_rel: str, amap=None, map_err: str | None = None, sc=None) -> dict:
    """amap= activation-map の classes(None= 不在/不能・map_err に理由)/ sc= self-conformance の正規表現(None= import 不能)。"""
    eco = str(entry.get("id"))
    da = entry.get("diff_audit") or {}
    order_ref = entry.get("order_ref")
    job = {
        "job": _field(f"JOB-{eco}", f"{register_rel}:{eco}.id(導出)"),
        "eco": _field(eco, f"{register_rel}:{eco}.id"),
        "objective": _field(entry.get("title"), f"{register_rel}:{eco}.title"),
        "state": _field(entry.get("status"), f"{register_rel}:{eco}.status(状態の正本)"),
        "inputs": _field({"order_ref": order_ref, "affected_refs": entry.get("affected_refs")},
                         f"{register_rel}:{eco}.order_ref/affected_refs"),
        "write_scope": _field(da.get("allowed_paths"), f"{register_rel}:{eco}.diff_audit.allowed_paths"),
        "diff_baseline": _field(da.get("baseline"), f"{register_rel}:{eco}.diff_audit.baseline"),
        "required_skills": _field(None, "〔後段で導出〕"),
        "required_capability": _field(None, "none(F2: 設備認定 ID の欄なし — 第 1 弾対象外)"),
        "forbidden": _field(None, "none(F3: order「採らない」は散文 — 転写しない)"),
        "expected_outputs": _field(None, "none(F4: order §1 は散文 — 転写しない)"),
        "independent_inspection": _field(None, "none(F6: verification は散文 — 転写しない)"),
        "stop_vocabulary": _field(list(STOP_VOCABULARY), "bomdd-job.py 固定値(F5)"),
        "stop_derivable_from_ledger": _field(list(DERIVABLE_FROM_LEDGER), "bomdd-job.py 固定値(被覆宣言)"),
    }
    # 停止種別の導出(台帳のみから)
    stop, reason = "NONE", "register と order の状態に矛盾なし"
    order_text = None
    if not order_ref:
        stop, reason = "MISSING_INPUT", "order_ref なし(検査対象が特定不能)"
    else:
        op = root / order_ref
        if not op.exists():
            stop, reason = "MISSING_INPUT", f"order 不在: {order_ref}"
        else:
            order_text = op.read_text(encoding="utf-8", errors="replace")
            text = FENCE_RE.sub("", order_text)
            closed = bool(CLOSE_HEAD_RE.search(text))
            status = str(entry.get("status"))
            if closed and status != "verified":
                stop, reason = "LEDGER_INCONSISTENT", f"order にクローズ節(verified)があるが register.status={status}"
            elif status == "verified" and not closed:
                stop, reason = "LEDGER_INCONSISTENT", "register.status=verified だが order にクローズ節(verified)がない"
    job["stop_type"] = _field(stop, f"導出: {reason}")

    # ECO-064(F1): required_skills(activation-map)・skills_observed(order の receipt 見出し)・skills_missing(差・情報欄)
    if amap is None:
        job["required_skills"] = _field(None, f"unknown(理由コード MAP_MISSING: {map_err or 'activation-map 不在'})")
    else:
        req, matched, undecidable = [], [], []
        for cls in amap:
            m = _class_matches(cls, entry, order_text, sc)
            if m is None:
                undecidable.append(str(cls.get("id")))
            elif m:
                matched.append(str(cls.get("id")))
                for s in cls.get("required_skills") or []:
                    if s not in req:
                        req.append(str(s))
        src = f"activation-map.yaml: {', '.join(matched) or '(該当 class なし)'}"
        if undecidable:
            src += f" / 判定不能 class= {', '.join(undecidable)}(order 不在または self-conformance import 不能)"
        job["required_skills"] = _field(req, src)
    obs = observed_skills(order_text, sc)
    if obs is None:
        job["skills_observed"] = _field(None, "unknown(order 不在または self-conformance import 不能)")
        job["skills_missing"] = _field(None, "unknown(observed が判定不能)")
    else:
        job["skills_observed"] = _field(obs, "order の receipt 見出し(fence 除去後・C16/C17 の正規表現を import・preflight は job 側の見出し検出)")
        req_v = job["required_skills"]["value"]
        if req_v is None:
            job["skills_missing"] = _field(None, "unknown(required が判定不能)")
        else:
            job["skills_missing"] = _field([s for s in req_v if s not in obs],
                                           "導出: required − observed(情報欄・停止語彙不変・gate 化しない — playbook §8.5)")
    return job


def render(job: dict) -> str:
    out = []
    for k, f in job.items():
        v = f["value"]
        vs = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
        out.append(f"{k}: {vs}\n  source: {f['source']}")
    return "\n".join(out) + "\n"


# --- selftest(陽性対照: 整合 / 不整合 2 方向 / order 不在 / 出所なし欄が null) ---------------
def selftest() -> int:
    fails = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "bomdd").mkdir()
        reg = root / "bomdd" / "60-change-register.yaml"
        (root / "bomdd" / "open.md").write_text("# Change Order — ECO-901\n\n## 3. 受入\n- 検討中\n", encoding="utf-8")
        (root / "bomdd" / "closed.md").write_text(
            "# Change Order — ECO-902\n\n## 6. クローズ(2026-09-03・verified)\n- 受入 PASS\n"
            "```\n## 9. クローズ(fence 内・verified)\n```\n", encoding="utf-8")
        (root / "bomdd" / "fenced.md").write_text(
            "# Change Order — ECO-904\n\n```\n## 6. クローズ(2026-09-03・verified)\n```\n", encoding="utf-8")
        reg.write_text(
            "changes:\n"
            "  - {id: ECO-901, title: t1, status: decided, order_ref: bomdd/open.md, affected_refs: [a.py],\n"
            "     diff_audit: {baseline: abc, allowed_paths: [a.py]}}\n"
            "  - {id: ECO-902, title: t2, status: in-progress, order_ref: bomdd/closed.md}\n"
            "  - {id: ECO-903, title: t3, status: verified, order_ref: bomdd/missing.md}\n"
            "  - {id: ECO-904, title: t4, status: verified, order_ref: bomdd/fenced.md}\n"
            "  - {id: ECO-905, title: t5, status: verified, order_ref: bomdd/closed.md}\n",
            encoding="utf-8")
        entries, err = load_register(reg)
        if err:
            return _report([f"fixture register 読取: {err}"])
        jobs = {e["id"]: project(e, root, "bomdd/60-change-register.yaml") for e in entries}
        exp = {"ECO-901": "NONE", "ECO-902": "LEDGER_INCONSISTENT", "ECO-903": "MISSING_INPUT",
               "ECO-904": "LEDGER_INCONSISTENT", "ECO-905": "NONE"}
        for k, want in exp.items():
            got = jobs[k]["stop_type"]["value"]
            if got != want:
                fails.append(f"{k}: stop_type {got} != {want}")
        j = jobs["ECO-901"]
        if j["write_scope"]["value"] != ["a.py"] or j["job"]["value"] != "JOB-ECO-901":
            fails.append("ECO-901: 導出欄が不正")
        for k in ("forbidden", "expected_outputs", "independent_inspection", "required_capability"):
            if j[k]["value"] is not None or not j[k]["source"].startswith("none"):
                fails.append(f"ECO-901: {k} は null + source none であるべき")
        # ECO-064: 上記 jobs は map/sc なしで project したため required は unknown(理由コード)であるべき
        if j["required_skills"]["value"] is not None or "MAP_MISSING" not in j["required_skills"]["source"]:
            fails.append(f"ECO-901: map なし project の required が unknown(MAP_MISSING)でない: {j['required_skills']}")
        if any("source" not in f for f in j.values()):
            fails.append("全欄 source 必須")
        # --- r2 追加腕(独立検査 IA-04 / IA-05 の陽性対照)---
        rel = "bomdd/60-change-register.yaml"
        jobs, _ = select(["ECO-901", "ECO-902", "--json", "--register", rel], root)
        doc = json.loads(json.dumps({"register": rel, "jobs": jobs}, ensure_ascii=False))
        if len(doc["jobs"]) != 2 or {j["eco"]["value"] for j in doc["jobs"]} != {"ECO-901", "ECO-902"}:
            fails.append("IA-04: 複数 job が単一 JSON 文書に 2 件で入るべき")
        jobs, _ = select(["--register"], root)
        if jobs[0]["stop_type"]["value"] != "MISSING_INPUT":
            fails.append("IA-05: --register 値なしが MISSING_INPUT でない")
        jobs, _ = select(["ECO-999", "--register", rel], root)
        if jobs[0]["stop_type"]["value"] != "MISSING_INPUT" or jobs[0]["eco"]["value"] != "ECO-999":
            fails.append("IA-05: 不在 ECO が MISSING_INPUT レコードでない")
        reg2 = root / "bomdd" / "null.yaml"
        reg2.write_text("changes:\n  - ~\n  - {id: ECO-906, title: t6, status: decided, order_ref: bomdd/open.md}\n", encoding="utf-8")
        jobs, _ = select(["--all", "--register", "bomdd/null.yaml"], root)
        kinds = sorted(j["stop_type"]["value"] for j in jobs)
        if kinds != ["MISSING_INPUT", "NONE"]:
            fails.append(f"IA-05: null エントリの扱いが不正: {kinds}")
        # IA-07(r2): 対象指定なし・未知オプションは空 jobs でなく MISSING_INPUT レコード
        for argv_bad in (["--json", "--register", rel], ["--bogus", "ECO-901", "--register", rel]):
            jobs, _ = select(argv_bad, root)
            if len(jobs) != 1 or jobs[0]["stop_type"]["value"] != "MISSING_INPUT":
                fails.append(f"IA-07: {argv_bad} が MISSING_INPUT レコードでない: {jobs}")
        # --- ECO-064(F1): activation-map と receipt 突合 ---
        amap, map_err = load_map()
        sc = _load_selfconf()
        if amap is None:
            fails.append(f"F1: 実 activation-map が読めない: {map_err}")
        if sc is None:
            fails.append("F1: self-conformance の正規表現を import できない")
        if amap is not None:
            skills_dir = MAP_PATH.parent
            for cls in amap:
                for k in ("id", "required_skills", "anchor_kind", "anchor", "source"):
                    if k not in cls:
                        fails.append(f"F1 V3: class {cls.get('id')} に {k} がない")
                for s in cls.get("required_skills") or []:
                    if not (skills_dir / f"{s}.md").exists():
                        fails.append(f"F1 V3: class {cls.get('id')} のスキル {s} が skills/ に実在しない")
                for src in str(cls.get("source", "")).split(";"):
                    fp = src.strip().split("#")[0].strip()
                    if fp and not (TOOLS_DIR.parent.parent / fp).exists():
                        fails.append(f"F1 V3: class {cls.get('id')} の source {fp} が実在しない")
        if amap is not None and sc is not None:
            # 陽性対照: design-synthesis(残ゲート= hard-positive)/ instrument-change(method/tools/x.py)/ verified / receipt 検出(fence 内は無視)
            (root / "bomdd" / "f1-pos.md").write_text(
                "# ECO-907\n\n## 6. 残ゲート\n- gate ① 裁定\n\n## /preflight receipt(起動経路: 自発)\n- ok\n\n"
                "## /converge receipt(起動経路: 自発)\n- 判定: 収束\n\n### 較正 receipt\n- 査定した主張\n", encoding="utf-8")
            (root / "bomdd" / "f1-neg.md").write_text(
                "# ECO-908\n\n## 1. 変更\n- 事実の記録のみ\n\n```\n## /converge receipt(fence 内)\n### 較正 receipt(fence 内)\n## /preflight receipt(fence 内)\n```\n",
                encoding="utf-8")
            pos = {"id": "ECO-907", "status": "verified", "order_ref": "bomdd/f1-pos.md", "affected_refs": ["method/tools/x.py"]}
            neg = {"id": "ECO-908", "status": "decided", "order_ref": "bomdd/f1-neg.md", "affected_refs": ["docs/a.md"]}
            jp = project(pos, root, rel, amap, None, sc)
            jn = project(neg, root, rel, amap, None, sc)
            if sorted(jp["required_skills"]["value"]) != ["calibrate", "converge", "preflight"]:
                fails.append(f"F1: 陽性 required が不正: {jp['required_skills']}")
            if jp["skills_observed"]["value"] != ["preflight", "converge", "calibrate"] or jp["skills_missing"]["value"] != []:
                fails.append(f"F1: 陽性 observed/missing が不正: {jp['skills_observed']} / {jp['skills_missing']}")
            if jn["required_skills"]["value"] != ["preflight"] or jn["skills_observed"]["value"] != [] or jn["skills_missing"]["value"] != ["preflight"]:
                fails.append(f"F1: 陰性(fence 内 receipt 無視・start のみ)が不正: {jn['required_skills']} / {jn['skills_observed']} / {jn['skills_missing']}")
            # map 不在 → required unknown(missing も unknown)/ sc 不能 → observed unknown・design-synthesis 判定不能
            ju = project(pos, root, rel, None, "activation-map 不在", sc)
            if ju["required_skills"]["value"] is not None or not ju["required_skills"]["source"].startswith("unknown"):
                fails.append("F1: map 不在で required が unknown でない")
            if ju["skills_missing"]["value"] is not None:
                fails.append("F1: map 不在で missing が unknown でない")
            js = project(pos, root, rel, amap, None, None)
            if js["skills_observed"]["value"] is not None or "判定不能 class= design-synthesis" not in js["required_skills"]["source"]:
                fails.append(f"F1: sc 不能で observed unknown / design-synthesis 判定不能 でない: {js['required_skills']['source']}")
            # order 不在 → observed unknown・required は台帳アンカー分のみ+design 判定不能
            jm = project({"id": "ECO-909", "status": "filed", "order_ref": "bomdd/none.md"}, root, rel, amap, None, sc)
            if jm["skills_observed"]["value"] is not None or jm["required_skills"]["value"] != ["preflight"]:
                fails.append(f"F1: order 不在の扱いが不正: {jm['required_skills']} / {jm['skills_observed']}")
            # --- 独立検査 r1(ECO-064)の陽性対照 ---
            base = MAP_PATH.resolve().parents[4]
            # IA-04: source 断片の陰性対照 — 断片を「不存在」にした map は validate_map が弾く / 実 map は 0 件
            if validate_map(amap, base):
                fails.append(f"IA-04: 実 map に validate 問題: {validate_map(amap, base)}")
            tampered = [dict(c, source=str(c.get("source")).split("#")[0] + "#不存在") for c in amap]
            if not validate_map(tampered, base):
                fails.append("IA-04: 断片不存在の map を validate_map が通した")
            # IA-01: statuses の型不正(int / str / dict)は traceback でなく MAP_INVALID(unknown)・判定関数は None
            vp = next(c for c in amap if c.get("id") == "verified-promotion")
            for badv in (7, "verified", {"verified": 1}):
                badc = dict(vp, statuses=badv)
                if _class_matches(badc, {"status": "verified"}, None, sc) is not None:
                    fails.append(f"IA-01: statuses={badv!r} が判定不能(None)でない")
                mp = root / "bomdd" / "bad-map.yaml"
                mp.write_text("classes:\n  - {id: verified-promotion, required_skills: [calibrate], anchor_kind: ledger-status,\n"
                              f"     statuses: {json.dumps(badv)}, anchor: a, source: 'method/templates/product-profile/skills/calibrate.md#自発起動契約'}}\n",
                              encoding="utf-8")
                cl, er = load_map(mp, base)
                if cl is not None or "MAP_INVALID" not in (er or ""):
                    fails.append(f"IA-01: statuses={badv!r} の map が MAP_INVALID にならない: {er}")
            # IA-02: glob は区切りを跨がない・`\\` は `/` に正規化・`**` は複数階層
            ic = next(c for c in amap if c.get("id") == "instrument-change")
            for ref, want in (("method/tools/x.py", True), ("method/tools/sub/x.py", False), ("method" + chr(92) + "tools" + chr(92) + "x.py", True),
                              ("docs/x.py", False), ("bomdd/hooks/pre-push", True)):
                got = _class_matches(ic, {"affected_refs": [ref]}, None, sc)
                if got is not want:
                    fails.append(f"IA-02: glob {ref!r} -> {got}(期待 {want})")
            if not _glob_match("a/b/c/x.py", "a/**/x.py") or _glob_match("a/b/x.py", "a/*/*/x.py"):
                fails.append("IA-02: ** / * の階層意味が不正")
            # anchor_kind 不正・required_skills のスキル不在も MAP_INVALID
            mp = root / "bomdd" / "bad-map2.yaml"
            mp.write_text("classes:\n  - {id: x, required_skills: [nosuchskill], anchor_kind: bogus, anchor: a, source: 'method/tools/self-conformance.py#C17_SCOPE_MIN'}\n",
                          encoding="utf-8")
            cl, er = load_map(mp, base)
            if cl is not None or "MAP_INVALID" not in (er or ""):
                fails.append(f"validate: anchor_kind 不正/スキル不在の map が MAP_INVALID にならない: {er}")
    return _report(fails)


def _report(fails) -> int:
    if fails:
        print("bomdd-job selftest FAILED:\n  " + "\n  ".join(fails))
        return 1
    print("bomdd-job selftest PASS(整合 NONE / 不整合 2 方向 / order 不在 / fence 内見出し無視 / 出所なし欄 null / 全欄 source / r2: 複数 --json 単一文書・引数不正 MISSING_INPUT・null エントリ・r2b: 対象なし/未知オプション MISSING_INPUT / F1: map 実在+source 実在・陽性/陰性 class・fence 内 receipt 無視・map 不在/sc 不能/order 不在= unknown・r1: 型不正 MAP_INVALID・source 断片の陰性対照・区切りを跨がない glob)")
    return 0


def _missing(reason: str, eco: str | None = None) -> dict:
    """欠測(MISSING_INPUT)を job と同形の 1 レコードで表す — 消費側が同じ parser で読める。"""
    rec = {"stop_type": _field("MISSING_INPUT", f"導出: {reason}")}
    if eco:
        rec = {"eco": _field(eco, "引数"), **rec}
    return rec


def select(argv: list, root: Path):
    """引数と register から (jobs, reg_rel) を返す。引数不正・register 不能・null エントリは
    MISSING_INPUT レコードにして返す(IA-05: traceback を出さない・終了コードは常に 0)。"""
    reg_rel = "bomdd/60-change-register.yaml"
    if "--register" in argv:
        i = argv.index("--register")
        if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
            return [_missing("--register に値がない(引数不正)")], reg_rel
        reg_rel = argv[i + 1]
    # IA-07(r2): 未知オプション・対象指定なしを「対象なし」と区別する(空 jobs を黙って返さない)
    known = {"--register", "--json", "--all", "--selftest"}
    unknown = [a for a in argv if a.startswith("--") and a not in known]
    if unknown:
        return [_missing(f"未知のオプション(引数不正): {' '.join(unknown)}")], reg_rel
    if "--all" not in argv and not any(a.startswith(("ECO-", "CAPA-")) for a in argv):
        return [_missing("対象指定なし(引数不正): ECO-NNN か --all を指定")], reg_rel
    entries, err = load_register(root / reg_rel)
    if err:
        return [_missing(err)], reg_rel
    jobs = []
    valid = [e for e in entries if isinstance(e, dict)]
    for bad in (e for e in entries if not isinstance(e, dict)):
        jobs.append(_missing(f"register エントリが object でない: {bad!r}"))
    want = [a for a in argv if a.startswith("ECO-") or a.startswith("CAPA-")]
    if "--all" in argv:
        sel = [e for e in valid if e.get("status") != "verified"]
    else:
        sel = [e for e in valid if str(e.get("id")) in want]
        for w in want:
            if not any(str(e.get("id")) == w for e in valid):
                jobs.append(_missing(f"register に {w} なし", w))
    amap, map_err = load_map()
    sc = _load_selfconf()
    jobs.extend(project(e, root, reg_rel, amap, map_err, sc) for e in sel)
    return jobs, reg_rel


def main(argv) -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", newline="\n")
    if "--selftest" in argv:
        return selftest()
    jobs, reg_rel = select(argv, Path.cwd())
    if "--json" in argv:
        # IA-04: 複数 job でも単一 JSON 文書(object)にする — 標準 parser で閉じる
        print(json.dumps({"register": reg_rel, "jobs": jobs}, ensure_ascii=False, indent=2))
    else:
        for job in jobs:
            print(render(job))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
