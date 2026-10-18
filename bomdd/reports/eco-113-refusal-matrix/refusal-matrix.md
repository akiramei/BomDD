# S4 refusal matrix — PASS

C1 (defined == table): True

| reason | defined in | S4 row | C2 | C3 | C4 (cites) | C5 (O1) | C6 |
|---|---|---|---|---|---|---|---|
| `ABNORMAL_END` | J2 | True | True | True | True ['R2'] | True [('STOP', '1')] | True |
| `CELL_ALIVE` | J2 | True | True | True | True ['L3'] | True [('STOP', '1')] | True |
| `ENTRY_ALIVE` | X2 | True | True | True | True ['L2'] | True [('STOP', '1')] | True |
| `JOURNAL_CORRUPT` | J2 | True | True | True | True ['R2', 'R3'] | True [('UNMEASURABLE', '2')] | True |
| `JOURNAL_UNREADABLE` | A3 | True | True | True | True ['A3'] | True [('UNMEASURABLE', '2')] | True |
| `LOCK_UNAVAILABLE` | X2 | True | True | True | True ['X2'] | True [('UNMEASURABLE', '2')] | True |
| `REPORT_EXISTS` | S1 | True | True | True | True ['L9'] | True [('UNMEASURABLE', '2')] | True |
| `UNKNOWN` | J2 | True | True | True | True ['R2'] | True [('UNMEASURABLE', '2')] | True |

Failures:
- none
