# Change Order — ECO-033(converge 非起動を commit gate で観測可能にする〔Phase 1〕)

> 由来: 2026-08-30 の maintainer 提言「converge 自発起動を『認識』から工程 Gate へ移す」と、
> 同日の裁定(推奨②採択・本 ECO は **Phase 1 のみ**・Phase 2 は別 ECO)。
> gate ① 承認待ち。

## 担当設備(equipment)

- 製造(設計者):
  - requested: `claude-opus-5`
  - resolved: `claude-opus-5`
  - ハーネス: Claude Code(Claude Agent SDK)
  - 来歴: **self-reported**
- 検査官: なし(独立検査なし)

## 0. 目的(裁定で確定・本 ECO の正本)

**converge 未実施の対象 artifact が正典化されることを阻止し、非起動を観測可能にする。**

**「人間への未収束提示を防ぐこと」は本 ECO の目的ではない**(それは Phase 2 = presentation
Gate の目的であり、別 ECO)。本 ECO が閉じても、人間は未収束の提示を一度受け取りうる。
本 ECO が保証するのは、**その提示が記録として正典化される前に止まること**だけである。

## 1. 起票根拠(実測)

### 1.1 非起動の再発

2026-08-30、`OBS-20260805-05` の昇格審査で converge が非起動だった。検出したのは受入でも
receipt でもなく**人間の質問**である。前回(2026-08-28)に続き 2 例目。

機序は 3 点で、いずれも注意不足では説明できない:

1. **mixed-task classification failure** — タスク前半(事実照会)の性質で全体を分類し、後半が
   裁定候補生成へ変化しても再分類する工程が無かった。converge の適用範囲は「単純な事実照会」を
   明示的に除外しており、この除外条項が誤分類を補強した。
2. **recognition-anchor failure** — 自発起動のアンカーが「設計合成だと**認識したら**」であり、
   工程上必ず発生するイベントではない。**converge 自身の DoD 第 1 項**(各規則に「必ず起きる
   イベント」のアンカーがある — 人の記憶・善意に依存しない)を、converge の自発起動契約が
   満たしていない。
3. **absence-observer failure** — receipt は起動時にしか生成されないため、`receipt なし` は
   「対象外だった」と「対象だったが起動しなかった」を区別しない。receipt の**不在を見る工程が
   存在しない** — 検出器のいない検出機構である。

### 1.2 既存 Gate のアンカー階層(実測)

| 測定対象 | 実測 |
|---|---|
| BomDD の Gate | `method/templates/process-core/hooks/pre-commit`・`commit-msg`(**git イベント**) |
| ViewTube の Gate | `bomdd/hooks/pre-commit`(staged パス判定・**git イベント**) |
| `.claude/settings.json` | **不在**(`.claude/` は `skills` と `worktrees` のみ) |

**既存の品質統制は例外なくリポ内で観測可能な git イベントへ張られている。** ハーネス層の
フック設定は BomDD に存在しない。

### 1.3 現行 receipt 契約は既に artifact へ落ちる

`method/templates/product-profile/skills/converge.md` の receipt 節:

> 提示物の中の一節として**埋め込む**(裁定候補なら decision 文書内、ECO なら本文内)。
> 新しい artifact 置場は作らない。

**receipt は設計上すでにリポ内 artifact に落ちる。** したがって提言 §4 の三段構造
(observable trigger → receipt required → receipt presence check)は、**ハーネス層なしで
既存の commit gate 上に構成できる**。これが Phase 1 を先行させる根拠である。

### 1.4 検出機会は実在した

2026-08-30 の昇格審査の結論は最終的に `method/improvements.md` へ落ち、コミットされた。
**commit 時点で receipt 不在を検査する機会は実在した** — 使われなかっただけである。

### 1.5 マーカーの実在率(predicate 設計の入力)

| 対象 | 実測 |
|---|---|
| `bomdd/60-change-order-eco-*.md` | 32 件 |
| うち `gate ①` を含む | **18 件** |
| うち「裁定対象/裁定候補/候補 X-N/案 X」型の文言を含む | **2 件** |
| うち converge / 収束 receipt を含む | 2 件 |
| `method/improvements.md` の「案 X / 織り込み案 X」出現 | 30 箇所 |

