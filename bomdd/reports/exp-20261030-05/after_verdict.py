"""Read after the verdict (results.md section 4; descriptive, not readings): per mutant the category of each writer next to
stage 1, the clean W3 errors, and the overlap of the counted pairs.

    python after_verdict.py <mock.html> <stage1-frozen.json> <a-frozen.json> <a-flags.json> <b-frozen.json> <b-flags.json> <out.json>
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compare as C  # noqa: E402


def load(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def main(mock, s1, a_scen, a_flags, b_scen, b_flags, out):
    clean, _ = C.W.parse(pathlib.Path(mock).read_text(encoding="utf-8"))
    scen = {"stage1": load(s1), "a": load(a_scen), "b": load(b_scen)}
    pairs = {k: {(st["in"], st["action"]) for _, st in C.counted_steps(clean, v)} for k, v in scen.items()}
    flags = {"a": load(a_flags), "b": load(b_flags)}
    rows = []
    for ra, rb in zip(flags["a"]["mutants"], flags["b"]["mutants"]):
        rows.append({"id": ra["id"], "class": ra["class"], "stage1": "inside" if ra["stage1_inside"] else "outside",
                     "a": ra.get("category", "f:" + str(len(ra.get("false_alarm", [])))),
                     "b": rb.get("category", "f:" + str(len(rb.get("false_alarm", [])))),
                     "a_detail": ra.get("detail"), "b_detail": rb.get("detail")})
    errors = {}
    for w in ("a", "b"):
        steps = {f"{s['id']}#{i}": st for s in scen[w]["scenarios"] for i, st in enumerate(s["steps"])}
        errors[w] = [{"at": f["at"], "why": f["why"], "step": steps[f["at"]]} for f in flags[w]["clean_stop_flags"]]
    overlap = {
        "a&b": len(pairs["a"] & pairs["b"]), "a|b": len(pairs["a"] | pairs["b"]),
        "stage1&a": len(pairs["stage1"] & pairs["a"]), "stage1&b": len(pairs["stage1"] & pairs["b"]),
        "stage1|a|b": len(pairs["stage1"] | pairs["a"] | pairs["b"]),
        "sizes": {k: len(v) for k, v in pairs.items()},
        "actions": {k: sorted({a for _, a in v}) for k, v in pairs.items()}}
    res = {"mutants": rows, "clean_errors": errors, "overlap": overlap,
           "agree_a_b": sum(r["a"] == r["b"] for r in rows if r["class"] != "f")}
    pathlib.Path(out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    for r in rows:
        if r["class"] != "f":
            print(r["id"], r["class"], "s1", r["stage1"], "a", r["a"], "b", r["b"])
    for w in ("a", "b"):
        for e in errors[w]:
            print(w, e["at"], e["why"])
    print({k: v for k, v in overlap.items() if k != "actions"}, "a/b agree on", res["agree_a_b"], "of 25")


if __name__ == "__main__":
    main(*sys.argv[1:8])
