"""Where validate_machinery_claims.py spends its time, on ViewTube HEAD (read-only).

Splits one run into: listing the record surface, reading and normalising each surface file once,
and the substring searches (one per claim x surface file). Counts claims, surface files and bytes.
Run twice in a row: the first run on a cold cache is what a fresh fixture or copy sees."""
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
VT = Path(r"C:\Users\akira\source\repos\ViewTube")
sys.path.insert(0, str(VT / "bomdd" / "tools"))
import validate_machinery_claims as gate  # noqa: E402
import yaml  # noqa: E402

policy = gate.load_policy(VT)
register = yaml.safe_load((VT / "bomdd/process/change-register.yaml").read_text(encoding="utf-8"))
entries = register.get("changes") or []
claims = [claim for entry in entries if gate.bound(entry, policy)
          for claim in gate.declarations(entry) if isinstance(claim, dict) and claim.get("claim")]
print(f"surface prefixes {policy['surface_prefixes']} suffixes {policy['surface_suffixes']}")
print(f"bound entries {sum(1 for entry in entries if gate.bound(entry, policy))}, claims {len(claims)}")

started = time.perf_counter()
surface = gate.record_surface(VT, policy)
listing = time.perf_counter() - started
size = sum(path.stat().st_size for path in surface)
print(f"record surface: {len(surface)} files, {size / 1e6:.1f} MB, listed in {listing:.2f}s")

started = time.perf_counter()
texts = {path: gate.normalise(open(path, encoding="utf-8", errors="replace", newline="").read(),
                              policy["remove"], policy["casefold"]) for path in surface}
reading = time.perf_counter() - started
print(f"read + normalise every surface file once: {reading:.2f}s")

needles = [gate.normalise(str(claim["claim"]), policy["remove"], policy["casefold"]) for claim in claims]
started = time.perf_counter()
hits = 0
hit_suffixes: dict = {}
for needle in needles:
    for path, text in texts.items():
        if needle and needle in text:
            hits += 1
            hit_suffixes[path.suffix] = hit_suffixes.get(path.suffix, 0) + 1
searching = time.perf_counter() - started
print(f"substring searches: {len(needles)} claims x {len(texts)} files = {len(needles) * len(texts):,} "
      f"in {searching:.2f}s ({hits} hits, by suffix {hit_suffixes})")

started = time.perf_counter()
payload = gate.inspect(VT)
print(f"whole inspect(): {time.perf_counter() - started:.2f}s, findings {payload['finding_count']}")