**文言バリエーションは広く、文言単独の検出は弱い**(提言 §7 の hard-positive 論を実測が支持)。
一方 `gate ①` は 18/32 で定着した構造マーカーである。

## 2. スコープ

### 本 ECO で行うこと(Phase 1)

1. **applicability predicate の確定**(gate ① 裁定事項 — 下記 §3)。
2. 確定した predicate に基づく **commit gate 検査**の実装。BomDD 側の実装先は
   `method/tools/self-conformance.py`(BomDD は process-core を設置しない — ECO-025)。
3. **fixture 5 種**(§4)による較正 — 予防ゲートのため陽性対照を必須とする
   (`OBS-20260828-05` / `EXP-20260828-06` の適用)。

> 接続: ECO-032 のスコープ外宣言「self-conformance への converge 固有検査の追加(§8.5 に
> 従い**実測後**)」— 本 ECO はその実測後の実施にあたる。

### 本 ECO で行わないこと

- **Phase 2(presentation Gate)** — 別 ECO。**ECO-020 との差分裁定を必須**とする(裁定 5)。
  比較対象には次の 2 案を**必ず**含める:
  - (i) presentation Gate を **repository 側の権威的 Gate** にする案
  - (ii) **repository commit gate を authoritative のまま維持**し、harness 側を
    **非権威的な early-preflight** とする案
- **receipt schema の `scope` / `downgraded` 追加** — 本 ECO から分離し別裁定(裁定 6)。
  現行契約は 3 項(周回数と各周の新規指摘件数 / 検証した主張と実測結果 / 未収束事項)であり、
  提言 §9 の 6 フィールドは**拡張**である。「既存契約の構造化」と読むと契約変更が紛れ込む。
- 製品リポ(`process-validator` 側)への設置 — 実装先が 2 系統に分かれるため、BomDD 側の
  実測後に別裁定。
- 既存 32 order・improvements.md 既存節への**遡及適用**(§3 の C で扱う)。

## 3. gate ① 裁定事項 — applicability predicate

> 裁定 3: 「どの artifact をどの機械的 predicate によって converge-required と判定するか」を
> **実装前に確定**すること。**receipt 不在検査だけでは applicability 判定側で再び fail-open し得る。**

### 論点 A — 対象 artifact 集合

- **A-1(推奨)**: `bomdd/60-change-order-eco-*.md` **と** `method/improvements.md` の新設節。
- A-2: ECO order のみ。
- A-3: ECO order + improvements.md + `method/` 本文 diff。

**A-2 を推奨しない理由(実測)**: 2026-08-30 の非起動事例の対象 artifact は ECO order ではなく
**improvements.md の「昇格審査記録」節**だった。A-2 では**再現 fixture(mixed-task 陽性・§4)が
書けない** — 裁定 4 が要求する fixture 集合が A-2 と両立しない。

### 論点 B — 判定 predicate

- **B-1(推奨)**: **構造マーカーによる自動 required ∪ 明示宣言、ただし宣言は緩める方向に使えない**。
  - 自動 required の条件: `gate ①` 相当の人間裁定要求、複数候補の列挙、推奨案の提示 の
    いずれかが存在する(具体の正規表現は製造時に fixture と対で決める)。
  - 書き手は `converge: required | not-required` を宣言できる。**`required` への引き上げは常に有効。
    `not-required` への引き下げは、hard-positive が 1 つでも実在する場合に却下し FAIL とする**
    (非対称設計 — 宣言で検査を弱められない)。
- B-2: 構造マーカーのみ(宣言なし)。→ **fail-open**: マーカーを書かない裁定候補を取り逃がす。
- B-3: 明示宣言のみ。→ **fail-open**: `not-required` と書けば通る。裁定 3 が名指しした欠陥そのもの。
- B-4: パス単独(対象パスなら常に required)。→ **過剰**: 事務的 ECO(状態遷移是正等)まで
  required になり、現行契約「機械受入がある是正実施には使わない」に反する。

> **裁定 4 が実質的に B-1 を要求している** — fixture「hard-positive と not-applicable 宣言の
> 矛盾検出」は宣言機構(B-3 要素)と構造マーカー(B-2 要素)の**両方**がなければ書けない。
> この従属関係を隠さず記す(選択肢は形式的に 4 つだが、B-1 以外は fixture 集合と両立しない)。

