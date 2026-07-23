# Traggo Web → C#/.NET/WPF 移行実証実験

このディレクトリは、`legacy-wpf-rdb` 移行手引きを実案件相当の OSS へ適用し、移行結果と手引きの使いやすさを同時に検証するための実験記録である。

## 作業者の入口

1. [実験プロトコル](experiment/experiment-protocol.md)で実験条件だけを確認する。
2. [案件に凍結したオンボーディング](bomdd/migration/guide/onboarding.md)を実行する。
3. `migration-workflow.py status` と `next` に表示された一つの Action だけを行う。
4. 手引きだけでは続行できなかった場合は、実施前に[介入ログ](experiment/intervention-log.md)へ記録する。

## 現在位置

正本は `bomdd/migration/migration-status.json`。表示コマンド:

```powershell
python bomdd\migration\tools\migration-workflow.py status `
  --project-root C:\Users\akira\source\repos\BomDD\experiments\legacy-wpf-rdb-01
```

## 実験対象

- 原版: [traggo/server](https://github.com/traggo/server)
- 固定版: `v0.8.3` / `6321119c3c2d55f04e2e4967f6492aabd6067b76`
- ライセンス: GPL-3.0
- 継続利用する RDB: SQLite
- 移行先: C# / .NET 10 / WPF / Windows x64

取得物は `.gitignore` 対象とし、再取得条件を [source-lock.json](experiment/source-lock.json) に固定する。
