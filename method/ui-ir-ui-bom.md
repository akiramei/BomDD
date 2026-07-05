# UI-IR / UI-BOM Candidate Extension

> **ステータス**: candidate / 未実証拡張。
> 本書は、HTML+JavaScript+CSS で作られた実行可能 UI モックを、BomDD の E-BOM / M-BOM / S-BOM へ接続するための入口モデルである。既存の method-v1 を置き換えず、フォワード開発や UI 移植案件で使う前段の観測・追跡層として扱う。

## 1. 位置づけ

UI モックは、BOM そのものではなく **実行可能な UI-CAD 表現**である。

```
HTML+JavaScript+CSS mock
  -> UI-IR
  -> UI-BOM
  -> Design System BOM
  -> E-BOM / M-BOM / Control Plan / S-BOM
```

- **UI-IR**: 自由に作られた UI モックから抽出する観測用・追跡用・BOM 化用の中間表現。設計を縛る原本ではない。
- **UI-BOM**: UI-IR から BOM 対象だけを昇格した候補部品表。HTML タグではなく、画面・領域・部品候補・出現・操作・入力・状態を扱う。
- **Design System BOM**: UI-CAD が要求する Card / CTA / Chip / Badge / IconButton などのデザインシステム部品を、E-BOM surface 部品と K-BOM design knowledge の組として明示する補助台帳。
- **E-BOM 連携**: UI-BOM の候補品目を、要求・仕様・表示契約・設計トークン・業務概念へ接続し、正式な E-BOM 品目へ昇格する。

HTML の DOM 構造をそのまま部品表にしない。`div` や `span` は、業務意味・操作・状態・入力・テスト観点を持つ場合だけ BOM 候補にする。

注意: UI-IR 単体は設計原本ではない。一方で、ユーザーが承認した **UI-CAD パッケージ(モック + UI-IR + UI-BOM + trace map)** は、製造品を検査する設計原器として扱える。つまり「UI-IR に合わせて設計する」のではなく、「承認済みモックから抽出した CAD パッケージで製造品を検査する」。

## 2. 基本原則

1. **UI-IR は原本ではなく観測表現**  
   デザイナーやユーザーは自由に UI モックを作る。AI はその出力を読み、BOM 化に必要な意味を抽出する。UI-IR に合わせて UI を作らせない。

2. **UI-BOM は HTML タグ一覧ではない**  
   `button` は「ボタンタグ」ではなく「保存操作」「タグ追加操作」のような業務操作として読む。装飾・余白・スタイル調整だけの要素は `decorative` / `nonBom` に落とす。

3. **設計意図は nonBom ではなく designIntent**  
   `DESIGN DIRECTION`、原則カード、COLOR / TYPE / ROW / STATE のトークンデモ、部品言語の説明は、アプリ画面そのものではなくても BOM 外に捨てない。これは設計憲章であり、`designIntent` として抽出して E-DESIGN / K-DESIGN / Control Plan へ接続する。

4. **仮品番で追跡する**  
   正式品番は E-BOM 以降で確定する。UI 抽出段階では `TMP-UI-*` の仮品番を使い、AI 再生成や差分の中で同じ UI 候補を追跡する。

5. **既存 stable id を優先する**  
   HTML に `data-ui-id` / `data-ui-temp-part-no` があれば優先する。意味が変わらない限り変更しない。

6. **不明点を仕様化しない**  
   推測は `confidence` を付け、未解決は `unresolved-questions.md` へ出す。確認なしに正式仕様・正式品番へ昇格しない。

## 3. 抽出対象

### BOM 候補にするもの

- 画面、主要領域、パネル、フォーム
- 入力項目、ボタン、メニュー、ナビゲーション
- 一覧、テーブル、カード、ツリー、タブ、モーダル
- 状態表示、エラーメッセージ、空状態、読み込み状態
- 検索条件、フィルタ、ソート
- 業務操作、API やデータ操作に関係する UI 要素
- ドメイン概念に対応する UI 要素
- 仕様・受入・テスト対象になりそうな UI 要素

### BOM 対象外にするもの

- 装飾用 `div`
- 余白調整用 wrapper
- CSS 調整だけの container / span
- 影・角丸・罫線だけの要素
- アイコン位置調整だけの要素
- 意味を持たない空要素

