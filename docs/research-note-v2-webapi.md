# 研究ノート v2 — Web/API での外部妥当性検証(予約 API)

> 単体で引用できる短い要旨。詳細な章は [FINDINGS.md §6](../FINDINGS.md) と [WHITEPAPER.md §11](../WHITEPAPER.md)、
> 手で追う手順は [reproduce-webapi-v2.md](reproduce-webapi-v2.md)。

## 要旨

MoviePad(デスクトップ動画編集)で観測した **核/表面の法則**が単一題材固有でないかを確かめるため、
別ドメイン **会議室予約 API**(.NET 10 minimal API)で BomDD を一巡させた。
機械可読 BOM(E/K/M-BOM・Control Plan・Routing・As-Built・Service BOM の YAML)から、
**原版非開示のクリーンな製造装置**が再製造し、**設計者側の固定ブラックボックス HTTP オラクル**
(原版と製造品への 2-way diff、HTTP 契約で採点・内部名に結合しない)で評価した。
証拠は公開リポ [akiramei/BomDD-WebApi-Sample](https://github.com/akiramei/BomDD-WebApi-Sample)。

- **核**: 予約可否 / 重複防止 / 冪等性 / キャンセル期限。
- **表面**: HTTP status code / OpenAPI 契約 / API key 認証 / UTC 日時表現 / JSON error schema。

## 主張(N=2 — いずれも「観測した範囲」)

### 1. 核/表面の法則は Web/API でも再現した

BOM・K-BOM・Control Plan が固定した契約(status / error code / overlap / cancel / auth / validation)は
能力ある工場で完全一致した=**鋳造**。分岐は常に **BOM が未規定の残渣**に現れ、核には現れなかった。
MoviePad で「ずる」が常に表面に出たのと同型。

### 2. BOM 補正で鋳造性は漸近的に上がる(2 → 3 → 0)

同一題材で「差分観測→BOM 補正→クリーンな別装置で再製造」を3回。原版との差分は **2 → 3 → 0**。

| ループ | BOM | 差分 | 出来事 |
|---|---|---|---|
| webapi-01 | seed | 2/16 | 冪等 fingerprint 構成未列挙 → customerId 次元の機能差(blocker) |
| webapi-01.5 | 第1次補正 | 3/16 | 上記消失。別の未規定次元(エラーコード名・非Zオフセット)が露出 |
| webapi-01.6 | 第2次補正 | 0/16 | 明記で解消(現固定オラクル被覆で未観測差分ゼロ) |

各補正は毎回 baseline も前ファクトリも知らない fresh device で一致した=**修正はコーチングでなく BOM に宿る**。
ただし**完全性は漸近**で、締めるたびに別の未規定次元が顔を出す。

### 3. 多工場で仕様面は転移し、未規定面は分散する

締めた BOM をタグ固定(`webapi-02-input-bom`)し opus/sonnet/haiku に同一供与。固定オラクル層:
**opus 0 / sonnet 1 / haiku 3**。差分は3分類に割れる:

- **capable factory transfer**: opus 0(締めた契約は能力ある工場へ完全転移)。
- **unspecified BOM residue**: sonnet 1(`not_found` code 名が未規定。単一ティアでは慣習で隠れ、別ティアが露見=共有暗黙知 C2)。
- **specified contract miss**: haiku 3(明記済み契約の取りこぼし=工場能力)。

探索プローブ層では未規定次元(ID 形式・一意性・日時表現・応答スキーマ)が全工場で分散=
**ばらつきは BOM が沈黙する場所に集中**。MoviePad Loop4(K-BOM で工場間ばらつきが消える)の Web 多工場版。

## 含意

決定性軸は **(a) 工場能力** と **(b) BOM 未規定** に分離して読むべき、というのが v2 の測定上の精緻化。
「工場間一致」は正しさを保証しない(揃って間違う「共有暗黙知の罠」)ので、決定性軸と正しさ軸は独立に検査する。

## 記述規律と限界

- 差分 0 は「完全鋳造」ではなく **「現固定オラクル(16シナリオ)被覆で未観測差分ゼロ」**。
- 指標は raw 一致率だけでなく **targeted_fix / blocker / new_unspecified / specified_contract_miss / exploratory** に分解して記録([loops/metrics-v2.csv](../loops/metrics-v2.csv))。
- **N=2**。一般法則としては未検証。次は題材 N の拡大(分散 / 組込・リアルタイム)。
- 当面の Future Work: 応答スキーマ・日時形式・ID アルゴリズム/一意性・`not_found` を締めて探索層の分散が消えるか(webapi-02.5)。
</content>
