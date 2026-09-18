# Change Order — ECO-080(受入節の書式: 受入条件〔計画〕と観測結果を文形で分離 — テンプレート二部形・自己適用 order も同形・Jev 第 3 回で弁別の回復を実測〔implemented〕)

> 裁定: user 2026-09-18 DECIDE「A」(EXP-20260918-01 第 2 回の結果= 受入節の書式が計画と結果を区別していない → 是正 ECO を起票)。**起票のみ**(製造裁定は別 DECIDE)。
> 出自= Jev 設備認定 第 2 回([報告 §4](reports/jev-qualification-01/README.md))。計器の欠陥ではなく記録の書式の欠陥、という読み。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-001
- inspector: EQ-002
- 検査官(独立検査併用時): 製造裁定 A(2026-09-18)で inspector 行を追加(gpt-5.6-sol @ Codex CLI・入口 `bomdd-run --executor EQ-002 --report … --range …`)。B/C なら追加しない。
  (起票時点で inspector 行を置くと job 射影が EQ 構文を要求する— 実測: 散文を置いて LEDGER_INCONSISTENT・是正して再射影)

## 0. 実測(起票根拠)

- **第 2 回の外れ 9 本はすべて `## 3. 受入` 節**(ECO-063/068/069/070/071/075/076/077/078)。本文の形= 「**V1**: self-conformance 全 PASS(C7 が 12/12・…)」「**V4**: CI 緑(headSha 照合)」—
  受入*条件*が、受入*結果*と同じ文形(体言止め・PASS/緑/件数)で書かれている。意図・条件を示す語(「であること」「候補」「計画」「製造前に凍結」)がない。Jev の confidence は 0.66〜1.00(拮抗でなく確信)。
- **正答した受入節との差**: ECO-062/064〜067 は見出しが「受入(製造時の候補)」・ECO-079 は「受入計画(修正前固定)」で本文も「…を RED 根拠とする」「…を観測」と手順形。**書式が違うと同じ計器が正しく読む**。
- **混在の実例**: ECO-077 §3 に「known-bad(実測): 実 map の 1 class から roles を外すと job selftest が FAIL(復元後 PASS)」— 受入節の中に実施済みの結果が書かれている(ラベル側の誤り 1 本= 書式が混在を許している証拠)。
- **性能の裏付け**: performed 78/78(実測/クローズ・較正 receipt・独立検査 round・§0 実測)・影響なし予測 17/17・製造裁定の候補 3/3・placeholder 1/1 — 「書かれていることは読める」。
  読めないのは書かれていない意味(計画か結果か)。
- **なぜ問題か(BomDD 側)**: 受入節は「製造前に凍結する条件」であり、結果は受入時に観測して書く(playbook §8・オラクル・ファースト)。両者が同形だと、①受入 commit で条件を結果へ「転記」しても
  文面が変わらず、観測の有無が記録から読めない(C17 限界 (5)「見出しだけの receipt」と同根・「予定を実測として転記」の危険)②第三者(独立検査官・後日の読者)が受入節を読んで
  「もう PASS している」と誤読しうる ③意味センサー(Jev)を将来 gate に置いても判別できない。
- **テンプレの現状(実読)**: `method/templates/60-change-order.md` §3 に「変更分の受入を先に追加」「治具の凍結条件」・§5 に「回帰+変更受入(失敗 5 分類)」— 受入*行*(オラクル)の規律はあるが、
  order 本文の受入節を「条件」と「観測」に分ける**書式**はない。自己適用 order には様式がなく、各 ECO が手で見出しを選んでいる(「受入」「受入(製造時の候補)」「受入計画」が混在)。

## 1. 変更要求(候補 — 製造裁定で凍結)

1. **テンプレート `method/templates/60-change-order.md` の受入欄を二部形にする**(§3「変更分の受入」と §5 の間か §5 冒頭): 各条件を
   `- V<n>(条件): <満たすべき状態> であること — 検査法: <手順・grep・コマンド>`(製造前に凍結・結果を書かない)と
   `- V<n>= PASS | FAIL | UNMEASURABLE(観測: <座標= ログ/commit/run id>)`(受入時に記入・条件行は書き換えない)に分ける。見出しは「受入条件(製造前に凍結)」と「受入結果(観測)」。
   注記 1 行: 「条件は結果の文形で書かない(『全 PASS』『緑』『12/12』は観測にだけ書く)」。
