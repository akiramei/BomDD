# Current Baseline — Traggo PostgreSQL

固定日時: 2026-07-19T11:41:19Z  
作成者: Experiment Operator (Codex)

## 原版

- Repository: `https://github.com/traggo/server.git`
- Tag / commit: `v0.8.3` / `6321119c3c2d55f04e2e4967f6492aabd6067b76`
- Windows release asset SHA-256: `a7cac6b591cf2a6122ecdebcae01cbfd3731e3afed2f13974dc040893a8cd8b7`
- License: GPL-3.0

## 実行個体

- Application: frozen official `traggo.exe`
- Database dialect: `postgres`
- Server: PostgreSQL 16.14 Windows x86-64
- Endpoint: `127.0.0.1:55432`
- Production相当DB: `traggo_prod`
- Gate用DB: `traggo_restore_control`
- Writer: `traggo_owner`だけ。validatorはproduction相当DBへCONNECT不可
- Secret: `runtime/`と実行processだけに置き、成果物へ記録しない

## 代表状態

- user `admin`が存在する。
- tag definition `project` / `#e6b3b3`が存在する。
- `project:experiment`を持つ完了time spanが1件存在する。
- login、List、Calendarを原版UIで観測した。

## 凍結成果物

- DB dump: `fixtures/baseline/traggo-postgresql.dump`
- dump SHA-256: `9b18cb620e0748cf7d103e50832f10aec184522b0eff13f563fc3f9ecef744d0`
- schema evidence: `bomdd/migration/evidence/baseline-schema-extracted.sql`
- UI evidence: `bomdd/migration/evidence/current-ui/`

原版source、release asset、production相当DBを以後のGate検査で変更しない。検査はdumpから作ったrestore-control DBだけで行う。

