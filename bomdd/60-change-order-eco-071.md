# Change Order — ECO-071(handoff 契約 v0.4: フリースタイル区間 — 人間の宣言で開始・終了/区間内は形式なし/片方向ラチェット〔起票+製造・製造者較正〕)

> 裁定: user 2026-09-12 DISCUSS への AGREE+「3 点を契約に足して起票して」— タスク中はプロトコル、フリースタイルの会話が相応しい場面もある、という切り分けの要求。
> 当方 thesis(切替の権限は人間・既定は契約・片方向ラチェット)に user が AGREE。**起票と製造を同一 commit で行う**(文書のみ・ECO-063/069/070 の型)・受入は製造者較正のみ。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**

## 0. 実測(起票根拠)

- user の問い(2026-09-12): 「タスク中はプロトコルに従うのは当然。一方、フリースタイルな会話が相応しいシーンもある。この切り分けが可能になりますか?」
- 契約 v0.3 の現状(実読): §2.7 に「user が『形式なし』を指示したメッセージ」が適用外として **1 通単位**で書かれているのみ。区間の開始・終了、区間内で裁定・依頼が生じたときの
  扱い、AI が推定で形式を落としてよいかは未定義。
- 実測(本会話): user は宣言せずに会話をしており、当方は DISCUSS の型で返した(v0.3 の 2 通目・3 通目)。会話に形式が付くコストはヘッダ 1 行+硬い文体。逆にタスク中に形式を
  落とすと再分析コスト(本プロトコルの出自・EXP-20260911-01 の基準線)が戻る — **誤分類のコストは非対称**。
- 設計上の根拠: 「これは報告か質問か」を AI が勝手に決めて混ぜたことがプロトコルの出発点であり、「これは会話かタスクか」の推定は同種の判断。推定で落とすと同じ失敗が形を変えて戻る。

## 1. 変更要求(凍結・文書のみ)

1. `.claude/skills/handoff/SKILL.md` を **v0.4** に: 契約 §1 Scope に **Free-style span** を定義 — (a) 既定は契約。区間の開始と終了は人間の宣言のみ。AI は推定で区間に入らない
   (b) 区間内はヘッダも必須要素もなし (c) 片方向ラチェット: 区間内でも裁定・依頼・タスクのターン終了を含む 1 通はその通だけ契約に戻り「区間は継続」と明記する。
   実装 §2: §2.1 に区間の扱い(決定木は Q0/Q1 の検出にだけ使う・終了はタスク指示を終了宣言とみなしてよいが最初の handoff に書く)・§2.3 に F6・§2.7 の 1 通単位の適用外を区間規則に置換・
   §3 に区間の例・§4 に指標 ⑥⑦⑧と thesis を変える条件。frontmatter description に区間の 1 文。
2. `AGENTS.md` の handoff 段落の版表記を ECO 参照に置換(v0.3 固定を外す)。
3. `method/improvements.md`: 本節+EXP-20260912-01 に v0.4 追加指標を注記。

**採らない**: AI 推定を既定にする(§4 の条件で再検討)/ 第 5 の mode(CHAT 等)の新設 / product-profile への正本化(別 ECO)/ self-conformance の `.claude/skills` 検査拡張。

## 2. 影響なし予測(製造前・凍結)

diff は SKILL.md・AGENTS.md・improvements.md+台帳系のみ。C12(AGENTS.md リンク)は文言変更のみでリンク先不変・C7 不変・C13 は新リンクなし。tools・templates・hooks・.github diff 0。
worklist: 新規 ID なし(EXP-20260912-01 の継続行に追記)・警告 0。

## 3. 受入

- **V1**: SKILL.md §1 に `Free-style span` と `One-way ratchet`・§2.3 に F6・§2.7 に区間規則・§4 に ⑥⑦⑧がある(grep)。**V2**: AGENTS.md リンク解決(C12 PASS)。
  **V3**: self-conformance 全 PASS・CI 緑・窓= 3 文書+台帳系。**V4**: 製造者較正のみ。**V5(クローズ条件でない)**: 指標 ⑥⑦⑧を EXP-20260912-01 で測る。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-071` の出力を開始 artifact として読んだ)

- 分類= 既裁定の適用実装(user AGREE+起票指示)。baseline `bf0924e`= **confirmed** / 次番 071= **confirmed**(grep 0)/ §2.7 の 1 通単位の適用外の存在= **confirmed**(実読)/
  凍結の非該当= **confirmed** / 同一ファイルへの進行中 ECO なし(ECO-070 は verified)= **confirmed**。
- job ビュー: required_skills= `["preflight"]`・skills_missing= `[]`(order 生成後に出力)
- 開始判定: **PROCEED**・override 0。

## 4. 製造と受入の実測(2026-09-12・同一 commit)

- 製造物: SKILL.md v0.4(description・§1 Scope・§2.1・§2.3 F6・§2.7・§3 例・§4)・AGENTS.md 1 行・improvements.md。
- **V1**= PASS(grep: `Free-style span` 1・`One-way ratchet` 1・`F6 区間` 1・`片方向ラチェット` ≥2・`⑧AI の推定` 1)/ **V2**・**V3**= §5。

## 5. 受入完了の記入予定(accept commit で書き換え)

- (accept commit で記入: V3 の self-conformance・CI・窓閉鎖)
