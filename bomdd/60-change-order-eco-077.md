# Change Order — ECO-077(役割 → 使用可能スキル集合の結線: activation-map の roles 軸・工場/検査官ブリーフの役割欄・register の receipt_author_role〔観測欄〕)

> 裁定: user 2026-09-14 DISCUSS(役割層の議論)に AGREE+補足 2 点 → DECIDE「A」(今 ECO を起票して製造に入る)。
> 凍結された最小形= 3 点(activation-map に role 軸 / ブリーフに role・allowed・observable forbidden / register に receipt author role)。
> **採らない**(user 裁定): persona プロンプト / 新しい Role・Process の YAML スキーマ / 役割の機械強制 / receipt_author_role の gate 化(自己較正と独立較正の差が実測されてから昇格を判断)。
> 記帳の正本= [improvements.md 2026-09-14 役割層の節+OBS-20260914-02](../method/improvements.md)。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**。
- producer: EQ-001
- inspector: EQ-002
- 検査官(独立検査併用時): gpt-5.6-sol @ Codex CLI(入口 `bomdd-run --executor EQ-002 --report … --range …` から起動・round の range と実行環境の差は各ブリーフに宣言。
  本 ECO の検査官ブリーフは §1-2 の役割欄を**自分に適用した最初の個体**)。

## 0. 実測(起票根拠)

- **部品は揃っている**(2026-09-14 突合): 「誰が」= 設備台帳 [70-equipment.yaml](70-equipment.yaml)+order 配員欄 producer/inspector / 「責任・見てよいもの」= playbook §9 表 /
  「決めてよい」= verified 昇格の inspection gate(ECO-074)・工場の commit 禁止 / 「観測可能な禁止」= allowed_paths 窓・diff 窓・witness / 「役割遷移と情報遮断」= 異系統設備・read-only・
  ブリーフ非開示 / 「役割パッケージ」= factory-delegate の工場ブリーフと検査官ブリーフ(ad hoc な 2 実例)。
- **欠落は 1 本**: [activation-map.yaml](../method/templates/product-profile/skills/activation-map.yaml) は ECO のクラス(状況)→ required_skills で、役割の軸がない。
  サブエージェント・工場・検査官へ「その役割で読む手順書」を渡す入力が台帳から導出できない。
- **同一実行主体の帽子替えが register 上で見えない**: 較正 receipt は製造者自身が書いて verified へ昇格している(ECO-076 は製造者較正のみ・独立検査なし)。playbook §9 は自己査定を
  「順守の記録であって弁別力の証明ではない」と注記するが、register に「誰の役割が書いたか」の欄がなく、自己較正と独立較正を機械的に弁別できない。
- **user 補足 2(2026-09-14)**: 「同じ review でも役割で評価関数が違う」は round の range と REJECT 意味論で実装済み、という当方の主張は強すぎる — それらは「何を検査する工程か」を
  定めるが「その役割として何を見るか」は定めない。role × review-purpose の軸は未定義のまま残す(本 ECO の範囲外・OBS-20260914-02 に記名)。

## 1. 変更要求(凍結・user 裁定 A)

1. **activation-map v1.2 — `roles` 軸**: 各 class に `roles: [producer | inspector]`(その class の receipt を書く役割の集合・語彙= 配員欄と同じ 2 語)。
   start / design-synthesis / instrument-change= `[producer]`・verified-promotion= `[producer, inspector]`(較正 receipt は自己較正でも独立較正でも書ける)。
   `bomdd-job.py`: `ROLE_VOCAB`・validate_map が roles の欠落/空/語彙外/重複/非配列を MAP_INVALID(fail-closed)・project が `required_skills_by_role`(該当 class の required_skills を
   roles ごとに集合化・**情報欄**・停止語彙不変・gate 化しない)を導出。既存の `required_skills`(和集合)は不変。
