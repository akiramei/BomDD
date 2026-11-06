"""EXP-20261107-02 tally (definitions.md section 4): R1' and R2' per B writer against C1 / C2 of EXP-20261107-01.

    python tally.py <scores.json> <scorer-key.json> <out.json>

A reading is fixed in section 4: both B >= 1 -> "a"; both 0 -> "not the field"; one each -> no claim.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
D = ["F1", "F2", "F3", "F4", "F5"]
N = ["F6", "F7", "F8", "F9", "F10", "F11"]


def reading(b):
    if all(x >= 1 for x in b):
        return "a (the field carried it)"
    if all(x == 0 for x in b):
        return "not the field (b, or the remaining scaffolding)"
    return None


def main(scores_p, key_p, out_p):
    scores = json.loads(pathlib.Path(scores_p).read_text(encoding="utf-8"))
    key = json.loads(pathlib.Path(key_p).read_text(encoding="utf-8"))
    per = {}
    for lab, w in key.items():
        comp = json.loads((HERE / f"run-{w}" / "compared.json").read_text(encoding="utf-8"))["summary"]
        f = scores[lab]["facts"]
        v = {fid: f[fid]["verdict"] for fid in D + N}
        per[w] = {"label": lab, "asserted": comp["asserted"], "fail": comp["fail"], "fail_share": comp["fail_share"],
                  "pressed_unavailable": comp["pressed-unavailable"],
                  "R2_N_wrong": sum(v[x] == "wrong" for x in N), "D_correct": sum(v[x] == "correct" for x in D),
                  "N_open": sum(v[x] == "open" for x in N), "N_correct": sum(v[x] == "correct" for x in N),
                  "verdicts": v, "questions": scores[lab]["questions"]["count"],
                  "questions_answered_by_sources": scores[lab]["questions"]["answered_by_sources"]}
    c = json.loads((HERE.parent / "exp-20261107-01" / "tally.json").read_text(encoding="utf-8"))["per_writer"]
    control = {w: {"fail": c[w]["fail"], "R2_N_wrong": c[w]["R2_N_wrong"]} for w in ("C1", "C2")}
    B = [per["B1"], per["B2"]]
    readings = {"R1'": reading([x["fail"] for x in B]), "R2'": reading([x["R2_N_wrong"] for x in B])}
    out = {"per_writer": per, "control_of_exp_20261107_01": control, "readings": readings}
    pathlib.Path(out_p).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    for w, x in per.items():
        print(w, x["label"], "fail", x["fail"], "/", x["asserted"], "R2'", x["R2_N_wrong"], "D correct", x["D_correct"],
              "N open", x["N_open"], "N correct", x["N_correct"], "q", x["questions"],
              "answered", x["questions_answered_by_sources"])
        print("   ", x["verdicts"])
    print("control", control)
    print("readings", readings)


if __name__ == "__main__":
    main(*sys.argv[1:4])
