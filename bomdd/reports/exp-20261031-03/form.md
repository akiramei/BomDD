# The specimen form

A **specimen** is a design of the output frame rate's five preset buttons, written so a program can compute what the screen
shows. It is one JSON object. `form_check.py <file>` checks a file against these rules and prints `OK` or the first error.
Each rule names the selftest fixture of `check.py` that pins it (`F…`).

## 1. The parts

```json
{
  "state":   { "<name>": "<expression>", ... },
  "buttons": { "<button>": { "<state name>": "<expression>", ... }, ... },
  "derived": { "<name>": "<expression>", ... },
  "observe": { "V1": "<expression>", ..., "V8": "<expression>" },
  "notes":   "anything (optional, ignored)",
  "meta":    "anything (optional, ignored)"
}
```

- **Top level**: exactly these keys; `notes` and `meta` may be left out. Any other key is an error (F21, F22).
- **`state`**: the variables of the design. Each one's expression is its value when a clip is opened; it may use `src` (the
  clip's source frame rate, a number) and nothing else (F14).
- **`buttons`**: the preset buttons, by these ids only: `Source`, `24`, `30`, `60`, `120` (another id is an error, F4). Each
  entry says which state variables the press changes and to what; only state variables may be assigned (F18). **A button left
  out is "not defined"**: a case that presses it gets an *undefined* counterexample, not an error (F3). An entry `{}` is defined
  and changes nothing (F23).
- **On a press**, every expression of the button is evaluated on the state before the press (with the derived values of that
  state), then all are assigned together (F12, F13).
- **`derived`**: named values computed from `src`, the state variables and other derived names; no cycles (F7). A name may not
  be both a state variable and a derived name (F16).
- **`observe`**: exactly the eight slots `V1`–`V8` (F9, F10); each may use `src`, the state variables and the derived names.
  Slot types: `V1` and `V8` strings; `V2`–`V7` booleans (true / false). A value of another type is an error (F8, F19).
- **Names**: letters, digits and `_`, not starting with a digit; not `src`, `True`, `False`, `abs`, `float`, `num`. Every name
  used must be one of these (F6).

## 2. Expressions

A string holding one Python expression, of these pieces only (anything else is an error, F5, F11):

- literals: numbers (`24`, `0.05`), strings (`'24'`, `" fps"`), `True`, `False`
- names (section 1)
- `a + b` (two numbers: addition; two strings: joining), `a - b`, `a * b`, `a / b` (numbers only; string + number is an
  error, F15)
- `a == b`, `a != b` (both numbers, or both of one type; a string compared with a number is an error, F20); `a < b`,
  `a <= b`, `a > b`, `a >= b` (numbers only); chains like `a < b < c`
- `a and b`, `a or b`, `not a` (booleans only); `x if c else y` (`c` boolean); `-a` (a number)
- `abs(x)` (a number); `float(x)` (a number, or a string that spells one); **`num(x, d)`** — the number `x` written with at most
  `d` decimals (`d` an integer 0–6), rounded half away from zero, trailing zeros and a trailing point removed:
  `num(29.97, 2)` is `"29.97"`, `num(30.0, 2)` is `"30"`, `num(29.97, 0)` is `"30"` (F2). Positional arguments only.

Any evaluation that breaks these rules (a wrong type, division by zero) is an error.

## 3. The slots

| slot | type | what of the screen |
|---|---|---|
| V1 | string | the export dialog summary's frame-rate text |
| V2 | boolean | the Source preset shown selected |
| V3 | boolean | the 24 preset shown selected |
| V4 | boolean | the 30 preset shown selected |
| V5 | boolean | the 60 preset shown selected |
| V6 | boolean | the 120 preset shown selected |
| V7 | boolean | the duplicate-frames note shown |
| V8 | string | the Source preset's tooltip text |

## 4. How a specimen is run

For a clip of source rate `src` and a list of presses: the state is opened (section 1), each press is applied in order, then
the eight slots are evaluated. `form_check.py` also runs a **type probe** — `src` = 47.5 (not a rate of any case), the opened
state, and each defined button pressed once — so a slot of the wrong type is found without any case (F24). It holds no case
and no expected value. `check.py` uses the same code.

An **error** anywhere makes the verdict UNKNOWN: never a pass, never a detection.
