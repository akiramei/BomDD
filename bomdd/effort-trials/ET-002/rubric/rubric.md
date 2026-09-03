# ET-002 rubric(封印 — run 開始前に確定・以後不変)

- 課題: self-conformance.py の全ゲートについて「走査母集団が 0 件のとき無音で PASS する(SILENT)」か「OK」かを判定
  (型④・空集合の合格化の横断掃引 — ECO-054 が未実施で閉じた仕事。§13 第 5 様態)。
- oracle の来歴: 製造者(claude-fable-5-1・self-reported)が各ゲートの `check()` 条件と PASS メッセージを読解し、
  要点(C3 の verified 0 件・C12 のリンク 0 件)は関数を空母集団で**実行**して確認した(2026-09-04)。oracle は
  **人の読解**であり実装そのものではない — 腕の不一致で oracle の誤りが判明した場合は評価 receipt を書き換えず、
  REPORT に oracle 欠陥として記録し、訂正 rubric は次 trial で使う。
- 合否: 採点対象 19 ゲートすべてで判定が期待と一致したとき **pass**、1 件でも不一致・欠落・形式違反があれば **fail**。
- 採点除外(出力は求めるが採点しない — 定義の曖昧さが effort でなく分類の問題になるため): **C4**(複合ゲート: 漏洩走査・
  生成 YAML 走査・参照集合が混在)/ **C8**(リポ直下 entry に対する不在検査 — 構造的に空にならない集合)。
- 症状語彙: `miss-silent`(SILENT を OK と判定)/ `false-silent`(OK を SILENT と判定)/ `missing-verdict` /
  `format-violation`(相反する判定行)。

| ゲート | 期待 | 根拠(oracle) |
|---|---|---|
| C1 | OK | `bool(files) and not bad` — YAML 0 件は FAIL |
| C2 | OK | `bool(files) and not bad` — JSON 0 件は FAIL |
| C3 | SILENT | verified entry 0 件 → problems 空 → PASS「(全 verified 適合)」・件数表示なし(実行で確認) |
| C5a | OK | 固定プローブ(存在しないリポへの exit 2)— 走査母集団なし |
| C5b | OK | 同上 |
| C6a | OK | 固定 fixture(理由なし rejected)— 走査母集団なし |
| C6b | OK | 固定 fixture(根拠つき rejected)— 走査母集団なし |
| C7 | OK | claims 0 件は `all([])` で PASS するが、メッセージに `[]` が表示される(空リスト表示) |
| C9 | OK | manifest suites 空 → FAIL / 空結果 → FAIL(ECO-054)/ 母集団突合は件数表示 |
| C10 | OK | families 空なら陽性対照(乖離検出)が反応せず FAIL |
| C11 | OK | 固定の scaffold+IQ/OQ 実行 — 走査母集団なし |
| C11b | OK | 同上(非既定構成) |
| C12 | OK | リンク 0 件でも「相対リンク 0 件すべて実在」と件数表示(実行で確認) |
| C13 | OK | `bool(repo_files) and total_a > 0`・陽性対照 — 0 件は FAIL |
| C14 | OK | 固定 7 腕の対照実測 — 走査母集団なし |
| C15 | OK | corpus 0 件 → FAIL / deprecated 宣言 0 件は「適用対象なし — 明示記録」 |
| C16 | OK | 対象 0 件でも「cutoff 以降 0 件」と件数表示(ガードは無い — 観測として REPORT へ) |
| C17 | OK | `n == 0` → FAIL / fixture 0 → FAIL(ECO-051) |
| C18 | OK | 固定の設定検査(hooksPath・hook 実在)— 走査母集団なし |
