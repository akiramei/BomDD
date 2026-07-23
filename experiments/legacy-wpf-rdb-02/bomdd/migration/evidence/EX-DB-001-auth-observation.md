# EX-DB-001 observation — authentication negotiation

Observed: 2026-07-19  
Milestone / STEP: MIG-10 / STEP-011  
Observer: Experiment Operator (Codex)

## Fixed inputs

- Application: Traggo v0.8.3, commit `6321119c3c2d55f04e2e4967f6492aabd6067b76`
- Driver: version frozen in the release binary
- Server: PostgreSQL 16.14 on `127.0.0.1:55432`
- Database: isolated `traggo_prod`
- Production DB: not used

## Result

The process exited before schema creation with:

```text
pq: unknown authentication response: 10
```

The runtime log contained the connection string including an experiment credential and therefore remains under ignored `runtime/`; it is not accepted evidence. This record contains the sanitized result only.

## Boundaries

- production DB: unchanged
- baseline fixture: not created
- current source: unchanged
- schema: no application tables created

Disposition: open `EX-DB-001`; DB Custodian must establish a server authentication method compatible with the frozen source before baseline capture continues.

