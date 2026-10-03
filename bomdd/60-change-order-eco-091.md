# Change Order — ECO-091(C9 が実行単位の異常を合格にする — TRX の行単位判定が中断・run-level Error・終了状態の不整合を見ない偽陰性の是正)

> 裁定: user 2026-10-03 DECIDE「2:A」(外部レビュー 2026-10-02 論点 8 — 検査器の偽陰性 2 件と文書矛盾 2 件を今すぐ起票。前例= 2026-09-29 裁定「検査器の偽陰性は実害待ちにしない」)。
> 出典: [外部レビュー 論点 8](reports/external-review-20261002/review.md) / 照合= [verification.md](reports/external-review-20261002/verification.md)。
> 目的(ECO-085 の型): 「不合格製品を防ぐ」より **C9 PASS に、実行が完了し報告と終了状態が整合しているという証拠能力を持たせる**。受入は「何を証拠として引用できるか」で測る。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-001
- inspector: EQ-002
  判定に関与する計器(C9 の FAIL 経路の追加)の変更のため、異系統の独立検査を併用する(前例= ECO-065 §3「判定に関与するなら異系統必須」・ECO-085 製造裁定 2:A)。
  range= 境界探索(r1)→ 是正確認+回帰(r2 以降)。read-only sandbox・セッション分離・外部 API 呼出しなし。実行環境の差(OS temp 不能・exit の丸め)はブリーフに明記。

## 0. 実測(起票根拠・2026-10-03)

- **機序**(`method/tools/self-conformance.py` の実読): `c9_dotnet()` は `dotnet test … --logger trx` を走らせ、`out.trx` が存在すれば `UnitTestResult` 行だけを読んで
  `_c9_suite_verdict(suite, results, messages)` に渡す。`p.returncode` を見るのは **trx が生成されないときだけ**(L1169)。`ResultSummary`(outcome= Completed / Failed / Aborted …)と
  `RunInfos/RunInfo`(outcome= Error の実行基盤エラー)への参照は **0 件**(grep)。
- **帰結**: 期待件数の行が揃っていれば、実行が中断(Aborted)していても、run-level Error が明示されていても、終了コードが行の内容と矛盾していても PASS になる。
  レビューは未変更の validator に合成 subprocess/TRX 入力を与え、次の 4 腕を実測した(当方は機序を読解で確認・合成腕は本 ECO の陽性対照として恒久化する):

  | 入力条件 | 現行 C9 |
  |---|---|
  | Passed 行・Completed・終了 0 | PASS(正常対照) |
  | 予期しない Failed 行・終了 1 | FAIL(異常対照) |
  | Passed 行・Aborted・run-level Error・終了 2 | **PASS(誤受入)** |
  | Passed 行・Failed・run-level Error・終了 1 | **PASS(誤受入)** |

- **既存の腕では補えない**: 件数(`total_ok`)・空出力(ECO-054 型④)・expected-failure 集合・identity 突合・`_c9_selftest` の 8 腕は、いずれも**行の内側**を測る。実行単位の異常は行の外にある。
- **制約**: `loops/loop-02-export` は意図的な赤 4 件を保存する期待赤 suite であり、`dotnet test` は**正当に非 0 で終了する**。「終了 0 必須」の規則は正しい suite を赤にする。
- **露出**: C9 は CI の windows job(`--dotnet`)で毎 push 走る= 本リポの最終層の計器。ローカル fast tier には入らない(witness の被覆外・ECO-046 限界 (2))。
- **自然発生例**: 未観測(合成入力のみ・N=1 ずつ)。self-conformance 全体の PASS に影響していない。

## 1. 変更要求(製造対象・凍結)

