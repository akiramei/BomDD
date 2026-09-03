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

## 4. 製造と受入の実測(2026-09-03)

- preflight 再確認: baseline `13cca3d`(起票 commit・作業ツリー clean)→ PROCEED。窓内= 52-metrics.yaml / playbook / improvements.md。
- **V1 self-conformance= PASS**(製造直後の実測。worklist 是正後に再実測 — §5)。52 は `yaml.safe_load` 成功。
- **V2 52 diff**: hunk 4(`@@ -9,3 +9,4` / `@@ -13,0 +15` = 冒頭コメント 1 箇所が 2 hunk・`@@ -20,2 +22,2` raw_match・`@@ -37 +39,3`
  user_rulings 注記)= **3 箇所**(受入基準どおり)。
- **V3 playbook diff**: hunk 2(`@@ -371 +371` §5.2 段落・`@@ -787 +787,3` §11 行+表外注記)= 受入基準どおり。
- **所見ごとの再現条件の再測(trigger ④)**: IA-02「和が合わ」0 件 / IA-07「導出可能な転写値」0 件 / IA-04「最低ライン(適格性)の判定」0 件・
  「制定保留」1 件 / IA-06「FINDINGS §11 t2」引用 0 件 / IA-05「基準線 3 ループ」0 件・override 注記 :789 / IA-08 縮小文言 1 件 /
  IA-03 52 冒頭が phase7 prompt:20「52-metrics.yaml に ECO 行」と同じ要求を宣言(整合)/ IA-01 §2 を訂正形で凍結済み。
- **製造中に自己検出した記帳欠陥(ECO-055 由来・本 ECO の窓内で是正)**: worklist が W1×2(EXP-20260902-05・OBS-20260902-02 の
  状態遷移を行の複製で書いていた — 規律「行内書き換え・複製禁止」違反)と W6×1(EXP-20260726-01 の別題材軸を擬似 bullet で書き、
  「<ID> — <内容>」形式に非適合)を検出。self-conformance は worklist を検査に含まないため素通り(worklist は読み取り専用・
  終了コード 0 の設計 — lesson-promote スキーマ節「強制化は運用実測後に判断」)。3 件とも行内書き換え・散文化で是正、
  警告 0 を確認。**受入 V1 に「worklist 警告 0」を含めていたのは ECO-056 §3 が初 — ECO-055 の受入には無かった**。
- 影響なし予測の照合: C4 parse OK・C13 FAIL なし・worklist 警告は上記 3 件(予測に「W 表示」を含めていた — 的中・under-inclusion 0)。

### 較正 receipt(/calibrate 自己適用 — trigger ④: 独立所見の是正。製造者較正の限界を前提)

- 査定した主張と判定:
  1. 「8 所見の再現条件が消えた」— **observed / 適格(条件付き)**: 各所見の再現 grep を上記のとおり再実行し 0 件または整合を確認。
     asked: 「grep 0 件は是正の証明か」→ 文言の除去の証明にすぎない。IA-03 の整合は phase7:20 との**同文要求**で確認したが、
     register テンプレ :31 との整合は文言上(「52 の ECO 行を参照」)のみ。**意味の正しさは異系統の独立再検査で測る**(§3)。
  2. 「V1 の緑は構文非破壊のみを示す」— **observed / 適格**(§2 訂正形のとおり。IA-01 の帳簿代用を繰り返していない:
     consumer を数えず「治具は無い」と宣言)。asked: 「今回も名称参照を consumer と数えていないか」→ 数えていない。
  3. 「窓外の変更なし」— **observed / 適格**(git status の変更 3 ファイル= allowed_paths)。asked。
  4. 「worklist 3 件の是正は記帳の意味を変えていない」— **observed / 適格**(状態遷移と証拠座標は保持・複製の除去と散文化のみ)。
     asked: 「原本行の書き換えで履歴が消えたか」→ 遷移前の状態は git 履歴(eb40fbd 以前)に残る。
- 検出した計器欠陥: **worklist 警告が self-conformance の検査面に無い**(設計どおり読み取り専用)— ECO-055 の記帳違反 3 件が
  CI 緑のまま通過した。計器欠陥ではなく被覆境界(宣言済み)。昇格条件「回収漏れの実害 1 例」には該当しない(実害なし・警告表示で
  検出)。記帳のみ(OBS-20260903-04 候補・本 order §6 で判断)。
