# 3. 振る舞い — 各操作の前後と画面

すべて起動直後(`cad/start-screen.json`: 4 区間・トリム 6〜132・再生ヘッド 20・選択 [6, 40] 速度 1 音量 100%・出力 142 秒・
1920×1080・30 fps・Undo/Redo とも使えない・保存済み)から始めたときの値。「—」は資料から決まらない値で、例(`examples.json`)にも書いていない。

## 3.1 編集操作(1 段を積む)

| 操作 | 文書の変化 | 画面に出る値(押したあと) | 決まらない値 |
|---|---|---|---|
| `ApplySpeedPreset:2` | 選択区間 [6, 40] の速度 1 → 2 | selected_speed 2、output_length 142 − 34 + 17 = **125**、undo 使える、redo 使えない、unsaved true | — |
| `ApplySpeedPreset:4` | 同 → 4 | output_length 142 − 34 + 8.5 = **116.5** | — |
| `ApplyVolumePreset:50` / `:0` | 選択区間の音量 → 0.5 / 0.0(0 は消音) | selected_volume_percent 50 / 0、output_length 142 のまま | — |
| `SetTrimIn`(再生ヘッド 20) | トリム開始 6 → 20、最初の区間 [6, 40] → [20, 40] | trim_start 20、selected_start 20、output_length 142 − 14 = **128**、trim_in_enabled true のまま(20 は [20, 40) の中・40 まで 20 秒)、merge_enabled false のまま | — |
| `Split`(再生ヘッド 20) | [6, 40] → [6, 20] と [20, 40](後半は新しい id、速度・音量は引き継ぐ) | region_count 5、output_length 142、playhead 20、trim 6/132、split_enabled **false**(20 は [20, 40] の始点で端から 0 秒)、trim_in_enabled **false**(20 は最初の区間 [6, 20) の外)、undo 使える、unsaved true | **selected_*・merge_enabled**(Q-01) |
| `SetTrimOut` | 起動直後は使えない(再生ヘッドが最後の区間にない) | — | — |
| `DeleteSelectedBoundary` | 起動直後は使えない(選択が最初の区間)。使えるときは選択区間と 1 つ前を結合し、前の区間の id・設定を残す(REQ-006) | — | 分割後に使えるかは Q-01 次第 |
| `Scale:0.5` | 出力の幅・高さ = even(1920 × 0.5)、even(1080 × 0.5) | out_width 960、out_height 540 | undo_enabled・unsaved(Q-03) |
| `SetFps:60` | 出力 fps → 60 | out_fps 60 | undo_enabled・unsaved(Q-03) |

## 3.2 Undo / Redo

| 操作 | 使える条件 | 前 → 後 | 画面 |
|---|---|---|---|
| `Undo` | undoStack が空でない | 文書を 1 段前へ。今の文書を redoStack へ | 文書由来の値が 1 段前の値に戻る。redo 使える。戻す段が尽きたら undo 使えない。playhead は変わらない(Q-06)。unsaved は—(Q-02) |
| `Redo` | redoStack が空でない | 文書を 1 段先へ。今の文書を undoStack へ | 文書由来の値がやり直した編集の後の値になる。undo 使える。やり直す段が尽きたら redo 使えない |
| 編集(Undo の後) | — | redoStack を空にする | redo 使えない(REQ-012) |

具体例(起動直後から):

1. `ApplySpeedPreset:2` → `Undo`: selected_speed 1、output_length 142、undo 使えない、redo 使える。
2. 続けて `Redo`: selected_speed 2、output_length 125、undo 使える、redo 使えない。
3. `ApplySpeedPreset:2` → `Undo` → `ApplyVolumePreset:50`: 速度 1・音量 50、redo 使えない(速度 2 はもう戻らない)、undo 使える(1 段)。
4. `ApplySpeedPreset:2` → `ApplyVolumePreset:50` → `Undo` → `Undo`: 新しい順に戻る(音量 → 速度)。2 回で undo 使えない、redo 使える。
5. `Split` → `Undo`: region_count 4、split_enabled・trim_in_enabled が true に戻る。選択は [6, 40] に戻ると読める
   (前半の id で引いても、再生ヘッドの下の区間で引いても同じ)が、分割後に後半が選ばれていた場合の引き直し先が
   資料にない(Q-01)ため、例には selected_*・merge_enabled を書いていない。

## 3.3 段を作らない操作

| 操作 | 文書 | 画面 |
|---|---|---|
| `StepForward` / `StepBack` | 変わらない | playhead ± 1/30 秒、undo/redo の可否は変わらない、unsaved は変わらない |
| `ToStart` / `ToEnd` | 変わらない | undo/redo の可否は変わらない。行き先(0 かトリム開始 6 か、長さかトリム終了 132 か)は資料にない(Q-04)。行き先によって選択も変わりうる |

Undo の後に再生ヘッドが動かないため、たとえば `StepForward` → `ApplySpeedPreset:2` → `Undo` では再生ヘッドは 20 + 1/30 秒のまま残る(Q-06)。

## 3.4 拒否される編集

拒否(例: 区間の端から 0.5 秒未満での分割、最後に残った出力区間の除外)は文書を変えず、段も増えない(U-06)。
画面ではボタン自体が使えない(`*_enabled` = false)ので、例では押さずに false と書いた。

## 3.5 例に入れなかった振る舞いと理由

- 50 段の上限: 51 回の編集が要り、1 例 15 手順に収まらない。
- 結合(`DeleteSelectedBoundary`)の Undo: 結合を使える状態にする手順が、分割後の選択(Q-01)に依存する。
- ドラッグ 1 回 = 1 段: 例で使える操作にドラッグがない。
- 出力設定の Undo: Q-03 が決まるまで値を書かない(押したあとの幅・高さ・fps だけ書いた)。