ただし装飾要素でも、アクセシビリティ、状態表示、ユーザー操作、業務意味を持つなら BOM 候補にしてよい。

## 4. ID と仮品番

### `data-ui-id`

人間が読める stable id とする。

```
screen.tag-management
region.tag-palette
region.hierarchy-editor
component.tag-card.region
action.tag.add
input.tag.search
state.tag-card.dragging
modal.tag.delete-confirm
```

推奨命名:

```
screen.<画面名>
region.<領域名>
component.<部品名>.<出現名>
button.<対象>.<操作>
action.<対象>.<操作>
input.<対象>.<項目>
state.<対象>.<状態>
modal.<対象>.<用途>
```

### 仮品番

| 接頭辞 | 意味 |
|---|---|
| `TMP-UI-SCR-0001` | 画面 |
| `TMP-UI-REG-0001` | 領域 |
| `TMP-UI-CMP-0001` | UI コンポーネント候補 |
| `TMP-UI-OCC-0001` | UI 部品の出現 |
| `TMP-UI-ACT-0001` | 操作 |
| `TMP-UI-INP-0001` | 入力項目 |
| `TMP-UI-STA-0001` | 状態 |
| `TMP-UI-DOM-0001` | 業務概念候補 |

同じ UI 候補には同じ仮品番を維持する。正式 E-BOM 品番へ昇格したら、trace map に `ebomItemRef` を追記する。

## 5. 成果物

テンプレートは [templates/ui-mock-extraction/](templates/ui-mock-extraction/) に置く。

| 成果物 | 役割 |
|---|---|
| `ui-ir.json` | HTML モックから抽出した観測・追跡用中間表現 |
| `ui-bom.json` | UI-IR から BOM 対象だけを昇格した候補部品表 |
| `ui-trace-map.json` | HTML selector / UI-IR / UI-BOM / E-BOM 候補の対応表 |
| `design-intent.md` | DESIGN DIRECTION / 原則 / COLOR・TYPE・ROW などの設計意図 |
| `extraction-report.md` | 抽出結果、BOM 対象理由、対象外理由、E-BOM 連携候補 |
| `unresolved-questions.md` | 仕様・UI 設計・E-BOM 昇格前に確認すべき事項(裁定台帳の open ビュー) |
| [templates/37-ui-rulings.yaml](templates/37-ui-rulings.yaml) | 裁定台帳。open / ruled / rejected / superseded を保持する設計資産(§13) |
| [templates/36-ui-dictionary.yaml](templates/36-ui-dictionary.yaml) | 文脈スコープ付き用語辞書。裁定からのみ成長する再利用資産(§13) |

必要に応じて、HTML に `data-ui-id` / `data-ui-temp-part-no` を付けた annotated HTML を追加してよい。

## 6. 抽出手順

1. **画面を特定する**  
   HTML 全体と機能説明から画面単位を特定し、`screen.*` と `TMP-UI-SCR-*` を与える。

2. **主要領域を抽出する**  
   ヘッダー、サイドバー、検索条件、一覧、詳細、編集パネル、タグパレット、階層ツリーなどを抽出する。

3. **UI 部品候補を抽出する**  
   再利用されそうか、名前を付けられるか、業務意味があるか、状態や操作を持つか、入力・出力・テストに関係するかで判断する。

4. **部品マスターと出現を分ける**  
   例: `TagCard` は部品マスター、`地域タグカード` / `季節タグカード` は出現。マスターは `TMP-UI-CMP-*`、出現は `TMP-UI-OCC-*`。

5. **操作を抽出する**  
   保存、検索、追加、削除、編集、ドラッグ、フィルタ適用などを `action.*` として扱う。クリック以外の操作も対象にする。

6. **入力項目を抽出する**  
   検索欄、フォーム、セレクト、チェックボックス、数値範囲、日付範囲を `input.*` として扱う。

7. **状態を抽出する**  
   選択中、編集中、ドラッグ中、読み込み中、エラー、無効、保存済み、空状態を `state.*` として扱う。

8. **業務概念を抽出する**  
   機能説明と表示文言から `Tag` / `View` / `Product` / `Order` などの概念を抽出し、UI 部品・操作・入力に関連付ける。

