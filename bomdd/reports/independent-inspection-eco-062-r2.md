# 判定: REJECT

- 検査対象 revision: `37057e5a7820254cad119a31837cbe8676ede926`（`main`、指定値と一致）
- 検査官設備: model `GPT-5 / Codex`、read-only sandbox — **self-reported**
- Codex CLI: `0.154.0`（`codex --version` 実測）
- Python: `3.13.1`
- Git: `2.47.1.windows.2`
- PyYAML: **あり**、`6.0.3`
- 作業木: 開始時・終了時とも `git status --short` 出力なし
- 既存 IA-01〜05: **resolved 2 / partially 3 / not resolved 0**
- 新規所見: **2 件**（medium 1 / low 1）

IA-03、IA-04 は指定された実 CLI 経路で解消を確認した。IA-01、IA-02、IA-05 も修正ロジック自体は期待値を返したが、read-only sandbox が OS temp 作成も禁止したため、r1 と同じ独立 temp Git リポによる統合再現は成立しなかった。

加えて、通常 PATH 下で一時 index を作成できない場合、witness の `verify` / `produce` が測定不能 exit 2 ではなく traceback・exit 1 になる新規欠陥 IA-06 を実測した。必須 selftest と8腕統合回帰も測定不能であり、ACCEPT へ昇格できない。

## /preflight receipt

- task classification: **continuation**。製造済み revision に対する r1 是正後の独立再検査であり、既存 baseline、現在状態、未解決所見、handoff、受入基準に依存する。
- baseline: **confirmed** — `git rev-parse HEAD` は指定 revision と一致。
- current-work-state: **confirmed** — register の ECO-062 は `implemented`、r2 引き渡し中。
- unresolved-items: **confirmed** — order §8.1 の IA-01〜05 と r2 受入条件を実読。
- handoff-state: **confirmed** — order、register、r1 報告、製造物2ファイルを実読。
- acceptance-target: **confirmed** — brief の観点1〜6および出力形式。
- discovered prerequisite:
  - Python/Git/PyYAML: **confirmed**
  - 作業木 clean: **confirmed**
  - OS temp への書込み: **contradicted** — `tempfile` が利用可能なディレクトリを発見できない
  - GitHub API 到達性: **unknown** — sandbox のネットワーク禁止
- 開始判定: **PROCEED_WITH_LIMITS** — 実リポの read-only 経路、引数処理、V2′、diff、コード単位のロジックを検査する。temp Git リポを必要とする統合試験は UNKNOWN とする。
- override: なし。

## IA-01〜05 再実測

### IA-01 — partially

空名 gate の生成拒否は実 CLI で解消を確認した。

```text
$ python method/tools/bomdd-witness.py produce --eco ECO-901 --gate =0 --producer independent
引数不正: --gate の形式不正: '=0'(name=exit:source・3 要素とも必須)
exit 2
```

構造不完全 witness は、temp ファイルを作れないため r1 と同じファイル経路では再現不能。`worktree_tree` だけを固定したインメモリ probe では次の結果となった。

```text
空名:
exit 1
STOP: gate 不完全(gate.name が空)

exit:false:
exit 1
STOP: gate 不完全(gate.exit が整数でない(g))

source なし:
exit 1
STOP: gate 不完全(gate.source が空(g)— 証拠座標が要る(W2))
```

該当実装: `method/tools/bomdd-witness.py:61-74,123-130,162-171,181-198`

修正ロジックは期待どおりだが、指定されたファイルベース CLI 統合経路は未検査なので **partially**。

### IA-02 — partially

インメモリ witness を用いて `verify()` の個体照合を実測した。

```text
witness.eco=ECO-900 / eco=ECO-901:
exit 1
STOP: 個体不一致(witness.eco=ECO-900 / 要求 ECO-901)— 別 job の receipt

witness.eco=ECO-900 / eco=ECO-900:
exit 0
ADVANCE: ... 個体 ECO-900 一致

PATH 経路相当（eco 引数なし）:
exit 0
ADVANCE: tree 一致(TREE)・gates 1 件 exit 0・stop NONE
```

