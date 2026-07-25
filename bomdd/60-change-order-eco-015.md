# ECO-015 — kit に工程設備の汎用核が無い(hooks/lifecycle validator/qualification runner を 2 実装から抽出し bomdd-init 標準装備へ)

> 状態: **verified(2026-07-26)**。fix= 933d181・検証 V0〜V8 全 PASS・窓は accept で閉鎖。
> 発端: ViewTube mature-process-bootstrap 還元(FINDINGS §11.5)+ maintainer 裁定
> (2026-07-25 会話 — 「2 実装から共通核を抽出して kit の標準装備にする」切り口で起票)。

## 裁定(gate ① — 2026-07-26)

- **製造承認(2026-07-26・maintainer — 「製造承認します。gate ① を通して製造に入ってください」)**。
  baseline を起票コミット ce6e105(是正開始直前)へ更新。
- 起票時に gate 裁定へ委ねた 2 点は、order 記載の案どおり採択:
  1. **self-conformance は C11 新設**(C4/C5 の拡張でなく — C4 は scaffold の形状検査・C11 は
     工程設備の稼働検査で関心が別)
  2. **CAD リポには process-core を設置しない**(CAD は製造リポでない — 裁定台帳のみ。
     ECO-010 の AGENTS.cad と同じ「内容の非対称は正直記録」)
- 追加裁定(製造中の設計確定 — スキル整合の実測に基づく):
  3. **既定プロファイルの状態語彙は `[staged, applied]`**(2 状態)。根拠= kit 同梱スキルの
     実挙動(eco-file が `status: staged`・eco-accept が `status: applied`・eco-fix は状態を
     変えない)。3 状態(staged→implemented→applied= ViewTube AC-PORT-003)は profile 設定で
     有効化できる(fix trailer 強制は 3 状態時のみ発火 — E04 の機械は validator selftest が
     合成 3 状態 profile で常時検査)。スキルテンプレの語彙改訂は本 ECO の allowed_paths 外 —
     手を出さない(観測として記録: templates/60-change-register.yaml のコメント語彙
     〔proposed→…→verified〕とスキル実挙動〔staged→applied〕の不一致は既存債務)
  4. **テンプレ placeholder エントリ(title が `<` で始まる)は検査対象外**として skip
     (scaffold 直後の台帳が placeholder で FAIL しないため — skip は警告表示で正直記録)
  5. **validator 不在+profile 存在時の pre-commit は全 commit 遮断**(保護パス限定でなく)。
     profile の存在が「本リポは process-core 管理下」の宣言であり、設備喪失は停止が正
     (fail-closed)。profile ごと撤去すれば無効化できる(脱出経路の明示)

## 起票(2026-07-25)

- 出典: **FINDINGS §11.5(転移の対照観測)+ improvements.md 2026-07-25 節**。bomdd-init は
  方法論(kit+lock)・入口(AGENTS.md)・スキル(③)を設置するが、**④の工程設備
  (hooks・lifecycle validator)と適格性確認装置を同梱しない**。新規プロジェクトは
  「起票なしに保護パスへ入らない」「状態遷移は履歴証拠と対」が②散文+③skill 止まりのまま
  製造に入れる — ECO-060 の遵守逆転実測(③は自然文で無音バイパスされる・FINDINGS §11.3)
  から、これは実測済みの無音面である。
- 実装の材料は既に 2 つ存在する(rule of two — 起票の根拠):
  1. **ViewPrism2**: bomdd/hooks(pre-commit/commit-msg)+ validate E14〜E19
     (lifecycle trailer・状態遷移・履歴証拠の fail-closed 検査。ECO-061 で変異 5 種収載)
  2. **ViewTube**: PR-HOOKS / PR-LIFECYCLE-VALIDATOR(上記の adapt 品 — reuse map に差分が
     明示記録済み)+ **process qualification runner**(IQ/OQ/PQ 機械実行・負例 16 種・
     byte-identical 決定性を実証)
  両者の差分は保護パス・register スキーマ・trailer 規約・製品語彙 — **config で注入可能な
  部分に限られる**(capture harness のような製品依存設備は差分が構造的で対象外)。
- 方法論上の位置づけ: onboarding pack §11 / playbook §1 の line readiness 3 点(入口到達・
  validator 稼働・hook 有効化)を、派生開発だけでなく **greenfield でも bomdd-init 直後から
  成立**させる。ECO-004(kit= 方法論の凍結配布)の続編 — kit は方法論を運ぶ装置だったが、
  本 ECO で最小の工程設備も運ぶ。OBS-20260725-01(工程様式の完全標準化・watch 1/3)の
  先行実装ではなく**部分集合**: 設備 3 点のみ昇格し、完全様式(process donor intake /
  reuse map / process BOM の標準成果物化)は watch 継続。

## 是正方針案(製造前・凍結前の草案)

