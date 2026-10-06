[INFORM / COMPLETE]

ACCEPT

- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- HEAD at start / at end: ee5eec6274cfc61410226bd738188b0f3774e185 / ee5eec6274cfc61410226bd738188b0f3774e185
- commit: 0 / ファイル変更: 0（開始・終了時とも `git status --short` 出力なし）
- 写しの sha256 の照合: 7 本すべて一致
  - `viewtube-32-mbom-invariant-entries.txt`: `7e78a63bfe1d1b7cf241478ca13d3ebbccee3dd2bd03213c2e9610c003ba5456`
  - `viewprism2-32-mbom-invariant-entries.txt`: `6daf9821646e22207b80c1a7be5a6ac2a9d80585b8ecd1c7cae73ebfd206bf6d`
  - `viewtube-eco-ids-of-the-entries.txt`: `222e7980ec4c88b24f455d384b7b4a51ca1e62581e8e25654b60b0082e48d08c`
  - `viewtube-eco-vt-232-body.md`: `57a637b4295c60f8cc752f8671d192d2886ff38a74a288e94af93e00ecff8c57`
  - `viewtube-register-eco-vt-232.yaml`: `9b80df3b7c63a466e986cc38702d19e95ac0812b812a7d540bf81678a2d56543`
  - `viewtube-33-known-limits-lines.txt`: `53e08aacfc864bd77acb220eb06c5fecb1b6b8d61876b3d88286d3ebcecb4bb0`
  - `viewtube-31-kbom-measured-lines.txt`: `ea5429c6982d6b125a55268a4ff19f2336618694208ca299639f491df732f413`

## 項目ごとの判定

| # | 項目 | 判定 | 根拠(file:line・コマンドと出力の要点) |
|---|---|---|---|
| 1 | 範囲 | PASS | `git diff --stat/name-status 37c4f82…ee5eec6` は19パスで、すべて register の `allowed_paths`（`bomdd/60-change-register.yaml:3249`）内。playbook の `git diff -U0` は旧348行・356行の2 hunkだけで、いずれも §4.5 内。§4.4・§9・§13 に差分なし。 |
| 2 | V1 の句 | PASS | §4.5（`method/bomdd-playbook-v1.md:341-361`）内の単純一致件数は、`変更記録(60 番台: ECO 本文と台帳)` 1、`ECO 番号の参照だけを残す` 1、`known_limits` 3、`M-BOM の記録句` 1、`ECO-102` 1、`**未測定**` 1、`置き場は**未決**` 0。見出しL344は candidate のまま。 |
| 3 | 記録との一致 | PASS | order `:23-32`、playbook `:350-352`、register `:3240-3242`、improvements `:8426` の値は `measurements.txt` と一致：ViewTube `128/87/87/17/54/5/14`、ViewPrism2 `63/0/15/0/0/0/1`、由来26号すべて body/register あり、本文語彙 `26/26/13/20`、Control Plan `42特性/15行/known_limits 7`、As-Built `244行/8件/最終更新2026-07-25`、K-BOM該当2行。効果・他製品への一般化はなく、1製品・読みだけ・未測定が明記されている。 |
| 4 | 既存本文との整合 | PASS | `known_limits` は検査行内（`33-control-plan.yaml:47-49`）で、検査対象との結線を担う `invariant_refs`（`:34-36`）を置換しない。検査しない不変条件の理由を仕様側へ書く規則とも、行自身の未測定条件を記す欄として両立。§13 `:1143-1149` の記録の経済・正本一つと参照の形に整合。As-Built の `test_evidence_refs`（`50-as-built.yaml:32-40`）は個体ごとの再測定結果で、検査行の能力限界とは役割が重ならない。ECO-086/098/100 の candidate と矛盾なし。 |
| 5 | テンプレの健全性 | PASS | 指定された `python -c` で32・33とも `yaml.safe_load` 成功。差分は32のコメント、33の `known_limits: []` とコメントだけ。新欄は主検査行 `characteristics[0]` 内。表示パリティ行は他の共通欄も省略した簡略例であり、新欄がないことは不整合ではない。 |
| 6 | 言い回し | PASS | §4.5 L348で四種の具体例とともに局所名「M-BOM の記録句」を定義しており、ECO-100 IA-01を回収。一般的な変更記録や§13の「記録」と区別して一意に読める。 |

## 所見(IA-01, IA-02, …)

- IA-01 — CLOSED。7写しすべての独立計算 SHA-256 が `measurements.txt` 記載値と一致。
- IA-02 — CLOSED。全要素写しがあり、項目単位の再計数結果と記録が一致。
- IA-03 — CLOSED。K-BOM の該当2行は知識の名称・文であり、日付・値・版を持つ実測記録ではない。
- IA-04 — CLOSED。製造物の配置・テンプレ構造に blocking 不整合なし。
- IA-05 — CLOSED。order `:36-37` は「完全に持つ」を、26号の body/register 存在と本文語彙の計数へ縮小し、個々の記録の完全収載は未測定と明記。
- IA-06 — CLOSED。order `:44` は「ViewPrism2 は由来のみ」を、`実測値・所見・未検査 0 / ECO参照15 / 裁定1` に置換し、排他の矛盾を解消。
- IA-07 — CLOSED。order `:95-96` は現存する7写しを正しく列挙し、削除済み旧写し名は訂正履歴に限定。
- 新規所見: なし。

## 検査しなかったこと(限界)

- ViewTube / ViewPrism2 のリポ本体は読まず、BomDD 内の測定記録と写しだけを検査した。
- `self-conformance`、worklist、CI、ビルド、テスト、外部 API は実行していない。
- brief に記された旧名 `viewtube-32-mbom-invariant-lines.txt` は現存しないため、order §4と `measurements.txt` が指定する後継の全要素写し `viewtube-32-mbom-invariant-entries.txt` を照合した。
- 26本のECO本文すべては写されていない。本文語彙の集計は `measurements.txt`、計数コードの読解、26 IDの存在一覧、およびECO-VT-232の例に限定される。語彙出現数は内容の意味的完全性を証明しない。
- 較正判定: observed / 条件付き適格。Q1・Q3・Q4・Q5・Q9・Q10・Q11 asked、Q2・Q6・Q7・Q8 NA。計器欠陥なし。未測定次元は上記の26本文全件の独立意味照合。

human_action: none。execution: COMPLETE — 指定範囲の独立検査を終了し、blocking / non-blocking 所見ともにありません。