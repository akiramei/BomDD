# Phase 3 — BOM・工程設計(設計者 AI への指示)

典拠: `method/bomdd-playbook-v1.md` §4。入力: `bomdd/20-spec.md`(G2/G2' 通過済み)。テンプレ: `method/templates/30〜43`。

## 手順(順序が重要)
順序と担当の正本は playbook §4.6「Phase 3 の順序と担当」(ECO-114)— 本節はその写しで、食い違えば正本が優先。部品と組み立て方が決まる前に Control Plan は作れない。
担当: 手順 1〜3 = 設計者(設計 AI が案を作り、人が裁定する)/ 手順 4〜6 = 統括 AI / 固定オラクルと探索プローブ = 設計者側。

1. **E-BOM**(`bomdd/30-ebom.yaml`)— 設計者: **部品分けと外向きの約束**(`interfaces` の `IF-`。別の E 品目や製品の外の利用者が当てにする境界だけ — playbook §4.1「外向きの約束」)を含めて作り、人が版の確定とともに裁定する。核/表面の型分け。核は requirement_refs、表面は external_source_ref 必須。HTML モックから UI-IR / UI-BOM を作った場合は `ui_sources` に参照を置き、UI-BOM の候補を E-BOM item / display contract / Control Plan 候補へ裁定する。原典あり UI/帳票 surface は `display_contracts` に表示要素集合を転記し、各 DE を E-BOM item と Control Plan へトレースする。横断部品には owner/consumers。**粒度規準(candidate・playbook §4.1)**: E-BOM 品目は仕様責任者に理解できる機能・責務で切り、受入観点が閉じる単位にする(`method/contracts/bom-granularity-guide.md` — クラス・ファイル・DOM の一覧にしない)。「独立に再製造・交換でき、単独で受入できる最小単位」は M-BOM unit 側の規準(迷ったら「この unit だけ fresh factory に再製造させられるか?」)。NFR は `nfr_targets`(測定可能な目標値)として置く(実現=M-BOM / 検証=Control Plan の三分割)。
   - **Design System BOM**(`bomdd/35-design-system-bom.yaml`): UI-CAD が要求する Card / CTA / Chip / Badge / IconButton / SectionHeader / HelpBox / DragHandle を E-DESIGN-* と K-DESIGN-* に分ける。UI-BOM の surface item ごとに `coverage_matrix` を埋め、`missing` のまま製造へ進めない。
2. **FMEA+沈黙掃討第2回**— 設計者: 部品(E 品目)ごとに故障モード列挙(Phase 1 の反例を種に)。FMEA の行は `ebom_ref` に E 品目を書き、`unit` と `targeted_by` は手順 4・5 で埋める。`method/silence-checklist.md` **全行**を3択宣言(specified / exploratory / out-of-scope)し、`32-mbom.yaml` の `silence_sweep` に記録。第1回掃討の `deferred-to-phase3` 行もここで必ず3択に解消する。原典あり UI/帳票 surface の `表示要素集合・原典表示パリティ` は specified または理由付き out-of-scope にし、exploratory のまま製造へ渡さない。**未宣言行・deferred 残りを残さない**(N=3 で分散は常に沈黙箇所に出た)。
3. **K-BOM 調達**(`bomdd/31-kbom.yaml`)— 設計者: 表面部品ごとに、**新しいクリーンなサブエージェント**に問う:
   > 「この領域(例: REST エラー設計)を BOM 記載なしで実装するとき、あなたが慣習で埋めるであろう判断をすべて列挙せよ」

   (=ずる報告の事前実行)。列挙された判断をユーザーと裁定し、固定するものを `managed_knowledge` に、固定しないものを exploratory に。
4. **M-BOM**(`bomdd/32-mbom.yaml`)— 統括 AI: 製造単位と、各単位の**部品規格** `part_standard`(`provides` / `requires`。外向きの約束は `ruled_ref: IF-…` で指すだけ・
   外向きでない境界は `statement`。playbook §4.5「部品規格」)と `mbom.assembly`。受入3条件(完全性・無矛盾性・Control Plan 列)。**調達部品**(依存パッケージ)を
   `procurement` に全列挙(版・選定理由・代替可否。列挙外の採用はずる報告対象と work order に明示)。各単位の項目がそろい、G3 の A1 が成り立つことを確かめる
   (外向きの約束を足す・変える必要が出たら人へ戻す — playbook §4.5 P3)。
5. **Control Plan とオラクル・ファースト**(製造より先)— Control Plan は統括 AI、固定オラクルと探索プローブは設計者側:
   - `bomdd/33-control-plan.yaml`: 特性ごとに深さ・許容差・治具・承認者。核=unit(exact, 丸め規定込み)。同期/座標系=L3。知覚=G+承認者。L0 既定不採用。
     各単位の `acceptance_refs` と `mbom.assembly.acceptance_refs` をここで埋める。部品規格の項目を測る行は `part_standard_refs` に挙げ、すべての `provides` が
     その単位の行のどれかに挙げられること(playbook §4.5 C1)を確かめる。完全性が要る特性には `test_vectors`(境界値・中間値・反例)を列挙。
   - 原典あり UI/帳票 surface は表示パリティ特性を Control Plan に追加する。pixel-exact ではなく、仕様化した required elements の存在・意味一致を検査する。
   - Design System BOM を使う場合は、design parts の presence / variant / state / application を Control Plan 行にする。Card や Chip が素の Border/Text に退化する差分は S2 以上として検出する。
   - `bomdd/41-fixed-oracle.yaml`: 仕様化済み契約だけの固定シナリオ。**期待値はすべて仕様から導く**——書けない行は仕様の穴なので Phase 2 へ差し戻す。原典あり UI/帳票では、凍結後に原典を直接見て期待値を補わない。等価規則(compares/ignores)を明記し、検査器自身の L0 過剰結合を防ぐ。**凍結前に治具セルフテストを必ず通す**(判定ヘルパ・デシリアライザ挙動を合成データで検証。フォワードは原版が無く治具が未検証のまま初回採点になる)。完成したら commit/tag で**凍結**(収束ループ中は不変)。
   - `bomdd/42-exploratory-probes.yaml`: exploratory 宣言行の観測プローブ(合否に入れない)。
   - 受入ハーネス(治具)を実装する場合は製品と同格に repo 管理。
6. **Routing / Work Order**(`34/40`)— 統括 AI: Work Order に重点ずる報告次元(exploratory 行)を列挙。UI-CAD 案件では `43-visual-gap-analysis.md` を Phase 5 の必須検査として指定する。

## ゲート G3 — ドライラン(BOM 自己完結性)
ドライランの前に、統括 AI が playbook §4.6 G3 の **A1 構造の解決**(7 節)と §4.5 の C1 を確かめ直す。落ちれば BOM が不完全で、G3 は通らない。
**設計文脈を持たない fresh サブエージェント**に製造パッケージ(定義の正本= playbook §4.6: 20/30–34/40・UI-CAD 案件は 35 も。**41/42 とこの会話は渡さない**)を読ませ、問う:
> 「この入力だけで製造に着手できるか。着手前に必要な質問をすべて挙げよ。各単位を、その部品規格と `acceptance_refs` の Control Plan の行だけで単独に受け入れられるか」

返ってきた質問=BOM の穴。exploratory 宣言済み以外の質問がゼロになるまで補正する。通過したら Phase 4(`phase4-manufacture.md`)へ。
