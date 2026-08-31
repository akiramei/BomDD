# Change Order — ECO-035(測定系較正スキル /calibrate の新設 — 証拠品質+検査器検査の工程入口)

> 裁定: user 2026-08-31「測定系較正(証拠品質+検査器検査の統合)について作成してください。
> もし、調査や設計が必要ならそれもおもなってください」— 調査・設計・作成の一括委任。
> 細目(名称・テーラリング方式・BomDD 写し)は担当設備が前例(ECO-032)に基づき採択し、
> maintainer の差し戻しに服する(下記 gate ① 節)。

## 担当設備(equipment)

- 製造(設計者):
  - requested: `claude-fable-5`
  - resolved: `claude-fable-5`
  - ハーネス: Claude Code(Claude Agent SDK)
  - 来歴: **self-reported**
- 検査官: なし(独立検査なし)

## 0. 実測(起票根拠・2026-08-31)

### 教義は正本にあるが、工程入口が無い

- **査定の教義は playbook §4.4 に正本がある**: 較正(negative control)・較正期待表の三点様式・
  「較正の形式的成立は被覆を証明しない」・「検査文はコードが測る以上を主張しない」・
  常設検査器の陽性対照・道具の個体参照・ablation・lineage 閉包
  (`method/bomdd-playbook-v1.md:135-263`)。
- **それでも計器欠陥は反復した**(いずれもリポ内の一次記録で確認可能):
  - CI が赤のまま **11 コミット・約 2 日・5 ECO を跨いで潜伏**(BomDD ECO-020 — 装置・操作対象は
    あり結線だけが無い。`CLAUDE.md` に背景恒久記載)
  - 検査結果(`exit=1`)が**観測される前に push が実行**(BomDD ECO-024)
  - 新設ゲート C16 が**同一弧内で偽陽性(出口なし)と過剰免除(自己免除)を連発**
    (BomDD ECO-033→034 — 受入 5 項目成立の直後)
  - **宣言 fixture への製品コード参照 0 件のまま CP 8 行全緑+human golden 合格・潜伏 14h15m**
    (TimetableAdv ECO-037→038 — 2026-08-31 還元済み・`method/cheat-taxonomy.md` LP 6 例目)
- **証拠の資格査定を判定時に起動する工程入口スキルは存在しない**: `method/tools/bomdd-init.py:48`
  の SKILLS= 9 本(`bomdd-next` `eco-file` `eco-fix` `eco-accept` `sec-advisory` `bomdd-refmodel`
  `bomdd-mock-lint` `bomdd-ui-cad` `converge`)。`/converge` は設計合成の収束であり、適用外を
  「機械受入がある是正実施には使わない」と明示宣言している — 証拠査定はまさにその宣言の外側で
  必要になる(ECO-033→034 の実測)。`git grep calibrate` = 0 件(名称衝突なし)。

### 前例(様式の由来)

ECO-032(/converge の配布スキル昇格)が同一クラスの変更様式を確立済み:
A-1(汎用型は BomDD 正本・実例と追記領域は製品側所有・汎用化は `/lesson-promote`)+
D-1(BomDD へ写しを設置し正本と同期規則を明記)+ CAL-1/CAL-2(配布結線の陽性対照)+
V1〜V5。本 ECO はこの様式を踏襲する。

## 1. 変更要求

### (a) 正本新設【製造対象】

`method/templates/product-profile/skills/calibrate.md` を新設し、**BomDD を正本**とする。
内容= 測定系較正ループ: 自発起動契約(受入節の執筆・緑の引用・検査器の新設変更直後・検査器
インシデント後 — いずれも必ず起きるイベントへアンカー)/ 検査 battery Q1〜Q10(各行に §4.4・
AGENTS.md 規律・cheat-taxonomy の正本アンカーを付け、**教義を複製せず参照する**)/
較正 receipt(3 値判定+計器欠陥+検出力の限界。成果物へ埋め込み・新 artifact 置場を作らない)/
失敗型カタログ 表 A(汎用 10 型・全行実測起源・初出来歴つき)+表 B(製品側追記領域)。

### (b) 配布リストへの追加【製造対象】

`method/tools/bomdd-init.py` の `SKILLS` へ `"calibrate"` を追加(9 本 → 10 本)+
README のスキル本数表記を更新(C7 結合 — §2)。