2. **ブリーフの役割欄**(`factory-delegate.md` 正本+`.claude/skills/factory-delegate/SKILL.md` 写し): 工程 1 の工場ブリーフに `役割: producer` / 使う手順書(役割パッケージ)/
   観測可能な禁止(触るパス・commit 0・台帳と受入節に diff 0・受入判定を書かない)。工程 5 に検査官ブリーフの役割欄(`役割: inspector` / 責任・手順書 / 観測可能な禁止= 製品と台帳への diff 0・
   commit 0・受入節と register の非接触)。**禁止は観測可能な項目のみ**(playbook §8.5)。
3. **register の `receipt_author_role`**(任意・観測欄): verified 時に「受入時の較正 receipt を書いた役割」(producer / inspector / human)を記す。テンプレ
   [60-change-register.yaml](../method/templates/60-change-register.yaml) にコメントで宣言・`bomdd-job.py` が同名欄をそのまま射影(欄なし= null・停止しない・文字列以外は null)。
   **gate にしない**(C 検査・入口の停止語彙・witness いずれにも入れない)。本 ECO 自身の verified 行が最初の個体。
4. **selftest 腕**(bomdd-job): roles 必須キー / by_role 陽性(verified+hard-positive+instrument → producer= calibrate・converge・preflight / inspector= calibrate)・陰性(decided → producer= preflight)/
   map 不在= unknown / receipt_author_role の射影(文字列のみ・欄なし null・有無で stop_type と required が不変= gate 化していない)/ roles 欠落・空・語彙外・重複・非配列・大文字= MAP_INVALID・語彙内= 通過。
5. **記帳**: improvements.md 節+EXP-20260914-03(receipt_author_role の分布と、producer-only で verified になった ECO で後に欠陥が検出された回数= 自己較正と独立較正の差)。

## 2. 影響なし予測(製造前・凍結)

diff= tools 1(bomdd-job)+templates 3(activation-map・factory-delegate 正本・60-change-register テンプレ)+写し 1+improvements.md+台帳系(order・register)。
bomdd-run・bomdd-witness・self-conformance・hooks・.github は diff 0(job JSON は additive に 2 欄増えるだけ— run/witness の selftest は不変で PASS)。既存 ECO の job ビューは
`required_skills` 不変・`receipt_author_role` null・`required_skills_by_role` が増える。activation-map の既存 4 class の required_skills・anchor・source は不変。写しの diff= 既知 2 hunk のみ。
C7 13 本不変(skills/ の .md 本数不変)。worklist 新規 ID 1(EXP-20260914-03)・警告 0。

## 3. 受入

- **V1** selftest: bomdd-job(F7 腕)・bomdd-run・bomdd-witness すべて PASS。**known-bad(実測)**: 実 map の 1 class から roles を外すと job selftest が FAIL(復元後 PASS)。
- **V2** 射影: 既存 ECO(ECO-076)の job ビューで `required_skills` 不変・`required_skills_by_role` が導出され・`receipt_author_role` が null。本 ECO の verified 行で `producer` が射影される。
- **V3** 文書: 正本の工程 1 に役割欄・工程 5 に検査官の役割欄(grep)/ 写しの diff= 既知 2 hunk・`{{METHOD}}` 未解決 0 / テンプレに `receipt_author_role` のコメント。
- **V4** self-conformance 全 PASS(exit 0 観測後に commit)・CI 緑・窓= allowed_paths のみ。
- **V5** 異系統独立検査(EQ-002・range つき・検査官ブリーフに §1-2 の役割欄を適用)。**V6** 較正 receipt(著者役割を register に記す)。

## /preflight receipt(起動経路: **自発** — 新規起票・register 追記前に判定)

- 分類= 既裁定の適用実装(user DECIDE A・最小形 3 点は凍結済み)。baseline `940e757`= **confirmed**(git log -1)/ 次番 077 未使用= **confirmed**(bomdd/ に ECO-077 なし・playbook の
  「ECO-077」は製品 ECO の言及)/ activation-map に roles なし= **confirmed**(実読)/ register に受入役割の欄なし= **confirmed**(テンプレ+実台帳の実読)/ bomdd-job が map を
  validate し selftest を持つ= **confirmed**(実読)/ 同一ファイルへの進行中 ECO なし(ECO-076 は verified)= **confirmed**。
