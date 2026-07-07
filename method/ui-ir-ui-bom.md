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
| `ui-ir.raw.json` | `tools/ui-extract.py` が HTML から決定的に抽出した事実(手書き・AI 生成禁止) |
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
- blocking の open 裁定を残したまま E-BOM / M-BOM へ昇格する(gate GU3)。
- 裁定の裏付け(source_rulings)なしに辞書エントリを作る、または scope を広げる(gate GU4)。
- 辞書ヒットを裁定台帳に記録せず final action を確定する(来歴の分散)。
- 抽出工程の失敗をメガプロンプトへの追記だけで直す(§14 の還流先規律に反する)。

## 11. AI への指示

標準は工程分離(§12)の 2 段プロンプトである。

| Prompt | 入力 | 出力 |
|---|---|---|
| [prompts/ui-raw-to-candidates.md](prompts/ui-raw-to-candidates.md) | `ui-ir.raw.json`+モック表示+機能説明+36 辞書+37 台帳 | `ui-ir.json`(候補)+台帳への質問レコード案 |
| [prompts/ui-apply-rulings-to-bom.md](prompts/ui-apply-rulings-to-bom.md) | `ui-ir.json`+37(裁定済み)+36+raw IR | `ui-bom.json`+`ui-trace-map.json`+`extraction-report.md` |

質問生成を第1段から独立させる 3 分割は、「候補と質問の混載で質が落ちる」ことが実測されてから行う(候補記録)。

旧一発変換 [prompts/ui-mock-to-ui-bom.md](prompts/ui-mock-to-ui-bom.md) は deprecated。raw 抽出治具を使えない環境での代替としてのみ残し、失敗知見を追記しない(還流先は §14)。

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
  ↓ 決定的抽出: tools/ui-extract.py(AI 不使用。同一 HTML → 同一 id)
ui-ir.raw.json      … HTML から機械的に確定できる事実(stable id は data-ui-id または DOM 由来)
  ↓ AI 意味付与: prompts/ui-raw-to-candidates.md
ui-ir.json          … 意味候補+confidence+根拠+rawRefs。候補であり製造入力ではない
  ↓ 裁定/辞書解決(人間+辞書)
37-ui-rulings.yaml + 36-ui-dictionary.yaml
  ↓ 昇格: prompts/ui-apply-rulings-to-bom.md(裁定ゲート合格時のみ)
ui-bom.json         … 製造へ流せる確定済み候補部品表
  ↓
