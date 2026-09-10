# 判定: REJECT

- 検査対象: `1440ef95ce16b05a14deacbe750fbf4be718716b`。開始時の `git rev-parse HEAD` は指定値と一致。
- 検査官設備（self-reported）: Codex。検査実行時のモデル自己記述は GPT-5 系、最終報告時は GPT-6 系。正確なモデル個体 ID は独立確認していない。
- CLI 実測: `codex-cli 0.154.0`
- Python: `3.13.1`、PyYAML: `6.0.3`、Git: `2.47.1.windows.2`、PowerShell: `7.6.5`
- 実行基盤（self-reported）: `workspace-write`、Windows 11、OS temp 利用可能。
- 作業木: 開始時および終了直前の `git status --short` は出力なし・exit 0。
- IA-01〜07: **resolved 7 / partially 0 / not resolved 0**
- 新規所見: **IA-08（medium）1 件**
- 報告ファイルは検査官から書き込んでいない。

指定された両 selftest、8 腕統合回帰、IA-01/02/05 の実ファイル CLI 経路、IA-06/07、IA-03/04、V2′は期待結果を得た。ただし、Windows 拡張長パスで作業木内出力が受理される W5 不適合を実測したため、判定は REJECT とする。対象 revision の CI 結論は環境制約により UNKNOWN。

## /preflight receipt

| 区分 | 前提 | 判定・根拠 |
|---|---|---|
| 最小契約 | task classification | continuation。r1/r2 の是正後に行う独立再受入 |
| 最小契約 | baseline | confirmed。指定 revision と HEAD が一致 |
| 最小契約 | current-work-state | confirmed。register の ECO-062 は `implemented`、r3 引き渡し中 |
| 最小契約 | unresolved-items | confirmed。order §8.1/§8.2 と r1/r2 報告の IA-01〜07 |
| 最小契約 | handoff-state | confirmed。order・register・過去報告・製造物を読解 |
| 最小契約 | acceptance-target | confirmed。依頼の検査観点と order §4/§5/§8.2 |
| 追加前提 | Python/Git/PyYAML・OS temp | confirmed。バージョン確認と実 fixture 作成に成功 |
| 追加前提 | CI 到達性 | unknown。環境制約により API 結論を取得できない |

開始判定は **PROCEED_WITH_LIMITS**。CI は別途 UNKNOWN とし、ローカル実測を進めた。例外裁定なし。

## 実験設備と記録方法

統合試験は次の OS temp 配下の独立 git リポで実施した。

```text
T = C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r3-inspection
```

製造物 2 ファイルを `T\tools` にコピーし、`a.txt` とともに初期 commit を作成した。以下の `tools/...` コマンドは `T` を作業ディレクトリとする。`method/tools/...` は対象リポを作業ディレクトリとする。

期待値は r1/r2 報告と凍結要求から設定した。各プロセスの終了コードを取得してから次の試験へ進んだ。以下の出力は主要部分を掲載する。

## 両 selftest

```text
$ python method/tools/bomdd-witness.py --selftest
bomdd-witness selftest PASS(known-good 0 / hash・fail・missing・stop・dirty 1 / 不在 2 / 不正 stop 2 / 作業木内出力 2 / r2: 構造不完全 gate 1・不完全 gate 生成拒否 2・個体不一致 1・git 不能 2・引数不正 ArgError・r2b: temp 不能 2・作業木内 temp 2)
exit 0
```

```text
$ python method/tools/bomdd-job.py --selftest
bomdd-job selftest PASS(整合 NONE / 不整合 2 方向 / order 不在 / fence 内見出し無視 / 出所なし欄 null / 全欄 source / r2: 複数 --json 単一文書・引数不正 MISSING_INPUT・null エントリ・r2b: 対象なし/未知オプション MISSING_INPUT)
exit 0
```

## r1 の 8 腕統合回帰

正常 witness を実 CLI で生成した。

