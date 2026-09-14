[INFORM / COMPLETE]
ACCEPT — IA 所見なし。range「是正確認+回帰」の指定項目はすべて r1 と一致した。

# ECO-075 独立検査報告 r2

- range: 是正確認+回帰
- inspector: EQ-002
- 対象 revision: `bd16bbb5810f149f21e996bc4f5683ab6dcd0f23`
- revision 差: r1 と同一。作業木には開始時から r1 報告 `bomdd/reports/independent-inspection-eco-075.md` の staged 追加のみ存在
- sandbox: workspace-write
- fixture: OS temp
- リポジトリ内の作成・変更・削除: なし

## `/preflight` receipt

- task classification: continuation — r1 境界探索後の同一 revision に対する限定回帰
- baseline: HEAD `bd16bbb5810f149f21e996bc4f5683ab6dcd0f23`、confirmed
- current-work-state: ECO-075 `implemented`、r1 報告追加済み、confirmed
- unresolved-items: r2 回帰と未知の固有語読解、confirmed
- handoff-state: r1 報告から再構成可能、confirmed
- acceptance-target: 本ブリーフの7項目回帰、未知語読解、生成物参照確認、confirmed
- 開始判定: PROCEED
- override: なし

## 1. core の固有語 grep 表

再現:

```powershell
# Python stdin script:
# adapter 見出しより前を抽出し、r1 の語群を大文字小文字無視・行ヒット数で集計。
# 同じ集計を git show f71e628:.claude/skills/handoff/SKILL.md に適用。
```

観測:

```text
HEAD=bd16bbb5810f149f21e996bc4f5683ab6dcd0f23
ADAPTER_LINE=231
BomDD=0
ECO-=0
bomdd/=0
Phase=0
run-02=0
R1～R8=各0
Codex=0
witness=0
self-conformance=0
停止語彙7種=各0
improvements.md=0
BROAD_REGEX_COUNT=0
KNOWN_BAD_TOTAL=44
MAIN=BomDD=6, ECO-=8, Phase=7, run-02=5,
     NORMATIVE_RULING=1, CONVERGENCE_LIMIT=1,
     PREFLIGHT_HOLD=1, VERIFICATION_FAIL=1,
     LEDGER_INCONSISTENT=1
LASTEXITCODE=0
```

r1 との差: なし。旧版の集計単位を「出現回数」でなく r1 と同じ「一致した行数」に合わせると、陽性対照も `44` で一致した。

## 2. 第三者としての再述（5行）

1. INFORM は `CONTINUING/COMPLETE/PAUSED`、DECIDE・DISCUSS は `CONTINUING/BLOCKED/PAUSED`、REQUEST は `CONTINUING/BLOCKED` だけが許容され、表外の組合せは送信しない。
2. INFORM は情報・人間作業なし・実行説明、DECIDE は問い・帰結付き選択肢・推奨・返答形式・実行説明、DISCUSS は問い・仮説・根拠・反論・変更条件・非裁定宣言、REQUEST は依頼・穴埋め成果物・人間が必要な理由・実行説明を要する。
3. ハーネス通知だけを待つターンは `INFORM / CONTINUING` とし、待つ対象と、それに依存する事項だけをヘッダ後2行以内で示す。
4. フリースタイル区間は人間だけが開始・終了でき、区間内でも裁定・依頼・タスク終了を含む一通は契約へ戻り、区間継続を明記する。
5. 送信前にヘッダ・許容組合せ・必須欄・単一 mode を structural に、目的・根拠・execution の整合を semantic に分けて検査し、structural FAIL は送らず書き直す。

再現:

```powershell
pwsh -NoProfile -Command "Get-Content method/templates/product-profile/skills/handoff.md | Select-Object -First 230"
```

観測: core を1回通読し、上記再述に必要な規則を確認。`$LASTEXITCODE=0`。

r1 との差: なし。再述不能・二義的箇所なし。

## 3. adapter の完全性

再現:

```powershell
git show f71e628:.claude/skills/handoff/SKILL.md
# 旧版と現正本から HANDOFF CONTRACT v0.4 のコードブロック本文を抽出し、
# 末尾改行を含めて SHA-256 を計算
```

観測:

```text
OLD_SHA256=e354017136173148403913fd473e31fed2154020dc7aef421f2195c51ced7fb4
NEW_SHA256=e354017136173148403913fd473e31fed2154020dc7aef421f2195c51ced7fb4
IDENTICAL=True
LASTEXITCODE=0
```

停止語彙対応は adapter A1、記録配置は一般化された core 規則と adapter A2、出自・計測は A3に存在する。classify/generate/validate/rewrite、待機形、フリースタイル、DISCUSS収束にも規範的欠落なし。

r1 との差: なし。

## 4. 写しの同期

再現:

```powershell
git diff --no-index --unified=2 -- method/templates/product-profile/skills/handoff.md .claude/skills/handoff/SKILL.md
```

観測: 既知の3 hunkのみ。

- 正本の正典行と写し側の5行注記
- A2 の `{{METHOD}}/method/improvements.md` の相対解決
- A3 の同じ相対解決

差が存在するため `$LASTEXITCODE=1`。これは期待された終了値。

写し注記を正典行へ、2件の相対パスを `{{METHOD}}` 形式へ正規化して比較した結果:

```text
NORMALIZED_DIFF_COUNT=0
LASTEXITCODE=0
```

r1 との差: なし。

## 5. 配布の結線

再現:

