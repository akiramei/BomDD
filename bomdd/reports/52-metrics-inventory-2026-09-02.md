# 52-metrics 全列棚卸し(2026-09-02・独立作業単位・修正は含まない)

> 裁定(user 2026-09-02): 能力記録から工程設計への辺が欠損している疑いに対し、charter やテンプレを
> 変更する前に **52-metrics の全列を棚卸しする**。判定基準は「consumer がいるか」ではなく
> `metric → consumer → decision → observable consequence` まで辿れるか。辿れない列は原則削除候補
> (「この値が変わったら何が変わるのか」に答えられない metric は計器ではなくログ)。
> 本書は棚卸しの記録であり、削除・改訂・charter 変更は**別途裁定**(本書の判定は暫定)。

## 0. 対象と方法

- 対象: [method/templates/52-metrics.yaml](../../method/templates/52-metrics.yaml) の全列(テンプレ正本)。
- 方法: 各列について producer(誰が書くか)・consumer(誰が読むか — 文書・ゲート・治具の実文で確認)・
  decision changed(その値で何の判断が変わるか)・observable consequence(判断の結果が成果物に残るか)・
  stale condition(いつ古くなるか)を playbook・prompts・tools の実文から逆引きした。
- 実消費者の実測: `52-metrics` を読む治具は `method/tools/stage0-survey.py` のみ(健診用・列は
  `stage0_topology_health_check` 専用で本テンプレの列ではない)。playbook の参照は §6.1(分解報告の規律)・
  §4.7(工場能力は単一軸でない)の 2 箇所。**工場選定・工程設計へ値を入力する経路は文書・治具のどちらにも存在しない。**

## 1. 列別棚卸し

判定語: **計器**(decision まで辿れる)/ **入力**(判断の材料だが判断規則が未定義 — 辿れるが弱い)/
**ログ**(consumer なし、または consumer はあるが decision なし → 削除候補)。

| metric | producer | consumer(実文) | decision changed | observable consequence | stale condition | 判定 |
|---|---|---|---|---|---|---|
| raw_match | 設計者(Phase 5) | §6.1「raw 一致率を単独で報告しない」 | なし(参考値と自己宣言) | なし | ループごと | **ログ**(分解列の存在確認用に残すなら「参考」明記のまま) |
| targeted_fix_success | 設計者 | §6.3 収束ループ・§6.1 分解報告 | 前ループの補正が消えたか → **再製造の要否** | 次ループの有無・fresh 工場投入 | ループごと | **計器** |
| blocker_diffs | 設計者 | §6.3 終了条件「blocker 差分ゼロ」 | **収束ループ終了/継続** | 納品可否 | ループごと | **計器** |
| new_unspecified_diffs | 設計者 | §6.3 終了条件「新規残渣ゼロ」・§6.2 質問リスト | 終了/継続+**裁定 3 択の起票** | 仕様昇格・オラクル追加行 | ループごと | **計器** |
| specified_contract_miss | 設計者 | method-v1 §5(帰属 3 分類)・FINDINGS §6 | 「BOM の穴でなく工場能力」という**帰属** — ただし帰属の先(工場交換・ティア変更・§5.2 工場数)へ接続する規則が**無い** | FINDINGS の記述のみ。charter の工場選定は推奨ティア列挙で本値を参照しない | ループ/工場ごと | **入力**(欠損辺の本体。消費者= 工場選定規則が未定義) |
| exploratory_variance_count | 設計者 | §6.2 質問リスト・42 probes | 分散次元を**裁定 3 択へ変換** | 仕様昇格 or exploratory 宣言 | ループごと | **計器** |
| visual_gap_s1_count / s2_count | 設計者(43 visual gap) | §4.4 UI-CAD・43 テンプレ・prompts phase5 | S1/S2 は**是正(CAPA)対象**、S3/S4 は許容 | 是正 ECO・golden | ECO ごと | **計器**(UI-CAD 案件のみ。非 UI は not-applicable 宣言が要る) |
| design_system_gap_causes | 設計者 | 43 テンプレ・35 Design System BOM | 原因別に**是正先**(35 追加/適用/表示契約/製造) | BOM 改訂 or 再製造 | ECO ごと | **計器**(UI-CAD 案件のみ) |
| defect_escape_count | 設計者/ユーザー確認 | §6.4 帰属調査 | 発生自体が **§6.4 の起動条件** | 是正経路の記録 | 発生ごと | **計器** |
| defect_escape_causes | 設計者 | §6.4 の 5 分類(+UI 系 2) | **どの上流成果物を改訂して再製造するか** | 仕様/BOM/CP/治具の改訂 | 発生ごと | **計器** |
| g3_dryrun_questions | 設計者(G3) | §4.6 G3 ゲート | blocker 質問ゼロ → **製造開始可否** | 製造パッケージ改訂 | Phase 3 ごと | **計器** |
| user_rulings | 設計者 | §6.2 | 件数自体で変わる判断は**無い**(裁定内容は 10/20/K-BOM へ書き戻される — そちらが正本) | なし(内訳は台帳が持つ) | ループごと | **ログ**(転写値。§13 記録規約「導出可能な値の転写禁止」に抵触の疑い) |
| timing.wall_clock_s | time-decomposition.py | FINDINGS §11(transfer-02 人間律速の発見)・52 コメント | 発見時は「人間待ち 56%」が **§9 裁定配置原則の根拠**になった。恒久的な判断規則(例: 人間待ち比率 > X で工程を見直す)は**未定義** | FINDINGS 記述 | セッションごと | **入力**(研究観測としては価値あり。運用計器としては未接続) |
| timing.union_duration_s.* / activity_span_sum_s.* | 同上 | 同上 | 同上 | 同上 | 同上 | **入力** |
| timing.self_reported_s | 同上 | FINDINGS(自己申告 17 倍乖離) | 自己申告を**信用しない**根拠 — 決定は一度きり(規則化済み) | §13「観測値と自己申告を混ぜない」 | セッションごと | **ログ**(命題は既に本文化。継続記録の判断規則なし) |
| timing.measurement.* | 治具 | 再現性(tool_revision 等) | 測定の**再解釈可否** | 再計算 | 治具改版時 | **計器**(来歴。timing 本体を残す場合のみ) |
| note | 設計者 | 人間 | なし | なし | — | 自由記述(判定対象外) |

