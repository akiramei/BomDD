# 02 要求・CAD・ドメインモデル・振る舞い契約の対応 — Undo/Redo

由来区分: EXP=SOURCE_EXPLICIT / DER=SOURCE_DERIVED / DC=DESIGN_CHOICE / PRO=PROPOSAL / UNR=UNRESOLVED / CON=CONFLICT。
位置の略記は `01-input-and-scope.md` の資料 ID(REQ-nnn は `sources/10-requirements.yaml`、README.md:n は英語版の行)。

## 1. 原資料にある Undo/Redo の主張(母集団)

| ID | 主張(条件 → 操作 → 結果) | 位置 | 区分 |
|---|---|---|---|
| F-01 | すべての編集は取り消し・やり直しできる | REQ-012 statement・README.md:23 | EXP |
| F-02 | 段数の上限は 50。51 段目で最も古い段が落ちる | REQ-012・README.md:23(「up to 50」) | EXP |
| F-03 | 新しい編集は Redo の段を消す | REQ-012 | EXP |
| F-04 | 1 回の連続ドラッグは 1 段。ドラッグ開始時に 1 回だけ保存する | REQ-012・README.md:145 | EXP |
| F-05 | 履歴は不変ドキュメント(DocumentState)の状態全体を積む(差分の再実行ではない) | REQ-012 rationale・README.md:145・README.ja.md:27 | EXP |
| F-06 | 拒否された分割はドキュメントを変えず、新しいドキュメントを返さない | REQ-004 statement・rationale | EXP |
| F-07 | Undo は選択を区間 id で解決する(だから新しい id を使い回すと誤った区間が選ばれる) | REQ-004 反例 3 | DER(反例からの読み取り。規範文ではない) |
| F-08 | 分割で後ろ側だけが新しい id、結合では左の区間の id が残る | REQ-004・REQ-006 | EXP |
| F-09 | ショートカット Ctrl+Z / Ctrl+Y(Ctrl+Shift+Z) | README.md:25 | EXP(CAD に操作がないので今回は扱わない) |
| F-10 | 起動直後は Undo・Redo とも使えず、表示は「保存済み」 | cad/start-screen.json | EXP(観測) |

注意: README.md:19 の「merge (undo a split)」の undo は「分割の逆操作」の意味で、履歴の Undo ではない。

## 2. CAD 対応

| CAD 要素 | 位置 | 対応する概念・状態 | 区分 |
|---|---|---|---|
| `Undo` ボタン(ToolbarView・"Undo") | cad/actions.json | 契約 B-03 | EXP |
| `Redo` ボタン(ToolbarView・"Redo") | cad/actions.json | 契約 B-04 | EXP |
| `undo_enabled` | cad/observations.json | = Undo 段が 1 つ以上ある | DER(F-01・F-10) |
| `redo_enabled` | cad/observations.json | = Redo 段が 1 つ以上ある | DER(F-03・F-10) |
| `region_count`・`trim_*`・`output_length`・`selected_*` | cad/observations.json | ドキュメント(+選択)からの派生。Undo/Redo で一緒に戻る | DER(F-05・REQ-011) |
| `split_enabled`・`trim_in_enabled`・`trim_out_enabled` | cad/observations.json | ドキュメントと再生ヘッドからの派生(CanSplitAt / CanTrimStartAt / CanTrimEndAt) | DER: start-screen の trim_out_enabled=false が CanTrimEndAt(20)=false(再生ヘッドが最後の区間にない)と一致することからの類推 |
| `merge_enabled` | cad/observations.json | 選択区間が先頭でない(ボタン文言「Merge the current region with the one before it」) | DER: start-screen で先頭区間選択時 false |
| `out_fps`・`out_width`・`out_height`(Scale・SetFps) | cad/observations.json・actions.json | 出力設定。履歴に入るかは Q2 | UNR |
| `playhead`(ToStart/ToEnd/StepBack/StepForward) | 同上 | 再生ヘッド。移動は編集ではない(B-05)。Undo で戻るかは Q5 | DER / UNR |
| `unsaved` | cad/observations.json | 何が「未保存」にするか資料にない。保存の操作も CAD にない | UNR(Q4) |

**属性と表示義務の区別**: 履歴の段数、何が戻るかの名前(「分割を元に戻す」等)、区間 id、ピッチ維持フラグは画面に出す義務の根拠がない。画面に出るのは `undo_enabled`/`redo_enabled` の 2 値だけで、段数の表示や Undo 内容のツールチップを要求に加えない。

## 3. 振る舞い契約(部分)

