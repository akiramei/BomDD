# EXP-20261025-02 — undeclared cross-unit dependencies in MoviePad-Remake delivery 1

Read-only on MoviePad-Remake (local repository, no remote); everything is read at commit `f30d771` with `git show` / `git ls-tree`. Text files are
LF; the sha256 values are of the bytes the commit stores.

| File | What | sha256 |
|---|---|---|
| `preregistration.md` | the decisions fixed before any scan (`9f31cdd`), with an amendment made before the delivery was read | `d928b1ae1a7ce203d01bf163fb1da2ed01425b58a98321a4a6fad4220de4e42e` |
| `scan_deps.py` | the scanner: file → unit, type-name references across units, verdicts against `part_standard.requires` | `9636580c68648b23354258220242205f89f2a6900c56f4252d5fbd3930bc9a00` |
| `run_exp.py` | calibration (synthetic fixture; the delivery with one undeclared reference added), then the delivery scan only if both pass | `b454b96339ef7ef3c23fa752e69d96346274f8f5f463467c7c085a8826ced23c` |
| `results.txt` | its output | `4540ba6361ac27b0ddef3f46879172d339c935bd50dfc3b8ad355f0cbb1a61f9` |
| `results.md` | the reading | — |

Command (from this folder; `PYTHONIOENCODING=utf-8` on a Windows console):

```
python -B run_exp.py ../../../../MoviePad-Remake results.txt
```
