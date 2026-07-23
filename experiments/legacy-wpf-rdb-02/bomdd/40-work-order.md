# Work Order — <ループID>

## ID
- Work Order ID: `WO-<ループID>-001`
- 対象 BOM tag/commit:
- Routing ref: `bomdd/34-routing.yaml`
- PLM Gate result: pass / fail

## 目的
<1〜3行: 何を製造するか>

## 実装開始条件
<!-- この条件を満たさない場合、製造装置は実装を始めない。 -->
- G1/G2/G2'/G3 が pass
- PLM stop finding が 0
- blocker unresolved questions が 0
- 製造パッケージに `20/30/31/32/33/34/40` が含まれる
- UI-CAD 案件では、製造パッケージに `35-design-system-bom.yaml` が含まれる

## 入力(これがすべて。これ以外を参照しない)
- `bomdd/20-spec.md`(仕様)
- `bomdd/30-ebom.yaml` / `31-kbom.yaml` / `32-mbom.yaml` / `33-control-plan.yaml` / `34-routing.yaml`
- UI-CAD 案件では必須: `bomdd/35-design-system-bom.yaml`
- <観測契約(in-process 題材のみ)>

## 製造対象
| M-BOM unit | E-BOM refs | Output artifact ref | Acceptance refs |
|---|---|---|---|
| M-<NAME>-001 | E-<NAME>-001 | <成果物パス> | CP-<NAME>-001 |

## TraceLink
| TraceLink | From | Relation | To | Evidence |
|---|---|---|---|---|
| TL-WO-M-001 | WO-<ループID>-001 | manufactures | M-<NAME>-001 | `bomdd/40-work-order.md` |

## 変更/是正時の改修境界
ECO/CAPA として既存ソース複製を渡された場合は、`61-impact-analysis.md` の影響あり範囲だけを改修する。影響なし範囲への変更は禁止し、納品後に `63-diff-audit.md` で測定される。仕様/BOM/Control Plan から導けない修正を見つけた場合は、直接広げず cheat-log に報告する。

## 必須受入(自己受入)
- <ビルドコマンド> が成功する
- <受入ハーネス実行コマンド> が成功する
- 受入ハーネスの必須範囲: Control Plan の unit 行 test_vectors 全被覆 + **L1 API/表面スモーク(起動+全エンドポイント正常系1本)**(unit 緑のまま表面が実行時全滅する盲点の対策。forward-01)
- UI-CAD 案件: `35-design-system-bom.yaml` の required design parts(Card/CTA/Chip/Badge/IconButton 等)を対象 surface に適用していること。素の panel/text/button で代替した場合は cheat-log に報告する。

## ずる報告(義務)
製造中に BOM/K-BOM/Control Plan から導けなかった判断は、**実装を止めずに**全件 cheat-log 形式で報告する:
```
### CHEAT-<ID> [分類] 一行要約
- 手法が与えなかったもの:
- 代替した判断(何をどう埋めたか):
- 重大度: blocker / friction / minor
```

特に以下の次元は判断したら必ず報告する(silence-checklist の exploratory 宣言行):
- <例 ID 生成方式>
- <例 応答に含めるフィールドの選択>
- <例 日時の小数秒桁>
- <例 Card/CTA/Chip/IconButton を実装せず素部品で代替した箇所>

## 調達部品の規律
依存パッケージは `32-mbom.yaml` の `procurement` に列挙されたものだけを使う。列挙外のパッケージが必要だと判断した場合、その採用は**ずる報告対象**(理由・代替案込みで報告し、実装は標準ライブラリで代替できるならそちらを優先)。

## 進めない級の問題(blocker)を発見した場合
BOM の自己矛盾・実装不能を発見した場合は、**当該製造単位を `blocked` とマークして他の単位を続行**し、cheat-log に C6(手戻り)として記録して納品時に報告する。製造を中断しての質問往復はしない(隔離の維持。修正は設計者側が BOM を改訂し fresh re-run する)。

## 自己受入が赤のままの場合
**自己受入に FAIL が残る状態は「納品」ではない。** 緑にできない場合は `stop/report`: 製造を停止し、FAIL 一覧・原因の見立て・試した修正を報告して終了する(赤のまま納品しない。manufacturing nonconformance として記録される。根拠: forward-01 factory-06)。

## 納品時に必ず返すもの
- 製造成果物
- 自己受入ログ
- cheat-report(0件なら 0件と明記)
- 変更した artifact の一覧
- `50-as-built.yaml` に転記可能な `ai_model`、`prompt_hash`、`artifacts_sha256` の材料

## 禁止事項
- 設計対話、固定オラクル期待値、他工場成果を参照する。
- PLM stop finding を無視して実装する。
- `32-mbom.yaml procurement` に無い依存を無申告で追加する。
- Control Plan に無い検査を合格根拠として扱う。
- 不明点を質問せず仕様確定したことにする。隔離製造中は cheat-report に残す。