PATH 経路では個体照合を要求せず、`--eco` 指定時だけ照合する仕様にも一致する。

該当実装: `method/tools/bomdd-witness.py:147-174,339-357`

別 ECO 名へ実ファイルをコピーする r1 と同じ CLI 手順は temp Git リポを作れず未検査なので **partially**。

### IA-03 — resolved

絶対パスの Python を PATH 空環境で起動した。

```text
$ PATH="" python.exe method/tools/bomdd-witness.py verify .git/bomdd-witness/ECO-062.json
現 tree を取得できない(git 不能)— 測定不能は合格ではない
exit 2

$ PATH="" python.exe method/tools/bomdd-witness.py produce --eco ECO-902 --gate g=0:x --out IA03-NO-WRITE.json
tree を取得できない(git 不能 — 測定不能は合格ではない)
exit 2
```

traceback はなく、出力ファイルも存在しなかった。該当実装は `method/tools/bomdd-witness.py:47-58`。**resolved**。

### IA-04 — resolved

実 register を使った複数 ECO と `--all` の両経路を標準 JSON parser へ渡した。

```text
$ python method/tools/bomdd-job.py ECO-055 ECO-062 --json
process exit 0
JSON.parse: OK
top-level type: object
jobs: 2
ecos: ECO-055,ECO-062

$ python method/tools/bomdd-job.py --all --json
process exit 0
JSON.parse: OK
top-level type: object
jobs: 2
```

該当実装: `method/tools/bomdd-job.py:228-239`。**resolved**。

### IA-05 — partially

実 CLI で確認できる4経路は期待どおりだった。

```text
$ python method/tools/bomdd-job.py --register
stop_type: MISSING_INPUT
source: 導出: --register に値がない(引数不正)
exit 0

$ python method/tools/bomdd-job.py ECO-999 --json
{"jobs":[{"eco":{"value":"ECO-999"},"stop_type":{"value":"MISSING_INPUT",...}}]}
exit 0

$ python method/tools/bomdd-witness.py produce --eco ECO-902 --gate malformed --out outside.json
引数不正: --gate の形式不正: 'malformed'(...)
exit 2

$ python method/tools/bomdd-witness.py verify --eco
引数不正: --eco に値がない
exit 2
```

null register エントリは `load_register` の戻りだけを差し替えたコード単位 probe で確認した。

```text
count=2
stops=['MISSING_INPUT', 'NONE']
sources=[
  '導出: register エントリが object でない: None',
  '導出: register と order の状態に矛盾なし'
]
```

該当実装: `method/tools/bomdd-job.py:192-225`、`method/tools/bomdd-witness.py:177-208,318-361`

null を含む実 register fixture の CLI 試験は temp 作成不能のため未検査。したがって **partially**。

## r1 8腕回帰

独立 temp Git リポでの指定統合回帰は **未検査（検査官環境）**。`tempfile.TemporaryDirectory()` が次で失敗した。

```text
FileNotFoundError: [Errno 2] No usable temporary directory found in
['C:\\Users\\akira\\AppData\\Local\\Temp', ..., 'C:\\Users\\akira\\source\\repos\\BomDD']
```

代替のコード単位 probe では期待値と一致した。

```text
known-good       0  ADVANCE
hash mismatch    1  STOP tree 不一致
FAIL gate        1  STOP gate FAIL 混入
gates empty      1  STOP gates 欠測
stop != NONE     1  STOP stop_type=NORMATIVE_RULING
dirty tree       1  STOP tree 不一致
absent witness   2  witness 読取不能
worktree output  2  作業木内に置けない
```

作業木内出力 `SHOULD-NOT-EXIST.json` は生成されなかった。ただしこれは実 Git/index/tempfile を通しておらず、指定された8腕統合回帰の代用として PASS には数えない。

## 副経路

- `--gate g=0:log.txt:12`: `source` は `log.txt:12` のまま受理された。
- `verify PATH`: 個体照合なしという仕様をコード単位 probe で確認。
- `verify --eco`: 一致時 0、不一致時 1 をコード単位 probe で確認。
- selftest 内の PATH 空腕: `finally` で元の PATH を復元する実装を確認した。ただし selftest 全体がそれ以前の temp 作成で停止するため、その腕への実到達は未検査。
- 通常 PATH での `verify PATH` と `verify --eco` はいずれも IA-06 により traceback・exit 1。

