# ECO-056 独立再検査(異系統・Codex・read-only)— 第 1 ラウンド+受理側の突合

> 検査官: Codex CLI(codex:codex-rescue 経由・**申告モデル名 Codex / GPT-5** — provider 側 snapshot ID は観測不能・自己申告)。所要 約 10 分。
> 開示範囲: 起票時 order §0〜§2(13cca3d 版)+製造 diff(13cca3d→58dd2bb: 52-metrics・playbook・improvements の OBS 行)+前回所見 8 件の ID/題名。
> 受入節 §3〜§5・receipt・register の verification/diff_audit・improvements 2026-09-03 節(開示行以外)は非開示(遵守申告は §4)。
> 報告本文は Codex の出力を**無改変**で転記(sandbox の read-only 制約で報告ファイルは書けず stdout 返却)。受理側の突合は「## 5.」。

---

# ECO-056 独立再検査(異系統・read-only)

対象 HEAD: `3e6c5f5094388fc939596027be5decdbdaf65097`(branch `main`)
検査官モデル名: **Codex / GPT-5**(システムによる自己申告。実到達 snapshot の細粒度 ID は観測不能)
判定: **REJECT**

前回8所見の結果は **CLOSED 5件 / PARTIAL 3件**。加えて新規所見6件(high 2 / medium 3 / low 1)を検出した。特に、ECO 行の記録契約がコメントだけで YAML 構造を持たず fail-open であること、および機械被覆を「C4のみ」とした説明が実装と異なるため、現在の工程契約上は受入不可と判定する。

## 1. 任務A 閉鎖判定表

| 所見 ID | 判定 | 再現条件と実測結果 | 該当箇所 file:line |
|---|---|---|---|
| ECO055-IA-01 | **PARTIAL** | `method/tools` 内の `52-metrics.yaml` 明示参照は `stage0-survey.py` の来歴コメント1件だけで、意味 consumer 不在への訂正は成立。ただし「被覆はC4のみ」は誤り。HEAD の原本テンプレは C1 が直接厳格 parse し、C4 は scaffold 後の生成 YAML を parse する。 | `method/tools/stage0-survey.py:6`、`method/tools/self-conformance.py:162-180`、`:226-270`、`method/tools/bomdd-init.py:45-46,307-309`、`method/templates/52-metrics.yaml:15` |
| ECO055-IA-02 | **CLOSED** | `raw_match` は参考値、3列を伴わない単独報告は禁止、3列は加算関係を持たず検算規則なし、と明記された。元の実行不能な「和」規則は消えている。 | `method/templates/52-metrics.yaml:22-26` |
| ECO055-IA-03 | **CLOSED** | 狭義の矛盾は解消。52ヘッダは Phase 7 の ECO 行記録を要求し、Phase 7 手順5–6、register テンプレの verification 参照と整合する。ただし ECO 行の構造がない別欠陥は新規所見 ECO056-IA-02。 | `method/templates/52-metrics.yaml:9-12`、`method/prompts/phase7-change-order.md:19-20`、`method/templates/60-change-register.yaml:25-31` |
| ECO055-IA-04 | **CLOSED** | equip 認定=最低ラインという成立済み制度の表現は削除され、限定資格制度・routing 昇格基準が制定保留であると明記された。equip-02 item 6 および equip-03 の routing 使用禁止・資格制度導出なしと整合する。 | `method/bomdd-playbook-v1.md:371`、`loops/equip-02/review-2026-08-02.md:16,21-26`、`loops/equip-03/protocol.md:24-25,60-62` |
| ECO055-IA-05 | **CLOSED** | 52 timing 行から研究必須条件が分離され、全規模 override として表外に明記された。「基準線3ループ」も、完全分解1系列・概算1・再利用1へ訂正。transfer-02 は詳細分解、cli-cad-01 は概算時刻、equip-01 は transfer データの再利用。 | `method/bomdd-playbook-v1.md:787-789`、`loops/transfer-02/t2-time-decomposition.md:11-28,47-59`、`loops/cli-cad-01/report.md:60-62`、`loops/equip-01/measurements.md:331-347` |
| ECO055-IA-06 | **PARTIAL** | 引用先は実在する正しい文書へ変更されたが、引用は主張全体を支えない。台帳#4 t2行と t2-report は「haiku採用」と「補償機構」を記録する一方、補償対象は担当者 sonnet の自発性低下である。haiku の `3/16 specified_contract_miss` は別の Plm P2 系列で、指定外の台帳#5にある。「contract miss 実績のある haiku を採用し続けて、その miss を補償した」という因果鎖は未証明。 | `method/bomdd-playbook-v1.md:371`、`loops/equip-01/measurements.md:333-339,350-356`、`loops/transfer-02/t2-report.md:3-5,23-34` |
| ECO055-IA-07 | **PARTIAL** | 「導出可能」の主張は削除され、ruling ID・集計規則が未定義と明記された。TimetableAdv の対象2ファイルは各自の HEAD と blob hash が一致し非0値も保存。ただし TimetableAdv 全体は own HEAD に対して clean ではなく `502 modified + 364 untracked`。対象記録の非接触は確認できるが「製品作業ツリー全体が不変」は確認不能。 | `method/templates/52-metrics.yaml:39-41`、TimetableAdv HEAD:`bomdd/52-metrics.yaml:69,87,105`、TimetableAdv HEAD:`bomdd-kit/method/templates/52-metrics.yaml:28` |
| ECO055-IA-08 | **CLOSED** | 「同じ4キー」は「意味上近い4指標」へ縮小され、`regressions`/`regression` の名称不一致も明記された。 | `method/improvements.md:5915-5917` |