1. **実行単位の判定を純関数に切り出す** `_c9_run_verdict(returncode, summary_outcome, run_errors, has_failed_rows) -> (ok, why)`:
   - (a) `summary_outcome` が None(`ResultSummary` 不在)→ FAIL「測定不能」(型④: 不在は合格ではない)。
   - (b) `summary_outcome` が `Completed` / `Failed` 以外(Aborted・Error・未知の語彙)→ FAIL(未知の語彙も fail-closed)。
   - (c) `run_errors`(`RunInfo outcome="Error"` の Text)が 1 件以上 → FAIL。`Warning` は通す(xunit は警告を出しうる・判定語でない)。
   - (d) 終了状態と報告の整合: `returncode == 0` なのに不合格行がある → FAIL / `returncode != 0` なのに不合格行が無い → FAIL(行の外の異常)。
     期待赤 suite は「不合格行あり+非 0」で (d) を通り、行単位の判定(既存)が期待集合と突合する — **一律の終了 0 要求にはしない**。
2. **TRX の読み取りを関数化** `_c9_parse_trx(root) -> (results, messages, summary_outcome, run_errors)`(既存の行の読み取りを移し、`ResultSummary@outcome` と `RunInfos/RunInfo[@outcome='Error']/Text` を追加)。
3. **`c9_dotnet` の結線**: suite ごとに (1) を先に判定し、FAIL なら理由を check 行へ出す。行単位の判定(`_c9_suite_verdict`)は**不変**。最終判定= 実行単位 AND 行単位。
4. **陽性対照**(`_c9_selftest` に追加・毎回実測): (1) に対する対の腕 — 正常完了(0・Completed・[]・不合格なし)= PASS / 期待どおりの失敗(1・Failed・[]・不合格あり)= PASS /
   行出力後の中断(2・Aborted・[err]・不合格なし)= FAIL / 実行エラー+終了 1+全行合格(1・Failed・[err]・不合格なし)= FAIL / 終了 0 なのに不合格行(0・Failed・[]・不合格あり)= FAIL /
   `ResultSummary` 不在(0・None・[]・不合格なし)= FAIL。加えて (2) に対する合成 TRX 文書 2 腕(正常 / Aborted+RunInfo Error)で抽出を実測する。
5. **採らない**: 一律の終了 0 要求(期待赤 suite を赤にする)/ `Counters`(total/executed)との突合(既存の `total_ok` が行数を見ている — 列挙の追加)/
   MTP(Microsoft.Testing.Platform)の終了コード体系への対応(本リポの loops は VSTest `--logger trx` のみ・(d) は体系に依存しない)/ 実 .NET のクラッシュ再現(合成の境界で測る— レビューと同じ立場)/
   行単位の判定の変更。

## 2. 影響なし予測(製造前・凍結)

diff= `method/tools/self-conformance.py`(C9 の関数 2 本の追加・`c9_dotnet` の結線・`_c9_selftest` の腕追加)+台帳系(order・register・improvements.md・reports)のみ。
C1〜C8・C10〜C18 の判定式とメッセージは**不変**。C9 の既存 4 suite は現行 CI で全て正常完了(Completed / Failed・RunInfo Error なし)のため、是正後も判定不変(V3 で CI 実測)。
templates・hooks・.github・schemas は diff 0。製品リポへ非波及(self-conformance は本リポ専用)。

## 3. 受入条件(製造前に凍結・二部形・ECO-080)

- V1(条件): `_c9_selftest` の追加腕(実行単位 6 腕+TRX 抽出 2 腕)が本番で毎回実測され、C9 の較正行に腕数が出ること — 検査法: `python method/tools/self-conformance.py --dotnet` の `[C9] PASS 計器較正` 行。
- V2(条件): レビューの 4 腕(§0 表)を本 ECO の純関数に与えたとき、正常対照= PASS・異常対照= FAIL・誤受入 2 腕= **FAIL** になること — 検査法: 独立検査官が関数を直接呼ぶ(ブリーフに検体を渡す)。
- V3(条件): 既存 4 suite の判定が不変(loop-02-export の期待赤 4 件が PASS のまま・他 3 suite PASS)であること — 検査法: CI windows job のログ(`[C9] PASS loops/…`)。
- V4(条件): diff が allowed_paths のみ・C1〜C18 の PASS 行が不変(C9 の較正行の文言差のみ)であること — 検査法: `git diff --name-only baseline..head`・PASS 行数の前後比較。
- V5(条件): self-conformance 全 PASS(exit 0 観測後に commit)・CI success であること。
- V6(条件): 異系統の独立検査(EQ-002)が ACCEPT であること(r1 は境界探索)。
- V7(条件): 較正 receipt(trigger ①③・receipt_author_role= producer)があること。

