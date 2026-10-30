# Derive states from a probe run's certify.json points (15 screen variables + Playing).
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
V15 = "CanDeleteBoundary CanRedo CanSetTrimIn CanSetTrimOut CanSplit CanUndo FfmpegInstalling HasClip HasLoadError HasSelection IsExporting ShowAbout ShowExport ShowFfmpegSetup ShowReset".split()
PLAYING = {("UC-13", 1), ("UC-14", 1), ("UC-18", 2)}  # after the first TogglePlay
# document shape per point (read from DocumentState/Sample; checked by the harness when the predicate is evaluated)
RC = {"UC-01": [4, 5, 5], "UC-02": [4, 5, 4, 5], "UC-03": [4, 5, 4, 5], "UC-16": [4, 3, 4, 3]}
TS = {"UC-05": [6, 10, 6]}
TE = {"UC-06": [132, 120, 132]}
PH = {"UC-01": [20]*3, "UC-02": [20]*4, "UC-03": [20]*4, "UC-04": [120]*3, "UC-05": [10]*3, "UC-06": [120]*3,
      "UC-14": [6, 6, 181/30, 6], "UC-15": [6, 132, 6], "UC-16": [50]*4}
def extra(s, k):
    d = {"RegionCount": RC.get(s, [4] * 9)[k], "TrimStart": TS.get(s, [6] * 9)[k], "TrimEnd": TE.get(s, [132] * 9)[k],
         "Playhead": PH.get(s, [6] * 9)[k]}
    return d

cert = json.load(open(os.path.join(HERE, "certify.json"), encoding="utf-8"))
pts = {}
for p in cert["points"]:
    pts[(p["Scenario"], p["K"])] = p["Values"]

def label(pred):
    t = lambda k: pred.get(k) is True
    shape = "(区間 %d・トリム %g〜%s 秒・再生ヘッド %.4g 秒)" % (pred["RegionCount"], pred["TrimStart"], pred.get("TrimEnd", "動画の長さ"), pred["Playhead"])
    if t("ShowFfmpegSetup"): return "ffmpeg 取得の案内" + ("(取得中)" if t("FfmpegInstalling") else "")
    under = dict(pred); under.update(ShowExport=False, ShowAbout=False, IsExporting=False)
    if t("ShowExport"): return "書き出しダイアログ" + ("(書き出し中)" if t("IsExporting") else "") + " / 背後= " + label(under)
    if t("ShowAbout"): return "About ダイアログ / 背後= " + label(under)
    parts = ["編集画面" + shape]
    if t("HasLoadError"): parts.append("読み込みエラー表示")
    if pred.get("Playing"): parts.append("再生中")
    ok = [n for k, n in [("CanSplit", "分割可"), ("CanDeleteBoundary", "結合可"), ("CanSetTrimIn", "In 可"),
                         ("CanSetTrimOut", "Out 可"), ("CanUndo", "取り消し可"), ("CanRedo", "やり直し可"),
                         ("ShowReset", "解像度変更あり")] if t(k)]
    parts.append("・".join(ok) if ok else "編集ボタンすべて無効")
    return ": ".join([parts[0], "・".join(parts[1:])])

states, ids, assign = [], {}, {}
order = sorted(pts)
sc_ids = sorted({s for s, _ in pts})
for s in sc_ids:
    ks = sorted(k for ss, k in pts if ss == s)
    seq = []
    for k in ks:
        v = pts[(s, k)]
        pred = {n: (v[n] == "True") for n in V15}
        pred["Playing"] = (s, k) in PLAYING
        pred.update(extra(s, k))
        key = json.dumps(pred, sort_keys=True)
        if key not in ids:
            sid = "ST-%02d" % (len(ids) + 1)
            ids[key] = sid
            states.append({"id": sid, "name": label(pred), "predicate": pred})
        seq.append(ids[key])
    assign[s] = seq

# expected landing of the unexecuted steps on success (read from the source, not run):
# ConfirmExport success -> ShowExport=false; InstallFfmpeg success -> ShowFfmpegSetup=false;
# Open success -> LoadClip resets history/selection (same flags as startup with the sample).
NOEXEC = {"ConfirmExport": {"ShowExport": False}, "InstallFfmpeg": {"ShowFfmpegSetup": False}, "Open": {"RegionCount": 1, "TrimStart": 0, "Playhead": 0, "TrimEnd": None, "HasLoadError": False,
                  "ShowReset": False, "CanUndo": False, "CanRedo": False, "Playing": False, "CanSplit": False,
                  "CanDeleteBoundary": False, "CanSetTrimIn": True, "CanSetTrimOut": False}}
# per-step (in, expect); scenarios ending on a harness:no step have one fewer point after it
gen = json.load(open(os.path.join(HERE, "scenarios.json"), encoding="utf-8"))
out = {}
for sc in gen["scenarios"]:
    seq = assign[sc["id"]]
    pairs = []
    for i, st in enumerate(sc["steps"]):
        pin = seq[i]
        pex = seq[i + 1] if i + 1 < len(seq) else pin
        if st.get("harness") == "no":
            pred = dict(next(x for x in states if x["id"] == pin)["predicate"])
            pred.update(NOEXEC[st["action"]])
            pred = {a: b for a, b in pred.items() if b is not None}
            key = json.dumps(pred, sort_keys=True)
            if key not in ids:
                ids[key] = "ST-%02d" % (len(ids) + 1)
                states.append({"id": ids[key], "name": label(pred), "predicate": pred})
            pex = ids[key]
        pairs.append([pin, pex])
    out[sc["id"]] = pairs
# destination determinism check
dest = {}
for sc in gen["scenarios"]:
    for (pin, pex), st in zip(out[sc["id"]], sc["steps"]):
        if st.get("harness") == "no": continue
        dest.setdefault((pin, st["action"]), set()).add(pex)
for k, v in dest.items():
    if len(v) > 1: print("CONFLICT", k, v)
json.dump({"states": states, "assign": out}, open(os.path.join(HERE, "states_assign.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for s in states: print(s["id"], s["name"])
for k, v in out.items(): print(k, v)
