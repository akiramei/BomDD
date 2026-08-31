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

**承認 2026-08-31 maintainer** — 6 点裁定:

1. 製造承認。
2. **(a)= a-3 採択(構造化突合)**: 凍結された loops/ 側は変更しない / failure identity は
   少なくとも test identity・failure/parse kind・Expected・Actual を用いて構成 /
   parse 不能・曖昧な形式を旧 substring 判定へ **silent fallback して PASS させない** /
   受入に「旧 substring なら一致するが構造化 identity が異なる別理由失敗」を known-bad として
   含める / 現行 4 件の期待赤が通る正常腕も維持。
3. **(b)= b-2 採択(母集団突合)**: Test SDK 参照 project の機械列挙と manifest を**双方向**に
   突合 — 未記載 project・不存在/対象外化した manifest entry の**双方を FAIL** / 自動追記は
   行わない / console harness 群は C9 の母集団外として境界を明記。
4. (c) 限界宣言は (a)(b) の製造結果を反映して確定。**SDK/環境差の再現性を今回測定していない
   ことも限界として残す**。
5. register 誤帰属は新規 CAPA とせず、**ECO-011 型の再発を既存 C3 が commit 前に捕捉した
   control-effectiveness 実例**として扱う。
6. EXP-20260831-04 では F2/F1/F3 を capability defect / boundary finding / declaration
   deficiency と分けて集計し、**C3 による記録層事故の捕捉を calibrate の効果へ算入しない**。

担当設備の適用解釈(裁定の文言内・order へ記録): (i) Contains 型(B01)の Message には
Actual が存在しない(String 欄は xunit が `···` で省略)ため、identity は kind 固有に
`actual: null` を**明示宣言**する — 沈黙の省略ではなく宣言された不在。(ii) 既存 `signature`
欄は補助検査として残し identity を主判定とする(identity の parse 不能は FAIL)。

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

## 4. 製造と受入の実測(2026-08-31)

- diff 監査の窓: baseline `a201226`(起票コミット= 是正開始直前へ更新)→ head は受入時に確定。
- **(a) a-3 製造**: `_c9_parse_failure`(trx Message → kind/expected/actual の構造化・識別不能は
  None)+ `_c9_identity_match`(want の `actual: null` は kind 固有の不在の明示宣言)+
  manifest の 4 entry へ identity 追加(2026-08-31 trx の実 Message から構造化採取・signature は
  補助へ降格)。parse 不能は FAIL(silent fallback なし)。loops/ のコード・テストは無変更。
- **(b) b-2 製造**: `_c9_population`(Test SDK/xunit 参照 csproj の機械列挙)+双方向突合
  (未記載 project と 不存在/対象外化 entry の双方を個別理由で FAIL・自動追記なし)。
  述語の実在検証= 13 csproj 中ちょうど manifest の 4 件が該当(Exe harness 3 件は自然に母集団外)。
- **(c) 製造**: c9 コード先頭へ限界宣言 3 点(Exe harness 母集団外 / identity は Message 表層の
  構造化で意味論同一性の完全な証明ではない / SDK・環境差の再現性未測定+SDK 個体非刻印)。
  docstring の C9 項も同期。
- **陽性対照(常設・毎回実測)**: 5 腕を c9 起動時に実行し、不成立なら本走査を行わない
  (計器を先に疑う)— 正腕 2(Equal 型・Contains 型の真の期待赤を受理)/ **known-bad**
  (`Expected: 1` は含むが Actual= 3 の別理由失敗 — 旧 substring は一致・identity は却下。
  gate 裁定 2 の要求そのもの)/ parse 不能却下 / known-bad の前提検査(substring が一致する
  合成であることの assert — 変異の適用自体を検証・OBS-20260716-07)。
- **V1(受理側 known-bad)PASS**: 上記 5 腕が常設化され毎回実測(初回実行で成立確認)。
- **V2(緑腕)PASS**: クリーン実測で 4 スイート全 PASS・期待赤 4 件一致・identity 突合 4 件。
- **V3(母集団変異)PASS**: 合成 test csproj(cal-probe-tmp)+ghost entry の同時変異で
  母集団突合が**双方向とも個別理由で FAIL**(`未記載: ['loops/cal-probe-tmp']` /
  `不存在: ['loops/ghost-probe/...']`)。実スイート 4 本は変異下でも PASS(巻き添えなし)。
  ghost entry のスイート実行も trx 不在で FAIL(既存 fail-closed の継承)。変異は完全復元
  (git status で identity 追加分のみの差分を確認)。
