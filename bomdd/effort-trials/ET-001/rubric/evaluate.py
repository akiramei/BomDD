#!/usr/bin/env python3
"""ET-001 評価者(oracle スクリプト・盲検は構造で担保: 本スクリプトは出力ファイルと rubric.md しか読まず、
treatment(model / effort / method_stack)を受け取る引数を持たない)。

使い方: python evaluate.py <RESULT.md> [rubric.md]
出力: JSON {result: pass|fail, observed_failures: [...], correct: n, expected: n, details: {...}}
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
VERDICT_RE = re.compile(r"^[ \t]*(S\d\d)\s*[:：]\s*(PASS|FAIL)\b", re.M)
ROW_RE = re.compile(r"^\|\s*(S\d\d)\s*\|\s*(\d+)\s*\|\s*(PASS|FAIL)\s*\|\s*`([^`]+)`\s*\|", re.M)


def load_rubric(p: Path) -> dict:
    rows = ROW_RE.findall(p.read_text(encoding="utf-8"))
    if not rows:
        raise SystemExit("rubric.md の期待表を読めない(評価不能は合格ではない)")
    return {sid: (exp, sym) for sid, _eco, exp, sym in rows}


def evaluate(result_text: str, rubric: dict) -> dict:
    found: dict[str, set] = {}
    for sid, v in VERDICT_RE.findall(result_text):
        found.setdefault(sid, set()).add(v)
    failures: list[str] = []
    details: dict[str, str] = {}
    correct = 0
    for sid, (exp, sym) in rubric.items():
        got = found.get(sid)
        if not got:
            failures.append("missing-verdict"); details[sid] = f"expected {exp}, got none"
        elif len(got) > 1:
            failures.append("format-violation"); details[sid] = f"expected {exp}, got conflicting {sorted(got)}"
        elif next(iter(got)) != exp:
            failures.append(sym); details[sid] = f"expected {exp}, got {next(iter(got))}"
        else:
            correct += 1; details[sid] = "ok"
    return {"result": "pass" if not failures else "fail",
            "observed_failures": sorted(set(failures)), "correct": correct,
            "expected": len(rubric), "details": details}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__); return 2
    rubric = load_rubric(Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "rubric.md")
    out = evaluate(Path(sys.argv[1]).read_text(encoding="utf-8"), rubric)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