- 開始判定: **PROCEED**・override 0。

## /converge receipt(起動経路: handoff DISCUSS → user AGREE+補足 → DECIDE A — 設計は user と収束させてから起票)

- **判定: 収束**(round 軌跡: DISCUSS 1 周= thesis 提示 → user 補足 2 点で thesis の 1 主張を取り下げ〔review(role,…) 実装済み → 未定義〕→ 最小形 3 点で合意 → DECIDE で開始時期のみ裁定。新規指摘 2 → 0)。
- 検証した主張: ①activation-map に役割軸がない(実読)②工場・検査官ブリーフは役割パッケージの ad hoc 実例(factory-delegate 実読)③受入役割の欄が register にない(実読)④禁止を観測可能な
  項目に限る根拠= playbook §8.5「委任の制約は遵守検査手段の被覆内にのみ」(実読)。
- DoD: ✔ 3 点が凍結 ✔ 採らないものが明記 ✔ gate 化しない条件が明記(昇格の判断基準= 自己較正と独立較正の差の実測)✔ 効果の計測先(EXP-20260914-03)。
- 未収束事項: role × review-purpose の軸(user 補足 2)— 本 ECO の範囲外として OBS-20260914-02 に記名。roles の語彙を 2 語に固定した点は配員欄の語彙に従った結果であり、
  較正者・変更管理者を独立の役割語にするかは実害の実測後。

## 4. 製造と受入の実測(2026-09-14)

- 製造物: `bomdd-job.py`(F7: ROLE_VOCAB・validate_map の roles 検査・project の by_role と receipt_author_role・selftest 腕・PASS 文言)/ `activation-map.yaml` v1.2(roles 4 class+規約)/
  `factory-delegate.md` 正本(工程 1 役割欄・由来・工程 5 検査官役割欄)/ 写し(正本から再生成)/ `60-change-register.yaml` テンプレ(コメント 2 行)/ improvements.md 節+EXP。
- **V1**= §4.1 に実測を記す。**V2**= §4.1。**V3**= §4.1。**V4**= §6(観測後)。**V5**= §5。**V6**= §6。

### 4.1 実測(製造者・commit 前)

- selftest: bomdd-job PASS(F7 腕込み)・bomdd-run PASS・bomdd-witness PASS(exit 0 観測)。
- known-bad(実測): 実 map の `start` から `roles` 行を外す → `bomdd-job selftest FAILED: F1: 実 activation-map が読めない: activation-map 不正(MAP_INVALID): class 'start': roles が非空の文字列配列でない`
  (exit 1)→ 復元後 PASS(exit 0)。欠落は無言の「全役割」にならず fail-closed。
- 射影(ECO-076・実測): `required_skills ["calibrate","preflight"]`(不変)/ `required_skills_by_role {"inspector":["calibrate"],"producer":["calibrate","preflight"]}` /
  `receipt_author_role null`(source= register の同名欄・欄なし)/ `stop_type NONE`(不変)。
- 文書 grep・写し diff: 写しの diff= 既知 2 hunk(8c8,12・10c14)・`{{METHOD}}` 0(実測)。

## 5. 独立検査(異系統・Codex EQ-002・入口 bomdd-run から `--report`/`--range` つきで起動・検査官ブリーフに §1-2 の役割欄を適用した最初の個体)

### 5.1 r1(2026-09-14・range= 境界探索)— 報告: [independent-inspection-eco-077.md](reports/independent-inspection-eco-077.md)

- 起動: fix commit 5917e29(witness tree cda1e4dd7c8f・入口 dry ADVANCE)→ `cell exit 0` → `report ACCEPT sha256:50eb8901cb1e (EQ-002)`・台帳 `range: 境界探索`・
  verdict_line `ACCEPT — ECO-077 V1〜V3 に適合。製造物に帰属する所見なし。`。**本節の判定は台帳の verdict から転記**。
