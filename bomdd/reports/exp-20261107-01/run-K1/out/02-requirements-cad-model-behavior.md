# 02 要求・CAD・ドメインモデル・振る舞い契約の対応 — Undo/Redo

由来区分は `kit/docs/artifact-contract.md` §2 の 6 区分(EXPLICIT / DERIVED / DESIGN_CHOICE / PROPOSAL / UNRESOLVED / CONFLICT)。資料の略号は 01 の §1。

## 1. 要求の分解(REQ-012 を中心に)

| ID | 条件 | 操作 | 結果 | 観測 | 時点 | 根拠・区分 |
|---|---|---|---|---|---|---|
| U-01 | 編集を 1 つ以上行った | Undo | 直前の編集の前のドキュメントに戻る | 区間・トリム・速度・音量と、それから導く表示(region_count, trim_*, output_length, selected_*) | 操作完了時 | REQ-012「Every edit can be undone」, MAN-JA:27「スナップショット」 / EXPLICIT(戻る中身が「ドキュメント全体」であることは MAN-JA:151-152 から DERIVED) |
| U-02 | Undo を 1 回以上した | Redo | 取り消した編集の後のドキュメントに戻る | 同上 | 操作完了時 | REQ-012 / EXPLICIT |
| U-03 | やり直しが残っている | 新しい編集 | やり直しが全部消える | redo_enabled=false | 操作完了時 | REQ-012「a new edit clears the redo steps」/ EXPLICIT(「全部」は "the redo steps" の複数形から DERIVED) |
| U-04 | 50 段ある | 51 個目の編集 | 最古の 1 段が落ちる | 51 回目の Undo ができない | 操作完了時 | REQ-012 / EXPLICIT。例では確かめられない(03 §2) |
| U-05 | ドラッグ中 | 連続した 1 回のドラッグ | 1 段 | — | ドラッグ終了 | REQ-012, MAN-JA:152 / EXPLICIT。今回の操作一覧にドラッグが無く例にできない |
| U-06 | 取り消せる段が無い | — | Undo できない | undo_enabled=false | 常時 | CAD-START(段なし→false)/ DERIVED: 起動直後の観測を「段が無ければ使えない」と一般化。逆向き(段があれば true)は REQ-012「can be undone」+ CAD-ACT の Undo ボタンから DERIVED |
| U-07 | やり直せる段が無い | — | Redo できない | redo_enabled=false | 常時 | CAD-START + REQ-012 / DERIVED(U-06 と同じ形) |
| U-08 | 起動直後(サンプルを読み込んだ状態) | — | 読み込みは取り消しの段ではない | undo_enabled=false | 起動直後 | CAD-START / EXPLICIT(観測値) |
| U-09 | — | 再生ヘッドの移動(StepForward 等) | 段を作らない・やり直しを消さない | undo/redo_enabled が変わらない | 操作完了時 | 前提 P0 に依存 / DERIVED |
| U-10 | — | 出力サイズ・フレームレートの変更 | 段になるか不明 | — | — | REQ-012「every edit」と REQ-013 UQ-REQ-013-001 / UNRESOLVED(Q1) |
| U-11 | — | 値が変わらない編集(1x に 1x) | 段になるか不明 | — | — | 資料に記述なし / UNRESOLVED(Q3) |
| U-12 | — | Undo / Redo | 再生ヘッド・選択への作用 | selected_*, playhead | — | 資料に直接の記述なし / P1 と CF-01 に依存(§3, §5) |
| U-13 | — | 編集・Undo | 「未保存の変更」表示への作用 | unsaved | — | 資料に保存・未保存の記述が一切ない / UNRESOLVED(Q4) |

Undo の対象になる編集の計算(例の値の出どころ): 分割 REQ-004(設定を引き継ぎ、0.5 秒未満なら拒否)、境界の帰属 REQ-003、結合 REQ-006、トリム REQ-007、速度 REQ-008、音量 REQ-009、出力の長さ REQ-011(除外していない区間の、トリム後の長さ ÷ 速度 の和)。

## 2. CAD との対応