1. **汎用核の抽出**(`method/templates/process-core/` 新設・kit 経由で凍結配布):
   - pre-commit hook: 保護パス(既定 `src/` `test/`)の変更に ECO 起票を要求。
     validator 不在時は保護パス commit を**ブロック**(fail-closed — ViewTube AC-PORT-008 と同じ)
   - commit-msg hook: lifecycle trailer(`BomDD-ECO-Fix` / `BomDD-ECO-Accept`)の強制
   - lifecycle validator: register の状態遷移(staged→implemented→applied 相当)+
     履歴証拠(trailer・commit 実在・祖先関係)を状態不変条件として検査+ self-test
2. **config 注入方式**: `bomdd/process-profile.yaml`(保護パス・register 位置・trailer 名・
   状態語彙)。2 実装の差分にあたる部分だけを設定化し、不変条件はコードに固定する
   (adapt を自由な再設計にしない — reuse map の規律を装置側で担保)
3. **qualification runner 同梱**: IQ(`core.hooksPath` 解決・hook 起動実測・validator
   self-test)+ OQ(事前登録負例の汎用サブセット: ①ECO なし保護パス変更 ②新規 entry を
   implemented で登録 ③遷移飛び越し ④fix/accept trailer 欠落 ⑤hook 無効 ⑥自然文承認の
   証拠登録)。全負例が登録理由で拒否されなければ FAIL
4. **bomdd-init 統合**: scaffold 時に process-core を設置し(`core.hooksPath` 設定込み)、
   初回 IQ/OQ を自動実行して line readiness を報告。不合格なら製造開始を案内しない
   (--skills-only 経路は既存リポの hook を保持 — ECO-004 の fail-safe と同じ)
5. **self-conformance 収載**: 生成 scaffold 上で負例が止まることの検査(C4/C5 の拡張または
   C11 新設 — gate で裁定)

## 受入基準(事前登録 — 製造前に凍結する)

- 陽性対照: 合成の正常 ECO が staged→implemented→applied を trailer つきで通過する
- 負例: 上記 OQ 6 種が各々**登録理由で**拒否される(想定外の通過 1 件で FAIL)
- 決定性: 同一入力で qualification 2 回実行の判定・理由集合が一致
- 回帰: 既存 scaffold 生成物(ECO-004/009/010 の検証項目)が不変・self-conformance 全 PASS
- 対応表: 汎用核の各不変条件 ↔ ViewPrism2 実装(E14〜E19)↔ ViewTube 実装(negative
  controls 1〜8/14)の対応を order に記録(取りこぼした不変条件を明示する — 黙って省略しない)

## 影響分析(製造前予測 — 未凍結)

- 影響なし予測: `method/tools/bomdd-init.py`・`method/templates/process-core/`(新設)・
  `method/tools/self-conformance.py` 以外 diff ゼロ。既存製品リポへは非波及(init は生成時のみ・
  --skills-only は既存 hook 保持)。正常系 scaffold の既存生成物は不変 — 追加は process-core
  一式+process-profile.yaml+git config。kit manifest(bomdd.lock)は process-core 分だけ
  件数・hash が変わる(設計どおりの来歴変化)
- ECO-009 §16(d) 教訓の適用: CAD リポ経路(--gui)と --skills-only 経路の生成差を起票時点
  から影響範囲に含む(CAD リポは製造リポでないため process-core を設置しない案 — gate で裁定)

## スコープ外(明示)

- capture harness 等の**製品依存設備**(UI-CAD 成立後に各リポが建てる — line readiness に含めない)
- process donor intake / reuse map / process BOM の**様式標準化**(OBS-20260725-01・2 例目待ち)
- 既存リポ(ViewPrism2/ViewTube)の汎用核への**置換**(動いている④を触らない — 対応表で
  同等性のみ記録)

## 是正(2026-07-26・fix= 933d181)

1. **`method/templates/process-core/` 新設**: process-profile.yaml(config 注入面)+
   hooks/pre-commit・commit-msg(sh・fail-closed・python は「PyYAML を import できる個体」を
   実行検査で選定 — Windows ストアスタブ/yaml なし python を弾く)+
   tools/process-validator.py(E01〜E07・selftest 23 項目内蔵・trailer 解釈は
   parse_trailers() 単一実装= commit-msg 検査と履歴証拠検査が共有〔ECO-078 教訓〕)+
   tools/process-qualification.py(IQ 6 項目+OQ sandbox 7 対照+決定性 --runs)
2. **E07 追加(製造中の裁定)**: 対応表作成時に ViewPrism2 E18(trailer 参照先の台帳実在)の
   取りこぼしを検出 → 数行で移植可能と判断し追加(E17 の順序検査は既定 2 状態で発火し得ない
   ため見送り — 対応表に正直記載)
