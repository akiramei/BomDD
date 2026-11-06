# 2. ドメインモデル — 取り消し/やり直し

## 2.1 概念

| 概念 | 内容 | 根拠 |
|---|---|---|
| ドキュメント状態(DocumentState) | 不変の値。区間の並び・トリム範囲を持つ。編集は新しい値を返す。 | README「Design notes」・REQ-002 |
| 区間(Region) | id・開始・終了・速度・ピッチ維持・音量・除外。区間は隙間なく並ぶ。 | REQ-003・REQ-004・REQ-008〜010 |
| トリム範囲 | [trim_start, trim_end]。先頭区間の開始・末尾区間の終了と連動。 | REQ-007 |
| 履歴(History) | 取り消しスタック(過去の状態)と、やり直しスタック(取り消した状態)。上限 50。 | REQ-012・README:23 |
| 段(Step) | 1 回の編集の前の状態 1 つ。ドラッグは開始時の 1 つ。 | REQ-012 |
| 選択中の区間 | 区間 id で指す編集対象。速度・音量・結合の対象。 | README:18「直下の区間が編集対象」・REQ-004 counterexample(undo resolves the selection by id) |
| 再生ヘッド | 時刻。ドキュメントの外(画面の状態)。分割・トリムの位置、選択の決め方に使う。 | REQ-003・REQ-004・REQ-007 |
| 出力設定 | 出力幅・高さ・フレームレート。ドキュメントの内か外かは未確定(Q-01)。 | REQ-013 |
| 保存状態の表示 | 「保存済み」/「未保存の変更」。 | `cad/observations.json` `unsaved` |

## 2.2 関係

```
History
 ├─ undo_stack : [DocumentState] (最大 50, 古い順に捨てる)
 ├─ present    : DocumentState   (画面に出ている状態)
 └─ redo_stack : [DocumentState]

DocumentState
 ├─ regions : [Region] (順序あり・隙間なし・>=1)
 └─ trim    : [start, end]

画面の状態(ドキュメントの外)
 ├─ playhead
 ├─ selected_region_id → DocumentState.regions のどれか
 └─ 出力設定(未確定: Q-01)
```

## 2.3 状態と遷移

履歴の状態は (取り消し段数 u, やり直し段数 r) で表す。`undo_enabled = (u > 0)`、`redo_enabled = (r > 0)`。

| 出来事 | 前 | 後 | ドキュメント |
|---|---|---|---|
| 編集(受理) | (u, r) | (min(u+1, 50), 0) | 新しい状態 |
| 編集(拒否) | (u, r) | (u, r) | 変わらない |
| Undo(u > 0) | (u, r) | (u−1, r+1) | 1 段前の状態 |
| Redo(r > 0) | (u, r) | (u+1, r−1) | 取り消した状態 |
| 再生ヘッドの移動 | (u, r) | (u, r) | 変わらない |
| ファイルを開く | — | 未確定(Q-06) | 新しいクリップの初期状態(REQ-002) |

不変条件:
- I-1 Undo の直後に Redo すると、Undo の直前と同じドキュメントになる(往復で値が変わらない)。
- I-2 Redo の直後に Undo すると、Redo の直前と同じドキュメントになる。
- I-3 Undo/Redo は区間の並びの不変条件(隙間なし・各区間 0.5 秒以上)を壊さない(どの段も編集で受理された状態だから)。
- I-4 区間の id は状態と一緒に戻る。分割で生まれた id は、その分割を取り消すと消える(REQ-004)。