```text
$ python tools/bomdd-witness.py produce --eco ECO-900 --gate "g=0:logs/g.log:12" --producer independent-r3
witness 生成: T\.git\bomdd-witness\ECO-900.json(tree 7d03a2588bc6・gates 1・stop NONE)
exit 0
```

この実ファイルを `known-good.json` にコピーし、各腕で一項目だけ変更した。

| 腕 | コマンド／入力操作 | 実測出力 | exit |
|---|---|---|---:|
| known-good | `python tools/bomdd-witness.py verify .git/bomdd-witness/known-good.json` | `ADVANCE: tree 一致(7d03a2588bc6)・gates 1 件 exit 0・stop NONE` | 0 |
| hash | `tree` を 40 個の `0` に変更した `kb-hash.json` を verify | `STOP: tree 不一致(witness 000000000000 / 現 7d03a2588bc6)— 検査後の変更か未検査` | 1 |
| FAIL | gate の `exit` を 1 に変更した `kb-fail.json` を verify | `STOP: gate FAIL 混入(g)` | 1 |
| gates 空 | `gates: []` の `kb-missing.json` を verify | `STOP: gates 欠測(測定不能は合格ではない)` | 1 |
| stop≠NONE | `stop_type: NORMATIVE_RULING` の `kb-stop.json` を verify | `STOP: stop_type=NORMATIVE_RULING` | 1 |
| dirty | 作業木に未追跡 `dirty.tmp` を追加して known-good を verify | `STOP: tree 不一致(witness 7d03a2588bc6 / 現 0884a999445c)— 検査後の変更か未検査` | 1 |
| 不在 | `python tools/bomdd-witness.py verify .git/bomdd-witness/does-not-exist.json` | `witness 読取不能: ... [Errno 2] No such file or directory ...` | 2 |
| 作業木内出力 | `python tools/bomdd-witness.py produce --eco ECO-901 --gate "g=0:logs/g.log:12" --out inside.json --producer independent-r3` | `witness を束縛対象の作業木内に置けない(自己参照): inside.json — .git 配下か作業木外を指定` | 2 |

`inside.json` は `exists=False`。dirty 腕の `dirty.tmp` はその腕の観測後に削除した。指定 8 腕は **8/8 期待一致**。

## IA-01 — resolved

構造不完全な witness を実 JSON ファイルとして用意し、実 CLI の verify に渡した。tree 等は known-good と同一で、gate だけを変更した。

```text
gates=[{"name":"","exit":0,"source":"x"}]

$ python tools/bomdd-witness.py verify .git/bomdd-witness/ia01-empty-name.json
STOP: gate 不完全(gate.name が空)
exit 1
```

```text
gates=[{"name":"g","exit":false,"source":"x"}]

$ python tools/bomdd-witness.py verify .git/bomdd-witness/ia01-bool.json
STOP: gate 不完全(gate.exit が整数でない(g))
exit 1
```

```text
gates=[{"name":"g","exit":0}]

$ python tools/bomdd-witness.py verify .git/bomdd-witness/ia01-no-source.json
STOP: gate 不完全(gate.source が空(g)— 証拠座標が要る(W2))
exit 1
```

生成側の不完全 gate 拒否は witness selftest でも PASS。r2 で未検査だった 3 形状の実ファイル CLI 経路が成立した。

該当実装: `method/tools/bomdd-witness.py:61–74,131–137,170–176`。

## IA-02 — resolved

ECO-900 の実ファイルを ECO-901 名へコピーした。JSON 内の `eco` は ECO-900 のままとした。

```text
$ Copy-Item .git/bomdd-witness/known-good.json .git/bomdd-witness/ECO-901.json

$ python tools/bomdd-witness.py verify --eco ECO-901
STOP: 個体不一致(witness.eco=ECO-900 / 要求 ECO-901)— 別 job の receipt
exit 1
```

