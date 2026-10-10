# Change Order — ECO-103(製品コードの変更の独立レビュー R8 と、独立の 2 段〔文脈の独立 / 設備の独立〕を配布キットの変更管理へ — 運転層の規約 §5 の委ね先の空白を埋める〔文書のみ・candidate〕)

> 裁定: user DECIDE「A」(2026-10-10・本 ECO の起票の直前)。A の内容は「打ち切り採用。独立を 2 段に分ける。R8 は文脈の独立(別の新しい文脈・同じ設備でよい)で足りる。設備の独立(異系統・運転層の規約 §4)は playbook §3 の高リスク検査治具などに限る。記録にはどちらの独立かを書く」。
> 示した選択肢: A(上記)/ B(打ち切り採用・R8 も設備の独立を必須)/ C(収束の手順をもう 1 周してから再提示)。推奨は A と添えた。
> 経緯: user が持ち込んだ議論(「方法論は何をするかは書くが誰がするかが曖昧・誰がはロール」)→ 当方 DISCUSS(提案 1〜3)→ user「1から進めて」→ 導出と /converge(未収束 6→1→0)→ DECIDE → 「A」。

## 担当設備(equipment)

- 起票・設計・製造: requested/resolved `claude-opus-5-5`・Claude Code(Claude Agent SDK)・来歴 **self-reported**(同じセッションの前半は `claude-sonnet-5-5`〔EQ-005〕。導出・/converge・DECIDE 以降は EQ-004)
- producer: EQ-004
- 独立検査: EQ-002(Codex CLI / gpt-5.6-sol・異系統)— 配布キットの文書の改訂のため受ける。

## 0. 根拠(起票・2026-10-10)

### 0.1 空白(導出の結果)

- 運転層の規約(キット `method/templates/product-profile/operator-layer.md:109`)は「`inspector` を書かない変更は製造者の自己較正だけで閉じる(それが許される変更かどうかは変更管理の規律が決める)」と委ねている。
- 委ね先の変更管理の規約(キット `change-management.md`)には、独立レビュー・独立検査の要否の条文が無い。`独立|independent|R8` の該当は 1 行で、受入証拠レイヤーの語(:97)だけ(`measurements.txt` M3)。
- キットの是正スキル(`skills/eco-fix.md`)にも独立レビューの段が無い(`R8|独立|fresh|異系統|セルフレビュー` 0 件・M3)。

### 0.2 製品が別々に置いた同じ規則(写しと sha256 は `bomdd/reports/eco-103-r8-independent-review/`)

- ViewTube `bomdd/process/change-management.md:103-107` R8「Any product-source change receives a fresh-context independent review」・`AGENTS.md:23`(写し `viewtube-r8.txt`。ViewTube は origin より 5 commit 先行で未 push のため写しを置いた)。
- ViewPrism2 `.claude/skills/eco-fix/SKILL.md:55-64` 手順 3.7「セルフレビュー(R8・src に触れた fix は必須)」。独立性の担保は「fix を書いたコンテキストと別の fresh context」。文書のみ・機械的 1 行変更は「R8 対象外」を宣言して省略できる。入れた commit は c49286a(2026-07-18)(写し `viewprism2-r8.txt`)。
- 両製品とも、独立を「別の新しい文脈」で担保している。モデル・ハーネス・系統を変えることは求めていない(ViewPrism2 の Codex は「裁量で追加」)。

### 0.3 規則どうしの食い違い

- 運転層の規約 §4(`operator-layer.md:91-96`)は、producer と inspector のモデル・ハーネス・系統の 3 軸がすべて一致すれば独立不成立とする。同じ設備のサブエージェントによる「別の新しい文脈」の見直しは、§4 では独立にならない。製品の R8 を同じ語でキットへ入れると、2 つの規約が矛盾する。

### 0.4 既にある関連の規則(変えない)

- playbook §3(`method/bomdd-playbook-v1.md:181`)— 高リスクの検査治具は異系統の独立受入検査を通す(必須条件は異系統性)。
- playbook §9 — 製造者の自己査定は自分の前提誤りに盲目。自己査定のみで verified にする場合は、その旨を register の verification に明記する。
- `method/control-plan.md:123-125` — 人間の golden は独立検査の下流で独立の弁別力を持つ。独立検査の PASS を golden の省略の根拠にしない。
- キット `change-management.md:36` R4 — 人の関門は裁定と golden の 2 つだけ。
- ECO-077(`bomdd/60-change-order-eco-077.md:5`)— 採らない: persona プロンプト / 新しい Role・Process の YAML スキーマ / 役割の機械強制 / receipt_author_role の門化。

