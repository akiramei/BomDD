# Change Order — ECO-062(運転層の分離 — job(射影)/ receipt(witness)/ ruling の 3 形式を、既存正本の射影として規格化する〔設計入力・起票のみ〕)

> 裁定: user 2026-09-10「この議論を bomdd/ に起票して記帳して」— 外部議論(Grok Bot を BomDD 製造セルの
> **外側**に運転員として横置きする案・2026-09-10)への当方応答の帰結。**起票のみ**(製造着手・製造範囲の凍結は
> 別裁定)。本 ECO は **Grok Bot の採否を扱わない** — 扱うのは「運転員(人・Bot・CI を問わない)が BomDD を理解せずに
> 工程を運べる最小の受け渡し規格」であり、運転員が誰でも成立する部分だけを対象にする。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**

## 0. 実測(起票根拠)

### 0.1 外部議論の骨子(出典: user 提示の議論本文 2026-09-10)

- Claude Code ハーネスを BomDD 製造セルとして残し、外側に Grok Bot を運転員(職長)として置く。両者を自然言語で
  結ばず、`job / receipt / ruling` の 3 形式(`bomdd/jobs/ bomdd/receipts/ bomdd/rulings/`)で受け渡す。
- 運転員は PASS を決めない・Grok Bot を独立検査器と見なさない(同一ユーザーの Bot は cloud computer を共有し
  セキュリティ境界でない)・Bot memory を正本にしない。段階: Phase 1= 自動実行なし(job 生成と receipt 回収のみ)、
  Phase 2= `/bomdd-run JOB-xxx` の狭い入口、Phase 3= 複数 executor・裁定キュー。
- 議論が引用する Grok Bot の仕様(handoff・shared cloud computer・per-command 承認・「Memory is not a substitute
  for an authoritative source」)は **当方未確認**(x.ai 文書の引用は議論相手のもの。本 ECO はこれらに依存する
  主張をしない — §1 の対象は運転員の実装に依存しない部分に限る)。

### 0.2 リポ内で実測した既存物(3 形式は新設ではなく散在している)

| 提案の形式 | 既存物(実読) |
|---|---|
| job | ECO order §4/§5/§6・[work order](../method/templates/40-work-order.md)(入力の閉包・納品物・stop/report)・[routing](../method/templates/34-routing.yaml)(工程列・gate)・[register](60-change-register.yaml) の status 機械 |
| receipt | converge / calibrate / preflight receipt(ECO 本文に埋め込み・C16/C17 が検出)・自己受入ログ・cheat-report・[pre-push](hooks/pre-push) の PASS witness(tree hash + PASS の 2 行) |
| ruling | ECO の gate ①/② 裁定・register `decided`・commit trailer(BomDD-ECO-Fix / Accept)・37-ui-rulings |

- **factory-delegate**(Claude 用スキル・所在= `~/.claude/skills/factory-delegate/SKILL.md`・**本リポ外**・
  改訂 2026-07-23 ECO-137 由来)は Codex 向けの job プロトコルそのもので、本提案が Grok で再発見することになる
  3 規律を既に持つ: **正本委譲**(要約でなくファイル)・**製造完了バリア**(status 表示を信じずツリーで判定)・
  **受入は自分で再実測**。リポ内での言及は improvements.md 1 箇所(2026-09-02 成熟度節)のみで、
  method/templates/product-profile/skills/ に正本がない(本 ECO で流用を言うなら**リポ内正本化が前提**)。

### 0.3 「receipt を見て次へ」が最も危ない — 運転員は status を読む機械そのもの

本リポの失敗史はほぼ全部「観測前に次へ進んだ」型: ECO-024(検査 exit を chain で潰し赤のまま push)/
ECO-045(同一クラス再演・`cat && commit && push`)/ ECO-020(CI 赤が 11 コミット・約 2 日潜伏)/
製品側 ECO-137(codex status が別ジョブを completed 表示・書き込み途中を検査し偽陽性 3 件)。運転員は定義上
「状態フィールドを読んで進める装置」であり、この型を量産する位置にいる。処方は慎重さでなく機構
(「慎重さは荷重を負わない」・pre-push witness と同じ型)。

### 0.4 job 形式が潰す実測済み弱点

