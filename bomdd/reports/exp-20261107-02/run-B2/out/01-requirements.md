# 1. 要求の整理 — 取り消し/やり直し(Undo/Redo)

資料: `sources/10-requirements.yaml`(以下 REQ-nnn)、`sources/README*.md`、`cad/*.json`。
本書の各項目に根拠を付ける。根拠が資料にない事項は「4. 確認したいこと」へ回し、ここでは決めない。

## 1.1 対象と前提

- 対象は「編集の取り消し/やり直し」。編集とは、ドキュメント(区間の並び・各区間の設定・トリム範囲)を変える操作(REQ-012「Every edit」)。
- ドキュメントは不変で、編集は新しい状態を返す。履歴は状態そのもの(スナップショット)を積む(README「Design notes: Immutable document」・REQ-012 rationale)。
- 起動直後は編集履歴が空(`cad/start-screen.json`: `undo_enabled=false`・`redo_enabled=false`・`unsaved=false`)。

## 1.2 要求

| id | 要求 | 根拠 |
|---|---|---|
| U-01 | 編集を 1 回行うごとに、編集前の状態が取り消し履歴に 1 段積まれる。 | REQ-012・README:23 |
| U-02 | Undo は直前の 1 段を取り消し、ドキュメントを編集前の状態へ戻す。戻した状態はやり直し履歴に積まれる。 | REQ-012 |
| U-03 | Redo は直前に取り消した 1 段をやり直す。 | REQ-012 |
| U-04 | 新しい編集を行うと、やり直し履歴は空になる。 | REQ-012(counterexample: redo kept after a new edit) |
| U-05 | 履歴は最大 50 段。51 段目を積むと最も古い段が捨てられる。 | REQ-012・README:23 |
| U-06 | 1 回の連続したドラッグ(境界・トリムのドラッグ)は 1 段。ドラッグ開始時に 1 回だけスナップショットを取る。 | REQ-012・README「Design notes」 |
| U-07 | 取り消し履歴が空のとき Undo ボタンは使えない。やり直し履歴が空のとき Redo ボタンは使えない。 | `cad/start-screen.json`(起動直後に両方 false)・`cad/observations.json` |
| U-08 | 拒否された編集(例: 区間の端から 0.5 秒未満での分割)はドキュメントを変えず、新しい状態を返さない。 | REQ-004(refusals return no new document) |
| U-09 | 再生ヘッドの移動(先頭へ・末尾へ・1 フレーム送り/戻し)は編集ではなく、履歴を変えない。 | REQ-012 は「edit」を対象とし、再生ヘッドは REQ-003 で編集対象の選び方にだけ使われる(推論) |
| U-10 | Undo/Redo のあと、画面の派生値(区間数・トリム・出力の長さ・各ボタンの可否)は戻した状態から計算し直される。 | REQ-003・REQ-004・REQ-007・REQ-011(ボタンの可否と長さはドキュメントの関数) |
| U-11 | Ctrl+Z で Undo、Ctrl+Y または Ctrl+Shift+Z で Redo。 | README:25 |

## 1.3 編集として履歴に積む操作(資料で確定しているもの)

| 操作 id | 編集内容 | 根拠 |
|---|---|---|
| `Split` | 再生ヘッドで区間を分割 | REQ-004 |
| `DeleteSelectedBoundary` | 選択中の区間を 1 つ前の区間と結合 | REQ-006 |
| `SetTrimIn` / `SetTrimOut` | トリム開始/終了を再生ヘッドへ | REQ-007 |
| `ApplySpeedPreset:*` | 選択中の区間の速度 | REQ-008 |
| `ApplyVolumePreset:*` | 選択中の区間の音量 | REQ-009 |
| (境界ドラッグ・トリムドラッグ) | 1 ドラッグ = 1 段 | REQ-005・REQ-007・REQ-012 |
| (除外/復帰: Delete キー) | 区間の除外 | REQ-010・README:25 |

**確定していないもの**: `Scale:*`・`SetFps:*`(出力サイズ・フレームレート)。REQ-013 はこれらが元製品では画面の view model にあると書いており、履歴が持つドキュメント(DocumentState)の外にある可能性がある。履歴に積むかは Q-01 で確認する。

## 1.4 範囲外

- 履歴のファイル保存・アプリ再起動をまたぐ履歴(資料に記述なし)。
- 「保存済み/未保存」表示の保存操作そのもの(操作一覧に保存がない)。表示と Undo の関係は Q-04。
