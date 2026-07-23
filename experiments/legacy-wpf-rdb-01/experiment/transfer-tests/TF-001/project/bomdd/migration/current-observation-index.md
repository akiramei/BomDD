# Current Behavior Observation Index

Original instance: Traggo v0.8.3 / `6321119c`, Windows amd64 official binary  
Observed: 2026-07-19 11:46 JST  
Observer: Experiment Operator (Codex)  
Fixture: synthetic data only

| Observation ID | FUNC/UI/DB refs | Class | Input and operation | Expected/observed result | Evidence |
|---|---|---|---|---|---|
| OBS-CURRENT-001 | login, UI-shell, list, users/devices | normal + empty | first launch; login as synthetic admin; open List | version `0.8.3@6321119c`; navigation displayed; no spans; default user/device rows created | `evidence/current-ui/OBS-UI-001-timesheet-empty.jpg`, `baseline-build.log` |
| OBS-CURRENT-002 | tags, timer, list, time_spans, time_span_tags | normal + populated | create tag key `project`; start `project:experiment`; stop after six seconds | list shows tag and 6s; DB has one definition, span and span tag | `evidence/current-ui/OBS-UI-002-timesheet-list.jpg`, `baseline-db-observation.md` |
| OBS-CURRENT-003 | calendar, time range | normal + alternate-view | open Calendar after OBS-CURRENT-002 | week 13–19 Jul 2026; accessible DOM contains `project:experiment START` on 19 Jul | `evidence/current-ui/OBS-UI-003-timesheet-calendar.jpg`, `evidence/current-ui/OBS-UI-003-calendar-dom.txt`, `baseline-db-observation.md` |

Screenshot SHA-256:

- OBS-CURRENT-001: `027f866840386c7c09f033136df3c653ded7d9bb874ec9c645f073e5e6a8be0e`
- OBS-CURRENT-002: `3b5df570972bb731dceaf096709ec42b1c0a5bfc43bca37e5ff8a758ba2f5c4d`
- OBS-CURRENT-003: `de6eb9f42b7798b5c3d6f19e21c6d663bf2b1754f1c364a87618f80f9d5c63a9`

MIG-10 freezes a representative baseline, not the final acceptance suite. MIG-20 must enumerate every feature and missing error/empty/concurrency observation. A critical behavior without an observation at MIG-30 requires a specification ruling and may not be guessed by the worker.

The machine-checked evidence closure is `evidence/current-ui-evidence-manifest.json`. It must enumerate exactly the observation IDs above and seal every screenshot and semantic evidence file.
