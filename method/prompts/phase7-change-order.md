# Phase 7 — 変更オーダー(設計者 AI への指示)

典拠: `method/bomdd-playbook-v1.md` §8(candidate・未実証)。テンプレ: `method/templates/60-change-order.md`。
入力: 納品済みの `bomdd/` 一式(BOM・固定オラクル・治具・As-Built)+変更要求。

## 規律(先に確認)
- **既存固定オラクル行は変更しない**(回帰のヤードスティック)。変更分の受入は**新規行として追加**する。
- 部分再製造の単位は **M-BOM unit**。再製造工場は fresh(変更前コード・設計対話・旧 cheat 非開示)。
- 影響分析は**絞り込み**が価値(under-inclusion=取りこぼしが最危険。影響なし判定には根拠を書く)。

## 手順
1. **変更要求の受理**: 変更を REQ の追加/改訂として書く(Phase 1 の根拠精度の規律 G1 を適用)。
2. **影響分析**: トレースを逆引きし(REQ→仕様節→E-BOM 部品[graph_edges の consumers 含む]→M-BOM unit→Control Plan→オラクル行→K-BOM/調達部品)、`bomdd/60-change-order.md` の影響表を埋める。
3. **BOM 改訂**: 影響部品だけを改訂し bom_rev を上げ tag を打つ。**再製造の前に**変更分の受入(新オラクル行・test_vectors・Control Plan 行)を追加する(オラクル・ファースト)。沈黙掃討: 変更が新しい沈黙次元を持ち込んでいないか `method/silence-checklist.md` の関連カテゴリを再掃討。
4. **部分再製造**: 変更された M-BOM unit のみを fresh サブエージェントに再鋳造させる(供与物=改訂 BOM+当該 unit の interface_contract+work order。Phase 4 の隔離規律と同じ)。未変更 unit は再利用。部分再製造が成立しない場合は理由を記録(粒度設計へのフィードバック)。
5. **回帰+変更受入**: 既存固定オラクル全行と新規行を実行。差分は「回帰(既存行)/変更の不備(新規行)」に帰属を分けて報告する。
6. **記録**: As-Built 追記・Service BOM 更新・cheat-log(C6 系)・metrics(`52-metrics.yaml` に ECO 行)。
