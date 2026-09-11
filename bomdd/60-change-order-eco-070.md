# Change Order — ECO-070(handoff 契約 v0.3: 試行評価の 5 点+待機形を織り込み、AGENTS.md から参照〔verified〕)

> 裁定: user 2026-09-12 DECIDE「A」(採用)+「5 点を v0.3 に織り込んで起票して」— handoff プロトコル(`.claude/skills/handoff/SKILL.md`・2026-09-11 運用開始・ECO なし)の
> 試行 EXP-20260911-01 を評価した結果、採用。当方が自己出力に見つけた改善 5 点と、評価で露出した待機通知の扱いを契約 v0.3 に織り込み、第三者(別セッション)が
> 到達できるよう AGENTS.md から参照する。**起票と製造を同一 commit で行う**(文書のみ・ECO-063/069 の型)・受入は製造者較正のみ。配布(product-profile への正本化)は本 ECO の範囲外。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**

## 0. 実測(起票根拠)

- **試行評価**(本セッション transcript を機械集計・2026-09-12): 運用開始以降の handoff 67(ヘッダ付き。運用前の同セッションはターン終了 65・ヘッダ 0)。
  mode 内訳 INFORM 44 / DECIDE 12 / REQUEST 8 / DISCUSS 3。DECIDE 12 回の user 返答は 12/12 が reply_format どおり(「Aです」「1:C 2:A」「B→C」等)。
  DISCUSS 3 回は各 1〜2 往復で AGREE か DECIDE に収束。mode 訂正 1(運転員依頼を INFORM/BLOCKED で 3 通 → user 訂正 → v0.2 REQUEST)。
  REQUEST 8 回のうち成果物(run-02 台帳 R1〜R8)の回収に追加 5 往復。INFORM/CONTINUING 38 通はほぼ全件がバックグラウンド検査の完了待ちでターンが
  切れたもの(user 返信 0・handoff の 57%)。運用前には「何に対応しましたか?私は何を試せますか?」「現在地が分かるようにしたい」「3 点の裁定です(長文)」型の
  再分析往復が 3 件、運用後は 0 件。限定子: 同一セッション・同一 user・N 小で学習効果と分離できない(示唆止まり)。
- **user の感想**(2026-09-12): INFORM に大きな注意力を割かずに済むようになった / DECIDE で候補の温度差が伝わった / 根拠(メリット・デメリット)はもっと分かりやすいと嬉しい。
- **当方の自己評価(5 点)**: ①DECIDE の option に「得る・失う・戻せるか」が揃っていない ②DECIDE の冒頭が状態報告で decision_question が後ろ ③option の束ねが粗く
  部分採択しにくい ④REQUEST の deliverable が穴埋め様式でなく回収に 5 往復 ⑤自己検査が形式的— INFORM/BLOCKED を FAIL H2 と申告しつつ送った。
  **訂正(正直記載)**: 当方は評価 DECIDE で「ヘッダ組合せの許容表がない」と述べたが、実読では §2.3 H2 に INFORM/BLOCKED 無効の規則は**あった**。欠けていたのは
  契約 §1 側の表と「structural FAIL は送らない」の規則で、規則があっても申告付きで送った点が欠陥である。
- **第三者到達性**: user が別セッションに本プロトコルの評価を求めたところ「知らない」と回答された。契約への経路は `/handoff` 起動・description 自動起動・
  本プロジェクト memory の索引 1 行のみで、AGENTS.md・CLAUDE.md・playbook・templates に参照 0(grep)。当方の順守は会話文脈由来で設置の証拠ではない。

## 1. 変更要求(凍結・文書のみ)

1. `.claude/skills/handoff/SKILL.md` を **v0.3** に: 契約 §1 — (a) ヘッダ組合せの許容表(INFORM/BLOCKED・*/COMPLETE の裁定系・REQUEST/PAUSED を無効)と
   「structural FAIL は送信停止・自己申告して送れるのは semantic のみ」(b) DECIDE の options は各案に帰結(得る/失う/戻せるか)・recommendation に非推奨案が劣る理由・
   独立項目は番号を分ける (c) REQUEST の deliverable は穴埋め様式 (d) Scope にターン終了型の待機= INFORM/CONTINUING 待機形。実装 §2 — decision_question 先頭・
   options 同形 4 欄・待機形 2 行以内・F2/F4/F5・§2.4/§2.7 更新。§3 例(待機形・DECIDE 新形・REQUEST 穴埋め)。§4 評価記録と EXP-20260912-01。
2. `AGENTS.md` 作業スキル節に handoff 契約の段落(正本= SKILL.md・全ハーネス適用)と「正本の所在」表に 1 行。
3. `method/improvements.md`: EXP-20260911-01 を recovered へ・評価節・EXP-20260912-01 起票。

**採らない**: product-profile への正本化・配布(別 ECO・EXP-20260912-01 の後)/ self-conformance の `.claude/skills` 検査拡張 / 契約 §1 に出現順の規則を置く
(順序は §2 のまま・§4 分岐で昇格を判断)/ CLAUDE.md・playbook の変更。

## 2. 影響なし予測(製造前・凍結)

diff は SKILL.md・AGENTS.md・improvements.md+台帳系のみ。self-conformance: C12(AGENTS.md の相対リンク全数実在)は追加リンク先 `.claude/skills/handoff/SKILL.md` が
実在するので PASS 維持・C7(スキル本数= bomdd-init.SKILLS)は不変(handoff は SKILLS 外)・C13(リンク)は SKILL.md 内に新リンクなし。tools・templates・hooks・.github diff 0。
worklist: EXP-20260911-01 の状態遷移 1・新規 open 1・警告 0。

