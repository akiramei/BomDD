# Change Order — ECO-104(handoff 実装規則の 2 点 — 停止の見分けと、独立項目の検査の区分/契約 v0.4 不変)

> 裁定: user 2026-10-11「A」— 第三者レビュー(user 転送・「参考になれば取り入れ、的外れなら無視してよい」)に対する当方の取捨(DECIDE: A= 2 点で起票 / B= 記帳のみ / C= A に権限の言い換えを加える)への返答。
> 契約 §1 は変えない。変えるのは §2 実装規則(交換可能・default)と adapter A3 の出自 1 行。**起票と製造を同一 commit で行う**(文書のみ・ECO-076 の型)・受入は製造者較正のみ。
> verified 昇格は self-conformance PASS と CI 結論を観測した後の受入 commit で(観測前に転記しない)。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-opus-5-5`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-004
- 独立検査: なし(文書のみ・製造者較正のみ。inspector 行は置かない)

## 0. 実測(起票根拠)

- **当たった指摘 1(実例 1)**: レビューに添付された出力例(ViewTube の門の検証器の是正・第 4 回の独立レビュー後の DECIDE)のヘッダは `[DECIDE / PAUSED]`。止めた理由は、当の AI が前のメッセージで告げた打ち切り(「4 回目の手直しはせず判断を仰ぐ」)。
  - 正本 §2.1 Q1 の木は「分岐に依存しない部分があれば CONTINUING、なければ BLOCKED」。出力例は依存しない部分(どれを選んでも行う記録の修正)を挙げているが、返答の前に進めるとは書いていない →
    木の上では BLOCKED(返答の前に進めるなら CONTINUING)。どちらにしても PAUSED は木から出てこない。
  - adapter A1 も「CONVERGENCE_LIMIT(上限到達)→ DECIDE/BLOCKED」。
  - 取り違えの機序(読解): 契約の定義 `PAUSED = work is intentionally suspended, independent of whether it could proceed` が「止めると自分で決めた」= 意図的な中断と読めた。契約は PAUSED を進行可能性と独立に定義しており、BLOCKED と重なる場面の優先順位を実装規則が書いていなかった。
- **当たった指摘 2(文面の矛盾)**: structural F2 に「独立項目は番号が分かれ」がある。何が独立に採否できる項目かは本文を読まないと決まらない(読み手規則 4 と同じ判定)。一方 §2.4 は structural の FAIL を送信停止にしている —
  読解の要る判定が送信停止の側にあると、書き手の判断ひとつで送れなくなる(レビューの「構造 FAIL で止まると復旧できない」懸念の実体はこの 1 項)。
- **採らなかった指摘**(扱いの全体は improvements.md 2026-10-11 節): scope 欄・裁定権限の外部定義・第 3 層の照合器・DISCUSS の収束規則・緊急用の形式・REQUEST の想定外の所見欄。
  採らない理由は「契約が既に決めている」「実例 0」「既裁定で採らない」のいずれか。候補は OBS-20261011-02 に実例待ちで記帳。
- **基準(25e1f24)の計数**(known-bad 側): 正本で「止めると自分で決めたことは PAUSED の理由にならない」0・F2 の行の「独立項目」1・「独立に採否できる項目は番号が分かれている」0・`ECO-104` 0。

## 1. 変更要求(凍結・文書のみ)

1. `method/templates/product-profile/skills/handoff.md` §2.1 Q1 の BLOCKED に括弧書きを足す: 自分で決めた・告げた打ち切り(上限・停止点・「これ以上は手直ししない」)で止まった場合も BLOCKED。
   止めると自分で決めたことは PAUSED の理由にならない。DECIDE/PAUSED は、人間の指示で作業を中断している間に、再開の条件ではない裁定を出すときに限る。
2. §2.3 structural F2 から「独立項目は番号が分かれ」を外し、semantic P8 に「独立に採否できる項目は番号が分かれている」と、structural に置かない理由 1 行(structural の FAIL は送信停止で、書き直せば必ず直る項目だけをそこに置く)を足す。
3. adapter A3 に出自 1 行(ECO-104)。`.claude/skills/handoff/SKILL.md` は正本から再生成(既知 3 hunk)。
4. `method/improvements.md` に本件の節・EXP-20260914-02 に計数④⑤(裁定の後に前提の不足が見つかった回数 / AI が決めるべきことを人間に回した回数とその逆)・OBS-20261011-02(候補 4 点)。

**採らない**: 契約 §1 の変更(PAUSED の定義の書き換えを含む — 実装規則で優先順位を決めれば足りる)/ scope 欄 / 裁定権限の外部定義(実例 0・EXP-20260914-02 ⑤で数える)/ 第 3 層の照合器 /
DISCUSS の収束規則の変更 / 緊急用の形式 / §3 の例の変更(フリースタイル区間の DECIDE/PAUSED は「人間の宣言で作業が中断している間」に当たり、新しい括弧書きと矛盾しない)/ F1 の「明瞭な 1 文」の扱い(実例 0)。

## 2. 影響なし予測(製造前・凍結)

diff= skills 正本・写し・improvements.md+台帳系(order・register)のみ。正本の差分= §2.1 Q1 の括弧書き 3 行・F2 の 1 句削除・P8 の 1 句と理由 1 行・A3 の 1 行。
契約 §1 の本文は不変(sha256 で確認)・core(adapter 区画より前)の固有語 0 を維持・写しの diff= 既知 3 hunk・tools/templates(60-change-order)/hooks/.github diff 0・worklist 新規 ID 1(OBS-20261011-02)・警告 0。

## 3. 受入

- **V1**: 条件= 正本に「止めると自分で決めたことは PAUSED の理由にならない」1・F2 の行に「独立項目」0・「独立に採否できる項目は番号が分かれている」1・`ECO-104` が adapter 区画にだけ 1(grep。基準 25e1f24 では 0/1/0/0)。
- **V2**: 条件= 契約 §1 の sha256 が変更前後で一致 / core の固有語 0(ECO-075 V1 の 13 語+`CONVERGENCE_LIMIT`)/ 写しの diff= 既知 3 hunk のみ。
- **V3**: 条件= self-conformance 全 PASS(exit 0 観測後に commit)・CI 緑・窓= 3 文書+台帳系。
- **V4**: 条件= 製造者較正のみ。**V5(クローズ条件でない)**: EXP-20260914-02(④⑤を含む)で効果を測る。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-104` の出力を開始 artifact として読んだ)

