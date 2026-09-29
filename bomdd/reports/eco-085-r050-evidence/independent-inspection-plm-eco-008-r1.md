[INFORM / COMPLETE]

REJECT IA-01, IA-02, IA-03, IA-04, IA-05

- range: 境界探索
- inspector: OpenAI GPT-5 / Codex API harness
- 対象 revision: `59941479c45d22ab0ada1ed369e95365538e441a`
- 比較基準: `eco-008-input`
- range 内 commit 数: 2
- 検査中 commit 数: 0
- 実行環境: Node.js `v22.13.1` / npm `11.5.2`
- 外部 API・ネットワーク呼出し: なし。旧個体の依存構築は `npm ci --offline --ignore-scripts`
- 検体・出力: すべて `C:\Users\akira\AppData\Local\Temp\...` 配下
- 開始時 `git status --short`: 出力なし
- 終了時 `git status --short`: 出力なし

## 判定概要

| 項目 | 判定 | 観測 |
|---|---|---|
| `npm run build` | PASS | exit 0、警告 0 |
| `node --test` | PASS | 133 tests、133 pass、0 fail |
| 固定オラクル | PASS | 49 PASS / 0 FAIL |
| self-hosting `--eco --fail-on error` | PASS | exit 0、error 0、warn 0、info 200、R-050 0。出力先はリポジトリ外 |
| 変更前個体による S-26 較正 | PASS | 旧 schema `ref-v0.10`、旧 `@bomdd/core` の symlink が旧展開先を指すことを確認。S-26 は 15 run 中13 FAIL・2 PASS、既存34 runは全PASS |
| M unit 複数・同一CPを複数M unitが参照 | PASS | 2 M unit が同じ `CP-CORE-001` を対象とし合格行なし → (a) 2件。別の `CP-CORE-002` の pass は所見なし |
| 製造記録複数・旧行fail、最新のみpass | PASS | 旧エントリの fail は無視され、最新 pass によりR-050 0、exit 0 |
| as_built複数ファイル・リスト/文書方言混在 | PASS | 文書方言と有効なリスト方言を別repoに配置。有効な最新リストを読みR-050 0、exit 0 |
| as_built末尾 null / 文字列 / 配列 | PASS | 各入力とも例外なし。(c) 1件、file=`32-mbom.yaml`、exit 1 |
| `test_evidence_refs` が文字列 / mapping / null | PASS | 各入力とも空行相当として(a) 1件、exit 1。クラッシュなし |
| 証跡行が mapping でない | PASS | scalar・配列・nullの各要素について(b)を各1件。いずれもtargetIdなし |
| cp_ref 欠落 / 数値 / 空文字 | PASS | 非pass行として各1件。(欠落・数値はtargetIdなし、空文字はtargetId=`""`) |
| result境界 | PASS | `Pass`、`PASS`、` pass `、`true`、`7`、`null`、空文字、欄なしをすべて(b)と判定 |
| 同一CPに合格行複数・非合格行複数 | PASS | pass 2行があるため(a)なし。非pass行は行ごとに(b) |
| 対象0・製造記録なし | PASS | (d) info 1件、exit 0 |
| 対象0・全行pass | PASS | (d) info 1件、(b)なし、exit 0 |
| 対象0・fail行あり | PASS | (d) info 1件+(b) error 1件、exit 1 |
| R-050抑止 | PASS | (a)(b)ともinfoへ降格、`suppressed:true`、理由・suppressRefあり、exit 0 |
| 5実行ゲート | PASS | always/G1/G3/freezeはexit 0、acceptanceのみexit 1。全ゲートのdiagnosticsにR-050 error 2件、各所見のgateは`acceptance` |
| 決定性 | PASS | 2回の`diagnostics.json`がbyte同一。SHA-256はいずれも `5FA176A7E3BE0A8CE36A07D4AAB5DB25880D1B02E82390E02F5822170342D092` |
| SARIF | PASS | diagnosticsのR-050 2件に対しSARIFも2件、levelはいずれもerror |
| viewer | PASS | `plm-view.html`生成成功。新しい(a)(b)双方のメッセージを埋込み |
| 同一M unit内の同一CP重複 | FAIL | IA-01。同じ(M unit, CP)に(a)を2件出力 |
| 壊れた32-mbomが存在する場合の(d)のfile | FAIL | IA-02。32-mbomではなく10-requirementsを指した |
| 成果物0件の対象0ケース | FAIL | IA-03。(d) infoが出ずR-050 0件 |
| `acceptance_refs: []` の「対象」解釈 | FAIL | IA-04。実装は対象0として(d)を出すが、規則文言の「acceptance_refsを持つM unit」と不整合な読みが可能 |
| cp_refを持てない行のline規定 | FAIL | IA-05。所見は出るがlineなし。仕様は(b)にcp_ref行番号を無条件要求しており充足不能 |

