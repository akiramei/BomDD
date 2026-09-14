[INFORM / COMPLETE]
ACCEPT — IA 所見なし。境界探索 round であり、打ち切り根拠にはしない。

# ECO-075 独立検査報告 r1

- range: 境界探索
- inspector: EQ-002
- 対象 revision: `bd16bbb5810f149f21e996bc4f5683ab6dcd0f23`
- worktree: 開始時・終了時とも `git status --short` 出力なし、exit 0
- 帰属: 検査対象は製造物、実行上の制約は環境へ帰属

## 1. core の環境非依存性

再現:

```powershell
$core=Get-Content method/templates/product-profile/skills/handoff.md | Select-Object -First 230
# 下表の各語を Contains および大文字小文字を無視した broad regex で走査
```

adapter 境界は `method/templates/product-profile/skills/handoff.md:231`。broad regex の観測は `BROAD_REGEX_COUNT=0`、exit 0。

| 語 | 件数 | 行 |
|---|---:|---|
| `BomDD` | 0 | — |
| `ECO-` | 0 | — |
| `bomdd/` | 0 | — |
| `Phase` | 0 | — |
| `run-02` | 0 | — |
| `R1` | 0 | — |
| `R2` | 0 | — |
| `R3` | 0 | — |
| `R4` | 0 | — |
| `R5` | 0 | — |
| `R6` | 0 | — |
| `R7` | 0 | — |
| `R8` | 0 | — |
| `Codex` | 0 | — |
| `witness` | 0 | — |
| `self-conformance` | 0 | — |
| `NORMATIVE_RULING` | 0 | — |
| `CONVERGENCE_LIMIT` | 0 | — |
| `PREFLIGHT_HOLD` | 0 | — |
| `VERIFICATION_FAIL` | 0 | — |
| `LEDGER_INCONSISTENT` | 0 | — |
| `INDEPENDENCE_FAIL` | 0 | — |
| `INSPECTION_MISSING` | 0 | — |
| `improvements.md` | 0 | — |

陽性対照として同じ語群を旧版へ適用した結果は `KNOWN_BAD_TOTAL=44`、exit 0。主な検出は `BomDD=6`、`ECO-=8`、`Phase=7`、`run-02=5`、停止語彙各 1。計器の沈黙ではないことを確認した。

期待との差: なし。帰属: 製造物。

## 2. 第三者としての再述（5行）

1. 許容組合せは INFORM=`CONTINUING/COMPLETE/PAUSED`、DECIDE・DISCUSS=`CONTINUING/BLOCKED/PAUSED`、REQUEST=`CONTINUING/BLOCKED` で、それ以外は送信しない。
2. INFORM は情報・人間作業なし・実行説明、DECIDE は問い・帰結付き選択肢・推奨・返答形式・実行説明、DISCUSS は問い・仮説・根拠・反論・変更条件・非裁定宣言、REQUEST は依頼・穴埋め成果物・人間が必要な理由・実行説明を要する。
3. ハーネス通知だけを待つ場合は `INFORM / CONTINUING` とし、待つ対象と依存事項だけをヘッダ後2行以内で示す。
4. フリースタイル区間は人間だけが開始・終了でき、区間内でも裁定・依頼・タスク終了の一通は契約へ戻して区間継続を明記する。
5. 送信前にヘッダ・許容組合せ・必須欄・単一 mode を structural に、目的と mode・根拠・execution の整合を semantic に別々に検査し、structural FAIL は送らず書き直す。

再述不能・二義的箇所: なし。任意環境の system of record は環境側が定義することも core 内で明示されている。

期待との差: なし。帰属: 製造物。

## 3. adapter の完全性

再現:

```powershell
git show f71e628:.claude/skills/handoff/SKILL.md
git diff --unified=2 f71e628 -- .claude/skills/handoff/SKILL.md
```

観測:

- 旧版と現正本の `HANDOFF CONTRACT v0.4` 本文は完全一致。
- 旧 SHA-256、新 SHA-256ともに `e354017136173148403913fd473e31fed2154020dc7aef421f2195c51ced7fb4`。
- 旧 §2.6 の停止語彙対応は現 adapter A1（238–240行）へ移動。
- 記録配置規則は core の一般的な system-of-record 規則（112–114行）と adapter A2へ分離。
- classify/generate/validate/rewrite、待機形、フリースタイル、DISCUSS収束などの規範は保持。
- 除去された内容は版履歴、試行計測、故障逸話または環境固有例。規範的な欠落は観測しなかった。

