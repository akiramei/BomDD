"""EXP-20261031-03 step 5 (definitions sections 7 and 9): run check.py's judge on every frozen specimen.

    python run_all.py        # writes outputs/a1.json, outputs/a2.json, outputs/a3.json and prints a summary
A1: every specimen on the judged cases; for each mutant, whether its named case and slot are among the counterexamples and
whether its base already fails there. A2: N2a against N2b, part by part. A3: N1, M6 and M6' on the control cases.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check  # noqa: E402

SPEC = HERE / "specimens"
OUT = HERE / "outputs"
BASES = ("N1", "N2a", "N2b")
MUTANTS = [f"M{i}" for i in range(1, 10)] + [f"M{i}p" for i in range(1, 10)]


def load(name):
    return json.loads((SPEC / f"{name}.json").read_text(encoding="utf-8"))


def hits(result, case, slot):
    for c in result.get("counterexamples") or []:
        if c["case"] != case:
            continue
        if slot == "undefined" and c["kind"] == "undefined":
            return True
        if c["kind"] == "value" and c.get("slot") == slot:
            return True
    return False


def main():
    OUT.mkdir(exist_ok=True)
    judged, control = check.cases(False), check.cases(True)
    a1 = {}
    for name in BASES:
        a1[name] = check.judge(load(name), judged)
    for name in MUTANTS:
        doc = load(name)
        meta = doc["meta"]
        r = check.judge(doc, judged)
        base = a1[meta["base"]]
        r["named"] = {"case": meta["named_case"], "slot": meta["slot"],
                      "hit": hits(r, meta["named_case"], meta["slot"]),
                      "base_fails_there": hits(base, meta["named_case"], meta["slot"])}
        r["slots_differing"] = sorted({c.get("slot", "undefined") for c in r.get("counterexamples") or []})
        r["cases_failing"] = len({c["case"] for c in r.get("counterexamples") or []})
        a1[name] = r
    (OUT / "a1.json").write_text(json.dumps(a1, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    a, b = load("N2a"), load("N2b")
    a2 = {part: {"N2a": a.get(part), "N2b": b.get(part), "same": a.get(part) == b.get(part)}
          for part in ("state", "buttons", "derived", "observe")}
    a2["verdicts"] = {"N2a": a1["N2a"]["verdict"], "N2b": a1["N2b"]["verdict"]}
    a2["notes_count"] = {"N2a": len(a.get("notes") or []), "N2b": len(b.get("notes") or [])}
    (OUT / "a2.json").write_text(json.dumps(a2, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    a3 = {name: check.judge(load(name), control) for name in ("N1", "M6", "M6p")}
    (OUT / "a3.json").write_text(json.dumps(a3, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    print(f"judged cases {len(judged)}, control cases {len(control)}")
    for name, r in a1.items():
        extra = ""
        if "named" in r:
            n = r["named"]
            extra = (f"  named {n['case']} {n['slot']}: hit={n['hit']} base_fails_there={n['base_fails_there']}"
                     f"  slots {r['slots_differing']}  cases {r['cases_failing']}")
        print(f"A1 {name:4} {r['verdict']:7} ce={len(r.get('counterexamples') or [])}{extra}"
              + (f"  error={r['error']}" if r["verdict"] == "UNKNOWN" else ""))
    for name, r in a3.items():
        print(f"A3 {name:4} {r['verdict']:7} ce={len(r.get('counterexamples') or [])}")
    print("A2 same parts:", {p: a2[p]["same"] for p in ("state", "buttons", "derived", "observe")})


if __name__ == "__main__":
    main()
