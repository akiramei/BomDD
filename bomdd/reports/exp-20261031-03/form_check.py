"""EXP-20261031-03 — the form of a specimen (form.md), checked and evaluated. Holds no case and no expected value.

    python form_check.py <specimen.json>      # prints OK, or the errors; exit 1 on an error

check.py imports this file: what passes here is well formed for check.py. The rules are form.md's; each is pinned by a
fixture of check.py's selftest.
"""
import ast
import json
import pathlib
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

BUTTONS = ("Source", "24", "30", "60", "120")
SLOTS = {"V1": str, "V2": bool, "V3": bool, "V4": bool, "V5": bool, "V6": bool, "V7": bool, "V8": str}
FUNCS = ("abs", "float", "num")
RESERVED = {"src", "True", "False", *FUNCS}
NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROBE_SRC = 47.5          # the type probe's source rate: not a rate of any case
TOP = {"state", "buttons", "derived", "observe", "notes", "meta"}


class FormError(Exception):
    pass


def num(x, d):
    if not _isnum(x) or not isinstance(d, int) or isinstance(d, bool) or not 0 <= d <= 6:
        raise FormError(f"num({x!r}, {d!r}): a number and an integer 0..6")
    q = Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    s = format(q, "f")
    return s.rstrip("0").rstrip(".") if "." in s else s


def _float(x):
    if isinstance(x, str):
        try:
            return float(x)
        except ValueError:
            raise FormError(f"float({x!r})")
    if _isnum(x):
        return float(x)
    raise FormError(f"float({x!r})")


def _isnum(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _same(a, b):
    return (_isnum(a) and _isnum(b)) or type(a) is type(b)


def parse(text, where):
    if not isinstance(text, str):
        raise FormError(f"{where}: an expression must be a string")
    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError as e:
        raise FormError(f"{where}: does not parse ({e.msg})")
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Expression, ast.Load, ast.operator, ast.cmpop, ast.boolop, ast.unaryop)):
            continue
        if isinstance(n, ast.Constant):
            if not isinstance(n.value, (int, float, str, bool)):
                raise FormError(f"{where}: constant {n.value!r} not allowed")
        elif isinstance(n, ast.Name):
            names.add(n.id)
        elif isinstance(n, ast.BinOp):
            if not isinstance(n.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                raise FormError(f"{where}: operator {type(n.op).__name__} not allowed")
        elif isinstance(n, ast.UnaryOp):
            if not isinstance(n.op, (ast.USub, ast.Not)):
                raise FormError(f"{where}: operator {type(n.op).__name__} not allowed")
        elif isinstance(n, (ast.BoolOp, ast.IfExp)):
            pass
        elif isinstance(n, ast.Compare):
            if not all(isinstance(o, (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)) for o in n.ops):
                raise FormError(f"{where}: comparison not allowed")
        elif isinstance(n, ast.Call):
            if not isinstance(n.func, ast.Name) or n.func.id not in FUNCS or n.keywords:
                raise FormError(f"{where}: only abs(), float() and num() may be called, positionally")
        else:
            raise FormError(f"{where}: {type(n).__name__} not allowed")
    calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call)}
    return tree, names - calls - {"True", "False"}


def _ev(n, env):
    if isinstance(n, ast.Expression):
        return _ev(n.body, env)
    if isinstance(n, ast.Constant):
        return n.value
    if isinstance(n, ast.Name):
        if n.id in ("True", "False"):
            return n.id == "True"
        return env(n.id)
    if isinstance(n, ast.BinOp):
        a, b = _ev(n.left, env), _ev(n.right, env)
        if isinstance(n.op, ast.Add) and isinstance(a, str) and isinstance(b, str):
            return a + b
        if not (_isnum(a) and _isnum(b)):
            raise FormError(f"{type(n.op).__name__} on {a!r}, {b!r}")
        if isinstance(n.op, ast.Add):
            return a + b
        if isinstance(n.op, ast.Sub):
            return a - b
        if isinstance(n.op, ast.Mult):
            return a * b
        if b == 0:
            raise FormError("division by zero")
        return a / b
    if isinstance(n, ast.UnaryOp):
        v = _ev(n.operand, env)
        if isinstance(n.op, ast.USub):
            if not _isnum(v):
                raise FormError(f"-{v!r}")
            return -v
        if not isinstance(v, bool):
            raise FormError(f"not {v!r}")
        return not v
    if isinstance(n, ast.BoolOp):
        vals = []
        for x in n.values:
            v = _ev(x, env)
            if not isinstance(v, bool):
                raise FormError(f"and/or on {v!r}")
            vals.append(v)
        return all(vals) if isinstance(n.op, ast.And) else any(vals)
    if isinstance(n, ast.IfExp):
        c = _ev(n.test, env)
        if not isinstance(c, bool):
            raise FormError(f"if on {c!r}")
        return _ev(n.body, env) if c else _ev(n.orelse, env)
    if isinstance(n, ast.Compare):
        left = _ev(n.left, env)
        for op, r in zip(n.ops, n.comparators):
            right = _ev(r, env)
            if isinstance(op, (ast.Eq, ast.NotEq)):
                if not _same(left, right):
                    raise FormError(f"comparing {left!r} with {right!r}")
                ok = (left == right) if isinstance(op, ast.Eq) else (left != right)
            else:
                if not (_isnum(left) and _isnum(right)):
                    raise FormError(f"ordering {left!r}, {right!r}")
                ok = {ast.Lt: left < right, ast.LtE: left <= right, ast.Gt: left > right,
                      ast.GtE: left >= right}[type(op)]
            if not ok:
                return False
            left = right
        return True
    if isinstance(n, ast.Call):
        args = [_ev(a, env) for a in n.args]
        f = {"abs": None, "float": _float, "num": num}[n.func.id]
        if n.func.id == "abs":
            if len(args) != 1 or not _isnum(args[0]):
                raise FormError(f"abs{tuple(args)!r}")
            return abs(args[0])
        try:
            return f(*args)
        except TypeError:
            raise FormError(f"{n.func.id}{tuple(args)!r}: wrong number of arguments")
    raise FormError(f"{type(n).__name__}")


