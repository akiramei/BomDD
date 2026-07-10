# Observation Schema Candidates(観測スキーマ候補 — draft / まだ JSON Schema ではない)

> **ステータス**: draft / candidates only。これは規格(JSON Schema)ではなく、**3ドメイン(MoviePad / Web-API / 分散Saga)を生き延びた「測定ハーネス側」の構造を抽出して眺めるための候補表**である。硬化(`schemas/draft/*.json`)はこの段階では**しない**。根拠は [bomdd-method-v1.md](bomdd-method-v1.md) と [../FINDINGS.md](../FINDINGS.md) §6、および各証拠リポジトリ(webapi-* / saga-*)。
>
> 対になる **product 側**(E/K/M-BOM・Routing・As-Built・Service BOM)は `product-schema-candidates.md`、両者の関係は `schema-candidates-index.md` に分ける(未作成)。この分割自体が本方法論の最重要規律=**製品差分と観測ハーネス差分の分離**(FINDINGS §6.4)をスキーマ構造として体現する。

## 1. Purpose(なぜ observation を product と分けて先に抽出するか)

BomDD の新規性が高く・他者が模倣しにくいのは、BOM のフィールド表(=製品の静的構造)ではなく、**AI 製造を測定可能にする規律**である:

- 隔離ファクトリ + ずる報告の義務化(製造装置に原版を見せない)
- **固定オラクル / 探索プローブの2層分離**(合否に未規定次元を混ぜない)
- **差分帰属**(差分を「AI 差」で止めず BOM欠落 / 工場能力 / 未規定面 / 検査器表現 に切り分ける)
- **観測契約**(ワイヤ境界が無い in-process でも黒箱を作る)
- **C2(共有暗黙知)が製品でなく検査器側に転移する**というメタ発見

このドキュメントは、これらを「3ドメインで実際に使った形」に正規化し、**何が共通(=方法論の不変)で、何が各ドメインに強制されて生えたか(=証拠)** を分けて記録する。`fixed oracle behavioral diff` と `literal observer representation diff` を別カテゴリに保つ(saga で死守した規律)ことを、ここで構造として固定する。

## 2. Layer Boundary(層境界 — 全エンティティが従う3分)

観測される差分は、必ず次の3層のどれかに属させる。混ぜると改善効果測定(鋳造性が上がったか)が濁る。

| 層 | 定義 | 合否に入るか |
|---|---|---|
| **product behavior** | BOM/契約が値を固定した振る舞い(status code・状態遷移・補償規則・冪等の同一性 等) | **入る**(固定オラクル) |
| **observation-harness behavior** | 検査器・観測契約自身の表現(JSON 形状・キー綴り・正規化の癖) | **入らない**(別カテゴリで記録) |
| **exploratory variance** | BOM が沈黙する未規定次元(ID 具体値・日時の小数秒・応答スキーマの未規定フィールド) | **入らない**(探索プローブ層で variance として観測) |

> 規律: 固定オラクルに入れてよいのは **product behavior** だけ。観測ハーネスの都合(層2)と未規定面(層3)は決して合否に混ぜない。

## 3. EquivalenceRule(等価規則 — observation の核概念)

**固定オラクルの「挙動契約」は、等価規則によって定義される。** 何を「同じ」と見なし何を比較しないかが決まって初めて、`behavioral diff` が定義可能になる。saga の2度の検査器ずる(events.json の map/array、dispatch キーの snake/camel)は、すべて「オラクルが付随表現に過剰結合し、本来無視すべき差を差分と誤検出した」事例であり、**等価規則の欠落**が原因だった。

候補フィールド:
```
EquivalenceRule
  id
  compares            : 契約セマンティクスのうち比較する観点(例: イベント種別の列, 補償の発火, 冪等の同一ID性)
  ignores             : 比較しない付随表現(例: JSON 形状 map/array, キー綴り snake/camel, GUID 具体値, 日時の小数秒)
  normalization       : 比較前に施す正規化(例: イベントログを {type, payload-contract} へ畳む)
  rationale           : なぜこの差を無視してよいか(契約に未規定 / 様式差 だから)
  applies_to          : FixedOracleCase の集合 | 全体
```

