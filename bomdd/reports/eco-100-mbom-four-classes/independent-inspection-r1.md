[INFORM / COMPLETE]

ACCEPT

- range: 境界探索
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象 revision: `fbd3f4a57bc1e5e4f511b0a83ec1779a8d46e25b`
- 写しの sha256 の照合: 一致
  - `ECO-VT-227.md`: `dc8629bcc3e5fa1cb5c87a8b353caf21154c6e0562579d8268d4d9fce03d5457`
  - `ECO-VT-227-independent-review.md`: `bf4fd410edbbbde98aef4316b2369fbd5035c488203629f0b1d863c2488dd23a`
  - `ECO-VT-228.md`: `6ee35d10ff439113e36d2b2937967d9473886d8c8c8e8297727cf164d8edb047`
- commit: 0
- 外部 API: 呼出しなし
- 読んだファイル一覧: `bomdd/60-change-order-eco-100.md`、`bomdd/60-change-order-eco-099.md`、`bomdd/60-change-order-eco-097.md`、`bomdd/60-change-register.yaml`、`bomdd/reports/eco-099-viewtube-second-example/{preregistration.md,classification-producer.md,inspection-report-r2.md,reconciliation.md}`、`bomdd/reports/eco-100-mbom-four-classes/viewtube-snapshot/{ECO-VT-227.md,ECO-VT-227-independent-review.md,ECO-VT-228.md}`、`method/bomdd-playbook-v1.md`、`method/improvements.md`、`method/templates/{31-kbom.yaml,32-mbom.yaml,33-control-plan.yaml,50-as-built.yaml}`、`method/docs/concept.md`、`method/terminology.md`
- self-conformance: 未実行（任意。既知の C14 環境差を判定から除外）
- 開始時 `git status --short`: 出力なし
- 終了時 `git status --short`: 出力なし
- 終了時 HEAD: `fbd3f4a57bc1e5e4f511b0a83ec1779a8d46e25b`

## 判定概要

| 項目 | 判定 | 観測 |
|---|---|---|
| 1. 範囲 | PASS | 差分 8 パスはすべて ECO-100 `allowed_paths` 内。`method/` は playbook、32-mbom、improvements のみ。playbook の hunks は §4.5 の対象項 L344–356 のみ。§4.4、§9、33-control-plan は差分 0。 |
| 2. V1 の句 | PASS | `ECO-098 / ECO-100`、`句の単位で 4 つに分ける`、`置き場は**未決**`、`コードを読んで確かめてから`、`**未測定**` は各 1 件。candidate、2 製品、ViewPrism2 2 単位、ViewTube 3 単位を見出しに明示。実証済み・効果保証への格上げなし。 |
| 3. 記録との一致 | PASS | 追加・変更された事実主張は ECO-097、ECO-099、register、ViewTube 写しと一致。異系統でない ViewTube レビューを「異系統」とする記述、実行確認済みとの記述、効果・一般化の断定はない。 |
| 4. V4・境界整合 | PASS | 層の所有、個別承認対象外、人へ戻す 3 種、lazy 遡及、§4.4、§7、§8、§9、§13、31/32/33/50 テンプレとの正面矛盾なし。ECO-086 の「各行は ID を先頭に」と、句単位の内容分類は両立する。既存テンプレに「記録」の一意な置き場を決める規定なし。 |
| 5. V2 | PASS | `32-mbom.yaml` は PyYAML `safe_load` 成功。変更行はすべてコメントで、非コメント変更 0。コメントに `句の単位` と `記録` を含む。 |
| 6. 言い回しの境界探索 | PASS | OBS-20261005-02/-03、OBS-20261006-01、ECO-VT-227、§7、§9 は実在し参照内容も対応。①書かない、②書き戻してから消す、④決まるまで区別して残す、の対象区分は分離されている。「コードが既にある場合」の限定と初回導出の未測定も明示。ECO-098 原文は実際に「各行は 3 つに分ける」であり訂正注記は正確。non-blocking 1 件は所見欄。 |

## 主張と根拠の表(項目 3)