| CAD | 種類 | 要求 | 状態との関係 |
|---|---|---|---|
| CAD-ACT `Undo`(ToolbarView) | 操作 | U-01 | History から 1 段戻す |
| CAD-ACT `Redo`(ToolbarView) | 操作 | U-02 | History から 1 段進める |
| CAD-ACT `Split`, `DeleteSelectedBoundary`, `SetTrimIn`, `SetTrimOut`, `ApplySpeedPreset:*`, `ApplyVolumePreset:*` | 操作(編集) | U-01〜U-03 の対象 | 新しいドキュメントを作り、History に積む |
| CAD-ACT `Scale:*`, `SetFps:*`(InspectorView) | 操作(出力設定) | U-10 | 履歴に入るか未決 |
| CAD-ACT `ToStart`, `ToEnd`, `StepBack`, `StepForward`(TransportView) | 操作(再生位置) | U-09 | 再生ヘッドだけを変える(P0) |
| CAD-OBS `undo_enabled` / `redo_enabled` | 派生表示 | U-06, U-07 | History の段の有無から導く |
| CAD-OBS `region_count`, `trim_start`, `trim_end`, `output_length` | 派生表示 | U-01, U-02 | ドキュメントから導く |
| CAD-OBS `selected_*` | 派生表示 | U-12 | 編集対象の区間(§3 P2)。Undo 後は CF-01 |
| CAD-OBS `out_fps`, `out_width`, `out_height` | 表示 | U-10 | 出力設定(ドキュメントの外か内かは Q1) |
| CAD-OBS `unsaved` | 表示 | U-13 | 何から導くか資料なし |
| CAD-OBS `split_enabled`, `merge_enabled`, `trim_in_enabled`, `trim_out_enabled` | 派生表示 | Undo の前提(押せるか) | ドキュメント+再生ヘッドから導く(REQ-004, REQ-006, REQ-007) |

CAD に無いもの: キーボードの Ctrl+Z / Ctrl+Y(MAN-JA:28)。ボタンが使えないときにショートカットが受け付けられるかは資料になく、今回は扱わない(UI で無効なことと、操作の受付は別)。

属性と表示義務の区別: History が「何段あるか」を持つことは REQ-012 から言えるが、段数を画面に出す義務は資料にない。画面に出すと言えるのは Undo/Redo ボタンの可否(CAD-OBS)だけ。

## 3. 前提(明記ではない。依存する例と主張に印を付けた)

- **P0(DERIVED)**: History の 1 段はドキュメントのスナップショットで、ドキュメントの中身は区間とトリム範囲(MAN-JA:27, :151-152; REQ-002「one region … and a trim range」)。再生ヘッドはプレビューの再生位置で(MAN-JA:157)、ドキュメントの項目ではない(REQ-003 は「the region at a time t」と時刻を外から与える)。よって再生ヘッドの移動は段を作らず、やり直しを消さない。— 依存: U-09, EX-10, EX-11。「新しい編集でやり直しが消える」は「編集以外では消えない」を明記していないので(「なら必ず」と「のみ」は別)、これは導出であって明記ではない。
- **P1(DERIVED)**: Undo/Redo はドキュメントを差し替える。差し替えで再生ヘッドを動かすとは書かれていない。ただし「動かさない」とも書かれていないので、再生ヘッドの値そのものは例で主張しない。主張するのは、取り消す編集の前後で再生ヘッドが同じ値(20 秒)で、かつ選択区間の id と範囲が変わらないときの選択表示だけ — このとき「再生ヘッドはそのまま」「編集前の位置へ戻す」のどちらの読みでも同じ値になる。
- **P2(DERIVED)**: `selected_*` は編集対象の区間を表示する。編集対象は再生ヘッドの下の区間で、境界の時刻は後ろの区間に属する(REQ-003 rationale「Which region is 'at the playhead' decides the target of every per-region edit; a boundary instant belongs to the later region」)。支え: CAD-START で再生ヘッド 20 秒と選択 [6,40) が一致する。— 依存: 分割後の選択 [20,40)、merge_enabled=true、trim_in_enabled=false(EX-02, EX-06, EX-09)。

## 4. ドメインモデル候補

| 概念 | 意味 | 識別 | 状態 | 根拠・区分 |
|---|---|---|---|---|
| Document | 1 つのクリップに対する編集結果(区間の列とトリム範囲)。不変 | 値として比較(id を持たせない) | regions, trimStart, trimEnd | MAN-JA:151, REQ-002 / EXPLICIT(不変は MAN の記述) |
| Region | 区間 | 区間 id(分割の後半は新しい id、結合は前の区間の id を残す) | start, end, speed, pitch, volume, excluded | REQ-003/004/006/008/009/010 / EXPLICIT |
| History | 取り消し・やり直しの段 | 1 つの編集画面に 1 つ | undo 側の段(最大 50)・redo 側の段 | REQ-012, MAN-JA:27 / EXPLICIT |
| EditTarget(選択) | 編集の対象区間 | Region の id か、再生ヘッドからの導出か — CF-01 | — | REQ-003, REQ-004 反例 / CONFLICT |
| Playhead | 再生位置(ソース時刻) | — | 秒 | MAN-JA:157 / EXPLICIT(History の外に置くのは P0) |
| OutputSettings | 出力の幅・高さ・フレームレート | — | width, height, fps | REQ-013 / EXPLICIT。History に入れるかは Q1 |
| SaveState(未保存表示) | 「未保存の変更」/「保存済み」 | — | 不明 | CAD-OBS `unsaved` のみ / UNRESOLVED(Q4) |

条件:

