# 判定: REJECT

- 検査対象 revision: `5249d06e63d41dd8cb86bf21258471d94dd3a9bb` (`main`)
- 製造物の起点: `1eefe352a306c27264ea84c83472f65a407bf301`。`git diff --name-status 1eefe35..5249d06 -- method/tools/bomdd-job.py method/tools/bomdd-witness.py` は出力なし。
- 検査官設備: model `gpt-5.6-sol` / Codex (`reasoning_effort=medium`, `windows_elevated`) — **self-reported**
- Codex CLI 版: **UNKNOWN** — `codex --version` は `ENOENT`、`where.exe codex` は exit 1。このセッションの CLI 版を申告できる実行個体が PATH 上にない。
- 実測環境: Python 3.13.1 / Git 2.47.1.windows.2 / PyYAML **不在**（検査官側 Python 個体）
- 所見: 5 件（high 2 / medium 2 / low 1）

指定された V1' の 8 腕は期待値 `(0 / 1 / 1 / 1 / 1 / 1 / 2 / 2)` と一致した。しかし、その battery が測っていない「gate の完全性」と「ECO 個体の結合」で、遷移を誤って `ADVANCE` する 2 経路を実測した。運転員の遷移判定という中核要求に対する fail-open なので、process decision は REJECT とする。

## /preflight receipt

- task classification: continuation（既に製造済みの特定 revision に対する独立受入の継続）。根拠は、baseline・現在状態・未解決の独立検査・handoff brief・受入対象が既存状態に依存するため。
- 最小契約:
  - baseline: **confirmed** — `git rev-parse HEAD` = 対象 revision。
  - current-work-state: **confirmed** — register ECO-062 は `implemented`、独立検査 UNKNOWN のまま。
  - unresolved-items: **confirmed** — order §8 と brief が独立検査未成立を明記。
  - handoff-state: **confirmed** — brief、order、register、製造物 2 ファイルを実読。
  - acceptance-target: **confirmed** — brief の観点 1〜7 と出力形式。
- discovered prerequisites: 作業木 clean、OS temp への fixture 作成、Git/Python の実行を **confirmed**。PyYAML は **missing**、GitHub CLI 認証は **missing**。
- 開始判定: **PROCEED_WITH_LIMITS** — witness、diff、コード読解、一次記録は検査する。実 Python 個体での V2' と CI API 再照合は UNKNOWN として昇格根拠に使わない。
- override: なし。

## 実行コマンドと主要出力

### 個体・差分窓

```text
$ git rev-parse HEAD
5249d06e63d41dd8cb86bf21258471d94dd3a9bb

$ git status --short
(出力なし)

$ git diff --stat e26802e..5249d06e63d41dd8cb86bf21258471d94dd3a9bb
 bomdd/60-change-order-eco-062.md | 346 +++++++++++++++++++++++++++++++++++++++
 bomdd/60-change-register.yaml    |  33 ++++
 method/improvements.md           |  97 +++++++++++
 method/tools/bomdd-job.py        | 204 +++++++++++++++++++++++
 method/tools/bomdd-witness.py    | 257 +++++++++++++++++++++++++++++
 5 files changed, 937 insertions(+)

$ git diff --name-status e26802e..5249d06e63d41dd8cb86bf21258471d94dd3a9bb
A  bomdd/60-change-order-eco-062.md
M  bomdd/60-change-register.yaml
M  method/improvements.md
A  method/tools/bomdd-job.py
A  method/tools/bomdd-witness.py

$ git diff --name-status 1eefe35..5249d06e63d41dd8cb86bf21258471d94dd3a9bb -- method/tools/bomdd-job.py method/tools/bomdd-witness.py
(出力なし)
```

窓内は register の `diff_audit.allowed_paths`（同ファイル 2282〜2285 行）と完全一致した。既存の hook、self-conformance.py、README、AGENTS.md、skills に diff はない。製造物のコード読解でも ruling 取り込み、設備認定参照、新規 gate、既存ツール改変は認めなかった。第 1 弾の凍結範囲超過は 0。

