[INFORM / COMPLETE]

REJECT — 理由: IA-01、IA-02、IA-03、IA-04、IA-05、IA-06、IA-07。

検査対象は HEAD `a43c7f8eb81bf8aa17325d5a7deff061c16dfa60`、差分基線は `c180cc8`。Windows・pwsh・workspace-write で、fixture、ledger、witness は OS temp に作成した。リポジトリ本体は変更しておらず、終了時 `git diff --exit-code` は exit 0。

## 所見

### IA-01 — 壊れた JSONL 行が黙って無視され、別行の ACCEPT gate が生成される

再現コマンド:

```powershell
Set-Content $L @(
  $rejectRow,
  '{broken',
  $acceptCorrectiveRow
)
python method/tools/bomdd-witness.py produce `
  --eco ECO-900 --out $W --inspection-from-ledger
$rc=$LASTEXITCODE
```

観測:

```text
ADVANCE PRODUCED: witness 生成: …(gates 2・stop NONE)
exit=0
inspection={"exit":0,"verdict":"ACCEPT","range":"是正確認+回帰","run_id":"r2"}
```

期待との差: `inspection_gate_from_ledger()` は JSON decode 失敗を `continue` で捨てる。追記途中・破損した最終行があっても、それ以前または以後の ACCEPT を採用できる。台帳破損は測定不能として `ARG_ERROR` にするのが fail-closed な入力検証であり、黙って有効行だけを選ぶ仕様は ECO-074 に明記されていない。

帰属: 製造物（`method/tools/bomdd-witness.py:228-231`）。

### IA-02 — 台帳行の ECO identity を照合せず、別 ECO の行から exit 0 gate を生成する

再現コマンド:

```powershell
# $L は .git/bomdd-run/ECO-900.jsonl
Set-Content $L $rowWhoseEcoIsECO999
python method/tools/bomdd-witness.py produce `
  --eco ECO-900 --out $W --inspection-from-ledger
$rc=$LASTEXITCODE
```

観測:

```text
ADVANCE PRODUCED: witness 生成: …(gates 1・stop NONE)
exit=0
inspection={"exit":0,"verdict":"ACCEPT","run_id":"rX"}  # row.eco=ECO-999
```

期待との差: ファイル名 `ECO-900.jsonl` だけに依存し、選択した cell 行の `eco` を要求個体と照合しない。別プロセスが書いた行を ECO-900 の inspection gate として採用できる。

帰属: 製造物（`method/tools/bomdd-witness.py:226-235`）。

### IA-03 — ledger 内の report.path に入口と同じ境界検証がなく、作業木外の報告から exit 0 gate を生成する

再現コマンド:

```powershell
'ACCEPT' | Set-Content $externalReport
$sha=(Get-FileHash -Algorithm SHA256 $externalReport).Hash.ToLowerInvariant()
# report.path=$externalReport（絶対パス）の ACCEPT/是正確認+回帰 row を $L へ記録
python method/tools/bomdd-witness.py produce `
  --eco ECO-900 --out $W --inspection-from-ledger
$rc=$LASTEXITCODE
```

観測:

```text
ADVANCE PRODUCED: witness 生成: …(gates 1・stop NONE)
exit=0
source=C:\Users\akira\AppData\Local\Temp\eco074-external-….md
```

期待との差: `bomdd-run --report` が拒否する絶対パス・作業木外パスを witness 側は再検証しない。別プロセスが書いた、正規の入口では生成不能な行から受入可能な gate が作られる。

帰属: 製造物（`method/tools/bomdd-witness.py:237-255`）。ECO-073 の report path 境界とも不整合。

### IA-04 — SHA 欠落を exit 2 のときだけ受理する

再現コマンド:

```powershell
# verdict=ACCEPT, range=境界探索, sha256=null, path=reports/r.md
Set-Content $L $acceptBoundaryWithoutShaRow
python method/tools/bomdd-witness.py produce `
  --eco ECO-900 --out $W --inspection-from-ledger
$rc=$LASTEXITCODE
```

観測:

```text
ADVANCE PRODUCED: witness 生成: …(gates 1・stop NONE)
exit=0
inspection={"exit":2,"verdict":"ACCEPT","sha256":null,"range":"境界探索"}
```

期待との差: ECO-074 §1/§4 は、現在の報告 SHA が台帳と一致しない場合は gate を作らず `ARG_ERROR` とする。SHA がない場合は一致を確認できないが、`ex == 2` なら検証を省略して gate を生成する。短い SHA・大文字 SHA は exit 2/0 の双方で `ARG_ERROR` になったため、欠落だけが例外になっている。

帰属: 製造物（`method/tools/bomdd-witness.py:246-253`）。

