# Change Order — ECO-087(完了ゲート G4 に妥当性確認の記録を足す — playbook §7 の項 5 と As-Built の validation 欄 / candidate・文書のみ・verified)

> 指示: user 2026-09-30「OBS-07の妥当性確認も進めて」→ DECIDE「B」(A 記帳のみ / B 記録欄 / C 要求のみから独立オラクルを作る工程 — C は採らない)。
> **起票と製造を同一 commit で行う**(文書のみ・ECO-082/086 の型)。受入は製造者較正のみ。verified 昇格は self-conformance PASS と CI 結論を観測した後の受入 commit で。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-sonnet-5-5`・Claude Code・来歴 **self-reported**
- producer: EQ-005
- 独立検査: なし(文書のみ・製造者較正のみ。inspector 行は置かない)

## 0. 実測(起票根拠・2026-09-30)

- 前回の記帳(OBS-20260929-07)は推論だった。実リポの記録に、**仕様の欠落が全検査合格のまま通った実例**がある:
  UnitConv ECO-003(結果が有限でない場合が仕様に無く、実装は仕様どおり・固定オラクルにも行が無い。発見= 運転員の境界プローブ〔固定オラクル外〕・潜伏 2 日)/
  ViewPrism2 ECO-004(各画面の表示契約が要件化されていない。発見= ユーザー確認)。ViewPrism2 ECO-005・006 も仕様の欠落だが、発見経路は確認していない。
- 実例はすべて「仕様に書かれていなかった欠落」で、OBS が書いた「仕様が要求を取り違えた」型の実例は見つかっていない。
- 発見と是正の経路(探索プローブ層・人間 golden・ユーザー確認・playbook §6.4 の帰属)は既にあり、上の実例では機能した。欠けているのは、仕様を経由しない確認を独立した役割として記録する場所。
- 現状の完了ゲート G4(playbook §7)は 4 項(完了の定義の充足・納品物の存在・Service BOM・引き渡しサマリ)で、要求原文と実物の突き合わせを問わない。50-as-built テンプレの inspections は固定オラクルと探索プローブの結果のみ。

## 1. 変更要求(凍結・文書のみ・candidate)

1. `method/bomdd-playbook-v1.md` §7 の G4 に項 5「妥当性確認の記録」を足す: As-Built の `validation` に、要求原文と実物を仕様を経由せずに突き合わせた確認(実施者・入力に仕様/固定オラクルを含めたか・使った要求と結果、または未実施の理由)を記録する。
   実施を強制する検査は無い。探索プローブ・人間 golden・ユーザー確認は、この役割を担うなら本欄に書く。
2. `method/templates/50-as-built.yaml` に `validation` 欄(performed_by / spec_given / requirements_used / result / not_performed_reason)を足す。
3. `bomdd/60-change-register.yaml` に本 ECO を登録し、`method/improvements.md` に本節と EXP-20260930-02(効果の計測)を置く。

**採らない**: 検査・lint・ゲートの追加 / 要求のみから独立にオラクルを作る工程(案 C)/ 既存製品リポへの遡及 / テンプレート以外(product-profile・kit)の変更 / OBS-20260929-07 の昇格(据え置き)。

## 2. 影響なし予測(製造前・凍結)

diff= playbook(§7 に 1 項)・50-as-built テンプレ(validation 欄)・improvements.md+台帳系(order・register)のみ。schemas・tools・hooks・.github diff 0。
テンプレートの YAML は厳格パースを通る(C1)・C4 scaffold 煙試験・C10 判定不変(validation は宣言エッジの対象外)・C13 リンク不変・worklist 警告 0。既設の製品リポは kit 再設置まで非波及。

## 3. 受入条件(製造前に凍結・二部形)

- V1(条件): playbook §7 の G4 に「妥当性確認の記録」を含む項が 1 つあり、50-as-built テンプレの例の記録に `validation:` が 1 つあること — 検査法: grep(注記や別の節に同じ語が現れる場合は該当箇所を実読で確認する)。
- V2(条件): diff が allowed_paths のみで、schemas・tools・hooks・.github が diff 0 であること — 検査法: `git diff --stat baseline..head`。
- V3(条件): self-conformance 全 PASS(exit 0 観測後に commit)・CI success であること。
- V4(条件): 製造者較正のみ・較正 receipt(trigger ①)があること。
- V5(条件・クローズ条件でない): 効果は EXP-20260930-02 で測ること。

## /preflight receipt(起動経路: **自発** — 既裁定の適用実装)

- 分類= 既裁定の適用実装(user DECIDE「B」)。baseline `e8173ec`= **confirmed**(作業木 clean・push 済み)/ 次番 087= **confirmed**(register に id 0 件)/
  変更対象 2 ファイルの現状= **confirmed**(実読: G4 は 4 項・inspections に妥当性の欄なし)/ 同じファイルを窓に持つ進行中の ECO がない= **confirmed**(進行中は ECO-079〔implemented〕のみ・playbook を含まない)/
  EQ-005 が設備台帳にある= **confirmed**(ECO-086 で登録)。
- 開始判定: **PROCEED**・override 0。

## 4. 製造の実測(2026-09-30・同一 commit 8d789cf)

- 製造物: playbook §7 の G4 に項 5(妥当性確認の記録)/ 50-as-built テンプレに validation 欄 / improvements.md(節+EXP-20260930-02)/ register(ECO-087)。
- **V1**= PASS(観測: playbook の「妥当性確認の記録」1 件〔G4 の項 5〕・50-as-built テンプレの行頭 `validation:` 1 件)。
- **V2**= PASS(観測: `git diff --name-only e8173ec 8d789cf` は allowed_paths の 5 ファイルのみ。schemas・tools・hooks・.github は diff 0)。

## 5. クローズ(2026-09-30・verified・製造者較正のみ)

- **V3**= PASS(観測: 変更を stage してから self-conformance を実行 → **exit=0 全 PASS** → witness〔tree c1a23e9ab426〕→ 入口 dry `ADVANCE ECO-087 OK` → 製造 commit 8d789cf → push → CI run 36720317759 **success**〔headSha 照合〕)。
  diff 監査の窓: baseline `e8173ec` → head `8d789cf`(**窓閉鎖**・受入 commit は台帳系のみ)。
- **V4**= 製造者較正のみ(独立検査なし)・下の較正 receipt。register: `implemented → verified`・head 凍結。
- **V5(非クローズ条件)**: EXP-20260930-02 で次の新規案件の As-Built の validation 欄を数える。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格・receipt_author_role= producer。文書のみの変更)

- 査定した主張と判定:
  1. 「G4 に妥当性確認の記録の項が入り、As-Built テンプレに validation 欄が入った」— **observed / 適格**(grep・V1)。
  2. 「変更は文書のみで、検査・スキーマ・ツールは変わっていない」— **observed / 適格**(窓の diff・V2)。
  3. 「仕様の欠落が全検査合格のまま通った実例がある」— **observed / 条件付き適格**(UnitConv ECO-003 と ViewPrism2 ECO-004 の記録の実読。測っていない次元= 実例の一般性〔2 製品〕・ViewPrism2 ECO-005/006 の発見経路)。
  4. 「欄を足すと妥当性確認が記録される」— **unknown(未測定・EXP-20260930-02)**。
- 検出した計器欠陥(帰属つき): 製造物 0 件。
- 検出力の限界: V1 は文字列の有無しか測らず、欄の書式が書き手に伝わるかは読解。実例の数え方は記録の実読で、網羅的な走査ではない。効果は未測定。独立検査なし。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 読解 | 項 5 は「強制しない・記録の有無で未実施が見える」と自分の範囲を宣言している |
  | Q2 | asked | NA 相当 | — | 文書変更に known-bad 対照なし(宣言) |
  | Q3 | asked | observed/適格 | 実測 | 2 ファイルを個別の grep で確認 |
  | Q4 | asked | observed/適格 | 実測 | 実例は実リポの実ファイルを直接読んだ(宣言 fixture なし) |
  | Q5 | asked | observed/適格 | 実測 | 未測定(効果・発見経路)を unknown として分離 |
  | Q6 | asked | observed/適格 | 実測 | 検査 exit 観測 → witness → 入口 dry → commit → push → CI success(条件で結んだ順) |
  | Q7 | asked | NA | — | 陽性対照なし(文書) |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | witness(ECO-087.json・tree c1a23e9ab426)・commit 8d789cf・CI run 36720317759 を同一個体として照合 |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」 |
  | Q11 | asked | observed/条件付き適格 | 読解 | 実例を「欠落型」と「取り違え型」に分け、後者の実例は 0 と記録した(OBS-07 は部分ごとに数え据え置き) |

- このクローズが支持しないもの: 欄を足した効果(EXP-20260930-02)/ 妥当性確認が実施されること(強制していない)/ 取り違え型の実例の存在 / 要求のみから独立にオラクルを作る工程(案 C・採っていない)/ 既存製品リポの是正 / 独立検査による確認。