2. **自己適用 order の同形化**: ECO-080 以降の自リポ order は同じ二部形(§3= 受入条件・クローズ節= 受入結果)。既存 order は**書き換えない**(履歴・第 2 回の検体は原文のまま保存)。
3. **playbook への候補提示のみ**: §8.4「受入記録の個体ラベル規律」に「条件と観測の文形分離」を織り込む案を improvements.md に置く(本文改訂は lesson-promote の停止点で別途・本 ECO の範囲外)。
4. **Jev 第 3 回(受入条件 V2)**: 第 2 回で誤読された 9 節を新書式に書き換えた検体(scratch・履歴は改作しない)と原文 9 節(対照)に同じ Choice 4 択を当て、新書式で planned ≥ 8/9・原文は
   performed のまま(書式が効いたことの対照)。認定条件は結果受領前に README §5 へ固定。

**採らない**: 既存 order の書き換え / 受入節の機械 lint(条件行に「PASS」等が出ないことの検査 — 誤りの再演が実測されてから)/ playbook 本文の直接改訂 / Jev の工程組み込み(設備認定は
EXP-20260918-01 の続き・別 ECO)/ ECO-079 の対象ファイル(change-management.md・acceptance-evidence.md)への変更(窓が重なる・ECO-079 は implemented)。

## 2. 影響なし予測(製造前・起票時点 — 製造裁定で凍結)

diff= templates/60-change-order.md(受入欄)+台帳系(order・register・improvements)+reports/jev-qualification-01(第 3 回の README 節・スクリプト・結果)。tools/hooks/.github diff 0・playbook diff 0・
C4/C14 advisory・C13 新リンク実在・ECO-079 の allowed_paths と交差なし。製品リポは次回 kit 再設置から(テンプレ差分のみ)。

## 3. 受入条件(製造前に凍結 — 本 ECO から二部形を自己適用)

- V1(条件): テンプレの受入欄に「(条件)」と「観測:」の二部形と注記 1 行があること — 検査法: grep。
- V2(条件): 新書式に書き換えた 9 節で Jev の choice が planned ≥ 8/9、かつ原文 9 節は performed のままであること — 検査法: 第 3 回スクリプト(README §5 に設計を先に固定)。
- V3(条件): self-conformance 全 PASS(exit 0 観測後に commit)・CI 緑・diff 窓= allowed_paths のみであること — 検査法: 単一入口・`gh run list --commit <full sha>`。
- V4(条件): 製造裁定 A なら異系統独立検査(r1 境界探索 → r2 是正確認+回帰・inspection gate 経由の昇格)/ B なら製造者較正のみ、であること。
- V5(条件): 較正 receipt(trigger ①)があること。

## 3b. 製造裁定の候補(別 DECIDE で提示)

