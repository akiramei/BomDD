# Change Order — ECO-055(52-metrics 棚卸しの帰結 — 計器/ログの整理・1-A/2-A/3-A/4-A の束)

> 裁定: user 2026-09-03「推奨案 1-A・2-A・3-A・4-A を採択、1 ECO に束ねて起票」。
> 起点= [52-metrics 全列棚卸し](reports/52-metrics-inventory-2026-09-02.md)(2026-09-02・独立作業単位・修正なし)の
> 裁定点 4 件を /converge で裁定可能な形に整理(2026-09-03・自発起動・round 4→1→0)した帰結。
> **本裁定は起票の承認であり、製造着手は別途の裁定を待つ**(status: filed)。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- 所見の出所: 当方の棚卸し(実文逆引き)+user の判定基準「metric → consumer → decision → observable consequence まで
  辿れない列は計器でなくログ」。独立検査は未実施(templates の変更は verified 昇格時に較正 receipt を要する — C17)。

## 0. 実測(起票根拠)

- **能力記録 → 工程設計の辺が欠損している疑い**(2026-09-02 検出)に対し、52-metrics 全列を棚卸しした結果:
  計器 10 列 / 入力 2 群 / ログ 3 列。棚卸し報告 §1。
- **棚卸し報告の判定 1 件を訂正**(converge round 1): `specified_contract_miss` の消費者は playbook §6.4 の帰属で、
  判断は「BOM を直さず(過剰仕様化しない)manufacturing_miss として fresh 再製造」。**計器として機能している**。
  欠けているのは工場交換・ティア変更の規則だけで、これは実測が単純規則を否定する — 能力差は領域で向きが逆転
  (parse= sonnet 優位 / family= opus 優位・playbook §4.7 注記)・ドメインで非一様(haiku contract miss webapi 3/16・
  saga 0・playbook §5.2 追補)・観測値は検査体制込み。transfer-02 では haiku を工場として採用継続(FINDINGS §11 t2 行)。
- **ログ 3 列**(raw_match / user_rulings / self_reported_s)は治具が書かない手書き列(`grep` method/tools: 該当 0)。
  製品リポでの記入= raw_match(TimetableAdv・LibraryLending)/ user_rulings 0 / self_reported_s 0。
- **timing 系**の使用実績= transfer-02・cli-cad-01・equip-01 の 3 ループ(研究レジームのみ)。製品 3 リポに timing キー 0。
  発見(人間待ち 56%・自己申告 17 倍乖離)は §9・§13 に本文化済み。
- **製品側キー**: ViewPrism2 と LibraryLending が独立に同じ 4 キー(change_miss / impact_prediction /
  unnecessary_modification / regression)を追加(N=2)。正本は既に 61(under-inclusion)・63(不要改変)・register
  (no_impact_prediction)にあり、52 は Phase 5 の計器で ECO レジームの欄を持たない。

## 1. 変更要求(製造対象 — 採択案のみ)

1. **1-A(52 テンプレ)**: `user_rulings` を削除(台帳〔10/20/K-BOM への書き戻し〕から導出可能な転写値 — §13 記録規約)。
   `raw_match` は残し、コメントを「分解 3 列(targeted_fix_success / blocker_diffs / new_unspecified_diffs)の検算用・
   単独報告禁止」へ改める。`self_reported_s` は timing ブロック内に残し 3-A に従う。
2. **2-A(52 テンプレ+playbook §5.2)**: `specified_contract_miss` のコメントに消費先と判断を明記 —
   「§6.4 帰属の計器。判断= BOM を改訂しない(過剰仕様化の防止)・manufacturing_miss として fresh 再製造」。
   playbook §5.2 に 1 文追加 — 「specified_contract_miss と equip 認定は**工場選定の単軸根拠にしない**(能力は領域・
   ドメインで非一様・検査体制込み)。工場選定は現行どおり『別ティアを混ぜる』。equip 認定は最低ライン(適格性)の判定」。
3. **3-A(playbook §11)**: テーラリング表に行を追加 — 「52 timing | S/M: 省略可 | L: 推奨 | 研究(transfer/equip 系): 必須」。
   閾値規則は置かない(§11「先に恣意的な閾値を置かない」・基準線 3 ループ)。
4. **4-A(52 テンプレ+improvements)**: 52 冒頭コメントに「本テンプレは Phase 5(受入・収束)の計器。ECO レジームの
   指標(影響なし予測の under-inclusion・不要改変・回帰)の正本は 61/63/register — 52 へ転写・集約しない」を明記。
   N=2 の 4 キーは OBS として記帳し、3 例目で 52 への ECO 要約欄の要否を判断(製品側キーの棚卸しは製品リポの作業単位)。

