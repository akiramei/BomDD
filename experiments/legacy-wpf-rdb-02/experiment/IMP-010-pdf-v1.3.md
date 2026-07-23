# IMP-010 — Version 1.3配布PDFを再生成する

## 問題

PostgreSQL第二実験後、Markdown正本はVersion 1.3、配布PDFはVersion 1.2になっていた。PDFだけを見る作業者には、engine別template、復元検査DB、read-only validator、PostgreSQL live Gate検査が伝わらない。

## 今回変更したもの

- Markdown正本Version 1.3から配布PDFを再生成した。
- 一時候補を構造・文字・画像で検査した後、同一hashの候補だけを配布先へ反映した。
- READMEの配布版説明を更新した。

## 今回変更していないもの

- milestone、Gate、artifact、approval、状態遷移。
- 第二実験案件の`migration-status.json`。
- Markdown正本の手順内容。

## 検査結果

| 指標 | 結果 |
|---|---|
| 表紙 | Version 1.3 / PDF generated 2026-07-20 |
| 用紙 / ページ数 | A4 / 35 |
| PDF outline entry | 87 |
| 全文抽出文字数 | 24,869 |
| 最小ページ文字数 | 108 |
| 20文字未満ページ | 0 |
| 必須語句 | Version 1.3、PostgreSQL、`baseline-fixture-postgresql-manifest.json`、`pg_restore`、`default_transaction_read_only`を抽出 |
| 画像化 | 35/35成功 |
| 全ページ目視 | 3枚のcontact sheetで35ページすべてを確認、欠陥0 |
| 重点目視 | 9、10、14、15、31、32、35ページを原寸確認、欠陥0 |
| 生成スクリプト | `py_compile` PASS |
| 候補/配布先hash | 一致 |
| 配布PDF SHA-256 | `61BB5D707301CC30FA9115BF24BB20997D6D937D18D2FA725ED3660B462EC018` |
| 案件status SHA-256 | `05F3A0D798179F8BA8A3206BFCAD0DA4957B8038241158AC3E149185A65AC1A1`（本作業では変更なし） |

## 判定

PASS。PDFスキルのrender-and-verify手順に従い、最新候補の全ページ画像検査後にだけ配布先へ反映した。Version 1.3のMarkdownとPDFの版ずれは解消した。