## /preflight receipt(起動経路: **自発** — 既裁定の適用実装の開始時〔bug-fix 類〕)

- 分類= 既裁定の適用実装(user 2026-10-03「2:A」)。baseline `069e0d5`= **confirmed**(HEAD・作業木 clean・push 済み・レビューの対象コミットと同一)/ 次番 091= **confirmed**(register 末尾= 090)/
  機序= **confirmed**(L1164〜1181 実読・`ResultSummary`/`RunInfos` 参照 0 件を grep)/ 期待赤 suite の存在= **confirmed**(loops/expected-results.yaml loop-02-export 4 件)/
  同一ファイルへの進行中 ECO= **confirmed**(なし。ECO-092 は同時起票だが対象関数が別〔witness〕— 窓は同じファイルを共有するため allowed_paths を双方に置き、受入は ECO ごとに測る)/
  dotnet SDK の手元実行= **unknown**(ローカルで `--dotnet` が走るかは製造時に確認・走らなければ V3 は CI で測る)。
- 開始判定: **PROCEED_WITH_LIMITS**(限界= V3 の実測場所が CI になりうる)・override 0。

## /converge receipt(起動経路: 自発 — 実行単位の判定規則の設計)

- **判定: 収束**(round 軌跡: 5→2→0)。
- DoD: ✔ 中断・run-level Error・終了状態と報告の不整合を FAIL にする / ✔ 期待赤 suite(非 0 終了が正当)を赤にしない / ✔ 対の陽性対照(正常・期待赤・中断・実行エラー)を持つ /
  ✔ 行単位の判定は不変 / ✔ 判定は純関数で selftest できる / ✔ 未知の語彙・不在は fail-closed。
- round 1(新規 5 件): ①一律の終了 0 要求は loop-02-export を赤にする → 整合規則 (d) へ ②`ResultSummary@outcome` の語彙(Completed / Failed / Aborted / Error / …)— 受理集合を 2 語に限定し、
  それ以外と未知は FAIL ③`ResultSummary` 不在は測定不能 → FAIL(型④)④`RunInfo` は Error のみ判定語にし Warning は通す ⑤終了コードの整合は「0 ⇔ 不合格行なし」の双方向。
- round 2(新規 2 件): ⑥`Counters`(total / executed)の突合は要るか → 既存 `total_ok` が行数を見ており、スキップは行数差で既に落ちる → 採らない ⑦MTP の終了コード体系(2= 失敗・8= テスト 0)は
  VSTest と異なる → (d) は「0 かどうか」と行の有無の整合だけを見るため体系に依存しない・本リポは VSTest のみ → 範囲外を宣言。round 3: 0 件。
- 検証した主張: 参照 0 件(grep)/ 期待赤 suite の存在と非 0 終了(expected-results.yaml・CI の慣行)/ CI で C9 が走る job(`.github/workflows` 実読)/ TRX の要素名(`ResultSummary`・`RunInfos/RunInfo`・VSTest スキーマ)。
- 敵対自問: 「(d) は dotnet の終了コードの意味に依存していないか」— 依存は「0= 成功」の 1 点のみで、VSTest / MTP とも共通。「Warning を通すのは fail-open では」— Warning は実行の完了を否定しない・
  Error と Aborted は否定する — 否定する側だけを判定語にする(過剰検出は出口があるが、ここでは本物の赤を生まない側を選ぶ)。