### IA-05 — inspection gate が exit 1/2 の decision 台帳で `inspection` が null

再現コマンド:

```powershell
python method/tools/bomdd-witness.py produce --eco ECO-900 `
  --out "$T/.git/bomdd-witness/ECO-900.json" `
  --gate base=0:x --gate inspection=1:r
$prc=$LASTEXITCODE
python method/tools/bomdd-run.py ECO-900 --ledger $ledger
$rrc=$LASTEXITCODE
```

観測:

```text
STOP ECO-900 GATE_FAIL → factory @44e46a490a65
run exit=1; decision=STOP; stop_type=VERIFICATION_FAIL
inspection=null
```

exit 2 でも同じく `STOP … GATE_FAIL → factory`、`inspection=null` だった。

期待との差: 判定と delivery は仕様どおりだが、ECO-074 §4 の製造記録は decision 行を `inspection: {required, inspector, gate}` として記録するとしている。実装は witness の非 0 で先に return するため、失敗した inspection gate が記録されない。

帰属: 製造物（`method/tools/bomdd-run.py:219-245`）。

### IA-06 — ECO-071 の後方互換は判定出力では成立するが、job ビューと decision 記録は同一でない

再現コマンド:

```powershell
git archive --format=zip --output=$oldZip a8ad524
git archive --format=zip --output=$newZip HEAD
# 各 archive を別の temp git repo に展開・commit
python $old/method/tools/bomdd-job.py ECO-071 --json
$orc=$LASTEXITCODE
python $new/method/tools/bomdd-job.py ECO-071 --json
$nrc=$LASTEXITCODE
```

観測:

```text
old_exit=0 new_exit=0 job_json_equal=False
old stop_vocabulary=…INDEPENDENCE_FAIL
new stop_vocabulary=…INDEPENDENCE_FAIL,INSPECTION_MISSING
```

dry の観測:

```text
旧/新とも exit=0、ADVANCE ECO-071 OK → next · dry @TREE
旧 decision inspection=null
新 decision inspection={"required":false}
```

期待との差: 運転結果は後方互換だが、ブリーフが求める「job ビューと dry が同じ」は厳密には成立しない。F6 の source 文言、停止語彙、decision 行の `inspection` 形状が変わる。additive compatibility を意図するなら、その限定を仕様へ記録する必要がある。

帰属: 製造物および影響なし予測の表現。

### IA-07 — witness produce の1行目が80桁を超える

再現コマンド:

```powershell
$line=[string](python method/tools/bomdd-witness.py produce `
  --eco ECO-900 --out "$T/.git/bomdd-witness/ECO-900.json" `
  --gate base=0:x)
$rc=$LASTEXITCODE
$line.Length
```

観測:

```text
exit=0; first_len=178
ADVANCE PRODUCED: witness 生成: C:\Users\akira\AppData\Local\Temp\…(tree …・gates 1・stop NONE)
```

期待との差: 新しい `INSPECTION_MISSING` 判定行は 56 桁で合格したが、`produce` 行は出力先の絶対パスを無制限に含め、80 桁を超えた。

帰属: 製造物（`method/tools/bomdd-witness.py:210`）。

## 仕様どおりだった観測

### 台帳からの導出

| 入力 | produce exit | inspection gate |
|---|---:|---|
| REJECT → ACCEPT | 0 | exit 0、後の ACCEPT |
| ACCEPT → REJECT | 0 | exit 1、後の REJECT |
| ACCEPT → report null | 0 | exit 0、直前の report 付き行 |
| verdict=`accept` | 0 | exit 2 |
| verdict=`MAYBE` | 0 | exit 2 |
| range=`是正確認` | 0 | exit 2 |
| range 欠落 | 0 | exit 2 |
| SHA 短縮・大文字 | 2 | ARG_ERROR、witness なし |
| 別 path・内容不一致 | 2 | ARG_ERROR、witness なし |

### 入口の要求

| 条件 | 結果 |
|---|---|
| verified＋inspector＋inspection なし | `STOP INSPECTION_MISSING → operator`、exit 1、起動なし |
| inspection exit 1/2 | `STOP GATE_FAIL → factory`、exit 1 |
| `Inspection` / `inspection ` | `INSPECTION_MISSING` |
| inspection が 0 と 1 の2個 | 並び順によらず `GATE_FAIL` |
| implemented＋inspector | ADVANCE |
| verified＋inspector なし | ADVANCE |
| inspector が設備台帳にない | `LEDGER_INCONSISTENT` が先行 |

### `--range`

