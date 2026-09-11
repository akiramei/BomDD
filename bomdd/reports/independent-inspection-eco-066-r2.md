# 独立検査報告 — ECO-066 r2(Codex gpt-5.6-sol・CLI 直接・workspace-write・2026-09-11・対象 commit b39c6f7・範囲= r1 所見の是正確認+回帰)

> 検査官の最終メッセージをそのまま転記(受理側の判定は order §7.2)。

ACCEPT

IA-01〜04 はすべて是正済み。指定された CLI・差分位置・cleanup の回帰も確認でき、新規所見 IA-05 以降はありません。対象個体は `b39c6f739aa38626ba0068c3a18d8ca517d8003b`。以下の一時パスは `$TMP` と略記します。

### IA-01 — 全経路の1行目形式と CODE 語彙

実行:

```powershell
python bomdd-witness.py produce --eco ECO-T --gate g=0:fixture --out $TMP/out/valid.json
python bomdd-witness.py produce --eco ECO-T --stop BOGUS
# import 後に produce(..., gates=[{"name":"","exit":0,"source":"fixture"}], ...)
python bomdd-witness.py produce --eco ECO-T --gate g=0:fixture --out $TMP/repo/inside.json
python bomdd-witness.py produce --eco ECO-T --gate g=0:fixture --out $TMP/out/blocker/child.json
python method/tools/bomdd-witness.py --selftest
```

観測:

```text
RC=0 ADVANCE PRODUCED: witness 生成: ...valid.json(...)
RC=2 UNMEASURABLE ARG_ERROR: stop_type 不正: BOGUS(...)
RC=2 UNMEASURABLE GATE_INCOMPLETE: gate 不完全: gate.name が空
RC=2 UNMEASURABLE ARG_ERROR: witness を束縛対象の作業木内に置けない(...)
RC=2 UNMEASURABLE WITNESS_UNWRITABLE: witness を書けない: ...\blocker\child.json(FileExistsError)...
RC=0 ADVANCE OK: selftest PASS(...)
```

全行が次の形式に一致し、stderr は空でした。

```text
<VERDICT> <CODE>[(<CAUSE>)]: <message>
```

`CODES_COUNT=15`、観測した全 CODE は語彙内でした。

```text
OK, IDENTITY_MISMATCH, IDENTITY_UNCHECKED, TREE_MISMATCH,
GATES_MISSING, GATE_INCOMPLETE, GATE_FAIL, STOP_TYPE,
WITNESS_UNREADABLE, WITNESS_MALFORMED, TREE_UNAVAILABLE,
ARG_ERROR, PRODUCED, WITNESS_UNWRITABLE, SELFTEST_FAIL
```

判定: IA-01 是正確認。

### IA-02 — index 複製失敗と OS temp 不能の分離

実行:

```powershell
git init -q $TMP/badidx
New-Item -ItemType Directory $TMP/badidx/.git/index
python bomdd-witness.py verify $TMP/probe.json --eco ECO-T
```

観測:

```text
RC=2
UNMEASURABLE TREE_UNAVAILABLE(INDEX_COPY_FAILED):
現 tree を取得できない(PermissionError: ...\.git\index)...
```

`TemporaryDirectory` コンストラクタへ `PermissionError("simulated OS temp unavailable")` を注入した観測:

```text
RC=2
UNMEASURABLE TREE_UNAVAILABLE(TEMP_UNAVAILABLE):
現 tree を取得できない(PermissionError: simulated OS temp unavailable)...
```

判定: IA-02 是正確認。`INDEX_COPY_FAILED` と `TEMP_UNAVAILABLE` は分離されています。

### IA-03 — rc 127 と git 不在

`_git` を各サブコマンドだけ rc 127 に差し替えて `worktree_tree()` を実行しました。

```text
rc127-rev-parse:
tree=None cause=GIT_DIR_FAILED
detail='fatal: executable ran; rev-parse tail'

rc127-add:
tree=None cause=ADD_FAILED
detail='fatal: executable ran; add tail'

rc127-write-tree:
tree=None cause=WRITE_TREE_FAILED
detail='fatal: executable ran; write-tree tail'
```

PATH を空にした実 git 不在経路:

```text
git-absent-PATH-empty:
tree=None cause=GIT_UNAVAILABLE detail='git unavailable'
```

判定: IA-03 是正確認。起動済みプロセスの rc 127 は `GIT_UNAVAILABLE` に誤分類されません。

### IA-04 — UTF-8・置換読取り

