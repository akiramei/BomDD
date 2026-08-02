# cheat-log — WEBAPI-01 / factory-opus5

製造装置: `claude-opus-5[1m]`(Claude Opus 5, 1M context / Claude Code — Claude Agent SDK 上)
入力: `bomdd/01-ebom.yaml`, `02-kbom.yaml`, `03-mbom.yaml`, `04-control-plan.yaml`, `05-routing.yaml`, `bomdd/work-order-webapi-01.md` のみ
記録対象: **BOM / K-BOM / Control Plan / work order から導けなかった判断**(導けたものは記録しない)

判定の凡例:

- **導出済み(記録しない)** — 入力に明記があり、装置は選んでいない。
- **CHEAT** — 入力に根拠がなく、装置が慣習・設計判断で補った。

---

## 0. 先に「導出済み」を明示する(ずるではないもの)

work order の「ずる報告」対象6項目のうち、以下は**入力から導出できた**ため CHEAT ではない。
装置が何を選び、何を選ばなかったかを分離するために明示する。

| work order の項目 | 導出元 | 導出結果 |
|---|---|---|
| HTTP status code(主要分) | K-HTTP-REST-001 / K-IDEMPOTENCY-HTTP-001 | 201 create・400 validation・401 auth・404 missing・409 conflict、冪等再送は **201**(明記あり) |
| エラーコード名(主要分) | K-HTTP-REST-001 / CP-* の oracle | `invalid_request`(`validation_error` 禁止も明記)・`slot_unavailable`・`idempotency_conflict`・`cancellation_window_closed`・`unauthorized` |
| API key header 名 | K-APIKEY-HEADER-001 / M-API-ENDPOINTS-001 | `X-Api-Key`、既定キー `demo-key` |
| 日時の UTC/offset 扱い | K-UTC-ISO8601-001 / E-BOOKING-INTERVAL-001 / CP-OFFSET-Z-001 | literal Z のみ受理、非Zは 400 `invalid_request` |
| 冪等性 fingerprint の対象項目 | E-IDEMPOTENCY-001 / K-IDEMPOTENCY-HTTP-001 | roomId, customerId, startUtc, endUtc(idempotencyKey は除外) |
| 予約 ID の生成方式(方針) | M-CORE-BOOKING-SERVICE-001 | 決定的ハッシュ・接頭辞 `bk_` |

以下が、**残った空白を装置が埋めた分**である。

---

## CHEAT-OPUS5-001 — エラーコード `not_found` の名称

- 区分: エラーコード名の選択
- 空白: K-HTTP-REST-001 は「404 represents missing resources」とだけ述べ、**その 404 に載せる `code` の文字列**を与えていない。E-ERROR-SCHEMA-001 も `code`/`message` を持つとしか言わない。他の4コード(`invalid_request` / `slot_unavailable` / `idempotency_conflict` / `cancellation_window_closed`)と `unauthorized` は入力に実在するが、not-found だけ穴。
- 補完: `not_found` を採用。
- 根拠: 入力側の命名が全て snake_case の名詞句であることへの整合。REST 慣習。
- 分岐リスク: 別装置は `booking_not_found` / `resource_not_found` / `NOT_FOUND` を選びうる。工場間で分岐する。
- 影響: `GET /v1/bookings/{id}` と `DELETE /v1/bookings/{id}` の 404 本文。
- 実装位置: `src/BomDD.WebApiSample.Core/ErrorCodes.cs`
- 提案: K-HTTP-REST-001 の managed_knowledge に `404 uses error code not_found` を追加するか、E-ERROR-SCHEMA-001 に code 語彙の閉じた列挙を置く。

## CHEAT-OPUS5-002 — `DELETE /v1/bookings/{id}` の成功時 status と本文