- 未収束事項: なし。

## 4. 製造(2026-10-03・製造者 EQ-001)

- 製造物(`method/tools/self-conformance.py`): `_c9_run_verdict(returncode, summary_outcome, run_errors, has_failed_rows)`(純関数)/ `_c9_parse_trx(root)`(行・Message・`ResultSummary@outcome`・`RunInfo[@outcome='Error']/Text` の抽出)/
  `c9_dotnet` の結線(行単位 AND 実行単位・FAIL 時は `実行単位の異常(exit N): <理由>` を check 行へ・PASS 時は `実行単位 ok(outcome=…・exit N)`)/ `_c9_selftest` に実行単位 7 腕+TRX 抽出 2 腕(較正行= 17 腕)。
  行単位の判定 `_c9_suite_verdict` は不変。
- **製造中の発見(規則 (c) の修正 — §1 は凍結のまま・逸脱は本節に記録)**: ローカルの `--dotnet` 1 回目で **loop-02-export(期待赤 suite)が FAIL**(`実行単位の異常(exit 1): run-level Error 4 件: '[xUnit.net 00:00:00.68] MoviePad.ExportSlice.Tests.ExportSliceTests.B10_Filt…'`)。
  機序= xUnit の VSTest アダプタは**失敗テストのメッセージ**を `RunInfo outcome="Error"` として TRX に書く(期待赤 4 件= RunInfo Error 4 件)。起票時の (c)「Error が 1 件以上 → FAIL」は、
  §1-5 で「採らない」と宣言した**正当な suite を赤にする側の誤り**を、別の経路で再導入していた。converge receipt の DoD「✔ 期待赤 suite を赤にしない」は合成腕でしか確かめておらず、
  実 TRX を 1 本も読んでいなかった(DoD の ✔ が過大 — ECO-085 クローズ追記①と同型)。是正= (c) を「**不合格行が無いのに** RunInfo Error がある → FAIL」に狭め、不合格行がある suite の Error は
  付随メッセージとみなす。較正に「期待赤 suite の実形(終了 1・Failed・RunInfo Error 4・不合格行あり)= PASS」の正腕を追加。**検出力の限界(較正 receipt へ)**: 不合格行と同居する実行基盤の
  エラーは outcome=Aborted・行数不一致(既存 `total_ok`)・終了状態の不整合でしか捕まらない。レビューの 4 腕はいずれも「不合格行なし」側のため判定は不変(FAIL のまま)。
- 製造者ローカルで `--dotnet` が走ること= 実測(preflight の unknown を解消・V3 はローカルと CI の両方で測れる)。

## 5. 受入の実測(2026-10-03・製造者・独立検査 r1 の前)

- **V1**= PASS(観測: 2 回目の全検査ログ `[C9] PASS 計器較正(陽性対照 17 腕: 行単位 8 … +実行単位 7 … +TRX 抽出 2〔ECO-091〕)`。1 回目のログは規則 (c) 修正前・16 腕)。
- **V2**= PASS(製造者の検体 `c9_arms.py`: 正常対照= 行単位 PASS・実行単位 PASS / 異常対照= 行単位 FAIL / 中断(Aborted・Error・exit 2)= 実行単位 FAIL「outcome='Aborted'」/
  実行エラー(Failed・Error・exit 1・全行 Passed)= 実行単位 FAIL「不合格行が無いのに run-level Error 1 件」。独立検査官が自前の検体で再測する)。
- **V3**= PASS(観測: 2 回目の全検査ログ — 4 suite とも `[C9] PASS`・loop-02-export は `26/30 合格・期待赤 4 件一致=True・identity 突合 4 件・signature 補助 4 件・実行単位 ok(outcome=Failed・exit 1)`・
  他 3 suite は `実行単位 ok(outcome=Completed・exit 0)`。**1 回目(修正前)は loop-02-export FAIL・exit 1**= 誤拒否の実測。2 回目は `self-conformance passed`・exit 0・check 行 28〔fast 21+C18 較正 1+C9 6〕)。
