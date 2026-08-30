# Change Order — ECO-034(C16 の偽陽性に出口を作る — 根拠つき not-required 宣言の受理)

> 由来: ECO-033(verified)で新設した C16 が、**初回の実運用で出口のない偽陽性**を起こした。
> 是正方針は 2026-08-30 の裁定で **O-2** を採択済み。gate は開いていない(方針裁定済み)。

<!-- converge: not-required reason: 是正方針(O-2)は起票前に裁定済みで未解決の選択はなく、製造は fixture 9 種の機械受入を持つ(converge 適用範囲「機械受入がある是正実施には使わない」)。本文中の `gate ①`・`残ゲート` は検査器の語彙を**説明・引用**する言及であり使用ではない。§4.1 の追加設計は削除可能な旨を開示した記載であって裁定要求ではない decided-by: claude-opus-5(製造側の自己宣言・監査対象。C16 が免除を件数と宣言者つきで毎回表示する) -->

## 担当設備(equipment)

- 製造(設計者):
  - requested: `claude-opus-5`
  - resolved: `claude-opus-5`
  - ハーネス: Claude Code(Claude Agent SDK)
  - 来歴: **self-reported**
- 検査官: なし(独立検査なし)

## 1. 症状(実測)

ECO-033 の受入直後、`method/improvements.md` へ ECO-033 弧の還元節(**記帳のみ**・
lesson-promote 手順 1〜5・裁定候補なし)を追記したところ、C16 が FAIL した。

```
[C16] FAIL … improvements.md #2026-08-30 BomDD 自己適用還元 — ECO-033 弧:
      converge-required(adjudication-gate,open-gate)だが収束 receipt がない
```

発火した 2 箇所はいずれも**マーカーの言及であって使用ではない**:

| マーカー | 実際の文脈 |
|---|---|
| `adjudication-gate` | 「**gate ① で承認された**選択肢 C-1 は…」— 過去の承認の叙述 |
| `open-gate` | 「**`残ゲート`** だけでは…14 件を取り逃がしていた」— **検査器そのものを論じる**文中での引用 |

use/mention の混同であり、ECO-033 §8.3 で是正した部分文字列ゲート欠陥と**同じクラス**
(テキストが概念を*遂行*しているか*言及*しているかを区別しない)。

## 2. 真の問題 — 偽陽性に出口がない

単なる精度欠陥ではない。B-1 の非対称設計は、**偽陽性に対して逃げ道を持たない**:

- `converge: not-required` の宣言 → hard-positive 実在時は**却下(FAIL)**が B-1 の設計
- 収束 receipt を書く → converge は記帳に適用しない契約であり、**やっていないことを書く**ことに
  なる(playbook §4.4「検査文はコードが測る以上を主張しない」に反する)
- 検査を黙って緩める → ハーネス変更であり ECO なしには行えない

結果として、**正当な作業がデッドロックする**。予防ゲートが偽陽性を持つこと自体は避けられないが、
**出口を持たない**設計は、偽陽性の頻度がゼロでない限り必ず作業を止める。

**頻度の実測**: 本 ECO 時点で cutoff 以降の対象 3 件のうち **1 件(33%)** が「検査を論じる文書」
クラスに該当した。還元節は検査・計器の話を多く含むため、頻度は低くない。

## 3. ECO-033 の受入が見落としていたもの

ECO-033 の較正は fixture 5/5・実在 known-bad 19/19・実コーパス全数分類(required 20 /
not-required 13)まで行ったが、**「検査器そのものを論じる文書」というクラスを一度も試していない**。
§8.6 で宣言した検出力の限界 3 点にも入っていなかった — **宣言した限界が不完全だった**。

これは `OBS-20260830-08`(合成 fixture の全通過は実コーパス上の精度も被覆も証明しない)の
**同一弧内での再発**である。実コーパス全数分類までやってなお、文書の**クラス**が 1 つ未試行だった。

## 4. 是正(裁定済み — O-2)

**`not-required` 宣言に根拠を必須にして受理する。根拠なしの宣言は現行どおり却下する。**

前例は本リポ内に実在する — `ui-cad-gate` の GU4(ECO-005・外部レビュー所見 5):

> rejected は GU2 の被覆に算入される(= action を落とせる)ため、来歴なしの黙殺を通さない —
> **却下根拠と決定者を必須にする**

同じ形を採る。**根拠(reason)と決定者(decided-by)の 2 点**を必須とし、片方でも欠ければ FAIL。

```
<!-- converge: not-required reason: <なぜ対象外か> decided-by: <誰が宣言したか> -->
```

- `required` 宣言は現行どおり**常に有効**(引き上げは無条件)。
- 根拠なしの `not-required` + hard-positive → **FAIL**(B-1 の非対称性を維持)。
- 根拠つきの `not-required` + hard-positive → **受理**。ただし記録に残り監査可能になる。

