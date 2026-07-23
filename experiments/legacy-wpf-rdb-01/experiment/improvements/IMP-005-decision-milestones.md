# IMP-005 — 技術判断を依存作業の直前へ再配置する

## 問題

旧RunbookのSTEP-003は、現行基準線、棚卸し、仕様復元より前のMIG-00で、.NET、Windows、構造、DI、DB provider/semantics、テスト、配布の8判断をすべて決めるよう要求した。一方、旧Gateはprofileの意味を検査せず、8件すべて`open`の新規案件でもMIG-00 GateがPASSした。

このため、手順どおり情報不足で早期選定するか、未決定のまま依存工程へ進むかを作業者が選ばなければならなかった。Traggo実験では作業継続のため、実験者がMIG-00で先行調査して8件を決めた。

## 今回変更するもの

- MIG-00 profileから8技術判断を除き、制約と責任者だけにする。
- `DEC-DB-SEMANTICS`をMIG-30 / STEP-030へ配置する。
- .NET、Windows、構造、DI、DB provider、テストをMIG-40 / STEP-040へ配置する。
- packaging、signing、install、updateをMIG-80 / STEP-080へ配置する。
- 三つの期限別decision artifactとローカル証跡hash。
- `decision-status`、`decision-record`、`next`による一件ずつの指示。
- 期限前・期限後の記録、owner不一致、案件外証跡、未決定artifact受入の拒否。
- 依存する以後の全Gateによるdecision artifactの累積再検査。
- 旧profileを変更せず移行する一回限りの`adopt-decision-layout`。

## 今回変更しないもの

- fixtureとUI証跡の検査幅。
- fresh worker transfer test。
- TraggoのMIG-20成果物作成。
- client-server RDBの第二実験。
- PDF。

## 配置原則

| 期限 | その時点で得られている入力 | 決めるもの | 直後の依存作業 |
|---|---|---|---|
| MIG-30 / STEP-030 | DB基準線、DB台帳 | DB semantics | requirements、DB compatibility contract |
| MIG-40 / STEP-040 | 現行契約、UI/DB仕様 | WPF実装方式 | E/K/M-BOM、Control Plan、Routing |
| MIG-80 / STEP-080 | 統合個体、install/起動結果、運用制約 | 配布方式 | cutover/rollback rehearsal |

最短化のための並行先行判断は許可しない。判断を一件ずつ期限STEPで記録する方を優先した。

## 合格条件

1. 新規MIG-00 profileに技術判断欄がなく、三成果物には8件が`open`で存在する。
2. 8件openでもMIG-00 Gateは正常にPASSする。
3. MIG-00/MIG-20から期限前の`decision-record`を実行すると終了コード2になる。
4. MIG-30 GateはopenのDB decision setをFAILにする。
5. `next`が期限到来した最初のdecision ID、owner、記録コマンドを表示する。
6. ownerとローカル証跡付きで決定し、decision artifactを受入した後だけSTEP-030を完了できる。
7. 判断証跡変更を期限Gateと以後のGateが検出する。
8. 旧案件のaccepted profile、MIG-00/10 Gate、通常位置を変えずにdecision layoutを採用できる。
9. 中央・凍結自己テストがPASSする。

## 変更前測定

旧templateで新規案件を初期化し、技術判断を一件も変更せずMIG-00三成果物を受入した。

| 測定 | 結果 |
|---|---|
| profile内の`open`判断 | 8件 |
| Runbook要求 | STEP-003で全件決定 |
| MIG-00 Gate | PASS、終了コード0 |

文書とGateが逆方向であり、作業者が判断時期を設計する必要があった。

## 変更後 — 新規案件試験

| 測定 | 結果 |
|---|---|
| profileに`decisions` property | なし |
| 期限別成果物の`open`判断 | 合計8件 |
| 8件openのMIG-00 Gate | PASS、終了コード0 |
| MIG-00で`DEC-DB-SEMANTICS`を記録 | dueはMIG-30として拒否、終了コード2 |
| MIG-30でopenのDB decision set | Gate FAIL、STEP-030完了拒否 |
| MIG-30でowner・ローカル証跡付き記録 | 成功 |
| `ART-DB-TECH-DECISIONS`受入後 | decision set検査PASS、STEP-031へ進行 |
| DB判断証跡の差し替え | evidence hash mismatchでFAIL |
| MIG-40の累積検査 | 既受入DB setはPASS、未決定implementation setはFAIL |
| DB判断証跡差し替え後のMIG-40 | 過去setの変更もFAIL |

中央自己テストは、MIG-40の`DEC-DOTNET`をMIG-30で記録する負例も拒否した。

## 変更後 — Traggo既存案件の移行

新しい凍結tool、milestone definition、guideを配置し、`IMP-005-decision-layout-upgrade.md`を証跡に`adopt-decision-layout`を一度実行した。

- accepted `migration-profile.json`: 内容変更なし。
- 通常位置: `MIG-20 / STEP-021`のまま。
- 新artifact: 3件、statusは`present`。
- 案件内証跡があり移行できた判断: 6件。
- URLのみのため期限時の再確認へ戻した判断: `DEC-DOTNET`、`DEC-DB-PROVIDER`の2件。
- MIG-00 Gate: PASS。
- MIG-10 Gate: PASS。
- status SHA-256: `1a171e803a9ec4b6f7c0dd84dc4f32bdbc47e5a6e292fa598979f8ef8952c00b`から`45e3aa86feb3158e0034199f0f1495dc444d260245e3063a3b20e929c3acb430`へ変更。これは三artifact登録とupgrade history追加による意図した状態変更である。

## 効果判定

合格条件を満たした。MIG-00では情報不足の技術選定を要求せず、依存作業の直前では未決定を機械的に止める。`next`が一件だけ示し、`decision-record`が期限、owner、ローカル証跡を検査するため、作業者が判断時期や担当を設計する必要がなくなった。

## 残る限界

- 技術判断の値そのものの妥当性は責任ownerとレビューが担う。
- 外部URLは根拠の所在としてdecision evidenceへ直接採用せず、案件内へ保存した観測・評価記録を要求する。
- 旧案件で移行できた判断は、旧profileの決定をローカル証跡とassigned ownerで再構成したものであり、新配置による判断品質の向上を直接証明しない。
- fresh workerが期限とコマンドを誤読しないかは後続transfer testで確認する。
