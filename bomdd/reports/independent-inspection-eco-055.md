# ECO-055 独立受入検査(異系統・Codex・read-only)+ 受理側の突合

> 検査官: Codex CLI(codex:codex-rescue 経由・session 01a063c9-72ad-7db2-8849-f26bd7fcc453・**申告モデル名 GPT-5 (Codex)** — 実到達モデルはランタイム記録で未確認・自己申告)。所要 14m10s。
> 開示範囲: 起票時 order §0〜§2+製造 diff(c692c3c の 52-metrics・playbook)のみ。受入節・較正 receipt・裁定結果・improvements 2026-09-03 節は非開示(遵守申告は §4)。
> 報告本文は Codex の出力を**無改変**で転記(Codex は sandbox の read-only 制約で報告ファイルを書けず、stdout で返した)。受理側の突合は末尾「## 5.」。

# ECO-055 独立受入検査(異系統・read-only)
対象 HEAD: `main` / `6cae16d3b06f84bc2c7fb239d2eaede3599e1f05` / 検査官モデル名: **GPT-5 (Codex)** / 判定: **REJECT**

REJECT は「現在の工程契約上、受入不可」という工程判定であり、製品欠陥一般の証明ではない。対象2ファイルは `c692c3c` から HEAD まで不変であることを `git diff --exit-code c692c3c HEAD -- method/bomdd-playbook-v1.md method/templates/52-metrics.yaml`（exit 0）で確認した。

## 1. 任務A 真正判定表

