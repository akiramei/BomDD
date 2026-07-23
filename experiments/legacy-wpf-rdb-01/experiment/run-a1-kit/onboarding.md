# はじめに - legacy-wpf-rdb 移行オンボーディング

このページが、初めて移行作業へ参加する人の入口である。ほかの資料を先に探さない。

対象:

- 既存システムを C#/.NET + WPF へ再実装する。
- 既存 RDB と既存データを継続利用する。
- 最短・最小コストより、迷わず安全に作業を続けることを優先する。

一つでも一致しない場合は、この手順を開始せず Migration Owner へ次の文面を送る。

```text
legacy-wpf-rdb の対象条件と案件条件が一致しません。
一致しない条件: <条件を書く>
別シナリオの指定をお願いします。
```

---

## 1. 最初の安全カード

作業開始前に、次の六項目を読む。例外を自分で判断しない。

1. 本番 DB で自動テストを実行しない。
2. 基準 fixture を直接更新しない。毎回、作業コピーを使う。
3. 新旧アプリを無設計で同時書込みさせない。書込み主体は一つにする。
4. 初期移行では DB schema を変更しない。必要なら別 ECO を起票する。
5. 移行と無関係なリファクタリングをしない。
6. 表示された現在 STEP 以外を「ついでに」始めない。

違反している可能性がある場合は作業を止め、[異常時処置集](exception-catalog.md)の `EX-DB-*` または `EX-STATE-*` を使う。

---

## 2. まず現在位置を表示する

対象プロジェクトに次のファイルがあるか確認する。

```text
bomdd/migration/migration-status.json
```

### ファイルがある場合

初期化を再実行しない。次を実行する。

```powershell
python method/scenarios/legacy-to-wpf-rdb/tools/migration-workflow.py status `
  --project-root C:\path\to\TargetProject

python method/scenarios/legacy-to-wpf-rdb/tools/migration-workflow.py next `
  --project-root C:\path\to\TargetProject
```

凍結済みの `bomdd-kit` から実行する案件では、先頭を次に読み替える。

```text
python bomdd-kit/method/scenarios/legacy-to-wpf-rdb/tools/migration-workflow.py
```

### ファイルがない場合 - Migration Owner

対象条件と対象リポジトリを確認し、一度だけ初期化する。

```powershell
python method/scenarios/legacy-to-wpf-rdb/tools/migration-workflow.py init `
  --project-root C:\path\to\TargetProject `
  --product ProductName
```

既存ファイルは上書きされない。`bomdd/migration/` がすでに存在する場合は停止する。

### ファイルがない場合 - Migration Worker

自分で初期化しない。Migration Owner へ次の文面を送る。

```text
bomdd/migration/migration-status.json がありません。
対象プロジェクト: <絶対パス>
legacy-wpf-rdb の初期化または別シナリオの指定をお願いします。
```

---

## 3. status の読み方

出力例:

```text
Project      : OrderDesk
Scenario     : legacy-wpf-rdb
Last passed  : MIG-50 製造準備完了
Current      : MIG-60 最小スライス合格
Current step : STEP-064
Work item    : SLICE-READ-ORDER-001
Action       : 現行画面とWPF画面の必須表示要素を比較する
Blockers     : 0
Unaccepted   : 1
Next         : STEP-065 観測差分を原因層へ帰属する
```

読む順序は固定する。

1. `Scenario` が `legacy-wpf-rdb` であることを確認する。
2. `Last passed` で、受入済みの最後の地点を確認する。
3. `Current` で、現在のマイルストーンを確認する。
4. `Current step` と `Action` を、そのまま今回の作業にする。
5. `Blockers` が 1 以上なら、実装を進めない。
6. `Unaccepted` で、Gate 通過に不足する成果物を確認する。
7. `Next` は現在 STEP 完了後の予告であり、同時に着手しない。

現在位置は次で決まる。

```text
現在位置 = 最後に通過したマイルストーン + 現在の STEP + 最初の未受入成果物
```

進捗率、作業時間、実装済み画面数では現在位置を決めない。

---

## 4. 色と行動