### 論点 C — 遡及境界

- **C-1(推奨)**: **staged 差分に限定**(新設・追加された対象節のみを検査)。既存 32 order と
  improvements.md 既存節は検査対象外。前例= 既存 hook が `STAGED` で判定する様式。
- C-2: 明示 cutoff マーカーを置く。前例= `<!-- worklist-legacy-audit-cutoff: YYYY-MM-DD -->`
  (`method/tools/worklist.py`)。C-1 と併用可。
- C-3: 全数遡及。→ **既存 32 order のうち receipt を持つのは 2 件**であり、全て FAIL する。不可。

## 4. 較正(fixture — 裁定 4 で確定)

予防ゲートであるため**陽性対照を必須**とする。是正面(赤プローブ)と予防面(陽性対照)を
2 系統持つ(`OBS-20260828-05`)。

| # | fixture | 期待 |
|---|---|---|
| F1 | required + receipt なし | **FAIL** |
| F2 | required + receipt あり | **PASS**(正常系 — これが無いと「常に FAIL する Gate」と弁別できない) |
| F3 | not-required + receipt なし | **PASS** |
| F4 | **mixed-task 陽性**(事実照会として始まり、途中で裁定候補〔複数案+推奨〕を生成した節) | **FAIL** |
| F5 | hard-positive 実在 かつ `converge: not-required` 宣言 | **FAIL**(宣言による引き下げの却下) |

- F4 は **2026-08-30 の非起動事例の再現**である。実在した不適合の再現であり、合成 fixture より
  強い対照になる(`OBS-20260725-02` の趣旨)。
- **known-bad control の特定は gate ① 後の製造初手とする** — 履歴中の「裁定候補を含むが
  receipt を持たない実在 artifact」を同定し、それに対して FAIL することを実測する。
  同定作業自体を製造記録に残す(該当 0 件なら 0 件と記録する)。

## 5. 影響 BOM(予測)

- `method/tools/self-conformance.py`: 検査 1 本追加(C16 想定)。既存 15 検査は判定不変の予測。
- `method/templates/product-profile/skills/converge.md`: **本 ECO では変更しない**
  (自発起動契約の書き換えは Phase 2 の裁定に依存するため。散文強化は主対策にならない —
  提言 §11)。
- `bomdd/60-change-register.yaml` / 本 order: 台帳系。
- 製品リポ・kit: **非波及**(配布物を変更しない)。

## 6. 残ゲート

**gate ① のみ**。人間は論点 A・B・C についてそれぞれ 1 つを指定する。

裁定だけでは実装しない。着手には裁定後の明示的な指示を要する。

## 7. `/converge` receipt

本 order の §3(predicate 設計)は機械オラクルの無い設計合成であるため、提示前に `/converge` を
適用した。

- **周回**: round 1 = 新規指摘 3 件 / round 2 = 2 件 / round 3 = 1 件。
  **2 周連続ゼロには未到達**(上限 3 周で打ち切り)— **収束は主張しない**。
- **round 1 の指摘**:
  1. B-4(パス単独)は現行の適用範囲契約「機械受入がある是正実施には使わない」に反する →
     選択肢に残すが非推奨理由を明記。
  2. B-2(構造マーカー単独)では **2026-08-30 の非起動事例そのものを捕捉できない** —
     当該 artifact は ECO order ですらなく improvements.md の節だった。
  3. 対象 artifact 集合に `method/improvements.md` を含めないと、裁定 4 が要求する
     **mixed-task fixture が書けない** → 論点 A の推奨を A-1 へ。
- **round 2 の指摘**:
  4. 裁定 4 の fixture 集合は実質 B-1 を強制する(F5 が宣言機構を要求)。選択肢が形式的に
     4 つあっても実効は 1 つ — **この従属関係を隠さず書く**(§3 論点 B に追記済み)。
  5. 実装先が 2 系統(BomDD= self-conformance / 製品リポ= process-validator)。BomDD は
     process-core を設置しない(ECO-025)ため同一実装を置けない → 製品リポ側を本 ECO の
     スコープ外へ明記。
- **round 3 の指摘**:
  6. 較正に known-bad control(実在する不適合)の特定を入れていなかった → §4 へ追加。
