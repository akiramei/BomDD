# Design Intent — <UI-CAD 名>

> UI-CAD の冒頭・注記・DESIGN DIRECTION・原則カード・トークンデモから抽出した設計意図。  
> これはプレゼン用マーケ素材ではなく、E-DESIGN / K-DESIGN / Control Plan へ接続する設計制約である。

## 1. source refs

| source | selector / area | 内容 |
|---|---|---|
| M1 | DESIGN DIRECTION 01 |  |
| M2 | DESIGN DIRECTION 02 |  |
| M3 | DESIGN DIRECTION 03 |  |

## 2. design thesis

- 一文要約:
- 例: ひとつの思想で束ねる / 階層が主役 / ひとつの部品言語 / 触れる余白

## 3. principles

| ID | 原則 | 設計要求としての意味 | E/K-DESIGN 反映 |
|---|---|---|---|
| DI-P01 |  |  |  |
| DI-P02 |  |  |  |
| DI-P03 |  |  |  |
| DI-P04 |  |  |  |

## 4. tokens

| token kind | 値 / ルール | K-DESIGN 反映 | Control Plan |
|---|---|---|---|
| COLOR |  | K-DESIGN-TOKENS-001 |  |
| TYPE |  | K-DESIGN-TOKENS-001 |  |
| ROW |  | K-DESIGN-TOKENS-001 |  |
| STATE |  | K-DESIGN-STATE-001 |  |

## 5. component language

| 部品言語 | 期待 | E-DESIGN 反映 |
|---|---|---|
| Row |  |  |
| Card |  |  |
| Chip |  |  |
| CTA |  |  |
| IconButton |  |  |

## 6. layout invariants（データ分散に対する安定レイアウト契約）

> モック / golden は単一データ1枚しか描かない。データが変わっても保たれるべきレイアウト契約を不変条件として明示する（失敗型 S3 の予防）。K-DESIGN / K-AVALONIA 規律へ昇格する。

| ID | 領域 | 不変条件 | antiPattern（違反例） | 境界状態 / 検証 | K-BOM 反映 |
|---|---|---|---|---|---|
| DI-L01 | <region> | <例: 中央クラスタは領域全幅基準で中央・兄弟幅に不変> | <例: DockPanel 残余空間中央 / 可変幅 sibling と中央 sibling の同列混在> | <最大幅（N/N）・空> | K-AVALONIA-LAYOUT-001 |

## 7. extraction decisions

| selector / area | 初期分類 | 訂正分類 | 理由 |
|---|---|---|---|
|  | nonBom | designIntent |  |

## 8. open questions

1. <フォント指定は製品全体で固定するか。>
2. <既存テーマと CAD トークンが衝突する場合、どちらを優先するか。>
3. <状態色や警告色をどの範囲まで E-DESIGN/K-DESIGN 化するか。>
