# 仕様書 — <プロジェクト名>

> 製造パッケージに含まれる(製造装置が読む)。REQ への双方向トレースを保つ。

## 1. 概要と用語

## 2. 機能仕様
<!-- 各節に実現する REQ を明記: (REQ-001, REQ-003) -->

### 2.x <機能名> (REQ-xxx)
- 振る舞い:
- 核/表面: core | surface(出所: )
- 受入観点(深さ・許容差の根拠):

## 3. 不変条件(M-BOM へ前倒し)
<!-- 識別子採番・座標系/基準系・冪等性・順序。CHEAT-008 対策 -->
| ID | 不変条件 | 関係する REQ |
|---|---|---|
| INV-001 | | |

## 4. 沈黙次元の第1回掃討(silence-checklist)
<!-- 全行を宣言する。語彙: specified / exploratory / out-of-scope / deferred-to-phase3
     deferred-to-phase3 は第1回掃討のみ有効な「明示的延期」。第2回(32-mbom.yaml)で必ず3択に解消する -->
| 次元 | 宣言 | 内容/参照 |
|---|---|---|
| 日時表現 | specified | literal-Z UTC のみ。非Zは invalid_request |
| エラー語彙 | deferred-to-phase3 | M-BOM で全列挙 |

## 5. トレース表
| REQ | 実現節 | 受入観点 |
|---|---|---|
| REQ-001 | §2.1 | |

---
## ゲート記録(G2/G2')
- マルチリーダー監査: リーダー数 N= / 差分箇所= / 補正後再監査=
- MeasurementCapability: 全 REQ が adequate へ到達可能(unmeasurable ゼロ)= yes/no
  - human-approval-required の REQ と承認者:
  - 観測契約が必要な REQ(in-process):
