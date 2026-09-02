# ECO-056 独立再検査 第 2 ラウンド(異系統・Codex・read-only)+ 受理側の突合

> 検査官: Codex CLI(codex:codex-rescue 経由・**申告 OpenAI Codex / GPT-5** — 自己申告)。所要 約 9 分。開示範囲: 起票時 order §0〜§2+第 2 ラウンド製造 diff
> (58dd2bb→86bef4f)+第 1 ラウンド所見 ID。受入節・receipt・§7 仮説節・register verification は非開示。遵守申告に**偶発アクセス 1 件**(rg の除外順序誤りで
> 検査報告・improvements の一致行が出力された — 検査官が自己申告し根拠から除外)。本ラウンドは §7 で凍結した**上限**。報告本文は無改変転記、突合は「## 5.」。

---

# ECO-056 独立再検査 第 2 ラウンド(異系統・read-only)

対象 HEAD: `b4b0f34ad46846d8ad0a2a1634e5b7d33acd87ea`
第2ラウンド fix: `86bef4f39b9465bb087b9ff5886ba13c35349184`
検査官モデル名: OpenAI Codex(GPT-5、自己申告)
判定: **REJECT**

主理由は、README/OBS が「Phase 7 §5–6 に従い、52 の ECO 行へ件数と参照のみを記録する」と新たに断定した一方、引用先は「52 に ECO 行」としか規定せず、さらに playbook §13 の転写禁止と衝突しているためである。IA-02 の別裁定への繰延自体ではなく、繰延中の設計を既定事項として複数箇所へ展開した点を不受理とした。

## 1. 任務A 閉鎖判定表

| 所見 ID | 判定 | 再現条件と実測結果 | 該当箇所 file:line |
|---|---|---|---|
| ECO056-IA-01 | **CLOSED** | C1 は `method/**/*.yaml` を直接列挙して厳格パースする。C4 は `bomdd-init` 生成物の全 YAML を厳格パースし、init は `52-metrics.yaml` を `[0-9][0-9]-*.yaml` として scaffold する。新ヘッダの「C1=原本、C4=生成物、意味未被覆」はコードと一致する。 | `method/templates/52-metrics.yaml:15-16`、`method/tools/self-conformance.py:162-181,226-269`、`method/tools/bomdd-init.py:45-46,304-309` |
| ECO056-IA-02 | **OPEN(別裁定へ繰延)** | Phase 7 は 52 の ECO 行を要求するが、現 YAML は `metric_runs` の Phase 5 系列だけで、ECO 行の構造・必須列・意味検査を持たない。第2ラウンド diff に「IA-02 を閉鎖した」という明示はない。ただし件数・参照という未制定の内容を README/OBS が既定化しており、新規所見 ECO056-R2-01 とした。 | `method/templates/52-metrics.yaml:18-69`、`method/prompts/phase7-change-order.md:19-20`、`method/templates/60-change-order.md:73-74` |
| ECO056-IA-03 | **CLOSED** | Plm P2 の haiku `webapi 3/16・saga 0` は台帳 #5、transfer-02 の「sonnet 側の自発性4項目をゲートが補償」は台帳 #4 t2 と t2-report §2 に正しく分離された。現文は「①の miss を②が補償した因果鎖は測っていない」と明示する。 | `method/bomdd-playbook-v1.md:371`、`loops/equip-01/measurements.md:338,350-359`、`loops/transfer-02/t2-report.md:23-34` |
| ECO056-IA-04 | **CLOSED** | 52 の索引は Phase 5 のみという旧記述から「Phase 5 測定＋Phase 7 ECO 受入記録」へ同期された。 | `method/templates/README.md:30` |
| ECO056-IA-05 | **CLOSED** | OBS は「61/63/register が正本で52へ集約しない」を撤回し、「詳細の正本」と「52には件数と参照」を区別した。後半の根拠問題は新規所見 ECO056-R2-01。 | `method/improvements.md:5915-5917` |
| ECO056-IA-06 | **CLOSED** | §11 注記は「observed のみ」から、timestamp は observed、区間分類は derived/classified、self-reported 単独では不足という契約へ精密化された。52 の来歴欄と一致する。 | `method/bomdd-playbook-v1.md:787-789`、`method/templates/52-metrics.yaml:44-45,59,61-68` |
| ECO055-IA-01 | **CLOSED** | 意味 consumer 不在と、構文被覆 C1/C4 の区別が現行ヘッダとコードの双方で成立した。stage0-survey の 52 参照は由来コメントだけである。 | `method/templates/52-metrics.yaml:15-16`、`method/tools/stage0-survey.py:4-7`、`method/tools/self-conformance.py:172-180,250-267` |
| ECO055-IA-06 | **CLOSED** | 誤座標 `FINDINGS §11 t2` は消え、haiku 採用と補償機構の一次座標へ訂正された。さらに別系列の因果接合も明示的に否定された。 | `method/bomdd-playbook-v1.md:371`、`loops/equip-01/measurements.md:338,355-356`、`loops/transfer-02/t2-report.md:4,23-34` |
| ECO055-IA-07 | **PARTIAL** | 現行52は削除根拠を consumer 不在に限定し、「導出可能」と主張せず、既存製品記録の非接触も明記した。一方、52 が棚卸し元として参照する既存報告には、なお `user_rulings` を「転写値」「導出可能」とする旧主張が残る。第2ラウンド diff に製品リポのファイルは含まれないが、外部製品リポの履歴までは再測定していない。 | `method/templates/52-metrics.yaml:40-42`、`bomdd/reports/52-metrics-inventory-2026-09-02.md:37,56` |

