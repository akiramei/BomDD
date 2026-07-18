# cli-cad-01 報告 — CAD 適格性の認定試験: CLI 媒体 N=1(2026-07-18)

> protocol rev2([protocol.md](protocol.md))の実施報告。kit 凍結= tag `cli-cad-01-kit-freeze`(24201cb)・oracle 凍結= tag `cli-cad-01-oracle-freeze`(6058f05・製造開始前)。

## 1. 結果要約

| 判定 | 結果 |
|---|---|
| **H1(認定試験の媒体非依存)** | **成立** — 再製品が凍結 oracle **91/91 PASS**+介入 method_explanation / rescue **0 件**(工場からの質問ゼロ・work order 発行のみ) |
| **H2(翻訳層の位置予測)** | **支持** — **観測された divergence 8 クラス中 8 クラスが P1**(100%・閾値 2/3。「CLI の暗黙次元を全数発見した」の意ではない)。P2(終了契約)・P3(環境前提)の観測差分は 0 |
| negative control | **5/5 検出** — 故障変異体全種を oracle が FAIL 化(適用 assert 5/5 PASS・無効変異 1 件を事前検出し差し替え) |
| CAD/原品乖離 | **0** — 原品も凍結 oracle 91/91 PASS |
| 転移の質 | 仮定 32 件を assumptions.md に全件記帳(未規定台帳は不変 — 補正④遵守)・fixtures での自己確認のみで納品 |

**結論(実験内判定)**: 構成的適格条件を満たす CLI-CAD 候補は、転移実測(認定試験)に合格した — 別ベンダーの fresh 製造者が CAD のみから「CAD で規定した意味論」の製品を製造し、CAD のみから独立導出された oracle がそれを判定できた。
**方法論上の一般化(2026-07-18 レビュー承認の表現)**: 構成的適格条件+転移認定試験の組み合わせは、UI に続き**非対話・読み取り専用 CLI** でも機能した。媒体横断の観測は 2 種類目。これ以上(CUI 全般・対話 CLI/TUI・副作用 CLI・API/イベント/データ CAD・あらゆる媒体)はまだ言えない — 本実証は「**非対話 CLI-CAD 実証**」として固定する。

## 2. 実施記録

| 段 | 実施 | 証拠 |
|---|---|---|
| CAD 起票 | 4 契約+U1〜U11・新規固定 13 契約群/既存散文由来 9 群 | kit/cli-cad.md・[cad-authoring-notes.md](cad-authoring-notes.md) |
| fixture 較正 | 原品 baseline 突合で起票欠陥 1 件検出・是正(f4 タイトル部分文字列衝突) | baseline/・authoring-notes §計数 |
| oracle 製造 | 独立検査官(fresh 文脈・kit のみ)が 91 検査+トレース表を導出。期待値は観測者 baseline と独立に全一致 | oracle/oracle-notes.md |
| negative control | 変異 5 種(exit 契約・区分混同・stats キー欠落・W1 除去・fence 無視)全て FAIL 化。blockquote 変異は fixtures 上で挙動差ゼロ= 無効変異と適用 assert が検出し fence 変異へ差し替え | acceptance/m*.oracle.txt・make_mutants.py |
| fresh 製造 | Codex(gpt-5.6-sol)が隔離 dir・kit のみで単一ファイル実装+仮定 32 件を納品。質問 0 | factory-deliverable/・[factory-assumptions.md](factory-assumptions.md) |
| 受入 | 固定 oracle(両者 91/91)+探索差分 11 ケース採取 | acceptance/ |

## 3. 探索差分の帰属(補正②の第 2 層 — 合否に不使用)

divergence 8 クラス(fixture 横断で同型を統合):

| # | 差分 | U 台帳 | 帰属 | P 分類 |
|---|---|---|---|---|
| 1 | worklist 行様式(原品= 固定幅列+見出し行/再製品= パイプ区切り・見出しなし)+件数行後の空行 | U1+U11+U3 | exploratory_unspecified_surface | P1 |
| 2 | actions due 行の書式(原品= 散文付き/再製品= `PROMOTION DUE: ID (watch 3/3)`) | **宣言漏れ**(トークンのみ規定・残余が U 台帳に不在) | unspecified_bom_residue | P1 |
| 3 | 境界なし時の legacy coverage(原品= 1 行/再製品= 3 行+0 節表示) | U6 | exploratory_unspecified_surface | P1 |
| 4 | unaudited 非ゼロ時の見出し文言 | U10 | exploratory_unspecified_surface | P1 |
| 5 | show の書式(コンパクト形+L 行番号 vs key:value 形・L 番号なし) | U5 | exploratory_unspecified_surface | P1 |
| 6 | usage 文言(`[path]` vs `[PATH]`) | **宣言漏れ**(U2 は警告・エラーのみを宣言) | unspecified_bom_residue | P1 |
| 7 | ファイル不在メッセージ文言(`file not found` vs `input file not found`) | U2 | exploratory_unspecified_surface | P1 |
| 8 | 警告メッセージ文言(日本語散文 vs 英語簡潔文 — `- L{n} {W}: ` 接頭は両者一致) | U2 | exploratory_unspecified_surface | P1 |

