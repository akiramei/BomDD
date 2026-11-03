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
