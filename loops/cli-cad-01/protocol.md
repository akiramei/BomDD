# cli-cad-01 — CAD 適格性の認定試験: CLI 媒体 N=1(protocol・rev2)

> **ステータス**: rev2(2026-07-18 レビュー補正①〜⑥適用)。kit 凍結をもって §1(仮説・予測)と CAD の未規定台帳を凍結する。
> **出典**: 2026-07-18 設計裁定(正本= method/improvements.md 2026-07-18 節+同日レビュー追記。提案原文= [external-proposal-20260718.md](external-proposal-20260718.md))。
> **原型**: [transfer-test.md](../../method/onboarding/transfer-test.md) §8(構成的適格条件+認定試験の二段)・transfer-04(独立受入検査)・ui-cad manufacture-01(CAD からの再製造)。
> **統制**: 変える軸は 1 つ — 媒体(UI→CLI)。隔離規律・介入台帳・差分帰属語彙は既存装置を転用。

## 1. 仮説(事前登録 — kit 凍結時に本節を凍結・実施中は改訂しない)

- **H1(認定試験の媒体非依存)**: CLI 媒体でも、構成的適格条件(transfer-test §8)を満たす CAD 候補に対する認定試験 — ①CAD のみを渡された fresh 製造者が介入なしに **CAD で規定した意味論**の製品を製造できる(**原品同一ではない**)②CAD のみから独立した受入検査を導出できる — が機能する。
- **H2(翻訳層の位置予測 — FINDINGS §10 のプロスペクティブ検証 1 例目)**: 職人芸(暗黙判断)は CAD→実装の翻訳層へ移動する。CLI 媒体では divergence が次に集中すると予測する:
  - **P1 出力契約の暗黙次元**: 列幅・整列・切り詰め・省略記号・空集合時の表示細部・行末処理。
  - **P2 終了契約のエラー経路写像**: どの内部失敗をどの exit code へ落とすか・不正入力での fail-open/closed。
  - **P3 環境前提**: cwd 依存・パス区切り・出力エンコーディング(Windows console)。
  - **反予測(落ちにくい)**: コマンド文法の主構造(サブコマンド・フラグ名・状態語彙)— 散文仕様が既存のため。
- **H2 の判定規則(補正⑤)**: divergence(固定オラクル不合格+探索差分の総数)が
  - **0 件 → H2 未検証**(判定しない — 検出力不足と区別できない)、
  - **1〜2 件 → 記述的所見**(位置の記録のみ・支持/不支持の判定は持ち越し)、
  - **3 件以上 → P1〜P3 該当率 2/3 以上で H2 支持**と判定する。
- どちらの不成立も報酬: H1 不成立= CLI-CAD 起票様式の欠陥データ。H2 不支持= §10 の反証または媒体依存性の発見。

## 2. 題材と一般化限界(補正⑥)

**題材**: `method/tools/worklist.py` 相当の CLI(improvements.md 追跡項目の読み取りビュー)。選定理由: 読み取り専用・入力 1 ファイル・意味論の正本(記帳スキーマ v1)が散文で既存 — CAD 起票が「散文契約の CAD 化」になり媒体変換の効果だけを測れる。見送り= self-conformance.py(リポ構造依存が深い)・ui-cad-gate.py / bomdd-init.py(UI 系列・生成系と交絡)。

**一般化限界(事前宣言)**: 本題材は**非対話・読み取り専用・単一入力ファイルの CLI** に限定される。次の次元は本実験の被覆外であり、CLI 媒体一般への外挿はこれらを除いて行う: **設定優先順位**(引数>環境変数>設定ファイル)・**TTY/非TTY 分岐**・**signal 処理(Ctrl+C/EOF/timeout)**・**対話状態機械**・**副作用 CLI(ファイル生成・変更・削除)**。これらは後続ラウンド(副作用・対話 CLI 題材)で earn する。

## 3. 役割分離(補正①)

| 役割 | 担当 | 入力 | してはならないこと |
|---|---|---|---|
| CAD 設計者 | 本セッション(Claude fable-5) | 記帳スキーマ v1 散文+原品の契約断面突合 | as-built 丸写し(CAD は上流正本) |
| 独立検査官 | 別エージェント(fresh 文脈) | **kit のみ**(CAD+fixtures+work order) | 原品実装・protocol §1・FINDINGS の参照。製造工場との交信 |
| 製造工場 | 別ベンダー fresh(第一候補= Codex/GPT 系) | **kit のみ** | kit 外の BomDD 情報参照。oracle の参照 |
| 観測者 | 本セッション | 全て | 検査官・工場への助言(交信は全て介入台帳へ) |

