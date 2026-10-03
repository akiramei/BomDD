# Change Order — ECO-095(ECO-094 試行の反映 — 上流の保守上の約束(maintainability REQ・E/S 版の設計リリース)を工程表と 10/53 テンプレへ candidate として置く〔文書のみ〕)

> 裁定: user 2026-10-03 DECIDE「1:A 2:A 3:A」(ECO-094 クローズ後の反映の判断)。1= 工程表と 53 テンプレに上流の約束の経路を candidate で置く / 2= 10/53 テンプレに candidate 欄を足す / 3= 行と vector の粒度差(OBS-20261003-03)は再設計(ECO-090 系列)の入力に回す(文書は変えない)。
> 根拠= ECO-094(verified)・ViewPrism2 ECO-144(applied)— N=1 の実行可能性。効果は主張しない(candidate 止まり)。
> 文書のみ・製造者較正のみ(前例= ECO-086 / ECO-093)。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-001
- 独立検査: なし(文書のみ・製造者較正のみ。inspector 行は置かない)

## 0. 根拠(起票・2026-10-03)

- ECO-094 の回収(EXP-20261003-01): 人が保守上の約束を REQ として裁定し(gate 1)、E/S 版を bom_version+tag で固定し、統括 AI が CP を導出する経路は 1 機能で完走。人へ戻した判断= 新しい約束 1 件・機械的派生 0 / 追跡 5/5 / 振り分け 1/2 / E→M 参照 0。
- 製品で使った欄(ViewPrism2 ECO-144・candidate): 10 の `classification_hint: maintainability` / 53 の `service_requirement_refs`・`replacement_policy: declared-coupling`。validate_bom は意味検査しない(構文のみ)。
- 現行の工程表(playbook §1)は Service BOM を Phase 6 にのみ置く。レビュー論点 1 への回答として、上流(Phase 1 の REQ)に約束の置き場があることを本文で示す。

## 1. 変更要求(製造対象・凍結)

1. **playbook §1 工程表**: Phase 1 の行に「保守上の約束(交換・継続・復旧・許容する境界)も要求として人が裁定する(maintainability REQ・candidate・ECO-094)」を、Phase 6 の行に「Service BOM= 下流(監視と再検査)。上流の約束は Phase 1 の REQ に置き、53 から参照する」を 1 句ずつ追記。
2. **playbook §7 Phase 6 の Service BOM 項目**: 上流の約束への参照(`service_requirement_refs`)と交換の方針(`replacement_policy`)が candidate 欄であること、E/S 版を bom_version+tag で設計リリースとして固定する経路(ECO-094 試行・N=1)を 1 文で追記。
3. **10-requirements テンプレ**: `classification_hint` のコメントに `maintainability(保守上の約束— 交換の方針・継続・復旧・許容する保守境界。人が裁定・E/S へ結線・candidate)` を追加。
4. **53-service-bom テンプレ**: item に `service_requirement_refs: []`(上流の約束 REQ への参照・candidate)と `replacement_policy: ~`(declared-coupling= 交換しない宣言された結合 / substitutable= 交換可・交換クラスは measured_leak・candidate)を追加(コメント付き)。
5. **採らない**: 行と vector の粒度差への対処(3:A= 再設計の入力・文書は不変)/ 既存製品テンプレの遡及改訂 / playbook の他節の改訂 / 新しい機械検査 / 効果の主張。

## 2. 影響なし予測(製造前・凍結)

diff= playbook(§1 工程表 2 行・§7 1 文)・templates/10-requirements.yaml(コメント 1 行)・templates/53-service-bom.yaml(欄 2 行)+台帳系のみ。tools・hooks・.github・schemas・contracts は diff 0。
C1(YAML 厳格パース)・C7・C13・C15 の判定不変。配布テンプレの内容が変わるが C4/C11 は内容を検査しない。製品リポへは次回配布時に波及・既存製品は不変。

## 3. 受入条件(製造前に凍結・二部形・ECO-080)

- V1(条件): playbook §1 の Phase 1・Phase 6 の行に上記の句があり、§7 に 1 文があること — 検査法: grep(`maintainability`・`service_requirement_refs`)。
- V2(条件): 10 テンプレの classification_hint コメントに `maintainability` が、53 テンプレの item に `service_requirement_refs` と `replacement_policy` があり、53 が厳格 YAML パースを通ること — 検査法: grep+C1。
- V3(条件): diff が allowed_paths のみ・self-conformance 全 PASS(exit 0 観測後に commit)・CI success であること。
- V4(条件): 製造者較正のみ・較正 receipt(trigger ①)があること。

## /preflight receipt(起動経路: **自発** — 既裁定の適用の開始時)

- 分類= 既裁定の適用(user 2026-10-03「1:A 2:A 3:A」)。baseline `b6f5fe2`= **confirmed**(HEAD・clean・CI success)/ 次番 095= **confirmed** / 対象箇所(§1 L26〜34・§7 L445〜455・10 L16・53 L17〜25)= **confirmed**(実読)/ 同一ファイルへの進行中 ECO= **confirmed**(なし)。
- 開始判定: **PROCEED**・override 0。

