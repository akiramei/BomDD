# 仕様書 — <プロジェクト名>

> 製造パッケージに含まれる(製造装置が読む)。REQ への双方向トレースを保つ。

## 1. 概要と用語

## 2. 機能仕様
<!-- 各節に実現する REQ を明記: (REQ-001, REQ-003) -->

### 2.x <機能名> (REQ-xxx)
- 仕様節ID: SPEC-<NAME>-001
- 振る舞い:
- 核/表面: core | surface(出所: )
- 受入観点(深さ・許容差の根拠):
- E-BOM 候補: E-<NAME>-001
- M-BOM 候補: M-<NAME>-001
- Control Plan 候補: CP-<NAME>-001
- UI-IR / UI-BOM 参照(HTMLモックから抽出した場合):
  - UI-IR:
  - UI-BOM:
  - trace map:
- 表示契約(原典あり/UI surface の場合):
  - 原典参照: <画面名/スクリーンショット/旧版 build/tag>
  - 提示要素: <フィールド・ラベル・サムネイル・ファイル名・状態表示・空/エラー表示を全列挙>
  - 対象外要素: <移植しない要素と理由>

## 3. 不変条件(M-BOM へ前倒し)
<!-- 識別子採番・座標系/基準系・冪等性・順序。CHEAT-008 対策 -->
| ID | 不変条件 | 関係する REQ |
|---|---|---|
| INV-001 | | |

## 3.5 DB / 永続化意図(DB がある場合)
<!-- DDL だけでなく、業務 entity、field、制約、保持期間、移行方針を書く。
     詳細テンプレートは bomdd/db/schema-intent.md。 -->
| Entity/Field | 意図 | REQ | E-BOM候補 | M-BOM候補 | Control Plan候補 |
|---|---|---|---|---|---|
| DB-ENT-001 | <例 Booking の永続化> | REQ-xxx | E-PERSISTENCE-001 | M-PERSISTENCE-001 | CP-PERSISTENCE-001 |

## 4. 沈黙次元の第1回掃討(silence-checklist)
<!-- 全行を宣言する。語彙: specified / exploratory / out-of-scope / deferred-to-phase3
     deferred-to-phase3 は第1回掃討のみ有効な「明示的延期」。第2回(32-mbom.yaml)で必ず3択に解消する -->
| 次元 | 宣言 | 内容/参照 |
|---|---|---|
| 表示要素集合・原典表示パリティ | specified | §2.x 表示契約。全提示要素を E-BOM/Control Plan へトレース |
| 日時表現 | specified | literal-Z UTC のみ。非Zは invalid_request |
| エラー語彙 | deferred-to-phase3 | M-BOM で全列挙 |

## 5. トレース表
| TraceLink | REQ | 実現節 | E-BOM | M-BOM | Control Plan | 受入観点 |
|---|---|---|---|---|---|---|
| TL-REQ-SPEC-001 | REQ-001 | SPEC-<NAME>-001 | E-<NAME>-001 | M-<NAME>-001 | CP-<NAME>-001 | unit / L1 / L2 / L3 / G |

## 6. PLM-ready 契約
- 仕様節は `SPEC-*` または見出し anchor で参照できる。
- 全 REQ が少なくとも 1 つの仕様節へ到達する。
- UI 表示要素は `DC-*` / `DE-*` として E-BOM / Control Plan へ接続する。
- DB entity/field は `DB-ENT-*` / `DB-FLD-*` として schema intent へ接続する。
- 未解決事項は下表に残し、blocker は manufacturing-ready を止める。

## 7. Unresolved Questions
| ID | Question | Severity | Owner | Affected refs | Status |
|---|---|---|---|---|---|
| UQ-SPEC-001 | <仕様として確定できない点> | blocker / non-blocker | human / AI | REQ-xxx / E-xxx / CP-xxx | open |

---
## ゲート記録(G2/G2')
- マルチリーダー監査: リーダー数 N= / 差分箇所= / 補正後再監査=
- MeasurementCapability: 全 REQ が adequate へ到達可能(unmeasurable ゼロ)= yes/no
  - human-approval-required の REQ と承認者:
  - 観測契約が必要な REQ(in-process):
- 原典パリティサインオフ(原典ありの移植・再現案件):
  - 原典表示要素の全数照合: done/not-needed
  - 未トレース表示要素: 0 件 / <件数と差し戻し先>
  - 承認者:
