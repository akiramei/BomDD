[INFORM / COMPLETE]

**`ce55fcb` として着地しました。設置するコミット自身が、設置する検査に判定されています。**

```
a commit that stages a declared equipment path must name an ECO,
in a step subject <verb>(ECO-VT-N) or a BomDD-ECO-Fix/Probe/Accept trailer
```

**hook は変えていません。**validator が自分で staged 集合を git に訊きます。**パス集合と動詞リストは契約に宣言**し、同じブロック走査（YAML を import しない）が 2 つのリストを読めるようにしました。**無ければ既定値ではなく所見です。**

**`enforcement_from` で範囲を切っていません**——このファイルの他の検査と違う扱いで、意図的です。**比較すべき ECO が無いことが欠陥そのもの**だからで、形状を選んだ測定も同じ理由で無範囲でした。

## 21 のケースが、私が対照を書く前に fail-closed 分岐を見つけました

検査を入れた瞬間、**ユニット 12 件が落ちました**——全部 `EQUIPMENT_PATHS_MISSING`。合成ポリシーがリストを宣言していなかったからです。直すと**hook 側で 9 件**が同じ理由で落ちました。

**分岐は緩めていません。**合成契約に本物と同じ形を与え、**そのうえで分岐に自前のケースを足しました**——偶然ではなく意図して到達できるように。

## 修理後のアーム

```
RED   装置 staged・chore:                拒否
RED   装置 staged・fix:（括弧なし）        拒否
RED   装置 staged・dist subject           拒否
GREEN 本物の dist swap（装置なし）        受理
GREEN 装置 staged・正しい fix step        受理、しかも何を測ったか言う
GREEN 装置 staged なし・chore:            受理
GREEN 12 の step 動詞すべて               受理
GREEN 較正スイート                        158 件 PASS
```

**3 本が反転し、3 本は反転しませんでした。**probe が宣言したとおりです。**全部拒否する検査なら赤 3 本は満たしてプロジェクトを壊します。**緑 4 本がその 2 つの結末の間に立っています。

**前と後は 2 ファイルで、上書きしていません。**`probe-arms.json` は probe が記録したまま、`fix-arms.json` が今回の実行。**どちらも他方を説明することを信用される必要がありません。**

## 較正ケースを 16 件追加

6 件は probe のアームの写し（**register が 1 本で書き、probe が 2 本に割ったものを含む**）。**3 件は hook で走ります**——本物のコミットが本物の装置パスを staged にする形で、**モジュール経由だけでなく規則が実際に走る場所**で。1 件は fail-closed 分岐。**6 件は照合器に各形式の「惜しい非一致」を並べたもの**（`bomdd/toolsx/x.py` は prefix に一致してはならない、`ui-golden-policy.yml` は glob に、`package-release.ps1.bak` は完全一致に）——**何にでも yes と言う照合器は、他の全ケースを通過してしまうからです。**

ツリーは clean。次は golden です。