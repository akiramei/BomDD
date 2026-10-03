[INFORM / COMPLETE]

REJECT IA-01, IA-02

- range: 境界探索
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象 revision: 5d90ba4839d7ab7c6350efae0f3af18a115b9ca7
- commit: 0
- 外部 API: 呼出しなし
- リポ内ファイル作成・変更・削除: 0
- 本リポ `.git/index` 操作: 0
- 読んだファイル一覧:
  - `bomdd/60-change-order-eco-092.md` §0・§1・§3・§4
  - `method/tools/self-conformance.py` の ECO-092 対象実装
  - `bomdd/hooks/pre-push`
  - `bomdd/60-change-register.yaml` の ECO-091〜093 `allowed_paths`
  - `method/templates/product-profile/skills/handoff.md`
- 読んだ差分:
  - `git diff 246c2fd..5d90ba4839d7ab7c6350efae0f3af18a115b9ca7 -- method/tools/self-conformance.py bomdd/hooks/pre-push`
  - `git diff --stat 069e0d5 5d90ba4839d7ab7c6350efae0f3af18a115b9ca7 -- bomdd/hooks/`
  - `git diff --name-only 069e0d5 5d90ba4839d7ab7c6350efae0f3af18a115b9ca7`

開始時:

- `git rev-parse HEAD`: `5d90ba4839d7ab7c6350efae0f3af18a115b9ca7`
- `git status --short`: 出力なし
- `git ls-files -v | grep -c '^[Sh]'` 相当: `0`

終了時:

- `git rev-parse HEAD`: `5d90ba4839d7ab7c6350efae0f3af18a115b9ca7`
- `git status --short`: 出力なし
- `git ls-files -v | grep -c '^[Sh]'` 相当: `0`

## 判定概要

| 条件 | 判定 | 観測 |
|---|---|---|
| V1 | PASS | 本番出力は `[C18] PASS witness 較正 skip-worktree 腕(tree の blob= 作業ツリー・実 index 不変)=True・対照腕=True・失敗腕(書かない)=True`。独立隔離リポでも `S f` のまま、返却 tree の blob は worktree の `hash-object` と一致し、`ls-files -s/-v`・status は前後不変。 |
| V2 | PASS | 本リポのフラグ 0 件状態で、是正前経路と `_witness_tree` は同一 tree `dbaba17fd20a7114aec5b269ab27c31fb987ce0e`。実 index・status 不変。 |
| V3 | PASS | 破損 index で `(None, why)`。stale witness は削除され、stdout・stderr の双方に同一の `[witness] 書出し省略(判定不変・証明しない・ECO-092): …` 行が出た。 |
| V4 | PASS | `bomdd/hooks/` の diff stat は空。正常な隔離リポで witness は `<40桁tree>\nPASS\n`、LF 2 個・CR なし。hook 本体は不変。 |
| V5 | FAIL | `python method/tools/self-conformance.py` は C18 PASS だが、C14 `kit-freshness` の `REAL` 腕が FAIL、最終 exit 1。また diff に ECO-091〜093 の `allowed_paths` 外の2パスが存在。 |
| C18対象実装 | PASS | 探索した通常・フラグ付き入力では、sparse-checkout を除き「検査対象 worktree と異なる bytes の証明」および実 index の変化は見つからなかった。 |

`python method/tools/self-conformance.py` の主要観測:

- `[C14] FAIL kit-freshness 対照実測(FRESH/STALE/UNKNOWN/TAMPERED/余剰/入力不正/実 scaffold = 6/7) — 失敗: ['REAL']`
- `[C18] PASS witness 較正 … True・対照腕=True・失敗腕=True`
- `[C18] PASS pre-push witness 設置(…witness 突合=True)`
- `[cleanup] 残置 0 件`
- `self-conformance FAILED — 1 件の不適合`
- exit code: `1`

## 境界探索の表

| 入力クラス | 入力 | 期待 | 実測 | 所見 |
|---|---|---|---|---|
| skip-worktree | index=`bad`、`S f`、worktree=`good` | tree は worktree bytes | 一致 | PASS。index・タグ・status 不変。 |
| assume-unchanged | `h assume` | tree は worktree bytes | 一致 | PASS。 |
| 両フラグ | 小文字 `s both` | 両フラグを外して worktree bytes | 一致 | PASS。 |
| 複数・サブディレクトリ | 5ファイル、`sub/a` を含む | 全件を正規化 | 全件一致 | PASS。`フラグ正規化 5 件`。 |
| 空白パス | `space name` | NUL 区切りで正しく処理 | 一致 | PASS。 |
| 非ASCIIパス | `日本語` | NUL 区切りで正しく処理 | 一致 | PASS。 |
| worktree 削除+S | index に `gone`、worktree から削除 | tree から削除 | tree に不在 | PASS。index は不変。 |
| 未追跡 | `untracked` | 是正前後で同じ | 両方 tree に追加 | PASS。 |
| `.gitignore` | `ignored` | tree に入れない | 不在 | PASS。 |
| intent-to-add | `git add -N ita` | 是正前後で同じ | 両方 tree に追加 | PASS。 |
| staged削除 | `git rm --cached cached`、worktreeには存在 | 是正前後で同じ | 両方 tree に再追加 | PASS。 |
| 非git root | 通常ディレクトリ | `(None, why)` | `ls-files 失敗(exit 128)` | PASS。 |
| init直後・index不在 | 空の新規gitリポ | 実測 | 空treeを正常返却 | `4b825d…`。現在の空worktreeを正しく表すため、失敗扱いにはならない。 |
| 破損index | index=`garbage` | `(None, why)` | `ls-files 失敗(exit 128)` | PASS。 |
| merge conflict | 未解決 conflict | 実測 | `add -A` が一時index上で解消し、treeを返却 | 実 index 不変。自然な `write-tree` 失敗腕にはならなかった。 |
| write-tree失敗 | `write-tree` に exit 17 を注入 | `(None, why)` | `write-tree 失敗(exit 17)` | 分岐を確認。実 index・status 不変。 |
| sparse-checkout | `keep/` のみ展開、`outside/b` は `S` | order宣言では outside を削除 | outside は返却treeに残った | IA-03。宣言と不一致だが、本roundの明示的な除外対象。 |
| 2オプション同時指定 | `--no-skip-worktree --no-assume-unchanged` | 製造者主張の再現 | rc 0、タグ `S` が残り、treeはindex bytes | 製造者の発見を独立再現。別呼出し実装は妥当。 |
| 実index不変性 | 上記各腕 | `-s/-v/status` 前後一致 | 全腕一致 | PASS。 |

## 自己検証の4類型

| 類型 | 観測 | 判定 |
|---|---|---|
| meta-failure | 全体検査が別条件 C14 で赤でも、C18 較正は実行され3腕の結果を表示した | C18 の自己検証は張られている。ただし V5 は満たさない。 |
| 未検枝 | 恒久較正は主に skip-worktree・対照・非git。assume-only、両フラグ、削除、特殊パス、sparse、writer失敗は恒久腕外 | 独立探索では通常境界は合格。sparse宣言だけ実測と不一致。 |
| 存在 vs 完全性 | 較正行の存在だけでなく、blob一致・実index不変・失敗時削除と二重出力を個別に実測 | 対象契約の主要部分は完全性まで確認。 |
| 副経路 | hook不変と witness形式を確認。`bomdd-witness.py` は凍結範囲外 | 対象経路に新たな欠陥なし。範囲外副経路は判定に含めない。 |

## 所見

### IA-01 — blocking — V5: 必須検査が非0終了

再現コマンド:

```text
python method/tools/self-conformance.py
```

期待:

```text
全検査 PASS、exit 0
```

実測:

```text
[C14] FAIL kit-freshness … 失敗: ['REAL']
self-conformance FAILED — 1 件の不適合
exit 1
```

帰属:

- 対象 revision の V5。
- C18 対象機能自体は PASS。
- 検査官は役割外のため原因調査・是正を行っていない。

### IA-02 — blocking — V5: diff が ECO-091〜093 の allowed_paths 外

再現コマンド:

```text
git diff --name-only 069e0d5 5d90ba4839d7ab7c6350efae0f3af18a115b9ca7
```

期待:

```text
register の ECO-091〜093 allowed_paths の和集合内のみ
```

実測した範囲外パス:

```text
bomdd/60-change-order-eco-094.md
bomdd/reports/eco-094-upstream-sbom-trial/preregistration.md
```

帰属:

- 指定された比較窓 `069e0d5..5d90ba4` と対象 revision。
- ECO-094 自体の正当性は本検査の役割外だが、凍結された V5 の文字どおりの条件には不適合。

### IA-03 — non-blocking — sparse-checkout の限界宣言と実測が不一致

再現要旨:

```text
git sparse-checkout init --cone
git sparse-checkout set keep
_witness_tree(repo, repo/".git")
```

期待（order §1・§4 の宣言）:

```text
sparse外の outside/b は削除としてtreeに記録される
```

実測:

```text
worktreeには outside/b がない
実indexタグは S outside/b
返却treeには outside/b が残る
実index・statusは不変
```

帰属:

- `git add -A` は sparse-checkout の適用範囲を尊重し、フラグを一時indexで外した後も sparse外パスを削除しなかった。
- order の限界説明は実挙動と一致しない。
- 本ブリーフが sparse-checkout を明示的に REJECT 基準から除外しているため、non-blocking とした。

### IA-04 — non-blocking — merge conflict は write-tree失敗腕にならない

再現要旨:

```text
未解決merge conflictを作成
_witness_tree(repo, repo/".git")
```

期待候補:

```text
一時indexに未解決entryが残り write-tree が失敗
```

実測:

```text
一時indexへの git add -A が conflict をworktree内容で解消し、write-treeは成功
```

補足:

- `write-tree` の非0分岐は exit 17 の注入で `(None, "write-tree 失敗…")` を確認した。
- 実index・タグ・statusは前後不変。
- 実装欠陥ではなく、ブリーフ記載例がこの処理順では自然な失敗腕にならないという所見。

## 範囲外の観察（判定に含めない）

- `method/tools/bomdd-witness.py` の同型機序は、ブリーフの指示に従い検査・判定対象にしていない。
- self-conformance の C14 `REAL` 失敗原因は調査していない。
- ECO-094 の内容・正当性は調査していない。
- 一時リポは OS temp 下だけに作成した。本リポの追跡ファイルおよび `.git/index` は開始時から不変。

human_action: none。検査は REJECT として完了し、未実施項目はない。