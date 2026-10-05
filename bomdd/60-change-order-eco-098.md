# Change Order — ECO-098(ECO-097 試行の反映 — 裁定層と導出層の欄の所有・M-BOM の 3 分類・検査行と裁定層の結線・人が読む表を playbook と 32 / 33 テンプレへ candidate として置く〔文書のみ〕)

> 裁定: user 2026-10-05 DECIDE「A」(ECO-097 クローズ後の反映の判断)= いま candidate として文書に書く。効果は主張しない(試行 1 回・2 製造単位・1 製品)。
> 出典: [ECO-097](60-change-order-eco-097.md) §7・§8 / EXP-20261005-01(回収済み)/ OBS-20261005-01・02 / ViewPrism2 ECO-145(applied 883cb08)。

## 担当設備(equipment)

- 起票・設計・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-001
- 独立検査: EQ-002(Codex CLI / gpt-5.6-sol・異系統)— method 本文の改訂のため受ける。

## 0. 根拠(起票・2026-10-05)

- ECO-097 の回収: (a) 対象 2 単位の M-BOM の invariants 6 行= 参照化 5・製造手段 1・人へ戻す 0(M は裁定層の言い換えを持っていた)(b) 人へ戻した判断 1 件(導出不能)・機械的派生 0
  (c) 裁定層の ID ごとの表で 10/10 の ID が Skip → 測定不能・赤 → 違反(行は割らない)。統制の実測= 異系統の検査官が対応づけの誤り 1・漏れ 1、別文脈のレビューが表の計器の blocking 2 を検出。
- 現行の文書の状態(実読): playbook §4.5 は M-BOM を「製造単位ごとに interface_contract / invariants / acceptance_refs」と書き、誰が所有するか・E-BOM との分担を述べない。32 テンプレの `invariants` は ECO-086 で「仕様 §3 の ID を先頭に書く」まで。
  33 テンプレは `requirement_refs`・`invariant_refs`(ECO-086)を持つが、測る時点・落ちたときの振り分けの欄は無い(ECO-090 M3: 主 2 本で処置の欄 0)。§9 の役割表は「設計者(ユーザー+設計 AI)」を 1 行にまとめ、層の所有を分けない。
- user の決め(2026-10-05): E-BOM は人が裁定する場所・M-BOM / Control Plan はその裁定に基づいて AI が判断する場所。責任分担は決めの問題。

## 1. 変更要求(製造対象・凍結)

1. **playbook §4.5** に 1 項「裁定層と導出層(candidate)」: 層の所有(裁定層= 10・20・30・31 / 導出層= 32・33・34)・導出層は人の個別承認の対象にしない・導出層は裁定層の内容を自分の言葉で持たない(M の invariants の 3 分類)・
   「裁定層に無い」の判定は裁定層の全部を読む・人へ戻す 3 種・試行の実測・lazy 遡及・未測定の列挙。
2. **playbook §4.4** に 1 項「検査行と裁定層の結線・人が読む表(candidate)」: CP 行の `requirement_refs` / `invariant_refs`・`when`・`on_fail`・人が受入で読む表のキーを裁定層の ID にする・作り方の規律 3 点
   (ID の集合を導出側の欄だけから取らない / 表は trait の文字列一致で、意味の審査と対 / 表は判定ではない)・限界。
3. **playbook §9** の配置原則に 1 項「層の所有(candidate)」: 導出層への統制を人の個別承認でなく、ID ごとの表・異系統審査・判断の列挙に置く。
4. **templates/32-mbom.yaml**: `invariants` のコメントに 3 分類(candidate)・`manufacturing_decisions: []`(candidate 欄)。
5. **templates/33-control-plan.yaml**: 先頭の例の行に `when`・`on_fail`(candidate 欄)・checklist に 1 項(refs は行のテストが実際に検査する ID・表の ID の集合)。

**採らない**: 実証済みへの格上げ(candidate のまま)/ 効果の主張 / 既存製品への遡及の要求 / schemas・ツール・検査器の変更(新しい機械検査を足さない)/ phase3-design などプロンプトの改訂(playbook を参照する側・次の実使用で必要が出たら)/
`interface_contract`・`display_contract` の「転記」指示の変更と E-BOM の `acceptance_refs` の向きの変更(試行で未測定)/ ECO-086 の candidate(M の行の先頭に ID)の撤回(両立する形で書く)/ cp_results 相当のツールの配布(製品側の実装 1 例のみ)。

## 2. 影響なし予測(製造前・凍結)

diff= playbook(§4.4 に 1 項・§4.5 に 1 項・§9 に 1 項)・templates/32(コメント 2 行+欄 2 行)・templates/33(欄 4 行+checklist 2 行)+台帳系+独立検査の報告のみ。tools・hooks・.github・schemas・contracts・prompts diff 0。
C1(YAML 厳格パース)は新しい欄を含めて PASS のまま・C7 / C13 / C14 / C15 判定不変。配布テンプレは次回配布時に波及・既存製品は不変。

## 3. 受入条件(製造前に凍結・二部形・ECO-080)