### 0.5 訂正の記録(DISCUSS・DECIDE の時点の発言)

- 「独立性が記録に残らない」は誤り。BomDD の自己適用は register の `producer` / `inspector` と設備台帳 `bomdd/70-equipment.yaml` の 3 軸で記録している(`inspector: EQ-` は 7 件・M4)。24 件すべてが producer だった `receipt_author_role` は「較正 receipt を誰が書いたか」の欄で、独立検査の有無の欄ではない。
- 「ViewPrism2 には条文が無い」は誤り(§0.2)。
- 「最近の ECO は 8 件が異系統の検査官」は誤りで、7 件(M4)。

## 1. 変更要求(user 裁定 A・凍結)

1. キット `method/templates/product-profile/change-management.md` §2 に **R8** を加える(R7 の後・candidate・ECO-103)。
   - 保護パス(`src/`・`test/`)に触れる ECO は、golden の提示(golden n/a なら受入の依頼)の**前**に、製造した文脈と別の新しい文脈で diff を見直す。
   - 所見は全列挙して処置する(スコープ内= R5 へ / スコープ外= R3)。未処置のスコープ内所見が 0 になるまで停止点へ進まない。
   - 文書のみ・機械的な 1 行変更は「R8 対象外」を宣言して省略できる。宣言は製造者が書く(自分の判断であることが記録に残る形)。
   - **独立の 2 段**: 文脈の独立(R8 の既定。同じ設備の別の新しい文脈でよい)/ 設備の独立(運転層の規約 §4。異系統)。設備の独立は playbook §3 の場合に要る。
   - レビューの記録には、どちらの独立かとレビューした設備を書く。設備の独立でないレビューを register の `inspector` に書かない(§4 で不成立になる)。
   - R4 の人の関門は増やさない。1 人が要求者・裁定者・golden 承認者を兼ねてよいが、それを独立した人の承認とは主張しない。
   - 由来(2 製品が別々に同じ規則を置いた)と、未測定(文脈の独立で足りるか)を併記する。
2. キット `skills/eco-fix.md` に手順 **3.6**(R8 の段)を加え、frontmatter の description に R8 を足す。
3. キット `operator-layer.md:109` の委ね先を「変更管理の規約 R8」と名指しにし、`inspector` が設備の独立の欄であることを添える。§4 は変えない。
4. `method/improvements.md` に本節(記帳)と EXP(効果の測定先)を置く。

**採らない**: 設備の独立を R8 の既定にすること(案 B)/ 機械的な強制・新しいスキーマ・新しい欄(ECO-077 の裁定と、ViewTube の門の費用の実測〔`bomdd/reports/viewtube-inspection-cost-20261010/`〕)/ 既存製品(ViewTube・ViewPrism2)への書き込み(次の配布で波及)/ BomDD の自己適用の規則の変更 / playbook・control-plan・operator-layer §4 の変更 / 効果の主張(candidate のまま)/ 初回製造(ECO を使わない段階。factory-delegate の役割分離が担う)。

## 2. 影響なし予測(製造前・凍結)

diff= キット change-management.md(§2 に R8 の 1 項)・skills/eco-fix.md(手順 3.6 と description)・operator-layer.md(:109 の 1 行)+台帳系(order・register・improvements.md)+`bomdd/reports/eco-103-r8-independent-review/` のみ。
change-management.md の R1〜R7・§0・§1・§3〜§5(ECO-079 が所有する §4 の受入証拠レイヤーの段落を含む)は 1 字も変えない。tools・hooks・.github・schemas・playbook・control-plan は diff 0。
self-conformance の判定は不変の見込み(C4〔bomdd-init 生成物の parse〕・C10〔正本と写しの同期〕の対象かは製造時に確認する)。配布テンプレは次回配布時に波及・既存製品は不変。

## 3. 受入条件(製造前に凍結・二部形・ECO-080)

