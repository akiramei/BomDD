# cli-cad-01 — CAD 適格性判定の媒体非依存化: CLI 媒体 N=1(protocol)

> **ステータス**: 設計(2026-07-18 起票・kit 凍結前・実施待ち)。
> **出典**: 2026-07-18 設計裁定(正本= method/improvements.md 2026-07-18 節。提案原文の凍結転記= [external-proposal-20260718.md](external-proposal-20260718.md))。
> **原型**: [transfer-test.md](../../method/onboarding/transfer-test.md)(N=3 実証)・transfer-04(独立受入検査の転移・FINDINGS §11.4)・ui-cad manufacture-01(UI-CAD からの再製造・FINDINGS §10)。
> **統制**: 変える軸は 1 つ — 媒体(UI→CLI)。転移の隔離規律・介入台帳・差分帰属語彙は既存装置をそのまま転用する。

## 1. 仮説(事前登録 — kit 凍結時に本節を凍結し、実施中は改訂しない)

- **H1(CAD 適格性の媒体非依存)**: 「その成果物のみを渡された fresh 製造者が、説明者の介入なしに同じ意味論の製品を製造でき、かつ独立した受入検査を導出できる」という transfer 実測は、UI 以外の媒体(CLI)でも CAD 適格性の判定として機能する。
- **H2(翻訳層の位置予測 — FINDINGS §10 のプロスペクティブ検証 1 例目)**: 職人芸(暗黙判断)は CAD→実装の翻訳層へ移動する。CLI 媒体では divergence(原品と再製品の観測可能な差)が次に集中すると予測する:
  - **P1 出力契約の暗黙次元**: 列順・切り詰め・表示幅・並び順・改行/エンコーディング・空集合時の表示。
  - **P2 終了契約のエラー経路写像**: どの内部失敗をどの exit code に落とすか・不正入力での fail-open/closed。
  - **P3 環境前提**: cwd 依存・パス区切り・console encoding(Windows)・非TTY/リダイレクト時の差。
  - **反予測(落ちにくい)**: コマンド文法の主構造(サブコマンド・フラグ名・主要な状態語彙)— 散文仕様が既存のため。
  - 採点: divergence 全数を帰属分類し、P1〜P3 該当率 **2/3 以上で H2 支持**。

どちらの不成立も報酬である: H1 不成立= CLI-CAD 起票様式の欠陥データ(何が書けなかったか)。H2 不成立= §10 の反証または媒体依存性の発見。

## 2. 題材

**`method/tools/worklist.py`**(improvements.md 追跡項目の走査 CLI)。

選定理由: ①読み取り専用・副作用なし ②入力 1 ファイル+意味論の正本(記帳スキーマ v1)が散文で既存 — CAD 起票が「ゼロからの発明」でなく「散文契約の CAD 化」になり、媒体変換の効果だけを測れる ③終了コード契約が単純(現仕様: 常に 0・--selftest のみ失敗時非 0)④出力面(worklist/actions due/warnings/legacy coverage/stats)が豊富で P1 の検出力がある。

見送り: self-conformance.py(リポ構造への依存が深く kit 隔離が高価)・ui-cad-gate.py / bomdd-init.py(UI 系列・生成系と交絡し「変える軸は 1 つ」を破る)。

## 3. 手順

1. **CLI-CAD 起票**(`cli-cad.md` — 本実験の設計正本): 4 契約+未規定台帳。
   - 文法契約: コマンド・フラグ(--full / show <ID> / --selftest)・引数解釈・既定動作。
   - 出力契約: stdout/stderr の使い分け・各セクションの意味と順序・機械可読性の範囲。人間向け出力は全文一致でなく「見出し・必須フィールド・意味・重要な順序」を契約化。
   - 終了契約: exit code の意味写像と fail-open/closed。
   - 環境契約: 入力ファイルの解決(探索位置・cwd)・encoding・非TTY。
   - **未規定台帳**: 意図的に未規定とする次元を未規定と明記(exploratory probe の測定対象)。
   - 規律: 既存実装の参照は「契約の選定断面の突合」に限定(as-built 丸写しの禁止 — CAD は上流正本)。**起票時に、既存散文(記帳スキーマ v1・スキル文書)に無かった契約の追記行数と内訳を記録する** — CAD 起票自体が第 1 の沈黙掃討であり、この計数が silence-checklist CLI 観点行の実測種になる。
2. **kit 凍結**(commit/tag): cli-cad.md+記帳スキーマ v1 抜粋+合成入力 fixture(正常系・W 系不整合・境界: 空ファイル/マーカー不在/ID 重複/watch 3/3)。**非開示**: worklist.py 本体・本 protocol §1(予測)・FINDINGS・improvements.md 実物。
3. **T1 fresh 製造**: 別ベンダー工場(第一候補= Codex/GPT 系 — transfer-03/04 と同じ隔離規律)。kit のみで再製造。介入台帳は transfer-test §5 様式(全交信・customer_ruling/method_explanation/rescue/tooling_gap+モデル・ハーネス記録)。
4. **受入(black-box subprocess oracle)**: 同一 fixture 集合で原品/再製品を実プロセス起動し (argv, stdin) → (stdout, stderr, exit code) を突合。CLI 内部関数の直接呼び出しは不可(製造と検査の解釈共有を遮断)。
5. **divergence 帰属**: 既存語彙(specified_contract_miss / unspecified_bom_residue / exploratory_unspecified_surface)+P1〜P3 該当のタグ付け。
6. **還元**: unspecified 由来の divergence → silence-checklist §10 CLI 観点行の実測種として /lesson-promote へ。EXP-20260718-01/02 の回収判定・transfer-test.md 新節(candidate)の昇格判定材料。

## 4. 成否基準

- **H1 成立** = oracle 主要 fixture PASS(divergence が unspecified 帰属のみ= CAD が規定した契約は全て転移)+介入分類 method_explanation / rescue が 0。
- **H2 支持** = divergence の 2/3 以上が P1〜P3 領域。
- 付帯測定: CAD 起票の追記行数(手順 1)・介入件数・divergence 件数と帰属分布・工数(time-decomposition 規律 — 壁時計/人間待ち/機械実働の分解・自己申告の無来歴転記禁止)。

## 5. 役割規律(transfer-test §3 の縮約)

- fresh 製造者: kit 参照と製造のみ。kit 外の BomDD 情報参照禁止。
- 観測者: 介入台帳の記録のみ・助言禁止。顧客役は置かない — 契約に関する質問は「その次元は未規定。実装者裁定とし、裁定を記録せよ」で返し、未規定台帳へ追記する(探索プローブの種)。

## 6. 実施条件

kit 凍結 commit が先行条件。実施は別セッション(観測者と製造者の文脈分離)。実施前に §1 の凍結を register へ記録する。
