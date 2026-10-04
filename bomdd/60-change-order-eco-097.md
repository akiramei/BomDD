# Change Order — ECO-097(M-BOM / Control Plan 再設計 — 欄の所有を「人の裁定層(E 側)」と「AI の導出層(M・CP)」に分け、2 製造単位・1 製品で試す〔事前登録つき・起票〕)

> 指示: user 2026-10-05「M-BOM / Control Plan 再設計に着手して。E-BOM は人間の裁定を行う場所であり、M-BOM / Control Plan はその裁定に基づいて AI が判断する場所。責任分担であり、決めの問題。
> 致命的な欠陥やトレードオフでは許容できない問題があれば、止まって相談」。
> 順序は既決のまま(ECO-090 §1・ECO-094): **文書より先に製品で試す**。本 ECO の窓では playbook・テンプレート・スキーマ・ツールを改訂しない。反映は試行の評価の後に別 ECO。
> **本 ECO は起票+事前登録まで**。設計の収束は未達(下の receipt)— 製品側の着手はその扱いの決定の後。

## 担当設備(equipment)

- 起票・設計: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-001
  (BomDD 側の記録・事前登録・導出〔統括 AI の役〕。製品側の製造は ViewPrism2 の型〔Codex 工場+退避隔離・独立レビュー R8〕に従い、その配員は製品側 ECO に記す)
- 独立検査: BomDD 側(記録・事前登録)は製造者較正のみ。製品側の導出の意味の審査は異系統の検査官(EQ-002)— 事前登録 R6。

## 0. 根拠(起票・2026-10-05・実測は読み取りのみ)

- **M-BOM が設計の内容を自分の言葉で持つ**(ECO-090 §0.1): E-BOM と機械で突き合わせられない並行の記述。今回の再計数(ViewPrism2 f622c3c / ViewTube 0c3e42d1):
  ViewPrism2= E の不変条件 288 行(ID つき 48)・M 69 行(ID つき 16)。ViewTube= E 48 行・M 114 行(ID つき 0)— **ViewTube は M の方が多くを持つ逆の形**。
- **実データに 3 種の行がある**(ViewPrism2 の 2 単位を実読): ①裁定層に同じ内容がある行(例 M-THUMB-008「INV-009 元画像へ書き込まない」= E-THUMB-020 に同文)
  ②設計の内容だが裁定層に無い行(例「読み取り不能キャッシュは削除して再生成」「EXIF 適用は表示系のみ — pHash 入力には適用しない」)③どう作るかの行(例 M-DB-007「接続は単一共有+SemaphoreSlim シリアル化」)。
  ②は「人が裁定していない設計の内容を、M が持ち、製造に使っている」状態で、責任分担の境界が欄に現れていない実例。
- **CP 行は裁定層の ID を持たない**: ViewPrism2 の CP 65 行は `requirement_refs` 0 行・`invariant_refs` 0 行・`verifies` の欄なし(結びつきは E / M 側の `acceptance_refs` だけ)。
  ECO-144 では約束(REQ-104〜106)との対応を vector の文言に書いた。その結果、1 つの約束の測定不能が行の区分に現れなかった(OBS-20261003-03・ECO-094 M3 1/2)。
- **CP は受入の入力として読まれない**(OBS-20261002-01・2/3)。ViewPrism2 ECO-143 以後は、CP 行ごとの結果の表が承認に添えられる。表のキーは CP 行(AI の導出層の ID)で、人が裁定した ID ではない。
- **「いつ測るか」「落ちたら何をするか」は CP 行に欄が無い**(ECO-090 M3: ViewPrism2 0/65)。ECO-144 は振り分け(製品修正 / 測定系復旧)を vector の文言に書いた。
- **調達の方針も同じ形**: 32 の `procurement.substitutable: false`(M 側)が、ECO-144 で人が裁定した約束(REQ-104 宣言された結合)と同じ内容を別の場所に持つ。

## 1. 設計(凍結候補 — 収束の扱いの決定後に凍結)

### 1.1 原則(user の決め)

- **裁定層**= 人が裁定する場所: 要求(10)・仕様(20・不変条件と数値)・E-BOM(30)・保守上の約束への参照(53)。版を `bom_version`+tag で固定する(設計リリース・ECO-094 で試行済み)。
- **導出層**= AI が判断する場所: M-BOM(32)・Control Plan(33)・工程表(34)・テストの trait・承認に添える表。統括 AI が、固定された裁定層の版から導出し、人の個別承認の対象にしない。
- 導出層は**裁定層の内容を自分の言葉で持たない**。必要な設計の内容が裁定層に無ければ、それは空白であり、人へ戻して裁定層へ書き戻す(playbook §9「裁定の出力は情報基盤へ書き戻す」の適用)。
- 人へ戻す判断は 3 種だけ: 新しい機能 / 新しい約束(設計の内容)/ 導出不能(許容差・期待値が裁定層から決まらない等)。それ以外は AI が決めて記録する。

