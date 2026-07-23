# Existing Project Migration Pack - 既存プロジェクト BomDD 移行用

この文書は、すでに実装や既存の `bomdd/` を持つプロジェクトを、新しい BomDD オンボーディング方法論へ移行するための AI 向け入口パックである。

新規プロジェクト開始用の [ai-onboarding-pack.md](ai-onboarding-pack.md) と目的は同じだが、入口が違う。既存プロジェクトでは、まず実装を変更せず、既存成果物を棚卸しし、標準成果物パスと PLM-ready 契約へ対応付ける。

## 1. 移行の目的

- 既存の仕様、UI、DB、BOM、工程、検査、保守証跡を `bomdd/` の標準構造へ対応付ける。
- BOM-DD PLM が不足、粗粒度、粒度不整合、トレース切れ、PLM-ready 契約違反を判定できるようにする。
- 既存実装をいきなり改修せず、まず方法論上の不足を可視化する。
- PLM 指摘を `bomdd/plm-intake/00-index.md` と `bomdd/plm-intake/{CandidateNo}.md` の個別作業票にする。
- 移行後の変更/是正は、仕様/BOM/Control Plan へ逆流してから行う。

## 2. 最初に守ること

1. 移行フェーズでは実装コードを変更しない。
2. 既存ファイルは移動より参照を優先する。
3. コピーまたは昇格した成果物には `source_ref` を残す。
4. 不明点は `unresolved_questions` または個別作業票へ残す。
5. 旧成果物を削除しない。
6. PLM Gate が通るまで製造、改修、リファクタを始めない。
7. 既存テストが緑でも、Control Plan に接続されるまでは BomDD 上の受入完了とは扱わない。

## 3. 人間へ最初に確認する質問

1. 現在の正とする仕様、README、設計メモ、チケットはどれですか。
2. 既存の `bomdd/` はありますか。ある場合、どの成果物を現行として扱いますか。
3. 実装済みの主要機能、画面、DB、外部依存は何ですか。
4. 既存 UI モック、スクリーンショット、Figma、HTML mock はありますか。
5. 既存 DDL、migration、seed、fixture、運用データ制約はありますか。
6. 既存テスト、受入ログ、CI 結果、手動確認証跡はどこにありますか。
7. 保守対象、障害履歴、依存更新履歴はありますか。
8. 移行中に絶対に変更してはいけない実装ファイルや生成物はありますか。
9. 移行完了の判定者は誰ですか。
10. PLM 指摘の `rejected` / `not-exported` を裁定できる人は誰ですか。

## 4. 移行先の標準構造

```text
bomdd/
  00-charter.md
  10-requirements.yaml
  20-spec.md
  ui/
    mock/
    <screen-or-flow>/
      ui-ir.json
      ui-bom.json
      ui-trace-map.json
      extraction-report.md
      unresolved-questions.md
  db/
    schema-intent.md
    ddl/
    migrations/
  30-ebom.yaml
  31-kbom.yaml
  32-mbom.yaml
  33-control-plan.yaml
  34-routing.yaml
  35-design-system-bom.yaml  # UI-CAD 案件のみ必須。非UI案件は not-applicable
  40-work-order.md
  50-as-built.yaml
  53-service-bom.yaml
  plm-intake/
    00-index.md
    CAND-001.md
    sync-results/
    migration-inventory.md
    source-map.md
```

## 5. 移行インベントリ

AI は最初に `bomdd/plm-intake/migration-inventory.md` を作る。これは既存リポジトリの棚卸しであり、まだ仕様や BOM ではない。

```markdown
# Migration Inventory

| Source | Kind | Current role | Candidate BomDD artifact | Action | Notes |
|---|---|---|---|---|---|
| README.md | spec-source | 概要と使い方 | bomdd/20-spec.md | reference | 正の仕様か要確認 |
| src/App | implementation | 既存実装 | bomdd/32-mbom.yaml | reference | 移行中は変更しない |
| tests/Acceptance | test | 既存受入 | bomdd/33-control-plan.yaml | map | CP ID へ接続 |
```

`Action` は次の語彙にする。