### (c) テーラリング方式【前例採択: A-1】

ECO-032 gate ① の A-1 裁定(汎用型= BomDD 正本 / 実例・追記領域= 製品側所有 / 汎用化して
戻すのは `/lesson-promote`)は本 ECO と同一の構造に適用できるため、**再裁定せず踏襲**する。
表 A の記述は製品固有 ID を本文に含めず、初出列の来歴(リポ名+ECO 番号)のみ許す。

### (d) BomDD 自身への設置【前例採択: D-1】

ECO-032 gate ① の D-1 裁定を踏襲し、`.claude/skills/calibrate/SKILL.md` を**写し**として設置
(冒頭に正本の所在と同期規則を明記)。

### (e) 名称【本 ECO の新規裁定点】

`calibrate` を採択。理由= converge と同じ動詞 1 語の系列で、user の命名「測定系較正」に対応する。
検討した代替= `gauge`(計器検査に閉じて証拠品質側が落ちる)/ `msa`(製造業略語で自明性が低い)。
既存用語との二義(§4.4 の「較正」= negative control 工程)は SKILL 本文の用語節で明示的に
解消した(本スキルはそれを**含む**査定工程であり置換しない)。

### 選択肢集合(スキル新設以外のレバー — 不採理由つき)

| 案 | 内容 | 不採理由 |
|---|---|---|
| B-1 | `/converge` へ統合(手順に証拠査定を追加) | 適用範囲が排他(converge は「機械受入がある是正実施には使わない」と宣言済み・証拠査定はまさにそこで要る)。統合は両者の適用宣言を破壊する |
| B-2 | self-conformance へ機械検査として追加 | 散文工程の機械化は非起動の実測後に判断(§8.5・ECO-032 が converge で同じ裁定 → 実測 2 回の後に C16 が生まれた前例に従い、スキルが先) |
| B-3 | playbook 本文のみ(スキル化しない) | 教義は §4.4 に既にあるのに事故は反復した(§0)。欠けているのは教義でなく判定時の工程入口 |

## gate ①(製造承認の来歴)

- **承認**: user 2026-08-31 の作成指示(冒頭引用)を製造承認として扱う — 調査・設計を含む
  作成の一括委任であり、ECO-034 の「新規 ECO で起票して製造まで進めて」と同型。
- 細目の採択= (c) A-1 踏襲 /(d) D-1 踏襲(いずれも ECO-032 で maintainer 承認済みの方式の
  同一クラス適用)/(e) `calibrate` は担当設備の採択。**maintainer は本 order のレビューで
  いずれも差し戻せる**(スキルは配布前に kit 再設置が起きるまで既設リポへ波及しない)。

## スコープ外(宣言済み境界)

- **非起動の機械観測(C16 同型ゲートの calibrate 版)**: §8.5 に従い非起動の実測後に判断
  (converge が ECO-032 → 実測 2 回 → ECO-033 と辿った道を先取りしない)。
- **既設製品リポへの遡及設置・TimetableAdv 側への設置**: 各リポの裁定。
- **効果測定の EXP 記帳**: 効果(計器欠陥の受入前検出率)の予測は本 ECO では裏取れない —
  適用実績が出てから `/lesson-promote` 経路で記帳を判断する。
- **playbook §4.4 本文の変更**: 本 ECO は参照のみで教義に触れない。

## 2. 影響なし予測(反証可能・製造前に凍結)

- diff は次の **3 ファイル+写し+台帳系**のみ、他は diff ゼロ:
  `method/templates/product-profile/skills/calibrate.md`(新設)/
  `method/tools/bomdd-init.py`(`SKILLS` 1 行)/ `README.md`(スキル本数表記)/
  `.claude/skills/calibrate/SKILL.md`(新設・D-1 分)。
- **C7 は README を直さなければ FAIL する**(ECO-032 で実測済みの結合): `c7_readme()` は
  SKILLS 実数と README の「スキル N 本」全一致を検査。現在 README.md:19 は「スキル 9 本」。
  → README 更新を製造に含め、未更新状態を **CAL-1 の陽性対照**に使う。
