# Schema Candidates Index(スキーマ候補・索引 — draft)

> **ステータス**: draft。BomDD の方法論骨格を、**製品(製造される物)**と**観測ハーネス(測る仕掛け)**の2系統の候補表に分けて抽出した。本書は両者の関係と**境界物の所有規則**を束ね、**JSON Schema 化はまだしない**ことを宣言する。

## 1. 2つの候補表
| 系統 | ドキュメント | 何の構造か |
|---|---|---|
| **observation / measurement** | [observation-schema-candidates.md](observation-schema-candidates.md) | 固定オラクル・探索プローブ・等価規則・差分帰属・MeasurementCapability・cheat-log・metrics・FactoryRun |
| **product** | [product-schema-candidates.md](product-schema-candidates.md) | E/K/M-BOM・Control Plan(製品側)・Routing・As-Built・Service BOM |

なぜ分けるか: 本研究の最重要規律=**製品差分と観測ハーネス差分の分離**(FINDINGS §6.4)。Web/API・Saga で最も効いたのは「製品が間違ったのか、測定器が間違ったのか」を分けたこと。これを schema 候補段階で混ぜると、獲得した規律が弱くなる。**分割そのものが方法論の主張**。

なぜ observation を先に作ったか: BomDD の新規性が高いのは BOM のフィールド表(=最も予測可能な層)でなく、**AI 製造を測定可能にする規律**。observation 側が知的資産として重い。

## 2. 境界物(boundary artifacts)の所有規則 — 確定
境界をまたぐ概念は、**溶かさず分割して両側に持つ**。越境参照は最小本数に絞る。

| 境界物 | product 側 | observation 側 | 越境参照 |
|---|---|---|---|
| **Control Plan** | `characteristic / classification / acceptance_ref / required_depth_ref`(何を保証するか) | `oracle / probe / equivalence / do_not_compare / diff attribution`(どう測り・何を比較しないか) | 張らない(概念分割) |
| **required_depth(L0–L3+golden)** | 特性への**深さ割当** | 梯子の**定義 + 実装治具**(L3 信号解析器 等) | 張らない(分担) |
| **As-Built ↔ FactoryRun** | `AsBuilt`(何を・どのモデル・どのプロンプトで作ったか) | `FactoryRun`(どの工場が何点) | **`FactoryRun.as_built_ref` の1本のみ**(観測→製品) |

**規律**: 越境は `FactoryRun.as_built_ref` 1本に限定(観測→製品の単方向)。逆向き(製品→観測)は張らない。他の境界物は概念分割で両側に持つ。

## 3. 直交する2軸(observation 内で確定した分類)
- **DiffAttribution**(差分はどこから来たか): product 帰属(確定3=`unspecified_bom_residue` / `specified_contract_miss` / `exploratory_unspecified_surface`)+ harness 帰属(候補2=`observer_representation_diff` / `observer_l0_overcoupling`)。
- **MeasurementCapability**(その差分を観測できる深さ・治具・承認者が足りるか): `unmeasurable / under-specified-oracle / insufficient-depth / human-approval-required` → `adequate`。**v1 C4「受入不能」はここ**。
- 両者は直交。「差分はどこから来たか」と「その差分を観測できるか」を混ぜない。

## 4. v1 cheat-taxonomy(C1–C6)の行き先(横断統合の要約)
| v1 C コード | 行き先 |
|---|---|
| C2 暗黙知(製品) | DiffAttribution `unspecified_bom_residue` |
| C2 暗黙知(検査器・新) | DiffAttribution harness 候補(`observer_*`)。**C2 が検査器に転移**(saga 新パターン) |
| C4 受入不能 | **MeasurementCapability**(別軸) |
| C1 表現ギャップ | product As-Built |
| C3 / C5 / C6 | 構造的に塞いだ(product/工程側)。観測スキーマに現れにくい |

## 5. JSON Schema 化への道(まだしない)
昇格条件(=`schemas/draft/*.json` を作ってよくなる時):
1. **共通項のテンプレ・バイアス**が晴れること。product 側の「強い候補」が著者の書き癖でなく不変だと言える根拠(第三者 or N≥4 ドメイン)。
2. **候補扱いの分類が安定**すること(harness 帰属2 / MeasurementCapability state 4 が新ドメインで増えない、または増え方が収束)。
3. **境界物の所有規則が運用で破綻しない**ことの確認。

それまでは `.md` 候補表で留め、硬化しない(早すぎる形式化=片ドメイン構造の焼き込み回避)。`draft` 化する時も名前を `draft` にし、規格でなく検証対象だと明示する。

## 6. ステータス
- [x] observation-schema-candidates.md(C4→MeasurementCapability・harness 候補化・越境1本 を反映済)
- [x] product-schema-candidates.md(delta 主役・共通項のテンプレバイアス明記)
- [x] schema-candidates-index.md(本書)
- [ ] JSON Schema draft(昇格条件 §5 を満たすまで保留)