3. **bomdd-init 統合**: install_process_core(既存 hooks/profile は保持= fail-safe・
   register 不在なら台帳テンプレ追設〔--skills-only の既存リポで IQ-06 FAIL を実測して追加〕)+
   git init 直後・初回 commit 前に core.hooksPath 設定(hook は commit #1 から有効)+
   初回 IQ/OQ 自動実行(不合格なら exit 1・製造開始を案内しない)+ --no-qualify。
   CAD リポは非設置(裁定 2)。既存 git() の encoding 未指定(cp932)が hook の UTF-8 出力で
   落ちる潜在欠陥を検出し是正(utf-8/replace)
4. **self-conformance C11 新設**: scaffold 上で IQ/OQ PASS+初回 commit hook 有効+
   変異(hooksPath 無効化)の IQ-03 検出

## 検証(2026-07-26・受入基準=起票時凍結分)

- **V0(selftest)**: validator 純関数 23 項目全 PASS(E01〜E07 各変異+陽性対照+placeholder
  skip+厳格ローダー対照+trailer 解釈対照)
- **V1(陽性対照)**: OQ POS — 合成 ECO が起票→保護パス変更→accept trailer→validate を通過
- **V2(負例)**: OQ N1〜N6 全て登録理由で拒否(E01/E02/E03/E05/E06/IQ-03。E04 は既定 2 状態で
  遷移が存在しないため selftest が合成 3 状態 profile で被覆 — 裁定 3 の設計どおり)。
  N6 は検出だけでなく「hook 無効時に違反 commit が素通りする」バイパスの実在も観測
- **V3(決定性)**: スイート 2 回実行の判定・理由集合一致(DET PASS・既定 --runs 2)
- **V4(実リポ直接プローブ)**: 生成リポの実 commit 経路で①ECO なし src/ 変更→ E01 遮断
  ②validator 退避→全 commit 遮断(裁定 5 の fail-closed)を実測・復元済み
- **V5(--skills-only)**: 既存 git リポへの追設で line ready PASS(register 追設込み)。
  再実行で既存保持(fail-safe)を確認
- **V6(CAD 経路)**: --gui の CAD リポに process-core 非設置・製品リポに設置を確認(裁定 2)
- **V7(回帰)**: self-conformance 全 PASS(C1〜C8/C10/C11 — C4 scaffold 形状・ECO-004/009/010
  検証項目とも不変)。所要 +C11 で全体 26s
- **V8(製造中に検出・是正した欠陥 — 正直記載)**: (a) OQ POS 判定の `or not list.append`
  恒真バグ(セルフレビューで検出)(b) hook の python 選定が PyYAML なし個体を掴み全 commit
  誤遮断(初回 end-to-end で fail-closed が正しく発火して検出)(c) bomdd-init git() の
  cp932 デコード落ち(同)— いずれも是正後に全経路再実測

## 不変条件対応表(受入基準 5 — 取りこぼしの明示)

| process-core | ViewPrism2(validate_bom E14〜E19) | ViewTube(AC-PORT-011 負例) | 備考 |
|---|---|---|---|
| E01 | (hook 相当) | 1・2(ECO なし保護パス変更) | ✓ |
| E02 | E19(非 staged 登場) | 3(新規 implemented 登録) | ✓ |
| E03 | E19(飛び越し・逆行) | 4(staged→applied skip) | ✓+削除・terminal・未知状態 |
| E04 | E15(前提) | 5(fix trailer 欠落) | 3 状態 profile 時のみ発火 |
| E05 | E16(前提) | 6(accept trailer 欠落) | ✓ |
| E06 | E15/E16(履歴実在) | 13(自然文了承の承認登録) | 既定 2 状態は accept 証拠のみ・3 状態で fix も要求 |
| E07 | E18(参照先実在) | — | 製造中に移植 |
| IQ-03 | — | 14(hook 無効) | +N6 でバイパス実在を観測 |
| **未移植** | E14(lifecycle_evidence 宣言・shallow 検査)・E17(fix→accept の祖先順序・逆行乖離) | 7(ECO body)・8(impacted files)・9〜11(視覚 golden)・12(役割分離)・15(hash)・16(known-bad) | E17 は既定 2 状態で発火不能のため見送り。7・8 は台帳スキーマ依存、9〜12・15・16 はスコープ外宣言どおり(製品依存設備・様式標準化は OBS-20260725-01 watch) |

## 教訓(還元候補 — lesson-promote 経由)

- **設備の受入検査は設備の操作対象(台帳)込みで通す** — --skills-only の IQ-06 FAIL は
  「設備はあるが操作対象が無い」構成を機械が正しく検出した例。設置 = 装置+操作対象+結線。
- **fail-closed は開発中の自分に最初に牙をむく(そしてそれが価値)** — hook の python 選定
  欠陥は、fail-closed 設計だったから初回実行で顕在化した(fail-open なら無音で素通りし
  「動いている」と誤認したまま出荷された)。

## 効果測定(宿題)

- EXP-20260725-03 の greenfield 版: 次の新規プロジェクトで line readiness が bomdd-init 直後
  から成立するか(工程 greenfield 化の再発ゼロ・「BomDD を採用して開発して」型の自由文開始でも
  ④が保護パスを塞いでいるか)
