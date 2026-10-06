[INFORM / COMPLETE]

REJECT

- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- HEAD at start / at end: `9212e719145a02cedad280bc17bea04a83641ba2` / `9212e719145a02cedad280bc17bea04a83641ba2`
- commit: 0 / ファイル変更: 0
- 写しの sha256 の照合:
  - `viewtube-32-mbom-invariant-entries.txt`: 一致 — `2cedc20320f67fe08fc34e5333624a7198b42b57b248897f21a0455fb5c20f42`
  - `viewtube-33-known-limits-lines.txt`: 一致 — `53e08aacfc864bd77acb220eb06c5fecb1b6b8d61876b3d88286d3ebcecb4bb0`
  - `viewtube-31-kbom-measured-lines.txt`: 一致 — `ea5429c6982d6b125a55268a4ff19f2336618694208ca299639f491df732f413`

## 項目ごとの判定

| # | 項目 | 判定 | 根拠(file:line・コマンドと出力の要点) |
|---:|---|---|---|
| 1 | 範囲 | PASS | `git diff --name-only 37c4f82..9212e71` の13ファイルは、`60-change-register.yaml:3249` の `allowed_paths` 内だけ。playbook の hunk は `@@ -348` と `@@ -356`、ともに §4.5 内。§4.4・§9・§13 に差分なし。 |
| 2 | V1 の句 | PASS | `method/bomdd-playbook-v1.md:341-360` を対象に文字列計数。6句は順に `1 / 1 / 3 / 1 / 1 / 1` 件、`置き場は**未決**` は0件。candidate 表示は同ファイル `:344` に維持。 |
| 3 | 記録との一致 | **FAIL (blocking)** | r2 の数値 `60 / 60 / 11 / 36 / 2 / 14` は `measurements.txt:13-20` と全項目写しに一致し、K-BOM 2行も `:64-68` と写しに一致。しかし、order `:27,33`、playbook `:350`、improvements `:8426` の「実測値・所見の正本はECO本文と台帳が既に持つ」、特に order の「4種すべてを毎回持つ」は、`measurements.txt` に対象ファイル、該当行、計数、写しがない。また、playbook `:351` の「ViewPrism2 は由来の参照だけ」は `measured=0 / ECO-=138` という語数だけでは排他的な「だけ」を立証しない。 |
| 4 | 既存本文との整合 | PASS | `known_limits` は33テンプレ `:47-49` で「この検査行が測っていない経路・条件」に限定され、§4.4 `:170-176` の `requirement_refs` / `invariant_refs` による結線を置換しない。変更記録を正本、M-BOMを参照とする形は§13 `:1142-1147` の第二宣言・静的転写の抑制と整合。50テンプレ `:32-39` の `test_evidence_refs` は個体に対する再測定結果であり、記録句の正本とは役割が重ならない。ECO-086/098/100由来のcandidate規則とも矛盾なし。 |
| 5 | テンプレの健全性 | PASS | 許可された `yaml.safe_load` を各1回実行し `32: OK`、`33: OK`。`git diff --numstat` は32が `+2/-1`、33が `+3/-0`。変更はコメントと `known_limits: []` のみ。新欄は `characteristics` の通常検査行内 (`33-control-plan.yaml:47`) にあり、表示パリティ例にはない。表示パリティ例も必要時に同じ欄を追加できるため、例の簡潔さを保つ判断として妥当。 |
| 6 | 言い回し | PASS | `playbook:348` で局所名「M-BOM の記録句」を定義し、ECO-100 IA-01に回答している。対象が「M-BOMの行に混入した4種の句」と一意に読め、§8.5や§13の一般的な「記録」と区別できる。 |

## 所見(IA-01, IA-02, …)

- IA-01 — **CLOSED**  
  r1のblocking所見。3写しすべてについて、今回の独立計算値が `measurements.txt:72-75` のsha256と一致した。

- IA-02 — **CLOSED**  
  r1のblocking所見。`viewtube-32-mbom-invariant-entries.txt` は60項目の全物理行422行を収録し、`measurements.txt:13-20` は項目単位で `60 / 60 / 11 / 36 / 2 / 14` を記録している。先頭行だけの写しによる再計数不能は解消した。

- IA-03 — **CLOSED**  
  r1のblocking所見。`viewtube-31-kbom-measured-lines.txt` に該当2行の全文があり、いずれも知識の名称・一般文で、日付・観測値・対象版を持つ実測記録ではないという限定された主張と一致する。

- IA-04 — **CLOSED / non-blocking**  
  r1所見。製造物はorder §4の記載どおりで、変更行はplaybook §4.5、32のコメント、33の欄とコメントに限定される。

- IA-05 — **blocking・中核根拠の記録欠落**  
  該当: `bomdd/60-change-order-eco-102.md:27,33`、`method/bomdd-playbook-v1.md:350`、`method/improvements.md:8426`。  
  「ECO本文と台帳が実測値・レビュー所見の正本を既に持つ」、さらにorderの「4種すべてを毎回持つ」は置き場の決定を直接支える事実だが、r2の `measurements.txt` と3写しに照合可能な根拠行がない。例示されたECO-VT-232の該当節・台帳行の写し、または対象集合と計数が必要。

- IA-06 — **blocking・記録より強い排他的表現**  
  該当: `method/bomdd-playbook-v1.md:351`。  
  記録が示すViewPrism2の事実は `measured` 0件と `ECO-` 138件だけである。「由来の参照だけ」は、他の実測表現や記録句がないことまで含む排他的主張であり、この2語のgrepだけでは立証できない。M-BOM全項目の写しか、記録句の語彙・構造を網羅した計数が必要。

## 検査しなかったこと(限界)

- `self-conformance`、worklistその他の検査器・ビルドは実行していない。
- 外部APIは呼んでいない。
- ViewTube / ViewPrism2 のリポジトリは読んでいない。BomDD内の測定記録と写しだけを使用した。
- CI、製品コードの動作、既存製品への適用効果は検査していない。
- `git diff --check` は実行したが、報告として保存されたr1文書のMarkdown行末空白だけを検出した。本検査の6項目および製造物の意味論には帰属させていない。