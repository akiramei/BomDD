# Change Order — ECO-072(ECO-062 Phase 7 第 1 弾: 設備台帳の属性化+独立性判定の機械化 — 独立検査として成立しない組合せを入口が弾く〔verified〕)

> 裁定: user 2026-09-12「ECO-062 を再開して。Phase 7 を DISCUSS から」→ DISCUSS(thesis: 第 1 弾は設備台帳の属性化+独立性判定に絞る・P6-02 は第 2 弾・裁定キューは保留)に
> user AGREE。**起票のみ**(製造裁定は別 DECIDE・範囲の凍結は裁定時)。親= [ECO-062](60-change-order-eco-062.md) §7 Phase 7(入口= Phase 6+設備認定台帳の属性化・
> 成果物= stop_type→配送先の機械定義〔ECO-067 で済〕+独立性判定の機械化〔§1-5〕・出口= **独立検査として成立しない組合せを機械が弾いた実測 1 例**)。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**。
- producer: EQ-001
- inspector: EQ-002
- 検査官(独立検査併用時): gpt-5.6-sol @ Codex CLI(`codex exec`・sandbox は round ごとにブリーフへ明記・セッション分離あり)。round の range と実行環境の差は各ブリーフに宣言。
  配員欄(producer/inspector)は本 ECO で新設した様式の初例(job 射影が `required_capability` に解決)。

## 0. 実測(起票根拠)

- **設備台帳は機械可読の形で存在しない**: `bomdd/` に設備台帳ファイル 0(ls)。設備認定 equip-01〜03 は improvements.md と loops の散文。order「担当設備」欄は事後記録・
  self-reported(ECO-062 §5.4 の欠落 F2= `required_capability` が設備認定 ID を参照する欄がない)。
- **入口は executor を識別しない**: `bomdd-run.py --cell` は cell を文字列で shell 起動し、run 台帳に残るのは cell 文字列と exit のみ(ECO-067 §1 の範囲)。製造者と検査官が同一設備でも
  入口は止められない(Phase 6 実 cell N=1 は Codex read-only で当方が手で選んだ)。
- **独立性は宣言属性の照合でしか判定できない**(実測): Grok 公式「Do not use separate Bots as a security boundary」(ECO-062 §10.1 確認済)/ モデル名記録の系統的欠落
  (EXP-20260711-05 再演 4 回)/ 製造担当モデルは maintainer 申告のみ(ViewTube)。→ 機械が弾けるのは「宣言上同一」までで、属性ごとの**来歴**(self-reported / harness-measured /
  user-declared)を台帳が持たないと偽の独立を通す。
- **設備属性が検出力を左右した実測**: Codex read-only sandbox の temp 不能(TEMP_UNAVAILABLE・Phase 6 §10.7)/ workspace-write と read-only で cell 挙動が違う(Phase 5 P5-05・P5-06)/
  pwsh -Command の exit 丸め(P5-07)。OBS-20260910-03 は 3/3 で playbook §3 に「実行環境の差を設計項目に」として織り込み済(f3974c9)・templates は ECO-069。→ sandbox モード・
  temp 可否・exit 伝播は台帳属性の候補。
- **独立性の評価軸(§1-5)**: 同一モデル / ハーネス / fixture / oracle / 前提。機械照合できるのはモデル・ハーネス・アカウント系統の 3 軸。fixture・oracle・前提は round ごとの宣言
  (検査ブリーフの range・環境欄= ECO-069)で、台帳属性ではない。

## 1. 変更要求(候補 — 製造裁定で凍結)

1. **設備台帳** `bomdd/70-equipment.yaml`(新規・register と同格の台帳・手書き正本): entry= `id`(EQ-NNN)・`kind`(ai-model / human)・`model`・`harness`・`account_lineage`
   (同一ユーザー/同一 API 所有者の系統)・`sandbox_modes`(利用可能なモード)・`temp_available`(モード別)・`exit_propagation`(丸めの有無)・`qualification_ref`(equip-01〜03 / loop・
   なければ unqualified)・**各属性の来歴** `provenance`(self-reported / harness-measured / user-declared)・`status`(active / retired)。初期エントリ 3: 当方(claude-fable-5-1 @ Claude
   Code)・Codex(gpt-5.6-sol @ Codex CLI・read-only/workspace-write・read-only は temp 不能)・人間運転員(run-02)。初期値の来歴はすべて self-reported/user-declared(harness-measured 0 を明記)。
