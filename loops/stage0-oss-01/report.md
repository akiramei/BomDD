# stage0-oss-01 レポート — OSS 3 リポへの stage-0 健診(H1〜H5 判定)

> 実施 2026-07-09。事前登録: [protocol.md](protocol.md)(凍結コミット ceb1a4c = 測定結果より前)。
> 治具: method/tools/stage0-survey.py(ViewGrid 較正済み — [calibration.md](calibration.md))。
> 対象: jellyfin(C#・53aafcd3)/ gitea(Go+TS・545ed923)/ home-assistant/core(Python・64fc462a)+基準点 ViewGrid。
> 一次データ: [results/](results/)(リポ別 JSON・HEAD SHA 記録済み・`--filter=blob:none` クローンで再現可能)。

## 1. 測定サマリ

| リポ | 追跡ファイル | LOC | 解析コミット | fix率 | H3 跨ぎ率 | fix跨ぎ率 | H1 top-1% fix集中 | H2 三冠/2冠 | H4 遅発率(p50) | revert(二重) |
|---|---|---|---|---|---|---|---|---|---|---|
| ViewGrid(基準) | 661 | 108k | 298 | 18.8% | 59.9% | 50.0% | **35.7%**(k=7) | 5 / 7 | 36.8%(14) | 3(0) |
| jellyfin | 2,485 | 361k | 22,415 | 15.3% | 37.5% | 36.7% | 14.2%(k=25) | 2 / 6 | 86.3%(347) | 141(1) |
| gitea | 5,615 | 774k | 19,923 | 26.6% | 46.2% | 44.8% | **24.0%**(k=57) | 0 / 5 | 90.7%(357) | 71(1) |
| core | 26,487 | 5.41M | 110,424 | 15.2% | 54.1% | 39.0% | **24.3%**(k=265) | 0 / 5 | 94.1%(1,720) | 686(12) |

(2冠 = churn 上位10 ∩ fix 上位10 の重なり。三冠 = さらにサイズ上位10 との共通部分)

## 2. 仮説判定(凍結基準どおり・事後変更なし)

判定は事前登録の凍結基準で行う。H1 は事後の読みを安定させるため 2 命題に**分解して提示**する(測定値・凍結判定は不変 — H1 の中に強い主張と弱い主張が混在していたことが判明したため。レビュー指摘 2026-07-09)。

| # | 仮説 | 判定 | 根拠 |
|---|---|---|---|
| H1a | churn 上位と fix 上位は重なる(2冠) | **支持(4/4)** | 重なり 7/6/5/5 — stage-0 の中核信号として残す |
| H1b | top-1% ファイルへ fix が強集中(≥20%) | **部分支持(2/3)** | gitea 24.0%・core 24.3% ✓ / jellyfin 14.2%(**弱集中だが 2冠は存在** — 25 ファイルが全 fix-touch の 1/7 を担う)。閾値仮説としては弱める |
| H2 | 三冠(churn∩fix∩size 上位10 重なり ≥3) | **不支持(0/3)** | jellyfin 2・gitea 0・core 0。**サイズの脚が OSS で脱落** — god-file 型ハブは普遍ではない(観測結果) |
| H3 | 跨ぎ率 30〜70% の帯(≥2/3) | **支持(3/3)** | 37.5 / 46.2 / 54.1% — 全リポで変更の 4〜5 割が unit 境界を跨ぐ。**fix に限っても 37〜45%**。導入価値の主指標に昇格 |
| H4 | 遅発 fix(距離>20)≥25%(≥2/3) | **形式支持(3/3)だが測定規約の不備を検出** | 86〜94% — 閾値「20 コミット」が履歴規模でスケールせず、大リポでは自明に充足。凍結値のまま判定した上で規約の欠陥として記録(§4-1) |
| H5 | 集中は規模で単調増加 | **反証** | share: ViewGrid(661f)35.7 → jellyfin(2.5kf)14.2 → gitea(5.6kf)24.0 → core(26kf)24.3 — 非単調。最小リポが最大値。「集中は体制の関数」は**次仮説**(H6)であり本測定の結論ではない |

### 2.1 互換性ノート(ViewGrid 跨ぎ率 49.8% → 59.9%)

旧 ViewGrid stage-0(2026-07-07・scratch 治具)は跨ぎ率 **49.8%** を報告し、本研究の基準値は **59.9%**。差は治具較正で特定済みの**定義差**である([calibration.md](calibration.md) §1-2): 旧= unit 算入を `src/**` に限定(tests は unit に数えない)・分母= src 接触コミット / 新(一般化定義)= 全ファイル(tests 含む)・分母=全非 bulk コミット。`--unit-scope src` で旧定義を再現すると 42.2%(残差=分母差)であり、**分子側の順位・件数は旧値と一致**する。旧値は歴史値として保持し、クロスリポ比較には新定義の値のみを使う。定義の互換性は較正で管理されている(都合による指標変更ではない)。

## 3. 中心的所見

1. **「変更ハブ= fix ハブ」(H1a)は 4/4 で普遍**(2冠 5〜7)。ハブは実在し、fix はそこに集まる。ただし**「巨大ファイル」との三冠は単独開発リポ(ViewGrid)の局所性**だった — OSS のサイズ上位は生成物・台帳的ファイルに占められ、god ファイルは分割済みか、そもそも集中の形が違う。**ハブの再定義**(H2 不支持の方法論への変換):

   ```text
   ハブ = 大きいファイルではなく、変更と修正が繰り返し戻ってくる unit
   Primary hub signal   : churn ∩ fix overlap(H1a)
   Secondary amplifier  : size / 所有分散 / 層跨ぎ位置 / テスト不在(危険増幅因子)
   Anti-pattern         : size 単独をハブ判定に使う
   ```
2. **fix の 4 割前後が unit 境界を跨ぐ**(37〜45%・4/4)— 影響宣言(BOM トレース)の回収価値を示す直接材料。stage-0 健診の「導入判断材料」としての中核数値。
3. **H5 反証の含意**: ハブ集中は規模の関数ではなかった。ViewGrid(単独開発)が最も強く、OSS では規模に依らず 14〜24% で頭打ち — 集中は**規模でなく開発体制(単独 vs 多人数)の関数**である可能性(探索的・次ラウンドの事前登録候補)。scale-01 の主張(影響*写像の外れ*がハブに集中)とは測定対象が異なることに注意 — 本測定は履歴の集中であり、宣言 vs 実 diff の採点は台帳なしリポでは原理的に不能(impact-retrospective との役割分担)。
4. **failed-fix 連鎖は規模で顕在**: revert-of-revert(二重失敗)が core で 12 件。ViewGrid で「実バグコストの印」だった信号(FINDINGS §10.5)が大規模でも検出可能。
5. **百万行級の未踏を初消化**: core 5.41M 行・110k コミットを治具がそのまま処理(name-status のみ・blob:none クローンで完結)— 規模の壁は「測定の壁」ではなかった。

## 4. 測定規約の不備(次ラウンドへの是正候補 — 事後変更はせず記録のみ)

1. **fix 潜伏の絶対距離は履歴規模でスケールしない**(H4)。探索的(post-hoc 明示)に正規化中央値(p50/総コミット)を見ると: ViewGrid 4.7% / jellyfin 1.5% / gitea 1.8% / core 1.6% — **OSS 3 リポが 1.5〜1.8% に収束**する興味深い規則性。次ラウンドの事前登録では絶対距離を廃し、次を併記する(レビュー裁定 2026-07-09): ① wall-clock latency(日数)② repo-global commit distance ③ **unit-local edit distance**(同一 unit への何回目の編集で fix が出たか — 巨大リポでは全体距離 20 は短時間で流れるが、unit 内距離は影響分析・回帰検査の失敗に近い信号)④ release distance(次リリース後の fix か)⑤ percentile latency(リポ内分布の上位 25%/10%)。
2. **台帳的ファイルの混入**: gitea の fix 上位に .VERSION(188)・README(160)・locale(148)— リリース・文書の随伴変更で、アーキテクチャ的ハブではない。次ラウンドは**除外でなく層分け**(A: 全ファイル / B: 製品コードのみ / C: テストのみ / D: config・registry・manifest・localization・生成物系)の二重集計を事前登録し、「結論が A と B で同じなら頑健・A だけで出るなら運用ファイル由来の見かけのハブ」と判定する。D 層は捨てるのではなく **coordination surface**(コードでないのに変更影響を集める面 — 依存 manifest・schema registry・integration list・localization catalog)として別分類する価値がある(今回は凍結定義のまま報告)。
3. jellyfin の SharedVersion.cs(95)も同種。fix 分類自体の適合率レビュー(サンプリング検査)は未実施。

## 5. RQ への答え(現時点)

- **RQ-B'(ハブ集中の普遍性)**: 「変更ハブ= fix ハブ」は多言語・大規模で再現(4/4)。ただし集中の**強さ**は規模で増えず(H5 反証)、形(サイズとの相関)も単独開発リポと異なる。主張は「ハブは普遍・三冠は局所」へ精密化。
- **RQ-E'(git 履歴だけの事前診断)**: 成立。1 リポ数分で、跨ぎ率(宣言回収価値)・ハブ台帳初期値(top units/files)・fix 潜伏・failed-fix 連鎖まで自動抽出できた。**rule of three 成立(適用 4 例)** — stage-0 スコア表(提案第6節の cross-unit rate / hub concentration / fix latency / revert chain / hub-first priority)の初版化は昇格裁定へ。

## 6. 限界

- 仮 unit = 深さ2ディレクトリ(裁定境界でない)。fix 分類は件名キーワード(適合率未検査・conventional commits 準拠度に依存 — 過小方向)。
- 相関であって因果でない。BomDD 導入効果の証明ではなく、導入判断の事前材料+scale-01 仮説の外部整合まで。
- 有名 OSS 3 本(選定バイアス)。single-developer OSS・企業内リポは未測定(H5 の「開発体制」仮説の検証はそこが対象)。

## 7. 還元(裁定 2026-07-09: 2 件とも採用・採用形を分離)

1. **stage0-survey.py の正式化**(実施済み — method/tools/ へ配置・較正記録つき)。
2. **stage-0 triage score(Alpha)**: 移行パック(existing-project-migration §7)へ **alpha・N=4 calibration・定義凍結= stage0-oss-01・計装注意つき**で採用。「診断スコア」でなく **triage score**(hub-first 部分移行の入口判断)として置く。→ 織り込み済み。
3. **FINDINGS 追補(本線)**: 「ハブは普遍」は churn∩fix overlap に限定し、「三冠は局所」(観測結果)と「集中は体制の関数」(次仮説)を書き分け、H2/H5 の反証を支持と同じ重さで扱う。→ §12 として織り込み済み。

## 8. 次ラウンドの事前登録候補(H6〜H10 — 凍結は次 protocol で)

| # | 仮説候補 |
|---|---|
| H6 | churn∩fix overlap の強さは、LOC・コミット数よりも **ownership entropy・module boundary clarity** に強く関連する(説明変数候補: contributor 数・所有分散・review density・境界明瞭度・test proximity・release cadence・台帳的ファイル比率) |
| H7 | churn∩fix overlap は unit 粒度(path / package / subsystem)を変えても上位候補の一部が安定する |
| H8 | 台帳的ファイル(D 層)を分離しても、製品コード unit の churn∩fix overlap は残る |
| H9 | cross-unit pressure が高いリポほど、PR の observed diff は初期変更後の repair-augmented diff で広がる |
| H10 | **stage-0 hub-first チェックリストを LLM 影響分析に足すと、observed diff に対する unit-level recall が上がる**(over-inclusion も併測)— stage-0 を診断で終わらせず影響分析の点検リストへ変換する仮説。ここまで行くと Paper 2b |

## 9. 論文ロードマップへの位置づけ(更新)

| 論文 | 本結果の効き方 |
|---|---|
| Paper 1a: transfer-01(fresh AI 担当者への転移) | 間接 — 「測定 kit が整備されている」証拠として採用材料 |
| **Paper 2a / Paper 5: stage0-oss-01(本研究)** | 中核 — stage-0 健診の外部妥当性を ViewGrid N=1 → N=4(C#/Go+TS/Python・36万〜541万行)へ拡張。数十万〜百万行級で測定実行可能を実証 |
| Paper 2b: hub-first shadow 影響分析 | 次段 — 実 PR/ECO で under-inclusion を測る(H9/H10) |

**規模の壁の再定式化**: 壁は LOC の単調関数ではなく、**開発体制・アーキテクチャ境界・unit 写像(組織構造と実装重心のずれ)の関数**として扱うべきである(H5 反証+scale-01 の写像集中の統合読み)。