- **V4(全検査)PASS**: `--dotnet` クリーン実行で全検査合格・exit 0(既存 15 検査判定不変)。
- V5(diff 窓)・CI は §5〜§6 で確定。

### V6 — 較正 receipt(/calibrate 自己適用・トリガー③: 検査器の変更直後。二軸)

- 査定した主張と判定(測定成立性×証拠資格):
  1. 「C9 は期待理由と異なる失敗を検出できる」— **observed / 適格へ昇格**(F2 是正後:
     known-bad〔substring 一致×identity 相違〕の却下を常設 5 腕で毎回実測。掃引時の
     「条件付き適格」から回復)。
  2. 「manifest は loops の test 母集団を被覆している」— **observed / 適格**(双方向突合が
     常設化・変異 2 種で発火実測)。
  3. 「identity は失敗理由の意味論的同一性を証明する」— **observed / 条件付き適格**
     〔測っていない次元: 同 kind・同 Expected/Actual で意味の異なる失敗は弁別外 —
     限界宣言 (2) に恒久記載〕。
  4. 「別環境・別 SDK でも判定は安定する」— **unknown(理由コード: 未実行 — 本弧は単一環境。
     ドリフトは FAIL 側に倒れる設計のみ保証)**。資格判定なし・昇格根拠に使用不可。
- 検出した計器欠陥と帰属: なし(本弧のプローブ・ゲートとも所見なし。V3 の FAIL は期待された赤)。
- 検出力の限界: c9 コード先頭の宣言 3 点+「陽性対照は合成 Message であり実 trx の書式変化は
  実スイートの期待赤 4 件が継続較正する」。

## 5. CI 実測

- 対象 revision: `4ddc9c3`(**ローカル HEAD と一致を確認**)
- run 識別子: 33401687017 — https://github.com/akiramei/BomDD/actions/runs/33401687017
- 結論: **PASS** — 全 3 job success(fast ubuntu / fast windows / **dotnet**)。
  dotnet job で新設の identity 突合・母集団突合・陽性対照 5 腕が **CI の別マシン環境で初走行し
  成立**(V6 主張 4〔別環境安定性〕は unknown のままだが、runner 1 環境での成立を副次観測
  として記録 — 再現性の測定には足りない)
- 観測日時 / 観測主体: 2026-08-31 / 本 ECO の担当設備(§担当設備)
- UNKNOWN の理由コード: 該当なし(headSha 照合・job 別結論まで観測)

## 6. クローズ

- diff 監査の窓: baseline `a201226` → head `4ddc9c3`(**窓閉鎖**)。窓内は
  `method/tools/self-conformance.py` / `loops/expected-results.yaml` /
  `method/improvements.md`(gate 裁定 6 の記帳)+台帳系のみ — 影響なし予測が的中。
- 受入: V1(陽性対照 5 腕・常設)/ V2(緑腕 4 スイート)/ V3(母集団変異 2 種の双方向 FAIL・
  巻き添えなし)/ V4(--dotnet 全検査 PASS)/ V5(diff 窓)/ CI(3 job 緑)すべて成立。
  V6 較正 receipt(二軸)は §4。
- **掃引所見の最終処置**: F2= 是正済み(「期待理由と異なる失敗の弁別」は条件付き適格→適格へ
  回復)/ F1= b-2 で常設化(将来増分の fail-open を閉鎖)/ F3= 限界宣言 3 点を恒久記載。
- gate 裁定 5 の記録: register 誤帰属(起票時)は新規 CAPA とせず、ECO-011 型の再発を既存 C3 が
  commit 前に捕捉した **control-effectiveness 実例**として扱う(calibrate の効果へ非算入 —
  裁定 6・improvements.md EXP-20260831-04 に明記)。
- このクローズが支持しないもの: 失敗理由の意味論的同一性の完全な証明(identity は Message
  表層の構造化 — 限界宣言 (2))/ 別環境・別 SDK での再現性(unknown・理由コード= 未実行)/
  Exe 型 acceptance harness の常設計器化(意図的境界)。