2. **order の配員欄**: `templates/60-change-order.md` の「担当設備」に `producer: EQ-NNN` を、検査官行に `inspector: EQ-NNN` を追加(自リポの新規 order も同様)。job 射影
   (`bomdd-job.py`)が order からこれを読み `required_capability` に解決(台帳に無い ID → 既存の停止語彙で止める・新語彙を増やさない)。
3. **独立性判定(入口)**: `bomdd-run.py --cell` に **`--executor EQ-NNN` を必須**にする(無ければ起動しない・fail-closed)。判定は宣言属性の照合: (a) producer と executor が同一 `id`
   → STOP (b) `model`・`harness`・`account_lineage` の 3 軸がすべて一致 → STOP(独立検査として不成立)(c) 3 軸のいずれかが台帳で `unknown` → STOP(照合不能を通過にしない)。
   新 stop code **`INDEPENDENCE_FAIL`**(配送先 operator= 配員のやり直し)を DELIVERY 表に追加。判定行は 1 行(`STOP INDEPENDENCE_FAIL(producer=EQ-001 executor=EQ-001 axes=id)`)。
4. **selftest 腕**: 同一 id / 3 軸一致(別 id)/ 異系統 → ADVANCE / `--executor` 欠落 / 未知 id / 台帳欠落・不正 / 軸 unknown。
5. **受入**(候補): **V1** selftest 全腕。**V2(出口条件)**: 実入口に producer と同一 executor を与えて STOP、異系統(Codex)を与えて ADVANCE→起動、を実 cell で 1 回ずつ実測(known-bad
   1 例+陽性対照 1 例)。**V3** self-conformance・CI・diff 窓。**V4** 異系統独立検査(Codex・range と実行環境の差をブリーフに宣言= ECO-069 の欄)。**V5** 較正 receipt(trigger ①③)。

**採らない**(起票時点): 台帳を register に埋め込む(二重正本)/ executor の自動検出(ハーネス計測は unknown を許し、来歴欄で区別する)/ 独立性の**実効**の主張(判定は宣言上の照合まで —
Grok 公式の境界)/ fixture・oracle・前提の機械照合(round ごとの宣言に留める)/ P6-02(cell 判定の receipt 回収= 第 2 弾)/ 裁定キュー(失敗未観測・保留)/ product-profile 配布(別 ECO)。

## 2. 影響なし予測(製造前・起票時点 — 製造裁定で凍結)

範囲 A(§3)なら diff= tools 2(bomdd-job.py・bomdd-run.py)+新規 yaml+templates/60-change-order.md 検査官行+自リポ order 1〜2 通の配員欄+台帳系。self-conformance: C4/C14(kit 鮮度)は
templates 変更で advisory・C7 不変・C13 は新 yaml へのリンク実在・tools の selftest は C11 系の対象外(自己 selftest で担保)。既存 ECO の job ビューは配員欄が無くても壊れない
(欄なし= required_capability null・従来どおり)ことを V1 に含める。hooks・.github diff 0。

## 3. 製造裁定の候補(別 DECIDE で提示)