- V1(条件): playbook §4.4・§4.5・§9 に各 1 項があり、いずれも candidate と試行の規模(N=1・2 製造単位・1 製品)を明示し、未測定・限界を併記していること — 検査法: grep(`ECO-098`)と実読。
- V2(条件): 32 テンプレに 3 分類のコメントと `manufacturing_decisions`、33 テンプレに `when`・`on_fail` と checklist の 1 項があり、両テンプレが厳格 YAML パースを通ること — 検査法: grep・C1。
- V3(条件): 文書の記述が ECO-097 の記録(§7・§8・reports)の値と一致し、記録に無い主張(効果・一般化・同等性)を含まないこと — 検査法: 独立検査(異系統)。
- V4(条件): ECO-086 の candidate(M の行の先頭に ID・CP の invariant_refs)と矛盾しないこと — 検査法: 実読・独立検査。
- V5(条件): diff が allowed_paths のみ・self-conformance 全 PASS(exit 0 観測後に commit)・CI success であること。
- V6(条件): 異系統の独立検査が ACCEPT であること(境界探索)。
- V7(条件): 較正 receipt(trigger ①)があること。

## /preflight receipt(起動経路: **自発** — 既裁定の適用の開始時)

- 分類= 既裁定の適用(user 2026-10-05「A」)。baseline `f99c7c4`= **confirmed**(HEAD・clean・CI success)/ 次番 098= **confirmed** / 対象箇所(playbook §4.4 L137〜・§4.5 L334〜336・§9 L804〜・32 L35〜43・33 L28〜32・L100〜105)= **confirmed**(実読)/
  同一ファイルへの進行中 ECO= **confirmed**(なし)/ 反映の入力(ECO-097 §7・§8・improvements 2026-10-05 節)= **confirmed**。
- 開始判定: **PROCEED**・override 0。

## /converge receipt(起動経路: 自発 — 反映の置き場と文言の設計)

- **判定: 収束**(round 軌跡: 3→0→0)。
- DoD: ✔ candidate 止まりで効果を主張しない / ✔ 置き場は既存の節・欄の隣(新しい節・台帳・検査器を作らない)/ ✔ 製品で実際に使った欄名と同じ(`manufacturing_decisions`・`when`・`on_fail`・`requirement_refs`・`invariant_refs`)/
  ✔ 試行の値は ECO-097 の記録と一致 / ✔ 未測定と限界を本文に併記 / ✔ 既存の candidate(ECO-086)と両立 / ✔ 既存製品へ遡及を求めない。
- round 1(新規 3 件): ①32 テンプレの現行コメント「各行は仕様 §3 の ID を先頭に書く(ECO-086)」と「裁定層に同じ内容がある行は書かない」が衝突する → 「ID だけの行は可」として両立(ECO-086 の目的= 検査行から辿れること は ID だけで足りる)
  ②32 テンプレの `display_contract`「30 から転記」と `interface_contract` も同じ問題(裁定層の写し)を持つが、試行で測っていない → 文書では変えず「未測定」に列挙 ③`on_fail` の区分を参照する節として §8.4 を引こうとしたが、§8.4 は個体ラベルの節で測定不能の区分の正本ではない(実読)→ ECO-089 の契約を名指す形に修正。
  round 2: 0 件(本文と ECO-097 §7・§8 の値の突合: 6 行= 5 / 1 / 0・10/10・誤り 1・漏れ 1・blocking 2 — 一致)。round 3: 0 件(敵対自問)。
- 検証した主張: 現行 §4.5・§9・32・33 の文面(実読)/ ECO-097 の回収値(order §7・§8)/ ViewPrism2 で使った欄名(32・33 の実ファイル・fix 491d2c1)/ テンプレの厳格パース(実行)。
- 敵対自問: 「N=1 で本文に 3 項は多いのでは」— 3 項は同じ決めの 3 つの置き場(M-BOM の節・検査の節・役割の節)で、どれか 1 つだけでは読み手が他の節で旧い読み方をする。各項に candidate と N=1 を書く。
  「『導出層は人の個別承認の対象にしない』は G3 などの既存ゲートと衝突しないか」— G3 は fresh AI への自己完結性のドライランで人の承認ではない。Control Plan の depth G の承認者は検査の実行者で、行の中身の承認ではない(本文は「人の承認点= 裁定層の版の確定と受入」と書く)。
  「人が M-BOM / CP を読んで直したい場合を禁じるのか」— 禁じない。個別承認を**要件にしない**だけで、読むこと・指摘することは妨げない(本文は「対象にしない」— 検査官が指摘すれば直す経路と同じ)。
- 未収束事項: なし。

## 4. 製造(2026-10-05・製造者 EQ-001)

- 製造物(3 ファイル・追加のみ 27 行): playbook §4.4 の 1 項(検査行と裁定層の結線・人が読む表・探索プローブの項の直前)・§4.5 の 1 項(裁定層と導出層・Routing の項の直後)・§9 の 1 項(層の所有・配置原則の先頭)/
  templates/32(`invariants` のコメント 2 行・`manufacturing_decisions: []` とコメント)/ templates/33(先頭の例の行に `when`・`on_fail`・checklist 2 行)。
- 起票 commit の後に製造した(文案は起票前に作り、起票 commit の作業木からは外して、起票後に適用)。

## 5. 受入の実測(2026-10-05・製造者)

- **V1**= PASS(観測: grep `ECO-098` → playbook の 3 項。各項に「candidate・ECO-097 試行 N=1」と、未測定 / 限界の句がある— §4.4「限界: …」・§4.5「**未測定**: …」・§9「同等かは未測定」)。
- **V2**= PASS(観測: 32 に 3 分類のコメントと `manufacturing_decisions: []`・33 に `when: acceptance`・`on_fail: {red, unmeasurable}`・checklist の 1 項。PyYAML の厳格パースで 2 ファイルとも読め、新しい欄の値を取り出せた。self-conformance の C1 PASS)。
- **V3**・**V4**・**V6**= 独立検査(§6)。**V5**・**V7**= クローズ節。
