---
name: bomdd-refmodel
description: モック受入検査 手順2: 参照概念モデル差分(外→内)。一般概念モデルとの gap から検討漏れ・スコープ・フェーズ計画をクリアにする。製品につき1回・スキップ可(理由必須)。/bomdd-mock-lint の前に実行または明示スキップ。
---

# /bomdd-refmodel — 参照概念モデル差分(モック受入検査 手順2・スキップ可)

正典: `{{METHOD}}/method/prompts/ui-mock-refmodel.md`(§17.1)。
治具: `{{METHOD}}/method/tools/ui-mock-inspect.py`(**判定は治具の exit code に従う。セッションの裁量で緩めない**)。

## 位置(ワークフロー)

```text
1. モック作成(人間・自由) → 2. /bomdd-refmodel(本スキル・skip可) → ②検討漏れあれば 1 へ
→ 3. /bomdd-mock-lint → 4. /bomdd-ui-cad(lint 合格まで治具が施錠)
```

## 手順

1. **前提**: モックパッケージ(設計者注記+状態ごとの snapshot+ui-ir.raw.json)を確認。
   raw IR が無ければ `{{METHOD}}/method/tools/ui-extract.py` で先に生成する。
2. **init(初回のみ)**: `python {{METHOD}}/method/tools/ui-mock-inspect.py init --dir bomdd/ui/<pkg> --mock <モックパッケージのファイル...>`
   — manifest(sha256)と隔離ステージングが作られる。
3. **スキップ判断**: 同一製品で参照モデル裁定済み(2画面目以降)等なら
   `... skip --stage refmodel --reason "<理由>"` を実行して /bomdd-mock-lint へ。**無言で飛ばさない**。
4. **プロンプト合成**: `... emit-prompt --dir bomdd/ui/<pkg> --stage refmodel`
5. **隔離実行**: 合成されたプロンプトで **fresh サブエージェント**を起動する。
   エージェントに渡してよい情報は合成プロンプトだけ(実装・台帳・git は汚染源)。
   報告書を `bomdd/ui/<pkg>/refmodel-report.md` に保存。
6. **機械検査**: `... check --dir bomdd/ui/<pkg> --stage refmodel --report refmodel-report.md`
   — fail なら報告書の書式・予算を直させて再検査(内容の質はここでは裁定しない)。
7. **ヒアリング**: gap 一覧を設計者に提示し、各 gap に ①意図的な非採用(理由必須)/
   ②検討漏れ/③スコープ外/④フェーズ計画 の回答をもらう。answers.yaml に記録して
   `... hearing --answers answers.yaml --rulings bomdd/ui/<pkg>/37-ui-rulings.yaml`
   — 台帳へ原子記入される。exit 3 =「②検討漏れあり」→ **モック改訂(手順1)へ戻る**と案内。
8. exit 0 なら /bomdd-mock-lint へ。

## 規律

- 検査エージェントの出力は全て候補と質問。最終事実は裁定のみ(§12 三行原則)。
- ①〜④の裁定は台帳資産 — モック改訂後の再実行で**同じ質問は二度と出ない**。
- 較正質問への回答が変われば参照モデルは改訂(gap 一覧の末尾の除外リスト参照)。
