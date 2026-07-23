# IMP-002 — Gateで受入後の内容変更を検出する

状態: 効果確認済み  
開始日: 2026-07-19

## 対象問題

Gateは成果物・証跡・承認証跡の存在とstatusを確認するが、受入後にファイル内容が変わっても検出しない。

## 仮説

成果物受入時と承認時にSHA-256を保存し、Gateで現在値と再照合すれば、同じパスのファイル内容が変更された場合にGateをFAILにできる。

## 今回変更するもの

- 成果物本体と成果物証跡のSHA-256封印
- 承認証跡のSHA-256封印
- Gateでの封印必須化と再照合
- 既存の受入済みmilestoneを明示的レビュー後に封印する移行command

## 今回変更しないもの

- 証跡内容が主張を意味的に支えるかの判定
- STEP遷移
- blocker・例外操作
- milestoneの成果物構成
- 承認者と責任者表の一致検査
- fixture、UI、PDF

## 変更前試験

1. 実験案件を一時ディレクトリへ複製する。
2. `MIG-10-artifact-review.md`だけを改変個体へ差し替える。
3. `check --milestone MIG-10`を実行する。

結果: 改変した証跡でもGate PASS、終了コード0。変更前Gateはパスとstatusだけを見ており、内容差を検出しなかった。

## 受入条件

1. 変更前の改変個体はGate PASS。
2. 変更後、未封印の受入成果物はGate FAIL。
3. 明示的レビューで既存MIG-00/10を封印すると正常個体はPASS。
4. 同じ証跡差し替えを行った改変個体はhash mismatchでFAIL。
5. 配布元キットselftestと凍結工具selftestがPASS。
6. 改変試験は複製上だけで行い、正本成果物の内容を変更しない。

## 結果

| 試験 | 結果 | 終了コード |
|---|---|---:|
| 変更前・MIG-10証跡差し替え | PASS | 0 |
| 変更後・未封印の既存MIG-10 | FAIL: content hash seal is missing | 2 |
| 明示レビュー後・正常MIG-00 | PASS | 0 |
| 明示レビュー後・正常MIG-10 | PASS | 0 |
| 変更後・同じMIG-10証跡差し替え | FAIL: content hash mismatch | 2 |
| 変更後・MIG-10承認証跡差し替え | FAIL: approval evidence content hash mismatch | 2 |
| 配布元キットselftest | PASS | 0 |
| 凍結工具selftest | PASS | 0 |

正常案件での凍結自己テスト前後status SHA-256:

```text
1a171e803a9ec4b6f7c0dd84dc4f32bdbc47e5a6e292fa598979f8ef8952c00b
```

前後で同一。改変試験は一時複製だけで実行し、正本成果物を変更していない。

## 実装された規則

- `accept-artifact`は成果物本体と全成果物証跡をSHA-256封印する。
- `approve`は承認証跡をSHA-256封印する。
- `check`は全hashを再計算し、未封印、欠落、内容差をFAILにする。
- hash導入前の受入済みMIG-00/10は、`IMP-002-existing-content-review.md`による明示レビュー後に`seal-milestone`で一回だけ移行した。
- Gate result schemaは`bomdd-legacy-wpf-gate-result/1.1`とした。

## 効果判定

仮説を支持する。同じパス・同じstatusのまま証跡または承認証跡の内容を差し替える変異は、改善前のPASSから改善後のFAILへ変わった。正常個体はPASSを維持した。

## この結果から主張しないこと

- 証跡の内容が仕様上十分かを意味的に判断できるとは主張しない。
- 正規の受入後変更・再承認workflowはIMP-003で別途定義・検証する。本実験単独ではその効果を主張しない。
- 承認者名が責任者表の割当と一致するかは検査していない。
- 上記は別の改善実験として扱う。