9. **UI-BOM を生成する**  
   UI-IR から BOM 対象だけを昇格する。装飾・余白・意味なし wrapper は `unmodeledElements` と trace map の `nonBom` に残す。

10. **E-BOM 連携候補を出す**  
    UI-BOM 品目ごとに、E-BOM 昇格候補、要求・仕様・表示契約・Control Plan 候補、K-BOM 候補を記録する。

11. **designIntent を抽出する**  
    DESIGN DIRECTION / 原則カード / COLOR・TYPE・ROW・STATE などを `design-intent.md` に抽出し、E-DESIGN / K-DESIGN / Control Plan の基盤にする。`アプリ画面ではない` という理由だけで nonBom にしない。

12. **Design System BOM 候補を出す**  
    UI-CAD が要求する Card / CTA / TypeChip / ConditionChip / CandidateValueChip / Badge / IconButton / SectionHeader / HelpBox / DragHandle などを抽出し、`35-design-system-bom.yaml` の候補へ接続する。これを省くと、実機が素の panel/text/button に退化しても E-BOM 上は検出しづらい。

13. **未解決事項を出す**  
    削除確認、保存タイミング、権限、バリデーション、検索条件、variant 境界などを推測で確定せず質問化する。

## 7. E-BOM への昇格規則

UI-BOM は候補であり、E-BOM ではない。昇格時は次を確認する。

| UI-BOM 種別 | E-BOM での扱い |
|---|---|
| `screen` | 表示契約または複数 E-BOM item の上位構成候補 |
| `region` | UI surface 部品または display contract の単位 |
| `component` | 再利用可能な surface 部品候補。デザインシステム依存があれば K-BOM 参照 |
| `componentOccurrence` | E-BOM 品目ではなく、trace / display contract の出現として扱うことが多い |
| `action` | 仕様・要求・Control Plan に接続。業務操作なら core / surface の境界を確認 |
| `input` | データ項目・バリデーション・API 契約へ接続 |
| `state` | 表示パリティ、受入観点、FMEA 故障モードへ接続 |

昇格判断の問い:

- その候補は独立に再製造・交換・受入できるか。
- その候補は要求または表示契約にトレースできるか。
- 変更時に影響分析の単位として意味があるか。
- デザインシステム、アクセシビリティ、UI フレームワーク、API 契約など K-BOM / S-BOM で追うべき外部知識依存を持つか。
- ただの出現か、再利用可能な部品マスターか。

## 8. Control Plan / S-BOM への接続

UI-BOM の表面候補は、受入と保守に接続する。

- **Control Plan**: DOM / アクセシビリティツリー / スクリーンショット / golden+承認者で、表示要素・操作・状態の存在と意味一致を検査する。pixel-exact は既定不採用。
- **K-BOM**: デザインシステム、コンポーネントライブラリ、アクセシビリティ規約、UI フレームワーク、ブラウザ互換、イベント慣習を管理する。
- **S-BOM**: デザイントークン変更、UI ライブラリ更新、ブラウザ挙動変更、AI モデル更新により再検査・再製造が必要な UI surface 部品を逆引きする。

## 9. 実プロジェクトからの追補: Visual Gap と Design System BOM

実プロジェクトで、CAD(モック + UI-IR/UI-BOM)と製造品(実機)を視覚突合した結果、UI-IR/UI-BOM だけでは塞げない新しい問題が見えた。

### 9.1 観測された失敗型

- **S1 欠落 / 構造**: CAD にある情報や構造が実機に無い。例: 階層の条件が色分けチップでなく muted 素テキストになる、パレットの候補値/範囲表示が欠落する、中央階層のカードコンテナが無い、作成ダイアログの2カラム+プレビュー帯が単一縦カラムになる、親行の型チップが無い。
- **S2 設計言語**: Card / CTA / 色付き型チップ / 条件チップ / アイコンボタン / 件数 / 凡例 / HOME ピルなど、CAD のデザイン言語を構成する部品が実機に存在しない。
- **S3 データ分散レイアウト**: 部品は存在し、モックが描く*その1状態*では正しいが、データが変わると崩れる。例: 下部バーのカウンタ `1/32` は正しく中央だが、`10/32` で桁が増えると中央のナビボタンがずれる(可変幅の兄弟が中央要素の中心を駆動していた)。任意長ファイル名・件数・空状態でも同型。

