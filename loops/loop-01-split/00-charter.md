# Loop 1 憲章 — 区間分割(Split)スライス

## 目的
BOM手法の全工程(①→⑥)を**一度通す**こと。アプリ完成でなく、どこで「ずる」が出るかの**初回測定**。

## スコープ(薄い縦スライス1本)
ユーザーが再生ヘッド位置で区間を2分割する機能。ドメイン + オーケストレーション + 入力 + 履歴 +
タイムライン再描画 を最小構成で貫く。**技術スタックは原版固定**(Avalonia 12 / .NET 10 / C# / CommunityToolkit.Mvvm)。

### 含む(原版の対応箇所)
- 分割ドメイン: `DocumentState.SplitAt` / `CanSplitAt` / `RegionAt`、`TimeMath.SnapFrame` / `MinLen`
- 属性継承: `Speed` / `PreservePitch` / `Volume`(`RegionData`)
- 分割コマンド: `MainWindowViewModel.Split`(ID採番 `_nextId`/`NextIdFor`、`CommitEdit`、選択 `SelectedId`)
- 履歴: `History`(snapshot/undo/redo)、選択再解決 `DocumentState.ResolveSelection`
- 入力: `MainWindow` の `Key.S`、ツールバー `SplitCommand`
- 表示: `TimelineControl` の境界線描画(state→視覚)

### 含まない(後続ループ)
トリム/境界移動/速度/音量/除外/書き出し/再生/サムネ/波形。

## 合否オラクル(技術固定ゆえ原版の挙動・テストを基準に使える)
- **客観**: 原版 `DocumentStateTests` の分割関連を移植し、製造コードに対して緑になること
  (`SplitAt_ValidPlayhead…` / `…TooCloseToEdge…` / `CanSplitAt_RespectsMinLen` / `SplitAt_InheritsVolume` / `Edits_DoNotMutateOriginal`)。
- **主観(UI/描画)**: S キーで境界線が現れる・後半が選択される、は単体テスト困難。
  → ここが C4(受入不能)を炙り出す想定。

## 製造装置の隔離
⑤製造は ③M-BOM + ④工程のみを渡した別エージェントに行わせ、原版ソース・本リバース仕様の「出典行」は与えない
(要求の意図は渡すが実装は渡さない)。装置が埋められない箇所 = 可視化されたギャップ。詳細: [../../method/cheat-taxonomy.md](../../method/cheat-taxonomy.md)。

## 終了条件
⑥合否まで到達し、`cheat-log.md` を分析して [loop-01-report.md](../loop-01-report.md) に手法改善提案を出す。
未達でも「ずる」で前進し、不足として記録する(止めない)。
