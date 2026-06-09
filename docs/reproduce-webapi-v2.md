# 再現ガイド — v2 Web/API 検証(予約 API)

本書は、BomDD v2 の Web/API 検証([FINDINGS.md §6](../FINDINGS.md) / [WHITEPAPER.md §11](../WHITEPAPER.md))を
**第三者が自分の手で追える**ようにする最短手順である。検証対象の主張は次の3つ。

1. **核/表面の法則が Web/API でも再現する**(MoviePad に続く2題材目)。
2. **BOM を「差分観測→補正→再製造」で締めると鋳造性が漸近的に上がる**(原版との差分 **2 → 3 → 0**)。
3. **多工場で仕様化済み契約は転移し、未規定の表面は分散する**(固定オラクル層 **opus 0 / sonnet 1 / haiku 3**)。

> 記述規律: 差分 0 を「完全鋳造」とは呼ばない。**「現固定オラクル(16シナリオ)被覆で未観測差分ゼロ」**である。
> N=2 ゆえ、すべて「観測した範囲」の主張。

---

## 0. 前提

- 証拠は別リポジトリにある: **[akiramei/BomDD-WebApi-Sample](https://github.com/akiramei/BomDD-WebApi-Sample)**(公開)。
- 必要なもの: **.NET 10 SDK** / **PowerShell 7+(`pwsh`)**。オラクルは PS7 の `-SkipHttpErrorCheck` を使う。
- 原版・各製造品(ファクトリ)・固定オラクル・採点結果 JSON は**すべてコミット済み**。
  したがって再現には2つの深さがある:
  - **(速い)** コミット済みの `result-*.json` を突き合わせて差分件数を確認する。
  - **(深い)** 各ファクトリを再ビルド・起動し、固定オラクルを投げ直して同じ差分を得る。

```powershell
git clone https://github.com/akiramei/BomDD-WebApi-Sample
cd BomDD-WebApi-Sample
```

## 1. 入力の固定点(コミット列)

| commit | 内容 | 原版との差分 |
|---|---|---|
| `35c3022` | seed(原版 + BOM 一式) | — |
| `7b3a4f2` | webapi-01(seed BOM で再製造) | **2 / 16** |
| `c46fe8b` | webapi-01.5(第1次補正) | **3 / 16** |
| `4eed25f` | webapi-01.6(第2次補正) — tag **`webapi-02-input-bom`** | **0 / 16** |
| `84338b0` | webapi-02(多工場 opus/sonnet/haiku) | **0 / 1 / 3** |

多工場ループの入力 BOM はタグで固定されている。確認:

```powershell
git show webapi-02-input-bom --stat   # = 4eed25f(01.6 の締めた BOM)
```

## 2. 採点の仕組み(固定ブラックボックス HTTP オラクル)

採点器は [`loops/webapi-01/blackbox-oracle.ps1`](https://github.com/akiramei/BomDD-WebApi-Sample/blob/main/loops/webapi-01/blackbox-oracle.ps1)。
**ループ間で不変**(同一ヤードスティック)。16 シナリオ(S1–S15、S14 は cancel + 二重 cancel の2件)を任意の `BaseUrl` に投げ、
各応答の **HTTP status / error code** を正規化 JSON で出力する。内部 C# 名には結合しない(L0 過剰結合の回避)。
**予約 ID 値は server 間で当然ばらつくので比較しない。**

```powershell
# 既定 BaseUrl=http://localhost:5099, ApiKey=demo-key
pwsh loops/webapi-01/blackbox-oracle.ps1 -BaseUrl http://localhost:5099
```

## 3. 主張2の再現 — 単一ファクトリ収束 2 → 3 → 0

各ファクトリは別 BOM 改訂から、原版・他ファクトリ・分岐を**一切知らないクリーンな製造装置**で再製造されている
(`factory-01`=seed / `factory-02`=rev1 / `factory-03`=rev2)。

### 速い経路 — コミット済み採点結果を突き合わせる

`loops/webapi-01/` に `result-original.json` と `result-factory0{1,2,3}.json` がある。
各ファクトリ結果を原版結果と status/code で突き合わせると、差分シナリオ数が **2 → 3 → 0** に減る。
分解値は [`loops/webapi-01/metrics.yaml`](https://github.com/akiramei/BomDD-WebApi-Sample/blob/main/loops/webapi-01/metrics.yaml)、
物語は `report.md` / `report-improvement.md` / `report-improvement-2.md`。

### 深い経路 — 再ビルドして採点し直す

原版とファクトリを別ポートで起動し、オラクルを両方へ投げて突き合わせる(factory-03=収束点の例):

```powershell
# 原版(リポジトリ・ルートの src/)を 5099 で
$orig = Start-Process dotnet -PassThru -ArgumentList `
  'run --project src/BomDD.WebApiSample.Api --urls http://localhost:5099'
# 製造品(収束点 factory-03)を 5098 で
$fac  = Start-Process dotnet -PassThru -ArgumentList `
  'run --project loops/webapi-01/factory-03/src/Api --urls http://localhost:5098'

# /v1/bookings が両ポートで応答するまで待ってから:
pwsh loops/webapi-01/blackbox-oracle.ps1 -BaseUrl http://localhost:5099 |
  Out-File result-original.json
pwsh loops/webapi-01/blackbox-oracle.ps1 -BaseUrl http://localhost:5098 |
  Out-File result-factory03.json

Stop-Process -Id $orig.Id; Stop-Process -Id $fac.Id
# status/code をシナリオ単位で突き合わせ → 期待差分 0
```

`factory-01`(差分2)・`factory-02`(差分3)も同じ手順で `--project loops/webapi-01/factory-0{1,2}/src/Api` に差し替えて確認できる。
各補正は毎回 fresh device で一致を出す=**修正はコーチングでなく BOM に宿る**。

## 4. 主張3の再現 — 多工場 0 / 1 / 3

タグ `webapi-02-input-bom`(締めた BOM)を opus/sonnet/haiku に**完全同一**で供与した再製造が
`loops/webapi-02/{opus,sonnet,haiku}/` にある。**同じ固定オラクル**で採点する。

```powershell
# 例: sonnet を 5098 で起動し、原版 5099 と突き合わせ
Start-Process dotnet -ArgumentList `
  'run --project loops/webapi-02/sonnet/src/Api --urls http://localhost:5098'
pwsh loops/webapi-01/blackbox-oracle.ps1 -BaseUrl http://localhost:5098 |
  Out-File result-sonnet.json
```

| 工場 | 固定オラクル層 差分 | 差分の帰属 |
|---|---|---|
| opus | **0 / 16** | capable factory transfer(締めた BOM が能力ある工場へ転移) |
| sonnet | **1 / 16** | unspecified BOM residue(`not_found` code 名は未規定 → 別ティアが露見) |
| haiku | **3 / 16** | specified contract miss(409→400・`unauthorized` 欠落 = 工場能力) |

コミット済み採点結果は `loops/webapi-02/result-{original,opus,sonnet,haiku}.json`、
分解は [`loops/webapi-02/metrics.yaml`](https://github.com/akiramei/BomDD-WebApi-Sample/blob/main/loops/webapi-02/metrics.yaml)、物語は `report.md`。
**探索プローブ層**([`exploratory-probe.ps1`](https://github.com/akiramei/BomDD-WebApi-Sample/blob/main/loops/webapi-02/exploratory-probe.ps1))は
BOM が値を固定していない次元(ID 形式・一意性・日時表現・応答スキーマ)を**観測のみ**で記録する(合否非混在)。

## 5. 既知の限界(再現で確認できることの境界)

- **被覆固定**: 差分 0 は固定オラクル **16 シナリオ**の被覆での話。被覆を広げれば未観測次元が顔を出しうる(`report.md` 末尾の通り、factory-03 も依然 cheat 申告を残す)。
- **N=2**: 題材は MoviePad と予約 API の2つ。一般法則としては未検証。
- **探索層は合否非混在**: 探索プローブ層のばらつきは「不合格」ではなく「BOM が沈黙する場所の観測値」。締める対象の候補であって失敗ではない。
- **非決定性の扱い**: 製造は LLM ゆえ再製造のたびに同一コードにはならない。本検証が固定するのは**コードでなく BOM/work-order とオラクル**であり、見るのは HTTP 契約の一致であって生成物の同一性ではない。

## 6. 関連

- 本体側まとめ: [FINDINGS.md §6](../FINDINGS.md) / [WHITEPAPER.md §11](../WHITEPAPER.md) / 短い研究ノート: [research-note-v2-webapi.md](research-note-v2-webapi.md)
- 指標分解: [loops/metrics-v2.csv](../loops/metrics-v2.csv)
- 用語(fixed oracle layer / exploratory probe layer / unspecified BOM residue / specified contract miss): [terminology.md](terminology.md)
- 証拠リポジトリ: [akiramei/BomDD-WebApi-Sample](https://github.com/akiramei/BomDD-WebApi-Sample)
</content>
</invoke>
