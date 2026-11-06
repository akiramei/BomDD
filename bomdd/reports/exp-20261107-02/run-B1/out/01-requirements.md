# 1. 要求の整理 — 取り消し/やり直し(Undo/Redo)

出典の略記: REQ-nnn = `sources/10-requirements.yaml`、README = `sources/README.md`/`README.ja.md`、
CAD = `cad/*.json`。資料に根拠がない点は「未確定」と書き、`04-owner-questions.md` の質問番号(Q-nn)を付けた。

## 1.1 中心の要求(資料にそのまま書かれていること)

| ID | 要求 | 出典 |
|---|---|---|
| U-01 | 編集は 1 つずつ取り消せ(Undo)、取り消した編集はやり直せる(Redo)。 | REQ-012、README「履歴」 |
| U-02 | 取り消せる深さは最大 50 段。51 段目の編集を記録すると、いちばん古い段が捨てられる(新しい段ではない)。 | REQ-012(反例「the newest step dropped」) |
| U-03 | 新しい編集をすると、やり直し待ちの段はすべて消える。 | REQ-012(反例「redo kept after a new edit」) |
| U-04 | ひと続きのドラッグ(境界移動・トリムのドラッグ)は 1 段として記録する。ドラッグ開始時に 1 回だけ状態を写す。 | REQ-012、README「設計上のポイント」 |
| U-05 | 履歴は「文書の状態の丸ごと」を積む(文書は不変で、編集は新しい文書を返す)。Undo は 1 つ前の文書へ、Redo は 1 つ先の文書へ戻す。 | REQ-012 rationale、README「不変ドキュメント」 |
| U-06 | 受け付けられなかった編集(拒否)は文書を変えない。したがって履歴の段も増えない、と読む。 | REQ-004「refused and leaves the document unchanged」、REQ-010 |
| U-07 | ツールバーに Undo / Redo ボタンがある。ショートカットは Ctrl+Z(Undo)、Ctrl+Y・Ctrl+Shift+Z(Redo)。 | CAD actions.json、README「ショートカット」 |
| U-08 | 戻す段がなければ Undo ボタンは使えない。やり直す段がなければ Redo ボタンは使えない。 | CAD start-screen(起動直後 両方 false)、観測の意味(observations.json) |

## 1.2 Undo/Redo の対象になる編集(文書を変える操作)

REQ-012 の「Every edit」を、文書(DocumentState)を変える操作として読む。

| 編集 | 画面の操作 | 出典 |
|---|---|---|
| 区間の分割 | `Split` | REQ-004 |
| 区間の結合(境界の削除) | `DeleteSelectedBoundary` | REQ-006 |
| 境界の移動(ドラッグ) | タイムライン上のドラッグ(例では使えない) | REQ-005 |
| トリム開始/終了 | `SetTrimIn` / `SetTrimOut`、トリムのドラッグ | REQ-007 |
| 区間の速度 | `ApplySpeedPreset:*` | REQ-008 |
| 区間の音量 | `ApplyVolumePreset:*` | REQ-009 |
| 区間の除外/復帰 | Delete キー(例では使えない) | REQ-010 |
| ピッチ維持の切り替え | インスペクタ(操作 id は CAD にない) | REQ-008 |

## 1.3 対象かどうか未確定のもの

| 操作 | なぜ未確定か | 質問 |
|---|---|---|
| 出力の幅・高さ(`Scale:*`)、出力フレームレート(`SetFps:*`) | REQ-012 は「every edit」だが、REQ-013 はこれらが画面側の view model にあると書く(文書の外)。文書の外なら履歴に乗らない。 | Q-03 |
| 現在と同じ値を押す(例: 1x の区間に `ApplySpeedPreset:1`) | 文書が変わらない操作が 1 段として積まれるかが書かれていない。 | Q-05 |

## 1.4 Undo/Redo の対象ではないもの(文書を変えない操作)

再生ヘッドの移動(`ToStart`・`ToEnd`・`StepBack`・`StepForward`・クリックでの頭出し)、再生、ズーム、言語切り替え、
書き出しのダイアログ。再生ヘッドは文書の要素として REQ-001〜019 のどこにも現れないため、これらは段を作らず、
Undo/Redo によって再生ヘッドが動くこともない、と読む(後者は Q-06 で確認する)。

## 1.5 画面に出る結果(観測できる表示との対応)

| 表示 | Undo/Redo との関係 |
|---|---|
| `undo_enabled` / `redo_enabled` | 戻す段 / やり直す段があるか(U-08) |
| `unsaved` | 編集で「未保存の変更」になる。Undo で開いた時点の状態へ戻ったときの表示は未確定(Q-02) |
| `region_count`・`trim_*`・`selected_*`・`output_length` | 文書から導かれる値。Undo/Redo で文書と一緒に戻る |
| `split_enabled`・`merge_enabled`・`trim_in_enabled`・`trim_out_enabled` | 文書と再生ヘッド・選択から導かれる。Undo/Redo 後に再計算される |
| `playhead` | 文書の外。Undo/Redo で変わらない(と読む・Q-06) |
| `out_fps`・`out_width`・`out_height` | Undo/Redo で戻るかは未確定(Q-03) |

## 1.6 範囲外

ドラッグの途中経過、50 段の上限そのものの画面例(1 例の手順が 15 個までのため例で示せない)、
ファイルを開き直したときの履歴の扱い(Q-07)。
