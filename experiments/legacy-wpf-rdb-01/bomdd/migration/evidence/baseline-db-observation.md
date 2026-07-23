# Baseline DB Observation

Observed read-only with SQLite CLI 3.49.1 on 2026-07-19.

## Integrity

```text
PRAGMA integrity_check;
ok

PRAGMA foreign_key_check;
<zero rows>
```

## Row counts

| Object | Rows |
|---|---:|
| users | 1 |
| tag_definitions | 1 |
| time_spans | 1 |
| time_span_tags | 1 |
| devices | 1 |
| user_settings | 0 |
| dashboards | 0 |
| dashboard_entries | 0 |
| dashboard_ranges | 0 |
| dashboard_tag_filters | 0 |

## Canonical visible data

```text
tag_definition: key=project, user_id=1, color=#e6b3b3
time_span: id=1, start_utc=2026-07-19 02:46:42+00:00, end_utc=2026-07-19 02:46:48+00:00
user_time: start=2026-07-19 11:46:42+00:00, end=2026-07-19 11:46:48+00:00, offset_utc=32400
tag_value: time_span_id=1, key=project, string_value=experiment
```

Password hash and generated device token are intentionally not extracted.

## Restore control

`fixtures/baseline/traggo.db` was copied to `fixtures/restore-control/traggo.db` for retained evidence. Restored hash remained `308b5feebc0eed2be1ac781698f20bee2fd771fbd61a298e8e5f4e1544237458`; integrity was `ok`, foreign-key violations were zero, and `time_spans` count was 1.
