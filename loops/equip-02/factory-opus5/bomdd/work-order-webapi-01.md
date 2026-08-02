# Work Order — WEBAPI-01

## 目的

BomDD の Web/API 題材として、会議室予約 API を製造する。

製造装置は、`bomdd/01-ebom.yaml`、`bomdd/02-kbom.yaml`、`bomdd/03-mbom.yaml`、`bomdd/04-control-plan.yaml`、`bomdd/05-routing.yaml` のみを入力とする。原版の `src/`、`test/`、`openapi/` は見ない。

## 製造対象

- .NET 10 の minimal API
- 予約ルールを持つ Core class library
- API 表面を持つ ASP.NET Core project
- OpenAPI 3.1 JSON document
- 受入ハーネス

## 必須受入

- `dotnet build` が成功する。
- `dotnet run --project test/BomDD.WebApiSample.Acceptance` が成功する。
- OpenAPIに `/v1/bookings`、`/v1/bookings/{id}`、`CreateBookingRequest`、`BookingResponse`、`ErrorResponse`、`ApiKeyAuth` がある。

## ずる報告

製造中に BOM/K-BOM/Control Plan から導けなかった判断は、実装を止めずに `cheat-log.md` 形式で報告する。

特に以下は報告対象とする。

- HTTP status code の選択
- エラーコード名の選択
- API key header 名
- 日時のUTC/offset扱い
- 冪等性fingerprintの正規化方式
- 予約ID生成方式
