# Change Order — ECO-089(測定不能の扱いの契約化 — 検査の判定を「違反」と「測れなかった」に分ける・ref-v0.12〔filed〕)

> 裁定: user 2026-10-01 DECIDE「A'」(提案「受入条件に RED と MEASUREMENT_FAILURE の分離を入れる」を取り込んで起票・前回の A は A' に置換)。
> 本 ECO は**起票のみ**。設計の収束が上限 3 周で未収束(5→2→1)のため、製造(スキーマ本体の改訂)は裁定待ち — 未収束の設計を製造へ進めない(/converge 手順 6)。
> 目的: M-BOM / Control Plan の再設計(後続)の前に、検査の判定語彙を整える。**不良を見つけたのか、測定器が測れなかったのかを混ぜない** —
> 混ぜたままだと、再設計の前後比較で「不良が増えた」のか「測れなくなった」のかを後から区別できない。
> 本 ECO は lint 強化ではなく、**測定不能の扱いの契約化**として扱う(user 提案の整理)。契約の正本は ref-edges・実装は BomDD-Plm の別 ECO。

## 担当設備(equipment)

- 起票: requested/resolved `claude-sonnet-5-5`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-005(製造者較正のみで足りるかは製造裁定 §3b)
- 独立検査: 本 ECO(規則文言と契約)は製造裁定で決める。検出の挙動を変える実装は BomDD-Plm 側の別 ECO で、そちらに異系統の独立検査を置く想定。

## 0. 実測(起票根拠・2026-10-01)

証拠の所在= [bomdd/reports/eco-089-measurability/](reports/eco-089-measurability/)(スクリプト 2 本・結果 2 本)。

### 0.1 較正測定: 現行の検査に「測れなかった」を当てた([arms-pre.md](reports/eco-089-measurability/arms-pre.md))

土台は BomDD-Plm `d02052b`(clean)の 2 構成: plm-self(自己ホストの `bomdd/`・他ファイルからの参照が多い)と minimal(固定オラクルの最小リポ+合格行 1 本)。
変異前は 2 構成とも両ゲート exit 0。各 arm は 1 つだけ壊す。期待は実装の前にスクリプトへ固定し、現行出力は突き合わせるだけ。

- **「黙って緑」は起きにくいが、起きる構成が実在した**: 期待= MEASUREMENT_FAILURE の arm で、現行が exit 0(無音で緑)になったのは **1 件だけ** —
  minimal から「他ファイルが M ID を参照しない」変種を作り、32-mbom の `manufacturing_units` を改名した arm(A9)の、コミット時ゲート(always)。
  同じ arm は受入ゲートでは R-012(製造可能な品目をどの M unit も実現していない)が error を出して止まる。キー改名・構文エラー・空文書の 5 arm(A2〜A6)は、2 構成 × 2 ゲートの全てで無音ではなかった。
- **「違反と混在」が主な失敗**: 上記の全 arm(キー改名・構文エラー・空文書 × 32-mbom / 33-control-plan)は exit 1 で止まるが、原因は**違反と同じ `error`** で出る。
  1 件の改名が plm-self では R-003(参照が解決できない)の error 8 件〜158 件に見える。minimal の改名は「既知の違反(存在しない ID への参照)」と**同じ規則・同じ件数**(error R-003 +1)で、
  出力から「不良を見つけた」と「測れなかった」を区別できない。
- 構文エラーは X-PARSE-001 が error で報告される(Plm 仕様 §2.2 が severity error として凍結)。空文書は X-TYPE-001 の warn に留まり、連鎖の R-003 error が止める。
- 測定の限界: 土台 2 構成・変異 8 種(minimal のみ変種 2 本を追加)・各 1 回。変異の分布は私の設計で、実在の事故の分布ではない。

### 0.2 実在リポの Control Plan(測定の副産物)

- 実リポ 7 本のうち 2 本(BomDD-UnitConv-Sample・BomDD-LibraryLending-Sample)の `33-control-plan.yaml` は **YAML として解析できない**(UnitConv は構文エラー 6 件を X-PARSE-001 が報告)。
- TimetableAdv の 33 は、節名をキーにした節(`dayplan_host_execution` など)と `characteristics` のリストが併存する。bomdd-lint の選択子(`control_plan.characteristics` のリスト)は 471 件を拾うが、
  字面で `id: CP-` と書かれた特性は 25 件。**母集団の定義が測り方で食い違う**(471 件の ID の大半は `CP-` 接頭辞でないと読めるが、中身は確かめていない)。
