[INFORM / COMPLETE]

ACCEPT

- range: ECO-009 r2（是正確認＋回帰）
- inspector: OpenAI Codex（製造者 EQ-004 / claude-opus-5-5 とは別系統）
- 対象 revision: `e252f696014d1e1af4d13f7ea82db5b8fe2280b9`
- r1 対象 revision: `b48a95d`
- 比較基準（変更前個体）: `7c1e157`
- 検査中 commit 数: 0（開始・終了とも HEAD は `e252f69`、`git rev-list --count e252f69..HEAD` は 0）
- 実行環境: Windows / PowerShell 7、Node.js `v22.13.1`、npm `11.5.2`、git `2.47.1.windows.2`、Asia/Tokyo
- ネットワーク呼び出し: なし
- 一時検査ルート: `C:\Users\akira\AppData\Local\Temp\bomdd-plm-eco009-r2-a70a83b333f14f03bf9c7a8e1651759c`
- 開始時 `git status --short`: 出力なし（clean）。ユーザー global ignore への permission warning あり。
- 終了時 `git status --short`: 出力なし（clean）。同 permission warning あり。
- 対象リポ・BomDD リポ・実在製品リポへの編集／commit: なし。検体・旧新実行物・出力は一時検査ルートにのみ作成。

## 判定概要

