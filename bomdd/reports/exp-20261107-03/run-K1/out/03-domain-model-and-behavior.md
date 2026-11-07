# 03 ドメインモデル候補と部分的な振る舞い契約

対象: 出力フレームレート。原製品 MoviePad 126eae9。要求 ID は 02 を参照。
今回の対象外と未検証: 書き出しファイルの実レート(NOT_RUN)、実機の画面表示(NOT_RUN・examples.json は未実行)。

## 1. ドメインモデル候補

| 概念 | 識別・値 | 状態 / 派生 | 根拠 | 区分 |
|---|---|---|---|---|
| 元動画(Clip) | ファイル 1 本 | `SourceFps`(double・avg_frame_rate 由来)、`IsVariableFrameRate`、コーデック | Models/ClipInfo.cs:9-24, MediaProbe.cs:88-98 | SOURCE_EXPLICIT |
| 出力設定(OutputSettings) | 開いている動画に 1 つ | `OutFps`(double)。ほかに出力幅・高さ・アスペクト維持 | VM:123-126 | SOURCE_EXPLICIT(まとまりは設計候補) |
| 編集文書(DocumentState) | 区間・トリム | **OutFps を含まない** | Models/DocumentState.cs(OutFps の参照なし) | SOURCE_EXPLICIT |
| 履歴(History) | DocumentState のスナップショット列 | OutFps を含まない | VM:680-712 | SOURCE_DERIVED |
| 保存状態(Edited) | 真偽 | 編集・設定変更で true、開く/書き出し成功で false | VM:344, 538, 856, 1068 | SOURCE_EXPLICIT |
| 書き出し計画(ExportPlan) | 書き出し要求ごと | `fpsChange = |OutFps − SourceFps| > 0.05`、`NeedsRerate`、`CanStreamCopy` | Exp:470-484 | SOURCE_EXPLICIT |
| 出力クロック(ExportClock) | 書き出し要求ごと | `OutRate` = OutFps を q∈{1,1001} の有理数として認識(できなければ二進厳密値)。VFR では作らない | ExportClock.cs:96-106, 156-165 | SOURCE_EXPLICIT |