| 状態 | 見分け方 | 行動 |
|---|---|---|
| Green | Gate PASS、blocker 0 | `advance` で次へ進む |
| Yellow | non-blocker のみ、既定処置あり | 既定処置を記録して現在 STEP を続ける |
| Red | blocker、Gate FAIL、必須成果物不足 | 表示された STEP に留まり、例外票を作る |

`ほぼGreen`、`条件付きGreen`、`だいたい完了` は使わない。

---

## 5. 初参加時に覚えるファイルは五つだけ

| 目的 | ファイル |
|---|---|
| 現在位置 | `bomdd/migration/migration-status.json` |
| 案件固有の技術・安全方針 | `bomdd/migration/migration-profile.json` |
| マイルストーンの通過条件 | `bomdd/migration/milestone-definition.json` |
| 実行する全手順 | `bomdd/migration/guide/migration-runbook.md` |
| 異常時の既定処置 | `bomdd/migration/guide/exception-catalog.md` |

ほかの成果物は `status` または現在 STEP から開く。自分で探索順を考えない。

---

## 6. 最初の30分

| 時間 | 行うこと | 完成または確認するもの |
|---|---|---|
| 0-5分 | 安全カードを読む | 禁止事項六項目を説明できる |
| 5-10分 | `status` を実行する | Scenario、Last passed、Current、STEP が見える |
| 10-15分 | `next` を実行する | 今回実行する Action が一つ表示される |
| 15-20分 | profile と責任者表を確認する | 自分の role と裁定先が分かる |
| 20-25分 | 現在 STEP の成果物を開く | 未記入箇所と完了条件が分かる |
| 25-30分 | 証跡保存先を確認して着手する | `bomdd/migration/evidence/` を使える |

30分以内に次の Action が一つに決まらない場合、オンボーディングは未完了である。推測で開始せず `EX-STATE-001` または `EX-STATE-002` を使う。

---

## 7. MIG-00 にいる人が最初に作るもの

`Current: MIG-00` の場合、次の三成果物だけを先に完成させる。

1. `bomdd/00-charter.md`
2. `bomdd/migration/migration-profile.json`
3. `bomdd/migration/responsibility-matrix.md`

三成果物を `accepted` にするには、成果物ファイル、証跡、Migration Owner の承認が必要である。ファイルが存在するだけでは完了ではない。

確認:

```powershell
python method/scenarios/legacy-to-wpf-rdb/tools/migration-workflow.py check `
  --project-root C:\path\to\TargetProject `
  --milestone MIG-00
```

PASS 後だけ次を実行する。

```powershell
python method/scenarios/legacy-to-wpf-rdb/tools/migration-workflow.py advance `
  --project-root C:\path\to\TargetProject
```

---

## 8. 困ったとき

### 技術や業務の選択を求められた

作業者は選ばない。責任者表にある owner へ裁定票を渡す。

### blocker が表示された

現在 STEP を進めない。`alternate_safe_work` があれば、それだけを行う。なければ例外票を作って待つ。

### 手順書と status が矛盾する

成果物と案件で凍結した `milestone-definition.json` を優先し、`EX-DOC-001` を記録する。

### 作業を中断・交代する

```powershell
python method/scenarios/legacy-to-wpf-rdb/tools/migration-workflow.py handoff `
  --project-root C:\path\to\TargetProject
```

生成された引継票に、現在位置、次の Action、blocker、未受入成果物、再開コマンドがあることを確認する。

---

## 9. オンボーディング完了条件

次がすべて満たされたら、オンボーディング完了である。

- 自分が Migration Owner か Migration Worker か分かる。
- `status` と `next` を実行できる。
- `Scenario`、`Last passed`、`Current`、`Current step` を説明できる。
- 今回実行する Action が一つに決まっている。
- 成果物と証跡の保存先が分かる。
- blocker 時の裁定先と例外 ID が分かる。
- 作業終了時に `handoff` を残せる。

完了後は、[標準移行作業手順書](migration-runbook.md)の現在マイルストーンだけを読む。最初から全章を暗記する必要はない。