- **A** §1 の 1〜4 すべて+異系統独立検査(検査官に「新書式の受入節を読んで、条件と結果を取り違えるか」も問う)。
- **B** §1 の 1〜4 すべて・製造者較正のみ。
- **C** 1〜3 のみ(Jev 第 3 回を行わない)・製造者較正のみ。
当方の推す案= A。テンプレは全製品リポへ配布される様式なので、第三者が読み違えないことを独立に確かめたい。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-080` の出力を開始 artifact として読んだ)

- 分類= 既裁定の適用(user DECIDE A= 起票)。baseline `54382e2`= **confirmed** / 次番 080= **confirmed**(grep 0)/ 第 2 回の外れ 9 本が受入節= **confirmed**(summary-02.md)/
  テンプレに受入節の書式なし= **confirmed**(実読)/ ECO-079(implemented)の窓と交差なし= **confirmed**(register 実読)。
- job ビュー(order 生成後): required_skills= `["preflight"]`・skills_missing= `[]`・required_capability= `{"producer": "EQ-001", "inspector": null}`(裁定 A で inspector を記入)・stop_type= NONE
  (1 回目は inspector 欄の散文で LEDGER_INCONSISTENT → 欄を検査官注記に移して再射影)。
- 開始判定: **PROCEED(起票のみ)**・override 0。製造は裁定後。

## 4. 製造裁定と製造(2026-09-18・user DECIDE「A」= 全部+異系統独立検査)

- **製造裁定 A**: §1 の 1〜4 すべて+独立検査。register `filed → implemented`(本 commit)・inspector EQ-002 を配員欄に追加・allowed_paths 再凍結(reports/independent-inspection-eco-080*.md を追加)。
- **製造物**:
  1. `method/templates/60-change-order.md` §5 冒頭に「受入節の書式(二部形・ECO-080)」5 行: 条件行 `V<n>(条件): … であること — 検査法`(製造前に凍結・結果を書かない)/
     結果行 `V<n>= PASS | FAIL | UNMEASURABLE(観測: 座標)`(受入時に記入・条件行は書き換えない)/ 注記(結果の文形は観測行にだけ・同形だと転記が読めない・由来 ECO-080)。
  2. 自己適用: 本 order の §3 が二部形の最初の個体(受入条件)。§6 クローズで結果行を書く(条件行は不変)。ECO-080 以降の order は同形。既存 order は不変。
  3. playbook §8.4 への織り込み案= improvements.md 2026-09-18 節(候補提示のみ・本文不変)。
  4. Jev 第 3 回= `bomdd/reports/jev-qualification-01/jev_qual_03.py`(検体= 誤読 9 節 × 3 腕・設計は README §5 に結果受領前に固定)。
- **受入結果(製造者・観測)**:
  - V1= PASS(観測: grep `(条件)` 1・`観測:` 1・`受入節の書式(二部形` 1 — 60-change-order.md)。
  - V2= PASS(観測: README §6・results-03.jsonl — new 9/9 planned〔p 0.98〜1.00〕・orig 9/9 performed〔対照再現〕・newh0 9/9 planned〔本文だけで効く〕・27 リクエスト・エラー 0・resolved jev-1.13.0)。
    **r1 是正後(03b)= PASS**(観測: results-03b.jsonl — new 9/9〔0.96〜1.00〕・orig 9/9 performed・newh0 9/9〔各 ECO の原文見出し・0.85〜1.00〕・27 リクエスト・エラー 0・tokens in 24,407)。
  - V3= §6 で記録(self-conformance・CI・窓)。V4= §5 独立検査。V5= §6 較正 receipt。

## 5. 独立検査(異系統・Codex EQ-002・入口 bomdd-run から `--report`/`--range` つきで起動)

### 5.1 r1(2026-09-18・range= 境界探索)— 報告: [independent-inspection-eco-080.md](reports/independent-inspection-eco-080.md)

- 起動: fix commit 79cdcf7(witness tree 659b05125f7d・入口 dry ADVANCE)→ `cell exit 0` → `report REJECT sha256:ed0ccb63f76e (EQ-002)`・台帳 `range: 境界探索`・
  verdict_line `REJECT IA-01・IA-02・IA-03・IA-04`。**本節の判定は台帳の verdict から転記**。
- 判定: **REJECT・所見 6(遮断 4・境界 2)**。検査官の観測: diff 0・commit 0・外部 API 呼び出しなし・9 節の第三者読解= 新書式はすべて「未実施の条件」と一意に読め、原文はすべて「結果と読み違える余地あり」
  (本 ECO の核心は第三者読解でも成立)・自己適用 §3/§4 整合・kit smoke exit 0 で二部形 5 行が生成物に含まれる・窓内・採らない項目は守られている。
- 所見と是正(すべて製造物帰属・同一 revision の是正 commit で):
  | IA | 所見 | 是正 |
  |---|---|---|
  | IA-01 | テンプレ §5 の二部形箇条書き直後に空行がなく、失敗 5 分類表が Markdown の表として成立しない(pandoc GFM で実測) | 表の前に空行を挿入(python-markdown で `<table>` 1 を確認) |
  | IA-02 | ECO-077 の新書式が「known-bad(実測)」(実施済みの記録)を条件へ変え fixture も変えた= 内容非保存 | 実測文を原文のまま残す(混在検体として測る) |
  | IA-03 | newh0 が原文見出しを固定値「## 3. 受入」に置換(ECO-068/075 は「(製造時の候補)」「(候補)」)= 実験定義と不一致 | 各 ECO の原文見出しを使う・README §5 の定義を修正 |
  | IA-04 | NEW_BODY の多くの条件に「— 検査法:」がなく、テンプレの完全な二部形を測っていない | 全条件に検査法を付す |
  | IA-05(境界) | UNMEASURABLE の記録要件(原因・試みたコマンド)が未規定 | テンプレの結果行に「測定不能の原因と試みたコマンドを書き PASS に数えない」を追加 |
  | IA-06(境界) | `state_sha256` が 16 桁の短縮値で命名と不一致 | 完全な 64 桁を記録(01/02/03 初版は 16 桁接頭辞のまま・README に注記) |
- 是正後の再測(03b)= new 9/9・newh0 9/9・orig 9/9(§4 V2)。検査官の限界宣言: 設計の結果受領前固定は同一 commit のため検証不能・GitHub 表示は未確認・Jev 再実行なし。

### 5.2 r2(2026-09-18・range= 是正確認+回帰・範囲限定 10 項目)— 報告: [independent-inspection-eco-080-r2.md](reports/independent-inspection-eco-080-r2.md)

- 起動: 是正 commit a3c95ee(witness tree 7baecdb67dbe・入口 dry ADVANCE)→ `cell exit 0` → `report REJECT sha256:4dad3f7bd227 (EQ-002)`・台帳 `range: 是正確認+回帰`・
  verdict_line `REJECT IA-06 — README に「第1回・第2回・第3回初版の state_sha256 は16桁接頭辞」という注記がなく、是正が完了していません。`。**本節の判定は台帳の verdict から転記**。
- 判定: **REJECT・未是正 1(IA-06 の README 注記)**。IA-01〜05= 是正済み(pandoc GFM で表が Table・NEW_BODY["077"] 原文保持・newh0 の見出し 2 件一致・V 項目 45 件に検査法 45 件・UNMEASURABLE 要件あり)/
  回帰 7〜10= 退行なし(§3 条件行不変・03b 27 行の数値一致・kit smoke exit 0 で二部形 5 行と要件行・窓 11 ファイルすべて allowed_paths 内・playbook 等 diff 0)。
- 是正: README 冒頭に記録の注記(旧 3 ファイルの `state_sha256` は先頭 16 桁の短縮値・03b 以降は 64 桁・旧記録は書き換えない)を追加 → r3(IA-06 の是正確認+回帰)。

### 5.3 r3(2026-09-18・range= 是正確認+回帰・範囲限定 4 項目)— 報告: [independent-inspection-eco-080-r3.md](reports/independent-inspection-eco-080-r3.md)

- 起動: r2 是正 commit c5ea61d(witness tree 4318cedd85fd・入口 dry ADVANCE)→ `cell exit 0` → `report REJECT sha256:55ebea8d8125 (EQ-002)`・台帳 `range: 是正確認+回帰`・
  verdict_line `REJECT IA-07 — a3c95ee..c5ea61d の差分に、指定された README と order 以外の r2 検査報告が含まれます。`。**本節の判定は台帳の verdict から転記**。
- 判定: **REJECT・所見 1(IA-07)・帰属= ブリーフ(受理側)**。IA-06= 是正済み(README 注記と JSONL 282 行〔旧 3 ファイル 16 桁・03b 64 桁〕が整合)/ §3 不変(両 revision の §3 が 8 行完全一致・sha256 同一)/
  窓= 12 ファイルすべて allowed_paths 内。IA-07 の実体: 是正差分 3 ファイル(README 4 行・order §5.2 8 行・r2 報告 76 行)のうち r2 報告は allowed_paths 内の**受理側の記録**であり製造物の逸脱ではないが、
  当方のブリーフ項目 2 が「README と order のみ」と書いたため検査官は正しく FAIL にした。製造物への是正なし。
- 是正(ブリーフ側): r4 の項目 2 を「README・order・r2 報告・r3 報告」に修正。教訓= 是正確認 round の差分限定条件は「前 round の報告の commit」を含めて書く(受理側の記録も差分に入る)。
