[INFORM / COMPLETE]

REJECT

- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- HEAD at start / at end: `78f96509474b16daf2bedf09625203cea1319c37` / `78f96509474b16daf2bedf09625203cea1319c37`
- commit: 0 / ファイル変更: 0
- 写しの sha256 の照合:
  - `viewtube-32-mbom-invariant-lines.txt`: 不一致（算出値 `3c957d1aaeefc38d4ab1b719edfcf22d647e1a60ce194e4aa455c806e54cdf6e`、`measurements.txt` に対応値なし）
  - `viewtube-33-known-limits-lines.txt`: 不一致（算出値 `53e08aacfc864bd77acb220eb06c5fecb1b6b8d61876b3d88286d3ebcecb4bb0`、`measurements.txt` に対応値なし）

## 項目ごとの判定

| # | 項目 | 判定 | 根拠(file:line・コマンドと出力の要点) |
|---|---|---|---|
| 1 | 範囲 | PASS | `git diff --stat 37c4f82..78f9650` は order、playbook、32、33 の4ファイルだけで、すべて `60-change-register.yaml:3245` の `allowed_paths` 内。playbook の `-U0` hunk は旧L348とL356の2個で、いずれも §4.5（現L341–360）内。§4.4・§9・§13に差分なし。 |
| 2 | V1 の句 | PASS | `method/bomdd-playbook-v1.md:348-359`。6句の件数は順に `1 / 1 / 3 / 1 / 1 / 1`、`置き場は**未決**` は0。見出しL344は引き続き `candidate`。 |
| 3 | 記録との一致 | FAIL（blocking） | `measurements.txt:5-12` は測定元ファイルのhashのみで、L90-91の写し2本にはhashを記録していない。さらに M-BOM 写し60行を再計数すると ECO開始60は一致する一方、`measured=0`（記録21）、review/round/finding=26（95）、未検査語=0（6）、ruling=14（15）。写しが先頭行だけを抽出し、主張の根拠となる継続行を欠くため独立突合不能。K-BOMも `measurements.txt:85-89` は `measured=2` を示すだけで「実測の記録を入れた例は無い」という解釈根拠がない。 |
| 4 | 既存本文との整合 | PASS | §4.4 L170-176の結線は `requirement_refs` / `invariant_refs`、新欄は検査行自身の非被覆の説明で役割が異なり衝突なし。§13 L914以降の記録経済と「正本一つ・他は参照」は整合。50テンプレL32-33の `test_evidence_refs` は個体別の再測定証跡で、変更記録や `known_limits` と重複しない。ECO-086/098/100のcandidateとも正面矛盾なし。 |
| 5 | テンプレの健全性 | PASS | 指定の `yaml.safe_load` を32・33それぞれに実行し両方 `OK`。`git diff` では32はコメント1行→2行、33はコメント2行と `known_limits: []` だけ。新欄は `characteristics` の検査行、`test_vectors` の直後（33:L47）にあり、表示パリティ例には追加されていない。candidateの局所導入として妥当。 |
| 6 | 言い回し | PASS | `method/bomdd-playbook-v1.md:348` で「M-BOM の記録句」を括弧内の4種とともに局所定義し、ECO-100 IA-01へ明示的に応答。L349で未検査注記だけを例外として分離しており、一意に読める。 |

## 所見(IA-01, IA-02, …)

- IA-01 — **blocking・証拠完全性**  
  該当: `bomdd/reports/eco-102-record-clause-home/measurements.txt:5-12,90-91`、order L56・L68・L90。  
  orderは写しを「sha256つき」と主張するが、記録されているhashは元ファイル群だけで、写し2本のhashがない。したがって、現在の写しが測定時の写しであることを記録と照合できない。

- IA-02 — **blocking・写しの被覆不足**  
  該当: `viewtube-32-mbom-invariant-lines.txt`、`measurements.txt:23-41`。  
  写しは `^    - '` に一致する不変条件の先頭行だけで、M2–M5が数えた継続行を含まない。独立再計数は `measured 0≠21`、review等 `26≠95`、未検査語 `0≠6`、ruling `14≠15`。数値が偽と確定したのではなく、指定された写しでは数値を裏取りできない。V3を満たさない。

- IA-03 — **blocking・記録より強い主張**  
  該当: order §0.2 L28、playbook L351、improvements.md L8426、`measurements.txt:85-89`。  
  「K-BOMに実測の記録を入れた例は無い」に対し、記録は `measured` が2件あることまでしか示さず、その2件を「実測の記録ではない」と分類する根拠行の写しがない。現記録からは当該全称主張を支持できない。

- IA-04 — **non-blocking・製造物と本文の整合**  
  §4.5、32、33の変更内容はorder §4の記述と一致し、candidate表示、未測定、効果非主張、既存製品への非遡及を維持している。blocking所見は設計内容ではなく、受入用証拠の欠落に帰属する。

## 検査しなかったこと(限界)

- 禁止に従い、ViewTube / ViewPrism2 リポは読んでいない。
- `self-conformance.py`、worklist、ビルド、CI、外部APIは実行していない。
- `measurements.txt` に記録された外部作業木のHEAD・clean状態・コマンド実行の真正は再実行していない。
- YAML確認は許可されたPyYAML `safe_load` の2本だけ。
- 本検査は現在の製造commitの受入可否であり、記載方式の将来効果や他製品への一般化を評価していない。

human_action: none。独立検査は完了し、証拠連鎖のblocking 3件によりREJECT。