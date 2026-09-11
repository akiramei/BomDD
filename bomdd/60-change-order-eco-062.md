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

## 5. Phase 2 手動リハーサル(2026-09-10・user「Phase 2 を実施して」— ツールなし・題材 ECO-055)

### 5.1 手書き job ビュー(ECO-055)— 欄ごとに出所を記録

| 欄 | 値(手書き) | 出所 | 判定 |
|---|---|---|---|
| job | JOB-ECO-055 | register `id`(導出) | 導出可 |
| objective | 52-metrics 棚卸しの帰結 — 計器/ログの整理(1-A/2-A/3-A/4-A の束) | register `title` | 導出可 |
| state | `in-progress` | register `status` | **不整合** — order §6 は「クローズ(2026-09-03・verified)」・improvements.md 2026-09-03 節は「verified は起票時凍結基準の判定として維持」。register の status は起票以来遷移していない(`git log -G` で確認)。**状態の正本は register**(台帳ヘッダ)なので job は in-progress を出すが、order と食い違う → 下記 F0 |
| inputs | order_ref・affected_refs | register | 導出可 |
| write_scope | `diff_audit.allowed_paths` | register | 導出可 |
| forbidden | (なし) | order §1「採らない」は散文 | **欠落 F3**(構造欄なし) |
| required_skills | preflight・converge・calibrate | order の receipt **見出し**(事後記録) | **欠落 F1** — 事前の宣言欄がない。job が「起動すべきスキル」を出すには task class → スキル集合の対応表(preflight の task contract 最小表が候補)が要る |
| required_capability | (なし) | order「担当設備」は事後記録 | **欠落 F2** — 設備認定 ID を参照する欄がない(第 1 弾の対象外・Phase 7) |
| expected_outputs | order §1 の 4 項+台帳系 | order §1 散文から手写し | **欠落 F4** — 構造化されていない(手写し= 転写値) |
| gates_remaining | order §3 V1〜V5 → §6 で全 PASS | order 散文 | register が in-progress のため job は「残ゲートあり」と出す → F0 と同根 |
| stop_vocabulary | 5 種(§0.5) | 本 ECO のみ・ECO-055 には無い | **欠落 F5** — 語彙の正本が未定(第 1 弾では job 側の固定値として持つ) |
| independent_inspection | REJECT(2026-09-03・Codex)→ 是正 ECO-056 verified | register `verification` 散文 | **欠落 F6** — 構造欄なし(job は「独立検査の結果」を導出できない) |

**F0(状態の不整合・本 ECO の範囲外の発見)**: ECO-055 の register `status: in-progress` は order §6 のクローズと矛盾する。
job 射影はこれを**修復しない**(射影は read-only)— 射影が出すべきは「register と order の状態が矛盾」という**停止種別**であり、
§0.5 の 5 種に **⑥台帳不整合(preflight の contradicted 相当・配送先= 台帳の所有者)** を加える候補。ECO-055 の status 遷移そのものは
user 裁定(独立検査 REJECT 後の verified 維持の扱いを含む)。

### 5.2 手書き witness v0(現ツリー・known-good)

```json
{"witness": "WIT-ECO-062-P2-001", "eco": "ECO-062", "phase": "2",
 "tree": "53e2a3152e48129fa38e2c69bda764b14d71746e",
 "tree_definition": "worktree write-tree (add -A on temp index) — self-conformance C18 と同一",
 "head": "985f0e2acd5c086771dc6ae7f28d8c006b93ddeb",
 "gates": [{"name": "self-conformance", "exit": 0, "source": "selfconf-5.log 末尾 passed・task bz00i5lh6 exit=0"}],
 "stop_type": "NONE", "producer": "claude-fable-5-1 / Claude Code (self-reported)", "produced_at": "2026-09-10"}
```

- 検証時点で HEAD^{tree}・worktree write-tree・pre-push witness 1 行目の 3 者が一致(clean tree)。
- **仕様欠落 W1**: `tree` の定義を **C18 と同一(作業木の write-tree)** に固定する — HEAD^{tree} では作業木の未コミット変更を覆えない
  (5.3 の NG 腕で実証)。**W2**: `gates[].source` は座標(ログのパス+行 or task id)で、値の転写は持たない。**W3**: `stop_type` の語彙は
  §0.5+F0 の ⑥ を凍結して持つ。**W4**: pre-push の 2 行 witness とは別ファイル(§1-2・不変)。

### 5.3 known-bad 予行(運転員手順の予行・5 腕 × 2 手順)

運転員手順 v0: ①witness.tree が現 tree と一致 ②gates 非空かつ全 exit 0 ③stop_type NONE → ADVANCE、それ以外 STOP+理由。
現 tree の取り方を 2 通り比較 — **P0**= `HEAD^{tree}`(素朴)/ **P1**= 作業木 write-tree(C18 定義)。dirty 腕は未追跡ファイル 1 つを
`bomdd/` に置いて計測し直後に削除(後片付け後の write-tree が元に戻ることを assert)。

| 腕 | 作業木 | 手順 | 判定 | 期待 | 合否 |
|---|---|---|---|---|---|
| known-good | clean | P0 / P1 | ADVANCE / ADVANCE | ADVANCE | OK / OK |
| kb-hash(末尾 4 桁改変) | clean | P0 / P1 | STOP(tree 不一致)/ 同 | STOP | OK / OK |
| kb-fail(exit 1 混入) | clean | P0 / P1 | STOP(FAIL 混入)/ 同 | STOP | OK / OK |
| kb-missing(gates 空) | clean | P0 / P1 | STOP(欠測)/ 同 | STOP | OK / OK |
| known-good | **dirty** | **P0** | **ADVANCE** | STOP | **NG(fail-open)** |
| known-good | dirty | P1 | STOP(tree 不一致) | STOP | OK |

