# Change Order — ECO-029(ref-edges に as-built 文書方言の宣言がなく検査が空振り — ref-v0.10)

> ViewPrism2 ECO-065(50-as-built の fail-open)残 2 面の是正先。gate ①= maintainer 裁定
> 2026-08-03「b(bomdd-lint 側)で gate ① を承認します。製造に進んでください」。
> 同名異物・宣言外方言による検査沈黙の **3 例目**(ref-v0.6 配列/ref-v0.9 ui 二方言に続く)。

## 0. 実測(起票根拠・2026-08-03)

- ref-edges は 50-as-built を **`as_built[]` リスト方言**(Plm 実物: AB/TE 定義・cp_ref 突合)でのみ
  宣言。ViewPrism2 実物は **`as_built:` mapping(文書方言)** — golden_approvals[]・
  golden_approvals_v2.results_round2[]・golden_approvals_v3.target・golden_approved[]・
  golden_findings[]・eco[] 等 — でセレクタが全て空振りし、**as-built の意味検査が無音で消えている**。
- 動的実証: ViewPrism2 で golden_approvals キー改名 → validate_bom(構文床)も lint も無反応
  (0 error/exit 0)。ECO-120 が閉じたのは構文・重複キー面のみで、参照整合・スキーマ面は
  検査経路が存在しない。
- 副発見: **Plm スナップショット(schemas/ref-v0)は ref-v0.8 のまま**(正本 0.9= 2026-07-16
  ECO-013 から 18 日未同期・3 ファイルとも divergence)。同期は Plm 側 ECO で実施
  (ECO-013 影響予測「次回リント実行から被覆が効き始め所見が増える可能性」の履行)。

## 1. 変更要求(ref-v0.10)

`bomdd/50-as-built.yaml` の artifacts エントリへ **文書方言の構造化サブセット**を追加宣言
(既存リスト方言は不変・両方言併記= ref-v0.5/0.9 の「実物が正」前例):

- defines: `as_built.golden_findings[].id` → family **GF**(id-grammar 既存)
- refs:
  - `as_built.golden_approvals[].cp_id` → CP(error)
  - `as_built.golden_approvals[].superseded_by` → [ECO, CAPA](warn)
  - `as_built.golden_approvals_v2.results_round2[].cp_id` → CP(error)
  - `as_built.golden_approvals_v3.target` → CP(error)
  - `as_built.golden_approved[]` → CP(error)
  - `as_built.eco[].id` → [ECO, CAPA](warn — register 正本との整合)

### スコープ外(宣言済み境界 — 本 ECO で明文化して残す)

- **散文面**: 日付キー(golden_2026_* 等の散文文字列)・register からの散文引用
  (golden_detail 内「50-as-built golden_2026_06_24」)・golden_findings_v4(mapping 形=
  キーが ID)— ref-v0.1「散文エッジ廃止」裁定とセレクタ機構の範囲外。閉じるには記録の
  構造化(ViewPrism2 側の記録様式 ECO 候補)が要る。
- **presence(キー消失・最小スキーマ)**: セレクタ空振りは検出不能 — 必要が実測されたら
  lint 規則新設(R-050 の文書方言版)を別 ECO で。
- Plm スナップショット同期・ViewPrism2 受入は各リポの ECO(Plm ECO-007/ViewPrism2 ECO-065)。

## 2. 影響なし予測(製造前)

- diff は method/schemas/draft/ref-edges.draft.yaml 1 ファイル+台帳系のみ。
- C10(派生同期検査)判定不変(突合対象= ID 層・ui 二方言・テンプレ — as-built エントリ非接触)。
- 既存リスト方言(Plm)の判定不変。製品リポへはスナップショット同期(別 ECO)まで非波及。

## 3. 較正と受入(起票時凍結)

- 較正(赤・2026-08-03 実測済み): ViewPrism2 実物で cp_id 改竄・キー改名が現行スキーマで素通り。
  workspace lint 基線= error 0 / warn 12 / info 502(ViewPrism2 6fe3706・ViewPrismUI 204723b・
  --eco なし)。
- 受入:
  - V1: `--schema <method/schemas/draft>` 直指定の workspace lint で **cp_id 改竄
    (CP-UI-G1→CP-UI-G99)が検出へ転化**(R-003)・復元で消える。
  - V2: 同直指定で正常台帳の新規所見を**全数帰属**(方言被覆の回復による正当な検出か・誤検出か)。
  - V3: self-conformance 全 PASS(C1/C10 込み)。
  - V4: push 後 CI 緑(4 値判定)。

## 4. 記録(2026-08-03 受入)

- 製造: ref-v0.10(文書方言 6 セレクタ+GF 定義+版ヘッダ)。**製造中の是正 1 件(正直記載)**:
  初版は v2/v3/v4 系 3 セレクタの親を `as_built.` と誤り空振り — 受入 V1 の**セレクタ個別結線
  検証**(各セレクタへ独立の改竄を注入し個別発火を確認する手順)が検出。実物は世代別トップレベル
  キー(as_built / as_built_v2 / as_built_v4)であり親を修正(「変異テストは変異の適用自体を
  検証する」= OBS-20260716-07 の適用実測)。将来世代キーの保守注意を宣言に明記。
- V1(検出転化・全セレクタ個別): cp_id 改竄 4 種(G95= golden_approvals/G98= v2 results_round2/
  G97= v3 target/G96= v4 golden_approved)→ **R-003 error 4 件が各行で個別発火**・
  superseded_by 改竄(ECO-923)→ warn 発火・復元で全消失。旧スキーマ(0.8)では同改竄が
  **error 0(素通り)** — 較正の赤と検出転化の対照が成立。
- V2(正常台帳・誤検出 0): error 0 / warn 12(基線同値)/ info 502→**498** — 差分は R-005 孤立
  解消 4 件のみで、**全て新エッジが参照する実体そのもの**(CP-UI-G3← cp_id/ECO-023←
  superseded_by/ECO-001・ECO-002← eco[].id)。機械突合(JSON diff)で新規所見 0 を確認。
- V3: self-conformance 全 PASS(C1/C10 込み — 結果は register verification 欄)。
- V4(CI): push 後に本欄へ追記(4 値判定)。
- 実行条件の固定(playbook §8.4 個体ラベル規律): 測定は ViewPrism2 6fe3706(clean)・
  ViewPrismUI 204723b・Plm CLI(HEAD 5c2965b 時点の dist)・`--schema <method/schemas/draft>`
  直指定・--eco なし。