```powershell
# bomdd-init.py を runpy.run_path で読み、SKILLS と実ファイルを集計
python method/tools/bomdd-init.py --help
```

観測:

```text
COUNT=13
HANDOFF_IN_SKILLS=True
FILE_COUNT=13
HANDOFF_FILE=True
README_HITS=19,58
AGENTS_47=product-profile/skills/handoff.md の正本参照
AGENTS_59=handoff 契約の正本・写し参照
CANON_EXISTS=True
COPY_EXISTS=True
LASTEXITCODE=0
```

`--help` は `--skills-only` と `--skills SKILLS` を表示し、`$LASTEXITCODE=0`。

r1 との差: なし。

## 6. OS temp での handoff 生成

再現:

```powershell
python method/tools/bomdd-init.py product `
  --dir <OS-temp-fixture> `
  --skills-only --skills handoff
```

観測:

```text
[ok] ...\product へスキル 1 本を設置しました
LASTEXITCODE=0
SKILL_EXISTS=True
UNRESOLVED_METHOD_COUNT=0
BOMDD_KIT_REF_COUNT=3
bomdd-kit/method/templates/product-profile/skills/handoff.md=True
bomdd-kit/method/improvements.md=True
LINE_8=正典: `bomdd-kit/method/templates/product-profile/skills/handoff.md`
LINE_244=...`bomdd-kit/method/improvements.md`
LINE_250=...`bomdd-kit/method/improvements.md`
LASTEXITCODE=0
```

`{{METHOD}}` は `bomdd-kit` に解決され、指定された2参照先はいずれも実在した。

r1 との差: なし。

## 7. 配員欄の文言境界

対象: `method/templates/60-change-order.md` 18–19行。

再現:

```powershell
# Python で18–19行だけを抽出し、対象語をリテラル集計
```

観測:

```text
解決する=0
解決し=0
止まる=0
STOP=0
照合し=0
LEDGER_INCONSISTENT=0
INDEPENDENCE_FAIL=0
導出=1
検証=1
強制=1
LASTEXITCODE=0
```

`導出`・`検証`・`強制` はすべて同一の明示的否定文「製品リポではこの欄は記述欄であり、機械的な導出・検証・強制は存在しない」内だけにある。

r1 との差: なし。

## 8. frontmatter

再現:

```powershell
# 両ファイルの --- 区画を PyYAML で解析し、
# name == handoff、description が非空かを検査
```

観測:

```text
method\templates\product-profile\skills\handoff.md:
  name='handoff', description_len=306, valid=True
.claude\skills\handoff\SKILL.md:
  name='handoff', description_len=306, valid=True
LASTEXITCODE=0
```

r1 との差: なし。

## 9. 未知の BomDD 固有語

adapter 区画より前の230行を、r1 の列挙語に頼らず1回通読した。

観測: **読解で 0**。列挙外の BomDD 固有語・パス・番号は確認されなかった。

冒頭の `{{METHOD}}/method/templates/product-profile/skills/handoff.md` は配布時に置換される正典ロケータであり、未解決の BomDD 固有語とは判定しなかった。別検査で、生成物では期待どおり `bomdd-kit/...` に解決されることを実測した。

r1 との差: r1 で条件付き適格として残した「列挙語以外の未知語」を今回の読解で確認し、0件。

## 終了時状態

再現:

```powershell
git rev-parse HEAD
git status --short
git diff --name-only
git diff --cached --name-only
```

観測:

```text
bd16bbb5810f149f21e996bc4f5683ab6dcd0f23
LASTEXITCODE=0
A  bomdd/reports/independent-inspection-eco-075.md
LASTEXITCODE=0
<unstaged diff なし>
LASTEXITCODE=0
bomdd/reports/independent-inspection-eco-075.md
LASTEXITCODE=0
```

開始時との差: なし。本検査によるリポジトリ変更なし。

## 所見

IA 所見なし。指定項目で測れなかったものはなし。

## `/calibrate` receipt

- 主張: 同一 revision のECO-075製造物は、r1の7検査軸を回帰し、列挙外固有語の読解確認と生成物の参照解決を含む本r2ブリーフを満たす。
- 測定成立性: `observed`
- 証拠資格: `適格`（本ブリーフで限定された是正確認+回帰の主張に対して）
- 検出した計器欠陥: なし。初回の旧版集計47は出現回数で数えた検査手順の不一致であり、r1と同じ行ヒット定義へ合わせて44を再現した。製造物への所見ではない。
- Q1 asked / Q2 asked（旧版 known-bad 44、現 core 0）/ Q3 asked（7軸を分離）/ Q4 asked（実ファイル・OS temp生成物）/ Q5 asked（各外部コマンドの終了値を直後に観測）/ Q6 asked / Q7 asked（旧版陽性対照）/ Q8 NA（予防ゲートではない）/ Q9 asked（HEAD刻印）/ Q10 asked / Q11 asked（字句・意味・同期・配布を分離）
- 検出力の限界: 単一検査官による1回の意味読解。契約v0.4の妥当性、実運用での mode 分類性能、全ハーネスの loader、運転層配布、CI・self-conformanceは本rangeの範囲外で未測定。

## 範囲外の観察

- OS temp fixture `bomdd-eco075-r2-4b515e1b60e14cbd907995701984a2d5` の削除要求は環境ポリシーによりプロセス起動前に拒否され、`$LASTEXITCODE` は取得不能だった。fixture は残存するがリポジトリへの変更はない。

human_action: none  
execution: COMPLETE — range「是正確認+回帰」の独立検査を完了した。