# Change Order — ECO-032(/converge を配布スキルへ昇格し、正本を BomDD へ移す)

> 裁定: user 2026-08-28「convergeスキルは私が観測した限り役立っています」「現在、十分実績があると
> 私は判断しています」「正本を BomDD へ移す前提で ECO-032 を起票して」。
> 経緯= TimetableAdv を BomDD で開発する中で「検討不足や推測が事実で否定されて後戻りする」問題への
> 対策として作成され、**実際に使用し実績を積んでから BomDD へ入れる**方針で保留されていた。
> gate ① 承認待ち。

## 担当設備(equipment)

- 製造(設計者):
  - requested: `claude-opus-5`
  - resolved: `claude-opus-5`
  - ハーネス: Claude Code(Claude Agent SDK)
  - 来歴: **self-reported**
- 検査官: なし(独立検査なし)

## 0. 実測(起票根拠・2026-08-28)

### 現状の所在

- **converge の現正本は TimetableAdv 側**: `bomdd/60-change-order-eco-023.md`
  (filed 2026-08-24 / status applied・golden 合格・クローズ 2026-08-25)が
  「設計収束ループ /converge を統治された入口スキルとして正典化する」と宣言。
  実体は `TimetableAdv/.claude/skills/converge/SKILL.md`(87 行)。
- **BomDD 側に実体はない**: `git ls-files | grep -i converge` = 0 件。
  言及は `method/improvements.md`(2026-08-11 の採用記録)1 ファイルのみ。
- **配布リストに入っていない**: `method/tools/bomdd-init.py:48` の
  `SKILLS`= 8 本(`bomdd-next` `eco-file` `eco-fix` `eco-accept` `sec-advisory`
  `bomdd-refmodel` `bomdd-mock-lint` `bomdd-ui-cad`)。
- したがって **bomdd-init で作った新規プロジェクトへ converge は配布されない**。
  BomDD 側で本手順を適用できていたのは、TimetableAdv の原文を読みに行っていたためであり、
  BomDD 単体にその参照経路は存在しない。

### 実績(リポ面で確認できる範囲)

- **TimetableAdv**: 出自= golden 統制設計(ECO-022 前段)の裁定候補レビューが**人間の中継で
  8 往復**を要し、差し戻しの大半が AI 自身でリポジトリ実測により反証できた主張だった。
  収束 receipt を埋め込んだ成果物 **1 件**(`bomdd/ui/public-demo-closed-alpha-v1/
  night-core-loop-cad-v1/PUBLIC-DEMO-NIGHT-CORE-LOOP-CAD-V1-001.md`)+ ECO-023 自身。
  注記: リポ内の `converge` 一致 82 ファイルの大半は**英単語 `convergence`**(ゲーム内の
  収束概念)であり適用実績ではない — 計数を実績と誤読しないこと。
- **BomDD**: 2026-08-11 に「裁定側の作業規律としてのみ採る」として採用(improvements.md 同節)。
  `EXP-20260811-01` で 2 回観測。**2026-08-28(本セッション)の適用で、提示前の前提 5 件が
  実測で反証された**:

  | # | 崩れた前提 | 実測 | 座標 |
  |---|---|---|---|
  | 1 | LF で統一されている | CR blob 70 件 | ECO-030 §0 |
  | 2 | kit は `render()` の newline 明示を通る | `copytree`/`copy2` のバイトコピー | ECO-030 §0 |
  | 3 | `git status` がクリーンなら index と一致 | stat キャッシュに 2 件の乖離 | ECO-030 §0 副次実測 |
  | 4 | 既定が是正になっている | 層別の既定が未宣言なだけ | improvements 2026-08-28 節・観測 1 |
  | 5 | §8.5 追記はハーネス変更で ECO が要る | 列挙外・`/lesson-promote` 経路 | 同・観測 3 |

  **うち 5 が提示済み選択肢の重さを変え、1〜3 が ECO-030 のスコープを正した。**
  いずれも converge を起動しなければ記録に入ってから反証される性質のものだった
  (= EXP-20260809-01 が測る「到達距離」を縮める側の実測)。