- **V4**〜**V7**= §6。

## 6. 独立検査(異系統・Codex EQ-002・入口 bomdd-run から `--report`/`--range` つきで起動)

### 6.1 r1(2026-10-03・range= 境界探索)— 報告: [independent-inspection-eco-091.md](reports/independent-inspection-eco-091.md)

- 起動: 製造 commit `e7d563b`(witness tree 222f53ac55ad・入口 `ADVANCE ECO-091 OK → next · launching`)→ `cell exit 0` → `report ACCEPT sha256:09110e9a4b2c (EQ-002)`・台帳 `range: 境界探索`。
  検査官の作業木: 開始・終了とも clean・commit 0・外部 API なし。
- 判定: **ACCEPT**(blocking 0・non-blocking 2)。V1 PASS(直接較正 `[]`・17 腕)/ V2 PASS(検査官自前の検体で 4 腕)/ V3 測れなかった(`--dotnet` 省略— 製造者ログと CI が担う)/ V4 PASS(15 パスが和集合の内)。
  境界探索 30 行: summary 語彙(Aborted / Error / Inconclusive / 未知 → FAIL)・属性なし・要素なし・RunInfo(Error×不合格行の有無・Warning/Info・複数・Text なし)・終了コード×行(負の値含む)・不合格行の定義(両経路とも `!= "Passed"`)・結線・TRX 不在経路・4 類型。誤受入 0・誤拒否 0。
- **IA-01(non-blocking・上流= §4 の宣言済み限界の実例)**: 期待赤 1 行+Passed 1 行・総数一致・Failed・exit 1・RunInfo Error に期待失敗と「host crashed」が同居 → 行単位 PASS・実行単位 PASS。
  検査官の判定= 実 VSTest がこの形の完成 TRX を書き切る実例は未観測のため単独では REJECT 条件を満たさない。受理側: 較正 receipt の「検出力の限界」に実例として引用する(是正しない — 文言で捕まえる手段が無く、
  行数・Aborted・終了状態が残る防御)。
- **IA-02(non-blocking・製造物の診断文)**: `ResultSummary` 要素はあるが `outcome` 属性が無い場合、要素不在と同じ「ResultSummary 不在」の理由になる(判定は FAIL で安全側)。
  **是正(同日)**: `_c9_parse_trx` は属性なしを `""` で返し、`_c9_run_verdict` は「ResultSummary に outcome 属性がない」と診断(FAIL 不変)。較正に TRX 抽出 3 腕目(属性なし)を追加(較正行= 18 腕)。
- 検査官の環境観測: fast tier の self-conformance は 6 分以上出力が無く中断(pwsh 経由の出力バッファ)。V1 は指定の代替較正で成立。ECO-092 のブリーフへ待ち時間の注記を追加。
- 次: r2(range= 是正確認+回帰: IA-02 の是正確認・V1/V2 の回帰)。playbook §3 の規則どおり ACCEPT は是正確認+回帰の round で確定する。

### 6.2 r2(2026-10-03・range= 是正確認+回帰・範囲限定)— 報告: [independent-inspection-eco-091-r2.md](reports/independent-inspection-eco-091-r2.md)