| # | 主張(本文の句) | 根拠の所在 | 一致 / 不一致 / 根拠なし |
|---:|---|---|---|
| 1 | ViewPrism2 2 単位、ViewTube 3 単位、計 2 製品 | `bomdd/60-change-order-eco-097.md:137-170`、`bomdd/60-change-order-eco-099.md:55-65` | 一致 |
| 2 | ViewTube の対象は 3 単位15行 | `bomdd/60-change-order-eco-099.md:55-65` | 一致 |
| 3 | 混在行 6/15・8/15 | `bomdd/60-change-order-eco-099.md:64`、`reconciliation.md:39` | 一致 |
| 4 | 「記録」の句 7・15 | `bomdd/60-change-order-eco-099.md:59,63`、`reconciliation.md:9-12,34` | 一致 |
| 5 | 「記録」は実測値・レビュー所見・未検査注記・ECO/裁定の由来 | `reconciliation.md:34-35`、`classification-producer.md:28-35`、`inspection-report-r2.md:46-61` | 一致 |
| 6 | 「記録」の置き場は未決 | `reconciliation.md:35`、`method/improvements.md:8373` | 一致 |
| 7 | 統括 AI 42句・検査官63句 | `bomdd/60-change-order-eco-099.md:59`、`reconciliation.md:9-12` | 一致 |
| 8 | 人へ戻す内容の一致3件・不一致2件・統括AIの誤り1件 | `bomdd/60-change-order-eco-099.md:60-61`、`reconciliation.md:27-30` | 一致 |
| 9 | 行ごとの区分集合の一致 7/15 | `bomdd/60-change-order-eco-099.md:65`、`reconciliation.md:61` | 一致 |
| 10 | 分類は分類者と句の切り方に依存する | `bomdd/60-change-order-eco-099.md:65,95,100`、`reconciliation.md:61` | 一致 |
| 11 | ViewTube は M-BOM 114行・E-BOM 48行 | `bomdd/60-change-register.yaml:3166`、`bomdd/60-change-order-eco-099.md:4` | 一致 |
| 12 | 人が「そのまま書き戻す」と裁定した4件 | `ECO-VT-227.md:39-43` | 一致 |
| 13 | 4件中1件でコードが M-BOM の文どおりに動かない経路を発見 | `ECO-VT-227.md:81-82`、`ECO-VT-227-independent-review.md:12-18`、`ECO-VT-228.md:12,37` | 一致 |
| 14 | 発見はコードの読みで、実行していない | `ECO-VT-227.md:27,81,83`、`ECO-VT-227-independent-review.md:3-4` | 一致 |
| 15 | 当該文を外し、別 ECO にした | `ECO-VT-227.md:42-43,82,90`、`ECO-VT-228.md:1,12` | 一致 |
| 16 | M-BOM の `forced` は未定義 | `ECO-VT-227.md:20,81,84` | 一致 |
| 17 | 担当の `forced` の言い換えはコードと違った | `ECO-VT-227.md:20,84` | 一致 |
| 18 | 人の裁定でコードの意味まで仕様に書いた | `ECO-VT-227.md:88,94` | 一致 |
| 19 | 裁定層の文は M-BOM の行より細かくなった | `ECO-VT-227.md:88` | 一致 |
| 20 | D1～D3 の全句は M-BOM と同じでコードとも合った | `ECO-VT-227.md:83` | 一致 |
| 21 | M-BOM・製品コード・検査コードは変更していない | `ECO-VT-227.md:54,75,88,98` | 一致 |
| 22 | 書き戻した句を ViewTube の M-BOM から消していない | `ECO-VT-227.md:48,54,75,88,98` | 一致 |
| 23 | ViewTube のレビュー担当は製造担当と別文脈だが異系統ではない | `ECO-VT-227-independent-review.md:1-4`、`bomdd/60-change-order-eco-100.md:42` | 一致 |
| 24 | ViewTube のコード突合は読みだけ | `ECO-VT-227.md:27,81,83,88` | 一致 |
| 25 | ViewPrism2 6行は参照化5・製造手段1・人へ戻す0 | `bomdd/60-change-order-eco-097.md:141,170` | 一致 |
| 26 | ViewPrism2 では異系統検査官が6行の所在を確認 | `bomdd/60-change-order-eco-097.md:170` | 一致 |
| 27 | ECO-098 は「各行は3つに分ける」と記載していた | `git show 569a4bc:method/bomdd-playbook-v1.md` 対象項、現行 playbook `:349` の訂正注記 | 一致 |
| 28 | 新規 OBS-20261006-01 の1例目は D4、裁定4件中1件 | `ECO-VT-227.md:41-43,81-82`、`method/improvements.md:8392-8394` | 一致 |
| 29 | OBS-20261005-03/-04 は同一単位のため加算しない | `method/improvements.md:8373-8376,8389`、`bomdd/60-change-order-eco-100.md:62` | 一致 |
| 30 | concept/terminology に M-BOM 3分類の別規定なし | `method/docs/concept.md`、`method/terminology.md` に対する `3 分類\|3 つに分\|M-BOM` 検索結果 0 | 一致 |
| 31 | 32 テンプレの「句」「記録」コメント | `reconciliation.md:34-35`、playbook `:346-349` | 一致 |
| 32 | user「A」により記録と playbook 改訂を裁定 | `bomdd/60-change-order-eco-100.md:3,83` | 一致 |

## 所見(IA-NN・blocking / non-blocking・根拠はファイル:行)

- IA-01 — non-blocking: 新設した「記録」は §4.5 内では4分類の一つとして列挙定義されているため判定可能だが、playbook には別の分類軸の「記録」もある（レビュー所見の処置区分: `method/bomdd-playbook-v1.md:794-804`、記録の経済: `:1139-1145`）。将来の改訂では「M-BOM の記録句」など局所名を与えると、§8.5・§13 の一般的な記録概念との取り違えを減らせる。現行文は対象が `invariants` の句であることと具体例を明示しており、正面の矛盾や判定不能には至らない。

blocking 所見なし。

## 範囲外の観察(判定に含めない)

なし。