### 配布物としての適合(実測)

- 既存配布スキル 8 本= 38〜50 行・frontmatter(`name` / `description`)あり・
  `{{METHOD}}` 等のプレースホルダーを `render()` で置換。
- converge SKILL.md= 87 行・frontmatter 様式は**一致**・プレースホルダー**なし**・
  **markdown リンク 0 件**(→ C13 リンク実在検査への露出なし)。
- **製品固有 ID が 6 件**埋まっている: `ECO-013` `ECO-021` `ECO-022` `ECO-023`×2 `FO-SIT-FIX-003`
  — 失敗型カタログの実例欄。**そのまま配ると新規プロジェクトが他製品のインシデント記録を継承する。**

## 1. 変更要求

### (a) 正本移管【製造対象】

`method/templates/product-profile/skills/converge.md` を新設し、**BomDD を正本**とする。
TimetableAdv 側は配布を受ける側へ降格する(下記スコープ外)。

### (b) 配布リストへの追加【製造対象】

`method/tools/bomdd-init.py` の `SKILLS` へ `"converge"` を追加(8 本 → 9 本)。

### (c) 失敗型カタログのテーラリング方式【**gate ① 裁定: A-1 採択**】

配布後、SKILL の学習ループ(「新しい型なら本 SKILL の表へ追記を提案する」)は**各製品リポで**
発火する。カタログを丸ごと配ると、追記が製品ごとに分岐して**カタログ自体が二正本問題を
再生産**する。方式の候補:

- **A-1(推奨)**: 表を〈**汎用型**(製品名を含まない命題・BomDD が正本)〉と
  〈**製品固有の実例・追記領域**(各製品リポが所有)〉に分離する。配布時は汎用型のみを載せ、
  実例欄は「初出」参照(製品リポ名+ECO 番号)として残すか空にする。
  学習ループの追記先は製品側の追記領域とし、汎用化して BomDD へ戻すのは `/lesson-promote` の仕事。
- **A-2**: 現行カタログを実例ごとそのまま配る(TimetableAdv の 6 件が全プロジェクトへ入る)。
- **A-3**: 実例を全削除して型だけ配る(具体性が落ち、型の識別が難しくなる可能性)。

### (d) BomDD 自身への設置の要否【**gate ① 裁定: D-1 採択**】

BomDD は製品リポではなく `bomdd-init` の配布先でもないため、正本(`product-profile/skills/`)を
置いても **BomDD 自身の `.claude/skills/` には入らない**。BomDD 側の裁定作業で使うなら
別途設置が要る(現状は TimetableAdv の原文を読みに行っている = 他リポ依存)。

- **D-1(推奨)**: `.claude/skills/converge/SKILL.md` を置く。ただし**正本は
  `product-profile/skills/converge.md`** とし、BomDD 側は写しであることを明記する
  (二正本を避けるため、同期規則を本 ECO で決める)。
- **D-2**: 置かず、BomDD 側は正本ファイルを直接読む運用にする(`.claude/skills/` に無いので
  `/converge` としては起動できない)。

## gate ①(製造承認)

- **承認 2026-08-28 maintainer**:「gate ① 承認。A-1 + D-1 で製造に進んで」
- 裁定 3 点 = ①製造承認 ②(c)= **A-1**(汎用型は BomDD 正本 / 実例と追記領域は製品側が所有・
  汎用化して戻すのは `/lesson-promote` の仕事)③(d)= **D-1**(BomDD にも写しを置き、正本が
  `product-profile/skills/converge.md` であることを明記し同期規則を定める)。
- 本 order の較正 CAL-1/CAL-2 と受入 V1〜V5 は起票時に凍結済み・変更なし
  (V2 は A-1 採択のため「配布された SKILL.md に製品固有 ID が残っていない」で確定)。

