# ② E-BOM(グラフ版) — 改善②: 木→部品グラフ + サブグラフ抽出

Loop 1 の CHEAT-002(1スライスのE-BOMが木にならない=woven)への対処。
E-BOM を**製品全体の部品グラフ**とし、横断部品に **owner(主担当機能)/ consumers(利用機能)** を持たせる。
スライスは「このグラフのサブグラフ抽出 + 共有部品への参照」として定義する。

## 部品ノード(製品グラフの一部。Split スライスに関わる範囲)
| コード | 部品 | 種別 | owner(主担当) | consumers(利用機能) | スライス内の役割 |
|---|---|---|---|---|---|
| EB-EDIT-DOC | 編集ドキュメント | domain | (基盤) | 分割/トリム/速度/音量/除外/境界/履歴/書出 | 中核・共有 |
| EB-REGION | 区間モデル | domain | (基盤) | 全編集・表示・書出 | 中核・共有 |
| EB-TIMEQ | 時間・フレーム整合 | domain | (基盤) | 分割/トリム/境界/表示 | 中核・共有 |
| EB-SPLIT | 区間分割ロジック | domain | 分割 | 分割 | **スライス固有** |
| EB-IDGEN | 区間ID採番 | orchestration | 分割 | 分割 | **スライス固有** |
| EB-HISTORY | 編集履歴 | orchestration | (基盤) | 全離散編集・ドラッグ | 共有 |
| EB-SELECT | 編集対象選択解決 | orchestration | (基盤) | 全編集 | 共有 |
| EB-SPLIT-CMD | 分割コマンド(統合) | orchestration | 分割 | 分割 | **スライス固有** |
| EB-KEYMAP | キー入力割付 | ui | (入力基盤) | 全ショートカット | 共有(分割は S を寄与) |
| EB-TIMELINE | タイムライン表示 | ui | タイムライン | 全編集の可視化 | 共有・重横断 |

## エッジ(関係)
```
EB-KEYMAP        --trigger-->  EB-SPLIT-CMD
EB-SPLIT-CMD     --uses-->     EB-IDGEN
EB-SPLIT-CMD     --uses-->     EB-SPLIT --uses--> EB-EDIT-DOC --contains--> EB-REGION
EB-SPLIT         --uses-->     EB-TIMEQ
EB-SPLIT-CMD     --uses-->     EB-HISTORY  --snapshots--> EB-EDIT-DOC
EB-SPLIT-CMD     --uses-->     EB-SELECT   --reads-->     EB-EDIT-DOC
EB-TIMELINE      --observes--> EB-EDIT-DOC
```

## Split スライス = サブグラフ抽出
- **固有ノード**(このスライスで新規製造): EB-SPLIT, EB-IDGEN, EB-SPLIT-CMD。
- **参照する共有ノード**(既存/他機能と共有, 変更時は consumers へ影響波及): EB-EDIT-DOC, EB-REGION, EB-TIMEQ, EB-HISTORY, EB-SELECT, EB-KEYMAP, EB-TIMELINE。

## 効果(対 CHEAT-002)
横断部品を「木の親子」に無理押しせず、owner/consumers 付きノードとして**記録する場所ができた**。
これにより共有部品の変更影響は consumers を辿って S-BOM 的に追跡可能になる(例: EB-EDIT-DOC を変えると8機能へ波及)。
→ CHEAT-002 の「表現ギャップ」は解消。残課題: グラフの自動抽出・影響波及の定量化は未着手。