## 3. 受入

- **V1**: SKILL.md §1 に許容表・DECIDE/REQUEST の必須要素追記・Scope の待機形がある(grep)/ §2.3 に F5・§2.4 に送信停止規則。**V2**: AGENTS.md のリンクが解決し C12 PASS。
  **V3**: self-conformance 全 PASS・CI 緑・窓= 3 文書+台帳系。**V4**: 製造者較正のみ。**V5(クローズ条件でない)**: EXP-20260912-01 を次の handoff 20 回で測る。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-070` の出力を開始 artifact として読んだ)

- 分類= 既裁定の適用実装(user DECIDE「A」+起票指示)。baseline `a5700e9`= **confirmed** / 次番 070= **confirmed**(grep 0)/ 試行条件の充足(20 回・DECIDE 5 以上)= **confirmed**(67・12)/
  §2.3 H2 の既存= **confirmed**(実読・上記訂正)/ 凍結の非該当= **confirmed** / 同一ファイルへの進行中 ECO なし= **confirmed**。
- job ビュー: required_skills= `["preflight"]`・skills_missing= `[]`(order 生成後に出力)
- 開始判定: **PROCEED**・override 0。

## 4. 製造と受入の実測(2026-09-12・同一 commit)

- 製造物: SKILL.md v0.3(§1 許容表・必須要素・Scope / §2.1 待機 / §2.2 DECIDE・REQUEST・待機形 / §2.3 H2・F2・F4・F5 / §2.4 / §2.7 / §3 例 / §4)・AGENTS.md 段落+表 1 行・
  improvements.md。
- **V1**= PASS(grep: `Valid combinations` 1・`fill-in form` 1・`wait form` 1・`F5 待機形` 1・`送信停止` 2〔v0.3 注記+§2.4〕)/ **V2**= C12 PASS(§5)/ **V3**= §5。

## 5. クローズ(2026-09-12・verified・製造者較正のみ)

- **V3**= PASS(self-conformance 全 PASS・CI run 34618524024〔起票+fix aa70b65〕success)。diff 監査の窓: baseline `a5700e9` → head `aa70b65`(**窓閉鎖**)。窓内= 3 文書+台帳系のみ。
- **V2**= C12 PASS(AGENTS.md の相対リンク 14 件すべて実在・追加 1 件を含む)。
- register: `implemented → verified`・head 凍結。製造者較正のみ。契約 v0.3 は本 commit 以降の全 handoff に適用(EXP-20260912-01 の計測開始)。
- 製造中の実測(正直記載): 起票+fix 段の self-conformance 1 回目は **C13 FAIL**(improvements.md → 新規 order へのリンクが「不在」— 新規ファイルを stage する前に
  実行したため。C13 は追跡ファイルに対して照合する)。stage 後の 2 回目で全 PASS(exit 0 観測)→ witness → 入口 dry ADVANCE → commit。ECO-069 の入口 STOP と同じく
  受理側の手順欠陥で、製造物の欠陥ではない。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格。文書のみの変更)

- 査定した主張と判定:
  1. 「契約 §1 に許容表・必須要素追記・待機形がある」— **observed / 適格**(grep 6 件・V1)。
  2. 「AGENTS.md から契約に到達できる」— **observed / 適格**(C12 が追加リンクの実在を検査・14 件 PASS)。到達性の実効(別セッションが読むか)は **unknown(未測定)**。
  3. 「試行評価の数値(67・12/12・訂正 1・追加 5 往復・38/67)」— **observed / 適格**(transcript を機械集計・スクリプトは scratchpad・非正本)。
     「再分析往復 3 → 0」は当方の読解による分類(同一セッション・学習効果と未分離)= **読解**。
  4. 「v0.3 が v0.2 の欠陥を消す」— **unknown(未測定・EXP-20260912-01)**。
- 検出した計器欠陥(帰属つき): 製造物 0 件。受理側 2 件= ①評価 DECIDE の「許容表がない」は不正確(§2.3 H2 は存在・order §0 で訂正)②C13 を stage 前に実行(手順)。
- 検出力の限界: 効果の主張はすべて 1 セッション・同一 user の示唆。第三者到達性は入口の存在までしか示せない。独立検査なし(製造者較正のみ)。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 実測 | grep 6 件・C12 14 件 |
  | Q2 | asked | NA 相当 | — | 文書変更に known-bad 対照なし(宣言) |
  | Q3 | asked | observed/適格 | 実測 | 変更前(AGENTS.md 参照 0)→ 変更後(1 段落+1 行) |
  | Q4 | asked | 読解 | 読解 | 評価数値は機械集計・再分析往復の分類は読解 |
  | Q5 | asked | observed/適格 | 実測 | 未測定(到達性の実効・v0.3 の効果)を宣言 |
  | Q6 | asked | observed/適格 | 実測 | 検査 exit 観測(FAIL→stage→PASS)→ witness → 入口 dry → commit → push → CI |
  | Q7 | asked | NA | — | 陽性対照なし(文書) |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | witness・register・commit・run 台帳(ECO-070.jsonl) |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」 |
  | Q11 | asked | observed/適格 | 読解 | 入力クラス= 契約/入口/記帳の 3 文書・評価の限定子(同一セッション) |

- このクローズが支持しないもの: v0.3 の効果(EXP-20260912-01)/ 別セッション・別ハーネスでの到達と順守 / product-profile 配布(別 ECO)。