| 主張 | 接地方法 | 判定 | 証拠 file:line |
|---|---|---|---|
| 全列棚卸しは「計器10列 / 入力2群 / ログ3列」 | コード読解・YAML解析 | **部分的** | `bomdd/reports/52-metrics-inventory-2026-09-02.md:24-50`。集計の計器行には `timing.measurement` も含まれ、キーを字義どおり数えると11。これを来歴群として除外するなら10だが、数え方が未明記。 |
| converge round 1 で棚卸し判定1件を訂正 | 未検証 | **未確定** | round receipt は非開示領域に依存し得るため未確認。内容面は次行で独立検証。 |
| `specified_contract_miss` の消費先は §6.4。BOMを改訂せず `manufacturing_miss` として fresh 再製造 | コード読解 | **CONFIRMED** | `method/bomdd-playbook-v1.md:379,393-404`。実例: `C:\Users\akira\source\repos\BomDD-LibraryLending-Sample\bomdd\52-metrics.yaml:31-39`。 |
| 欠けていたのは工場交換・ティア変更規則。単純能力序列は領域・ドメイン実測に反する | grep・コード読解 | **CONFIRMED** | `method/bomdd-playbook-v1.md:361-369`、`FINDINGS.md:1080-1084,1097-1098`、`bomdd/reports/52-metrics-inventory-2026-09-02.md:54`。ただし「§4.7 注記」は節番号誤りで、実体は §5.2。§4.7 は `method/bomdd-playbook-v1.md:312-343`。 |
| haiku は webapi 3/16・saga 0。transfer-02 でも採用され補償機構が成立 | grep・一次記録読解 | **部分的** | webapi/saga: `FINDINGS.md:151-155,167-175`。haiku採用: `loops/transfer-02/t2-report.md:4`、`loops/transfer-02/intervention-ledger.md:17,19`。補償機構: `FINDINGS.md:642-648`。ただし新段落が引用する `FINDINGS §11 t2` 本文だけには haiku/contract miss の記載がない。 |
| 工場能力の観測値は検査体制込み | grep | **CONFIRMED** | `method/bomdd-playbook-v1.md:369`、`FINDINGS.md:1097-1098`。 |
| raw_match / user_rulings / self_reported_s は治具が書かない手書き列 | grep | **CONFIRMED** | `rg` で `method/tools` の3キー該当0。52名称は `method/tools/stage0-survey.py:6` の由来コメントだけ。 |
| 製品での記入は raw_match が TimetableAdv・LibraryLending、user_rulings 0、self_reported_s 0 | 兄弟リポgrep | **誤り** | TimetableAdv に `user_rulings` の非0記録が多数存在。例: `C:\Users\akira\source\repos\TimetableAdv\bomdd\52-metrics.yaml:58-69,76-87`。self_reported_s は製品実52で0件。 |
| timing 使用実績は transfer-02・cli-cad-01・equip-01 の3ループ | 一次記録読解 | **部分的** | transfer-02 は全数分解: `loops/transfer-02/t2-time-decomposition.md:1-20`。cli-cad は概算時刻のみで分類未実施: `loops/cli-cad-01/report.md:60-62`。equip-01 は同じtransfer t2データを再利用: `loops/equip-01/measurements.md:331-339`。独立した「基準線3ループ」ではない。 |
| 製品3リポの実52に timing キー0 | 兄弟リポgrep | **CONFIRMED** | ViewPrism2 / TimetableAdv / LibraryLending の各 `bomdd/52-metrics.yaml` に対する timing各キーの exact grep は0。凍結 `bomdd-kit` の旧テンプレは製品実記録ではない。 |
| 人間待ち56%・自己申告17倍乖離は §9・§13 に本文化済み | grep・コード読解 | **誤り** | 数値は `FINDINGS.md:655-664,1093-1095`、規律は `method/onboarding/transfer-test.md:59-61`。playbook §9/§13 に対する該当語grepは0。 |
| ViewPrism2 と LibraryLending が独立に同じ4キーを追加 | 兄弟リポgrep・git履歴 | **部分的** | 別リポでの独立追加は確認。しかし ViewPrism2 は `regressions` (`...\ViewPrism2\bomdd\52-metrics.yaml:44,53-56`)、LibraryLending は `regression` (`...\BomDD-LibraryLending-Sample\bomdd\52-metrics.yaml:88-114`)。exact schemaは同一でない。 |
| under-inclusion / 不要改変 / no_impact_prediction / 回帰の正本は61 / 63 / register | コード読解 | **部分的** | 61: `method/templates/61-impact-analysis.md:74-88`、63: `method/templates/63-diff-audit.md:15-31`、no-impact: `method/templates/60-change-register.yaml:25`。registerに専用 regression 欄はなく、verification は52のECO行を参照すると明記: `:31`。 |
| 52はPhase 5計器で、旧テンプレにECOレジーム欄なし | YAML解析・grep | **CONFIRMED** | `method/templates/README.md:30`。`git show c692c3c^:method/templates/52-metrics.yaml` のsafe_load結果にECO4キーなし。 |
| 1-A: user_rulings削除、raw_matchを3列の検算用・単独報告禁止へ変更 | 実プローブ・コード読解 | **CONFIRMED（実装存在）** | safe_load成功、`user_rulings_present False`。`method/templates/52-metrics.yaml:20-24,37`。検算意味の欠陥は IA-02。 |
| 2-A: specified_contract_missの消費先・判断と単軸禁止を明記 | コード読解 | **CONFIRMED（実装存在）** | `method/templates/52-metrics.yaml:25-28`、`method/bomdd-playbook-v1.md:371`。equip認定との矛盾は IA-04。 |
| 3-A: §11にS/M省略可・L推奨・研究必須、閾値なしを追加 | コード読解 | **CONFIRMED（実装存在）** | `method/bomdd-playbook-v1.md:764-787`。基準線と表構造の欠陥は IA-05。 |
| 4-A: 52冒頭にPhase 5 / ECO指標を集約しない旨を追加 | コード読解 | **CONFIRMED（実装存在）** | `method/templates/52-metrics.yaml:9-13`。Phase 7正典との矛盾は IA-03。 |
| 52-metricsを読む治具はstage0-survey.pyのみで、読む列はstage0_topology_health_check | コード読解・grep | **誤り** | `method/tools/stage0-survey.py:1-31` はgit履歴を入力とし、52の出現は由来コメント `:6` のみ。52 YAMLをopen/read/parseする経路はない。 |
| 既存製品記録は変更せず、次回scaffoldへ適用。既存kitはlock凍結、STALEはadvisory | git diff・コード読解 | **CONFIRMED** | `method/tools/bomdd-init.py:143-190`、`method/tools/kit-freshness.py:7-12,135-146`。 |
| playbook変更は§5.2と§11のみ | git diff | **CONFIRMED** | `git diff --unified=0 c692c3c^ c692c3c -- method/bomdd-playbook-v1.md` のhunkは現行 `:371` と `:787` のみ。 |
| stage0列参照ならselftest赤、C13が52参照依存ならFAIL。self-conformanceが観測する | コード読解 | **誤り** | C5は不存在リポのexit 2だけ: `method/tools/self-conformance.py:395-409`。C13はMarkdown link検査でtemplates/bomdd-kitを除外: `:498-550,552-579`。52の列意味を観測しない。self-conformance実行結果自体は未測定。 |

