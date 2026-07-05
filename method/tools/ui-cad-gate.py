# ui-cad-gate — UI-CAD 裁定ゲート(PR-1・candidate)
#
# UI-CAD 前工程の成果物(ui-ir / ui-bom / trace map / 裁定台帳 / 辞書)を機械検査し、
# 「曖昧なまま製造へ流れる」を人間の通読ではなくゲートで止める。
# 初出: UI-CAD 工程分離(ui-ir-ui-bom.md §12–§15・2026-07-05)。
#
# 使い方:
#   python ui-cad-gate.py --ui-dir <path>/bomdd/ui
#     [--ui-ir ui-ir.json] [--ui-bom ui-bom.json] [--trace-map ui-trace-map.json]
#     [--rulings 37-ui-rulings.yaml] [--dictionary 36-ui-dictionary.yaml]
#
# 検査(不変条件は ui-ir-ui-bom.md §15 で凍結):
#   G2 会計   : ui-ir の全 action は「ui-bom に採用済み」「裁定台帳で rejected(理由付き ignore)」
#              「裁定台帳の open question に紐づく」のいずれかでなければならない。
#   G3 裁定   : blocking: true かつ status: open の裁定が 1 件でもあれば製造昇格禁止。
#   G4 来歴   : ui-bom の action item は status: ruled の裁定を持たなければならない。
#              辞書エントリは source_rulings(実在し ruled)を持たなければならない。
#              裁定の dictionary_entry は辞書に実在しなければならない。
#   G5 追跡   : ui-bom item(region/component/action/input)は trace map で
#              HTML selector へ辿れなければならない(screen は warning のみ)。
#
# G1(raw 抽出網羅)と G6(stable id 揺れ)は ui-extract.py(PR-2)導入後に追加する。
# raw IR が存在しない間、G2 の母集団は ui-ir.json の actions とする(経過措置)。
#
# 終了コード: 0 = 全ゲート合格 / 1 = 不合格あり / 2 = 入力エラー

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML が必要です: pip install pyyaml")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RULING_STATUSES = {"open", "ruled", "rejected", "superseded"}
TRACE_REQUIRED_TYPES = {"region", "component", "action", "input"}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve(ui_dir, explicit, candidates):
    """明示指定を優先し、なければ ui_dir 直下の候補名を順に探す"""
    if explicit:
        p = Path(explicit)
        return p if p.is_absolute() else ui_dir / p
    for name in candidates:
        p = ui_dir / name
        if p.exists():
            return p
    return ui_dir / candidates[0]


