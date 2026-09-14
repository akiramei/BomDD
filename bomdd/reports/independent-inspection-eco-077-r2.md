[INFORM / COMPLETE]

ACCEPT — 指定 7 項目はすべて同一 revision の r1 と一致。是正対象は 0 件、製造物帰属の新規所見は 0 件。

- range: 是正確認+回帰（指定 7 項目のみ）
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象 revision: `5917e29bbeb0fa56ffddf4d6d4ab78e76a83d74a`
- commit: 開始・終了とも同 revision（commit 0）
- 報告出力先: `bomdd/reports/independent-inspection-eco-077-r2.md`
- 報告ファイルへの検査官による書込み: 0（本最終メッセージを CLI が `-o` で保存する）

開始時 `git status --short`:

```text
 M bomdd/60-change-order-eco-077.md
A  bomdd/reports/independent-inspection-eco-077.md
```

終了時 `git status --short`:

```text
 M bomdd/60-change-order-eco-077.md
A  bomdd/reports/independent-inspection-eco-077.md
```

開始・終了は同一。上記 order の unstaged 変更と r1 報告の staged 追加は開始前から存在し、検査官による製品・register・order・r1 報告への追加差分は 0。本報告出力先は、終了時 status 採取後に CLI が本メッセージを保存するため、この観測時点では未生成。

## /preflight receipt

- task classification: continuation。r1 の検査個体について、受理側が指定した回帰 7 項目を同一 revision で再測定する作業。
- 最小契約:
  - baseline: `5917e29bbeb0fa56ffddf4d6d4ab78e76a83d74a` — confirmed（`git rev-parse HEAD` と指定 revision が一致）
  - current-work-state: r1 ACCEPT・所見 0、r2 再実施待ち — confirmed（r1 報告・order §5.2）
  - unresolved-items: 前回 r2 は保存報告の証拠不足。報告ファイルを直接書かず最終メッセージへ全文を置く処置 — confirmed（order §5.2）
  - handoff-state: 本ブリーフ、r1 報告、order から再構成 — confirmed
  - acceptance-target: 本ブリーフの指定 7 項目で r1 との一致/不一致を判定 — confirmed
- repo 固有前提: 追加なし。
- discovered prerequisite: 開始時と終了時の status、HEAD、報告ファイル非接触 — confirmed。
- 開始判定: PROCEED。
- override: なし。

## 1. selftest 3 本

再現コマンド:

```powershell
python method/tools/bomdd-job.py --selftest
python method/tools/bomdd-run.py --selftest
python method/tools/bomdd-witness.py --selftest
```

観測:

```text
bomdd-job selftest PASS(... F7〔ECO-077〕: roles 必須キー・by_role 陽性/陰性・map 不在= unknown・receipt_author_role 射影〔文字列のみ・欄なし null・stop/required 不変〕・roles 欠落/空/語彙外/重複/非配列/大文字= MAP_INVALID・語彙内 2 語= 通過)
EXIT=0

ADVANCE OK: selftest PASS(起動4/dry2/kb5/job1/不能3/独立性9/報告27/gate6/構文5/台帳3/引数13/表)
EXIT=0

ADVANCE OK: selftest PASS(known-good / hash・fail・missing・stop・dirty・不完全 gate・個体不一致 ... / inspection-from-ledger〔ECO-074〕 ...)
EXIT=0
```

`bomdd-run` の初回呼出しは完了情報を返さなかったため証拠に採用せず、単独で再実行して exit 0 と PASS 文言を観測した。

r1 との一致: 一致。3 本とも exit 0、PASS。`bomdd-job` の PASS 文言に F7 を含む。

## 2. known-bad: roles 欠落

再現コマンド:

```powershell
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()
$env:PYTHONIOENCODING='utf-8'
@'
import importlib.util
import shutil
import tempfile
from pathlib import Path
import yaml

repo = Path.cwd()
src = repo / 'method/templates/product-profile/skills/activation-map.yaml'
spec = importlib.util.spec_from_file_location(
    'bomdd_job', repo / 'method/tools/bomdd-job.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with tempfile.TemporaryDirectory(prefix='eco077-r2-') as td:
    bad = Path(td) / 'activation-map.yaml'
    shutil.copy2(src, bad)
    data = yaml.safe_load(bad.read_text(encoding='utf-8'))
    target = data['classes'][0]
    class_id = target['id']
    del target['roles']
    bad.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding='utf-8'
    )
    classes, error = mod.load_map(bad, repo)
    print(f'class={class_id}')
    print(f'classes={classes}')
    print(f'error={error}')
    raise SystemExit(
        0 if classes is None
        and error
        and 'MAP_INVALID' in error
        and 'roles' in error
        else 1
    )
'@ | python -
```

観測:

```text
class=start
classes=None
error=activation-map 不正(MAP_INVALID): class 'start': roles が非空の文字列配列でない
EXIT=0
```

r1 との一致: 一致。OS temp の複製 map から `start.roles` を削除すると、`load_map` は `classes=None` と MAP_INVALID を返した。実 map は変更していない。

