# 再現ガイド — フォワード・モード検証(forward-01 / rev2 / 01.5)

本書は、BomDD フォワード・モード(原版なしの新規開発)の主張([FINDINGS.md §7](../FINDINGS.md))を
第三者が自分の手で追うための最短手順。検証する主張は3つ。

1. **作れる(forward-01)**: 原版なしでも、能力ある2工場(opus/sonnet)が初回製造で固定オラクル **20/20**・**BOM 未規定残渣 0**(収束ループ 0 回)。
2. **直せる(rev2)**: ユーザー裁定の仕様昇格4点が、コーチングなしで fresh 2工場へ転移(**23/23**)。
3. **保守できる(forward-01.5 = ECO)**: 変更オーダー(会員区分+スキーマ自動移行)が、fresh 2工場で**回帰 23/23・変更 2/2・移行 4/4・不要改変 0**。

> 記述規律: 全通過は「完全鋳造」でなく**「現固定オラクル被覆で未観測差分ゼロ」**。
> haiku の脱落(v1: 6/20 = API 表面の実行時欠陥 / rev2 retry: 19/23 = ローカル TZ 混入)は **BOM 起因でなく工場能力**(FINDINGS §7.1/7.2)。

---

## 0. 前提
- 証拠は別リポジトリ: **[akiramei/BomDD-LibraryLending-Sample](https://github.com/akiramei/BomDD-LibraryLending-Sample)**(公開)。
- 必要: **.NET 10 SDK** / **PowerShell 7+(`pwsh`)**。BOM・治具・全工場成果物・採点/較正結果はすべてコミット済。

```powershell
git clone https://github.com/akiramei/BomDD-LibraryLending-Sample
cd BomDD-LibraryLending-Sample
```

## 1. 固定点(タグ)
| tag | 役割 | commit |
|---|---|---|
| `forward-01-input-bom` | 初回製造の**入力 BOM 固定**(G3 補正後。オラクル S01–S20) | `4973080` |
| `v0.1-forward-01-baseline` | forward-01 **結果固定**(opus/sonnet 20/20・haiku 6/20) | `c368e66` |
| `forward-01-rev2-input-bom` | rev2 入力(裁定4点昇格・オラクル v2 = S01–S23・治具セルフテスト導入) | `410a913` |
| `v0.2-forward-01-rev2` | rev2 **結果固定**(fresh 23/23 ×2) | `4f23d44` |
| `forward-015-input` | ECO-001 凍結(影響なし予測・S24–S25・migration oracle・fixture・**較正**) | `cda7f17` |
| `v0.3-forward-015` | forward-01.5 **結果固定**(回帰 0・移行 4/4・不要改変 0)= main | `deb5433` |

**速い経路**(全主張共通): main のコミット済み採点結果を読む — `loops/forward-01/result-*.json`(v1・rev2・re-validation)・`loops/forward-015/result-eco-*.json`・`loops/forward-015/calibration-*.json`。以下は再実行する深い経路。

## 2. 主張1の再現 — forward-01 初回 20/20(残渣 0)
v1 時点の治具・オラクル(S01–S20)で v1 工場を採点する:
```powershell
git checkout v0.1-forward-01-baseline
pwsh oracle/fixed-oracle.ps1 -FactoryDir loops/forward-01/factory-01-opus   -Port 5211 -ResultFile repro-opus.json
pwsh oracle/fixed-oracle.ps1 -FactoryDir loops/forward-01/factory-02-sonnet -Port 5212 -ResultFile repro-sonnet.json
# 期待: 20/20 / 20/20(haiku は factory-03-haiku で 6/20)
```
> 注: v1 治具には検査器バグ CHEAT-F01-H002(PS 変数名の大小非区別)が潜在していた(rev2 のセルフテスト導入で捕捉)。
> 修正後比較器による v1 成果物の再採点で v1 判定の妥当性を確認済み — `loops/forward-01/result-{opus,sonnet}-revalidation.json`(S01–S20 全 PASS)。

## 3. 主張2の再現 — rev2 仕様昇格の転移(23/23)+ negative control
```powershell
git checkout v0.2-forward-01-rev2
pwsh oracle/fixed-oracle.ps1 -SelfTest    # 治具セルフテスト(rev2 で必須化)
pwsh oracle/fixed-oracle.ps1 -FactoryDir loops/forward-01/factory-04-opus-rev2   -Port 5213 -ResultFile repro-opus-rev2.json
pwsh oracle/fixed-oracle.ps1 -FactoryDir loops/forward-01/factory-05-sonnet-rev2 -Port 5214 -ResultFile repro-sonnet-rev2.json
# 期待: 23/23 / 23/23
pwsh oracle/fixed-oracle.ps1 -FactoryDir loops/forward-01/factory-01-opus -Port 5215 -ResultFile repro-negcontrol.json
# 期待: v1 個体は S23(空文字=400)で FAIL = 昇格行が変更を実際に検出している(較正)
# かつ fresh の rev2 個体は PASS = 修正はコーチングでなく BOM に宿った
```

## 4. 主張3の再現 — ECO: 回帰・変更・移行・不要改変(forward-01.5)
```powershell
git checkout v0.3-forward-015   # = main
# 回帰+変更受入(オラクル v3 = S01–S25)
pwsh oracle/fixed-oracle.ps1 -FactoryDir loops/forward-015/factory-eco-01-opus   -Port 5216 -ResultFile repro-eco-opus.json
pwsh oracle/fixed-oracle.ps1 -FactoryDir loops/forward-015/factory-eco-02-sonnet -Port 5217 -ResultFile repro-eco-sonnet.json
# 期待: 25/25(= 回帰 S01–S23 + 変更 S24–S25)×2
# データ移行(fixture = v0.2 個体の実 DB。一時コピーに対して rev3 ビルドを起動)
pwsh oracle/migration-oracle.ps1 -FactoryDir loops/forward-015/factory-eco-01-opus   -Port 5241 -ResultFile repro-mig-opus.json
pwsh oracle/migration-oracle.ps1 -FactoryDir loops/forward-015/factory-eco-02-sonnet -Port 5242 -ResultFile repro-mig-sonnet.json
# 期待: M01–M04 = 4/4 ×2
```
**較正(negative control)の再現** — 凍結前に検査一式を変更前個体(v0.2)へ当てた記録の追試:
```powershell
pwsh oracle/fixed-oracle.ps1     -FactoryDir loops/forward-01/factory-04-opus-rev2 -Port 5218 -ResultFile repro-calib-fixed.json
# 期待: 23/25 — S01–S23 全 PASS(検査器が偽回帰を作らない)・S24/S25 のみ FAIL(変更行が変更を検出できる)
pwsh oracle/migration-oracle.ps1 -FactoryDir loops/forward-01/factory-04-opus-rev2 -Port 5243 -ResultFile repro-calib-mig.json
# 期待: 4/4(v0.2 は既定 standard=上限3 のため M03 も成立)
```
**不要改変 0 の確認** — diff 基準点(変更前ソースの複製コミット)との突合:
```powershell
git diff db0e20e..deb5433 --stat -- loops/forward-015/factory-eco-01-opus loops/forward-015/factory-eco-02-sonnet
# 期待: 両工場とも、製品側の変更は影響分析(bomdd/60-change-order-eco-001.md §2)記載の
#       4ファイル(Program.cs / Store.cs / LendingDomain.cs / UnitChecks.cs)のみ
#       +ずる報告(cheat-report.md。納品義務の成果物であり製品改変ではない)= 影響分析外への diff 0
```

## 5. 読み合わせ
- ECO 本体(影響なし予測の凍結と的中): [`bomdd/60-change-order-eco-001.md`](https://github.com/akiramei/BomDD-LibraryLending-Sample/blob/main/bomdd/60-change-order-eco-001.md)
- metrics 分解(raw 一致率単独で報告しない規律): [`bomdd/52-metrics.yaml`](https://github.com/akiramei/BomDD-LibraryLending-Sample/blob/main/bomdd/52-metrics.yaml)
- ずる台帳(製造側・検査器側・手法側): [`bomdd/51-cheat-log.md`](https://github.com/akiramei/BomDD-LibraryLending-Sample/blob/main/bomdd/51-cheat-log.md)
- ループ報告: [`loops/forward-01/report.md`](https://github.com/akiramei/BomDD-LibraryLending-Sample/blob/main/loops/forward-01/report.md) / [`loops/forward-015/report.md`](https://github.com/akiramei/BomDD-LibraryLending-Sample/blob/main/loops/forward-015/report.md)
