# ECO-115 closure — acceptance at verified (2026-10-26, the user's "ECO-115 をクローズして")

Run 2026-10-26 from the BomDD root. All files are LF; sha256 of the committed bytes.

| File | What | sha256 |
|---|---|---|
| `diff_window.py` | every commit from the register's `diff_audit.baseline` to the head is ECO-115's (by its subject's prefix) and every path it changed is inside the register entry's `allowed_paths`; `--control-drop` removes one allowed path as a positive control | `0147f2b6577cfe3cfc54d4edfe4ae45ef4f4e8e0f769e5486c43c8dc54ae5623` |
| `diff-window.md` | `python -B diff_window.py . 37e0fd9 ebd15c9` — PASS: 11 commits, all ECO-115's, every path allowed | `1850889b096199a414ffb71882eeda9d07274eebcbe3d32f8ad10492e71f46ea` |
| `control-drop-40-work-order.md` | the same with `--control-drop method/templates/40-work-order.md` — FAIL on the three commits that changed it (the control) | `81abb21c29a1a12bd090810f76556fa8bc0ef5a585d88a07d02ec3d9b3640203` |
| `v1-v2.txt` | `../manufacture/check_v1_v2.py` on the closure tree: PASS 144/144 (the same bytes as `../repair-r5/v1-v2.txt`: the records added at closure are outside what it reads) | `b7f595b754484d8cd8424f24cee693a0f8cbe58b94983cf2e08293b46dcf8af8` |
| `redfirst-all.txt` | `../repair-r4/redfirst_all.py` on the closure tree: 5 of 5 controls show their own failure, 2 of 2 wrong set-ups refused (the same bytes as `../repair-r5/redfirst-all.txt`) | `fe18487bed7854b6f02d50c1997d5f29cc279783b74e19728f3e77076c145c28` |

The window script stopped on the console encoding (cp932) at its first run, so its first PASS and FAIL were both unmeasured (exit 1 for that reason);
it now writes UTF-8, and the outputs above are from the repaired script. The acceptance commit after `ebd15c9` holds records only.
