[INFORM / COMPLETE]

ACCEPT

- range: 是正確認+回帰
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象 revision: `2d2f4ae0165d659c209e4513a6f750004b3d9af6`
- commit: 0（開始・終了とも同一 HEAD）
- 外部 API: 呼出しなし
- self-conformance: ブリーフの指定どおり再実行なし
- register / order §5.2・§6: 編集なし

開始時 `git status --short`:

```text
（出力なし）
```

終了時 `git status --short`:

```text
（出力なし）
```

## IA-01 — diff 窓と旧 baseline の恒久再現

確認方法:

```text
git diff --name-only fa0d848 2d2f4ae0165d659c209e4513a6f750004b3d9af6
git diff --name-only e0d4b52 fa0d848
```

観測:

- register に `baseline: "fa0d848"` と `baseline_v1: "e0d4b52"` が共存。
- 新窓の変更は次の9ファイルで、すべて `ECO-081.diff_audit.allowed_paths` 内。

```text
bomdd/60-change-order-eco-081.md
bomdd/60-change-register.yaml
bomdd/reports/independent-inspection-eco-081.md
method/improvements.md
method/templates/60-change-register.yaml
method/templates/70-equipment.yaml
method/templates/product-profile/README.md
method/templates/product-profile/operator-layer.md
method/tools/bomdd-init.py
```

- 旧窓 `e0d4b52..fa0d848` は11ファイルを返した。
- その内訳は、r1 で報告した allowed_paths 外8ファイルと、ECO-081 の台帳系3ファイル（order・register・improvements）に完全一致。余分なファイルは0。
- r2報告経路 `bomdd/reports/independent-inspection-eco-081-r2.md` も allowed_paths に登録済み。

判定: **PASS — IA-01 是正確認済み**。新窓は限定され、`baseline_v1` は旧窓の混入を再現する恒久フィールドとして機能する。

## IA-03 — 第三者記述試験

確認方法: `operator-layer.md` の core §3を記述根拠として、設備2件を OS temp の `bomdd-eco081-r2-equipment.yaml` に作成。その後、雛形とは別に比較した。

観測:

- provenance の対象は3軸だけと明記。
- `active` / `retired` の2値が明記。
- `provenance` は属性名→来歴の対応表と明記され、YAML例も存在。
- 推測で補った箇所: **0**。

成果物:

```yaml
equipment:
  - id: EQ-101
    kind: ai-model
    model: model-alpha
    harness: harness-red
    account_lineage: account-a
    provenance: {model: self-reported, harness: harness-measured, account_lineage: user-declared}
    qualification_ref: "qualification-record-ai-01"
    status: active
    note: "fictional inspection specimen A"
  - id: EQ-102
    kind: human
    model: human-reviewer
    harness: manual-review
    account_lineage: account-b
    provenance: {model: user-declared, harness: user-declared, account_lineage: user-declared}
    qualification_ref: "unqualified"
    status: retired
    note: "fictional inspection specimen B"
```

判定: **PASS — IA-03 是正確認済み**。

## IA-04 — core 語彙の閉包

- `bomdd/`: **PASS** — 配布先のディレクトリ規約であり、別配置では読み替えると定義。
- `verified`: **PASS** — 受入条件が観測済みで閉じた最終状態と定義。
- `executor`: **PASS** — 実際に検査を実行した設備として定義され、inspector と異なる場合の扱いも明記。
- `{{PRODUCT}}`: **PASS** — 設置時に製品名へ置換されるプレースホルダ。
- `{{METHOD}}`: **PASS** — 設置時に同梱方法論の相対パスへ置換されるプレースホルダ。
- `BOM`: **PASS** — 製品を構成する部品と工程の宣言である部品表。
- `handoff`: **PASS** — AIが人間へ制御を返す、先頭が型宣言になったメッセージ。

§0 自体も読解したが、意味の確定に配布元固有の知識を新たに要求する語は認めなかった。

判定: **PASS — IA-04 是正確認済み**。

## IA-05 — 射影と機構の有無

確認方法: core §1と§7を相互に読解。

観測:

- 「機構があれば」という条件文はあるが、自動生成機構が実在すると主張する文はない。
- §1は、機構がなければ運転員が台帳を読んでその場で射影を書き出すと規定。
- §7は、分類・照合・記述・回収を運転員が手で行い、その事実を変更指示書へ書くと規定。
- §1と§7は同じ人手経路を示しており、一義的に読める。
- 禁止対象だった「射影は手書きしない」は残っていない。

