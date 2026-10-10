[INFORM / COMPLETE]

REJECT IA-01

- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- HEAD at start / at end: fab10e10ed6f6488a2c51ef70058b325aebe469e / fab10e10ed6f6488a2c51ef70058b325aebe469e
- commit: 0 / ファイル変更: 0
- 写しの sha256 の照合: 一致
  - `viewtube-r8.txt`: `956f3283993fc2618358d437bc5870cba52c2e9a35b544366e8ba623da536a48`
  - `viewprism2-r8.txt`: `872454cd8e0d9c502e8e084fcc20ae0ee6f4f4800b9b5a0ba7d9774b75ee402d`

## 項目ごとの判定

| # | 項目 | 判定 | 根拠(file:line・コマンドと出力の要点) |
|---|---|---|---|
| 1 | 範囲 | PASS | `git diff --stat/name-only c41838a..fab10e1` は order、reports 2 ファイル、配布キット 3 ファイルのみで、すべて ECO-103 `allowed_paths` 内。`git diff --unified=0` は `change-management.md` が `@@ -48,0 +49,10` のみ、`operator-layer.md` が `@@ -109 +109` のみ、`eco-fix.md` が description と `@@ -34,0 +35,5` のみ。R1〜R7、§0・§1・§3〜§5、operator-layer §4、ECO-079 の受入証拠段落に差分なし。 |
| 2 | V1・V2 の句 | PASS | `change-management.md:49-58` に V1 の 7 句、`eco-fix.md:35-39` に V2 の 3 句あり。PyYAML で frontmatter を読み込み、`name` と `description` を取得し、description に `R8` あり。 |
| 3 | 記録との一致 | FAIL（blocking、IA-01） | 写しの SHA-256 は `measurements.txt` と一致。order §0.1〜0.5 の欠落、7件、24件、独立性3軸などは記録と一致。ただし `method/improvements.md:8512` は両製品が「保護パスに触れる変更」を同じ規則の対象にしたと記述する一方、ViewPrism2 写しが支えるのは `src`、ViewTube 写しが支えるのは `product-source` である。BomDD R8 の保護パスは `src/` と `test/` (`change-management.md:49`)なので、少なくとも ViewPrism2について `test/` まで含む主張は写しにない。V4 の「記録より強い主張を含まない」を満たさない。 |
| 4 | 既存の規則との整合 | PASS | R8 は文脈の独立と設備の独立を明示的に分離し、設備の独立を `operator-layer.md` §4へ委譲。`inspector` を設備の独立に限定する記述は §4・§5の配員契約と両立する。R3/R5への処置、R4の2関門維持、高リスク治具の異系統性、自己査定の限界、golden非代替、ECO-077の不採用事項、ECO-079の段落との矛盾なし。 |
| 5 | 配布の健全性 | PASS | `bomdd-init.py:320-324` は change-management と operator-layer を同じ `bomdd/` に配置し、eco-fix を `.claude/skills/eco-fix/SKILL.md` に配置する。R8 の `operator-layer.md` §4参照は配布先で解決する。追加行に新規 `{{…}}` なし。 |
| 6 | 言い回し | FAIL（non-blocking、IA-02） | 範囲、時点、R5/R3への処置は R8 (`change-management.md:49-51`) と手順3.6 (`eco-fix.md:35-39`) で一致。「文脈の独立」「設備の独立」も定義により区別可能。ただし「文書のみ・機械的な1行変更」は「文書のみ、または機械的な1行変更」という2類型か、「文書のみで、かつ機械的な1行変更」という1類型か一意でない。 |

## 所見(IA-01, IA-02, …)

- IA-01 — blocking  
  該当: `method/improvements.md:8512`  
  「ViewTube と ViewPrism2 が、保護パスに触れる変更を別の新しい文脈で見直す同じ規則を置いた」とする主張のうち、ViewPrism2 写しが示す範囲は `src` のみで、BomDD が保護パスとして加えた `test/` は示されていない。  
  例えば「ViewTube と ViewPrism2 は、製品コードの変更を別の新しい文脈で見直す規則をそれぞれ置いていた。対象範囲の表記は ViewTube が product-source、ViewPrism2 が src」のように境界を保持する必要がある。

- IA-02 — non-blocking  
  該当: `change-management.md:52`、`skills/eco-fix.md:39`  
  「文書のみ・機械的な1行変更」の論理関係が曖昧。「文書のみ、または機械的な1行変更」か「文書のみ、かつ機械的な1行変更」かを明記すると、「R8 対象外」の自己宣言範囲が一意になる。

## 検査しなかったこと(限界)

- 指示に従い、ビルド、self-conformance、worklist、`accept103.sh` その他の検査器は実行していない。
- 外部 API、ViewTube、ViewPrism2 のリポジトリは参照していない。外部リポの HEAD、origin 比較、commit `c49286a` の実在は、保存された `measurements.txt` と写しの範囲でのみ評価した。
- CI の状態は確認していない。
- 開始時から存在した未追跡ファイル `bomdd/reports/eco-103-r8-independent-review/inspection-brief-r1.md` は読み書きしておらず、終了時にも同じ状態だった。