## 2. 集計

| 判定 | 列 |
|---|---|
| 計器(decision まで辿れる) | targeted_fix_success / blocker_diffs / new_unspecified_diffs / exploratory_variance_count / visual_gap_s1・s2 / design_system_gap_causes / defect_escape_count・causes / g3_dryrun_questions / timing.measurement |
| 入力(材料だが判断規則なし) | **specified_contract_miss** / timing.wall_clock_s・union・span |
| ログ(削除候補) | raw_match / user_rulings / timing.self_reported_s |

## 3. 所見(裁定材料)

1. **欠損辺の本体は `specified_contract_miss` の 1 列に局在する。** 「ミスは製造能力として記録する」思想の書き込み側はこの列で実装済みだが、読み出し側(工場選定・ティア変更・工場数)の規則が playbook・charter テンプレ・prompts のどこにも無い。equip-01〜03 の設備認定結果も同様に charter から参照されていない(TimetableAdv charter は推奨ティアの列挙)。是正するなら「charter の工場構成欄が specified_contract_miss / equip 認定を参照する規則」を 1 箇所に置くことになるが、それは本書の範囲外(別途裁定・templates 変更のため起票対象)。
2. **timing 系は研究観測と運用計器が混在している。** transfer-02 の発見(人間律速・自己申告乖離)は既に §9・§13 へ本文化済みで、以後の継続記録が何の判断を変えるかは未定義。研究レジームでは残し、製品レジームでは §11 テーラリングで省略可とする、または人間待ち比率の閾値を判断規則として置く、のいずれかを裁定する。
3. **ログ 3 列は削除候補。** raw_match は「参考値」と自己宣言しており、user_rulings は台帳から導出可能な転写値、self_reported_s は命題が本文化済み。ただし削除はテンプレ変更(起票対象)であり、製品リポの既存記録には触れない(歴史的記録の非消去)。
4. **テンプレと実運用の乖離。** ViewPrism2 の 52-metrics は本テンプレに無い約 90 種のキーを持ち(hub_concentration・probe_first・under_inclusion 等)、TimetableAdv・LibraryLending はテンプレ列にほぼ準拠。テンプレの列設計が製品の実需要(ECO レジームの指標)を捉えていない可能性がある。本書の棚卸しはテンプレ正本に限定し、製品側キーの棚卸しは別単位とする。
5. **原価列は存在しない。** EXP-20260802-02 が「原価欠落 >80%」と測ったのは equip 系列の記録に対してであり、52-metrics テンプレには原価列自体が無い。原価を計器にするかは「その値で何の判断が変わるか」(工場数・ティア選定)を先に定義してから決める。

## 4. 次の裁定点(本書は判定しない)

- ログ 3 列の削除可否(templates 変更 → 起票)
- specified_contract_miss と equip 認定の消費者を charter の工場構成欄に置くか(templates 変更 → 起票)
- timing 系の扱い(研究のみ / 閾値規則化 / 省略可)
- 製品側キー(ViewPrism2 約 90 種)の棚卸しを別単位で行うか

source: user 裁定 2026-09-02(2 → 1 → 3 の順・3 は棚卸しを独立単位に)
evidence: 本書 §1 各行の consumer 列(playbook 節番号・治具名)
