#!/usr/bin/env python3
"""ET-002 評価者(oracle スクリプト・構造的盲検: 出力ファイルと rubric.md 以外を読まず、treatment を受け取る引数を持たない)。

使い方: python evaluate.py <RESULT.md> [rubric.md]
出力: JSON {result: pass|fail, observed_failures: [...], correct: n, expected: n, details: {...}}
採点対象は rubric.md の期待表に載るゲートのみ(除外ゲートは表に載せない)。
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
VERDICT_RE = re.compile(r"^[ \t]*(C\d{1,2}[ab]?)\s*[:：]\s*(SILENT|OK)\b", re.M | re.I)
ROW_RE = re.compile(r"^\|\s*(C\d{1,2}[ab]?)\s*\|\s*(SILENT|OK)\s*\|", re.M)


def load_rubric(p: Path) -> dict:
    rows = ROW_RE.findall(p.read_text(encoding="utf-8"))
    if not rows:
        raise SystemExit("rubric.md の期待表を読めない(評価不能は合格ではない)")
    return {g: v for g, v in rows}


def evaluate(text: str, rubric: dict) -> dict:
    found: dict[str, set] = {}
    for g, v in VERDICT_RE.findall(text):
        # v1 の計器欠陥(ET-002 較正で捕捉): g.upper() が "C5a"→"C5A" にして rubric キーと不一致になり、
        # 添字つきゲート 5 本が全腕で missing-verdict になった。正規化は「C+数字+小文字添字」に揃える。
        key = "C" + g[1:].rstrip("abAB") + g[len(g.rstrip("abAB")):].lower()
        found.setdefault(key, set()).add(v.upper())
    failures, details, correct = [], {}, 0
    for g, exp in rubric.items():
        got = found.get(g)
        if not got:
            failures.append("missing-verdict"); details[g] = f"expected {exp}, got none"
        elif len(got) > 1:
            failures.append("format-violation"); details[g] = f"expected {exp}, got conflicting {sorted(got)}"
        elif next(iter(got)) != exp:
            failures.append("miss-silent" if exp == "SILENT" else "false-silent")
            details[g] = f"expected {exp}, got {next(iter(got))}"
        else:
            correct += 1; details[g] = "ok"
    return {"result": "pass" if not failures else "fail", "observed_failures": sorted(set(failures)),
            "correct": correct, "expected": len(rubric), "details": details}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__); return 2
    rubric = load_rubric(Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "rubric.md")
    print(json.dumps(evaluate(Path(sys.argv[1]).read_text(encoding="utf-8"), rubric), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
