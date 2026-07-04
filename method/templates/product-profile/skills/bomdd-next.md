---
name: bomdd-next
description: フォワード・モード(Phase 0〜6)の現在地を bomdd/ の状態から判定し、次の一手を実行する。まっさらな状態から初回納品までの入口。納品後(変更管理 regime)に呼ばれたら /eco-file 系へ誘導して自分の役目を終える。
---

# /bomdd-next — フォワード工程の現在地判定と次の一手

正典: `{{METHOD}}/method/bomdd-playbook-v1.md`+`{{METHOD}}/method/prompts/phase0-charter.md`〜
`phase5-accept.md`(**実行手順はプロンプト側が正**。本スキルは現在地判定と誘導のみを担う)。
チェックリスト: `{{METHOD}}/method/onboarding/new-project-checklist.md`。

## 絶対規律(方法論 onboarding より)

- **Gate を通すまで実装(製品コード)を始めない。**
- 不明点は推測で埋めず `unresolved questions` に残す。
- 製造工場(fresh サブエージェント)へ渡してよいのは製造パッケージ(20/30-34/40)だけ。
  設計対話・41/42(オラクル・プローブ)・他工場の成果は渡さない。

## 手順

1. **現在地判定**: `bomdd/` を読み、次の表で最初に該当した行が現在フェーズ。
   「テンプレのまま」= プレースホルダ・記入欄が未記入のこと。

| 判定(上から順) | 現在地 | 次の一手(正典プロンプト) |
|---|---|---|
| `00-charter.md` がテンプレのまま | Phase 0 | phase0-charter.md(人間と対話して埋める) |
| `10-requirements.yaml` が空/テンプレ | Phase 1 | phase1-brainstorm.md(REQ 台帳化) |
| `20-spec.md` がテンプレのまま | Phase 2 | phase2-spec.md。GUI なら CAD(`../{{CAD}}`)のモック+screens が入力(UI-IR 抽出= ui-mock-to-ui-bom.md) |
| `30-ebom/32-mbom/33-control-plan` がテンプレ | Phase 3 | phase3-design.md(E/K/M-BOM・Control Plan・Routing)。**41 固定オラクルもここで設計(工場非開示)**。完了時に CLAUDE.md の機械受入コマンド欄を確定させる |
| `40-work-order.md` がテンプレ | Phase 4 準備 | 製造パッケージ組成+work order(diff 基準点・stop/report 宣言) |
| `50-as-built.yaml` に受入記録なし | Phase 4-5 | phase4-manufacture.md(fresh 工場)→ phase5-accept.md(機械受入+golden← human gate) |
| as-built に golden 承認あり | **納品済み** | 本スキルの役目終了。「以後の変更はすべて /eco-file が入口」と案内して停止 |

2. **チェックリスト先行**: Phase 0 開始前に new-project-checklist §1(入力資料)・§2(人間が
   配置するファイル)を人間と一緒に埋める。§2 は human gate(資料の配置は人間の作業)。
3. **実行**: 該当フェーズの正典プロンプトを読み、その指示に従って成果物を作る。
   フェーズ完了ごとにコミット(人間の指示があってから)。
4. **停止点**: 各フェーズの human gate(charter の合意・裁定・golden)では
   「人間がやることはこれだけ」を明示して停止する。

## 出力様式

毎回、冒頭に現在地を 1 行で示す:
`現在地: Phase N(<フェーズ名>)/ 根拠: <判定したファイルと状態> / 次: <一手>`