- 区分: HTTP status code の選択
- 空白: E-HTTP-CONTRACT-001 は `DELETE /v1/bookings/{id}` の存在だけを与える。REQ-004 は「キャンセルできる」までで、成功時の応答を規定していない。K-HTTP-REST-001 も DELETE の成功形(204 か 200 か)に触れていない。
- 補完: **200 + `BookingResponse`(`status: "cancelled"`)** を返す。204 No Content は採らなかった。
- 根拠: E-CANCELLATION-001 が「すでに cancelled への再キャンセルは同じ結果を返す」と要求しており、"同じ結果" を呼び出し側が観測できるためには本文が要る。204 では再送の同一性を客に見せられない。
- 分岐リスク: 別装置は 204 No Content を選びうる。その場合、再キャンセルの同一性は観測不能になる。
- 影響: `openapi/openapi.json` の delete レスポンス、`test/.../HttpChecks.cs` の cancel 系。
- 提案: E-HTTP-CONTRACT-001 の surface_contract に各 operation の成功 status を書く。

## CHEAT-OPUS5-003 — `GET /v1/bookings` の応答が裸の配列であること

- 区分: HTTP 表面形(work order の列挙外だが同種)
- 空白: 一覧の応答形が未規定。ページング、フィルタ(roomId / status / 期間)、包み(`{"items":[...]}`)の有無すべて空白。
- 補完: **裸の JSON 配列 `BookingResponse[]`**、フィルタなし、ページングなし、作成順、confirmed と cancelled の両方を含む。
- 根拠: 未規定の表面を増やさない(BOM にない機能を足さない)方針。OpenAPI では `type: array` として表現できる。
- 分岐リスク: 別装置は `{"items": [...], "total": n}` を返しうる。クライアント互換性が壊れる。
- 影響: `openapi/openapi.json` の `/v1/bookings` get、`src/BomDD.WebApiSample.Api/Program.cs`
- 提案: 一覧は E-BOM に要求が無い(REQ-005 が「一覧」とだけ言う)。E-LISTING 品目を起こし、包み・順序・フィルタを invariants にする。

## CHEAT-OPUS5-004 — 予約 ID のハッシュ入力・長さ・衝突時の扱い

- 区分: 予約ID生成方式
- 空白: M-CORE-BOOKING-SERVICE-001 は「deterministic hash with prefix bk_」まで。**何をハッシュするか / どのアルゴリズムか / 何文字か / 衝突したらどうするか**は空白。
- 補完: `bk_` + SHA-256(`canonicalFingerprint + "|" + idempotencyKey`) の先頭 12 バイト = 24 桁小文字 hex。同一 id が既存なら seed に連番を足して再計算する。
- 根拠: fingerprint を種にすれば「同じ内容の予約は同じ id」という決定性が最も強く出る。idempotencyKey を種に含めたのは、**キャンセル後に同一内容を作り直したときに id が衝突する**ため(cancelled は重複判定対象外なので、この再作成は正当に成功する)。それでも衝突しうるので連番で回避する。
- 分岐リスク: 別装置は GUID・ULID・連番・SHA-1 を選びうる。id は外部に漏れる識別子なので、工場が違えば互換性が無い。また「決定的」の解釈が「同一入力で同一 id」なのか「同一プロセス内で再現」なのかも分岐する。
- 影響: `src/BomDD.WebApiSample.Core/BookingService.cs`、`openapi/openapi.json` の id pattern `^bk_[0-9a-f]+$`
- 提案: M-BOM の invariant を `bk_ + first 24 hex chars of SHA-256(fingerprint|idempotencyKey)` まで具体化する。決定性の観測範囲(プロセス跨ぎか否か)も書く。

## CHEAT-OPUS5-005 — canonical fingerprint の**正規化方式**(区切り・大小・空白・時刻精度)

- 区分: 冪等性 fingerprint の正規化方式
- 空白: E-IDEMPOTENCY-001 は「roomId, customerId, startUtc, endUtc を正規化して連結する」と言うが、**どう正規化しどう連結するか**は空白。M-BOM の「roomId is normalized to uppercase」は *重複比較* の文脈で述べられており、fingerprint での扱いは明示されていない。
- 補完:
  - 区切り文字 `|`(4 項目を固定順で連結)
  - roomId: `Trim()` → `ToUpperInvariant()`
  - customerId: `Trim()` のみ(**大小は区別する**)
  - startUtc/endUtc: UTC に正規化し `yyyy-MM-ddTHH:mm:ss.fffffffZ` の固定 7 桁精度で描画
