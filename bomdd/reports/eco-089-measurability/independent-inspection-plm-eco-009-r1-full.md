[INFORM / COMPLETE]

REJECT IA-01

- range: ECO-009 r1（境界探索）
- inspector: OpenAI Codex（EQ-004 / claude-opus-5-5 とは別系統）
- 対象 revision: `b48a95d`
- 比較基準: `7c1e157`
- 検査中 commit 数: 0
- 実行環境: Windows / PowerShell 7、Node.js `v22.13.1`、npm `11.5.2`、Asia/Tokyo、ネットワーク不使用
- 一時検査ルート: `C:\Users\akira\AppData\Local\Temp\bomdd-ia-b0439b3337a340acb928a4229aff1115`
- 開始時 `git status --short`: 出力なし（clean）。付随してユーザー global ignore の permission warning あり。
- 終了時 `git status --short`: 出力なし（clean）。付随して同 warning あり。
- 対象リポ・BomDD リポ・実在製品リポへの編集/commit: なし。両 revision は `git archive` で一時領域に展開した。

## 判定概要

| 項目 | 判定 | 観測 |
|---|---|---|
| 正本の byte 複写 | PASS | `git rev-parse 2748359:method/schemas/draft/ref-edges.draft.yaml` と `git rev-parse b48a95d:schemas/ref-v0/ref-edges.draft.yaml` は同一 blob `ddad77dd21b4766d3f1f02b77d9b107d51bcee98`。 |
| `npm run build` | PASS | 一時展開した `b48a95d` で exit 0、TypeScript warning 0。依存は `npm ci --offline --ignore-scripts` で展開。 |
| `node --test` | PASS | `152/152` pass、fail 0、skip 0。 |
| 固定オラクル | PASS | `cd oracle && node harness/run-oracle.mjs --cli "node ../packages/cli/dist/main.js"` → `49 PASS / 0 FAIL`。git ignore warning は出たが判定には影響なし。 |
| self-hosting | PASS | `node packages/cli/dist/main.js . --eco --fail-on error --out <temp>` → exit 0、error 0 / warn 0 / info 208。 |
| 変更前個体の較正 | PASS | `7c1e157` を別一時領域で build 後、`b48a95d:test/measurability.test.js` 相当を実行 → 15 件中 14 FAIL、1 PASS、exit 1。`plm-diag/1`、outcome/measurement 不在を直接観測した。 |
| error/warn と info の outcome | PASS | 独自 dangling + R-050 検体で全 error/warn に outcome。観測専用 R-005 info には outcome なし。 |
| 抑止 | PASS | 抑止された R-003 は severity info へ降格後も `outcome: RED`。X-SUPPRESS-001(error) / 002(warn) も RED。 |
| 複数定義サイト | PASS | FMEA を 32 と 33 の両方の対象にし、32 で 1 定義を残し 33 側を空振りさせた。FMEA measurement 0、参照解決成功。 |
| candidate 定義だけの族 | **FAIL** | `bomdd/60-change-order-eco-999.md`（宣言済み candidate filename 定義）だけで ECO-999 を定義し、30 の `lineage.change_ref` から参照。R-003 warn / MEASUREMENT_FAILURE が誤発火。IA-01。 |
| 複数リポ片側破損 | PASS | workspace の good/bad 2 repo のうち bad の M selector だけ改名。good に M 定義が残るため M measurement 0。 |
| null / scalar / 入れ子 / 空リスト | PASS | `manufacturing_units` が null/scalar/mapping は selector-miss、`[]` は empty-required-source。上流 E 有りでは R-012/R-050 と連鎖が測定不能、exit 1。 |
| R-050(d) 上流なし | PASS | E を draft、M selector-miss とした。R-050 は info / NOT_APPLICABLE、R-050 の MEASUREMENT_FAILURE なし。 |
| R-050(d) 上流あり | PASS | manufacturing-ready E + M の null/scalar/mapping/empty の全形で R-050 error / MEASUREMENT_FAILURE、acceptance で exit 1。 |
| acceptance_refs なし | PASS | 製造者検体の再確認を含む。M が読めて存在する場合は R-050 info / NOT_APPLICABLE、measurement なし。 |
| gate と exit | PASS | 他から参照されない M selector-miss の独自検体: always=0、G1=0、G3=1、freeze=1、acceptance=1。A9 の宣言済み限界と一致。 |
| measurement 単独の exit | PASS | 上記 A9 型で always の error/warn なし・measurement は G3 のため未適用で exit 0、G3 以降は measurement が適用され exit 1。 |
| JSON Schema | PASS | PowerShell `Test-Json -SchemaFile schemas/plm-diag-2.schema.json` で独自 shape-empty の diagnostics.json が True。 |
| キー順・ソート・決定性 | PASS | 独自 dangling 検体を 2 回実行し diagnostics.json byte 同一。既存の schema-order test も pass。 |
| SARIF outcome | PASS | 独自 dangling 検体の error/warning 全 result で `properties.outcome` を確認（RED / MEASUREMENT_FAILURE / RED）。 |
| text 出力 | PASS | `区分: RED 0 / 測定不能 3 / 適用外 0` と 3 本の `測定不能の原因:` 行を確認。 |
| 変更前後の不変性 | PASS | 独自 dangling 検体で outcome 等の新欄を除く rule/severity/gate/file/line/targetId/message と件数、exit は新旧同一（各 exit 1、各 3 所見）。 |
| TimetableAdv 帰属 | PASS | MF の R-003 は DE 2 / FMEA 74 / ROUTE 48。例: ROUTE-SCHEDULE-RUN-SG04-001 は 34 に字面の定義があるが schema の `routing.steps[].id` でなく実物方言に置かれ、FMEA-CONTRACT-001 は `fmea_id` で宣言 selector `.id` と不一致。真の未定義 RED ではなく「宣言済みサイトから読めない」帰属が妥当。 |
| ViewTube 帰属 | PASS | MF の R-003 は CAPA 3 / ECO 10。CAPA-VT-001 と ECO-VT-* は `bomdd/capa/`、`bomdd/eco/`、`bomdd/process/change-register.yaml` に実在するが、宣言サイト `bomdd/60-change-order-*.md` / `bomdd/60-change-register.yaml` ではない。測定不能帰属が妥当。 |
| X-GIT-001 例外 | PASS | 非 git の archive self-hosting `--eco` で X-GIT-001 を 7 件観測。いずれも info、outcome 欄なし、exit 0。仕様 §2.6 と order の宣言どおり。 |

