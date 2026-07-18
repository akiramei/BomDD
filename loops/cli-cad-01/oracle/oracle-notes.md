# oracle-notes.md — 受入検査のトレースと導出記録

- 検査官: 独立受入検査(ブラックボックス)。入力= kit/cli-cad.md・kit/schema-excerpt.md・kit/fixtures/ のみ。実装は一切参照していない。
- 実行= `python oracle.py <被検実装.py>`。観測= subprocess 経由の (stdout, stderr, exit code) のみ。
- 検査項目数: **91**(fixture 実行 6 種+show 5 種+ファイル不在+selftest+引数解釈 2 種)。

## 1. 検査項目 → cli-cad.md 節番号 対応表

| 検査項目(接頭) | 内容 | CAD 根拠 |
|---|---|---|
| */exit0 | 通常実行・show・不在・selftest 成功の exit 0 | §6 |
| */stderr-empty | stderr は常に空 | §5 冒頭 |
| */headings-order | 5 セクション見出しの正確文字列+順序 | §5 |
| f*/worklist-count-line | 冒頭件数行の正確書式(native/migrated × open/watch) | §5 worklist |
| f1/worklist-appearance-order | open/watch 項目の入力出現順 | §5 worklist |
| f1/item-{ID} | 各行に ID・状態(watch N/3)・origin・節日付を含む | §5 worklist・§3(origin 既定と origin: 上書き・節日付) |
| f1/item-due-star | DUE 項目の行に ★DUE | §5 worklist |
| f1full/fulltext-{ID} | `--full` で `{記帳座標セグメント} — {本文全文}` を含む | §2 --full・§5 worklist |
| f1/worklist-excludes-closed | closed 3 状態は worklist に列挙されない | §5(open/watch のみ列挙) |
| f1/excluded-regions-not-parsed | fence/blockquote/HTML コメント内 ID の非出現 | §3 除外領域 |
| f1/actions-due-line | PROMOTION DUE+ID+watch 3/3 を別セクションに | §4 要処理・§5 actions due |
| f1/warnings-zero | 警告 0(リンク行非誤検出・DUE を警告に混ぜない) | §3 リンク行・§4・§5 |
| f2/item-normal-listed | 正常項目の列挙 | §5 |
| f2/warned-lines-not-counted | W2〜W6 行は項目に計上しない | §4 |
| f2/warning-line-format | 各行 `- L{行番号} {Wコード}: ` 始まり | §5 validation warnings |
| f2/warning-set | W1〜W6 の発火条件と行番号 | §4 表 |
| f2/warning-ascending | 行番号昇順 | §5 |
| f2〜f5/legacy-basis-* | `境界の根拠: marker` / `migration-section(fallback)` を 1 行目に | §3 legacy 監査区分・§5 legacy coverage |
| f*/legacy-audited-* | `audited(棚卸し済み — 状態の正本は移行残高節): {n} 節` | §5 |
| f1・f2/legacy-unaudited-zero | `unaudited: 0 節` の正確文字列 | §5 |
| f4・f5/legacy-unaudited-enum | 列挙行 `- L{行番号}: `+節タイトル | §5 |
| f3/legacy-no-boundary | 境界なし分岐(基準 2 文字列の非出現のみ検査) | §3・§5(文言は U6) |
| f*/stats | 10 キー・この順・正確書式(elapsed_ms は `\d+` のみ) | §5 stats(値は §3-§4 の適用) |
| show-*/content | ID・状態・origin・本文・source/evidence・節タイトル | §5 show |
| show-notfound/content | not found の旨+当該 ID・exit 0 | §5・§6 |
| show-no-id/usage-one-line | 使用法 1 行のみ・exit 0 | §2 |
| missing-file/path-in-stdout | エラーの旨+当該パスを stdout・exit 0 | §5・§6 |
| selftest/pass-line | `selftest: PASS` を含む行+exit 0 | §7・§6 |
| argparse/first-nonflag-is-path | 最初の非フラグ引数= PATH(`--full <PATH>` 順) | §2 |
| path/relative-accepted | 相対 PATH(cwd 基準)受け付け | §8 |

## 2. fixture ごとの期待値導出(CAD §3-§4 を手で適用)

### f1-normal.md(節= L3, L9, L19, L36 / 境界マーカー= L7)

| 導出量 | 値 | 根拠 |
|---|---|---|
| sections_scanned | 4 | `## ` 行 4 本(§3。`# ` 表題は節でない) |
| structured_sections | 3 | 移行残高(F1)・新規節(F1)・追補節 |
| legacy audited / unaudited | 1 / 0 | 旧様式の節(L3)< マーカー(L7)→ audited・根拠= marker |
| open_items | 4(native 3 / migrated 1) | migrated: EXP-20260601-01。native: EXP-20260702-04(`origin: native` 上書き・§3)・EXP-20260702-01・EXP-20260702-06 |
| watch_items | 2(native 1 / migrated 1) | OBS-20260601-02(2/3・migrated)・OBS-20260702-02(3/3・native) |
| actions_due | 1 | watch 3/3 → PROMOTION DUE(§4) |
| closed_items | 3 | recovered EXP-20260601-03・withdrawn EXP-20260702-03・superseded OBS-20260702-05 |
| validation_warnings | 0 | リンク行(L26)は非対象(§3)・除外領域(L28-34)は解析対象外 |
| 件数行 | `native(新書式の新規): open 3 / watch 1 ・ migrated(期首移行残高): open 1 / watch 1` | §5 |
| 節日付 | 移行残高= 2026-07-01・新規節= 2026-07-02・追補節= `-`(無日付) | §3 |