## 2. 任務B 所見

### ECO055-IA-01 — high — 影響なし予測が、実際には52を読まない治具をconsumerとしている

- 再現条件: `rg -n "52-metrics|stage0_topology_health_check" method/tools` とstage0/C5/C13の入力経路を読む。
- 実測結果: stage0の52参照はコメント1行だけ。C5は不存在リポ検査、C13はMarkdown link検査で、52の列削除・意味変更を検出しない。名称参照をconsumerと誤認した帳簿代用であり、影響予測のunder-inclusion。
- 該当行: `method/tools/stage0-survey.py:3-6,27-31`、`method/tools/self-conformance.py:395-409,498-550`。
- 是正提案: consumerを0へ訂正し、実際に被覆するC4の全YAML parse (`method/tools/self-conformance.py:247-269`)と意味被覆なしを明記する。意味回帰が必要なら専用schema fixtureを設ける。

### ECO055-IA-02 — high — raw_matchは3列の「和」を検算できない

- 再現条件: 新コメントと既存製品の同一runを突合する。
- 実測結果: raw 23/23、targeted 1/1、blocker 0、new unspecified 0など、3列は単位も意味も異なり加算関係がない。「和が合わなければ」は実行不能な検算規則。
- 該当行: `method/templates/52-metrics.yaml:20-24`、`C:\Users\akira\source\repos\BomDD-LibraryLending-Sample\bomdd\52-metrics.yaml:31-39,54-63`、`method/bomdd-playbook-v1.md:375-380`。
- 是正提案: 「和が合う」を削除し、単独報告禁止の参考値へ戻す。算術検算が必要なら排他的カテゴリ・分母・算式を持つ別schemaを定義する。

### ECO055-IA-03 — high — 「52へECOを集約しない」がPhase 7正典とregisterテンプレに矛盾する

- 再現条件: 52冒頭コメントをPhase 7 promptとregister templateへ突合する。
- 実測結果: 新コメントはECO指標を52へ集約しないとする一方、Phase 7は52へのECO行記録を要求し、register verificationも52のECO行を参照する。両経路が影響集合から漏れた。
- 該当行: `method/templates/52-metrics.yaml:9-13`、`method/prompts/phase7-change-order.md:19-20`、`method/templates/60-change-register.yaml:25-31`。
- 是正提案: 正本を一意に裁定し、phase7 promptとregister templateを同一ECOで同期する。回帰結果の保存座標も明記する。

### ECO055-IA-04 — high — 「equip認定は最低ライン」と資格制度制定保留が矛盾する

