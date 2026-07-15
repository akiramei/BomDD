# ECO-013 — 参照スキーマの正本/派生乖離(uiId の domain 欠落+ui-mock-extraction 族の二方言=同名異物)

> 状態: **verified(2026-07-16)**。fix= 11424ca・検証 V1〜V3 全 PASS・窓は accept で閉鎖。

## 起票(2026-07-16)

- 出典: **保存形式レビュー(2026-07-16)所見2**(正本と派生スキーマの乖離 — uiId の domain・
  trace-map の mappings/entries の 2 件を指摘)。起票時に**全数走査**(所見1系列で回収済みの
  規律 EXP-20260715-08 の適用)を実施し、実相はレビューの額面より深いことを確定した。
- **全数走査の実測(2026-07-16)**:
  - **ID 層 — 乖離は uiId の 1 系統のみ**。機械突合(uiId/tmpUiPartNo/anyKnownId/単純 prefix の
    個別 def 被覆/S・M0 の family_pattern 文字列一致)の結果:
    - DRIFT: uiId — 正本 `^(screen|region|component|button|action|input|state|modal|domain)\.…`
      / 派生 `^(screen|…|modal)\.…`(**domain 欠落**)
    - 一致: tmpUiPartNo(SCR/REG/CMP/OCC/ACT/INP/STA/DOM/LIV 完全一致)・anyKnownId
      (正本 prefix 全被覆)・個別 def 被覆・oracleCaseId/migrationCaseId
  - **構造層 — 同一ファイル名に 2 成果物型が写像される二方言(同名異物)**:

    | 成果物 | UI-CAD 抽出方言(テンプレ・MoviePad 実物・ui-cad-gate が消費) | 参照層方言(ref-edges/Schema/id-grammar が宣言・ViewPrism2 実物) |
    |---|---|---|
    | ui-trace-map.json | `mappings[] {uiId, tempPartNo, uiBomItemNo, ebomItemRef, htmlSelector…}`+schemaVersion/artifactType 封筒 | `entries[] {uiIr, uiBom, ebomItemRef[], file, locator, handling}`+meta |
    | ui-ir.json | `componentCandidates` / `componentOccurrences` | `components` / `occurrences` |
    | ui-bom.json | `items[]`(一致 — 乖離なし) | `items[]` |

  - **実害= glob 束縛検査の沈黙**: ref-edges の file glob `bomdd/ui/**/ui-{ir,trace-map}.json` は
    両方言にマッチするが、セレクタは参照層方言の키のみを束縛する。UI-CAD 方言の実物
    (MoviePad export-dialog)ではセレクタが**空振り**し、仮品番(TMP-UI-CMP/OCC)の一意性検査・
    trace 参照(ebomItemRef 越境)の検査が**黙って消える**。逆に ui-cad-gate.py の GU5 は
    `mappings` を読むため、参照層方言(ViewPrism2 形)には空振りする。
  - 消費者の実測座標: ui-cad-gate.py:230(`trace_map.get("mappings")`)/
    ref-edges.draft.yaml:271-275(`entries[]` セレクタ)/ Schema `uiTraceMapFile` は
    `required: ["entries"]`。
- 既知観測との接続: ref-v0.6「セレクタが配列をスキップ=検査が黙って消える」(README §4.1)の
  同族 2 例目(変種の出現でセレクタ束縛が沈黙)。二方言の成因は工程系列の並行進化 —
  参照層(plm-v0 遡及リント・ViewPrism2 を正規化)と UI-CAD 系列(PR-2 決定的抽出・MoviePad)が
  それぞれ正当に確立した形で、どちらも「実物」(README「実物が正」の適用対象が 2 つある)。

## 裁定

- **製造承認(2026-07-16・maintainer「1はa、2はOK」)**: 裁定点 1 = **a) 両方言宣言 採用**・
  裁定点 2 = **domain 追加 承認**。baseline を是正開始直前 35b875a へ更新。
- 起票時の裁定点(記録):
- **裁定点 1 — 方言の解決方向(推奨= a)**:
  - **a) 両方言宣言(推奨)**: ref-edges/Schema が両方言を宣言し、型は**判別キー**で機械判別
    (UI-CAD 方言= `schemaVersion`+`artifactType` 封筒を持つ/参照層方言= `meta` または
    判別キー不在)。実物・テンプレ・治具は**全て不変**。検査沈黙は宣言追補で解消。
    README「実物が正」(両実物とも合法な慣行)と整合し、draft 期間の規律どおりスキーマ側が動く。
  - b) 方言統一: 実物 2〜3 リポ+テンプレ+ui-cad-gate の改修波及 — 意味論の統一設計は
    v2 スキーマ共設計の範疇。見送り案。
  - c) ファイル名での分離(改名): 実物改名の波及+ECO-010 で確立した「入口様式」の轍。見送り案。
- **裁定点 2 — uiId の方向**: 正本序列(README §2「矛盾時は YAML 側が勝つ」)により
  **派生 Schema へ domain を追加**(機械的・即決可)。