- `reference`: 既存ファイルをそのまま参照する。
- `copy`: `bomdd/` へコピーし、`source_ref` を残す。
- `summarize`: 既存資料を要約して BomDD 成果物へ昇格する。
- `split`: 粗い資料を複数成果物へ分割する。
- `not-exported`: 今回 BomDD へ取り込まない。理由を残す。

## 6. 旧成果物から新成果物への対応付け

AI は `bomdd/plm-intake/source-map.md` を作り、旧成果物と標準成果物を接続する。

```markdown
# Source Map

| Old source | New BomDD path | Mapping type | Source refs | Status |
|---|---|---|---|---|
| docs/spec.md | bomdd/20-spec.md | summarize | docs/spec.md@<commit> | proposed |
| tests/BookingTests.cs | bomdd/33-control-plan.yaml | reference | tests/BookingTests.cs@<commit> | proposed |
```

`Status` は PLM 作業票と同じ語彙にする: `proposed` / `assigned` / `applied` / `verified` / `rejected` / `not-exported`。

## 7. 標準移行フロー

**hub-first 部分移行(軽量順路)**: 全成果物の一括対応付けの前に、stage-0 健診(変更トポロジー測定)でハブ unit を特定し、ハブから as-built M-BOM を起こす順路を選べる(初適用= ViewGrid 2026-07-07)。

git 履歴は 4 種の学習信号を持つ — fix 連鎖= FMEA の種、設計反転(Revert・再設計)= K 層/decision note 昇格候補、churn×サイズ時系列= god 化曲線、feat→ファイル写像= 影響予測の教師データ。ただし生存者バイアス・why の欠落・分類ノイズを限界として明示して使う。

### 7.1 stage-0 triage score(**alpha** — 較正 N=4・定義凍結= stage0-oss-01)

