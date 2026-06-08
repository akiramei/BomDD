# ⑥ 合否 — 区間分割(Split)スライス

隔離製造物 `build/MoviePad.SplitSlice` に対し、装置未開示の隠しオラクル
`build/MoviePad.SplitSlice.Tests`(14ケース)を実行。

## 結果

| 回 | 結果 | 備考 |
|---|---|---|
| 1回目(BOMのみ製造物そのまま) | **13 / 14 合格** | 失敗: `Controller_NewIds_MonotonicAcrossUndo`(AC-12 / NFR-SPLIT-2) |
| 2回目(従来手法で1点修正後) | **14 / 14 合格** | CHEAT-004 適用後 |

### 失敗の中身(1回目)
製造装置は ID 採番を「毎操作後に `max(Id)+1` を再計算」で実装(`ComputeNextId`)。
Undo で区間が減ると nextId が**巻き戻り**、Undo→再Split で**同じIDを再利用** → NFR-SPLIT-2「単調増加」に違反。
原版は単調増分カウンタ(`_nextId++`、Undoで巻き戻さない)。**M-BOM の AC-12 が両読み可能(自己矛盾)**だったため発散。
→ 製造装置自身も Gap#14 で同矛盾を自己申告していた。

### 従来手法による修正(=CHEAT-004)
原版挙動を参照し、`SplitController` の nextId を増分カウンタ化(Undo/Redo で再計算しない)。修正3行。→ 全green。

## オラクルが捕捉できなかった乖離(重要)
- **SnapFrame の丸め方式**: 製造物は `MidpointRounding.AwayFromZero`、原版は C# 既定の `ToEven`(銀行家丸め)。
  移植テストのベクタ(50 / 40.2 / 63.8)は中間値を踏まないため**テストは全green でも実挙動は乖離**。
  製造報告 Gap#1 が無ければ気付けなかった = **「気づかれないずる」を防壁(製造報告)が捕えた実例**。→ CHEAT-005。

## 検査不能領域(Loop1 合否対象外)
- EB-KEYMAP(S キー・入力中無効)、EB-TIMELINE(分割で境界線が現れる)は単体検査不能。製造もしていない。→ CHEAT-006。

## 判定
**条件付き合格**: 客観検査範囲(ドメイン+統合ロジック)は従来手法1点介入で全green。
ただし (a) サイレント乖離1件(SnapFrame)、(b) 未検査のUI部品2件 が残る。これらは Loop2 以降の手法課題。
