[INFORM / COMPLETE]

ACCEPT

- range: 境界探索
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象 revision: f34a6d6e7555ef912bbd516872667fb0c64cd07e
- commit: 0
- 外部 API: 呼出しなし
- 読んだファイル一覧: `bomdd/60-change-order-eco-096.md` §0・§1・§3・§4・§5、`bomdd/60-change-order-eco-092.md` §4・§6、`method/tools/bomdd-witness.py`、`.github/workflows/self-conformance.yml`、`bomdd/60-change-register.yaml`
- 開始時 `git status --short`: 空
- 開始時 S・h entry 数: 0
- 終了時 `git status --short`: 空
- 終了時 S・h entry 数: 0
- 終了時 revision: f34a6d6e7555ef912bbd516872667fb0c64cd07e
- 本リポの `.git/index`: 操作なし。前後の作業木状態に変化なし

注: PowerShell の case-insensitive な `-match` では通常 entry の `H` 1161 件を誤算入したため破棄した。指定式と同義の case-sensitive `-cmatch '^[Sh]'` では 0 件。開始時の `rg -c` 無出力とも整合する。

## 判定概要

| 条件 | 判定 | 観測 |
|---|---|---|
| V1 | PASS | `python method/tools/bomdd-witness.py --selftest` は exit 0、1 行目 `ADVANCE OK:`。`_normalize_index_flags` を no-op に差し替えると exit 1、`STOP SELFTEST_FAIL: 3 件`。skip-worktree、assume-unchanged、正規化失敗の各腕が発火した。 |
| V2 | PASS | 隔離リポのフラグ 0 件状態で、是正前経路と `worktree_tree` は同一 tree `9c897ccb1b1baad147f4cc798b2d4788ba079ecb`。実 index 不変。 |
| V3 | PASS | 自環境は S/h 0 件のため隔離リポで代替。index=不正 bytes、S、worktree=正しい bytes とし、是正前は index blob、是正後は worktree blob。サブディレクトリ、空白、非 ASCII の3例で確認。実 index 不変。 |
| V4 | PASS | `_normalize_index_flags(..., ["no-such-file"])` は `(False, "update-index --no-assume-unchanged 失敗(exit 128・1 件)…")`。失敗注入した `worktree_tree` は `INDEX_NORMALIZE_FAILED`、`produce` は exit 2、1行目は `UNMEASURABLE TREE_UNAVAILABLE(INDEX_NORMALIZE_FAILED): ...`。 |
| V5 | PASS | 窓の5パスは全て ECO-096 `allowed_paths` 内。workflow は追加2行（コメント1、実行1）。selftest は `fast` の ubuntu/windows matrix 内で、`dotnet` job にはない。 |
| 実 index 不変 | PASS | 全隔離境界腕で index の状態を前後比較。本リポでは index 操作なし。 |
| 判定基準 | PASS | 宣言済み sparse-checkout 限界以外に、作業ツリーと異なる bytes の束縛または実 index の変更を発見せず。 |

## 境界探索の表

| 入力クラス | 入力 | 期待 | 実測 | 所見 |
|---|---|---|---|---|
| assume-unchanged のみ | `sub/a.txt`、index≠worktree、`h` | 新=worktree、旧=index | 期待どおり。tree は反転、実 index 不変 | PASS |
| 両フラグ | assume-unchanged後にskip-worktree、小文字 `s` | 新=worktree、旧=index | 期待どおり。実 index 不変 | PASS |
| 複数・サブディレクトリ | 3ファイル、うち `sub/a.txt` | 全対象を正規化 | 全対象で新=worktree、旧=index | PASS |
| 空白パス | `sp ace.txt` | NUL区切りで完全に扱う | 新=worktree、旧=index | PASS |
| 非ASCIIパス | `jp-日本.txt`相当 | NUL区切りで完全に扱う | 新=worktree、旧=index | PASS |
| 作業ツリー削除+S | `f.txt` を削除、temp indexでS解除 | 新treeから削除、旧treeにはindex blob | `add -A` 後は `D  f.txt`、新treeにはpathなし。旧treeにはpathあり | PASS |
| 未追跡 | `u.txt` | 是正前後とも追加 | 両treeに存在、同一 | PASS |
| `.gitignore` | `ignored.txt` | 是正前後とも除外 | 両treeから除外 | PASS |
| intent-to-add | `git add -N ita.txt` | `add -A` で内容を束縛 | 是正前後同一、treeに存在 | PASS |
| staged削除 | `base.txt` を削除し `git add -u` | 両treeから削除 | 是正前後同一、pathなし | PASS |
| フラグ0件 | cleanな隔離リポ | 是正前後同一 | tree `9c897ccb…` で一致 | PASS |
| produce→verify | S付き、index≠worktree | 不変ならADVANCE | `ADVANCE OK` | PASS |
| produce後のworktree変更 | Sを残して内容変更 | TREE_MISMATCH | `STOP TREE_MISMATCH` | PASS。旧経路のtreeはindex側に固定されるため、この変更を識別しないことも対照腕で確認 |
| 2オプション同時指定 | `--no-assume-unchanged --no-skip-worktree -z --stdin` | Git 2.47でSが残る | exit 0かつ `S f.txt` のまま。逆順でも同じ | 製造者主張を独立再現。別呼出しが必要 |
| 正規化失敗 | indexにないpath | `(False, update-index失敗…)` | exit 128を理由付きで返した | PASS |
| 原因語彙 | `INDEX_NORMALIZE_FAILED` | `TREE_CAUSES`に存在し1行目へ写像 | 存在し、`(...INDEX_NORMALIZE_FAILED)` と表示 | PASS |
| 語彙外を弾く経路との整合 | selftestの語彙検査 | 新原因が既知語彙として受理される | selftest PASS。原因存在の明示腕あり | PASS |
| CI結線 | workflow fast matrix | ubuntu/windowsで実行 | `fast` matrix内に実行行あり | PASS |
| dotnet job | selftest不要 | 結線なし | 結線なし | PASS |
| CI副作用 | selftest実装読解 | OS tempのみ | `TemporaryDirectory` 配下の隔離リポ・出力を使用 | PASS |

## 自己検証の張り損ない4類型

| 類型 | 査定 | 観測 |
|---|---|---|
| meta-failure | 穴なし | 正常selftestだけでなく、正規化no-op変異で3腕が赤転した。 |
| 未検枝 | 穴なし | S、h、両フラグ、複数、特殊パス、削除、失敗経路を境界探索で補完した。 |
| 存在 vs 完全性 | 穴なし | 語彙の存在だけでなく、失敗原因から `report_line` までの写像を実測した。 |
| 副経路 | 穴なし | `worktree_tree` 単体に加え、`produce→verify` 往復と変更後の `TREE_MISMATCH` を実測した。CI結線も確認した。 |

## 所見

blocking / non-blocking ともになし。

## 範囲外の観察（判定に含めない）

- fast tierの `self-conformance.py` 全体は、ブリーフで既知とされた検査官sandboxのC14 REAL差を判定に使わないため実行していない。
- CIの外部状態は、外部API禁止および本roundのV6・V7範囲外のため照会していない。
- sparse-checkout外pathでindex≠HEADの場合の限界は、orderと実装コメントに既知の限界として明示されており、本判定はその対応を支持しない。