- 分類= 既裁定の適用実装(user「A」・契約は不変)。baseline `25e1f24`= **confirmed**(git status clean・HEAD 一致)/ 次番 104= **confirmed**(register の最終 ECO-103・order の最終 eco-103)/
  正本 §2.1 Q1 と §2.3 F2・P8 の現行文= **confirmed**(実読)/ 同一ファイルへの進行中 ECO なし(ECO-076 は verified・以後の handoff.md の変更なし)= **confirmed**(git log)。
- job ビュー(register 追記後・order 生成前): required_skills= `["preflight"]`(order 不在のため判定不能 class= design-synthesis — 本ファイル生成で解消)・write_scope= allowed_paths 5 本・diff_baseline= 25e1f24・independent_inspection= null。
- 開始判定: **PROCEED**・override 0。

## 4. 製造と受入の実測(2026-10-11・同一 commit)

- 製造物: 正本 §2.1 Q1 の括弧書き・§2.3 F2/P8・A3 の出自 1 行 / 写し(正本から再生成)/ improvements.md の節・EXP-20260914-02 の④⑤・OBS-20261011-02。
- **V1 結果**: PASS(製造後 1/0/1/1・`ECO-104` は 283 行目= adapter 区画〔263 行目から〕の中。基準 25e1f24 では 0/1/0/0)。
- **V2 結果**: PASS(契約 §1 の ```text ブロック 63 行の sha256 `e3540171…`〔変更前後で一致〕/ core の固有語 14 語すべて 0 / 写しの diff= 3 hunk〔8c8,12 冒頭注記・A2/A3 の `{{METHOD}}` 解決 2 行〕)。
- **V3 結果**: 受入 commit のクローズ節で記録(観測後)。