- 再現条件: 新§5.2末文をequip-02/03の凍結裁定へ突合する。
- 実測結果: 新文はequip認定を既存の適格性判定として断定するが、既存裁定は資格制度・routing基準を制定保留とし、各protocolも認定を導出しないとする。未実装の制度を成立済みとして扱う散文契約。
- 該当行: `method/bomdd-playbook-v1.md:371`、`loops/equip-02/review-2026-08-02.md:16-18`、`loops/equip-02/protocol.md:23`、`loops/equip-03/protocol.md:25,62`、`FINDINGS.md:1100`。
- 是正提案: 「equip観測値はrouting根拠にしない」までへ縮小する。資格制度は別ECOでconsumer・対象構成・合否を定義する。

### ECO055-IA-05 — medium — 「基準線3ループ」は測定深度を混同し、研究必須条件がLセル内に埋まる

- 再現条件: transfer-02 / cli-cad-01 / equip-01の時間記録と§11表構造を比較する。
- 実測結果: 完全分解はtransfer-02の1系列。cli-cadは概算、equip-01は同じt2データの再利用。「基準線3」と数えられない。また研究必須がL列セル内にあり、S/M研究への適用が曖昧。
- 該当行: `method/bomdd-playbook-v1.md:775-787`、`loops/transfer-02/t2-time-decomposition.md:1-20`、`loops/cli-cad-01/report.md:60-62`、`loops/equip-01/measurements.md:331-339`。
- 是正提案: 「完全分解N=1 / 部分観測N=1 / 再利用N=1」を分離し、研究条件は全規模overrideとして表外または独立列へ置く。

### ECO055-IA-06 — medium — haiku/contract missの引用座標が主張を単独で支えない

- 再現条件: 引用された `FINDINGS §11 t2` だけでhaiku/contract missを検索する。
- 実測結果: §11.1は補償機構を述べるが、haiku/contract missは述べない。haiku採用はt2-report、過去contract missはFINDINGS §6/§7に分散する。
- 該当行: `method/bomdd-playbook-v1.md:371`、`FINDINGS.md:635-668`、`loops/transfer-02/t2-report.md:4`、`FINDINGS.md:151-155,193-203`。
- 是正提案: 複数の実証座標を明記するか、§11単独で裏付けられる主張へ縮小する。

### ECO055-IA-07 — medium — user_rulingsの「導出可能な件数」に導出規則がない

- 再現条件: 10/20/31テンプレでruling event ID・一件の境界・重複排除算式を検索する。
- 実測結果: 裁定内容の書戻しは規定されるが、件数を一意に導出するschemaがない。TimetableAdvでは実際に非0のuser_rulingsを記録している。削除自体は歴史を消さないが、「導出可能な転写値」という根拠は未証明。
- 該当行: `method/templates/10-requirements.yaml:11-34`、`method/templates/20-spec.md:40-47`、`method/templates/31-kbom.yaml:6-27`、`method/bomdd-playbook-v1.md:382-387,1007-1013,1030-1040`。
- 是正提案: consumer不在を削除根拠に限定する。件数を導出可能と呼ぶならstable ruling IDと集計規則を定義し、実プローブで一致させる。

### ECO055-IA-08 — low — 「同じ4キーN=2」はregressionの単複差を隠す

- 再現条件: 両製品のキーをexact matchで比較する。
- 実測結果: ViewPrism2は `regressions`、LibraryLendingは `regression`。意味上の類似はあるが同一schemaへの独立収束ではない。
- 該当行: `C:\Users\akira\source\repos\ViewPrism2\bomdd\52-metrics.yaml:44,53-56`、`C:\Users\akira\source\repos\BomDD-LibraryLending-Sample\bomdd\52-metrics.yaml:88-114`。
- 是正提案: 「意味上近い4指標（regressionは名称不一致）」へ主張を縮小する。

非所見:

- `PYTHONDONTWRITEBYTECODE=1` で `yaml.safe_load` した結果、`YAML_OK dict ['bomdd', 'metric_runs']`。user_rulingsは不在。
- `user_rulings` のdangling consumerはprompts/onboarding/docs/toolsに検出しなかった。
- raw_matchの単独報告禁止は `method/prompts/phase5-accept.md:20-24`、`method/observation-schema-candidates.md:128,217`、`FINDINGS.md:226` と整合する。
- bomdd-initはscaffold時にmethod全体をコピーしてhashを生成するため、固定manifest/hash更新漏れはない (`method/tools/bomdd-init.py:161-190`)。

## 3. 検出力の限界

- `self-conformance.py` は一時scaffold等を書き込むため、指定報告書以外を書かない制約下では実行していない。self-conformance、stage0 selftest、CIは **UNKNOWN**。
- 外部CI、リモートGitHub、製品build/testは未実施。
- grep該当0は検索語で観測できる参照の不在までで、異名・動的生成・リポ外consumerの不存在を証明しない。
- 指定された4兄弟リポのローカル現存記録を測定した。他製品や未取得branchは未被覆。
- converge round receiptは情報遮断対象に隣接するため未検証。

較正receipt（`/calibrate`）:

| battery | 記録 |
|---|---|
| Q1 | asked — 新散文と実consumer/codeを比較 |
| Q2 | NA — 独立known-good/known-bad対照腕なし |
| Q3 | asked — YAML parse成功を意味被覆へ拡大解釈せず |
| Q4 | asked — stage0名称コメントからeffective inputまでablation |
| Q5 | asked — 未実行検査をUNKNOWN化 |
| Q6 | asked — 後続repo操作・pushなし |
| Q7 | NA — 常設検査器の変更なし |
| Q8 | NA — 新規予防ゲートなし |
| Q9 | asked — HEADとc692c3cの対象個体同一性を確認 |
| Q10 | asked — 本節に限界を宣言 |
| Q11 | asked — 完全分解/概算/再利用、製品実記録/kitを別クラス化 |

文書/YAML/consumer lineageの測定成立性は **observed**、証拠資格は対象範囲に限り **条件付き適格**。self-conformance/CIは **unknown**。

## 4. 遵守申告

- `bomdd/60-change-order-eco-055.md` §3–§6、`bomdd/60-change-register.yaml` のECO-055 verification fields、`method/improvements.md` の2026-09-03節は読んでいない。
- `git diff --name-only` で上記ファイル名が変更集合に含まれることだけは見たが、内容・節・fieldsは開いていない。
- `git show` のcommit subjectに製造者のPASS文言が含まれたが、判定根拠には使用していない。
- リポ内で作成・変更・stage・commit・pushを行っていない。最終 `git status --short` は空。
- Pythonは `PYTHONDONTWRITEBYTECODE=1` でYAMLをメモリ上にloadした。
- 指定報告書への書込みもsandboxに拒否されたため、実際のファイル書込みは0件。

Codex session ID: 01a063c9-72ad-7db2-8849-f26bd7fcc453
Resume in Codex: codex resume 01a063c9-72ad-7db2-8849-f26bd7fcc453

## 5. 受理側の突合(2026-09-03・claude-fable-5-1・真正判定)

判定語は ECO-041 還元の意味論(REJECT= process decision・集計は evidence class+留保併記)に従う。