散文契約の自発起動不発 3 例(improvements.md 2026-09-02 節「実施要求≠実施証明」・OBS-20260828-02 →
playbook §9 へ昇格済み)。job が `required_skills` を明示するなら、製造セルは自発起動に頼らず明示起動でよく、
不発という失敗類がそもそも消える。**Grok の価値より先に job 形式単体の価値がここにある**(測定= EXP-20260910-01)。

### 0.5 停止の語彙は 1 種類ではない(既存判定値)

提案は `on: ruling_required: STOP` の 1 種だが、BomDD の停止は種類ごとに配送先が違う:
①規範判断が要る(gate ①・converge の裁定点)→ 人 / ②検査赤(自己受入 FAIL の stop/report)→ 工場へ差し戻し
(帰属は harness_bug を先に消す)/ ③BOM 自己矛盾(blocked)→ 当該単位のみ停止・設計者が BOM 改訂 /
④未収束の上限到達(converge・自動延長不可)→ 裁定点であり再実行ではない / ⑤開始条件不成立(preflight HOLD/STOP)
→ 工程判定であり製品判断ではない。

## 1. 変更要求(製造対象の候補 — 製造裁定時に凍結)

**設計原則(本 ECO の中心命題)**: 3 形式は**既存正本の射影**として規格化し、正本を二重化しない。
運転員は BomDD を理解しなくてよいが、**receipt を再検証してから進める**。

1. **JOB = 生成される射影(手書きしない)**: register + ECO order §6 残ゲートから worklist.py と同型の
   read-only ツールが job を生成する。job は ECO ID・required_skills・required_capability・write_scope・
   停止語彙(§0.5 の 5 種)を持つ。**運転状態(RUNNING 等)は job に書き戻さない** — 運転員所有の run 台帳
   (正本でない)に置く。
2. **RECEIPT = witness 形式**: 産出時の tree hash・ゲート結果(検査名+exit)・停止種別のみを持つ機械可読
   ファイル。散文 receipt(converge/calibrate/preflight)は従来どおり ECO 本文。**pre-push の witness
   (`.git/bomdd-selfconf-witness`・2 行固定)とは別ファイル**にする(hook の `sed -n 1p/2p` 読取を壊さない)。
3. **運転員の遷移条件**: 「receipt ファイルが存在する」ではなく「receipt の tree hash が現在のツリーと一致し、
   ゲート結果が機械検証できる」。**known-bad 対照腕**(ハッシュ不一致・FAIL 混入の receipt)を常設し、
   運転員が進めてしまうかを測る(EXP-20260910-02)。
4. **RULING = 唯一の人間手書き新規物**: 運転員は ECO 本文へ書かない。検証付きツールが ruling を
   register(`decided`)へ取り込む。裁定材料の人間への提示は**要約させず原文パス提示**(ECO-137 の下書き要約
   誤りと同じ機序が Bot 側で再演するため — EXP-20260910-03)。
5. **配員は設備認定台帳を参照**: `required_capability` の値は設備認定(equip-01〜03 の型)を通った executor の
   ID を参照する。独立性の評価軸(同一モデル/ハーネス/fixture/oracle/前提)は台帳属性として持ち、
   運転員が「独立検査として成立しない組合せ」を機械的に弾けるようにする。
6. **前提**: factory-delegate の正本を method/templates/product-profile/skills/ へ置く(リポ外正本の解消)。
   本 ECO の製造範囲に含めるか別 ECO かは製造裁定時に決める。

**採らない**: `bomdd/jobs/` を人や Bot が直接書く台帳にすること(register と job の二重正本 — 転写値禁止と
同じ理由・提案自身の「Memory は正本の代替でない」と同型)/ BomDD を理解しない Bot に正本 Markdown を触らせる
こと / Grok Bot(または同一ユーザーの複数 Bot)を独立検査器と扱うこと / Bot memory に裁定内容を持たせること /
Phase 1(自動実行なし)の測定より前に Phase 2 の自動起動を実装すること / Grok Bot 採否そのものの裁定(本 ECO の
対象外 — 3 形式は運転員が誰でも成立する部分)/ 新しい機械ゲートの先行新設(運転員が生まれてから)。

## 2. 影響なし予測(起票段階・反証可能)

起票の diff は台帳系のみ(本 order・register・improvements.md)。method/ 本文・tools・templates・skills・
hooks・CI は非接触。self-conformance の判定は不変(C16 は本 order の converge receipt で通過・C17 は verified
非対象・C13 は本 order の相対リンク 4 本が既存追跡ファイルへ解決)。製造時の影響なし予測は製造裁定時に凍結する
(候補: pre-push hook の 2 行 witness 形式は不変・既存 receipt 検出 C16/C17 の判定不変・製品リポは kit 再設置まで非波及)。

