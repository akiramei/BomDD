# ECO-010 — bomdd-init がハーネス中立の入口(AGENTS.md)を生成せず、別ハーネスが入口スキルを初手で発見できない

## 起票(2026-07-11)

- 出典: **Codex(GPT)による BomDD 管理リポでの運用ログ観測**(2026-07-11・maintainer 提供)。
  Codex は初手で「/eco-file はこのセッションの利用可能スキル一覧にはありません」と認識し、
  「同等の起票」を自前で開始 → 途中でリポ探索により `.claude/skills/eco-file/SKILL.md` を発見し
  「正規手順が見つかりました。ここからはその手順を完全に読み、指定どおり起票・工程診断を
  進めます」と正本準拠へ切替えた。**結果は健全(発見→正本準拠)だが、初手からの発見が
  できなかった** — 入口の発見可能性がハーネス固有。
- 根因: scaffold(bomdd-init)の生成物は `CLAUDE.md` + `.claude/skills/`(いずれも
  **Claude Code のハーネス規約**)のみ。Codex 等が初手で読む規約ファイル **`AGENTS.md`
  (リポ直下)が生成されない**。ハーネス中立な入口ポインタの欠落。
- 既知観測との接続(方法論側はすでに測定済みの系列):
  - transfer-03「文化は横断し、様式は横断しない」(FINDINGS §11.2)
  - ECO-060「入口コマンド化(ラダー③)は起動されなければ存在しないのと同じ」(§11.3・playbook §13)
  - 本件= ③の**発見層**版。入口様式の非横断が「無視」でなく「不可視」として現れた初観測。
- 実測(2026-07-11): ViewPrism2 に AGENTS.md 不在を確認(scaffold 由来の全製品リポで同様)。
  transfer 系列(別ハーネス担当者の継続運用ラウンド)では、初手発見の遅延が
  tooling_gap(梱包の破れ)として測定を汚す交絡になる。

## 裁定

- ユーザー製造指示(2026-07-11)「/eco-fix eco-010」— 当セッションに同名スキルは無いため
  (それ自体が本 ECO の主題の自己実演)、明示のコマンド起動を製造承認として受理。
  案 4(CLAUDE.md 相互参照 1 行)は推奨どおり**採用**(可逆な 1 行・乖離債務なし)。

### 是正方針(裁定済み)

1. `method/templates/product-profile/` に **AGENTS.md テンプレ新設**。内容は**薄いポインタのみ**
   (変更管理正本・入口 SKILL.md への実パス・台帳・validator・human gate の 2 点)。
   スキル本文が単一正本 — AGENTS.md に手順を複製しない(乖離債務を作らない。
   ECO-004 で kit を選別しなかったのと同じ理由)。
