# Deriver A — final report (verbatim, Japanese as written)

Run 2026-10-31, 240.7 s, 10 tool uses; isolation (`../exp-20261030-04/isolation.py`): Read 4, Write 4, Bash 3, flags 0.
Model frozen: `domain-model.json` SHA-256 `4ce36104e1489e85dd644d6e0ce7b66876e488b27563b9d40026680bea4d7475`.
`fix_initials.py` is the deriver's own working script, kept as found.

---

domain-model.json を書き終えました。`python check_model.py domain-model.json` は ERROR なしで通ります(このツールが確かめるのは形と、根拠の id が実在するかだけです)。

ファイル: C:\Users\akira\AppData\Local\Temp\claude\C--Users-akira-source-repos-BomDD\c6a0cd2c-98cc-4b3c-bca7-73f54d8a43a0\scratchpad\exp06\derive-a\domain-model.json
同じフォルダに作業用の fix_initials.py も残っています(推測ではなく仕様から決まる初期値を、いくつかの属性に入れ直すために使ったものです)。

**数(check_model の出力)**
- 実体 18、属性 89、関係 47、questions 24
- 初期値を書いた属性 78。残り 11 は `unknown` で、11 件とも questions に挙げています。
- 実体の内訳: SourceFile, ClipInfo, Document, Region, Playhead, Selection, FrameGrid, History, OutputSettings, ExportFormat, ExportRequest, KeptPiece, ExportPlan, CopySpan, KeyframeLookup, ExportJob, OutputFile, FfmpegLocator
- 出力フレームレートの属性としてツールが拾ったもの: OutputSettings.fps, ExportRequest.outFps, CopySpan.canStreamCopy, OutputFile.frameRate

**迷ったところ(主なもの)**
1. 編集操作に渡す fps: SplitAt・MoveBoundary・MoveTrim は fps を引数に取りますが、渡すのがソースのレートか出力のレート(OutputSettings.fps)かが書かれていません。出力を 24 や 60 にしたとき、分割位置がどちらのグリッドに乗るかが決まりません。
2. 出力設定と書き出し依頼のつながり: OutputSettings の幅・高さ・fps が ExportRequest の outWidth・outHeight・outFps になることは文脈から読めるだけで、明記はありません。このため依頼側の初期値は `unknown` にしました。既定の形式と出力先フォルダも書かれていません。
3. History の範囲: 初期状態(空かどうか)と Clear の呼ばれる時が書かれていません。出力設定の変更が取り消しの対象か、どの操作が Snapshot を取るか(拒否された操作でも取るか)、どれが「連続ドラッグ」に当たるかも不明です。
4. 仕様の外にある状態: 再生位置と選択は、初期値も、それを変える操作も、持ち主も書かれていません。分割の newId の採番規則もありません。
5. keepAspect の抜け: もう一方の寸法を導出するとき、その値に [16, 7680] / [16, 4320] の clamp がかかりません。初期サイズは奇数のままの場合があります。ToggleKeepAspect を off にしたときの効果も書かれていません。
6. 要求と仕様の文面の食い違い(仕様が意図した差と書いているものも含む):
   - SetFps は正で有限なら任意の値を受けるが、REQ-013 は 24/30/60/120 とする。
   - SplitAt と CanSplitAt は、ちょうど 0.5 s のところで判定が分かれる。
   - 併合で、どれも残らない Document ができる(INV-005)。REQ-010 の「全部の除外は拒否」と文面上合わない。
   - 誤りの判定順で FfmpegUnavailable が空編集の誤りより先に来る。REQ-018 は「空の出力は ffmpeg 実行前に拒否」とする。
   - コピー時の進捗の分母がキーフレームからの導入部を含み、REQ-018 の「出力長」とずれる。
   - ExportJob の状態遷移に、ffmpeg 実行前の拒否が含まれていない。

どれも推測で埋めず、questions に根拠の id をつけて書いています。