- **共通(仮説)**: `compares` は常に Control Plan / 契約の語彙で書く(内部実装名に結合しない=L0 過剰結合の回避)。
- **domain delta(証拠)**:
  - MoviePad — `ignores` に「妥当な配色差・サブピクセル丸め」、`compares` に L3 信号(PSNR/相関)。golden は許容差+承認者を要した。
  - Web/API — `ignores` に「内部 C# 名」、`compares` に HTTP status / error code / 状態。等価規則は事実上 OpenAPI 契約。
  - Saga — `ignores` に「events.json 形状(map/array)・dispatch キー綴り・eventId 形式」、`compares` に「イベント契約セマンティクス」。**この `ignores` 欄が saga で初めて重くなった**=非同期 in-process がワイヤ表現を持たないぶん、等価規則を明示しないと検査器が表現に結合する。

## 4. Candidate Entities(候補エンティティ)

各エンティティに【共通=3ドメインで残った=方法論の不変仮説】【domain delta=各ドメインが強制した成長=証拠】を付す。

### 4.1 ObservationContract
黒箱境界の定義。「固定シナリオを流すと、内部実装名でなく契約語彙で正規化した観測出力(イベントログ / dispatch trace / HTTP 応答)を emit する」I/F。
```
ObservationContract
  id
  boundary_kind       : wire(HTTP) | in-process-emit | gui-render+signal
  scenarios_ref       : 固定シナリオ集合(FixedOracleCase の入力)
  emitted_shape       : 正規化観測出力の契約(内部名非依存)
  vocabulary_ref      : 観測語彙の出所(Control Plan / event contract / OpenAPI)
```
- **共通**: 観測語彙は必ず製品契約 or Control Plan に紐付く。内部 C# 名に結合しない。
- **domain delta**: MoviePad=GUI レンダ + L3 信号抽出 / Web/API=ワイヤ境界がそのまま黒箱(契約が自明) / **Saga=観測契約という概念自体が新設**(ワイヤ境界の不在を埋めるため `emit モード`で正規化ログを吐く。method v1.2 addendum (a))。

### 4.2 FixedOracleCase
合否を出す固定シナリオ1件。**ループ間で凍結**(同一ヤードスティック)。
```
FixedOracleCase
  id
  scenario            : 入力(決定的)
  contract_expectation: 契約上の期待(product behavior のみ)
  equivalence_ref     : 適用する EquivalenceRule
  depth               : required_depth(L0–L3+golden の梯子上の位置。梯子定義は §6)
  frozen_since        : この case を固定したコミット/タグ
```
- **不変条件**: 固定オラクルの集合は study 内で**不変**。途中で増やすと収束測定(2→3→0)が無効になる(§6 規律)。
- **domain delta**: MoviePad 7観点(うち知覚は golden+承認者) / Web/API 16シナリオ(HTTP 契約) / Saga 7観点(6ランタイム + 1静的契約)。

### 4.3 ExploratoryProbe
未規定次元を**合否非混在で**観測する。variance を記録するだけで pass/fail を出さない。
```
ExploratoryProbe
  id
  scenario            : 探索入力(例: create→cancel→別keyで同内容re-create)
  dimension           : 観測する未規定次元(ID 形式 / ID 一意性 / 日時表現 / 応答スキーマ形)
  observed_variance   : 工場ごとの値の分布(合否でなく分布)
```
- **共通**: 「ばらつきは BOM が沈黙する場所に正確に集中する」を測る装置。
- **domain delta**: Web/API=ID 形式 bk_+{16/24/16/12}hex・日時 offset・最小応答スキーマ / Saga=eventId 4通り・timestamp 精度・sequence 基点・inbox 区切り・causationId 方針。