- V1(条件): change-management.md §2 に R8 の項があり、次の句をすべて含むこと — `R8`・`文脈の独立`・`設備の独立`・`R8 対象外`・`inspector`・`ECO-103`・`未測定`。R1〜R7・§0・§1・§3〜§5 は 1 字も変わらないこと — 検査法: 各句の grep・`git diff` の hunk が §2 の R7 の後の 1 か所だけであることの実読。
- V2(条件): eco-fix.md に手順 3.6 があり、`R8`・`停止点に進まない`・`R8 対象外` を含み、他の手順と停止点の節が変わらず、frontmatter が YAML として読めること — 検査法: grep・`git diff`・PyYAML。
- V3(条件): operator-layer.md の diff が :109 の 1 行だけで、§4(:89-99)が変わらないこと — 検査法: `git diff`。
- V4(条件): 本文の事実の主張(§0)が写し・測定(`measurements.txt`)・BomDD の記録の値と一致し、記録より強い主張(効果・一般化)を含まないこと — 検査法: 異系統の独立検査。
- V5(条件): 改訂後の 3 つの文が、運転層の規約 §4・§5、R4、playbook §3・§9、control-plan:123-125、ECO-077 の採らないもの、ECO-079 の段落と矛盾しないこと — 検査法: 実読・独立検査。
- V6(条件): diff が allowed_paths のみ・self-conformance 全 PASS(exit 0 の観測後に commit)・CI success であること。
- V7(条件): 異系統の独立検査が ACCEPT であること。
- V8(条件): 較正 receipt(trigger ①)があること。
- V9(条件): improvements.md に記帳と EXP があり、worklist の検証警告が 0 であること — 検査法: `python method/tools/worklist.py`。

## /preflight receipt(起動経路: **自発** — 既裁定の適用の開始時)

- 分類= 既裁定の適用(user「A」)。設計の空白は文言と置き場所だけ。
- 最小契約: baseline `810b442`= **confirmed**(HEAD・clean・CI 38020016730 success)/ 裁定の内容= **confirmed**(DECIDE の文面と「A」)/ 空白と食い違い= **confirmed**(§0.1〜0.3 の file:line と M3)/ acceptance-target= **missing** → 本 order §3 で定義。
- discovered(契約外): **ECO-079(status implemented・独立検査未了)が同じファイル `change-management.md` を affected_refs に持つ**。ECO-079 の製造物は §4 の受入証拠レイヤーの段落(:96-100)で、本 ECO は §2 だけに触れる。V1 で §4 の不変を確かめる。ECO-079 の窓・状態には触れない。
- 次番 103= **confirmed**(register の最大 ECO-102)。
- 開始判定: **PROCEED_WITH_LIMITS**(限界= ECO-079 と同じファイルに触れる・§4 を変えないことを V1 で検査)。override なし。

## /converge receipt(起動経路: 自発 — 独立性の規則の設計と提示)

- **判定: 未収束**(round 軌跡: 6→1→0)。上限 3 周で 2 周連続ゼロに届かず。**user 裁定 A= 打ち切り採用**(2026-10-10)。延長はしていない。
- DoD(着手前に固定): ✔ 正本が一意(要否の条文はキット change-management の R8 の 1 か所・eco-fix は実行の段・operator-layer は参照)/ ✔ 既裁定の実文と突合(R4・ECO-077 の採らないもの・playbook §3・§9・control-plan:123-125・operator-layer §4)/ ✔ 必ず起きるイベントのアンカー(golden の提示または受入の依頼の前 — 是正のたびに必ず通る eco-fix の段)/ ✔ 影響が行単位(3 ファイルの 3 か所)/ ✔ 機械的な強制・新しいスキーマを足さない / ✘ 文脈の独立で足りるかの実測(未測定のまま提示)。
- round 1(新規 6 件): ①ViewPrism2 にも R8 がある(主張「条文なし」の反証)②キットの eco-fix にも段が無い — 規約だけに書くと実行の時点が定まらない ③「対象外」の宣言は製造者による権限の自己付与(OBS-20260806-02 の型)— 限界として明記 ④初回製造は ECO を使わないので範囲外 ⑤R4 の人の関門を増やさない ⑥文脈の独立と §4 の設備の独立が矛盾する(§0.3)。
- round 2(新規 1 件): 設備の独立でない見直しを `inspector` に書くと §4 で不成立になる → 記録の置き場を分けた(レビューの記録は order の実施記録・`inspector` は設備の独立だけ)。
- round 3: 0 件(失敗型 ①〜⑧ の照合・敵対自問「起票時に要否を決めると製造者が自分で決める」→ 既定はパスで決まり、外すのは宣言つきの 2 種だけ)。
- 検証した主張(実測): §0.1〜0.4 の file:line(`measurements.txt` M1〜M4)。
- 未収束事項: 文脈の独立で足りるかは未測定(EXP で測る)。round 3 の後の確認周は行っていない(裁定 A)。

## 4. 製造

(次の commit で記録する。)