| 項目 | 判定 | 観測 |
|---|---|---|
| IA-01 r1 検体の再現 | PASS | 合格済み R-050 基礎検体へ `60-change-order-eco-999.md` と `lineage.change_ref: ECO-999` を追加し、`--gate acceptance` で実行。exit 0、R-003 0、MEASUREMENT_FAILURE 0、measurement 0、ECO-999 node 1、edge `resolved:true`。 |
| `60-change-order-eco-vt-025.md` | PASS | `ECO-VT-025` を参照。exit 0、R-003 0、measurement 0、候補 node 1、edge resolved。複合 ID 族を右端から取得した。 |
| `60-change-order-capa-003.md` | PASS | `CAPA-003` を参照。exit 0、R-003 0、measurement 0、候補 node 1、edge resolved。 |
| 右端に ID 族がないファイル名 | PASS | `60-change-order-draft.md` は候補を作らず、ECO-025 は node 0、R-003 1、edge unresolved。右端一致を要求する §2.4 (a) と一致。 |
| ID の後ろに語が続くファイル名 | PASS | `60-change-order-eco-025-draft.md` は ECO-025 を候補化せず、node 0、R-003 1、edge unresolved。`ECO-025-DRAFT` 全体は family pattern に一致せず、右端が ID でないため §2.4 (a) と一致。 |
| 正定義と候補の併存 | PASS | `60-change-register.yaml` と `60-change-order-eco-025.md` を併置。ECO-025 node は 1 件だけで、source は register。R-002/R-003 なし、正定義が優先された。 |
| ファイル名の大小文字 | PASS | `60-change-order-EcO-vT-026.md` から `ECO-VT-026` を生成し参照解決。§2.4 (a) の「大文字化」に一致。 |
| 参照値の大小文字 | PASS | 小文字参照 `eco-vt-027` は、大文字化された候補 `ECO-VT-027` と一致せず R-003。ファイル名だけを大文字化し、参照照合は case-sensitive という仕様境界と一致。 |
| `npm run build` | PASS | exit 0、TypeScript warning 0。 |
| `node --test` | PASS | 155/155 pass、fail 0、cancelled 0、skipped 0。 |
| 固定オラクル | PASS | `cd oracle && node harness/run-oracle.mjs --cli "node ../packages/cli/dist/main.js"` → 49 PASS / 0 FAIL。 |
| self-hosting | PASS | `node packages/cli/dist/main.js . --eco --fail-on error --format json --out <temp>` → exit 0、error 0、warn 0、R-005 info 201、RED 0、MEASUREMENT_FAILURE 0、NOT_APPLICABLE 0、measurement 0。 |
| 区分の割当 | PASS | 独自 M selector-miss 検体で RED 0、MEASUREMENT_FAILURE 3（R-003/R-012/R-050）、原因 3 件はいずれも selector-miss。独自 dangling と既存境界の直接実行では真の未解決を RED として観測。 |
| 抑止 | PASS | `oracle/fixtures/suppress/bomdd-workspace.yaml` を直接実行。抑止対象 R-003 は severity info、`suppressed:true`、reason/ref あり、元判定 `outcome:RED` を保持。X-SUPPRESS-001/002 も RED。 |
| 定義サイトの状態 | PASS | selector-miss、unreadable-input、empty-required-source、定義が残る部分欠落を含む検体が通過。独自 selector-miss 検体では measurement の cause/file/family/rule を直接確認。 |
| R-050 (d) | PASS | M 定義サイト selector-miss＋manufacturing-ready E では error / MEASUREMENT_FAILURE。受入対象 M unit なしでは info / NOT_APPLICABLE。正常証跡検体は R-050 0、exit 0。 |
| measurement と exit | PASS | 他から参照されない M selector-miss 検体を直接実行。always=0、G1=0、G3=1、freeze=1、acceptance=1。diagnostics には全ゲートで R-012 MF と G3 measurement が存在し、適用ゲートから exit に反映された。 |
| JSON Schema 適合 | PASS | PowerShell `Test-Json -SchemaFile` で self-hosting、IA-01、全ファイル名境界検体について diagnostics/graph/ledger を検証。全 27 検証が True。 |
| キー順・ソート・決定性 | PASS | IA-01 合格検体を2回実行。diagnostics、graph、ledger、SARIF の SHA-256 が各々完全一致。`diagnostics.json` は `50988E…A8B280`。 |
| SARIF | PASS | 独自 selector-miss 検体で SARIF 2.1.0、results 5＝diagnostics findings 5、outcome を保持。2回実行の `sarif.json` は byte 同一（SHA-256 `477ACE…99B0B8`）。 |
| text 出力 | PASS | 独自 selector-miss 検体で `区分: RED 0 / 測定不能 3 / 適用外 0` と、selector-miss の原因行 3 本を観測。 |
| 旧新比較: BomDD-Plm | PASS | `b48a95d` / `e252f69` とも exit 0、所見 201、R-005 201、非 R-005 0。区分欄を除いた非 R-005 所見差 0。 |
| 旧新比較: TimetableAdv | PASS | 両 revision とも exit 1、所見 4896、R-005 754、非 R-005 4142、error 2326。区分欄を除いた非 R-005 所見差 0。 |
| 旧新比較: ViewTube | PASS | 両 revision とも exit 1、所見 712、R-005 123、非 R-005 589、error 417。区分欄を除いた非 R-005 所見差 0。 |
| 是正の副作用 | PASS | 3 実在リポすべてで終了コード不変。許容対象の R-005 を除いた所見集合は rule/severity/gate/file/line/column/targetId/message/fixTarget/suppress 欄で完全一致し、差 0。今回は R-005 件数にも差なし。 |
| read-only／作業木不変 | PASS | 終了時 HEAD は `e252f69`、`git status --short` と `git diff --stat` は出力なし。 |

## 所見

所見なし。

## 観測と推測の分離

- 観測: IA-01 の元検体は、是正後 revision で参照解決し、R-003・測定不能とも発生しなかった。
- 観測: 右端に完全な family ID がある場合だけ候補定義となり、ファイル名は大文字化される。後続語がある形は候補化されなかった。
- 観測: 正定義と候補が併存すると、graph には正定義だけが採用された。
- 観測: 標準回帰、固定オラクル、self-hosting、独自区分・exit・出力検体、実在リポ旧新比較はすべて期待どおりだった。
- 推測: なし。判定は上記コマンドの実測結果だけに基づく。