採らない(裁定済み): 1-B(3 列全削除)・2-B(charter が equip/contract miss を参照する工場選定規則 — 単軸規則を
否定する実測 3 件)・3-B(人間待ち比率の閾値)・3-C(timing 削除)・4-B(52 に eco_runs 集約 — 二重正本・転写値)・
4-C(製品側キーを方法論側で棚卸し)。

## 2. 影響なし予測(反証可能・製造前に凍結)

- 治具: 52-metrics を読む治具は `stage0-survey.py` のみで、読む列は `stage0_topology_health_check`(本 ECO の変更列外)
  → **治具の判定は不変**(self-conformance 全検査・stage0-survey selftest が緑のまま)。
- 製品リポ: 既存の 52-metrics 記録には触れない(歴史的記録の非消去)。テンプレ変更は bomdd-init の**次回 scaffold から**
  適用され、既存製品の kit は bomdd.lock で凍結(kit-freshness が STALE を advisory で示す — 不適合ではない)。
- playbook: §5.2 と §11 の追記のみ。他節の diff ゼロ。
- 予測が外れる形: stage0-survey が本テンプレの列名を参照していた(→ selftest 赤)/ C13 リンク検査が 52 内の参照に
  依存していた(→ FAIL)。いずれも製造時の self-conformance で観測する。

## 3. 受入(製造着手後)

- V1: self-conformance 全検査 PASS(C13 二文脈・C14 kit-freshness 7/7・stage0-survey を含む)。
- V2: 52 テンプレの diff が 4 項目(user_rulings 削除・raw_match 注記・specified_contract_miss 注記・冒頭の Phase 5 限定)
  のみ — `git diff` の窓を目視+行数で確認。
- V3: playbook の diff が §5.2 と §11 の追記のみ(他節 diff ゼロ)。
- V4: CI 結論 success(対象 revision 一致)。
- V5: 較正 receipt(C17・trigger ①= verified 昇格): 「V1 の緑は本 ECO の変更に対して感度があるか」を問う — 変更列が
  治具の読取列外である以上、V1 は**変更の正しさを証明せず、壊していないことだけを示す**。正しさは V2/V3 の目視と
  本 order §0 の実文逆引きが根拠(限界として明示)。
- verified 後: improvements の OBS(4 キー N=2)を watch 1/3 で登録。

## /preflight receipt(起動経路: 自発 — 既裁定の適用実装〔起票〕)

- 分類= 既裁定の適用実装(厳しい側= continuation)。状態: baseline `c515318`(起票時 HEAD)/ 次番 055= **confirmed**
  (register 直近 054)/ 棚卸し報告の実在= **confirmed**(bomdd/reports/52-metrics-inventory-2026-09-02.md・追跡済み)/
  4 裁定点の user 裁定= **confirmed**(2026-09-03 会話)/ 製造着手の可否= **unknown(理由コード: 裁定待ち)** → status: filed。
- 開始判定: **PROCEED(起票のみ)**・override 0。

## /converge receipt(起動経路: 自発 — 裁定点 4 件の裁定候補合成)

- **判定: 未収束**(round 軌跡: 4→1→0)。上限 3 周で 2 周連続ゼロに未到達。残存指摘は round 3 で解消済みで、
  user 裁定「打ち切り採用(1-A/2-A/3-A/4-A)」により起票へ進む。
- 起動経路: 自発(裁定候補の合成= 設計合成タスク)。
- round 1 = 4 件(①specified_contract_miss は入力でなく計器〔消費者= §6.4 帰属・判断= BOM 非改訂〕②timing は研究レジーム
  3 ループのみ・製品 0 ③製品側 4 キーは N=2 で正本は 61/63/register ④ログ 3 列は治具非依存)/ round 2 = 1 件
  (製品側キーの 52 集約は転写値・二重正本 → 4-B を落とす)/ round 3 = 0 件。
- DoD: 選択肢 2 つ以上+変更対象+起票要否 ✔ / 前提主張の実文裏取り ✔(playbook §5.2/§4.7 注記・FINDINGS §11 t2・
  templates 61/63・register テンプレ・method/tools grep・製品 3 リポの 52 キー)/ 各案の「この値が変わったら何が変わるか」
  一文 ✔ / 推奨と効果の疑いの分離 ✔(推奨案の効果は未測定)。
- 検証した主張: §5.2 の現行文(工場数のみ・選定規則なし)/ equip-01 の非一様性(playbook §5.2 追補)/ haiku 採用継続
  (FINDINGS §11 t2)/ time-decomposition 使用 3 ループ(loops grep)/ 61:87 under-inclusion・63:1 不要改変・register:25
  no_impact_prediction / stage0-survey の読取列(tools grep)。
- 未収束事項: なし(残存 1 件は 4-B の棄却で解消)。
