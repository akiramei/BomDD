# 独立検査報告 — ECO-066 r1(Codex gpt-5.6-sol・CLI 直接・workspace-write・2026-09-11・対象 commit 4068029)

> 検査官の最終メッセージをそのまま転記(受理側の真正判定は order §7)。ブリーフ= 製造者作成・正本委譲(order・register・製造物のパス)。

REJECT（IA-01、IA-02、IA-03）

独立 fixture はすべて OS 一時領域に作成・消去した。最終 `git status --porcelain=v1` は出力なしで、リポジトリは変更していない。

### IA-01 — 固定報告形式が全 CLI 経路には適用されていない

[run_cli](/C:/Users/akira/source/repos/BomDD/method/tools/bomdd-witness.py:280) の `produce` 分岐は `report_line()` を通さず、生の `produce()` メッセージを返す。`--selftest` も [_report](/C:/Users/akira/source/repos/BomDD/method/tools/bomdd-witness.py:521) を直接印字する。

再現手順（一時 git repo 内）:

```powershell
python C:\Users\akira\source\repos\BomDD\method\tools\bomdd-witness.py produce --eco ECO-T --gate g=0:fixture
python C:\Users\akira\source\repos\BomDD\method\tools\bomdd-witness.py produce --eco ECO-T --stop BOGUS
python C:\Users\akira\source\repos\BomDD\method\tools\bomdd-witness.py --selftest
```

観測:

```text
RC=0
witness 生成: ...\ECO-T.json(tree 96843dd5f45c・gates 1・stop NONE)

RC=2
stop_type 不正: BOGUS(語彙= NONE, ...)

RC=0
bomdd-witness selftest PASS(...)
```

いずれも `<VERDICT> <CODE>[(<CAUSE>)]: <message>` ではない。verify・通常の引数不正・既定パス導出失敗には固定形式が適用されていた。

影響: **文言のみ**（終了コードは正しい）が、§1-1 の「標準出力の1行目」「すべての CLI 経路」という受入条件には不適合。

### IA-02 — temp-index の元 index 複製失敗を TEMP_UNAVAILABLE と誤分類する

[worktree_tree](/C:/Users/akira/source/repos/BomDD/method/tools/bomdd-witness.py:106) は `TemporaryDirectory` 作成だけでなく、`.git/index` の [copy2](/C:/Users/akira/source/repos/BomDD/method/tools/bomdd-witness.py:126) を含むブロック全体の `OSError` を `TEMP_UNAVAILABLE` にする。

再現手順:

```powershell
git init -q $TMP_REPO
New-Item -ItemType Directory "$TMP_REPO\.git\index"
Set-Location $TMP_REPO
python ...\bomdd-witness.py verify $WITNESS --eco ECO-T
```

観測:

```text
RC=2
UNMEASURABLE TREE_UNAVAILABLE(TEMP_UNAVAILABLE): 現 tree を取得できない(
PermissionError: [Errno 13] Permission denied: '...\badidx\.git\index'
)— 測定不能は合格ではない
```

OS temp は利用可能で、失敗したのは既存 index の読取り・複製である。`TEMP_UNAVAILABLE〔TMPDIR 不能〕` という原因とは一致しない。

影響: **判定の誤り**（VERDICT/exit 2 は正しいが CAUSE が誤り）。

### IA-03 — return code 127 だけでは GIT_UNAVAILABLE を識別できない

[worktree_tree](/C:/Users/akira/source/repos/BomDD/method/tools/bomdd-witness.py:111) は `rev-parse`、`add`、`write-tree` のすべてで rc 127 を無条件に `GIT_UNAVAILABLE` とする。

再現手順（`_git` の戻り値を独立注入）:

```powershell
python -c "<bomdd-witness.py を importし、
_git を rc=127 / rc=9009 / stderr空の結果に差し替えて worktree_tree(Path('.'))>"
```

観測:

```text
rc127-existing
(None, None, ('GIT_UNAVAILABLE', 'fatal: executable ran and returned 127'))

rc9009-missing-style
(None, None, ('GIT_DIR_FAILED', "'git' is not recognized"))

empty-stderr
(None, None, ('GIT_DIR_FAILED', ''))
```

したがって、実行された git・ラッパーが内部エラーとして 127 を返した場合は `GIT_UNAVAILABLE` に誤分類される。反対に、実行基盤が「git 不在」を 9009 等で返すラッパー構成では `GIT_DIR_FAILED` になる。現在の直接 `subprocess.run` で実行ファイルが無い経路は `OSError → _GitUnavailable(rc 127)` となるため正しく分類された。

