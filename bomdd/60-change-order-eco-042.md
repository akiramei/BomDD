# Change Order — ECO-042(/preflight — 作業開始条件の再認証スキルの新設)

> 裁定: user 2026-09-01「起票して」— 外部設計案(Task Contract + Revalidation・/converge
> ループ済み)+当方評価(採択推奨・採用条件 4 点)を受けての起票。
> **gate ① 承認待ち — 製造は本 order の提示で停止する。**

## 担当設備(equipment)

- 評価・起票:
  - requested: `claude-fable-5`
  - resolved: `claude-fable-5`
  - ハーネス: Claude Code(Claude Agent SDK)
  - 来歴: **self-reported**
- 設計原案: 外部(user 経由・/converge 適用済み — round 軌跡 3→3→0)

## 0. 実測(起票根拠・2026-09-01)

### 対象の故障クラスは本リポで実測が厚い

- 前提誤りには専用測定項目が既にある(EXP-20260809-01= 裁定側前提誤り件数 /
  OBS-20260809-04「前提誤りは『発生させない』でなく『到達させない』」)。
- converge 導入日の適用 1 回で**開始時前提 5 件が実測で反証**(ECO-032 §0 の表)・ECO-031 でも
  起票時前提 3 件が gate ① 前に崩れた。「既に完了している」という現在状態の未確認で選択肢を
  落とした実測もある(EXP-20260811-01 第 3 回)。
- **空白**: この前提検査は現状 converge が走るときだけ起きる。converge のトリガーは設計合成
  のみ — 設計を伴わない実装・continuation は前提検査なしで開始される。
- **8/31 初回裁定の誤り認定**: 当方は「前提再認証は converge への吸収を試す」と裁定したが、
  吸収先の converge はトリガーが異なり(設計合成 vs 作業開始)吸収不能 — 本案は当時の
  第 2 位候補(引き継ぎ可能性検査)と第 5 位(前提再認証)の正しい統合である。

### 部分実装が既に存在する(境界宣言が必須)

process-core E01(起票が先)= protected-change クラスの entry gate の機械化 /
eco-fix・eco-accept の前提確認節 / bomdd-next(次作業の選定入口)。/preflight はこれらを
置換せず上に載る — 排他境界の宣言を製造対象に含める(calibrate が converge/eco-accept に
対して行った様式)。

### 設計原案の形式判定

原案の収束 receipt は round 軌跡 3→3→0 — ECO-036 で凍結した手順 5 では**収束失敗**であり、
採用は**打ち切り採用の裁定**として記録する(未収束事項= task class ごとの契約具体表・
原案自身が正直に宣言)。

## 1. 変更要求(gate ① 承認後に製造)

### (a) /preflight 配布スキルの新設【打ち切り採用の骨格】

- 目的: 「現在実際に利用可能な状態から、この作業を正当に開始・継続できるか」の工程判定。
- 中核構造: ①task classification(receipt に**分類と根拠を必ず記録** — 採用条件 2)
  ②minimum task contract の読込(正本化・下記 (b))③repository 固有前提の追加
  ④task 固有の discovered prerequisites(**最小契約と区別して表示** — 案 B への退化防止)
  ⑤authoritative source の所在確認 ⑥各前提の 5 状態判定
  (**confirmed / missing / stale / contradicted / unknown** — missing と unknown を分離)
  ⑦開始判定(**PROCEED / PROCEED_WITH_LIMITS / HOLD / STOP** — STOP は「現在の入力状態では
  正当に開始できない」という**工程判定に限定**・製品判断ではない)⑧preflight receipt の
  成果物埋め込み。
- **HOLD/STOP の根拠つき出口**(採用条件 3): override は reason+decided-by 必須・件数と
  宣言者を receipt に表示(C16 免除様式の踏襲 — 帰結のない判定と出口のないゲートの両轍回避)。
- **Phase 1 は entry trigger のみ**(既存状態依存タスクの開始時)。invalidation trigger
  (実測・裁定・baseline 変更による失効時再認証)は Phase 2 — スコープ外へ。
- 工程線: preflight(入力状態の資格)→ converge(採用の収束)→ 製造 → calibrate(証拠の資格)。
  converge を通らない経路(既定設計の実装)も合法。

### (b) task contract 最小表【裁定対象 — 初期クラス集合】

- 初期クラス(推奨): **continuation** と **bug-fix** の 2 つのみ(原案の契約案を土台に最小化)。
  handoff は「artifact 必須」でなく「**available or reconstructable**」(git 履歴・register・
  order からの再構成を合法とする)。
