# PostgreSQL Gate validation

実施日: 2026-07-19

## 正常系

凍結工具の`accept-artifact ART-DB-BASELINE`を、`BOMDD_POSTGRES_PASSWORD`を実行時だけ設定して実行した。custom dump catalog、復元検査DBのread-only状態、PostgreSQL major version、未検証constraint、無効index、live schema hash、5件のcanonical queryが一致し、受入はPASSした。

## 変異試験

manifestをメモリ上で変更してvalidator関数を直接実行した。DB、dump、追跡対象証跡は変更していない。

| 変異 | 期待 | 結果 |
|---|---|---|
| `BOMDD_POSTGRES_PASSWORD`を未設定 | credential不足でRed | `required credential environment variable is not set`でRed |
| table counts期待値を`999`へ変更 | 実データ差でRed | actual 10列との不一致でRed |
| restore control名と接続先を`traggo_prod`へ変更 | 本番相当DBへ接続できずRed | `permission denied for database traggo_prod`でRed |

結論: 証跡の存在だけでなく、credential境界、接続先権限、復元DBのlive内容を検査している。
