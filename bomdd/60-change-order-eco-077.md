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