- 判定: **ACCEPT・所見 0**(境界探索のため受入根拠にしない= r2 へ)。検査官の観測: ①selftest 3 本 PASS・known-bad(temp map の roles 欠落 → MAP_INVALID)②validate_map の境界 10 入力
  (dict / 数値 / 空文字 / 前後空白 / 大文字 / null / 語彙外 3 語目 / 重複 → 全て問題として列挙・traceback 0・語彙内 2 語は順不同で通過)③project: 複数 role の同一 skill は重複なく辞書順・
  class 反転で不変・map 不在= null+unknown・receipt_author_role は文字列以外 null(空文字・語彙外文字列は透過= 観測欄仕様と一致・所見にしない)・有無で stop/required/missing 不変
  ④回帰: 旧版 940e757 との全 register 77 件比較で required_skills 差分 0・新欄欠落 0 ⑤文書: 写し diff= 2 hunk・`{{METHOD}}` 0・観測不能な禁止の混入なし・テンプレ YAML パース可・scaffold 生成可
  ⑥ROLE_VOCAB= ASSIGN_RE・停止語彙不変・run/witness は baseline と差分なし。
- 役割欄の適用(実測): 検査官は `git status --short` を開始時・終了時に貼り(diff 0)・commit 0・製品修理なし。役割外の作業は発生せず。
- 測定不能(環境帰属・検査官が分離): sandbox から `.git/bomdd-run/` に書けず `bomdd-run ECO-076`(dry)の既定実行は ARG_ERROR → 検査官は対象 revision を `git bundle` で OS temp に複製し
  同 tree の witness で ADVANCE を代替測定(additive な job 欄で入口が壊れないことを確認)。
- 検査官の較正 receipt: V1〜V3 PASS・計器欠陥 0(環境 2 件を分離)・限界= V4〜V6・CI・POSIX・並行・網羅 fuzz は未測定。

### 5.2 r2(2026-09-14・range= 是正確認+回帰・範囲限定 7 項目)— 報告: [independent-inspection-eco-077-r2.md](reports/independent-inspection-eco-077-r2.md)

- **1 回目(受理側で不受理・証拠不足)**: 台帳 `report ACCEPT sha256:8490a7b3527b`・verdict_line `ACCEPT — 指定7項目はすべて r1 と一致しました。是正対象は0件です。`。しかし保存された報告は
  9 行の要約のみ(項目別の再現コマンド・観測・`git status` 出力・較正 receipt が無く、自分自身のパスへのリンクを含む)。機序= 検査官が報告全文を同じパスへ自分で書き、CLI の `-o` が最終メッセージ
  (要約)で上書きした。帰属= **ブリーフ**(「最終報告は `-o` で保存される」の一文が「報告ファイルを自分で書く」と両立して読めた)。処置= verdict は台帳に残るが受入根拠にせず(証拠が主張を
  証明していない・calibrate の証拠品質)、要約ファイルは scratchpad へ退避してリポから外し、ブリーフに「報告ファイルを自分で書かない・最終メッセージに全文」を追記して再実施。
- **2 回目**: 〔実測後に記す〕
- **2 回目(受理)**: witness 再生成(tree= order §5.1 追記後)→ 入口 ADVANCE → `cell exit 0` → `report ACCEPT sha256:d11b21e091a4 (EQ-002)`・台帳 `range: 是正確認+回帰`・verdict_line
  `ACCEPT — 指定 7 項目はすべて同一 revision の r1 と一致。是正対象は 0 件、製造物帰属の新規所見は 0 件。`。**本節の判定は台帳の verdict から転記**。報告は 402 行(項目 1〜7 の再現コマンド・
  観測・`git status` 開始/終了・検査官の preflight/較正 receipt)・検査官の報告ファイル書込み 0(最終メッセージを CLI が保存)。
