# 3. 振る舞い — 各操作の前後と画面

表示名は `cad/observations.json` の名前。起点は `cad/start-screen.json`:
区間 4 個・トリム 6〜132 秒・出力 142 秒・再生ヘッド 20 秒・選択中の区間 [6, 40]・速度 1・音量 100%・出力 30 fps 1920×1080・Undo/Redo とも使えない・保存済み。

出力の長さは、選択中の区間(先頭区間 [6, 40]、34 秒、1x)の項だけを差し替えて求める(他の 3 区間の速度は資料から分からないため、合計 142 から差し引きで扱う):
`output_length = 142 − 34 + (その区間の、トリム後の長さ) / 速度`(REQ-011)。

## 3.1 Undo / Redo そのもの

| 操作 | 使える条件 | 前 → 後(ドキュメント) | 画面 |
|---|---|---|---|
| Undo | 取り消し段数 > 0 | 1 段前の状態に戻る | `undo_enabled` は残り段数 > 0 か。`redo_enabled` = true。区間数・トリム・出力の長さ・選択中の区間の値・各編集ボタンの可否は戻した状態から計算し直す。 |
| Redo | やり直し段数 > 0 | 取り消した状態に進む | `undo_enabled` = true。`redo_enabled` は残り段数 > 0 か。値は進めた状態から計算し直す。 |

再生ヘッド・出力設定が Undo/Redo で戻るかは資料にない(Q-02・Q-01)。

## 3.2 起動直後からの各編集と、その Undo/Redo

| 編集(起動直後に 1 回) | 編集後の画面 | Undo 後 | Redo 後 | 根拠 |
|---|---|---|---|---|
| `Split`(20 秒) | `region_count` 5・出力 142(速度は両側に引き継ぐ)・`undo_enabled` true・`redo_enabled` false・`split_enabled` false・`trim_in_enabled` false | `region_count` 4・出力 142・`undo_enabled` false・`redo_enabled` true・`split_enabled` true・`trim_in_enabled` true | 編集後と同じ | REQ-003(境界の瞬間は後ろの区間に属す)・REQ-004(端から 0.5 秒未満は分割不可)・REQ-007(先頭区間の中でだけ In 可) |
| `SetTrimIn`(20 秒) | `trim_start` 20・`selected_start` 20・`selected_end` 40・出力 128・`split_enabled` false(再生ヘッドが先頭区間の開始と一致)・`trim_in_enabled` true | `trim_start` 6・`selected_start` 6・出力 142・`split_enabled` true・Undo 不可・Redo 可 | 編集後と同じ | REQ-007・REQ-011・REQ-004 |
| `ApplySpeedPreset:2` | `selected_speed` 2・出力 125 | `selected_speed` 1・出力 142 | 編集後と同じ | REQ-008・REQ-011 |
| `ApplySpeedPreset:4` | `selected_speed` 4・出力 116.5 | `selected_speed` 1・出力 142 | 編集後と同じ | REQ-008・REQ-011 |
| `ApplySpeedPreset:0.5` | `selected_speed` 0.5・出力 176 | `selected_speed` 1・出力 142 | 編集後と同じ | REQ-008・REQ-011 |
| `ApplyVolumePreset:50` | `selected_volume_percent` 50・出力 142(音量は長さに影響しない) | `selected_volume_percent` 100 | 編集後と同じ | REQ-009・REQ-011 |
| `ApplyVolumePreset:0` | `selected_volume_percent` 0(ミュート) | 100 | 編集後と同じ | REQ-009 |

## 3.3 複数段

- 積んだ順の逆に戻る。例: 速度 2 → 音量 50 → In(20 秒) の 3 段で、出力は 125 → 125 → 118(= 142 − 34 + 20/2)。Undo 3 回で 118 → 125(トリム 6)→ 125(音量 100)→ 142(速度 1)。Redo 3 回で逆にたどる。3 回目の Undo の後 `undo_enabled` false、3 回目の Redo の後 `redo_enabled` false。
- 途中で新しい編集をすると、やり直し履歴が消える(`redo_enabled` false)。取り消し履歴はそのまま残り、新しい編集が 1 段増える。
- 51 段目を積むと最も古い段が捨てられ、Undo は 50 回までしか戻れない(REQ-012。例の手順数上限 15 では示せないため、例は作らない)。

## 3.4 編集でない操作

- `ToStart`・`ToEnd`・`StepBack`・`StepForward` は再生ヘッドだけを動かし、`undo_enabled`・`redo_enabled` を変えない。Undo の後にこれらを押しても Redo は残る(U-09)。
- 移動先の時刻(先頭/末尾がクリップの端かトリムの端か)と、移動で選択中の区間が変わるかは本書では決めない(Q-07)。

## 3.5 拒否される編集

- ボタンが使えない状態の編集(例: 分割直後の同じ位置での `Split`)は押せず、履歴は変わらない。
- 同じ値の再適用(速度 1 の区間に `ApplySpeedPreset:1`)が段を積むかは未確定(Q-03)。

## 3.6 本書で決めていない画面の値

| 値 | 場面 | 確認 |
|---|---|---|
| `selected_*`・`merge_enabled` | `Split` の直後(前半と後半のどちらが選択されるか) | Q-05 |
| `selected_*` | 新しく生まれた区間を選択したまま、その分割を Undo したとき | Q-05 |
| `undo_enabled` | `Scale:*`・`SetFps:*` の後 | Q-01 |
| `playhead` | Undo/Redo の後 | Q-02 |
| `unsaved` | Undo で起動直後と同じ状態に戻ったとき | Q-04 |
