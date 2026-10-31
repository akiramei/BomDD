"""Write N1 and M1-M9 (definitions section 5) into specimens/. Each mutant changes one meaning of N1 and names its case."""
import copy
import json
import pathlib

OUT = pathlib.Path("specimens")
OUT.mkdir(exist_ok=True)

N1 = {
    "meta": {"id": "N1", "what": "direct: the settable value 'out' is read by every slot"},
    "state": {"out": "src"},
    "buttons": {"Source": {"out": "src"}, "24": {"out": "24"}, "30": {"out": "30"}, "60": {"out": "60"},
                "120": {"out": "120"}},
    "derived": {"text": "num(out, 2)"},
    "observe": {"V1": "text + ' fps'", "V2": "abs(out - src) < 0.05", "V3": "text == '24'", "V4": "text == '30'",
                "V5": "text == '60'", "V6": "text == '120'", "V7": "out > src + 0.05",
                "V8": "'Same as source (' + num(src, 2) + ' fps)'"},
}


def mutant(mid, meaning, case, slot, expected, mutated, change):
    d = copy.deepcopy(N1)
    change(d)
    d["meta"] = {"id": mid, "base": "N1", "meaning": meaning, "named_case": case, "slot": slot,
                 "expected": expected, "mutant": mutated}
    return d


def m3(d):
    d["state"]["prev"] = "src"
    for b in d["buttons"].values():
        b["prev"] = "out"
    d["observe"]["V1"] = "num(prev, 2) + ' fps'"


MUTANTS = [
    mutant("M1", "the 60 button keeps the previous value", "25|none|60", "V1", "60 fps", "25 fps",
           lambda d: d["buttons"].update({"60": {"out": "out"}})),
    mutant("M2", "Source keeps the previous value", "25|60|Source", "V1", "25 fps", "60 fps",
           lambda d: d["buttons"].update({"Source": {"out": "out"}})),
    mutant("M3", "the summary text shows the value before the last press", "25|24|60", "V1", "60 fps", "24 fps", m3),
    mutant("M4", "the summary text shows the source rate", "25|none|24", "V1", "24 fps", "25 fps",
           lambda d: d["observe"].update({"V1": "num(src, 2) + ' fps'"})),
    mutant("M5", "the 120 button is not defined", "25|none|120", "undefined", None, None,
           lambda d: d["buttons"].pop("120")),
    mutant("M6", "Source sets a constant 30", "25|60|Source", "V1", "25 fps", "30 fps",
           lambda d: d["buttons"].update({"Source": {"out": "30"}})),
    mutant("M7", "Source shown selected only on exact equality", "29.97|none|30", "V2", True, False,
           lambda d: d["observe"].update({"V2": "out == src"})),
    mutant("M8", "the note shown when the output exceeds the source, no margin", "29.97|none|30", "V7", False, True,
           lambda d: d["observe"].update({"V7": "out > src"})),
    mutant("M9", "the text rounded to whole numbers", "29.97|opened", "V1", "29.97 fps", "30 fps",
           lambda d: d["observe"].update({"V1": "num(out, 0) + ' fps'"})),
]

for d in [N1, *MUTANTS]:
    (OUT / f"{d['meta']['id']}.json").write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8",
                                                 newline="\n")
print(len(MUTANTS) + 1, "specimens written")
