# Change Order — ECO-088(As-Built の証拠行の書き方を注記する — 各エントリは受入対象の全 CP を今回の個体で再測定した行として持つ / candidate・文書のみ・verified)

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

## 4. 製造の実測(2026-09-30・同一 commit 35d2ae2)

- 製造物: 50-as-built テンプレの注記 2 箇所(test_evidence_refs の再測定の注記・checklist 1 行)/ OBS-20260929-08 への訂正の追記 / improvements.md(節+EXP-20260930-03)/ register(ECO-088)/ reports(測定スクリプトと基準線)。
- **V1**= PASS(観測: 50-as-built テンプレの `test_evidence_refs:` の行に「再測定」を含む注記 2 行〔33・34 行目〕・checklist に「ECO-088」を含む行 1 つ〔66 行目〕。`ECO-088` の出現は 2 件で、どちらも該当箇所)。
- **V2**= PASS(観測: `git diff --name-only b5ba425 35d2ae2` は allowed_paths の 6 ファイルのみ。schemas・tools・hooks・.github・playbook は diff 0)。

## 5. クローズ(2026-09-30・verified・製造者較正のみ)

- **V3**= PASS(観測: 変更を stage してから self-conformance を実行 → **exit=0 全 PASS** → witness〔tree 8993ad2ba5b4〕→ 入口 dry `ADVANCE ECO-088 OK` → 製造 commit 35d2ae2 → push → CI run 36726478955 **success**〔headSha 照合〕)。
  diff 監査の窓: baseline `b5ba425` → head `35d2ae2`(**窓閉鎖**・受入 commit は台帳系のみ)。
- **V4**= 製造者較正のみ(独立検査なし)・下の較正 receipt。register: `implemented → verified`・head 凍結。
- **V5(非クローズ条件)**: EXP-20260930-03 で、次に As-Built へエントリを足す製品の最新エントリの再測定行の割合を数える。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格・receipt_author_role= producer。文書のみの変更)

- 査定した主張と判定:
  1. 「As-Built テンプレに、各エントリは受入対象の全 CP を今回の個体で再測定した行を持つ、という注記が入った」— **observed / 適格**(grep・V1)。
  2. 「変更は文書のみで、R-050 の規則・Plm・スキーマは変わっていない」— **observed / 適格**(窓の diff・V2)。
  3. 「赤の大半は増分記録でなく証拠行の欠如で、増分記録が原因なのは 23 CP のみ」— **observed / 条件付き適格**(測定スクリプトの再実行で再現。測っていない次元= LibraryLending の別書式の可能性・TimetableAdv の廃止済み製造単位・前のエントリの合格が現在の個体の証拠か)。
  4. 「注記を足すと増分記録の製品でも最新エントリが全 CP を持つようになる」— **unknown(未測定・EXP-20260930-03)**。
- 検出した計器欠陥(帰属つき): 製造物 0 件。上流(私の前回の記帳)1 件 — OBS-20260929-08 の「原因は増分記録」が過大だった(§0 で訂正済み・帰属= 記帳の見立て)。
- 検出力の限界: V1 は文字列の有無しか測らず、注記が書き手に伝わるかは読解。分類は記録の形だけで証拠の中身は見ていない。効果は未測定。独立検査なし。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 読解 | 注記は「強制しない・行が無いことで未再測定が見える」と自分の範囲を宣言している |
  | Q2 | asked | NA 相当 | — | 文書変更に known-bad 対照なし(宣言) |
  | Q3 | asked | observed/適格 | 実測 | 注記と checklist を別々の grep で確認 |
  | Q4 | asked | observed/適格 | 実測 | 分類は実リポの実ファイルを直接読む(宣言 fixture なし) |
  | Q5 | asked | observed/適格 | 実測 | 未測定(効果・別書式・廃止済み単位)を unknown として分離 |
  | Q6 | asked | observed/適格 | 実測 | 検査 exit 観測 → witness → 入口 dry → commit → push → CI success(条件で結んだ順) |
  | Q7 | asked | NA | — | 陽性対照なし(文書) |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | witness(ECO-088.json・tree 8993ad2ba5b4)・commit 35d2ae2・CI run 36726478955 を同一個体として照合 |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」 |
  | Q11 | asked | observed/適格 | 実測 | 入力クラス(最新で合格・前のエントリで合格・前のエントリで不合格・どこにも行なし)を分けて数えた — 集計すると「増分記録」が主因に見えた |

- このクローズが支持しないもの: 注記の効果(EXP-20260930-03)/ 前のエントリの合格が今回の個体の証拠であること / 規則(R-050)の変更(案 C・採っていない)/ 証拠行が無い製品リポの是正 / 既存製品リポの記録の是正 / 独立検査による確認。
