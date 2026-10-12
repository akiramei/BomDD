# ECO-105 evidence: C11b runs beside C11's own qualification runs

**The scripts** are kept here. Their outputs are files where a run wrote one. Where a run printed to the console, the printed text is copied below; that is noted beside it.

## Measurement before the change (2026-10-12, this machine)

**`sc_profile.py`**: each self-conformance check timed in the order `main()` runs them. Console output, abridged to the slow lines:

```
total 337.9 s, failures 0
  330.6 s  c11_process_core  10 subprocesses 330.0 s; slowest: 167.1s process-qualification.py; 156.2s process-qualification.py; 3.0s bomdd-init.py AdaptSmoke
    2.1 s  c14_kit_freshness
    1.5 s  c4_scaffold
    1.4 s  c13_link_integrity
  (every other check under 1 s)
```

**`pq_profile.py`**: one full process-qualification run as C11 runs it, with the timing probe of `../viewtube-gate-equipment-20261012/site/` on PYTHONPATH. Console output:

```
process-qualification rc=0 total 160.6 s; python processes started 613
python process-validator processes (from hooks and direct): 232
    120.9 s  x134  git commit
     24.9 s  x1194 git rev-parse
     20.3 s  x42   python process-validator.py
     14.2 s  x644  git show
process-validator runs: 232, total 59.6 s, mean 0.26 s
```

**CI run 38258045785** (`gh run view --json jobs`):

| Job | Total | Of which self-conformance |
|---|---:|---:|
| fast (ubuntu-latest) | 71 s | 61 s |
| fast (windows-latest) | 242 s | 215 s |
| dotnet | 351 s | 328 s (`--dotnet`) |

## The prototype (`compare105.py`, in a throwaway clone at e35c73d)

Console output:

```
original: exit 1, 336.5 s, 25 lines
ECO-105: exit 1, 188.3 s, 25 lines
same exit code and check lines: True
```

Both runs exited 1 on C18 only, because the clone has no `core.hooksPath`; that was confirmed by running every check except C11 in the clone. It is the same in both versions.

## The failing side (`equiv105.py`)

- `equiv-output.txt`: 6 scenarios, all the same. C11's and C11b's subprocess calls are replaced by a fake; the printed lines, FAILURES and the exception are compared.
- `equiv-mutants-output.txt`: two broken versions are told apart (10 DIFFERENT rows between them):
  - one does not wait for C11b;
  - one does not report C11b's results.

## The real repository

- `sc-before-output.txt`: the original self-conformance at the filing commit c82b852, exit 0, 387 s wall time.
- The changed version's run before the manufacture commit is recorded in the order's section 4.
