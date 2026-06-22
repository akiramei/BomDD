# BOM 粒度ガイド

このガイドは、BOM-DD PLM が「粗すぎる」「細かすぎる」「層がずれている」と判定する基準を、人間と AI が先に理解するためのもの。

## 1. 基本原則

BOM item は、検索、分類、トレース、製造、検査、保守のいずれかで意味を持つ単位にする。単なるファイル一覧、DOM タグ一覧、クラス一覧ではない。

判定質問:

1. その item は何のために存在するか。
2. どの REQ、表示契約、外部知識、制約に接続するか。
3. どの Control Plan で検査するか。
4. 変更時に影響分析の単位になるか。
5. 製造または保守で独立に扱えるか。

## 2. E-BOM 粒度

E-BOM は、仕様担当が理解できる設計部品表である。

### よい粒度

```yaml
id: E-BOOKING-RULES-001
purpose: Prevent overlapping bookings and enforce room capacity.
requirement_refs: [REQ-003, REQ-004]
acceptance_refs: [CP-BOOKING-RULES-001]
```

この粒度は、存在理由、要求、検査が閉じている。

### 粗すぎる例

```yaml
id: E-APP-001
purpose: Whole application
requirement_refs: [REQ-001, REQ-002, REQ-003, REQ-004, REQ-005]
```

問題:

- 変更時にどこを直すか分からない。
- 検査 depth が混在する。
- 仕様担当が部品の存在理由を判断できない。

### 細かすぎる例

```yaml
id: E-BUTTON-BORDER-001
purpose: Border around the save button
```

問題:

- 要求、検査、保守の単位ではない。
- UI-BOM の nonBom または Design System token に留めるべき。

## 3. K-BOM 粒度

K-BOM は、外部知識、設計根拠、依存バージョン、制約を追跡する。

### よい粒度

```yaml
id: K-REST-ERRORS-001
knowledge_kind: domain-convention
version: v1
managed_knowledge:
  - Validation errors return HTTP 400 with code invalid_request.
  - Missing resources return HTTP 404 with code not_found.
consumers: [E-BOOKING-API-001]
```

### 粗すぎる例

`K-WEB-001` に REST、SQLite、React、CSS、認証、ログを全部入れる。

### 細かすぎる例

HTTP status code 400 と 404 を別 item にする。ただし別々に版更新、保守逆引き、責務分離が必要なら分割してよい。

## 4. M-BOM 粒度

M-BOM は、製造工程管理者が現在何が起きているか把握できる単位にする。

### よい粒度

```yaml
id: M-BOOKING-API-001
ebom_refs: [E-BOOKING-API-001, E-BOOKING-RULES-001]
output_artifact_ref: src/Booking.Api
acceptance_refs: [CP-BOOKING-API-001]
```

この単位は、製造対象、出力、検査が明確である。

### 粗すぎる例

`M-BUILD-ALL-001` が API、DB、UI、受入ハーネスを全部作る。

### 細かすぎる例

1 メソッド、1 CSS class、1 SQL column を独立 M-BOM unit にする。単独で製造、受入、保守しないなら細かすぎる。

## 5. Service BOM 粒度

Service BOM は、保守・サポート担当者が障害時に逆引きできる粒度にする。

### よい粒度

```yaml
id: SB-BOOKING-DATETIME-001
part_ref: E-BOOKING-RULES-001
external_deps:
  - kbom_ref: K-DATETIME-UTC-001
reinspect_on_change:
  - cp_ref: CP-DATETIME-001
```

### 粗すぎる例

`SB-APP-001` が全ライブラリ、全 UI、全 DB を持つ。どの変更でどこを再検査するか分からない。

## 6. UI の粒度

UI では、HTML タグではなく、画面、領域、業務操作、入力、状態、表示契約、デザインシステム部品を扱う。

E-BOM へ昇格する候補:

- 画面または主要領域が要求や表示契約を持つ。
- 操作が業務意味を持つ。
- 入力が validation、DB、API に接続する。
- 状態表示が受入対象になる。
- Card / CTA / Chip / Badge / IconButton などが UI-CAD の design language として必要。

E-BOM にしない候補:

- 意味のない wrapper。
- 余白調整だけの `div`。
- shadow、border、radius の単発装飾。ただし design token として K-BOM または Design System BOM で管理する場合は別。

## 7. DB の粒度

DB は、DDL の物理構造だけでなく、永続化意図を扱う。

E-BOM にする候補:

- 業務 entity。
- lifecycle を持つ aggregate。
- 仕様上の制約、一意性、保持期間、監査要件。

M-BOM にする候補:

- migration unit。
- repository/persistence adapter。
- schema validation / seed / fixture generation。

K-BOM にする候補:

- DB エンジンの型、日時、transaction、locking、migration convention。

## 8. 分割の合図

次の兆候があれば分割する。

- `purpose` に `and` が 2 回以上出る。
- `requirement_refs` が unrelated な要求を多く含む。
- `acceptance_refs` の depth が unit と G など大きく離れる。
- `depends_on` が大量で理由を説明できない。
- 変更時に「この一部だけ直したい」となる。

## 9. 結合の合図

次の兆候があれば細かすぎるので結合する。

- 単独で検査できない。
- 変更時に常に同じ親と同時に変わる。
- 人間の読み手が存在理由を説明できない。
- PLM item だが TraceLink が requirement、knowledge、acceptance のどこにも繋がらない。