- 以上は「測定できない・測り方で食い違う」が机上でなく実在することを示す。ただし 1 時点・各リポ 1 回で、TimetableAdv の作業木は dirty(2140 行)。

### 0.3 基準線の空白: Control Plan の特性 ID がコードへ字面で届く率([cp-reach.md](reports/eco-089-measurability/cp-reach.md))

字面一致のみ(届く≠検査されている・届かない≠検査されていない)。届く率: Plm 18/21・UnitConv 0/8(33 解析不可)・LibraryLending 6/12(33 解析不可)・ViewTube 12/41・
ViewPrism2 57/65・Transfer03 0/10(git 追跡なし・走査 11 ファイル)・TimetableAdv 25/25(母集団不一致のため率として読まない)。
これは ECO-086 の INV 到達率(検査計画の行へ 0〜3 割)と同じ型の下限の目安で、**実際に検査されているか**は測っていない(未測定)。

### 0.4 訂正(正直記載 — 本 ECO の議論過程で私が述べた 2 点)

1. 「構造が変わると、コミット時の hook は通す(fail-open)ので壊れ方が静か」と述べたが、**hook が通すのは終了コード 2(検査器の実行障害)だけ**。
   測定不能が RED と同じ error で出る場合は exit 1 で commit を止める(arms 実測)。静かなのは A9 の 1 構成に限られる。
2. 「黙って緑になる」を最悪の壊れ方と述べたが、実測では起きにくい(上記)。**主な問題は無音ではなく混在**で、本 ECO の動機はこちらに置き換える。

### 0.5 未観測

- 不良サンプルが実在の事故の分布を代表するか。M ID が他から参照されない構成が実在リポでどれだけあるか。
- Control Plan が実際に検査へ結ばれているか(字面でなく実行)。受入ゲート(R-050)を製品の判定経路で実行している製品リポは見つかっていない(ECO-085 の既記録)。

## 1. 変更要求(候補 — 製造裁定で凍結)

契約の置き場= `method/schemas/draft/ref-edges.draft.yaml`(`edges_version` を ref-v0.12・版ヘッダに経緯・新節「測定可能性契約」・対象 4 規則に宣言欄)。実装= BomDD-Plm の別 ECO。

1. **判定の 4 状態**(検査対象ごと): PASS(対象が 1 件以上・測定が完了・違反なし)/ RED(測定が完了し違反あり)/ MEASUREMENT_FAILURE(測定が完了していない)/
   NOT_APPLICABLE(対象 0 件が上流の宣言と整合し、適用外と明示されている)。「PASS」と書いてよいのは、測定が完了し MEASUREMENT_FAILURE と RED が 0 のときだけ。
2. **MEASUREMENT_FAILURE の原因は閉語彙**: unreadable-input(構文エラー・不正 UTF-8)/ selector-miss(読めたが期待するキーが無い)/
   empty-required-source(必須成果物が空・不在)/ tool-failure(検査器自身の実行障害)。
3. **対象 0 件の判定**: 規則は「その規則の対象が非空であるべき根拠(上流の宣言)」を 1 つ宣言する。上流が 1 件以上なのに対象が 0 件なら MEASUREMENT_FAILURE、
   上流も 0 件なら NOT_APPLICABLE(適用外を明示)。宣言の無い規則は「宣言なし」と明示する(沈黙させない)。本 ECO の宣言対象は M-BOM / Control Plan / As-Built を読む **R-011・R-012・R-014・R-050** のみ。
   上流の宣言の実例= 30-ebom の `lifecycle_state: manufacturing-ready`(R-012 が既に使っている)。製造前のリポ(上流も 0)は適用外のまま — ECO-085 の裁定(製造前は製造記録が無いのが正常)と整合する。
4. **RED と MEASUREMENT_FAILURE の境界**: 必須の定義サイトが読めない・空・キー空振りは MEASUREMENT_FAILURE(RED にしない)。RED は「読めた定義サイトの内容が期待と矛盾する」場合だけ。
   R-050 規則 (c)(ECO-085: 製造記録が読めない=測定不能)と同じ向き。
5. **連鎖所見の帰属**: 測定不能の結果として生じる派生所見(定義が見えなくなったことによる参照不解決など)は、原因の MEASUREMENT_FAILURE 1 件へ従属させ、違反として数えない
   (実測: 改名 1 件が R-003 の error 158 件に見えた)。**疑い(未検証)**: 検査器が「改名による全件不解決」と「1 件だけの本物の不解決」を区別できるか — arms(A2〜A6 対 A7)で測る。機構は実装 ECO。