### 4.4 DiffAttribution
観測した差分を帰属させる。**2層**(§5 に詳述)。
```
DiffAttribution
  diff_id
  tier                : product-attributed(確定3分類) | harness-attributed(候補)
  category            : §5 の分類のいずれか(harness 側は候補扱い)
  evidence            : 観測ログ/result-*.json への参照
  legacy_code         : 対応する v1 C1–C6(あれば。C4 はここでなく MeasurementCapability §4.9)
```

### 4.5 CheatRecord
ずる(BOM由来でない産物)1件。様式は [cheat-taxonomy.md](cheat-taxonomy.md) を踏襲しつつ、**製造側ずる**と**検査器側ずる**を区別するフィールドを追加。
```
CheatRecord
  id                  : CHEAT-NNN / CHEAT-<domain>-NN-NNN
  side                : factory(製造側) | harness(検査器側)   ← v1.2 で追加が必要になった軸
  stage               : ①リバース ②E-BOM ③M-BOM ④工程 ⑤製造 ⑥合否
  category            : C1–C6(cheat-taxonomy)
  missing             : 手法が与えなかったもの
  substituted         : 代替した従来技術
  severity            : blocker | friction | minor
  proposed_fix        : 次ループでの BOM/工程/検査器の修正
```
- **domain delta(重要)**: `side: harness` は **saga で初めて必要**になった。CHEAT-SAGA-01-002(events.json map/array)・CHEAT-SAGA-02-002(dispatch キー camelCase)は製造差分でなく**測定ハーネスの表現差**。C2 が製品でなく検査器に出た新パターン。

### 4.6 MetricRun
1回の測定の集計。**raw 一致率を単独で置かない**(死守規律)。
```
MetricRun
  id
  factory_run_ref     : FactoryRun
  oracle_ref          : 固定オラクル集合(frozen)
  raw_match           : 参考値(単独では報告しない)
  targeted_fix_success: 狙った補正が消したか
  blocker_diffs       : blocker 件数(例: 1→0)
  new_unspecified_diffs: 補正で新たに露出した未規定次元
  exploratory_variance: 探索層の分布(合否外)
```
- **共通**: 収束は `targeted_fix / blocker / new_unspecified` の分解で語る(例: webapi 2→3→0)。
- **domain delta**: MoviePad は受入合格率 + Loop4 ばらつき0 / Web/API は収束表 + 多工場 0/1/3 / Saga は多工場 0/0/0(haiku も転移)。

### 4.7 FactoryRun
1ファクトリの製造実行(観測対象)。**product 側 As-Built を参照して join**(境界をまたがず連結)。
```
FactoryRun
  id
  tier                : opus | sonnet | haiku | ...(Agent model 上書きで分離)
  input_bom_ref       : 供与した固定 BOM(tag)
  isolation           : clean(原版・前ファクトリ・cheat 非開示)
  as_built_ref        : → product 側 As-Built(model / prompt_hash / artifacts sha256)
  self_acceptance     : 自己受入結果(例: 7/7, 26/26)
```
- **共通**: 各ファクトリは clean context(改善が BOM に宿ったかを公正に測るため前ファクトリ・分岐・cheat を渡さない)。
- 注: `as_built_ref` が **observation→product の唯一の越境参照**。FactoryRun(観測: どの工場が何点)は As-Built(製品: 何を・どのモデルで作ったか)を指すが、両者は別ファイル。

### 4.8 Control Plan(観測側の持ち分のみ)
Control Plan は**境界をまたぐ artifact**。本ドキュメントが持つのは観測側だけ:
```
Control Plan (observation side)
  oracle_ref          : この特性を測る FixedOracleCase
  probe_ref           : 未規定面なら ExploratoryProbe
  equivalence_ref     : 適用 EquivalenceRule(何を比較しないか)
  diff_attribution    : 差分が出たときの帰属先
```
製品側(`characteristic / acceptance_ref / required_depth`)は `product-schema-candidates.md` に置く。`required_depth` の**梯子定義**は §6、**特性への深さ割当**は product 側、で分担する。