S1/S2 は「**無い**」問題だが、S3 は「**在るが契約が未記述**」の問題である。モックも単一 golden スナップショットも*1つのデータ値*しか持たないため、この型は両者の構造的盲点に落ちる。これは「見た目の微差」ではなく、**レイアウト不変条件(designIntent)とデータ分散(contentVariance)が UI-IR に未モデル化だった**ことに起因する製造不適合である。E1〜E7 の業務スライスが正しくても、E-DESIGN-028 / K-DESIGN 相当の Card / CTA / Chip / Badge / IconButton などの surface 部品が無いと、実機は薄い素実装に退化する。

### 9.2 追加するゲート

UI-CAD を使った案件では、Phase 3 と Phase 5 に次を追加する。

1. **Design System BOM gate**  
   `35-design-system-bom.yaml` に、UI-BOM の surface item が必要とする design parts を列挙する。`coverage_status` が `covered` または理由付き `out-of-scope` でない item は製造へ進めない。

2. **Visual Gap Analysis**  
   製造後に `43-visual-gap-analysis.md` を作り、CAD と実機を突合する。S1/S2 は cosmetic ではなく blocker として扱い、`design_system_part_missing / display_contract_gap / oracle_gap / manufacturing_miss` のいずれかへ帰属する。

   推奨運用は **golden-in-the-loop**: 反復ごとに実機スクリーンショットを M1/M2/M3 などの CAD スクリーンショットと突合し、S1 を先に潰してから S2 の design system 適用へ進む。

3. **CAPA への逆流**  
   Design System BOM が原因なら、直接 UI コードを直さず、`35 / 30 / 31 / 33 / 40` を同期して fresh factory で再製造する。

4. **データ分散ゲート(S3 予防)**  
   UI-IR 抽出時に、レンダ幅がデータで変わる部品出現へ `contentVariance`(値域・境界状態=最小幅 / 最大幅 / 空)を、その部品が属する領域へ `layoutInvariants`(`TMP-UI-LIV-*`。例「中央クラスタは領域全幅基準で中央・兄弟幅に不変」)を記述する。  
   - **golden は IR 由来の境界状態で撮る**。初期1枚でなく、IR が宣言した *最大幅 / 空* 状態を必ず突合する(「数字が増えたら?」を勘でなく IR 駆動にする)。  
   - 不変条件は **K-BOM(K-DESIGN / K-AVALONIA 規律)へ昇格**し、「可変幅の兄弟が中央/固定要素の中心を駆動しない(DockPanel 残余中央等の antiPattern 禁止)」を恒久規律として一般化する。  
   - UI-IR は静的記述でレイアウトを実行しない。強制はレビュー(契約突合)か、将来のデータ状態別レンダリングテストによる。IR は予防を *specifiable・repeatable* にするが、自動防止そのものは与えない。

### 9.3 新しい差分帰属

| 帰属 | 意味 | 是正 |
|---|---|---|
| `design_system_part_missing` | CAD が要求する Card / CTA / Chip 等が E-BOM/K-BOM/Design System BOM に無い | 35 を追加し、E-DESIGN-* / K-DESIGN-* / Control Plan へ同期 |
| `design_system_not_applied` | 部品は BOM にあるが対象 surface への適用 matrix が無い | 35 coverage_matrix と 30 display_contract_refs を補正 |
| `display_contract_gap` | CAD に見える情報・値・範囲・件数・凡例が display contract に落ちていない | 20 / 30 / 33 / 41 を補正 |
| `visual_manufacturing_miss` | BOM と検査は十分だが工場が実装で外した | manufacturing miss として fresh factory で再製造 |
| `layout_invariant_gap` | 部品は在るが、データ分散(桁数・名長・件数・空)で崩れる。`contentVariance` / `layoutInvariants` が UI-IR に無い(S3) | UI-IR に不変条件と境界状態を追記 → K-BOM(K-AVALONIA)へ昇格 → golden を境界状態で再突合 |

## 10. やってはいけないこと