- **A** 台帳+配員欄+入口判定+selftest(§1 の 1〜4 すべて・出口条件を満たす最小の完全形)。
- **B** 台帳+入口判定のみ(§1 の 1・3・4。producer は `--producer EQ-NNN` で運転員が宣言・job 射影と templates は第 2 弾)。
- **C** 台帳のみ(判定は人間・機械化は次 ECO)。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-072` の出力を開始 artifact として読んだ)

- 分類= 新規機能(親 ECO-062 の Phase 7・DISCUSS→AGREE 済)。baseline `58205be`= **confirmed** / 次番 072= **confirmed**(grep 0)/ Phase 6 出口の成立= **confirmed**(ECO-067 verified・
  実 cell N=1・user 裁定で Phase 7 入口)/ 設備台帳の不在= **confirmed**(ls)/ 入口の executor 非識別= **confirmed**(bomdd-run.py 実読)/ 同一ファイルへの進行中 ECO なし= **confirmed**
  (ECO-067/068 は verified)。
- job ビュー: required_skills= `["calibrate", "preflight"]`・skills_missing= `["calibrate"]`(order 生成後に出力)
- 開始判定: **PROCEED(起票のみ)**・override 0。製造は裁定後。

## 4. 製造裁定と製造(2026-09-12・user DECIDE「A」= 完全形)

- **製造裁定 A**(user 2026-09-12): §1 の 1〜4 すべて。register `filed → implemented`(本 commit)・allowed_paths 再凍結= tools 2+`bomdd/70-equipment.yaml`+templates/60-change-order.md+
  自リポ order(本 ECO・ECO-062)+register+improvements.md+`bomdd/reports/independent-inspection-eco-072*.md`。
- **製造物**:
  1. `bomdd/70-equipment.yaml`(新規): EQ-001(claude-fable-5-1 @ claude-code・akiramei@anthropic)・EQ-002(gpt-5.6-sol @ codex-cli・akiramei@openai・read-only/workspace-write・
     read-only は temp 不能)・EQ-003(human @ terminal・akiramei)。各属性に provenance(harness-measured は sandbox/temp のみ・他は self-reported/user-declared・exit_propagation は unknown 2 件)。
  2. `bomdd-job.py`(F2): `load_equipment`(形状・id 構文・重複を検査)・`assignments`(fence 外の `- producer:`/`- inspector:`)・`resolve_capability`(構文外/異なる id/台帳に無い id →
     LEDGER_INCONSISTENT・台帳不能+宣言あり → MISSING_INPUT・欄なし → null F2 従来どおり)。STOP_VOCABULARY に `INDEPENDENCE_FAIL`(job は導出しない・被覆宣言不変)。
  3. `bomdd-run.py`(R9): `--executor EQ-NNN`(--cell に必須・構文検査)・`check_independence`(SAME_ID / SAME_LINEAGE〔3 軸一致〕/ AXIS_UNKNOWN:<axis> / PRODUCER_UNDECLARED /
     EXECUTOR_UNKNOWN → STOP INDEPENDENCE_FAIL → operator・台帳不能 → UNMEASURABLE)。照合は job・receipt が ADVANCE のあと(先行する停止理由を隠さない)。台帳レコードに
     executor/producer/independence{cause,detail,axes}・env `BOMDD_EXECUTOR`・判定行 `STOP ECO-NNN INDEPENDENCE_FAIL(<cause>) → operator @tree`。
  4. `templates/60-change-order.md` 担当設備欄に `- producer:`/`- inspector:` の 2 行(プレースホルダは構文外なので、未記入のまま製品 order に写すと LEDGER_INCONSISTENT で止まる= 意図)。
  5. 本 order の担当設備欄に `- producer: EQ-001` / `- inspector: EQ-002`(様式の初例・job ビュー `required_capability= {producer: EQ-001, inspector: EQ-002}`)。
- **V1**= PASS: `bomdd-job.py --selftest` exit 0(F2 腕: 配員欄→台帳実在・fence 内無視・未知 id/構文外/重複= LEDGER_INCONSISTENT・台帳不在= MISSING_INPUT・台帳 id 重複/構文外= 不正)/
  `bomdd-run.py --selftest` exit 0(独立性 8 腕: SAME_ID・SAME_LINEAGE・AXIS_UNKNOWN・EXECUTOR_UNKNOWN・1 軸違いは起動+BOMDD_EXECUTOR 受領・PRODUCER_UNDECLARED・dry 2・台帳不在・
  --executor なし/構文外 3= ARG_ERROR)/ `bomdd-witness.py --selftest` exit 0(不変)。自己捕捉 1 件: usage 行 85 桁(R7)→ 80 桁に修正。既存 order(ECO-071)の job ビューは
  required_capability null+F2 で従来どおり(後方互換)。
- **V2(Phase 7 出口条件)= PASS・実入口で実測(witness tree 9e77ae540c45・台帳 `.git/bomdd-run/ECO-072.jsonl`)**:

  | 腕 | コマンド | 判定行 | exit | 起動痕跡 |
  |---|---|---|---|---|
  | a 同一 executor(known-bad) | `ECO-072 --executor EQ-001 --cell <marker>` | `STOP ECO-072 INDEPENDENCE_FAIL(SAME_ID) → operator @9e77ae540c45` | 1 | なし |
  | b 異系統(陽性対照) | `ECO-072 --executor EQ-002 --cell <marker>` | `ADVANCE ECO-072 OK → next · launching @9e77ae540c45` / `cell exit 0` | 0 | `ECO-072|EQ-002` |
  | c 人間 executor dry | `ECO-072 --executor EQ-003` | `ADVANCE ECO-072 OK → next · dry @9e77ae540c45` | 0 | — |
  | d --cell に --executor なし | `ECO-072 --cell <marker>` | `UNMEASURABLE ARG_ERROR: --cell には --executor EQ-NNN が必須(独立性判定)` | 2 | なし |

  **独立検査として成立しない組合せ(producer= executor= EQ-001)を機械が弾いた実測 1 例**(§7 Phase 7 の出口)。腕 b が陽性対照(同じ job・同じ receipt で異系統なら起動)。
- **実 cell(V4 r1 の起動経路)**: Codex r1 は `bomdd-run.py ECO-072 --executor EQ-002 --cell "codex exec -s workspace-write …"` で入口から起動(台帳に decision→cell の 2 行)。
  結果は §5。

## 5. 独立検査(異系統・Codex EQ-002・入口 bomdd-run から実 cell として起動)

### 5.1 r1(2026-09-12・range= 境界探索・sandbox workspace-write)— 報告: [independent-inspection-eco-072.md](reports/independent-inspection-eco-072.md)

- 起動: `bomdd-run.py ECO-072 --executor EQ-002 --cell "codex exec -s workspace-write -m gpt-5.6-sol …"` → 判定行 `ADVANCE ECO-072 OK → next · launching @9e77ae540c45` → `cell exit 0`
  (台帳 decision→cell の 2 行・作業木非汚染= 検査官の申告と porcelain の一致)。**検査官の報告は handoff 契約のヘッダ `[INFORM / COMPLETE]` で始まった** — AGENTS.md → SKILL.md の経路で
  第三者(異系統ハーネス)が契約に到達した実測 1 例(ECO-070 較正 receipt の unknown「到達性の実効」が observed に)。
- 判定: **REJECT**(IA-01〜03)。受理側の真正判定(帰属つき):

  | 所見 | 内容 | 受理側判定 | 是正(r1b) |
  |---|---|---|---|
  | IA-01 | 未選択 entry(EQ-003)の `model: [bad]` でも起動する — `load_equipment` は id しか検査しない | **CONFIRMED・製造物**(台帳全体の形状を fail-closed にすべき) | `load_equipment` が全 entry の 3 軸を「文字列か欠落/null」以外なら台帳不正(→ 宣言ありなら MISSING_INPUT)。selftest 陰性対照 3(list / 数値 / null は許容) |
  | IA-02 | `model: m1` vs `M1` の大小文字差だけで 1 軸違い= 独立と数えて起動 | **CONFIRMED・製造物**(表記揺れは独立の根拠にならない) | 比較を `casefold`+連続空白正規化(`_norm`)に。selftest 腕 `ind-case-only`(M1/'  h1  '/A1 → SAME_LINEAGE) |
  | IA-03 | HTML コメント内・他節(`## 説明`)の `- producer: EQ-001` を配員として採用し起動 | **CONFIRMED・製造物**(use/mention の区別が閉じていない) | `assignments` を担当設備節(見出しに「担当設備」/「equipment」・次の同位以上の見出しまで・下位見出しは節内)に限定し、HTML コメントを除去。selftest 陰性対照(コメント・他節・節なし)+下位見出し陽性 |
  | IA-04 | UTF-8 BOM 付き台帳が読める(ブリーフは BOM を読取不能の例に挙げた) | **NOT CONFIRMED・ブリーフ帰属** — PyYAML の標準挙動。入力規格に BOM 禁止を置く理由がない | 仕様の明確化: BOM は許容(製造物不変) |

