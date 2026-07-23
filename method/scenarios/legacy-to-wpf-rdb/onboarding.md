# はじめに — 大規模Java/JavaFX移行オンボーディング

版: 2.0  
所要時間: 30分  
完了結果: 自分の役割、現在位置、実行するコマンド一つ、成果物、完了証跡、判断先が言える

---

この文書が全員の入口である。手引書を最初から通読してから作業を始める必要はない。この文書で現在位置を決め、該当STEPだけを[移行作業手順書](migration-runbook.md)で読む。

## 1. 対象確認

次を声に出して確認する。

- 原版は顧客が実運用するJava + JavaFXシステムである。
- 移行先はC#/.NET + WPFである。
- 既存RDBのschema/dataを継続利用する。
- 数十万行、複数module/team/customerをworkstreamとsliceへ分割する。

一つでも違う場合、このscenarioを有効化しない。Migration Ownerへ別scenarioの選定を依頼する。

## 2. 安全カード

全員が守る。

1. production DBで自動試験しない。
2. 基準fixtureを直接更新しない。
3. 新旧を無設計で同時書込みさせない。
4. `migration-status.json`と`workstreams/*/status.json`を手編集しない。
5. Gate Red、未受入、未裁定、blockerを飛び越えない。
6. 移行とrefactoring/new featureを混ぜない。
7. accepted成果物を変えるときは`change-open`から開始する。
8. 実装担当者はclaimしたsliceだけを変更し、WIP上限を守る。
9. claimantは自分のsliceを最終受入しない。
10. コマンドが失敗したらstatusを書き換えず、表示された最初の問題を一件だけ直す。

## 3. 自分の入口を選ぶ

### A. Program Manager / Migration Owner / MIG-50以前の担当者

次を実行する。

```powershell
python bomdd/migration/tools/migration-workflow.py status --project-root C:\path\to\TargetProject
python bomdd/migration/tools/migration-workflow.py next --project-root C:\path\to\TargetProject
```

`Current`、`Current step`、`Action`をメモする。`next`が示した一件以外を開始しない。

### B. MIG-50以後のworkstream lead / worker / reviewer

Program全体の`next`ではなく、自分のworkstreamを見る。

```powershell
python bomdd/migration/tools/migration-workflow.py workstream-status `
  --project-root C:\path\to\TargetProject `
  --workstream WS-ID
```

- lead: `planned`を、入力・test・interface・変更範囲が揃った証跡付きで`ready`へ進める。
- worker: `ready`を一件だけ`slice-claim`する。
- reviewer/delegate: `self-accepted`以後を独立確認し、一状態ずつ進める。
- Program Manager: 全workstreamのstate/blocker/validationを集約する。

自分のworkstream ID、slice ID、役割が不明なら作業を開始しない。`responsibility-matrix.md`と`workstream-register.json`をProgram Managerに確認する。

### C. migration workspaceがまだないMigration Owner

対象repositoryがGit管理下であることを確認して一度だけ実行する。

```powershell
python method/scenarios/legacy-to-wpf-rdb/tools/migration-workflow.py init `
  --project-root C:\path\to\TargetProject `
  --product "Product Name"
```

生成された案件内の`bomdd/migration/guide/onboarding.md`へ移動する。以後は必ず案件内の凍結toolとguideを使う。

### D. migration workspaceがないMigration Worker

初期化しない。Migration Ownerへ「scenario未有効、作業開始不可」と連絡し、対象repository、product、Migration Ownerを明記する。

## 4. statusの読み方

Programの現在位置は次で決まる。

```text
最後にPASSしたMIG + Current MIG/STEP + 最初の未受入成果物
```

実装担当者の現在位置は次で決まる。

```text
WS-ID + SLICE-ID + state + claimed_by + blockers + 次の一状態
```

主観的な進捗率、作った画面数、消化工数、口頭の「ほぼ完了」は現在位置ではない。

Programマイルストーンは次の十二個である。

| MIG | 到達状態 |
|---|---|
| MIG-00 | 顧客保護境界、規模、RACI、統制が確定 |
| MIG-10 | Java/JavaFX/build/RDB/UI/NFR/security/operations基準線が確定 |
| MIG-15 | 七つの技術risk classを実証してGo |
| MIG-20 | 全数棚卸しとworkstream/slice割当が完了 |
| MIG-30 | 言語、UI、DB、NFR、security、顧客互換契約が確定 |
| MIG-40 | target architectureとmigration factory設計が確定 |
| MIG-50 | CI、test data、oracle、claim可能なfactoryが準備完了 |
| MIG-60 | 複数risk classのpilot waveが合格 |
| MIG-70 | 全slice as-built、統合/NFR/securityが合格 |
| MIG-75 | 同一Release Candidateを顧客・運用・securityが受入 |
| MIG-80 | signed release、cohort、support、rollback/restoreが準備完了 |
| MIG-90 | 全顧客cohortがacceptedまたは正式deferred |
| MIG-100 | 安定化と運用移管、旧系処置が完了 |

## 5. 最初の30分