- すべての `div` / `span` を BOM 品目にする。
- HTML タグ名だけで UI 部品を判断する。
- 装飾要素を大量に UI-BOM へ入れる。
- 推測した仕様を確定事項として扱う。
- 正式品番を勝手に採番する。
- UI-IR を設計原本として扱う。
- UI-CAD の Card / CTA / Chip / Badge / IconButton を「ただの見た目」として BOM 対象外にする。
- 視覚ギャップを実機側の手直しだけで塞ぎ、Design System BOM / E-BOM / K-BOM / Control Plan へ逆流しない。
- モックや golden の*1状態*を全状態の代表として扱い、データ分散(桁数・名長・件数・空)でのレイアウト崩れを未モデル化のまま放置する(S3)。
- 可変幅の兄弟要素が中央/固定要素の中心位置を駆動する実装(DockPanel 残余空間中央など)を、`layoutInvariants` で禁止せず放置する。
- 不明点を未解決事項に出さず埋める。
- 既存 stable id を理由なく変更する。
- blocking の open 裁定を残したまま E-BOM / M-BOM へ昇格する(gate G3)。
- 裁定の裏付け(source_rulings)なしに辞書エントリを作る、または scope を広げる(gate G4)。
- 辞書ヒットを裁定台帳に記録せず final action を確定する(来歴の分散)。
- 抽出工程の失敗をメガプロンプトへの追記だけで直す(§14 の還流先規律に反する)。

## 11. AI への指示

実際に AI へ渡すプロンプトは [prompts/ui-mock-to-ui-bom.md](prompts/ui-mock-to-ui-bom.md) を使う。出力は次の順で揃える。

1. 抽出概要
2. `ui-ir.json`
3. `ui-bom.json`
4. `ui-trace-map.json`
5. `extraction-report.md`
6. `unresolved-questions.md`

> **経過措置**: 本プロンプトは一発変換(Raw 抽出+意味付与+質問生成の混載)であり、§12 の工程分離が完成するまでの経過措置である。raw 抽出治具(`ui-extract.py`)導入後は、決定的抽出を治具に移し、プロンプトは意味候補付与と質問生成に縮小する。失敗知見をこのプロンプトへ無限に追記しない(還流先は §14)。

## 12. 工程分離原則(candidate)

UI-CAD 前工程の設計原則を次の 3 行に固定する。

```text
機械で決まる事実は、AI に推測させない。
AI が出すのは、意味候補・根拠・未裁定質問である。
最終事実になるのは、辞書ヒットまたは裁定済みレコードだけである。
```

工程と成果物は 5 層に分離する。

```text
mock.html
  ↓ 決定的抽出(ui-extract.py — 未実装。導入までは §11 の一発変換で代替)
ui-ir.raw.json      … HTML から機械的に確定できる事実(stable id は DOM 由来で決定的に採番)
  ↓ AI 意味付与
ui-ir.json          … 意味候補+confidence+根拠。候補であり製造入力ではない
  ↓ 裁定/辞書解決
37-ui-rulings.yaml + 36-ui-dictionary.yaml
  ↓ 昇格(裁定ゲート合格時のみ)
ui-bom.json         … 製造へ流せる確定済み候補部品表
  ↓
E-BOM / M-BOM / Control Plan / S-BOM
```

- `confidence` は製造許可ではなく、レビュー優先度にだけ使う。
- AI は raw IR に存在しないノードを作ってはならない。final action を確定してはならない。曖昧な意味は未裁定質問として出す。
- 工程を 1 つのメガプロンプトに混載すると、失敗のたびにプロンプトが太り、職人芸が増える(§14)。

## 13. 裁定台帳と文脈付き辞書

### 13.1 裁定台帳(37-ui-rulings.yaml)

未裁定リストは残タスクだが、裁定台帳は設計資産である。`open` だけでなく `ruled` / `rejected` / `superseded` を保持し、「同じ質問を二度としない」ための来歴を残す。

- **辞書ヒットも台帳の 1 レコード**(`decided_by: dictionary`)として記録する。来歴が台帳に一元化され、ゲートは台帳だけを見れば済む。
- **裁定には否定側を残す**。「追加」が `AttachTagToItem` で*あり* `CreateTag` では*ない*という境界の言明が、次回以降の AI の迷いを減らす。
- 裁定を覆すときは上書きせず、新レコードを起こして旧を `superseded` にする(lineage 温存 — 64 と同じ規律)。

