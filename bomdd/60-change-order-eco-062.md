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

## 7. 計画(user 2026-09-10「§7 として記帳して」— 現在地が追えるように Phase 化)

**現在地(更新は行内書き換え・履歴は register の status と commit に残る)**:
`Phase 3 製造 第 1 弾: 製造・製造者受入(V1' V2' V4)・CI 緑(§6・§8)→ **停止点: 独立検査 UNKNOWN**(Codex 環境障害 2 回・§8)— user 裁定待ち(復旧再引き渡し / 別検査官 / 裁定 3 の変更)。付随裁定待ち= ECO-055 の register status(§5.1 F0)。`

```text
Phase 0 議論・起票 ─── 完了 2026-09-10
        │
        ▼
Phase 1 製造裁定 ─── 完了 2026-09-10(§4)
        │           ┌ Phase 2 手動リハーサル ─── 完了 2026-09-10(§5)
        ▼           ▼
Phase 3 製造 第 1 弾(job 射影+witness)◀━━ ★ 現在地= 製造済み・独立検査 UNKNOWN(停止点・§8)
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
| 2 手動リハーサル | Phase 0 完了(1 と並行可) | 手書き job ビュー 1 枚(題材= in-progress の ECO-055)・手書き witness 1 枚・known-bad 予行(人間運転員・tree hash 故意不一致)の記録 | 書けなかった欄が §1 の仕様欠落として列挙される | 済 2026-09-10(§5.4)・user 確認待ち |
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
