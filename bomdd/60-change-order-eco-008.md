# ECO-008 — self-conformance ゲート自身の fail-open 2件(C5 exit 2 の由来非検査・C9 空 manifest の無音 PASS)

## 起票(2026-07-11)

- 出典: **transfer-04(検査の転移)パイロット N=2**。別ベンダーの独立受入検査官(Codex gpt-5.5・
  read-only 敵対レビュー)に、ECO-006 で新設した自己適合ゲート `self-conformance.py` を当てて検出。
  harness 系列は自己レビューで ECO-007 クローズ済みだったが、**独立パスが追加被覆を提供**した
  (独立検査は自己レビュー超の被覆を足す、の実証)。所見は当方で実コード検証し CONFIRMED。
- 再現(実測 2026-07-11・いずれも現 HEAD 4dd025b に残存):
  - **C5(fail-closed 陽性対照が偽 PASS)**: `c5_fail_closed` は検査対象 tool を
    `python <tool> --repo <ghost>` で起動し `p.returncode == 2` のみを合格条件にする。
    ところが **`python <存在しないスクリプト>.py` も CPython が exit 2 を返す**(実測確認)。
    よって stage0-survey.py / impact-retrospective.py が削除・改名されても C5 は
    「fail-closed 成立」と誤 PASS する。die() の測定不能 exit 2 と Python-not-found の
    exit 2 を区別していない — 陽性対照が守るべき領域(治具の消失)にちょうど盲点。
  - **C9(空/欠落 manifest の無音 PASS)**: `c9_dotnet` は manifest 不在は FAIL にするが、
    パースは成功して `suites` が空/None の場合 `for suite in doc.get("suites") or []:` が
    1度も回らず、**check() が一切呼ばれないまま C9 が PASS 扱い**になる。C1/C2 は
    `bool(files) and not bad` で空集合を FAIL にするのに、C9 だけ非対称。
  - 両者ともゲート自身の docstring「**欠測・実行不能は「問題なし」ではない: 検査対象が
    見つからない/実行できない場合も FAIL**」に自己違反している。

## 裁定

- ユーザー承認(2026-07-11)「進めて」— 還元織り込み(fba7f1b)確定後の製造着手。
  順序規律: 是正コミットは fba7f1b(観測+対策設計)の後 — 観測→対策が履歴で判別可能。
- 是正方針: 起票時の草案どおり。
  - C5: 各 tool の存在を事前検査し、無ければ FAIL(測定不能でなく検査器の前提破綻=
    対象欠落チャレンジ)。加えて exit 2 の由来を die() の stderr マーカー(「測定不能:」)で
    確認し、Python-not-found(`can't open file`・同じく exit 2)と区別する。
  - C9: `suites` が空/None なら FAIL(control-plan「検査の対照3種」の対象欠落チャレンジ。
    C9 は対象必須の検査 — vacuous pass を遮断)。

## 影響分析(製造前凍結)

- 影響なし予測: `method/tools/self-conformance.py` 以外 diff ゼロ。既存の C1〜C9 の
  正常判定は不変(基線再実行で確認)。C9 の非空ガードは現行 manifest(suites 4件)では
  PASS 不変。

## 是正(2026-07-11)

1. C5: `tool_path.is_file()` 事前検査(欠落= FAIL・exit code 検査以前)+
   `"測定不能:" in p.stderr` の由来突合を合格条件へ追加。
2. C9: `suites = (doc or {}).get("suites") or []` を先に評価し、空なら
   「vacuous pass を遮断」の FAIL で return。
3. 製造中の追加検出: 初版是正は `doc.get(...)` 直書きで、**空 YAML(doc=None)のとき
   FAIL でなく AttributeError クラッシュ**した(変異 B2 が検出)。`(doc or {})` で
   同一 FAIL 経路へ — 是正自身が silence §16(a) の同族穴を持っていた実例。

## 検証(2026-07-11)

- 基線(fast): C1〜C8 全 PASS。C5a/C5b は「exit 2・測定不能マーカー=True」で PASS
  (正常陰性対照)。
- **変異 A(対象欠落チャレンジ・C5)**: stage0-survey.py を一時退避 → C5a が
  「検査対象の消失」で **FAIL(exit 1)** — 是正前は偽 PASS だったケース。復元済み。
- **変異 B(対象欠落チャレンジ・C9)**: manifest を `suites: []` へ改変 →
  「manifest に suites がない/空(vacuous pass を遮断)」で **FAIL**。復元済み。
- **変異 B2(空ファイル= doc None)**: 初版是正がクラッシュ → `(doc or {})` 是正後、
  同じ FAIL 経路で **FAIL**。復元済み。
- C9 正常基線(--dotnet 実走): 4 スイート全 PASS(14/14・15/15・**26/30 期待赤 4 件
  一致・signature 突合 4 件**・9/9)— 実験証拠の保存検査は不変。
- 影響なし予測: 的中(diff は self-conformance.py のみ)。

## 教訓(還元候補 — lesson-promote 経由・transfer-04 系列)

- **陽性対照つき検査自身の meta-failure**(対象が不在なら無音 PASS しないか)は、
  自己検証が張り損なう類型。自己検証は「あるべき時に FAIL するか」は張るが、
  「検査対象そのものが消えた時に FAIL するか」を張り損なう。独立×別ベンダー検査が
  この穴を高精度に突いた(transfer-04 の創発パターン・4類型の1つ)。
