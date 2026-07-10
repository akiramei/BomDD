# 匿名化規則(scale-01/02 個票 — ViewPrism2 公開までのつなぎ)

- **ファイルパス**: `f_` + sha256(リポ相対パス・UTF-8)の先頭8桁へ置換。同一ファイルは同一トークンに写る(集中度・重複の検算が可能)。衝突確率は本件の規模(数百ファイル)で無視できる。
- **unit ID(M-*)・E-BOM ID・ECO ID・件数・コミット数**: 非匿名(FINDINGS で既に公開済みの語彙)。
- **ECO タイトル・本文・コミットメッセージ**: 含めない(製品情報・固有名詞を含み得るため)。
- **検算手順**: ViewPrism2 公開後、`python method/tools/impact-retrospective.py --repo ViewPrism2 --test-unit M-HARNESS-015` の出力パスへ本規則を適用し、本個票との一致を確認できる。それまでは開示合意の下での監査で照合に応じる(docs/evidence-index.md §3)。
- **scale-01 公表値との関係**: 本エクスポートは現時点の全履歴再採点(採点規約 v2・見出しは fail-closed)。scale-01 論文公表値(実 under 55・14/16)は 2026-07-04 時点の母集団 34 ECO に対する**裁定済み3分解**(test-only 74 / 写像未所有 8 / 実 under 55)であり、v2 出力の decomposition から v1 相当値を再現できる。