## V2′

PyYAML 6.0.3 が利用可能だったため、実 register で実行した。

```text
$ python method/tools/bomdd-job.py ECO-055 ECO-062 --json
exit 0
JSON.parse: OK
```

実測結果:

```text
ECO-055:
  stop_type = LEDGER_INCONSISTENT
  reason = order にクローズ節(verified)があるが register.status=in-progress

ECO-062:
  stop_type = NONE
  reason = register と order の状態に矛盾なし
```

両 job とも15欄すべてに非空の `source` が存在した。`required_skills`、`required_capability`、`forbidden`、`expected_outputs`、`independent_inspection` は `null + source none(Fn...)` で、order 散文からの値転写は認めなかった。V2′は **observed PASS**。

## diff 監査

```text
$ git diff --name-status 1eefe35..37057e5a7820254cad119a31837cbe8676ede926
M  bomdd/60-change-order-eco-062.md
M  bomdd/60-change-register.yaml
A  bomdd/reports/independent-inspection-eco-062.md
M  method/tools/bomdd-job.py
M  method/tools/bomdd-witness.py
```

差分は製造物2ファイルと台帳系（order、register、r1検査報告）の5ファイルだけだった。既存 hook、self-conformance、README、AGENTS、skills、その他の method ファイルに差分はない。指定窓の diff 監査は **PASS**。

## selftest と V4

### witness selftest

```text
$ python method/tools/bomdd-witness.py --selftest
exit 1
Traceback:
FileNotFoundError: No usable temporary directory found
```

### job selftest

```text
$ python method/tools/bomdd-job.py --selftest
exit 1
Traceback:
FileNotFoundError: No usable temporary directory found
```

両方とも fixture の temp 作成前提で停止した。製品ロジックの FAIL ではなく検査官環境による **測定成立性 unknown** だが、PASS には数えない。

### self-conformance

```text
$ python method/tools/self-conformance.py
[C1] PASS YAML 66 件
[C2] PASS JSON 32 件
exit 1
C3 の陽性対照用 tempfile.mkdtemp で FileNotFoundError
```

C3以降は未実行。V4 self-conformance は **unknown**。

### CI

```text
$ gh run list --repo akiramei/BomDD --limit 3
exit 1
dial tcp ... connectex: socket access forbidden
```

CI はネットワーク制約により **unknown**。製造者申告を PASS の代用にしていない。

## selftest が測っていない枝

witness selftest が未被覆の主な枝:

- OS temp/index の作成不能と cleanup 失敗
- CLI の `verify PATH` / `verify --eco` の end-to-end 引数配線
- source に `:` を含む座標
- malformed JSON、top-level 非object、gate 非object、文字列・float exit
- linked worktree、symlink、ignored file、同時更新、非ASCIIパス

job selftest が未被覆の主な枝:

- selector なし・未知 option（IA-07）
- main の実 stdout を標準 JSON parserへ渡す end-to-end 経路
- 不正 YAML、重複 ECO ID、必要キー欠落、複数 `--register`
- 実 register の ECO-055/ECO-062
- クローズ見出しのMarkdown変種、非ASCIIパス、同時更新

## 新規所見

### IA-06 — temp/index 作成不能を測定不能へ分類できず traceback・exit 1

- severity: **medium**
- evidence class: **実 CLI コマンド+出力 / コード読解**
- 該当行: `method/tools/bomdd-witness.py:77-96,123-157,318-357`
- 内容: `_git()` は `OSError` を捕捉するが、`tempfile.TemporaryDirectory()` の `OSError` は捕捉しない。tree 測定に必要な一時 index を作れないと、契約した exit 2 ではなく traceback・exit 1 になる。
- 再現:

