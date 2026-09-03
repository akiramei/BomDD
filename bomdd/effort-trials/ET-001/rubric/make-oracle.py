#!/usr/bin/env python3
"""ET-001 — 検体 12 件を書き出し、oracle(self-conformance.py の C16 実装 `converge_verdict`)で
期待判定を計算して rubric.md の期待表へ凍結する。**run 開始前に 1 回だけ実行**(rubric 封印)。
来歴: oracle は本リポの method/tools/self-conformance.py を import して実行(実装そのものが真実 —
散文仕様は TASK.md 側の転写であり、転写の忠実性は本スクリプトでは測らない)。"""
from __future__ import annotations
import hashlib, importlib.util, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRIAL = HERE.parent
ROOT = TRIAL.parents[2]
SAMPLES = TRIAL / "samples"
sys.stdout.reconfigure(encoding="utf-8")

# (id, eco_no, 症状語彙(誤答時に記録する語), 本文)
CASES = [
    ("S01", 60, "miss-hard-positive",
     "## 残ゲート\n候補 A / 候補 B を指定する。\n"),
    ("S02", 60, "miss-heading-label",
     "## 論点\ngate ① は user 裁定。\n"
     "## /converge receipt(起動経路: 自発)\n- 判定: 収束(round 軌跡: 2→0→0)\n"
     "- 未収束事項: なし\n- DoD: 正本一意 ✔ / 影響列挙 ✔\n"),
    ("S03", 40, "miss-legacy-rule",
     "## 残ゲート\n候補 A(推奨)。\n## 収束 receipt\n- round 1 = 3 件 / round 2 = 0 件\n- 未収束事項: なし\n"),
    ("S04", 60, "miss-new-rule-labels",
     "## 残ゲート\n候補 A(推奨)。\n## 収束 receipt\n- round 1 = 3 件 / round 2 = 0 件\n- 未収束事項: なし\n"),
    ("S05", 60, "miss-grounded-exemption",
     "<!-- converge: not-required reason: 記帳のみ decided-by: maintainer -->\n"
     "## 記録\n案 α を推奨: 記帳のみで裁定なし。\n"),
    ("S06", 60, "miss-fence-declaration",
     "宣言の書き方:\n\n```\n<!-- converge: not-required reason: 記帳のみ decided-by: maintainer -->\n```\n\n"
     "## 残ゲート\n候補 α(推奨)。\n"),
    ("S07", 60, "miss-declared-required",
     "<!-- converge: required -->\n## 記録\nstatus を filed から applied へ。\n"),
    ("S08", 60, "miss-fenced-hard-positive",
     "## 記録\n次の文言は使わない例:\n\n```\n裁定をお願いします\n```\n\n差分は 1 行。\n"),
    ("S09", 60, "miss-conflict-precedence",
     "<!-- converge: not-required reason: 事務クローズ decided-by:  -->\n"
     "## 裁定対象\n案 A / 案 B。\n"
     "## /converge receipt(起動経路: 人間呼び出し)\n- 判定: 収束(round 軌跡: 1→0→0)\n"
     "- 未収束事項: なし\n- DoD ✔\n"),
    ("S10", 60, "miss-body-boundary",
     "## 残ゲート\n候補 A(推奨)。\n### 収束 receipt\n- 判定: 収束(round 軌跡: 2→0)\n"
     "- 起動経路: 自発\n- DoD: アンカー ✔\n## 補足\n- 未収束事項: なし\n"),
    ("S11", 60, "miss-unclosed-fence",
     "## 残ゲート\n候補 A(推奨)。\n実行例:\n```\npython tool.py\n\n"
     "## /converge receipt(起動経路: 自発)\n- 判定: 収束(round 軌跡: 1→0→0)\n"
     "- 未収束事項: なし\n- DoD ✔\n"),
    ("S12", 60, "false-fail-control",
     "## 残ゲート\n候補 A(推奨)。\n~~~\nsample code\n~~~\n"
     "## /converge receipt(起動経路: 自発)\n- 判定: 収束(round 軌跡: 1→0→0)\n"
     "- 未収束事項: なし\n- DoD: 影響列挙 ✔\n"),
]


def load_gate():
    p = ROOT / "method" / "tools" / "self-conformance.py"
    spec = importlib.util.spec_from_file_location("selfconf", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m, p


def main() -> int:
    gate, gate_path = load_gate()
    rev = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    gate_sha = hashlib.sha256(gate_path.read_bytes()).hexdigest()
    SAMPLES.mkdir(exist_ok=True)
    rows = []
    for sid, eco, sym, text in CASES:
        (SAMPLES / f"{sid}.md").write_text(text, encoding="utf-8")
        ok, why = gate.converge_verdict(text, eco)
        rows.append((sid, eco, "PASS" if ok else "FAIL", sym, why))
    lines = ["# ET-001 rubric(封印 — run 開始前に確定・以後不変)", "",
             f"- oracle: `method/tools/self-conformance.py` の `converge_verdict(text, eco_no)` @ `{rev}`",
             f"  (sha256 `{gate_sha}`)",
             "- 合否: 12 検体すべてで `Sxx: PASS|FAIL` の判定が期待と一致したとき **pass**、1 件でも不一致・欠落・",
             "  形式違反があれば **fail**(閾値なし — 部分点は評価 receipt に持ち込まない)",
             "- 症状語彙: 不一致の検体に対応する語(下表)+ `missing-verdict`(判定行なし)+ `format-violation`",
             "  (同一検体に相反する判定行、または判定行の書式外)",
             "", "| 検体 | eco_no | 期待 | 誤答時の症状語 | oracle 理由 |", "|---|---|---|---|---|"]
    for sid, eco, v, sym, why in rows:
        lines.append(f"| {sid} | {eco} | {v} | `{sym}` | {why.replace('|', '/')} |")
    (HERE / "rubric.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for r in rows:
        print(*r[:4])
    return 0


if __name__ == "__main__":
    sys.exit(main())
