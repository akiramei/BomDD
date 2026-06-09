# Phase 3 — BOM・工程設計(設計者 AI への指示)

典拠: `method/bomdd-playbook-v1.md` §4。入力: `bomdd/20-spec.md`(G2/G2' 通過済み)。テンプレ: `method/templates/30〜42`。

## 手順(順序が重要)
1. **E-BOM**(`bomdd/30-ebom.yaml`): 核/表面の型分け。核は requirement_refs、表面は external_source_ref 必須。横断部品には owner/consumers。**粒度規準**: 部品は「独立に再製造・交換でき、単独で受入できる最小単位」で切る(迷ったら「この部品だけ fresh factory に再製造させられるか?」)。NFR は `nfr_targets`(測定可能な目標値)として置く(実現=M-BOM / 検証=Control Plan の三分割)。
2. **FMEA+沈黙掃討第2回**: 部品ごとに故障モード列挙(Phase 1 の反例を種に)。`method/silence-checklist.md` **全行**を3択宣言(specified / exploratory / out-of-scope)し、`32-mbom.yaml` の `silence_sweep` に記録。第1回掃討の `deferred-to-phase3` 行もここで必ず3択に解消する。**未宣言行・deferred 残りを残さない**(N=3 で分散は常に沈黙箇所に出た)。
3. **K-BOM 調達**(`bomdd/31-kbom.yaml`): 表面部品ごとに、**新しいクリーンなサブエージェント**に問う:
   > 「この領域(例: REST エラー設計)を BOM 記載なしで実装するとき、あなたが慣習で埋めるであろう判断をすべて列挙せよ」

   (=ずる報告の事前実行)。列挙された判断をユーザーと裁定し、固定するものを `managed_knowledge` に、固定しないものを exploratory に。
4. **オラクル・ファースト**(製造より先・設計者側のみ):
   - `bomdd/33-control-plan.yaml`: 特性ごとに深さ・許容差・治具・承認者。核=unit(exact, 丸め規定込み)。同期/座標系=L3。知覚=G+承認者。L0 既定不採用。
   - `bomdd/41-fixed-oracle.yaml`: 仕様化済み契約だけの固定シナリオ。**期待値はすべて仕様から導く**——書けない行は仕様の穴なので Phase 2 へ差し戻す。等価規則(compares/ignores)を明記し、検査器自身の L0 過剰結合を防ぐ。完成したら commit/tag で**凍結**(収束ループ中は不変)。
   - `bomdd/42-exploratory-probes.yaml`: exploratory 宣言行の観測プローブ(合否に入れない)。
   - 受入ハーネス(治具)を実装する場合は製品と同格に repo 管理。
5. **M-BOM / Routing / Work Order**(`32/34/40`): 受入3条件(完全性・無矛盾性・Control Plan 列)。**調達部品**(依存パッケージ)を `procurement` に全列挙(版・選定理由・代替可否。列挙外の採用はずる報告対象と work order に明示)。完全性が要る特性には `test_vectors`(境界値・中間値・反例)を列挙。Work Order に重点ずる報告次元(exploratory 行)を列挙。

## ゲート G3 — ドライラン(BOM 自己完結性)
**設計文脈を持たない fresh サブエージェント**に製造パッケージ(20/30–34/40 の内容のみ。**41/42 とこの会話は渡さない**)を読ませ、問う:
> 「この入力だけで製造に着手できるか。着手前に必要な質問をすべて挙げよ」

返ってきた質問=BOM の穴。exploratory 宣言済み以外の質問がゼロになるまで補正する。通過したら Phase 4(`phase4-manufacture.md`)へ。
