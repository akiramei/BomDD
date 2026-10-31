"""Write M1'-M9' (definitions section 5): the nine meanings on N2a, in N2a's own representation (run from this folder)."""
import copy
import json
import pathlib

OUT = pathlib.Path("specimens")
N2A = json.loads((OUT / "N2a.json").read_text(encoding="utf-8"))


def mutant(mid, meaning, case, slot, expected, mutated, how, change):
    d = copy.deepcopy(N2A)
    d.pop("notes", None)
    change(d)
    d["meta"] = {"id": mid, "base": "N2a", "meaning": meaning, "named_case": case, "slot": slot,
                 "expected": expected, "mutant": mutated, "how": how}
    return d


def m3(d):
    d["state"]["prevFps"] = "src"
    for b in d["buttons"].values():
        b["prevFps"] = "outputFps"
    d["observe"]["V1"] = "num(prevFps, 2) + ' fps'"


MUTANTS = [
    mutant("M1p", "the 60 button keeps the previous value", "25|none|60", "V1", "60 fps", "25 fps",
           "buttons.60: outputFps = outputFps", lambda d: d["buttons"].update({"60": {"outputFps": "outputFps"}})),
    mutant("M2p", "Source keeps the previous value", "25|60|Source", "V1", "25 fps", "60 fps",
           "buttons.Source: outputFps = outputFps", lambda d: d["buttons"].update({"Source": {"outputFps": "outputFps"}})),
    mutant("M3p", "the summary text shows the value before the last press", "25|24|60", "V1", "60 fps", "24 fps",
           "a state prevFps set to outputFps by every button; V1 from prevFps", m3),
    mutant("M4p", "the summary text shows the source rate", "25|none|24", "V1", "24 fps", "25 fps",
           "V1 = fpsText (the clip's own text, the tooltip's number)", lambda d: d["observe"].update({"V1": "fpsText"})),
    mutant("M5p", "the 120 button is not defined", "25|none|120", "undefined", None, None,
           "buttons.120 removed", lambda d: d["buttons"].pop("120")),
    mutant("M6p", "Source sets a constant 30", "25|60|Source", "V1", "25 fps", "30 fps",
           "buttons.Source: outputFps = 30", lambda d: d["buttons"].update({"Source": {"outputFps": "30"}})),
    mutant("M7p", "Source shown selected only on exact equality", "29.97|none|30", "V2", True, False,
           "derived.fpsSourceActive = outputFps == src",
           lambda d: d["derived"].update({"fpsSourceActive": "outputFps == src"})),
    mutant("M8p", "the note shown when the output exceeds the source, no margin", "29.97|none|30", "V7", False, True,
           "derived.fpsUpsampling = outputFps > src", lambda d: d["derived"].update({"fpsUpsampling": "outputFps > src"})),
    mutant("M9p", "the text rounded to whole numbers", "29.97|opened", "V1", "29.97 fps", "30 fps",
           "derived.outputFpsText = num(outputFps, 0) (in N2a this also feeds V3-V6)",
           lambda d: d["derived"].update({"outputFpsText": "num(outputFps, 0)"})),
]

for d in MUTANTS:
    (OUT / f"{d['meta']['id']}.json").write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8",
                                                 newline="\n")
print(len(MUTANTS), "mutants of N2a written; none NA")
