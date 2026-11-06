# 02 ドメインモデル — 取り消し/やり直し

## 1. 概念

```
EditorSession(画面 1 つ分)
 ├─ Clip(開いたファイル: 長さ・幅・高さ・fps…)            REQ-001  読み取り専用
 ├─ History
 │    ├─ present : DocumentState   ← いま表示しているドキュメント
 │    ├─ past    : [DocumentState] ← 取り消しの段(古い→新しい・最大 50)
 │    └─ future  : [DocumentState] ← やり直しの段(取り消した順)
 ├─ Selection : RegionId           ← 編集対象の区間(id で持つ)
 ├─ Playhead  : 秒                 ← ドキュメント外(推定)
 ├─ OutputSettings(幅・高さ・アスペクト維持・fps)         履歴に入るか未確定(Q-2)
 └─ DirtyFlag(未保存の変更/保存済み)                     規則は未確定(Q-3)

DocumentState(不変・値)                                   REQ-002〜011
 ├─ regions : [Region]  隙間なく時間順に並ぶ(REQ-003)
 │    Region = { id, start, end, speed, preservePitch, volume, excluded }
 └─ trim    : [trimStart, trimEnd]   (最初の区間の start = trimStart、最後の区間の end = trimEnd)
```

## 2. 不変条件

| ID | 内容 | 根拠 |
|---|---|---|
| I-1 | `len(past) ≤ 50`。 | REQ-012 |
| I-2 | `present` は常に区間の並びの不変条件(隙間なし・各区間 0.5 s 以上・速度 0.25〜4.0・音量 0〜2.0・除外されていない区間が 1 つ以上)を満たす。過去・未来の段も同じ(それ自体がかつての present だから)。 | REQ-003〜010 |
| I-3 | 区間 id は一度使ったら使い回さない(取り消しで消えた id も)。 | REQ-004 反例 3 |
| I-4 | `past`・`future` の各段はドキュメント全体のスナップショット。段同士は参照を共有してよい(不変だから)。 | README 設計上のポイント |
| I-5 | `present` が変わらない操作(拒否された編集)は `past`/`future` を変えない。 | REQ-004 "refusals return no new document" |

## 3. 履歴の状態と遷移

状態は `(len(past), len(future))` で表せる。

```
undo_enabled = len(past)   > 0
redo_enabled = len(future) > 0
```

| 出来事 | past | present | future |
|---|---|---|---|
| ファイルを開く/起動(サンプル読込) | [] | 読込状態 | [] |
| 編集 e(受理) | past + [present](51 個になったら先頭を捨てる) | e(present) | **[]** |
| 編集 e(拒否) | 変化なし | 変化なし | 変化なし |
| ドラッグ開始→移動→終了 | 開始時に past + [present] を 1 回だけ | 移動のたびに更新(段は増えない) | [] |
| 取り消し(past が空でない) | past の末尾を外す | past の末尾 | [旧 present] + future |
| やり直し(future が空でない) | past + [旧 present] | future の先頭 | future の先頭を外す |

注: やり直しで past が 51 になる場合の扱いは資料に無いが、やり直しで積み直されるのは取り消しで外した段だけなので、
取り消し→やり直しの往復だけでは 50 を超えない。

## 4. ドキュメントの外にあるもの と 取り消しの関係

| 状態 | 取り消し/やり直しで | 根拠 / 確度 |
|---|---|---|
| Selection(区間 id) | 変えない。新しい present で同じ id を探す。見つからなければ(取り消しで消えた後ろ側の区間)再生ヘッドの下の区間へ解決する(推定)。 | REQ-004 反例 3(id で解決)/ 解決できない場合は推定 |
| Playhead | 変えない(新しいトリム範囲の中にある限り)。範囲外になる場合は未確定(Q-5)。 | ドキュメントに無い(REQ-002)・推定 |
| OutputSettings | 未確定(Q-2)。ただし、出力設定のあとに別の編集をし、その編集だけを取り消すなら、どちらの模型でも出力設定は変わらない。 | REQ-013 / README |
| DirtyFlag | 未確定(Q-3)。 | 資料に記述なし |

## 5. 画面の表示との対応(cad/observations.json)

| 表示 | 導出元 |
|---|---|
| `undo_enabled` / `redo_enabled` | History(§3 の式) |
| `region_count`, `trim_start`, `trim_end` | present |
| `output_length` | present(除外されていない区間の (トリム後の長さ / 速度) の和 — REQ-011) |
| `selected_start/end/speed/volume_percent` | present の中で Selection の id を持つ区間 |
| `split_enabled` | present と Playhead(区間内かつ両端から 0.5 s 以上 — REQ-004) |
| `merge_enabled` | present と Selection(選択区間の前に区間があるとき — ボタン文言「1 つ前の区間と結合」 / REQ-006) |
| `trim_in_enabled` / `trim_out_enabled` | present と Playhead(REQ-007) |
| `playhead` | Playhead |
| `out_fps`, `out_width`, `out_height` | OutputSettings |
| `unsaved` | DirtyFlag |

これらは保存された値ではなく**導出値**なので、取り消し/やり直しのあとは新しい present から計算し直す。