一致側も実 CLI で確認した。

```text
$ python tools/bomdd-witness.py verify --eco ECO-900
ADVANCE: tree 一致(7d03a2588bc6)・gates 1 件 exit 0・stop NONE・個体 ECO-900 一致
exit 0
```

該当実装: `method/tools/bomdd-witness.py:155–167,361–377`。

## IA-03 — resolved

Python の絶対パスを取得した後、子プロセスの PATH を空にして実行した。

```text
$ PATH="" python.exe tools/bomdd-witness.py verify .git/bomdd-witness/known-good.json
現 tree を取得できない(git 不能または一時 index 不能)— 測定不能は合格ではない
exit 2
```

```text
$ PATH="" python.exe tools/bomdd-witness.py produce --eco ECO-903 --gate "g=0:log:12" --out .git/bomdd-witness/nogit.json --producer independent-r3
tree を取得できない(git 不能または一時 index 不能 — 測定不能は合格ではない)
exit 2
exists=False
```

両経路とも traceback なし。該当実装: `method/tools/bomdd-witness.py:47–58,138–140,163–165`。

## IA-04 — resolved

実 register に対する CLI 出力を標準 JSON parser（`System.Text.Json.JsonDocument.Parse`）へ渡した。

```text
$ python method/tools/bomdd-job.py ECO-055 ECO-062 --json
JSON.parse=OK
jobs=2
ecos/stops=ECO-055:LEDGER_INCONSISTENT,ECO-062:NONE
exit 0
```

```text
$ python method/tools/bomdd-job.py --all --json
JSON.parse=OK
jobs=2
exit 0
```

いずれも単一 object。該当実装: `method/tools/bomdd-job.py:240–251`。

## IA-05 — resolved

OS temp の実 register fixture:

```yaml
changes:
  - ~
  - {id: ECO-906, title: t6, status: decided, order_ref: bomdd/open.md}
```

`bomdd/open.md` はクローズ見出しを持たない実ファイルとして作成した。

```text
$ python tools/bomdd-job.py --all --json --register bomdd/null.yaml
exit 0
```

出力は単一 JSON object の `jobs` 2 件。主要部分:

```json
[
  {
    "stop_type": {
      "value": "MISSING_INPUT",
      "source": "導出: register エントリが object でない: None"
    }
  },
  {
    "eco": {
      "value": "ECO-906",
      "source": "bomdd/null.yaml:ECO-906.id"
    },
    "stop_type": {
      "value": "NONE",
      "source": "導出: register と order の状態に矛盾なし"
    }
  }
]
```

残りの既知 CLI 経路も再実測した。

```text
$ python method/tools/bomdd-job.py --register
stop_type: MISSING_INPUT
  source: 導出: --register に値がない(引数不正)
exit 0

$ python method/tools/bomdd-job.py ECO-999 --json
eco.value: ECO-999
stop_type.value: MISSING_INPUT
stop_type.source: 導出: register に ECO-999 なし
exit 0

$ python tools/bomdd-witness.py produce --eco ECO-909 --gate malformed --out .git/bomdd-witness/malformed.json --producer independent-r3
引数不正: --gate の形式不正: 'malformed'(name=exit:source・3 要素とも必須)
exit 2
exists=False

$ python tools/bomdd-witness.py verify --eco
引数不正: --eco に値がない
exit 2
```

該当実装: `method/tools/bomdd-job.py:197–237`、`method/tools/bomdd-witness.py:185–216,349–383`。

## IA-06 — resolved

最初に環境変数による再現の成立性を確認した。

```text
TMP=C:\no-such-bomdd-r3-temp\nested
TEMP=C:\no-such-bomdd-r3-temp\nested
TMPDIR=C:\no-such-bomdd-r3-temp\nested
gettempdir=C:\Users\akira\AppData\Local\Temp
exit 0
```

