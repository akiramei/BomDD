# ECO-121 survey evidence (filing basis; read-only)

- `survey.py` → `survey.txt`: each product's register read with `git show <head>:<path>` at ViewPrism2 `82c362ed` and ViewTube
  `62d2b3e4`. It counts the open entries (`staged`, `implemented`) and classifies them by what the register already says about why they
  wait. Run: `python -X utf8 survey.py [<repos-root>]`.
- `probe/`: whether each product's own validators accept `waiting_on` on an entry and a top-level `paused` block. Both products were
  cloned with `git clone --local` into the session scratchpad, so neither product repository was written. `add_keys.py` added the two
  keys to the clone's register. The validators were then run before and after the change; the last lines are kept as `*_base.tail.txt`
  and `*_mod.tail.txt`.
  - ViewPrism2: `bomdd/validate_bom.py` gave 0 errors and 0 warnings before and after. The probe edit also flipped the line ending of the
    one line it touched; `vp.diff` is taken with `--ignore-cr-at-eol`.
  - ViewTube: `validate_process.py`, `validate_record_language.py` and `validate_record_consistency.py --mode active` exited 0 before and
    after. `vt.diff` is the probe edit, which included a stray blank line (scratch only).
  - `vp.dwell.txt`: `bomdd-job.py --dwell` on the probed ViewPrism2 clone after a scratch commit. The pause groups all 24 open entries,
    and the reason written in that commit is 0.0 days old.

## Manufacture evidence (section 4; V3 at each product's fix commit)

- `compare_table.py`: compares the N-th table of a product ECO whose header starts `| Entry | waiting_on |` with the entries that
  carry a `waiting_on` in `bomdd-job.py --dwell --json` (the set and each value). It fails on any warning about `waiting_on` or
  `paused`. Exit 0 = equal, 1 = differs, 2 = input error. `--selftest` removes the table's first row and changes its last value, and
  must catch both.
- `viewprism2/fix-a726322.*`: the dwell JSON at ViewPrism2 `a726322`, and the comparison with ECO-149's table: EQUAL, 8 rows.
- `viewtube/fix-3517ae21.*`: the dwell JSON at ViewTube `3517ae21`, and the comparison with ECO-VT-273's table 1: EQUAL, 4 rows.
- The `.compare.txt` files hold the comparison's output followed by its selftest output, normalised to LF.
- `*/applied-*.dwell.json` and `*/applied-*.compare.txt`: the same at each product's applied commit (ViewPrism2 `9bdbe91`, ViewTube
  `42936d96`), against each product ECO's closure table (`--table 2`): EQUAL, 7 rows and 3 rows.
- `closure_checks.py` → `closure_checks.txt`: V1 (the `waiting_on` line counts per file, base to applied, and the change-management
  names) and V4 (each changed path with its class from section 2), read from git. Run: `python -X utf8 closure_checks.py [<repos-root>]`.