- **C4 は判定不変**: 参照の非空+参照先 SKILL.md の実在検査のみ(固定本数 assertion なし)。
  生成器が新スキルを render し AGENTS.md へ載せる限り PASS。
- **C13 は判定不変**: 新設 SKILL の markdown リンクは写し冒頭の正本参照 1 件のみ
  (`../../../method/templates/product-profile/skills/calibrate.md` — 実在パス)。
- **C16 は本 order を required と判定する見込み**(hard-positive 語彙を含む)—
  `/converge` receipt を本 order へ埋め込む(下記)。
- 既存 9 スキルの内容・挙動は不変。既設製品リポへは **kit 再設置まで非波及**。
- 適用範囲の二重化は起きない: converge(設計合成)/ calibrate(証拠査定)/ eco-fix(是正実施)/
  eco-accept(クローズ事務)の排他境界を SKILL 本文の適用範囲節で宣言済み。

## 3. 較正と受入(起票時凍結)

新規配布物の追加であり既存違反の除去ではないため予防側 — **陽性対照で較正する**(ECO-032 様式)。

- **CAL-1**: `SKILLS`= 10 本・README= 9 本のままの状態で `self-conformance` を実行し、
  **C7 が単独で FAIL する**(その規則固有の理由で赤くなり、巻き添え・覆い隠しがない)ことを実測。
- **CAL-2**: `bomdd-init` の実 scaffold から `calibrate` の SKILL.md を除去すると、C4 と同一の
  判定(AGENTS.md 参照抽出 → 参照先実在)が PASS→FAIL(missing=['calibrate'])へ転化し、
  他スキルへの巻き添えがないことを実測。
- 受入:
  - **V1**: 実 scaffold に `.claude/skills/calibrate/SKILL.md` が実在し AGENTS.md から参照される。
  - **V2**: 配布 SKILL の本文記述(初出・出典列を除く)に製品固有 ID が残っていない。
  - **V3**: `self-conformance` 全検査 PASS(C7 が 10 本で一致・C4・C13・C16 込み)。
  - **V4**: push 後 CI 緑(4 値判定・headSha 照合)。
  - **V5**: diff が影響なし予測の窓内(3 ファイル+写し+台帳系)に収まる。
  - **V6(初回自己適用)**: 本 ECO の受入証拠 V1〜V5 自体へ `/calibrate` を初回適用し、
    較正 receipt を §4 末尾へ埋め込む(新設機構の初回使用者= 新設者 — ECO-034 の前例)。

## /converge receipt(本 order の設計に適用)

- 周回数と新規指摘: round 1 = 3 件(converge/eco-fix/eco-accept との境界宣言の精密化・
  選択肢集合 B-1〜B-3 の明示・V6 初回自己適用の追加)/ round 2 = 2 件(名称二義の用語節・
  C16 との関係宣言)/ round 3 = 1 件(初出来歴のリポ名修飾の必須化)。2 周連続ゼロ未到達の
  ため収束は主張しない(上限 3 周で提示)。
- 検証した主張(要点): 教義の所在= `method/bomdd-playbook-v1.md:135-263` 実読 / 工程入口の
  不在= `bomdd-init.py:48` SKILLS 9 本+`git grep calibrate` 0 件 / C7 結合= ECO-032 §2 の
  実測記録+README.md:19 実読 / C16 の receipt 判定条件= `self-conformance.py:902-1010` 実読
  (`## /converge receipt` 見出しが正規表現に一致することを確認)/ 事故 4 件の一次記録=
  register ECO-020/024/033/034+ECO-038 還元コミット(47cea59・9306769)実読 /
  中間 status の様式= `git show 44d2904:bomdd/60-change-register.yaml`(applied+V4/V5 push 後確定)。
- 未収束事項: なし(round 3 の 1 件は draft へ織り込み済み。効果の予測は本手順では裏取れない
  ため受入・適用実績へ回す — スコープ外節に記載)。

## 4. 製造と較正の実測(2026-08-31)

- diff 監査の窓: baseline `47cea59`(起票直前 HEAD)→ head は受入時に確定。
- (a) 正本 `method/templates/product-profile/skills/calibrate.md` を新設(プレースホルダーは
  `{{METHOD}}` のみ — render 対応済み語彙)。
