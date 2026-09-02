# BomDD 構想の全体像 (concept)

> このドキュメントは、以前 README が「セッションメモリ参照」としていた**構想の全体像**を、外部読者だけで完結して読めるよう公開ドキュメント化したものである。実証記録は [WHITEPAPER.md](../WHITEPAPER.md) / [FINDINGS.md](../FINDINGS.md)、現行の方法論の正本は [method/bomdd-playbook-v1.md](../method/bomdd-playbook-v1.md)(v1 時点の凍結スナップショットは [method/bomdd-method-v1.md](../method/bomdd-method-v1.md))、用語の固定は [terminology.md](terminology.md) を参照。

## 1. これは何か

BomDD(BOM-Driven Development)は、ソフトウェア開発を「人間が都度コードを書く作業」ではなく、**設計BOM → AI 製造 → 保守BOM を貫く工業プロセス**として扱えるかを問う研究である。新規製造と収束ループでは fresh 工場が BOM のみから再製造する(修正がコーチングでなく BOM に宿ることの証明形式)。保守レジーム(Phase 7・ECO)では BOM は**変更統制の正本**であり、是正は設計者 AI のプローブ先行の直接最小是正+BOM/Control Plan 同期で行う(fresh 再製造は要さない) — 製造の正本としての BOM は新規製造時に限る。

