# T0 読者A(G2型監査)raw 出力

> 実施 2026-07-08。fresh サブエージェント(general-purpose)。kit のみ参照・事前知識使用禁止の制約下。以下は読者の最終出力の逐語保存(§1 手順抽出表は突合に使用済みのため要旨、§2〜§4 は逐語)。

## 1. 実行手順の抽出(要旨)

Phase 0〜7 の全フェーズについて目的・成果物・ゲート・判定方法を正しく抽出。判定の機械/人間の別:
- G0/G1/G2/G2'/G3 = 人間判断(exit code 化された治具なし)
- Phase 4 自己受入 = 機械判定(ただしハーネスは自作治具)、ずる報告の全件性 = 人間確認
- Phase 5 = 混合(オラクル実行は機械、差分帰属・blocker 判定・裁定は人間)
- Phase 6 = **ゲート名なし・判定方法は kit からは不明**(prompts/ に phase6 ファイルなし。チャーター「完了の定義」が実質の完了条件)
- Phase 7 = 混合(回帰・較正は機械、diff 監査の機械化ツール bomdd-lint は kit 外、帰属は人間)

スキャフォールドは `bomdd-init.py --no-gui`(非対話時の既定は GUI=True のため `--no-gui` 明示が必要 — bomdd-init.py L129)と特定。

## 2. 一意に読めない箇所の全件列挙(逐語)