- (b) `SKILLS` へ `calibrate` 追加(9→10 本)+ README.md:19 を 10 本表記へ更新。
- (d) 写し `.claude/skills/calibrate/SKILL.md` を設置(正本の所在・同期規則・由来を冒頭に明記。
  `{{METHOD}}/method/…` は自リポ相対 `method/…` へ解決)。設置直後、ハーネスの利用可能スキル
  一覧へ `/calibrate` が実際に出現した(D-1 の実地確認)。

### 較正(陽性対照 — **下記の赤は期待された赤であり不適合ではない**)

- **CAL-1 成立**: `SKILLS`= 10 本・README= 9 本のまま `self-conformance` を実行:

  ```
  [C7] FAIL README のスキル本数表記 [9] = SKILLS 実数 10
  self-conformance FAILED — 1 件の不適合   (exit 1)
  ```

  落ちたのは C7 の 1 件のみ。同実行の C4(参照スキル 20 件)・C13・C16 は PASS —
  その規則固有の理由で赤くなり、巻き添え・覆い隠しがない。
  正直記載: この実行は order 起票の書き込みと並走した(C16 の対象件数が 5 件時点)。
  C7 の判定は SKILLS と README のみに依存するため並走の影響はない。
- **CAL-2 成立**: `bomdd-init` の実 scaffold(`--no-gui --no-git`)へ C4 と同一の判定
  (AGENTS.md 参照抽出 → 参照先 SKILL.md 実在)を適用:

  ```
  [CAL-2 前] 判定= PASS / 参照 20 件(ユニーク 10 スキル)
  [CAL-2 後] 判定= FAIL / missing= ['calibrate', 'calibrate']
  ```

  除去で PASS→FAIL へ転化。missing のユニーク集合は {calibrate} のみで他スキルへの
  巻き添えなし(2 件と数えられたのは AGENTS.md が各スキルを 2 回参照するため —
  プローブ初版の期待値 `['calibrate']` の方が粗く、ゲートは健全。プローブ帰属)。

### 受入

- **V1 PASS**: 実 scaffold に `.claude/skills/calibrate/SKILL.md` が実在し AGENTS.md から
  参照される(参照 20 件・ユニーク 10 スキル)。BomDD 側の写しもスキル一覧へ実出現。
- **V2 PASS**: 配布 SKILL の未置換プレースホルダー 0 件。ECO 言及 15 行はすべて
  リポ名修飾つきの来歴(初出・出典列)で、修飾なしの製品固有 ID は 0 行。
- **V3 PASS**: `self-conformance` 全 16 検査 PASS・FAIL 0・exit 0。
  `[C7] PASS README のスキル本数表記 [10] = SKILLS 実数 10` で復帰。CAL-1 実行との比較で
  転化したのは C7 のみ= 既存 15 検査は判定不変。C16 は本 order を required と判定し
  receipt を検出(対象 6 件= 従来 4+2026-08-31 の ECO-038 還元節+本 order・免除は既存 2 件から増えず)。
- **V4 / V5**: push 後に §5・§6 で確定。

### V6 — /calibrate の初回自己適用(較正 receipt)

新設機構の初回使用者は新設者自身(ECO-034 の前例)。本 ECO の受入証拠へ検査 battery を適用した。

- 査定した主張と 3 値判定:
  1. 「calibrate は配布結線に組み込まれ、欠落すれば機械検出される」— **証明している**
     (CAL-1= C7 単独発火 / CAL-2= 除去で FAIL 転化・巻き添えなし)。
  2. 「本変更は既存検査を壊していない」— **証明している**(CAL-1→V3 で転化は C7 のみ)。
  3. 「本スキルは計器欠陥の受入前検出率を上げる」— **証明していない**(効果は本受入では
     測れない — スコープ外宣言どおり適用実績で測る。Q1: 本 order はこの主張を証拠なしに
     書かない)。
  4. 「写しと正本は同期している」— **部分的**(本 ECO 時点の内容同等はヘッダーと
     プレースホルダー解決を除き目視確認。恒久の同期検査はない — converge 写しと同じ限界)。
- 検出した計器欠陥と帰属: プローブ側 1 件 — CAL-2 プローブ初版の期待値が missing の重複
  保持(C4 の実挙動)を織り込んでいなかった(プローブ帰属・ゲート健全・§4 に正直記載)。
  ゲート側の欠陥は 0 件。