- 判定: **ACCEPT**(是正 0・回帰 7/7 一致: selftest 3 本 F7 込み / known-bad MAP_INVALID / ECO-076 射影 4 欄 / 旧版 940e757 との 77 件比較 差分 0・新欄欠落 0〔検査官は `--all` が 1 件しか返さない
  ことを観測し全 ID 個別投入へ切替= 範囲外の観察として §6 に記録〕/ 写し diff 2 hunk・`{{METHOD}}` 0 / テンプレ YAML 可・コメント行実在 / HEAD= 5917e29・製造物 diff 0)。
  検査官の較正 receipt: 条件付き適格(7 項目の一致に限る)・計器欠陥 0(ハーネス側の完了情報欠落 1・`--all` の選択仕様 1 を分離)。

## 6. クローズ(2026-09-15・verified)

- **V1**= PASS(§4.1 selftest 3 本・known-bad 実測。検査官 r1/r2 で再現)/ **V2**= PASS(§4.1 ECO-076 射影・検査官 r1 の 77 件比較・本 ECO の verified 行= `receipt_author_role: producer` が最初の個体)/
  **V3**= PASS(§4.1 写し diff 2 hunk・`{{METHOD}}` 0・検査官 r1 で観測不能な禁止の混入なし・テンプレ YAML・scaffold 生成可)。
- **V4**= PASS(self-conformance: 製造 commit 前 2 回 全 PASS〔exit 0 観測後に witness cda1e4dd7c8f → 入口 dry ADVANCE → fix commit 5917e29〕→ push → CI run 34856772714 **success**。
  受入 commit 前に再度 全 PASS を観測してから commit)。diff 監査の窓: baseline `940e757` → head `5917e29`(**窓閉鎖**・受入 commit は台帳系+reports のみ)。窓内= allowed_paths のみ。
- **V5**= 異系統独立検査 r1(境界探索・ACCEPT 所見 0)→ r2 1 回目(証拠不足で不受理・§5.2)→ r2 2 回目(是正確認+回帰・ACCEPT 7/7)。verified 昇格は入口の inspection gate(r2 2 回目の台帳から導出・
  ECO-074 の運用)を通した。**役割欄を適用した検査官ブリーフの最初の 3 個体**: 検査官は 3 round とも diff 0・commit 0・製品修理 0・役割外作業 0(自己申告+`git status` 出力+受理側の status 確認)。
- **V6**= 下記 較正 receipt。著者役割= **producer**(製造者の自己較正。独立検査官は r1/r2 で自分の較正 receipt を書いたが、verified 昇格の receipt は本節= 製造者)。register: `implemented → verified`・
  head 凍結・`receipt_author_role: producer`。
- **範囲外の観察(検査官 r2)**: `bomdd-job.py --all --json` は「verified 以外の全 ECO」を返す仕様(header の usage どおり)で、検査官の期待した「全 ECO」と異なった。仕様どおりであり所見にしないが、
  全件回帰の計器として使うときは ID 個別投入が要る(記録のみ)。
- **受理側の手順欠陥(記録)**: r2 1 回目の報告上書き(§5.2)。帰属= ブリーフ文言。是正= ブリーフに「報告ファイルを自分で書かない・最終メッセージに全文」(本 ECO 内で是正・factory-delegate 正本の
  工程 5 には**入れない** — Codex CLI `-o` 固有の挙動であり、正本は環境非依存に保つ。次回同型が出たら adapter 相当の記述先を判断)。
- **到達点**: 役割 → 使用可能スキル集合の結線が台帳から導出可能(job ビュー `required_skills_by_role`)・ブリーフに役割欄(観測可能な禁止のみ)・register に受入 receipt の著者役割(観測欄)。
  効果は EXP-20260914-03(自己較正と独立較正の差)で測る。role × review-purpose の軸は OBS-20260914-02 に残置。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格・著者役割= producer)