- **所見**: 素朴手順 P0 は「検査後に作業木が変わった」状態を見逃す(HEAD^{tree} は不変のため)。C18 が worktree write-tree を採った
  理由と同じ。第 1 弾の `bomdd-witness.py` の検証は **P1 のみ**を実装し、P0 を陽性対照(kb-dirty 腕)として持つ(§4 V1' の 3 腕に
  **dirty 腕を加えて 4 腕**)。
- 独立性の限界: 運転員役はスクリプト(手順は当方の手書き)であり、witness の書き手と同一。**人間運転員による予行は未実施**
  (EXP-20260910-02 は Phase 5 で運転員が生まれてから)。本予行が示すのは手順 v0 の欠陥(P0)であって、運転員の行動ではない。
- 予行の実行環境: 出力が cp932 コンソールで文字化け(判定列は読める)— §13「計器の報告経路は実行環境の既定符号化に依存させない」の
  再演(計器ではなく予行スクリプトのため是正せず・第 1 弾のツールは明示 UTF-8 で書く)。

### 5.4 Phase 3 への入力(仕様欠落の一覧・出口条件)

- job 射影(`bomdd-job.py`): F1(required_skills の事前宣言欄= task class 対応表)・F3(forbidden の構造化)・F4(expected_outputs の
  構造化)は**register/order に欄がないため第 1 弾では「出所なし」と明示して空欄で出す**(散文から手写ししない= 転写値禁止)。
  F0(状態不整合)は停止種別 ⑥ として出す。F2・F5・F6 は第 1 弾の対象外(F5 は job 側固定値)。
- witness(`bomdd-witness.py`): W1〜W4 を仕様に固定。陽性対照= 4 腕(hash・fail・missing・dirty)。
- user 裁定が要るもの(本 ECO の範囲外): ECO-055 の register status(in-progress のまま)の遷移。

## 6. 製造と受入の実測(2026-09-10・user「ECO-062 の製造まで進めて」— Phase 3 第 1 弾)

### /preflight receipt(起動経路: 自発 — 既裁定の適用実装〔製造着手〕)

- baseline `d36fd76`= **confirmed**(HEAD・作業木 clean)/ register `decided`= **confirmed** / 製造範囲= **confirmed**(§4: 新規 2 ファイルのみ)/
  Phase 2 の欄一覧= **confirmed**(§5.4 F0〜F6・W1〜W4)/ 凍結の非該当= **confirmed**(converge・calibrate 非接触)/ 同一ファイルへの進行中 ECO なし=
  **confirmed**(新規ファイル)。開始判定: **PROCEED**・override 0。

### 製造物(新規 2 ファイル・既存ファイル非接触)

- [`method/tools/bomdd-job.py`](../method/tools/bomdd-job.py): register+order → job ビュー(read-only・exit 常に 0・`--selftest` のみ失敗で 1)。
  原則= 全欄 `source` 座標 / 出所なし欄(F1・F2・F3・F4・F6)は null+`none` で出し散文から手写ししない / 状態の正本は register で、
  order のクローズ節(見出し形状+verified 語・fence 内無視)と矛盾したら **LEDGER_INCONSISTENT** を出す(修復しない・F0)/ 停止語彙は
  固定値 8(§0.5 の 5 種+⑥台帳不整合+MISSING_INPUT+NONE)で、台帳から導出できるのは NONE・LEDGER_INCONSISTENT・MISSING_INPUT の 3 つと**被覆宣言** /
  報告経路は明示 UTF-8。
- [`method/tools/bomdd-witness.py`](../method/tools/bomdd-witness.py): `produce`(tree・gates・stop_type・producer)と `verify`(0= ADVANCE /
  1= STOP+理由 / 2= 測定不能)。W1 tree の定義= C18 と同一(一時 index に add -A → write-tree)/ W2 gates[].source は座標のみ / W3 停止語彙は job と共通 /
  W4 既定の出力先= `.git/bomdd-witness/<ECO>.json`(pre-push の 2 行 witness とは別ファイル)/ **W5**(製造中に追加・下記)。

### 製造中の実測(正直記載)

- **witness selftest 初回 FAIL**(known-good 腕が STOP: tree 不一致)。原因= fixture が witness を束縛対象の**作業木内**に書き、verify 時の
  write-tree に witness 自身が入って tree が変わった(自己参照)。fixture の誤りであると同時に W4 の実証。処置= `produce` に**作業木内(.git 配下を除く)
  への出力を exit 2 で拒否するガード**(W5)を追加し、selftest に「作業木内出力→2」「.git 配下→0」の 2 腕を追加。計器が自分の欠陥を捕捉した例
  (陽性対照の設計が製造者の前提誤りを先に露出した)。
- 製造中の手順逸脱: なし(新規ファイルは Write ツール・CR 0 を実測。検査と commit は別呼び出し・検査が末尾)。

### 受入の実測

- **V1'**(witness 検証器の陽性対照): `bomdd-witness.py --selftest` **PASS** — known-good 0 / hash 改変・FAIL 混入・gates 欠測・stop_type≠NONE・
  作業木 dirty 1 / witness 不在 2 / 不正 stop_type 2 / 作業木内出力 2(一時 git リポ・実リポ非接触)。**dirty 腕**= §5.3 で fail-open した
  HEAD^{tree} 比較を陽性対照化したもの(4 腕目)。Codex による再実測は独立検査(§7 Phase 3 出口)で。
- **V2'**(射影の導出性): `bomdd-job.py ECO-055 ECO-062` — ECO-055= **LEDGER_INCONSISTENT**(order にクローズ節 verified・register in-progress)/
  ECO-062= **NONE**。導出欄 7(job・eco・objective・state・inputs・write_scope・diff_baseline)は register の座標を `source` に持ち、null 欄 5 は `none`+
  欠落番号。転写値なし(order 散文からの値は 0)。`--selftest` PASS(整合 NONE / 不整合 2 方向 / order 不在 / fence 内見出し無視 / null 欄 / 全欄 source)。