- **実測した主張**(`file:line` / 実行):
  - 既存 Gate は全て git イベント: `method/templates/process-core/hooks/pre-commit`
  - ハーネス層フック設定の不在: `.claude/` に `settings.json` なし(実行: `ls .claude/`)
  - receipt は artifact へ埋め込む契約: `method/templates/product-profile/skills/converge.md`
    「収束 receipt(提示物に添付)」節
  - マーカー実在率 32/18/2/2 と improvements.md 30 箇所: §1.5(grep 実測)
  - cutoff マーカーの前例: `method/improvements.md:834` / `method/tools/worklist.py:49`
  - 現行 receipt 契約は 3 項(提言 §9 の 6 フィールドは拡張): 同 skill の receipt 節
- **未収束事項**: **「提示物が artifact に落ちないケース」の被覆**。チャット出力のみで終わり
  記録へ落ちない裁定は Phase 1 の被覆外であり、Phase 2 を要する。本 ECO はこれを解かない
  (§0 の目的限定はこの限界の明示でもある)。
- **効果の予測は本手順では裏取れない**: 「Phase 1 だけで非起動率が下がる」は疑いのままであり、
  測定は受入または EXP へ回す。

## 8. 製造記録(gate ① 承認後)

**gate ① 承認 2026-08-30 maintainer**「gate ① 承認。A-1 + B-1 + C-1 で製造に進んで」。
その後 **C-1 の前提が CI で成立しないことを実測**して差し戻し、
**C-1c 採択・cutoff = 2026-08-30** の追加裁定を受けた。

### 8.1 C-1 → C-1c の差し戻し(実測による前提の否認)

| 測定 | 結果 |
|---|---|
| `.github/workflows/*.yml` の checkout | `actions/checkout@v4` — **`fetch-depth` 指定なし**(既定 = shallow・depth 1) |
| self-conformance の git 使用 | `git ls-files` と一時 scaffold 内のみ。**履歴・diff は未使用** |

CI にはステージング領域がなく履歴も 1 コミット分しかないため、**C-1(staged 差分限定)は CI で
計算できない**。BomDD の権威的ゲートは CI であり(CLAUDE.md「押し戻すのは CI である」)、
CI で常に測定不能になる検査は規律 6 に照らして **fail-open** — 本 ECO が除去対象としている
欠陥クラスそのものになる。

採択した **C-1c** は **staged を意味論から外す**: 判定の正本を「cutoff 以降の全数走査」に置き、
staged は同じ判定を早く返すローカル最適化に格下げする。ローカル版と CI 版で結論が食い違う経路が
構造的に消える。

### 8.2 実装

`method/tools/self-conformance.py` へ **C16** を追加(既存 15 検査は判定不変 — 実測で確認)。

- `converge_classify(text)` = required / reasons / declared / conflict / receipt
- `converge_verdict(text)` = (ok, 理由)。**conflict は receipt の有無によらず FAIL**
- hard-positive 5 種: 裁定要求 / `gate ①` / 裁定対象 / 残ゲート / 推奨
- 宣言 `<!-- converge: required | not-required -->`(HTML コメント — 描画に出ず機械可読。
  前例= `worklist-legacy-audit-cutoff`)
- **B-1 非対称設計**: `required` への引き上げは常に有効 / `not-required` への引き下げは
  hard-positive 実在時に却下し FAIL(宣言で検査を弱められない)
- 対象集合(A-1): 台帳の `date >= cutoff` なエントリの `order_ref` + `improvements.md` の
  `## YYYY-MM-DD` 節で日付が cutoff 以降のもの

### 8.3 R5 probe(製造中に計器の欠陥を 2 件検出)

**実個体へ当てた結果、計器側の欠陥が 2 件出た。いずれも配線前に是正した**(較正の規律
「不一致時は計器を先に疑う」)。

1. **部分文字列ゲート(精度欠陥)**。初版の選択肢列挙マーカー `[A-Z]-\d+` が **ID の部分文字列**を
   拾った — `ECO-034` → `O-034`、`RSC-CP-CLOSURE-001` → `E-001`、`OBS-20260830` → `S-20260830`。
   実リポの 1 節で **36 ラベル中 29 件が誤検出**。**ViewTube NF-10 の R9 と同型**(定数・部分文字列
   比較で意味を測ったつもりになる)であり、本日 playbook §4.4 へ織り込んだ「検査文はコードが
   測る以上を主張しない」の**自リポ実例**。是正= 選択肢列挙を hard-positive から**削除**した
   (候補ラベルは「提案」と「完了裁定の記録」の双方に現れ両者を弁別できないため。再現力の
   低下は宣言で補い、限界として宣言する)。
