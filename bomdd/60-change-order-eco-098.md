# Change Order — ECO-098(ECO-097 試行の反映 — 裁定層と導出層の欄の所有・M-BOM の 3 分類・検査行と裁定層の結線・人が読む表を playbook と 32 / 33 テンプレへ candidate として置く〔文書のみ・verified〕)

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

## 6. 独立検査(異系統・EQ-002 Codex gpt-5.6-sol)

### 6.1 r1(2026-10-05・境界探索・対象 8d84edb)— **REJECT IA-01**

- 報告= [independent-inspection-eco-098.md](reports/independent-inspection-eco-098.md)。項目 1(範囲)・2(記録との一致: 主張 16 件すべて一致・記録に無い主張なし)・4(既存本文・テンプレとの矛盾なし・ECO-086 と両立)・5(機械的健全性)・6(言い回し)= PASS。
- **IA-01(blocking・製造物)**: §9 の新しい項の見出しが `candidate・ECO-097 試行 N=1` だけで、「2 製造単位・1 製品」が無い(§4.4・§4.5 にはある)。V1 の条件(3 項とも試行の規模を明示)を満たさない。
- 帰属= 製造者(V1 の条件を自分で書いておきながら、3 項のうち 1 項で規模の句を落とし、受入の実測 §5 で「各項に candidate・N=1」とだけ確かめて PASS とした— 条件の「2 製造単位・1 製品」を grep していない)。
- 是正= §9 の見出しを他の 2 項と同じ `candidate・ECO-097 試行 N=1〔2 製造単位・1 製品〕・ECO-098` に(1 行)。§5 の V1 の観測は r1 の時点では誤り(是正後に再測し、クローズ節に書く)。

### 6.2 r2(2026-10-05・是正確認+回帰・対象として渡した revision= 8d84edb)— **REJECT IA-01 / IA-02(受理側の手順の誤り・製造物の所見ではない)**

- 報告= [independent-inspection-eco-098-r2.md](reports/independent-inspection-eco-098-r2.md)。項目 3(回帰)= PASS(未 commit の是正 1 行も「規模の句の追加だけで新しい不一致・矛盾なし」と観測)。
- **IA-01 / IA-02(blocking・帰属= 受理側〔製造者の運転〕)**: 是正を commit しないまま検査を起動した。commit のコマンドで、未追跡の r1 報告を `git add -u <path>` に渡してエラーになり、`&&` で結んだ commit と push が実行されなかった。
  その後ろに `;` で並べた「HEAD の sha を取る → ブリーフに埋める → 検査を起動」は止まらずに走り、検査官には是正前の revision(8d84edb)が渡った。検査官は「対象 revision では是正されていない」「是正の差分の窓がゼロ幅」と正しく判定した。
- 機序= 検査と後続の操作を条件で結ばなかった(AGENTS.md 規律 3・ECO-024 と同型。今回は commit の失敗を観測する前に、検査の起動が実行された)。実害= 検査 1 round の空費(push・昇格は起きていない)。
- 処置= 是正・r1 報告・r2 報告・本記録を commit し(commit の成否を観測してから)、r3 で是正確認をやり直す。r3 の報告の置き場を allowed_paths に足す。

### 6.3 r3(2026-10-05・是正確認+回帰・対象 ad9d836)— **ACCEPT**

- 報告= [independent-inspection-eco-098-r3.md](reports/independent-inspection-eco-098-r3.md)。項目 1(3 項すべての見出しが `candidate・ECO-097 試行 N=1〔2 製造単位・1 製品〕・ECO-098`)・2(`git diff 8d84edb ad9d836 -- method/` は §9 の 1 行だけ・変更 5 パスは allowed_paths 内)・
  3(回帰: r1 の PASS 項目に新しい不一致・矛盾なし・テンプレは r1 から不変)= PASS。所見なし。

## 7. クローズ(2026-10-05・verified・異系統の独立検査 r3 ACCEPT)