### V1' 標準 selftest と独立 8 腕

```text
$ python method/tools/bomdd-witness.py --selftest
exit 0
bomdd-witness selftest PASS(known-good 0 / hash・fail・missing・stop・dirty 1 / 不在 2 / 不正 stop 2 / 作業木内出力 2)
```

独立 fixture は `%TEMP%\eco62-witness-*` に `git init` して commit 1 件を作成し、終了時に再帰削除した。`core.autocrlf=false`、検査対象スクリプトは対象 revision の絶対パスを使った。

```text
$ python ...\bomdd-witness.py produce --eco ECO-900 --gate g=0:log.txt:1 --out %TEMP%\...\good.json --producer independent
exit 0
witness 生成: ...\good.json(tree 08585692ce06・gates 1・stop NONE)

$ python ...\bomdd-witness.py verify ...\good.json
exit 0
ADVANCE: tree 一致(08585692ce06)・gates 1 件 exit 0・stop NONE

$ python ...\bomdd-witness.py verify ...\hash.json
exit 1
STOP: tree 不一致(witness 08585692ce06 / 現 08585692ce06)— 検査後の変更か未検査

$ python ...\bomdd-witness.py verify ...\fail.json
exit 1
STOP: gate FAIL 混入(g)

$ python ...\bomdd-witness.py verify ...\gates-empty.json
exit 1
STOP: gates 欠測(測定不能は合格ではない)

$ python ...\bomdd-witness.py verify ...\stop.json
exit 1
STOP: stop_type=NORMATIVE_RULING

$ python ...\bomdd-witness.py verify ...\dirty.json
exit 1
STOP: tree 不一致(witness 08585692ce06 / 現 e9c0f10b4a5c)— 検査後の変更か未検査

$ python ...\bomdd-witness.py verify ...\absent.json
exit 2
witness 読取不能: ...\absent.json([Errno 2] No such file or directory ...)— 測定不能は合格ではない

$ python ...\bomdd-witness.py produce --eco ECO-900 --gate g=0:x --out <fixture-worktree>\inside.json
exit 2
witness を束縛対象の作業木内に置けない(自己参照): ...\inside.json — .git 配下か作業木外を指定
```

期待との照合: known-good 0 / hash 1 / FAIL 1 / gates 空 1 / stop_type≠NONE 1 / dirty 1 / witness 不在 2 / 作業木内出力 2。8/8 一致。生成 JSON の byte 検査は `hasCR=false`, `endsLF=true`。拒否された作業木内出力は存在しなかった。

### V2' と job selftest

```text
$ python -c "import yaml; print(yaml.__version__)"
exit 1
ModuleNotFoundError: No module named 'yaml'

$ python method/tools/bomdd-job.py --selftest
exit 1
bomdd-job selftest FAILED:
  fixture register 読取: PyYAML 不在

$ python method/tools/bomdd-job.py ECO-055 ECO-062 --json
exit 0
stop_type: MISSING_INPUT
  source: 導出: PyYAML 不在
```

したがって、対象 register を用いた V2' の実行結果は **未検査（測定成立性 unknown / reason: INSPECTOR_PYYAML_MISSING）**。これを PASS に数えない。一方、一次記録の独立読解では register ECO-055 の `status: in-progress`（2049〜2053 行）と order ECO-055 の `## 6. クローズ(...verified)`（139〜142 行）の矛盾、register ECO-062 の `status: implemented`（2266〜2270 行）と未クローズを確認した。コード 73〜111 行の射影規則に従えば前者は `LEDGER_INCONSISTENT`、後者は `NONE` となる。これはコード読解であって、V2' 実行成功の代用にはしない。

出所なし欄は job 86〜90 行で `null + source none(Fn...)`、導出欄は 78〜85 行で register の論理座標を参照しており、order 散文値の転写は認めなかった。停止語彙は job 41〜50 行と witness 42〜43 行で同一の 8 値だった。

