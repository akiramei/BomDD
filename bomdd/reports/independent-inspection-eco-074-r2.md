[INFORM / COMPLETE]

ACCEPT — IA-01〜IA-05 の是正を確認し、指定された回帰範囲に差異はありません。

検査対象は HEAD `df0d7c3f8ad1dfee83910b66e74cc76df27a5dcb`。Windows・PowerShell・`workspace-write` 環境で、fixture、ledger、witness は OS temp に作成した。リポジトリ内のファイルは作成・変更・削除していない。終了時の `git status --short` は空、`git diff --exit-code` と `git diff --cached --exit-code` はともに exit 0。

## IA-01 — 壊れた台帳行と非 object

再現コンド:

```powershell
# $L は OS temp fixture の .git/bomdd-run/ECO-074.jsonl
Set-Content $L @('{broken', $validRow)       # 先頭
Set-Content $L @($validRow, '{broken', $validRow) # 中間
Set-Content $L @($validRow, '{broken')       # 末尾
Set-Content $L @('[]', $validRow)            # 非 object

python method/tools/bomdd-witness.py produce `
  --eco ECO-074 --gate self-conformance=0:fixture `
  --inspection-from-ledger --out $OS_TEMP_WITNESS
$rc=$LASTEXITCODE
```

観測:

```text
先頭: UNUNMEABLE ARG ARG_ERROR: run: …壊れた行がある(1 行目)…
中間: UNMEURABLEABLE ARG ARG_ERROR:: …壊れた行がある(2 行目)…
末尾: UNMEURABLEABLE ARG_ERROR: …壊れた行がある(2 行目)…
非 object: UNMEASURABLE ARG_ERROR: …1 行目が object でない
すべて exit=2、WITNESS_EXISTS=False
```

空行を先頭・末尾に置いた対照では exit 0、inspection gate は `exit:0` で生成された。

期待との差: なし。IA-01 は是正済み。

## IA-02 — ECO 個体照合

再現コマンド:

```powershell
# ECO-074.jsonl の選択行に eco=ECO-073 を記録
python method/tools/bomdd-witness.py produce `
  --eco ECO-074 --gate self-conformance=0:fixture `
  --inspection-from-ledger --out $OS_TEMP_WITNESS
$rc=$LASTEXITCODE
```

観測:

```text
UNMEASURABLE ARG_ERROR: …台帳の cell 行の個体が一致しない:
'ECO-073' != ECO-074
exit=2、WITNESS_EXISTS=False
```

期待との差: なし。IA-02 は是正済み。

## IA-03 — report.path 境界

再現コマンド:

```powershell
# report.path を各値に置換して produce を個別実行
# 絶対パス / ../outside.md / .git/x.md /
# " bomdd/…" / "bomdd/… " / bomdd//reports/x.md /
# junction 経由の作業木外 linkout/r.md

python method/tools/bomdd-witness.py produce `
  --eco ECO-074 --gate self-conformance=0:fixture `
  --inspection-from-ledger --out $OS_TEMP_WITNESS
$rc=$LASTEXITCODE
```

観測:

| path クラス | 観測 |
|---|---|
| 絶対、`..`、前後空白、空要素 | `ARG_ERROR: report.path がリポ相対でない`、exit 2 |
| `.git/` 配下 | `ARG_ERROR: .git 配下を指す`、exit 2 |
| junction 経由の作業木外 | `ARG_ERROR: 作業木の外を指す`、exit 2 |
| 正常なリポ相対 path | produce exit 0、inspection gate exit 0 |

不正ケースはすべて witness なし。

期待との差: なし。IA-03 は是正済み。作業木外判定は実 junction を使って確認した。

## IA-04 — SHA-256 の形状

再現コマンド:

```powershell
# verdict=ACCEPT/REJECT/UNPARSED で sha256 を
# null、"abcd"、64桁大文字へ変更
# verdict=MISSING では sha256=null / 正常SHA の双方を確認

python method/tools/bomdd-witness.py produce `
  --eco ECO-074 --gate self-conformance=0:fixture `
  --inspection-from-ledger --out $OS_TEMP_WITNESS
$rc=$LASTEXITCODE
```