3 変数を存在しないパスにしても `tempfile.gettempdir()` は既定 OS temp を返した。この方法では temp 作成不能を再現できなかった。

依頼で指定された代替方法として、`python -c` でモジュールをロードし、`tempfile.tempdir` を不在パスに固定して関数を直接呼んだ。表示経路は `PYTHONIOENCODING=utf-8` とした。

```python
tempfile.tempdir = str(Path.cwd() / "no-such-dir" / "nested")
rc, msg = m.verify(
    Path.cwd(), Path(".git/bomdd-witness/known-good.json")
)
print(msg)
raise SystemExit(rc)
```

```text
tempfile.tempdir=T\no-such-dir\nested
現 tree を取得できない(git 不能または一時 index 不能)— 測定不能は合格ではない
return=2
process_exit=2
```

produce 側:

```python
tempfile.tempdir = str(Path.cwd() / "no-such-dir" / "nested")
out = Path(".git/bomdd-witness/notmp.json")
rc, msg, _ = m.produce(
    Path.cwd(), "ECO-902",
    [{"name": "g", "exit": 0, "source": "log:12"}],
    "NONE", out, "independent-r3"
)
print(msg)
print("exists=" + str(out.exists()))
raise SystemExit(rc)
```

```text
tree を取得できない(git 不能または一時 index 不能 — 測定不能は合格ではない)
exists=False
return=2
process_exit=2
```

両方とも traceback なし。初回の直接 probe は検査官側の cp932 表示で `UnicodeEncodeError` となったため、その実行は判定根拠から除外し、UTF-8 指定後の実測を採用した。

該当実装: `method/tools/bomdd-witness.py:77–104,138–140,163–165`。この resolved は依頼で認められた直接関数 probe に基づく。

## IA-07 — resolved

```text
$ python method/tools/bomdd-job.py --json
jobs: 1 件
stop_type.value: MISSING_INPUT
stop_type.source: 導出: 対象指定なし(引数不正): ECO-NNN か --all を指定
exit 0
```

```text
$ python method/tools/bomdd-job.py --bogus ECO-062 --json
jobs: 1 件
stop_type.value: MISSING_INPUT
stop_type.source: 導出: 未知のオプション(引数不正): --bogus
exit 0
```

```text
$ python method/tools/bomdd-job.py ECO-062 --json
jobs: 1 件
eco.value: ECO-062
state.value: implemented
stop_type.value: NONE
stop_type.source: 導出: register と order の状態に矛盾なし
exit 0
```

該当実装: `method/tools/bomdd-job.py:205–220`。

## V2′・既存 witness

```text
$ python method/tools/bomdd-job.py ECO-055 ECO-062 --json
ECO-055 fields=15 empty_sources=0 stop=LEDGER_INCONSISTENT
ECO-062 fields=15 empty_sources=0 stop=NONE
exit 0
```

各 job の 15 欄すべてに非空 source が存在した。必要スキル・必要設備・制限事項・期待成果物・独立検査結果の 5 欄は `null + none(Fn...)`。order 散文からの値転写は認めなかった。V2′は **observed PASS**。

対象リポに既存の witness も再検証した。

```text
$ python method/tools/bomdd-witness.py verify --eco ECO-062
ADVANCE: tree 一致(5343b26612f1)・gates 1 件 exit 0・stop NONE・個体 ECO-062 一致
exit 0
```

JSON 内の tree は対象 commit の tree と一致。`head` は生成時の `37057e5a...` だったが、本仕様の検証対象は worktree tree である。gate の申告値そのものの正確さは、この verify では測定していない。

## diff 監査

```text
$ git diff --name-status 37057e5..1440ef95ce16b05a14deacbe750fbf4be718716b
M  bomdd/60-change-order-eco-062.md
M  bomdd/60-change-register.yaml
A  bomdd/reports/independent-inspection-eco-062-r2.md
M  method/tools/bomdd-job.py
M  method/tools/bomdd-witness.py
```

