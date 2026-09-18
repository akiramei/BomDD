records=150 answered=150 errors=0 models=['jev-1.13.0']
tokens in=165221 out=7764

## 混同行列(行= ラベル・列= Jev の choice)

| ラベル \ choice | performed | planned | template | omitted | N | 正答率 |
|---|---|---|---|---|---|---|
| performed | 78 | 0 | 0 | 0 | 78 | 1.00 |
| planned | 9 | 25 | 0 | 0 | 34 | 0.74 |
| template | 3 | 13 | 16 | 0 | 32 | 0.50 |
| omitted | 2 | 0 | 0 | 4 | 6 | 0.67 |

## sub 別(ラベル内の内訳)

| ラベル/sub | N | 正答 | 誤分類先 | 拮抗(conf<0.5) |
|---|---|---|---|---|
| omitted/exemption | 1 | 0 | {'performed': 1} | 0 |
| omitted/fixture | 4 | 3 | {'performed': 1} | 0 |
| omitted/placeholder | 1 | 1 | — | 0 |
| performed/close/measure | 29 | 29 | — | 0 |
| performed/receipt | 17 | 17 | — | 0 |
| performed/round | 21 | 21 | — | 0 |
| performed/s0 | 11 | 11 | — | 0 |
| planned/acceptance | 14 | 5 | {'performed': 9} | 0 |
| planned/candidates | 3 | 3 | — | 0 |
| planned/prediction | 17 | 17 | — | 1 |
| template/template | 32 | 16 | {'planned': 13, 'performed': 3} | 7 |

## 認定条件(事前宣言)

- ① planned → performed の誤分類: 9/34 = 26.47%(条件 ≤ 10%)→ 未達
- ② performed の再現率: 78/78 = 100.00%(条件 ≥ 85%)→ 達成
- ③ planned+performed の正答率: 103/112 = 91.96%(条件 ≥ 85%)→ 達成
- 拮抗(confidence < 0.5): 8/150

## 誤分類の検体(全件)

| id | ラベル/sub | choice | conf | p(performed) | p(planned) |
|---|---|---|---|---|---|
| ECO-063:## 3. 受入 | planned/acceptance | performed | 0.98 | 0.99 | 0.01 |
| ECO-068:## 3. 受入(製造時の候補) | planned/acceptance | performed | 0.66 | 0.75 | 0.25 |
| ECO-069:## 3. 受入 | planned/acceptance | performed | 0.97 | 0.98 | 0.01 |
| ECO-070:## 3. 受入 | planned/acceptance | performed | 0.88 | 0.91 | 0.09 |
| ECO-071:## 3. 受入 | planned/acceptance | performed | 0.90 | 0.93 | 0.07 |
| ECO-075:## 3. 受入(候補) | planned/acceptance | performed | 0.72 | 0.79 | 0.21 |
| ECO-076:## 3. 受入 | planned/acceptance | performed | 0.97 | 0.98 | 0.02 |
| ECO-077:## 3. 受入 | planned/acceptance | performed | 1.00 | 1.00 | 0.00 |
| ECO-078:## 3. 受入 | planned/acceptance | performed | 0.84 | 0.88 | 0.11 |
| TPL:60-change-order.md:## 2. 影響分析(トレース逆引き+影響なし予測) | template/template | planned | 0.92 | 0.01 | 0.93 |
| TPL:60-change-order.md:## 6. 記録 | template/template | performed | 0.85 | 0.89 | 0.00 |
| TPL:61-impact-analysis.md:### 1.1 閉集合宣言の掃討(plm ECO-002 の | template/template | planned | 0.97 | 0.00 | 0.99 |
| TPL:61-impact-analysis.md:### 1.2 As-Maintained 実物の呼び出しサ | template/template | planned | 0.64 | 0.22 | 0.73 |
| TPL:61-impact-analysis.md:### 1.3 ビルド派生物の波及先(plm ECO-004 | template/template | performed | 0.47 | 0.61 | 0.39 |
| TPL:61-impact-analysis.md:### 1.4 ハブ台帳 — under 実績 unit の | template/template | planned | 0.51 | 0.23 | 0.63 |
| TPL:61-impact-analysis.md:### 1.5 暗黙入力(共有定数・既定値)の分岐洗い出し( | template/template | performed | 0.51 | 0.64 | 0.28 |
| TPL:61-impact-analysis.md:## 2. 影響なし予測(反証可能 — 製造前に凍結) | template/template | planned | 0.75 | 0.00 | 0.81 |
| TPL:62-migration-oracle.md:## 2. 検査行(M 行)と失敗分類 | template/template | planned | 0.89 | 0.07 | 0.92 |
| TPL:62-migration-oracle.md:## 3. 較正(negative control — 凍結 | template/template | planned | 0.87 | 0.09 | 0.90 |
| TPL:62-migration-oracle.md:## 5. 効力(effectivity)オラクル — 本テ | template/template | planned | 0.67 | 0.12 | 0.75 |
| TPL:63-diff-audit.md:## 1. diff 基準点 | template/template | planned | 0.62 | 0.02 | 0.71 |
| TPL:64-part-lineage-reattribution.md:## 2. Lineage update | template/template | planned | 0.44 | 0.08 | 0.58 |
| TPL:64-part-lineage-reattribution.md:## 6. Active Graph Inte | template/template | planned | 0.68 | 0.05 | 0.76 |
| TPL:64-part-lineage-reattribution.md:## 7. Deferred content  | template/template | planned | 0.39 | 0.00 | 0.55 |
| TPL:64-part-lineage-reattribution.md:## 8. Completion checkl | template/template | planned | 0.60 | 0.23 | 0.70 |
| OM:eco-034:exemption | omitted/exemption | performed | 0.94 | 0.96 | 0.00 |
| OM:C17-F8 | omitted/fixture | performed | 0.69 | 0.77 | 0.00 |
