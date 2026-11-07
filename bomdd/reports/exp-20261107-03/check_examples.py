"""Form check of examples.json (EXP-20261107-03 definitions section 5). Checks the form only, never the values.

    python check_examples.py examples.json
"""
import json
import sys

SHOWS_WORDS = {"visible", "hidden", "active", "not active"}


def check(doc):
    errs = []
    if not isinstance(doc, dict) or set(doc) != {"examples"} or not isinstance(doc["examples"], list):
        return ['top level must be {"examples": [...]}']
    exs = doc["examples"]
    if not 3 <= len(exs) <= 20:
        errs.append(f"{len(exs)} examples (3-20 allowed)")
    ids = set()
    for i, ex in enumerate(exs):
        w = f"example {i + 1}"
        if not isinstance(ex, dict):
            errs.append(f"{w}: not an object")
            continue
        extra = set(ex) - {"id", "title", "steps"}
        if extra:
            errs.append(f"{w}: unknown keys {sorted(extra)}")
        if not isinstance(ex.get("id"), str) or not ex["id"]:
            errs.append(f"{w}: id must be a non-empty string")
        elif ex["id"] in ids:
            errs.append(f"{w}: duplicate id {ex['id']}")
        else:
            ids.add(ex["id"])
            w = ex["id"]
        if not isinstance(ex.get("title"), str):
            errs.append(f"{w}: title must be a string")
        steps = ex.get("steps")
        if not isinstance(steps, list) or not 1 <= len(steps) <= 8:
            errs.append(f"{w}: steps must be a list of 1-8")
            continue
        for k, st in enumerate(steps):
            sw = f"{w} step {k + 1}"
            if not isinstance(st, dict) or set(st) - {"press", "expect"} or "press" not in st or "expect" not in st:
                errs.append(f"{sw}: must have exactly press and expect")
                continue
            p = st["press"]
            if p is None:
                if k != 0:
                    errs.append(f"{sw}: press null is allowed only on the first step")
            elif not isinstance(p, str) or not p.strip():
                errs.append(f"{sw}: press must be null or a non-empty string")
            ex_ = st["expect"]
            if not isinstance(ex_, list):
                errs.append(f"{sw}: expect must be a list")
                continue
            for j, e in enumerate(ex_):
                ew = f"{sw} expect {j + 1}"
                if not isinstance(e, dict) or set(e) != {"element", "shows"}:
                    errs.append(f"{ew}: must have exactly element and shows")
                    continue
                if not isinstance(e["element"], str) or not e["element"].strip():
                    errs.append(f"{ew}: element must be a non-empty string")
                if not isinstance(e["shows"], str) or not e["shows"].strip():
                    errs.append(f"{ew}: shows must be a non-empty string")
    return errs


def main(path):
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as e:  # noqa: BLE001 - report any read or parse failure as a form error
        print("FAIL:", e)
        return 1
    errs = check(doc)
    for e in errs:
        print("ERROR", e)
    n = len(doc.get("examples", [])) if isinstance(doc, dict) else 0
    print("OK" if not errs else f"{len(errs)} errors", f"({n} examples)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