- 査定した主張と判定:
  1. 「activation-map の roles 欠落・語彙外・重複は MAP_INVALID(fail-closed)」— **observed / 適格**(selftest F7 腕・製造者 known-bad・検査官 r1 の 10 入力・r2 の再現)。
  2. 「required_skills_by_role は情報欄で gate 化していない・既存 ECO の required_skills は不変」— **observed / 適格**(有無で stop/required/missing 不変= selftest+検査官・旧版 77 件比較 差分 0・
     停止語彙不変・run/witness diff 0)。
  3. 「receipt_author_role は register の同名欄をそのまま射影し停止しない」— **observed / 適格**(欄なし null・文字列以外 null・本 ECO の verified 行で `producer`)。ただし**空文字・語彙外の文字列は
     透過する**(仕様: 観測欄に語彙検査を置かない)— 検査官 r1 が所見にしないと判定・受理側も同意。
  4. 「ブリーフの役割欄の禁止は観測可能な項目のみ」— **observed / 適格**(検査官 r1: 観測不能な禁止の混入なし。実適用 3 個体で diff 0・commit 0)。
  5. 「役割欄は検査官の越権を抑える」— **unknown(未測定)**: 3 個体とも越権 0 だが、役割欄なしの対照(ECO-072〜075 の検査官も越権 0)と差がなく、効果は弁別できない。EXP-20260914-03 は
     receipt 著者役割の差を測るもので、ブリーフ役割欄の効果は測らない(計測欄なし・実害 1 件が出てから)。
- 検出した計器欠陥(帰属つき): 製造物 0 件。受理側 2 件= ①r2 1 回目の報告上書き(ブリーフ文言・本 ECO 内で是正)②`--all` の対象範囲を検査官が「全 ECO」と読んだ(usage どおり・記録のみ)。
- 検出力の限界: 検査官 1 系統(Codex)・POSIX 未測定・並行実行未測定・receipt_author_role の分布は N=1(本 ECO)・ブリーフ役割欄の効果は対照なし・製品リポでの適用(bomdd-init 配布後)は未測定。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 実測 | selftest・known-bad・射影・77 件比較・写し diff(V1〜V3) |
  | Q2 | asked | observed/適格 | 実測 | known-good= 実 map PASS / known-bad= roles 欠落 → MAP_INVALID(製造者+検査官 r1/r2 の 3 回) |
  | Q3 | asked | observed/適格 | 実測 | 変更前(roles なし・by_role なし・receipt 欄なし)→ 変更後(4 class roles・by_role 導出・欄射影) |
  | Q4 | asked | observed/適格 | 実測 | 実 map・実 register・OS temp の複製で load_map に接続(検査官) |
  | Q5 | asked | observed/適格 | 実測 | 未測定(主張 5・POSIX・並行・製品リポ)を宣言。r2 1 回目の ACCEPT は証拠不足として不採用 |
  | Q6 | asked | observed/適格 | 実測 | 検査 exit 観測 → witness → 入口 dry → commit → push → CI success(fix)。受入も同順 |
  | Q7 | asked | observed/適格 | 実測 | 陽性対照= roles 欠落 known-bad(製造者 1・検査官 2) |
  | Q8 | NA | — | — | 免除機構なし(receipt_author_role は gate でないため免除も存在しない) |
  | Q9 | asked | observed/適格 | 実測 | witness(ECO-077.json)・run 台帳(ECO-077.jsonl・cell 行 3)・report sha256 2 本・fix commit 5917e29 |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」 |
  | Q11 | asked | observed/適格 | 読解 | 入力クラス= map 形状 / 射影 / 回帰 / 文書 / テンプレ / revision の 6 類(検査官 r2 の 7 項目と対応) |

- このクローズが支持しないもの: ブリーフ役割欄の越権抑止効果(対照なし)/ receipt_author_role の差の実測(EXP-20260914-03・N=1)/ role × review-purpose の軸 / 製品リポでの配布結果 /
  受理側の手順欠陥(報告上書き)の再発防止の機構化(記録のみ)。
