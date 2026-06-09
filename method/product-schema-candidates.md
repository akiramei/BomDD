# Product Schema Candidates(製品スキーマ候補 — draft / まだ JSON Schema ではない)

> **ステータス**: draft / candidates only。製造される**物**(E/K/M-BOM・Control Plan の製品側持ち分・Routing・As-Built・Service BOM)の構造を、3ドメイン(MoviePad / Web-API / 分散Saga)から抽出した候補表。硬化(`schemas/draft/*.json`)はこの段階では**しない**。
>
> 対になる **observation 側**(固定オラクル・探索プローブ・等価規則・差分帰属・MeasurementCapability・metrics)は [observation-schema-candidates.md](observation-schema-candidates.md)、両者の関係と境界物の所有規則は `schema-candidates-index.md` に分ける(未作成)。

## 0. 読み方の注意 — 共通項より delta を見る

product 側は **同一著者が同一テンプレ(核/表面・Control Plan・K-BOM・As-Built という語彙)で3回書いた**層なので、共通フィールドが残るのは半ば当然で、**「3ドメインを生き延びた」の証拠力は見た目より弱い**。

したがって本ドキュメントは、各エントリで:
- 【共通=仮説】= 3ドメインで残った。方法論の不変仮説だが、テンプレ由来の可能性を割り引く。
- 【domain delta=証拠】= **各ドメインが core/M-BOM に成長を強制した箇所**。ここが本当の情報量。生き残り・成長の証拠。
- 【未昇格】= まだ共通化を主張しない候補。

を分ける。**delta を主役にする。** → §2 の共通フィールド表は**足場**であり、§3「各ドメインが core/M-BOM/K-BOM に強制したもの」が本ドキュメントの**本体**。共通項だけ見て満足しない。

## 1. 第一原理 — 核 / 表面の型分け(product の組織原理)

すべての E-BOM 部品は2型に分かれる([bomdd-method-v1.md](bomdd-method-v1.md) §0):
- **核(core)**: 要求から導出可・unit で検査・**鋳造できる**。`rationale_type = requirement`。
- **表面(surface)**: 外部ツール文法・画面の見た目=外部/設計知識の転記が必須。出所(ツール仕様/デザインシステム)へトレース必須。変更は defect でなく**知識更新**。

この型が product スキーマの最上位の分類軸。「ずるは表面で出る」(観測した範囲)。

## 2. Candidate Entities(候補エンティティ)

### 2.1 E-BOM item(設計部品)
```
EbomItem
  id
  classification      : core | surface                         【共通=強い候補(3ドメインで検証された第一原理)】
  rationale_type      : requirement | defect-class | constraint
                      | external-knowledge | design-token       【概念=共通 / enum=候補・未昇格(MoviePad 由来。全値が全ドメインで出たわけでない)】
  requirement_refs    : 核が紐づく要求(core 必須)              【共通=強い候補(core にほぼ定義的)】
  external_source_ref : 表面の出所(ツール仕様/デザインシステム)【共通(表面のみ)】
  kbom_refs           : 参照する知識部品(K-BOM)                【候補・未昇格(K-BOM は MoviePad で最も検証。Web/API・Saga は余地どまり)】
  acceptance_refs     : 受入観点(→ M-BOM AC / Control Plan)    【共通=強い候補】
  graph_edges         : owner / consumers(woven 部品の横断辺)  【共通=仮説】
```
- **共通=強い候補**(過信しない範囲で): `id` / `classification(core|surface)` / `requirement_refs` / `acceptance_refs`。とくに `classification` は3ドメインで検証された第一原理。
- **候補・未昇格(テンプレ由来を疑う)**: `rationale_type` の enum(MoviePad 由来、全ドメインで全値は出ていない)/ `kbom_refs`(K-BOM は MoviePad の ffmpeg パックで最も検証され、Web/API・Saga では未充足)。不安なものはここへ落として硬くする。
- **木でなくグラフ**: 横断(woven)部品に owner/consumers(CHEAT-002)。
- **domain delta(証拠)**:
  - MoviePad — `design-token`(レイアウト定数・配色)、`external-knowledge`(ffmpeg コピー白名簿)が表面型として**新設を強制**(CHEAT-007/010)。
  - Web/API — 冪等 `fingerprint` 構成フィールドの列挙が core に必要(未列挙→customerId 次元の機能差 blocker)。要求 REQ-003 を core が運ぶ。
  - Saga — **補償規則(payment 失敗→在庫解放 / shipment 失敗→在庫解放+支払い void)が核**。状態遷移が要求由来の core。

