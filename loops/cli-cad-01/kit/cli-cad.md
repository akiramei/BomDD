# CLI-CAD: worklist — 追跡項目読み取りビュー CLI(設計正本 v1)

> **設計権威**: 本文書は CLI「worklist」の外部観測可能な契約(文法・解析意味論・出力・終了・環境)の**設計上の正本**である。上位正本= 記帳スキーマ v1([schema-excerpt.md](schema-excerpt.md) — 入力データの意味論)。本文書と実装が乖離した場合、本文書が優先する。
> **上流性**: 本文書は実装より上流にある。実装の内部構造・関数分割・アルゴリズムは規定しない。
> **権威境界**: 規定する= 外部から観測可能な (argv, 入力ファイル) → (stdout, stderr, exit code) の対応。規定しない= §U 未規定台帳の各項(実装者裁量 — 差は探索観測であり不合格事由でない)。
> **トレース**: 記帳スキーマ v1(上位)→ 本 CAD → 受入検査(本 CAD のみから独立導出)・製造品。
> **裁定来歴**: §H 参照。

## 1. 目的と対象

improvements.md 形式の Markdown(記帳スキーマ v1 準拠)を走査し、追跡項目(EXP/OBS)の
open/watch 残高・要処理事項・記帳不整合・legacy 棚卸し被覆・統計を表示する**読み取り専用**ビュー。
ファイルへの書き込み・変更は一切行わない。

## 2. 文法契約

```
worklist.py [PATH] [--full]
worklist.py show <ID> [PATH]
worklist.py --selftest
```

- `PATH` 省略時の既定入力: スクリプト設置ディレクトリの**親**にある `improvements.md`
  (= `<script_dir>/../improvements.md`)。
- `--full`: worklist 表の本文切り詰めを行わない(全文表示)。
- `show <ID>`: 単一項目の詳細表示。`show` の直後に ID が無い場合は使用法 1 行を stdout に
  出力し exit 0。
- `--selftest`: 内蔵陽性対照の実行(§7)。
- 位置引数のうち最初の非フラグ引数(`--` で始まらない引数)を PATH と解釈する。
- 未知フラグ・余剰位置引数・フラグの組合せ(`show` と `--full` の併用等)の扱いは未規定(U8)。

## 3. 解析意味論(入力の読み方 — 正本= schema-excerpt.md・本節はその CLI 適用)

- **節**: 行頭 `## ` の行が節を開始する。節日付= 節タイトル中に最初に現れる
  `YYYY-MM-DD` または `YYYY-MM`(いずれも無ければ無日付として `-` 扱い)。
  **移行残高節**= タイトルに「移行残高」を含む節。
- **追跡行**: `- [<状態マーカー>] <ID> — <本文>`。bullet は `-`・行頭の空白は許容。
  ID と本文の区切りは**前後に空白を伴う em ダッシュ「 — 」**。
  ID 文法= `(EXP|OBS)-<英数字 1 個以上>-<数字 2 桁>`。
- **状態マーカー**(5 語彙): `open` / `watch N/3`(N は 1 桁の数字)/
  `recovered YYYY-MM-DD via <証拠>` / `withdrawn 同` / `superseded 同`。
- **継続行**: 追跡行の直後に続く「行頭空白+`evidence:` | `source:` | `origin:`」の行は、
  直前に確定した追跡項目へ付与する。他の非空行が挟まると付与は切れる。
  空行を挟んだ場合の帰属は未規定(U9)。