### 4.1 追加した設計(裁定 3 の懸念への直接の応答)

裁定 3 は「receipt 不在検査だけでは applicability 判定側で再び fail-open し得る」と警告していた。
根拠つき宣言はその fail-open を**再導入しうる**。緩和として:

**免除は数えて表示する。** C16 は有効な `not-required` 宣言の件数を毎回の判定行へ出力する。
**沈黙する免除が fail-open を作る**のであり、件数が常時可視なら増加が観測できる。
(この 1 点は O-2 の裁定範囲を超える追加である — 不要なら削除してよい。)

## 5. 影響 BOM

- `method/tools/self-conformance.py`: C16 の宣言パーサと conflict 判定のみ。
  **hard-positive 語彙・対象集合(A-1)・cutoff(C-1c)は変更しない**。
- `method/improvements.md`: ECO-033 弧の還元節へ根拠つき宣言を付す(本 ECO の最初の適用例)。
- `bomdd/60-change-register.yaml` / 本 order: 台帳系。
- 既存 15 検査・fixture F1〜F5: **判定不変**の予測。
- 配布物は変更しないため製品リポ・kit へは**非波及**。

## 6. スコープ外

- **O-1(use/mention 弁別)** — コードスパン内のマーカー除外。実測で `残ゲート` には効くが
  `gate ①` の素テキストには効かず**単独では不十分**。O-2 で出口が確保されるため、精度改善は
  実害の実測が出てから別 ECO とする。
- **O-3(improvements.md を対象から外す)** — 却下済み。A-1 の裁定を覆し mixed-task fixture が
  書けなくなる。
- 「根拠の**質**」の機械判定 — 測らない(§8 の限界宣言で明示する)。
- Phase 2(presentation Gate)・receipt schema 拡張・製品リポへの設置 — いずれも別 ECO。

## 7. 較正

| # | fixture | 期待 |
|---|---|---|
| F1〜F5 | ECO-033 の既存 5 種 | **判定不変** |
| F6 | hard-positive + `not-required`(**reason のみ**・decided-by なし) | **FAIL** |
| F7 | hard-positive + `not-required` + reason + decided-by | **PASS** |
| F8 | hard-positive + `not-required` + **空の reason** | **FAIL**(欄の存在でなく中身を測る) |

赤プローブ(是正面): 本 ECO の症状そのもの — ECO-033 弧の還元節が**宣言前に FAIL し、
宣言後に PASS する**ことを実測する。合成でなく**実在する不適合**である。

## 8. 製造記録

### 8.1 実装

`method/tools/self-conformance.py` の C16 のみを改修した。**hard-positive 語彙・対象集合(A-1)・
cutoff(C-1c)は一切変更していない**。

- 宣言パーサを `converge: (required|not-required)` + 任意の `reason:` / `decided-by:` へ拡張。
- `converge_classify` に `grounded`(reason と decided-by が**ともに非空**)と `exempted` を追加。
- conflict 判定を精密化: `not-required` + hard-positive のとき、**根拠なしなら FAIL / 根拠つきなら
  受理**。`required` への引き上げは無条件で有効(不変)。
- FAIL メッセージは**欠落した欄名**を出す(`欠落: decided-by` 等)— 何を書けば通るかが判る。
- 判定行に**有効な免除の件数と宣言者**を出力(§4.1)。

### 8.2 較正 — 予防面(fixture 8 種・毎回実行)

| # | fixture | 期待 | 実測 |
|---|---|---|---|
| F1 | required + receipt なし | FAIL | FAIL |
| F2 | required + receipt あり(正常系) | PASS | PASS |
| F3 | not-required + receipt なし | PASS | PASS |
| F4 | mixed-task 陽性 | FAIL | FAIL |
| F5 | hard-positive + **根拠なし** not-required | FAIL | FAIL |
| F6 | not-required + **reason のみ**(decided-by なし) | FAIL | FAIL |
| F7 | not-required + reason + decided-by | **PASS** | PASS |
| F8 | not-required + **空の reason** | FAIL | FAIL |

**8/8 一致。** F1〜F5 は判定不変(ECO-033 からの回帰なし)。F8 は「欄の存在」でなく「欄の中身」を
測っていることの対照 — これがないと `reason:` と書くだけで通る。

### 8.3 較正 — 是正面(実在する不適合の赤→緑)

合成ではなく**本 ECO の症状そのもの**を対照にした。

```
宣言 前: [C16] FAIL … improvements.md #2026-08-30 BomDD 自己適用還元 — ECO-033 弧:
         converge-required(adjudication-gate,open-gate)だが収束 receipt がない
宣言 後: [C16] PASS … 根拠つき免除 1 件[… (by claude-opus-5(製造側の自己宣言・監査対象…))]
```

