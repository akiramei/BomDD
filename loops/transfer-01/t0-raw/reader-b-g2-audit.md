# T0 読者B(G2型監査)raw 出力

> 実施 2026-07-08。fresh サブエージェント(general-purpose)。kit のみ参照・事前知識使用禁止の制約下。以下は読者の最終出力の逐語保存(§1 手順抽出表は突合に使用済みのため要旨、§2〜§4 は逐語)。

## 1. 実行手順の抽出(要旨)

Phase 0〜7+横断ゲート(PLM Gate)を抽出。読者Aとの主な抽出差分:
- 読者Bは「横断ゲート — PLM Gate / PLM 同期」を独立の行として立て、「判定方法は kit からは不明(実行不能)」と明記
- G0 について「チャーターテンプレの Gate 表には別に G0 Intake と PLM Gate があるが判定手段は kit からは不明」と併記
- Phase 6 のゲートについて「example-session-log.md L213 は『G4 充足=納品』と呼ぶが G4 は他のどの文書でも未定義」を検出(読者Aは未検出)
- G2 の判定を「AI 実行+人間判断」、G2' を「人間判断」と分類(Aと一致)

## 2. 一意に読めない箇所の全件列挙(逐語)

| # | 該当ファイル・箇所 | 何が決まらないか | 分類 |
|---|---|---|---|
| 2-1 | `templates/00-charter.md` L53–68 / `templates/40-work-order.md` L7,L17 / `templates/README.md` L51 / `onboarding/ai-onboarding-pack.md` L23,L206–207 / `onboarding/new-project-checklist.md` §4–6 / `contracts/plm-ready-contract.md` 全体 / `onboarding/developer-navigation.md` §5 | 「BOM-DD PLM に同期し stop finding 0 を確認する」が必須手順・実装開始 Gate として繰り返し要求されるが、PLM ツール本体が kit に同梱されていない。手動代替の可否・手順も未記載 | **参照切れ+前提ツール不明**(最重大) |
| 2-2 | playbook §8 手順5(L242)/ `templates/63-diff-audit.md` L3 / `templates/product-profile/change-management.md` L18,L28 | diff 監査の機械実行手段「BomDD-Plm(bomdd-lint)R-052」が外部 GitHub リポ。kit 内に実行物なし | 参照切れ |
| 2-3 | `README.md` L12,L49–62 / playbook L5,L332 / `docs/reproduce-*.md` 全3本 | 実証証拠・採点治具の実物(`blackbox-oracle.ps1`・`exploratory-probe.ps1`・`loops/`・metrics.csv)がすべて外部。固定オラクルランナーの**動く実例が kit 内に一つも無い** | 参照切れ |
| 2-4 | `README.md` L4(`../MoviePad`)、L49–62(`loops/`) | README が指す題材リポと loops/ が kit に無い | 参照切れ |
| 2-5 | `templates/00-charter.md` L57(G0 Intake)vs `prompts/phase0-charter.md` L20–23(G0=固定項目完備) | G0 の定義が2通りあり、どちらを G0 として記録すべきか一意でない | 矛盾 |
| 2-6 | `prompts/phase2-spec.md` L14(「3 体のサブエージェント」)vs playbook §11(S: 「リーダー1体に縮退可」) | 数REQ規模で G2 リーダー数をどちらに従うか。正典(prompts)とテーラリング表のどちらが優先か未規定 | 曖昧 |
| 2-7 | playbook §11(S: 「10/20 統合可」「30–32 統合可」「G3 省略可」「42/53 省略可」)vs `contracts/plm-ready-contract.md` §13(「必須成果物 00/10/20/30/31/32/33/34/40 が欠けている」=実装開始停止)/ `templates/40-work-order.md` L12–18(G3 pass を実装開始条件に列挙) | テーラリングで統合・省略した場合に PLM 契約・Work Order の開始条件と形式的に矛盾する。統合ファイルの命名・PLM の読み方も未規定 | 矛盾 |
| 2-8 | `templates/41-fixed-oracle.yaml`(宣言のみ)/ playbook §4.4 / `prompts/phase3-design.md` 手順4 | 固定オラクルの**実行系**(ハーネスの言語・起動方法・合否の exit code 規約・結果 JSON の形式)が未規定。「治具セルフテスト」も「合成データで検証」という散文のみで合格基準・手順が無い | 前提ツール不明+曖昧 |
| 2-9 | `prompts/phase4-manufacture.md` L13(「各工場は別ディレクトリに製造」) | 単一工場(S)での成果物配置、および合格した工場ビルドをリポ本体(`src/` 等)へ「納品物」として昇格させる手順・基準が無い | 曖昧 |
| 2-10 | `prompts/phase2-spec.md` L14 / `prompts/phase4-manufacture.md` L7,L13 | 「互いを知らない別モデルティアのサブエージェント」の実現手段が「Claude Code なら Agent ツールの model 指定」の一文のみ。他環境での隔離・ティア混成の実現方法、「クリーンな文脈」の検証方法が未規定 | 前提ツール不明 |
| 2-11 | `method/cheat-taxonomy.md` L28–37(様式: `CHEAT-NNN`・発生段=①リバース…)vs `templates/51-cheat-log.md`(様式: `CHEAT-<LOOP>-001`・発生段=①要求…+side/差分帰属/欠陥帰属欄) | ずる記録の正式様式・ID 形式・発生段語彙が2文書で不一致。どちらで記録すべきか一意でない(テンプレ側が新しいと推測できるが kit 内に優先宣言なし) | 矛盾 |
| 2-12 | `onboarding/example-session-log.md` L213(「G4 充足=納品」) | G4 が playbook・prompts・テンプレのどこにも定義されていない。納品判定のゲート名・判定方法が不在(Phase 6 に prompt ファイル自体が無い) | 矛盾(用語)+曖昧 |
| 2-13 | `templates/00-charter.md` L61(G3 の証跡=`bomdd/plm-intake/00-index.md` / `{CandidateNo}.md`) | G3 の証跡が plm-intake 作業票とされるが、`prompts/phase3-design.md` の G3 手順は質問リストの補正のみで、plm-intake への記録手順が無い | 曖昧 |
| 2-14 | `prompts/phase2-spec.md` L10(HTML モック入力時は `ui-mock-to-ui-bom.md` を使え)vs `prompts/README.md` L14(同ファイルは **deprecated**・新経路は ui-raw-to-candidates→ui-apply-rulings-to-bom) | GUI 入力がある場合にどちらの抽出経路が正か矛盾(本件 API では非該当だが kit の一意性欠陥) | 矛盾 |
| 2-15 | `method/silence-checklist.md` §14(永続化・データ: 全行「予防候補(未観測)」)/ `templates/db/schema-intent.md` §7(CP-MIGRATION-001) | 新規開発の初回ループで「マイグレーション」「データ互換性」行をどう宣言すべきか(初回は out-of-scope でよいのか、playbook §10 のように意図的に1回スコープへ含めるのか)の基準が無い | 曖昧 |
| 2-16 | playbook §4.4「較正(negative control。既知個体が存在する時点から必須)」 | 初回ループは「セルフテストまで」と書かれる一方、収束2周目の「既知個体」に初回工場ビルドを使うのか、較正の具体手順(期待プロファイルの書式)が未規定 | 曖昧 |
| 2-17 | `templates/40-work-order.md` L63–67 | blocker 発見時「blocked マークで続行」と自己受入赤「stop/report」が併存し、blocked unit があるため自己受入を緑にできない場合の優先順位・納品可否が未規定 | 曖昧 |
| 2-18 | `templates/10-requirements.yaml` ほか YAML 全テンプレ冒頭 `experiment: <ループID>` | ループ ID・bom_rev・凍結 tag の命名規約が例示のみで規定なし(52-metrics の集計キーになるため揺れると測定が濁る) | 曖昧 |
| 2-19 | `templates/33-control-plan.yaml` L14–19(depth_ladder は「この題材での定義」を自分で書く) | Web API 題材での unit/L1/L2/L3 の具体的定義は設計者裁量。webapi 実例の対応表は kit 外リポにしか無い | 曖昧 |
| 2-20 | `templates/product-profile/skills/*.md`(`{{METHOD}}`/`{{PRODUCT}}` プレースホルダ)+ `tools/bomdd-init.py` L21(`METHOD_ROOT = parents[2]`) | bomdd-init を kit 内で実行すると METHOD_ROOT=transfer-kit になり動作見込みだが、kit(一時ディレクトリ)を恒久の「方法論リポ」として参照してよいかは運用判断。init を使わず手動コピーする場合のプレースホルダ解決手順は未記載 | 曖昧 |
| 2-21 | `prompts/phase5-accept.md` §2 / playbook §6.2 | ユーザー裁定の3択を「誰が・いつまでに」返すかの運用(非同期時の停止規律)が無い。裁定が得られない場合にループを進めてよいかは不明 | 曖昧 |
| 2-22 | kit 全体 | 実装技術スタックの決め方が無い。選定の権限(設計者AI 単独か、ユーザー裁定必須か)は未規定 | 曖昧 |