> 治具: `method/tools/stage0-survey.py`(較正記録: BomDD loops/stage0-oss-01/calibration.md)。
> 較正点: ViewGrid(108k行・単独開発)+ jellyfin(C#・361k行)+ gitea(Go+TS・774k行)+ home-assistant core(Python・5.41M行)。
> 位置づけ: **診断スコアではなく triage**(hub-first 部分移行の入口判断と優先度づけ)。閾値は N=4 の暫定であり、閾値の改訂は次ラウンドの事前登録を経る。

| 項目 | 判定材料(治具出力) | 意味 |
|---|---|---|
| Cross-unit pressure | multi-unit 跨ぎ率(fix 限定値も併記) | ECO 影響宣言で回収できる余地 |
| Cross-layer pressure | 層跨ぎ率(治具出力は未対応 — 手動観点) | 層境界を跨ぐ変更管理の必要性 |
| Churn-fix hub overlap | churn 上位10 ∩ fix 上位10 | **主信号**。hub-first 候補の安定性 |
| Fix concentration | top-1% fix share | 少数 unit への修正集中 |
| Late-fix signal | fix 潜伏(正規化指標は次ラウンド事前登録 — 現行の絶対距離は大規模リポで飽和するため参考値) | 回帰検査・影響分析の不足候補 |
| God-file amplifier | size 上位が hub と重なるか | **増幅因子**(主指標にしない — 三冠は単独開発リポの局所性。stage0-oss-01 H2 不支持) |
| Instrumentation warnings | 台帳的ファイル(VERSION/locale/manifest)の上位混入・分類ノイズ | 測定値の信用度 |

暫定閾値(N=4 較正):

```text
cross-unit rate     : <30% low / 30–45% medium / >45% high
churn-fix overlap   : 0–1 weak / 2–4 medium / >=5 strong
top-1% fix share    : <15% 弱集中 / 15–25% 中集中 / >25% 強集中
```

ハブの定義(stage0-oss-01 の実測で再定義):
**ハブ= 大きいファイルではなく、変更と修正が繰り返し戻ってくる unit**。主信号= churn∩fix overlap。
size・所有分散・層跨ぎ位置・テスト不在は増幅因子。**size 単独をハブ判定に使うのはアンチパターン**。

1. `bomdd/plm-intake/migration-inventory.md` を作る。
2. `bomdd/plm-intake/source-map.md` を作る。
3. 既存仕様を `10-requirements.yaml` と `20-spec.md` に対応付ける。
4. GUI がある場合、既存画面、スクリーンショット、モックを `bomdd/ui/mock/` へ参照またはコピーし、UI-IR/UI-BOM/trace map を作る。
5. UI-CAD 案件なら `35-design-system-bom.yaml` を作る。
6. DB がある場合、既存 DDL/migration を `bomdd/db/` へ参照またはコピーし、`db/schema-intent.md` を作る。
7. 既存実装の主要単位を `30-ebom.yaml`、`31-kbom.yaml`、`32-mbom.yaml`、`33-control-plan.yaml`、`34-routing.yaml` へ対応付ける。
8. 既存ビルド、テスト、CI、手動確認証跡を `50-as-built.yaml` の seed として記録する。
9. 既存依存、障害履歴、外部知識を `53-service-bom.yaml` へ対応付ける。
10. BOM-DD PLM へ同期する。
11. PLM 指摘を `plm-intake/00-index.md` と個別作業票へ落とす。
12. stop finding が 0 になるまで BomDD 成果物を修復する。実装は変更しない。
13. 移行完了後に、必要なら変更/是正オーダーとして実装変更を開始する。

## 8. PLM 作業票の形式

`bomdd/plm-intake/00-index.md`:

```markdown
# PLM Intake Index

| CandidateNo | PLM finding | severity | owner | target ticket | status |
|---|---|---|---|---|---|
| CAND-001 | Existing tests are not mapped to Control Plan | stop | AI | `bomdd/plm-intake/CAND-001.md` | proposed |
```

`bomdd/plm-intake/CAND-001.md`:

```markdown
# CAND-001 - Existing tests are not mapped to Control Plan

status: proposed
severity: stop
owner: AI
target_artifacts:
- bomdd/33-control-plan.yaml
- bomdd/50-as-built.yaml

## Finding
Existing acceptance tests are present, but no CP-* rows reference them.

## Required action
Create Control Plan characteristics and link test evidence from As-Built.

## Resolution
- status: applied / verified / rejected / not-exported
- evidence:
```

`status` は `proposed` / `assigned` / `applied` / `verified` / `rejected` / `not-exported` のみを使う。

## 9. 移行 Gate

| Gate | 通過条件 |
|---|---|
| M0 Freeze | 移行中に実装を変更しない方針が明記されている |
| M1 Inventory | `migration-inventory.md` と `source-map.md` がある |
| M2 Structure | 標準成果物パスが存在または not-applicable 理由付き |
| M3 Trace | REQ -> Spec -> E-BOM -> M-BOM -> Control Plan の経路がある |
| M4 Evidence | 既存テスト/CI/手動確認が Control Plan と As-Built へ接続されている |
| M5 PLM | stop finding が 0。warning は個別作業票で裁定済み |

## 10. 移行中にやってはいけないこと

- 既存コードをついでに直す。
- 既存テストを BomDD へ接続せずに「テスト済み」と扱う。
- 古い仕様を上書きし、出所を消す。
- 旧 BOM を削除して新 BOM だけにする。
- `source_ref` なしで要約を作る。
- PLM 指摘を口頭メモだけで処理する。
- PLM が認識しない status 語彙を使う。
- 移行 Gate を通す前に製造 AI へ Work Order を渡す。

## 11. 移行完了の定義

- 既存成果物の棚卸しがある。
- 旧成果物と新標準パスの対応表がある。
- 必須 BomDD 成果物が存在する、または not-applicable 理由がある。
- PLM が標準成果物を読める。
- stop finding が 0。
- unresolved question は blocker / non-blocker に分類されている。
- 既存実装の As-Built seed がある。
- 次の実装変更は Phase 7 の変更/是正オーダーとして開始できる。

## 12. シナリオ専用の後続手順

本書は既存成果物を BomDD / PLM-ready へ載せるところまでを扱う。技術の異なる実装へ再製造し、本番切替まで行う場合は、対象シナリオに一致する専用手順を明示的に選ぶ。

- **C#/.NET + WPF へ再実装し、既存 RDB を継続利用する場合**: [legacy-to-wpf-rdb](../scenarios/legacy-to-wpf-rdb/README.md)

専用手順は通常の新規開発へ設置しない。対象プロジェクトでシナリオ初期化コマンドを実行した場合だけ有効になる。
