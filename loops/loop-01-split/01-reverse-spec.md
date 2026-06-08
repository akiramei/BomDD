# ① リバース復元仕様 — 区間分割(Split)スライス

MoviePad のソース/テストから復元した要求・機能仕様。各項に**出典(原版 file:line)**を付し監査可能にする。
※ この出典は研究用の監査証跡。**製造装置には出典を渡さない**(オラクル汚染防止)。

## 用語・前提制約(ドメイン不変条件)
- 区間 `RegionData` は隙間なく順序付きで敷き詰まる(`region[i].End == region[i+1].Start`)。出典: RegionData.cs:4
- 時刻は**半開区間 [Start, End)**。境界時刻ちょうどは**後続区間**に属する。**最終区間のみ終端を含む**。出典: DocumentState.cs:52-69
- 最小区間長 `MinLen = 0.5s`、既定 `DefaultFps = 30`。出典: TimeMath.cs:9-12
- 編集は**非破壊**: `DocumentState`/`RegionData` は record で、全操作が新インスタンスを返す。出典: DocumentState.cs:7-12

## 要求仕様(REQ)
| ID | 要求 | 出典 |
|---|---|---|
| REQ-SPLIT-1 | ユーザーは再生ヘッド位置で、その直下の区間を2つに分割できる | README.ja.md:22, DocumentState.cs:158 |
| REQ-SPLIT-2 | 分割は **S キー**(Ctrl無し・テキスト入力中は無効)またはツールバーボタンで起動 | MainWindow.axaml.cs:51, README.ja.md:28 |
| REQ-SPLIT-3 | 分割後、**後半(新規)区間が編集対象(選択)**になる | MainWindowViewModel.cs:722-724 |
| REQ-SPLIT-4 | 分割は元区間の **速度・ピッチ維持・音量を両区間に継承** | DocumentState.cs:174-175, Tests:78-80,306-313 |
| REQ-SPLIT-5 | 区間端から **MinLen(0.5s)以内**、または**区間外/トリム外**では分割不可 | DocumentState.cs:166-167, Tests:84-90 |
| REQ-SPLIT-6 | 分割点は**フレームグリッドにスナップ**(`SnapFrame`) | DocumentState.cs:164 |
| REQ-SPLIT-7 | 分割は **1回の undo 単位**として履歴に積まれる(履歴最大50) | MainWindowViewModel.cs:680-688, README.ja.md:27 |
| REQ-SPLIT-8 | 編集は非破壊(元 state は不変) | Tests:233-242 |

## 非機能要求(NFR)
| ID | 非機能要求 | 出典 |
|---|---|---|
| NFR-SPLIT-1 | 分割は不変リストの O(n) コピーで即時(知覚遅延なし) | DocumentState.cs:169-182 |
| NFR-SPLIT-2 | 新IDは既存最大ID+1から単調増加、衝突しない | MainWindowViewModel.cs:50,64,518-522,717-720 |

## 機能仕様(コードから確定した振る舞い)
**起動可否** `CanSplit = HasClip && CanSplitAt(playhead)`。`CanSplitAt`: 直下区間が在り、かつ
`playhead > Start+MinLen && playhead < End-MinLen`。出典: MainWindowViewModel.cs:330, DocumentState.cs:93-98

**分割手順** `Split()`:
1. `newId = _nextId`(初期100。クリップ読込時 `NextIdFor=max(Id)+1` で再初期化)
2. `s = SplitAt(playhead, newId, fps)`; `s==null` なら**何もせず終了**(履歴も汚さない)
3. `SplitAt` 内: `ph = SnapFrame(playhead)` → 直下区間 `r` を `RegionAt(ph)` で特定 →
   `ph` が `r` の端から MinLen 以内なら `null` → 否なら `r` を `{End=ph}` と `{Id=newId, Start=ph}` の2区間に置換(他属性継承)
4. `_nextId++`
5. `CommitEdit(s)`: 旧 state を履歴 snapshot → state 差替 → `ResyncSelection` → `Edited=true`
6. `SelectedId = newId`(後半を選択)
出典: MainWindowViewModel.cs:714-725, DocumentState.cs:162-183

**選択再解決** `ResolveSelection(current, playhead)`: 再生ヘッド直下が在ればそのID、無ければ current が生存なら維持、
それも無効なら先頭区間。出典: DocumentState.cs:85-91(分割直後は後半区間が直下に一致)

## 復元の不確かさ(製造前に解消すべき曖昧点)
- U1: 履歴上限50の正確な破棄方針(FIFO/redoクリア条件)は `History.cs` 未読。→ M-BOM で要確定。
- U2: ツールバー `SplitCommand` の活性条件が `CanSplit` と同期する仕組み(`NotifyCanExecuteChanged`)は未確認。
- U3: 「テキスト入力中は無効」のフォーカス判定は View 層責務(`FocusManager`)。スライス境界に含めるか要判断。