## 3. 着手前にユーザーへ確認が必要な質問リスト(逐語・13問)

| # | 質問 | 理由 |
|---|---|---|
| Q1 | 題材の中身は何か | kit は方法のみで題材を含まない |
| Q2 | 工場構成とモデル。別ティアのサブエージェントを起動できる環境か | チャーター固定項目+環境事実 |
| Q3 | 収束ループ予算はいくつか | 人間宣言が必須 |
| Q4 | 役割: 設計者・G2 リーダー数・承認者。Sサイズ縮退を適用してよいか | prompts と §11 が食い違い(2-6, 2-7) |
| Q5 | PLM 同期・PLM Gate はどう扱うか(スキップ承認/手動代替/ツール支給) | 必須 Gate なのにツールが無い(2-1) |
| Q6 | 実装技術スタックと procurement の許可範囲 | 選定基準・権限の規定なし(2-22) |
| Q7 | 固定オラクル/ハーネスの実装技術と実行環境の指定 | 実装標準が無く実例は参照禁止の外部リポのみ(2-8, 2-3) |
| Q8 | DB マイグレーションを初回スコープに含めるか | §14 の宣言基準が無い(2-15) |
| Q9 | Phase 7 まで「一周」に含めるか。変更要求は誰がいつ出すか | 外部入力が無いと発火しない |
| Q10 | 成果物リポの場所・git 運用(タグ権限、工場成果物の配置と昇格) | 配置・昇格手順が未規定(2-9, 2-18) |
| Q11 | Phase 5 の裁定を都度返答してもらえるか。得られない場合の既定動作は | 非同期時の規律が無い(2-21) |
| Q12 | ずる記録の様式は 51 テンプレ版(新)で統一してよいか | 2文書が不一致で優先宣言が無い(2-11) |
| Q13 | 納品判定(Phase 6)は「完了の定義の充足+ユーザー承認」でよいか | ゲートが未定義・「G4」は他文書に無い(2-12) |