判定: **PASS — IA-05 是正確認済み**。

## 回帰

- V1: **PASS** — 指定正規表現は core 0件、adapter 陽性対照16件。
- V2 init: **PASS** — `bomdd-init.py Smoke --dir <OS temp> --no-gui --no-git` exit 0。
- V2生成物: **PASS** — `bomdd/70-equipment.yaml` と `bomdd/operator-layer.md` が実在。
- V2置換: **PASS** — 上記2ファイルの未解決 `{{` は各0件。
- V2 YAML: **PASS** — 重複キーを拒否する厳格ローダーで parse 成功、equipment 1件。
- V2 skills: **PASS** — `.claude/skills/` は13件。
- V3: **PASS** — `70-equipment.yaml` の注記、およびregisterテンプレの producer/inspector 注記2行とも禁止語0件。
- 停止語彙: **PASS** — core §2、`bomdd-job.py` の `STOP_VOCABULARY`、`bomdd-run.py` の `DELIVERY` は10語が一致。
- 配送先: **PASS** — 10語すべてで core §2 と `DELIVERY` が1対1一致。
- 「採らない」対象: **PASS** — 新窓 `fa0d848..2d2f4ae` における指定7対象の差分は0。

## 是正による別欠陥の有無

- §0のexecutor定義と§4: **整合**。executor が inspector と異なる場合はexecutorを照合し、§4もexecutorの台帳登録を要求する。
- §0のverified定義と§5: **整合**。独立検査結果の回収前は最終状態へ上げない。
- §0の運転員定義と§3〜§6: **整合**。運転員は製造・独立検査ではなく、分類・照合・記述・回収を担う。
- §3 YAML例と `method/templates/70-equipment.yaml`: **一致**。キー構成、3軸、provenance map、qualification_ref、2値status、noteの形が一致。

指定された整合性検査では、新たな欠陥を認めなかった。

## 較正 receipt

査定した主張と判定:

- IA-01是正: **observed × 適格** — 対象revisionをfull SHAで照合し、新旧diff窓とregisterを直接比較。
- IA-03〜05是正: **observed × 適格** — core本文による第三者記述試験と節間読解が成立。
- V1〜V3回帰: **observed × 適格** — 指定計器で再実行し、件数・終了コード・生成物を観測。
- 停止語彙・配送先および非採用対象: **observed × 適格** — 定数をASTで読み、文書表との完全一致と新窓diff 0を観測。

検出した計器欠陥と帰属:

- 初回V2後処理で、検査ラッパーが生成先 `<temp>/Smoke` ではなく親 `<temp>` を参照して中断した。帰属は検査官の一時ラッパー。製品のinit自体はexit 0だった。
- freshな別OS tempで生成から後処理まで再実行し、上記V2結果を取得したため、最終証拠には失敗したラッパーの結果を使用していない。
- それ以外の計器欠陥: なし。

検出力の限界:

- ブリーフ指定により self-conformance は再実行していない。
- 外部API禁止のためCIは照会していない。
- 第三者記述試験は指定どおりr1と同じ検査官であり、盲検・別査定者による再現性は測っていない。
- V1にはadapter陽性対照があるが、V2・V3には本roundで欠陥注入による陽性対照を置いていない。
- range外の新規境界・実運用時の理解一致・設備認定参照の実在性は測っていない。

battery:

- Q1: asked — 報告上の主張を実測範囲に限定。
- Q2: asked — r1の不成立状態とr2を対にし、V1ではadapter陽性対照も観測。
- Q3: asked — IA別およびV1〜V3別に独立して判定。
- Q4: asked — 対象HEAD、register、実生成物を実入力として使用。
- Q5: asked — 未実行のself-conformanceとCIをPASSへ算入していない。
- Q6: asked — 全結果を観測してから最終判定を作成。
- Q7: asked — V1陽性対照を確認。V2・V3の陽性対照なしは限界として宣言。
- Q8: NA — 予防ゲートの出口設計は本rangeの査定対象外。
- Q9: asked — 開始・終了HEADが対象full SHAと一致。
- Q10: asked — 未測定次元を上記に宣言。
- Q11: asked — core/adapter、生成/YAML/skills、注記2種を分けて観測。

## 範囲外の観察

なし。

human_action: none。execution: COMPLETE — 指定された是正確認+回帰は全項目成立。