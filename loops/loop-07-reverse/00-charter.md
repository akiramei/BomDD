# Loop 7 憲章 — リバース工程の形式化(CHEAT-001)

三層BOMは一周した。残る CHEAT-001 は**入口保証**=「原版から BOM をどう漏れなく起こすか」。
全アプリを読む実験にはせず、**Export seek/audio 経路**で形式化する(CHEAT-008/K-BOM/L2-L3/S-BOM が全て繋がる経路)。

## 工程の定義(完全読解ではない)
> 原版から BOM を起こす工程は、完全な読解ではなく、
> 「**観測ソース → REQ → E-BOM/K-BOM → M-BOM/Control Plan → 治具**」の双方向トレースを作り、**未トレースを明示する**工程である。

## 成果物(薄い)
- [01-source-inventory.md](01-source-inventory.md) — 原版証拠の棚卸し
- [02-reverse-routing.md](02-reverse-routing.md) — リバース工程の手順
- [03-trace-matrix.md](03-trace-matrix.md) — 双方向トレース(中核)
- [04-coverage-audit.md](04-coverage-audit.md) — カバレッジ監査+マルチファクトリ・リバースの差分
- [report.md](report.md)

## マルチファクトリ・リバース(リバース装置の検証)
同じ原版 seek/audio 実装を**複数リーダー(opus/sonnet/haiku)**に読ませ、抽出 REQ の差分を測る。
**差分が出た場所 = 仕様として自然に読めない場所 = リバース工程の弱点**(Loop4 製造ばらつきのリバース版)。

## 成功条件(「全部読めた」ではない)
1. 原版証拠 → REQ/E-BOM/M-BOM/Control Plan へ**片方向に辿れる**。
2. 各 BOM部品・AC・治具 → 原版証拠へ**逆引きできる**。
3. 未トレースの原版要素を `out-of-scope / unknown / ignored-with-reason` に**分類できる**。
4. 既知の危険点(特に **CHEAT-008 級=座標系**)が **FMEA と L3 受入**へ到達する。
