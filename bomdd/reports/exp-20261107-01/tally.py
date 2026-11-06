"""EXP-20261107-01 tally (definitions.md section 8): R1-R3 per writer and the fixed readings.

    python tally.py <scores.json> <scorer-key.json> <out.json>
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
D = ["F1", "F2", "F3", "F4", "F5"]
N = ["F6", "F7", "F8", "F9", "F10", "F11"]


def direction(k, c, lower_is_better):
    """'K' / 'C' when the arms do not overlap in the better direction, else None."""
    if lower_is_better:
        if max(k) < min(c):
            return "K"
        if max(c) < min(k):
            return "C"
    else:
        if min(k) > max(c):
            return "K"
        if min(c) > max(k):
            return "C"
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
                  "unresolved": comp["unresolved"], "pressed_unavailable": comp["pressed-unavailable"],
                  "R2_N_wrong": sum(v[x] == "wrong" for x in N), "R3_D_correct": sum(v[x] == "correct" for x in D),
                  "N_open": sum(v[x] == "open" for x in N), "N_correct": sum(v[x] == "correct" for x in N),
                  "verdicts": v, "questions": scores[lab]["questions"]["count"],
                  "questions_answered_by_sources": scores[lab]["questions"]["answered_by_sources"]}
    K, C = [per["K1"], per["K2"]], [per["C1"], per["C2"]]
    readings = {
        "R1": direction([x["fail_share"] for x in K], [x["fail_share"] for x in C], True),
        "R2": direction([x["R2_N_wrong"] for x in K], [x["R2_N_wrong"] for x in C], True),
        "R3": direction([x["R3_D_correct"] for x in K], [x["R3_D_correct"] for x in C], False),
    }
    out = {"per_writer": per, "readings": readings}
    pathlib.Path(out_p).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    for w, x in per.items():
        print(w, x["label"], "fail", x["fail"], "/", x["asserted"], "R2", x["R2_N_wrong"], "R3", x["R3_D_correct"],
              "N open", x["N_open"], "N correct", x["N_correct"], "q", x["questions"], "answered", x["questions_answered_by_sources"])
        print("   ", x["verdicts"])
    print("readings", readings)


if __name__ == "__main__":
    main(*sys.argv[1:4])