## 3. 受入(製造時の候補 — Phase 1 で測る 3 量)

- **V1(fail-open)**: known-bad receipt(hash 不一致 / FAIL 混入)を持つ job を運転員が進めた件数= **0**
  (対照腕の known-good は進める — 両腕で感度と特異度を出す。calibrate の盲検感度試験と同構造)。
- **V2(伝言ゲーム率)**: 裁定材料の提示が原文(order の options / evidence)と乖離した件数。
- **V3(観測負荷)**: 人間が裁定に際して order 以外の artifact(製造セルのログ等)を参照した回数。
- **V4**: self-conformance 全 PASS・CI 緑・diff 窓= allowed_paths+台帳系。
- 独立検査: 製造範囲が tool/hook を含むなら**異系統独立検査必須**(運転員の遷移判定は機械挙動)。

## 4. 製造裁定(Phase 1・user 2026-09-10・3 点)

**裁定(原文の要旨)**:

1. **第 1 弾の範囲= §1-1 job 射影と §1-2 witness の 2 項のみ。** §1-3(known-bad 常設)・§1-4(ruling 取り込み)・
   §1-5(設備認定参照)は第 1 弾に含めない(§7 Phase 5 以降・運転員の実測後)。
2. **factory-delegate 正本化(§1-6)= 別 ECO。** 本 ECO の前提から外す(第 1 弾の 2 項は factory-delegate に依存しない)。
   起票は未実施 — 起票トリガー= Phase 3 着手時、または別 ECO の必要が先に生じたとき。
3. **独立検査= 異系統必須・Codex**(factory-delegate 経由の先例= 製品側 ECO-137)。製造者(Claude Code)の自己受入で閉じない。

**帰結(製造前に凍結)**:

- 製造対象= 新規 2 ファイル:
  - `method/tools/bomdd-job.py` — register+order から job ビューを生成する **read-only 射影**(worklist.py 同型・exit 常に 0・
    導出値のみで転写値を持たない)。出力項目は §1-1(ECO ID・required_skills・required_capability・write_scope・停止語彙)。
  - `method/tools/bomdd-witness.py` — witness の**生成**(tree hash・検査名+exit・停止種別)と**検証**(現ツリーとの hash 一致+
    ゲート結果の再解釈。不一致・欠測・FAIL 混入は非 0 — 測定不能は合格ではない)。pre-push の 2 行 witness とは別ファイルに書く(§1-2)。
  - ファイル名は製造時に変えてよい(変更は register の allowed_paths を同一 commit で更新)。
- allowed_paths= 上記 2 ファイル+台帳系(本 order・register・improvements.md)。既存ファイル(pre-push hook・self-conformance.py・
  README・AGENTS.md・skills)は**非接触**。AGENTS.md「正本の所在」表への行追加は第 1 弾に含めない(読者= 運転員が生まれてから
  宣言する・§13 記録の経済)。
- 影響なし予測(反証可能): 既存の全検査 C1〜C18 の判定不変(新規 .py は検査対象集合に入らない — C5a/C5b は名指しの 2 スクリプトのみ・
  C4 scaffold は kit に含めない)・pre-push witness の 2 行形式と読取不変・製品リポ非波及。diff 窓= baseline `e26802e`(起票直前)のまま —
  窓内は台帳系(起票・逸脱記帳・§7・本 §4)+新規 2 ファイルのみになる予測。
- 受入(§3 を第 1 弾へ具体化):
  - **V1'**(witness 検証器の陽性対照): hash 不一致・FAIL 混入・欠測の 3 腕で非 0、known-good で 0 — **製造者が実測し、Codex が再実測**。
  - **V2'**(射影の導出性): job ビューが既存 ECO(ECO-055・ECO-062)に対して生成でき、内容が register/order と一致・転写値なし。
  - **V4**: self-conformance 全 PASS・CI 緑・窓内= allowed_paths のみ。
  - V1〜V3(運転員の測定)は Phase 5 の対象であり第 1 弾の受入ではない。
- Phase 2(手動リハーサル)は本裁定と独立に着手可。その欄一覧(書けなかった欄)を Phase 3 の入力にする。**Phase 3 の着手は user 指示**。

