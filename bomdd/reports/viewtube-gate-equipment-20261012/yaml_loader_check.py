"""Spot-check of a subagent finding: parse time of ViewTube's register with the pure-Python and the C YAML loader."""
import sys
import time
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8")
text = Path(r"C:\Users\akira\source\repos\ViewTube\bomdd\process\change-register.yaml").read_text(encoding="utf-8")
started = time.perf_counter()
pure = yaml.load(text, Loader=yaml.SafeLoader)
middle = time.perf_counter()
fast = yaml.load(text, Loader=yaml.CSafeLoader)
end = time.perf_counter()
print(f"register {len(text) / 1e6:.1f} MB: SafeLoader {middle - started:.2f}s, CSafeLoader {end - middle:.2f}s, equal={pure == fast}")
