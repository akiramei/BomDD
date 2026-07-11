# ECO-008 — self-conformance ゲート自身の fail-open 2件(C5 exit 2 の由来非検査・C9 空 manifest の無音 PASS)

> 状態: **起票のみ(裁定・製造前)**。是正/検証は未着手 — ユーザー裁定で停止中。

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

- **未(ユーザー承認待ち)**。製造(コード変更)は個別 blocking 裁定+明示承認が前提。

### 是正方針案(製造前・凍結前の草案)

- C5: 各 tool の存在を事前検査(`Path.exists()`)し、無ければ FAIL(測定不能でなく
  検査器の前提破綻)。加えて exit 2 の由来を die() の stderr マーカー(「測定不能:」)で
  確認し、Python-not-found(`can't open file`)と区別する。
- C9: `suites` が空/None なら FAIL(C1/C2 と対称の非空ガード)。

## 影響分析(製造前予測 — 未凍結)

- 影響なし予測: `method/tools/self-conformance.py` 以外 diff ゼロ。既存の C1〜C9 の
  正常判定は不変(陽性/陰性対照で確認予定)。C9 の非空ガードは現行 manifest(suites 4件)
  では PASS 不変。

## 是正

- (未着手)

## 検証

- (未実施)

## 教訓(還元候補 — lesson-promote 経由・transfer-04 系列)

- **陽性対照つき検査自身の meta-failure**(対象が不在なら無音 PASS しないか)は、
  自己検証が張り損なう類型。自己検証は「あるべき時に FAIL するか」は張るが、
  「検査対象そのものが消えた時に FAIL するか」を張り損なう。独立×別ベンダー検査が
  この穴を高精度に突いた(transfer-04 の創発パターン・4類型の1つ)。