## /preflight receipt(起動経路: 自発 — 既裁定の適用実装〔起票〕)

- 分類= 既裁定の適用実装(user 裁定 2026-09-10「起票して記帳して」)。baseline `e26802e`= **confirmed**
  (HEAD・作業木 clean)/ 次番 062= **confirmed**(register 末尾= 061)/ 既存物の実在= **confirmed**
  (work order・routing・register・pre-push・factory-delegate SKILL.md・improvements.md 2026-09-02 節を実読)/
  凍結の非該当= **confirmed**(凍結は converge・calibrate — 本 ECO は両スキルに触れない)/ 同一ファイルへの
  進行中 ECO なし= **confirmed**(in-progress は ECO-055 のみ・refs= 52-metrics.yaml+playbook・本 ECO は台帳系のみ)/
  Grok Bot 仕様= **unknown**(未確認・§1 は依存しない)。
- 開始判定: **PROCEED**(起票まで)・override 0。製造は別裁定。

## /converge receipt(起動経路: 自発 — 3 形式の設計・応答提示時は receipt 未提示〔本起票で実施〕)

- **判定: 収束**(round 軌跡: 4→2→0→0)。
- DoD: ✔ 3 形式が既存正本の射影として定義され二重正本を作らない / ✔ 遷移条件が status でなくツリー真実に束縛
  される / ✔ 停止語彙が既存判定値へ写像される / ✔ リポ内主張は実読で裏取りし、外部主張(Grok 仕様)は unknown と
  明示する / ✔ 製造は別裁定・起票のみ / ✔ Grok 採否と切り離し、運転員が誰でも成立する部分に限る。
- round 1(新規 4 件): ①factory-delegate の正本が**リポ外**(`~/.claude/skills`)— 流用を言うなら正本化が前提
  (§1-6 へ)②register の status 語彙は台帳ヘッダ(proposed…)と実運用(filed / in-progress / verified)が
  異なる — 起票時は ECO-055 の先例 `filed` に合わせる ③自発起動不発の出典を「2026-09-02 成熟度節の一文」から
  正本(2026-09-02「実施要求≠実施証明」節・OBS-20260828-02)へ差し替え ④Grok 仕様 4 点を unknown 宣言(§0.1)。
- round 2(新規 2 件): ①現行 witness は 2 行固定で pre-push が `sed -n 1p/2p` で読む — receipt witness を同一
  ファイルへ拡張すると hook が壊れる → 別ファイル(§1-2)②V3「人間がログを見ずに裁定できた比率」は分母が
  不定 → 「order 以外の artifact を参照した回数」へ言い換え(§3)。
- round 3: 0 件。round 4: 0 件。
- 検証した主張: 既存物の所在(§0.2 の各ファイルを cat / ls)/ witness の形式(pre-push 実読)/ 失敗史の型
  (register ECO-024・045・020 の記載・factory-delegate SKILL.md の ECO-137 教訓)/ 自発起動不発 3 例
  (improvements.md:5728 節)/ 設備認定の実在(improvements.md equip-01〜03 の適用実測行)。
- 敵対自問: 「自分の設計の帰結を構造的制約と読み替えていないか」— 「job は射影」は転写値禁止の帰結だが、運転員が
  状態を書き戻す必要は残る → 運転状態を job でなく run 台帳(非正本)へ分離(§1-1)。「選択肢を落としていないか」—
  提案元の `bomdd/jobs/` 手書き案は採らない理由を明記(§1 採らない)。「Grok 不要へ誘導していないか」— Grok 採否は
  対象外と宣言し、3 形式の価値を Grok と独立に測る(§0.4・EXP-01)。「独立検査を自分で免除していないか」— 製造範囲が
  機械挙動を含むなら独立検査必須(§3)。
- 未収束事項: なし(製造範囲の凍結・factory-delegate 正本化の ECO 分割は本 ECO の未決でなく**製造裁定の入力**)。

## 7. 計画(user 2026-09-10「§7 として記帳して」— 現在地が追えるように Phase 化)

**現在地(更新は行内書き換え・履歴は register の status と commit に残る)**:
`Phase 1 完了(2026-09-10・裁定 3 点= §4・起票 9ac802e/52fef56)→ Phase 2 手動リハーサル(着手可)/ Phase 3 製造 第 1 弾(入口= Phase 2 の欄一覧・着手は user 指示)。`