### 13.2 文脈付き辞書(36-ui-dictionary.yaml)

表示文言は多義である(「追加」= タグ追加/行追加/条件追加…)。辞書は無条件のグローバル alias 集にしない。

- **scope は `instance` / `screen` / `product` の 3 値**。scope の拡大はそれ自体が 1 件の裁定であり、台帳に記録する。feature / domain 等への細分化は、誤った一般化の誤爆が実測されてから裁定する(rule of three 待ち)。
- **エントリの新設は裁定の裏付け(`source_rulings`)を必須とする**。裏付けのないエントリはゲート不合格。
- **文脈条件の機械照合(applies_when DSL)は導入しない**。実行エンジンのない条件節は死んだ仕様になる。照合は AI 候補生成+人間裁定が担い、誤爆が実測された時点で機械化を候補として裁定する。

### 13.3 測定

裁定装置の価値は質問を出す能力ではなく、**同じ質問を二度と出さない能力**で測る。

| 指標 | 期待 |
|---|---|
| 再質問率(裁定済みの意味を再度質問した率) | 下がるべき |
| 辞書ヒット率(人間裁定なしで解決した率) | 画面数に対して上がるべき |
| 未裁定充填検出数(AI が質問せず埋めた件数) | ずる台帳(51)と直結。ゼロであるべき |
| prompt 追記量 | 失敗知見がプロンプトへ漏れていないかの canary |

この曲線が出ないなら、辞書還流か scope 設計が失敗している。

## 14. 抽出工程の失敗型 X1/X2/X3 と還流先

§9.1 の S1/S2/S3 は**視覚突合(製造後)**の失敗型である。ここで定義する X1〜X3 は**抽出工程(製造前)**の失敗型であり、別系列として扱う(同一記号の二義使用禁止)。

| 失敗型 | 例 | 還流先 |
|---|---|---|
| X1 raw 抽出漏れ | button の見落とし、aria-label 未取得 | パーサ治具の修正+治具テスト追加。**プロンプトで直さない** |
| X2 構造認識ミス | div 群を Card でなく素の panel と解釈 | AI 候補プロンプトの修正+golden 追加 |
| X3 意味裁定ミス | 「追加」を CreateTag と誤解 | 裁定台帳+辞書の negative 追加。**プロンプトだけで直さない** |

失敗のたびにメガプロンプトへ知見を追記するのは X1/X3 の誤った還流であり、プロンプト肥大=職人芸の再蓄積である。

## 15. UI-CAD 裁定ゲート

「人間がちゃんと読んだか」ではなく「製造に流してよい条件を満たすか」で止める。不変条件は次の 4 つ(凍結。変更する場合は fork して宣言):

1. すべての interactable(raw 抽出治具の導入まで、母集団は `ui-ir.json` の action)は、「ui-bom 採用済み」「理由付き ignore(`rejected` 裁定)」「open question に紐づく」のいずれかでなければならない。
2. final action は `ruled` 裁定(辞書ヒット由来を含む)を持たなければならない。
3. `blocking: true` の `open` が 1 件でも残っていれば、E-BOM / M-BOM 昇格禁止。
4. ui-bom item は raw DOM node への trace を持たなければならない。

検査治具は [tools/ui-cad-gate.py](tools/ui-cad-gate.py)。

| Gate | 検査内容 | 失敗時 |
|---|---|---|
| G2 会計 | 全 action が 採用 / ignore / 質問 のいずれかに分類済みか | AI 候補生成または質問追加 |
| G3 裁定 | blocking の open が残っていないか | 製造停止。裁定してから再実行 |
| G4 来歴 | final action に ruled 裁定があるか。辞書エントリに source_rulings があるか | 裁定追加または辞書修正 |
| G5 追跡 | ui-bom item が trace map 経由で HTML selector へ辿れるか | 昇格禁止。trace 補完 |

G1(raw 抽出網羅)と G6(stable id 揺れ)は、`ui-extract.py` 導入後に追加する(決定的抽出が存在して初めて検査可能になるため)。