ソースおよび `_git` 呼出しを捕捉した観測:

```text
_RUN_KW={
  'capture_output': True,
  'text': True,
  'encoding': 'utf-8',
  'errors': 'replace'
}
```

`_git` の subprocess 実行先を、stderr に `b'first\n\x81\xff tail\n'` を出す子プロセスへ差し替えました。

```text
_git-result:
rc=127
stderr='first\n�� tail\n'
tail='�� tail'

worktree-result:
tree=None
cause=GIT_DIR_FAILED
detail='�� tail'
```

例外・reader-thread traceback は出ず、末尾の `tail` が置換文字付きで保存されました。

判定: IA-04 是正確認。

### 指定回帰 — CLI 経路

独立 temp repo と witness で観測:

| 経路 | 観測 |
|---|---|
| `verify PATH --eco ECO-T` | `0 ADVANCE OK` |
| `verify PATH` | `2 UNMEASURABLE IDENTITY_UNCHECKED` |
| `verify --out PATH` | `2 UNMEASURABLE IDENTITY_UNCHECKED` |
| `verify PATH --eco ECO-X` | `1 STOP IDENTITY_MISMATCH` |
| `verify --eco ECO-MISSING` | `2 UNMEASURABLE WITNESS_UNREADABLE` |
| 引数なし | `2 UNMEASURABLE ARG_ERROR` |
| `verify` 単独 | `2 UNMEASURABLE ARG_ERROR` |
| `produce --eco` | `2 UNMEASURABLE ARG_ERROR` |
| 未知コマンド | `2 UNMEASURABLE ARG_ERROR` |
| PATH 空 | `2 TREE_UNAVAILABLE(GIT_UNAVAILABLE)` |
| 非 git directory | `2 TREE_UNAVAILABLE(GIT_DIR_FAILED)` |
| temp が作業木内 | `2 TREE_UNAVAILABLE(TEMP_IN_WORKTREE)` |
| 実 clean-filter 失敗 | `2 TREE_UNAVAILABLE(ADD_FAILED)` |
| `--selftest` | `0 ADVANCE OK` |

clean-filter は次を設定して実際の `git add -A` を失敗させました。

```powershell
git config filter.fail.clean command-that-does-not-exist-eco066
git config filter.fail.required true
```

観測:

```text
UNMEASURABLE TREE_UNAVAILABLE(ADD_FAILED):
現 tree を取得できない(fatal: bad.txt: clean filter 'fail' failed)...
```

最初の試行では `required=true` がなく Git が任意フィルタの失敗を許容したため、その結果は ADD_FAILED の証拠には採用していません。

### 指定回帰 — tree 差分位置

制御した40文字の現 tree に対する観測:

```text
短縮:   最初の差分位置 39
延長:   最初の差分位置 40
先頭差: 最初の差分位置 0
末尾差: 最初の差分位置 39
非文字列: 最初の差分位置 n/a(tree が文字列でない)
```

文字列の場合、witness/current の双方が省略されず出力されました。r1 で確認した境界値から変化はありません。

### `ignore_cleanup_errors=True`

cleanup 失敗を模した context manager を注入し、渡された引数と判定結果を観測しました。

```text
cleanup-probe:
tree_len=40
err=None
ignore_cleanup_errors=True
simulated_cleanup_suppressed=True
```

cleanup 抑止後も tree 判定は成功し、判定値への影響はありませんでした。実 OS の権限故障ではなく、cleanup 失敗注入による確認です。

### 差分・作業木

実行:

```powershell
git diff --check 4068029 -- method/tools/bomdd-witness.py
git diff --numstat 4068029 -- method/tools/bomdd-witness.py
git status --porcelain=v1
git rev-parse HEAD
```

観測:

```text
DIFF_CHECK_RC=0
98  45  method/tools/bomdd-witness.py
STATUS_BEGIN
STATUS_END
b39c6f739aa38626ba0068c3a18d8ca517d8003b
```

リポジトリ内のファイルは作成・変更・削除していません。`self-conformance.py` は PASS witness を `.git` に書くため、今回の読み取り専用条件では実行していません。

較正判定: 指定範囲の主張「IA-01〜04 が是正され、指定回帰がない」は `observed・適格`。計器欠陥の追加検出なし。Q1〜Q7・Q9〜Q11=`asked`、Q8=`NA`。検出力の限界は、実 git バイナリ自身からの非 UTF-8 出力ではなく `_git` subprocess 経路への raw-byte 子プロセス注入である点、および cleanup 故障が注入である点です。