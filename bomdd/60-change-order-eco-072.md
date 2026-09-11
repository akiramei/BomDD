# Change Order — ECO-072(ECO-062 Phase 7 第 1 弾: 設備台帳の属性化+独立性判定の機械化 — 独立検査として成立しない組合せを入口が弾く〔filed〕)

> 裁定: user 2026-09-12「ECO-062 を再開して。Phase 7 を DISCUSS から」→ DISCUSS(thesis: 第 1 弾は設備台帳の属性化+独立性判定に絞る・P6-02 は第 2 弾・裁定キューは保留)に
> user AGREE。**起票のみ**(製造裁定は別 DECIDE・範囲の凍結は裁定時)。親= [ECO-062](60-change-order-eco-062.md) §7 Phase 7(入口= Phase 6+設備認定台帳の属性化・
> 成果物= stop_type→配送先の機械定義〔ECO-067 で済〕+独立性判定の機械化〔§1-5〕・出口= **独立検査として成立しない組合せを機械が弾いた実測 1 例**)。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**。製造・検査官は製造裁定で配員(本 ECO の対象そのもの)。

## 0. 実測(起票根拠)

- **設備台帳は機械可読の形で存在しない**: `bomdd/` に設備台帳ファイル 0(ls)。設備認定 equip-01〜03 は improvements.md と loops の散文。order「担当設備」欄は事後記録・
  self-reported(ECO-062 §5.4 の欠落 F2= `required_capability` が設備認定 ID を参照する欄がない)。
- **入口は executor を識別しない**: `bomdd-run.py --cell` は cell を文字列で shell 起動し、run 台帳に残るのは cell 文字列と exit のみ(ECO-067 §1 の範囲)。製造者と検査官が同一設備でも
  入口は止められない(Phase 6 実 cell N=1 は Codex read-only で当方が手で選んだ)。
- **独立性は宣言属性の照合でしか判定できない**(実測): Grok 公式「Do not use separate Bots as a security boundary」(ECO-062 §10.1 確認済)/ モデル名記録の系統的欠落
  (EXP-20260711-05 再演 4 回)/ 製造担当モデルは maintainer 申告のみ(ViewTube)。→ 機械が弾けるのは「宣言上同一」までで、属性ごとの**来歴**(self-reported / harness-measured /
  user-declared)を台帳が持たないと偽の独立を通す。
- **設備属性が検出力を左右した実測**: Codex read-only sandbox の temp 不能(TEMP_UNAVAILABLE・Phase 6 §10.7)/ workspace-write と read-only で cell 挙動が違う(Phase 5 P5-05・P5-06)/
  pwsh -Command の exit 丸め(P5-07)。OBS-20260910-03 は 3/3 で playbook §3 に「実行環境の差を設計項目に」として織り込み済(f3974c9)・templates は ECO-069。→ sandbox モード・
  temp 可否・exit 伝播は台帳属性の候補。
- **独立性の評価軸(§1-5)**: 同一モデル / ハーネス / fixture / oracle / 前提。機械照合できるのはモデル・ハーネス・アカウント系統の 3 軸。fixture・oracle・前提は round ごとの宣言
  (検査ブリーフの range・環境欄= ECO-069)で、台帳属性ではない。

## 1. 変更要求(候補 — 製造裁定で凍結)

1. **設備台帳** `bomdd/70-equipment.yaml`(新規・register と同格の台帳・手書き正本): entry= `id`(EQ-NNN)・`kind`(ai-model / human)・`model`・`harness`・`account_lineage`
   (同一ユーザー/同一 API 所有者の系統)・`sandbox_modes`(利用可能なモード)・`temp_available`(モード別)・`exit_propagation`(丸めの有無)・`qualification_ref`(equip-01〜03 / loop・
   なければ unqualified)・**各属性の来歴** `provenance`(self-reported / harness-measured / user-declared)・`status`(active / retired)。初期エントリ 3: 当方(claude-fable-5-1 @ Claude
   Code)・Codex(gpt-5.6-sol @ Codex CLI・read-only/workspace-write・read-only は temp 不能)・人間運転員(run-02)。初期値の来歴はすべて self-reported/user-declared(harness-measured 0 を明記)。