### 製造者申告と V4

```text
$ git show --no-patch --format=%H%n%T%n%P%n%s 1eefe35
1eefe352a306c27264ea84c83472f65a407bf301
d21b9a6b9d31b97f2dfdc32825ded1501c7481db
d36fd766c6cdad6a3be793237e69bd893a357f1e
fix(eco-062): ... selftest 両 PASS・V2' ECO-055=LEDGER_INCONSISTENT/ECO-062=NONE・V4 全 PASS ...

$ gh run view 34467755878 --repo akiramei/BomDD --json databaseId,headSha,conclusion,status,jobs
exit 4
To get started with GitHub CLI, please run: gh auth login
```

order §6 が参照する `scratchpad/selfconf-7.log` は実在し、`[env] python 3.13.1・PyYAML 6.0.3`、C1〜C18 PASS、C13 `105 files/216 links`、C16 `order 30 件`、末尾 `self-conformance passed — 全検査合格` を含む。selfconf-8/9 も同内容だった。ただしこれは製造者系統の一次記録の実在確認であり、独立再実測ではない。検査官側では PyYAML 不在、GitHub CLI は未認証なので、self-conformance と CI run 34467755878 の結論・headSha は **未検査（unknown）**。diff 窓だけは observed PASS。

## 所見

### IA-01 — 完全性を欠く gate を生成・検証して ADVANCE する

- severity: **high**
- evidence class: **実測コマンド+出力 / コード読解**
- 要求: order §4 122〜123 行、§5 W2 174〜176 行。witness の gate は検査名+exit を持ち、`source` は証拠座標でなければならない。
- 該当行: `method/tools/bomdd-witness.py:128-146`, `:231`。`parse_gates` は空名・空 source を許し、`verify` は list が非空で `g.get("exit") == 0` なら name/source/型を検証しない。JSON `false` も Python では `0` と等価。
- 再現手順と実測:

```text
$ python ...\bomdd-witness.py produce --eco ECO-901 --gate =0 --producer independent
exit 0
witness 生成: ...\.git\bomdd-witness\ECO-901.json(... gates 1・stop NONE)

$ python ...\bomdd-witness.py verify --eco ECO-901
exit 0
ADVANCE: tree 一致(...)・gates 1 件 exit 0・stop NONE

# current tree を持つ JSON の gates を [{"name":"","exit":false,"source":null}] に変更
$ python ...\bomdd-witness.py verify ...\structurally-incomplete.json
exit 0
ADVANCE: tree 一致(...)・gates 1 件 exit 0・stop NONE
```

- 帰結: gates の「存在」は見るが「完全性」を見ない。実在する検査結果を 1 件も指さない witness で運転員を進められるため、V1' の中心命題を反証する。

### IA-02 — `verify --eco` が別 ECO の witness を受理する

- severity: **high**
- evidence class: **実測コマンド+出力 / コード読解**
- 要求: 個体参照（witness の `eco` / `witness` と `--eco` の一致）と、ECO ごとの receipt 再検証。
- 該当行: `method/tools/bomdd-witness.py:108-110`, `:117-136`, `:223-245`。生成時は個体 ID を書くが、検証時は一度も照合しない。
- 再現手順と実測:

```text
$ python ...\bomdd-witness.py produce --eco ECO-900 --gate g=0:log:1
exit 0
# ECO-900.json を .git/bomdd-witness/ECO-901.json へコピー（JSON 内 eco/witness は ECO-900 のまま）
$ python ...\bomdd-witness.py verify --eco ECO-901
exit 0
ADVANCE: tree 一致(aaff74984ccc)・gates 1 件 exit 0・stop NONE
```

- 帰結: 同一 tree 上の別 job の receipt を取り違えても進行する。改竄だけでなくファイル誤配置という副経路で発生し、個体束縛が成立していない。

### IA-03 — git 実行不能を exit 2 に分類できず traceback / exit 1 になる