- **contract 行の追加統制**(採用条件 1): 行の追加は「欠落事故 1 件の実測」または「裁定」経由 —
  出典なき行の増分を禁止(案 C= 過剰 gate への漸進退化の防止)。表は
  〈最小契約= BomDD 正本〉+〈製品側追記領域〉の A-1 構造。
- 検出力の限界を本文へ恒久宣言: **required-known-information absence detector であり
  unknown-unknown detector ではない**(未記録の口頭決定は原理的に検出不能)。

### (c) 配布結線【製造対象】

`bomdd-init.py` SKILLS 10→11+README 表記更新(C7 結合)。BomDD 写し(D-1 前例)。

### (d) 効果測定の事前登録【採用条件 4】

製造時に EXP を記帳: Phase 1 の**検出率**(missing/stale/contradicted の実検出件数)と
**偽停止率**(HOLD/STOP が override された率)— 基準線ゼロから系列測定。Phase 2(invalidation)
への昇格条件= Phase 1 の運用実測。

## gate ①(製造承認)

**承認 2026-09-01 maintainer**「gate ① 承認。推奨どおり①〜④採択で製造に進めて」—
①打ち切り採用(骨格= (a)・契約具体表は最小 2 クラスのみ)②continuation / bug-fix
③採用条件 4 点は起票文言どおり ④名称= `/preflight`。

## スコープ外(宣言済み境界)

- **Phase 2**(invalidation trigger・失効時再認証)— Phase 1 の運用実測後。
- 非起動の機械観測(C16 同型 gate)— 実測後(converge/calibrate と同じ路線)。
- 全 task class の契約表(migration・refactoring 等)— 各クラスの欠落事故の実測 or 裁定で追加。
- 既設製品リポへの遡及設置・TimetableAdv 側への設置。
- E01・eco-fix 前提確認節の置換(preflight は上に載る — 排他境界は SKILL 本文で宣言)。

## 2. 影響なし予測(反証可能・製造前に凍結)

- diff は skill 正本(新設)/ bomdd-init.py(SKILLS 1 行)/ README(本数表記)/
  BomDD 写し+台帳系のみ。**C7 は README を 11 本へ更新しなければ FAIL**(CAL-1 の対照に使う)。
  C4 判定不変(参照非空+実在検査のみ)。C16 は本 order を required と判定する見込み —
  receipt 埋め込み済み。既存 10 スキル不変・既設リポへは kit 再設置まで非波及。

## 3. 較正と受入(起票時凍結・gate 裁定で確定)

- **CAL-1**: SKILLS 11/README 10 で C7 単独 FAIL の実測。**CAL-2**: scaffold から SKILL.md
  除去で C4 判定 FAIL 転化(巻き添えなし)。
- **CAL-3(判定弁別)**: 5 状態それぞれが**固有の理由で**判定される合成 fixture 5 種
  (confirmed/missing/stale/contradicted/unknown 各 1)+ PROCEED 正常系(「常に HOLD」との
  弁別 — C16 F2 の教訓)。
- **V1**: scaffold 実在+AGENTS 参照。**V2**: 製品固有 ID の本文残存なし。**V3**: 全検査 PASS。
  **V4**: CI 緑。**V5**: diff 窓。**V6(初回実使用)**: 実タスク(本 ECO クローズ後の次作業)
  へ /preflight を初回適用し preflight receipt を実個体で残す(新設者= 初回使用者の前例)。

## /converge receipt(本起票の設計に適用 — 起動経路: 自発〔評価時〕+人間裁定〔起票指示〕)

- **判定: 収束**(当方評価ループ round 軌跡: 2→0→0)。**原案側は収束失敗(3→3→0)であり、
  本 ECO はその打ち切り採用を裁定として記録する**(混同しない — 原案の未収束事項= 契約具体表は
  (b) の最小 2 クラス+追加統制で処置)。
- 周回数と新規指摘(評価ループ): round 1 = 2 件(8/31「converge へ吸収」裁定の誤り認定 /
  既存部分実装〔E01・eco-fix 前提確認・bomdd-next〕との境界要求)/ round 2 = 0 / round 3 = 0。
- 検証した主張(要点): 前提誤りの実測群= EXP-20260809-01・ECO-032 §0・ECO-031・
  EXP-20260811-01 第 3 回(本セッション実読)/ converge のトリガー範囲= SKILL 正本実文 /
  部分実装の実在= process-core E01・eco-accept 前提確認節・SKILLS 一覧 /
  register 末尾= ECO-041(次番 042)。
