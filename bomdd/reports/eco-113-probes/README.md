# ECO-113 — OS probes cited in the order §0 (Windows 11, CPython 3.13, 2026-10-18)

Each script creates its own files in a temp directory (or next to itself) and runs on Windows only (`msvcrt`, `kernel32`).

| folder | script | what it measured (the order §0) |
|---|---|---|
| `oslock/` | `probe.py` (+ `holder.py`) | P1-P4: a live holder blocks `LK_NBLCK`; the lock is free at once after the holder is killed; a child does not keep it; a second handle is blocked |
| `jobobject/` | `jobprobe.py` (+ `jobholder.py`, `loop.py`) | J1-J4: a named kill-on-close job, the entry inside it; killing the entry ends the grandchild; the job is then gone |
| `jobobject/` | `jobprobe2.py` (+ `loop.py`) | K1-K3: the entry outside the job, the cell started suspended, assigned by handle, resumed; normal end and killed entry |
| `reviewer/` | `lockprobe.py` | (round-1 reviewer of ECO-113) errno values on conflict, inheritance, text-mode writes, `LK_LOCK` |
| `reviewer/` | `r2probe.py` | (round-2 reviewer) unlocked concurrent ledger appends lose and tear lines; killing a `shell=True` shell leaves its child running |
