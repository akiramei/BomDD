"""Does each pinned rule's fixture go red when the checker breaks that rule? (run from this folder)"""
import contextlib
import io
import sys

sys.path.insert(0, ".")
import check  # noqa: E402
import form_check as fc  # noqa: E402


def run_selftest():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = check.selftest()
    return rc, [l for l in buf.getvalue().splitlines() if l.startswith("FAIL")]


orig_num, orig_run, orig_init = fc.num, fc.Specimen.run, fc.Specimen.__init__


def banker(x, d):
    s = f"{round(float(x), d):.{d}f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def sequential(self, src, presses):
    state = {n: fc._ev(t, {"src": src}.__getitem__) for n, (t, _) in self.state.items()}
    for b in presses:
        if b not in self.buttons:
            return "undefined", b
        for v, t in self.buttons[b].items():
            state[v] = fc._ev(t, self._env(src, state).__getitem__)
    env = self._env(src, state)
    return "ok", {s: fc._ev(t, env.__getitem__) for s, t in self.observe.items()}


def no_type_check(self, src, presses):
    state = {n: fc._ev(t, {"src": src}.__getitem__) for n, (t, _) in self.state.items()}
    for b in presses:
        if b not in self.buttons:
            return "undefined", b
        env = self._env(src, state)
        state = {**state, **{v: fc._ev(t, env.__getitem__) for v, t in self.buttons[b].items()}}
    env = self._env(src, state)
    return "ok", {s: fc._ev(t, env.__getitem__) for s, t in self.observe.items()}


def missing_is_error(self, src, presses):
    for b in presses:
        if b not in self.buttons:
            raise fc.FormError("undefined")
    return orig_run(self, src, presses)


for name, apply, undo, want in (
        ("num rounds half to even", lambda: setattr(fc, "num", banker), lambda: setattr(fc, "num", orig_num), "F2"),
        ("buttons assign one by one", lambda: setattr(fc.Specimen, "run", sequential),
         lambda: setattr(fc.Specimen, "run", orig_run), "F12"),
        ("no slot type check", lambda: setattr(fc.Specimen, "run", no_type_check),
         lambda: setattr(fc.Specimen, "run", orig_run), "F8"),
        ("an undefined button is an error", lambda: setattr(fc.Specimen, "run", missing_is_error),
         lambda: setattr(fc.Specimen, "run", orig_run), "F3")):
    apply()
    rc, fails = run_selftest()
    undo()
    hit = any(f.startswith("FAIL " + want + " ") for f in fails)
    print(f"{name}: selftest exit {rc}, {len(fails)} red, {want} red: {hit}")