### f2-warnings.md(節= L5 / マーカー= L3)

| 行 | 内容 | 判定 | 根拠 |
|---|---|---|---|
| L7 | `[open] EXP-20260710-01` | 項目(open native) | §3 |
| L8 | `[watch]` 現在値なし | W4・非計上 | §4 |
| L9 | `[recovered 2026-07-11]` via なし | W3・非計上 | §4 |
| L10 | `[pending]` | W2・非計上 | §4 |
| L11 | マーカーなし直書き | W5・非計上 | §4 |
| L12 | 区切り `--`(em ダッシュでない) | W6・非計上 | §4 |
| L13 | `[recovered … via ECO-111] EXP-20260710-01` | 項目(closed)+**W1**(L7 と重複) | §4(W1 は有効マーカー行 — 計上対象。非計上は W2〜W6 のみ) |

stats: sections 1 / structured 1 / legacy 0-0 / open 1(native 1) / watch 0 / due 0 / closed 1 / warnings **6**(W1 の報告行番号は L7 か L13 か未確定のためどちらも許容。W1 を両行で報告する実装も条件成立の同値報告として **7 を許容** — 列挙件数と stats 値の一致は検査する)。

### f3-empty.md(空ファイル)

全量 0。境界なし(マーカーも移行残高節もない)→ legacy coverage は U6 文言のため、`境界の根拠: marker` / `境界の根拠: migration-section(fallback)` の**非出現のみ**検査。stats 全 0 の正確文字列。

### f4-no-marker.md(節= L3, L7, L12 / マーカーなし)

マーカー不在 → 最後の移行残高節(L7)で代替(§3)。旧節A(L3)= audited・旧節B(L12)= unaudited。根拠= `migration-section(fallback)`。items: migrated open 1(EXP-20260615-01)+ migrated watch 1(OBS-20260615-02・1/3 → due 0)。unaudited 列挙= `- L12: `+タイトル(照合は「旧節B」の部分一致 — U7 切り詰め許容)。

### f5-unaudited.md(節= L3, L9, L13 / マーカー= L7)

旧節(L3)< L7 = audited・後置 legacy 節(L13)> L7 = unaudited(根拠= marker)。native open 1(EXP-20260716-01)。列挙= `- L13: `+「後置」部分一致。

## 3. 意図的に検査しなかった事項(U 台帳対応)

| U | 内容 | oracle での扱い |
|---|---|---|
| U1 | 列幅・整列・切り詰め幅・省略記号 | 既定表示では ID/状態/origin/日付の**含有**のみ。本文全文は `--full` でのみ検査 |
| U2 | 警告・エラー文言の細部 | 警告は `- L{n} {W}: ` 接頭のみ。不在エラーは「パスを含む」のみ |
| U3 | 改行コード・行末空白・空行数 | 行単位 strip 比較で無効化(CRLF/LF 不問) |
| U4 | elapsed_ms の値 | `elapsed_ms: \d+` の形式のみ |
| U5 | show の書式細部 | 表示要素の含有のみ(順序・インデント不問) |
| U6 | 境界なし時の文言 | f3 は境界あり用 2 文字列の非出現のみ |
| U7 | 列挙行の切り詰め幅 | 節タイトルは短い部分文字列(「旧節B」「後置」)で照合 |
| U8 | 未知フラグ・余剰引数・フラグ組合せ | 一切検査しない(`show`+`--full` 併用等も不投入) |
| U9 | 空行を挟んだ継続行の帰属 | 該当入力を投入しない(fixtures にも存在しない) |
| U10 | unaudited 列挙の見出し文言 | 列挙は `- L\d+: ` 行のみ抽出・他の行を問わない |
| U11 | worklist 表見出し行 | 件数行(冒頭)以外の非項目行を問わない |

その他の非検査事項(U 外・理由つき):
- **PATH 省略時の既定入力**(§2 `<script_dir>/../improvements.md`): 被検実装の設置ディレクトリ側への配置を要するためブラックボックス検査から除外(実装の環境に手を触れない)。
- **--selftest の内蔵 fixture 内容**(§7): 内容は実装裁量と明記されているため `selftest: PASS`+exit 0 のみ。
- **不在パスの全文一致**: パス区切り・絶対化の正規化を許容し、ファイル名(`no-such-input-zz9.md`)の含有で照合(全文一致の必要条件)。
- **出力エンコーディング**: stdout バイト列を UTF-8 で復号(§5)。復号不能バイトは replace され文字列照合が FAIL となることで間接検査。
- **行番号の基数**: `L{行番号}` は 1 始まりの物理行と解釈(§5 の L 表記に対する通常解釈。fixtures の期待行番号はこの前提で導出)。

## 4. 自己検証(oracle 機構)

- `stub_selfcheck.py`(入力を読まない全ゼロ固定出力のダミー CLI — **期待値導出には不使用**)に対し `python oracle.py stub_selfcheck.py` を実行。
- 結果: 91 検査が全件実行され、`ORACLE: FAIL (45/91)`・exit code 1。subprocess 呼び出し・セクション分割・PASS/FAIL 集計・期待/実測の印字・exit code 伝播の全機構が動作。
- PASS 側 45 件は stub が偶然満たす契約(exit 0・stderr 空・見出し・f3 全ゼロ・selftest 行・not found/usage 形)であり、期待値が CAD 由来であることと矛盾しない(f3 の期待値は空入力から独立導出)。