### 1.2 欄の所有(1 欄 1 行・試行で使う範囲)

| ファイル | 欄 | 所有 | 再設計での扱い |
|---|---|---|---|
| 30 E-BOM | 品目・purpose・classification・requirement_refs・invariants・depends_on・nfr_targets・display_contracts | 人 | 不変。参照される不変条件の行には ID を付ける(必要になった行だけ) |
| 30 E-BOM | acceptance_refs(→ CP) | AI | E から導出層への参照は持たない向きが正(ECO-094 M4)。試行では変更せず、件数の記録のみ |
| 32 M-BOM | ebom_refs | AI | 参照先の E 品目の不変条件を**すべて引き継ぐ**(写さない) |
| 32 M-BOM | invariants | — | 3 分類で解消: 参照化(行を消し ebom_refs に任せる・ID があれば ID だけ残す)/ 人へ戻す(E へ書き戻してから消す)/ 製造手段(下の欄へ移す) |
| 32 M-BOM | manufacturing_decisions(新・試行の欄名) | AI | どう作るかの決定(並行制御・ライブラリの使い方・分割)。K-BOM の参照つき |
| 32 M-BOM | artifact・interface_contract・fmea・routing_refs・(製造順の)depends_on | AI | 不変。interface_contract に混ざる設計の内容は**件数の記録のみ**(試行で移さない) |
| 32 procurement | substitutable(方針) | 人 | 正本は裁定層(REQ・53 の replacement_policy)。32 は従属。試行では M-THUMB-008 の 1 件の食い違いの有無の確認のみ |
| 33 CP | 行の分け方・depth・fixture・oracle・test_vectors | AI | 行の粒度は AI が決める(行を約束ごとに割らない) |
| 33 CP | requirement_refs / invariant_refs | AI | 対象行に置く(行が検査する裁定層の ID)。ECO-086 の candidate 欄の使用 |
| 33 CP | tolerance・期待値 | AI(導出) | 裁定層の値から導出する。裁定層に値が無ければ導出不能として人へ戻し、仕様へ書き戻す |
| 33 CP | approver(depth G) | 人 | 人は検査の実行者として残る(知覚・golden)。行の中身の所有とは別 |
| 33 CP | when / on_fail(新・試行の欄名) | AI | 測る時点(受入・劣化イベント等)と、落ちたときの振り分け(製品修正 / 測定系復旧 / 人の承認)。区分は ECO-089 の outcome / measurement に対応させ、新しい語を作らない |
| テスト | trait `cp`(既存)+裁定層の ID の trait(新) | AI | 1 テストが検査する REQ / INV を trait で持つ |
| 表(cp_results) | CP 行ごとの表(既存)+**裁定層の ID ごとの表**(新) | AI | 人が受入で読むキーを、人が裁定した ID にする。届く検査が無い ID は「検査なし」と出す |

### 1.3 人の承認点と、AI の層への統制

- 人の承認点は 2 つ: **gate 1**= 裁定層の版の確定(「人へ戻す」行の裁定を含む)/ **gate 2**= 受入(裁定層の ID ごとの表+検査官の判定を読む)。M-BOM・CP の中身の個別承認は置かない。
- AI の層への統制(人の承認に頼らない): ①裁定層の ID ごとの表(届かない ID・測定不能が見える)②異系統の検査官による導出の意味の審査(R6)③人へ戻した判断と、戻さず AI が決めた判断の列挙(R2・後から「人が決めるべきだった」と判定されたら導出の欠陥として記録)。
- 機械で止めない(ViewPrism2 の裁定 A・ECO-143 のまま)— 表は承認者への入力。

### 1.4 既存の BOM への遡及

- 一括では直さない。次にその単位へ触れる変更で直す(playbook §4.4 の lazy 遡及と同じ)。試行は 2 単位に閉じる。

### 1.5 採らない

行を約束ごとに割る(trait とテストの対応 57/65 を壊す・行の粒度は AI の領分)/ 新しい台帳・新しい検査器(既存の欄・cp_results・ECO-090 の計数スクリプトだけ)/ playbook・テンプレの改訂(評価の後)/
標準 M-BOM・文脈境界(OBS-20261002-03 の着手条件未達)/ ViewTube への適用 / interface_contract の移し替え / E の acceptance_refs の撤去 / 効果量の推定。

## 2. 試行の手順(製品側 ECO= ViewPrism2 ECO-145〔仮〕)