class Specimen:
    """A parsed specimen. Raises FormError for anything form.md makes an error, except the type of values, which the
    evaluation checks (form_check runs the type probe for that)."""

    def __init__(self, doc):
        if not isinstance(doc, dict):
            raise FormError("a specimen is a JSON object")
        extra = set(doc) - TOP
        if extra:
            raise FormError(f"unknown top-level keys {sorted(extra)}")
        for k in ("state", "buttons", "derived", "observe"):
            if not isinstance(doc.get(k), dict):
                raise FormError(f"'{k}' must be an object")
        self.state, self.derived = {}, {}
        for part, store in (("state", self.state), ("derived", self.derived)):
            for name, text in doc[part].items():
                if not NAME.match(name) or name in RESERVED:
                    raise FormError(f"{part} name {name!r} not allowed")
                store[name] = parse(text, f"{part}.{name}")
        clash = set(self.state) & set(self.derived)
        if clash:
            raise FormError(f"names in both state and derived: {sorted(clash)}")
        for name, (_, names) in self.state.items():
            if names - {"src"}:
                raise FormError(f"state.{name}: an opening value may use src only, not {sorted(names - {'src'})}")
        known = {"src", *self.state, *self.derived}
        for name, (_, names) in self.derived.items():
            if names - known:
                raise FormError(f"derived.{name}: unresolved {sorted(names - known)}")
        self._order = self._topo()
        self.buttons = {}
        for b, assigns in doc["buttons"].items():
            if b not in BUTTONS:
                raise FormError(f"button {b!r} is not one of {BUTTONS}")
            if not isinstance(assigns, dict):
                raise FormError(f"buttons.{b} must be an object")
            self.buttons[b] = {}
            for var, text in assigns.items():
                if var not in self.state:
                    raise FormError(f"buttons.{b}: {var!r} is not a state variable")
                tree, names = parse(text, f"buttons.{b}.{var}")
                if names - known:
                    raise FormError(f"buttons.{b}.{var}: unresolved {sorted(names - known)}")
                self.buttons[b][var] = tree
        if set(doc["observe"]) != set(SLOTS):
            raise FormError(f"observe must give exactly {sorted(SLOTS)}")
        self.observe = {}
        for slot, text in doc["observe"].items():
            tree, names = parse(text, f"observe.{slot}")
            if names - known:
                raise FormError(f"observe.{slot}: unresolved {sorted(names - known)}")
            self.observe[slot] = tree

    def _topo(self):
        order, mark = [], {}

        def visit(n, path):
            if mark.get(n) == 1:
                raise FormError(f"derived cycle: {' -> '.join(path + [n])}")
            if mark.get(n) == 2:
                return
            mark[n] = 1
            for m in sorted(self.derived[n][1] & set(self.derived)):
                visit(m, path + [n])
            mark[n] = 2
            order.append(n)

        for n in self.derived:
            visit(n, [])
        return order

    def _env(self, src, state):
        vals = {"src": src, **state}
        for n in self._order:
            vals[n] = _ev(self.derived[n][0], vals.__getitem__)
        return vals

    def run(self, src, presses):
        """('ok', slots) or ('undefined', button). FormError on an evaluation error or a slot of the wrong type."""
        state = {n: _ev(t, {"src": src}.__getitem__) for n, (t, _) in self.state.items()}
        for b in presses:
            if b not in self.buttons:
                return "undefined", b
            env = self._env(src, state)
            new = {v: _ev(t, env.__getitem__) for v, t in self.buttons[b].items()}
            state = {**state, **new}
        env = self._env(src, state)
        out = {}
        for slot, t in self.observe.items():
            v = _ev(t, env.__getitem__)
            if not isinstance(v, SLOTS[slot]):
                raise FormError(f"observe.{slot} gave {v!r}, not a {SLOTS[slot].__name__}")
            out[slot] = v
        return "ok", out


def load(path):
    try:
        doc = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise FormError(f"not a JSON file: {e}")
    return Specimen(doc)


def probe(spec):
    """The type probe: open at PROBE_SRC, then each defined button once from the opening state."""
    spec.run(PROBE_SRC, [])
    for b in spec.buttons:
        spec.run(PROBE_SRC, [b])


def main():
    try:
        spec = load(sys.argv[1])
        probe(spec)
    except FormError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    missing = [b for b in BUTTONS if b not in spec.buttons]
    print("OK" + (f" (buttons not defined: {', '.join(missing)})" if missing else ""))


if __name__ == "__main__":
    main()
