# Manufacturing Report — WEBAPI-01 / factory-opus5

| 項目 | 値 |
|---|---|
| work order | `bomdd/work-order-webapi-01.md`(WEBAPI-01) |
| routing | `ROUTING-WEBAPI-BOOKING-001` |
| 製造装置(自己申告) | **`claude-opus-5[1m]`** — Claude Opus 5(1M context)。Claude Code / Claude Agent SDK 上の subagent として動作 |
| 製造日 | 2026-08-02 |
| SDK | .NET 10.0.100(`net10.0`) |
| workspace 外アクセス | **なし**(下記「隔離の遵守」参照) |
| `dotnet build` | **成功**(0 エラー / 0 警告) |
| 受入 | **PASS**(43 passed / 0 failed、exit 0) |
| cheat-log 件数 | **16 件**(`CHEAT-OPUS5-001` 〜 `-016`) |

---

## 1. 隔離の遵守(isolation_rule)

`05-routing.yaml` の `isolation_rule.formal_experiment` と、ハーネスからの規律 2/3 に従い、
参照した入力は以下の 6 ファイルのみである。

- `bomdd/01-ebom.yaml` / `02-kbom.yaml` / `03-mbom.yaml` / `04-control-plan.yaml` / `05-routing.yaml`
- `bomdd/work-order-webapi-01.md`

- 原版の `src/` `test/` `openapi/` は見ていない(この workspace には最初から存在しなかった)。
- workspace 外のパス・リポジトリ・Web へのアクセスは行っていない。
  実行したコマンドは workspace 内での `dotnet new sln` / `dotnet sln add` / `dotnet build` / `dotnet run` と、
  受入ハーネスが `http://127.0.0.1:5210`(自プロセス)へ発行した HTTP のみ。
  NuGet からの追加パッケージ取得は発生していない(**外部パッケージ参照ゼロ**、
  `Microsoft.NET.Sdk` / `Microsoft.NET.Sdk.Web` の暗黙参照だけで成立させた)。
- `bomdd/` 配下の入力ファイルは読み取りのみで、一切変更していない。

---

## 2. Routing の実行結果

| order | step | 状態 | 実成果 |
|---|---|---|---|
| 1 | ROUTE-EBOM | 完了 | 7 品目・5 要求を読み、§3 の対応表へ落とした |
| 2 | ROUTE-KBOM | 完了 | status code / auth header / OpenAPI / UTC / 冪等の 5 方針を確定(§4) |
| 3 | ROUTE-MANUFACTURE-CORE | 完了 | `src/BomDD.WebApiSample.Core` |
| 4 | ROUTE-MANUFACTURE-SURFACE | 完了 | `src/BomDD.WebApiSample.Api`、`openapi/openapi.json` |
| 5 | ROUTE-ACCEPTANCE | 完了 | `dotnet build` 成功、受入 43/43 PASS(§6) |
| 6 | ROUTE-ASBUILT | **ファイル未生成**(内容は §7 に記載) | 出力先が `bomdd/06-as-built.yaml` であり、ハーネス規律 4(`bomdd/` を変更しない)・規律 5(成果物の列挙)と衝突するため、**ファイルを作らず本報告書の §7 に as-built を記載**した |
| 7 | ROUTE-SERVICE-BOM | **ファイル未生成**(内容は §8 に記載) | 同上。保守トレースは §8 に記載 |

> order 6/7 を「勝手に判断して省略」したのではなく、**出力先の指定と隔離規律が衝突したので、内容は残し置き場所だけ変えた**。
> 置き場所を戻すべきなら §7/§8 をそのまま `bomdd/06-as-built.yaml` / `07-service-bom.yaml` へ移せる。

---

## 3. E-BOM → 製造単位 → 実装 の対応(トレーサビリティ)

| E-BOM 品目 | 要求 | 製造単位 | 実装位置 | 受入 |
|---|---|---|---|---|
| E-BOOKING-INTERVAL-001 | REQ-001 | M-CORE-BOOKING-SERVICE-001 | `Core/UtcTimestamp.cs`, `Core/BookingRules.cs`, `Core/BookingService.Create` | unit ×5, L3 ×3 |
| E-AVAILABILITY-001 | REQ-001 | M-CORE-BOOKING-SERVICE-001 | `Core/BookingService.Overlaps` / `.Create` | unit ×4, L3 ×1 |
| E-IDEMPOTENCY-001 | REQ-002/003 | M-CORE-BOOKING-SERVICE-001 | `Core/BookingService.CanonicalFingerprint` / `.Create` | unit ×4, L3 ×2 |
| E-CANCELLATION-001 | REQ-004 | M-CORE-BOOKING-SERVICE-001 | `Core/BookingService.Cancel` | unit ×4, L3 ×2 |
| E-HTTP-CONTRACT-001 | REQ-005 | M-API-ENDPOINTS-001 / M-OPENAPI-DOCUMENT-001 | `Api/Program.cs`, `openapi/openapi.json` | L2 ×2, L3 ×4 |
| E-AUTH-APIKEY-001 | REQ-005 | M-API-ENDPOINTS-001 | `Api/Program.cs`(認証ミドルウェア) | L2 ×1, L3 ×2 |
| E-ERROR-SCHEMA-001 | REQ-005 | M-API-ENDPOINTS-001 / M-OPENAPI-DOCUMENT-001 | `Api/Contracts.cs`(`ErrorResponse`), `Api/ApiResults` | L2 ×1, L3(全エラー系) |