6. **出力と終了コード**: RED と MEASUREMENT_FAILURE を機械可読に区別して出す(所見ごとの区分+実行全体の件数)。MEASUREMENT_FAILURE は exit 0 にならない。
   終了コード 0/1/2 の意味は変えない案を第一候補とする(Plm 仕様 INV-006 が凍結・hook が exit 2 を通す設計のため、規則単位の測定不能に 2 を割り当てない)。値の設計は実装 ECO(Plm 仕様の改訂)で裁定する。

### 1.1 レバーの比較(選択肢の落とし防止 — 失敗型 ⑦)

| 案 | 内容 | 捕まえる arm(実測) | 捕まえない arm | 戻せるか |
|---|---|---|---|---|
| C-a | 規則ごとの上流宣言(1・3)で対象 0 件を判定 | A9(被参照の無い構成の改名・コミット時) | 連鎖の大量 error は減らさない | 可 |
| C-b | ファミリー単位の「参照あり・定義 0」検出で連鎖を 1 件の測定不能へまとめる(5) | A2〜A6(連鎖 error 8〜158 件) | A9(参照 0・定義 0 なので検出できない) | 可 |
| C-c | C-a と C-b の両方 | 上記の和 | — | 可(部分採用へ縮小できる) |

両者は代替でなく補完関係(arms の実測による)。第一候補= C-c。**効果の予測(連鎖の帰属が誤判定しないこと)は疑いのまま** — 実装後の arms で測る。

### 1.2 設計上の選択と理由

| 選択 | 採った案 | 退けた案と理由 |
|---|---|---|
| 終了コード | 0/1/2 を維持し区分を属性で出す | exit 3 新設 — Plm 仕様 INV-006(0/1/2 契約)と既存 hook の判定を変える / exit 2 流用 — hook が通す設計で、規則単位の測定不能が素通りする |
| X-PARSE-001 の severity | 本 ECO では変えない | 変更 — Plm 仕様 §2.2 が severity error として凍結。区分の属性で表す |
| 対象 0 件 | 上流の宣言と突き合わせる | 一律に測定不能 — 製造前のリポが誤報になる(ECO-085 の裁定)/ 一律に適用外(現状)— A9 が無音になる |
| 契約の置き場 | ref-edges(規則カタログ) | playbook — 検査器の実装契約でなく規則の意味の正本は ref-edges(ECO-085 と同じ) |
| 宣言の範囲 | M-BOM / Control Plan / As-Built を読む 4 規則 | 全 19 規則 — 他の規則の上流宣言は根拠が未測定。後続 ECO |

**採らない**: Plm の実装・Plm 仕様の改訂 / X-* の閉集合(8 種)の変更 / hook・CI の方針(各製品の判断)/ 受入ゲートの製品判定経路への結線 /
id-grammar・派生 JSON Schema・templates・tools の改訂 / 実リポの記録の是正 / **M-BOM / Control Plan の再設計**(本 ECO の後続・本 ECO は比較の前提を整えるまで)。

## 2. 影響なし予測(製造前・起票時点 — 製造裁定で凍結)

- 本リポの diff= `method/schemas/draft/ref-edges.draft.yaml`(版ヘッダ+新節+対象 4 規則の宣言欄)+台帳系(order・register・improvements.md・reports)のみ。
  id-grammar・派生 JSON Schema・templates・tools・hooks・.github は diff 0。C10(派生同期検査)の判定不変(lint_rules は派生の対象外 — ECO-085 と同じ構造・製造時に実測で確認)。
- 規則文言だけでは挙動は変わらない(ECO-085 と同型 — V4 で実測)。
- 実装後の実リポへの影響は**未予測**: BomDD-Plm 側 ECO の影響分析で実リポ全数を測る(本 ECO は予測の記録まで)。ただし 33 が解析できない 2 リポは、区分が分かれた後も「測定不能」で出る。

## 3. 受入条件(製造前に凍結・二部形)