- 検査官のその他の観測(受理側で確認・是正なし): 停止の優先順位は job > receipt > independence で一意(三条件同時で `job:LEDGER_INCONSISTENT → ledger-owner`)/ 本ツールの行は最大 80 桁・
  400 桁 executor でも 80 桁 / 別プロセス・別 cwd・pwsh cell から `BOMDD_EXECUTOR=EQ-002` 受領 / **pwsh -Command の exit 2→1 丸め(P5-07)は検査官環境では再現せず**(環境差の記録)/
  後方互換: 配員欄なし fixture の dry は旧新同一・ECO-071 の job は `required_capability=null`・stop NONE 同一 / selftest 被覆表(IA-01〜03 のクラスが未被覆= r1b で腕を追加)。
- 範囲外の観察(環境帰属・是正なし): 検査官 sandbox では `self-conformance.py` の C14 REAL が git `dubious ownership`(別所有者)で 6/7 FAIL — 製造物には帰属しない(設備属性の候補:
  sandbox 内の git 所有者)。検査官が self-conformance を重複起動し残存プロセスを停止できなかった(sandbox 管理)。
- 検査官の報告は自前の較正 receipt(observed・条件付き適格・計器欠陥= selftest に IA-01〜03 の陽性対照なし)と preflight receipt(PROCEED_WITH_LIMITS)を含む(記録のみ・受理側判定は上表)。
- r1b 後の V1: `bomdd-job.py --selftest` exit 0(r1 腕 IA-01/IA-03 追加)・`bomdd-run.py --selftest` exit 0(独立性 9 腕)。実 order の job ビュー: ECO-072 `{producer: EQ-001, inspector: EQ-002}`・
  ECO-071 null(不変)。

