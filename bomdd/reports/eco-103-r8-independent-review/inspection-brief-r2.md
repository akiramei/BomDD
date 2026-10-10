# 独立検査ブリーフ r2 — BomDD ECO-103(製品コードの変更の独立レビュー R8 と独立の 2 段・検査官= EQ-002)

- 役割: **inspector(検査官)**・EQ-002(Codex CLI / gpt-5.6-sol)。責任= 製造物(配布キットの 3 ファイル)と order の事実の主張を、記録と突き合わせて判定すること。境界探索(範囲の外れ・記録より強い主張・既存の規則との矛盾)を主な仕事とする。
- range: **是正確認+回帰**(r1 の IA-01・IA-02 の処置の確認と、項目 1〜6 の回帰。新しい種類の境界の探索は本 round の仕事ではない — 見つけた場合は所見に書いてよいが、範囲の外として区別する)。
- 対象: BomDD の commit `4cf6304`(r1 の処置 commit。製造 commit は `fab10e1`)。起票 commit は `c41838a`。開始時と終了時に `git rev-parse HEAD` を報告に写す(一致しなければ UNMEASURABLE)。
- してはいけないこと(観測できる形で): ファイルの作成・変更・削除 0・commit 0・ビルドしない・self-conformance などの検査器を実行しない・外部 API を呼ばない・ViewTube / ViewPrism2 のリポを読まない(写しを使う)。
- 読んでよいもの: BomDD のリポ(作業ディレクトリ)全体。特に `bomdd/60-change-order-eco-103.md`・`bomdd/60-change-register.yaml`(ECO-103 の項)・`method/templates/product-profile/change-management.md`・`method/templates/product-profile/skills/eco-fix.md`・`method/templates/product-profile/operator-layer.md`・`method/tools/bomdd-init.py`(配置の確認)・`method/bomdd-playbook-v1.md`(§3 の高リスク検査治具の項・§9)・`method/control-plan.md`・`bomdd/60-change-order-eco-077.md`・`bomdd/60-change-order-eco-079.md`・`bomdd/70-equipment.yaml`・`method/improvements.md`(2026-10-10 ECO-103 の節)・`bomdd/reports/eco-103-r8-independent-review/`(測定の記録と写し)。
- **報告の正本経路**: 報告ファイルを自分で書かない。最終メッセージ全文を CLI が保存する。1 行目(任意の `[INFORM / COMPLETE]` の次の最初の非空行)は行頭から `ACCEPT` / `REJECT` / `UNMEASURABLE <理由>`。
- 語の注意: 報告では、環境やツールの制約に触れるときは「実行環境の制約」のような中立の語を使う。

## 対象の変更(`git diff c41838a..4cf6304`)

1. キット `change-management.md` §2: R7 の直後に R8 の項(10 行)。
2. キット `skills/eco-fix.md`: 手順 3.6(5 行)と frontmatter の description(1 行の変更)。
3. キット `operator-layer.md:109`: 委ね先を R8 と名指し(1 行の変更)。
4. order §4・§5(製造と受入の実測)・`accept103.sh`・`accept-output.txt`。

## r1 の所見の処置の確認(最初に行う)

- r1 の報告= `independent-inspection-r1.md`、処置の記録= order §6.1。
- IA-01: 「両製品が同じ規則(保護パスに触れる変更)を置いた」の類の文が、改訂後の improvements.md・register・キット change-management R8・order に残っていないか(`同じ規則` の grep と実読)。直した文が写し(`viewtube-r8.txt`・`viewprism2-r8.txt`)の範囲に収まっているか。凍結した order §1 の訂正に注記があり、要求の内容が変わっていないか。
- IA-02: R8・eco-fix 3.6・order §1 が「文書のみの変更、または機械的な 1 行の変更」に揃っているか。
- 各所見を CLOSED / OPEN で報告する。

## 検査項目(各項目に PASS / FAIL と根拠。FAIL は blocking か non-blocking かを書く)

1. **範囲**: `git diff --stat c41838a..4cf6304` が register の ECO-103 の `allowed_paths` の中だけか。change-management.md の hunk が §2 の R7 の後の 1 か所だけで、R1〜R7・§0・§1・§3〜§5(ECO-079 の受入証拠レイヤーの段落を含む)に差分が無いか。operator-layer.md の差分が :109 の 1 行だけで、§4 に差分が無いか。eco-fix.md の差分が description と 3.6 だけか。
2. **V1・V2 の句**: order §3 の V1 の 7 句が R8 の項の中に、V2 の 3 句が 3.6 の中にあること(1 句ずつ grep)。eco-fix.md の frontmatter が YAML として読めること(`python -c "import yaml"` で読み込みを確かめてよい — 検査器の実行ではなく読み込みの確認)。
3. **記録との一致(境界探索の主眼)**: order §0(0.1〜0.5)の各事実を、`measurements.txt` と写し(`viewtube-r8.txt`・`viewprism2-r8.txt`)と BomDD の該当ファイルで 1 件ずつ突き合わせる。写しの sha256 を自分で計算し、`measurements.txt` の値と一致するかを報告に写す。記録に無い主張・記録より強い主張(効果の断定・一般化・「すべての製品で」)が order・register・改訂後の 3 ファイル・improvements.md の節に無いか。特に「2 製品が別々に同じ規則を置いた」が写しで支えられる範囲を超えていないか。
4. **既存の規則との整合**: 改訂後の R8・3.6・:109 が、operator-layer §4(不成立の 4 条件)・§5、change-management の R4(人の関門は 2 つ)・R3・R5・R7、playbook §3 の高リスク検査治具の項、playbook §9(自己査定の限界と明記の規則)、`method/control-plan.md:123-125`(独立検査は golden を置き換えない)、ECO-077 の採らないもの、ECO-079 の段落と矛盾しないか。特に: 「設備の独立でない見直しを `inspector` に書かない」が §4・§5 と整合するか / 「R8 対象外」の宣言の扱いが自己付与の限界として正直に書かれているか / 文脈の独立の定義と §4 の独立の定義が読み手に区別できるか。
5. **配布の健全性**: `bomdd-init.py` が change-management.md と operator-layer.md を製品リポの同じ場所に置き、R8 の中の `operator-layer.md` §4 への参照が配布先で解決するか。新しい `{{…}}` のプレースホルダや、配布先に存在しないパスへの参照を足していないか。
6. **言い回し**: 「文脈の独立」「設備の独立」「R8 対象外」が日本語として一意に読めるか。R8 の項と 3.6 で、範囲(保護パス `src/`・`test/`)・時点(golden の前 / 受入の依頼の前)・処置(R5 / R3)の書き方が食い違っていないか。

## 報告の様式(最終メッセージ全文)

```
[INFORM / COMPLETE]

ACCEPT            ← または REJECT / UNMEASURABLE <理由>

- inspector: EQ-002 / Codex CLI / <model>
- HEAD at start / at end: <sha> / <sha>
- commit: 0 / ファイル変更: 0
- 写しの sha256 の照合: 一致 / 不一致(ファイルごと)

## 項目ごとの判定
| # | 項目 | 判定 | 根拠(file:line・コマンドと出力の要点) |

## 所見(IA-01, IA-02, …)
- 各所見に blocking / non-blocking・該当箇所・何が記録と違うか / 何と矛盾するか

## 検査しなかったこと(限界)
```