def ruling_target_ids(ruling):
    target = ruling.get("target") or {}
    ids = target.get("ui_ids") or []
    return set(ids if isinstance(ids, list) else [ids])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ui-dir", default="bomdd/ui")
    ap.add_argument("--ui-ir", default=None)
    ap.add_argument("--ui-bom", default=None)
    ap.add_argument("--trace-map", default=None)
    ap.add_argument("--rulings", default=None)
    ap.add_argument("--dictionary", default=None)
    args = ap.parse_args()

    ui_dir = Path(args.ui_dir)
    paths = {
        "ui-ir": resolve(ui_dir, args.ui_ir, ["ui-ir.json"]),
        "ui-bom": resolve(ui_dir, args.ui_bom, ["ui-bom.json"]),
        "trace-map": resolve(ui_dir, args.trace_map, ["ui-trace-map.json"]),
        "rulings": resolve(ui_dir, args.rulings, ["37-ui-rulings.yaml", "ui-rulings.yaml"]),
        "dictionary": resolve(ui_dir, args.dictionary, ["36-ui-dictionary.yaml", "ui-dictionary.yaml"]),
    }

    missing = [f"{k}: {v}" for k, v in paths.items() if k != "dictionary" and not v.exists()]
    if missing:
        print("[input] 必須成果物が見つかりません(裁定台帳のない案件は本ゲートの対象外です):")
        for m in missing:
            print(f"  - {m}")
        sys.exit(2)

    ui_ir = load_json(paths["ui-ir"])
    ui_bom = load_json(paths["ui-bom"])
    trace_map = load_json(paths["trace-map"])
    rulings_doc = load_yaml(paths["rulings"])
    if paths["dictionary"].exists():
        dictionary_doc = load_yaml(paths["dictionary"])
    else:
        dictionary_doc = {}
        print(f"[warn] 辞書がありません({paths['dictionary']})。空辞書として検査します。")

    rulings = rulings_doc.get("rulings") or []
    dict_entries = {}
    for section in ("actions", "parts", "terms"):
        for entry_id, entry in (dictionary_doc.get(section) or {}).items():
            dict_entries[entry_id] = entry or {}

    failures = {}   # gate -> [messages]
    warnings = []

    def fail(gate, msg):
        failures.setdefault(gate, []).append(msg)

    # --- 台帳の形式検査(全ゲートの前提) ---
    rulings_by_id = {}
    for r in rulings:
        rid = r.get("id")
        if not rid:
            fail("G4", "id のない裁定レコードがある")
            continue
        if rid in rulings_by_id:
            fail("G4", f"{rid}: id が重複している")
        rulings_by_id[rid] = r
        status = r.get("status")
        if status not in RULING_STATUSES:
            fail("G4", f"{rid}: status が不正({status})")
        if status == "ruled" and not r.get("ruling"):
            fail("G4", f"{rid}: ruled なのに ruling が空")
        if status == "superseded" and not r.get("superseded_by"):
            fail("G4", f"{rid}: superseded なのに superseded_by が空")

    active_rulings = [r for r in rulings if r.get("status") != "superseded"]

    # --- G2 会計: ui-ir の全 action が採用/ignore/質問のいずれかに分類済みか ---
    adopted_ui_ids = set()
    for item in ui_bom.get("items") or []:
        for uid in item.get("sourceUiIds") or []:
            adopted_ui_ids.add(uid)
    covered_by_ruling = set()
    for r in active_rulings:
        covered_by_ruling |= ruling_target_ids(r)

    for action in ui_ir.get("actions") or []:
        uid = action.get("uiId")
        if not uid:
            continue
        if uid not in adopted_ui_ids and uid not in covered_by_ruling:
            fail("G2", f"{uid}: ui-bom 未採用かつ裁定台帳にも現れない(黙って落ちている)")

    # --- G3 裁定: blocking open が残っていないか ---
    for r in active_rulings:
        if r.get("blocking") and r.get("status") == "open":
            fail("G3", f"{r.get('id')}: blocking の未裁定が残っている — {str(r.get('question', '')).strip()}")

    # --- G4 来歴: action item の ruled 裁定・辞書の裏付け ---
    ruled_ui_ids = set()
    for r in active_rulings:
        if r.get("status") == "ruled":
            ruled_ui_ids |= ruling_target_ids(r)

    for item in ui_bom.get("items") or []:
        if item.get("itemType") != "action":
            continue
        item_no = item.get("bomItemNo")
        source_ids = set(item.get("sourceUiIds") or [])
        if not source_ids & ruled_ui_ids:
            fail("G4", f"{item_no}: action item に ruled 裁定がない(辞書ヒットも台帳へ記録する規約)")

    for entry_id, entry in dict_entries.items():
        source_rulings = entry.get("source_rulings") or []
        if not source_rulings:
            fail("G4", f"辞書 {entry_id}: source_rulings が空(裁定の裏付けがない)")
        for rid in source_rulings:
            r = rulings_by_id.get(rid)
            if r is None:
                fail("G4", f"辞書 {entry_id}: source_rulings の {rid} が台帳に存在しない")
            elif r.get("status") != "ruled":
                fail("G4", f"辞書 {entry_id}: source_rulings の {rid} が ruled でない({r.get('status')})")

    for r in active_rulings:
        entry_ref = r.get("dictionary_entry")
        if entry_ref and entry_ref not in dict_entries:
            fail("G4", f"{r.get('id')}: dictionary_entry '{entry_ref}' が辞書に存在しない")

    # --- G5 追跡: ui-bom item が trace map 経由で HTML selector へ辿れるか ---
    traced_ui_ids = set()
    for m in trace_map.get("mappings") or []:
        selector = m.get("htmlSelector") or m.get("fallbackSelector")
        if m.get("uiId") and selector:
            traced_ui_ids.add(m["uiId"])

    for item in ui_bom.get("items") or []:
        item_no = item.get("bomItemNo")
        item_type = item.get("itemType")
        source_ids = set(item.get("sourceUiIds") or [])
        if not source_ids & traced_ui_ids:
            if item_type in TRACE_REQUIRED_TYPES:
                fail("G5", f"{item_no}({item_type}): trace map に HTML selector 付きの対応がない")
            elif item_type == "screen":
                warnings.append(f"[warn][G5] {item_no}(screen): trace なし(screen は warning のみ)")

    # --- 出力 ---
    print(f"ui-cad-gate: {ui_dir}")
    for w in warnings:
        print(w)
    all_gates = [
        ("G2", "会計(interactable accounting)"),
        ("G3", "裁定(blocking open)"),
        ("G4", "来歴(dictionary/ruling provenance)"),
        ("G5", "追跡(raw trace)"),
    ]
    exit_code = 0
    for gate, label in all_gates:
        msgs = failures.get(gate, [])
        if msgs:
            exit_code = 1
            print(f"[{gate}] FAIL {label} — {len(msgs)} 件")
            for m in msgs:
                print(f"    - {m}")
        else:
            print(f"[{gate}] PASS {label}")
    if exit_code == 0:
        print("all gates passed — E-BOM/M-BOM 昇格可")
    else:
        print("gate failed — 昇格禁止(裁定・辞書・trace を補ってから再実行)")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
