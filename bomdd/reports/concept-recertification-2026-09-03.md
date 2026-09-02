# concept.md 全命題の初回再認証(2026-09-03・4 値・改訂は含まない)

> 裁定(user 2026-09-02〜03): 思想文書の命題を信条でなく**実証状態を持つ仮説**として扱う。/lesson-promote 手順 3b
> の 4 値(supported / contradicted / superseded / untested)を [docs/concept.md](../../docs/concept.md) の全命題に
> 初回適用し、基準線を作る。本書は判定の記録であり、concept.md 本文の改訂は**レビュー停止点**の後(改訂案は §3)。

## 0. 方法

- 対象: concept.md(2026-09-02 版・74 行)から、事実または規範を主張する文を全数抽出(参照・読む順序は除外)。24 命題。
- 判定語: **supported**= 現在の実測(FINDINGS・loops・製品リポ・playbook の実文)が支持 / **contradicted**= 実測と矛盾 /
  **superseded**= より精密な命題に置換済みで旧文言の除去または限定が要る / **untested**= 実測なし(信条のまま)。
- 証拠は `file:line` または loop ID。推測は「疑い」と明記。

## 1. 命題別判定

| # | 行 | 命題(要約) | 判定 | 根拠(実測) | 改訂要否 |
|---|---|---|---|---|---|
| 1 | 7 | ソフトウェア開発を設計BOM→AI製造→保守BOMの工業プロセスとして扱えるかを問う | **supported**(新規製造)/ **superseded**(保守) | 新規: forward-01 rev2 fresh 2 工場 23/23(FINDINGS:203)。保守: /eco-fix は設計者 AI のプローブ先行・直接最小是正で fresh 再製造ではない(eco-fix.md:3)。BOM は変更統制の正本として保たれ、製造の正本は新規製造時のみ | 要(保守レジームの実態を明示) |
| 2 | 9 | これは開発でなく研究である | **superseded** | 確立済みリポの継続運用は別レジームとして観測開始(FINDINGS:701)。ViewPrism2 141 ECO・TimetableAdv 42 ECO が製品運用中 | 要(研究+製品運用の二レジーム) |
| 3 | 9 | 題材は MoviePad・7 ループ | **superseded** | v2 で Web/API・分散 Saga(N=3 ドメイン・FINDINGS:180)、フォワード 4 題材、製品 3 リポ | 要 |
| 4 | 13 | AI=製造装置。プロンプトでなく投入情報を NC データとして管理する | **supported** | 製造パッケージ限定供与(playbook §5.1)・kit 凍結と bomdd.lock(bomdd-init.py:12-16)・work order | 不要 |
| 5 | 14 | BOM=製造指示(意図・構成・製造単位・受入基準の構造化) | **supported** | templates 20/30〜34/40・§4.4 | 不要 |
| 6 | 15 | 失敗は部品表不足だけでなく暗黙知・治具・検査・許容差の未管理に起因 | **supported** | ずる C2/C4 集中(FINDINGS:48)・K-BOM 価値(method-v1:65)・§4.4 test_vectors(CHEAT-005) | 不要 |
| 7 | 16 | 来歴を SLSA provenance 拡張(As-Built)で記録 | **supported** | 50-as-built.yaml:6・terminology:72(webapi で運用) | 不要 |
| 8 | 22 | E-BOM= 論理部品+存在理由↔仕様トレース | **supported** | 30-ebom・terminology(グラフ・woven)。粒度ガイド | 不要(「木でなくグラフ」を補うと精密) |
| 9 | 23 | M-BOM+工程= 実現技術・合否基準・CP・FMEA・隔離・多工場 | **supported** | 32/33/34・§4.2・§5 | 不要 |
| 10 | 24 | S-BOM= 外部知識依存の劣化→影響→再検査→交換判断 | **supported** | forward-03 で実 GHSA を DEG 起票→再製造まで一周(FINDINGS:241-254) | 不要 |
| 11 | 26 | K-BOM= 外部/設計知識を部品化し暗黙知を管理対象に | **supported** | webapi opus 0 / haiku 3(method-v1:65)・k-bom-ffmpeg | 不要 |
| 12 | 27 | S-BOM は一般的 SBOM ではない | **supported** | terminology #s-bom | 不要 |
| 13 | 28 | UI-IR/UI-BOM は **candidate**。正式 E-BOM を置き換えない | 後半 **supported** / 「candidate」ラベルは **superseded** | playbook §1 全体フローで Phase 1.5 は GUI 案件の正規工程(完了条件= 治具 exit code・playbook:27)。ViewPrism2 で ui-bom.json が ECO-016 等の再帰属対象として運用中。ui-ir-ui-bom.md 自身は「candidate / 未実証拡張」を自己宣言(ui-ir-ui-bom.md:3)= 文書間で状態が不一致 | 要(状態語の一意化 — どちらが正か裁定) |
| 14 | 29 | Design System BOM / Visual Gap は candidate | **superseded** | 検証済み一般化= 標準部品台帳(terminology:35・playbook §4.7・ViewPrism2 ECO-122)。Visual Gap は §4.4/43 テンプレで運用 | 要(標準部品台帳へ言及・candidate の限定) |
| 15 | 33 | 3 領域(純粋ロジック/外部ツール/UI)が同じ構造に収束 | **supported** | MoviePad 7 ループ+N=3 ドメイン再現(FINDINGS:180) | 不要(N を更新すると精密) |
| 16 | 35-40 | 核= 要求から導出可・unit・鋳造可 / 表面= 知識転記+検査工程・golden+人間判断 | **supported** | forward-01 20/20・webapi 収束・golden 規律(§4.4) | 不要 |
| 17 | 42 | **観測した 12 件のずるはすべて表面側**(単一題材・一般法則未検証) | **superseded** | 論文査読必須修正 3 を受けた盲検第二評価者再分類(2026-07-11): 一次発現層の確定分布= **artifact-surface 4・oracle 5・process 1・bom-metamodel 2・artifact-core 0**(results-blind:28)。確定命題は「成果物上に発現した 4 件はいずれも外部知識依存面・核 0」(X=4・results-blind:29)。「すべて表面」は一次発現層としては不正確。「単一題材」も N=3 で更新済み | **要(中核発見の文言そのもの)** |
| 18 | 43 | 核は鋳造 YES・表面は仕上げ検査で鋳造保証。工業化は部分的成立 | **supported** | 同上+UI-CAD で mock 改版ゼロ N=3(§8.3)。表面の「半自動+人間検査」は golden 必須で継続 | 不要 |
| 19 | 47 | ずるは測定器。ゼロが目的でなく管理場所を決める | **supported** | §6.2 3 択・cheat-log 運用 | 不要 |
| 20 | 49 | 隔離+網羅報告が最も効いた測定器(C2 可視化) | **supported** | Loop1 16 ギャップ(metrics.csv:2)・forward-03 でずる報告が劣化イベント受信機を兼ねた | 不要 |
| 21 | 50 | 分類は C1〜C6 | **superseded** | taxonomy に「証拠偽装」(2026-08-02 昇格)と「帳簿代用」(2026-08-17 昇格・実測 6 例)が追加(cheat-taxonomy.md:28,45) | 要(拡張分類への言及) |
| 22 | 54 | 受入の梯子 L0<L1<L2<L3<golden。L0/pixel-exact 既定不採用 | **supported** | method-v1 §5・41 規律・terminology(例外条件つき) | 不要 |
| 23 | 55 | 品質の二軸。一致≠正しさ(共有暗黙知の罠) | **supported** | CHEAT-012・Loop5 L3 座標系(FINDINGS:46,82)。検査器側にも同型(saga v1.2) | 不要 |
| 24 | 59-63 | v1 完了 / v2 完了 N=3 / フォワード実証 / 現在= 自己適用と計器較正 / スキーマ候補 | **supported** | 2026-09-02 更新済み。schema-candidates-index | 不要 |