## 2. 任務B 新規所見

### ECO056-R2-01 — high — 「件数と参照のみ」を引用先にない Phase 7 契約として既定化

機序分類: **(i) 引用先を開かず記憶で書いた**

再現条件:
1. 第2ラウンドで追加・変更された README と OBS の「件数と参照のみ」を確認する。
2. 引用された Phase 7 §5–6、playbook Phase 7、order/register テンプレを開く。
3. §13 の転写値規律および現行52の構造と突合する。

実測結果:
- README は `ECO 行= 件数と参照のみ` と断定する。
- OBS は `phase7-change-order.md §5-6 に従い件数と参照のみを記録` と帰属する。
- しかし Phase 7 §5 は失敗分類を規定し、§6 は「`52-metrics.yaml` に ECO 行」とだけ記載する。件数・参照のみという列契約はない。
- playbook も `metrics に ECO 行(52)`、order テンプレも `metrics(52・ECO 行)`、register テンプレも `52-metrics の ECO 行 / as-built` への参照までである。
- §13 は「導出可能なハッシュ・件数・数値は記録しない」と規定する。61/63 の詳細から導出できる件数を52へ転写するなら、明示的な例外裁定が必要になる。
- 現行52には ECO 行の YAML 構造自体がない。このため「件数と参照のみ」は観測済みの実装ではなく、未制定の散文契約である。

引用突合:
- `method/prompts/phase7-change-order.md:19`: 「回帰+変更受入」と失敗5分類。
- 同 `:20`: 「metrics(`52-metrics.yaml` に ECO 行)」。
- `method/bomdd-playbook-v1.md:429-430`: 「失敗5分類」/「metrics に ECO 行(52)」。
- `method/templates/60-change-order.md:74`: 「metrics(52・ECO 行)」。
- `method/templates/60-change-register.yaml:31`: 「52-metrics の ECO 行 / as-built 追記」。
- `method/bomdd-playbook-v1.md:1032-1034`: 「導出可能な…件数・数値は記録しない」。
- 対象断定: `method/templates/README.md:30`、`method/improvements.md:5917`。

是正提案:
別裁定で次のいずれかを確定する。
- 52 に ECO 集計を置くなら、明示的な ECO スキーマ、各値の一次資料参照、必須性、§13 の例外根拠、意味検査を制定する。
- 参照だけを置くなら「件数」を撤回し、Phase 7・52・README・OBS を参照契約へ統一する。
- 52 を参照先にしないなら、Phase 7/register の既存契約自体を一括改訂する。

### ECO056-R2-02 — low — 実差分に列挙外の検査報告追加がある

機序分類: **(iv) その他 — 製造本文と証拠成果物を別扱いしたスコープ会計漏れ**

再現条件: `git diff --stat 58dd2bb 86bef4f` と `git diff --name-status 58dd2bb 86bef4f` を実行し、4本文ファイル＋2台帳と照合する。

実測結果: 実差分は7ファイルであり、列挙された6ファイル以外に `bomdd/reports/independent-reinspection-eco-056.md`(A, 104 insertions)が追加されている。情報遮断条件に従い内容は監査対象にせず、追加という事実だけを測定した。検査証拠の保存自体は合理的だが、凍結影響集合・開示差分との完全一致にはなっていない。

該当行: `git diff --stat/name-status 58dd2bb 86bef4f`

是正提案: 検査報告を evidence-only の許可対象として影響集合に明記するか、製造 fix とは別の台帳・証拠 commit に分離する。

### 新規所見以外の実測

