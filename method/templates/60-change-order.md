# Change / Corrective Order — <ECO/CAPA-ID>(Phase 7 変更/是正オーダー)

> 納品後の仕様変更・機能追加・欠陥是正の再入口(playbook §8・candidate / forward-01.5 で1回検証済み)。
> 規律: 影響分析で**絞り込み**+**影響なし予測の先行凍結**、部分再製造は fresh factory、既存固定オラクルは**不変**(回帰のヤードスティック)。
> 欠陥是正の規律: 直接ソース修正から始めない。まず Phase 5 の帰属調査で `spec_omission / bom_sync_gap / oracle_gap / manufacturing_miss / harness_bug` を決め、原因が仕様/BOM/検査器なら上流成果物を改訂・同期してから再製造する。
> 詳細ワークシート: 影響分析=[61-impact-analysis.md](61-impact-analysis.md) / データ移行=[62-migration-oracle.md](62-migration-oracle.md) / 不要改変監査=[63-diff-audit.md](63-diff-audit.md) / 部品分割・置換=[64-part-lineage-reattribution.md](64-part-lineage-reattribution.md)。

## 担当設備(equipment — 起票時から記録・ECO 途中の交代も追記)

> 由来: equip-01 遡及採点(2026-08-02・BomDD ECO-028)— 遡及 5 台帳で台帳本文の設備記録 0/60・
> 設備交代 2 回が無記録(commit trailer でのみ可視)。識別の成否は「記録を要求する様式の有無」に従う。

- 製造(設計者/工場ごとに 1 行):
  - requested: <要求したモデル・alias(例: claude-fable-5 / gpt-5.6-sol)>
  - resolved: <実到達モデル。**確認できなければ `unknown` — 推定で埋めない**>
  - ハーネス: <CLI・統合層とその版(例: Claude Code vX / Codex CLI vY)>
  - 来歴: observed(機械記録: as-built・セッションログ・API 応答)/ self-reported(申告・ハーネス表示)の別を明記
- 検査官(独立検査併用時): 同 4 項+read-only の強制方法・セッション分離の有無
- 注意: requested と resolved は**乖離しうる**(実測: `gpt-5.6-sol` 要求が統合層のクライアント識別ゲートで `gpt-5.5` へ到達 — transfer-04)。commit trailer は自己申告であり resolved の証明にならない。設備構成(モデル・ハーネス・prompt)が ECO 途中で変わったら、変更点と時点を本欄へ追記する(**交代の無記録が最危険**)

## 0. 変更前 baseline の凍結
- As-Maintained 個体: <どの工場のどのビルドを改修するか(tag/commit)>
- データ fixture(永続データを持つ題材): <実データ DB+期待値 manifest(62 §1)>
- 既存固定オラクル: <S-行の範囲。凍結済み・不変>

## 1. 変更/欠陥要求
- ID:
- 発生契機: 仕様変更 / 機能追加 / ユーザー指摘 / 固定オラクル失敗 / 探索プローブ / 保守イベント
- 内容(1〜3行):
- 種別: REQ 追加 / REQ 改訂 / 欠陥修正(=劣化部品の交換)
- 欠陥帰属(欠陥修正時): spec_omission / bom_sync_gap / oracle_gap / manufacturing_miss / harness_bug
- 観測と再現手順(欠陥修正時):
- 原因が宿った上流成果物:
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
- 部品分割・置換がある場合: [64-part-lineage-reattribution.md](64-part-lineage-reattribution.md) を作り、旧 ID の active 参照を全て再帰属する
- 同期確認: REQ / 仕様 / E-BOM / K-BOM / M-BOM / Control Plan / Oracle / Routing / Work Order
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