| ID | 前提・履歴 | 操作 | 実行条件 | 更新・保持 | 結果 | 観測 | 根拠 |
|---|---|---|---|---|---|---|---|
| B-01 | 任意 | 受け付けられた編集(Split・DeleteSelectedBoundary・SetTrimIn/Out・速度/音量プリセット・ドラッグ) | 各編集の条件(REQ-004〜010) | 直前のドキュメントを Undo 段に積む・Redo 段を空にする・51 段目で最古を落とす | 成功 | undo_enabled=true・redo_enabled=false・各派生表示が新しい状態 | F-01〜F-04 EXP |
| B-02 | 分割位置が区間の端から 0.5 秒未満 | Split | 拒否 | ドキュメント不変。履歴も積まない | 拒否(UI ではボタン不可) | split_enabled=false | F-06 EXP(履歴を積まないのは「新しいドキュメントを返さない」からの DER) |
| B-03 | Undo 段 ≥ 1 | Undo | undo_enabled | 現在の状態を Redo 段へ、Undo 段の最上段を現在へ | 成功 | ドキュメント由来の表示がすべてその状態に戻る。選択は id で解決(F-07)。id がもう無いときの選択は **Q1** | F-01・F-05 EXP、選択は DER/UNR |
| B-04 | Redo 段 ≥ 1 | Redo | redo_enabled | 現在を Undo 段へ、Redo 段の最上段を現在へ。**保存した状態に戻すのであって、今の再生ヘッドで操作をやり直すのではない** | 成功 | 同上 | F-05 EXP → EX-04 |
| B-05 | 任意 | StepForward・StepBack・ToStart・ToEnd | — | 履歴を変えない(Undo 段も Redo 段も残る) | 成功 | undo/redo_enabled は不変 | DER: 再生ヘッドはプレビュー側(README.md:147・:126)でドキュメント外。F-01 の「編集」に当たらない |
| B-06 | 任意 | Scale:*・SetFps:* | — | 出力設定を変える。**履歴に積むか・Redo を消すか・Undo で戻るかは Q2** | 成功 | out_* は REQ-013 どおり | REQ-013 EXP / 履歴は UNR |
| B-07 | 値がすでに同じ | ApplySpeedPreset:*・ApplyVolumePreset:* | — | **段を積むかは Q3** | 成功 | 値は不変 | UNR |
| B-08 | Undo 段 = 0 / Redo 段 = 0 | (ショートカットでの Undo/Redo) | — | 未規定 | 未規定 | — | CAD 外。「無視」とも「拒否」とも決めない |
| B-09 | 任意 | Undo/Redo | — | 「未保存/保存済み」表示の変化は **Q4** | 未規定 | unsaved | UNR |

守る条件:

| ID | 条件 | いつ | 根拠 |
|---|---|---|---|
| INV-01 | Undo 段の数 ≤ 50 | 各編集の完了時 | F-02 EXP |
| INV-02 | 編集の直後は Redo 段が空 | 各編集の完了時 | F-03 EXP |
| INV-03 | Undo の直後に Redo すると、Undo 前と同じドキュメント(値として等しい) | 操作完了時 | F-05 DER |
| INV-04 | Undo/Redo は再生ヘッドの位置で何かを再計算しない | 操作完了時 | F-05 DER |

## 4. ドメインモデル候補

| 概念 | 意味 | 識別 | 状態 | 根拠 |
|---|---|---|---|---|
| Document(DocumentState) | 1 本のクリップの編集内容。不変の値 | 値として比較(識別なし) | クリップ情報・区間列・トリム範囲 | REQ-002・README.md:145 |
| Region | タイムラインの区間 | id(分割で後ろに新 id・結合で左の id が残る) | start・end・speed・pitch・volume・excluded | REQ-003〜010 |
| EditHistory | 取り消し・やり直しの段 | 編集セッションに 1 つ | Undo 段(≤50 個の Document)・Redo 段 | REQ-012 |
| Selection | 編集対象の区間 | — | 区間 id(Document の外) | F-07(DER)・README.md:18 |
| Playhead | 再生位置(ソース時刻) | — | 秒 | README.md:147。Document の外(DER)・Undo で戻るかは Q5 |
| OutputSettings | 出力の幅・高さ・fps | — | width・height・fps | REQ-013・UQ-REQ-013-001。履歴との関係は Q2 |
| SaveStatus | 「未保存/保存済み」 | — | 不明 | cad/observations.json のみ。Q4 |

関係と責務の候補:
- EditHistory は Document の値を積むだけで、編集の規則(分割・トリム)は Document 側(REQ-012 rationale「The document is immutable, so history holds whole states」)。
- Selection は Document の外にあり、Undo/Redo のたびに「その id の区間」を新しい Document から引き直す(F-07)。id が新しい Document に無い場合(分割の Undo で後ろ側の id が消える等)の扱いは未規定 → Q1。
- `undo_enabled`・`redo_enabled`・`split_enabled` 等は保存する値ではなく派生値。

## 5. 委任範囲で決めた内部設計(DESIGN_CHOICE・外部動作は変えない)

| 選択 | 理由 |
|---|---|
| 履歴は Document の参照を 2 本の有界スタック(Undo 側は先頭を落とせる両端キュー)で持つ | F-05 と INV-01 をそのまま満たす最小の形。差分方式は INV-03 の証明が要る |
| EditHistory を Document と別の部品(編集セッション側)に置く | Document は不変の値で、履歴は時系列の可変状態。境界はこれが唯一ではない(集約の分け方は候補) |
| Selection は区間 id で保持し、区間の位置では保持しない | F-07。位置で持つと分割後の Undo で別区間を指しうる |

PROPOSAL(未採択): なし。業務上の追加(段数表示・Undo 内容の表示など)は提案しない。

CONFLICT: 検出した範囲ではなし。ただし F-01「every edit」と、出力設定がドキュメント外にあること(UQ-REQ-013-001)は両立の仕方が決まっていない(Q2・矛盾ではなく不足として扱う)。
