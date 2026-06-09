# Phase 2 — 仕様化(設計者 AI への指示)

典拠: `method/bomdd-playbook-v1.md` §3。入力: `bomdd/10-requirements.yaml`(無ければ先に Phase 1)。

## 1. 仕様書を書く
テンプレ `method/templates/20-spec.md` で `bomdd/20-spec.md` を作る。必須:
- 各節に REQ トレース(双方向: 宙に浮いた節・実現されない REQ をゼロに)
- **不変条件の節**(識別子採番・座標系/基準系・冪等性・順序)
- `method/silence-checklist.md` の**第1回掃討**: 全行を `specified / exploratory / out-of-scope / deferred-to-phase3` で宣言する(deferred は第1回のみ有効な明示的延期)。無言の先送り禁止。

## 2. ゲート G2 — マルチリーダー仕様監査
1. **互いを知らない 3 体のサブエージェント**(可能なら別モデルティア: opus/sonnet/haiku。Claude Code なら Agent ツールの model 指定)を起動する。各リーダーには**仕様書の内容だけ**を渡す(この会話の文脈・要求台帳・他リーダーの結果は渡さない)。
2. 各リーダーへの指示: 「この仕様書から ①REQ 一覧 ②不変条件 ③各 REQ の受入深さ(unit/L1–L3/golden)と許容差 を抽出して構造化して返せ」
3. 3 体の抽出結果を突合する。**差分が出た箇所=仕様が一意に読めない箇所**(特に深さ・許容差の読みの割れを優先。Loop7 では振る舞いは一致し根拠精度で割れた)。
4. ユーザーと補正 → 再監査。差分ゼロ(または残差に理由付き)で通過。

## 3. ゲート G2' — 測定可能性(MeasurementCapability)
各 REQ に問う: 「観測する深さ・治具・承認者は足りるか?」
- 状態: `adequate / unmeasurable / under-specified-oracle / insufficient-depth / human-approval-required`
- `unmeasurable` の REQ は**仕様未完成**。知覚系→golden+許容差+承認者を計画 / in-process→観測契約を計画 / それでも測れない→ユーザーと要求を見直す。
- 結果を仕様書末尾のゲート記録に書く。

完了したら Phase 3(`phase3-design.md`)へ。