- V1(条件): スキーマ本体が §1 の 6 項(4 状態・原因の閉語彙・対象 0 件の判定・境界・連鎖の帰属・出力)と対象 4 規則(R-011・R-012・R-014・R-050)の上流宣言を持ち、`edges_version` が ref-v0.12 であること — 検査法: YAML 解析して該当キーを読む。
- V2(条件・較正): 期待= MEASUREMENT_FAILURE の arm が、是正前の個体で全て期待と不一致(無音または違反と混在)と測定されており、期待が実装の前に固定されていること — 検査法: `measure-arms.py` の ARMS と出力 arms-pre.md(起票時点で測定済み)。
- V3(条件・基準線): Control Plan→コード到達の字面基準線が、母集団の不一致・解析不可・走査 0 を 0% に丸めず状態列に残して記録されていること — 検査法: cp-reach.md(起票時点で測定済み)。
- V4(条件): 改訂後のスキーマを直指定した現行実装の所見出力が同梱スキーマの出力と同一であること(文言だけでは挙動が変わらない)— 検査法: clean 検体と所見が出る検体の出力 diff。
- V5(条件・実装後の陽性・陰性対照): BomDD-Plm の実装個体で、期待= MEASUREMENT_FAILURE の全 arm が PASS とも RED とも区別でき exit 0 にならず、期待= RED の arm が RED、期待= PASS の arm が PASS(A8 は always で PASS・acceptance で RED)であること — 検査法: `measure-arms.py` へ期待比較モード(--expect post)を足して実行(製造時)。
- V6(条件・連鎖の帰属): 実装個体で、A3(Control Plan のキー改名)が違反として数える error 件数が、原因の測定不能 1 件分を超えないこと — 検査法: V5 と同じ実行の error 件数。
- V7(条件): self-conformance 全 PASS(exit 0 を観測してから commit)・CI success・diff 窓が allowed_paths のみであること。
- V8(条件): 較正 receipt(trigger ①③)があること。独立検査の有無は製造裁定による。
- V5・V6 は BomDD-Plm の実装個体で測る。それまで本 ECO は `implemented` に留め、`verified` へ上げない。

## 3b. 製造裁定の候補(別 DECIDE で提示)

1. 収束の扱い: 打ち切り採用 / 延長 / 差し戻し(収束 receipt の裁定質問)。
2. レバー: C-a / C-b / C-c(§1.1)。
3. 実装側(BomDD-Plm 別 ECO)の起票時期と配員: 本 ECO の規則文言の後 / 並行・製造者較正のみ / 異系統の独立検査を併用。

## /preflight receipt(起動経路: **自発** — 既裁定の適用の開始時)