派生表示(状態ではない): `OutFpsText`(0.## 表記)、`FpsSourceActive`、`FpsUpsampling`、`FpsText`(元 fps 表記)、`FpsSourceTip`、`CanFastExport`。
画面の表示値は状態からの派生であり、OutFps の生の値がどこかに常時出る必要はない(02 §1 末尾)。

設計上の注意(候補であり唯一の分割ではない):

- 同じ「ソース」選択表示でも、内部の OutFps が元 fps と完全に同じとは限らない(差 < 0.05 の範囲)。例: 元 29.97002997 で「30」を押すと「ソース」も選択表示のまま、OutFps は 30。
  見た目が同じでも書き出し結果(再エンコード時の `-r 30/1`)が異なるので、再実装では「ソース指定」と「数値指定」を値として区別できる表現が必要になりうる(Q-01 の回答次第)。
  原製品は区別していない(どちらも double 1 個)。
- OutFps を DocumentState に入れるか、履歴に乗せるかは外部動作を変える(Undo で戻るかどうか)。原製品は「入れない」。再実装はこれに従う(正本=原製品)。

委任範囲で決めた設計選択(DESIGN_CHOICE、外部動作を変えない):

- D-01 再実装の内部では OutFps を「出力設定」概念として DocumentState と分けて扱う案を採る。理由: 原製品の外部動作(Undo 非対象・開くとリセット)に直接対応し、履歴の対象を変えないため。
- D-02 比較の許容 0.05 と表記 `0.##` は外部動作(選択表示・コピー可否)に効くため、内部選択ではなく契約側に置く(下記 INV)。

## 2. 振る舞い契約

| 契約ID | 前提・履歴 | 操作と入力 | 実行条件 | 更新・保持 | 結果種別 | 観測・成立時点 | 根拠と未決 |
|---|---|---|---|---|---|---|---|
| B-01 | なし | 動画を開く(元 fps = F) | 解析成功 | OutFps := F、Edited := false、履歴クリア、FastExport := false | 成功 | 「ソース」選択表示、数値プリセットは `0.##(F)` と一致するものだけ選択表示、注記なし、「保存済み」 | R-01, R-15。VM:526-559 |
| B-02 | 動画あり | プリセット n ∈ {24,30,60,120} を押す | なし(常に押せる) | OutFps := n、Edited := true。履歴は変えない | 成功(値が同じでも成功・Edited は true) | 「n」選択表示、「ソース」は \|n−F\|<0.05 なら選択表示、注記は n > F+0.05 で表示、「未保存の変更」 | R-02, R-04〜R-09。Q-02 |
| B-03 | 動画あり | 「ソース」を押す | なし | OutFps := F、Edited := true | 成功 | 「ソース」選択表示、注記なし、「未保存の変更」 | R-03, R-08 |
| B-04 | 任意 | 元に戻す / やり直す | CanUndo / CanRedo | DocumentState だけ差し替え。**OutFps・Edited は保持** | 成功(履歴が無ければ何もしない) | fps の選択表示・ダイアログの「フレームレート」は変わらない | R-09。VM:691-712。保持の根拠= Undo/Redo が OutFps・Edited を代入しない |
| B-05 | 動画あり | 「書き出し」を押す | なし | ShowExport := true | 成功 | サマリ「フレームレート」= `0.##(OutFps) fps`。\|OutFps−F\|≥0.05 なら「高速・無劣化（コピー）」は隠れる | R-10, R-12 |
| B-06 | ダイアログ表示中 | 書き出す(再エンコード) | 保存先選択・ffmpeg 成功 | Edited := false。OutFps 保持 | 成功 / 業務エラー(ffmpeg 失敗は ExportStatus に生エラー) | 出力ファイルは `-r p/q` の CFR(速度・fps 変更・VFR のとき fps フィルタ) | R-16, R-19。**NOT_RUN**(実行禁止) |
| B-07 | ダイアログ表示中・コピー有効 | 書き出す(コピー) | CanStreamCopy | ストリームコピー。fps 引数なし | 成功 | 出力は元のタイミングのまま | Exp:183-198。**NOT_RUN** |
| B-08 | 動画あり | 1 フレーム送り / 戻し | なし | Playhead := clamp((round(p·F)±1)/F, TrimStart, TrimEnd) | 成功 | タイムコードは F 基準で ±1 フレーム。**OutFps は関与しない** | R-18。VM:640-644 |

拒否・無視: fps プリセットに拒否経路は無い(常に押せる・値は固定文字列から解釈。解釈失敗時は現在値を保持 VM:854 だが、UI からは起きない)。

## 3. 守る条件

| 条件ID | 条件と適用範囲 | いつ | 根拠 | 未決 |
|---|---|---|---|---|
| INV-01 | 「ソース」の選択表示 ⇔ \|OutFps − F\| < 0.05 | 常時(派生) | VM:460 | Q-01(許容を引き継ぐか) |
| INV-02 | 数値プリセット n の選択表示 ⇔ `0.##(OutFps)` = "n" | 常時(派生) | VM:459 + EqualsConverter | — |
| INV-03 | 注記の表示 ⇔ OutFps > F + 0.05 | 常時(派生) | VM:461 | — |
| INV-04 | \|OutFps − F\| > 0.05 ⇒ コピー不可(トグル非表示) | 常時(派生) | Exp:473, 482 | Q-01 |
| INV-05 | OutFps は Undo/Redo で変わらない | 常時 | VM:691-712 | — |
| INV-06 | 1 フレームの単位・タイムコードは元 fps F | 常時 | VM:305, 643 | — |

INV-01 と INV-04 の境界: 差がちょうど 0.05 のとき、INV-01 は偽(< 0.05)、INV-04 の fpsChange も偽(> 0.05)。
つまり差 0.05 ちょうどでは「ソース」は選択表示されないがコピーは妨げない。プリセット値と実在のレートでこの差が出る組はまず無いが、記録しておく(SOURCE_DERIVED)。

## 4. 未決が影響する範囲

- Q-01(04 参照): INV-01・INV-04・B-02・B-05・B-07 とドメインの「ソース指定/数値指定の区別」。30 fps 固定の開始状態の例(examples.json)には影響しない。
- Q-02: B-02 の Edited 更新だけ。ほかは進められる。
