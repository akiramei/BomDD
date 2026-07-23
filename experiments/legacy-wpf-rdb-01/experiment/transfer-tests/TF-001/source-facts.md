# TF-001 Supplied Source Facts

These are supplied observations, not choices for the worker. Copy them into the two manifest templates exactly where the corresponding field asks for them.

## DB fixture

| Field | Supplied value |
|---|---|
| schema | `bomdd-legacy-wpf-baseline-fixture/1.0` |
| fixture ID | `TRAGGO-BASELINE-001` |
| engine | `sqlite` |
| source snapshot | `2026-07-19T02:46:48Z` |
| working copy policy | `copy-per-test` |
| baseline fixture | `fixtures/baseline/traggo.db` |
| restore copy | `fixtures/restore-control/traggo.db` |
| fixture and restore SHA-256 | `308b5feebc0eed2be1ac781698f20bee2fd771fbd61a298e8e5f4e1544237458` |
| DB baseline | `bomdd/migration/db-baseline.md` / `6db0086e81c69239ec7b2832ad5ee931cb75fa92c03bb8c728c8f5764a09231e` |
| schema evidence | `bomdd/migration/evidence/baseline-schema.sql` / `dd5179a4c76f010a8ccc2705233bbedf1439ee471751cd729cad90c820796b73` |
| normalized schema SHA-256 | `b74799d39cabfc458d18beed7c92d1401bc4fafed04267e7701d01bf57d8d804` |
| DB observation | `bomdd/migration/evidence/baseline-db-observation.md` / `fe9e7fe40f76568b8061bff15a4cc3d8793b720d137762c0b10bf081083afca9` |
| expected checks | integrity `ok`; FK violations `0`; restore `pass`; restored SHA equals fixture SHA |

Canonical queries and expected rows:

```json
[
  {
    "id": "APPLICATION-TABLE-COUNTS",
    "sql": "SELECT (SELECT COUNT(*) FROM users),(SELECT COUNT(*) FROM tag_definitions),(SELECT COUNT(*) FROM time_spans),(SELECT COUNT(*) FROM time_span_tags),(SELECT COUNT(*) FROM devices),(SELECT COUNT(*) FROM user_settings),(SELECT COUNT(*) FROM dashboards),(SELECT COUNT(*) FROM dashboard_entries),(SELECT COUNT(*) FROM dashboard_ranges),(SELECT COUNT(*) FROM dashboard_tag_filters)",
    "expected_rows": [[1, 1, 1, 1, 1, 0, 0, 0, 0, 0]]
  },
  {
    "id": "VISIBLE-TAG",
    "sql": "SELECT key,user_id,color FROM tag_definitions ORDER BY key,user_id",
    "expected_rows": [["project", 1, "#e6b3b3"]]
  },
  {
    "id": "VISIBLE-SPAN",
    "sql": "SELECT id,start_utc,end_utc,start_user_time,end_user_time,offset_utc,user_id,note FROM time_spans ORDER BY id",
    "expected_rows": [[1, "2026-07-19 02:46:42+00:00", "2026-07-19 02:46:48+00:00", "2026-07-19 11:46:42+00:00", "2026-07-19 11:46:48+00:00", 32400, 1, ""]]
  },
  {
    "id": "VISIBLE-TAG-VALUE",
    "sql": "SELECT time_span_id,key,string_value FROM time_span_tags ORDER BY time_span_id,key",
    "expected_rows": [[1, "project", "experiment"]]
  }
]
```

## UI observations

| Field | Supplied value |
|---|---|
| schema | `bomdd-legacy-wpf-ui-evidence/1.0` |
| source version | `Traggo v0.8.3 / 6321119c / Windows amd64 official binary` |
| observation index | `bomdd/migration/current-observation-index.md` / `99556b9171dee7d60308f9518d1700fa20de8cc4cd0463d9aa0ce6df097e1a5a` |
| required states | `empty`, `populated`, `alternate-view` |
| minimum dimensions | `1024 x 600` |
| actual screenshot dimensions | all `1280 x 720` |
| media type | all `image/jpeg` |
| OBS-CURRENT-001 screenshot | `bomdd/migration/evidence/current-ui/OBS-UI-001-timesheet-empty.jpg` / `027f866840386c7c09f033136df3c653ded7d9bb874ec9c645f073e5e6a8be0e` |
| OBS-CURRENT-001 semantic evidence | `execution-log`; `bomdd/migration/evidence/baseline-build.log` / `0a0195de96013aff05334825634f9880aff53688248c66f54136a9c738b926cf` |
| OBS-CURRENT-002 screenshot | `bomdd/migration/evidence/current-ui/OBS-UI-002-timesheet-list.jpg` / `3b5df570972bb731dceaf096709ec42b1c0a5bfc43bca37e5ff8a758ba2f5c4d` |
| OBS-CURRENT-002 semantic evidence | `database`; `bomdd/migration/evidence/baseline-db-observation.md` / `fe9e7fe40f76568b8061bff15a4cc3d8793b720d137762c0b10bf081083afca9` |
| OBS-CURRENT-003 screenshot | `bomdd/migration/evidence/current-ui/OBS-UI-003-timesheet-calendar.jpg` / `de6eb9f42b7798b5c3d6f19e21c6d663bf2b1754f1c364a87618f80f9d5c63a9` |
| OBS-CURRENT-003 DOM | `dom`; `bomdd/migration/evidence/current-ui/OBS-UI-003-calendar-dom.txt` / `654135a3a3c1089f38f33638fb5026ce23ca698c3dcb3e5af2fcc5ba7ff60c31` |
| OBS-CURRENT-003 DB evidence | `database`; same DB observation path/hash as above |

Claims to record:

| Observation | Screenshot-supported claim | Semantic-supported claim |
|---|---|---|
| OBS-CURRENT-001 | empty List view and navigation are visible | frozen original instance started successfully |
| OBS-CURRENT-002 | populated List shows `project:experiment` and six seconds | matching tag and span rows exist |
| OBS-CURRENT-003 | Calendar and week 13-19 Jul 2026 are visible | `project:experiment START` exists outside the captured viewport |