2. **order の配員欄**: `templates/60-change-order.md` の「担当設備」に `producer: EQ-NNN` を、検査官行に `inspector: EQ-NNN` を追加(自リポの新規 order も同様)。job 射影
   (`bomdd-job.py`)が order からこれを読み `required_capability` に解決(台帳に無い ID → 既存の停止語彙で止める・新語彙を増やさない)。
3. **独立性判定(入口)**: `bomdd-run.py --cell` に **`--executor EQ-NNN` を必須**にする(無ければ起動しない・fail-closed)。判定は宣言属性の照合: (a) producer と executor が同一 `id`
   → STOP (b) `model`・`harness`・`account_lineage` の 3 軸がすべて一致 → STOP(独立検査として不成立)(c) 3 軸のいずれかが台帳で `unknown` → STOP(照合不能を通過にしない)。
   新 stop code **`INDEPENDENCE_FAIL`**(配送先 operator= 配員のやり直し)を DELIVERY 表に追加。判定行は 1 行(`STOP INDEPENDENCE_FAIL(producer=EQ-001 executor=EQ-001 axes=id)`)。
4. **selftest 腕**: 同一 id / 3 軸一致(別 id)/ 異系統 → ADVANCE / `--executor` 欠落 / 未知 id / 台帳欠落・不正 / 軸 unknown。
5. **受入**(候補): **V1** selftest 全腕。**V2(出口条件)**: 実入口に producer と同一 executor を与えて STOP、異系統(Codex)を与えて ADVANCE→起動、を実 cell で 1 回ずつ実測(known-bad
   1 例+陽性対照 1 例)。**V3** self-conformance・CI・diff 窓。**V4** 異系統独立検査(Codex・range と実行環境の差をブリーフに宣言= ECO-069 の欄)。**V5** 較正 receipt(trigger ①③)。

**採らない**(起票時点): 台帳を register に埋め込む(二重正本)/ executor の自動検出(ハーネス計測は unknown を許し、来歴欄で区別する)/ 独立性の**実効**の主張(判定は宣言上の照合まで —
Grok 公式の境界)/ fixture・oracle・前提の機械照合(round ごとの宣言に留める)/ P6-02(cell 判定の receipt 回収= 第 2 弾)/ 裁定キュー(失敗未観測・保留)/ product-profile 配布(別 ECO)。

## 2. 影響なし予測(製造前・起票時点 — 製造裁定で凍結)

範囲 A(§3)なら diff= tools 2(bomdd-job.py・bomdd-run.py)+新規 yaml+templates/60-change-order.md 検査官行+自リポ order 1〜2 通の配員欄+台帳系。self-conformance: C4/C14(kit 鮮度)は
templates 変更で advisory・C7 不変・C13 は新 yaml へのリンク実在・tools の selftest は C11 系の対象外(自己 selftest で担保)。既存 ECO の job ビューは配員欄が無くても壊れない
(欄なし= required_capability null・従来どおり)ことを V1 に含める。hooks・.github diff 0。

## 3. 製造裁定の候補(別 DECIDE で提示)

- **A** 台帳+配員欄+入口判定+selftest(§1 の 1〜4 すべて・出口条件を満たす最小の完全形)。
- **B** 台帳+入口判定のみ(§1 の 1・3・4。producer は `--producer EQ-NNN` で運転員が宣言・job 射影と templates は第 2 弾)。
- **C** 台帳のみ(判定は人間・機械化は次 ECO)。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-072` の出力を開始 artifact として読んだ)

- 分類= 新規機能(親 ECO-062 の Phase 7・DISCUSS→AGREE 済)。baseline `58205be`= **confirmed** / 次番 072= **confirmed**(grep 0)/ Phase 6 出口の成立= **confirmed**(ECO-067 verified・
  実 cell N=1・user 裁定で Phase 7 入口)/ 設備台帳の不在= **confirmed**(ls)/ 入口の executor 非識別= **confirmed**(bomdd-run.py 実読)/ 同一ファイルへの進行中 ECO なし= **confirmed**
  (ECO-067/068 は verified)。
- job ビュー: required_skills= `["calibrate", "preflight"]`・skills_missing= `["calibrate"]`(order 生成後に出力)
- 開始判定: **PROCEED(起票のみ)**・override 0。製造は裁定後。

## 4. 製造と受入の実測

- (製造裁定後に記入)