- 根拠: roomId の uppercase は M-BOM から read-across。customerId は識別子であって部屋名ではないため、大小同一視は勝手な同一視になると判断した(逆向きの判断もありうる)。時刻は 7 桁固定にしないと `10:00:00Z` と `10:00:00.000Z` が別 fingerprint になり、同一再送が conflict へ落ちる。
- 分岐リスク: 別装置が JSON 再直列化・ソート済みキー・`;` 区切り・秒精度切り捨て・customerId 小文字化を選ぶと、**同じ payload が別 fingerprint になる**。fingerprint は永続化・外部露出しないので実害は工場内に閉じるが、再送判定の境界が動く。特に **customerId の大小同一視の有無**は `CP-IDEMPOTENCY-FIELDS-001` の判定を変えうる。
- 影響: `src/BomDD.WebApiSample.Core/BookingService.CanonicalFingerprint`
- 提案: E-IDEMPOTENCY-001 の invariant に、区切り・各項目の正規化・時刻の描画精度を書き切る。

## CHEAT-OPUS5-006 — 応答時刻の描画精度(秒 or 7桁)

- 区分: 日時のUTC/offset扱い(**入力側は導出済み。出力側が空白**)
- 空白: K-UTC-ISO8601-001 は「response timestamps are serialized as date-time strings」まで。**精度**(秒か、ミリ秒か、7 桁か)が空白。
- 補完: 端数が 0 なら `yyyy-MM-ddTHH:mm:ssZ`、端数があれば `yyyy-MM-ddTHH:mm:ss.fffffffZ`。常に literal Z。
- 根拠: 典型入力 `2026-08-03T10:00:00Z` をそのままエコーバックできる(round-trip する)ことを優先した。常に 7 桁にすると入力と応答が字面で食い違う。
- 分岐リスク: 別装置は常に `.0000000Z`(`"O"` 書式)か常にミリ秒 3 桁を選びうる。文字列比較する客先オラクルは分岐する。
- 影響: `src/BomDD.WebApiSample.Core/UtcTimestamp.Format`
- 提案: K-UTC-ISO8601-001 に「応答は入力精度を保存する / 常に N 桁」のいずれかを明記する。

## CHEAT-OPUS5-007 — `+00:00` と小文字 `z` も拒否したこと

- 区分: 日時のUTC/offset扱い(境界の解釈)
- 空白: 入力は「非Zオフセット(例 +09:00)は invalid_request」「literal Z 必須」と言う。**`+00:00`(値としては UTC だが字面は Z でない)** と **小文字 `z`(RFC 3339 は大小どちらも許す)** の扱いは、二つの記述のどちらを優先するかで割れる。
- 補完: どちらも **拒否**(400 invalid_request)。
- 根拠: 「literal Z 必須」を字面の要件として厳格に読んだ。CP-OFFSET-Z-001 の狙い(format: date-time の曖昧さを潰す)にも整合する。
- 分岐リスク: 別装置は `+00:00` を「UTC だから受理」と読みうる。`z` 小文字も RFC 3339 準拠を理由に受理しうる。
- 影響: `src/BomDD.WebApiSample.Core/UtcTimestamp.TryParse`、`openapi/openapi.json` の `UtcTimestamp.pattern`
- 提案: E-BOOKING-INTERVAL-001 に `+00:00` と小文字 z の可否を明記する(現状は「例」しか無く境界が閉じていない)。

## CHEAT-OPUS5-008 — `idempotencyKey` が任意項目であること