```text
$ python method/tools/bomdd-witness.py verify --eco ECO-062
FileNotFoundError: No usable temporary directory found ...
exit 1

$ python method/tools/bomdd-witness.py verify .git/bomdd-witness/ECO-062.json
FileNotFoundError: No usable temporary directory found ...
exit 1

$ python method/tools/bomdd-witness.py produce --eco ECO-902 --gate g=0:log.txt:12 --out IA06-NO-WRITE.json
FileNotFoundError: No usable temporary directory found ...
exit 1
```

出力ファイルは生成されなかった。fail-open ではないが、0/1/2 の機械契約を壊し、STOP と測定不能を消費側が区別できない。

### IA-07 — job の selector なし・未知 option が空 jobs として黙って成功する

- severity: **low**
- evidence class: **実 CLI コマンド+出力 / コード読解**
- 該当行: `method/tools/bomdd-job.py:200-225,228-239`
- 内容: `select()` の自己記述は「引数不正を MISSING_INPUT レコードにする」だが、ECO IDも `--all` もない場合や未知 option を検出せず、空配列を返す。
- 再現:

```text
$ python method/tools/bomdd-job.py --json
{"register":"bomdd/60-change-register.yaml","jobs":[]}
exit 0

$ python method/tools/bomdd-job.py --bogus --json
{"register":"bomdd/60-change-register.yaml","jobs":[]}
exit 0
```

read-only 射影なので直接の遷移 fail-open ではないが、運転員は「対象なし」と「入力誤り」を区別できない。`MISSING_INPUT` レコード化または明示的な引数拒否が必要。

## /calibrate receipt

| 査定した主張 | 測定成立性 | 証拠資格 | 根拠・帰結 |
|---|---|---|---|
| IA-03 の git 不在分類 | observed | 適格 | verify/produce とも exit 2、traceback なし |
| IA-04 の複数 JSON | observed | 適格 | 実 register、複数指定と `--all` の双方で `JSON.parse` 成功 |
| IA-01/02/05 の是正 | observed（一部コード単位） | 条件付き適格 | 修正ロジックは期待一致。temp Git リポのCLI統合経路は未測定 |
| r1 8腕回帰 | unknown (`NO_WRITABLE_OS_TEMP`) | — | コード単位 probe は一致したが、指定統合試験の根拠には不使用 |
| V2′ | observed | 適格 | 実 register、期待停止種別、全欄source、散文転写なし |
| diff 窓 | observed | 適格 | 指定5ファイルだけ |
| selftest両方 / self-conformance | unknown (`NO_WRITABLE_OS_TEMP`) | — | traceback・exit 1。PASSに数えない |
| CI | unknown (`NETWORK_DENIED`) | — | APIへ到達不能 |
| witness の0/1/2契約 | observed | 不適格 | IA-06 により通常 PATH のtemp不能がexit 1 |
| job の不正入力分類 | observed | 条件付き適格 | 指定IA-05経路は改善、未検枝でIA-07 |

- 検出した計器欠陥と帰属: IA-06、IA-07 は製造物帰属。OS temp書込み禁止とネットワーク禁止は検査官環境帰属。
- battery:
  - Q1 **asked**
  - Q2 **asked**
  - Q3 **asked**
  - Q4 **asked**
  - Q5 **asked**
  - Q6 **asked**
  - Q7 **asked**
  - Q8 **NA**
  - Q9 **asked**
  - Q10 **asked**
  - Q11 **asked**
- 帰結: IA-06 が機械終了コード契約を反証し、必須統合試験も unknown のため **REJECT**。IA-07 は追加是正対象。

## 未検査

- OS temp の独立 Git リポによる r1 8腕の end-to-end 回帰。
- IA-01の構造不完全JSON、IA-02の別ECOファイルコピー、IA-05のnull registerを用いた同一CLI再現。
- selftest両方のfixture到達後、self-conformance C3以降、対象 revision のCI結論。
- Linux、linked worktree、symlink、submodule、ignored file、同時更新、非ASCIIパス。

## この検査が支持しないもの

本検査は、temp Git リポを使う8腕統合回帰・selftest・self-conformanceの合格を支持しない。  
witness の改竄耐性、gate申告値の真実性、全Git構成でのtree同一性を支持しない。  
CI、未検枝、未知の入力クラスに欠陥がないことを支持しない。