### 是正方針案(製造前・凍結前の草案 — 裁定 a 前提)

1. Schema `uiId` pattern へ `domain` を追加(正本 family_pattern と文字列一致させる)。
2. ref-edges の ui-trace-map 節へ UI-CAD 方言のエッジを**併記**(`mappings[].tempPartNo` /
   `mappings[].uiBomItemNo` / `mappings[].ebomItemRef`(scalar・null 許容)— family は既存と同一)+
   ui-ir 節のセレクタ起点へ `componentCandidates|componentOccurrences` を追補。
   各エッジに方言注記(判別キー)を付す。
3. Schema `uiTraceMapFile` を両方言対応へ: `required: ["entries"]` を外し、entries 形/mappings 形
   いずれかの存在を要求(oneOf)+各形の参照フィールドを宣言。`uiIrCollection` 側も
   componentCandidates/componentOccurrences を許容。
4. README 改訂列へ **ref-v0.9** を追記(二方言の判別キーと「同名異物は判別キーで型判別」の規律
   1 行)。grammar_version 等の版表記を ref-v0.9 に整合。
5. クローズ条件: 全数走査の再実行で ID 層乖離 0・構造層は両方言とも宣言に被覆され
   空振りセレクタ 0(MoviePad/ViewPrism2 実物の双方でセレクタ起点キーが宣言と交差すること)。

## 影響分析(製造前予測 — 未凍結)

- 影響なし予測: `method/schemas/draft/` の 4 ファイル以外 diff ゼロ。実物リポ・テンプレ・治具は
  不変(両対応案のため)。
- **正直記載(検査が効き始めることによる変化)**: Plm リンタは ref-edges を読むため、次回リント
  実行から UI-CAD 方言の実物に検査が初めて効き、**新規所見が出る可能性**がある(被覆回復に伴う
  検出増 — 欠陥の増加ではない)。silence §16(d)(副経路)の予防適用として起票時から明記。

## 是正(2026-07-16)

1. **Schema `uiId`**: pattern へ `domain` を追加(正本 family_pattern と文字列一致)。
   来歴の実測: 正本への domain 追加は **ref-v0.3(c)(2026-07-03・ViewPrism2 実 IR の慣行)** —
   派生は以来 **13 日間未同期**だった(手管理派生の無検査を裏付ける潜伏期間)。
2. **Schema `uiIrFile`**: `componentCandidates`/`componentOccurrences` を uiIrCollection として
   追補+$comment に二方言と判別キーを明記。
3. **Schema `uiTraceMapFile`**: `required: ["entries"]` を `oneOf: [required entries / required
   mappings]` へ。mappings 形の参照フィールド(uiId/tempPartNo/componentCandidateNo/
   uiBomItemNo/ebomItemRef= null|scalar|array)を宣言。
4. **ref-edges(ref-v0.9 版上げ)**: ヘッダへ改訂台帳追記(二方言・判別キー・被覆境界の明示=
   stableIdDecisions 等は実需要待ちで未宣言)。ui-ir セレクタ起点へ componentCandidates/
   componentOccurrences 追補。trace-map 節へ mappings[] エッジ 7 本併記(ebomItemRef は
   ref-v0.6 の配列併記原則どおり単数+配列)。
5. **id-grammar**: TMP-UI-CMP/OCC の defined_in を両方言形へ+note。
6. **README**: 改訂列へ ref-v0.9 追記(判別キー規律 1 行+C10 への参照)。

## 検証(2026-07-16)

- **V1(全数走査の再実行 — クローズ条件)**: 起票時の機械突合スクリプトを再実行 →
  **ID 層乖離 0 系統**(是正前= uiId の 1 系統)。
- **V2(空振り解消 — クローズ条件)**: 実物 4 ファイル(MoviePad ui-ir/ui-trace-map・
  ViewPrism2 image-tab ui-ir/ui-trace-map)の実在キーが ref-edges セレクタ起点と交差することを
  機械確認 — 両方言とも被覆(是正前= MoviePad 側 2 ファイルが空振り)。
- **V3(構文回帰)**: self-conformance fast 全 PASS(C1 厳格パースに schemas/draft の YAML、
  C2 に JSON Schema が含まれる)。
- 影響なし予測: 的中(diff は method/schemas/draft/ 4 ファイル+台帳系のみ)。

## 教訓(還元候補 — lesson-promote 経由)

- **同名異物は glob 束縛検査を沈黙させる**: 同一ファイル名(glob)に複数の成果物型が写像されると、
  構造セレクタは不一致方言で空振りし検査が黙って消える。型は名前でなく判別キー(封筒)で判別し、
  宣言は全方言を被覆する(OBS-20260716-05・ref-v0.6 と同族 2 例目)。
- レビュー所見の額面(2 乖離)より実相(1 系統+系統的二方言)が深い — 外部所見の取り込みは
  同型全数走査で閉包してから起票する(EXP-20260715-08 回収済み規律の適用実例)。