E-BOM 不変条件の実装対応(抜粋):

- 半開区間 `[start, end)`・隣接非重複 → `BookingService.Overlaps` は `startA < endB && startB < endA`。
- duration 30 分以上 4 時間以下 → `BookingRules`。境界(ちょうど 30 分 / ちょうど 4 時間)は**受理**side で検査済み。
- literal Z のみ受理 → `UtcTimestamp.TryParse` は末尾 `Z` の序数検査 + `TryParseExact`。`+00:00` と小文字 `z` も拒否(CHEAT-OPUS5-007)。
- roomId は比較前に uppercase → `BookingService.NormalizeRoomId`(保存値も正規化。CHEAT-OPUS5-011)。
- confirmed のみ重複候補 → cancelled は候補から外れ、枠が解放される(unit / L3 両方で検査)。
- fingerprint は roomId, customerId, startUtc, endUtc で idempotencyKey を含まない → `CanonicalFingerprint` は引数に key を取らない(**構造で保証**。検査も存在)。
- `UtcNow <= startUtc - 24h` のみキャンセル可 → 境界ちょうど(= 24h 前)は**許可**side で検査済み。

---

## 4. K-BOM の適用結果(工場が慣習で埋めなかった箇所)

| K-BOM | 適用結果 |
|---|---|
| K-HTTP-REST-001 | 201 create / 400 `invalid_request` / 401 / 404 / 409。**`validation_error` は使用せず**、OpenAPI 文書中にも一度も出現しない(L2 で文字列走査して検査) |
| K-OPENAPI-3-1-001 | `openapi: 3.1.0`、paths / operations / components.schemas / components.securitySchemes を手書きで正本化 |
| K-APIKEY-HEADER-001 | header 名 `X-Api-Key`、失敗時 401 + `ErrorResponse{code: unauthorized}` |
| K-UTC-ISO8601-001 | 入力は literal Z のみ。`format: date-time` では `+09:00` を許すため、契約側に `pattern: ...Z$` を明記(L2 で pattern 末尾を検査) |
| K-IDEMPOTENCY-HTTP-001 | 同一 key + 同一 fingerprint の再送は **201 で元の予約**(204/200 ではない)。同一 key + 異なる payload は **409 `idempotency_conflict`** |

---

## 5. Control Plan の被覆

| 特性 | depth | 状態 | 実 fixture |
|---|---|---|---|
| CP-CORE-OVERLAP-001 | unit | PASS | `UnitChecks` |
| CP-CORE-IDEMPOTENCY-001 | unit | PASS | `UnitChecks` + L3 で再確認 |
| CP-CORE-CANCEL-001 | unit | PASS | `UnitChecks`(固定時計)+ L3(2 時間後開始) |
| CP-OPENAPI-SURFACE-001 | L2 | PASS | `ContractChecks`(System.Text.Json で `openapi/openapi.json` を検査) |
| CP-AUTH-SURFACE-001 | L3 | PASS(**planned を解消**) | `HttpChecks`(実プロセス・port 5210) |
| CP-CONCURRENCY-SURFACE-001 | L3 | PASS(**planned を解消**) | `HttpChecks`(8 並列 POST → 201 が厳密に 1 件) |
| CP-IDEMPOTENCY-FIELDS-001 | L3 | PASS | `HttpChecks` + unit |
| CP-VALIDATION-CODE-001 | L3 | PASS | `HttpChecks`(短/長 duration・欠損・壊れた JSON・逆転範囲) |
| CP-OFFSET-Z-001 | L3 | PASS | `HttpChecks`(`+09:00`)+ unit + L2(契約の pattern) |

- `status: planned` の 2 件(CP-AUTH-SURFACE-001 / CP-CONCURRENCY-SURFACE-001)は、
  fixture が `planned HTTP smoke/concurrency harness` としか書かれておらず、本 workspace に実体が無い。
  **未測定のまま緑にすると fail-open になる**ため、受入ハーネス内に HTTP 経路を作って実測した(CHEAT-OPUS5-016)。