製造物 2 ファイルと台帳系 3 ファイルだけ。指定窓の監査は **PASS**。

## 副経路

source の `:` は実生成ファイルで保持された。

```text
--gate "g=0:logs/g.log:12"
source=logs/g.log:12
exact=True
```

`_inside_worktree` の直接 probe:

```text
direct-inside:                 True
direct-outside:                False
inside-junction-to-outside:    False
outside-junction-to-inside:    True
extended-prefix-inside:       False
```

通常パスと junction の 4 腕は期待どおり。最後の拡張長パスは IA-08 として CLI 再現した。

selftest 前後の `tempfile.tempdir` も測定した。

```text
bomdd-witness selftest PASS(...)
before=None
after='C:\Users\akira\AppData\Local\Temp'
restored=False
exit 0
```

これは selftest 冒頭の通常 temp 利用で既定パスがキャッシュされることと整合する。差し替えた不在パスや作業木パスは終了後に残っていない。ただし、selftest 後の同一プロセスで追加の正常 verify を行う試験は未実施。

## IA-08 — Windows 拡張長パスで作業木内出力を受理する

- severity: **medium**
- evidence class: **実 CLI・実ファイル出力・関数 probe・コード読解**
- 該当行: `method/tools/bomdd-witness.py:111–128,141–151`
- 対応要求: W5「作業木内への出力は exit 2 で拒否」
- 状態: 新規検出。今回の是正差分で導入されたか、以前から存在したかは未確定。

`\\?\C:\...` 表記のパスは、通常表記と同じファイルを指す。しかし `path.resolve()` と `root.resolve()` の表記が揃わず、`relative_to` が作業木との包含関係を認識しない。

再現手順:

```text
cwd=T

$ python tools/bomdd-witness.py produce --eco ECO-908 --gate "g=0:log:12" --out "\\?\C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r3-inspection\ia08-extended.json" --producer independent-r3
witness 生成: \\?\C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r3-inspection\ia08-extended.json(tree c4b4d46818cc・gates 1・stop NONE)
exit 0
normal_path_exists=True
```

期待は **exit 2・出力ファイルなし**。実際は **exit 0・作業木内にファイルあり**。

直後の verify:

```text
$ python tools/bomdd-witness.py verify "\\?\C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r3-inspection\ia08-extended.json"
STOP: tree 不一致(witness c4b4d46818cc / 現 de95ac707fd7)— 検査後の変更か未検査
exit 1
```

生成された witness 自身が次の tree に入り、自己参照による不一致となった。verify は停止したが、produce の W5 契約は成立していない。パス表記の正規化と、通常表記／拡張長表記を対にした回帰試験が必要。

## V4

self-conformance は `.git/bomdd-selfconf-witness` を生成するため、対象リポでは実行せず、対象 commit の archive を OS temp に展開した再構成 git リポで実行した。

```text
$ python method/tools/self-conformance.py
```

初回:

```text
C1〜C17: PASS
[C18] FAIL pre-push witness 設置(hooksPath=未設定・hook 実在+witness 突合=True)
self-conformance FAILED — 1 件の不適合
exit 1
```

temp fixture に `git config core.hooksPath bomdd/hooks` を設定後、同じ単一入口を再実行した。

```text
C1〜C17: PASS
[C18] PASS pre-push witness 設置(hooksPath=bomdd/hooks・hook 実在+witness 突合=True)
self-conformance passed — 全検査合格
exit 0
```

初回 C18 不適合は fixture の設定不足に帰属する。ただし再構成リポの tree は `be8564de...`、対象 commit の tree は `5343b266...` で一致していない。差の完全な照合は未実施のため、再構成環境での PASS を対象 revision の V4 全体の成立へ昇格させない。

CI:

```text
$ gh run list --repo akiramei/BomDD --limit 5 --json databaseId,headSha,status,conclusion,name,createdAt
exit 1
```

