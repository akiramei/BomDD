[INFORM / COMPLETE]

ACCEPT

- range: 是正確認 + 回帰
- inspector: OpenAI GPT-5 / Codex API harness
- 対象 revision: `4c2556d443649873e5c28f53719df390a2ec0a77`
- 是正範囲: `59941479c45d22ab0ada1ed369e95365538e441a..4c2556d443649873e5c28f53719df390a2ec0a77`
- 是正範囲の commit 数: 1
- 全体範囲 `eco-008-input..4c2556d`: 3 commits
- 検査中 commit 数: 0
- 環境: Node.js `v22.13.1` / npm `11.5.2`
- 外部 API・ネットワーク呼出し: なし
- 検体・出力: すべて `C:\Users\akira\AppData\Local\Temp\bomdd-r2-inspection-6a2ea6bf3f784656956ca40dead6714c` 配下
- 開始時 `git status --short`: 出力なし
- 終了時 `git status --short`: 出力なし

## 是正確認

| 所見 | 判定 | 自分の検体の内容 | 観測 |
|---|---|---|---|
| IA-01 | 是正済み | 同一 M unit の `acceptance_refs` に同一 CP を2回記載。別検体では、さらに別 M unit から同じ CP を参照 | 同一 M unit だけでは (a) 1件。同じ CP を参照する別 M unit を加えると (a) 2件。組内の重複だけが除かれ、別組は消されていない。(b) は証跡行ごとに別途1件 |
| IA-02 | 是正済み | `32-mbom.yaml` を①非mappingの配列、②空ファイル、③`mbom`キーなし、④YAML構文エラーにした4検体 | 全4検体で (d) 1件、`file=repo/bomdd/32-mbom.yaml`。中身ではなく成果物型で選択されている |
| IA-03 | 是正済み | 成果物0件の単一リポ、および成果物0件の2リポworkspace（宣言順は `zeta`, `alpha`） | 単一リポは (d) 1件、`file=repo/bomdd/32-mbom.yaml`。workspaceも実行全体で1件、`file=zeta/bomdd/32-mbom.yaml`。辞書順ではなく先頭リポを使用 |
| IA-04 | 是正済み | `acceptance_refs` が①`[]`、②キーなし、③`null`、④文字列の4検体 | すべて対象 `(M unit, CP)` は0組として (d) 1件。(a)(c) はなし。正本の「acceptance_refsが無い・空のM unitは組を作らない」およびCPとの組という定義に一致 |
| IA-05 | 是正済み | `50-as-built.yaml` の5行目にcp_refなしmapping、8行目にscalar行 | 各行の (b) がそれぞれ `line: 5`、`line: 8` を持ち、実際の行要素位置と一致。両方とも文字列cp_refがないためtargetIdなし |

## 回帰

| 項目 | 判定 | 観測 |
|---|---|---|
| `npm run build` | PASS | exit 0、警告0 |
| `node --test` | PASS | 137 tests、137 pass、0 fail |
| 固定オラクル | PASS | 49 PASS / 0 FAIL |
| self-hosting `--eco --fail-on error` | PASS | exit 0、error 0、warn 0、info 200、R-050 0。`--out`はリポジトリ外 |
| oracle不変 | PASS | `git diff 5994147 4c2556d -- oracle/` は空。`S-26-acceptance-evidence.json` と `oracle/fixtures/rules/R-050/` に変更なし |
| 同一CPを複数M unitが参照 | PASS | 2つのM unitに対して (a) 2件。同一M unit内の重複参照は1件に縮約 |
| 対象0件・製造記録なし | PASS | (d) info 1件、(b)なし、exit 0 |
| 対象0件・全証跡行pass | PASS | (d) info 1件、(b)なし、exit 0 |
| 対象0件・fail行あり | PASS | (d) info 1件と(b) error 1件が併存、exit 1 |
| 5実行ゲート | PASS | always/G1/G3/freezeはexit 0、acceptanceのみexit 1。全ゲートのdiagnosticsにR-050 error 2件、gateはいずれも`acceptance` |
| R-050抑止 | PASS | (a)(b)ともinfoへ降格し、`suppressed:true`、理由、`suppressRef`あり。exit 0 |
| 決定性 | PASS | 独立した出力先への2実行で`diagnostics.json`がbyte同一。SHA-256はいずれも `05b3b9a4c0ffa5baf54b3a6b90c815d98cd7cc9a18b87577460ef5162534c0ff` |
| 正本との整合 | PASS | IA-01/04の対象定義、IA-03の成果物0件時のfile、IA-05の代替lineが現行R-050および仕様§2.6に一致 |
| 作業木不変 | PASS | 検査前後とも`git status --short`は出力なし |

## 新しい所見

なし。IA-06以降に採番すべき欠陥は観測しなかった。

## 範囲外の観察

- `git`実行時にユーザー側グローバルignore `C:\Users\akira\.config\git\ignore` へのアクセス警告が出た。各Gitコマンドの結果および作業木判定には影響しなかった。
- 壊れた32-mbomや型違反の`acceptance_refs`では、R-050以外のparse/schema/reference所見によりプロセス全体がexit 1になる場合がある。本検査ではR-050の所見プロファイルを分離して判定した。
- self-hostingのinfo 200件は既存のR-005等で、error/warnおよびR-050は0件だった。

## 測れなかったこと

なし。