- 区分: 冪等性(項目の必須性)
- 空白: E-IDEMPOTENCY-001 は「idempotencyKey はリクエスト本文の正規化 fingerprint に紐づく」と言うが、**キーが無い POST を受理するか**が空白。
- 補完: **任意**。無ければ冪等照合を行わず、重複判定(E-AVAILABILITY-001)だけを通す。空白文字のみのキーは「無し」と同一視する。
- 根拠: 必須にすると `CP-CONCURRENCY-SURFACE-001`(並列 POST で 1 件だけ 201)がキー無しで表現できなくなる。Control Plan がキー無し POST の並列を想定していると読んだ。
- 分岐リスク: 別装置が必須にすると、キー無しリクエストが 400 になり同じ受入が通らない。
- 影響: `openapi/openapi.json` の `CreateBookingRequest.required`(4 項目のみ)、`BookingService.Create`
- 提案: E-IDEMPOTENCY-001 に「idempotencyKey は optional。無い場合は冪等照合を行わない」を追加する。

## CHEAT-OPUS5-009 — 検査の優先順位(冪等 > 重複、認証 > 検証)

- 区分: HTTP status code の選択(どのコードが勝つか)
- 空白: 複数の規則に同時に抵触する要求で、**どのエラーを返すか**が未規定。
  - (a) 同一キー + 異なる payload で、かつ新 payload が既存予約と時間重複する → `idempotency_conflict` か `slot_unavailable` か
  - (b) API key が無く、かつ本文も不正 → 401 か 400 か
  - (c) 期限切れの予約を **再度**キャンセル → `cancellation_window_closed` か 成功(同じ結果)か
- 補完: (a) 冪等照合を先に行い `idempotency_conflict`(409)。(b) 認証を先に行い 401。(c) cancelled 判定を先に行い **成功**(200)。
- 根拠: (a) 冪等再送(同一キー+同一 payload)が自分自身と重複して `slot_unavailable` に落ちるのを防ぐには冪等照合が先でなければならない。同じ順序を conflict 側にも適用した。(b) 認証は資源に触れる前の関門。(c) E-CANCELLATION-001 の「すでに cancelled への再キャンセルは同じ結果を返す」を、期限を跨いでも成り立つ不変条件として読んだ。
- 分岐リスク: (c) は割れやすい。別装置は「今は期限外だから 409」と読みうる。その場合、同じ DELETE を 2 回叩くと 200 → 409 と結果が変わり、冪等でなくなる。
- 影響: `src/BomDD.WebApiSample.Core/BookingService.Create` / `.Cancel`、`src/BomDD.WebApiSample.Api/Program.cs` の認証ミドルウェア位置
- 提案: E-BOM に「規則の適用順序」を明示する品目を置く(競合裁定は表面ではなく核の設計事項)。

## CHEAT-OPUS5-010 — 不正 JSON / 不正 Content-Type を 400 `invalid_request` にしたこと

- 区分: HTTP status code の選択
- 空白: 本文が JSON として壊れている場合、Content-Type が `application/json` でない場合の扱いが空白。ASP.NET Core の既定は `application/problem+json`(RFC 7807)であり、E-ERROR-SCHEMA-001 の `{code, message}` と**形が違う**。
- 補完: 本文の読み取り例外を捕捉して **400 + `{"code":"invalid_request", ...}`** に統一。Content-Type 不一致も 415 ではなく 400 `invalid_request`。
- 根拠: K-HTTP-REST-001 の「all input validation failures use HTTP 400 with error code invalid_request」を、フレームワーク既定より優先した。E-ERROR-SCHEMA-001 の「エラーは code と message を持つ」に穴を空けないため。
- 分岐リスク: 別装置はフレームワーク既定の ProblemDetails を素通しし、**エラー形式が経路によって二種類**になる(表面の穴)。415 を選ぶ工場ともここで分岐する。
- 影響: `src/BomDD.WebApiSample.Api/Program.cs` の POST ハンドラ
- 提案: E-ERROR-SCHEMA-001 に「フレームワーク既定のエラー本文を露出しない」を明記する(これは検査可能な不変条件)。

## CHEAT-OPUS5-011 — 応答が `roomId` を**正規化後の大文字**で返すこと

