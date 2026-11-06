# MoviePad 取り消し/やり直し — ドメインモデル

## 概念

```
Session(画面の状態・ViewModel)
 ├─ document: Document            … 今のドキュメント(不変)
 ├─ history: History               … 過去と未来のドキュメント
 ├─ playhead: 秒                   … ドキュメントの外(履歴に積まない)
 ├─ selection: RegionId?           … ドキュメントの外。表示は document 上で解決(規則は Q-02)
 ├─ output: OutputSettings         … 幅・高さ・縦横比維持・fps(履歴に積むかは Q-01)
 └─ saveState: 保存済み / 未保存の変更(規則は Q-05)

Document(不変・record) … 編集はすべて新しい Document を返す(README Design notes)
 ├─ clip: ClipInfo(長さ・幅・高さ・fps・コーデック …)  REQ-001
 ├─ regions: Region[1..]   時間順に隙間なく並ぶ            REQ-003
 └─ trim: [trimStart, trimEnd]                              REQ-007

Region
 ├─ id                     分割の後半は新しい id、結合は前側の id を残す  REQ-004/006
 ├─ start, end             半開区間 [start, end)(最後の区間は end も含む)  REQ-003
 ├─ speed  0.25〜4.0(0.01 刻み)  REQ-008
 ├─ preservePitch: bool             REQ-008
 ├─ volume 0.0〜2.0(0.01 刻み・0 はミュート)  REQ-009
 └─ excluded: bool                  REQ-010

History                                              REQ-012
 ├─ past:   Document[0..50]   取り消し用(古い順。51 個目で最古を捨てる)
 └─ future: Document[0..]     やり直し用
```

## 不変条件

- I-1 `past` の長さは 50 以下。
- I-2 `undo_enabled ⇔ past が空でない`、`redo_enabled ⇔ future が空でない`。
- I-3 新しい編集を記録すると `future` は空になる。
- I-4 `past`・`future` の各要素は、どこかの時点で `document` だった値そのもの(部分的な差分ではない)。
- I-5 履歴に入るのは Document だけ。playhead は入らない。selection・output・saveState が入るかは未決(Q-01・Q-02・Q-05)。

## 状態遷移(History)

| 契機 | 前 | 後 |
|---|---|---|
| 編集 e(受理され新しい Document d' が返る) | document=d, past=P, future=F | document=d', past=P+[d](51 個なら先頭を捨てる), future=[] |
| 編集 e が拒否される | 変化なし | 変化なし(履歴に積まない) |
| ドラッグ開始 → 移動 … → 終了 | document=d | 開始時に past へ d を 1 回だけ積み、途中は document だけ更新 |
| Undo(past が空でない) | document=d, past=P+[p], future=F | document=p, past=P, future=[d]+F |
| Redo(future が空でない) | document=d, past=P, future=[f]+F | document=f, past=P+[d], future=F |
| 再生ヘッドの移動 | — | playhead だけ変わる。past・future は変わらない |

## 派生値(画面の表示はこれらから計算される)

| 表示 | 計算 | 出典 |
|---|---|---|
| region_count | regions の数 | — |
| trim_start / trim_end | trim | REQ-007 |
| output_length | 非除外区間について Σ(トリム後の長さ / speed) | REQ-011 |
| selected_* | selection を document 上で解決した区間の start/end/speed/volume×100 | OBS、Q-02 |
| split_enabled | 再生ヘッド(フレーム吸着後)が区間の中で、両端から 0.5 s 以上 | REQ-004 |
| merge_enabled | 選択中区間に 1 つ前の区間がある | ACT「Merge the current region with the one before it」、REQ-006 |
| trim_in_enabled | 再生ヘッドが最初の区間の中で、その終端から 0.5 s 以上 | REQ-007 |
| trim_out_enabled | 再生ヘッドが最後の区間の中で、その始端から 0.5 s 以上 | REQ-007 |
| undo_enabled / redo_enabled | I-2 | REQ-012 |

`*_enabled` が可否条件をそのまま映すことは起動直後の画面で確かめられる: 再生ヘッド 20 秒・選択中 [6, 40) で
split=true(両端から 14 秒・20 秒)、merge=false(最初の区間)、trim_in=true(最初の区間・40 から 20 秒)、trim_out=false(最後の区間でない)。

## 起動直後の状態から読めること・読めないこと

- 読める: ソースの fps = 30(REQ-013「出力 fps はソースの fps で始まる」+ START の out_fps 30)。したがって 20 秒はフレーム格子上にあり、20 秒での分割は再生ヘッドを動かさない。1 フレーム = 1/30 秒。
- 読める: 最初の区間 = [6, 40)、速度 1、音量 100%。
- 読めない: 2〜4 番目の区間の境界・速度、各区間の除外の有無、クリップの長さ。トリム後のソース長 126 秒に対し出力長 142 秒なので、どこかに速度 1 未満の区間がある(除外は出力長を減らす方向にしか働かない)。このため、最初の区間の速度・トリムを変えた直後の output_length は決まらない(取り消しで戻った 142 だけは言える)。