**赤→緑の対を同一個体で実測した。** 落ちたのは C16 の 1 件のみで、他 15 検査は両実行で判定不変。

### 8.4 受入

- **V1(予防面)= PASS**: fixture 8/8。
- **V2(是正面)= PASS**: 実在不適合の赤→緑を実測。
- **V3(全検査)= PASS**: self-conformance 全 16 検査 PASS。既存 15 は判定不変。
- **V4(CI)/ V5(diff 窓)**: push 後に確定。

### 8.5 宣言した検出力の限界(ECO-033 §8.6 への追補)

ECO-033 で宣言した 3 点に加え、本 ECO で判明・導入した 2 点:

4. **use/mention を区別しない** — 検査器そのものを論じる文書はマーカーを**言及**するだけで
   required になる。本 ECO はこれを**精度改善では解かず、出口(根拠つき免除)で解いた**。
   精度側の是正(O-1)は実害の実測後に別 ECO とする。
5. **根拠の「質」は測っていない** — `reason` と `decided-by` の**非空**しか測らない。
   `reason: x` でも通る。緩和は防止ではなく**観測可能化**であり、免除の件数と宣言者を毎回
   表示することで増加が観測できる形にしてある。**自己宣言も許す**(人間の裁定を毎回要求すると
   converge の目的〈人間の仕事を裁定だけに戻す〉に反するため)— 代わりに全免除が監査面に出る。

### 8.6 この ECO が支持しないもの

use/mention の精度改善(O-1)/ 免除の質の保証 / Phase 2(presentation Gate)/
receipt schema 拡張 / 製品リポへの設置。いずれも別 ECO・別裁定である。

### 8.7 製造中の第 2 の欠陥 — 宣言構文の説明が自己免除を作った

O-2 の実装直後、**本 order 自身**が不正な免除を得ていることを C16 が報告した。

```
根拠つき免除 2 件[ECO-034(by <誰が宣言したか>) / …]
```

原因は §4 のコードフェンス内に置いた**宣言構文のテンプレート**である。**宣言の書式を説明する
文書が、その説明によって自分を免除していた** — use/mention の第 2 の現れであり、しかも
今度は**過剰検出でなく過剰免除**(fail-open)だった。

**検出したのは §4.1 で追加した免除の可視化そのものである。** 件数だけでなく宣言者を出していた
ため、`by <誰が宣言したか>` というプレースホルダが目に入った。件数のみの表示なら
「免除 2 件」で通り過ぎていた可能性が高い。

**是正(倒れる方向を揃える)**: **免除を与える文はコードフェンス内では読まない**。一方
hard-positive は**フェンス内でも読む**。この非対称は意図的である —

| 種別 | フェンス内 | 理由 |
|---|---|---|
| hard-positive(required を上げる) | **読む** | 過剰検出は**出口がある**ので安全側 |
| 宣言(not-required を与える) | **読まない** | 過剰免除は **fail-open** で出口を要さない |

fixture **F9**(コードフェンス内の宣言は免除を与えない)を追加。F1〜F8 は判定不変で **9/9**。

### 8.8 本 order 自身への適用(出口の初回使用)

フェンス修正後、本 order は `gate ①`・`残ゲート` の**言及**により正当に required と判定され
FAIL した。ECO-034 が作った出口を使い、根拠つき宣言を付して受理させた
(reason= 方針は起票前に裁定済み・製造は fixture 9 種の機械受入を持つ・マーカーは言及である /
decided-by= claude-opus-5 の自己宣言・監査対象)。

**新設した機構の初回使用者が新設者自身**であり、赤→緑を実個体で通した。現在の有効な免除は
**2 件**で、いずれも判定行に宣言者つきで表示される。

### 8.9 受入結果(確定)

| 項目 | 結果 |
|---|---|
| V1 予防面較正(fixture) | **PASS** — 9/9。F1〜F5 は ECO-033 から判定不変(回帰なし) |
| V2 是正面較正(実在不適合) | **PASS** — 赤→緑を同一個体で実測。加えて免除の可視化が過剰免除 1 件を検出 |
| V3 全検査 | **PASS** — 全 16 検査 PASS。既存 15 は判定不変 |
| V4 CI | **PASS** — run 33308191831・success・headSha `44d2904` 一致 |
| V5 diff 窓 | **PASS** — `9ec716e`→`44d2904` は `allowed_paths` のみ(予測的中) |

ECO-034 を `verified` へ閉じる。

**このクローズが支持しないもの**: use/mention の精度改善(O-1)/ 免除の**質**の保証 /
Phase 2(presentation Gate)/ receipt schema 拡張 / 製品リポへの設置。いずれも別 ECO・別裁定。