- 区分: 表面のデータ整合(work order の列挙外)
- 空白: M-BOM は「重複比較の前に uppercase 正規化」と言うだけで、**保存値と応答値のどちらを正規化するか**が空白。`room-a` で作った予約を `ROOM-A` として返すのは、入力の非可逆な書き換えである。
- 補完: 正規化値を保存し、応答もそれを返す。原文は保持しない。
- 根拠: 原文を別途保持すると「同じ部屋なのに表示が二通り」になり、一覧が不整合に見える。
- 分岐リスク: 別装置は原文をエコーバックしうる。その場合、客先は `roomId` が入力どおりに戻る前提でコードを書ける(こちらの実装では戻らない)。
- 影響: `src/BomDD.WebApiSample.Api/Contracts.cs`、`openapi/openapi.json` の `BookingResponse.roomId` 説明
- 提案: E-BOM に roomId の正規化の適用範囲(比較のみ / 保存も)を書く。

## CHEAT-OPUS5-012 — 永続化が in-memory であること、および並列制御の方式

- 区分: 製造方式(work order の列挙外だが、`CP-CONCURRENCY-SURFACE-001` の成立条件)
- 空白: 保存先が一切未規定(M-BOM は artifact の type しか言わない)。`CP-CONCURRENCY-SURFACE-001` は「並列 POST で重複を作らない」と要求するが、**どう作らないか**は空白。
- 補完: プロセス内 `Dictionary` + 単一 `lock` による直列化。DB もトランザクションも使わない。プロセスを落とすとデータは消える。
- 根拠: 入力に永続化の要求が無く、受入(`dotnet run` 一発)が外部依存を持てない。並列は最小の相互排他で満たす。
- 分岐リスク: 別装置が DB を選ぶと、重複防止は一意制約か楽観ロックになり、**失敗時の status が 409 以外**(例: 500、あるいはリトライ)に化けうる。単一プロセス前提もスケールアウトで破れる。
- 影響: `src/BomDD.WebApiSample.Core/BookingService.cs`
- 提案: M-BOM に「in-memory・単一プロセス前提」を as-built の制約として記録し、S-BOM 側で「多重化時に破れる不変条件」として引き継ぐ。

## CHEAT-OPUS5-013 — `/health` エンドポイントの存在とパス名

- 区分: 表面の追加(work order の列挙外)
- 空白: Control Plan の depth L1 が「process starts and health endpoint responds」と言うが、**health endpoint のパス・応答形・認証要否**は E-HTTP-CONTRACT-001 の paths に無い。
- 補完: `GET /health`、認証不要、`{"status":"ok"}` を 200 で返す。`/v1` 配下に置かない。
- 根拠: L1 を測るには到達点が要る。認証必須にすると「プロセスが起きたか」と「キーが合っているか」が分離できない。
- 分岐リスク: 別装置は `/healthz`・`/v1/health`・`/` を選ぶ。受入ハーネスがパスを直接叩くため、工場間でハーネスが流用できなくなる。
- 影響: `src/BomDD.WebApiSample.Api/Program.cs`、`openapi/openapi.json` の `/health`、`test/.../ApiProcess.cs`
- 提案: E-HTTP-CONTRACT-001 の surface_contract に `GET /health (no auth)` を足す。Control Plan が参照する経路は E-BOM に実在させる。

## CHEAT-OPUS5-014 — 予約開始時刻が過去でも受理すること

- 区分: 検証規則の**不在**の解釈
- 空白: E-BOOKING-INTERVAL-001 に「開始は未来でなければならない」という不変条件が**無い**。無いことが意図か抜けかは判定できない。
- 補完: **過去の開始時刻も受理する**(検証を足さない)。
- 根拠: BOM にない制約を実装が勝手に増やすと、BOM が実装の下位互換になる。E-CANCELLATION-001 が「開始 24 時間前を過ぎたキャンセルは拒否」と言うだけで作成側に触れていないことも、作成には期限が無い読みを支持する。
- 分岐リスク: 別装置は「常識的に過去予約は 400」と補いうる。その場合、`CP-CORE-CANCEL-001` を HTTP 経由で測る際に「2 時間後に始まる予約」を作れるかどうかは変わらないが、過去日付の回帰テストは通らなくなる。**"足さなかった" ことも分岐である**ため記録する。
- 影響: `src/BomDD.WebApiSample.Core/BookingService.Create`(該当検証を意図的に置いていない)
- 提案: E-BOOKING-INTERVAL-001 に「過去の開始時刻を受理する/しない」を明記する。