- **V1**= PASS(観測: 是正後の grep `試行 N=1〔2 製造単位・1 製品〕・ECO-098` → playbook 3 行〔§4.4・§4.5・§9〕。各項に未測定 / 限界の句。検査官 r3 項目 1)。§5 の V1 の観測は r1 の時点では誤りだった(§9 に規模の句が無かった・§6.1)。
- **V2**= PASS(観測: §5 のとおり・検査官 r1 項目 5〔PyYAML で読める・新しい欄の型・schema は新しい欄を拒否しない〕)。
- **V3**= PASS(観測: 検査官 r1 項目 2 — 本文の事実の主張 16 件すべてが ECO-097 の記録と一致・記録に無い主張〔効果・一般化・同等性〕なし)。
- **V4**= PASS(観測: 検査官 r1 項目 4 — §4.1・§4.4・§4.5・§4.6・§7・§9・§11・§13・30 / 32 / 33 / 34 テンプレと正面の矛盾なし・ECO-086 の ID だけの行と両立。phase3-design は新しい所有・結線を説明していないが逆の作業を指示していない)。
- **V5**= PASS(観測: 窓 `f99c7c4` → `ad9d836`= allowed_paths のみ〔playbook・32・33・台帳系・r1 / r2 報告〕・tools / hooks / .github / schemas / prompts diff 0。各 commit は self-conformance exit 0 観測後。CI cf1852f / 8d84edb / ad9d836 とも success。本クローズ commit は台帳系+r3 報告のみ)。
- **V6**= PASS(観測: r1 REJECT IA-01 → 是正 → r2 REJECT〔受理側の手順の誤り〕→ r3 **ACCEPT**・所見なし)。
- **V7**= 下の較正 receipt。register: `implemented → verified`。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格・receipt_author_role= producer。文書のみの変更・異系統の独立検査 3 round)

- 査定した主張と判定:
  1. 「playbook の 3 項と 32 / 33 テンプレの追加は、ECO-097 の記録と一致し、記録より強い主張を含まない」— **observed / 適格**(検査官 r1: 主張 16 件を 1 件ずつ記録と突合・全件一致)。
  2. 「3 項とも candidate と試行の規模を明示している」— **observed / 適格**(是正後・検査官 r3)。製造時点では不成立(§9 の 1 項で規模の句が欠落)で、製造者の受入の実測は誤って PASS としていた。
  3. 「追加は既存の本文・テンプレ(ECO-086 を含む)と矛盾しない」— **observed / 適格**(検査官 r1 が §4.1〜§13 と 30〜34 テンプレ・phase3-design を実読)。
  4. 「テンプレは機械的に健全」— **observed / 適格**(PyYAML・C1・schema は additionalProperties を拒否しない)。
  5. 「この記載で、次の製品の担当者が同じ分け方を実行できる」— **unknown**(文書を読んだ別の担当者による実施は未実施。phase3-design などのプロンプトは未改訂で、新しい項を参照していない)。
  6. 「この分け方は効果がある・他の製品でも機能する」— **unknown(本文も主張しない)**。
- 検出した計器欠陥(帰属つき): 製造物 1 件= IA-01(§9 の項に規模の句が無い・是正済み)。製造者の受入 1 件= V1 の条件の全部を測らずに PASS とした(「candidate・N=1」だけを確かめ「2 製造単位・1 製品」を grep しなかった)。
  受理側の運転 2 件= ①検査の起動のパス指定の誤り(検査は始まらず・再実行)②是正の commit の失敗を観測する前に検査の起動が走り、是正前の revision を検査へ渡した(r2 の空費・AGENTS.md 規律 3 と同型・push と昇格は起きていない)。
- 検出力の限界: 文書のみ。検査官は 1 系統(Codex)・読解中心。本文の「実行可能性」(読み手が実際に従えるか)は測っていない。試行の根拠自体が 2 単位・1 製品・同日。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 読解 | 受入条件は「記録との一致・candidate の表示・矛盾なし・健全性」までで、効果を条件にしていない。主張 5・6 を unknown に分離 |
  | Q2 | asked | observed/適格 | 実測 | V1 は是正前の revision で検査官が FAIL・是正後に PASS(同じ項目が反転)。r2 は是正前の revision を渡すと FAIL になることを意図せず実演した |
  | Q3 | asked | observed/適格 | 実測 | 製造者の grep・PyYAML・self-conformance と、検査官の主張ごとの突合を別々に行った |
  | Q4 | asked | observed/適格 | 実測 | 実ファイル・実 commit(cf1852f / 8d84edb / ad9d836)・CI |
  | Q5 | asked | observed/適格 | 実測 | 未改訂のプロンプト・未測定の実行可能性を限界として分離 |
  | Q6 | asked | **逸脱 1 件** | 実測 | commit の成否を観測する前に検査を起動した(r2)。以後は commit を単独で実行して exit を観測してから起動(r3)。push・昇格の順序は保たれた |
  | Q7 | asked | observed/適格 | 実測 | 陽性対照= r1 の FAIL(規模の句の欠落)と r2 の FAIL(是正前の revision)。検査官は 2 回とも落とした |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | 検査の対象 revision の完全 SHA をブリーフに埋め、検査官が `git rev-parse HEAD` と照合(r3= ad9d836…)。r2 は渡した SHA が是正前だったことを検査官が検出 |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」+主張 5・6 |
  | Q11 | asked | observed/適格 | 読解 | 入力クラス(playbook の 3 項 / テンプレ 2 本 / 既存節との照合 / schema・ツールへの影響)を分けて検査させた |

- このクローズが支持しないもの: 記載した分け方の効果 / 他の製品への一般化 / 文書だけで別の担当者が実施できること / candidate の実証済みへの格上げ。
