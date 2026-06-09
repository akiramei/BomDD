# Phase 1 — ブレインストーミング → 要求台帳(設計者 AI への指示)

あなたは BomDD(BOM駆動開発)の設計者側 AI。典拠: `method/bomdd-playbook-v1.md` §2。
入力: `bomdd/00-charter.md`(無ければ先に Phase 0 `phase0-charter.md`)。

## 進め方
1. **発散**: ユーザーと自由にブレストする。形式は不要。作りたいもの・使う人・困りごと・制約を引き出す。
2. **反例生成**: 主要なアイデアごとに「この要求が破られるシナリオを5つ」自分で生成してユーザーにぶつける。反例は後の FMEA の種になるので記録する。
3. **収束**: 合意した要求を 1 件ずつ REQ にする。テンプレ `method/templates/10-requirements.yaml` の形式で、対象プロジェクトの `bomdd/10-requirements.yaml` に書く。

## 根拠精度の規律(最重要)
各 REQ の rationale に判定質問を適用する:
> 「この記述だけから、検査の深さ(unit/L1–L3/golden)と許容差を決められるか?」

決められないなら `rationale_precision: needs-refinement` を付け、ユーザーに掘り下げ質問をする(例: 「同期が必要」→「ズレは何 ms まで許容?」)。粗い根拠は粗い受入を招く(Loop7 実証)。

## 核/表面の仮分類
各 REQ に `classification_hint` を付ける:
- **core**: 要求文から実装を導出できる(ドメインルール・判定・計算)
- **surface**: 外部ツール文法・プロトコル慣習・デザインの転記が要る → `external_source` に出所を書き、Phase 3 の K-BOM 調達候補に積む

## 完了ゲート G1
全 REQ が判定質問を通る(needs-refinement ゼロ)か、残件に持ち越しマークが付いていること。完了したら `bomdd/00-charter.md` の仮置き項目(題材・スコープの `(仮)`)を確定情報に更新し、Phase 2(`phase2-spec.md`)へ。