- 検出力の限界: 製造者較正は製造者の前提誤りに盲目(ECO-055 で実証・asked 4/4 が誤り 4 件を素通し)。本 receipt の asked も
  同じ限界を持つ。**verified 昇格は独立再検査 1 ラウンドを前提**とし、本 receipt は昇格根拠に数えない。行別: 1 asked / 2 asked /
  3 asked / 4 asked — NA なし。

## 5. CI 実測(V4)と現在状態

- fix commit `58dd2bb` を push → CI run **33685763913**・completed / **success**・headSha `58dd2bb` 一致。ジョブ別= dotnet / fast (windows-latest) /
  fast (ubuntu-latest) すべて success。
- 受入 5 項目の状態: V1 PASS(worklist 是正後の再実測・警告 0)/ V2 PASS(52 hunk 4= 3 箇所)/ V3 PASS(playbook hunk 2)/ V4 PASS /
  V5 較正 receipt(§4・製造者較正の限界を明示)。diff 監査: baseline `13cca3d` → head `58dd2bb`・窓内= 52-metrics / playbook / improvements+
  台帳系のみ・under-inclusion 0。
- **status: in-progress のまま**。verified 昇格の前提= §3 の異系統独立再検査 1 ラウンド(未実施・user 裁定待ち)。製造者較正は ECO-055 で
  誤り 4 件を素通しした実績があり、本 ECO の是正の正しさを製造者自身の緑で昇格させない。
- 製造中の手順逸脱(記録): worklist 是正の 1 回目の適用がアサーション失敗で未反映のまま、§4 に「警告 0 を確認」を先に書いた
  (観測前の記述)。2 回目の適用後に警告 0 を実測し、記述と事実が一致してからコミットした — 「検査の結論を観測してから書く」の
  順序逸脱として本 ECO 自身に記録(ECO-024 型の書面版・実害なし・commit 前に自己検出)。

## 6. 独立再検査(第 1 ラウンド)と第 2 ラウンド fix(2026-09-03)

- 再検査= [independent-reinspection-eco-056.md](reports/independent-reinspection-eco-056.md)(Codex・read-only)= **REJECT**。前回 8 所見= CLOSED 5 /
  PARTIAL 3。新規 6(high 2 / medium 3 / low 1)・受理側真正判定 **6/6 CONFIRMED**・誤検出 0。うち本 ECO が持ち込んだ欠陥 5・既存欠陥の指摘 1(IA-02)。
- **第 2 ラウンド fix(本 ECO の窓内)**: 056-IA-01(52 ヘッダの機械被覆を「意味 consumer 0 / 構文= C1 原本+C4 生成物 / 列意味は未被覆」へ訂正 —
  当方が再び検査 ID を取り違えた帳簿代用)/ 056-IA-03(§5.2 の出典を系列ごとに分離: Plm P2 の haiku miss〔台帳 #5〕と transfer-02 の
  担当者 sonnet 側の補償〔台帳 #4・t2-report §2〕— 因果鎖は測っていないと明記)/ 056-IA-04(templates/README.md:30 を同期 — **窓の拡張**:
  allowed_paths に templates/README.md を追加・理由= 再検査が影響なし予測の under-inclusion を検出)/ 056-IA-05(OBS-20260903-02 末尾の
  旧結論を訂正)/ 056-IA-06(§11 注記の来歴区分を明記)。
- **裁定点(本 ECO の範囲外・設備追加)**: 056-IA-02= 52 に ECO 行の標準形(eco_id・5 分類件数・61/63/受入証拠参照)を追加し C3 で参照実在と
  必須キーを検査する提案。既存欠陥(52 は当初から ECO 行構造を持たず phase7 prompt は散文要求)であり fail-open の指摘は正しいが、
  是正は新規 schema+検査の追加= 設備。選択肢: (a) 別 ECO で 52 の ECO 行 schema のみ追加(検査は追加しない)(b) schema+C3 拡張
  (c) watch(実害= ECO 行未記録が受入を素通りした実例 1 件で起票)。user 裁定待ち。
- 受理側の教訓: 2 ラウンド連続で「引用先を開いて読み直さず記憶で是正文を書く」機序が混入(C4 のみ / FINDINGS §11 t2 / 別系列の接合)。
  較正 receipt はこれを検出しない(OBS-20260902-02 の 3 例目候補 — 2/3 → 昇格審査は lesson-promote で)。
