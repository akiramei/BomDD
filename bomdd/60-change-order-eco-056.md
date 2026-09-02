# Change Order — ECO-056(ECO-055 独立検査所見 IA-01〜08 の是正 — 二重正本・検算規則・散文契約・引用座標)

> 裁定: user 2026-09-03「ECO-056 を起票して製造まで進めて」。
> 起点= [ECO-055 独立受入検査(Codex・REJECT)](reports/independent-inspection-eco-055.md)— 受理側真正判定 8/8 CONFIRMED・
> 留保 1(IA-04)・誤検出 0。ECO-055 の verified は起票時凍結基準の判定として維持し(ECO-041 意味論)、被覆外だった
> 欠陥を本 ECO で閉じる(先例: ECO-015 独立検査 → ECO-016/017)。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- 所見の出所: 異系統独立検査官(Codex・申告 GPT-5 Codex・read-only・情報遮断)— **当方が設計していない所見**。
  当方の較正 receipt(ECO-055 §4・asked 4/4)はこれらを 1 件も検出しなかった(OBS-20260902-02 の 2 例目)。

## 0. 実測(起票根拠)— 所見と受理側の再測(独立検査報告 §5)

| ID | sev | 欠陥 | 実測座標 |
|---|---|---|---|
| IA-01 | high | 影響なし予測が名称参照を consumer と誤認(帳簿代用)。実 consumer 0・被覆は C4 YAML parse のみ | stage0-survey.py:6(コメントのみ)・self-conformance.py C4/C13 |
| IA-02 | high | raw_match コメント「和が合わなければ分解漏れ」は 3 列が加算関係を持たず実行不能 | 52-metrics.yaml:20-24 |
| IA-03 | high | 52 冒頭「ECO 指標は 52 へ集約しない」が Phase 7 正典と矛盾 — phase7 prompt:20「metrics(52 に ECO 行)」・register テンプレ :31「verification: 52 の ECO 行」 | 52-metrics.yaml:9-13・phase7-change-order.md:20・60-change-register.yaml(テンプレ):31 |
| IA-04 | high | §5.2 新文「equip 認定は最低ライン(適格性)の判定」は制定保留の資格制度を成立済みとして扱う散文(equip-02 review 項 6「趣旨採択・制定は保留」)。留保: 個別認定の実在は事実 | playbook §5.2 追記段落・equip-02/review-2026-08-02.md:16 |
| IA-05 | medium | §11 行の「基準線 3 ループ」は完全分解 1(transfer-02)・概算 1(cli-cad-01)・再利用 1(equip-01 台帳 #4)の混同。研究必須が L セル内に埋まる | playbook §11 表 52 timing 行 |
| IA-06 | medium | §5.2 段落の引用「FINDINGS §11 t2」は誤座標 — haiku 採用の実体は loops/equip-01/measurements.md 台帳 #4 t2 行・loops/transfer-02/t2-report.md:4 | playbook §5.2 追記段落 |
| IA-07 | medium | 52 コメント「user_rulings は導出可能な転写値」は ruling ID・集計規則が無く未証明。TimetableAdv に非 0 記録(7/1/4)が実在し、ECO-055 §0 の「記入 0 リポ」は誤り | 52-metrics.yaml:37・TimetableAdv 52-metrics.yaml:69,87,105 |
| IA-08 | low | OBS-20260903-02「同じ 4 キー」は regressions / regression の名称不一致を隠す | improvements.md OBS-20260903-02 |

## 1. 変更要求(製造対象)

1. **IA-03(52 冒頭コメント)**: 「ECO レジームの指標は 61/63/register が正本で 52 へ転写・集約しない」を撤回し、Phase 7 正典に整合する文へ置換 —
   「Phase 7(ECO)では phase7-change-order.md §5-6 のとおり **ECO 行(回帰/変更受入/不要改変件数)を本ファイルへ記録**し、register の
   verification がそれを参照する。影響分析の詳細(61)・不要改変監査の分類(63)は各成果物が正本で、本ファイルには**件数と参照のみ**を置く
   (詳細の転写禁止 — §13)」。
2. **IA-02(52 raw_match)**: 「和が合わなければ分解漏れ」を削除。「分解 3 列を伴わない単独報告禁止(§6.1)・参考値」へ戻す。
3. **IA-07(52 user_rulings 削除注記)**: 削除根拠を「consumer 不在(件数で変わる判断が無い)」に限定し、「導出可能な転写値」の主張を除去。
   製品リポの既存記録(TimetableAdv 等)は非接触と明記。
4. **IA-04(playbook §5.2 段落)**: 末文を「equip 認定は最低ライン(適格性)の判定であって、ティア選択の判定ではない」から
   「equip 系列の観測値(P2 等)は routing・ティア選択の根拠にしない。設備の限定資格制度と routing 昇格基準は制定保留
   (equip-02 review 項 6)」へ縮小。
5. **IA-06(同段落)**: 引用座標を「FINDINGS §11 t2」から「loops/equip-01/measurements.md 台帳 #4 t2 行・loops/transfer-02/t2-report.md」へ訂正。
   「plm-v0 注記(§4.7)」の節番号は ECO-055 order 内の記述誤りで playbook 本文には無い — 訂正は本 order §0 の記録のみ。
6. **IA-05(playbook §11 表)**: 52 timing 行を「S: 省略可 / M: 省略可 / L: 推奨」とし、研究レジーム必須は表外の注記へ移す
   (全規模 override として)。「基準線 3 ループ」を「完全分解 1 系列(transfer-02)・概算 1(cli-cad-01)・再利用 1(equip-01)」へ置換し、
   閾値規則を置かない理由を「完全分解の基準線が 1 系列」に改める。
7. **IA-08(improvements OBS-20260903-02)**: 文言を「意味上近い 4 指標(regression は単複の名称不一致)」へ縮小(行内書き換え)。
8. **IA-01(記録の訂正)**: ECO-055 order §2 は履歴として書き換えない。本 order §2 で影響なし予測を正しい形(実 consumer 0・被覆は C4 の
   YAML parse のみ・意味被覆なし)で凍結し直す。

採らない: 52 の意味回帰用 schema fixture の新設(IA-01 是正提案の後半)— 「証明のための複雑性」。列意味の被覆は独立検査
(本件で機能した)と OBS-20260903-03 の watch で扱う。ECO-055 order/register の遡及書き換え — 履歴は残す。

## 2. 影響なし予測(反証可能・製造前に凍結 — IA-01 の訂正形)

- **52-metrics.yaml を読む治具は存在しない**(stage0-survey.py の参照はコメント 1 行・grep `open|safe_load` 該当なし)。被覆は
  self-conformance **C4 の全 YAML parse のみ**(構文)で、列の意味は機械被覆されない。したがって V1 の緑は構文非破壊のみを示す。
- playbook: §5.2 追記段落と §11 表の 52 timing 行+表外注記のみ。他節 diff ゼロ。
- improvements: OBS-20260903-02 の行内書き換え+本 ECO の記帳節のみ。
- 製品リポ・kit: 非接触(bomdd.lock 凍結・次回 scaffold から)。
- 予測が外れる形: C4 で 52 が parse 不能(→ FAIL)/ C13 で参照切れ(→ FAIL)/ worklist が OBS 行の書き換えで警告(→ W 表示)。

## 3. 受入(製造着手後)

- V1: self-conformance 全検査 PASS(C4 構文・C13 リンク・worklist 警告 0)。
- V2: 52 diff の窓= 冒頭コメント・raw_match・user_rulings 注記の 3 箇所のみ。
- V3: playbook diff の窓= §5.2 段落・§11 行+注記のみ(hunk 2 箇所)。
- V4: CI success(revision 一致)。
- V5: 較正 receipt(trigger ④= 独立所見の是正)。**当方較正の限界を前提に**、各是正が対応する所見の再現条件を消したかを所見ごとに
  問う(IA-03 は phase7 prompt:20 と register テンプレ :31 との突合を再実行)。
- 是正後の再検査: **異系統の独立再検査を 1 ラウンド**(先例 016-017 再検査)— verified 昇格の前提とする(裁定: user 承認済み範囲=
  製造まで。再検査の実施は製造完了後に別途)。

## /preflight receipt(起動経路: 自発 — 既裁定の適用実装〔是正〕)

- 分類= 是正実施(bug-fix 型・continuation)。状態: baseline= 起票コミット後の HEAD(製造着手時に確定)/ 次番 056= **confirmed**
  (register 直近 055)/ 独立検査報告の実在= **confirmed**(bomdd/reports/independent-inspection-eco-055.md)/ 8 所見の受理側
  真正判定= **confirmed**(報告 §5)/ 製造着手の裁定= **confirmed**(user 2026-09-03「起票して製造まで進めて」)。
- 開始判定: **PROCEED**・override 0。

## /converge receipt(起動経路: 自発 — 是正案の設計〔採らない案の切り分け〕)

- **判定: 収束**(round 軌跡: 2→0→0)。round 1 = 2 件 — ①IA-03 の是正を「Phase 7 正典に 52 を合わせる」か「Phase 7 側を 52 に
  合わせる」かの選択肢欠落(失敗型 ⑦)→ 正典(prompts/=実行手順の正典・register テンプレ)へ合わせる側を採る(理由: 2 製品が既に
  52 に ECO 行を持つ実運用と一致)②IA-01 の是正提案後半(schema fixture 新設)は設備追加 → 採らないと明示。
- 起動経路: 自発。DoD: 正本が一意 ✔(52 は Phase 7 正典に従属・61/63 は詳細の正本)/ 凍結行の実文と突合 ✔(phase7:20・
  register テンプレ :31・equip-02 review 項 6・t2-report:4)/ 影響が行単位 ✔(§1 の 8 項目)/ 効果の主張は疑い ✔(是正の
  正しさは独立再検査で測る)。
- 検証した主張: phase7 prompt:20 の実文 / register テンプレ :31 / equip-02 review:16 / TimetableAdv 52:69,87,105 /
  ViewPrism2 52:44 `regressions` / LibraryLending 52:89 `regression` / stage0-survey.py:6。
- 未収束事項: なし。