| 条件 | 時点 | 関わる状態・操作 | 根拠 |
|---|---|---|---|
| INV-H1 undo 側の段は 50 以下 | 操作完了時 | History・すべての編集 | REQ-012 |
| INV-H2 新しい編集の直後、redo 側は空 | 操作完了時 | History・編集 | REQ-012 |
| INV-H3 Undo→Redo で、取り消す前と同じドキュメント | 操作完了時 | History・Document | REQ-012(DERIVED: 「redone」をそう読む) |
| INV-D1 区間は隙間なく並ぶ・0.5 秒以上 | 常時(どの段のドキュメントでも) | Document | REQ-003/004/005。スナップショットを戻すので Undo 後も成り立つ(DERIVED) |

設計選択(DESIGN_CHOICE。依頼の範囲で AI が決めた。外部の約束は足さない):
- DC-1 History は Document の参照を 2 本のスタック(undo 側・redo 側)で持つ。理由: MAN-JA:152「参照を積むだけ」と同じ形で、REQ-012 の 3 規則(上限・最古を落とす・新しい編集で redo を消す)をそのまま書ける。差分の記録(コマンドの逆操作)は採らない — 不変ドキュメントなので必要がない。
- DC-2 History は Document を持つ側(編集の窓口)の内側に置き、画面は undo/redo の可否だけを読む。理由: undo_enabled/redo_enabled は段の有無から導ける派生値で、画面ごとに別の状態を持つ必要がない。
- DC-3 OutputSettings を History に入れるかは**決めない**(外部動作が変わるので Q1 の答えに従う)。どちらにも組めるよう、History が持つ型を Document か「Document+OutputSettings」かの 1 か所で決まる形にしておく。
- 集約の境界(Document と History を同じ単位で変えるか)は候補であり、唯一の分割とは言っていない。

## 5. 矛盾・ゆれ

- **CF-01(CONFLICT 寄り・同じ文脈で両立しない可能性)**: 選択の決まり方。REQ-003 rationale は「再生ヘッドの下の区間が編集対象」、REQ-004 反例 3 は「id の再利用で undo が選択を別の区間へ解決する」— 選択が区間 id として保持され、Undo の後に id から解決されることを示す。どちらの読みでも同じ結果になる場面(取り消す編集で選択区間の id と範囲が変わらない)は例で値を書き、分かれる場面(分割・結合の取り消し・やり直しで、選んでいた id が消える/現れる)は `unresolved` にした。問い Q2。
- 再実装と原製品の差: REQ-013 の UQ-REQ-013-001 は「再実装では出力設定をコアの設定モデルに置く。置き場所は E-BOM の判断で利用者への問いではない」としている。置き場所は内部の問題だが、**Undo で出力設定が戻るかは利用者に見える動作**なので、こちらは Q1 として利用者へ返す(置き場所そのものは問わない)。

## 6. 振る舞い契約(部分)

| 契約ID | 前提・履歴 | 操作 | 実行条件 | 更新・保持 | 結果 | 観測 | 根拠 |
|---|---|---|---|---|---|---|---|
| B-01 | undo 側に 1 段以上 | Undo | undo_enabled=true | Document ← undo 側の最新。取り消した Document を redo 側へ | 成功 | 区間・トリム由来の表示がその段の値。redo_enabled=true。undo_enabled は残り段の有無 | U-01, U-06, U-07 |
| B-02 | redo 側に 1 段以上 | Redo | redo_enabled=true | Document ← redo 側の最新。現在を undo 側へ | 成功 | 同上。redo_enabled は残り段の有無 | U-02 |
| B-03 | 任意 | 編集(Split/結合/In/Out/速度/音量)で Document が変わる | その編集の実行条件(REQ-004/006/007) | 現在を undo 側へ積み、redo 側を空にする。51 段目なら最古を落とす | 成功 | undo_enabled=true, redo_enabled=false | U-03, U-04 |
| B-04 | 任意 | 編集の実行条件を満たさない | — | 変えない(REQ-004「leaves the document unchanged」) | 拒否 | 段は増えない(DERIVED: ドキュメントが変わらない) | REQ-004。ボタンは押せない前提で例にしていない |
| B-05 | 任意 | 再生ヘッドの移動 | — | History を変えない | 成功 | undo/redo_enabled 不変 | U-09(P0) |
| B-06 | 任意 | 出力設定の変更 | — | 未決 | 未規定 | — | U-10(Q1) |
| B-07 | 任意 | 値が変わらない編集 | — | 未決 | 未規定 | — | U-11(Q3) |
| B-08 | undo 側が空 | Undo | undo_enabled=false | — | ボタンは使えない(押した時の受付は未規定) | undo_enabled=false | U-06 |

Undo 後の再生ヘッド・選択(U-12)と未保存表示(U-13)は、B-01/B-02 の「観測」から外してある(未決)。