- verified 昇格= 第 2 ラウンド fix に対する再検査(第 2 ラウンド)の結果に従う。
- 第 2 ラウンド fix commit `86bef4f` → CI run **33691090797**・completed / **success**(dotnet / fast windows / fast ubuntu)。diff 監査の窓=
  baseline `13cca3d` → head `86bef4f`(第 2 ラウンドで templates/README.md を窓に追加)。V1 PASS・worklist 警告 0。

## 7. 第 2 ラウンド fix の仮説と再発防止の根拠(2026-09-03・user 指摘「仮説が伝わっていない」への応答)

- **第 1 ラウンド fix の(暗黙の)仮説**: 「8 所見は個別の文言誤りであり、各文を直せば閉じる」。再検査で**同じ型の新規欠陥 5 件**
  (検査 ID の取り違え・別系列の出典接合・同じ主張を述べる他所の未同期 2・来歴区分の曖昧)が出たことで、この仮説は**反証された**。
  欠陥は文にあるのではなく、文を書く手順にあった。
- **第 2 ラウンドの仮説(機序 3 つ)**: 当方が是正文を書くとき、①引用先を開かず記憶で書く ②治具の挙動(検査 ID)をコードで確かめず書く
  ③同じ主張を述べる他の箇所を全列挙せず 1 箇所だけ直す(read-across 漏れ・§4.4「契約×適用面の全列挙」の記述版)。
  第 1 ラウンド 8 件・再検査 5 件の計 13 件は、すべてこの 3 つのいずれかで説明できる(①= IA-06/056-IA-03、②= IA-01/056-IA-01、
  ③= 056-IA-04/056-IA-05、残りは①と③の複合)。
- **第 2 ラウンドで実施した対策(観測可能な結果つき)**: ①引用先を開いて実文を確認してから書いた(台帳 #5「haiku= 3/16」・t2-report §2
  「補償機構= 担当者の自発性 4 項目」・C1 `c1_yaml` の列挙対象)②C1/C4 の挙動をコードで読んだ(self-conformance.py:162-180/226-270)
  ③同じ主張を述べる箇所を grep で全列挙し、残存 0 を確認した(「52 へ集約しない」型: 残存は所見の引用文のみ / 「C4 のみ」型: 0 /
  「FINDINGS §11 t2」: 0 / 「最低ライン」: 0 / README の 52 行: 同期済み — 本節記入直前の実測)。
- **再発しないと言える根拠の範囲**: 上記 3 機序については、対策の結果が観測可能で全て clean。**言えないこと**: 機序の一覧が完全である
  こと(第 2 ラウンドの再検査が測るのはここ)。再検査で同じ 3 型の欠陥が出れば対策の仮説が誤り、新しい型が出れば一覧が不完全、
  0 なら ACCEPT。
- **ループの上限と出口(事前凍結・§9)**: 再検査は**第 2 ラウンドを上限**とする。第 2 ラウンドが REJECT なら追加ラウンドを自動で
  積まず、〈残所見・当方の対策仮説の状態〉を添えて user 裁定(打ち切り採用 / 延長 / 差し戻し)へ遷移する。

## 8. 独立再検査 第 2 ラウンド(上限)= REJECT・判定基準への当てはめ・裁定待ち(2026-09-03)

- 報告= [independent-reinspection-r2-eco-056.md](reports/independent-reinspection-r2-eco-056.md)。前回所見 CLOSED 7 / OPEN 1(IA-02 繰延)/ PARTIAL 1(IA-07)。
  新規 2(high 1・low 1)・受理側 **2/2 CONFIRMED**・誤検出 0。検査官の偶発アクセス 1 件(自己申告・根拠から除外 — 情報遮断資格の毀損として記録)。
- **R2-01(high・機序 (i))**: 「52 の ECO 行= 件数と参照のみ」は Phase 7 正典(phase7 prompt:20「52 に ECO 行」のみ)に無く、§13 記録規約①
  「導出可能な件数は記録しない」と衝突する契約を、当方が r1 で 52 ヘッダに設計意図から書き、r2 で README・OBS へ展開した。
- **§7 判定基準への当てはめ**: 機序 (i) → **(a) 対策仮説の誤り**。IA-07 の残存(棚卸し報告の「導出可能」)は (iii) の実例。**上限到達・REJECT → 追加ラウンドを
  積まず user 裁定へ**(§7 凍結どおり)。
- **工程欠陥の自己診断**: §7 の対策 3 つ(引用先を開く・治具をコードで確かめる・他所を全列挙する)は内容として正しいが、**適用範囲を製造者が自分で選ぶ**
  限り漏れる(r2 で新規に書いた文だけに適用し、r1 由来で r2 に展開した主張には適用しなかった。read-across の対象語も記憶から選んだ)。欠陥は
  「検証手順の欠如」でなく「**検証範囲の自己選択**」。製造者較正が製造者の前提誤りに盲目である機序の 3 例目(OBS-20260902-02 → 3/3)。