影響: **判定の誤り**（CAUSE）。

### IA-04 — 非 UTF-8/非 cp932 stderr は末尾行を保存できない

[_git](/C:/Users/akira/source/repos/BomDD/method/tools/bomdd-witness.py:77) は `text=True` だけで明示 encoding・`errors="replace"` がない。

再現手順:

```powershell
python -c "
import subprocess
p=subprocess.run(
 ['powershell','-NoProfile','-Command',
  '[Console]::OpenStandardError().WriteByte(129); exit 128'],
 capture_output=True,text=True)
print(p.returncode,repr(p.stderr))
"
```

同じ subprocess 呼出しを `_git` に注入した観測:

```text
worktree_tree= (None, None, ('GIT_DIR_FAILED', ''))

Exception in thread Thread-2 (_readerthread):
...
UnicodeDecodeError: 'cp932' codec can't decode byte 0x81 ...
```

この環境（Python 3.13、既定 cp932）では CAUSE は返ったが stderr は失われ、別スレッドの traceback が stderr に出た。実際の git が同じバイト列を出す個体は作成できず、そこは**測れなかった**。

影響: **文言のみ**（stderr 末尾という要求を満たさず、余分な traceback が出る）。

### 確認できた項目

独自 fixture で次を確認した。

| 経路 | exit / 1行目 |
|---|---|
| `verify --eco ECO-T` | `0 ADVANCE OK: ...` |
| `verify PATH` | `2 UNMEASURABLE IDENTITY_UNCHECKED: ...` |
| `verify --out PATH` | `2 UNMEASURABLE IDENTITY_UNCHECKED: ...` |
| `verify PATH --eco ECO-X` | `1 STOP IDENTITY_MISMATCH: ...` |
| 既定 witness 不在 | `2 UNMEASURABLE WITNESS_UNREADABLE: ...` |
| 引数なし・`verify` 単独・値なし・未知コマンド | `2 UNMEASURABLE ARG_ERROR: ...` |
| git 不在 | `2 TREE_UNAVAILABLE(GIT_UNAVAILABLE)` |
| 非 git directory | `2 TREE_UNAVAILABLE(GIT_DIR_FAILED)` |
| temp が作業木内 | `2 TREE_UNAVAILABLE(TEMP_IN_WORKTREE)` |
| 実 clean-filter 失敗 | `2 TREE_UNAVAILABLE(ADD_FAILED)` |

tree 差分位置は短縮=39、延長=40、先頭差=0、末尾差=39、非文字列=`n/a(tree が文字列でない)`。文字列入力では双方が省略されず表示された。

`--selftest` は exit 0。コード読解上、12 CODE 全てに腕があり、6 CAUSE 全てにも腕がある。ただし `GIT_DIR_FAILED`・`ADD_FAILED`・`WRITE_TREE_FAILED` は `_git` モックであり、特に `WRITE_TREE_FAILED` の実 git 障害は**測れなかった**。モックは IA-02/03/04 の境界を覆わないため、「CAUSE 6/6」は分岐到達の証拠に限れば適格、実障害分類の正しさには不適格。

影響なし予測については、baseline 差分の読解上、追加の終了コード意味変更は見つからなかった。意図された `verify PATH` の 0/1→2 以外は 0/1/2 の意味を保存している。

- `bomdd/hooks/pre-push` は `.git/bomdd-selfconf-witness` の2行だけを読む。
- `bomdd-job.py` は本ツールを import・実行せず、出力も解析しない。
- `self-conformance.py` は本ツールを検査対象にせず、C18 は別 witness を生成する。

`self-conformance.py` 自体は PASS 時に `.git/bomdd-selfconf-witness` を書くため、read-only ブリーフに従って実行していない。したがって今回の個体での全 C1〜C18 判定は**測れなかった**。

W7 の設計については、個体未照合を `UNMEASURABLE(exit 2)` とする判断への反証はない。証拠が不一致だと確定した状態ではなく、要求された照合を実施できていない状態だからである。CODE を job の停止語彙と分離することにも本 ECO 単体での反証はないが、CODE→job 停止語彙の写像は依然として本ツール外である。

較正判定: selftest 緑は **observed・条件付き適格**。検出した計器欠陥は IA-01〜04。Q1/Q2/Q3/Q5/Q7/Q9/Q10/Q11=`asked`、Q4=`asked`（モック結線を追跡）、Q6=`asked`、Q8=`NA`。