## スコープ外(宣言済み境界 — 本 ECO で明文化して残す)

- **TimetableAdv 側の正本降格・同期**: 別リポの変更であり **TimetableAdv 側の ECO** で行う
  (同リポ ECO-023 が現地ファイルを正典と宣言しているため、本 ECO 単独では閉じない)。
  本 ECO は BomDD 側の配布仕様のみを扱う。
- **既設製品リポ(ViewTube・Plm 等)への遡及設置**: 各リポの裁定。
  2026-08-11 の裁定「ViewTube には入れない(新規 workflow authority の追加は process policy の
  拡張で凍結に触れ、AGENTS.md は保護パス)」は**既設リポへの後付け**に関するもので、
  新規プロジェクトへの配布とは別問題として生きている。
- **`self-conformance` への converge 固有検査の追加**: 採らない
  (playbook §8.5 — 様式化・validator 強制は実測後に判断)。

## 2. 影響なし予測(反証可能・製造前に凍結)

- diff は次の**3 ファイル + 台帳系**のみ、他は diff ゼロ:
  `method/templates/product-profile/skills/converge.md`(新設)/
  `method/tools/bomdd-init.py`(`SKILLS` 1 行)/ `README.md`(下記)。
  (d) の裁定次第で `.claude/skills/converge/SKILL.md` が加わる。
- **C7 は README を直さなければ FAIL する**(実測で確認した結合):
  `self-conformance.py:414` の `c7_readme()` は `bomdd-init.py` の `SKILLS` 実数と
  README 内の正規表現 `スキル\s*(\d+)\s*本` の全一致を検査する。現在 README.md:19 に
  「スキル 8 本」があり、**SKILLS を 9 本にすると不一致で FAIL**。
  → 本 ECO は README.md:19 の表記を 9 本へ更新することを**製造に含める**。
  これは「既存依存の新しい使い方でその依存の既定値を製造前に列挙する」(EXP-20260727-09)の
  適用であり、同 EXP は直近 2 例連続で反証されている — 本 ECO はその処方の 3 度目の試行にあたる。
- **C4 は判定不変**: `c4_scaffold()` は AGENTS.md の参照スキル数を**表示するだけ**で、
  検査は「参照が非空」かつ「参照先 SKILL.md が全実在」(`self-conformance.py:218-226`)。
  固定本数の assertion はない。生成器が新スキルを render し AGENTS.md へ載せる限り PASS。
- **C13 は判定不変**: converge SKILL.md の markdown リンクは **0 件**(実測)。
- 既存 8 スキルの内容・挙動は不変。既設製品リポへは **kit 再設置まで非波及**。
- **適用範囲の二重化は起きない**: SKILL 本文が「機械受入がある是正実施には使わない
  (`/eco-fix` がその収束機構)」と適用外を宣言しており、TimetableAdv で実証済み。

## 3. 較正と受入(起票時凍結)

**是正と予防を兼ねる統制ではない**(新規配布物の追加であり既存違反の除去ではない)ため、
playbook §4.4 の対応表では**予防側**にあたる。赤プローブは原理的に存在しないので
**陽性対照で較正する**(ECO-030 で予防面の対照を設計し損ねた反省の適用 — OBS-20260828-05)。

- **較正(赤・予防ゲートの陽性対照)**:
  - **CAL-1**: `SKILLS` を 9 本にした状態で README を 8 本のままにすると **C7 が FAIL する**
    ことを実測する(検査が実際に発火することの確認 — 空振りでないことの証拠)。
  - **CAL-2**: scaffold した製品リポに `converge` の SKILL.md が**存在しない**状態を作ると
    C4 が FAIL することを実測する(参照と実体の結線が効いていることの確認)。
