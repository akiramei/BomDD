[INFORM / COMPLETE]

ACCEPT

- range: 境界探索
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象 revision: e7d563b11587e0b041d6868df0199e1f0c21366f
- commit: 0
- 外部 API: 呼出しなし
- 読んだファイル一覧:
  - `bomdd/60-change-order-eco-091.md` §0・§1・§3・§4
  - `bomdd/60-change-register.yaml` の ECO-091 エントリ・`allowed_paths`
  - `method/tools/self-conformance.py` の対象差分および C9 関連実装
  - `loops/expected-results.yaml`

開始時 `git status --short`: 空 / 終了時 `git status --short`: 空

## 判定概要

| 条件 | 判定 | 観測 |
|---|---|---|
| V1 | PASS | 指定の直接較正コマンドは `[]`。17 腕の較正成立。fast tier の `python method/tools/self-conformance.py` も開始したが、6 分以上標準出力がなく終了を観測できなかったため中断した。V1 が指定する代替較正は成立した。 |
| V2 | PASS | 正常対照 PASS。予期しない Failed 行は `_c9_suite_verdict` が FAIL。Aborted・Error・exit 2 は FAIL。Failed・Error・exit 1・全行 Passed は FAIL。 |
| V3 | 測れなかった | 本 round では `--dotnet` を省略。 |
| V4 | PASS | `git diff --name-only 069e0d5 e7d563b...` の15パスは、register の ECO-091/092/093 共通 `allowed_paths` の内側。範囲外パス 0。 |

## 境界探索の表

| 入力クラス | 入力 | 期待 | 実測 | 所見 |
|---|---|---|---|---|
| summary 語彙 | `Completed`・exit 0・Passed 行 | PASS | PASS (`ok`) | 正常対照 |
| summary 語彙 | `Failed`・exit 1・Failed 行 | PASS | PASS (`ok`) | 期待赤を許容 |
| summary 語彙 | `Aborted` / `Error` / `Inconclusive` / `Novel` | FAIL | 全て FAIL | 許可語彙以外を fail-closed |
| summary 不完全 | 要素あり・`outcome` 属性なし | FAIL | FAIL | `None` として拒否 |
| summary 不在 | `ResultSummary` 要素なし | FAIL | FAIL | `None` として拒否 |
| V2 正常 | Completed・exit 0・全行 Passed | PASS | PASS | 正常対照 |
| V2 異常行 | Failed・exit 1・予期しない Failed 行 | FAIL | 行単位 FAIL、実行単位 PASS、AND は FAIL | 結線で拒否 |
| V2 中断 | Aborted・exit 2・全行 Passed・Error | FAIL | FAIL | summary 語彙で拒否 |
| V2 実行エラー | Failed・exit 1・全行 Passed・Error | FAIL | FAIL | 「不合格行なしの Error」で拒否 |
| RunInfo | Error 1件・不合格行なし | FAIL | FAIL | 規則 (c) |
| RunInfo | Error 1件・不合格行あり | PASS可能 | PASS | §4 の修正规則どおり |
| RunInfo | Warning / Info・不合格行なし/あり | 判定語にしない | Error リストに入らず、他条件が整合すれば PASS | 意図どおり |
| RunInfo | Error 複数・不合格行なし | FAIL | FAIL、件数 2 を理由に表示 | 正常 |
| RunInfo | Error 複数・不合格行あり | PASS可能 | PASS | 宣言済み限界 |
| RunInfo | Error・`Text` 子要素なし | 不合格行なしなら FAIL | `"(Text なし)"` として抽出し FAIL | 測定可能な理由を保持 |
| 終了コード×行 | `(0, 不合格あり)` | FAIL | FAIL | 不整合を検出 |
| 終了コード×行 | `(1, 不合格なし)` / `(2, 不合格なし)` | FAIL | FAIL | 行の外の異常を検出 |
| 終了コード×行 | `(0, 不合格なし)` | PASS | PASS | 正常 |
| 終了コード×行 | `(1, 不合格あり)` | PASS可能 | PASS | 期待赤対応 |
| 終了コード×行 | `(-1, 不合格なし)` | FAIL | FAIL | 非0として処理 |
| 終了コード×行 | `(-1, 不合格あり)` | 規則上 PASS可能 | PASS | 規則 (d) は非0の値を区別しない |
| 不合格行の定義 | `Passed` | false | false | 両経路一致 |
| 不合格行の定義 | `Failed` / `NotExecuted` / `Inconclusive` / `Timeout` | true | 全て true | `c9_dotnet` と `_c9_suite_verdict` は共に `outcome != "Passed"` |
| 宣言済み限界 | 期待赤1行＋Passed 1行、総数一致、Failed、exit 1、期待失敗 Error＋ホスト異常 Error | §4 の限界として PASS可能 | 行単位 PASS・実行単位 PASS・AND PASS | 合成可能。IA-01参照 |
| 結線 | 実行単位 FAIL | check 行も FAIL、理由を表示 | `check("C9", ok_s and ok_r, ...)` と `実行単位の異常(exit N): ...` を確認 | 正常 |
| TRX 不在 | `out.trx` が生成されない | 既存どおり FAIL | `check("C9", False, "...trx が生成されない...")` | ECO-091 による退行なし |
| meta-failure | `_c9_selftest()` 自体が異常を返す | C9 を停止して FAIL | `計器較正不成立` を出して return | 自己検証失敗を合格化しない |
| 未検枝 | 未知 summary、属性なし、Warning/Info、複数/Textなし Error、負の exit | 安全側または規則どおり | 上表どおり | 恒久 selftest の個別腕はないが、汎用条件を直接実測 |
| 存在 vs 完全性 | summary 要素あり・属性なし | FAIL | FAIL | 診断文のみ IA-02 |
| 副経路 | 行単位 PASS・実行単位 FAIL | 最終 FAIL | AND 結線をコード読解で確認 | 抜け道なし |

