# 要求・ユースケース・シナリオ — 出力フレームレート

対象・版: MoviePad 126eae9 の出力フレームレート機能(再実装のための上流整理)
原資料の正本: `moviepad/`(入力一覧 01 の SRC-*)
今回の整理: 下書き(AI 一人の自己点検のみ。専門家確認なし)
専門家が実際に確認した範囲: なし

由来区分は BehaviorForge 共通契約 §2(SOURCE_EXPLICIT / SOURCE_DERIVED / DESIGN_CHOICE / PROPOSAL / UNRESOLVED / CONFLICT)。
**注意**: 振る舞いの正本はコードなので、コードから読み取った振る舞いは「原製品の事実」だが、**それが業務上の意図か偶然かは別**。コードで決まる事実は SOURCE_DERIVED(コード位置付き)とし、手引き・画面文言に明記があるものだけ SOURCE_EXPLICIT とする。

## 利用目的と範囲

利用者と達成したいこと: 動画を書き出す利用者が、書き出し動画のフレームレートを元動画と同じ、または 24 / 30 / 60 / 120 fps から選ぶ(SRC-QS §4.6)。
今回扱うこと: 出力 fps の選択・表示・既定値・注記・書き出しダイアログ表示・高速コピー可否への影響・未保存表示・Undo/Redo との関係・タイムコードとコマ送りとの関係・書き出し時の再サンプル(コード上)。
合意済みの対象外: なし(依頼は「関わるすべての振る舞い」)。ただし書き出し実行・実ファイル観測は今回の禁止範囲により机上のみ。
未確認の範囲: 出力ファイルの実 fps・フレーム数、VFR・29.97 素材の画面、英語 UI、任意値の入力手段の有無(実装上はプリセットのみ)。

## 要求

