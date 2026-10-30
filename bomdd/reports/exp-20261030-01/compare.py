"""EXP-20261030-01 - count the two classifiers' files by definitions.md section 6; writes summary.json.

Refuses (exit 2) a missing file, an item missing or duplicated, or a value outside the vocabulary - an unreadable input is not a count.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRODUCTS = ["ViewTube", "ViewPrism2", "MoviePad-Remake"]
GENERAL = ["ViewTube", "ViewPrism2"]
OUT_REASONS = {"impl", "derived", "feature", "process", "unclear"}
KINDS = {"missing", "wrong", "ambiguous", "contradictory"}


def fail(msg):
    sys.stderr.write(f"UNMEASURABLE: {msg}\n")
    sys.exit(2)


def load(letter, product, expected):
    path = HERE / f"classifier-{letter}-{product}.json"
    if not path.exists():
        fail(f"{path.name} missing")
    rows = json.loads(path.read_text(encoding="utf-8"))["items"]
    by_id = {}
    for r in rows:
        if r["id"] in by_id:
            fail(f"{path.name}: {r['id']} twice")
        by_id[r["id"]] = r
        if r["screen"] == "OUT":
            if r.get("out_reason") not in OUT_REASONS or r.get("classes"):
                fail(f"{path.name}: {r['id']} OUT with out_reason {r.get('out_reason')!r} classes {r.get('classes')!r}")
        elif r["screen"] == "IN":
            c = r.get("classes") or []
            ok = c in (["N"], ["U"]) or (c and set(c) <= {"K1", "K2", "K3"})
            if not ok or r.get("kind") not in KINDS:
                fail(f"{path.name}: {r['id']} IN with classes {c!r} kind {r.get('kind')!r}")
        else:
            fail(f"{path.name}: {r['id']} screen {r['screen']!r}")
    if set(by_id) != set(expected):
        fail(f"{path.name}: items differ from items.json (missing {sorted(set(expected) - set(by_id))[:5]}, "
             f"extra {sorted(set(by_id) - set(expected))[:5]})")
    return by_id


def structural(r):
    return r["screen"] == "IN" and bool({"K1", "K2"} & set(r["classes"]))


def pct(n, d):
    return None if d == 0 else round(100 * n / d, 1)


def main():
    items = json.loads((HERE / "items.json").read_text(encoding="utf-8"))["items"]
    summary, disagreements = {}, []
    for p in PRODUCTS:
        ids = [i["id"] for i in items if i["product"] == p]
        a, b = load("a", p, ids), load("b", p, ids)
        both_in = [i for i in ids if a[i]["screen"] == "IN" and b[i]["screen"] == "IN"]
        s_both = sum(structural(a[i]) and structural(b[i]) for i in both_in)
        s_either = sum(structural(a[i]) or structural(b[i]) for i in both_in)
        split = [i for i in both_in if structural(a[i]) != structural(b[i])]
        per = {}
        for letter, d in (("a", a), ("b", b)):
            ins = [i for i in ids if d[i]["screen"] == "IN"]
            per[letter] = {
                "IN": len(ins), "OUT": len(ids) - len(ins),
                "out_reasons": {k: sum(d[i].get("out_reason") == k for i in ids) for k in sorted(OUT_REASONS)},
                **{k: sum(k in d[i]["classes"] for i in ins) for k in ("K1", "K2", "K3", "N", "U")},
                "kinds": {k: sum(d[i].get("kind") == k for i in ins) for k in sorted(KINDS)},
            }
        summary[p] = {
            "items": len(ids), "screen_agree": sum(a[i]["screen"] == b[i]["screen"] for i in ids),
            "in_both": len(both_in), "structural_both": s_both, "structural_either": s_either,
            "S_both_pct": pct(s_both, len(both_in)), "S_either_pct": pct(s_either, len(both_in)),
            "K1_both": sum("K1" in a[i]["classes"] and "K1" in b[i]["classes"] for i in both_in),
            "K3_both": sum("K3" in a[i]["classes"] and "K3" in b[i]["classes"] for i in both_in),
            "structural_split": len(split),
            "no_claim_rule4": len(both_in) > 0 and len(split) * 3 > len(both_in),
            "per_classifier": per,
        }
        for i in ids:
            if a[i]["screen"] != b[i]["screen"] or (i in both_in and set(a[i]["classes"]) != set(b[i]["classes"])):
                disagreements.append({"id": i, "a": [a[i]["screen"], a[i]["classes"], a[i]["reason"]],
                                      "b": [b[i]["screen"], b[i]["classes"], b[i]["reason"]]})
    g = [summary[p] for p in GENERAL]
    if any(s["S_both_pct"] is not None and s["S_both_pct"] >= 25 and not s["no_claim_rule4"] for s in g):
        reading = "trial"
    elif all(s["S_either_pct"] is not None and s["S_either_pct"] <= 10 and not s["no_claim_rule4"] for s in g):
        reading = "not-useful-here"
    else:
        reading = "no-claim"
    k1 = sum(s["K1_both"] for s in g)
    out = {"reading_rule2": reading, "K1_both_general": k1, "rule3_connection_rules_do_not_pay": k1 <= 1,
           "products": summary, "disagreements": disagreements}
    (HERE / "summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    sys.stdout.write(json.dumps({k: out[k] for k in ("reading_rule2", "K1_both_general")}) + "\n")
    for p, s in summary.items():
        sys.stdout.write(f"{p}: in_both {s['in_both']} S_both {s['S_both_pct']} S_either {s['S_either_pct']} "
                         f"split {s['structural_split']} screen_agree {s['screen_agree']}/{s['items']}\n")


if __name__ == "__main__":
    main()