### 4.9 MeasurementCapability(測定能力 — C4 の逃がし先)
**DiffAttribution と直交する軸**。DiffAttribution が「この差分はどこから来たか」を答えるのに対し、MeasurementCapability は「**そもそもその差分を観測できる深さ・治具・承認者が足りているか**」を答える。v1 の **C4「受入不能」はここに属する**——C4 は失敗の原因分類でなく、**測定器をどこまで深くする必要があるかを示す信号**だから。
```
MeasurementCapability
  characteristic_ref  : 対象の受入観点/特性
  state               : adequate
                      | unmeasurable           ← 客観オラクル自体が無い(知覚 golden 不在)
                      | under-specified-oracle  ← オラクルはあるが当該次元を固定していない
                      | insufficient-depth      ← 梯子が浅すぎる(L0/L2 で L3 が要る)
                      | human-approval-required ← 承認者を要する(知覚 golden + 許容差)
  current_depth       : 現在の required_depth 上の位置
  needed_depth        : 観測に必要と判明した深さ
  remedy              : 治具追加 / 深さ引き上げ / 承認者導入 / オラクル明細化
```
- **共通(仮説)**: 「受入不能」は固定でなく、治具・深さ・承認者で**遷移可能な状態**。研究の進展はこの state を `adequate` 方向へ動かすこと。
- **domain delta(証拠)**:
  - MoviePad UI/色 — `unmeasurable` / `human-approval-required`(知覚に客観オラクル不在)→ remedy=許容差+設計承認者。
  - MoviePad 音声 — `insufficient-depth`(L2 では尺同一で区別不能)→ remedy=L3 信号比較治具へ深さ引き上げ(Loop5 で座標系バグ捕捉)。
  - Saga — `unmeasurable`(ワイヤ境界が無い)→ remedy=**ObservationContract を新設**(emit モードで正規化ログ)。
  > C4 が「測定設計の未成熟状態」であることの証拠: 3ドメインとも、最初に観測不能だった特性を**測定器の側を深くする**ことで観測可能にした。差分の帰属(誰のせいか)とは別の話。

## 5. Diff Attribution(差分帰属 — 2層 + v1 C コードとの突合)

差分を「AI ごとに精度が違う」で止めず、次へ帰属させる。**product 帰属(確定3分類)と harness 帰属(現時点の候補)** に分け——失敗分類それ自体が product/observation 境界を尊重する。harness 側は `observed harness attribution candidates` の温度感で扱い、N=3 で観測した2つに閉じない(§8)。

| tier | category | 定義 | 根拠 |
|---|---|---|---|
| product(確定) | `unspecified_bom_residue` | BOM に無く工場が自由に埋めた。別ティアで露見=C2 | webapi-02 sonnet 1/16(not_found 未規定) |
| product(確定) | `specified_contract_miss` | BOM は明記したが低能力工場が外した=**工場能力** | webapi-02 haiku 3/16(409→400 等) |
| product(確定) | `exploratory_unspecified_surface` | 合否外で観測した未規定面の分散 | 全ドメインの探索層 |
| harness(候補) | `observer_representation_diff` | 検査器/工場の**出力表現**差(挙動は一致) | CHEAT-SAGA-02-002(dispatch camelCase) |
| harness(候補) | `observer_l0_overcoupling` | 検査器が原版の付随表現に L0 結合し誤検出 | CHEAT-SAGA-01-002(events.json map/array) |

### v1 cheat-taxonomy(C1–C6)との突合(横断統合 — 本ドキュメントの目玉)
v1(MoviePad)の C1–C6 は「製造側ずるの原因分類」、v2 の5分類は「観測した差分の帰属先」。両者は直交軸であり、次のように対応づく:

| v1 C コード | v2 帰属 category | 関係 |
|---|---|---|
| C2 暗黙知 | `unspecified_bom_residue` | 製品側に出た C2。共有暗黙知が尽きた点で露見 |
| C2 暗黙知(新) | `observer_representation_diff` / `observer_l0_overcoupling`(候補) | **C2 が検査器側に転移**(v1.2 saga の新パターン) |
| C4 受入不能 | **DiffAttribution でなく `MeasurementCapability`(§4.9)** | 差分の帰属でなく「観測できる深さ・治具・承認者が足りるか」の別軸 |
| C1 表現ギャップ | — | As-Built(product 側)で扱う |
| C3 工程欠落 / C5 粒度崩壊 / C6 手戻り | — | 構造的に塞いだ(product/工程側)。観測スキーマには現れにくい |

→ **観測スキーマで一級なのは C2 と C4。ただし両者は別軸**: C2 は **DiffAttribution**(製品 / 検査器どちらに出たかを `tier` で区別)、C4 は **MeasurementCapability**(測定器をどこまで深くするか)。「差分はどこから来たか」と「その差分を観測できるか」を混ぜない。

## 6. Invariants / Discipline(スキーマに埋め込む不変条件)

1. **固定オラクルはループ間で凍結**。FixedOracleCase 集合は study 内で不変(同一ヤードスティック)。違反すると収束測定が無効。
2. **プローブ→オラクル昇格の禁止**。study 途中で探索プローブの発見を固定オラクルへ移さない(移すと「途中でオラクルを拡張した」ことになり改善効果が濁る)。次 study の入口で正式に昇格させる。
3. **metrics は分解**。`raw_match` 単独で報告せず `targeted_fix_success / blocker_diffs / new_unspecified_diffs` に分ける。
4. **表現規律**。全工場一致を「完全鋳造」と呼ばず「**現固定オラクル被覆で未観測差分ゼロ**」とする。主張は常に「観測した範囲」。
5. **製品 / 検査器の分離**。差分帰属でも `tier` を必ず付け、`observer_*` を製造差分と混ぜない。
6. **L0 回避は検査器自身にも課す**。等価規則の `compares` は契約セマンティクス、`ignores` に付随表現。これを製造品だけでなく観測契約・採点器の設計にも適用する。

### required_depth(検査の梯子 — 定義は observation 側)
```
L0 文字列照合 < L1 存在/終了コード < L2 メタデータ < L3 content/signal < golden+承認者
```
- L0 は既定不採用(様式差を誤検出・意味乖離を見逃す)。例外=canonical serialization が仕様化されている / deterministic raster が製品特性(JSON 正規形・QR・暗号ハッシュ)。
- 各特性への深さ**割当**は product 側 Control Plan が、梯子の**定義と実装**(L3 信号解析器 等の治具)は observation 側が持つ。

## 7. Domain Evidence(各ドメインが観測ハーネスに強制した成長)

共通項は同一著者・同一テンプレの帰結なので証拠力は限定的。**情報量があるのは「各ドメインがハーネスに何を生やしたか」**:

| ドメイン | 黒箱境界 | ハーネスに強制された成長 |
|---|---|---|
| MoviePad(同期GUI) | GUI レンダ + 信号抽出 | **L3 信号比較 / golden + 許容差 + 承認者**(知覚は客観オラクル不在)。`EquivalenceRule.ignores` に妥当な配色差 |
| Web/API(同期HTTP) | ワイヤ境界(自明) | **固定オラクル/探索プローブの2層分離**(v1.1)・**差分帰属3分類**(v1.1)。等価規則=HTTP 契約 |
| 分散Saga(非同期) | **無い→観測契約を新設** | **ObservationContract という概念自体**(v1.2 a)・**検査器側 C2 / L0 回避**(v1.2 b)。`EquivalenceRule.ignores` が最も重い |

→ 観測ハーネス自身がドメイン圧で成長した。これは「同一テンプレを3回当てた」では説明できない、生き残り構造の証拠。

## 8. Not Yet Promoted / Open Questions(JSON Schema 化の前に詰める)