- severity: **medium**
- evidence class: **実測コマンド+出力 / コード読解**
- 要求: witness 18〜20 行の契約「git 不能 → exit 2（測定不能）」、order §4 123 行。
- 該当行: `method/tools/bomdd-witness.py:47-55`, `:100-102`, `:123-125`。`subprocess.run` の `FileNotFoundError` が捕捉されない。
- 再現手順: commit 済み temp repo で、絶対パスの Python を `PATH` 空の環境から起動する。

```text
$ env(PATH="") C:\Python313\python.exe ...\bomdd-witness.py verify ...\ECO-900.json
exit 1
Traceback ... FileNotFoundError: [WinError 2] ...

$ env(PATH="") C:\Python313\python.exe ...\bomdd-witness.py produce --eco ECO-902 --gate g=0:x --out ...\x.json
exit 1
Traceback ... FileNotFoundError: [WinError 2] ...
```

- 帰結: 測定不能と検証 STOP が同じ process exit 1 に潰れ、仕様の 0/1/2 分類を消費側が利用できない。

### IA-04 — 複数 job の `--json` 出力が JSON 文書でない

- severity: **medium**
- evidence class: **実測コマンド+出力 / コード読解**
- 要求: job は運転員向けの機械可読ビュー（job 1〜4 行）。CLI は複数 ECO と `--all` を許す（18〜21、186〜199 行）。
- 該当行: `method/tools/bomdd-job.py:186-199`。選択された各 entry を独立した JSON object として連続 `print` する。
- 再現手順: OS temp に JSON（YAML の部分集合）の register 2 entry と、JSON `safe_load` fixture を置いて対象スクリプトを実行。fixture は parser 依存を分離し、render/main のみを測った。

```text
$ C:\Python313\python.exe ...\bomdd-job.py ECO-901 ECO-902 --register %TEMP%\...\register.json --json
exit 0
{ ... ECO-901 ... }
{ ... ECO-902 ... }

$ JSON.parse(stdout)
invalid: Unexpected non-whitespace character after JSON at position 2234 (line 83 column 1)
```

- 帰結: 複数 ECO または `--all --json` を標準 JSON parser へ渡せず、機械可読出力として閉じていない。

### IA-05 — 不正入力経路が契約した終了コードで閉じず traceback を出す

- severity: **low**
- evidence class: **実測コマンド+出力 / コード読解**
- 要求: job の exit は selftest 失敗を除き常に 0（job 15 行、174〜200 行）。witness の測定不能は exit 2（witness 18〜20 行）。
- 該当行: `method/tools/bomdd-job.py:179-180`, `:187-190`; `method/tools/bomdd-witness.py:139-146`, `:223-230`。
- 再現手順と実測:

```text
$ python method/tools/bomdd-job.py --register
exit 1
Traceback ... IndexError: list index out of range

$ python ...\bomdd-witness.py produce --eco ECO-902 --gate malformed --out ...\malformed.json
exit 1
Traceback ... ValueError: invalid literal for int() with base 10: ''

$ python ...\bomdd-witness.py verify --eco
exit 1
Traceback ... IndexError: list index out of range

# safe_load が {"changes":[null]} を返す register
$ python ...\bomdd-job.py --all --register ...\register.json
exit 1
Traceback ... AttributeError: 'NoneType' object has no attribute 'get'
```

- 帰結: meta-failure を定義済みの MISSING_INPUT / exit 2 へ分類できない。通常の正本では発火しないため severity は low とした。

## 仕様整合の結果