### 5.2 r2(2026-09-12・range= 是正確認+回帰・範囲限定)— 報告: [independent-inspection-eco-072-r2.md](reports/independent-inspection-eco-072-r2.md)

- 起動: 入口から実 cell(`--executor EQ-002`・witness tree 23242098fc55= fix commit 2dad24f の作業木)→ `cell exit 0`。報告は再び handoff ヘッダで開始(第三者到達 2 例目)。
- 判定: **ACCEPT**・新規所見なし。IA-01(未選択 entry の list/数値/dict → `job:MISSING_INPUT` 起動なし・null/欠落は許容・選択 entry の null は `AXIS_UNKNOWN:model`)/ IA-02(`M1/'  h1  '/A1` →
  SAME_LINEAGE 起動なし・`m2` なら起動)/ IA-03(コメント内外・他節・見出しなし・同位見出し以降= PRODUCER_UNDECLARED / 直下・下位見出し・英語 equipment 見出し= 採用)= すべて期待どおり。
  回帰: r1 の全腕不変・停止優先順位 job > receipt > independence 不変・別プロセス/別 cwd で `BOMDD_EXECUTOR=EQ-002`・後方互換 dry 旧新同一・3 ツール selftest exit 0・ECO-071 null / ECO-072
  `{producer: EQ-001, inspector: EQ-002}`。BOM 付き台帳は ADVANCE(明確化した仕様どおり)。検査官の較正 receipt: 計器欠陥なし(r1 の対照腕が selftest に入った)。範囲外の観察: なし。

## 6. クローズ(2026-09-12・verified)

- **V1**= PASS(selftest 3 ツール exit 0・§4)/ **V2**= PASS(Phase 7 出口条件の実測 1 例+陽性対照・§4)/ **V3**= PASS(self-conformance 全 PASS・CI run 34637503548〔fix 2dad24f〕success)。
  diff 監査の窓: baseline `58205be` → head `2dad24f`(**窓閉鎖**)。窓内= tools 2・新規 yaml・templates 1・order 2・register・improvements・reports(r1)= allowed_paths のみ。