- 起動: commit `9b496fc`(witness tree 814d5b745531・入口 `ADVANCE ECO-091 OK → next · launching`)→ `cell exit 0` → `report REJECT sha256:947bb2a059e9 (EQ-002)`・台帳 `range: 是正確認+回帰`。作業木 clean・commit 0・外部 API なし。
- 判定: **REJECT IA-03**(blocking 1)。項目 1(IA-02 の是正確認)PASS / 2(V1・V2 の回帰)PASS / 3(境界表 8 行の抜き取り)PASS・r1 と同一 / **4(窓)FAIL**。
- **IA-03(blocking)— 帰属= 受理側のブリーフ**: 項目 4 を「`git diff e7d563b..REV -- self-conformance.py` が IA-02 の是正に限られること」と書いたが、同じファイルには **ECO-092 r1 IA-03 のコメント訂正 4 行**(C18 の限界宣言 (6)・commit e096369)が同居する。
  検査官はブリーフの文面どおり FAIL とした(正当)。製造物の欠陥ではない。窓を共有する姉妹 ECO の差分をブリーフの条件が除外していなかった(IA-02 と同型の、受理側の窓の扱いの不備・2 例目)。
- 是正= r3 のブリーフで項目 4 を「差分= IA-02 の是正(抽出・診断文・較正腕・較正行)+ECO-092 r1 IA-03 のコメント 4 行〔`_witness_tree` 等の関数本体に差分なし〕に限られること」と正しく定義し、範囲を項目 4 のみに限定する。

### 6.3 r3(2026-10-03・range= 是正確認+回帰・項目 4 のみ)— 報告: [independent-inspection-eco-091-r3.md](reports/independent-inspection-eco-091-r3.md)

- 起動: commit `e8a7ee6`(witness tree 7bda72ed711b・入口 `ADVANCE ECO-091 OK → next · launching`)→ `cell exit 0` → `report ACCEPT sha256:a995b1eb7189 (EQ-002)`。作業木 clean・commit 0・外部 API なし。
- 判定: **ACCEPT**(所見なし)。4'(a) 窓 21 パス全て和集合の内 / 4'(b) 対象ファイルの差分 5 hunk= ①IA-02 の是正 4 hunk+②ECO-092 IA-03 のコメント 4 行・関数本体にコード差分なし(`c9_dotnet` は較正行の文言のみ)/ 4'(c) 受理側の記録と一致。
- 独立検査の総括: r1 ACCEPT(境界探索・non-blocking 2)→ 是正 → r2 REJECT(受理側ブリーフの欠陥・製造物非改変)→ r3 ACCEPT(窓)。製造物に対する blocking 所見= **0**。受理側帰属= 1(ブリーフ)。

## 7. クローズ(2026-10-03・verified)

- **V4**= PASS(観測: 窓 `069e0d5` → `e8a7ee6`= 21 パス・全て和集合の内〔r3 4'(a)〕。PASS 行の差= C9 の較正行の文言と C18 の較正行 1 行(ECO-092)のみ・FAIL 0・他の check 行の文言は不変)。
- **V5**= PASS(観測: 製造 commit e7d563b CI 37102721323 success / 是正 5d90ba4 CI 37104338649 success / e096369 CI 37105504245 success / 窓末尾 e8a7ee6 CI 37106713044 success〔fast ubuntu・fast windows・dotnet= C9 4 suite 込み〕。
  各 commit は self-conformance exit 0 を観測してから作成)。
- **V6**= PASS(観測: 異系統の独立検査 r1 ACCEPT〔境界探索・non-blocking 2〕→ r2 REJECT〔受理側ブリーフの欠陥・製造物非改変〕→ r3 ACCEPT〔窓・項目 4 のみ〕。製造物に対する blocking 所見 0)。
- **V7**= 下の較正 receipt。diff 監査の窓: baseline `069e0d5` → head `e8a7ee6`(**窓閉鎖**・本クローズ commit は台帳系+r3 報告のみ)。register: `implemented → verified`。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格+③: 計器〔C9 の実行単位の判定〕の変更・receipt_author_role= producer・独立検査あり)

