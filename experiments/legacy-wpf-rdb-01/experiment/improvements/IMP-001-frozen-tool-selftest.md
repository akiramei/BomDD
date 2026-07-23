# IMP-001 — 凍結工具の自己テストを読取り専用で成立させる

状態: 効果確認済み  
開始日: 2026-07-19

## 対象問題

案件へコピーした `bomdd/migration/tools/migration-workflow.py --selftest` が、案件内に存在しない初期化用templateを探して終了コード1になる。

## 仮説

工具が「配布元キット」と「初期化済み案件」を識別し、後者では案件状態を変更しないruntime自己検査を行えば、凍結工具単体の健全性を確認できる。

## 今回変更するもの

- `--selftest` の実行場所判定
- 初期化済み案件用のread-only自己検査

## 今回変更しないもの

- Gate条件
- 成果物受入条件
- STEP遷移
- 例外処置
- template内容
- milestone定義

## 変更前測定

- 凍結工具: FAIL、終了コード1
- 原因: `bomdd/migration/templates/migration-profile.json`を探してFileNotFoundError
- 配布元キット自己テスト: PASS、終了コード0
- 実験status SHA-256: `481ca95d85af00c50ebb24c9f43371d72ab69c25b9bd4b35c69b94c7d4d09e17`

## 受入条件

1. 凍結工具の`--selftest`が終了コード0。
2. 配布元キットの`--selftest`も終了コード0のまま。
3. 凍結工具の検査前後でmigration-status.jsonのSHA-256が同一。
4. Gate、成果物、STEP、承認、blockerを変更しない。

## 結果

| 測定 | 変更前 | 変更後 | 判定 |
|---|---|---|---|
| 凍結工具 `--selftest` | FAIL / exit 1 | PASS / exit 0 | 改善あり |
| 配布元キット `--selftest` | PASS / exit 0 | PASS / exit 0 | 退行なし |
| status SHA-256 | `481ca95d...d09e17` | `481ca95d...d09e17` | 状態変更なし |

変更後出力:

```text
frozen-selftest: PASS - MIG-20 STEP-021; files unchanged
```

## 効果判定

仮説を支持する。凍結工具は、存在しない初期化templateへ依存せず、現在案件のscenario、milestone、STEP、guide、Gate読取りを検査できるようになった。検査は対象ファイルのhashを前後比較し、read-onlyであることも確認した。

## この結果から主張しないこと

- 凍結工具から新しい案件を`init`できるとは主張しない。初期化は配布元キットの責務のまま。
- Gate内容の妥当性、証跡hash、例外操作、transfer testは改善していない。
- それらは別の改善実験として扱う。
