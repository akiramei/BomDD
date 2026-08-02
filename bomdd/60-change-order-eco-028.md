# ECO-028 — ECO 記録様式に AI 設備構成の記録欄がない(担当設備の系統的無記録)

状態: **verified(2026-08-02)**。fix= 122ea7e・検証 V1〜V2 実測済み(下記)・窓は accept で閉鎖。
V3(CI)は push 後に実測し本 order へ追記(4 値判定)。

## 製造・検証記録(2026-08-02)

- V1= **PASS**: テンプレに担当設備欄が存在。unknown 規律(「確認できなければ `unknown` — 推定で
  埋めない」)・来歴区別(observed / self-reported)・交絡実例(transfer-04 の統合層ゲート)・
  途中交代の追記規則を含む。検査官併記あり。
- V2= **PASS**: self-conformance C1〜C15 全 PASS(C4 scaffold 煙試験= 生成 kit にテンプレ同梱・
  YAML 厳格パース不変)。
- 影響なし予測の検証: **的中** — diff は method/templates/60-change-order.md+台帳系のみ
  (fix 122ea7e = 2 files)。
- V3(CI)= push 後に追記。

## gate ① 裁定(2026-08-02 maintainer「gate ① 承認します。ECO-028 の製造に入ってください」)

- 裁定 1: register 側スキーマへの equipment 欄追加= **見送り採択**(order のみ。register への昇格は
  EXP-20260802-05 の運用実測後)。
- 裁定 2: 欄の機械強制(validator / self-conformance)= **見送り採択**(記録が先・強制は基準線実測後)。
- 裁定 3: 既存 ECO への遡及記入なし(歴史的記録の非改竄)= **確認**。

## 担当設備(本 ECO — 新欄の自己適用)

- 製造: requested= claude-fable-5(セッション既定)/ resolved= claude-fable-5
  (**ハーネス自己申告= self-reported** — 外部検証なし)/ ハーネス= Claude Code(desktop)/
  来歴= self-reported(ハーネス表示)。
- 検査官: 独立検査なし(機械受入のみ — V1〜V3)。

## 出典

- equip-01(AI 設備の工程別能力の遡及採点)の実測([FINDINGS §13](../FINDINGS.md)・
  loops/equip-01/measurements.md §1/§10): 遡及 5 台帳・60+件で**台帳本文の担当設備(モデル)記録
  0/60**。設備交代 2 回(fable→opus→fable)が commit trailer でのみ可視・台帳無記録。ViewTube では
  誤記録(汚染)3 系統(治具 identity の本番 commit 混入・人間 identity での AI 製造 commit・
  レビュー識別子ずれ)。唯一識別が機能したのは記録様式を持つ transfer 台帳 —
  **識別の成否は様式の有無に従う**。
- EXP-20260711-05(継続運用でも担当者モデル+ハーネスが記録されるか)の**再演 3 回**
  (2026-07-26 / 2026-08-01 / 2026-08-02 全数遡及)— 「記録欄の宿題」が散発でなく系統的欠落と確定。
- 還元レビュー(2026-08-02 maintainer)で織り込み案 D として**採択済み**(テンプレ変更のため
  ECO 起票を経由 — ECO-022 前例・origin: improvement)。

## 症状

`method/templates/60-change-order.md`(ECO order の雛形)に担当設備の記録欄がなく、製造・検査の
実行主体(モデル・ハーネス)が台帳へ残らない。結果として (a) 設備構成の変更が不可視になる
(b) 遡及測定・帰属分析(specified_contract_miss= 工場能力)の設備軸が構成不能になる
(c) trailer 等の台帳外自己申告痕跡へ依存する。

## 是正方針

`method/templates/60-change-order.md` へ「担当設備」欄を追加する(transfer-test §5 の継続運用への
一般化):

- **requested**(要求したモデル・alias)/ **resolved**(実到達モデル — **確認できなければ
  `unknown`・推定で埋めない**)/ **ハーネス**(CLI・統合層とその版)/ **来歴**(observed か
  self-reported かを明記)。検査官(独立検査併用時)も同様に記録。
- 記入例に unknown 規律と交絡実例(requested gpt-5.6-sol → resolved gpt-5.5 = 統合層ゲート)を含める。

## 裁定点(gate ①)

1. **register 側スキーマへの equipment 欄追加**は今回行うか — 推奨= **見送り**(order のみ。
   register への昇格は運用実測〔EXP-20260802-05〕の後)。
2. **欄の存在の機械強制**(validator / self-conformance)は今回行うか — 推奨= **見送り**
   (記録が先・強制は基準線実測後 — worklist ④昇格と同じ規律)。
3. **既存 ECO への遡及記入**はしない(歴史的記録の非改竄)— 確認のみ。

## 影響なし予測(製造前)

diff は `method/templates/60-change-order.md` のみ(+台帳系)。既存製品リポへは kit 再設置まで
非波及(ECO-004 設計)。self-conformance C1〜C15 の判定は不変(C4 scaffold 煙試験は生成 kit に
本テンプレを含むが検査対象は生成成功と YAML 厳格パース)。

## 受入基準(凍結)

- V1: テンプレに担当設備欄が存在し、記入例が unknown 規律・来歴区別・交絡実例を含む。
- V2: self-conformance 全 PASS(C4 込み)。
- V3: push 後 CI 緑の実測(ECO-020 規律・4 値判定で記録)。

## スコープ外(明示)

- 既存 ECO・既存製品リポ台帳への遡及記入(非改竄)。
- validator / hook による欄の強制(EXP-20260802-05 の実測後に判断)。
- register スキーマ変更(裁定点 1 次第・既定は見送り)。
- 製品リポへの kit 一括再配布。