2. bomdd-init の 3 経路(scaffold_product / scaffold_cad / --skills-only)で AGENTS.md を生成。
   - スキル一覧は**実設置**を反映(ECO-009 #4 と同族 — install される skills 引数と同期)。
   - **CAD リポの AGENTS.md は CAD 用内容**(スキルなし・裁定台帳/権威宣言への参照)—
     ECO-009 の教訓「影響分析も副経路を見落とす」(silence §16(d))の適用として、
     CAD 経路を起票時点から影響範囲に含める。
   - 既存 AGENTS.md は保持(kit と同じ fail-safe — 無断上書きしない)。
3. self-conformance **C4(scaffold 煙試験)へ収載**: AGENTS.md の存在+参照先スキルの実在+
   絶対パス漏れ 0(rglob 対象に自動で入るが、存在検査を明示)。陽性対照つき
   (playbook §13: 検査の新設は陽性対照と対で)。
4. CLAUDE.md テンプレへの相互参照 1 行(「非 Claude ハーネスは AGENTS.md 参照」)は
   gate で採否裁定(任意)。

## 影響分析(製造前凍結)

- 影響なし予測: `method/tools/bomdd-init.py`・`method/templates/product-profile/`(AGENTS
  テンプレ新設+CLAUDE テンプレ 1 行の可能性)・`method/tools/self-conformance.py`(C4 拡張)
  以外は diff ゼロ。既存製品リポには波及しない(init は生成時のみ)。
  正常系 scaffold の既存生成物(CLAUDE.md・skills・kit・lock)は不変 — 追加は AGENTS.md のみ。

## 是正(2026-07-11)

1. テンプレ新設: `AGENTS.product.md`(スキル表は `{{SKILLS_TABLE}}` で実設置分を動的生成・
   用途説明は複製せず「SKILL.md の冒頭に用途」と参照)+ `AGENTS.cad.md`(CAD 用 —
   実装しない宣言・裁定台帳参照・スキルなし)。human gate 2 点と
   「自然文の了承を実行へ昇格させない」(ECO-060 再発防止)を両テンプレに明記。
2. bomdd-init: `_skills_table()`+`install_agents()` 新設。3 経路で生成 —
   scaffold_product(SKILLS)/ scaffold_cad(CAD 版・skills=[])/ --skills-only(selected=
   実設置のみ記載・ECO-009 #4 と同族の正直記録)。既存 AGENTS.md は保持(kit と同じ fail-safe)。
3. CLAUDE.product.md / CLAUDE.cad.md へ相互参照 1 行(案 4 採用)。
4. self-conformance C4 へ収載: AGENTS.md の存在+参照する SKILL.md の全実在
   (regex 抽出→実在突合。参照ゼロも FAIL = 空ポインタの vacuous pass 遮断)。

## 検証(2026-07-11・検証治具 10 項目全 PASS)

- **V1(正常系)**: scaffold → AGENTS.md 生成・スキル参照 16 件(8 スキル×コマンド列+リンク列)
  全実在・placeholder 全解決・CLAUDE.md に相互参照。
- **V2(CAD 経路)**: --gui → CAD リポの AGENTS.md は CAD 用内容(「ここでは実装しません」・
  スキル表参照なし)+CAD 側 CLAUDE.md にも相互参照 — ECO-009 教訓(§16(d) 副経路)を
  起票時から影響範囲に含めた経路の実測。
- **V3(部分集合)**: `--skills-only --skills bomdd-next,eco-file` → 記載も 2 本のみ(正直記録)。
- **V4(fail-safe)**: 既存 AGENTS.md(SENTINEL)を保持し上書きしない。
- **V5(変異=対象欠落チャレンジ)**: AGENTS.md 削除 → C4 同一ロジックが FAIL —
  是正前の scaffold 出力(AGENTS.md 不在)に対して新 C4 が FAIL することの等価証明=陽性対照。
- **V6(変異=参照切れ)**: SKILL.md を 1 本削除 → missing 検出で FAIL。
- gate fast 全 PASS(C4 に「AGENTS.md 参照スキル 16 件」が恒久収載)。
- 影響なし予測: 的中(diff は bomdd-init.py・product-profile/・self-conformance.py のみ)。

## 関連

- **製品リポ側の即効修正(②)**: ViewPrism2 へ AGENTS.md を先行配置(2026-07-11・maintainer 指示)。
  ViewPrism2 R1 のスコープは src/tests のため ECO 不要(CLAUDE.md と同格のハーネス配線)。
  恒久形は本 ECO の scaffold/kit 経由 — 先行配置の内容が本 ECO のテンプレ原型になる。

## 教訓(還元候補 — lesson-promote 経由)

- **入口様式の非横断は「無視」の前に「不可視」として現れる**(発見層): ラダー③の強制力は
  「起動された場合」に限る(ECO-060)だけでなく、**ハーネスが違えば起動可能性の手前の
  発見可能性から失われる**。入口はハーネスごとの初手読み込み規約(CLAUDE.md/AGENTS.md 等)
  すべてに**ポインタを置く**(本文は単一正本)。ECO-060(§11.3)への追補候補 —
  継続運用×異ハーネスの 2 例目(rule of three は 3 例目待ち)。