| # | 該当箇所 | 何が決まらないか | 分類 |
|---|---|---|---|
| 1 | `templates/00-charter.md` L53–68(実装開始 Gate 表・PLM 同期方針)、`onboarding/new-project-checklist.md` §5–6、`onboarding/ai-onboarding-pack.md` §10 手順10–11、`templates/40-work-order.md` L7「PLM Gate result」、`contracts/plm-ready-contract.md` 全体 | 「BOM-DD PLM に同期する」の実行手段。PLM 本体が kit に**存在しない**。contract は判定条件を定義するが実行体が無く、PLM Gate pass を機械的に得る方法が無い | 前提ツール不明+参照切れ |
| 2 | `templates/63-diff-audit.md` L3–13、playbook §8 手順5(L242)、`templates/product-profile/change-management.md` L18・R1 | diff 監査の機械実行は「BomDD-Plm(bomdd-lint)の R-052」を指すが、当該リポは kit に無い。手動 63 で代替可と明記されているため実行は可能だが、「機械実行」の経路は再現不能 | 参照切れ(代替手順あり) |
| 3 | `README.md` L4(`../MoviePad`)・L49–62(`loops/` 配下の構成記述)・証拠リポ3本、`docs/reproduce-*.md` 全3本、playbook L5/L332 の `../FINDINGS.md` §7 が参照する証拠 | `loops/`・MoviePad・全証拠リポが kit 外。方法論の実行には不要だが、「実証済み」主張の一次証拠と再現手順は kit 単独では検証不能 | 参照切れ(実行には非致命) |
| 4 | `prompts/phase2-spec.md` L14、`prompts/phase4-manufacture.md` L7・L13、playbook §4.3/§4.6/§5.1 | 「互いを知らない N 体のサブエージェント」「クリーンな文脈のサブエージェント」の実現方法は「Claude Code なら Agent ツール」とだけ例示。他環境での隔離担保・別モデルティアの調達方法は未規定 | 前提ツール不明 |
| 5 | playbook §11 テーラリング表(L334–350) | 本件は「S」に該当するが、縮退は全て「〜可」表記。どれを採るかの決定規準が無く、採否の裁定者も未規定 | 曖昧 |
| 6 | `method/cheat-taxonomy.md` L32(発生段: ①リバース/②E-BOM/③M-BOM/④工程/⑤製造/⑥合否)vs `templates/51-cheat-log.md` L9(発生段: ①要求/②仕様/③BOM設計/④工程/⑤製造/⑥合否) | ずる記録の「発生段」語彙が2文書で異なる(版差と推測されるが、どちらを使うかの指示なし) | 矛盾(軽微) |
| 7 | `prompts/README.md` L8「G0 固定項目完備」vs `templates/00-charter.md` L57「G0 Intake(人間が最初に配置した資料一覧)」 | G0 の定義が2通りに読める | 矛盾/曖昧 |
| 8 | `templates/10-requirements.yaml` L15(`rationale_precision: ok | needs-refinement`)vs `onboarding/new-project-checklist.md` §6 G1(「根拠精度が **adequate**」) | G1 判定の状態語彙が不一致(ok と adequate)。機械照合するなら正規語彙が決まらない | 曖昧(軽微) |
| 9 | playbook §2 G1(L56)vs `prompts/phase1-brainstorm.md` L23 | 持ち越しを認める条件と、持ち越し可否を誰が裁定するかが未規定 | 曖昧 |
| 10 | `templates/41-fixed-oracle.yaml` L17(self_test)・`templates/33-control-plan.yaml` fixture 欄・`templates/32-mbom.yaml` L54(M-ACCEPTANCE-HARNESS)・playbook §4.4 | 固定オラクル治具の実装形(言語・実行コマンド・レポート形式)は完全に各プロジェクト自作。playbook §13 は「完了条件は治具の exit code で書く」を運用規則とするが、非 GUI 題材向けの既製治具は kit に 1 本も無い | 曖昧(実装は設計者に全委任) |
| 11 | `prompts/phase4-manufacture.md` L13(工場成果物は「別ディレクトリ(例 `loops/<loop>/factory-0N/`)」)vs `onboarding/ai-onboarding-pack.md` §4 標準フォルダ構成(`loops/` を含まない) | 多工場成果物・採点結果の標準配置が例示レベルで、標準構成と接続していない | 曖昧 |
| 12 | playbook §7 / prompts/ 一式 | Phase 6 に完了ゲートと実行プロンプトが無い。納品判定の正式な判定手続きはチャーター「完了の定義」からの類推になる | kit からは不明 |
| 13 | playbook §8 / `prompts/phase7-change-order.md` L4 | 新規開発の「一周」に Phase 7 を含める場合、変更要求(ECO の種)が外部入力として必要。一周の範囲に含めるか自体が決まらない | 曖昧(タスク定義との不整合) |
| 14 | `method/silence-checklist.md` §13(調達部品)・§14(永続化・データ)— いずれも「予防候補(未観測)」 | SQLite 題材の最重要次元(トランザクション境界・同時更新競合・マイグレーション・データ互換)は掃討行として存在するが、証拠付き推奨決定が無い | その他(方法論の自認する未検証領域) |
| 15 | `templates/00-charter.md` L61(G3 の証跡欄が `bomdd/plm-intake/00-index.md` / `{CandidateNo}.md` を指す) | G3 の証跡が PLM intake ファイルとされるが、ドライラン結果を plm-intake へ記録する手順はどのプロンプトにも書かれていない | 曖昧/参照不整合 |
| 16 | playbook §6.3・`prompts/phase5-accept.md` §3+`templates/00-charter.md`(収束ループ予算) | 予算(回数上限)を使い切っても終了条件未達の場合の処置(納品拒否か、条件緩和か、blocker 残しの引き渡しか)が未規定 | kit からは不明 |
| 17 | `templates/product-profile/skills/*.md` の `{{METHOD}}` プレースホルダ(bomdd-init.py L117/147 が方法論リポの**絶対パス**を転写) | 生成されるスキルは方法論リポの恒久パスを前提とする。kit が一時ディレクトリにある本状況では、どこを METHOD として恒久配置するかが決まらない | その他(運用前提) |
| 18 | `templates/33-control-plan.yaml` L84–95(CP-NFR 行)・`templates/30-ebom.yaml` L107–113(nfr_targets)— いずれも「candidate」 | NFR 目標値を数 REQ 規模で立てるべきかの基準なし | 曖昧 |
| 19 | `templates/52-metrics.yaml`・playbook §6.1 | 1工場構成での探索プローブの意味(分散が観測できない)と、その場合の unspecified_bom_residue 検出力低下の補償手段は「ずる報告で代替」(§11)とあるのみで手順化されていない | 曖昧(軽微) |
| 20 | `templates/40-work-order.md` L5「対象 BOM tag/commit」、41 L16「frozen_since」 | 凍結タグの命名規約・打刻タイミングの正式規則が無い(reproduce-forward-01.md L27–33 に実例があるのみ) | 曖昧(軽微) |
| 21 | cheat 重大度 blocker / friction / minor(cheat-taxonomy・51 テンプレ) | 「blocker」の判定基準が定義されておらず、収束終了条件「blocker 差分ゼロ」の判定が判定者依存 | 曖昧 |
| 22 | `onboarding/new-project-checklist.md` §3・§6 の「PLM: stop 状態がない」 | 実装開始判定 5 条件のうち PLM 条件のみ実行不能(#1 と同根)。残 4 条件(G1/G2/G2'/G3)で開始してよいかは未規定 | 曖昧(#1 の帰結) |

## 3. 着手前にユーザーへ確認が必要な質問リスト(逐語)

| # | 質問 | なぜ kit 内で解決できないか |
|---|---|---|
| 1 | 何を作るか(Web API の題材・数 REQ の中身・スコープ外)を対話で確定させてください | Phase 1 はユーザーとのブレスト・裁定が構造上必須で、kit は方法であって要求を含まない |
| 2 | 工場構成を固定します: 1工場(S 規模の既定)か、初回 2–3 工場(推奨・別モデルティア)か。利用可能なモデルティアは何ですか | Phase 0 で固定し以後不変の項目であり、実行環境のモデル調達可否は kit の外 |
| 3 | 収束ループ予算(回数上限)は何回にしますか。予算超過で未収束の場合の処置は? | チャーター固定項目だが値の既定なし。超過時の処置は kit 未規定 |
| 4 | 役割の確定: 裁定者は誰ですか。G2' で human-approval-required が出た場合の承認者は? | human gate は方法論に組み込みで、人間不在では収束ループが完了しない |
| 5 | テーラリング S の縮退採否: G2 監査をリーダー1体に縮退 / G3 ドライラン省略 / 42 探索プローブ省略 / 53 Service BOM 省略 — それぞれ採用しますか | playbook §11 は全て「可」であり、採否の決定規準・裁定者が kit に無い |
| 6 | 「Phase 0〜7 の一周」に Phase 7(ECO)を含めますか。含めるなら納品後の変更要求を出してもらえますか | Phase 7 は「納品後の再入口」であり変更要求という外部入力が無いと実施不能 |
| 7 | PLM Gate の扱い: BOM-DD PLM ツールが kit に無いため、手動セルフチェック+plm-ready-contract の目視照合で代替してよいですか | PLM 実行体が kit に存在せず、charter/checklist/work-order が要求する「PLM sync result」を正規に得られない |
| 8 | 実現技術スタック(言語・フレームワーク・SQLite ドライバ)に指定・制約はありますか。procurement に載せてよいものは? | M-BOM の「実現技術」「調達部品」は設計判断であり kit に既定なし。工場は procurement 外の依存を使えないため事前確定が必要 |
| 9 | NFR(性能・可用性)要求はありますか。あるなら測定可能な数値で | NFR 目標は candidate 扱いで要否基準が無く、「速い」のままでは G2' で仕様未完成になる |
| 10 | 成果物リポの場所と git 運用(オラクル凍結 tag・diff 基準点コミットを打つ権限、多工場成果物の配置先)を指定してください | 凍結・較正・diff 監査は git タグ/コミットを前提とするが、配置と権限は kit の外 |
| 11 | 隔離サブエージェントを起動できる実行環境を使ってよいですか。使えない場合の代替の許容は? | 隔離の実現方法が「Claude Code なら Agent ツール」の例示のみ |
| 12 | 方法論一式(この kit)をどこに恒久配置しますか | bomdd-init.py が方法論リポの絶対パスを転写する設計で、一時ディレクトリのままでは生成物が壊れる |

## 4. 実行可否の自己評価(逐語)

**判定: 条件付きでできる。**

根拠: フェーズ手順(prompts/ 正典)・全成果物テンプレ・沈黙次元カタログ・ずる記録様式・テーラリング規約は kit 内で自己完結しており、非 GUI の Web API + SQLite は kit が想定する主題材そのもの(templates の記入例が予約 API/SQLite/`K-SQLITE-001`/`db/schema-intent.md` で書かれている)。§3 の質問(特に 1–5, 7–8)への回答が得られれば、Phase 0→6 の一周は実行可能。Phase 7 は変更要求の供給があれば実行可能。

**最大の障害(3つ)**:

1. **PLM Gate の実行体が kit に無い**: チャーター・チェックリスト・Work Order が実装開始条件として「PLM sync result / stop finding 0」を要求するが、`bomdd/` を機械検査する PLM ツールは kit 外。plm-ready-contract.md を目視照合する手動代替は可能だが、方法論が明記する機械ゲートを 1 つ欠いたまま回すことになる。
2. **human gate が構造的に組み込まれており、kit 単独では一周が閉じない**: 要求の中身・チャーター固定項目・Phase 5 の 3 択裁定は全てユーザー入力が必須。これは欠陥ではなく設計だが、「kit だけで完遂」は原理的に不可で、ユーザーの応答可用性が律速になる。
3. **検査治具(固定オラクルハーネス・セルフテスト・較正)が全面自作**: 機械判定の要である受入ハーネス・オラクル実行器・L1 スモークは実装形が未規定で、本題材向けの既製治具は kit に無い。フォワードでは「治具は未検証のまま初回採点に臨む」と kit 自身が警告する領域であり、治具品質=一周の測定品質が実装者依存になる。加えて SQLite 永続化の沈黙次元(silence-checklist §14)は「予防候補(未観測)」で、証拠付きの推奨決定が無い。