- `52-metrics.yaml` は Python `-B`、重複キー拒否ローダーによるメモリ内ロードで `STRICT_PARSE=PASS`。ルートは `bomdd` と `metric_runs`、`metric_runs` は list。
- `git diff --check 58dd2bb 86bef4f` は出力なし。
- 許可された検索範囲で、旧表現 `C4 のみ`、`52 へ集約しない`、`FINDINGS §11 t2`、`最低ライン`、`基準線 3 ループ`、`observed のみ` の残存は0件。
- `Phase 5 測定` は `method/templates/README.md:30` に残るが、同セルで Phase 7 ECO 受入記録が追加済みであり、旧主張の残存ではない。
- `user_rulings` の旧「導出可能」主張は棚卸し報告に残存するため、ECO055-IA-07 の PARTIAL として扱い、新規所見には重複計上していない。
- 系列分離・timing の引用突合はいずれも支持された(equip-01/transfer-02/equip-02/cli-cad-01 各所)。

## 3. 検出力の限界

- read-only 条件のため `python method/tools/self-conformance.py` は実行していない。C4 は一時ディレクトリへ scaffold するため、コード読解で検証した。
- YAML は対象52だけをメモリ内で厳格パースした。全 YAML・生成物の実行検証ではない。
- `bomdd/60-change-order-eco-056.md` §3–§7、receipt、register の ECO-056 verification/diff_audit は意図的に読んでいない。
- 外部製品リポの既存 `user_rulings` 値や非接触は、今回の Git 差分外であることまでしか再測定していない。
- 追加された独立再検査報告の内容は監査対象から除外したため、ECO056-R2-02 の内容上の影響は判定していない。

## 4. 遵守申告

- リポジトリへの create / modify / stage / commit は行っていない。使用したのは `git show/diff/log/status`、`rg`、`Get-Content`、Python `-B` によるメモリ内 YAML ロードだけ。
- ECO-056 order §3–§7、receipt、register の禁止フィールドにはアクセスしていない。
- **偶発アクセス申告**: 初回の残存検索で `rg` の glob 除外指定順序を誤り、`bomdd/reports/independent-inspection-eco-055.md`、`bomdd/reports/independent-reinspection-eco-056.md` の一致行、および disclosed OBS 以外の `method/improvements.md` 一致行が出力された。直後に条件を修正して再検索し、偶発出力の内容は本判定の根拠から除外したが、これにより完全な情報遮断資格は毀損していることを明記する。
- 指定出力先は書き込み権限がなかったため、本報告を stdout 相当として全文返した。

---

## 5. 受理側の突合(2026-09-03・claude-fable-5-1・真正判定)

| ID | sev | 受理側判定 | 接地方法 | 受理側の実測 |
|---|---|---|---|---|
| ECO056-R2-01 | high | **CONFIRMED** | grep・実文読解 | phase7-change-order.md:20 は「metrics(`52-metrics.yaml` に ECO 行)」のみ。playbook §13 記録規約 第 1 層①「導出可能なハッシュ・件数・数値は記録しない」(:1032-1033)。「件数と参照のみ」は当方が ECO-056 r1(IA-03 是正)で 52 ヘッダに**設計意図から書き**、r2 で README・OBS へ展開した — 引用先に無い契約の既定化(機序 (i))。IA-02(ECO 行の構造未制定)と同根 |
| ECO056-R2-02 | low | **CONFIRMED** | git | `git diff --name-status 58dd2bb 86bef4f` は 7 ファイル。再検査報告(A)は allowed_paths に無い。証拠成果物の窓外追加(会計漏れ) |
| ECO055-IA-07 PARTIAL | — | **受理** | grep | 52-metrics-inventory-2026-09-02.md:37,56 に「転写値」「導出可能」の旧主張が残存。棚卸し報告は歴史的記録だが、当方の r2 read-across(§7 ③)の grep 対象語に `導出可能` を含めておらず、**対象語の選択自体が記憶依存**だった(機序 (iii) の実例) |

**集計(evidence class 併記)**: 前回所見= CLOSED 7 / OPEN 1(IA-02・繰延)/ PARTIAL 1(IA-07)。新規 2 提起 / CONFIRMED 2(実文読解・git)/ 誤検出 0。
**§7 で事前固定した判定基準への当てはめ**: R2-01 の機序は (i) → **(a) 対策仮説の誤り**に該当。IA-07 の残存も (iii) の実例。**上限(第 2 ラウンド)到達・REJECT** → 追加ラウンドは積まず user 裁定へ(§7 凍結どおり)。
**受理側が認める工程欠陥(自己診断)**: §7 の対策 3 つは内容としては正しかったが、**適用範囲を当方が自分で選んだ**(r2 で新しく書いた文だけに①〜③を適用し、r1 で書いて r2 で他所へ展開した「件数と参照のみ」には適用しなかった。read-across の grep 対象語も記憶から選んだ)。つまり欠陥は「検証手順の欠如」ではなく「**検証範囲の自己選択(under-scoping)**」であり、対策を製造者自身が適用する限り再発する。これは ECO-055 で実測した「製造者較正は製造者の前提誤りに盲目」の同型(OBS-20260902-02 の 3 例目)。