E-BOM / M-BOM / Control Plan / S-BOM
```

- `confidence` は製造許可ではなく、レビュー優先度にだけ使う。
- AI は raw IR に存在しないノードを作ってはならない。final action を確定してはならない。曖昧な意味は未裁定質問として出す。
- 工程を 1 つのメガプロンプトに混載すると、失敗のたびにプロンプトが太り、職人芸が増える(§14)。

### 12.1 DOM スナップショット治具(runtime 描画モックの入力化)

HTML が実行時に DOM を生成するモック(React+Babel 等)は、静的 HTML に UI が存在しない。この場合:

1. ブラウザでレンダリングし、**computed style の cursor を `data-snap-cursor` 属性として焼き込んで**から DOM を保存する(snapshot)。フレームワークが JS でリスナーを付ける要素は静的属性に痕跡が無く、これをしないと丸ごと X1 になる(実測: MoviePad retro-01 でリスナー駆動要素 15 件が旧判定で全滅。div 製カスタムラジオを含む)。
2. snapshot は**状態ごと**に撮る(モーダル・選択状態など。モックの初期状態が全てを描いているとは限らない)。
3. `ui-extract.py` の入力は snapshot ファイルとする。snapshot が source-of-record であり、GU6 の突合対象も snapshot。

## 13. 裁定台帳と文脈付き辞書

### 13.1 裁定台帳(37-ui-rulings.yaml)

未裁定リストは残タスクだが、裁定台帳は設計資産である。`open` だけでなく `ruled` / `rejected` / `superseded` を保持し、「同じ質問を二度としない」ための来歴を残す。

- **辞書ヒットも台帳の 1 レコード**(`decided_by: dictionary`)として記録する。来歴が台帳に一元化され、ゲートは台帳だけを見れば済む。
- **裁定には否定側を残す**。「追加」が `AttachTagToItem` で*あり* `CreateTag` では*ない*という境界の言明が、次回以降の AI の迷いを減らす(実測: MoviePad retro-01 で R1 に書いた negative が R2 の「書き出す」を人間への質問なしで解決した)。
- 裁定を覆すときは上書きせず、新レコードを起こして旧を `superseded` にする(lineage 温存 — 64 と同じ規律)。
- **options は候補であり、回答を拘束しない**。選択肢外の回答は正当。ただし選択肢外・曖昧な回答を記録するときは、**記録者の解釈をユーザーへ復唱して確認を取ってから ruled 化する**(実測: retro-01 で「区分解除のボタン」を選択解除と誤解釈して ruled 化 → supersede 訂正が必要になった)。
- **実機のある遡及(as-built 裁定)では、実機の挙動・コードを evidence に含めてから裁定にかける**。実測(retro-01): 実機 evidence 付きで裁定した項目は全て conform、モック+README だけで裁定した項目は 2/2 が実機と矛盾し supersede になった。既存実装は準拠度が低くても実使用で磨かれた判断の蓄積であり、乖離解決の既定は実機優先推定(実機変更は個別裁定+明示承認)。
- **ruling の記入と status の更新はセット**で行う(ruled 化の作業単位)。片方だけの更新は GU3/GU4 が検出する(retro-01 で 2 回実測 — 記録者ミスの頻発型)。

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

初回実測(MoviePad ui-cad-retro-01・2026-07-05): R1 = 質問 8 / interactable 40・辞書 0。
R2 = 質問 3 / interactable 5・**辞書ヒット 2(うち 1 は R1 の negative 由来)・再質問率 0%・未裁定充填 0**。
prompt 追記量 0(失敗還流は全て治具・台帳側で吸収 — X1 は ui-extract 修正、X3 は negative 追記)。

## 16. 実証からの候補記録(rule of three 待ち — 形式化しない)

- **複数画面パッケージの raw id 名前空間**: `RAW-ACT-*` は snapshot ファイルごとに 0001 から採番されるため、複数 snapshot を持つパッケージでは衝突する。retro-01 では画面別サブディレクトリ(`export-dialog/`)+ゲートの `--rulings ../` 参照で回避した。恒久解(id への source prefix か、サブディレクトリ標準化)は第 3 例で裁定する。
- **ruled 化補助治具**: 「ruling 記入と status 更新」の片方忘れが retro-01 で 2 回発生し、いずれも GU3/GU4 が検出した。3 回目が出たら `ui-rule.py`(1 コマンドで ruling+status+decided_at を原子的に更新)を起票する。**部分実現(2026-07-05)**: モック検査のヒアリング裁定については ui-mock-inspect.py `hearing` が原子記入を実装(§17.2)。一般の UQ ruled 化への拡張は引き続き 3 例目待ち。
- **UI 裁定 → 要求台帳への還流経路**: UI の裁定質問が要求漏れを発見することがある(retro-01 UQ-0004: 未保存終了保護の不在を「表示契約の問題ではなく要求漏れ」と分類)。裁定台帳から 10-requirements への還流を標準経路にするかは次の実例待ち。
- **work order 表示契約の機械生成(翻訳層の排除)**: manufacture-01 で、設計者が work order を手書き翻訳した層から CAD 表示要素が 4 件欠落した(製造・申告は契約に対し完璧= ずる 0)。決定的パイプラインの端点に手書き翻訳が残ると、そこが新たな漏れ点になる。候補対策: (a) work order の表示契約節を UI-BOM+trace map+snapshot から機械生成する、(b) 工場に snapshot(視覚原器)を同梱し「文言・構造は BOM、見た目は snapshot」と役割分担する。強い 1 例目(FINDINGS §10)。
  **具体設計(2026-07-07 追記)**: 視覚原器は人手スクショでなく**固定条件レンダリングによる機械生成**とする(viewport / deviceScaleFactor / テーマ / フォント / 待機条件を pin した headless ブラウザ。撮影対象は UI-IR/裁定台帳から機械導出する **capture plan** — 「何を撮るか」の選択を作業者依存にしない)。来歴= モック hash → レンダ環境 pin → 画像 hash。位置づけは検査用派生成果物の 2 層: 第 1 層= 幾何・実効色の headless 物理量突合(自動合否可・ECO-056 の headless プローブ化の型)/第 2 層= 並置突合の golden(許容差+承認者。**pixel-exact 既定不採用の原則は維持** — Chromium レンダと実装側レンダはフォント・AA・フォーム部品で原理的に画素一致しない)。バイト再現の宣言範囲は pin されたレンダ環境内に限る(OS フォント描画差は残る)。
  **プロト実測(2026-07-08・scratch 1 例目 = MoviePad モック)**: (1) 固定条件レンダリング(viewport/dSF/テーマ/motion/locale/TZ pin+fonts.ready+rAF×2+アニメ凍結 CSS)は、DOM snapshot 5 状態+原版ライブ描画の全 6 キャプチャーで **2 回の独立起動間バイト同一**を達成(同一マシン・同一 Chrome 版内)。(2) **発見: §12.1 の DOM snapshot は視覚原器として自己完結でない** — `<style>`/`<link>` を含まず素の UA 描画に落ちる(構造抽出の source-of-record と視覚原器は別物)。帰結: 視覚原器は「DOM snapshot と**同一レンダリングセッション**から pixel capture を双子出力」する設計になる(事後の snapshot→画像生成は不可能・状態再現も snapshot 撮影時にしかできない → capture plan は §12.1 の状態別 snapshot 手順に統合)。(3) 原版側の債務: モックの Google Fonts 依存は版 pin なし= 視覚再現性がフォント配信に依存(CDN スクリプトは SRI pin 済み)。K 層債務として記録する様式候補。治具昇格は 2 例目待ち — プロト一式(治具 2 本+キャプチャー+manifest+非自己完結の証拠画像)の保全先= MoviePad `bomdd/ui/mock-capture-01/`(main 90df557)。
- **契約の検証可能性チェック(G2' の UI 版)**: 「既定選択は MP4」のように、成果物の範囲(View 単体)では検証不能な契約が work order に混入した。work order 発行時に「各契約は本製造の成果物だけで検査可能か」を確認する観点。1 例目。
- **モック受入検査のゲート化(GM 系列)と playbook 必須工程化**: §17 の検査を止め装置(exit code 付きゲート)にするか、playbook の標準工程に昇格するかは、プロスペクティブ適用(次の実題材でモック作成直後に実施)の実測を経てから裁定する。遡及1例(mock-inspect-retro-01)では検査自体の価値は立ったが、ゲート化の誤検出率・運用負担は未測定。
- **検査→乖離台帳→ECO の三重奏の明文化**: mock-inspect-retro-01 の miss 型分析で、検査(製造前)・乖離台帳(as-built)・ECO(実使用要望)の3装置が異なる型の漏れを受け持つ分業が観測された。全体像を method の1枚図にするかは次の実例待ち。
- **ドロップターゲット証拠の焼き込み(X1 型・1例目)**: cursor ベースの interactable 証拠は**ドロップターゲットを原理的に見ない**(ドラッグ中しかカーソルが変わらない)。prospective-01 の種 S1(注記「ドロップで読み込める」vs DOM 痕跡なし)を層1 が見逃した実測。候補対策: §12.1 スナップショット治具に `data-drop-target` 相当を焼き込み、ui-extract が interactable 証拠として扱う。2例目で起票。
- **状態横断の data-ui-id 対称性**: 既存 snapshot 群へ後から状態を追加すると、新 snapshot だけ data-ui-id 付き・旧は sha1 フォールバックという非対称が生じ、同一アクションの状態横断同定が不安定になる(prospective-01 C10 で lint が検出)。運用規律(状態追加時は全 snapshot に id 注釈を揃える)か治具検査(GU6 拡張)かは次例で裁定。
- **lint 合格(書式)と内容決着の2段構え**: gate-cad の解錠は check(書式・予算)合格であり、矛盾・質問の内容裁定は含まない。内容は CAD 段の GU3(blocking open で昇格禁止)が止める設計。この2段構えの妥当性は /bomdd-ui-cad 完走例で確認する。

## 14. 抽出工程の失敗型 X1/X2/X3 と還流先

§9.1 の S1/S2/S3 は**視覚突合(製造後)**の失敗型である。ここで定義する X1〜X3 は**抽出工程(製造前)**の失敗型であり、別系列として扱う(同一記号の二義使用禁止)。

| 失敗型 | 例 | 還流先 |
|---|---|---|
| X1 raw 抽出漏れ | button の見落とし、aria-label 未取得 | パーサ治具の修正+治具テスト追加。**プロンプトで直さない** |
| X2 構造認識ミス | div 群を Card でなく素の panel と解釈 | AI 候補プロンプトの修正+golden 追加 |
| X3 意味裁定ミス | 「追加」を CreateTag と誤解 | 裁定台帳+辞書の negative 追加。**プロンプトだけで直さない** |

失敗のたびにメガプロンプトへ知見を追記するのは X1/X3 の誤った還流であり、プロンプト肥大=職人芸の再蓄積である。

## 15. UI-CAD 裁定ゲート

「人間がちゃんと読んだか」ではなく「製造に流してよい条件を満たすか」で止める。ゲート記号は **GU 系列**とする(playbook のフェーズゲート G0〜G3 / G2' と衝突するため。§14 の S→X 改名と同じ理由)。不変条件は次の 5 つ(凍結。変更する場合は fork して宣言):

1. raw IR の全 interactable は、`ui-ir.json` の `rawRefs`(actions / inputs / unmodeledElements)または裁定台帳のいずれかに現れなければならない(黙って落とさない)。
2. `ui-ir.json` の全 action は、「ui-bom 採用済み」「理由付き ignore(`rejected` 裁定)」「open question に紐づく」のいずれかでなければならない。
3. final action は `ruled` 裁定(辞書ヒット由来を含む)を持たなければならない。
4. `blocking: true` の `open` が 1 件でも残っていれば、E-BOM / M-BOM 昇格禁止。
5. ui-bom item は raw DOM node への trace を持たなければならない。

検査治具は [tools/ui-cad-gate.py](tools/ui-cad-gate.py)(raw 抽出は [tools/ui-extract.py](tools/ui-extract.py))。

| Gate | 検査内容 | 失敗時 |
|---|---|---|
| GU1 raw会計 | raw IR の全 interactable が候補層か台帳に現れるか(raw IR なしでは skip) | AI 候補の再生成または unmodeled 追記 |
| GU2 会計 | 全 action が 採用 / ignore / 質問 のいずれかに分類済みか | AI 候補生成または質問追加 |
| GU3 裁定 | blocking の open が残っていないか | 製造停止。裁定してから再実行 |
| GU4 来歴 | final action に ruled 裁定があるか。辞書エントリに source_rulings があるか | 裁定追加または辞書修正 |
| GU5 追跡 | ui-bom item が trace map 経由で HTML selector へ辿れるか | 昇格禁止。trace 補完 |
| GU6 id揺れ | `--mock` 指定時、再抽出して stable id の揺れがないか | extractor 修正またはモック改変の diff 追従 |

raw IR のない旧方式(§11 一発変換)の案件では GU1/GU6 は skip され、GU2 が会計の全責務を負う(経過措置)。

## 17. モック受入検査(candidate)

§12 パイプラインの**さらに前**に置く検査。要望→仕様ギャップ・問題領域→解決領域ギャップ・
モックを見た人間の認知の限界により歩留まり 100% は不可能である、という前提の下で、目標を
**歩留まり向上・早い工程での発見(リリース後発覚が最悪)・修正コストの高い問題の優先検出**に置く。

設計原則: **モック作成の工程・やり方には干渉しない。検査するのは成果物(モック)だけ**。
人間に対する負担が大きい装置は役立つ前に使われなくなる。BomDD 語彙では、モックは
**管理外サプライヤ(人間の自由な創作)からの支給部品**であり、本検査はその受入検査(IQC)である。
サプライヤの工程は管理せず、入荷成果物を検査する — 製造業の標準的な割り切りと同じ。

三層+復唱の構造(プロンプト: [prompts/ui-mock-coverage.md](prompts/ui-mock-coverage.md)):

```text
mock パッケージ(注記+snapshot+raw IR)
  ↓