片側のみ、`是正確認`、末尾空白、全角 `＋`、重複はすべて `UNMEASURABLE ARG_ERROR`、exit 2、起動なし、台帳 SHA 不変。正常な境界探索では cell が `BOMDD_RANGE=境界探索` を観測し、台帳 `report.range=境界探索` と一致した。

### 報告変更後の verify

通常の追跡対象報告を書き換えると:

```text
STOP TREE_MISMATCH: tree 不一致(…)
exit=1
```

gitignore 対象の報告を書き換えると:

```text
ADVANCE OK: tree 一致(…)・gates 1 件 exit 0・stop NONE・個体 ECO-900 一致
exit=0
```

`verify` は report SHA を再照合せず、witness の gate を固定値として検証する。これは witness 冒頭の限界 (2)「gate を再実測しない」と (3)「gitignore 対象は tree に入らない」で一般的には明記されている。ただし ECO-074 固有の受理限界としてはまだ記録されていない。

## selftest 被覆表

| 新腕 | selftest が覆う範囲 | 未被覆または不十分な範囲 |
|---|---|---|
| job F6 | inspector あり、inspector なし | 未知 inspector 時の F6 null と停止優先順位を F6 assertion として確認していない |
| witness inspection 11腕 | 正常 ACCEPT 2 range、range 欠落、REJECT、MISSING、UNPARSED、SHA 不一致、報告/台帳/cell 不在、REJECT→ACCEPT | 壊れた JSON 行、ACCEPT→REJECT、末尾 report null、小文字・未知 verdict、語彙外 range、SHA の短縮・大文字・欠落、別内容 path、行の ECO identity、作業木外 path、生成後の report 変更 |
| run range | 片側欠落、語彙外1例、絶対 report path、正常時の台帳 range | 末尾空白・全角記号違い、`--range` 自身の重複を専用腕として未確認 |
| run inspection gate | gate 0、なし、1、2、verified inspector なし、非 verified | 大文字・末尾空白名、0/1 の重複、失敗時の decision `inspection` 欄 |
| 80桁 | run/selftest 判定行 | witness produce 行 |

組込み selftest は3本とも exit 0だったが、上表の未被覆クラスで IA-01〜IA-07 が検出されたため、全 PASS は受理根拠として不十分。

## 較正 receipt

査定主張:

1. 「台帳から導出した inspection gate だけで verified 昇格を制御できる」— observed / 不適格。別 ECO 行・作業木外 path を受理する。
2. 「SHA 再照合で報告との結線が閉じる」— observed / 条件付き適格。正常・短縮・大文字・不一致は弁別するが、exit 2 の SHA 欠落を許す。
3. 「入口の停止判定と配送は仕様どおり」— observed / 適格。ただし失敗時の inspection 記録が欠落。
4. 「既存 ECO は後方互換」— observed / 条件付き適格。判定出力は同じだが JSON/ledger 形状は異なる。

検出した計器欠陥: selftest の未被覆は上表のとおり。帰属は製造物。UNKNOWN を PASS に算入していない。

検出力の限界: 同時 append の競合、symlink/junction、ACL、非 UTF-8 JSONL、プロセス強制終了中の部分書込みタイミングは未測定。外部プロセスによる暗号学的な改竄耐性・独立性判定は範囲外。

| Q | asked/NA | 判定 |
|---|---|---|
| Q1 | asked | 仕様・コメント・実出力を照合 |
| Q2 | asked | ACCEPT/REJECT、SHA 一致/不一致、gate 有/無を対で実測 |
| Q3 | asked | JSON破損・identity・path・SHA・range・gate を独立に落とした |
| Q4 | asked | OS temp の実 git repo、実 JSONL、実報告を使用 |
| Q5 | asked | 実行不能・未実行を合格に数えず |
| Q6 | asked | 各コマンド直後に `$LASTEXITCODE` を記録 |
| Q7 | asked | known-good と known-bad の双方あり |
| Q8 | asked | inspection 欠落と gate 非0の出口・配送を確認 |
| Q9 | asked | HEAD `a43c7f8…` と baseline `c180cc8` を刻印 |
| Q10 | asked | 未測定次元を上記に宣言 |
| Q11 | asked | 語彙・型・順序・identity・path・時間変化を分離 |

## 測れなかったこと

同時書込み競合、symlink/junction、ACL、非 UTF-8 JSONL は測れなかった。指定された1〜7の主要クラスは測定できた。

## 範囲外の観察

- `--gate inspection=0:declared` だけで作った witness は、仕様どおり `ADVANCE` した（exit 0、source=`declared`）。本判定には含めない。
- register 自動遷移、CI、ECO-072 の独立性判定、ECO-073 の報告束ねは再検査していない。

human_action: none。execution: COMPLETE — 境界探索 round の検査と報告を完了した。