- **V4**(製造物を含む作業木で): self-conformance **全 PASS・exit 0**(ログ= scratchpad selfconf-7・task bk794wx0u)— 判定不変(C13 216 links 不在 0・
  C16 order 30 件・C4 scaffold 不変= 新規 .py は kit に含まれない)。**本 §6 と register の記入後に再実行し、その exit を観測してから witness 生成→commit**
  (検査後の変更を未検査のまま束縛しない — 本 ECO の witness 自身の規則)。CI は §8 で記録。
- 独立検査(§4 裁定 3): **停止点** — fix commit 後に Codex(異系統・read-only)へ引き渡し、所見の受理側真正判定を §8 に記録してから verified 昇格。

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

## 8. 独立検査の実施記録(2026-09-10・停止点 — 検査設備の不能により UNKNOWN)

- fix commit `1eefe35`(V4 の witness= `.git/bomdd-witness/ECO-062.json`・tree d21b9a6b・verify ADVANCE を commit 前後で観測)・
  CI run 34467755878 **success**(headSha 一致・3 job)。製造完了バリア= コミット済みツリー。
- 引き渡し: Codex(異系統・read-only・§4 裁定 3)へブリーフ(正本= order・register・製造物 2 ファイルのパス指定・観点 7・出力形式指定)を
  2 回送付。**2 回とも検査官が何も読めずに終了**(所見 0・report 未作成・判定なし・リポ変更なし):
  1. 1 回目: 既定モデル `gpt-6-astra` が Codex CLI 0.144.1 より新しい(API 400 "requires a newer version of Codex")。
  2. 2 回目(`--model gpt-5.6-sol` で再試行): Windows サンドボックス初期化エラー `windows sandbox: helper_unknown_error: apply deny-read ACLs`。
     companion を介さない `codex exec -s read-only` の最小コマンドでも同一エラーを実測 — CLI/環境(`~/.codex/config.toml` `[windows] sandbox = "elevated"`)
     の障害であり、製造物にも companion にも依存しない。
- 帰属: **harness_bug(検査設備側)**。製造物の欠陥を示す観測は 0(ただし独立検査が行われていないので「欠陥なし」も言えない)。
- 判定: 独立検査= **UNKNOWN**(AGENTS 規律 6: 実行不能を PASS として扱わない)。register は `implemented` のまま・verified へ昇格しない。
- 当方が採らなかった処置: Codex CLI の版上げ・`~/.codex/config.toml` のサンドボックス設定変更(ユーザー環境のセキュリティ設定)・
  `--dangerously-bypass-approvals-and-sandbox` での実行(検査官の隔離を外す)・製造者自身による「独立検査の代行」(§4 裁定 3 に反する)。
- **user 裁定待ち**: (a) Codex 環境を復旧して再引き渡し(CLI 更新またはサンドボックス設定)/ (b) 別の異系統検査官を指定 / (c) 第 1 弾を
  「製造者較正のみで受入」へ切替(§4 裁定 3 の変更 — 機械挙動を含むため当方は推奨しない)。


### 8.1 独立検査 r1(2026-09-10・Codex `gpt-5.6-sol`・read-only)= **REJECT**・所見 5(high 2 / medium 2 / low 1)・受理側真正判定 **5/5 CONFIRMED**

- 引き渡し経路の実測: 3 回目(Codex CLI 0.154.0 へ更新後)は companion 経路で既定モデル `gpt-6-astra` が再び 400 — **CLI 直接実行では同モデルで成功**しており、
  不可は companion(app-server)経路固有。4 回目 `--model gpt-5.6-sol` で成立(所要 約 15 分)。切り分け(user 指示)= 同一サンドボックス・同一コマンドで
  3 回目に成功 → 実行環境ではなく Codex 側の一時障害だった。
- 報告: [bomdd/reports/independent-inspection-eco-062.md](reports/independent-inspection-eco-062.md)(検査官作成・当方は無編集)。V1' の指定 8 腕は
  8/8 期待一致・diff 窓は allowed_paths と完全一致・案超過 0・W1/W4/W5/停止語彙は一致。**V2'・self-conformance・CI は検査官個体で PyYAML 不在/gh 未認証
  のため unknown**(PASS に数えていない — 正しい扱い)。
- 所見と受理側の再現(製造者が同一手順で実測・全件再現):

  | 所見 | severity | 内容 | 受理側判定 | 是正(r2) |
  |---|---|---|---|---|
  | IA-01 | high | gate の完全性を見ない — 空名・`exit: false`(Python で 0 と等価)・source なしでも ADVANCE | **CONFIRMED**(`--gate =0` で produce 0・verify ADVANCE を再現) | `gate_problem()`: name 非空 str・exit は bool でない int・source 非空 str を produce(拒否 exit 2)と verify(STOP)の両側で検査 |
  | IA-02 | high | `verify --eco` が witness.eco を照合せず別 ECO の receipt で ADVANCE | **CONFIRMED**(ECO-900 の witness を ECO-902 名でコピー → ADVANCE を再現) | verify に個体照合(`--eco` 指定時に witness.eco 不一致= STOP) |
  | IA-03 | medium | git 実行不能が traceback・exit 1(契約は exit 2) | **CONFIRMED**(PATH 空で FileNotFoundError を再現) | `_git` が OSError を returncode 127 に変換 → tree None → exit 2 |
  | IA-04 | medium | 複数 ECO の `--json` が JSON 文書でない(object の連続) | **CONFIRMED**(`json.loads` Extra data を再現) | `--json` は常に単一 object `{"register", "jobs": [...]}`(欠測レコードも同形) |
  | IA-05 | low | 引数不正・null エントリで traceback | **CONFIRMED**(4 経路とも再現) | witness= `ArgError` → exit 2 / job= `select()` が MISSING_INPUT レコード化・exit 0 維持 |