## 2. 任務B 新規所見

**ECO056-IA-01 - high - 機械被覆を「C4のみ」とした訂正が実装と異なる**
再現条件: `52-metrics.yaml:15` の被覆説明と `self-conformance.py` の C1/C4 を突合。
実測結果: C1 は `method/**/*.yaml` を直接列挙し原本テンプレ自体を厳格parseする。C4は`bomdd-init`が生成した製品/kit物を後からparseする。正確な説明は「意味consumer不在。構文被覆はC1の原本parseとC4の生成物parse」であり「C4のみ」ではない。
該当行: `method/templates/52-metrics.yaml:15`、`method/tools/self-conformance.py:172-180,226-270`、`method/tools/bomdd-init.py:45-46,161-166,305-309`
是正提案: ヘッダを「意味consumer 0 / C1=原本構文 / C4=生成物構文 / 列意味は未被覆」に訂正。

**ECO056-IA-02 - high - ECO行の記録契約がコメントだけでYAML構造も機械検査もない**
再現条件: Phase 7手順5–6、register verification、52テンプレ実フィールド、C3検査を突合。
実測結果: Phase 7とテンプレは5分類のECO行記録を要求するが、52テンプレの`metric_runs`には標準フィールド・ECO ID・参照欄が存在しない。C3はverificationの非空だけを確認し、52への参照実在は検査しない。YAML parserはキー欠落を検出しないため、ECO行未記録が構文PASSのまま通る(fail-open)。
該当行: `method/prompts/phase7-change-order.md:19-20`、`method/templates/60-change-order.md:63-74`、`method/templates/60-change-register.yaml:25-31`、`method/templates/52-metrics.yaml:17-68`、`method/tools/self-conformance.py:214-223`
是正提案: 52に標準ECO行形(eco_id・5分類件数・under/over-inclusion・61/63/受入証拠参照)を追加し、C3等で参照実在と必須キーを検査する。

**ECO056-IA-03 - medium - haikuのcontract missとtransfer-02補償機構を別系列から接合**
再現条件: §5.2の一文を指定2出典だけで再構成。
実測結果: transfer-02の「補償機構」は担当者sonnetの自発性4項目を工程ゲートが補った観測。haikuの`3/16 specified_contract_miss`は別系列(webapi-02のPlm P2)で、transfer-02の観測ではない。現行文は別系列のmissと補償を一つの実証鎖のように提示している。
該当行: `method/bomdd-playbook-v1.md:371`、`loops/equip-01/measurements.md:338,350-356`、`loops/transfer-02/t2-report.md:4,23-34`
是正提案: 「Plm P2ではhaikuのcontract missがドメイン非一様」「transfer-02ではhaiku採用時に担当者側の自発性低下を工程ゲートが補償」と別文・別出典に分離。