### 2.2 K-BOM item(知識部品)
製造装置が参照する外部/設計知識を、要求 BOM と**別に**管理(Loop4)。C2 暗黙知を管理対象化する装置。
```
KbomItem
  id
  knowledge_kind      : tool-grammar | design-system | domain-convention 【共通=仮説】
  source              : 出所(ツール仕様 URL / デザインシステム / 規約)  【共通】
  version             : 版(S-BOM が劣化逆引きに使う)                    【共通=仮説】
  consumers           : この知識を参照する表面部品                       【共通】
```
- **共通**: `id` / `source` / `version` / `consumers`。「K-BOM に無い判断は CHEAT として記録」。
- **domain delta(証拠)**:
  - MoviePad — **ffmpeg 文法パック**([k-bom-ffmpeg.md])。K-BOM の原型・最も厚い実例。3工場実験で K-BOMなし=全次元分岐 / あり=ばらつき0。
  - Web/API — HTTP 規約・エラーコード語彙(`not_found` 名は未規定で sonnet が露見=C2)。K-BOM 化の余地。
  - Saga — event envelope 規約・inbox key 規約。締めた seed BOM が低能力ティアの取りこぼしを防いだ=K-BOM 価値の裏側(saga-02 で haiku も 0)。
- **未昇格**: `version` の粒度(semver / commit / 日付)はドメインで割れる。K-BOM の正規形は要追加観測。

### 2.3 M-BOM unit(製造部品)
```
MbomUnit
  id
  interface_contract  : 公開インターフェース契約                        【共通】
  acceptance:
    completeness       : 全数値/全フィールド規定(丸め・継承・既定値)   【共通=強い候補】
    consistency        : AC 同士が矛盾しないか(識別子ポリシー等)        【共通=強い候補】
    control_plan_ref   : → Control Plan(深さ+許容差+承認者)            【共通=強い候補】
  invariants          : 関係の不変条件(識別子採番 / 座標系)            【共通。中身は domain delta】
  fmea_refs           : 先行 FMEA で列挙した故障モード                   【共通=仮説】
```
- **共通(強い候補)**: 受入3条件(完全性 / 無矛盾性 / Control Plan 列)は3ドメインで効いた(CHEAT-004/005/009/011)。
- **domain delta(証拠 — `invariants` の中身がドメインで全く違う)**:
  - MoviePad — **座標系の不変条件**(シーク時の音声は絶対時刻=seekBase。CHEAT-008 音ズレ実バグ)。表面バグの主因。
  - Web/API — **識別子採番ポリシー + 冪等 fingerprint の完全性**(未規定次元が「テスト緑でも乖離」を生む)。
  - Saga — **at-least-once + 冪等 consumer(inbox key=handler+eventId)+ retry/dead-letter(maxAttempts=3)+ ordering**。非同期固有の不変条件群を M-BOM が運ぶ。
- → `invariants` は**共通フィールド・中身は完全に domain delta**。「不変条件を明示せよ」が方法論、何を明示するかがドメイン圧の証拠。

### 2.4 Control Plan(製品側の持ち分のみ)
Control Plan は**境界をまたぐ artifact**。product 側が持つのは「何を保証するか」:
```
Control Plan (product side)
  characteristic       : 保証する特性/受入観点
  classification       : core | surface(なぜこの深さが要るかの根拠)
  acceptance_ref       : 対応する M-BOM AC
  required_depth_ref   : 必要な検査深さの割当(梯子の定義は observation 側を参照)
```
- **梯子の定義と実装**(L3 信号解析器 等の治具)は **observation 側**([observation-schema-candidates.md] §6)。product 側は **`required_depth_ref`(割当=参照)** だけを持つ。`oracle / normalization / equivalence / do_not_compare` は observation 側(§4.8)に置き、product 側へ戻さない。
- 観測側持ち分(oracle / probe / equivalence / diff attribution)は observation §4.8。

### 2.5 Routing step(工程)
```
RoutingStep
  id
  step_kind           : reverse | manufacture | inspect | finish              【共通=仮説】
  factory_isolation   : 製造は M-BOM+工程のみ供与(原版/正解非開示)         【共通=規律】
  cheat_report        : 「BOMに無く慣習で埋めた箇所」の網羅報告を義務化       【共通=規律】
  work_order_ref      : 製造指示                                              【共通】
  jigs_ref            : 治具・測定器(execution harness / golden gen / L3 解析)【共通】
```
- **共通(規律)**: 製造装置の隔離・ずる報告の義務化・マルチファクトリ・治具の成果物管理(Loop1〜5)。これは product 構造というより**工程規律**で、3ドメインで最も安定。
- **domain delta(証拠)**:
  - 全ドメイン共通で「リバース工程(双方向トレース+カバレッジ監査)」を入口に置く(Loop7, CHEAT-001)。
  - Saga — 製造の隔離が「clean サブエージェント(model 上書きでティア分け)」として運用確立。

### 2.6 As-Built(製造来歴 — observation との join 点)
観測済み実行の記録。SLSA provenance の AI 製造拡張([bomdd-core-concept])。
```
AsBuilt
  id
  mbom_ref            : 何を作ったか                          【共通】
  routing_ref         : どの工程で                            【共通】
  ai_model            : 製造装置(opus/sonnet/haiku ...)       【共通=証拠】
  prompt_hash         : 投入プロンプトのハッシュ              【共通=証拠】
  context_refs        : 供与した BOM/work-order(NC データ)    【共通】
  artifacts_sha256    : 成果物のハッシュ                      【共通】
  inspections         : 受入結果                              【共通】
  cheats              : 申告されたずる                        【共通】
```
- **越境**: As-Built は observation 側 `FactoryRun.as_built_ref` から指される(**観測→製品の唯一の越境参照**)。FactoryRun=観測(どの工場が何点)、As-Built=製品(何を・どのモデル・どのプロンプトで)。
- **domain delta(証拠)**: v2 で初めて機械可読 YAML 化(webapi `as-built-factory0{1,2,3}.yaml` / saga `as-built.yaml`)。MoviePad(v1)は非形式的記述。`ai_model` / `prompt_hash` はマルチファクトリ(N≥2)で初めて意味を持った。