- 分類= 新規の設計(改善起点・user DECIDE「A'」)。検査器の既知の穴の実測(arms)に基づく。

| 区分 | 前提 | 判定 | 正本座標 |
|---|---|---|---|
| 最小契約 | failing-behavior(観測) | confirmed | reports/eco-089-measurability/arms-pre.md |
| 最小契約 | target-specimen(対象個体) | confirmed | BomDD a3aa327(起票前・作業木に追跡対象の変更なし)・BomDD-Plm d02052b(clean) |
| 最小契約 | expected-behavior(期待の正本) | confirmed | method/control-plan.md「各検査は対象集合が空の場合の意味を宣言する」・AGENTS.md 規律 4・6・ECO-085 規則 (c)(d) |
| 最小契約 | acceptance-target | confirmed | 本 order §3 |
| discovered | 次番 089 が未使用 | confirmed | register に id 0 件 |
| discovered | 同じファイルを窓に持つ進行中の ECO がない | confirmed | 進行中(implemented)は ECO-079 のみ・allowed_paths に schemas なし |
| discovered | 実装先(BomDD-Plm)の凍結済み仕様との整合 | **contradicted → 是正** | 初案の「終了コード新設」は INV-006(0/1/2)と衝突 → §1.2 で取り下げ |
| discovered | hook の挙動の理解 | **contradicted → 是正** | 「測定不能は hook が通す」は誤り・通すのは exit 2 だけ(§0.4) |
| discovered | TimetableAdv の作業木が安定 | unknown | dirty(2140 行)— 基準線の 1 行は参考値(§0.2) |

- 開始判定: **PROCEED_WITH_LIMITS** — 縮小範囲= 起票と測定まで。製造(スキーマ本体の改訂)は収束の裁定後。override 0。

## 収束 receipt(/converge — 起動経路: 自発)

- **判定: 未収束**(round 軌跡: 5→2→1・上限 3 周に到達・2 周連続ゼロに至らず)。裁定質問= 打ち切り採用 / 延長 / 差し戻し。製造・正典化は裁定まで進めない。
- 周回と新規指摘:
  - round 1(5 件): ①初案の「終了コード新設」が実装先の凍結済み仕様(INV-006・X-PARSE-001 の severity・X-* の閉集合)と衝突 ②hook の挙動の読み違い(測定不能は exit 1 で止まる・通すのは exit 2 のみ)
    ③RED と測定不能の境界が未定義(必須成果物が空・不在はどちらか)④連鎖所見の帰属が未定義(改名 1 件が R-003 158 件に見える)⑤受入ゲートの実行が製品の判定経路に結線されていない(範囲外と宣言)。
  - round 2(2 件): ⑥「他ファイルが参照しない構成」で無音になるかが未測定 → arms A1b・A9 を足して実測(結果= コミット時ゲートで無音 1 件)⑦選択肢の欠落(失敗型 ⑦): 規則ごとの上流宣言だけが案でなく、ファミリー単位の検出という別のレバーがある。
  - round 3(1 件): ⑧ 2 つのレバーは代替でなく補完 — ファミリー単位の検出は A9 を捕まえず(参照 0・定義 0)、上流宣言は連鎖の大量 error を減らさない(arms の実測)。第一候補を C-c(両方)へ改めた。
- DoD:
  - ✘ 各規則に必ず起きるイベントのアンカーがある — 契約を適用する検査が製品の判定経路で実行される保証は無い(結線は範囲外と宣言・ECO-085 と同じ。§0.5)。
  - ✔ 各規則に実在確認済みの実装先がある — 契約= ref-edges.draft.yaml・実装= BomDD-Plm の `computeExit`(cli/src/main.ts)・`parse.ts`・`evaluate.ts`(実読)。
  - ✔ 各検査にその規則固有の理由で赤くなる検体の方針がある — arms A2〜A9(2 土台・原因別に壊す。連鎖で覆われないよう A9 を足した)。
  - ✔ 全状態に所有者がある — 契約= ref-edges(本リポ)・実装と Plm 仕様の改訂= Plm 側 ECO・hook の方針= 各製品。
  - ✔ 正本が一意 — 4 状態の意味は ref-edges に置き、Plm 仕様は実装の写像だけを持つ(Plm 仕様 §2.2・§2.6・§2.10 を実読した上で、凍結行は本 ECO で変えないと明記)。
  - ✔ 凍結行・既裁定の実文と突合済み — Plm 仕様 §2.2(X-PARSE-001 severity error)・§2.6(X-* 閉集合・全規則を毎回評価し gate を付ける)・§2.10/INV-006(exit 0/1/2)、ECO-085 規則 (c)(d)・§1.2。
  - ✔ 影響が列挙されている — 本リポの diff(§2)。実装後の実リポへの影響は**未予測**と宣言(§2)— ✔ は本リポの範囲に限る。
- 検証した主張(要点):
  - 「改名・構文エラー・空文書は違反と同じ error で出る」= 実測(arms-pre.md・2 土台)。「無音で緑は A9 のコミット時ゲートのみ」= 実測(minimal・1 arm)。
  - 「hook が通すのは exit 2 のみ」= 実読(BomDD-Plm bomdd/hooks/pre-commit・ViewPrism2 bomdd/hooks/pre-commit)。「INV-006 は 0/1/2 を凍結」= 実読(BomDD-Plm bomdd/20-spec.md)。
  - 「改名 1 件と本物の不解決 1 件が同じ所見(error R-003 +1)」= 実測(minimal の A2 対 A7)。「C-b は A9 を捕まえない」= 実測の読み(参照 0・定義 0)で、実装は無いので**検出できないことの裏取りは構造上の推論**。
  - 「C-c の連鎖の帰属が誤判定しない」= **疑い(未検証)**— 実装が無いため測れない。受入 V5・V6 へ回す。
- 未収束事項: ①周回ごとに指摘が 1 件以上残っており、次の周で 0 になる根拠がない ②連鎖の帰属(5)が実装可能か(改名と本物の不解決の区別)が未検証 ③不良サンプルの分布が実在の事故を代表するか未測定
  ④対象 4 規則の「上流の宣言」の妥当性(R-011・R-014 の上流を何とするか)は R-012・R-050 ほど確かめていない ⑤ TimetableAdv の作業木が dirty のため基準線の 1 行が参考値。

## 4. 製造・クローズ

起票時点では未着手。製造裁定(§3b)の後に、本節へ製造の実測・V 結果・クローズ(較正 receipt)を追記する。