**ECO056-IA-04 - medium - 影響なし予測がテンプレ索引の同期対象を落としている**
実測結果: 52ヘッダは役割を「Phase 5計器」から「Phase 5＋Phase 7 ECO行」へ拡張したが、`method/templates/README.md`は現在も「Phase 5測定」とだけ記載。§2はREADMEを影響集合に含めておらずunder-inclusion。
該当行: `method/templates/52-metrics.yaml:9-12`、`method/templates/README.md:30`、`method/prompts/phase7-change-order.md:20`
是正提案: README該当行を「Phase 5測定＋Phase 7 ECO受入記録」等へ同期。

**ECO056-IA-05 - medium - OBSの結論が新しい52ヘッダと再び矛盾する**
実測結果: OBS-20260903-02は名称差を正しく縮小したが「正本は61/63/registerにあり52へは集約しない」との旧結論を残す。52ヘッダは「詳細は61/63が正本だが件数と参照は52へ記録」と明記しており、「詳細は」の限定がないOBS文と食い違う。
該当行: `method/improvements.md:5915-5917`、`method/templates/52-metrics.yaml:9-12`
是正提案: OBS末尾を「詳細の正本は61/63/register。52にはPhase 7正典に従い件数と参照のみを記録」に同期。

**ECO056-IA-06 - low - 「observedのみ」が時間テンプレの来歴区分と曖昧に衝突**
実測結果: §11表外注記の全規模override自体は妥当だが、「observedのみ」の文言は時間規律(タイムスタンプ=observed、区間の意味付け=derived/classified)や`self_reported_s`保持可能との整合が曖昧。
該当行: `method/bomdd-playbook-v1.md:789`、`method/onboarding/transfer-test.md:59-60`、`method/templates/52-metrics.yaml:42-67`
是正提案: 「必須測定はobserved timestampを入力とし、区間分類はderived/classified。self-reported単独では充足しない」と明記。

### 非所見として確認した事項
- YAML validity: `python -B`で`yaml.safe_load`成功、`YAML_OK dict ['bomdd', 'metric_runs'] 1`。
- raw_matchの3列非加算説明は各列の意味と整合。
- §11の「完全分解1系列・概算1・再利用1」は証拠文書と一致。
- `git diff --check 13cca3d 58dd2bb`は出力なし。
- `13cca3d→58dd2bb`は5ファイル(58 additions/23 deletions):製造対象=`method/templates/52-metrics.yaml`、`method/bomdd-playbook-v1.md`、`method/improvements.md`/台帳=`bomdd/60-change-order-eco-056.md`、`bomdd/60-change-register.yaml`。`58dd2bb→3e6c5f5`は上記2台帳のみ。兄弟リポのパスはBomDDのdiffに含まれない。

## 3. 検出力の限界
- strict read-onlyのため`method/tools/self-conformance.py`は実行せず、C4の実装読解と52 YAMLの直接メモリparseで代替した。
- ECO-056の受入節・receipt・register verification/diff_auditは情報遮断対象として不読。
- TimetableAdvは検査時点で`502 modified/364 untracked`。対象2ファイルはown HEADとhash一致だが、作業ツリー全体の変更時期・主体・ECO-056との因果は判定不能。
- 静的探索(`rg`)で意味consumerを検出しなかったが、動的組み立てツールや非公開リポのconsumerは被覆外。
- 実到達モデルのprovider-side snapshot IDは取得不能。

## 4. 遵守申告
- 開示パケットを最初に読んだ。
- `bomdd/60-change-order-eco-056.md`の§3〜§5および receiptは**開いていない**。パス名とdiff統計のみ観測。
- `bomdd/60-change-register.yaml`のECO-056 verification/diff_auditフィールドは**開いていない**。
- `method/improvements.md`は開示されたOBS-20260903-02の3行以外の2026-09-03節を**開いていない**。
- リポジトリへの作成・変更・stage・commitは**0件**。
- 使用モデル: Codex / GPT-5(自己申告)。