## 4. 実行可否の自己評価(逐語)

**判定: 条件付きでできる。**

手順の骨格は playbook+prompts+templates で一貫して追跡可能であり、非GUI・wire 境界の本件は kit が最も厚く実証を語る形態(Web/API)に一致する。ただし以下を人間の裁定で埋めない限り、kit の字義通りには一周を完遂できない。

**最大の障害(3つ)**:

1. **PLM Gate が実行不能**: 複数文書が「PLM 同期で stop finding 0」を実装開始の必須条件とするのに、判定ツールが kit に同梱されていない。`plm-ready-contract.md` を手動チェックリストとして代替する以外に進む道が無く、その代替は kit が認めていない逸脱(=ずるとして記録すべき事象)になる。
2. **検査器(固定オラクルランナー・自己受入ハーネス)の実装標準と動く実例が kit 内に皆無**: 41/33 は宣言テンプレのみで、実行系・exit code 規約・「治具セルフテスト」の合格基準が散文。kit 自身が最重要と位置づける「検査器側のずる」への防御が、初回実施者の自己流実装に依存する。
3. **人間(ユーザー)の同席が構造的に必須なのに、その運用規約が薄い**: 題材・チャーター固定項目・G1 精度裁定・K-BOM 裁定・Phase 5 の3択裁定はすべて人間ゲートであり AI 側で代替不能。加えて G0 の二重定義・G2 リーダー数の prompts/テーラリング不一致・Phase 6 ゲート不在(未定義の「G4」)など、人間と合意すべき点そのものが kit 内で一意に読めない。
