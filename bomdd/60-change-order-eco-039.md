# Change Order — ECO-039(C9 measurement capability — signature 弁別力・母集団責務・限界宣言)

> 出典: /calibrate 較正掃引(user 裁定 2026-08-31「まず、①を回してみましょう」)+
> 外部レビュー同意(所見分類の三分割・修理方式の固定回避を追補)。
> EXP-20260831-04(calibrate 効果測定)の第 1 回観測。
> **gate ① 承認待ち — 製造は本 order の提示で停止する。**

## 担当設備(equipment)

- 査定・起票:
  - requested: `claude-fable-5`
  - resolved: `claude-fable-5`
  - ハーネス: Claude Code(Claude Agent SDK)
  - 来歴: **self-reported**
- 検査官: 外部レビュア(匿名・user 経由)— 所見分類と方式比較の要求を追補・裁定権限なし

## 0. 実測(起票根拠・2026-08-31 較正掃引)

**対照条件**: C9 は CI dotnet job で毎 push 実行(直近 run 33391355774 の dotnet job= success)・
本掃引の再実測でも 4 スイート全て manifest と完全一致(14/14・15/15・26/30+期待赤 4/
signature 4 突合・9/9)。「テストが動いているか」型のレビューでは**問題なし**になる状態から、
battery の受理側の問い(Q2/Q11)が以下を検出した。

### F2【measurement capability defect】signature 4 件中 3 件が汎用 substring

期待赤 4 件の実 Message を trx から採取(本掃引):

- B01= `[cv]null[vout]`(フィルタグラフ固有トークン — **強い弁別子**)
- B10= `Expected: 2` / B11= `Expected: 1` / B12= `Expected: 1` — **xunit Assert.Equal の定型文**。
  実 Message は `Assert.Equal() Failure: Values differ / Expected: N / Actual: 0` であり、
  signature は Expected 側の literal しか含まない。

故障シナリオ: SDK 更新等で計算値が変わり B11 が `Expected: 1 / Actual: 3` という**別の乖離**で
失敗しても、signature は一致し C9 は緑のまま — manifest の class 欄が主張する
`assertion-failure/L0-overcoupling` という**失敗理由の同一性を signature は符号化していない**。
「期待理由と異なる失敗も FAIL」(ECO-007 の導入目的・`loops/expected-results.yaml:8`)に対し、
3/4 の行で弁別力が弱い。**受理側の較正は一度も行われていない** — ECO-007 の変異テストは
「signature を偽値化 → FAIL」(赤側)のみで、「同一テストが別理由で失敗しても signature が
一致してしまう」側の known-bad は無い。C16 で是正した部分文字列ゲート(ECO-033 R5)と同族。

### F1【coverage boundary — 現行欠陥ではない】母集団の将来増分検出が非搭載

loops/ 配下の csproj 全 13 件を列挙・実読した結果、`dotnet test` 対象(Test SDK/xunit 参照)は
manifest の 4 スイートで**現在被覆は完全**。残る 3 件(loop-02.5 ExportAcceptance /
loop-05 L3Acceptance / equip-02 Acceptance)は `OutputType=Exe` の console harness で対象外。
ただし **manifest は suite 母集団の全数列挙と突合されない**ため、将来テストスイートが追加されて
も未記載なら沈黙する(fail-open は将来増分に対してのみ)。

### F3【declaration defect】検出力の限界が未宣言

C9 には限界宣言がない(未列挙スイート非対象・signature の弁別限界・SDK 個体の非刻印)。
ECO-033 が C16 で確立した様式(「実施した検査が測っていない次元」のコード恒久記載)の
**未遡及** — C9 は様式成立(2026-08-30)以前の設備(2026-07-10)。

