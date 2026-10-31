"""The domain model's form check and counts.

  python check_model.py <domain-model.json> [<folder with 10-requirements.yaml and 20-spec.md>]
  python check_model.py selftest

Checks the form and that every cited source id exists in the given texts. Prints ERROR lines (the author fixes them) and the
counts. Judges nothing about the content.
"""
import json
import pathlib
import re
import sys

ID = re.compile(r"\b(REQ-\d{3}|SPEC-[A-Z]+(?:-[A-Z]+)*-\d{3}|INV-\d{3})\b")


def known_ids(folder):
    text = "".join((pathlib.Path(folder) / n).read_text(encoding="utf-8") for n in ("10-requirements.yaml", "20-spec.md"))
    return set(ID.findall(text))


def errors_of(model, ids):
    errs = []
    if not isinstance(model.get("entities"), list) or not model["entities"]:
        return ["entities: a non-empty list is required"]
    names = set()
    for e in model["entities"]:
        n = e.get("name")
        if not isinstance(n, str) or not n:
            errs.append(f"entity without a name: {json.dumps(e, ensure_ascii=False)[:80]}")
            continue
        if n in names:
            errs.append(f"{n}: entity name repeated")
        names.add(n)
        for key in ("description", "source", "attributes", "relations"):
            if key not in e:
                errs.append(f"{n}: '{key}' missing")
        for a in e.get("attributes", []):
            an = f"{n}.{a.get('name')}"
            for key in ("name", "description", "type", "initial", "set_by", "source"):
                if key not in a:
                    errs.append(f"{an}: '{key}' missing")
            if not isinstance(a.get("set_by", []), list):
                errs.append(f"{an}: set_by must be a list")
        for r in e.get("relations", []):
            if r.get("to") not in {x.get("name") for x in model["entities"]}:
                errs.append(f"{n}: relation to an entity not in the model: {r.get('to')}")
    for q in model.get("questions", []):
        for key in ("subject", "text", "source"):
            if key not in q:
                errs.append(f"question without '{key}': {json.dumps(q, ensure_ascii=False)[:80]}")
    for where, src in cited(model):
        for i in ID.findall(" ".join(src) if isinstance(src, list) else str(src)):
            if i not in ids:
                errs.append(f"{where}: cites {i}, which is not in the given texts")
    return errs


def cited(model):
    for e in model.get("entities", []):
        yield e.get("name"), e.get("source", [])
        for a in e.get("attributes", []):
            yield f"{e.get('name')}.{a.get('name')}", a.get("source", [])
        for r in e.get("relations", []):
            yield f"{e.get('name')}->{r.get('to')}", r.get("source", [])
    for q in model.get("questions", []):
        yield f"question {q.get('subject')}", q.get("source", [])


def counts(model):
    attrs = [(e, a) for e in model["entities"] for a in e.get("attributes", [])]
    src = lambda a, p: any(str(s).startswith(p) or p in str(s) for s in (a.get("source") or []))
    return {"entities": len(model["entities"]), "attributes": len(attrs),
            "relations": sum(len(e.get("relations", [])) for e in model["entities"]),
            "questions": len(model.get("questions", [])),
            "attributes_with_initial": sum(1 for _, a in attrs if str(a.get("initial", "")).strip().lower() not in ("", "unknown")),
            "attributes_with_set_by": sum(1 for _, a in attrs if a.get("set_by")),
            "attributes_citing_req": sum(1 for _, a in attrs if src(a, "REQ-")),
            "attributes_citing_spec": sum(1 for _, a in attrs if src(a, "SPEC-") or src(a, "§"))}


def selftest():
    ids = {"REQ-001", "SPEC-EDIT-001"}
    good = {"entities": [{"name": "Clip", "description": "d", "source": ["REQ-001"], "relations": [],
                          "attributes": [{"name": "duration", "description": "length in seconds", "type": "double",
                                          "initial": "probe", "set_by": [], "source": ["REQ-001"]}]},
                         {"name": "Mixer", "description": "sound", "source": ["SPEC-EDIT-001"],
                          "relations": [{"to": "Clip", "kind": "belongs to", "source": ["REQ-001"]}],
                          "attributes": [{"name": "gain", "description": "gain in percent", "type": "int",
                                          "initial": "100", "set_by": ["SetGain"], "source": ["SPEC-EDIT-001"]}]}],
            "questions": []}
    cases = [("good", good, 0)]
    bad_src = json.loads(json.dumps(good)); bad_src["entities"][0]["source"] = ["REQ-099"]
    bad_rel = json.loads(json.dumps(good)); bad_rel["entities"][1]["relations"][0]["to"] = "Nope"
    bad_key = json.loads(json.dumps(good)); del bad_key["entities"][0]["attributes"][0]["initial"]
    cases += [("unknown source", bad_src, 1), ("dangling relation", bad_rel, 1), ("missing key", bad_key, 1)]
    ok = True
    for name, m, want in cases:
        got = len(errors_of(m, ids))
        ok &= (got > 0) == (want > 0)
        print(("PASS" if (got > 0) == (want > 0) else "FAIL"), name, got)
    c = counts(good)
    ok &= (c["attributes"], c["attributes_with_set_by"]) == (2, 1)
    print("PASS" if (c["attributes"], c["attributes_with_set_by"]) == (2, 1) else "FAIL", "counts", c)
    return 0 if ok else 1


def main():
    if sys.argv[1] == "selftest":
        return selftest()
    model = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    folder = sys.argv[2] if len(sys.argv) > 2 else pathlib.Path(sys.argv[1]).parent
    errs = errors_of(model, known_ids(folder))
    for e in errs:
        print("ERROR", e)
    if not errs:
        print(json.dumps(counts(model), ensure_ascii=False))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
