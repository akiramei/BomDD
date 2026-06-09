# 再現ガイド — v2 分散 Saga 検証(N=3 / Order Fulfillment Saga)

本書は、BomDD の3題材目=**非同期・分散イベント駆動**の主張([FINDINGS.md §6.4](../FINDINGS.md))を
第三者が自分の手で追うための最短手順。検証する主張は3つ。

1. **核/表面の法則が分散・非同期イベント駆動でも再現**(MoviePad / Web-API に続く3題材目)。
2. 単一ファクトリで固定オラクル **0/7**(核を分散ドメインで鋳造)。
3. 多工場(opus/sonnet/haiku)で**挙動契約 0/0/0**=仕様面は全ティアへ転移し、未規定面のみ分散。

> 記述規律: 0/7 は「完全鋳造」でなく**「現固定オラクル(7観点)被覆で未観測差分ゼロ」**。
> sonnet の見かけ上の差(リテラルキー採点 1/7)は**製品でなく観測ハーネスの表現差**(snake_case vs camelCase の dispatch キー)。

---

## 0. 前提
- 証拠は別リポジトリ: **[akiramei/BomDD-DistributedSaga-Sample](https://github.com/akiramei/BomDD-DistributedSaga-Sample)**(公開)。
- 必要: **.NET 10 SDK** / **PowerShell 7+(`pwsh`)**。原版・各工場・設計者オラクル・採点結果はすべてコミット済。

```powershell
git clone https://github.com/akiramei/BomDD-DistributedSaga-Sample
cd BomDD-DistributedSaga-Sample
```

## 1. 固定点(タグ)
| tag | 役割 | commit |
|---|---|---|
| `saga-02-input-bom` | 多工場の**入力 BOM 固定**(factory-01 結果非混入) | `5facf25` |
| `v0.1-saga-multifactory` | **結果固定**(挙動 0/0/0) | `ce21e52` |

コミット列: `cef17bf` seed → `5facf25` 設計者オラクル → `fbed7e7` saga-01(0/7)→ `ce21e52` saga-02(0/0/0)。

## 2. 観測の仕組み(in-process 題材の黒箱境界)
HTTP のようなワイヤ境界が無いので、観測契約 [`loops/saga-01/observation-contract.md`](https://github.com/akiramei/BomDD-DistributedSaga-Sample/blob/main/loops/saga-01/observation-contract.md)
が「固定シナリオ(`scenarios.json`)を流し、**正規化イベントログ/dispatch trace の JSON を emit** する」I/F を定義する。
採点器 [`loops/saga-01/oracle/score.ps1`](https://github.com/akiramei/BomDD-DistributedSaga-Sample/blob/main/loops/saga-01/oracle/score.ps1)
が原版と各工場の正規化結果を**契約セマンティクスで**2-way diff する(キー綴り/JSON 形状/内部 C# 名は**非比較**)。

## 3. 主張2の再現 — saga-01 単一ファクトリ 0/7
**速い経路**: コミット済の `loops/saga-01/result-original.json` と `result-factory01.json` を score.ps1 にかける。
**深い経路**(再生成):
```powershell
dotnet build loops/saga-01/oracle/OracleProbe
dotnet run --no-build --project loops/saga-01/oracle/OracleProbe -- loops/saga-01/scenarios.json > loops/saga-01/result-original.json
dotnet build loops/saga-01/factory-01/Acceptance
dotnet run --no-build --project loops/saga-01/factory-01/Acceptance -- emit (Resolve-Path loops/saga-01/scenarios.json) > loops/saga-01/result-factory01.json
pwsh loops/saga-01/oracle/score.ps1 -Original loops/saga-01/result-original.json -Factory loops/saga-01/result-factory01.json -ContractJson loops/saga-01/factory-01/contracts/events.json
# 期待: FIXED-ORACLE DIFFS: 0 / 7
```

## 4. 主張3の再現 — saga-02 多工場 0/0/0
コミット済の `loops/saga-02/result-{opus,sonnet,haiku}.json` を score.ps1 にかける(または各工場の Acceptance を `-- emit` で再生成。
プロジェクト名は工場で異なる=`loops/saga-02/report.md` 参照):
```powershell
foreach ($t in 'opus','sonnet','haiku') {
  pwsh loops/saga-01/oracle/score.ps1 `
    -Original loops/saga-01/result-original.json `
    -Factory  loops/saga-02/result-$t.json `
    -ContractJson loops/saga-02/$t/contracts/events.json
}
# 期待: opus 0/7 ・ sonnet 0/7(リテラルキー採点は 1/7=観測出力 camelCase)・ haiku 0/7
```

| 工場 | 挙動契約差分 | 帰属 |
|---|---|---|
| opus | **0/7** | capable factory transfer |
| sonnet | **0/7**(リテラル 1/7) | 観測ハーネス表現差(C# camelCase。製品差分でない) |
| haiku | **0/7** | 全ティア転移(webapi-02 の haiku 3/16 と対照) |

## 5. 既知の限界
- **被覆固定**: 7観点(6 ランタイムシナリオ + 1 静的契約)。広げれば未観測次元が出うる。
- **ティア各1試行**: 同ティア再現性は未測定。N=3 だが一般法則は未検証。
- **探索層**は合否非混在の観測値(eventId 形式 / timestamp 精度 / sequence 基点 / inbox 区切り / dispatch キー綴り / JSON 形状)=BOM が沈黙する次元。
- **検査器側の規律**: 設計者オラクル自身が原版の付随表現(JSON 形状・キー綴り)に L0 過剰結合し2度補正した。「オラクルは契約セマンティクスを見る」は検査器にも課す(`bomdd/cheat-log.md` の CHEAT-SAGA-01-002 / -02-002)。

## 6. 関連
- まとめ: [FINDINGS.md §6.4](../FINDINGS.md) / [WHITEPAPER.md §11](../WHITEPAPER.md) / 指標: [loops/metrics-v2.csv](../loops/metrics-v2.csv)
- 証拠リポ: [akiramei/BomDD-DistributedSaga-Sample](https://github.com/akiramei/BomDD-DistributedSaga-Sample)(report: `loops/saga-02/report.md` / `loops/saga-01/report.md`)
- Web/API 版の再現ガイド: [reproduce-webapi-v2.md](reproduce-webapi-v2.md)