- **EquivalenceRule の `ignores` をどこまで形式化できるか**。現状は自然言語規律。機械可読化すると検査器の表現非依存を CI で強制できるが、早すぎると片ドメイン(saga の map/array)を焼き込む恐れ。
- **`required_depth` の depth と equivalence の関係**。深さが上がると等価規則の `compares` が増える。両者を独立フィールドにするか、depth を equivalence の関数にするか未決。
- **MetricRun の収束の正規形**。`2→3→0` のような系列をどう型で表すか(系列 vs 各ループの3分解の集合)。
- **harness 帰属カテゴリの数**。`observer_representation_diff` / `observer_l0_overcoupling` は **現時点の候補**(`observed harness attribution candidates`)であり、N=3 では足りたが確定分類にしない。新ドメインで第3が出る可能性(漸近)。
- **MeasurementCapability の state 列挙**。`unmeasurable / under-specified-oracle / insufficient-depth / human-approval-required` の4つで N=3 を覆えたが、これも候補。state 遷移(`adequate` への動かし方)を治具/承認者とどう結ぶか。
- **observation と product をまたぐ参照**(`FactoryRun.as_built_ref`, Control Plan 分割, `required_depth`)の所有規則を index で確定する。**越境は `FactoryRun.as_built_ref` の1本に限定**(観測→製品)、Control Plan と required_depth は概念分割して両側に持つ、で確定(本ドラフトの決定)。

### 管理特性候補および工程能力評価への準備(2026-07-10・transfer-02 還元)

次の属性品質特性を候補として登録する。

- **申告なき充填**: 発生件数および検査機会当たりの発生率。受入基準は 0 件。
- **method_explanation 欠落および rescue 欠落**: 原則として別特性として測定する。同一の検査機会と故障機構を持つことが実証された場合に限り統合する。
- **「影響なし」予測の under**: under 件数に加え、「影響なし」と予測した総件数を分母として記録する。
- **伏せ項目被覆**: 3 値の分布を保存するとともに、要求水準以上を満たした比率を算出する。

各特性について、検査単位、検査機会、分母、重複計数規則、受入基準、測定治具の版を凍結する。規格値 0 は受入基準であり、直ちに Cp/Cpk の規格限界として扱わない。

5 ラウンド蓄積時点では、測定継続の可否、定義の安定性、初期ランチャートの確認までを行う。管理限界の確定または工程能力の判定は行わない。十分な合理的群が蓄積した後、データの性質に応じて p 管理図、np 管理図、c 管理図または u 管理図を選択する。全件 0 の場合も能力達成とは断定せず、検査機会数に基づく欠陥率の信頼上限を併記する。

Cp/Cpk は、連続量であり、工程が安定し、工学的な規格限界が独立に定められている特性に限定する。時間特性は、測定系解析、工程構造別の層別、測定方法および規格限界の凍結が完了するまで、工程能力指数の対象にしない(時間の測定系: transfer-test.md §6・templates/52-metrics.yaml `timing`)。

### 確定した設計判断(このドラフトで決めた)
- **C4 は DiffAttribution でなく `MeasurementCapability`(§4.9)**。差分帰属と測定能力は直交軸。
- **越境参照は1本**(`FactoryRun.as_built_ref`)。他の境界物は分割保持。
- **harness 帰属は候補扱い**で確定させない。

## 9. 関係
- 対: `product-schema-candidates.md`(E/K/M-BOM・Routing・As-Built・Service BOM。Control Plan の製品側持ち分・`required_depth` の割当)
- 索引: `schema-candidates-index.md`(境界物の所有規則・JSON Schema 化はまだしない宣言)
- 根拠: [bomdd-method-v1.md](bomdd-method-v1.md)(§5 受入の2層分離 / §6 差分帰属 / v1.2 addendum)・[cheat-taxonomy.md](cheat-taxonomy.md)(C1–C6)・[../FINDINGS.md](../FINDINGS.md) §6