## 3. ECO-076 job 射影

再現コマンド:

```powershell
python method/tools/bomdd-job.py ECO-076 --json
```

観測:

```yaml
required_skills:
  - calibrate
  - preflight
required_skills_by_role:
  inspector:
    - calibrate
  producer:
    - calibrate
    - preflight
receipt_author_role: null
stop_type: NONE
EXIT: 0
```

r1 との一致: 一致。4 欄すべて r1 の値と同一。

## 4. 旧版との全 register entry 比較

再現コマンド:

```powershell
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()
$env:PYTHONIOENCODING='utf-8'
@'
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
import yaml

repo = Path.cwd()
register = yaml.safe_load(
    (repo / 'bomdd/60-change-register.yaml').read_text(encoding='utf-8')
)
entries = register if isinstance(register, list) else register.get(
    'changes', register.get('entries', [])
)
ids = [entry['id'] for entry in entries]

with tempfile.TemporaryDirectory(prefix='eco077-r2-old-') as td:
    td = Path(td)
    archive = td / 'old.zip'
    oldroot = td / 'old'
    oldroot.mkdir()

    with archive.open('wb') as stream:
        proc = subprocess.run(
            ['git', 'archive', '--format=zip', '940e757'],
            cwd=repo,
            stdout=stream,
            stderr=subprocess.PIPE
        )
    if proc.returncode:
        raise SystemExit(proc.returncode)

    with zipfile.ZipFile(archive) as package:
        package.extractall(oldroot)

    shutil.copy2(
        repo / 'bomdd/60-change-register.yaml',
        oldroot / 'bomdd/60-change-register.yaml'
    )
    for source in (repo / 'bomdd').glob('60-change-order-eco-*.md'):
        shutil.copy2(source, oldroot / 'bomdd' / source.name)

    def project(root, eco):
        proc = subprocess.run(
            ['python', 'method/tools/bomdd-job.py', eco, '--json'],
            cwd=root,
            text=True,
            encoding='utf-8',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if proc.returncode:
            raise RuntimeError(
                f'{root}:{eco}:rc={proc.returncode}:{proc.stderr}'
            )
        return json.loads(proc.stdout)['jobs'][0]

    differences = []
    missing = []

    for eco in ids:
        old = project(oldroot, eco)
        new = project(repo, eco)

        if old['required_skills']['value'] != new['required_skills']['value']:
            differences.append(eco)

        for field in ('required_skills_by_role', 'receipt_author_role'):
            if field not in new:
                missing.append(f'{eco}:{field}')

    print(f'entries_compared={len(ids)}')
    print(f'required_skills_difference_count={len(differences)}')
    print(f'new_field_missing_count={len(missing)}')
    print(f'required_skills_differences={differences}')
    print(f'new_field_missing={missing}')
'@ | python -
```

観測:

```text
entries_compared=77
required_skills_difference_count=0
new_field_missing_count=0
required_skills_differences=[]
new_field_missing=[]
EXIT=0
```

旧版個体は `940e757` を OS temp へ archive 展開し、現 register と各 order を temp 個体へ複製して全 77 ID を個別に射影した。最初に試した `--all` は処理対象 1 件だけを返したため、全件比較の証拠には採用していない。

r1 との一致: 一致。比較件数 77、`required_skills` 差分 0、新欄欠落 0。

## 5. factory-delegate 正本・写し

再現コマンド:

```powershell
git diff --no-index --unified=0 -- `
  method/templates/product-profile/skills/factory-delegate.md `
  .claude/skills/factory-delegate/SKILL.md
```

観測:

```diff
@@ -8 +8,5 @@
-正典: `{{METHOD}}/method/templates/product-profile/skills/factory-delegate.md`(本ファイルの配布元)。
+> **本ファイルは写しである。正本は [`method/templates/product-profile/skills/factory-delegate.md`](../../../method/templates/product-profile/skills/factory-delegate.md)。**
+> BomDD は `bomdd-init` の配布先ではないため、正本を置いても `.claude/skills/` には入らない。
+> **同期規則**: 変更は必ず**正本側**へ入れ、本ファイルへ反映する(プレースホルダーは自リポ相対へ解決する)。
+> 本ファイルだけを直接編集しない — 配布元と分岐すると、どちらかが必ず腐る。
+> 由来: ECO-063(D-1 前例= ECO-042 / ECO-032 の踏襲)。ユーザー階層 `~/.claude/skills/factory-delegate/` の旧写しは本ファイルへ統合(利用者が削除)。

@@ -10 +14 @@
-`{{METHOD}}/method/bomdd-playbook-v1.md` §5.1(隔離ファクトリ)・§8.1(工場運用の隔離規律)。
+`method/bomdd-playbook-v1.md` §5.1(隔離ファクトリ)・§8.1(工場運用の隔離規律)。
EXIT=1
```

exit 1 は `--no-index` で差分が存在することを示す期待値。差分は 2 hunk のみ。

再現コマンド:

```powershell
rg -n -F '{{METHOD}}' .claude/skills/factory-delegate/SKILL.md
```

観測:

```text
（出力なし）
EXIT=1
```

`rg` exit 1 は一致 0 件。

r1 との一致: 一致。正本・写しの差分は既知 2 hunk のみ、写しの `{{METHOD}}` は 0 件。

## 6. register テンプレ

再現コマンド:

```powershell
python -c "import pathlib,yaml; p=pathlib.Path('method/templates/60-change-register.yaml'); d=yaml.safe_load(p.read_text(encoding='utf-8')); print(type(d).__name__, type(d.get('changes')).__name__, len(d.get('changes', [])))"
```

観測:

```text
dict list 1
EXIT=0
```

再現コマンド:

```powershell
rg -n "receipt_author_role" method/templates/60-change-register.yaml
```

観測:

```text
32:    # receipt_author_role: producer   # 任意・観測欄(BomDD ECO-077): 受入時の較正 receipt を書いた役割。producer= 製造者の自己較正 /
EXIT=0
```

r1 との一致: 一致。テンプレは YAML としてパース可能で、`receipt_author_role` のコメント行が存在する。

## 7. 対象 revision・製造物差分

再現コマンド:

```powershell
git rev-parse HEAD
git diff 5917e29 --stat
```

観測:

```text
5917e29bbeb0fa56ffddf4d6d4ab78e76a83d74a
```

```text
 bomdd/60-change-order-eco-077.md                |  24 +++
 bomdd/reports/independent-inspection-eco-077.md | 222 ++++++++++++++++++++++++
 2 files changed, 246 insertions(+)
EXIT=0
```

差分は受理側が開始前に置いた order 更新と staged r1 報告だけで、ECO-077 の製造物ファイルは出現しない。HEAD は指定 revision と完全一致。

r1 との一致: 一致。対象 revision は r1 から動いておらず、製造物ファイルの差分は 0。

## 総合判定

指定 7 項目はすべて r1 と一致した。是正対象は r1 で 0 件であり、本 round でも製造物帰属の所見は 0 件。

検査官によるリポジトリ変更は 0、commit は 0。開始時・終了時 status は同一で、register と order の受入節には接触していない。

## 較正 receipt

### 査定した主張と判定

- 主張: revision `5917e29bbeb0fa56ffddf4d6d4ab78e76a83d74a` について、指定 7 回帰項目の観測が r1 と一致する。
- 測定成立性: observed。
- 証拠資格: 条件付き適格。指定 7 項目の一致判定には適格だが、range 外の品質・受入条件全体を証明しない。
- 根拠: 各項目の上記再現コマンド、終了コード、観測値、および開始・終了の HEAD/status。

### 検出した計器欠陥と帰属

- 製造物の計器欠陥: なし。
- 初回 `bomdd-run --selftest` 呼出しの完了情報欠落: 実行ハーネス側の観測不成立。PASS に数えず、単独再実行の exit 0/PASS を証拠に採用した。
- `--all --json` が 1 件だけを返すこと: CLI の処理対象選択仕様であり、全台帳比較の計器としては不十分。全 77 ID の個別投入へ切り替えた。製造物欠陥としては扱わない。

### battery

- Q1 asked — 主張を受理側指定の 7 項目と r1 一致に限定し、受入全体へ拡張していない。
- Q2 asked — 現 revision の selftest 緑と、roles を除去した OS-temp known-bad の MAP_INVALID を対で実測した。
- Q3 asked — 7 項目を個別に判定した。これは指定範囲の回帰確認であり、契約全項の独立故障注入ではない。
- Q4 asked — 複製 map を実際に `load_map` へ入力し、旧版比較も旧 script 個体へ各 ID を実投入した。
- Q5 asked — 完了情報のない初回 selftest と、全件にならない `--all` 結果を合格証拠に数えていない。
- Q6 asked — 各検査の終了コードを観測してから次の検査へ進み、未完了の実行は単独再実行した。
- Q7 asked — roles 欠落の陽性対照を実測した。
- Q8 NA — 予防ゲートや免除経路は本 range で評価していない。
- Q9 asked — HEAD の完全 hash を開始・終了に突合し、旧版は `940e757` の archive 個体を使用した。
- Q10 asked — 下記の検出力限界を宣言した。
- Q11 asked — selftest、known-bad、射影、全件回帰、文書同期、YAML、revision 差分を別入力クラスとして測定した。

### 検出力の限界

- 受理側指定の 7 項目以外は測定していない。
- self-conformance、CI、V4〜V6 の成立、既定 `bomdd-run` 統合経路、POSIX、並行実行、網羅的 fuzz は本 round の証拠に含まない。
- roles 欠落以外の map 不正入力は再注入していない。これらは r1 の境界探索結果を再測定する指定に含まれない。
- `git diff --stat` は差分パスと量を測るが、range 外の意味的正しさや履歴外の状態を測らない。
- 開始・終了 status の一致は検査官による残存差分 0 を示すが、CLI が本メッセージを報告出力先へ保存する処理は終了時 status 採取後に行われる。

human_action: none  
execution state: 指定範囲の独立検査 r2 は完了。未実施の range 内項目なし。