- **裁定の選択肢**(上限到達の出口):
  - (A) **打ち切り採用+最小是正(第 3 ラウンド fix・再検査なし)**: R2-01 を「引用先が言うことだけを書く」形で閉じる — 52 ヘッダ・README・OBS の
    「件数と参照のみ」を撤回し「Phase 7 §6 のとおり 52 に ECO 行を記録する。行の構造は未制定(IA-02 裁定待ち)」へ統一。R2-02 は register の
    allowed_paths に `bomdd/reports/`(evidence-only)を追加。IA-07 は棚卸し報告に訂正注記を 1 行追加。verified は**製造者較正のみ**で昇格し、
    その旨を register に明記(独立検査 2 ラウンドの結果と未閉鎖の残余= IA-02 を併記)。
  - (B) **延長(第 3 ラウンド再検査)**: (A) の是正後にもう 1 ラウンド。ただし §7 で上限 2 と凍結しており、延長は user 裁定のみ。
  - (C) **差し戻し**: IA-02 の裁定(52 の ECO 行 schema の要否)を先に確定し、その結果に合わせて 52/README/OBS を一括改訂する。R2-01 と IA-02 は同根
    なので、設計を先に決めてから文言を書く順序になる。
  - 当方の推奨: **(C) → (A)** の順。R2-01 は「未制定の設計を文言で先取りした」欠陥であり、文言の書き直しより設計の裁定が先。IA-02 の裁定が
    「schema は作らない(watch)」なら (A) の文言(行の構造は未制定)がそのまま正になる。

## 9. 裁定 C → A の実施(2026-09-03・user「C → A で進めて。IA-02 は watch」)

- **C(IA-02 の裁定)**: watch。52 の ECO 行 schema も C3 拡張も作らない。OBS-20260903-04(watch 1/3)として記帳 — 起票トリガー= 「ECO 行未記録が
  受入を素通りした実例」1 件。それまで 52 ヘッダ・README・OBS は「Phase 7 §6 のとおり ECO 行を記録する。行の構造は未制定」とだけ書く。
- **A(第 3 ラウンド最小是正・再検査なし)**: R2-01= 「件数と参照のみ」を 52 ヘッダ(:9-12)・templates/README.md:30・OBS-20260903-02 末尾から撤回し、
  引用先(phase7-change-order.md:20「metrics(52-metrics.yaml に ECO 行)」)が言うことだけを書いた。R2-02= register の allowed_paths に
  `bomdd/reports/`(evidence-only)を追加。IA-07= 棚卸し報告 52-metrics-inventory-2026-09-02.md 冒頭に訂正注記を追記(本文は歴史的記録として
  書き換えない)。
- **§7 対策の適用範囲を「diff の全主張」へ拡張**(r2 の欠陥= 適用範囲の自己選択への対策): read-across の対象語を diff の変更前後の文言から機械的に
  抽出(件数と参照 / 件数のみ / 転写・集約しない / 導出可能な転写値 / C4 のみ / FINDINGS §11 t2 / 最低ライン / 基準線 3 ループ)して method・docs・
  README・register を走査。残存= 「件数と参照」2(improvements:5760= 誤りを引用した所見記録・主張ではない / register:2098= ECO-056 summary の r1
  記述 → r3 の撤回を追記)・「件数のみ」1(register:1211= 別 ECO の無関係語)・他 0。引用先の実文は phase7-change-order.md:20 を開いて確認
  (「6. **記録**: … metrics(`52-metrics.yaml` に ECO 行)」)。治具の挙動主張は本 diff に含まない。52 は yaml.safe_load 成功・worklist 警告 0。
- **verified 昇格の根拠(明記)**: 独立検査 2 ラウンド(r1 REJECT・r2 REJECT= 上限)の結果と、r3 の是正が**製造者較正のみ**で受入されたことを
  register に併記する。残余= IA-02 watch(OBS-20260903-04)。製造者較正の限界(OBS-20260902-02・3/3)は昇格審査へ。
- 受入: V1 self-conformance(r3)PASS / V2 52 diff= ヘッダ 1 箇所 / V3 playbook diff なし(r3 は playbook 非接触)/ V4 CI(r3 commit)/ V5 本節。