### 2.7 Service BOM(保守部品 — PLM 層)
表面部品の劣化を追う([s-bom-template.md], Loop6)。**Software の SBOM(依存台帳)とは別物=Service/保守 BOM**。
```
ServiceBom
  id
  surface_part_ref    : 監視対象の表面部品                          【共通】
  external_dep         : 依存する外部知識 + version(K-BOM ID+ver)   【共通】
  reinspect_on_change : 変更時に再実行する検査(深さ付き)           【共通】
  ai_model_drift       : AI 製造装置のモデル変更による再製造差分      【共通=仮説】
  replacement_decision : 交換不要 / K-BOM更新のみ / 再製造必要        【共通】
```
- **共通**: 劣化イベントを逆引きし、影響部品・再検査深さ・交換判断を導く。PLM の価値は被覆でなく**絞り込み**(影響しない核を巻き込まない)。
- **domain delta / 未昇格**:
  - MoviePad — Loop6 で K-BOM 知識更新イベント注入による**概念実証**(影響を6部品中1へ絞込)。実 ffmpeg 更新でなく注入。
  - **個体別 As-Maintained 構成**([bomdd-open-questions] #2)は3ドメインとも**未実装**。「誰に通達するか」を出す effectivity 管理は最大の難所で、**未昇格の最重要 open question**。

## 3. 各ドメインが core/M-BOM に強制したもの(delta サマリ — 本ドキュメントの主役)

| ドメイン | core に強制 | M-BOM invariants に強制 | K-BOM に強制 |
|---|---|---|---|
| MoviePad(同期GUI) | design-token / external-knowledge 型 | **座標系**(seekBase 絶対時刻) | **ffmpeg 文法パック**(原型) |
| Web/API(同期HTTP) | 冪等 fingerprint フィールド列挙 | 識別子採番 / fingerprint 完全性 | HTTP 規約・エラーコード語彙 |
| 分散Saga(非同期) | **補償規則・状態遷移** | **inbox key / at-least-once / retry / ordering** | event envelope 規約・inbox 規約 |

→ 「核/表面の型分け」「受入3条件」「不変条件を明示せよ」という**枠は共通(方法論)**だが、**埋まる中身は完全にドメイン圧**。これが「同一テンプレを3回当てた」では説明できない、生き残り構造の証拠。共通フィールド表だけ見ると見落とす部分。

## 4. Cross-boundary(observation との境界 — index で確定)
- **越境参照は1本**: `FactoryRun.as_built_ref`(観測→製品)。逆向き(製品→観測)は張らない。
- **Control Plan は分割**: product=`characteristic / classification / acceptance_ref / required_depth_ref`、observation=`oracle / probe / equivalence / diff attribution`。
- **required_depth は分担**: 割当=product の `required_depth_ref`(本書 §2.4)、梯子定義+治具=observation。
- 詳細な所有規則は `schema-candidates-index.md` で確定する。

## 5. Not Yet Promoted / Open Questions(JSON Schema 化の前に)
- **個体別 Service BOM(effectivity 管理)**: 顧客/デプロイ個体ごとの As-Maintained 構成。3ドメインとも未実装。PLM 実用価値の核だが**最も未成熟**([bomdd-open-questions] #2)。
- **K-BOM の version 粒度**: semver / commit / 日付 がドメインで割れる。正規形要追加観測。
- **工程は M-BOM の一部か分離か**([bomdd-open-questions] #1): 本ドラフトは Routing を別エンティティに分離したが、「交換=同じ部品を新工程で再製造」を表すには分離が良い、を採用。要確認。
- **NFR の置き場所**([bomdd-open-questions] #3): 目標値=E-BOM 側 / 実現+検証=M-BOM 側 の分割案。未確定。
- **共通項のテンプレ・バイアス**: §2 の「強い候補」が本当に不変か、それとも著者の書き癖か。第三者・別ドメイン(N≥4)での適用が要る(今は実施しない)。

## 6. 関係
- 対: [observation-schema-candidates.md](observation-schema-candidates.md)(測定ハーネス側)
- 索引: `schema-candidates-index.md`(境界物の所有規則・JSON Schema 化はまだしない宣言)
- 根拠: [bomdd-method-v1.md](bomdd-method-v1.md) / [k-bom-ffmpeg.md](k-bom-ffmpeg.md) / [s-bom-template.md](s-bom-template.md) / [control-plan.md](control-plan.md) / [../FINDINGS.md](../FINDINGS.md) §4・§6
