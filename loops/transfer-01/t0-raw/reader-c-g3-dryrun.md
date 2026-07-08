# T0 読者C(G3型ドライラン)raw 出力

> 実施 2026-07-08。fresh サブエージェント(general-purpose)。kit のみ参照・事前知識使用禁止の制約下。以下は読者の最終出力の逐語保存。

## 1. 着手可否

**判定: 質問への回答があれば着手できる。**

理由: 方法論そのもの(工程フロー Phase 0〜7、各フェーズの実行プロンプト、成果物テンプレ 00〜64、完了ゲート G0/G1/G2/G2'/G3、沈黙次元カタログ、隔離製造・ずる報告・オラクル・ファーストの規律)は kit 内で自己完結しており、今回の題材「小型 Web API+SQLite・数REQ規模」は playbook が単一題材検証済みと明記する forward-01(図書貸出 API・SQLite 永続化)とほぼ同型で、手順の適用に方法論上の穴はない。着手を止めるのは方法論知識の不足ではなく、(a) Phase 0 で「以後不変」として固定を要求される項目(工場構成・予算・役割)を埋めるための環境・契約情報が kit の外にあること、(b) kit が随所で前提とする「BOM-DD PLM」工具が kit に同梱されておらず PLM Gate の扱いが決められないこと、の2点。これらは質問で解消できる(なお本 kit 自身の G3 ドライラン規準「残る質問が exploratory 宣言済みならゼロ扱い」に照らしても、下記 B/C の質問は宣言済みでない=補正対象)。

## 2. 着手前質問の全件列挙

### 【A: kit内に答えあり】(解決までの探索が長かったもの=導線の問題のみ)

| # | 質問 | 解決箇所と導線の問題 |
|---|---|---|
| A1 | 新規開始の正しい入口はどれか(README→playbook→prompts→onboarding→bomdd-init→/bomdd-next と入口候補が6つある) | 最終解: `method/tools/bomdd-init.py` で scaffold → `/bomdd-next`(`method/templates/product-profile/skills/bomdd-next.md` の判定表)→ 実行手順の正典は `method/prompts/phase0〜5`。`README.md` L14 の1段落と `method/onboarding/new-project-checklist.md` 冒頭を突合して初めて確定。README 冒頭に「新規開発者はここから」の一本道がない |
| A2 | スキル(/bomdd-next 等)は使うのか使わないのか | `method/prompts/README.md` L20 は「`.claude/skills` を置かない」(2026-06-10 方針)、一方 `bomdd-init.py` はスキル8本を製品リポへ設置する。`README.md` L14「2026-07 に adapter 層として追加」で時系列的に解消するが、prompts/README が未更新のまま残っており矛盾に見える |
| A3 | SQLite 永続化は方法論でどう扱うのか(未検証領域ではないのか) | `method/silence-checklist.md` §14 は「予防候補(未観測: N=3 は全て in-memory)」と書くが、`method/bomdd-playbook-v1.md` L5 で forward-01(SQLite 永続化+マイグレーション)が一周済み。実務上の受け皿は `method/templates/db/schema-intent.md` と `method/contracts/plm-ready-contract.md` の K-SQLITE-001 例。§14 の「未観測」表記が forward-01 後も未更新に見え、確信を得るのに複数文書の突合が要った |
| A4 | 数REQ規模でどこまで省略できるか | `method/bomdd-playbook-v1.md` §11 テーラリング表(S列)で解決。ただし `new-project-checklist.md` §3/§6・`templates/00-charter.md`・`templates/40-work-order.md` は常にフル装備前提で書かれ、S列との読み替えは読者任せ |
| A5 | 固定オラクルの「実行手段」は何か(テンプレ 41 は YAML 定義のみ) | 採点治具は設計者が自作し製品と同格に repo 管理する、が答え(playbook §4.4+`templates/34-routing.yaml` の自己受入 step+41 の self_test 欄)。汎用ランナーを探して tools/ を回ったが存在しない |
| A6 | Phase 6(引き渡し)の実行プロンプトはどこか | 独立ファイルは無い。`method/prompts/phase5-accept.md` 末尾の1段落+playbook §7 が正。prompts/README の表に Phase 6 の行が無く、欠落かどうかの確認に往復した |

### 【B: kit内で曖昧】(読み方で作業が変わる)

| # | 質問 | 候補の読み方 |
|---|---|---|
| B1 | **PLM Gate は実装開始の必須条件か**。`00-charter.md` テンプレ・`40-work-order.md`「PLM stop finding が 0」・`new-project-checklist.md` §6・`developer-navigation.md` §7 は PLM Gate pass を実装開始条件に含めるが、kit に PLM 工具は無く、`onboarding/example-session-log.md` は PLM 同期を一度も行わずに納品まで進む | (a) PLM 工具が無い環境では not-applicable と明記して省略 / (b) `contracts/plm-ready-contract.md` を設計AI/人間がセルフチェックして代替 / (c) 外部リポ BomDD-Plm の導入が事実上の前提。どれを取るかで Phase 3 の完了条件と工数が変わる |
| B2 | G2 マルチリーダー監査の体数。playbook §11 S列は「リーダー1体(セルフ監査)に縮退可」、`prompts/phase2-spec.md` は無条件に「互いを知らない3体・別モデルティア」 | S列を優先(1体)/ プロンプト正典を優先(3体)。「差分=仕様の曖昧箇所」という監査の検出力は1体だとほぼ失われるため、どちらを取るかは測定設計に直結 |
| B3 | G3 ドライランの要否。S列=「省略可」、`new-project-checklist.md` §6 と `40-work-order.md` 実装開始条件=「G3 pass」必須 | 省略する/しない。forward-01 実測(7問+矛盾2件を製造前検出・安価)からはやる価値が高いが、規範がどちらかは読めない |
| B4 | 42 探索プローブの要否。S列=「省略可(ずる報告で代替)」、`prompts/phase5-accept.md` は手順3で探索プローブ実行を無条件に含む | 省略時は Phase 5 手順を読み替える必要があるが、その読み替え規則は書かれていない |
| B5 | 工場数。playbook §5.2「推奨=初回2–3工場(別ティア)」と「工場能力は単一軸でない(強いモデル1体運用は穴を通す)」vs §11 S列「1工場」 | 1工場で C2(共有暗黙知)検出を捨てる / 初回のみ2–3工場。チャーターで「以後不変」に固定させられるため、着手前に裁定が必須 |
| B6 | 「顧客」と「人間(裁定・golden 担当)」は同一人物か。`working-with-ai.md` は人間の仕事=裁定+golden と定義するが、顧客がその役を担う前提かは書かれていない。また GUI 無し(黒箱境界=wire)なら golden 承認者は不要と読めるが、G2' で `human-approval-required` 特性が出た場合の承認者は誰か | 顧客=裁定者 / 開発側に別途裁定者を置く。承認者はチャーター時点で確保が必須(phase0-charter.md)なので着手前に決める必要がある |
| B7 | 成果物リポの初期化は `bomdd-init.py`(CLAUDE.md+スキル込み・Claude Code 前提)か、`templates/` の手動コピー(playbook §1 の記述)か | Claude Code 環境なら init 一択に見えるが、prompts が「任意の AI アシスタント」を掲げるため、非 Claude 環境での正規手順が二義的 |
| B8 | §11 で「10 要求/20 仕様は1ファイルに統合可」とされるが、`plm-ready-contract.md` §13 は「必須成果物 00/10/20/30-34/40 が欠けている」を stop と定義する。統合したら PLM 上は欠落扱いか | 統合を諦める / stop を承知で not-applicable 裁定する。B1 の裁定に従属 |

### 【C: kitに無い】(欠けている情報の種別を併記)

| # | 質問 | 欠けている情報 |
|---|---|---|
| C1 | 顧客は誰で、いつブレストに使えるか。スコープ・完了の定義・納期・収束ループ予算(回数上限)への合意は取れるか | 題材・契約情報。Phase 0 の「以後不変」固定項目の材料 |
| C2 | 隔離ファクトリ/マルチリーダーを実現する AI 実行環境は何か。使えるモデルティアは何か(prompts は「Claude Code なら Agent ツールの model 指定 opus/sonnet/haiku」とだけ書く)。API コスト予算は | 環境・ツール。fresh なクリーン文脈のサブエージェント起動手段は方法論の根幹(隔離規律)だが、その実現手段は環境依存で kit は Claude Code 以外の代替を示さない |
| C3 | 技術スタック(言語・Web フレームワーク・SQLite ドライバ)の顧客制約はあるか | 題材情報。kit はスタック非依存(実例は .NET+PS7)で、M-BOM「実現技術」を埋めるのは Phase 3 だが、制約の有無は顧客に聞くしかない |
| C4 | BOM-DD PLM(bomdd-lint)工具の入手方法。`change-management.md`・`plm-ready-contract.md`・`63-diff-audit.md`(R-052 機械実行)が前提とするが、kit 内に実体もインストール手順も無い(外部 GitHub リポ名の言及のみ) | ツール実体。B1 の裁定材料 |
| C5 | 完全に記入済みの `bomdd/` 一式の実例はどこで見られるか。kit 内は空テンプレ+断片例のみで、実例(BomDD-WebApi-Sample / BomDD-LibraryLending-Sample 等)は全て外部 GitHub リポ。今回の参照禁止制約下では見られない | 参照資料。初見者が「埋まった姿」を知る手段 |
| C6 | `60-change-register.yaml` のテンプレ/スキーマ。`CLAUDE.product.md`・`skills/eco-file.md`・`schemas/draft/ref-edges.draft.yaml` が前提とするが、テンプレ一式(00〜64)に存在しない(draft スキーマに記述はあるが「硬化しない」宣言つき) | テンプレ欠落。納品後(Phase 7)に顕在化 |
| C7 | 開発マシンの前提一覧(python3・git は治具と凍結 tag 運用に必須だが、明示された前提要件リストが kit に無い) | 環境要件の明文 |
| C8 | 納品物に `bomdd/` 一式(cheat-log・オラクル・治具込み)を含める前提だが、顧客はそれを受け入れるか(納品形態・リポ所有権) | 契約情報 |

## 3. 最初の3日間の作業計画

前提: 上記 B1(PLM Gate)・B2/B5(監査体数・工場数)・C1〜C3 の回答を Day 1 冒頭までに得る。

**Day 1 — スキャフォールド+Phase 0+Phase 1**
1. `python method/tools/bomdd-init.py <Product> --no-gui` で製品リポ生成(成果物: `bomdd/` テンプレ一式+CLAUDE.md+スキル8本、初回コミット)。
2. `new-project-checklist.md` §1(入力資料)・§2(人間配置ファイル)を顧客と記入。DB=yes なので `bomdd/db/` を有効化。— **ゲート G0 Intake**
3. `prompts/phase0-charter.md` に従い `bomdd/00-charter.md`: 黒箱境界=**wire(HTTP)**、工場構成(裁定結果を固定・以後不変)、収束ループ予算、役割・承認者。— **ゲート G0(固定項目完備)**
4. `prompts/phase1-brainstorm.md` に従い顧客ブレスト(発散→反例生成5件/要求→収束)→ `bomdd/10-requirements.yaml`。各 REQ に根拠精度の判定質問、核/表面の仮分類、SQLite 関連判断を K-BOM 調達候補へ。— **ゲート G1**+charter の `(仮)` 確定

**Day 2 — Phase 2 仕様化**
1. `prompts/phase2-spec.md` に従い `bomdd/20-spec.md`: REQ 双方向トレース、不変条件節、`silence-checklist.md` **第1回掃討**(§3 識別子・§4 日時・§6 エラー・§7 冪等・§8 出力スキーマ・§12 状態機械・§13 調達・§14 永続化が本件の主戦場)。
2. `bomdd/db/schema-intent.md`(templates/db 版): entity/field/invariant/migration 方針/K-DB 候補。
3. **ゲート G2** マルチリーダー仕様監査(体数は Day 1 裁定に従う)。
4. **ゲート G2'** 測定可能性(全 REQ を adequate に)。

**Day 3 — Phase 3 BOM・工程設計**
1. `prompts/phase3-design.md` の順序どおり: `30-ebom.yaml` → FMEA+**沈黙掃討第2回** → `31-kbom.yaml`(クリーンなサブエージェントに慣習判断の全列挙→裁定)。
2. **オラクル・ファースト**: `33-control-plan.yaml` → `41-fixed-oracle.yaml`(治具実装+**セルフテスト**→ commit/tag で凍結)→ `42-exploratory-probes.yaml`(採用時)。
3. `32-mbom.yaml` / `34-routing.yaml` / `40-work-order.md`。
4. **ゲート G3** ドライラン: fresh サブエージェントに製造パッケージのみ渡し質問ゼロまで補正。

**計画が書けない箇所(それ自体を記録)**
- **PLM Gate の実施**: charter テンプレと checklist §6 が要求するが、工具が kit に無く手順が書けない(B1/C4 未裁定)。暫定は plm-ready-contract の人力セルフチェックだが、これは私の判断であり kit の指示ではない。
- **G2 の体数・工場数の確定値**: §11 S列と prompts 正典が食い違い、裁定なしでは計画表に数字が書けない(B2/B5)。
- **Phase 4 開始日**: 工場数と収束予算(C1/C2)が決まるまで見積不能。順調なら Day 4。

## 4. ツール・環境の前提チェック(kit が前提とするが kit 内に無い/入手方法不明)

| 前提物 | どこが前提としているか | kit 内の状態 |
|---|---|---|
| **BOM-DD PLM 工具(bomdd-lint。R-052 diff_audit・PLM sync・stop/warning findings)** | `templates/00-charter.md` PLM Gate 行、`new-project-checklist.md` §4-6、`contracts/plm-ready-contract.md`(工具の仕様書のみ)、`onboarding/developer-navigation.md` §5-6、`templates/63-diff-audit.md`、`change-management.md` | **実体なし**。外部 GitHub リポ(BomDD-Plm)への言及のみで入手手順なし |
| **60-change-register.yaml のテンプレ** | `product-profile/CLAUDE.product.md`、`skills/eco-file.md`、`schemas/draft/ref-edges.draft.yaml`、`tools/impact-retrospective.py` | テンプレ一式(00〜64)に**存在しない**。draft スキーマの記述のみ |
| **/lesson-promote スキル** | playbook §13(手順の成熟度ラダーの実例として言及) | kit に無い(方法論リポ側スキルの模様) |
| **固定オラクル実行ハーネス(汎用ランナー)** | 41 テンプレ・Routing 自己受入 step・phase5 測定手順 | 汎用工具は無く**案件ごとに自作**が正(playbook §4.4)。実例(blackbox-oracle.ps1)は外部リポにのみ存在 |
| **隔離ファクトリ/マルチリーダーの実行基盤** | prompts/phase2〜4「Claude Code なら Agent ツールの model 指定(opus/sonnet/haiku)」 | Claude Code+複数モデルティアが事実上の前提。他環境での fresh 文脈・非開示の実現手順は無い |
| **実証サンプルリポ3本+ loops/ ディレクトリ** | README・playbook・method-v1・docs/reproduce-* が証拠・実例として多数参照 | すべて kit 外。追試・実例参照は kit 単体では不可(着手自体には不要) |
| python3+git | `tools/*.py`、オラクル凍結 tag、bomdd-init の git init | 実行環境として必要だが、前提要件の明文リストは kit に無い |
| GUI 系治具(ui-mock-inspect.py / ui-cad-gate.py / ui-extract.py) | Phase 1.5(GUI 案件のみ) | **kit 内に有り**(本件 Web API では不要) |
