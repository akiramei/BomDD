# ECO-114 basis and design evidence — part standards and assembly resolution in two products (read-only)

Measured and run 2026-10-24 for the filing of [ECO-114](../../60-change-order-eco-114.md) (§0 and the receipt) and of ECO-115's B3. Nothing in either
product repository was written. All files are LF; the sha256 values are of the bytes the commit stores.

| File | What | sha256 |
|---|---|---|
| `measure.py` | reads `bomdd/30-ebom.yaml`, `32-mbom.yaml`, `33-control-plan.yaml` at each repo's HEAD with `git show`; ViewTube's control plan also at its last 40 revisions | `07c807a0feea3a7831f5a98dd6079f7ffe76a7d224d8c0ca7d1c66709edeeb57` |
| `measurements.txt` | its output: ViewPrism2 at `504921a`, ViewTube at `c214dec0` | `9a24b594d9ce0cd6edf6f390d6ffa48f61640b824bf3e8dc41390d2ad79ff3a1` |
| `vp2-cp-results.json` | ViewPrism2 `python bomdd/cp_results.py --json` at `504921a` on the stored `tests/ViewPrism2.Tests/TestResults/cp-results.xml` (CRLF from the redirect converted to LF) | `8465e780c2249abe1365f3f3c393064bb2f13de987dcfcdd333cba959172554a` |
| `vp2-cp-results-summary.txt` | the counts read from that JSON | `725f3d56c1adce8e38ba598f175bb13b3e64d29abc00a0ccf093b71538c706a3` |
| `shapes.py` | enumerates every structural shape of both products' E-BOM, M-BOM and control plan and of the templates' own examples (ViewPrism2 at HEAD; ViewTube E/M at HEAD, control plan at `fc35bf1d`) | `38e5c34cbd89da7f3445437fefa5789a91aa085f0a3d62f4623b66181c598536` |
| `shapes.txt` | its output | `6072b5cd62640f815981cbd8d01ea44bdc090b73cb06ed566c9f9c75f6bea207` |
| `rehearse_part.py` | P1's ID check, C1 and A1 as the order states them (design evidence; not shipped) | `825f6b5767932a782992d592a52db9745ed57f138839bdb667d8600de7940395` |
| `rehearsal-bom.yaml` | a rehearsal BOM in the new shape, written from ViewPrism2's entries for three E items and four units | `9c59c5c3917be45e648eaeb7fe57ad8c92b01603db2d5fe5edbec86c6d4e9de3` |
| `run_rehearsal.py` | runs `rehearse_part.py` on both products' real BOMs as they are and on the unchanged rehearsal BOM (3 baseline runs), and on the rehearsal BOM with one change per case (23: 4 allowed, 19 known-bad) | `0e82af844a780d2b755131e503a4404da1186cba2893e04f995b223e3238d4a8` |
| `rehearsal.txt` | its output | `cd0ecedf95d4356b07ba3a3e7dc4ae83442a929bef9e567a1957655fcc38e813` |

Commands (from this folder):

```
python measure.py ../../../../ViewPrism2 ../../../../ViewTube measurements.txt
(cd ../../../../ViewPrism2 && python bomdd/cp_results.py --json) > vp2-cp-results.json
python shapes.py ../../.. ../../../../ViewPrism2 ../../../../ViewTube shapes.txt
python -B run_rehearsal.py ../../../../ViewPrism2 ../../../../ViewTube rehearsal.txt
```