- **除外領域**(例示を追跡項目と誤認しない): 次の内部は解析対象外 —
  fenced code block(``` ``` ``` または `~~~` で開閉)/ blockquote(行頭 `>`)/
  HTML コメント(`<!-- -->`。複数行に跨るコメントも対象)。
- **棚卸し境界マーカー** `worklist-legacy-audit-cutoff: YYYY-MM-DD`:
  **生テキストで最初に現れた行**を境界とする(HTML コメント内に書かれていても有効 —
  実運用ではコメントとして記載される)。
- 角括弧 bullet 行のうち追跡 ID を含まないもの(通常の Markdown リンク行
  `- [表示名](URL)` 等)は追跡項目ではなく、警告対象にもしない。
- **origin 区分**: 既定= 移行残高節内の項目は `migrated`・それ以外は `native`。
  継続行 `origin:` の値で明示上書きできる。
- **structured 節**= 追跡行(または追跡 ID を含む不整合行)を 1 つ以上含む節。
  **legacy 節**= それ以外の節(散文のみ)。legacy 節の内容を推測して項目化しない。
- **legacy 監査区分**: 境界マーカーがあれば、マーカー行より**前**の legacy 節= audited・
  **後**= unaudited(境界根拠= `marker`)。マーカーが無ければ**最後の移行残高節**の位置で
  代替し、それより前の legacy 節= audited・後= unaudited(境界根拠=
  `migration-section(fallback)`)。どちらも無ければ境界なし(全 legacy 節が未棚卸し)。

## 4. 検査規則

**記帳不整合(validation warnings — 記帳ミスの検出)**:

| コード | 発火条件 |
|---|---|
| W1 | ID 重複 — 同一 ID の追跡行が 2 本以上(状態遷移は行内書き換えの規律) |
| W2 | 語彙外の状態値 — 角括弧内の先頭語が 5 語彙のいずれでもなく、行が追跡 ID を含む |
| W3 | closed 系(recovered/withdrawn/superseded)の日付または `via <証拠>` の欠落 |
| W4 | watch の現在値 `N/3` の欠落 |
| W5 | 状態マーカーのない追跡項目(`- <ID> …` の直書き) |
| W6 | 本文が `<ID> — <内容>` 形式でない(`open` に余分な語が付く場合を含む) |

- マーカーが不成立の行(W2〜W6)は項目として**計上しない**(警告のみ)。
- **要処理(actions due — 記帳は正常)**: `watch N/3` の N≧3 は PROMOTION DUE。
  **記帳不整合と混ぜない**(別セクションで表示 — 正常運用の停止点要求を警告に埋めない)。

## 5. 出力契約(stdout)

- **全出力は stdout。stderr には何も出力しない。** 出力エンコーディングは UTF-8。
- セクションは次の 5 つ・この順・**見出し文字列は正確に**:
  1. `== worklist(open / watch)==`
  2. `== actions due(要処理 — 記帳は正常)==`
  3. `== validation warnings(記帳不整合)==`
  4. `== legacy coverage ==`
  5. `== stats ==`
- **worklist**: open/watch 項目を入力での出現順に列挙。0 件なら `(0 件)`。
  1 件以上なら冒頭に件数行(**正確な書式**):
  `native(新書式の新規): open {a} / watch {b} ・ migrated(期首移行残高): open {c} / watch {d}`
  各項目は 1 行で、次を**含む**: ID / 状態表示(watch は `watch N/3`・PROMOTION DUE 項目は
  `★DUE` を含む)/ origin(`native`|`migrated`)/ 節日付(無日付は `-`)/
  `{ID の記帳座標セグメント} — {本文}`。列幅・整列・切り詰めは未規定(U1)。
  `--full` 時は本文を切り詰めない。表見出し行の有無・内容は未規定(U11)。
- **actions due**: 0 件なら `(0 件)`。各行に `PROMOTION DUE`・当該 ID・`watch {N}/3` を含む。
- **validation warnings**: 0 件なら `(0 件)`。各行は `- L{行番号} {Wコード}: ` で始まる
  (以降の文言は未規定 U2)。**行番号の昇順**で列挙。
- **legacy coverage**: 境界があれば 1 行目に `境界の根拠: marker` または
  `境界の根拠: migration-section(fallback)`、続いて
  `audited(棚卸し済み — 状態の正本は移行残高節): {n} 節`。
  unaudited が 0 件なら `unaudited: 0 節`、1 件以上なら列挙(各行は `- L{行番号}: ` で始まり
  節タイトルを含む・切り詰めは U7・列挙の見出し文言は U10)。
  境界が無ければ「境界なし・全 legacy 節が未棚卸し」の旨の表示(文言未規定 U6)+列挙。
- **stats**: 次のキーを**この順**・**正確な書式**で:

```
sections_scanned: {n}
structured_sections: {n}
audited_legacy_sections: {n}
unaudited_legacy_sections: {n}
open_items: {n}(native {x} / migrated {y})
watch_items: {n}(native {x} / migrated {y})
actions_due: {n}
closed_items: {n}(recovered/withdrawn/superseded)
validation_warnings: {n}
elapsed_ms: {n}
```

  `elapsed_ms` の値は未規定(非負整数)。
- **show <ID>**: 該当項目の ID・状態・origin・本文・(付与されていれば)source・evidence・
  所属節タイトルを表示。該当が無い場合は not found の旨(当該 ID を含む)を表示。
  いずれも exit 0。書式細部は未規定(U5)。
- **入力ファイル不在**: エラーの旨(当該パスを含む)を stdout へ表示し exit 0(§6)。

## 6. 終了契約

| 条件 | exit code |
|---|---:|
| 通常実行(警告・PROMOTION DUE の有無によらず) | 0 |
| `show`(該当なしを含む)・`show` の ID 引数欠落 | 0 |
| 入力ファイル不在 | 0 |
| `--selftest` 成功 | 0 |
| `--selftest` 失敗 | 1 |

本ツールは読み取り専用ビューであり**ゲートとして使わない**(v1 で凍結された運用裁定)。
警告件数・DUE 件数を exit code へ反映しない。

## 7. --selftest(陽性対照)

- 内蔵の恒久 fixture(内容は実装裁量)で**少なくとも次を踏む**: 全 5 状態/全 6 警告種/
  PROMOTION DUE(3/3 とそれを超える値)/除外 3 領域(fence・blockquote・HTML コメント)/
  リンク行の非誤検出/`origin:` 上書き/継続行(evidence)の付与/棚卸し境界マーカー/
  native・migrated 区分。
- 期待値照合の結果を `selftest: PASS` または `selftest: FAIL` を含む行で stdout へ表示
  (FAIL 時は不一致の詳細を続けてよい・書式未規定)。exit code は §6。

## 8. 環境契約

- Python 3・標準ライブラリのみ・単一ファイル。
- 入力は UTF-8 の Markdown ファイル。PATH は相対・絶対とも受け付ける(相対は cwd 基準)。
- Windows / Unix の両方で動作すること(パス区切りの差を吸収する)。

## U. 未規定台帳(権威境界 — 実験中は不変・実装差は探索観測)

- U1 worklist 表の列幅・整列・本文切り詰め幅・省略記号。
- U2 警告・エラーメッセージの文言細部(規定したトークン以外)。
- U3 改行コード(LF/CRLF)・行末空白・セクション間の空行数。
- U4 elapsed_ms の値・計時方法。
- U5 show の書式(表示順・インデント)細部。
- U6 境界なし時の legacy coverage 表示文言。
- U7 列挙行のタイトル・本文の切り詰め幅。
- U8 未知フラグ・余剰位置引数・フラグ組合せの扱い。
- U9 空行を挟んだ継続行の帰属。
- U10 unaudited 列挙の見出し文言。
- U11 worklist 表の見出し行の有無・内容。

## H. 裁定来歴

- v1(2026-07-18): 起票。裁定主体= 2026-07-18 プロジェクトレビュー(修正採択)。
  上位正本= 記帳スキーマ v1。下流= 受入検査(本 CAD のみから独立導出)・製造品。
