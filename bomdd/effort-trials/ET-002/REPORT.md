# ET-002 — 型④の横断掃引を実タスクとして Luna none / medium / high + Sol medium で計測(EXP-20260903-04)

> 測定器: [`effort-calibration.py`](../../../method/tools/effort-calibration.py)(ECO-058/059)・実行器:
> [`effort-trial-runner`](../../effort-trial-runner/README.md)。正本= [`trial.yaml`](trial.yaml)・[`runs/`](runs/)。
> 導出物= [`projection.yaml`](projection.yaml)。**本 report の §4「裁定後の一致」は事後の導出であり receipt ではない。**

## 1. 課題と treatment

- **課題**(`input/TASK.md`・self-conformance.py 全文 @ `a372771` を埋め込み・sha256 は trial.input_hash): 全 21 ゲートについて
  「走査母集団が 0 件のとき無音で PASS(SILENT)か OK か」を判定する。**ECO-054 が「第 4 の計器の有無は横断掃引未実施」と
  書いて閉じた実仕事**であり、§13 第 5 様態(同族計器の横断掃引)の実施を兼ねる。測るために作った課題ではない。
- **oracle**(`rubric/rubric.md`・run 前に封印): 製造者(claude)の読解+要点の実行確認(C3 の verified 0 件・C12 のリンク 0 件)。
  採点 19 ゲート(C4・C8 は定義の曖昧さで採点除外)。**oracle は人の読解であり実装ではない** — 腕との不一致で oracle の
  誤りが判明したら receipt を書き換えず本 report に記録する、と rubric に事前宣言。
- **評価者**: `rubric/evaluate.py`(oracle スクリプト・構造的盲検)。
- **treatment**(4 腕 × 反復 2 = 8 run・並列): LN= Luna none / LM= Luna medium / LH= Luna high / SM= Sol medium。
  到達モデル・到達 effort は unknown。

## 2. 結果(封印 rubric に対する evaluation receipt → projection)

| 腕 | n | pass | pass_rate | 正答(19 中) | reasoning tokens | mean tokens(in+out) |
|---|---|---|---|---|---|---|
| LN Luna none | 2 | 0 | 0.0 | 16 / 14 | 0 / 0 | 46,408 |
| LM Luna medium | 2 | 2 | 1.0 | 19 / 19 | 516 / 516 | 45,876 |
| LH Luna high | 2 | 0 | 0.0 | 16 / 15 | 7,250 / 7,250 | 52,646 |
| SM Sol medium | 2 | 0 | 0.0 | 16 / 16 | 4,660 / 3,106 | 51,732 |

- 導出(projection): none→medium **supported** / medium→high **unsupported** / none→high unsupported。
- **この符号は封印 oracle の誤りの帰結である**(§3)。Luna medium は製造者の粗い読解と一致し、高 effort 腕は製造者が
  見落とした 3 ゲートを正しく SILENT と判定して「不一致」になった。封印 rubric に対する receipt はこのまま正本として残す
  (書き換えない)。

## 3. 不一致の裁定 — oracle 欠陥 3 件・評価器欠陥 1 件・腕の誤り

**評価器欠陥(製造者・較正で自己捕捉)**: v1 の evaluate.py がゲート ID を `upper()` して rubric キー(`C5a` 等)と不一致になり、
添字つき 5 ゲート(C5a/C5b/C6a/C6b/C11b)が**全腕で missing-verdict** になった。評価結果の詳細と生出力の突合で発見。
v1 の receipt は `runs/defective-evaluator-v1/` に隔離(証拠として保存・削除しない)し、修正した evaluate.py(別 spec_hash)で
再評価した。封印 rubric は不変。

**oracle 欠陥(腕の指摘を実文で裁定 — 3 件とも腕が正しい)**:
| ゲート | 封印 oracle | 裁定 | 根拠(実文) |
|---|---|---|---|
| C11b | OK | **SILENT** | `failed = [c for c in iq+oq if not pass]` が C11b 自身の走査で、空なら `failed=[]`・件数表示なし |
| C10 | OK | **SILENT** | テンプレ実在キーの空振り走査(`missed = [k for k in ir_t ...]`)に非空ガードなし・件数表示なし。ID 層の families は陽性対照でガードされるが、テンプレキー母集団は別 |
| C16 | OK | **SILENT** | targets と sections は別母集団だが個別ガードがなく、表示は合算 `n` のみ — 一方が 0 件でも見えない |

**腕の誤り(裁定後も誤り)**: C11 を SILENT とした LH×2・SM-01(C11 は run 1 の iq/oq を走査せず、run 2 の iq は
`bool(iq3)` でガード)/ LN×2 の C7・C12(定義 (b)「件数・空リスト表示なら OK」を適用していない)/ LN-02 の C17・C18 欠落
(最終回答が途中で終わる)。

## 4. 裁定後の一致(事後の導出 — receipt ではない)

C10 / C11b / C16 を SILENT に訂正した oracle での正答数(19 中):

| 腕 | run 1 | run 2 | 誤り |
|---|---|---|---|
| LN Luna none | 15 | 13 | C7・C12(定義未適用)・C10・C11b・(C17/C18 欠落) |
| LM Luna medium | 16 | 16 | C10・C11b・C16(製造者と同じ見落とし) |
| LH Luna high | 17 | 18 | C11(過検出)・C16(run 1) |
| SM Sol medium | 17 | 19 | C11・C16(run 1)/ run 2 は全問正答 |

- Luna 内は none < medium < high と単調で、reasoning tokens(0 / 516 / 7,250)と同順。**問題側が計算量に反応した**ことを支持する
  (裁定後の導出であり、封印 receipt の分類ではない)。
- Sol medium は Luna high と同等以上(17–19 対 17–18)。能力の段差は本 trial では小さい。
- 高 effort 腕(LH・SM)の誤りは「過検出」(C11)に寄り、低 effort 腕(LN)の誤りは「定義の未適用」と「出力の途切れ」に寄る。

## 5. 横断掃引の結果(実仕事の成果 — 起票候補・本 trial では是正しない)

型④(空母集団の無音 PASS)が構造として存在するゲート: **C3**(verified 0 件)・**C10**(テンプレキー走査)・**C11b**(iq/oq 走査)・
**C16**(母集団別の件数なし)。採点除外の **C8** は 8/8 腕が SILENT(不在検査の構造)、**C4** は 4/4 で割れた(生成 YAML 走査に
非空ガードなし)。ECO-054 が「未実施」と明示した第 4 の計器は**少なくとも 4 本**あった。是正の要否・範囲は別途裁定(§13 第 5 様態:
類として扱い、クローズ節に対象列挙)。

## 6. EXP-20260903-04 への回答と、このクローズが支持しないもの

- effort 感度: 封印 receipt では supported(none→medium)/ unsupported(medium→high)。裁定後の導出では Luna 内単調。
  **封印 oracle の誤りは effort 感度の符号を反転させうる** — 測定器は oracle の誤りを吸収しない(限界として記録)。
- 支持しないもの: 到達モデル/effort(unknown)/ 裁定後の一致を receipt と同格に扱うこと / C11 の腕の主張(run 1 の
  iq/oq)が「上流 runner の母集団」として問題ないこと(本 trial の定義外)/ 是正の優先度。
- 実行器: 8 run とも exit 0・RESULT.md 非空(ET-001 の欠陥は再演せず)。codex backend は正常。
