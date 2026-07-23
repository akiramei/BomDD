# IMP-004 — blocker・例外操作をコマンド化する

## 問題

例外カタログと例外票templateは存在したが、例外の登録、分類、owner設定、`blockers`/`non_blockers`/`alternate_safe_work`の更新、解消時の解除はstatus JSONの手編集だった。変更前の凍結工具で`exception-open`を実行するとargparseの`invalid choice`で終了コード2になり、その後の`next`は問題を知らずMIG-20 / STEP-021の通常作業を表示した。

## 今回変更するもの

- `exception-catalog`による凍結カタログ検索。
- `exception-open`による分類、owner、既定処置、三境界、現在位置、証跡hash、open記録の自動登録。
- `exception-safe-work`によるblocker中の限定作業と責任者証跡。
- `exception-resolve`による解消記録、解消証跡hash、status解除、元位置再表示。
- blocker中の通常STEP、通常受入・承認、受入後変更、seal、advanceの拒否。
- non-blocker/defectの同一入口と、未解消時の`next`優先表示。
- 例外記録・証跡の継続的なGate再照合。
- Runbook、例外カタログ、オンボーディングの操作説明。

## 今回変更しないもの

- 技術判断を行うマイルストーンの再配置。
- fixtureとUI証跡の検査幅。
- fresh worker transfer test。
- TraggoのMIG-20以降。
- PDF。

## 安全側の既定値

- カタログが`non-blocker または blocker`ならblockerにする。
- production DB、baseline fixture、current sourceのどれかが`changed`または`unknown`で、元分類がblocker以外ならblockerへ格上げする。
- blocker中のalternate safe workは空を既定とし、責任者が`exception-safe-work`で一作業ずつ許可する。
- 例外中も通常のmilestone/STEPを動かさない。カタログの再開欄は自動ジャンプではなくフォロー先として表示する。

## 合格条件

1. 症状語からcatalog ID、分類、既定処置、再開情報を表示できる。
2. `exception-open`が例外票とstatusを生成し、通常位置を変更しない。
3. blocker中の`complete-step`を終了コード2で拒否する。
4. `next`がowner、既定処置、解消コマンド、許可済み安全作業を表示する。
5. open記録または観測証跡が変わった場合、`exception-resolve`が拒否する。
6. 正しい解消証跡ならblockerと安全作業を解除し、元のMIG-20 / STEP-021へ戻る。
7. non-blockerはGateを止めず、同じ解消操作で履歴化できる。
8. 解消後の記録・証跡変更をGateが検出する。
9. 中央・凍結自己テストがPASSし、正本statusを変更しない。

## 変更前測定

| 操作 | 結果 | 終了コード |
|---|---|---:|
| `exception-open ...` | argparse `invalid choice` | 2 |
| 続けて`next` | 問題を認識せず`[DO] STEP-021` | 0 |

## 変更後試験

正本案件の`bomdd/`を一時領域へ複製し、DB接続失敗を模擬した。

| 操作 | 結果 | 終了コード |
|---|---|---:|
| `exception-catalog --query 棚卸し接続不可` | `EX-DB-001`、blocker、既定処置、STEP-013を表示 | 0 |
| `exception-open EX-DB-001` | 発生ID生成、DB Custodian割当、MIG-20 / STEP-021保存 | 0 |
| blocker中の`complete-step` | active blockerを理由に拒否 | 2 |
| `exception-safe-work` | 一作業とauthorizer証跡を登録 | 0 |
| 観測証跡を差し替えた`exception-resolve` | hash mismatchで拒否 | 2 |
| 証跡を復元した`exception-resolve` | blocker・safe work解除、元STEP表示 | 0 |
| `EX-DB-003`をopen | non-blocker、blocker 0、`next`はYELLOWで既定処置 | 0 |
| non-blocker中のMIG-10 Gate | PASS | 0 |
| `EX-DB-003`をresolve | non-blocker解除、履歴2件 | 0 |

最終状態は`MIG-20 / STEP-021`、blocker 0、non-blocker 0、`exception_history` 2件、status schema `bomdd-legacy-wpf-status/1.2`だった。

追加の負例として解消済み証跡を差し替えると、Gateの`EXCEPTION-SEALS`がFAILして終了コード2になり、`next`は`EX-STATE-001`の登録を指示した。

## 回帰確認

- 中央工具`--selftest`: PASS。
- 凍結工具`--selftest`: PASS、`MIG-20 STEP-021; files unchanged`。
- 正本MIG-10 Gate: PASS。`EXCEPTION-SEALS`、`ACTIVE-BLOCKERS`ともPASS。
- 正本status SHA-256: `1a171e803a9ec4b6f7c0dd84dc4f32bdbc47e5a6e292fa598979f8ef8952c00b`で不変。

## 効果判定

合格条件を満たした。作業者がstatus構造を調べたり、blocker解除条件を設計したりせず、凍結カタログと`next`に従って発生から解消まで進める。通常位置と例外フォロー先を分離したため、例外処置によるSTEP飛ばしも起こらない。

## 残る限界

- 症状に最も近いcatalog IDの選択は人が行う。`exception-catalog --query`は候補を絞るが意味判断はしない。
- 解消証跡の意味的十分性は自動判定しない。
- resolver名と責任者表の割当一致はまだ強制しない。
- カタログにない症状は、最も近いIDまたは`EX-STATE-001`で保全し、カタログ追加を別改善として扱う。
