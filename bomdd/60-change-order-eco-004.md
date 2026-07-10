# ECO-004 — bomdd-init の絶対パス結合 → 版付き kit 同梱+bomdd.lock(版固定)

## 起票(2026-07-10)

- 出典: メンバー外部レビュー所見2(P1)。「初期化したプロジェクトが、ローカルの可変な方法論
  リポジトリへ絶対パスで結合する。別 PC への移動で壊れるだけでなく、方法論リポジトリを更新すると、
  既存製品が参照する手順も無記録で変わる。これは凍結・来歴・再現性という BomDD 自身の原則と衝突する。
  方法論を自己完結した版付き kit として同梱し、bomdd.lock に方法論 commit/hash、adapter 版、
  依存版を固定するのがよい」。
- 再現(是正前・実測): scaffold 生成物のうち **7 ファイル**(CLAUDE.md・スキル 8 本の一部・
  change-management.md)に `METHOD_ROOT` 絶対パスが埋め込まれる。画面出力の案内 3 行も絶対パス。
- 皮肉な傍証: **transfer 実験自体はこの問題を凍結 kit(transfer01-kit-v1〜v3 タグ)で回避済み**
  だった — 実験でアドホックに確立した型が製品(bomdd-init)に還元されていなかった。

## 裁定

- ユーザー承認(2026-07-10)「手順3を進めて」。
- 是正方針: レビュー提案どおり **kit 同梱+lock**。
  - kit = `method/` 全体(996K・100 files — 実行時参照される playbook/prompts/onboarding/
    tools/templates を選別せず全量。選別は乖離債務になるため)を製品リポ `bomdd-kit/method/` へ
    凍結コピー。`{{METHOD}}` 置換値を絶対パス → `bomdd-kit`(リポ内相対)へ。
  - `bomdd.lock` = method の出自(origin_path・commit・dirty)+ kit(files 数・
    per-file sha256 manifest への参照+manifest 自体の sha256)+ adapter(スキル一覧)+
    runtime(python 版)。**origin_path は来歴であって実行時依存ではない**(教訓の一般形昇格の
    送り先 — change-management の役割表もこの語彙に追随)。
  - method リポが git checkout でない環境では commit を `not-computed(...)` と正直記録
    (t3 as-built の prompt_hash 様式)。dirty スナップショット時は警告+lock 記録。
  - `--skills-only`(既存リポへの追設)でも kit+lock を設置。既存 kit は**保持**
    (無断上書きしない — 版更新は明示的な削除+再実行)。
- スコープ外(F6 へ): kit 鮮度の自己検査(lock の commit と方法論リポの乖離検出)・
  既存製品リポ(ViewPrism2 等)への kit 後付け移行。

## 影響分析(製造前凍結)

- 影響なし予測: `bomdd-init.py` と product-profile テンプレ({{METHOD}} 記述 3 ファイル+README)
  以外は diff ゼロ。既存製品リポには波及しない(init は生成時のみ作用)。

## 是正

1. `KIT_DIRNAME = "bomdd-kit"`・`install_kit()`(copytree+manifest+lock)・`_method_provenance()`。
2. repl の `METHOD` を絶対パス → `KIT_DIRNAME`(scaffold・--skills-only の両経路)。
3. scaffold_product / scaffold_cad / --skills-only の 3 経路で `install_kit()` 呼び出し
   (CAD リポも自己完結 — 製品リポへの相対参照は配置替えで壊れるため各リポに同梱)。
4. 画面出力の案内 3 行+協働ガイド参照を kit 相対パスへ。
5. product-profile テンプレ 3 ファイル: 正典の説明を「同梱凍結スナップショット+bomdd.lock」へ、
   change-management の役割表を「kit は凍結写し・昇格送り先は正本リポ(origin_path)」へ。

## 検証(2026-07-10)

- **陽性対照**: 是正前 scaffold = 生成物 7 ファイルに絶対パス → 是正後 **0**
  (唯一の出現は bomdd.lock `origin_path` = 設計どおりの来歴フィールド)。
- **可搬性**: 生成リポをディレクトリ移動(`TestProd` → `MovedProd`)後、kit 治具
  (ui-cad-gate/ui-extract)が製品ルートから実行可。
- **来歴の正確性**: lock の method commit = 生成時 HEAD(437c78b)一致・**dirty: true を正直記録**
  (本 ECO 作業中の未コミット変更を正しく検出)・manifest sha256 の再計算一致(改ざん検出可)。
- **--skills-only**: kit+lock 設置・再実行時は既存 kit 保持(fail-safe)を確認。
- **fail-closed の継承**: kit 内 stage0-survey が exit 2(ECO-002 の是正が kit 経由でも有効)。
- 影響なし予測: 的中。

## 教訓(還元候補 — lesson-promote 経由)

- **実験で確立した型(凍結 kit)は製品経路(init)へ還元されるまで方法論の原則違反が残る** —
  transfer が kit を必要とした理由(凍結・自己完結)は、転移テストに限らず全製品に該当していた。
- 来歴フィールド(origin_path)と実行時依存の区別を lock 内コメントで宣言する型 —
  「絶対パス=悪」ではなく「無記録の可変結合=悪」(1 例目)。
- kit 更新の規律(いつ・どう上げるか= lock diff を ECO として扱うか)は未設計 —
  既存製品への後付け移行と合わせて F6 以降の宿題。