## 2. 集計と所見

| 判定 | 件数 | 命題 # |
|---|---|---|
| supported | 17 | 4〜12, 15, 16, 18〜20, 22〜24(+1 前半・13 後半) |
| superseded | 6 | 1(保守)・2・3・13(ラベル)・14・17・21 |
| contradicted | 0 | — |
| untested | 0 | — |

所見:

1. **中核発見(#17)の文言が 2026-07-11 から陳腐化していた。** 盲検再分類は論文用に実施され results と論文表 22 へ反映されたが、concept.md には届かなかった。欠損辺①(教訓→思想層)の最も重い実例で、置換後の命題「成果物上に発現した 4 件はいずれも外部知識依存面・核 0」は元の命題より弱いが正確である。terminology.md「表面」項(「12 件のずるはすべてここで出た」)と README の「ずる台帳 12 件」表現も同時に点検対象。
2. **contradicted は 0 件だが、#1 の保守レジームは境界例。** 「AI 製造」を保守にも貫くという読みなら実態(設計者 AI の直接是正)と矛盾する。superseded としたのは、BOM が変更統制の正本として保たれており、命題の精密化で足りるため。
3. **状態語の不一致(#13・#14)。** 「candidate」が文書ごとに違う意味で残っている(playbook では正規工程、原典文書では未実証拡張)。状態語の正本を一箇所に決める裁定が要る。
4. **untested が 0 件なのは、concept.md が主張を実証済み範囲に絞って書かれてきた証拠**であり、思想文書としての品質は高い。劣化は「誤り」ではなく「更新の不達」に集中している。

## 3. 改訂案(レビュー停止点 — 承認された項のみ適用)

| 項 | 改訂案 |
|---|---|
| A(#17) | 行 42 を「観測した 12 件のずるのうち成果物上に発現したのは 4 件で、いずれも外部知識依存面(核 0)。残りは oracle 5・process 1・bom-metamodel 2 に発現(盲検第二評価者再分類 2026-07-11・一致 10/12・κ 0.77)。3 ドメインで再現、一般法則は引き続き未検証」へ置換 |
| B(#1) | 行 7 の直後に「保守レジーム(Phase 7)では BOM は変更統制の正本であり、是正は設計者 AI のプローブ先行直接是正+BOM 同期で行う(fresh 再製造は新規製造と収束ループ)」を 1 文追加 |
| C(#2,#3) | 行 9 を「研究(方法論リポ)と製品運用(ViewPrism2・TimetableAdv 等)の二レジーム。初期題材は MoviePad 7 ループ、以後 N=3 ドメイン+フォワード」へ |
| D(#13,#14) | 行 28-29 の「candidate」を、裁定後の状態語(GUI 案件の正規工程 / 標準部品台帳への一般化済み)へ置換。ui-ir-ui-bom.md:3 の自己宣言も同時に揃える |
| E(#21) | 行 50 に「+ 証拠偽装・帳簿代用(2026-08 昇格)」を追記 |
| F(付随) | terminology.md「表面」項・README「ずる台帳 12 件」の同型点検 |

source: user 裁定 2026-09-03(concept.md 全命題の初回再認証)
evidence: 本書 §1 根拠列
