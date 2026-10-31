"""EXP-20261031-03 step 1 cross-check (definitions section 6): the expected table computed from S1's requirements as written,
without the authority, compared with expected.json value by value.

    python req070.py        # writes req070-check.json; exit 1 on any difference

The rules, each from the statement it cites (EXP-20261031-02 `s1/10-requirements.yaml`, frozen):
- REQ-020: on opening, the output fps is the source's fps.
- REQ-070: "Source" sets the output fps to the source's fps, a number sets that value; the output fps is written with at most
  two decimals; "Source" is shown selected when |output - source| < 0.05, a number when the written output equals it (both
  can be selected); the note shows when output > source + 0.05; Source's tooltip is "Same as source ({fps} fps)".
- REQ-077: the summary shows the frame rate as "{the written output fps} fps".
"""
import json
import pathlib
import sys
from decimal import Decimal, ROUND_HALF_UP

HERE = pathlib.Path(__file__).resolve().parent


def written(x):
    """At most two decimals, trailing zeros and the point removed (REQ-070 小数 2 桁まで)."""
    s = str(Decimal(repr(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return s.rstrip("0").rstrip(".") if "." in s else s


def slots(rate, presses):
    out = rate                                    # REQ-020
    for b in presses:
        out = rate if b == "Source" else float(b)  # REQ-070
    t = written(out)
    return {"V1": f"{t} fps",                      # REQ-077
            "V2": abs(out - rate) < 0.05,
            "V3": t == "24", "V4": t == "30", "V5": t == "60", "V6": t == "120",
            "V7": out > rate + 0.05,
            "V8": f"Same as source ({written(rate)} fps)"}


def main():
    exp = json.loads((HERE / "expected.json").read_text(encoding="utf-8"))
    diffs, n = [], 0
    for c in exp["cases"]:
        mine = slots(c["rate"], c["presses"])
        for k, v in mine.items():
            n += 1
            if c[k] != v:
                diffs.append({"case": c["id"], "slot": k, "authority": c[k], "requirements": v})
    res = {"values_compared": n, "differences": len(diffs), "diffs": diffs,
           "cultures": [exp["CurrentCulture"], exp["CurrentUICulture"], exp["LocalizerCulture"]]}
    (HERE / "req070-check.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{n} values compared, {len(diffs)} differences; cultures {res['cultures']}")
    if diffs or res["cultures"] != ["en", "en", "en"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
