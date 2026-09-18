# Jev 設備認定 — 第 1 回(EXP-20260918-01・receipt の実在を意味で読めるか)

> 目的: TypeSafe/Jev(System One・型付き判定モデル)を BomDD の「自己申告」意味検査の別計器として使う前に、
> 既存のラベル付き検体で感度と偽陽性を測る(設備認定・equip-01〜03 の型)。工程への組み込みは本試験の後。
> 裁定: user 2026-09-18 AGREE(方針)→ DECIDE A(鍵ファイル `C:\Users\akira\.typesafe\api_key` を user が作成= A・鍵設定済み)。
> 本節「1. 設計」は**結果受領前に固定**(スクリプト `jev_qual_01.py` の定数と同一・結果は §2 以降)。

## 1. 設計(結果受領前に固定・2026-09-18)

- **検体**(合計 78 リクエスト= ja 36+en 35+real 7・疎通 dry 1 は別ファイル):
  - C17 fixture 18 本(`self-conformance.py _C17_FIXTURES`・受入 receipt の use/mention)— 腕 ja(原文)/ en(当方訳)。
  - C16 fixture 17 本(`_CONVERGE_FIXTURES`・収束 receipt)— 腕 ja / en。
  - 病的 receipt P1(見出し内の否定「較正 receipt は省略した」+本体ラベル完備— C17 限界 (5)「機械は通す・意味は測らない」)— ja のみ。
  - 実検体 R1〜R7(order の節・ja のみ): R1〜R3= ECO-071/075/076 の較正 receipt(実施済み)/ R4= ECO-076 §4 実測(receipt 様式でない実施報告)/
    R5= ECO-076 §3 受入(計画)/ R6= ECO-075 §3 受入(候補)/ R7= ECO-076 §5 の製造 commit 時点(cea4b41・「未記入」placeholder)。
- **ラベル**(Jev から独立): fixture の `want_ok` は「gate が通るか」であり「receipt が実質として存在するか」ではないので、次で写像する
  — receipt 実在= **positive**: C17 F1・F9・F17 / C16 F2・F14・F16・F17(F14 は C16 では様式違反で FAIL だが、意味上は「round 1 = 2 件」という実施報告なので positive・事前宣言)。
  それ以外(receipt なし・免除宣言・fence 内の様式例・省略の言及・status 対象外)= **negative**。P1= negative。R1〜R4= positive・R5〜R7= negative。
  → fixture 36 本(ja)= positive 7・negative 29。en 35 本= positive 7・negative 28。real 7 本= positive 4・negative 3。
- **質問**(固定・英語・Noul 1 問): 「`section` は実際に実施された査定(較正 receipt / 収束 receipt)の結果を報告しているか。様式例・テンプレート・
  省略/免除の言及・後で書くという記述・検査計画・無関係な節なら no」。criteria true/false は同旨。state= `{section, context(order の 1 節・台帳 status)}`。
- **閾値**(事前宣言): P ≥ 0.5 → positive 予測。拮抗帯 0.4〜0.6 は件数を別掲。
- **認定条件**(事前宣言・EXP-20260918-01 の「15/17」を検体数に合わせて比率で読み替え= 0.88): ja 腕で **negative の正答 ≥ 26/29 かつ positive の正答 ≥ 6/7**、
  かつ **P1 が negative 側**。未達なら en 腕の値で再判定(CJK 差の分離)・それも未達なら「採らない」。real 7 本は N が小さいので認定条件に含めず別掲(実運用文の長さでの挙動観察)。
- **記録**: `results.jsonl`(検体 id・腕・ラベル・state の sha256・model・P・usage)。鍵は表示・記録しない。到達不能・認証失敗は UNMEASURABLE として記録し PASS に数えない。
- **限界(宣言)**: 検体は receipt 文(候補 3)であり handoff 本文(候補 1)の認定ではない / en 腕の訳は当方(製造者)の訳で独立でない / 実検体の positive は当方が書いた receipt(自己適用)。

## 2. 結果(2026-09-18・78 リクエスト・応答 78・エラー 0・resolved model `jev-1.13.0`・tokens in 42,738 / out 1,794)

集計= [summary.md](summary.md)(腕別指標・ja/en 差・検体別表)。生記録= [results.jsonl](results.jsonl)。

| 腕 | N | negative 正答 | positive 正答 | 拮抗帯 0.4〜0.6 | 認定条件 |
|---|---|---|---|---|---|
| ja | 36 | **26/29**(達成 ≥26) | **4/7**(未達 ≥6) | 6 | **未達** |
| en | 35 | 24/28 | 4/7 | 0 | 未達(ja より悪い) |
| real | 7 | 1/3 | 4/4 | 0 | (認定条件外・別掲) |

- **判定: 認定条件 未達 → 事前宣言どおり、この質問設計では「採らない」**。en 腕でも改善しないので CJK 精度は主因ではない(ja/en の判定反転は 35 本中 1 本・|Δp|≥0.3 は 0)。
- **何が当たったか**: 病的 receipt P1(見出し内の否定+本体ラベル完備— C17 が構造的に通す検体)= **P 0.04 で negative**(機械の限界 (5) を意味で埋めた 1 例)。
  実 receipt R1〜R3= 0.95/0.96/0.96・実測節 R4= 0.93・未記入 placeholder R7= 0.04・免除宣言(C17 F4/F6・C16 F5〜F9)と status 対象外(F3/F18)はすべて negative。
- **何が外れたか(3 群)**:
  1. **計画 vs 実施**: 実検体の受入計画節 R5(0.70)・R6(0.82)を「実施済みの報告」と読んだ。V1〜V5 の列挙(grep で確認する、等)を結果と区別していない。**候補 3(receipt の観測/予定)で
     最も測りたい弁別がここで、2/3 失敗**。
  2. **fixture の positive が薄い**: C17 F1/F9/F17 の本文は「査定した主張と判定…」の省略記号だけで、実施報告としての実質がない(構造検査用の stub)。Jev はこれを negative 側(0.35〜0.42)に
     置いた— ラベル(want_ok 由来)の方が意味検査には粗い。逆に C17 F2「V1 PASS」(0.72)は結果報告と読んだ。**fixture の positive 3 本の MISS は検体側の欠陥が濃く、計器の欠陥と断定できない**。
  3. **fence 内の様式例**: C16 F10〜F12(fence 内の receipt 例)を 0.48〜0.83 で content として読む(en 腕はすべて 0.67 以上)。fence の use/mention は Jev に任せず code が先に剥がす
     (self-conformance の `_strip_fences` と同じ分業)— 設計で吸収できる外れ。
- **示唆(第 2 回の設計入力・実施は別裁定)**: (a) 検体を実 order の節に寄せる(計画節 / 実測節 / クローズ節 / placeholder / receipt を各 ECO から機械抽出・ラベルは見出しと台帳 status
  から導出)(b) 質問を Noul 1 問から **Choice**(performed / planned / template-or-example / omitted-or-exempt)に変え、計画と実施の弁別を候補として明示する(c) fence は code で
  剥がしてから渡す(d) 認定条件は planned→performed の誤読率で切る(第 1 回 2/3)。
- **費用**: 78 リクエストで input 42,738 / output 1,794 tokens(単価は docs 未記載)。所要 約 2 分。