- **oracle は製造開始前に凍結する**: 検査官が CAD のみから oracle を製造 → commit 凍結 → その後に工場が着手。凍結後の oracle は是正しない(negative control で検出力不足が出ても記録のみ — fail-closed の正直記帳)。
- **交絡の記録**: CAD 設計者と観測者は同一人格(本セッション)。検査官・工場の遮断は隔離ディレクトリ+指示ベースであり物理遮断でない — T0 と同じく「合格は弱く不合格は強い」片側検出器として扱う。各エージェントの provider/model/ハーネスを台帳へ記録(transfer-test §5)。

## 4. 受入の二層(補正②)と negative control(補正③)

1. **固定オラクル(合否)**: 検査官が CAD から導出し凍結した black-box subprocess 検査。fixture 行列に対し (argv, stdin) → (stdout, stderr, exit code) を観測し、**CAD が規定した契約のみ**を assert する。CLI 内部関数の直接呼び出しは不可。原品・再製品の両方に同一 oracle を実行する(原品の不合格も隠さず記録 — CAD/原品乖離の実測)。
2. **探索差分(観測)**: 原品と再製品の出力を fixture ごとに直接 diff し、**CAD 未規定次元の値の差**を採取する。合否には使わない — 全件を帰属分類(P1〜P3 該当・specified_contract_miss / unspecified_bom_residue / exploratory_unspecified_surface)して H2 の材料にする。
3. **negative control(故障変異体)**: 原品のコピーへ既知の故障 5 種(終了契約違反・区分混同・stats キー欠落・W1 検出除去・除外領域無視)を注入し、**oracle が各変異体を FAIL にする**ことを確認する。変異の適用自体を先に assert する(変異体の出力が原品と実際に異なることの確認 — OBS-20260716-07「変異未適用の偽陰性」対策)。oracle が変異体を PASS させた場合は検出力の限界として記録する(凍結後の是正はしない)。

## 5. 台帳規律(補正④)

- **CAD の未規定台帳は実験中不変**: kit 凍結後、未規定台帳への追加・変更・削除を行わない。
- **factory assumption 台帳**(loops/cli-cad-01/factory-assumptions.md): 製造工場が置いた仮定・解釈・質問は CAD へ反映せず本台帳へ記録する。実験後の還元で「CAD 改訂候補(規定すべきだった)/未規定のままでよい(実装裁量)」に裁定する。
- **介入台帳**(loops/cli-cad-01/intervention-ledger.md): 全交信を transfer-test §5 分類(customer_ruling / method_explanation / rescue / tooling_gap)で記録。契約に関する工場からの質問には「その次元は未規定。実装者裁定とし assumption 台帳へ記録せよ」で返す(顧客役は置かない)。

## 6. 手順

1. **CLI-CAD 起票**(kit/cli-cad.md): 文法/出力/終了/環境の 4 契約+権威境界宣言+未規定台帳。既存散文(記帳スキーマ v1)に無かった契約の追記量と内訳を記録(**CAD 起票自体が第 1 の沈黙掃討** — silence CLI 観点行の実測種)。
2. **kit 凍結**(commit+tag): cli-cad.md+schema-excerpt.md+work-order.md+fixtures/。非開示= 原品 worklist.py・本 protocol・FINDINGS・improvements.md 実物・oracle(工場に対して)。
3. **oracle 製造・凍結**(検査官・工場着手前)。
4. **negative control**(観測者: 変異体 5 種で oracle 較正)。
5. **T1 fresh 製造**(工場・隔離ディレクトリ・kit のみ)。
6. **受入**: 固定オラクル(原品/再製品)+探索差分+帰属分類。
7. **報告**: report.md(H1/H2 判定・介入台帳・assumption 台帳・工数の分解記録)→ /lesson-promote で還元(silence CLI 観点行・EXP-20260718-01/02 の回収判定・transfer-test §8 candidate の昇格材料・見送り中の織り込み案B/C の再裁定)。

## 7. 成否基準

- **H1 成立** = 再製品が固定オラクル PASS(不合格が残る場合、全て CAD 未規定次元への oracle 側過剰 assert と裁定されること)+介入分類 method_explanation / rescue が 0。
- **H2** = §1 の段階規則(0=未検証/1〜2=記述的所見/3+で 2/3 判定)。
- 付帯測定: CAD 起票の追記量(手順 1)・介入件数・divergence 件数と帰属分布・negative control 検出数(5 変異中)・工数(壁時計/人間待ち/機械実働の分解・自己申告の無来歴転記禁止)。