- `CP-IDEMPOTENCY-FIELDS-001` / `CP-VALIDATION-CODE-001` / `CP-OFFSET-Z-001` の fixture 指定
  `loops/webapi-01/blackbox-oracle.ps1` は workspace 外のため参照していない。同じ oracle を受入ハーネス内で実装した。

---

## 6. 受入結果

```
dotnet build
  → ビルドに成功しました。0 個の警告 / 0 エラー

dotnet run --project test/BomDD.WebApiSample.Acceptance
  → acceptance: 43 passed, 0 failed
     ACCEPTANCE: PASS   (exit 0)
```

内訳: unit 21 件 / L2 6 件 / L1 1 件 / L3 15 件 = 43 件。

必須受入(work order §必須受入)の確認:

- [x] `dotnet build` が成功する
- [x] `dotnet run --project test/BomDD.WebApiSample.Acceptance` が成功する(exit 0)
- [x] OpenAPI に `/v1/bookings`、`/v1/bookings/{id}`、`CreateBookingRequest`、`BookingResponse`、`ErrorResponse`、`ApiKeyAuth` がある(L2 で機械検査)

### 受入ハーネス自身の検出力(変異検査 1 件)

「緑」が測定の結果であって既定値でないことを確認するため、製造完了後に変異を 1 件注入した。

- 変異: `UtcTimestamp.TryParse` から literal Z の要件を外し、一般の `DateTimeOffset.TryParse` に置換
  (= K-UTC-ISO8601-001 が警告する「`format: date-time` だけの実装」に相当する典型的なずる)
- 結果: **2 件が FAIL、exit 1**(`CP-OFFSET-Z-001` の unit 検査と L3 検査の両方が検出)
- 変異は撤回済み。最終状態は上記のとおり 43/43 PASS。

---

## 7. As-Built(ROUTE-ASBUILT の内容)

| 製造単位 | artifact | 実体 | 状態 |
|---|---|---|---|
| M-CORE-BOOKING-SERVICE-001 | `src/BomDD.WebApiSample.Core` (dotnet-classlib) | `net10.0` classlib、外部パッケージ 0 | as-built |
| M-API-ENDPOINTS-001 | `src/BomDD.WebApiSample.Api` (aspnetcore-minimal-api) | `net10.0` Web SDK、minimal API、外部パッケージ 0 | as-built |
| M-OPENAPI-DOCUMENT-001 | `openapi/openapi.json` (openapi-3.1-json) | 手書きの正本(実装からの生成物ではない) | as-built |
| M-ACCEPTANCE-HARNESS-001 | `test/BomDD.WebApiSample.Acceptance` (dotnet-console-acceptance) | console、Core を参照、Api は build-order 依存のみ | as-built。**verifies を 3 単位へ拡張**(M-API-ENDPOINTS-001 を追加、CHEAT-OPUS5-016) |

as-built で確定した実装事実(BOM に無いか、BOM より具体的なもの):

- 予約 ID: `bk_` + SHA-256(`fingerprint|idempotencyKey`) の先頭 24 桁小文字 hex、衝突時は seed に連番を付与。
- fingerprint: `UPPER(roomId) | customerId | start(7桁Z) | end(7桁Z)`。
- 保存: プロセス内メモリ、単一 `lock` で直列化。**永続化なし・単一プロセス前提**。
- 認証: 単一キー(`Api:Key`、既定 `demo-key`)、序数比較。
- 追加表面: `GET /health`(認証不要)。
- 既定ポート: 環境変数 `ASPNETCORE_URLS` 未設定時は `http://127.0.0.1:5210`。

---

## 8. Service BOM 相当の保守トレース(ROUTE-SERVICE-BOM の内容)

K-BOM 依存(版が動いたら再検証が要る箇所):

| K-BOM | 版 | 影響を受ける実装 | 破れたときの症状 |
|---|---|---|---|
| K-HTTP-REST-001 | v1 | `ApiResults.StatusFor` | status ↔ code の対応が客先期待とずれる |
| K-OPENAPI-3-1-001 | 3.1.0 | `openapi/openapi.json` | 3.0 系ツールは `type: ["string","null"]` と `examples` 配列を解釈できない |
| K-APIKEY-HEADER-001 | v1 | 認証ミドルウェア、契約の `ApiKeyAuth` | header 名変更は全クライアント破壊 |
| K-UTC-ISO8601-001 | v1 | `UtcTimestamp` | 受理範囲(`+00:00`・小文字 z)の解釈が動く |
| K-IDEMPOTENCY-HTTP-001 | v1 | `BookingService.Create` の検査順序 | 再送が 200/409 に化ける |

