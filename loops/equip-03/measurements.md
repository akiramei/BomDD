# equip-03 measurements(実行記録 — 進行中)

## 0. 起票前検証 — fail-closed 停止と題材の再裁定(2026-08-02)

protocol §3 手順 1 の実在確認で **凍結題材の消滅を検出**し、製造に入らず停止した(逸脱ではなく
fail-closed の正常動作。工場起動・介入・製造は一切発生していない)。

- 実測: 候補「repo: 形の repo 不在= X-XREPO skip へ」は **Plm ECO-002(2026-07-03)で解消済み**。
  証拠= 20-spec §2.4(rev3・受理形3 の repo 不在= X-XREPO-001 skip)/オラクル S-24
  (change_ref: ECO-002・「ViewPrism2 pre-commit 実害の再現形」)/packages/core/src/resolve/
  model.ts(「rev3/ECO-002 CH-3」注記つき実装)。
- 根因: 52-metrics の候補行に解消マーカーが無く(他候補は「→ 解消(ECO-00N)」を持つ)、
  現存候補に見えていた — **台帳の記帳漏れ**。protocol 凍結(93b1be9)と gate ① 裁定 1 は
  この誤った在庫認識に基づいていた。
- 処置: 解消マーカーを追記(Plm 076f6c3・歴史記述は非改竄・追記のみ)。
- 教訓候補: 「候補台帳の解消マーカーは人手 — 起票前の実在検証(spec/oracle/src 突合)が
  最後の防壁」。equip-02 レビュー採択の入力検証(EXP-20260802-06 系)が**題材の存在**にも
  適用されるべき実例 1 件。

## 0.1 代替在庫の実測(再裁定の材料・2026-08-02)

| リポ | 実測結果 |
|---|---|
| Plm | 現存候補は **M-BOM 写像被覆ギャップのみ**(unmapped 76 files・受入= unmapped 0 が機械判定可。ただし「単独 ECO は過剰・次回 32-mbom 改訂時に便乗」と記録済み= 昇格には再裁定が要る)。宣言中心で src 製造は僅少 |
| ViewPrism2 | ECO-141 まで**全クローズ**・未起票候補なし |
| ViewGrid | 宣言系債務 4 件(catch-all ペア写像・csproj/sln 所有・tests unit・CP 接続)— いずれも「ECO 運用開始時」預り。60-register 未設= 測定系 bootstrap 込みになる |
| MoviePad | line ready・ECO-001 済み・未起票候補なし(W1〜W5 は製品是正不要と決着済み) |

= **src 変更を伴う実在の未起票 ECO 候補は現在ゼロ**。gate ① 再裁定へ(選択肢: Plm M-BOM
ギャップの単独昇格/ViewGrid 初 ECO/実需発生待ち)。
