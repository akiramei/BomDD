# 証拠インデックス — 論文主張と公開証拠の対応(査読対応・つなぎ版)

> 査読必須修正8「中核証拠の公開」への対応(2026-07-10)。ViewPrism2 は将来公開予定だが、
> 個人情報・セキュリティ情報の削除が未了のため、それまでの**つなぎ**として、
> (a) 既に公開済みの一次記録への索引 (b) 非公開分の匿名化集計の置き場 (c) 監査申し出への応諾方針、を定める。

## 1. 公開済み(このリポジトリ・投稿時点で利用可能)

| 論文の主張 | 一次記録(公開) |
|---|---|
| 実験VIII 転移3構成(介入台帳・事前予測・採点・伏せ項目) | `loops/transfer-01〜03/`(protocol=事前登録・intervention-ledger 全件・t1/t2/t3-report)+ kit凍結タグ transfer01-kit-v1〜v3 |
| 実験VIII 工数の観測分解(17倍乖離・6h12m・人間律速) | `loops/transfer-02/t2-time-decomposition.md`+治具 `method/tools/time-decomposition.py` |
| stage0-oss(3リポ・H1〜H5 事前登録・三冠不再現・H5反証) | `loops/stage0-oss-01/`(protocol・calibration・results JSON〔対象リポの HEAD SHA 記録〕・report) |
| 採点治具(規約v1/v2・v1数値の恒久再現) | `method/tools/impact-retrospective.py`(規約はファイル冒頭に版宣言) |
| 健診治具(定義凍結・fail-closed) | `method/tools/stage0-survey.py` |
| 検査治具の第三者監査→是正の全記録 | `bomdd/60-change-register.yaml`+ECO-001〜007 order・self-conformance(C1〜C9)+CI(`.github/workflows/`) |
| loop 実験の期待結果(意図的な赤の保存検査) | `loops/expected-results.yaml`(失敗分類+シグネチャ) |
| ずる12件の個票・分類 | `FINDINGS.md` ずる台帳(第二評価者プロトコル= `loops/cheat-reclassification-01/`) |
| forward/webapi/saga 系列 | 各公開リポ(論文付録A表17のタグ・コミット列) |

## 2. 非公開分のつなぎ(匿名化集計 — 公開までの暫定)

- **scale-01/02(ViewPrism2)**: 公表値は裁定済み3分解(`ViewPrism2/bomdd/studies/scale-01-impact-retrospective.md`・非公開)。
  つなぎとして、**匿名化採点個票を `docs/evidence/scale-01-anonymized/` へエクスポート済み(2026-07-10)**:
  `scoring-v2-anonymized.json`(ECO単位の宣言影響集合×実diff・under/unmapped 個票=パスは sha256 先頭8桁)・
  `excluded-ecos.md`(除外39件の ID と理由)・`masking-rules.md`(置換規則と検算手順)。
- **UI-CAD(MoviePad)**: 裁定台帳の様式・ゲート判定は method 本文と治具で公開済み。個票は監査応諾で対応。
- **完全公開の条件**: ViewPrism2 の個人情報・セキュリティ情報の削除完了(作業中)。完了後、本インデックスの該当行を公開リポ参照へ差し替える。

## 3. 監査への応諾

非公開一次記録(ViewPrism2・MoviePad)は、開示合意の下での監査(コミットID・diff統計・個票の照合)に応じる。
再現性は「同じ出力の再生成」(非決定的な外部モデルのため保証しない)と「当時の証拠の監査可能性」
(凍結タグ・ハッシュ・台帳)を区別して主張する(論文付録A の再現性3階層)。
