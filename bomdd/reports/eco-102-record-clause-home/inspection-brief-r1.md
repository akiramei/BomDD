# 独立検査ブリーフ r1 — BomDD ECO-102(「記録」の置き場の決定・検査官= EQ-002)

- 役割: **inspector(検査官)**・EQ-002(Codex CLI / gpt-5.6-sol)。責任= 製造物(playbook §4.5 ④・32/33 テンプレ)と order の事実の主張を、記録と突き合わせて判定すること。境界探索(範囲の外れ・記録より強い主張・既存の節との矛盾)を主な仕事とする。
- 対象: BomDD の commit `MFG_SHA`(製造 commit)。開始時と終了時に `git rev-parse HEAD` を報告に写す(一致しなければ UNMEASURABLE)。
- 禁止(観測可能): ファイルの作成・変更・削除 0・commit 0・ビルド・検査器の実行(self-conformance 等)をしない・外部 API を呼ばない・ViewTube / ViewPrism2 のリポを読まない(読めない。写しを使う)。
- 読んでよいもの: BomDD のリポ(作業ディレクトリ)全体。特に `bomdd/60-change-order-eco-102.md`・`bomdd/60-change-register.yaml`(ECO-102 の項)・`method/bomdd-playbook-v1.md` §4.5・`method/templates/32-mbom.yaml`・`method/templates/33-control-plan.yaml`・`method/improvements.md`(2026-10-07 ECO-102 の節と OBS-20261005-03)・`bomdd/60-change-order-eco-100.md`・`bomdd/reports/eco-102-record-clause-home/`(測定の記録と写し)。
- **報告の正本経路**: 報告ファイルを自分で書かない。最終メッセージ全文をハーネスが保存する。1 行目(任意の `[INFORM / COMPLETE]` の次の最初の非空行)は行頭から `ACCEPT` / `REJECT` / `UNMEASURABLE <理由>`。

## 対象の変更(製造 commit の diff・起票 commit `FILE_SHA` からの窓)

1. playbook §4.5 の④の文(置き場の決定)と、同じ項の「未測定」の列挙の 1 句。
2. `method/templates/32-mbom.yaml` の `invariants` のコメント(2 行)。
3. `method/templates/33-control-plan.yaml` の検査行に `known_limits: []` の欄とコメント(3 行)。
4. order §4・§5(製造と受入の実測)。

## 検査項目(各項目に PASS / FAIL と根拠。FAIL は blocking か non-blocking かを書く)

1. **範囲**: `git diff --stat FILE_SHA..MFG_SHA` が order §2 の影響なし予測(allowed_paths)の中だけか。playbook の hunk が §4.5 の 1 項の中だけで、§4.4・§9・§13 の項に差分が無いか(`git diff -U0 FILE_SHA..MFG_SHA -- method/bomdd-playbook-v1.md` の hunk の位置で判定)。
2. **V1 の句**: order §3 V1 の 6 つの句が §4.5 の項に各 1 件あり、`置き場は**未決**` が無いこと(grep で 1 句ずつ)。項が candidate の表示のままであること。
3. **記録との一致(境界探索の主眼)**: order §0.2 と §4.5 ④の根拠の各数値・各事実を、`bomdd/reports/eco-102-record-clause-home/measurements.txt`(測定の記録)と写し(`viewtube-32-mbom-invariant-lines.txt`・`viewtube-33-known-limits-lines.txt`)で 1 件ずつ突き合わせる。写しの sha256 を自分で計算し、measurements.txt の値と一致するかを報告に写す。記録に無い主張・記録より強い主張(効果の断定・一般化・「他の製品でも」)が本文・playbook・テンプレのコメント・improvements.md の節に無いか。
4. **既存の本文との整合**: 改訂後の④が、§13(転写値禁止・記録の経済)、§4.4(検査行と裁定層の結線・`invariant_refs`)、§9、ECO-086 / 098 / 100 の他の candidate の項、31 / 32 / 33 / 50 テンプレの他のコメントと矛盾しないか。特に: 「未検査の注記を 33 の known_limits へ」が §4.4 の結線の規則と衝突しないか / 「正本は変更記録」が §13 と同じ形か / 50 テンプレ(As-Built)の `test_evidence_refs` との役割の重なりが無いか。
5. **テンプレの健全性**: 32・33 テンプレが PyYAML `safe_load` で読めること(検査官は `python -c "import yaml,sys; yaml.safe_load(open(p,encoding='utf-8'))"` を 2 本に対して実行してよい— これは検査器の実行ではなく読み込みの確認)。33 の新しい欄が検査行(`characteristics` の要素)の中にあり、表示パリティ行の例には無いことの妥当性。変更行がコメントと空リストの欄だけであること。
6. **言い回し**: 局所名「M-BOM の記録句」が §4.5 の中で定義され、ECO-100 IA-01 の指摘(他の節の「記録」との同語)に答えているか。日本語として一意に読めるか。

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