観測:

| 入力 | 観測 |
|---|---|
| ACCEPT: sha 欠落・短縮・大文字 | `ARG_ERROR: 64 桁小文字 hex`、exit 2、witness なし |
| REJECT/UNPARSED: sha 欠落 | 同上 |
| MISSING: sha なし | produce exit 0、inspection gate exit 2、`sha256:null` |
| MISSING: sha あり | `ARG_ERROR: MISSING 行に sha256 がある`、exit 2、witness なし |

期待との差: なし。IA-04 は是正済み。

## IA-05 — 失敗 gate の decision 記録

再現コマンド:

```powershell
python method/tools/bomdd-witness.py produce `
  --eco ECO-074 --out $OS_TEMP_WITNESS `
  --gate self-conformance=0:fixture `
  --gate inspection=1:fixture-report
$prc=$LASTEXITCODE

# OS temp fixture の既定 witness 位置へ配置
python method/tools/bomdd-run.py ECO-074 --ledger $OS_TEMP_LEDGER
$rrc=$LASTEXITCODE
```

inspection exit 2 と gate なしも同様に個別実行した。

観測:

```text
inspection exit 1:
STOP ECO-074 GATE_FAIL → factory
run exit=1
inspection={"required":true,"inspector":"EQ-002",
            "gate":{"name":"inspection","exit":1,…}}

inspection exit 2:
STOP ECO-074 GATE_FAIL → factory
run exit=1
inspection={"required":true,"inspector":"EQ-002",
            "gate":{"name":"inspection","exit":2,…}}

inspection なし:
STOP ECO-074 INSPECTION_MISSING → operator
run exit=1
inspection={"required":true,"inspector":"EQ-002","gate":null}
```

失敗 gate の decision は `stop_type=VERIFICATION_FAIL`、`delivery=factory` を維持した。

期待との差: なし。IA-05 は是正済み。

## 回帰 — 台帳からの導出

| 入力 | 観測 |
|---|---|
| REJECT → ACCEPT | produce exit 0、後の ACCEPT、gate exit 0、`run_id=r2` |
| ACCEPT → REJECT | produce exit 0、後の REJECT、gate exit 1 |
| ACCEPT → report null | 直前の report 付き行、gate exit 0 |
| verdict=`accept` / `MAYBE` | produce exit 0、gate exit 2 |
| range=`是正確認` / 欠落 | produce exit 0、gate exit 2 |
| SHA 短縮・大文字 | exit 2、ARG_ERROR、witness なし |
| 別 path・内容不一致 | exit 2、`sha256 が台帳と一致しない`、witness なし |

r1 の表から変化なし。

## 回帰 — 入口の要求

| 条件 | 観測 |
|---|---|
| verified＋inspector＋gate なし | `INSPECTION_MISSING → operator`、exit 1 |
| inspection exit 1/2 | `GATE_FAIL → factory`、exit 1 |
| `Inspection` / `inspection ` | `INSPECTION_MISSING` |
| inspection 0 と 1 の重複 | 並び順によらず `GATE_FAIL` |
| implemented＋inspector | `ADVANCE … dry`、exit 0 |
| verified＋inspector なし | `ADVANCE … dry`、exit 0 |
| 未登録 inspector | `job:LEDGER_INCONSISTENT → ledger-owner` が先行 |

r1 の表から変化なし。

## 回帰 — `--range`

再現コマンドの形:

```powershell
python method/tools/bomdd-run.py ECO-071 `
  --ledger $OS_TEMP_LEDGER --cell $CELL --executor EQ-002 `
  --report bomdd/reports/range.md --range $VALUE
