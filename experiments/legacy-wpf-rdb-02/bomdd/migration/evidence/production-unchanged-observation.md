# Production-equivalent database unchanged observation

2026-07-19、MIG-10 Gateのpersist後に`traggo_prod`へ`BEGIN TRANSACTION READ ONLY`で接続し、次を確認した。

- application table counts: `1,1,1,1`（users, tag_definitions, time_spans, time_span_tags）
- tag: `project,1,#e6b3b3`
- tag value: `1,project,experiment`

基準線作成時の代表値と一致した。Gate自体のmanifestには`traggo_prod`の接続先もowner資格情報もなく、`traggo_validator`は同DBへのCONNECTを拒否される。
