# IMP-003 — 受入後変更を正規手順で閉じる

## 問題

IMP-002後のGateは受入済みファイルの内容差を検出できる。しかし過去MIG-10の受入内容を変えた隔離コピーで`check`を実行すると、FAIL後の`next`は現在位置MIG-20 / STEP-021をそのまま指した。旧受入、旧承認、旧Gateをどう扱い、どこで再検査して通常作業へ戻るかは作業者判断だった。

## 今回変更するもの

- `change-open`、`change-retest`、`change-accept`、`change-approve`、`change-close`の一本道。
- 変更中の通常STEP、通常受入・承認、seal、advanceの停止。
- 受入済み成果物への通常`accept-artifact`、既存承認への通常`approve`、封印済みmilestoneへの`seal-milestone`による迂回の拒否。
- sealからの影響成果物の自動逆引き。共有証跡は複数成果物をまとめる。
- 旧受入、旧承認、旧Gateのsuperseded履歴と置換Gate。
- `status`と`next`による変更位置・次操作の表示。
- Runbook、README、オンボーディングの操作説明。

## 今回変更しないもの

- blocker・例外操作のコマンド化。
- 技術判断を行うマイルストーンの再配置。
- fixture、UI証跡の検査幅。
- TraggoのMIG-20以降の成果物。
- PDF。

## 仮説

受入後変更を一件ずつ状態機械にし、工具が通常作業を一時停止して次コマンドを一つだけ示せば、作業者は過去milestoneの変更でも履歴を失わずに元のSTEPへ戻れる。

## 合格条件

1. hash mismatch後に`change-open`の具体的入口が表示される。
2. 変更中は通常の`complete-step`が終了コード2で拒否される。
3. `next`が再検査、再受入、必須roleごとの再承認、closeを順番に一つずつ示す。
4. close前に置換GateがPASSし、close後は元のMIG-20 / STEP-021へ戻る。
5. 旧受入、旧承認、旧Gateと置換Gateの参照が残る。
6. 共有証跡の変更時は影響成果物をsealから自動特定する。
7. 中央自己テスト、案件凍結工具自己テストがPASSする。
8. 正本案件の`migration-status.json`を変更しない。
9. 通常の再受入、再承認、再sealでは正規手順を迂回できない。

## 変更前測定

正本案件の`bomdd/`だけを一時領域へ複製し、MIG-10の受入証跡を同じパスで差し替えた。

| 操作 | 結果 | 終了コード |
|---|---|---:|
| `check --milestone MIG-10` | hash mismatchでFAIL | 2 |
| 続けて`next` | `[DO] STEP-021`を表示。MIG-10変更の復旧操作なし | 0 |

## 変更後試験

別の隔離コピーで`current-baseline.md`を差し替え、次を順に実行した。正本の成果物内容は変更していない。

| 測定 | 結果 | 終了コード |
|---|---|---:|
| 初回`check --milestone MIG-10` | hash mismatchと具体的`change-open`を表示 | 2 |
| `change-open` | 旧MIG-10承認2件をsuperseded、通常位置STEP-021を保存 | 0 |
| 変更中の`complete-step` | active changeを理由に拒否 | 2 |
| `change-retest` | 新しい再検査証跡hashを保存 | 0 |
| `change-accept` | 影響成果物を新hashで再受入 | 0 |
| `change-approve` Migration Owner | 次roleとしてDB Custodianを表示 | 0 |
| `change-approve` DB Custodian | 次操作として`change-close`を表示 | 0 |
| `change-close` | 置換Gate PASS、変更をclosed | 0 |
| 最終`check --milestone MIG-10` | PASS | 0 |
| 最終`next` | 元のMIG-20 / STEP-021を表示 | 0 |

保存状態:

- `active_accepted_change`: なし。
- `accepted_change_history`: 1件。
- `gate_supersessions[-1].status`: `replaced`。
- 置換Gate: `bomdd/migration/gates/MIG-10-recheck-COR-MIG-10-<timestamp>.json`。

共有証跡`MIG-10-artifact-review.md`を差し替えた追加試験では、`change-open`が`ART-BASELINE`と`ART-CURRENT-OBS`の2件を自動的に影響対象へ入れた。

## 回帰確認

- 中央工具`--selftest`: PASS。
- 中央自己テスト内で、通常の再受入、再承認、再sealの3経路がすべて拒否された。
- 凍結工具`--selftest`: PASS、`MIG-20 STEP-021; files unchanged`。
- 正本status SHA-256（工具同期前後）: `1a171e803a9ec4b6f7c0dd84dc4f32bdbc47e5a6e292fa598979f8ef8952c00b`で不変。

## 効果判定

合格条件を満たした。変更検出だけで停止していた状態から、作業者が`next`を繰り返すことで再検査、再受入、全再承認、置換Gate、元STEP復帰まで完走できる状態になった。旧記録を削除・上書きせず、supersededとreplacementの関係も残る。

## 残る限界

- 再検査証跡の意味的な十分性は自動判定しない。
- 承認者名と責任者表の割当一致は検査しない。
- 同時に開ける受入後変更は一件だけである。迷いを減らすための意図的な制約とした。
- blocker・例外の登録・解除はまだ手操作である。次の独立改善で扱う。
