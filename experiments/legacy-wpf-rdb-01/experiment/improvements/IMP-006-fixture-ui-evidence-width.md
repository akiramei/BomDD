# IMP-006 — fixtureとUI証跡の検査幅を拡大する

## 問題

IMP-002でaccepted成果物とstatusに列挙された証跡のSHA-256は検査できるようになったが、索引文書の中から参照されるfixture、screenshot、DOM等の実体まではたどっていなかった。

改善前の凍結案件を二つの一時コピーで測定した。

| 負例 | MIG-10 | exit |
|---|---|---:|
| `fixtures/`をコピーせず、基準fixtureを欠落させる | PASS | 0 |
| UI画像1枚とcalendar DOMを削除する | PASS | 0 |

また、3枚の`*.png`は実体がJPEG/JFIFだった。hashは正しかったが、旧Gateは実形式も寸法も検査しないため、この不一致を受入時に検出できなかった。

## 今回変更するもの

- `baseline-fixture-manifest.json`とテンプレート。
- `current-ui-evidence-manifest.json`とテンプレート。
- manifest自身をaccepted artifact evidenceへ含める強制条件。
- fixture、restore copy、DB基準線、schema、DB観測のpath/hash再照合。
- SQLite header、read-only `integrity_check`、`foreign_key_check`、代表SELECTの実行。
- current observation indexとUI manifestのID集合一致。
- empty/populated/alternate-viewの代表状態網羅。
- 各観測のscreenshotと非画像semantic evidence。
- screenshotのhash、実media type、拡張子、寸法、最低寸法。
- 観測主張から証跡IDへの明示的な対応。
- MIG-10のUI Approver承認。
- 旧案件でDB/UI成果物を一つの受入後変更へまとめる複数`--changed-file`。

## 今回変更しないもの

- MIG-20以後のfixture/UI acceptance oracle設計。
- 画素差分やOCRによる表示内容の自動判定。
- fresh worker transfer test。
- client-server RDBの第二実験。
- PDF。

## 合格条件

1. 有効なSQLite fixture/UI manifestを持つMIG-10がPASSする。
2. fixture実体またはrestore control copyが無ければFAILする。
3. SQLite integrity、FKまたは代表SELECTが期待と異なればFAILする。
4. observation indexとmanifestのIDが異なればFAILする。
5. 必須状態、screenshot、semantic evidenceまたはclaim supportが不足すればFAILする。
6. UI証跡のbytes、実形式、拡張子または寸法がmanifestと異なればFAILする。
7. manifestがartifact evidenceに含まれなければ受入を拒否する。
8. 既通過案件を正規の受入後変更で再受入し、MIG-20 / STEP-021へ戻る。
9. 中央・凍結自己テスト、MIG-00、置換MIG-10 GateがPASSする。

## 実装結果

Traggo実験では次を保存した。

- fixture: `fixtures/baseline/traggo.db`
- retained restore control: `fixtures/restore-control/traggo.db`
- 両者のSHA-256: `308b5feebc0eed2be1ac781698f20bee2fd771fbd61a298e8e5f4e1544237458`
- fixture manifest: `bomdd/migration/evidence/baseline-fixture-manifest.json`
- UI manifest: `bomdd/migration/evidence/current-ui-evidence-manifest.json`
- UI evidence: 3観測、3状態、3 JPEG、build/DB/DOM semantic evidence
- canonical query: table counts、visible tag、span、tag valueの4件

誤っていた3拡張子は`.png`から`.jpg`へ訂正した。画像bytesとSHA-256は変更していない。

## 変更後測定

| 測定 | 結果 |
|---|---|
| 中央selftestの有効manifest | PASS |
| selftest fixture削除 | MIG-10 FAIL |
| selftest UI bytes差替え | MIG-10 FAIL |
| Traggo fixture/UI semantic validation | 問題0件 |
| Traggo fixture削除 | MIG-10 FAIL、exit 2 |
| Traggo UI画像とDOM削除 | MIG-10 FAIL、exit 2 |
| MIG-10 required approvals | Migration Owner、DB Custodian、UI Approverの3件PASS |
| 中央/凍結tool、definition、guide、2template | SHA-256一致 |
| 中央selftest | PASS |
| 凍結selftest | PASS、read-only、status不変 |
| MIG-00 Gate | PASS |
| 置換MIG-10 Gate | PASS |
| 通常位置 | MIG-20 / STEP-021を維持 |

最終status SHA-256は`e5f21ade3fefcacf5a924a3d1d65f7367cb2c6c222e9b8ddc57bc08cd0ca8f8b`。前回`45e3aa86feb3158e0034199f0f1495dc444d260245e3063a3b20e929c3acb430`からの変更は、2manifest、MIG-10再受入、UI Approver承認、Gate supersession、受入後変更履歴による意図した変更である。

## 実行中に得た追加フィードバック

IMP-006の説明を既存の共有レビュー証跡へ追記したところ、同じ証跡をsealしていたMIG-00がFAILした。説明は専用IMP-006記録へ移し、共有証跡を保存済み改善前コピーから元bytesへ戻した。その後MIG-10も正規手順で再受入し、MIG-00/MIG-10の両方をPASSさせた。

これは受入後hash管理が共有証跡の横断影響を正しく検出した結果である。今後の改善説明は既存共有証跡へ追記せず、専用の新規証跡へ保存する。

## 効果判定

合格条件を満たした。作業者は「索引に書いたから存在するはず」と判断せず、2テンプレートを上から埋めてGateの最初のFAILを一件ずつ直せる。manifest自身がsealされ、その先の実体をGateが毎回たどるため、同名差替えだけでなく、欠落、形式偽装、寸法不足、観測漏れ、意味証跡漏れ、代表DB値の変化を止められる。

## 残る限界

- UIの見た目や業務上の正しさ自体はUI Approverが判断する。今回の自動検査は証跡closureと最低品質を対象とする。
- SQLite専用のlive validatorである。client-server RDBは第二実験でengine別validatorを追加する。
- required statesは代表基準線であり、全画面・全error/concurrency状態の網羅はMIG-20以後の台帳とacceptance oracleで行う。
- fresh workerがmanifestのplaceholderとGate出力だけで迷わず完了できるかは次のtransfer testで確認する。