## 所見

- IA-01 — non-blocking  
  宣言済み限界の実例を構成できた。

  - 再現入力: `total=2`、期待赤 `ExpectedRed` 1件、実行結果は ExpectedRed=Failed・B=Passed、`ResultSummary outcome="Failed"`、exit 1。`RunInfo Error` に期待失敗メッセージと `"host crashed after row write"` を同居させる。
  - 期待: §4 の宣言どおり、現規則では異常を識別できず PASS になりうる。
  - 実測: `_c9_suite_verdict=True`、`_c9_run_verdict=True`、AND=True。
  - 帰属: 上流＝order §4 の規則。
  - blocking 判定: non-blocking。本入力は宣言済み限界そのもの。xUnit が失敗メッセージを RunInfo Error に書く根拠は §4 の実測にあるが、失敗行とホスト異常が同居し、かつ VSTest が全行・`outcome=Failed` の完成 TRX を書き切る実例は今回未観測。単独では REJECT 条件を満たさない。

- IA-02 — non-blocking  
  `ResultSummary` 要素は存在するが `outcome` 属性がない場合、抽出結果は要素不在と同じ `None` になり、理由が「ResultSummary 不在」となる。

  - 期待: FAIL。
  - 実測: FAIL。
  - 帰属: 製造物の診断文。
  - blocking 判定: non-blocking。判定は安全側であり、誤受入・誤拒否ではない。

- 自己検証4類型の査定:
  - meta-failure: selftest 非成立時に C9 が停止・FAILする。
  - 未検枝: 恒久腕にない語彙・RunInfo・終了コード境界を今回直接測定し、誤受入なし。
  - 存在 vs 完全性: 属性欠落も FAIL。ただし IA-02 の診断精度のみ残る。
  - 副経路: 行単位と実行単位は `ok_s and ok_r`。TRX 不在経路も既存どおり FAIL。
  - 結論: 製造者の §1・§3・§4 の主張を覆す穴は認めない。

## 範囲外の観察

- ECO-092 の witness 関数群・C18 差分は同一ファイルに同居するが、判定対象に含めなかった。
- `python method/tools/self-conformance.py` は6分以上出力・終了を観測できず中断した。リポ内変更は発生せず、終了時の作業ツリーは clean。
- GitHub、CIその他の外部 API は呼び出していない。