## CHEAT-OPUS5-015 — API キーが単一・平文・設定既定値であること

- 区分: 認証の実装方式
- 空白: M-BOM は `default_demo_key: demo-key` を与えるが、**キーが 1 本か複数か、どこから読むか、比較方法**は空白。
- 補完: 設定キー `Api:Key`(未設定なら `demo-key`)から 1 本だけ読み、序数一致で比較する。ハッシュ照合も定数時間比較もしない。複数キー、失効、スコープは無い。
- 根拠: 「default_demo_key」という語が単一キーのサンプルを示唆している。
- 分岐リスク: 別装置は複数キーや `Bearer` 併用を実装しうる。また実運用ではタイミング攻撃耐性のある比較が要るが、BOM にその要求が無いので入れていない。
- 影響: `src/BomDD.WebApiSample.Api/Program.cs`
- 提案: E-AUTH-APIKEY-001 に鍵の本数・供給元・比較方法を書く(セキュリティ要求は表面ではなく E-BOM の不変条件)。

## CHEAT-OPUS5-016 — 受入ハーネスが API プロセスを自分で起動すること

- 区分: 受入の構成(work order の列挙外)
- 空白: M-ACCEPTANCE-HARNESS-001 の `verifies` は `M-CORE-BOOKING-SERVICE-001` と `M-OPENAPI-DOCUMENT-001` の 2 つだけで、**`M-API-ENDPOINTS-001` が verifies に無い**。一方 Control Plan は L3 の特性を 5 件持ち、その fixture は `planned HTTP smoke/concurrency harness` と `loops/webapi-01/blackbox-oracle.ps1` を指す。後者は本 workspace に存在しない。
- 補完: 受入ハーネスがビルド済み API dll を子プロセスとして **port 5210** で起動し、L1/L3 を HTTP で測る。終了時にプロセスツリーごと停止する。dll が見つからなければ `dotnet run` にフォールバックする。
- 根拠: 必須受入は `dotnet run --project test/BomDD.WebApiSample.Acceptance` の一本であり、その外に L3 の測定経路が無い。測れない特性を「planned」のまま緑にすると fail-open になる。
- 分岐リスク: 別装置は L3 を測らずに(unit + L2 だけで)受入を緑にしうる。その場合 `CP-AUTH-SURFACE-001` / `CP-CONCURRENCY-SURFACE-001` は**未測定のまま合格扱い**になる。
- 影響: `test/BomDD.WebApiSample.Acceptance/ApiProcess.cs`、`Program.cs`、`BomDD.WebApiSample.Acceptance.csproj`(Api への build-order 依存)
- 提案: M-ACCEPTANCE-HARNESS-001 の `verifies` に `M-API-ENDPOINTS-001` を追加し、Control Plan の `status: planned` を解消するか、planned のままなら「未測定」として受入結果に出す規律を書く。

---

## 記録しなかった判断(境界の説明)

以下は空白ではあるが、成果物の外部観測可能な振る舞いに影響しないため CHEAT として起票していない。
判断の存在自体は残す。

- C# の名前空間・ファイル分割・`TimeProvider` 注入などの内部構造(M-BOM の artifact.path と type には従っている)。
- 受入ハーネスの出力書式(PASS/FAIL 行、集計行)。
- OpenAPI の `info.title` / `servers` / `tags` / `examples` などの記述的メタデータ。
- ログ出力方針(ASP.NET Core の既定のまま、追加していない)。
