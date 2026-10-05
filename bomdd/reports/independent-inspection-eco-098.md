[INFORM / COMPLETE]

REJECT IA-01

- range: 境界探索
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象 revision: 8d84edb86c85bbd01c94dfb5a3181004c6de602a
- commit: 0
- 外部 API: 呼出しなし
- 読んだファイル一覧: `bomdd/60-change-register.yaml`、`bomdd/60-change-order-eco-086.md`、`bomdd/60-change-order-eco-089.md`、`bomdd/60-change-order-eco-097.md`、`bomdd/60-change-order-eco-098.md`、`bomdd/reports/eco-097-mbom-cp-redesign/` 配下全 14 ファイル、`method/improvements.md`、`method/bomdd-playbook-v1.md`、`method/templates/30-ebom.yaml`、`method/templates/32-mbom.yaml`、`method/templates/33-control-plan.yaml`、`method/templates/34-routing.yaml`、`method/prompts/phase3-design.md`、`method/schemas/draft/README.md`、`method/schemas/draft/bomdd-ref.draft.schema.json`、`method/schemas/draft/ref-edges.draft.yaml`、`method/schemas/draft/id-grammar.draft.yaml`、`method/tools/impact-retrospective.py`、`method/tools/self-conformance.py`
- 開始時 `git status --short`: 出力なし / 終了時: 出力なし

## 判定概要

| 項目 | 判定 | 観測 |
|---|---|---|
| 1. 範囲 | PASS | 差分は allowed_paths 内の 6 ファイル。method/ は指定 3 ファイルのみ。numstat は全ファイル削除 0 行。`git diff --check` も出力なし。 |
| 2. 記録との一致 | PASS | 数値・試行結果・限界は ECO-097 §7・§8 および reports と一致。効果、他製品への一般化、人と検査官の同等性は主張していない。 |
| 3. candidate の表示 | **FAIL** | 3 項とも candidate・N=1 はあるが、§9 の新項だけ「2 製造単位・1 製品」が欠落。ECO-098 V1 の明示条件を満たさない。 |
| 4. 既存本文・テンプレとの矛盾 | PASS | §4.1、§4.4、§4.5、§4.6、§7、§9、§11、§13、30/32/33/34 テンプレと正面矛盾なし。ECO-086 の ID-only 行と両立。phase3-design は新しい所有・結線を説明していないが、逆の作業を指示する正面矛盾ではない。 |
| 5. 機械的健全性 | PASS | 32・33 は PyYAML で読めた。`manufacturing_decisions`=`list`、`when`=`str`、`on_fail`=`dict`、各値=`str`。draft schema は `additionalProperties: true` で新欄を拒否しない。ref-edges/id-grammar と既存 reader に破壊的影響なし。 |
| 6. 言い回しの境界探索 | PASS | 用語は新項と ECO-097 で対応が読める。OBS/ECO/節参照は実在し内容も一致。人の受入、depth G、既存 gate を廃止する文意ではない。`on_fail` の英日対応はテンプレコメントに明記。 |

## 主張と根拠の表(項目 2)

| # | 主張(本文の句) | 根拠の所在 | 一致 / 不一致 / 根拠なし |
|---|---|---|---|
| 1 | ECO-097 試行は N=1・2 製造単位・1 製品 | ECO-097:1、§7:137–143、§8:177–181、preregistration.md | 一致 |
| 2 | 一行に複数の約束があると、約束単位の測定不能が行区分に現れない | ECO-097:23、§7 R3、improvements.md:8295 | 一致 |
| 3 | 10/10 の ID で Skip→測定不能・赤→違反、行区分は合格のまま | ECO-097:143、170–172、rehearsal.md | 一致 |
| 4 | refs に入れなかった要求が表から消えた | derivation.md X3:75、improvements.md:8338 | 一致 |
| 5 | trait の対応誤りなら誤った ID を合格と出す | review-and-inspection.md:30–36、derivation.md X1:73 | 一致 |
| 6 | 要求の一部しか測らなくても表は合格と出る | review-and-inspection.md:34–36 | 一致 |
| 7 | ID の一部だけが Skip なら合格のまま | ECO-097:143、172 | 一致 |
| 8 | lazy 遡及では共有行の別 E 品目が「検査なし」と出る | preregistration.md の事前登録 R3 限界、rehearsal.md | 一致 |
| 9 | ViewPrism2 の 6 行は参照化 5・製造手段 1・人へ戻す 0 | ECO-097:141、170、derivation.md:14–26 | 一致 |
| 10 | 対象単位で M が自分の言葉で持つ設計内容は 0 行 | ECO-097:141、170、derivation.md:23 | 一致 |
| 11 | 異系統検査官が 6 行の裁定層上の所在を確認 | ECO-097:170、inspection-report-eco-145-r2.md | 一致 |
| 12 | E-BOM に無いとした行が仕様に存在した | ECO-097:131、178–179、derivation.md:26、improvements.md:8341 | 一致 |
| 13 | 検査官が対応づけの誤り 1 件・漏れ 1 件を検出 | ECO-097:174、178、derivation.md:40・X1/X2、review-and-inspection.md:30–34 | 一致 |
| 14 | 別文脈レビューが blocking 2 件を検出し、自己受入は通過していた | ECO-097:149、174、review-and-inspection.md:40–54 | 一致 |
| 15 | 検査官の審査と人の審査の同等性は未測定 | ECO-097:118、177、181–182、199 | 一致 |
| 16 | 効果量と他製品への一般化は未測定 | ECO-097:177、199、improvements.md:8326 | 一致 |

## 所見

### IA-01 — blocking — §9 の新項に試行規模の一部がない

ECO-098 の V1 は、playbook の追加 3 項すべてについて「candidate と試行の規模（N=1・2 製造単位・1 製品）を明示」することを要求している。

- §4.4 は `candidate・ECO-097 試行 N=1〔2 製造単位・1 製品〕` と明示する（`method/bomdd-playbook-v1.md:170`）。
- §4.5 も同じ規模を明示する（`method/bomdd-playbook-v1.md:344`）。
- §9 は `candidate・ECO-097 試行 N=1` のみで、「2 製造単位・1 製品」がない（`method/bomdd-playbook-v1.md:828`）。

直後の試行結果にも製造単位数・製品数は記載されておらず、当該項単体では規模を復元できない。candidate 表示の欠落に関する指定の REJECT 基準に該当する。

是正案: §9 の見出し句を他の 2 項と同じ `candidate・ECO-097 試行 N=1〔2 製造単位・1 製品〕・ECO-098` にする。

## 範囲外の観察(判定に含めない)

なし。