期待との差: なし。帰属: 製造物。

## 4. 写しの同期

再現:

```powershell
git diff --no-index -- method/templates/product-profile/skills/handoff.md .claude/skills/handoff/SKILL.md
```

観測: exit 1（差があるため正常）。差は3 hunkのみ。

- 正本の正典行と、写し側の5行の写し注記
- A2 の `{{METHOD}}/method/improvements.md` → `method/improvements.md`
- A3 の同じ相対解決

これらを正規化した比較は `NORMALIZED_DIFF_COUNT=0`、exit 0。

期待との差: なし。帰属: 製造物。

## 5. 配布の結線

再現と観測:

- `bomdd-init.py` を `runpy.run_path` で読み込み: `COUNT=13`、`handoff` を含む、exit 0。
- product-profile の実ファイル: `FILE_COUNT=13`、`handoff.md` を含む、exit 0。
- README の完全一致検索: `スキル 13 本` は19行・58行の2件、exit 0。
- AGENTS.md: 47行・59行が product-profile 正本を参照し、正本と写しはいずれも `EXISTS=True`。
- `python method/tools/bomdd-init.py --help`: exit 0、`--skills-only` と `--skills SKILLS` を表示。
- OS temp で `--skills-only --skills handoff`: 「スキル 1 本を設置」、exit 0。
- 生成先でスキル、同梱正本、`bomdd-kit/method/improvements.md` が全て実在し、`UNRESOLVED_METHOD_COUNT=0`。

期待との差: なし。帰属: 製造物。

## 6. 配員欄の文言境界

対象は `method/templates/60-change-order.md:18–19`。

| 語 | 件数 |
|---|---:|
| `解決する` | 0 |
| `解決し` | 0 |
| `止まる` | 0 |
| `STOP` | 0 |
| `照合し` | 0 |
| `LEDGER_INCONSISTENT` | 0 |
| `INDEPENDENCE_FAIL` | 0 |

`導出`・`検証`・`強制` は各1件だが、同一の「製品リポでは…存在しない」という明示的否定文内だけにある。機械化への言及は「BomDD 方法論リポの自己適用でのみ」と限定されている。inspector 欄も製品リポでは記述欄で、独立性は人間の配員規律によると明記する。

期待との差: なし。帰属: 製造物。

## 7. frontmatter

再現: 両ファイルの frontmatter を PyYAML で解析し、`name == "handoff"` と非空 description を検査。

観測:

- 正本: `name='handoff'`、`description_len=306`、`valid=True`
- 写し: `name='handoff'`、`description_len=306`、`valid=True`
- exit 0

期待との差: なし。帰属: 製造物。

## 所見

IA 所見なし。測れなかった指定項目はなし。

## `/calibrate` receipt

- 主張: 指定された7検査軸について ECO-075 の製造物がブリーフの期待を満たす。
- 測定成立性: `observed`。
- 証拠資格: `条件付き適格`。指定語と指定 revision に対する受入には使用可能だが、境界探索であり未知の固有語や将来の loader 実装までの完全被覆は主張しない。
- 検出した計器欠陥: なし。
- Q1 asked / Q2 asked（旧版 known-bad 44件、現 core 0件）/ Q3 asked / Q4 asked（実ファイルとOS temp生成物を実入力化）/ Q5 asked / Q6 asked / Q7 asked（旧版を陽性対照化）/ Q8 NA（予防ゲートの検査ではない）/ Q9 asked（HEAD刻印・clean確認）/ Q10 asked / Q11 asked（字句検査と意味比較を分離）。
- 検出力の限界: 単一検査官、列挙語以外の未知語、実運用での mode 分類性能、全ハーネスの loader 挙動、CI・self-conformance は本 round で再測定していない。

## 範囲外の観察

- OS temp fixture `bomdd-eco075-74908e5299b94b13a545a2a1b902d2e9` は削除操作が環境ポリシーに拒否されたため残存する。リポジトリへの変更はない。

human_action: none  
execution: COMPLETE — 境界探索 r1 の指定範囲を検査し、判定と較正 receipt を提示した。