接続が実行基盤の環境制約で成立しなかった。Web 経路でも対象 run の結論を取得できなかった。CI は **UNKNOWN**。

## /calibrate receipt

| 査定した主張 | 測定成立性 | 証拠資格・帰結 |
|---|---|---|
| 両 selftest が成功 | observed | 適格。両方 exit 0 |
| 指定 8 腕が期待どおり | observed | 適格。実 git・CLI・ファイル経路で 8/8 |
| IA-01/02/05 の未了統合経路が解消 | observed | 適格。構造不完全 JSON、別 ECO コピー、null YAML を実入力として使用 |
| IA-03/04/07 が解消 | observed | 適格。実 CLI と JSON parser で確認 |
| IA-06 が解消 | observed | 条件付き適格。指定代替 probe による関数経路 |
| V2′ | observed | 適格。期待停止種別・各 15 欄 source・散文転写なし |
| 指定 diff 窓 | observed | 適格。指定 5 ファイルのみ |
| W5 が全対象パスで成立 | observed | 不適格。IA-08 が反証 |
| 再構成 fixture の self-conformance | observed | 条件付き適格。設定補正後 PASS、対象 tree との完全一致は未確認 |
| 対象 revision の CI | unknown（CI_UNREACHABLE） | 資格判定なし |

計器・製造物の新規所見は IA-08。検査官側の表示符号化、fixture 設定不足、CI 接続不能は別帰属として扱った。

battery 記録:

| 問い | 記録 | 要点 |
|---|---|---|
| Q1 | asked | W5 の宣言と実挙動の差を IA-08 で検出 |
| Q2 | asked | known-good と変更・欠測腕を対で測定 |
| Q3 | asked | hash・gate・stop・dirty・個体・実行不能を個別に測定 |
| Q4 | asked | 実ファイルと CLI を接続。IA-06 の直接 probe は明示 |
| Q5 | asked | CI と対象 tree 未照合を PASS に数えない |
| Q6 | asked | 終了コードを観測してから後続試験へ進行 |
| Q7 | asked | 両 selftest の陽性対照を実行 |
| Q8 | NA | 新規予防ゲートの受入ではない |
| Q9 | asked | 指定 HEAD、別 ECO、既存 witness の tree を突合 |
| Q10 | asked | 未測定の次元を末尾に宣言 |
| Q11 | asked | 通常パス・junction・拡張長パスを別クラスで測定 |

## 後片付けと終了確認

終了前に OS temp の検査用ディレクトリ・archive の削除を要求したが、自動実行チェックによりコマンドが実行されなかった。したがって、**次の検査用データの削除は未完了**。

```text
C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r3-inspection
C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r3-outside
C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r3-selfconf
C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r3-selfconf.tar
```

前二つには検査で作成した junction がある。後片付けでは junction 自体を先に除去する必要がある。

対象リポの終了確認:

```text
$ git status --short
（出力なし）
exit 0
```

通常の status は空だった。ただし、この確認だけで Git の表示対象外ファイルまで無変更と証明できるわけではない。

## 未検査・未完了

- 対象 revision の CI 結論。
- 対象リポそのものに対する self-conformance の再実行と、archive 再構成 tree の差の完全照合。
- 実ネットワーク共有の UNC、通常の symbolic link、linked worktree、submodule、Linux、同時更新。
- IA-08 の旧 revision 比較。
- selftest 終了後の同一プロセスでの追加正常 verify。
- OS temp に残った上記検査用データの削除。

## この検査が支持しないもの

witness の申告値が実際の検査結果と一致すること、すべての Git 構成・パス表記で正しく動くことは支持しない。  
対象 revision の CI 成功、対象 tree に対する V4 全体の成立、OS temp の後片付け完了は支持しない。  
通常の `git status` に表示されないファイルまで無変更であること、未検査の入力クラスに不適合がないことは支持しない。
