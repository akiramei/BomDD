# Change Order — ECO-063(factory-delegate のリポ内正本化 — product-profile スキル 12 本目・kit 配布・Claude 写し)

> 裁定: user 2026-09-10(ECO-062 §4 裁定 2)「factory-delegate 正本化は別 ECO」→ 同日 user「Phase 4 を実施して」
> (ECO-062 §7: job 経由で起動する ECO を回す)。本 ECO は **Phase 4 の 1 本目**として、ECO-062 の製造物(job 射影+witness)
> を工程の起動と遷移に使う。方向は裁定済み・製造の実施は Phase 4 の指示による。範囲は**移設**(正本化)であり、
> 手順の設計変更はしない(例外= 工程 2 に ECO-062 弧で実測した「経路が止まったときの切替」を追記 — 既知の実測のみ・§1)。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- 起動経路: **job 経由**(`python method/tools/bomdd-job.py ECO-063` — §6 に記録)

## 0. 実測(起票根拠)

- factory-delegate スキルの所在= `~/.claude/skills/factory-delegate/SKILL.md`(利用者のユーザー階層・**リポ外**・115 行・出自 2026-07-23
  ViewPrism2 ECO-137)。リポ内の言及は improvements.md 1 箇所のみ(ECO-062 §0.2 で発見・OBS-20260910-01 の 1 例)。
- product-profile スキルの正本= [method/templates/product-profile/skills/](../method/templates/product-profile/skills/)(11 本)・
  配布= `bomdd-init.py` の `SKILLS` 定数(11 名)・README の「スキル 11 本」表記 2 箇所を C7 が `SKILLS` 実数と突合。Claude 用写しは
  `.claude/skills/<name>/SKILL.md`(D-1 同期規則・ECO-042/032)。
- ECO-062 弧(2026-09-10)で Codex 委譲の経路障害 4 種と復旧経路(CLI 直接・resume)を実測(OBS-20260910-04)。旧写しにはこの知見がない。

## 1. 変更要求(製造対象)

1. **正本**: `method/templates/product-profile/skills/factory-delegate.md` を新設(旧写しの本文を移設。frontmatter は同一。冒頭に
   正典行・関連スキル・出自/正本化の注記を他スキルと同型で追加。playbook 参照は `{{METHOD}}` プレースホルダ)。
2. **工程 2 への追記**(唯一の本文追加): 「経路が止まったときの切替」— companion 経路の障害 2 型・CLI 直接の呼び出し形・read-only と
   workspace-write の使い分け・コンテンツフィルタ遮断時の `resume`・後片付けの確認。すべて ECO-062 §8〜8.4 の実測に限る(新規則なし)。
3. **写し**: `.claude/skills/factory-delegate/SKILL.md`(正本から生成・写し注記・`{{METHOD}}` を自リポ相対へ解決)。
4. **配布**: `bomdd-init.py` の `SKILLS` に `factory-delegate` を追加(次回 scaffold から配布・既存 kit は lock 凍結)。
5. **README**: 「スキル 11 本」→「12 本」(2 箇所・C7)+ product-profile/README.md の表に 1 行。
6. **採らない**: 旧写し(`~/.claude/skills/`)の削除(利用者環境・当方は触れない — 写し注記で統合を宣言)/ 手順本体の改訂(工程 0〜6 の
   規律は不変)/ Codex 以外の工場への一般化 / lesson-promote の正本化(別件・harness 専用)。

## 2. 影響なし予測(反証可能・製造前に凍結)

- diff= 新規 2 ファイル(正本・写し)+ `bomdd-init.py` 1 行 + README 2 箇所 + product-profile/README.md 1 行 + 台帳系。**他の 11 スキル・
  hooks・self-conformance.py・playbook は diff 0**。
- self-conformance: C7 は README 12 = SKILLS 12 で PASS(11 のままなら FAIL — 変更に対して感度あり)。C4 scaffold は 12 本を配布し
  「AGENTS.md 参照スキル」件数が +2(product/cad の 2 テンプレ)になる可能性 — 件数表示のみで判定不変。C13 は写しの相対リンク 1 本
  (`../../../method/templates/product-profile/skills/factory-delegate.md`)が追跡集合へ解決。C14 kit-freshness は対照実測のみ・不変。
- 製品リポ: 既存 kit は `bomdd.lock` で凍結(STALE は advisory)。新規 scaffold から 12 本。

## 3. 受入