0〜5分:

1. この安全カードを読む。
2. `migration-profile.json`のscenarioが`legacy-wpf-rdb`、modeが`enterprise-javafx`であることを確認する。
3. 自分の名前が`responsibility-matrix.md`または`workstream-register.json`にあることを確認する。

5〜10分:

1. Program担当は`status`と`next`、slice担当は`workstream-status`を実行する。
2. active change、global blocker、local blockerを確認する。
3. 自分が編集を許可されたpathを確認する。

10〜20分:

1. 該当STEPまたはslice stateの入力成果物だけを開く。
2. acceptance/Control Plan、実行コマンド、期待結果を読む。
3. 証跡保存先を先に決める。
4. 案件固有判断が残る場合、ownerへ裁定を依頼してblockする。

20〜30分:

次の一文を記入する。

```text
私は <ROLE> として <MIG/STEP または WS/SLICE/state> にいる。
次に <COMMAND/ACTION> を実行し、<ARTIFACT> と <EVIDENCE> を作る。
完了は <MEASURABLE CONDITION> で確認する。
判断が必要なら <OWNER>、失敗なら <EXCEPTION/BLOCKER> へ渡す。
```

空欄が一つでもあれば作業開始しない。

## 6. slice担当者の一本道

leadがreadyにする:

```powershell
python bomdd/migration/tools/migration-workflow.py slice-transition `
  --project-root C:\path\to\TargetProject --workstream WS-ID --slice SLICE-ID `
  --to ready --actor "Lead Name" --evidence bomdd/migration/evidence/SLICE-ID-ready.md
```

workerがclaimする:

```powershell
python bomdd/migration/tools/migration-workflow.py slice-claim `
  --project-root C:\path\to\TargetProject --workstream WS-ID --slice SLICE-ID `
  --worker "Worker Name" --evidence bomdd/migration/evidence/SLICE-ID-claim.md
```

以後、状態を飛ばさず`slice-transition`する。

```text
claimed -> manufacturing -> self-accepted
        -> integrated -> compared -> accepted -> as-built
```

`manufacturing`と`self-accepted`はclaimant、`integrated`以後はclaimantと異なるreviewer/delegateが実行する。毎回、新しい実行・比較・受入証跡を渡す。

離脱時:

```powershell
python bomdd/migration/tools/migration-workflow.py slice-release `
  --project-root C:\path\to\TargetProject --workstream WS-ID --slice SLICE-ID `
  --actor "Worker or Lead" --evidence bomdd/migration/evidence/SLICE-ID-release.md
```

局所blockerは`slice-block`、解決後は`slice-unblock`を使う。他workstreamは止めない。production DB、安全境界、Program全体へ波及する問題は[例外カタログ](exception-catalog.md)の`exception-open`を使う。

## 7. 成果物受入とGate

Program成果物は作成しただけでは完了しない。

```powershell
python bomdd/migration/tools/migration-workflow.py accept-artifact `
  --project-root C:\path\to\TargetProject --artifact ART-ID `
  --evidence bomdd/migration/evidence/review.md

python bomdd/migration/tools/migration-workflow.py approve `
  --project-root C:\path\to\TargetProject --role "Required Role" `
  --approver "Assigned Name" --evidence bomdd/migration/evidence/approval.md

python bomdd/migration/tools/migration-workflow.py check `
  --project-root C:\path\to\TargetProject --milestone MIG-ID
```

GateがFAILなら最初のFAILを一件だけ直す。PASS後にProgram Managerが`advance`する。`check`はread-only、`advance`が再検査・Gate保存・次MIG移動を行う。

JSONが参照する計測log、manifest、contract、CI、pilot、RC、release、cohort証跡は、同じ`accept-artifact`の`--evidence`へ一件ずつ追加する。これをしないと内容検査が受入を拒否する。

## 8. 困ったとき

- `content hash mismatch`: 変更を隠さず`change-open`を使う。以後は毎回`next`に従う。
- 技術選択を求められた: `decision-status`で期限とownerを確認し、作業者は決めない。
- Program blocker: `exception-catalog`でIDを選び`exception-open`する。
- local slice blocker: `slice-block`で当該sliceだけ止める。
- 手順書とstatusが矛盾: `EX-STATE-001`。statusを手編集しない。
- 成果物の意味が矛盾: `EX-DOC-001`。独自解釈で続けない。
- 中断・交代: Program担当は`handoff`、slice担当はclaim継続可否をleadと決め、離脱なら`slice-release`する。

## 9. オンボーディング完了条件

次を全て満たせば完了である。

- 自分がProgram系かworkstream系か言える。
- 現在のMIG/STEP、またはWS/SLICE/stateを表示できる。
- 次に実行するコマンドが一つに決まっている。
- 作る成果物、証跡、数値または観測による完了条件が言える。
- 判断ownerとblocker入口が分かる。
- production DB禁止、status手編集禁止、claim/WIP/独立受入を説明できる。

完了しなければ、開始30分で得た出力をそのままProgram Managerへ渡す。推測してコードを書き始めない。