- 受入:
  - **V1**: `bomdd-init` で scaffold した製品リポに `.claude/skills/converge/SKILL.md` が
    実在し、AGENTS.md から参照されている。
  - **V2**: 配布された SKILL.md に**製品固有 ID が残っていない**((c) の裁定が A-1/A-3 の場合)。
    A-2 採択時は本項を「実例が意図どおり残っている」へ読み替える。
  - **V3**: `self-conformance` 全検査 PASS(**C7 が 9 本で一致**・C4・C13 込み)。
  - **V4**: push 後 CI 緑(4 値判定)。
  - **V5**: diff が影響なし予測の窓内(3 ファイル + 台帳系 +(d)裁定分)に収まる。

## 4. 製造と較正の実測(2026-08-28)

### 製造

- diff 監査の窓: baseline `731d9fb`(gate ① 記録コミット= 是正開始直前)→ head は本節末に追記。
- (a) `method/templates/product-profile/skills/converge.md` を新設(111 行)。**A-1 テーラリング**:
  失敗型カタログを〈**表 A= 汎用型**(方法論側の正本・型の記述から製品固有の記述を除去し初出の
  来歴のみ残す)〉と〈**表 B= 本リポ固有**(製品リポが所有する空の追記領域)〉へ分離。
  学習ループの追記先を表 B に固定し、汎用化して表 A へ戻すのは `/lesson-promote` の仕事だと本文へ明記。
- (b) `bomdd-init.py` の `SKILLS` へ `converge` を追加(8 → 9 本)+ README のスキル本数表記を更新。
- (d) D-1: `.claude/skills/converge/SKILL.md`(117 行)を写しとして設置。冒頭に正本の所在と
  同期規則(変更は正本側へ入れる・本ファイルだけを直接編集しない)を明記。
- 元 SKILL からの実質的追加 3 点(本セッションまでの実測の反映): 失敗型 **⑦ 選択肢集合の欠落**
  (初出= BomDD 2026-08-28・EXP-20260811-01 の測定対象)/ 手順 3 へ「**効果の予測は本手順では
  裏取れない**」の明記 / 自発起動契約へ「散文の規定は起動を保証しない・**起動したこと自体を
  成果物に残す**」の注記(OBS-20260828-02)。

### 較正(予防ゲート — 陽性対照。**下記の赤は期待された赤であり不適合ではない**)

- **CAL-1 成立**: `SKILLS` を 9 本にし README を 8 本のままにした状態で `self-conformance` を実行:

  ```
  [C7] FAIL README のスキル本数表記 [8] = SKILLS 実数 9
  self-conformance FAILED — 1 件の不適合   (exit 1)
  ```

  **落ちたのは C7 の 1 件のみ**で、同実行の `[C4] PASS`(参照スキル 18 件)・
  `[C13] PASS`(設置先文脈 25 files/71 links)は判定不変 — **その規則固有の理由で赤くなり、
  他検査の巻き添えや schema 不足で覆い隠されていない**ことの実測(DoD 条件)。
- **CAL-2 成立**: `bomdd-init` で実 scaffold を生成し、`self-conformance.py:223-226` と同一の
  判定ロジック(AGENTS.md の参照抽出 → 参照先 SKILL.md の実在確認)を適用:

  ```
  [CAL-2 前] 判定= PASS / 参照 18 件(ユニーク 9 スキル・各 2 回参照)
  [CAL-2 後] 判定= FAIL / missing= ['converge']
  [CAL-2] 陽性対照= 成立(PASS→FAIL へ転化・巻き添えなし)
  ```

  converge の SKILL.md を削除すると PASS → FAIL へ転化し、他スキルへの巻き添えはゼロ。
- **由来**: ECO-030 は予防面の陽性対照を設計せず偶発の実発生に依存した(OBS-20260828-05)。
  本 ECO はその反省を起票時に適用した最初の事例であり、**EXP-20260828-06 の第 1 回観測**にあたる。

### 受入

- **V1 PASS**: 実 scaffold で `.claude/skills/converge/SKILL.md` が実在し、AGENTS.md から
  参照されている(判定 PASS・missing なし)。加えて **BomDD 側の写しはハーネスのスキル一覧へ
  実際に現れた**(D-1 の実地確認)。
