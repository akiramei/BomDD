# scenarios.json generator. pass 1: placeholder state "ANY"; pass 2: states from certify.json points.
import json, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
TB, IN, TR, TL, TT, EX, AB, MW = ("ToolbarView", "InspectorView", "TransportView", "TimelineView",
                                  "TitleBarView", "ExportDialogView", "AboutDialogView", "MainWindow")
NOFF = {"set": "ShowFfmpegSetup", "value": False}
def ph(t): return {"set": "Playhead", "value": t}

# (id, title, goal, flow, setup, [(action, surface, harness_no)])
SC = [
 ("UC-01", "再生ヘッド位置で区間を分割し、後半の速度を変える", "区間の途中から速度を変える", "main",
  [NOFF, ph(20)], [("Split", TB), ("ApplySpeedPreset:0.5", IN)]),
 ("UC-02", "分割を取り消し、やり直す", "誤った分割を戻し、また適用する", "alternate",
  [NOFF, ph(20)], [("Split", TB), ("Undo", TB), ("Redo", TB)]),
 ("UC-03", "分割した境界を前の区間と結合して戻す", "分割を境界削除で取り消し、結合も元に戻す", "alternate",
  [NOFF, ph(20)], [("Split", TB), ("DeleteSelectedBoundary", TB), ("Undo", TB)]),
 ("UC-04", "既存区間の速度を等速に戻し、取り消す", "0.5x 区間の速度を変え、変更を戻す", "main",
  [NOFF, ph(120)], [("ApplySpeedPreset:1", IN), ("Undo", TB)]),
 ("UC-05", "再生ヘッド位置をトリム開始(In)にして、取り消す", "動画の頭を詰める", "main",
  [NOFF, ph(10)], [("SetTrimIn", TB), ("Undo", TB)]),
 ("UC-06", "再生ヘッド位置をトリム終了(Out)にして、取り消す", "動画の終わりを詰める", "main",
  [NOFF, ph(120)], [("SetTrimOut", TB), ("Undo", TB)]),
 ("UC-07", "区間をミュートし、100% に戻す", "区間の音を消す・戻す", "main",
  [NOFF], [("ApplyVolumePreset:0", IN), ("ApplyVolumePreset:100", IN)]),
 ("UC-08", "取り消した後に別の編集をすると、やり直しが消える", "取り消しの後に別の速度を選ぶ", "alternate",
  [NOFF], [("ApplySpeedPreset:2", IN), ("Undo", TB), ("ApplySpeedPreset:0.5", IN)]),
 ("UC-09", "出力解像度を 50% にし、リセットで元に戻す", "出力サイズを小さくする・戻す", "main",
  [NOFF], [("Scale:0.5", IN), ("Scale:1", IN)]),
 ("UC-10", "出力フレームレートを 60fps にし、ソースに戻す", "出力 fps を変える・戻す", "main",
  [NOFF], [("SetFps:60", IN), ("SetFps:source", IN)]),
 ("UC-11", "書き出しダイアログを開いてキャンセルする", "書き出し設定を見て、やめる", "alternate",
  [NOFF], [("ShowExportDialog", TB), ("CloseExport", EX)]),
 ("UC-12", "解像度を 75% にして書き出す", "編集結果を動画ファイルに書き出す(実ファイルを開いているとき。サンプルのままでは保存先を聞かずエラー表示になりダイアログは閉じない)", "main",
  [NOFF], [("Scale:0.75", IN), ("ShowExportDialog", TB), ("ConfirmExport", EX, True)]),
 ("UC-13", "再生して一時停止する", "プレビューを再生して止める", "main",
  [NOFF], [("TogglePlay", TR), ("TogglePlay", TR)]),
 ("UC-14", "再生中にフレーム送りで止める", "再生を止める別の入口(コマ送り)", "alternate",
  [NOFF], [("TogglePlay", TR), ("StepForward", TR), ("StepBack", TR)]),
 ("UC-15", "末尾へ移動してから先頭へ戻る", "再生ヘッドを端へ移動する", "main",
  [NOFF], [("ToEnd", TR), ("ToStart", TR)]),
 ("UC-16", "境界を削除して隣の区間と結合し、取り消し・やり直す", "区間を一つにまとめる", "main",
  [NOFF, ph(50)], [("DeleteSelectedBoundary", TB), ("Undo", TB), ("Redo", TB)]),
 ("UC-17", "About を開いて閉じる", "バージョンとライセンスを確認する", "main",
  [NOFF], [("OpenAbout", TT), ("CloseAbout", AB)]),
 ("UC-18", "ffmpeg の取得を後回しにして、プレビューを再生する", "初回起動の案内を閉じて作業を始める", "alternate",
  [{"set": "ShowFfmpegSetup", "value": True}], [("DismissFfmpegSetup", MW), ("TogglePlay", TR)]),
 ("UC-19", "ffmpeg を取得する", "初回起動の案内から ffmpeg を取得する", "main",
  [{"set": "ShowFfmpegSetup", "value": True}], [("InstallFfmpeg", MW, True)]),
 ("UC-20", "読み込みエラーの表示を閉じて、別のファイルを開き直す", "開けなかったファイルのエラーから戻る", "alternate",
  [NOFF, {"set": "LoadError", "value": "読み込みに失敗しました"}], [("ClearError", MW), ("Open", TB, True)]),
 ("UC-21", "作業中に別の動画ファイルを開く", "編集する動画を読み込む(読み込むと履歴と出力解像度は元に戻り、全長 1 区間・再生ヘッド 0 秒から始まる)", "main",
  [NOFF], [("Scale:0.5", IN), ("Open", TB, True)]),
 ("UC-22", "タイムラインを拡大して縮小する", "細かい位置を見る・全体に戻す", "main",
  [NOFF], [("ZoomIn", TL), ("ZoomOut", TL)]),
]

def build(states, assign):
    out = []
    for i, (sid, title, goal, flow, setup, steps) in enumerate(SC):
        st = []
        for k, s in enumerate(steps):
            a, surf = s[0], s[1]
            pin, pex = assign(sid, k)
            d = {"in": pin, "action": a, "surface": surf, "expect": pex}
            if len(s) > 2 and s[2]: d["harness"] = "no"
            st.append(d)
        out.append({"id": sid, "title": title, "goal": goal, "flow": flow, "setup": setup, "steps": st})
    return {"states": states, "scenarios": out}

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "probe":
        doc = build([{"id": "ANY", "name": "任意", "predicate": {}}], lambda s, k: ("ANY", "ANY"))
    else:
        doc = json.load(open(os.path.join(HERE, "states_assign.json"), encoding="utf-8"))
        doc = build(doc["states"], lambda s, k: tuple(doc["assign"][s][k]))
    json.dump(doc, open(os.path.join(HERE, "scenarios.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
