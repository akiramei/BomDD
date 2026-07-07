# {{PRODUCT}}

BomDD(BOM 駆動開発)で製造するプロダクト。`bomdd/` が設計・受入・変更管理の台帳(git が正本)。
UI/UX の設計原器(CAD)は別リポ `../{{CAD}}`(乖離時は常に CAD が正 — `../{{CAD}}/docs/02_mock_fidelity_policy.md`)。
方法論の正典は `{{METHOD}}`(playbook・テンプレ・フェーズ実行プロンプト)。

## 現在地と入口

- **初回納品前(フォワード・モード Phase 0〜6)**: 入口は `/bomdd-next`。現在フェーズを判定し
  次の一手へ誘導する(UI/UX デザイン= Phase 1.5 のモック作成・検査・CAD 化も誘導に含む —
  **開始時に人間が覚えるのはこのコマンドだけ**)。**Gate を通すまで実装を始めない**(方法論 onboarding 規律)。
- **初回納品後(変更管理 regime)**: すべての変更は ECO 経由。入口は下表のスキル。
  手順の正本: [bomdd/change-management.md](bomdd/change-management.md)。

## 変更管理の要点(納品後)

- **起票なき src/tests 変更は禁止**。すべての変更は ECO(`bomdd/60-change-register.yaml`)から。
- **コードから入らない**: 所見はまず工程診断(CAD/BOM/実装のどこの欠陥か)。上流欠陥は上流から直す。
- **ついで修正禁止**: スコープ外所見は分離起票か 51-cheat-log 記録の二択。
- **是正はプローブ先行**: 是正前に不合格となる回帰テストで真因を実測裏取りしてから触る。
- **既存固定オラクル行は変更しない**。受入は新規行を追加。
- **human gate は「裁定」と「golden(実機承認)」の 2 つだけ**。それ以外は AI が進め、
  gate 到達時に「人間がやること」を明示して停止する。

### 入口スキル(自由文プロンプトの代わりにこれを使う)

| コマンド | 用途 |
|---|---|
| `/bomdd-next` | フォワード工程の現在地判定と次の一手(納品前の入口。Phase 1.5 含む) |
| `/bomdd-refmodel` | UI モックの参照概念モデル差分検査(Phase 1.5・製品につき 1 回・skip 可) |
| `/bomdd-mock-lint` | UI モック受入検査(三層+復唱。blocking 0 まで差し戻し) |
| `/bomdd-ui-cad` | モック→UI-IR/UI-BOM の CAD 化(施錠付き・§12.1 双子出力= DOM+PNG) |
| `/eco-file <症状・要求>` | ECO 起票+工程診断(不具合・新機能・拡張すべての入口) |
| `/eco-fix <eco-NNN>` | プローブ先行の是正+機械受入 → golden 基準提示で停止 |
| `/eco-accept <eco-NNN>` | golden 合格後のクローズ(観点明記・register applied・教訓) |
| `/sec-advisory <CVE等>` | OSS 脆弱性の実測逆引き → 処置選択肢提示で停止 |

## 機械受入(全て緑が納品条件)

Phase 3(工程設計)で確定したらここへ記入する。それまでは TODO のまま。

```
# TODO(/bomdd-next Phase 3 で確定): build / test / オラクル / 台帳整合検査 のコマンドを列挙
```

## コミット規約

フォワード: フェーズ成果物ごと。変更管理: `起票(eco-NNN):` → `decide(eco-NNN):`(裁定のみ)
→ `fix(eco-NNN):` → `accept(eco-NNN):`。コミットは人間の指示があってから。

## 人間との分担

人間の仕事は**裁定**(選択肢から選ぶ)と **golden**(実機確認)の 2 つだけ。詳細は
`{{METHOD}}/method/onboarding/working-with-ai.md`(人間向け協働ガイド)。