- 未収束事項: なし(原案由来の未収束= 契約具体表は gate 裁定対象 ② として提示)。

## 4. 製造と受入の実測(2026-09-01)

- diff 監査の窓: baseline `a56f504`(起票コミット= 是正開始直前へ更新)→ head は受入時に確定。
- 正本 `method/templates/product-profile/skills/preflight.md` を新設(採用条件 4 点を本文へ
  内蔵: 行の追加統制 / 分類と根拠の receipt 必須記録+曖昧時は厳しい側 / HOLD・STOP の
  reason+decided-by 出口と免除の件数表示 / Phase 1= entry のみの明文)。検出力の限界 3 点を
  恒久宣言(unknown-unknown detector ではない / invalidation 非検出 / discovered の再現非保証)。
- 写しを機械生成(プレースホルダー解決+D-1 ヘッダー・未置換 assert つき)— **正本⇔写しの
  機械突合= 正規化後の残差 0 行**。設置直後、ハーネスのスキル一覧へ `/preflight` が実出現
  (D-1 実地確認)。SKILLS 10→11+README 11 本表記。
- EXP-20260901-03(検出率・偽停止率・起動率)を improvements.md へ記帳(採用条件 4)。

### 較正(陽性対照 — **下記の赤は期待された赤であり不適合ではない**)

- **CAL-1 成立**: SKILLS 11・README 10 のまま実行 → `[C7] FAIL README のスキル本数表記 [10] =
  SKILLS 実数 11` の**単独 FAIL**(同実行の C4 は参照 22 件で PASS — 巻き添え・覆い隠しなし)。
- **CAL-2 成立**: 実 scaffold(参照 22 件・ユニーク 11 スキル)から preflight の SKILL.md を
  除去 → C4 同一判定が PASS→FAIL へ転化・missing のユニーク集合= {preflight} のみ
  (巻き添えなし。ECO-035 プローブの重複計数の粗さはユニーク集合判定で是正済み)。
- **CAL-3 成立(5 状態+PROCEED の弁別 — 各 fixture が固有の契約行・固有の理由で判定される)**:

  | # | 合成シナリオ(クラス) | 発火行 | 判定 | 開始判定 |
  |---|---|---|---|---|
  | F1 | register= verified・order に現況/残課題・受入基準凍結・baseline 記録あり(continuation) | 全行 | **confirmed** | **PROCEED**(「常に HOLD」との弁別= C16 F2 の教訓) |
  | F2 | register に entry なし・order なし・git 履歴に作業痕跡なし(continuation) | current-work-state | **missing**(再構成不能) | HOLD(不足前提を名指し) |
  | F3 | handoff は存在するが以後 baseline が進み受入基準が改訂済み(continuation) | acceptance-target | **stale** | PROCEED_WITH_LIMITS(旧基準非依存の範囲のみ)または HOLD |
  | F4 | order は「製造中」・register は verified(continuation) | current-work-state | **contradicted** | HOLD(矛盾解消= 裁定が先) |
  | F5 | unresolved-items が外部トラッカー参照のみでアクセス手段なし(continuation) | unresolved-items | **unknown**(missing と区別 — 確認手段の不在) | PROCEED_WITH_LIMITS(外部項目非依存の範囲)+ unknown を理由コードつき保持 |
  | F6 | failing-behavior 未提供・target-specimen 不明(bug-fix) | failing-behavior / target-specimen | **missing** ×2 | HOLD |

  5 状態すべてが 1 回以上・各 fixture は**別の契約行**から発火し、判定は重ならない。
  散文スキルにつき本較正は文書化された判定 walkthrough である(機械 fixture 化は
  非起動・効果の実測後 — スコープ外宣言どおり)。

### 受入

- **V1 PASS**: 実 scaffold に SKILL.md 実在+AGENTS.md 参照(22 件・ユニーク 11)。
- **V2 PASS**: 未置換プレースホルダー 0 件・製品固有 ID は出自の来歴(リポ名修飾つき)のみ。
- **V3〜V5**: §5 で確定。
- **V6(初回実使用)**: 起票時凍結どおり**本 ECO クローズ後の次の既存状態依存タスク**で
  /preflight を初回適用し receipt を実個体で残す — クローズ時点では**未実施**として §6 に
  記録(EXP-20260901-03 の起動率測定の第 1 個体を兼ねる)。

## 5. CI 実測

(push 後に追記)

## 6. クローズ

(受入後に追記)
