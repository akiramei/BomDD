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
#   (2) required_skills / forbidden / expected_outputs / independent_inspection は register/order に
#       構造欄がないため常に null(F1/F3/F4/F6)。task class → スキル対応表は第 1 弾の対象外。
#   (3) 受入の PASS/FAIL は導出しない(witness の担当・bomdd-witness.py)。

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


def project(entry: dict, root: Path, register_rel: str) -> dict:
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
        "required_skills": _field(None, "none(F1: 事前宣言欄なし — receipt 見出しは事後記録のため転写しない)"),
        "required_capability": _field(None, "none(F2: 設備認定 ID の欄なし — 第 1 弾対象外)"),
        "forbidden": _field(None, "none(F3: order「採らない」は散文 — 転写しない)"),
        "expected_outputs": _field(None, "none(F4: order §1 は散文 — 転写しない)"),
        "independent_inspection": _field(None, "none(F6: verification は散文 — 転写しない)"),
        "stop_vocabulary": _field(list(STOP_VOCABULARY), "bomdd-job.py 固定値(F5)"),
        "stop_derivable_from_ledger": _field(list(DERIVABLE_FROM_LEDGER), "bomdd-job.py 固定値(被覆宣言)"),
    }
    # 停止種別の導出(台帳のみから)
    stop, reason = "NONE", "register と order の状態に矛盾なし"
    if not order_ref:
        stop, reason = "MISSING_INPUT", "order_ref なし(検査対象が特定不能)"
    else:
        op = root / order_ref
        if not op.exists():
            stop, reason = "MISSING_INPUT", f"order 不在: {order_ref}"
        else:
            text = FENCE_RE.sub("", op.read_text(encoding="utf-8", errors="replace"))
            closed = bool(CLOSE_HEAD_RE.search(text))
            status = str(entry.get("status"))
            if closed and status != "verified":
                stop, reason = "LEDGER_INCONSISTENT", f"order にクローズ節(verified)があるが register.status={status}"
            elif status == "verified" and not closed:
                stop, reason = "LEDGER_INCONSISTENT", "register.status=verified だが order にクローズ節(verified)がない"
    job["stop_type"] = _field(stop, f"導出: {reason}")
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
        for k in ("required_skills", "forbidden", "expected_outputs", "independent_inspection", "required_capability"):
            if j[k]["value"] is not None or not j[k]["source"].startswith("none"):
                fails.append(f"ECO-901: {k} は null + source none であるべき")
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
    return _report(fails)


def _report(fails) -> int:
    if fails:
        print("bomdd-job selftest FAILED:\n  " + "\n  ".join(fails))
        return 1
    print("bomdd-job selftest PASS(整合 NONE / 不整合 2 方向 / order 不在 / fence 内見出し無視 / 出所なし欄 null / 全欄 source / r2: 複数 --json 単一文書・引数不正 MISSING_INPUT・null エントリ)")
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
    jobs.extend(project(e, root, reg_rel) for e in sel)
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
