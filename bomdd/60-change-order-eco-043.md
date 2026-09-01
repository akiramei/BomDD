# Change Order — ECO-043(calibrate 非起動 gate — verified 昇格時の較正 receipt 検査・trigger ① 限定)

> 裁定: user 2026-09-01(calibrate 非起動の初実測への 6 点裁定)—「calibrate 非起動 gate の
> 設計 ECO を起票してよい。ただし初期 scope は trigger ① だけとする」「初期 gate のアンカーは
> 『ECO verification 節を書くこと』ではなく『**ECO を verified へ昇格させる状態遷移**』とする」。
> **gate ① 承認待ち — 製造は本 order の提示で停止する。**

## 担当設備(equipment)

- 設計・起票:
  - requested: `claude-fable-5`
  - resolved: `claude-fable-5`
  - ハーネス: Claude Code(Claude Agent SDK)
  - 来歴: **self-reported**

## 0. 実測(起票根拠・2026-09-01)

- **calibrate 非起動の初実測**(EXP-20260831-04 第 4 回観測): 2 ECO 弧 / 3 trigger
  opportunity / 2 trigger class。**機械検出 0・発見は人間の質問** — converge 非起動 2 回
  (ECO-033 の起票根拠)と同一の検出器・同一の機序(OBS-20260828-02)。
- **対照条件**: 較正掃引 3 回(題材指定= 人間裁定起動)は 3/3 起動 — 自発起動が要る通常作業へ
  戻った最初の 2 弧で 0/3。起動率は起動経路に強く依存する。
- ECO-035 のスコープ外宣言「非起動の機械観測(C16 同型)は必要が実測されてから判断」の
  **実測が立った** — 本 ECO はその実施にあたる(converge が ECO-032 → 非起動実測 → ECO-033 と
  辿った道の calibrate 版)。
- 前例装置: C16(converge receipt ゲート・ECO-033/034)— 較正 fixture・根拠つき免除・
  フェンス非対称・免除の件数表示という設計資産が既にあり、同型で流用できる。
- 天然の既知個体: **本 ECO 起票と同弧で債務返済した ECO-041/042** — 返済前の order blob
  (較正 receipt なしの verified)がハッシュ固定の known-bad、返済後が known-good の対になる。

## 1. 変更要求(gate ① 承認後に製造)

### (a) C17 新設: verified 昇格時の較正 receipt 検査【trigger ① 限定】

- **アンカー(裁定 4)**: 「受入節を書くこと」ではなく「**register 上で status: verified へ
  昇格した状態遷移**」。検査は self-conformance 実行時に register の verified エントリを走査 —
  規律上 verified 化は accept commit で行われ、commit 前検査+CI が結線済みのイベントである。
- **predicate**: 適用範囲内の verified エントリごとに、order_ref の実文へ
  **較正 receipt マーカー**(`較正 receipt` / `calibrate receipt`)**または根拠つき免除宣言**
  (`<!-- calibrate: not-required reason: <非空> decided-by: <非空> -->`)を要求。どちらも
  無ければ FAIL。
- **免除様式(C16/ECO-034 の継承)**: reason+decided-by の 2 点必須 / 免除を与える文は
  コードフェンス内では読まない(過剰免除= fail-open の防止)/ 有効な免除は**件数と宣言者
  つきで毎回表示**(沈黙する免除を作らない)。
- **検出力の限界(コード恒久宣言)**: (1) receipt の構造的存在しか測らない(battery を
  本当に当てたかは測らない)(2) trigger ②(緑の引用)・③(検査器新設)・④(インシデント後)は
  被覆外 — trigger ① gate が**最後の防波堤**(裁定 5)(3) artifact に落ちない査定は被覆外。

### (b) 適用範囲【裁定対象】

- **A-1(推奨)**: **ECO-041 以降**(ID 数値比較)。債務返済済みの 041/042 が最初の適用個体
  かつ天然対照になり、遡及の書き換えは不要(040 以前は対象外 — 歴史的記録の非消去)。
- A-2: ECO-043 以降(新弧のみ — 天然対照を捨てる)。

### (c) 変更しないもの(裁定 5・6 の凍結)

- **calibrate 本文・battery は無変更**(今回は査定能力でなく工程投入の欠陥)。
- **trigger ③ の機械 classifier は作らない**(OBS-20260901-04 で watch 継続)。

## gate ①(製造承認)

**承認待ち。** 裁定対象= ①製造承認 ②(b) 適用範囲(A-1 推奨)③免除様式・限界宣言の文言。

## スコープ外(宣言済み境界)

- trigger ②③④ の機械観測(③= OBS-20260901-04 watch・②④= 実測待ち)。
- preflight receipt の同型 gate(preflight は V6 初回実使用すら未実施 — 運用実測が先)。
- 製品リポ process-validator 側への設置(ECO-033 と同じ分離 — BomDD 実測後に別裁定)。

## 2. 影響なし予測(反証可能・製造前に凍結)

- diff は `method/tools/self-conformance.py`+台帳系のみ。既存 C1〜C16 の判定不変。
- **適用範囲内の現況**: ECO-041/042 は債務返済済み(較正 receipt あり)につき、導入時点で
  FAIL 0 の見込み — 天然対照は git show の返済前 blob で赤を実測する(ECO-012 V2 の様式)。
- C16 は本 order を required と判定する見込み — receipt 埋め込み済み。

## 3. 較正と受入(起票時凍結・細部は gate 裁定後)

- **fixture(予防面)**: F1= verified+receipt → PASS / F2= verified+なし → FAIL /
  F3= filed・applied+なし → PASS(verified のみ対象)/ F4= 根拠つき免除 → 受理+宣言者表示 /
  F5= フェンス内の免除宣言 → 無効(F9 教訓)/ F6= reason 空 → FAIL。
- **天然対照(是正面)**: `git show <返済前 blob>` の ECO-041/042 order(較正 receipt なし・
  verified)で FAIL 発火をハッシュ固定で実測(合成でなく実在した不適合 — OBS-20260725-02)。
- **受入**: V1= fixture 全数一致 / V2= 天然対照の赤+現況の緑(赤→緑を実個体で)/
  V3= 全検査 PASS・既存判定不変 / V4= CI 緑 / V5= diff 窓。

## /converge receipt(本設計に適用 — 起動経路: 人間裁定〔6 点裁定〕+自発〔設計詳細化〕)

- **判定: 収束**(round 軌跡: 2→0→0)。
- 周回数と新規指摘: round 1 = 2 件(適用範囲を A-1 とし債務返済個体を天然対照に転用する設計 /
  「verified のみ対象」の F3 fixture — filed/applied を巻き込むと起票途中の order が偽陽性に
  なる= C16 初版の轍)/ round 2 = 0 / round 3 = 0。
- 検証した主張(要点): 非起動の実測= EXP-20260831-04 第 4 回(本弧で記帳)/ C16 の設計資産
  (fixture 9 種・免除様式・フェンス非対称)= `self-conformance.py:883-1010` 実読 /
  verified 化が accept commit で行われる運用= ECO-034〜042 の実績 / 返済前 blob の存在=
  本弧の git 履歴。
- 未収束事項: なし。

## 4. 製造と受入の実測

(gate ① 承認後に記入)