1. 統括 AI が対象 2 単位の M の不変条件を 3 分類し、「人へ戻す」行を E 側の文案にする(gate 1 の材料)。
2. **人が裁定する(gate 1)**: 「人へ戻す」行を E の不変条件として採るか・文言・AI が決めてよいと返すか。裁定層の版を固定(bom_version・tag)。
3. 統括 AI が導出する: M の invariants の解消・manufacturing_decisions・CP 対象行の requirement_refs / invariant_refs・when / on_fail・テストの trait・表の拡張の仕様。
4. 工場が製造する: trait の付与と表の拡張(cp_results)。製品の挙動は変えない。
5. 異系統の検査官が導出の意味を審査する(R6)。リハーサル(R3)。計数の再実行(R1・R4)。
6. **人が受入する(gate 2)**: 裁定層の ID ごとの表と検査官の判定を読む。

## 3. 影響なし予測(起票段階・凍結)

本 ECO の diff= 台帳系(order・register・improvements.md・reports/eco-097-mbom-cp-redesign/)のみ。method/ の playbook・templates・schemas・tools・hooks・.github は diff 0。
製品側(ViewPrism2)の diff は製品側 ECO の影響分析で予測する。C16(収束 receipt あり)・C13・worklist 警告 0。

## 4. 受入条件(製造前に凍結・二部形・ECO-080)

- V1(条件): 事前登録が製品側の着手より前の commit にあること — 検査法: 両リポの commit。
- V2(条件): 「人へ戻す」行が人の裁定つきで裁定層に固定され、版が bom_version+tag で固定されていること — 検査法: ViewPrism2 の 30・register・tag。
- V3(条件): R1〜R7 が事前登録の読み方で記録されていること — 検査法: reports。
- V4(条件): 停止条件 S1〜S4 の発生の有無が記録されていること — 検査法: reports。
- V5(条件): 製品側 ECO が ViewPrism2 の受入(機械受入+独立レビュー+人の受入)を通過していること — 検査法: ViewPrism2 register。
- V6(条件): playbook・テンプレが本 ECO の窓で非改訂・self-conformance 全 PASS・CI success — 検査法: diff・CI。
- V7(条件): 製造者較正・較正 receipt(trigger ①)。
評価(playbook・テンプレへの反映)は本 ECO のクローズ条件ではなく、EXP-20261005-01 で回収する。

## /preflight receipt(起動経路: **自発** — 継続作業の開始時)

- 分類= continuation(ECO-089 → 090 → 094/095 の続き・user 2026-10-05 の指示)。根拠= 起点は既存の実測(ECO-090)と試行(ECO-094)に依存。
- 最小契約: baseline= BomDD `6810d2c`・ViewPrism2 `f622c3c`(両方 clean)= **confirmed** / current-work-state= ECO-090・094・095 verified・ECO-097 は次番(register 末尾 096)= **confirmed** /
  unresolved-items= OBS-20261002-01(2/3)・OBS-20261003-03(1/3)・EXP-20261001-01(open)・EXP-20261002-01(回収中)= **confirmed**(improvements.md 実読)/
  handoff-state= ECO-090 order・ECO-094 order と reports から再構成= **confirmed** / acceptance-target= **missing**(再設計の完了条件は未定義だった)→ 本 order §4 と事前登録で定義。
- discovered(契約外): 「文書より先に製品で試す」の順序(ECO-090 §1)は今回の指示で覆されていない= 本 ECO はテンプレに触れない。ViewPrism2 の次番は 145(register 実読)。
- 開始判定: **PROCEED_WITH_LIMITS**(縮小= 起票と事前登録まで。製品側の着手は収束の扱いの決定の後)・override 0。

## /converge receipt(起動経路: 自発 — 再設計〔欄の所有・人へ戻す条件・人が読む表のキー・統制〕)

- **判定: 未収束**(round 軌跡: 6→4→0・上限 3 周に到達・2 周連続ゼロに至らず)。開いた論点は 0 件。扱い(打ち切り採用 / 延長 / 差し戻し)は人が決める — 決まるまで製品側に着手しない。
- DoD: ✔ 設計の内容の正本が 1 箇所(裁定層)/ ✔ 各欄に所有者が 1 つ(§1.2)/ ✔ 人へ戻す条件が列挙され、書き戻し先が裁定層 / ✔ 既存 BOM の一括遡及を要しない /
  ✔ 新しい台帳・検査器を増やさない / ✔ 指標と読み方を製品側の着手前に固定し、前後比較は ECO-090 と同じ数え方 / ✔ 停止条件を事前に列挙 / ✔ AI の層への統制が人の個別承認に依存しない。