分類を一括しない(レビュー裁定): capability defect 1 / boundary 1 / declaration 1。
較正 receipt(二軸)は提示メッセージに添付済み・要旨= 主張 1「凍結挙動の一致」observed/適格・
主張 2「期待理由と異なる失敗の弁別」observed/**条件付き適格**・主張 3「母集団被覆」
observed/適格〔将来増分は限界〕。

## 1. 変更要求(gate ① の裁定対象)

### (a) F2 — signature 弁別力の強化【方式 4 案の裁定】

| 案 | 内容 | 評価 |
|---|---|---|
| a-1 | substring を長くする(`Actual` 値まで含める) | 安価だが xunit 書式への結合が強まり、今回の発見の**局所修理**に留まる |
| a-2 | テスト側に failure marker を埋める | **棄却推奨** — 凍結された loop テストコードの改変が必要(loops/ は不可逆観測データ・実験証拠の書き換えになる) |
| a-3 | **構造化突合**(推奨): C9 側で trx Message を解析し Expected/Actual 等の対で照合。manifest の signature を構造化フィールドへ拡張(旧形 substring も後方互換で受理)。loops 側は無変更・パーサに陽性対照を内蔵 | 失敗理由の identity へ最も近く、変更は計器側に閉じる |
| a-4 | 正規化 Message のハッシュ pin | 最強の同一性だが診断性が低く、無害な書式変化でも赤になる(壊れ方が不親切) |

いずれの案でも受入に**受理側 known-bad**(同一テスト名・別理由の合成 trx → FAIL)と
**緑腕**(現行 4 赤の実測 → PASS)の両腕を含める(§4.4「腕を対で持つ」)。

### (b) F1 — 母集団責務の裁定【二択】

- **b-1**: 境界宣言のみ(manifest は意図的な静的台帳 — 増分は人が追記する旨を F3 の限界宣言へ)
- **b-2(推奨)**: C9 へ母集団突合を追加 — loops/ 配下の Test SDK/xunit 参照 csproj を機械列挙し
  manifest suites と突合、差分で FAIL(検出のみ・自動追記はしない)。判定材料は csproj の
  機械可読参照で安定・変異(合成 test csproj 追加 → FAIL)で較正可能

### (c) F3 — 限界宣言の追記【製造対象・文言は (a)(b) の裁定後に確定】

C9 docstring へ検出力の限界を恒久記載(ECO-033 様式の遡及)。内容= Exe 型 acceptance harness
は対象外(loops は不可逆観測データ・実行環境依存の意図的境界)/ signature の弁別限界
((a) 裁定後の残余)/ SDK 個体の非刻印。

## gate ①(製造承認)

**承認待ち。** 裁定対象= ①製造承認 ②(a) 方式(a-1〜a-4・推奨 a-3・a-2 棄却推奨)
③(b) 二択(推奨 b-2)。

## スコープ外(宣言済み境界)

- Exe 型 acceptance harness(loop-02.5/05・equip-02)の常設計器化 — 実行環境依存
  (ffmpeg・API 起動)の意図的境界。必要が実測されたら別 ECO。
- SDK 個体の刻印(Q9)— (c) で限界として宣言し、実害の実測後に判断。
- 他計器への掃引展開(題材 ②③)— 別セッションの裁定。

## 2. 影響なし予測(反証可能・製造前に凍結)

- diff は `method/tools/self-conformance.py` / `loops/expected-results.yaml`((a) 裁定が
  manifest 拡張を含む場合)+ 台帳系のみ。**loops/ のコード・テスト・観測データは変更しない**。
- 既存 C1〜C8・C10〜C16 の判定不変。C9 の正常判定(現行 4 スイート)も不変の予測
  ((a) は弁別の追加であり現行赤の受理を変えない)。
- C16 は本 order を required と判定する見込み — receipt を下記に埋め込む。

## 3. 受入(起票時凍結・方式裁定後に較正の具体形を確定)

- **V1(受理側 known-bad)**: 同一テスト名・別理由失敗の合成 trx で C9 が FAIL(赤腕)。
- **V2(緑腕)**: 現行 4 スイートの実測で PASS 不変(既存の期待赤 4 件も従来どおり受理)。
- **V3**: (b)= b-2 採択時 — 合成 test csproj の追加(一時)で母集団突合が FAIL。
- **V4**: `self-conformance --dotnet` 全 PASS+CI 緑(headSha 照合)。
- **V5**: diff 窓が §2 の範囲に収まる。
- **V6**: 較正 receipt(二軸)を fix 時に埋め込む。

## /converge receipt(本裁定候補の設計に適用 — 起動経路: 自発)

- **判定: 収束**(round 軌跡: 2→0→0 — 2 周連続ゼロ成立)。
- 周回数と新規指摘: round 1 = 2 件(a-2 の棄却根拠を「凍結コード改変」として実測制約へ固定 /
  EXP 効果指標の多次元化は order でなく improvements.md 側へ記帳)/ round 2 = 0 / round 3 = 0。
- 検証した主張(要点): 4 スイート現在値= `--dotnet` 実測 / 実 Message 4 件= trx 採取 /
  母集団= csproj 13 件全列挙+3 件の実読(Exe 確認)/ ECO-007 変異の片側性= register
  ECO-007 verification 実読 / CI dotnet job の毎 push 実行= run 33391355774 の jobs 実測 /
  C9 コードの fail-closed 面(trx 不在・空 manifest・total pin)= `self-conformance.py:819-880` 実読。
- 未収束事項: なし。