2. **被覆欠落(検出力欠陥)**。`残ゲート` だけでは、本リポで確立した裁定要求マーカー `gate ①`
   (18/32 order が使用)を持つ **14 件を取り逃がしていた** — 弁別力(fixture は全通過)は
   成立していたが**被覆が無い**状態。playbook §4.4「較正の形式的成立は被覆を証明しない」の
   自リポ実例。是正= `gate ①` / `裁定対象` を hard-positive へ追加し、取りこぼし 0 を実測。

### 8.4 較正(予防面=陽性対照 / 是正面=実在 known-bad)

**予防面(fixture 5 種・毎回実行)**: F1〜F5 すべて期待どおり(5/5)。C16 は fixture 較正が
不成立なら本走査を行わず「計器を先に疑う」FAIL を返す。

**是正面(known-bad control — 実在する不適合品)**: 履歴の全 33 order を分類した結果、
**required 20 件 / not-required 13 件**、うち **required かつ receipt なし = 19 件**を同定し、
**19 件すべてに FAIL が発火することを実測**した(合成でなく実物 — `OBS-20260725-02` の趣旨)。
発火例: ECO-013(recommended-option)/ ECO-015・016・017(adjudication-gate)。

**精度の確認**: not-required 13 件は ECO-001〜012・014 — いずれも `gate ①` 規約以前の、機械受入を
持つ是正 ECO(fail-open 修正・ゲート新設)であり、converge の適用範囲が明示的に除外する
クラスである。誤除外なし。

**取りこぼしの確認**: `gate ①` を含みながら required にならない order = **0 件**。

### 8.5 受入

- **V1(fixture 較正)= PASS**: F1〜F5 の 5/5 が期待と一致。
- **V2(known-bad 発火)= PASS**: 実在 known-bad 19/19 が FAIL。
- **V3(全検査)= PASS**: self-conformance 全 16 検査 PASS・FAIL 0。既存 15 検査は判定不変。
- **V4(CI)= push 後に本節へ追記**。
- **V5(diff 窓)= push 後に diff 監査して台帳へ記録**。
- 適用範囲内(cutoff 以降)の実測対象は 2 件(ECO-033 order・improvements.md 2026-08-30 節)で
  いずれも PASS。

### 8.6 宣言した検出力の限界(未了項目リストではない)

コード側 docstring に恒久記載した。**実施した検査が測っていない次元**は次の 3 つ:

1. receipt の**構造的存在**しか測らない。「本当に敵対自問したか」「実測で裏取りしたか」は
   測っていない — 目的は converge 工程が**完全に素通りする故障**の検出に限定する。
2. hard-positive は高精度・低再現。マーカーを一切使わない裁定候補は自動 required にならず、
   その被覆は書き手の `converge: required` 宣言に依存する(**残余の fail-open**)。
3. **artifact に落ちない提示**(チャットのみで終わる裁定)は原理的に被覆外 — Phase 2 の対象。

### 8.7 受入結果(確定)

| 項目 | 結果 |
|---|---|
| V1 予防面較正(fixture) | **PASS** — 5/5 が期待と一致 |
| V2 是正面較正(実在 known-bad) | **PASS** — 19 件同定・19/19 発火。被覆(`gate ①` 取りこぼし)0 件・誤除外 0 件 |
| V3 全検査 | **PASS** — self-conformance 全 16 検査 PASS。既存 15 検査は判定不変 |
| V4 CI | **PASS** — run 33294106881・conclusion success・headSha `6f33631` がローカル HEAD と一致 |
| V5 diff 窓 | **PASS** — `78af21b`→`6f33631` の窓内は `allowed_paths` のみ(予測的中) |

ECO-033(Phase 1)を `verified` へ閉じる。

**このクローズが支持しないもの**: 提示前の防止(Phase 2)/ artifact に落ちない裁定の被覆 /
receipt の内容的な真正性(構造的存在のみ)/ 製品リポへの設置 / receipt schema の拡張。
いずれも別 ECO・別裁定である。