深さ別の再検証コスト(Control Plan depth_ladder に対応):

- `unit` — プロセス不要。核の変更時は常に走る。
- `L2` — `openapi/openapi.json` の編集時に必ず走る。実装からの生成物ではないので、**実装と契約は自動では同期しない**(手で合わせる責任が残る)。
- `L1`/`L3` — API プロセスを port 5210 で起動する。ポート衝突時は失敗する(環境依存)。
- `G` — 未実施(human review)。API の使いやすさ・文書の明快さは自動受入の範囲外。

既知の制約(次の版で先に壊れる場所):

1. **in-memory 単一プロセス** — 多重化すると `CP-CONCURRENCY-SURFACE-001` の保証(単一 `lock`)が消える。
2. **契約と実装の二重管理** — `openapi/openapi.json` は手書き正本。実装だけ変えても L2 は緑のまま通る
   (逆に契約だけ変えれば L3 が落ちる)。契約→実装方向の乖離を捕まえる検査は無い。
3. **`status: planned` を実測へ昇格させた分**は、Control Plan 側の記述(fixture が workspace 外を指す)と
   実装(ハーネス内蔵)が一致していない。次版で Control Plan の fixture 欄を実体へ更新するのが筋。

---

## 9. ずる(cheat-log)の要約

全 16 件。詳細と各件の「入力のどこが空白か / 何を補ったか / 分岐リスク / BOM への提案」は `cheat-log.md` を参照。

| 分類(work order の報告対象) | 件数 | 該当 |
|---|---|---|
| HTTP status code の選択 | 3 | 002(DELETE 成功形)、009(検査の優先順位)、010(壊れた JSON / Content-Type) |
| エラーコード名の選択 | 1 | 001(`not_found`) |
| API key header 名 | 0 | **導出済み**(K-APIKEY-HEADER-001 に明記)。関連する空白は 015(鍵の本数・供給元・比較方法) |
| 日時の UTC/offset 扱い | 2 | 006(応答の描画精度)、007(`+00:00` と小文字 z の拒否) |
| 冪等性 fingerprint の正規化方式 | 2 | 005(区切り・大小・時刻精度)、008(key が任意) |
| 予約 ID 生成方式 | 1 | 004(ハッシュ入力・長さ・衝突時) |
| 上記以外(表面・製造方式・受入構成) | 7 | 003(一覧の形)、011(roomId のエコー)、012(in-memory と並列制御)、013(`/health`)、014(過去開始を受理=**足さなかった判断**)、015(鍵の扱い)、016(受入が API を起動) |

工場間で最も分岐しやすいと見ているのは以下:

1. **009(c)** 期限切れ予約の再キャンセル — 200(同じ結果)か 409 か。同じ DELETE の 2 回目で結果が変わるかどうかが割れる。
2. **004** 予約 ID — 外部識別子なので、GUID を選ぶ工場とは互換性が無い。
3. **003** 一覧の包み — 裸配列か `{items:[...]}` か。
4. **002** DELETE の成功形 — 200+本文 か 204。
5. **016** L3 を測るか否か — 測らない工場は `planned` 2 件を未測定のまま緑にできる(**受入の緑の意味が工場ごとに違う**)。

---

## 10. 成果物一覧(workspace 相対)

```
BomDD.WebApiSample.sln
manufacturing-report.md
cheat-log.md
openapi/openapi.json
src/BomDD.WebApiSample.Core/BomDD.WebApiSample.Core.csproj
src/BomDD.WebApiSample.Core/Booking.cs
src/BomDD.WebApiSample.Core/BookingRules.cs
src/BomDD.WebApiSample.Core/BookingService.cs
src/BomDD.WebApiSample.Core/ErrorCodes.cs
src/BomDD.WebApiSample.Core/UtcTimestamp.cs
src/BomDD.WebApiSample.Api/BomDD.WebApiSample.Api.csproj
src/BomDD.WebApiSample.Api/Contracts.cs
src/BomDD.WebApiSample.Api/Program.cs
test/BomDD.WebApiSample.Acceptance/BomDD.WebApiSample.Acceptance.csproj
test/BomDD.WebApiSample.Acceptance/ApiProcess.cs
test/BomDD.WebApiSample.Acceptance/ContractChecks.cs
test/BomDD.WebApiSample.Acceptance/HttpChecks.cs
test/BomDD.WebApiSample.Acceptance/HttpProbe.cs
test/BomDD.WebApiSample.Acceptance/Program.cs
test/BomDD.WebApiSample.Acceptance/Runner.cs
test/BomDD.WebApiSample.Acceptance/UnitChecks.cs
```

`bomdd/` 配下は入力のみで、追加・変更していない。
`bin/` `obj/` はビルド生成物。
