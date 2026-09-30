# Change Order — ECO-088(As-Built の証拠行の書き方を注記する — 各エントリは受入対象の全 CP を今回の個体で再測定した行として持つ / candidate・文書のみ)

> 指示: user 2026-09-30「OBS-08の増分記録も進めて」→ DECIDE「B」(A 記帳の訂正のみ / B 書き方の規約 / C 規則を「特性ごとの最新の証拠」へ変更 — C は採らない)。
> **起票と製造を同一 commit で行う**(文書のみ・ECO-082/086/087 の型)。受入は製造者較正のみ。verified 昇格は self-conformance PASS と CI 結論を観測した後の受入 commit で。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-sonnet-5-5`・Claude Code・来歴 **self-reported**
- producer: EQ-005
- 独立検査: なし(文書のみ・製造者較正のみ。inspector 行は置かない)

## 0. 実測(起票根拠・2026-09-30)

証拠の所在= [bomdd/reports/eco-088-incremental/](reports/eco-088-incremental/incr-reach.py)(測定スクリプト)。

- OBS-20260929-08 は「実リポ 7 本中 5 本が不合格でない理由で受入証跡の検査(R-050)で赤になる。原因は増分記録」と読んでいた。受入対象の CP を、最後に証拠行が現れたエントリで分類し直した:
  赤の大半は**証拠行が無い**(LibraryLending 12/12・ViewTube 27/28・TimetableAdv 402/427)— 規則の指摘は正当で直す対象ではない。
  **増分記録が原因なのは UnitConv の 5 件と TimetableAdv の 18 件(前のエントリで合格・最新で未再測定)だけ**。
- 既に守れているリポがある: Plm は各 ECO のエントリで受入対象の全 CP を再測定した行を持ち(17/17)、Transfer03 も同様。UnitConv は変更した CP だけを記録していた。
- 現状の 50-as-built テンプレは、エントリが受入対象のどこまでを持つかを書いていない。
- 限界(測定の): LibraryLending は履歴全体で証拠行が 0 件(別の書式で記録している可能性は未確認)/ TimetableAdv の 427 件に廃止済みの製造単位が含まれるかは分けていない / 前のエントリの合格が現在の個体の証拠かは記録だけでは分からない。
- 訂正(正直記載): OBS-20260929-08 の「原因は増分記録」は過大だった。上記の内訳で訂正し、improvements.md の該当行に追記した。

## 1. 変更要求(凍結・文書のみ・candidate)

1. `method/templates/50-as-built.yaml`: `test_evidence_refs` の注記に「各エントリは受入対象の全 CP について、このエントリの個体に対して再測定した行を持つ。再測定していない CP は行を書かない(前のエントリの合格は今回の個体の証拠ではない)」を置く。
   PLM-ready checklist に 1 行(最新エントリは全 CP について合格行を持つ・R-050 の前提・実例つき)。
2. `bomdd/reports/eco-088-incremental/` に測定スクリプトを保存。
3. `bomdd/60-change-register.yaml` に本 ECO を登録。`method/improvements.md` に本節・OBS-20260929-08 の訂正・EXP-20260930-03。

**採らない**: R-050 の規則文言・BomDD-Plm の実装の変更(案 C)/ 「最新」の定義の変更 / playbook の改訂 / 既存製品リポの記録の是正 / 証拠行が無い製品リポ(LibraryLending・ViewTube・TimetableAdv の大半)への対応。

## 2. 影響なし予測(製造前・凍結)

diff= 50-as-built テンプレ・improvements.md+台帳系(order・register・reports)のみ。schemas・tools・hooks・.github・playbook diff 0。
テンプレートの YAML は厳格パースを通る(C1)・C4 scaffold 煙試験・C10 判定不変・C13 リンク不変・worklist 警告 0。既設の製品リポは kit 再設置まで非波及。R-050 の判定は全リポで不変。

## 3. 受入条件(製造前に凍結・二部形)

- V1(条件): 50-as-built テンプレの `test_evidence_refs:` の行に「再測定」を含む注記があり、PLM-ready checklist に「ECO-088」を含む行が 1 つあること — 検査法: grep(別の箇所に同じ語が現れる場合は該当箇所を実読で確認する)。
- V2(条件): diff が allowed_paths のみで、schemas・tools・hooks・.github・playbook が diff 0 であること — 検査法: `git diff --stat baseline..head`。
- V3(条件): self-conformance 全 PASS(exit 0 観測後に commit)・CI success であること。
- V4(条件): 製造者較正のみ・較正 receipt(trigger ①)があること。
- V5(条件・クローズ条件でない): 効果は EXP-20260930-03 で測ること。

## /preflight receipt(起動経路: **自発** — 既裁定の適用実装)

- 分類= 既裁定の適用実装(user DECIDE「B」)。baseline `b5ba425`= **confirmed**(作業木 clean・push 済み)/ 次番 088= **confirmed**(register に id 0 件)/
  変更対象の現状= **confirmed**(実読: テンプレに再測定の記述なし)/ 同じファイルを窓に持つ進行中の ECO がない= **confirmed**(進行中は ECO-079〔implemented〕のみ・templates を含まない)/ EQ-005 が設備台帳にある= **confirmed**。
- discovered(推測・契約外): 直前の記帳(OBS-08)の原因の見立てが実測と違う= **contradicted → 是正**(§0 訂正)。
- 開始判定: **PROCEED**・override 0。
