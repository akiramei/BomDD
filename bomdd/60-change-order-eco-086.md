# Change Order — ECO-086(不変条件から検査行への対応欄をテンプレートへ足す — Control Plan の invariant_refs・仕様 §3 の「検査する CP」列・M-BOM の INV 先頭記法 / candidate・文書のみ)

> 指示: user 2026-09-30「OBS-06の特性単位の対応を進めて」→ DECIDE「B」(A 記帳のみ / B テンプレートと規約 / C 機械検査まで — C は採らない)。OBS-20260929-06 の着手条件「実例 1 件、または裁定」を、この指示で満たしたものとして扱う。
> **起票と製造を同一 commit で行う**(文書のみ・ECO-082 の型)。受入は製造者較正のみ。verified 昇格は self-conformance PASS と CI 結論を観測した後の受入 commit で。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-sonnet-5-5`・Claude Code・来歴 **self-reported**
- producer: EQ-005
- 独立検査: なし(文書のみ・製造者較正のみ。inspector 行は置かない)
- 設備台帳: 本 ECO で EQ-005(claude-sonnet-5-5 @ claude-code・unqualified)を登録する(セッション途中で /model により切替わった — EQ-001 は claude-fable-5-1)。

## 0. 実測(起票根拠・2026-09-30)

証拠の所在= [bomdd/reports/eco-086-inv-reach/](reports/eco-086-inv-reach/baseline.md)(測定スクリプトと基準線)。

- 仕様が採番した不変条件(INV)が、後段のどこまで字面で届くか(実リポ 7 本のうち定義のある 5 本): M-BOM へは多くが届く(Plm 9/10・UnitConv 6/7・Transfer03 8/8・ViewPrism2 15/15・ViewTube 0/17)が、
  **検査計画の行へ届くのは 0〜3 割**(Plm 1/10・UnitConv 2/7・Transfer03 0/8・ViewTube 0/17・ViewPrism2 3/15)。固定オラクルには一部が届く(UnitConv 5/7・ViewPrism2 7/15)。
- テンプレートの現状: 20-spec §3 は INV を採番するが検査への対応欄がない / 32-mbom の invariants は自由記述で INV ID を書く規約がない / 33-control-plan の verifies は E-*/M-* まで(不変条件を指す欄がない)。
  現行の門(R-011)は「部品に検査行が 1 本ある」ことしか見ず、不変条件ごとの検査は意味しない。
- スキーマ側: INV 族は strictness advisory・定義サイトが散文の表で機械可読でない(id-grammar の note に明記)。機械検査(案 C)は定義サイトの構造化を先に要する。
- 限界(測定の): 字面の一致だけ。検査行が INV 番号を書かずに実質的に検査している場合は「届かない」に数える。LibraryLending と TimetableAdv は INV の表形式が違い測れていない。

## 1. 変更要求(凍結・文書のみ・candidate)

1. `method/templates/33-control-plan.yaml`: 例の行に `invariant_refs: []`(この行が検査する仕様 §3 の INV ID)を足し、注記に「空= 検査に届いていない不変条件」「検査しない不変条件は 20-spec §3 に理由を書く」を置く。末尾の PLM-ready checklist に 1 行。
2. `method/templates/20-spec.md` §3: 表に第 4 列「検査する CP(または未検査の理由)」を足し、空欄のまま製造へ渡さない旨の注記を置く。
3. `method/templates/32-mbom.yaml`: `invariants` の各行は仕様 §3 の INV ID を先頭に書く、という注記と例の書き換え。
4. `bomdd/70-equipment.yaml` に EQ-005 を登録。`method/improvements.md` に本節と EXP-20260930-01(効果の計測)。

**採らない**: INV 定義サイトの構造化 / ref-edges・id-grammar・Plm の変更(案 C)/ 新しい lint 規則 / playbook の改訂(N=1 のため candidate はテンプレートの注記に留める)/
既存製品リポへの遡及適用 / 既存の product-profile・kit への配布物の変更(テンプレートは bomdd-init が次回配布時に拾う)。

## 2. 影響なし予測(製造前・凍結)

diff= templates 3 ファイル・70-equipment.yaml・improvements.md+台帳系(order・register・reports)のみ。schemas・tools・hooks・.github・playbook は diff 0。
テンプレートの YAML は厳格パースを通る(C1)・C4 scaffold 煙試験・C10(テンプレ空振り検査)判定不変(invariant_refs は宣言エッジの対象外)・C13 リンク不変・worklist 警告 0。
既設の製品リポは kit 再設置まで非波及。

## 3. 受入条件(製造前に凍結・二部形)

- V1(条件): 33-control-plan テンプレに `invariant_refs` が 1 件・仕様テンプレの §3 表に「検査する CP」列が 1 件・32-mbom テンプレの invariants 例が `INV-` で始まること — 検査法: grep。
- V2(条件): diff が allowed_paths のみで、schemas・tools・hooks・.github・playbook が diff 0であること — 検査法: `git diff --stat baseline..head`。
- V3(条件): self-conformance 全 PASS(exit 0 観測後に commit)・CI success であること。
- V4(条件): 製造者較正のみ・較正 receipt(trigger ①)があること。
- V5(条件・クローズ条件でない): 効果は EXP-20260930-01 で測ること(次の新規案件で仕様の INV が検査行に届く率)。

## /preflight receipt(起動経路: **自発** — 既裁定の適用実装)

- 分類= 既裁定の適用実装(user DECIDE「B」)。baseline `0f8805d`= **confirmed**(作業木 clean・push 済み)/ 次番 086= **confirmed**(register に id 0 件)/
  変更対象 3 テンプレの現状= **confirmed**(実読)/ 同じファイルを窓に持つ進行中の ECO がない= **confirmed**(進行中は ECO-079〔implemented〕のみ・templates を含まない)。
- discovered(推測・契約外): 製造者の設備が台帳に無い(EQ-005 未登録)= **confirmed**(実読)→ §1-4 で登録。
- 開始判定: **PROCEED**・override 0。