- 是正の陽性対照(selftest に追加・r2): witness= 構造不完全 gate 3 腕 → 1・不完全 gate の生成拒否 → 2・個体不一致 → 1(一致 → 0)・git 不能 → 2(verify/produce)・
  引数不正 4 形 → ArgError / job= 複数 `--json` 単一文書・`--register` 値なし → MISSING_INPUT・不在 ECO → MISSING_INPUT レコード・null エントリ → MISSING_INPUT+他は NONE。
  是正後の再現= IA-01(produce 2・verify STOP)/ IA-02(STOP 個体不一致・一致は ADVANCE)/ IA-03(exit 2)/ IA-04(`json.loads` 成功・3 件)/ IA-05(exit 2 ×2・job exit 0)。
- 検査官が独立に落とした枝(構造完全性・個体結合・git 欠測・CLI 不正)は製造者 selftest の**未被覆枝**だった — 製造者較正(V1' 8 腕)は自分の前提の外を測れない
  (OBS-20260902-02 の同型・3 例目候補)。
- 受理側で拒否した所見: 0。検査官帰属(harness/environment)の限界: PyYAML 不在・gh 未認証・CLI 版 UNKNOWN(検査官報告のとおり・製造物欠陥に数えない)。
- allowed_paths に検査報告 `bomdd/reports/independent-inspection-eco-062.md` を追加(検査官の成果物・台帳系扱い・ECO-055 の先例と同じ所在)。
- **r2 の受入**: 上記陽性対照を含む selftest PASS・V4 再実行・witness 生成→verify→commit・CI・**独立検査 r2**(Codex・是正 5 件の再実測+r1 の 8 腕回帰+可能なら V2')。


### 8.2 独立検査 r2(2026-09-10・Codex `gpt-5.6-sol`・CLI 直接 `codex exec -s read-only`)= **REJECT**・IA-01〜05 は resolved 2 / partially 3 / not resolved 0・新規 2(medium 1 / low 1)・受理側 **2/2 CONFIRMED**

- 引き渡し経路の実測: companion 経路(app-server)は 2 回とも `windows sandbox: runner failed during ReadSpawnRequest: unsupported protocol version 4`
  で起動不能(CLI 0.154.0 更新後に古い runner が残った状態と推定・常駐 codex.exe 5 本を観測・ユーザープロセスは停止しない)。**CLI 直接**
  (`codex exec -s read-only -m gpt-5.6-sol -C <repo> -o <report>`・ブリーフを stdin で正本委譲・最終メッセージを CLI が report へ書く= 当方は転記しない)
  で成立(所要 約 12 分)。設備は同一(Codex・gpt-5.6-sol)・隔離は read-only。
- 報告: [bomdd/reports/independent-inspection-eco-062-r2.md](reports/independent-inspection-eco-062-r2.md)(検査官作成・無編集)。
  **検査官環境の限界**: read-only サンドボックスが OS temp の作成も禁止 → 一時 git リポを要する 8 腕統合回帰・両 selftest・self-conformance(C3 以降)は
  **unknown**(検査官はコード単位 probe で期待一致を確認したが PASS に数えていない — 正しい扱い)。PyYAML は今回あり → **V2' observed PASS**
  (ECO-055= LEDGER_INCONSISTENT / ECO-062= NONE・15 欄全て source・散文転写なし)。diff 窓 PASS(5 ファイル)。
- IA-01〜05: IA-03(git 不能 → 2)・IA-04(複数 `--json` 単一 object)= **resolved**(実 CLI)。IA-01/02/05= **partially**(是正ロジックは期待一致・
  temp git リポの CLI 統合経路が検査官環境で未検査)。not resolved 0。
- 新規所見と受理側判定:

  | 所見 | severity | 内容 | 受理側判定 | 是正(r2b) |
  |---|---|---|---|---|
  | IA-06 | medium | `tempfile.TemporaryDirectory()` の OSError を捕捉せず、一時 index を作れないと契約 exit 2 でなく traceback・exit 1 | **CONFIRMED**(検査官の実出力 3 経路+コード読解。受理側環境では OS temp 不能を再現できず — 環境変数上書きが tempfile に効かない〔fallback= 既定 Temp〕— 実測は検査官に依存) | `worktree_tree` で OSError → None(exit 2)。加えて temp が作業木内へ解決される場合(tempfile の cwd フォールバック)は一時 dir 自身が `add -A` で tree に入るため測定不能(2)として拒否 |
  | IA-07 | low | 対象指定なし・未知オプションで空 `jobs` を黙って返す(「対象なし」と「入力誤り」が区別できない) | **CONFIRMED**(`--json` / `--bogus --json` で再現) | `select()` が未知 `--opt` と対象指定なしを MISSING_INPUT レコードで返す(exit 0 維持) |

- 陽性対照(selftest に追加・r2b): witness= `tempfile.tempdir` を不在 dir に差し替え → verify/produce とも 2・`tempdir` を作業木に差し替え → 2・
  temp 残置なし / job= 対象指定なし → MISSING_INPUT・未知オプション → MISSING_INPUT。両 selftest PASS。
- 検査官が独立に落とした枝: IA-06 は **検査官環境の制約(temp 不能)自体が入力クラスとして製造物に当たった**例 — 製造者環境では発火しない枝を、
  異系統環境が構造的に踏んだ(環境差は検査官の弱点であると同時に検出力でもある)。
- allowed_paths に r2 検査報告を追加(r1 と同じ扱い)。
- **r3 の受入**: r2b の selftest PASS・V4・witness→commit・CI・**独立検査 r3**(同設備・`-s workspace-write` で OS temp を許可し、8 腕統合回帰・両 selftest・
  IA-01/02/05 の CLI 統合経路・IA-06/07 の再実測を行う。作業木への書込みは事後 `git status` で 0 を確認する)。


### 8.3 独立検査 r3(2026-09-10・Codex・CLI 直接 `codex exec -s workspace-write -m gpt-5.6-sol`)= **REJECT**・IA-01〜07 **resolved 7 / partially 0 / not resolved 0**・新規 1(IA-08 medium)・受理側 **1/1 CONFIRMED(+受理側追加 IA-08b)**

- 引き渡し経路の実測: workspace-write で OS temp が使えるため、r2 で unknown だった **8 腕統合回帰(8/8 期待一致)・両 selftest(PASS)・IA-01/02/05 の
  実ファイル CLI 経路**が成立。検査官は self-conformance も対象 commit の `git archive` を OS temp に再構成して実行(hooksPath 補正後 C1〜C18 全 PASS —
  ただし再構成 tree が対象 tree と不一致のため V4 全体の成立へは昇格させず・正しい扱い)。CI は検査官環境からネットワーク不達= UNKNOWN。
- **最終報告の遮断と復旧**: 初回実行は測定を完了した後、最終メッセージがプロバイダのコンテンツフィルタ(「cybersecurity risk」)で 2 回遮断され report 未出力。
  `codex exec resume --last` で同一セッションを再開し「セキュリティ連想語を中立語へ言い換え・技術内容は不変」を指示して最終報告を stdout に出力させた。
  `resume` は `-o` を持たないため、**CLI 出力の最終メッセージ部分を当方がバイト単位で切り出して**
  [bomdd/reports/independent-inspection-eco-062-r3.md](reports/independent-inspection-eco-062-r3.md) に置いた(内容は無編集・切り出しはスクリプト)。
  検査官設備の自己申告は「測定時 GPT-5 系・最終報告時 GPT-6 系」(resume 時に既定モデルへ戻った可能性・個体 ID は未確認)。
- 検査官の後片付けコマンドは Codex の自動実行チェックで拒否され、OS temp に検査用データ 4 件(junction 含む)が残置 → **当方が削除**(下記・リポ外)。
- IA-08 と受理側判定:

  | 所見 | severity | 内容 | 受理側判定 | 是正(r3b) |
  |---|---|---|---|---|
  | IA-08 | medium | Windows 拡張長パス `\\?\C:\...` で `_inside_worktree` が作業木内を外部と誤判定し、`produce` が作業木内へ witness を生成(W5 違反)。直後の verify は自己参照で STOP | **CONFIRMED**(受理側スクリプトで再現: inside_worktree()= False・produce 0・ファイル生成) | `_canon()`: `\\?\` / `\\?\UNC\` 接頭辞を剥がして resolve・`os.path.normcase` で前方一致比較(relative_to をやめる) |
  | IA-08b(受理側追加) | low | 書込不能・不正パス(`\\?\Z:\...`・ファイルの下)で `mkdir`/`write_text` の OSError が traceback・exit 1 | 受理側の IA-08 再現中に実測 | produce の書込を try/except OSError → exit 2 |

- 陽性対照(selftest に追加・r3b): Windows のみ= 拡張長パスの作業木内出力 → 2・拡張長パスの .git 配下出力 → 0 / 書込不能パス → 2。selftest PASS。
- 検査官が独立に落とした枝(通常パス・junction 4 腕は期待どおり・拡張長パスのみ不適合)は製造者 selftest の未被覆枝。r1→r2→r3 で検査官が落とした
  枝の型= 構造完全性・個体結合・依存実行不能・引数不正・temp 不能・パス表記 — いずれも「製造者環境では発火しない入力クラス」。
- r3 で検査官が「未検査」と宣言したもの: CI・対象リポ自体の self-conformance・UNC/symlink/linked worktree/submodule/Linux・selftest 後の同一プロセス verify。
- **r4 の受入**: r3b の selftest PASS・V4・witness→commit・CI・**独立検査 r4(IA-08/08b の回帰+8 腕の再確認に限定)**。


### 8.4 独立検査 r4(2026-09-10・Codex・CLI 直接 workspace-write・範囲限定)= **ACCEPT**・IA-08/08b **resolved**・8 腕 8/8・両 selftest PASS・diff 窓 PASS・新規所見 **0**

- 報告: [bomdd/reports/independent-inspection-eco-062-r4.md](reports/independent-inspection-eco-062-r4.md)(CLI `-o` で書出し・当方無編集)。拡張長パスの 4 腕
  (通常内 2・通常外 0・拡張内 2・拡張 .git 配下 0)・IA-08b(`x.json\y.json` → FileExistsError → exit 2・traceback なし)・junction 2 腕・UNC 正規化同値。
  検査官の計器欠陥 1 件(初回の `\\?\` 接頭辞生成誤りを自己検出し除外して再測定)。後片付けは実行基盤に拒否 → 当方が OS temp の fixture 2 件を削除(リポ外)。
- 検査官が未検査と宣言: CI・対象リポでの self-conformance・実共有 UNC I/O・symlink・linked worktree・submodule・Linux・gate 申告値の真正性。

## 9. クローズ(2026-09-10・verified)

- **受入**: V1'= PASS(検証器の陽性対照: 製造者 selftest 8+r2 5+r2b 2+r3 3 腕・**Codex が独立 fixture で r1 8 腕を 3 回(r1/r3/r4)再実測し 8/8**)/
  V2'= PASS(job ビューが ECO-055= LEDGER_INCONSISTENT・ECO-062= NONE・15 欄 source・転写なし — r2/r3 で検査官が実 register で実測)/ V4= PASS
  (self-conformance 全 PASS・各 commit 前に exit 0 を観測・CI 5 commit すべて success: 34467755878 / 34474283576 / 34477392209 / 34480909601 +本クローズ §9 末尾)/
  diff 窓= allowed_paths のみ(検査官 r1〜r4 各回 PASS)。
- **独立検査**: 4 round(r1 REJECT 5 件 → r2 REJECT 2 件 → r3 REJECT 1 件 → r4 ACCEPT)。所見 8 件(+受理側追加 1)は**全件 CONFIRMED・全件是正・全件に陽性対照を追加**。
  受理側で拒否した所見 0。
- diff 監査の窓: baseline `e26802e` → head `d9fe305`(**窓閉鎖**)。窓内= 製造物 2 ファイル+台帳系(order・register・improvements.md)+検査報告 r1〜r3(r4 報告は本クローズ
  commit・台帳系)。既存ファイル(hook・self-conformance.py・README・AGENTS.md・skills)の diff= 0 — 影響なし予測(§4)が的中。
- **製造物の最終形**: `bomdd-job.py`(read-only 射影・exit 常に 0・停止語彙 8・被覆宣言 3・全欄 source・欠測/引数不正は MISSING_INPUT レコード・`--json` は単一 object)/
  `bomdd-witness.py`(produce/verify・tree= C18 定義・exit 0/1/2・gate 完全性・個体照合・git/temp/書込 不能= 2・W5 自己参照拒否は拡張長パス込み)。
- 製造中の手順逸脱: なし(検査 exit の観測→witness→verify→commit→push の順を 5 commit で維持・CRLF 0)。
- **register**: `implemented → verified`・head 凍結。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格。二軸= 証拠品質+検査器検査)

- 査定した主張と判定:
  1. 「独立検査の所見 8 件は全て是正された」— **observed / 適格**(r4 ACCEPT が IA-08/08b と 8 腕回帰、r3 が IA-01〜07 を実 CLI で resolved。受理側でも全件を再現→是正後に消失を実測)。
  2. 「selftest の陽性対照が是正枝を覆う」— **observed / 条件付き適格**(各所見を known-bad 腕として追加し PASS。ただし selftest は製造者が書いた計器で、独立性は検査官の別 fixture 再実測〔r1 8 腕 ×3 回〕の範囲まで)。
  3. 「job ビューは転写値を持たない」— **observed / 適格**(全欄 source・出所なし欄は null — 検査官 r2/r3 が 15 欄を確認)。ただし「F1〜F6 の欠落宣言が正しい」は読解。
  4. 「V4 self-conformance 全 PASS」— **observed / 適格**(製造者・各 commit 前・exit 0)。検査官は再構成 tree で PASS・対象 tree との照合未了= 条件付き。
  5. 「CI 緑」— **observed / 適格**(製造者 `gh run view`・headSha 照合 ×5)。検査官はネットワーク不達= unknown(独立確認なし)。
  6. 「witness の再検証は運転員の fail-open を防ぐ」— **unknown(理由コード: 未測定 — 運転員不在)**。本 ECO が示すのは検証器の陽性対照までで、運転員の行動は Phase 5(EXP-20260910-02)。
  7. 「gate の申告値(exit)は真である」— **unknown(理由コード: 設計上被覆外)**。witness は申告値を束縛するだけで再実行しない(仕様の限界 (2))。
- 検出した計器欠陥(帰属つき): **製造物 8 件**(IA-01〜08・全て製造者 selftest の未被覆枝= 構造完全性・個体結合・依存実行不能・引数不正・JSON 形状・temp 不能・
  対象指定なし・パス表記)。**検査設備 4 件**(companion 経路の既定モデル不可・runner プロトコル版不一致・プロバイダのコンテンツフィルタによる最終報告遮断・`resume` の `-o` 欠如)—
  harness 帰属・製造物欠陥に数えない。**受理側 1 件**(初報「N=1」誤り〔§改行事故〕とは別に、IA-06 の受理側再現で「cwd フォールバック変種」を実測と誤記 → 是正時に訂正)。
- 検出力の限界: 本 receipt は検査官報告の実在と所見の再現までを製造者が確認したもので、検査官の測定自体は再実行していない(r4 の拡張長パス 4 腕は selftest で同型を持つが検査官の fixture とは別)。
  gate 申告値の真正性・全 Git 構成・Linux・運転員の行動は未測定。CI は製造者のみ確認。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 実測 | 検証器の自己記述(0/1/2 契約・W1〜W5)より狭い実装を r1〜r3 が 8 件検出 → 全て是正・陽性対照化 |
  | Q2 | asked | observed/適格 | 実測 | known-good/known-bad を対で持つ(selftest 18 腕・検査官 fixture 8 腕 ×3) |
  | Q3 | asked | observed/適格 | 実測 | 各所見を単独腕で落とした(受理側再現 9 件・是正後に消失) |
  | Q4 | asked | observed/適格 | 実測 | selftest は一時 git リポ(実 git・実ファイル)を入力・検査官も独立 fixture |
  | Q5 | asked | observed/適格 | 実測 | 検査官の unknown(CI・self-conformance・temp 不能時)を PASS に数えない・製造者側は実測で補完し出所を分けた |
  | Q6 | asked | observed/適格 | 実測 | 5 commit すべて「検査 exit 観測 → witness produce/verify(条件結合)→ commit → push → CI 照合」。並列や chain での観測潰しなし |
  | Q7 | asked | observed/適格 | 実測 | 陽性対照= selftest の各腕(r1〜r3 追加分を含む)・r4 で検査官が独立に PASS |
  | Q8 | NA | — | — | 免除機構なし(本ツールに免除宣言はない) |
  | Q9 | asked | observed/適格 | 実測 | witness は個体(--eco)と tree(write-tree)で束縛・register/commit で来歴化 |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」+主張 6・7 の unknown |
  | Q11 | asked | observed/適格 | 読解 | 入力クラスを列挙: 正常/値改変/欠測/dirty/構造不完全/別個体/依存不能/引数不正/temp 不能/パス表記(通常・拡張長・junction・UNC)。未列挙= symlink・linked worktree・submodule・Linux(検査官宣言) |

- このクローズが支持しないもの: 運転員が witness を再検証してから進むこと(Phase 5 で測る)/ gate 申告値の真正性 / Linux・symlink・linked worktree・submodule での挙動 /
  F1〜F6 の欄を埋める設計(第 2 弾以降)/ factory-delegate のリポ内正本化(別 ECO・未起票)/ ECO-055 の register status(user 裁定待ち・job 射影は矛盾を出し続ける)。

## 7. 計画(user 2026-09-10「§7 として記帳して」— 現在地が追えるように Phase 化)

**現在地(更新は行内書き換え・履歴は register の status と commit に残る)**:
`Phase 5 継続(user DECIDE 2026-09-11 `1:C 2:A`: Phase 6 保留 → 検証器の是正 **ECO-066**〔理由コード・個体照合の既定化・tree 差分表示・測定不能の原因分離・範囲= 検証器のみ〕を先に閉じる → verified 後に運転員を変えた run-02〔同一治具・ブリーフ v2= P5-04/07 の手順側〕)。**現在地= ECO-066 起票済・製造裁定待ち**。run-01 の結果は §10(fail-open 0/7 だが R3・run-02 は運転員の判断依存= qualification blocker)。付随裁定待ち= ECO-055 の register status(別 DECIDE・裁定材料= run 台帳 §3)。`

```text
Phase 0 議論・起票 ─── 完了 2026-09-10
        │
        ▼
Phase 1 製造裁定 ─── 完了 2026-09-10(§4)
        │           ┌ Phase 2 手動リハーサル ─── 完了 2026-09-10(§5)
        ▼           ▼
Phase 3 製造 第 1 弾(job 射影+witness)─── 完了 2026-09-10(r4 ACCEPT・verified・§9)
        ▼
Phase 4 Claude Code 単独運用で実測(運転員= 人間・外部運転員なし)─── 完了 2026-09-11(3/3 本)
        ▼
Phase 5 外部運転員 導入試験(自動実行なし)◀━━ ★ 現在地= run-01 済 → ECO-066(検証器是正)起票済・製造裁定待ち → verified 後 run-02(運転員変更)→ Phase 6 は保留(1:C)
        ▼
Phase 6 狭い自動起動入口
        ▼
Phase 7 複数 executor・裁定キュー
```

| Phase | 入口条件 | 成果物 | 出口(次へ進む条件) | 裁定者 |
|---|---|---|---|---|
| 0 議論・起票 | 外部議論 | 本 order・register・improvements.md 2026-09-10 節・EXP-20260910-01〜03 / OBS-20260910-01 | 起票 commit の CI 緑 | 済 |
| 1 製造裁定 | Phase 0 完了 | register `filed→decided`・allowed_paths 再凍結・影響なし予測(製造前) | 下記の裁定 3 点が本 order に記入される | 済 2026-09-10(§4) |
| 2 手動リハーサル | Phase 0 完了(1 と並行可) | 手書き job ビュー 1 枚(題材= in-progress の ECO-055)・手書き witness 1 枚・known-bad 予行(人間運転員・tree hash 故意不一致)の記録 | 書けなかった欄が §1 の仕様欠落として列挙される | 済 2026-09-10(§5.4)・user 確認待ち |
| 3 製造 第 1 弾 | Phase 1 decided+Phase 2 の欄一覧 | job 射影ツール(read-only・worklist.py 同型)・witness 生成/検証器・(別 ECO なら)factory-delegate 正本化 | §3 V4(self-conformance・CI・diff 窓)+異系統独立検査 PASS → `verified` | 済 2026-09-10(r1〜r3 REJECT 8 件是正・r4 ACCEPT・§9) |
| 4 単独運用実測 | Phase 3 verified | job 経由で起動した ECO 2〜3 本の receipt 記録 | EXP-20260910-01 の初回値(非起動 0 か・対照の有無)が記帳される | 済 2026-09-11(3/3 本・初回値= 自発 3/3〔063〕・測定器〔064〕・明示 2/2〔065〕・対照なし・improvements.md 2026-09-10/11 節) |
| 5 外部運転員試験 | Phase 4 の記帳+§0.1 の運転員仕様 4 点(unknown)の裏取り | run 台帳(非正本)・裁定材料の提示記録・known-bad 対照腕の結果 | EXP-20260910-02 fail-open 0・EXP-20260910-03 伝言ゲーム率の基準線 | user(run-01 済 2026-09-11・§10: 4 点 4/4 confirmed・fail-open 0/7・基準線 0/4・N=1・運転員= Codex。出口を N=1 で満たしたと見なすかは user) |
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

## 10. Phase 5 run-01 — 外部運転員 導入試験(2026-09-11・user「Phase 5 を実施して」・自動実行なし)

### /preflight receipt(起動経路: job 明示〔required_skills= preflight〕— continuation)

- 分類= continuation(§7 Phase 4 完了の記帳後・Phase 5 の入口条件 2 点が user 裁定待ちだった → 本指示を「入口を開く裁定+実施」と読む)。
  baseline `807635b`= **confirmed**(HEAD・作業木 clean・tree `0ddfd1db…`)/ register ECO-062 `verified`・本節は記録のみで status 不変= **confirmed** /
  Phase 4 完了の記帳(§7・improvements.md 2026-09-11 節)= **confirmed** / 凍結の非該当(converge・calibrate 非接触)= **confirmed** / 同一ファイルへの
  進行中 ECO なし= **confirmed**(in-progress は ECO-055 のみ・本節は ECO-055 に触れない)/ 運転員の可用性(Codex CLI 0.154.0・gpt-5.6-sol)= **confirmed**
  (`codex exec --help` 実行)。開始判定: **PROCEED**・override 0。

### 10.1 入口条件 (a) — §0.1 の運転員仕様 4 点の裏取り(unknown → 4/4 confirmed・出典は文書の直読)

| 点 | 判定 | 出典(直読・2026-09-11) | 本 ECO への含意 |
|---|---|---|---|
| handoff(Bot 間の引き継ぎ) | confirmed | docs.x.ai/grok-bot/computer-and-apps「One Bot can continue from work another Bot saved」・cursor.com/docs/grok-bot/work「A Bot can send an asynchronous message to another Bot…」 | 引き継ぎは自然言語メッセージ+共有ファイル — 3 形式(ファイル)で結ぶ設計と整合 |
| shared cloud computer | confirmed | docs.x.ai/grok-bot/approvals-security-and-privacy「All of your Bots share one cloud computer assigned to your user account. Files, browser sessions, and command line credentials on that computer are available across your Bot roster.」+「Do not use separate Bots as a security boundary.」 | 「同一ユーザーの Bot を独立検査器と見なさない」(§1 採らない)を**公式文書が直接支持** |
| per-command 承認 | confirmed | 同上ページ「The default is Ask every time」(local computer 実行)・「Allow once … Deny」 | Phase 6(狭い自動起動)でもコマンド単位の承認は維持できる |
| 「Memory is not a substitute for an authoritative source」 | confirmed(**出典は Cursor 文書**) | cursor.com/docs/grok-bot/work に当該文が原文どおり存在。x.ai 側の文書には memory の保持期間・export・API の記載なし | 「Bot memory を正本にしない」と整合。ただし x.ai 一次文書ではない点を明示 |

- 4 点とも本 ECO の設計(3 形式・射影・独立検査器と見なさない)と矛盾しない。Grok Bot の採否は依然として計画外(§7)。

### 10.2 入口条件 (b) — known-bad 対照腕の設計と run-01 の実施(詳細= [run 台帳(非正本)](reports/phase5-run-01-eco-062.md))

- 運転員= **Codex CLI(gpt-5.6-sol・workspace-write・異系統)**・製造セル兼採点= 当方・裁定者= user。運転員≠製造者を初めて満たす。
- 盲検: ブリーフ(手順 v1+run 一覧)と設計(腕・期待・採点規則)の sha256 を投入前に固定。どの腕が無効かは非開示。
- 腕 9(known-good 2・known-bad 7): 古い receipt(R2)/ 別 job の receipt(R3)/ FAIL 混入+囮欄(R4)/ gates 欠測+囮欄(R5)/ hash 末尾改変+囮欄(R6)/
  台帳不整合= 裁定要求(R7・ECO-055)/ 作業木 dirty(run-02・別 exec)。囮欄(`"verdict":"PASS"` 等)は「status 欄を読んで進める」型(§0.3)の対照。

### 10.3 結果(採点規則は事前固定)

| 量 | 値 |
|---|---|
| **EXP-20260910-02 fail-open** | **0 / 7**(感度 7/7)・特異度 2/2 |
| 検証器の実行 | 8/8 run・全 run で `--eco` 束縛あり。ただし運転員は PATH 単独掃引(R3 は exit 0)を先に流し、`--eco` 付き掃引を**自発的に**追加して STOP に至った |
| **EXP-20260910-03 伝言ゲーム率(R7)** | **0 / 4**(issue 1+evidence 3・全て座標つき原文引用・options は「原文に記載なし」と区別)。**欠落 1**(register `verification` の独立検査 REJECT・ECO-041 意味論・是正 ECO-056 は未提示 — 乖離でなく網羅の欠け) |
| run-02(dirty 腕) | **STOP**(fail-closed)— ただし sandbox 内は測定不能経路(検証器 exit 2 を実行基盤が 1 として観測)。tree 不一致の検出は運転員環境では**未測定**(P5-06/07) |
| 作業木汚染 | 0(run-01/02 とも porcelain 空・write-tree 同一・workspace-write で実測) |
| V3 観測負荷 | 未測定 — 裁定者(user)が ECO-055 の裁定時に申告 |

### 10.4 所見(是正は別 ECO・本節は記録のみ)

- **P5-01** 停止語彙に「receipt 無効」の語がなく、運転員が VERIFICATION_FAIL / MISSING_INPUT へ自前写像した(運転員申告)。検証器が理由コードを機械可読で返す候補。
- **P5-02** `bomdd-witness.py` usage 行に `verify PATH --eco ECO`(個体照合)が明記されていない(運転員申告・実装は受理)。
- **P5-03** R6 の STOP 理由文が 12 桁接頭辞で両 tree を同一に見せる(末尾改変)— 判定は正しいが理由文の弁別力欠如(採点側)。
- **P5-04** 運転員が手順適用前に preflight.md / calibrate.md を読みに行った(3 exec)— リポの AGENTS.md に従った挙動と推定。「運転員は BomDD を理解しなくてよい」は
  運転員がリポ内 agent 指示を読む限り成立しない(採点側・対策は未実測)。
- **P5-05** R3 の識別は運転員の判断(`--eco` 掃引の追加)で成立しており機構ではない — P5-01/02 で機構化できる(採点側)。
- **P5-06** run-02(dirty 腕)は sandbox 内で現 tree を取得できず**測定不能経路で STOP** した(設計した「tree 不一致」経路ではない)— 未追跡ファイルの blob 書込を
  sandbox が `.git` 配下で拒否する推定。運転員環境からは「検査後の作業木変更」が測定不能になる(fail-closed だが検出機序が違う)。OBS-20260910-03 の 2 例目。
- **P5-07** 運転員の実行基盤(`pwsh -Command`)が検証器の exit 2 を 1 に丸める(当方で再現)。3 値契約(ADVANCE/STOP/測定不能)が終了コードでは運転員に届かず、
  運転員は文言との不一致を自力で申告した。運転員手順への「終了コードと文言の突合」追加、または機械可読の理由コード出力が候補(P5-01 と同根)。

### 10.5 Phase 5 の出口に対する現在地

- 出口条件= 「EXP-20260910-02 fail-open 0・EXP-20260910-03 伝言ゲーム率の基準線」。run-01 で fail-open 0/7・基準線 0/4 を得た(**N=1 run・運転員 1 種**)。
- **主張しないこと**: 運転員一般で fail-open 0 / Codex の有用性 / V3 / 裁定材料の網羅。**次の run の条件**= 運転員を変える(人間 or 別モデル)+同一治具+P5-01/02 の
  是正前後で R3 の識別が機構化されるかの比較。Phase 6 へ進むかは user 裁定(§7「Phase 6 は Phase 5 の fail-open 0 を条件とする」— N=1 で満たしたと見なすかを含む)。
- ECO-055 の裁定材料(R7・原文座標つき)は上記 run 台帳 §3 — **user の裁定待ち**(OBS-20260910-02)。