- 査定した主張と判定:
  1. 「C9 PASS は、実行が完了し(Completed / Failed)、不合格行で説明できない基盤エラーが無く、終了状態と報告が整合していることを含意する」— **observed / 適格**(純関数の対の腕 7+TRX 抽出 3・独立検査官の境界探索 30 行で誤受入 0)。
  2. 「期待赤 suite(loop-02-export)は赤にならない」— **observed / 適格**(ローカル `--dotnet` 2 回目と CI dotnet job で `実行単位 ok(outcome=Failed・exit 1)`。1 回目の FAIL が規則 (c) の誤りを捕捉した= 実 TRX を読む前の DoD ✔ は過大だった)。
  3. 「レビューの誤受入 2 腕(中断 / 実行エラー+全行合格)は FAIL になる」— **observed / 適格**(製造者の検体+検査官の自前の検体)。
  4. 「行単位の判定は不変」— **observed / 適格**(`_c9_suite_verdict` に diff なし・検査官 r3 4'(b))。
  5. 「既存 4 suite の判定は不変」— **observed / 適格**(CI dotnet job・ローカル 2 回目)。
  6. 「不合格行と同居する基盤エラーも捕まえる」— **unknown / 宣言済み限界**(検査官 r1 IA-01 がその形を合成: outcome=Failed・行数一致・exit 1 のまま PASS。実 VSTest がこの形を書き切る実例は未観測。残る防御= Aborted・行数不一致・終了状態の不整合)。
- 検出した計器欠陥(帰属つき): 製造物 1 件= 起票時の規則 (c)「RunInfo Error があれば FAIL」が期待赤 suite を誤拒否(製造中に是正・§4)/ 製造物 1 件= outcome 属性なしの診断文(検査官 r1 IA-02・是正)/
  受理側 1 件= r2 ブリーフの窓の条件が姉妹 ECO の差分を除外していなかった(r2 REJECT・製造物非改変)/ 上流 0 件。
- 検出力の限界: 合成入力で測った(実 .NET のクラッシュは再現していない— レビューと同じ立場)。主張 6 の形は捕まえられない。VSTest の TRX のみ(MTP の TRX 形式は未検証)。`Warning` は判定語にしない。
  独立検査官は 1 系統(EQ-002)。CI は fast tier が ubuntu / windows・dotnet は windows のみ。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 読解 | 計器は自分の範囲(行の外の異常・限界= 不合格行と同居する Error)を check 行の文言と注記で宣言している |
  | Q2 | asked | observed/適格 | 実測 | 対の腕(正常 / 期待赤 / 期待赤の実形)と known-bad(中断 / 説明できない Error / 終了 0 と不合格行 / 不在 / 属性なし)を毎回実測 |
  | Q3 | asked | observed/適格 | 実測 | 是正前の誤受入(レビュー 2 腕)と誤拒否(ローカル 1 回目)の双方を是正後に反転させた |
  | Q4 | asked | observed/適格 | 実測 | 実 TRX(4 suite)と合成 TRX の両方を入力にした |
  | Q5 | asked | observed/適格 | 実測 | 未測定(主張 6・MTP 形式・実クラッシュ)を unknown / 限界として分離 |
  | Q6 | asked | observed/適格 | 実測 | 各 commit で検査 exit 観測 → witness → 入口 → commit → push → CI(条件で結んだ順) |
  | Q7 | asked | observed/適格 | 実測 | 陽性対照= C9 較正行 18 腕(毎回実行・不成立なら本走査を止める) |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | witness(tree)・commit・CI run・独立検査報告の sha256 を同一個体として照合 |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」+主張 6 |
  | Q11 | asked | observed/適格 | 実測 | 入力クラス(語彙 / 属性なし / 不在 / Error×不合格行の有無 / Warning / 終了コード×行 / 期待赤の実形)を分けて測った— 検査官が製造者の検体の外(負の終了コード・複数 Error・Text なし)を追加 |

- このクローズが支持しないもの: 主張 6 の形の検出 / MTP 形式の TRX / 実クラッシュの再現 / 製品リポの受入実行(C9 は本リポ専用)。