- round 1(新規 6 件): ①「M は参照だけ」では足りない — 実データに製造手段の行がある(M-DB-007)→ 3 分類+manufacturing_decisions ②ViewPrism2 の CP 行は裁定層の ID を 1 つも持たない(0/65)→ 対象行に refs を置く
  ③OBS-20261003-03 の対処を「行を割る」にすると trait 対応を壊す → 人が読む表のキーを裁定層の ID にし、行の粒度は AI に任せる ④調達の substitutable は方針= 人の裁定(ECO-144 の実例)→ 正本は裁定層
  ⑤意味の審査の担当 — ECO-094 では人。今回の決めでは CP は AI の場所 → 異系統の検査官へ(§1.3 ②・得失は下)⑥ViewTube は逆の形(M 114 / E 48)→ 対象外と明記・遡及は lazy。
- round 2(新規 4 件): ⑦M の interface_contract にも設計の内容が混ざる(キャッシュファイル名の `-v2` 規則= REQ-105 の約束)→ 件数の記録だけにして範囲を切る ⑧E の不変条件の行の多くは ID が無い(ViewPrism2 240/288)→
  M は ebom_refs で品目ごと引き継げば行の ID は要らない。ID が要るのは検査(trait)から指す行だけ → 必要な行にだけ付ける ⑨許容差・期待値が裁定層に無い場合の扱い → 導出不能として人へ戻し仕様へ書き戻す
  ⑩E の acceptance_refs(E → CP)は向きが逆 → 試行では触らず記録のみ(撤去は validate_bom の参照検査に影響しうる)。round 3: 0 件。
- 検証した主張(実測): ViewPrism2 / ViewTube の行数と ID の数(scratchpad の計数・事前登録の基準線に転記)/ 対象 2 単位の M・E の行(実読)/ CP 行のキー(ViewPrism2 に requirement_refs・verifies なし)/
  テストの trait の種類(cp 132・oracle 47 ほか)/ cp_results の区分の定義(bomdd/cp_results.py 冒頭)/ ECO-090 の順序の既決(order §1)。
- 疑い(未検証・効果の予測): 裁定層の ID ごとの表で Skip が見えるようになる(R3 で測る)/ 検査官の審査が人の審査の代わりになる(R6 は件数の記録まで・同等性は測らない)。
- 敵対自問: 「AI が検査を導出し、AI が審査するなら、人は弱い検査に気づけない」— 残る。人に見えるのは届かない ID・測定不能・検査官の否まで。届いているが中身が弱い検査は検査官の検出力に依存する(playbook §9: 自己査定は製造者の前提誤りに盲目 → 異系統を条件にした)。
  「行を割らないなら OBS-20261003-03 は直らないのでは」— 行の区分は直らない。人が読むキーを変えることで、約束単位の測定不能を見せる(R3 が不成立なら行を割る案へ戻る)。
  「E に ID を付けて回るのは一括遡及では」— 検査から指す行だけ・対象 2 単位だけ。
- 未収束事項: なし(上限到達による形式上の未収束)。

## 5. 起票時の状態

- 起票 commit の後、収束の扱い(と §1.3 ②の得失)を人に問う。採用なら ViewPrism2 ECO-145 を起票し、gate 1 の材料(「人へ戻す」行の文案)を提示する。

## 6. 扱いの決定と製品側の着手(2026-10-05)

- **決定(user 2026-10-05)**: 「A」= 未収束のまま打ち切り採用(全部)・意味の審査は異系統の検査官(§1.3 ②)。§1 の設計を凍結する。
- **着手前の訂正(統括 AI・事前登録「変更の履歴」)**: 起票時に「人へ戻す」と仮に分類した 2 行は、仕様(20-spec.md L346・L352 / REQ-085・REQ-106)に既にあった。訂正後の仮の分類= 参照化 5・製造手段 1・人へ戻す 0。
  起票時の handoff で「最初にお戻しする内容になる」と述べたのは誤り(E-BOM だけを読んで裁定層に無いと断定した— converge 失敗型 ②「検索の打ち切り」)。
  帰結: 製品側 gate 1 で人が決める E 側の文案は無い。裁定層は不変で、bom_version と tag は動かさない。V2 は「人へ戻す行 0・該当なし」として記録する。
- **設計の補正(凍結後の発見・記録のみ)**: 裁定層の列挙(§1.1)に K-BOM(31)が抜けていた。K-BOM の項目は人が裁定する(playbook §4.3)ので裁定層に含める。M の「製造手段」の行は、K-BOM にある決定の参照になることがある(M-DB-007 の接続戦略= K-SQLITE・ADR-0003)。
- 製品側 ECO= ViewPrism2 **ECO-145**(起票は本 commit の後)。導出記録・リハーサル・検査官の報告は本リポ reports/eco-097-mbom-cp-redesign/ に置く。
