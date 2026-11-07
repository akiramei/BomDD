"""EXP-20261107-03 tally (definitions.md section 7): R1 and R2 per writer and the fixed readings.

    python tally.py <scores.json> <scorer-key.json> <out.json>
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ITEMS = [f"T{i:02d}" for i in range(1, 17)]


def classes():
    """item -> class (a / b / c) and run flag, read from targets.md's table."""
    out = {}
    for line in (HERE / "targets.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (T\d\d) \|.*\| ([abc]) \| (yes|no) \|", line)
        if m:
            out[m.group(1)] = {"class": m.group(2), "run": m.group(3) == "yes"}
    if sorted(out) != ITEMS:
        sys.exit(f"targets.md table read {sorted(out)}")
    return out


def direction(k, c, higher_is_better):
    if higher_is_better:
        if min(k) > max(c):
            return "K"
        if min(c) > max(k):
            return "C"
    else:
        if max(k) < min(c):
            return "K"
        if max(c) < min(k):
            return "C"
    return None


def main(scores_p, key_p, out_p):
    scores = json.loads(pathlib.Path(scores_p).read_text(encoding="utf-8"))
    key = json.loads(pathlib.Path(key_p).read_text(encoding="utf-8"))
    cl = classes()
    per = {}
    for lab, w in key.items():
        v = {t: scores[lab]["items"][t]["verdict"] for t in ITEMS}
        bad = {t: x for t, x in v.items() if x not in ("correct", "wrong", "open", "absent")}
        if bad:
            sys.exit(f"{lab}: unknown verdicts {bad}")
        per[w] = {"label": lab,
                  "R1_correct": sum(x == "correct" for x in v.values()),
                  "R2_wrong": sum(x == "wrong" for x in v.values()),
                  "open": sum(x == "open" for x in v.values()),
                  "absent": sum(x == "absent" for x in v.values()),
                  "correct_by_class": {k: sum(v[t] == "correct" for t in ITEMS if cl[t]["class"] == k) for k in "abc"},
                  "verdicts": v,
                  "questions": scores[lab]["questions"]["count"],
                  "questions_answered_by_original": scores[lab]["questions"]["answered_by_original"]}
    K, C = [per["K1"], per["K2"]], [per["C1"], per["C2"]]
    readings = {"R1": direction([x["R1_correct"] for x in K], [x["R1_correct"] for x in C], True),
                "R2": direction([x["R2_wrong"] for x in K], [x["R2_wrong"] for x in C], False)}
    out = {"per_writer": per, "readings": readings,
           "class_sizes": {k: sum(cl[t]["class"] == k for t in ITEMS) for k in "abc"}}
    pathlib.Path(out_p).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    for w, x in per.items():
        print(w, x["label"], "correct", x["R1_correct"], "wrong", x["R2_wrong"], "open", x["open"], "absent", x["absent"],
              "by class", x["correct_by_class"], "q", x["questions"], "answered", x["questions_answered_by_original"])
        print("   ", x["verdicts"])
    print("readings", readings)


if __name__ == "__main__":
    main(*sys.argv[1:4])
