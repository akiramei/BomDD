# Change Order — <ECO-ID>(Phase 7 変更オーダー)

> 納品後の仕様変更・機能追加の再入口(playbook §8・candidate)。
> 規律: 影響分析で**絞り込み**、部分再製造は **M-BOM unit 単位・fresh factory**、既存固定オラクルは**不変**(回帰のヤードスティック)。

## 1. 変更要求
- ECO-ID:
- 変更内容(1〜3行):
- 種別: REQ 追加 / REQ 改訂 / 欠陥修正(=劣化部品の交換)
- REQ への反映: <REQ-xxx 新規 or 改訂。根拠精度の規律(G1)を適用>

## 2. 影響分析(トレース逆引き)
| 段 | 影響 ID | 備考 |
|---|---|---|
| 仕様節 | | |
| E-BOM 部品(graph_edges 含む) | | woven の consumers を忘れない |
| M-BOM unit | | **=再製造する単位** |
| Control Plan 特性 | | |
| 固定オラクル行 | | 既存行は変更しない。新規行のみ追加 |
| K-BOM / 調達部品 | | |
- 影響なしと判定した部品の根拠(under-inclusion=取りこぼしが最危険):

## 3. BOM 改訂
- bom_rev: <旧> → <新>(tag: )
- 改訂ファイル:
- **変更分の受入を先に追加**(オラクル・ファースト): 新オラクル行 / test_vectors / Control Plan 行:

## 4. 部分再製造
- 再製造 unit: <M-xxx のみ>
- 再利用 unit: <変更なし一覧>
- 工場: fresh factory(変更前コード・設計対話・旧 cheat 非開示。改訂 BOM+当該 unit の interface_contract を供与)
- 部分再製造できなかった場合: 理由を記録(粒度設計の失敗として playbook §4.1 へフィードバック)

## 5. 回帰+変更受入
- 既存固定オラクル全行(不変): <結果。差分=回帰>
- 新規オラクル行: <結果。差分=変更の不備>
- 差分帰属(回帰/変更不備を混ぜない):

## 6. 記録
- As-Built 追記(50): / Service BOM 更新(53): / cheat-log(51・C6系):