- specified_contract_miss: **0**(固定 oracle が両者 PASS)。
- exit code・stderr(空)・stats 10 キー書式・見出し 5 種・警告コード/順序・DUE 別区分・legacy 3 分岐・除外領域: 全ケースで一致(P2 領域の差 0)。
- **CAD 側の発見 2 件**(#2・#6): 「トークンを規定した行の残余書式」が U 台帳から漏れていた — 権威境界は「規定+明示的未規定」で全面を覆う書き分けが必要(沈黙の第 3 領域を作らない)。CLI-CAD 起票様式の改善種。

## 4. H2 の解釈

観測された divergence(8 クラス)は全数 P1(出力契約の暗黙次元)に集中した。P2・P3 は明示規定され、観測差分は 0 だった — 規定が薄い P1 に差分が集中するという予測と**整合**する。ただし P2/P3 差分ゼロの因果を「明示規定が効いた」と断定はしない: 題材の単純さ・fixture 被覆内で差が出なかった可能性・工場が偶然原品と同じ判断をした可能性が残る(negative control が exit 契約の検出力を実証しているため証拠は強いが、因果の完全証明ではない)。本判定は本題材で観測された 8 クラスに対する支持であり、**媒体一般の翻訳層分布は未確定**。fixture 較正で検出した f4 起票欠陥(タイトル部分文字列衝突)は、CAD→fixture 翻訳層の職人芸残留の実測でもある。

## 5. 限界(protocol §2 の事前宣言+実施上の追加)

1. 非対話・読み取り専用・単一入力 CLI に限定(設定優先順位・TTY・signal・対話状態機械・副作用 CLI は未被覆)。
2. 検査官・工場の遮断は隔離 dir+指示ベース(物理遮断でない)— 合格は弱く不合格は強い。
3. 検査官は設計者と同ベンダー(Anthropic)・別文脈。ベンダー横断は工場側のみ。
4. 題材の意味論正本(記帳スキーマ v1)が良質な散文で既存 — 正本が薄い題材での CAD 起票コストは未測定。
5. N=1・単一題材。transfer-test §8 の candidate 昇格には別媒体/別題材の反復が要る。

## 6. 工数(time-decomposition 規律 — observed のみ・自己申告なし)

単一セッション内で kit 凍結(24201cb)→ oracle 凍結(6058f05)→ 製造→受入まで実施。工場(Codex)の製造はバックグラウンド実行で、着工〜納品検出はセッション記録上おおむね 15:02〜15:15 前後(observed・壁時計)。人間応答待ちはレビュー裁定 1 回(protocol 補正指示)。細粒度の区間分解はセッショントランスクリプトから導出可能(derived への意味付けは未実施 — 本報告では観測値のみ記載)。

## 7. 還元への引き継ぎ(次パス= /lesson-promote)

- EXP-20260718-01(H1)・EXP-20260718-02(H2)の回収判定。
- silence CLI 観点行の実測種: 新規固定 13 契約群(authoring-notes)+divergence 8 クラス+宣言漏れ 2 件+タイトル部分文字列衝突。
- 見送り中の織り込み案B(silence §10 CLI 行)・案C(playbook 相互参照)の再裁定。
- OBS-20260718-03: 媒体実証 2/3 到達の判定材料(CLI = 本報告)。
- OBS-20260711-09 への更新材料: クライアント/セッション記録上の resolved model = gpt-5.6-sol(サーバ側最終到達は未確認)。transfer-04 時とは観測された resolved model フィールドが変化した — ルーティングまたは統合層更新の**候補証拠**(断定しない)。
- OBS-20260716-07 の 2 例目: 変異の適用 assert が無効変異(blockquote 除去= fixtures 上で挙動差ゼロ)を実検出。
