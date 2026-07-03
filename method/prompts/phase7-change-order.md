# Phase 7 — 変更/是正オーダー(設計者 AI への指示)

典拠: `method/bomdd-playbook-v1.md` §8(candidate / forward-01.5+forward-02 で2回検証済み)。テンプレ: `method/templates/60-change-order.md`(+61 影響分析 / 62 移行・効力オラクル / 63 不要改変監査)。
入力: 納品済みの `bomdd/` 一式(BOM・固定オラクル・治具・As-Built)+変更要求、または Phase 5 で帰属済みの欠陥指摘。

## 規律(先に確認)
- **既存固定オラクル行は変更しない**(回帰のヤードスティック)。変更分の受入は**新規行として追加**する。
- **影響なし予測を反証可能な形で製造前に凍結**する(回帰結果が予測の採点。外れ=under-inclusion)。
- 再製造工場は fresh(設計対話・オラクル・旧 cheat 非開示)。**非開示には移行オラクル実装・fixture 期待値を含める**。
- 影響分析は**絞り込み**が価値(under-inclusion=取りこぼしが最危険。影響なし判定には根拠を書く)。小規模で影響集合が全 unit に達する場合は E-BOM 粒度+diff 測定で代替(playbook §4.1)。
- 欠陥是正では**直接ソース修正から始めない**。Phase 5 の帰属(`spec_omission / bom_sync_gap / oracle_gap / manufacturing_miss / harness_bug`)を確認し、原因が仕様/BOM/検査器なら上流成果物を改訂・同期してから再製造する。

## 手順
0. **baseline 凍結**: 改修対象の As-Maintained 個体(どの工場ビルドか)を固定。永続データを持つ題材は、その個体から**実データ fixture+期待値 manifest** を採取する(62 §1)。
1. **変更/欠陥要求の受理**: 変更を REQ の追加/改訂として書く。欠陥修正なら、観測・再現手順・期待/実際・欠陥帰属・原因が宿った上流成果物を記録してから、必要な REQ/仕様改訂を書く(Phase 1 の根拠精度の規律 G1 を適用)。
2. **影響分析**: トレースを逆引きし(REQ→仕様節→E-BOM 部品[graph_edges の consumers 含む]→M-BOM unit→Control Plan→オラクル行→K-BOM/調達部品)、影響表を埋める。部分改修では**As-Maintained 実物の呼び出しサイト点検**(変更対象シンボルの全参照 grep・シグネチャ変更の追従先確認)を行ってから影響集合を凍結する(61 §1.2 — 品目→unit の写像は BOM だけでは辿れない)。**同時に「影響なし」側を既存オラクル行1行ずつ根拠付きで予測し、「ファイル単位の diff ゼロ」級の反証可能な形で製造前に凍結**する(61 §2)。
3. **BOM 改訂**: 影響部品だけを改訂し bom_rev を上げる。split / supersede / retire がある場合は、必ず `method/templates/64-part-lineage-reattribution.md` を作り、旧 ID の active 構造参照(E-BOM depends_on/consumers、M-BOM ebom_refs、Control Plan verifies、Service BOM part_ref、UI-BOM/trace-map、active TraceLink)を全て再帰属し、Active Graph Integrity gate を `0 stop findings` で通す。prose の同期だけは `deferred-content-only` にできるが、ID ラベルの張り替えは繰延不可。**再製造の前に**変更分の受入(新オラクル行・test_vectors・Control Plan 行)を追加する(オラクル・ファースト)。スキーマ変更を伴う場合は移行専用オラクル+fixture を立てる(62)。スキーマ変更が無い規則変更でも、効力(遡及の有無・確定値と再計算の別)を REQ に明文化し、効力専用オラクル+fixture を立てる(62 §5)。沈黙掃討: 変更が新しい沈黙次元を持ち込んでいないか `method/silence-checklist.md` の関連カテゴリを再掃討し、原典あり UI/帳票 surface では表示パリティ行を再確認する。REQ/仕様/E-BOM/K-BOM/M-BOM/Control Plan/Oracle/Routing/Work Order の同期を確認する。**治具はセルフテスト+較正(変更前個体に対し既存行=PASS・新規行=FAIL)を通してから凍結 tag**(playbook §4.4)。
4. **部分再製造**: 変更影響箇所のみを fresh サブエージェントに改修/再鋳造させる。部分**改修**の場合は変更前ソースの複製を**設計者が事前コミット=diff 基準点**にする(63)。work order に「影響分析にある箇所だけを改修。影響なし箇所への変更は禁止。diff を測定する」と**事前宣言**し、自己受入**赤=stop/report**(nonconformance。納品・採点しない)を明記する。未変更 unit は再利用。部分再製造が成立しない場合は理由を記録(粒度設計へのフィードバック)。
5. **回帰+変更受入**: 既存固定オラクル全行・新規行・移行オラクルを実行し、納品 diff を基準点と突合する。**失敗5分類**で帰属: `regression`(既存行)/ `change miss`(新規行)/ `data-preservation miss`(移行)/ `unnecessary modification`(影響分析外 diff。format-noise / test-only / behavior-risk / contract-change)/ `manufacturing nonconformance`(自己受入赤)。影響なし予測の的中(under/over-inclusion)を採点する(61 §3)。
6. **記録**: As-Built 追記(不要改変件数込み)・Service BOM 更新・cheat-log(C6 系)・metrics(`52-metrics.yaml` に ECO 行)。