---

## 5. 受理側の突合(2026-09-03・claude-fable-5-1・真正判定)

| ID | sev | 受理側判定 | 接地方法 | 受理側の実測 |
|---|---|---|---|---|
| ECO056-IA-01 | high | **CONFIRMED** | コード読解 | self-conformance.py C1(`c1_yaml`)は `method/**/*.yaml`+`bomdd/**/*.yaml` を列挙し `strict_yaml_load` — 原本テンプレを直接厳格 parse する。当方の「被覆は C4 のみ」は再び帳簿代用(検査 ID の取り違え)。正しくは「意味 consumer 0 / 構文被覆= C1(原本)+C4(生成物)/ 列意味は未被覆」 |
| ECO056-IA-02 | high | **CONFIRMED(事実)・処置は裁定** | コード読解 | C3 は `verification` の非空とプレースホルダ判定のみ(:214-223)。52 に ECO 行の標準形は無い。**ECO-056 が持ち込んだ欠陥ではなく既存**(52 は当初から ECO 行構造を持たず、phase7 prompt は散文で要求)。是正提案は 52 の schema 追加+C3 拡張= **設備追加** → 本 ECO の範囲外として裁定点へ |
| ECO056-IA-03 | medium | **CONFIRMED** | 一次記録読解 | equip-01 台帳 #5「webapi-02: haiku= 3/16(specified_contract_miss)」・t2-report §2「補償機構= 担当者 sonnet の自発性 4 項目をゲートが補償」。当方の §5.2 文は別系列の miss と補償を 1 つの因果鎖に接合していた(ECO055-IA-06 の PARTIAL と同根) |
| ECO056-IA-04 | medium | **CONFIRMED** | grep | templates/README.md:30「Phase 5 測定」— 52 ヘッダの役割拡張(Phase 7 ECO 行)に未同期。§2 影響なし予測の under-inclusion(README は allowed_paths 外 → **窓の拡張が要る**) |
| ECO056-IA-05 | medium | **CONFIRMED** | grep | OBS-20260903-02 末尾「正本は 61/63/register にあり 52 へは集約しない(ECO-055 4-A)」が残存。IA-08 の縮小で名称のみ直し結論を直していない |
| ECO056-IA-06 | low | **CONFIRMED** | 実文読解 | §11 表外注記「observed のみ」は 52 timing の来歴区分(timestamp= observed / 区間分類= classified)と表現が曖昧 |
| 055-IA-01/06/07 PARTIAL | — | **受理** | — | IA-01/06 は上記 056-IA-01/03 で閉じる。IA-07 の TimetableAdv 作業ツリー汚れ(当方実測 555 件)は本 ECO と無関係の既存状態 — 対象 2 ファイルの blob 一致で非接触は確認済み。限界として記録 |

**集計(evidence class 併記)**: 前回 8 所見= CLOSED 5 / PARTIAL 3(いずれも新規所見へ接続)。新規 6 提起 / CONFIRMED 6(コード読解 2・一次記録読解 1・grep 2・実文読解 1)/ 誤検出 0 / うち **ECO-056 が持ち込んだ欠陥= 5(IA-01/03/04/05/06)・既存欠陥の指摘= 1(IA-02)**。
**process decision**: REJECT を受理。ECO-056 は in-progress のまま**第 2 ラウンド fix**(IA-01/03/04/05/06・テキスト是正・templates/README を窓に追加)を行い、IA-02 は設備追加のため**別途裁定**(別 ECO 起票 / watch / 見送り)。verified 昇格は第 2 ラウンド後の再検査結果に従う(先例 ECO-019: 4 ラウンド)。
**受理側の教訓(候補)**: 2 ラウンド連続で「検査 ID・出典の取り違え」(C4 のみ / FINDINGS §11 t2 / 別系列の接合)が当方の記述に混入 — 是正文を書くとき、引用先を**開いて読み直さずに記憶で書く**機序。較正 receipt の asked はこれを検出しない(3 例目候補・OBS-20260902-02)。