| 要求ID | 条件・必要な履歴 | 必要／禁止／未規定／選択可 | 操作と結果 | 観測と成立時点 | 根拠・由来区分 |
|---|---|---|---|---|---|
| R-01 | クリップ読込済み | 必要 | 出力 fps を「ソース / 24 / 30 / 60 / 120」の 5 つから選べる | インスペクター下部「出力フレームレート (fps)」に 5 ボタン。押した時点で選択が変わる | QUICKSTART.ja §4.6 / SOURCE_EXPLICIT。画面配置は InspectorView.axaml 86-105 / SOURCE_DERIVED |
| R-02 | 動画を開いた(読み込んだ)直後 | 必要 | 出力 fps はソースの fps になる(上限なし) | 読込完了時。30 fps 素材なら 30 | ResolutionTests 49-61・VM `LoadClip` 536 / SOURCE_DERIVED(テストの期待として明示)。手引きに既定値の記述は無い |
| R-03 | 出力 fps の値 | 必要 | 「ソース」ボタンは 出力fps とソースfps の差が 0.05 未満のとき強調。数値ボタン(24/30/60/120)は出力fps の表示文字列(小数 2 桁まで・末尾 0 除去)が ボタンの数字と**文字列一致**するとき強調 | 値が変わった時点。**30 fps 素材では「ソース」と「30」が同時に強調**される | VM 458-461、InspectorView 91-101、EqualsConverter / SOURCE_DERIVED。画像 10/11 でも両方強調 / SOURCE_EXPLICIT(外観) |
| R-04 | 出力 fps > ソース fps + 0.05 | 必要 | 注記「ソースより高いfpsはフレーム複製になります（画質は向上しません）。」を出す。それ以外は隠す | 値が変わった時点 | VM 461、InspectorView 103-104、Strings / SOURCE_DERIVED(文言は SOURCE_EXPLICIT) |
| R-05 | 書き出しダイアログ表示中 | 必要 | サマリ行「フレームレート」に `<出力fps表示> fps` を出す | ダイアログを開いている間 | ExportDialogView 111-114 / SOURCE_DERIVED。画像 11 / SOURCE_EXPLICIT(外観)。手引き §5 図説明「フレームレート…が表示されている」/ SOURCE_EXPLICIT |
| R-06 | 出力 fps とソース fps の差 > 0.05 | 必要 | 高速・無劣化(コピー)は不適格。ダイアログのトグルを隠す(他の条件が揃っていても) | ダイアログ表示中・値が変わった時点で再評価 | QUICKSTART.ja §5「出力解像度・fps を変えた」/ SOURCE_EXPLICIT。ExportPlan.Analyze 473-482・ExportPlanTests 46-51 / SOURCE_DERIVED |
| R-07 | 任意 | 必要(実装事実) | 出力 fps のボタンを押すと、値が変わらなくても「未保存の変更」になる | 押した時点。タイトルバー状態表示 | VM `SetFps` 850-857(`Edited = true` 無条件) / SOURCE_DERIVED。**意図かは UNRESOLVED(Q-2)** |
| R-08 | 任意 | 実装事実 | 出力 fps の変更は Undo/Redo 履歴に入らない。Undo/Redo で出力 fps は変わらない | 常時 | `_outFps` は DocumentState 外(VM 125)、`SetFps` は Snapshot しない / SOURCE_DERIVED。**意図かは UNRESOLVED(Q-1)** |
| R-09 | 任意 | 実装事実 | 出力 fps はタイムコード表示とコマ送り単位に影響しない(どちらもソース fps) | 常時 | VM `Fps`=Clip.Fps(305)、`PlayheadTc`(335)、`StepFrame`(640-644) / SOURCE_DERIVED。設計モックもコマ送りは FPS=30 定数 / SOURCE_EXPLICIT(モック) |
| R-10 | 再エンコード書き出し時 | 必要 | 出力動画は選んだ fps の固定フレームレートになる。区間速度の変更・fps 変更・VFR 素材のいずれかがあるときだけ再サンプルし、無ければ再サンプルしない | 書き出し完了時(外部出力) | 「区間速度は setpts、最終出力をこの fps へ再サンプル」VM 458 コメント、ExportPlan.NeedsRerate、FfmpegExporter 204-207・261-264、ExportClock.Build 156-221 / SOURCE_DERIVED。**実ファイル未観測(NOT_RUN)** |
| R-11 | CFR 素材の書き出し | 実装事実 | 出力フレーム数 = round_half_up(速度適用後の出力時間 × 出力 fps)。fps は p/q(q∈{1,1001})で表せるときその有理数として扱う | 書き出し時 | ExportClock 96-106・200 / SOURCE_DERIVED。今回の画面例では観測できない |
| R-12 | 別の動画を開く | 必要 | 出力 fps は新しいソースの fps に戻る(前の選択を持ち越さない) | 読込完了時 | VM `LoadClip` 536 / SOURCE_DERIVED |
| R-13 | 区間速度・トリム・除外・音量の編集 | 実装事実 | 出力 fps の選択は変わらない | 常時 | 編集系は DocumentState のみ更新 / SOURCE_DERIVED |
| R-14 | 「ソース」ボタンにポインタを置く | 必要 | ツールチップ「元動画と同じ（30 fps）」(ソース fps を表示) | ホバー中 | VM 443、Strings Inspector_FpsSourceTip / SOURCE_DERIVED |
| R-15 | ソース fps の表示 | 属性はあるが表示義務は未確定 | インスペクター「クリップ情報」の「フレームレート 30 fps」は**選択区間が無いときだけ**表示。実装では読込後つねに区間が選択されるため、通常操作では表示されない | — | InspectorView 247-270・DocumentState.ResolveSelection 85-91・VM 533 / SOURCE_DERIVED。モックは「未選択」状態を持つ / **CONFLICT(C-1)** |
| R-16 | 任意の数値入力 | 未規定 | プリセット以外の値(例 25, 50)を入力する手段は原製品に無い。禁止とも規定されていない | — | InspectorView にはプリセットのみ / SOURCE_DERIVED。再実装で追加するかは PROPOSAL 外(今回提案しない) |
| R-17 | 書き出し成功 | 実装事実 | 状態が「保存済み」に戻る(出力 fps の値は保持) | 書き出し成功時 | VM ConfirmExport 1065-1068 / SOURCE_DERIVED。NOT_RUN |
| R-18 | VFR 素材・書き出しダイアログで「高速・無劣化（コピー）」が ON かつコピー可能 | 必要(実装事実) | 注記「高速コピーは元のタイムスタンプを保持するため、VFR（可変フレームレート）素材は VFR のまま書き出されます（CFR には変換されません）。…」を出す。再エンコード時は VFR 素材でも出力 fps で CFR 化する | ダイアログ表示中 | VM `ShowVfrCopyNote` 234・ExportDialogView 90-91・ExportPlan.Analyze 474 / SOURCE_DERIVED(文言は SOURCE_EXPLICIT)。今回の前提(30fps 固定)では出ないため例にしていない: UNVERIFIED |

## ユースケース

UC-FPS-1・目的: 書き出し動画のフレームレートを選ぶ。
利用者: 動画を書き出す一般利用者。
開始条件: 動画を開いている(インスペクターは `HasClip` のときだけ表示)。
主経路: インスペクター下部「出力フレームレート (fps)」でボタンを押す → 押したボタン(と、値がソースと同じなら「ソース」)が強調 → ツールバー「書き出し」→ ダイアログの「フレームレート」行で確認 → 形式を選び「書き出す」。
代替経路: (a) ソースより高い値 → 注記が出る(拒否はしない)。(b) ソースと同じ値・「ソース」に戻す → 高速コピー可否は他の条件次第で元に戻る。(c) 別の動画を開く → ソース fps へ戻る。
失敗経路: 出力 fps に起因する拒否・エラーは原製品に無い(SOURCE_DERIVED: SetFps にガードなし)。書き出し失敗は ffmpeg 側(本機能の範囲外)。
終了条件・外部出力: 出力動画が選んだ fps の CFR(R-10、NOT_RUN)。
各経路に対応する原資料位置: 上表の根拠列。

## シナリオ

操作例は `examples.json`(EX-01〜EX-11)を正とする。要求との対応は 05 の「元資料に基づく具体例」と 06 の対応表を参照。

## 未決・矛盾

UNRESOLVED: Q-1(R-08)、Q-2(R-07)、Q-3(R-15)。CONFLICT: C-1(R-15 のモックと実装)、C-2(モックに出力fps 自体が無い)。詳細と問いは 06。
