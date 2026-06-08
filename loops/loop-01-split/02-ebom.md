# ② E-BOM — 区間分割(Split)スライス

単位は「責務・存在理由を持つ**論理部品**」(Class/関数ではない)。各部品は存在理由(REQ)へトレースする。
**共有/横断(woven)**列 = このスライス専用でなく他機能と共有される部品(=純粋な木構造に乗らない)。

## 論理部品表

| 品目コード | 論理部品名 | 責務 | 存在理由(REQ) | 共有/横断 | 製造区分 |
|---|---|---|---|---|---|
| EB-EDIT-DOC | 編集ドキュメント | トリム範囲と区間列を**不変**に保持。編集操作は新インスタンスを返す | REQ-SPLIT-8, 前提制約 | ◎ 全編集機能の基盤 | generate |
| EB-REGION | 区間モデル | 1区間の属性(時刻/速度/ピッチ維持/音量/除外)と派生値 | REQ-SPLIT-4 | ◎ 全編集機能 | generate |
| EB-SPLIT | 区間分割ロジック | 直下区間を分割点で2分割し属性継承。可否判定 | REQ-SPLIT-1,4,5 | ○ スライス中核 | generate |
| EB-TIMEQ | 時間・フレーム整合 | フレームグリッドへのスナップ、最小長/クランプ | REQ-SPLIT-5,6 | ◎ 全編集機能 | generate |
| EB-IDGEN | 区間ID採番 | 衝突しない単調増加IDの払い出し(load時に最大+1へ再初期化) | NFR-SPLIT-2 | ○ 分割で生成 | generate |
| EB-HISTORY | 編集履歴 | undo/redo のためのstateスナップショット(上限50) | REQ-SPLIT-7 | ◎ 全離散編集 | generate(U1要確定) |
| EB-SELECT | 編集対象選択解決 | state差替後に「編集対象=再生ヘッド直下」へ選択IDを再同期 | REQ-SPLIT-3 | ◎ 全編集 | generate |
| EB-SPLIT-CMD | 分割コマンド(統合) | 入力→採番→分割→履歴→選択 のオーケストレーション。活性条件 `CanSplit` | REQ-SPLIT-1,2,3,7 | ○ スライス中核 | generate |
| EB-KEYMAP | キー入力割付 | `S`(Ctrl無/非入力中)を分割コマンドへ | REQ-SPLIT-2 | ◎ 全ショートカット | generate(U3要判断) |
| EB-TIMELINE | タイムライン表示 | state を視覚化(分割で境界線が出現) | REQ-SPLIT-1(可視) | ◎◎ 自前描画・重横断 | generate(難) |

## 構成関係(展開)
```
区間分割スライス
├─ EB-SPLIT-CMD (統合)
│   ├─ uses → EB-IDGEN
│   ├─ uses → EB-SPLIT ──→ EB-EDIT-DOC ──→ EB-REGION
│   │                  └─→ EB-TIMEQ
│   ├─ uses → EB-HISTORY (← EB-EDIT-DOC のスナップショット)
│   └─ uses → EB-SELECT  (← EB-EDIT-DOC)
├─ EB-KEYMAP ──trigger──→ EB-SPLIT-CMD
└─ EB-TIMELINE ──observe──→ EB-EDIT-DOC
```

## E-BOM が既に露呈させた構造的事実(→ 分析へ)
1. **木構造に乗らない**: ◎印の EB-EDIT-DOC / EB-TIMEQ / EB-HISTORY / EB-SELECT / EB-KEYMAP / EB-TIMELINE は
   「分割スライス」専用部品ではなく**全編集機能と共有(woven)**。1スライスの E-BOM は独立サブツリーにならない。→ CHEAT-002 / 分類C5。
2. **存在理由が前方仕様でない部品がある**: EB-SELECT(`ResolveSelection`)は**バグ修正由来**で生まれた部品で、
   存在理由が「要求」でなく「観測された欠陥クラス」。E-BOM の「存在理由=どの仕様による」枠に収まらない。→ CHEAT-003 / 分類C1。
3. **同一性の払い出し(EB-IDGEN)はドメイン外**: 分割ドメイン `SplitAt` は newId を**引数で受け取る**。
   「誰がIDを採番するか」は統合(オーケストレーション)責務であり、ドメイン部品の責務でない。設計の継ぎ目として明示が要る。