$rc=$LASTEXITCODE
```

片側のみ、`是正確認`、末尾空白、全角 `＋`、重複の6ケースはすべて `UNMEASURABLE ARG_ERROR`、exit 2、ledger 不生成だった。

正常な `境界探索` は OS temp fixture の cell が `BOMDD_RANGE=境界探索` を観測し、台帳も次の値を記録した。

```text
cell exit 0
report ACCEPT sha256:bd3ba6fb4ec4 (EQ-002)
run exit=0
report.range="境界探索"
```

r1 の表から変化なし。

## 3ツールの selftest

```powershell
python method/tools/bomdd-witness.py --selftest
$rc=$LASTEXITCODE
python method/tools/bomdd-run.py --selftest
$rc=$LASTEXITCODE
python method/tools/bomdd-job.py --selftest
$rc=$LASTEXITCODE
```

観測: 3本とも PASS、各 `$LASTEXITCODE=0`。

## job 射影と ECO-071 後方互換

```powershell
python method/tools/bomdd-job.py ECO-074 --json
$rc=$LASTEXITCODE
```

観測:

```json
"required_capability": {
  "value": {"producer":"EQ-001","inspector":"EQ-002"}
},
"independent_inspection": {
  "value": {"required":true,"inspector":"EQ-002"}
}
```

exit 0。

ECO-071 は `required_capability.value=null`、`independent_inspection.value=null`。旧基線 `a8ad524` と現個体を別々の OS temp fixture で実行し、双方とも次の判定だった。

```text
ADVANCE ECO-071 OK → next · dry @TREE
exit=0
```

decision の additive 差は r1 の受理判定どおり、旧 `inspection:null`、現 `{required:false}`。判定・配送・dry 出力形式は不変。

実リポの既存 ECO-071 witness は現 tree と一致せず `TREE_MISMATCH` だったため、旧新比較は各 revision から作成した fresh witness を使う OS temp fixture で実施した。比較対象は測定できた。

## 較正 receipt

査定した主張:

1. 「IA-01〜04 の不正入力を fail-closed に拒否する」— observed / 適格。
2. 「inspection gate の失敗値を停止時にも decision 行へ残す」— observed / 適格。
3. 「r1 で正常だった導出・入口・range の挙動を維持する」— observed / 適格。
4. 「配員欄なしの既存 ECO の運転判定は後方互換」— observed / 適格。JSON の additive 差は仕様に明記済み。

検出した計器欠陥: なし。

検出力の限界: 同時 append、ACL、非 UTF-8 JSONL、プロセス強制終了中の部分書込みは今回の限定 range では測定していない。junction 経由の作業木外 path は測定済み。

| Q | asked/NA | 判定 |
|---|---|---|
| Q1 | asked | order §5.1、コード、CLI 出力を照合 |
| Q2 | asked | 正常・不正入力、gate 0/1/2、有無を対で実測 |
| Q3 | asked | IA-01〜05 を入力クラス別に独立実行 |
| Q4 | asked | OS temp の実 git repo、実 JSONL、実報告を入力 |
| Q5 | asked | 実行拒否や未実行を PASS に算入せず |
| Q6 | asked | 各コマンド直後に `$LASTEXITCODE` を取得 |
| Q7 | asked | known-good と known-bad の双方を使用 |
| Q8 | asked | gate 欠落・非0の停止先を確認 |
| Q9 | asked | 対象 HEAD と旧基線を revision 単位で分離 |
| Q10 | asked | 未測定次元を上記に宣言 |
| Q11 | asked | 型、順序、identity、path、sha、range、状態を分離 |

## 測れなかったこと

指定された IA-01〜05 と回帰項目に測定不能はない。上記の同時書込み、ACL、非 UTF-8、強制終了タイミングは本 round の範囲外。

## 範囲外の観察

- `verify` による報告 SHA の再照合、申告 gate、witness の80桁契約は再検査していない。ECO-074 §6 に記録すべき既知の限界・運用規律として判定から除外した。
- 新しい入力クラスの探索は行っていない。

human_action: none。execution: COMPLETE — 「是正確認+回帰」の独立検査を完了した。