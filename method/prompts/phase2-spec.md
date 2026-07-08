# Phase 2 — 仕様化(設計者 AI への指示)

典拠: `method/bomdd-playbook-v1.md` §3。入力: `bomdd/10-requirements.yaml`(無ければ先に Phase 1)。

## 1. 仕様書を書く
テンプレ `method/templates/20-spec.md` で `bomdd/20-spec.md` を作る。必須:
- 各節に REQ トレース(双方向: 宙に浮いた節・実現されない REQ をゼロに)
- **不変条件の節**(識別子採番・座標系/基準系・冪等性・順序)
- 原典ありの UI/帳票 surface は**表示契約**を書く。原典に見える提示フィールド・ラベル・サムネイル・ファイル名・状態表示・空/エラー表示を全列挙し、移植対象外は理由を書く。
- HTML モックが入力にある場合は、先に Phase 1.5 の 2 段抽出(`method/prompts/ui-raw-to-candidates.md` → `ui-apply-rulings-to-bom.md`)で UI-IR / UI-BOM / trace map を作り、表示契約と E-BOM 候補の素材として使う(旧一発変換 `ui-mock-to-ui-bom.md` は deprecated)。UI-BOM は候補であり、仕様・E-BOM への昇格前に未解決事項(裁定台帳の open)を確認する。
- `method/silence-checklist.md` の**第1回掃討**: 全行を `specified / exploratory / out-of-scope / deferred-to-phase3` で宣言する(deferred は第1回のみ有効な明示的延期)。無言の先送り禁止。

## 2. ゲート G2 — マルチリーダー仕様監査
1. **互いを知らないサブエージェント**を起動する(体数は playbook §11 テーラリングの規模セルに従う — 標準 3 体・S 規模は 1 体セルフ監査へ縮退可。採否は charter に記録)。可能なら別モデルティア: opus/sonnet/haiku。Claude Code なら Agent ツールの model 指定。各リーダーには**仕様書の内容だけ**を渡す(この会話の文脈・要求台帳・他リーダーの結果は渡さない)。
2. 各リーダーへの指示: 「この仕様書から ①REQ 一覧 ②不変条件 ③各 REQ の受入深さ(unit/L1–L3/golden)と許容差 を抽出して構造化して返せ」
3. 3 体の抽出結果を突合する。**差分が出た箇所=仕様が一意に読めない箇所**(特に深さ・許容差の読みの割れを優先。Loop7 では振る舞いは一致し根拠精度で割れた)。
4. ユーザーと補正 → 再監査。差分ゼロ(または残差に理由付き)で通過。

## 3. ゲート G2' — 測定可能性(MeasurementCapability)
各 REQ に問う: 「観測する深さ・治具・承認者は足りるか?」
- 状態: `adequate / unmeasurable / under-specified-oracle / insufficient-depth / human-approval-required`
- `unmeasurable` の REQ は**仕様未完成**。知覚系→golden+許容差+承認者を計画 / in-process→観測契約を計画 / それでも測れない→ユーザーと要求を見直す。
- 結果を仕様書末尾のゲート記録に書く。

## 4. 原典パリティサインオフ(原典ありの場合)
凍結後の工場は原典を見ないため、原典との比較でしか見つからない欠落はここで止める。表示要素集合を `仕様節 / REQ / E-BOM候補 / Control Plan候補` に仮トレースし、未トレース要素ゼロまたは理由付き out-of-scope を確認してから Phase 3 へ進む。

完了したら Phase 3(`phase3-design.md`)へ。