- 検出力の限界(実施した検査が測っていない次元):
  1. C13 のリポ文脈は `.claude/`・`bomdd/*.md` を走査しない(`self-conformance.py:522-523`)
     — 写し冒頭の正本リンクは機械検査外(実在は手動確認済み)。
  2. 写し⇔正本の同期逸脱は恒久検査されない(散文の同期規則のみ)。
  3. `/calibrate` 自身の非起動は機械観測されない(C16 は converge receipt のみを見る —
     スコープ外宣言どおり実測後に判断)。

## 5. CI 実測(V4)

- 対象 revision: `7707a59fea787315b329567465165c361cd5620b`(**ローカル HEAD と一致を確認**)
- 規則版: workflow `self-conformance`(リポ内定義= 測定器)
- run 識別子: 33358795224 — https://github.com/akiramei/BomDD/actions/runs/33358795224
- 結論: **PASS**(`status: completed` / `conclusion: success`)
- 観測日時 / 観測主体: 2026-08-31 / 本 ECO の担当設備(§担当設備)
- UNKNOWN の理由コード: 該当なし(headSha 照合を経て当該 run を特定 — §13 の 4 値判定)

## 6. クローズ

- diff 監査の窓: baseline `47cea59` → head `7707a59`(**窓閉鎖**)。窓内は
  `method/templates/product-profile/skills/calibrate.md`(新設)/ `method/tools/bomdd-init.py` /
  `README.md` / `.claude/skills/calibrate/SKILL.md`(新設・D-1 分)+ 台帳系
  (register・本 order)のみ — 影響なし予測が的中(`git diff --name-only 47cea59..7707a59` で機械確認)。
- 受入: V1 / V2 / V3 / V4 / V5 すべて PASS。較正 CAL-1 / CAL-2 いずれも成立。
  V6(初回自己適用)の較正 receipt は §4 に埋め込み済み。
- **恒久回帰**: C7(README のスキル本数 = SKILLS 実数)と C4(AGENTS.md 参照スキルの実在)が
  本変更クラスの再発を遮断し、両者が実際に作動することの陽性対照を製造中に実測済み
  (CAL-1 / CAL-2・§4)。
- このクローズが支持しないもの(V6 で宣言した限界の再掲): 本スキルの**効果**
  (計器欠陥の受入前検出率の向上)は未証明 — 適用実績で測る。`/calibrate` 自身の非起動は
  機械観測されない(C16 同型ゲートは §8.5 に従い実測後)。写し⇔正本の同期逸脱は恒久検査されない。
- 残(いずれもスコープ外・宣言済み境界): 非起動の機械観測 / 既設製品リポ・TimetableAdv への
  遡及設置(各リポの裁定)/ 効果測定の EXP 記帳(適用実績後に `/lesson-promote` 経路)。

## 追記(2026-08-31): 収束債務の返済 — 延長裁定による round 4〜6

user 裁定 2026-08-31「延長として実行して」により、本 order の `/converge` ループを延長した
(ECO-036 改訂後の手順 5「延長は人間裁定のみ」の**初適用**・上限 +3 周)。
結果= **round 4 = 2 件 / round 5 = 0 件 / round 6 = 0 件 — 2 周連続ゼロで収束成立**
(通算軌跡: 3→2→1→2→0→0)。round 4 の指摘 2 件:

1. 手順 4 の 3 値判定「証明していない」に**帰結が未規定** — 判定を receipt に書けば、証明して
   いない証拠を根拠にした昇格がそのまま通る(ECO-036 で是正した「帰結のない宣言」=
   converge 表 A ⑧ の calibrate 版)。
2. 検査 battery に「**入力の意味クラス別に測ったか**」の行がない — §4.4 同等性受入
   (系統誤差は特定の入力クラスの体験だけを静かに劣化させる・playbook:143-149)が
   index されていない。

いずれも配布スキルの変更につき **ECO-037 として起票し gate ① で裁定に上げた**。
本 order の既存記録(receipt 含む)は書き換えない(append-only・遡及なし)。
副次実測= 引用 §6.4 の `harness_bug` 帰属は実文と一致(playbook:369 — round 4 で裏取り済み・
指摘ではない)。