```text
Phase 0 議論・起票 ─── 完了 2026-09-10
        │
        ▼
Phase 1 製造裁定 ─── 完了 2026-09-10(§4)
        │           ┌ Phase 2 手動リハーサル(裁定と並行可)
        ▼           ▼
Phase 3 製造 第 1 弾(job 射影+witness)◀━━ ★ 現在地= 2/3 の入口(2 は着手可・3 は user 指示待ち)
        ▼
Phase 4 Claude Code 単独運用で実測(運転員= 人間・外部運転員なし)
        ▼
Phase 5 外部運転員 導入試験(自動実行なし)
        ▼
Phase 6 狭い自動起動入口
        ▼
Phase 7 複数 executor・裁定キュー
```

| Phase | 入口条件 | 成果物 | 出口(次へ進む条件) | 裁定者 |
|---|---|---|---|---|
| 0 議論・起票 | 外部議論 | 本 order・register・improvements.md 2026-09-10 節・EXP-20260910-01〜03 / OBS-20260910-01 | 起票 commit の CI 緑 | 済 |
| 1 製造裁定 | Phase 0 完了 | register `filed→decided`・allowed_paths 再凍結・影響なし予測(製造前) | 下記の裁定 3 点が本 order に記入される | 済 2026-09-10(§4) |
| 2 手動リハーサル | Phase 0 完了(1 と並行可) | 手書き job ビュー 1 枚(題材= in-progress の ECO-055)・手書き witness 1 枚・known-bad 予行(人間運転員・tree hash 故意不一致)の記録 | 書けなかった欄が §1 の仕様欠落として列挙される | 当方が実施・user が確認 |
| 3 製造 第 1 弾 | Phase 1 decided+Phase 2 の欄一覧 | job 射影ツール(read-only・worklist.py 同型)・witness 生成/検証器・(別 ECO なら)factory-delegate 正本化 | §3 V4(self-conformance・CI・diff 窓)+異系統独立検査 PASS → `verified` | 独立検査官+user |
| 4 単独運用実測 | Phase 3 verified | job 経由で起動した ECO 2〜3 本の receipt 記録 | EXP-20260910-01 の初回値(非起動 0 か・対照の有無)が記帳される | 当方が記帳・user が読む |
| 5 外部運転員試験 | Phase 4 の記帳+§0.1 の運転員仕様 4 点(unknown)の裏取り | run 台帳(非正本)・裁定材料の提示記録・known-bad 対照腕の結果 | EXP-20260910-02 fail-open 0・EXP-20260910-03 伝言ゲーム率の基準線 | user |
| 6 狭い自動起動 | Phase 5 で fail-open 0 | 単一入口(`bomdd-run <job>` 相当・コマンド単位の承認は維持) | 自動起動 job で witness 再検証が機械的に効いた実測 | user |
| 7 複数 executor | Phase 6+設備認定台帳の属性化 | stop_type→配送先の機械定義(§0.5 の 5 種)・独立性判定の機械化(§1-5) | 独立検査として成立しない組合せを機械が弾いた実測 1 例 | user |

**Phase 1 で決める 3 点(開かないと Phase 3 に進めない)**:

1. **第 1 弾の範囲**: §1 候補 6 項のうち何を含めるか。当方案= ①job 射影と ②witness の 2 項のみ。③遷移条件の known-bad 常設は
   Phase 2 の予行結果で判断・④ruling 取り込み・⑤設備認定参照は Phase 5 以降の実測後。
2. **factory-delegate 正本化(§1-6)**: 本 ECO に含めるか別 ECO か。当方案= 別 ECO(独立検査の対象が「新規ツール」と「既存スキルの
   移設」で異なり、diff 窓が混ざる)。
3. **独立検査の配員**: 第 1 弾は機械挙動を含むため異系統必須(§3)。候補= Codex(factory-delegate 経由の先例= 製品側 ECO-137)。

**計画外に置くもの**: 外部運転員の採否そのもの(Phase 5 の入口は仕様の裏取りであって採用ではない)/ 新しい機械ゲートの
先行新設(運転員が生まれてから)/ Phase 5 完了前の自動起動(Phase 6 は Phase 5 の fail-open 0 を条件とする)。

**この計画が主張しないこと**: 各 Phase の所要・順序の最適性・Phase 5 で外部運転員が有用であること(いずれも未測定)。
Phase の追加・分割は本節の行内書き換えで行い、変更理由は commit message に残す。
