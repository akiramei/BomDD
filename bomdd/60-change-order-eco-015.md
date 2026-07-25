# ECO-015 — kit に工程設備の汎用核が無い(hooks/lifecycle validator/qualification runner を 2 実装から抽出し bomdd-init 標準装備へ)

> 状態: **implemented(2026-07-26)**。gate ①(製造承認)通過 → 製造中。
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

## 効果測定(宿題)

- EXP-20260725-03 の greenfield 版: 次の新規プロジェクトで line readiness が bomdd-init 直後
  から成立するか(工程 greenfield 化の再発ゼロ・「BomDD を採用して開発して」型の自由文開始でも
  ④が保護パスを塞いでいるか)