- **V1**: self-conformance 全 PASS(C7 が 12/12・C4 scaffold に factory-delegate が配置される)。
- **V2**: 正本と写しの差分= 写し注記ブロック+`{{METHOD}}` 解決の 2 箇所のみ(frontmatter 同一)。
- **V3**: 旧写し(`~/.claude/skills/factory-delegate/SKILL.md`)と正本の本文差分= 冒頭注記+工程 2 追記のみ(手順本体の逸脱 0)。
- **V4**: CI 緑(headSha 照合)。**V5**: diff 窓= allowed_paths+台帳系のみ。
- **witness**: 検査 exit 観測後に `bomdd-witness.py produce --eco ECO-063` → `verify --eco ECO-063` が ADVANCE のときだけ commit(ECO-062 の機構を実運用)。
- 独立検査: **製造者較正のみで受入**(散文の移設・機械挙動の変更= `SKILLS` 定数 1 名追加のみ・ECO-061 の先例)。user が異系統検査を求めれば §8 として追加。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-063` の出力を開始 artifact として読んだ〔§6〕)

- 分類= 既裁定の適用実装(方向= ECO-062 裁定 2・実施= Phase 4 指示)。baseline `a45f30b`= **confirmed**(HEAD・作業木 clean)/ 次番 063=
  **confirmed**(register 末尾= 062)/ 旧写しの実在= **confirmed**(115 行・実読)/ 配布機構= **confirmed**(`SKILLS` 定数・C7 の突合式を実読)/
  写し規約= **confirmed**(preflight.md の写しヘッダを実読)/ 凍結の非該当= **confirmed**(converge・calibrate 非接触)/ 同一ファイルへの進行中 ECO なし=
  **confirmed**。job ビュー(§6)の `required_skills`= null(F1・出所なし)→ スキル起動は自発起動に依存(EXP-20260910-01 の限界として記録)。
- 開始判定: **PROCEED**・override 0。

## /converge receipt(起動経路: 自発 — 正本化の範囲設計)

- **判定: 収束**(round 軌跡: 2→0→0)。
- DoD: ✔ 移設であり手順本体を変えない / ✔ 追記は実測済みの経路知見のみ(新規則なし) / ✔ 配布・写し・README の 3 経路を同一 commit で揃える(C7 が感度を持つ)/
  ✔ 旧写し(利用者環境)は触れず統合を宣言 / ✔ job 経由の起動と witness 遷移を記録する。
- round 1(新規 2 件): ①`{{METHOD}}` を playbook 参照に使う(他スキルと同型・写しで解決)②ハーネス依存部(Agent ツール・codex-rescue)を工程 2 に
  局在させ、他ハーネスの読み替え点を明示。round 2: 0 件。round 3: 0 件。
- 検証した主張: `SKILLS` 定数と C7 の突合式(self-conformance.py:521-529 実読)/ README の「スキル 11 本」2 箇所(grep)/ 写し規約(preflight.md・SKILL.md 冒頭)/
  旧写し 115 行(実読)。
- 敵対自問: 「正本化に乗じて手順を改訂していないか」— 追記は工程 2 の切替手順のみで、規律 4 項・工程 0〜6 の文は不変(V3 で diff を測る)。
  「lesson-promote も同時に正本化すべきでは」— harness 専用(method 還元の入口)で製品リポに配布しない → 対象外(§1-6)。
- 未収束事項: なし。

## 6. Phase 4 実測(job 経由の起動・witness 遷移)

- **job 経由の起動**: `python method/tools/bomdd-job.py ECO-063`(register 追記直後・製造前)→ `state: decided`・`stop_type: NONE`(register と order に矛盾なし)・
  `write_scope`= allowed_paths 8 パス・`diff_baseline`= a45f30b・`required_skills: null`(F1・出所なし)。job ビューを開始 artifact として読み、preflight receipt の
  前提(baseline・write_scope・inputs)は job の値を用いた。**運転員= 当方(製造者と同一)** — Phase 4 は「Claude Code 単独運用」なので運転員の独立性はない。
- **スキルの起動**(EXP-20260910-01 の初回観測・self-report): job の `required_skills` が null のため明示起動は起きず、**自発起動に依存**。実績= preflight 起動(receipt 上記)・
  converge 起動(receipt 上記)・calibrate は verified 昇格時(§7)。非起動 0/2(受入時 0/3 を §7 で確定)。**対照(job なし工程)は同期間に存在せず感度側のみ**。
  明示起動の効果は F1(task class → スキル対応表)が実装されるまで測れない — Phase 4 の限界として記録。
- **V1**= PASS(self-conformance 全 PASS・exit 0・C7 `[12, 12] = SKILLS 実数 12`〔11 のままなら FAIL — 感度の実証〕・C4 scaffold 参照スキル 22→24 件・C13 217 links 不在 0・C14 7/7)。
- **V2**= PASS(正本と写しの diff= 8 行= 写し注記ブロック 5 行+正典行 1 行+`{{METHOD}}` 解決 2 行・frontmatter 同一)。
- **V3**= PASS(旧写し `~/.claude/skills/factory-delegate/SKILL.md` との本文差分= 出自注記の追加〔ViewPrism2 の明記+正本化の注記〕・工程 2 の見出し語+経路切替の追記・
  工程 5 の全角括弧 1 文字の正規化。規律 4 項・工程 0〜6 の手順文は不変)。frontmatter の description は旧写しと同一(初版で 1 語縮めたのを V3 で検出し復元)。
- **witness**: 本 §6 記入後に self-conformance を再実行し、その exit を gate として `bomdd-witness.py produce --eco ECO-063` → `verify --eco ECO-063` が ADVANCE のときだけ
  commit(結果は commit message と §7 に記録)。