本リポは**研究**(方法論リポ)である。真の成果物は動くアプリではなく、「**BOM 手法がどこで破れ(=ずる)、どう埋めるか**」の記録と手法改善である。初期題材は既存アプリ MoviePad(Avalonia/.NET/C# + LibVLC + ffmpeg の非破壊動画編集デスクトップ)の 7 ループのアクションリサーチで、以後 Web/API・分散 Saga(N=3 ドメイン)、原版の無いフォワード題材、そして製品リポ(ViewPrism2・TimetableAdv 等)の**継続運用レジーム**へ広がった。研究レジームと製品運用レジームは別物として測る。

## 2. 中核アナロジー — AI = 製造装置

- **AI = 製造装置**(NC 工作機械の類比)。重要なのはプロンプトを書くことではなく、装置への投入情報を NC データ/工程指示として管理すること。
- **BOM = 製造指示**。設計の意図・部品構成・製造単位・受入基準を構造化したもの。
- **失敗は部品表の不足だけでなく**、装置が使う暗黙知・治具・検査・許容差が未管理であることに起因する。
- AI 製造の来歴(モデル・プロンプト・コンテキスト・生成ルール・検査・人間承認)は SLSA provenance を拡張した形で記録する(v2 で **As-Built BOM** として形式化済み — [terminology.md](terminology.md) 参照)。

## 3. 三層BOM(E / M / S)+ K-BOM

| 層 | 役割 | 単位 |
|---|---|---|
| **E-BOM** | 設計(論理部品構成 + 存在理由↔仕様トレース) | 設計上独立した責務・I/F・受入条件・変更理由を持つ「論理部品」 |
| **M-BOM + 工程** | 製造(実現技術・非機能・合否基準・Control Plan・FMEA・隔離・マルチファクトリ) | AI が生成・組立・検査・ビルドできる「製造単位」 |
| **S-BOM(Service BOM)** | 保守(外部知識依存の劣化 → 影響 → 再検査 → 交換判断) | 稼働後に状態監視・不具合判定・交換できる「実体部品」 |

- **K-BOM(知識部品表)**: 要求 BOM とは別に、製造装置が参照する「外部ツール/設計の管理知識」(ffmpeg 文法パック、デザイントークン等)を部品化する。暗黙知を管理対象に変える仕組み。
- **S-BOM は一般的な SBOM(Software Bill of Materials)ではない。** 本研究の S-BOM は **Service BOM / 保守 BOM** であり、OSS 依存一覧はその一部に過ぎない。詳細は [terminology.md](terminology.md#s-bom)。
- **UI-IR / UI-BOM(GUI 案件の正規工程= playbook Phase 1.5)**: HTML モックを DOM タグ一覧としてではなく、画面・領域・UI 部品候補・操作・入力・状態の出現として読み、E-BOM へ昇格できる候補部品表に変換する入口。UI-IR は観測用中間表現、UI-BOM は仮品番付き候補部品表であり、正式な E-BOM を置き換えない。状態語の正本は playbook §1(完了条件は治具 exit code)。詳細は [method/ui-ir-ui-bom.md](../method/ui-ir-ui-bom.md)。
- **Design System BOM(candidate・playbook §4.1)/ Visual Gap(運用中・§4.4)**: UI-CAD 案件では、Card / CTA / Chip / Badge / IconButton などの設計言語部品を E/K-BOM へ明示し、製造後に CAD と実機を視覚突合する。素の panel/text/button への退化は cosmetic ではなく、BOM 化されていない surface 部品の欠落として扱う。検証済みの一般化は**標準部品台帳**(playbook §4.7・ViewPrism2 ECO-122 で実証)。

## 4. 中核発見 — 核と表面の法則

3 つの異なる領域(純粋ロジック / 外部ツール / UI)が同じ構造に収束した。

| | 核 (Deterministic Core) | 表面 (External Surface) |
|---|---|---|
| 例 | ドメイン代数・判定規則・幾何 | ffmpeg コマンド文法・画面の画素 |
| 正しさの出所 | 要求から導出可 | 外部仕様/設計トークン(知識) |
| BOM から鋳造? | ✅ unit で検査 | △ 知識転記 + 検査工程が要る |
| 受入 | unit | execution/golden + 人間判断 |

- 観測した 12 件のずるのうち、**成果物上に発現したのは 4 件で、いずれも外部知識依存面(核 0)**。残りは oracle 5・process 1・bom-metamodel 2 に発現した(盲検第二評価者による再分類 2026-07-11・単純一致 10/12・κ 0.77 — [loops/cheat-reclassification-01/](../loops/cheat-reclassification-01/)。初出の「12 件すべて表面側」は一次発現層としては不正確で、この命題に置換)。核/表面の構造は 3 ドメイン(GUI・Web/API・分散 Saga)で再現。一般法則としては引き続き未検証。
- 「コードを鋳造品とみなせるか」の答え: **核は YES。表面は仕上げ・検査工程を伴って初めて鋳造保証**が立つ(製造業の表面処理・外観検査と同型)。よって工業化は**部分的に成立**=核は自動化に向かい、表面は半自動 + 人間検査に落ち着く。

## 5. ずる = 測定器

BomDD の測定器は「ずる」である。AI が BOM/工程から導けず、慣習・暗黙知・原版記憶・未文書の判断で埋めた箇所をすべて記録する。**ずるをゼロにすることが目的ではなく、ずるを BOM・K-BOM・工程・検査・S-BOM のどこで管理するかを決める**ことが目的である。

- 製造装置は原版非開示の別エージェントとして**隔離**し、「BOM に無く慣習で埋めた箇所」の網羅報告を正式工程にする(C2 暗黙知の可視化=本研究で最も効いた測定器)。
- 分類: C1 表現ギャップ / C2 暗黙知 / C3 工程欠落 / C4 受入不能 / C5 粒度崩壊 / C6 手戻り。2026-08 に**証拠偽装**(検査を欺く証拠の製造)と**帳簿代用**(存在検査を実体検査の代用にする共進化型)を rule of three 成立で追加(→ [method/cheat-taxonomy.md](../method/cheat-taxonomy.md))。

## 6. 受入の梯子と品質の二軸

- **受入の梯子**: `L0 文字列 < L1 存在 < L2 メタデータ < L3 内容/信号 < golden + 承認者`。核 = unit、表面 = 領域別の深さ。L0/pixel-exact は過剰結合のため既定不採用。
- **品質の二軸**: (1) 決定性 = 工場間ばらつき(同一 BOM を複数装置に渡した出力の分散)、(2) 正しさ = 受入(L2/L3/golden)。**一致 ≠ 正しさ**——複数工場が揃って同じ誤りを出す「共有暗黙知の罠」があるため、両軸を独立に検査する。

## 7. 研究の現状と次段

- **v1 完了**: 入口(リバース)→ E-BOM → M-BOM + 工程 → S-BOM が一周。ずる 12 件すべてに手法的対策。
- **v2 完了(外部妥当性・N=3)**: Web/API と分散 Saga で「核/表面の法則」と BOM 補正による収束が再現(FINDINGS §6)。As-Built BOM・受入 2 層(固定オラクル/探索プローブ)・差分帰属 3 分類を追加。
- **フォワード・モード実証済み**: 原版の無い新規開発を forward-01〜04・scale-01・transfer-01〜03(ベンダー横断・説明介入ゼロ)で回した([method/bomdd-playbook-v1.md](../method/bomdd-playbook-v1.md)・FINDINGS §7/9/11)。
- **現在(2026-09)**: 方法論の**自己適用**(本リポの変更を ECO として管理・`bomdd/`)と、工程設備の較正 — 設計収束 `/converge`・証拠資格査定 `/calibrate`・開始条件再認証 `/preflight` を作業スキルとして配布し、receipt の構造的存在を機械検査(self-conformance)で押さえる。裁定の配置原則(導出できない空白のみを裁定し、出力を BOM・台帳へ書き戻す)は playbook §9。
- **スキーマ**: 機械可読な共通スキーマ(E/M/K-BOM・Control Plan・Routing・As-Built・Service BOM)は候補のまま([method/schema-candidates-index.md](../method/schema-candidates-index.md))。**複数ドメインを生き延びてから固める**方針は維持。

## 読む順序

1. このドキュメント(概念)
2. [terminology.md](terminology.md)(用語の固定)
3. [WHITEPAPER.md](../WHITEPAPER.md)(公開版・強い主張/未検証の分離)
4. [FINDINGS.md](../FINDINGS.md)(7 ループの詳細記録・ずる台帳 12 件)
5. [method/bomdd-playbook-v1.md](../method/bomdd-playbook-v1.md)(フォワード・モードの実践手順 — 実際に回すならここ。§9 に裁定・統制の配置原則)
6. [method/](../method/)(Control Plan・K-BOM・S-BOM テンプレート・ずる分類・onboarding。method-v1 は v1 時点の凍結版)
7. [loops/](../loops/) / [loops/metrics.csv](../loops/metrics.csv)(各ループの生成物と測定値)
8. 本リポで作業する場合は [AGENTS.md](../AGENTS.md)(作業規律 6 項目・正本の所在)