## 所見

| ID | 内容 | 帰属(製造物 / 仕様 / 規則文言 / 計器) | 重さ(blocking / non-blocking) | 再現手順 |
|---|---|---|---|---|
| IA-01 | 宣言済み candidate filename 定義が解決索引に入らない。`60-change-order-eco-999.md` は ref-v0 の candidate fallback 定義サイトであり、正定義が無いとき ECO-999 を解決できるべきだが、R-003 warn が残り、新個体では MEASUREMENT_FAILURE に分類される。観測: graph の ECO node 0、R-003 targetId=ECO-999。比較観測: `7c1e157` でも R-003 と exit は同じで、ECO-009 が新規に作った退行ではない。しかし対象 revision は正本の candidate 意味論を満たさず、境界要求そのものに不適合。 | 製造物 | blocking | clean fixture を一時領域へ複製。`bomdd/60-change-order-eco-999.md` に `# ECO-999` を置き、30-ebom の item に `lineage: { change_ref: ECO-999 }` を追加。`node packages/cli/dist/main.js <fixture> --gate always --format json --out <temp>`。期待: 参照解決、R-003 なし。実測: R-003 warn / `outcome: MEASUREMENT_FAILURE`、exit 0（warn のため）。検体スクリプト: 一時領域の `boundary.mjs`、結果: `boundary-results.json`。 |

## 観測と推測の分離

- 観測: IA-01 の候補ファイルは discovery 上の型付きファイルには数えられるが、graph の ECO node と ID 数には入らず、参照は未解決になった。
- 観測: 旧個体でも同一の未解決所見が出るため、ECO-009 の差分が rule/severity/exit を壊したものではない。
- 推測: filename selector の候補定義が Markdown parse/model 経路で definitions に投入されていない可能性が高い。原因箇所の確定は本検査の判定に不要であり、実装修正は行っていない。
- 観測: 実在リポの「字面の定義」は宣言外のパス/方言にある。したがって、それらを RED（本当に未定義）にせず MEASUREMENT_FAILURE とした ECO-009 の帰属は妥当。

