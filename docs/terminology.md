# BomDD 用語集 (terminology)

本研究の用語を固定する。英語別名は将来の英語化・論文化のための補助であり、日本語本文では従来語を用いる。概念の全体像は [concept.md](concept.md) を参照。

## BOM 層

### E-BOM
**Engineering BOM / 設計部品表。** 論理部品の構成と、各部品の存在理由がどの仕様に紐づくか(責務↔仕様トレース)を持つ。部品は**核/表面で型分け**し、存在理由を型(`requirement / defect-class / constraint / external-knowledge / design-token`)で記録する。木でなく**グラフ**(横断部品=woven に owner/consumers を持たせる)。

### M-BOM
**Manufacturing BOM / 製造部品表。** 実現技術・非機能・**合否判断基準**・調達部品。受入基準に〔完全性(全数値/全フィールド規定)・無矛盾性・検査モダリティ列(L0–L3+golden)と承認者〕を必須化し、識別子・座標系の不変条件を明示する。製造工程(Routing)、Control Plan、FMEA を伴う。

### S-BOM <a id="s-bom"></a>
**Service BOM / Maintenance BOM / 保守部品表。**

> ⚠️ **本研究の S-BOM は、一般的な SBOM(Software Bill of Materials)ではない。** Service BOM / Maintenance BOM としての保守部品表を指す。OSS 依存一覧はその一部に過ぎない。S-BOM は「外部知識依存 × 受入深さ」を持ち、劣化イベント(ffmpeg 版・OS・デザイントークン・AI モデルの変化)を逆引きして「何が影響し、何を再検査し、交換・再製造が要るか」を導く。
>
> 用語衝突を避けるため、外部向けには **Service BOM(S-BOM)** と表記する。

PLM の価値は被覆でなく**絞り込み**(影響しない核を巻き込まない)。

### K-BOM
**Knowledge BOM / 知識部品表。** 要求 BOM とは別に、製造装置が参照する「外部ツール/設計の管理知識」(ffmpeg 文法パック、デザイントークン、外部ツール仕様)を部品化したもの。AI が一見「勝手に知っている」暗黙知を管理対象に変える。→ [method/k-bom-ffmpeg.md](../method/k-bom-ffmpeg.md)

## 核と表面

### 核
**Deterministic Core / 要求導出部品。** ドメイン代数・判定規則・幾何など、要求から導出可能で unit 検査でき、BOM から鋳造できる部品。

### 表面
**External Surface / 知識依存部品。** ffmpeg コマンド文法・画面の画素など、要求から導けず外部仕様/設計トークンの知識転記を要し、受入に execution/golden + 人間判断を要する部品。観測した 12 件のずるはすべてここで出た。

## 測定・工程

### ずる
**Manufacturing Gap / BOM 自己完結性違反。** AI が BOM・工程から導けず、慣習・暗黙知・原版記憶・未文書の判断で埋めた箇所。失敗ではなく**観測データ**。分類 C1–C6 は [method/cheat-taxonomy.md](../method/cheat-taxonomy.md)。

### 鋳造できる (castable)
**BOM-only reproducible.** 原版非開示の製造装置が BOM/工程のみから成果物を生成し、定義済み受入(unit/L2/L3/golden)を**手修正なしで通過**すること。比喩でなく、この操作的条件で測る。

### 受入の梯子
検査深さの段階: `L0 文字列 < L1 存在/終了コード < L2 メタデータ(ffprobe) < L3 内容/信号(PSNR/相関) < golden + 人間承認`。核 = unit、表面 = 領域別の深さ。L0/pixel-exact は過剰結合のため既定不採用(例外: 正規化シリアライズ/deterministic raster が製品特性の場合)。

### Control Plan
**製造条件表 + 検査計画。** 各受入基準(特性)ごとに、検査深さ・許容差・治具・承認者を持たせる表。→ [method/control-plan.md](../method/control-plan.md)

### FMEA
**Failure Mode and Effects Analysis。** M-BOM 前に部品の故障モードを列挙し、受入を狙い撃ちする(例: 音声座標系バグ)。

### マルチファクトリ (multi-factory)
同一 BOM を複数の製造装置に渡し、出力の分散(=決定性)を測る手法。本研究の multi-factory は完全独立ベンダではなく、**同一モデル系列内の複数装置/設定**(opus/sonnet/haiku)を指す。

### 品質の二軸
(1) **決定性** = 工場間ばらつき(low ほど BOM が出力を一意化)、(2) **正しさ** = 受入(L2/L3/golden)。**一致 ≠ 正しさ**(揃って間違う「共有暗黙知の罠」)。両軸を独立に検査する。

### As-Built BOM (v2 で導入済み)
実際に製造された成果物とその来歴(mbom_ref / routing_ref / AI モデル・モデル版 / inputs の sha256 / 成果物の sha256 / 検査結果 / ずる)。設計 BOM・製造 BOM と「実際に作られた構成」を分ける(AI 製造は同一 BOM でも完全同一とは限らないため)。SLSA provenance の拡張。v2 の別リポジトリ BomDD-WebApi-Sample(`loops/webapi-0*/as-built*.yaml`)で運用。

## 受入の2層と差分の帰属(v2: webapi-02)

### fixed oracle layer(固定オラクル層)
合否判定に使う固定の受入。**仕様化済み契約だけ**を比較する(status code・error code・状態・ID の pattern・冪等 replay の同一ID性 等)。ループ間で**不変**に保つ(同一ヤードスティック)。ID 具体値や日時小数秒は混ぜない(L0 過剰結合の回避)。

### exploratory probe layer(探索プローブ層)
**合否でなく観測**。BOM が値を固定していない次元(ID アルゴリズム・一意性・日時形式・応答スキーマのフィールド集合 等)の工場間分散を `exploratory_variance` として測る。固定オラクルに混ぜると「途中でオラクルを拡張した」ことになり改善効果測定が濁る。

### unspecified BOM residue(BOM未規定残渣)
仕様に書かれておらず、製造装置が自由に埋めた箇所。単一ティアでは慣習で揃って隠れ、**別ティアで露見しやすい**(共有暗黙知 C2)。例: `not_found` という code 名を BOM が規定せず、sonnet だけ `booking_not_found` を選んだ。

### specified contract miss(仕様契約の取りこぼし)
BOM/Control Plan が**明記した**契約を、低能力工場が外したもの=**工場能力**の問題(BOM の穴ではない)。K-BOM の価値の裏返し。例: haiku が「409=state conflict」「code=unauthorized」を取りこぼした。

> ばらつきを「AI ごとに精度が違う」で止めず、**BOM欠落(未規定残渣)/ 工場能力(仕様取りこぼし)/ 探索的未規定面**に切り分けるのが BomDD の成果。
