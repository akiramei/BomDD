"""EXP-20261031-03 — the checker (definitions section 4.2): a specimen against the expected table.

    python check.py selftest                         # the fixtures that pin form.md's rules; exit 1 on a failure
    python check.py run <specimen.json> [--control]  # verdict as JSON on stdout: the judged cases, or the control cases

Judged cases: source rates 25 and 29.97 of expected.json; control: rate 30 (A3, not judged). Verdicts: FAIL (a value or an
undefined counterexample), UNKNOWN (anything form.md makes an error), PASS.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import form_check as fc  # noqa: E402

JUDGED, CONTROL = (25, 29.97), (30,)


def cases(control=False):
    exp = json.loads((HERE / "expected.json").read_text(encoding="utf-8"))
    want = CONTROL if control else JUDGED
    return [c for c in exp["cases"] if c["rate"] in want]


def judge(doc, table):
    """doc: the specimen's JSON object; table: cases with id, rate, presses, V1..V8."""
    try:
        spec = fc.Specimen(doc)
        ces = []
        for c in table:
            kind, val = spec.run(c["rate"], c["presses"])
            if kind == "undefined":
                ces.append({"case": c["id"], "kind": "undefined", "button": val})
                continue
            for slot in fc.SLOTS:
                if val[slot] != c[slot]:
                    ces.append({"case": c["id"], "kind": "value", "slot": slot, "expected": c[slot],
                                "predicted": val[slot]})
    except fc.FormError as e:
        return {"verdict": "UNKNOWN", "error": str(e), "cases": len(table)}
    return {"verdict": "FAIL" if ces else "PASS", "cases": len(table), "counterexamples": ces}


# ---------------------------------------------------------------- selftest (fixtures for form.md's rules, not the mutants)

def _base():
    return {"state": {"v": "src"},
            "buttons": {b: {"v": "src" if b == "Source" else b} for b in fc.BUTTONS},
            "derived": {"t": "num(v, 2)"},
            "observe": {"V1": "t + ' x'", "V2": "v == src", "V3": "t == '24'", "V4": "False", "V5": "False",
                        "V6": "False", "V7": "v > src", "V8": "num(src, 2)"}}


def _row(cid, rate, presses, **slots):
    r = {"id": cid, "rate": rate, "presses": presses, "V1": "", "V2": False, "V3": False, "V4": False, "V5": False,
         "V6": False, "V7": False, "V8": ""}
    r.update(slots)
    return r


def _mut(change):
    d = _base()
    change(d)
    return d


