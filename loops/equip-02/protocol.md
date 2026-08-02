# equip-02 — claude-opus-5 の P2 セル プロスペクティブ測定(webapi-02 多工場プロトコルへの行追加)

- 起票: 2026-08-02
- 承認: maintainer 指示(2026-08-02 セッション)「あなたの提案を採用します。Opus 5 の性能を測るのに
  有意義な検証を計画し、実行してください」— 本ラウンドの設計・実行の承認として記録する。
- 状態: **凍結**(本 commit 以降、製造開始後にプロトコル本文を変更しない。変更が必要になったら
  逸脱として measurements へ正直記載する)

## 1. 目的と位置づけ

equip-01(FINDINGS §13)で claude-opus-5 は **n=3(P5 のみ)・判定不能**、識別は trailer 頼み
(交代無記録)だった。本ラウンドは:

1. **P2(固定 BOM からの製造)セルへ claude-opus-5 の行を追加**する。P2 は equip-01 で唯一の
   同一クラス多設備比較データ(webapi-02: opus-4.8= 0/16 / sonnet-4.5= 1/16 / haiku-4.5= 3/16 —
   出典は BomDD-WebApi-Sample loops/webapi-02/as-built.yaml・機種名は as-built 記載を正とする)。
2. equip-01 の**記録欄仕様を最初からプロトコルへ入れる**(EXP-20260802-03 の適用実測):
   工程分類/requested・resolved・harness・prompt bundle/時間分解/差戻・介入・範囲外の
   3 カウンタ/費用(取得不能なら unknown)。
3. 測定は**実在の凍結測定系の再利用**であり、新規の人工課題を作らない(webapi-02 の BOM・
   オラクル・採点規約は一切変更しない)。

**採らないもの**: 本ラウンドから routing 規則・認定・率の統計的判定は導出しない
(equip-01 protocol の凍結裁定を継承)。結果は観測として記帳する。

## 2. 題材(凍結済み測定系)

- リポ: BomDD-WebApi-Sample(ローカル C:\Users\akira\source\repos\BomDD-WebApi-Sample)
- 入力 BOM: tag `webapi-02-input-bom` → **commit 4eed25f**(git 実測)。
  **正直記載**: 既存 as-built.yaml / report.md は入力 commit を `abfd667` と記すが、現タグの
  指示先は 4eed25f — 不一致を観測として記録する(本ラウンドはタグの現指示先を正とする。
  歴史記録の改竄はしない)。
- 供与物(前ラウンドと完全同一の様式): tag 時点の `bomdd/01-ebom.yaml` `02-kbom.yaml`
  `03-mbom.yaml` `04-control-plan.yaml` `05-routing.yaml` + `work-order-webapi-01.md` のみ。
- 非開示: 原版 `src/` `test/` `openapi/`・他工場成果物・`result-*.json`・報告書類。
- 採点器(ループ間不変): `loops/webapi-01/blackbox-oracle.ps1`(固定オラクル層・16 シナリオ)/
  `loops/webapi-02/exploratory-probe.ps1`(探索プローブ層・合否非混在)。

## 3. 設備構成の記録(ECO-028 欄様式の実験への適用)

- 製造設備: requested= Agent tool `model: "opus"`(ハーネス別名。セッション環境の定義では
  最新 Opus= claude-opus-5)/ resolved= 工場の自己申告を記録(**self-reported・証明ではない**。
  申告不能なら unknown のまま埋めない)
- ハーネス: Claude Code Agent tool subagent(親セッション= claude-fable-5)
- 主観察者(記帳・採点・commit): claude-fable-5 — **採点者は製造と別系統**(equip-01 の
  「fable が fable を採点」限界の部分改善)。ただし採点の大半は機械(固定オラクル突合)。
- git trailer 交絡の事前宣言: 本リポへの commit は親セッションの trailer(Fable 5)が付く。
  **trailer は製造設備の証拠にならない** — 製造設備の正本記録は本ファイルと measurements とする。
- 検査官: 機械オラクル+主観察者突合(独立 AI 検査官は本ラウンド不使用 — P2 の合否は
  ブラックボックス HTTP 契約突合で客観化されているため。限界として記録)。

## 4. 隔離

- 工場には新規 workspace(セッション scratchpad 配下)に複写した供与物のみを与える。
- 工場への指示: workspace 外のパスへアクセスしない。原版・他工場の存在は開示しない。
- **限界の事前宣言**: 隔離は指示ベースであり機械的強制はない(前ラウンドと同等)。工場の
  作業報告から範囲外アクセスの申告を確認し、範囲外カウンタへ記録する。

## 5. 手順(事前登録)

1. V0 ヤードスティック健全性: 原版(リポ HEAD の src/)を起動しオラクルを実行、コミット済み
   `loops/webapi-02/result-original.json` と status/code が一致することを確認(不一致なら停止)。
2. 製造: 工場 subagent を起動(prompt bundle は `prompt-bundle.md` に全文+sha256 で凍結)。
   冒頭でモデル自己申告を求める。介入 0 を原則とし、行った介入は全て記録する。
3. 受入: `dotnet build` → API 起動 → 固定オラクル 16 シナリオ → 原版と 2-way diff
   (status/code のみ。ID 値・extra の server 依存値は比較しない — 前ラウンド規約)。
4. 探索プローブ: 観測のみ(合否非混在)。
5. 記録: measurements.md へ全欄記入 → BomDD へ commit(self-conformance 合格を条件に)→
   push → CI 結論を 4 値判定で記録(ECO-020 規律)。

## 6. 事前予測(反証可能な形で)

- H-e2-1: **固定オラクル層 0/16**(「締めた BOM は能力ある工場へ転移する」— webapi-02 の
  capable factory transfer の新機種への外挿)。1 件以上の差分が出た場合は 3 分類
  (能力/未規定残渣/その他)で帰属する。
- 探索層は予測を固定しない(分散の観測が目的)。
- 時間・費用: 予測なし(初のプロスペクティブ時間記録が目的)。

## 7. 測定項目(記録先= measurements.md)

fixed_oracle_diff(/16・分岐の実値と帰属)/ 探索 5 次元(ID 形式・別 key 同 ID・startUtc echo・
createdAtUtc・cancelledAtUtc)/ build 結果 / cheat 報告数 / 時間分解(壁時計・製造/受入の区間)/
介入・差戻・範囲外の 3 カウンタ / 費用(unknown 可・推定禁止)/ resolved 来歴。
