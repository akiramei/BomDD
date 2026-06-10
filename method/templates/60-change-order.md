# Change Order — <ECO-ID>(Phase 7 変更オーダー)

> 納品後の仕様変更・機能追加の再入口(playbook §8・candidate / forward-01.5 で1回検証済み)。
> 規律: 影響分析で**絞り込み**+**影響なし予測の先行凍結**、部分再製造は fresh factory、既存固定オラクルは**不変**(回帰のヤードスティック)。
> 詳細ワークシート: 影響分析=[61-impact-analysis.md](61-impact-analysis.md) / データ移行=[62-migration-oracle.md](62-migration-oracle.md) / 不要改変監査=[63-diff-audit.md](63-diff-audit.md)。

## 0. 変更前 baseline の凍結
- As-Maintained 個体: <どの工場のどのビルドを改修するか(tag/commit)>
- データ fixture(永続データを持つ題材): <実データ DB+期待値 manifest(62 §1)>
- 既存固定オラクル: <S-行の範囲。凍結済み・不変>

## 1. 変更要求
- ECO-ID:
- 変更内容(1〜3行):
- 種別: REQ 追加 / REQ 改訂 / 欠陥修正(=劣化部品の交換)
- REQ への反映: <REQ-xxx 新規 or 改訂。根拠精度の規律(G1)を適用>

## 2. 影響分析(トレース逆引き+影響なし予測)
| 段 | 影響 ID | 備考 |
|---|---|---|
| 仕様節 | | |
| E-BOM 部品(graph_edges 含む) | | woven の consumers を忘れない |
| M-BOM unit | | 小規模で全 unit に達したら E-BOM 粒度+63 で代替(playbook §4.1) |
| Control Plan 特性 | | |
| 固定オラクル行 | | 既存行は変更しない。新規行のみ追加 |
| K-BOM / 調達部品 | | |
- **影響なし予測(反証可能・製造前に凍結)**: <既存オラクル行・非対象ファイル群と根拠。詳細は 61 §2>(under-inclusion=取りこぼしが最危険)

## 3. BOM 改訂
- bom_rev: <旧> → <新>(tag: )
- 改訂ファイル:
- **変更分の受入を先に追加**(オラクル・ファースト): 新オラクル行 / test_vectors / Control Plan 行 / 移行オラクル(スキーマ変更時。62):
- **治具の凍結条件**: セルフテスト+**較正**(変更前個体に対し既存行=PASS・新規行=FAIL。playbook §4.4):

## 4. 部分再製造
- 再製造/改修対象: <影響箇所のみ>
- 再利用 unit: <変更なし一覧>
- 工場: fresh factory(設計対話・旧 cheat 非開示)。部分**改修**の場合は変更前ソースの複製を**事前コミット=diff 基準点**(63)
- 渡すもの: <改訂 BOM+本 ECO+(改修なら)ソース複製> / **渡さないもの**: 設計対話・固定オラクル・探索プローブ・**移行オラクル実装・fixture 期待値**・他工場成果
- 自己受入: <既存ハーネス+追加 vectors>。**赤=stop/report**(nonconformance。納品・採点しない)
- 部分再製造できなかった場合: 理由を記録(粒度設計の失敗として playbook §4.1 へフィードバック)

## 5. 回帰+変更受入(失敗5分類で帰属)
| 観測 | 分類 |
|---|---|
| 既存オラクル行の失敗 | **regression** |
| 新規行の失敗 | **change miss** |
| 移行オラクルの失敗 | **data-preservation miss** |
| 影響分析外への diff | **unnecessary modification**(format-noise / test-only / behavior-risk / contract-change) |
| 自己受入赤での停止 | **manufacturing nonconformance**(採点対象外) |
- 結果:

## 6. 記録
- As-Built 追記(50・不要改変件数込み): / Service BOM 更新(53): / cheat-log(51・C6系): / metrics(52・ECO 行):
