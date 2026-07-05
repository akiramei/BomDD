---
name: bomdd-mock-lint
description: モック受入検査 手順3: モック lint(内→外)。内部矛盾・カバレッジ写像・隣接未カバー質問・復唱文で「行ったこと≟行いたかったこと」を製造前に突合する。合格が /bomdd-ui-cad の解錠条件。
---

# /bomdd-mock-lint — モック lint(モック受入検査 手順3・必須)

正典: `{{METHOD}}/method/prompts/ui-mock-coverage.md`(§17)。
治具: `{{METHOD}}/method/tools/ui-mock-inspect.py`(**判定は治具の exit code に従う。セッションの裁量で緩めない**)。

## 位置(ワークフロー)

```text
1. モック作成 → 2. /bomdd-refmodel(skip可) → 3. /bomdd-mock-lint(本スキル)
→ 実在矛盾・blocking 未解決なら 1 へ → 4. /bomdd-ui-cad(本スキル合格で治具が解錠)
```

## 手順

1. **前提**: `... status --dir bomdd/ui/<pkg>` で refmodel が done/skipped であること
   (pending なら /bomdd-refmodel へ誘導。init 未実施ならそちらの手順2で init)。
2. **プロンプト合成**: `python {{METHOD}}/method/tools/ui-mock-inspect.py emit-prompt --dir bomdd/ui/<pkg> --stage lint`
   — refmodel 未決着なら治具が拒否する(順序強制)。
3. **隔離実行**: 合成プロンプトで **fresh サブエージェント**を起動(渡すのは合成プロンプトのみ)。
   報告書を `bomdd/ui/<pkg>/lint-report.md` に保存。
4. **機械検査**: `... check --dir bomdd/ui/<pkg> --stage lint --report lint-report.md`
   — 合格で CAD 工程が解錠される。fail は書式・予算を直させて再検査。
5. **人間の裁定**:
   - 層1 の矛盾候補 → 実在なら**モック改訂(手順1)へ戻る**
   - 層3 の質問 → 裁定台帳へ(blocking が残る限り先へ進まない)
   - 層4 の復唱文 → 設計者が各文に Yes/No。「未規定」宣言に異議があれば裁定を起票
6. 矛盾・blocking が無くなったら /bomdd-ui-cad へ。

## 規律

- 質問は正典プロンプトの予算(≤20・コスト降順)内。予算超過は check が落とす。
- 失敗の還流先は §14(X1=治具修正/X2=プロンプト+golden/X3=台帳 negative)。
  **観点の追加は実測 miss 時のみ・1還流3行まで**(肥大防止則)。
- モック改訂後の再実行は安価: 抽出は決定的、裁定・negative は台帳が保持(再質問率 0% 実測)。