- **V2 PASS**(A-1 採択のため「製品固有 ID が残っていない」で判定): 配布された SKILL.md に
  `FO-SIT-FIX-003` `ECO-013` `ECO-021` `ECO-022` の残存**なし**。表 B(製品固有の追記領域)が
  存在し、プレースホルダーは置換済み。
- **V3 PASS**: `self-conformance` 全 17 検査 PASS・FAIL 0・exit 0。
  `[C7] PASS README のスキル本数表記 [9] = SKILLS 実数 9` で復帰。
- **V5 PASS**: 変更は `README.md` / `method/tools/bomdd-init.py` /
  `method/templates/product-profile/skills/converge.md`(新設)/ `.claude/skills/converge/`(新設・
  裁定 D-1 分)+ 台帳系のみ — **影響なし予測の窓内**。
- **V4**: 下記。

### 製造中の計器の所見(記録)

写しを生成する処理に置いた `assert '{{' not in body` が、**未置換のプレースホルダー 1 件を
捕捉した**(「表 A は方法論側の正本(`{{METHOD}}` 配下)」— `/method/` が続かないため単純置換から
漏れていた)。assert がなければプレースホルダーの露出した写しがそのまま入っていた。
**fail-closed が設置者の眼前で作動した実測**(§13 遮断方向の規則)。

## 5. CI 実測(V4)

- 対象 revision: `b3503f4135655ba3f23cffe74e241049f915f641`(**ローカル HEAD と一致を確認**)
- 規則版: workflow `self-conformance`(リポ内定義= 測定器)
- run 識別子: 33120966741 — https://github.com/akiramei/BomDD/actions/runs/33120966741
- 結論: **PASS**(`status: completed` / `conclusion: success`)
- 観測日時 / 観測主体: 2026-08-28 / 本 ECO の担当設備(§担当設備)
- UNKNOWN の理由コード: 該当なし。**ただし取得時に「別 commit の結果しかない」状態を一度経由した**
  — `gh run list --limit 1` は push 直後で前回 push の run(33117916712 / `c987e34`)を返しており、
  `headSha` で照合せずに使えば前回の緑を本 ECO の結論として記録していた。**照合を経て正しい run
  を特定**した(§13 の 4 値判定・理由コード「別 commit の結果しかない」の実発生と回避)。

## 6. クローズ

- diff 監査の窓: baseline `731d9fb` → head `b3503f4`(**窓閉鎖**)。窓内は
  `README.md` / `method/tools/bomdd-init.py` / `method/templates/product-profile/skills/converge.md`(新設)/
  `.claude/skills/converge/SKILL.md`(新設・裁定 D-1 分)+ 台帳系のみ — 影響なし予測が的中。
- 受入: V1 / V2 / V3 / V4 / V5 すべて PASS。較正 CAL-1 / CAL-2 いずれも成立。
- **恒久回帰**: C7(README のスキル本数 = SKILLS 実数)と C4(AGENTS.md 参照スキルの実在)が
  本変更クラスの再発を遮断する。**両者が実際に作動することの陽性対照を製造中に実測済み**
  (CAL-1 / CAL-2・§4)。§13「恒久回帰と、その検出器が実際に作動することを示す陽性対照を
  自己適合ゲートへ収載してからクローズする」を充足。
  **ECO-030 との差**: あちらは予防面の対照を設計せず偶発の実発生に依存した。本 ECO は
  起票時に設計して製造中に発火させた = **EXP-20260828-06 の第 1 回観測**。
- 残(いずれも本 ECO のスコープ外・宣言済み境界):
  - **TimetableAdv 側の正本降格・同期** — 移管先が実在したため起票可能な状態になった。別リポ ECO。
  - 既設製品リポへの遡及設置 — 各リポの裁定。
  - `self-conformance` への converge 固有検査の追加 — §8.5 に従い実測後。