[層1] 内部矛盾検査(注記 vs DOM、DOM 内部)……「完全な誤り」の検出
[層2] カバレッジ写像(判定なし・記述のみ)……「現在カバーしているスコープ」の逆宣言
[層3] 隣接未カバー質問(≤20問・手戻りコスト降順)……認知の限界の代行
[層4] 復唱文「製造するとこうなる」……行ったこと≟行いたかったこと の突合
  ↓ スコープ十分の裁定(スコープ外も 37 台帳の裁定として記録=沈黙にしない)
§12 パイプライン(決定的抽出 → 候補 → 裁定 → UI-BOM)
```

- **宣言の向きの反転**が核。作業者に事前スコープ宣言を強制しない(負担)。AI がモックから
  「カバーしているもの」を導出して提示し、隣接未カバーを質問する。人間は「在るもの」のレビューは
  得意だが「無いもの」の列挙は苦手 — そこだけ機械に代行させる。
- 検査エージェントは**隔離**して実行(実装・台帳類・git は汚染源)。出力は全て候補と質問であり、
  §12 三行原則を変更しない。
- 測定(初回実測 mock-inspect-retro-01・MoviePad・盲検遡及・2026-07-05):
  下流発覚 16 項目のオラクルに対し hit 7 / partial 4 / miss 5(69%)。
  **修正コスト高の「未規定契約」クラスは 5/6(83%)**。発行質問 17+矛盾 6 のうちノイズは実質 1
  (有意味率 22/23 — 全件実機証拠付きで裁定)。オラクル外の真発見 3(うち 1 件は retro-01 の
  全パイプラインをすり抜けた実在モック欠陥 = TC 単位ラベル矛盾)。
- **分業線(この装置の miss は欠陥ではない)**:
  - as-built 型(実機が後から加えた改善)→ 乖離台帳(retro 系)の分業
  - 実使用要望型(使い込んで初めて出る要望)→ 歩留まり 100% 不可能の残余。ここはリリース後の
    ECO 経路が受ける
  - 観点リスト欠落型のみ改善可能 → プロンプトの肥大防止則の範囲内で還流(実測 miss 時のみ・3行まで)
- 凍結しないもの: 検査のゲート化(GM 系列等)は誤検出・実測が溜まるまで導入しない。
  playbook への必須工程化はプロスペクティブ適用(次の実題材)を経てから裁定する。

### 17.1 層2.5: 参照概念モデル差分(外→内・candidate)

層3(隣接質問)は**内→外**の導出であり、モックの隣接から導出しにくい欠落(実使用要望・定型設備)を
取りこぼす。補完として、製品カテゴリの一般概念モデル(ユビキタス言語)を立てモックと差分を取る
**外→内**の導出を層2.5 に置く(プロンプト: [prompts/ui-mock-refmodel.md](prompts/ui-mock-refmodel.md)。
製品につき1回で足りる — 画面ごとに繰り返さない)。

構造: 製品クラス較正(≤3問。粒度爆発の防止)→ 参照モデル生成(機能カテゴリ粒度・範囲規律)→
写像 → gap 一覧(≤15・コスト順)→ **ヒアリング= 4分類の裁定**:
① 意図的な非採用 → negative scope 裁定(資産=二度と聞かない)/② 検討漏れ → モック改訂 or 要求台帳 /
③ 対象だがスコープ外 → scope 裁定 /④ フェーズ計画 → deferred 記録(将来 ECO の予告)。

**望遠鏡効果**(mock-inspect-02 実測): 外→内はカテゴリ丸ごとの欠落(空状態・エラー系・進捗・D&D・
定型設備)を確実に見つけるが、「カバー済み」と写像されたカテゴリ**内部**のインスタンス欠落
(操作の対称性・個別設定項目)には構造的に盲目。分解能の性質であり欠陥ではない。導出の分業:

| 導出 | 得意領域 | 実測 |
|---|---|---|
| 層1 矛盾検査 | モック内部の食い違い | 01: 実在欠陥 2 を含む 6 件 |
| 層3 内→外(隣接) | 未規定契約+カテゴリ内インスタンス | 01: 未規定契約 83% |
| 層2.5 外→内(参照モデル) | カテゴリ丸ごとの欠落 | 02: 完全新規 4(空状態・D&D・設定記憶・a11y)・ヒアリング4/4分類可・ノイズ 0/10 |
| 残余(どちらも不可) | 深い慣用操作・as-built 配置 | → 乖離台帳・ECO の分業(統制群で確認: as-built 型は浮上しない) |

限界: 参照モデルは AI の事前分布であり主流製品に偏る。差別化製品では gap の多くが①になるため、
①の一括裁定(「この参照カテゴリ群は全部非採用」)で潰す。その運用感はプロスペクティブ適用で測る。

### 17.2 コマンド化 — ワークフローの機械強制(adapter 層)

プロンプト依存の検査は規律(隔離・順序・予算・台帳記入)が属人性(属セッション性)として残る。
プロンプト=作業標準書、コマンド+治具=**治具・ポカヨケ**の分業で、凍結済み規律だけを機械化する
(検査内容の質と裁定は機械化しない)。

- 治具: [tools/ui-mock-inspect.py](tools/ui-mock-inspect.py) — `init`(manifest sha256+**隔離ステージング**:
  検査エージェントの入力からリポへのパスを排除)/`skip`(理由必須=スキップも来歴)/
  `emit-prompt`(正典 prompts/ から合成・版数を来歴記録=正典は prompts/ のまま)/
  `check`(予算・書式・コスト降順・①〜④形式・禁止パターンの lint。exit 0/1/2)/
  `hearing`(①〜④回答を 37 台帳へ原子記入。②検討漏れありは exit 3=モック改訂へ戻る合図)/
  `gate-cad`(CAD 工程の施錠)。セルフテスト 17 項目同梱。
- コマンド(製品リポへ bomdd-init が設置。`--skills-only --skills ...` で既存リポにも):
  `/bomdd-refmodel`(手順2・skip可)→ `/bomdd-mock-lint`(手順3・必須)→ `/bomdd-ui-cad`(手順4。
  **gate-cad が exit 0 になるまで施錠**)。ワークフロー: モック作成(自由)→2→②あれば戻る→3→
  矛盾/blocking あれば戻る→4。「1 に戻る」ループは台帳が収束させる(再質問率 0% 実測)。
- 遡及検証(2026-07-05): 01 実報告書= pass(違反0)。02 実報告書= **実在の書式逸脱 1 件を検出**
  (gap#4 のヒアリング質問だけ①記号を欠いていた)— check は空砲ではない。
- 隔離の限界(明記): ステージングはバーを上げるがサンドボックスではない。指示ベース隔離の残余は
  治具 docstring に記載。
- **プロスペクティブ1周目の実測**(prospective-01・MoviePad モックのコピー+新ゴール・2026-07-06):
  全遷移が治具強制下で成立 — hearing の②検討漏れが **exit 3 でループを発動**し、モック改訂→
  skip(理由付き来歴)→ lint → gate-cad 施錠→解錠まで通った。
  **設計者役(AI)の非意図欠陥 5 件を lint が捕捉**(Inspector セクション欠落・項目セット食い違い・
  構造非対称・disabled/非表示の混在・id 注釈非対称)=「工程は縛らず成果物で拾う」の実演。
  **台帳収束**: lint(台帳盲検)の 18 問中 6 問が台帳突合で人間に届く前に自動決着。
  check は run 間の**コスト表記ドリフト**([high] vs 【high】)を実戦検出 → §14 の規律どおり
  プロンプトでなく治具側を較正した(意味的等価の表記ゆれは治具で吸収)。
