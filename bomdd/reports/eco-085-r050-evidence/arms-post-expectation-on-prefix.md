CLI の個体: BomDD-Plm HEAD 6937a66abcb74f327251cf44e28224f94e584a59・作業木 clean・evaluate.js sha256 d10200432cbb
期待: post

| 腕 | 説明 | ゲート | exit | R-050 error の対象 | R-050 info の対象 | R-050 以外の error | 期待との一致 |
|---|---|---|---|---|---|---|---|
| good | 正常陰性対照: 合格 | acceptance | 0 | なし | なし | 0 | 一致 |
| fail | 違反陽性対照: 不合格 | acceptance | 0 | なし | なし | 0 | 不一致 |
| notrun | 違反陽性対照: 未実行 | acceptance | 0 | なし | なし | 0 | 不一致 |
| blocked | 違反陽性対照: 保留 | acceptance | 0 | なし | なし | 0 | 不一致 |
| nofield | 違反陽性対照: 合否値の欄なし | acceptance | 0 | なし | なし | 0 | 不一致 |
| unknown | 違反陽性対照: 語彙外の値 | acceptance | 0 | なし | なし | 0 | 不一致 |
| mixed | 違反陽性対照: 同一 CP に合格と不合格 | acceptance | 0 | なし | なし | 0 | 不一致 |
| extra | 違反陽性対照: 受入対象外の CP に不合格行 | acceptance | 0 | なし | なし | 0 | 不一致 |
| missing | 既存の陽性対照: 証拠行が空 | acceptance | 1 | CP-CORE-001 | なし | 0 | 一致 |
| noab | 対象欠落チャレンジ: 製造記録ファイルなし | acceptance | 0 | なし | なし | 0 | 不一致 |
| emptylist | 対象欠落チャレンジ: as_built が空リスト | acceptance | 0 | なし | なし | 0 | 不一致 |
| docdialect | 対象欠落チャレンジ: 文書方言(mapping) | acceptance | 0 | なし | なし | 0 | 不一致 |
| noab-G3 | ゲートの対照: 製造記録なしを G3 で実行(製造前は正常な状態) | G3 | 0 | なし | なし | 0 | 一致 |
| notarget | 適用外の対照: 受入対象の M unit なし | acceptance | 1 | なし | なし | 1 | 不一致 |
| notarget-fail | 適用外かつ違反: 受入対象なし・不合格行あり | acceptance | 1 | なし | なし | 1 | 不一致 |

実在標本: ViewTube(d75a1b6)の製造記録エントリ 1 本・証拠行 3・合格以外の行を持つ CP 2 件
  exit 1・R-050 error 67 件・合格以外の行を持つ CP のうち所見に出たもの 0 件
  期待(合格以外の行を持つ CP がすべて所見に出る)との一致: 不一致