def selftest():
    T = [_row("a", 7, [], V1="7 x", V2=True, V8="7"), _row("b", 7, ["24"], V1="24 x", V3=True, V7=True, V8="7")]
    checks = []

    def expect(name, doc, verdict, test=None, table=T):
        r = judge(doc, table)
        ok = r["verdict"] == verdict and (test is None or test(r))
        checks.append((name, ok, r))

    expect("F1 a well-formed specimen that matches passes", _base(), "PASS")
    checks.append(("F2 num: at most d decimals, trailing zeros and point removed, half away from zero",
                   [fc.num(29.97, 2), fc.num(30.0, 2), fc.num(29.97, 0), fc.num(25, 2), fc.num(0.125, 2), fc.num(2.5, 0)]
                   == ["29.97", "30", "30", "25", "0.13", "3"], None))
    expect("F3 a button with no entry gives an undefined counterexample (FAIL, not UNKNOWN)",
           _mut(lambda d: d["buttons"].pop("24")), "FAIL",
           lambda r: r["counterexamples"] == [{"case": "b", "kind": "undefined", "button": "24"}])
    expect("F4 an unknown button id is an error", _mut(lambda d: d["buttons"].update({"25": {}})), "UNKNOWN")
    expect("F5 a parse error is an error", _mut(lambda d: d["observe"].update({"V1": "t +"})), "UNKNOWN")
    expect("F6 an unresolved name is an error", _mut(lambda d: d["observe"].update({"V1": "w + ' x'"})), "UNKNOWN")
    expect("F7 a derived cycle is an error",
           _mut(lambda d: d["derived"].update({"p": "q", "q": "p"})), "UNKNOWN")
    expect("F8 a slot of the wrong type is an error", _mut(lambda d: d["observe"].update({"V2": "'yes'"})), "UNKNOWN")
    expect("F9 a missing slot is an error", _mut(lambda d: d["observe"].pop("V8")), "UNKNOWN")
    expect("F10 an extra slot is an error", _mut(lambda d: d["observe"].update({"V9": "True"})), "UNKNOWN")
    for i, bad in enumerate(("t.upper()", "[t][0]", "(lambda: t)()", "len(t)", "num(v, d=2)", "v % 2 == 0")):
        expect(f"F11.{i} a node outside the subset is an error: {bad}",
               _mut(lambda d, bad=bad: d["observe"].update({"V1": bad})), "UNKNOWN")
    expect("F12 a button's expressions see the state before the press and are assigned together",
           {"state": {"a": "1", "b": "2"}, "buttons": {"24": {"a": "b", "b": "a"}}, "derived": {},
            "observe": {"V1": "num(a, 0) + num(b, 0)", **{f"V{i}": "False" for i in range(2, 8)}, "V8": "''"}},
           "PASS", table=[_row("s", 7, ["24"], V1="21")])
    expect("F13 a button sees the derived values of the state before the press",
           {"state": {"a": "1", "c": "0"}, "buttons": {"24": {"a": "5", "c": "d"}}, "derived": {"d": "a + 1"},
            "observe": {"V1": "num(c, 0)", **{f"V{i}": "False" for i in range(2, 8)}, "V8": "''"}},
           "PASS", table=[_row("s", 7, ["24"], V1="2")])
    expect("F14 an opening value may use src only", _mut(lambda d: d["state"].update({"w": "v"})), "UNKNOWN")
    expect("F15 string + number is an error", _mut(lambda d: d["observe"].update({"V1": "t + 1"})), "UNKNOWN")
    expect("F16 a name in both state and derived is an error", _mut(lambda d: d["derived"].update({"v": "1"})), "UNKNOWN")
    expect("F17 a value counterexample gives case, slot, expected and predicted",
           _mut(lambda d: d["observe"].update({"V7": "False"})), "FAIL",
           lambda r: r["counterexamples"] == [{"case": "b", "kind": "value", "slot": "V7", "expected": True,
                                               "predicted": False}])
    expect("F18 a button assigning a name that is not a state variable is an error",
           _mut(lambda d: d["buttons"]["24"].update({"t": "'x'"})), "UNKNOWN")
    expect("F19 a number is not a boolean slot", _mut(lambda d: d["observe"].update({"V2": "1"})), "UNKNOWN")
    expect("F20 comparing a string with a number is an error",
           _mut(lambda d: d["observe"].update({"V3": "t == 24"})), "UNKNOWN")
    expect("F21 an unknown top-level key is an error", _mut(lambda d: d.update({"extra": {}})), "UNKNOWN")
    expect("F22 notes and meta are allowed and ignored",
           _mut(lambda d: d.update({"notes": ["x"], "meta": {"id": "y"}})), "PASS")
    expect("F23 an empty button entry is defined and changes nothing",
           _mut(lambda d: d["buttons"].update({"24": {}})), "FAIL",
           lambda r: all(c["kind"] == "value" for c in r["counterexamples"]))
    try:
        fc.probe(fc.Specimen(_mut(lambda d: d["observe"].update({"V2": "'yes'"}))))
        probed = False
    except fc.FormError:
        probed = True
    checks.append(("F24 form_check's type probe finds a slot of the wrong type without any case", probed, None))

    bad = [c for c in checks if not c[1]]
    for name, ok, r in checks:
        print(("PASS " if ok else "FAIL ") + name + ("" if ok or r is None else f"  -> {json.dumps(r)[:300]}"))
    print(f"selftest: {len(checks) - len(bad)} of {len(checks)} pass")
    return 1 if bad else 0


def main():
    if sys.argv[1:2] == ["selftest"]:
        sys.exit(selftest())
    if sys.argv[1:2] == ["run"] and len(sys.argv) >= 3:
        try:
            doc = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(json.dumps({"verdict": "UNKNOWN", "error": f"not a JSON file: {e}"}))
            return
        r = judge(doc, cases("--control" in sys.argv))
        r["specimen"] = pathlib.Path(sys.argv[2]).name
        print(json.dumps(r, indent=1, ensure_ascii=False))
        return
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