## /converge receipt(起動経路: 自発 — 反映の置き場と文言の設計)

- **判定: 収束**(round 軌跡: 2→0)。
- DoD: ✔ candidate 止まりで効果を主張しない / ✔ 置き場は既存の節・欄(新しい節・台帳を作らない)/ ✔ 3:A のとおり粒度差の対処を文書に書かない / ✔ 製品で実際に使った欄名と同じ。
- round 1(新規 2 件): ①工程表に Phase 1.6 のような新 Phase を足すか → 足さない(Phase 1 の REQ に句を足す— 新しい工程を発明しない)②53 の `replacement_policy` の語彙= declared-coupling / substitutable の 2 値+measured_leak との関係を注記(方針と実測コストは別軸= s-bom-template の既存原則)。round 2: 0 件。
- 検証した主張: ECO-094 §8 の回収値 / ViewPrism2 で使った欄名(53・10 の実ファイル)/ 現行テンプレの欄構成(実読)。
- 敵対自問: 「N=1 で本文に書くのは早いのでは」— candidate 表示+ECO-094 参照で実証状況を明示する(playbook 冒頭の規律: candidate を実証済みへ格上げしない)。
- 未収束事項: なし。

## 4. 製造(2026-10-03・製造者 EQ-001)

- 製造物(3 ファイル): playbook §1 L28(Phase 1 の句)・L34(Phase 6 の句)・§7 L457(結線と設計リリースの 1 項・粒度差は再設計の入力と明記)/ templates/10 L16(classification_hint のコメントに maintainability)/
  templates/53 L18〜19(`service_requirement_refs: []`・`replacement_policy: ~`・コメント)。

## 5. 受入の実測(2026-10-03・製造者)

- **V1**= PASS(観測: grep `maintainability` → playbook L28・L457 / `service_requirement_refs` → L34・L457)。
- **V2**= PASS(観測: 10 L16 に maintainability・53 L18〜19 に 2 欄。self-conformance `[C1] PASS YAML 69 件厳格パース`)。
- **V3**・**V4**= §6。

## 6. クローズ(2026-10-03・verified・製造者較正のみ)

- **V3**= PASS(観測: 製造 commit `23b6bd5`= self-conformance 全 PASS〔staged・exit 0 観測後〕→ witness → 入口 dry `ADVANCE ECO-095 OK` → commit → push → CI run 37130912102 **success**。diff 窓 `b6f5fe2` → `23b6bd5`= allowed_paths の 6 パスのみ〔playbook・10・53・improvements・order・register〕・tools・hooks・.github・schemas・contracts diff 0。窓閉鎖= head `23b6bd5`・本クローズ commit は台帳系のみ)。
- **V4**= 製造者較正のみ・下の較正 receipt。register: `implemented → verified`。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格・receipt_author_role= producer。文書のみの変更)

- 査定した主張と判定:
  1. 「工程表と Phase 6 に上流の約束の経路が candidate として置かれた」— **observed / 適格**(grep・V1)。
  2. 「10/53 テンプレの欄名は製品(ViewPrism2 ECO-144)で実際に使った欄名と同じ」— **observed / 適格**(53 `service_requirement_refs` / `replacement_policy`・10 `maintainability`— ViewPrism2 の実ファイルと同名)。
  3. 「candidate 表示で実証状況(N=1)を明示し、効果を主張していない」— **observed / 適格**(各追記に candidate・ECO-094 試行 N=1 の語)。
  4. 「3:A のとおり粒度差の対処は文書に書かず再設計の入力に留めた」— **observed / 適格**(§7 の 1 項は所見の参照のみ・対処案を書かない)。
  5. 「配布テンプレの変更は次回配布時にのみ波及する」— **読解**(bomdd-init は手動起動)。
  6. 「この経路は他製品でも機能する」— **unknown**(N=1・主張しない)。
- 検出した計器欠陥(帰属つき): 製造物 0 件・受理側 0 件・上流 0 件。
- 検出力の限界: 文書の整合は grep と実読のみ・配布先での効果は未測定・独立検査なし。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 読解 | 追記は candidate・N=1 を自分で宣言している |
  | Q2 | asked | observed/適格 | 実測 | 是正前(grep 0 件)と是正後(各箇所)の対 |
  | Q3 | asked | observed/適格 | 実測 | V1・V2 を別々の grep と C1 で確認 |
  | Q4 | asked | observed/適格 | 実測 | 実ファイルを直接 grep・C1 の厳格パース |
  | Q5 | asked | observed/適格 | 実測 | 配布先の効果・他製品を unknown として分離 |
  | Q6 | asked | observed/適格 | 実測 | 検査 exit 観測 → witness → 入口 dry → commit → push → CI success |
  | Q7 | asked | NA | — | 陽性対照なし(文書のみ) |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | witness・commit 23b6bd5・CI run 37130912102 を同一個体として照合 |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」+主張 6 |
  | Q11 | asked | observed/適格 | 実測 | 反映 3 点を独立に扱い(1・2 は文書・3 は記帳のまま)それぞれの置き場を確認 |

- このクローズが支持しないもの: 他製品での経路の成立 / 配布先での効果 / 粒度差への対処の選択(再設計の入力)。