| ID | sev | 受理側判定 | 接地方法 | 受理側の実測 |
|---|---|---|---|---|
| IA-01 | high | **CONFIRMED** | grep | stage0-survey.py の 52 参照は :6 の由来コメントのみ。YAML を open/parse する経路なし。order §2 の「読取列は stage0_topology_health_check」は**名称参照を consumer と誤認した帳簿代用**。影響なし予測の under-inclusion(実 consumer 0・被覆は C4 の全 YAML parse のみ) |
| IA-02 | high | **CONFIRMED** | 意味論読解 | targeted_fix_success(真偽/比)・blocker_diffs(件数)・new_unspecified_diffs(件数)は加算関係を持たない。「和が合わなければ分解漏れ」は実行不能な検算規則 — 当方の作文誤り |
| IA-03 | high | **CONFIRMED** | grep | phase7-change-order.md:20「metrics(52-metrics.yaml に ECO 行)」・register テンプレ :31「verification: 52-metrics の ECO 行 / as-built」。52 冒頭の「ECO 指標は 52 へ集約しない」は Phase 7 正典と矛盾 — **当方が二重正本を新たに作った**(4-A の裁定「61/63/register を正本」自体が Phase 7 の既存規定を見落としていた) |
| IA-04 | high | **CONFIRMED(留保 1)** | grep | equip-02 review 項 6「限定資格と routing 昇格基準= 趣旨採択・制定は保留」。§5.2 新文「equip 認定は最低ライン(適格性)の判定」は保留中の制度を成立済みとして扱う散文。留保: equip-01〜03 の個別認定(Opus 5 の P2 0/16 等)は実在 — 是正は「制度」でなく「観測値」への縮小で足りる |
| IA-05 | medium | **CONFIRMED** | 一次記録読解 | cli-cad-01 report §6 は概算時刻のみ・equip-01 台帳 #4 は transfer データの再利用。完全分解は transfer-02 の 1 系列。「基準線 3 ループ」は測定深度を混同。研究必須が L セル内に埋まる点も表構造の欠陥 |
| IA-06 | medium | **CONFIRMED** | grep | 当方が「FINDINGS §11 t2 行」と引用した haiku 採用の座標は誤り — 実体は loops/equip-01/measurements.md 台帳 #4 t2 行と loops/transfer-02/t2-report.md:4(当方の grep 出力の出典を FINDINGS と取り違えた) |
| IA-07 | medium | **CONFIRMED** | grep | TimetableAdv 52-metrics に user_rulings = 7 / 1 / 4 の非 0 記録(:69,:87,:105)。当方の「user_rulings 記入 0 リポ」は**自分の grep 出力(TimetableAdv キー一覧に user_rulings あり)の誤読**。「導出可能な転写値」は ruling ID と集計規則が無く未証明 — 削除根拠は consumer 不在に限定すべき |
| IA-08 | low | **CONFIRMED** | grep | ViewPrism2 `regressions` / LibraryLending `regression`。「同じ 4 キー」は名称不一致を隠す。OBS-20260903-02 の文言を縮小 |

任務 A 真正判定表の「誤り」4 件も受理側で再測: ①user_rulings 0 リポ= 誤り(上記)②stage0 の読取列= 誤り(上記)③「56%・17 倍は §9/§13 に本文化済み」= 誤り(playbook に該当語 0・実体は FINDINGS §11/§13 節番号は improvements 側の記述と混同)④「§4.7 注記」= 節番号誤り(実体 §5.2)。「基準線 3 ループ」「4 キー同一」「61/63/register が正本」は部分的。

**集計(evidence class 併記)**: 提起 8 / CONFIRMED 8(grep・コード読解 6・一次記録読解 1・意味論読解 1)/ 留保 1(IA-04)/ 誤検出 0 / 単純再述 0。当方主張の誤り 4・部分的 3。
**process decision**: 検査官の REJECT を受理。ECO-055 の verified は「起票時凍結の受入基準(V1〜V5)に対する判定」として維持(ECO-041 意味論)。ただし受入基準自体が被覆していなかった欠陥(IA-01〜08)は**是正 ECO を別途起票**して閉じる(先例: ECO-015 独立検査 → ECO-016/017)。
**受理側の教訓(候補)**: ①名称参照を consumer と数える帳簿代用(IA-01)②自分の grep 出力の誤読が起票根拠に混入(IA-06/07)— 較正 receipt の asked 4/4 は当方の主張を当方が査定しただけで、いずれも検出できなかった(OBS-20260902-02「asked は弁別力の証明ではない」の 2 例目)③既存正典(Phase 7 prompt)の見落としで二重正本を作った(IA-03)— converge の DoD「正本が一意」を 4-A で問わなかった。