## 所見

### IA-01 — 同一 `(M unit, CP)` に(a)が重複する

- 再現検体:

```yaml
mbom:
  manufacturing_units:
    - id: M-CORE-001
      acceptance_refs: [CP-CORE-001, CP-CORE-001]
```

最新証跡は `CP-CORE-001 / result: fail` 1行。

- 再現コマンド:

```text
node packages/cli/dist/main.js <duplicate-ref/repo> --gate acceptance --fail-on error --out <外部temp>
```

- 観測: R-050 3件。内訳は同一内容の(a) 2件と(b) 1件、exit 1。
- 期待との差: `20-spec.md` §2.6 は(a)の粒度を「対象の `(M unit, CP)` ごとに1件」と固定している。同一M unit・同一CPという1組なので(a)は1件でなければならない。実装は`acceptance_refs`の配列要素を重複排除せず反復している。
- 重さ: blocking。§2.6の完全一致・過検出もFAILという受入規定に違反。
- 帰属: 製造物

### IA-02 — (d) のfileが存在する32-mbomを指さない

- 再現検体:

```yaml
# bomdd/32-mbom.yaml
not_mbom: true
```

他の成果物は存在し、受入対象は0件。

- 観測: (d) info 1件は出たが、`file` は `repo/bomdd/10-requirements.yaml`。R-050以外のerrorにより全体exitは1。
- 期待との差: `20-spec.md` §2.6は(d)のfileを「先頭の32-mbom（無ければ先頭の成果物）」と固定している。この検体には型付けされた32-mbomファイルが存在するため、内容の形にかかわらず `repo/bomdd/32-mbom.yaml` が期待値。
- 重さ: blocking。必須診断プロファイルのfileが仕様不一致。
- 帰属: 製造物

### IA-03 — 成果物0件では(d)を出せない仕様穴

- 再現検体: 空の `bomdd/` を持つリポジトリ。型付け成果物0件、M unit 0件、製造記録なし。
- 観測: exit 0、findings 0、R-050 0件。
- 期待との差: 正本R-050(d)は対象0件なら適用外infoを実行ごとに1件要求する。一方、§2.6はfileを「先頭の32-mbom、無ければ先頭の成果物」とするだけで、成果物自体が0件の場合を定義していない。現実装ではfileを選べず所見が消える。
- 重さ: blocking。正本が要求する明示状態を合法な空入力で生成できず、正確な是正方法も仕様から一意に導けない。
- 帰属: 仕様

### IA-04 — (d) の「対象」定義が空リストで曖昧

- 再現検体:

```yaml
mbom:
  manufacturing_units:
    - id: M-CORE-001
      acceptance_refs: []
```

- 観測: 実装は対象0件として(d) info 1件、exit 0。
- 期待との差: 正本R-050(d)の「対象」は「acceptance_refsを持つM unit」と書かれており、キーを持つが空リストのM unitを数える読みが可能。一方、(a)は「CP行すべて」、§2.6は`(M unit, CP)`粒度なので、空リストを対象1件とすると(a)(c)の所見対象CPが存在しない。非空CPを持つM unitだけを意味するのか、CP組の件数を意味するのかが明記されていない。
- 重さ: non-blocking。実装の解釈は整合的だが、規則文言単独では一意でない。
- 帰属: 規則文言

### IA-05 — cp_ref欠落・非mapping行では(b)のline規定が実装不能

- 再現検体の証跡行:

```yaml
test_evidence_refs:
  - {evidence_id: TE-1, result: fail}   # cp_refなし
  - scalar-row
  - [nested, row]
  - null
```

- 観測: 各行について(b) errorが出たが、いずれも`line`なし。
- 期待との差: 正本(b)はresult欄なしや語彙外を違反とするため、非mapping要素を「result欄なし」と扱う実装は合理的。一方、§2.6は「(b)はcp_refの行番号をlineに持つ」と無条件に要求する。cp_refが存在しないmappingや非mapping要素にはcp_ref行番号が存在せず、規定を満たせない。行要素自体の行番号を使うか、line省略を許すかが未規定。
- 重さ: non-blocking。判定とexitは安全側だが、位置情報契約が一意に実装できない。
- 帰属: 仕様

## 範囲外の観察

- `git`実行時にユーザー側グローバルignoreへのアクセス警告が出たが、各コマンドの成否・検査結果には影響しなかった。
- row-matrixや壊れた32-mbomではR-050以外の参照・構造所見も発生した。上表と所見ではR-050の期待比較から除外した。
- self-hostingのinfo 200件は既存のR-005等で、error/warnは0だった。
- 複数成果物間で何を「最後」とするかは実装上、正準パス順の解析順に依存する。ECO-008が宣言済み境界として残した事項のため、本判定には追加欠陥として算入していない。

## 測れなかったこと

なし。