- W1: **一致**。witness 51〜70 行は index を一時コピーし `git add -A` → `write-tree`。self-conformance 1609〜1634 行と同じ tree 定義で、witness 側はさらに `git add` の return code も確認する。
- W4/W5: **一致**。既定は `.git/bomdd-witness/<ECO>.json`（73〜74、111〜113 行）、pre-push の `.git/bomdd-selfconf-witness` とは別。作業木内出力は exit 2 で拒否し、残置なしを実測。
- stop vocabulary: **一致**。job 41〜50 行と witness 42〜43 行は順序・値とも同一。
- job の「終了コードは常に 0」: 通常の PyYAML 欠測は exit 0 で MISSING_INPUT。ただし IA-05 の CLI/形状不正経路で不一致。
- 案超過: **なし**。凍結された job 射影+witness 以外の機能、既存ツール改変、新 gate は差分・コードの双方で認めない。

## /calibrate receipt

| 査定した主張 | 測定成立性 | 証拠資格 | 根拠・帰結 |
|---|---|---|---|
| V1' 指定 8 腕の exit が期待どおり | observed | 条件付き適格 | 独立 temp repo で 8/8 一致。ただし gate 完全性と ECO 個体結合を測らず、IA-01/02 で fail-open。限定主張にのみ使用可。 |
| witness が「再検証してから進める」を保証 | observed | 不適格 | IA-01/02。REJECT の直接根拠。 |
| V2' 実 register で ECO-055/062 を導出 | unknown (`INSPECTOR_PYYAML_MISSING`) | — | 検査官個体では実行不能。コード/一次記録読解を実行成功の代用にしない。 |
| diff 窓が allowed_paths のみ | observed | 適格 | `git diff --name-status/stat` と register 2282〜2285 行を突合。 |
| V4 self-conformance / CI | unknown (`PYYAML_MISSING` / `GH_AUTH_MISSING`) | — | 製造者ログの実在は確認したが、独立昇格根拠には不使用。 |

- 検出した計器欠陥と帰属: IA-01〜05 は製造物（witness/job）帰属。検査官側 PyYAML 欠測と GitHub CLI 未認証は harness/environment 帰属で、製造物欠陥には数えない。
- battery 記録:
  - Q1 **asked** — 検証器の自己記述より狭い実装を IA-01/02/03 で検出。
  - Q2 **asked** — known-good と hash/FAIL/空/stop/dirty/不在/作業木内出力を対で実測。
  - Q3 **asked** — 指定腕に加え、構造完全性・個体結合・git 欠測を独立に落とした。
  - Q4 **asked** — temp fixture を対象スクリプトの実入力にし、終了時に削除。job JSON probe の parser fixture は render/main だけの限定測定と明記。
  - Q5 **asked** — PyYAML、CI、CLI 版の欠測を UNKNOWN とし PASS に数えない。
  - Q6 **asked** — 各 exit/stdout を受領してから次腕を作成・判定。後続操作との条件なし chain なし。
  - Q7 **asked** — selftest の陽性対照は存在するが、IA-01/02/03 の枝は未被覆。
  - Q8 **NA** — 本変更は常設予防 gate を新設しない。
  - Q9 **asked** — revision は一致。witness の ECO 個体不一致を IA-02 で検出。
  - Q10 **asked** — 下記「この検査が支持しないもの」に宣言。
  - Q11 **asked** — 正常/値改変/欠測/dirty に加え、構造不完全/別 ECO/依存実行不能/CLI 不正を別クラスとして測定。

## 未検査

- 実 register + PyYAML での `bomdd-job.py ECO-055 ECO-062` と job selftest（検査官 Python に PyYAML がない）。
- `python method/tools/self-conformance.py` の独立再実行、および CI run 34467755878 の API 結論・headSha（それぞれ PyYAML 不在、GitHub CLI 未認証）。
- Linux 上の実行、symlink/worktree/submodule、ignored ファイル、非 ASCII パス、同時更新競合。Windows の LF 出力と通常 temp path は実測済み。

## この検査が支持しないもの

本検査は witness の改竄耐性、gate 自体の真実性、全 Git 構成での tree 同一性を支持しない。
V2'・self-conformance・CI は独立実測が成立しておらず、製造者記録の実在確認を PASS へ昇格していない。
所見ゼロの未検枝や未知の入力クラスに欠陥がないことを支持しない。