- **V4**= 異系統独立検査 r1(境界探索・REJECT 3 是正+ブリーフ帰属 1)→ r2(是正確認+回帰・ACCEPT)。range と実行環境の差(workspace-write・別プロセス・pwsh)をブリーフに宣言(ECO-069 の欄)。
- **V5**= 下記 較正 receipt。register: `implemented → verified`・head 凍結。
- **Phase 7 第 1 弾の到達点**: 設備台帳(3 entry・来歴つき)・配員欄を job 射影が解決(F2 解消)・入口が独立性を宣言属性で照合し、成立しない組合せを弾いた(N=1・陽性対照 1・r1/r2 の実 cell 起動 2)。
  §7 Phase 7 の残り= P6-02(cell の判定を receipt として回収)・裁定キュー(保留)・設備属性の harness-measured 化(exit_propagation 2 件が unknown・r1 で pwsh 丸めが非再現= 環境依存)。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格・③: 計器変更〔tools〕)

- 査定した主張と判定:
  1. 「成立しない組合せを機械が弾いた実測 1 例」— **observed / 適格**(実入口・witness 個体照合つき・台帳 `.git/bomdd-run/ECO-072.jsonl` に decision 行・起動痕跡なし。陽性対照= 同 job で EQ-002 は起動)。
  2. 「fail-closed(独立と判定できない限り起動しない)」— **observed / 条件付き適格**(selftest 9 腕+r1 境界探索で 3 クラスの fail-open を検出→是正→r2 で確認。全入力の網羅は主張しない・
     Unicode 正規化は仕様外)。
  3. 「独立性の判定は宣言属性の照合まで」— **宣言**(実効は主張しない・Grok 公式の境界。台帳の来歴は harness-measured が sandbox/temp のみ・他は self-reported/user-declared)。
  4. 「後方互換(配員欄なしの order は従来どおり)」— **observed / 適格**(ECO-071 の job 不変・dry 旧新同一= 検査官 r1/r2 の実測)。
  5. 「配員欄が製品 order で書かれるようになる」— **unknown(未測定・templates 経由の配布は次回 kit 再設置から)**。
- 検出した計器欠陥(帰属つき): 製造物 3 件(IA-01〜03・r1 境界探索が検出・r1b 是正・selftest に対照腕を追加)。受理側 2 件= ①ブリーフが BOM を読取不能の例に挙げた(IA-04・仕様明確化)
  ②記帳スクリプトの anchor 不一致で self-conformance が走らないまま「exit=1」を返した(受理側手順・再適用で解消・製造物無関係)。自己捕捉 1 件(usage 80 桁)。
- 検出力の限界: N=1 の出口実測(組合せ 1 種)。独立性の実効・Unicode 正規化・別 OS・別 YAML 実装は未測定。設備属性の来歴は大半が申告。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 実測 | V2 4 腕・selftest 3 ツール・r1/r2 |
  | Q2 | asked | observed/適格 | 実測 | known-bad= 同一 executor(STOP)/ 陽性対照= 異系統(起動)/ r1 の fail-open 3 例が是正後に STOP |
  | Q3 | asked | observed/適格 | 実測 | 是正前後: r1 起動 → r1b 起動なし(検査官 r2 で確認) |
  | Q4 | asked | observed/適格 | 実測 | 実入口・実 order・実台帳(fixture は selftest と検査官の temp) |
  | Q5 | asked | observed/適格 | 実測 | 未測定(実効・Unicode・配布)を宣言 |
  | Q6 | asked | observed/適格 | 実測 | 検査 exit 観測 → witness → 入口 dry → commit → push → CI(fix・accept とも) |
  | Q7 | asked | observed/適格 | 実測 | 陽性対照あり(EQ-002 起動・r1 の 3 クラス) |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | witness・register・run 台帳(decision/cell 行)・r1/r2 報告 |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」 |
  | Q11 | asked | observed/適格 | 読解 | 入力クラス= 台帳形状/配員欄の所在/表記揺れ/executor 引数/停止優先順位(r1 被覆表) |

- このクローズが支持しないもの: 独立性の実効 / 製品 order での配員欄の記入率 / 偽陽性率(EXP-20260912-02 で製造後 3 ECO)/ P6-02・裁定キュー(Phase 7 の残り)。
