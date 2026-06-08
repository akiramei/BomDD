# ③ M-BOM v2 — 改善①③⑤適用(区間分割スライス)

[../loop-01-split/03-mbom.md](../loop-01-split/03-mbom.md) からの差分のみ記す。インターフェース契約・調達・環境は v1 と同一。

## 無矛盾性検査(改善③)の結果
v1 の AC 群を無矛盾性検査 → **AC-12 が両読み可能(自己矛盾)**と判明。単一ポリシーへ修正(下記)。他 AC に矛盾なし。

## 改訂した受入基準(検査モダリティ列=改善⑤ を追加)
| AC | 受入条件 | モダリティ | 由来 |
|---|---|---|---|
| AC-5 | `SplitAt` は分割前に playhead を `SnapFrame` する。**`SnapFrame` は最近接フレーム、中間値は偶数側(`MidpointRounding.ToEven` = .NET `Math.Round` 既定)** | unit(中間値ベクタ必須) | REQ-SPLIT-6 |
| AC-12 | **新IDは構築時に `max(Id)+1` で初期化した永続カウンタから払い出し、`Split` 成功ごとに +1。`Undo`/`Redo` では巻き戻さない**(単調増加・衝突なし) | unit | NFR-SPLIT-2 |
| AC-1〜4,6〜11 | v1 と同一 | unit | v1 参照 |
| (UI) | S キーで境界線が現れる / 後半が選択(見た目) | **manual**(Loop1.5 では未検査=不足明示) | REQ-SPLIT-1,2 |

## ① 完全性: 数値ACの規定
- `SnapFrame`: 丸め = ToEven、グリッド = `1/fps` 秒、`fps<=0` は `DefaultFps`。
- **必須テストベクタ(中間値)**: `SnapFrame(0.25, 2) == 0.0`(0.5→偶数0)、`SnapFrame(1.25, 2) == 1.0`(2.5→偶数2)。
- `Clamp`/`MinLen` の境界: v1 の AC-4/7 が `Start+MinLen < ph < End-MinLen`(両端 MinLen ちょうどは不可)を被覆済み。

## 効果測定の対象
- AC-12 単一化 → 製造装置は再計算/カウンタで迷わない(CHEAT-004 消滅見込み)。
- ToEven 明記 + 中間値ベクタ → 丸め次元が被覆され乖離検出可能(CHEAT-005 消滅見込み)。
