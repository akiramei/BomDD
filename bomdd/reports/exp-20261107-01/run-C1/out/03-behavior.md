# 03 振る舞い — 各操作の前後で何が変わり、画面に何が出るか

記号: P = 再生ヘッド、R(t) = 時刻 t の区間(REQ-003: 半開区間 [start, end)・最後の区間は end も含む)、
Sel = 選択中の区間、`past`/`future` = 取り消し/やり直しの段(02-domain-model §3)。

## B-1. Undo(取り消し)

| | 内容 |
|---|---|
| 使える条件 | `past` が空でない(`undo_enabled` = true)。それ以外ではボタンは使えない。 |
| ドキュメント | 1 つ前のスナップショットへ丸ごと戻る(区間の数・境界・速度・音量・除外・トリムすべて)。 |
| 履歴 | `past` が 1 減り、`future` が 1 増える → `redo_enabled` = true。`past` が空になれば `undo_enabled` = false。 |
| 選択 | id を保つ。戻った状態にその id が無ければ再生ヘッドの下の区間(推定 — Q-1 と同根)。 |
| 再生ヘッド | 動かない(推定)。戻ったトリム範囲の外になる場合は未確定(Q-5)。 |
| 画面 | `region_count`・`trim_*`・`output_length`・`selected_*` が戻った状態の値に。`split/merge/trim_in/trim_out_enabled` は戻った状態と再生ヘッドから計算し直し。`unsaved` は未確定(Q-3)。 |

## B-2. Redo(やり直し)

| | 内容 |
|---|---|
| 使える条件 | `future` が空でない(`redo_enabled` = true)。 |
| ドキュメント | 取り消したスナップショットへ進む。 |
| 履歴 | `future` が 1 減り、`past` が 1 増える(`undo_enabled` = true)。 |
| 選択・再生ヘッド・画面 | B-1 と同じ規則。 |

## B-3. 新しい編集(Split / DeleteSelectedBoundary / SetTrimIn / SetTrimOut / ApplySpeedPreset / ApplyVolumePreset / ドラッグ / 除外)

| | 内容 |
|---|---|
| 受理されたとき | 旧 present を `past` へ積む(51 段目なら最古を捨てる)・**`future` を空にする** → `undo_enabled` = true, `redo_enabled` = false。 |
| 拒否されたとき | 何も変わらない(履歴も)。ボタンが使えない状態なので普通は押せない。 |
| 値が変わらないとき(同じ速度を再度、など) | 未確定(Q-4)。 |

## B-4. 操作ごとの具体(起動直後の画面から: P = 20、Sel = [6, 40)・速度 1・音量 100%)

| 操作 | ドキュメントの変化 | 画面(主なもの) | 取り消しで |
|---|---|---|---|
| `Split` | [6,40) → [6,20) + [20,40)(後ろが新 id) | `region_count` 5、`output_length` 142 のまま、`split_enabled` false(P が新しい境界)、`trim_in_enabled` false(20 は [6,20) に入らない)。選択はどちらか未確定(Q-1)→ `merge_enabled` も未確定 | `region_count` 4、選択 [6,40)、`split/trim_in_enabled` true、`merge_enabled` false |
| `SetTrimIn` | トリム開始 6 → 20、最初の区間 [20,40) | `trim_start` 20、`selected_start` 20、`output_length` 128(142 − 14)、`split_enabled` false(P が区間の端) | `trim_start` 6、`selected_start` 6、`output_length` 142、`split_enabled` true |
| `ApplySpeedPreset:2` | 区間 1 の速度 1 → 2 | `selected_speed` 2、`output_length` 125(142 − 34 + 17) | 速度 1、142 |
| `ApplySpeedPreset:0.5` | 速度 1 → 0.5 | `output_length` 176(142 − 34 + 68) | 速度 1、142 |
| `ApplyVolumePreset:50` | 音量 1.0 → 0.5 | `selected_volume_percent` 50、`output_length` 不変 | 100% |
| `Scale:0.5` | ドキュメントは不変 | `out_width` 960、`out_height` 540。`undo_enabled` は未確定(Q-2) | 未確定 |
| `SetFps:60` | ドキュメントは不変 | `out_fps` 60。`undo_enabled` は未確定(Q-2) | 未確定 |
| `StepForward` / `StepBack` | 不変 | P ± 1/30 s。`undo/redo_enabled` 不変 | (段にならない) |
| `ToStart` / `ToEnd` | 不変 | P が端へ(トリムの端か動画の端かは Q-6)。どちらでも `split_enabled` false(区間の端 0.5 s 未満、または区間外)。`undo/redo_enabled` 不変(やり直しも消えない) | (段にならない) |

### 分割を取り消したあとの選択について(推定の根拠)

分割直後の選択が前半([6,20)・元の id)なら、取り消し後もその id が [6,40) として残る。
後半([20,40)・新 id)なら、取り消し後その id は無いので解決し直しが要る。
解決先の候補 — 「再生ヘッドの下の区間」「最初の区間」— はどちらも [6,40) になる。
このため examples では取り消し後の選択を [6,40) と書いた(規則でなく、候補の収束に基づく唯一の主張)。
「選択なし」になる実装だけはこれと食い違う(Q-1 で併せて確認)。

## B-5. 50 段の上限(examples では 15 手順に収まらないため文書で)

1. 編集を 50 回 → `past` 50 段。`undo_enabled` true。
2. 51 回目の編集 → 最も古い段(読込直後の状態)が捨てられ、`past` は 50 段のまま。
3. 取り消しを 50 回 → 1 回目の編集の**後**の状態に戻る。読込直後の状態へは戻れない。`undo_enabled` false。
4. やり直しを 50 回 → 51 回目の編集の後の状態。

## B-6. ドラッグ(examples の操作一覧に無いので文書で)

境界・トリムをドラッグして離すまでが 1 段。離したあとの取り消し 1 回で、ドラッグ開始前の位置に戻る。
ドラッグ中の途中位置へは戻れない(段が無い)。

## B-7. 例(examples.json)との対応

| 例 | 確かめる振る舞い |
|---|---|
| EX-01 | U-9 起動直後は両方使えない |
| EX-02〜04 | B-1/B-2 の往復(速度・音量) |
| EX-05 | 2 段の取り消し・やり直しの順序 |
| EX-06 | B-3 新しい編集でやり直しが消える |
| EX-07, EX-09 | トリムの取り消し・トリム+速度の 2 段 |
| EX-08 | 分割の取り消し(選択の推定を含む) |
| EX-10, EX-11 | 再生ヘッドの移動は段にならず、やり直しを消さない |
| EX-12, EX-13 | 出力設定は、後の別の編集の取り消しで変わらない |
