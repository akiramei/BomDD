# 製造ブリーフ r3 — ViewPrism2 ECO-145(独立レビュー所見の是正・工場= Codex)

- 役割: **producer(工場)**。対象リポ: C:\Users\akira\source\repos\ViewPrism2(作業ディレクトリ= リポのルート・HEAD は `git rev-parse HEAD` で確認して報告に写す)。
- 製造対象(これだけ): `bomdd/cp_results.py`。**他のファイルは変更しない。commit しない。**
- 入力(これがすべて): 本ブリーフ / `bomdd/cp_results.py`(r2 まで拡張済み)。必要なら `bomdd/30-ebom.yaml`・`bomdd/33-control-plan.yaml` の欄の形だけ。
- 読まないもの: `bomdd/41-fixed-oracle.yaml`・`bomdd/42-*`・`bomdd/60-change-order-*.md`・`.claude/`・`AGENTS.md`・`CLAUDE.md`。
- 不変: CP 行ごとの表の出力(1 文字も変えない)・既存の区分の定義・終了コードの意味(0= 表を出せた / 2= 表を出せない)。

## 是正する所見(別文脈の独立レビュー・各所見は実行で再現済み)

### F1(blocking)— 新しい経路の例外で、既存の行ごとの表まで出なくなる・終了コードが変わる

再現: E 品目の `acceptance_refs: [[CP-A], CP-A]` → `TypeError: unhashable type: 'list'`・終了 1・出力 0 バイト / E-BOM が UTF-8 として不正 → `UnicodeDecodeError`(ValueError の派生)が `main` の `except ValueError` に入り「FATAL … 終了 2」で表が出ない /
33 の行の `id` が整数で refs を持つ → `", ".join` で TypeError・終了 1(HEAD では終了 0)。E 品目の `id` が整数・list でも同じ。

是正:
1. `load_ebom_items` は `ValueError`(UnicodeDecodeError を含む)も捕まえて「読めない」として返す。
2. `build` は、E-BOM の読み取りと ID ごとの区分(`load_ebom_items`+`classify_ruled`)の**全体**を保護する: そこで何が起きても、行ごとの表のデータ(既存のキー)は必ず返す。失敗したら `ruled_ids: []`・`ruled_orphans: []`・`ruled_error: "<例外の型と文>"` を返す。
3. `render` は `ruled_error` があれば、ID ごとの節に `- **ID ごとの表を作れない(<理由>)— 行ごとの表だけを出した**` の 1 行を出す(行ごとの表はそのまま)。
4. 個別の防御: `acceptance_refs` の要素は文字列だけを見る / E 品目の `id` は文字列のものだけ対象 / 33 の行の `id` を表に出すときは `str()` / join は `str()` を通す。
5. `main` の終了コードは、ID ごとの表の失敗では変えない(0 のまま)。

### F2(blocking)— selftest に「行は合格だが ID は測定不能」の腕が無い

現状の REQ-SKIP は、違反の行(CP-B)の refs にあり、Skip のテストは測定不能の行(CP-C)に付いている。合格の行に同居していない。「参照する行が合格なら ID も合格にする」という壊れ方(本拡張が見せたい埋没そのもの)を入れても selftest が通る。

是正: 全件 Skip の ID を**合格の行**に置く(例: CP-G〔pass+skip → 合格〕の `requirement_refs` にその ID を置き、CP-G の Skip のテストにその ID の trait を付ける)。同じ `expect` で「その行の区分が合格」かつ「その ID の区分が測定不能」を確かめる。

### F3(non-blocking)— selftest の抜け(変異が生き残る)

次の腕を足す。各腕は「その機能を壊すと selftest が FAIL する」こと:
- `invariant_refs` を持つ行(現状は合成データに 1 行も無い)→ その ID が集合に入る
- refs の list に None・整数が混ざる → 文字列だけが ID になり、例外にならない
- `main` の配線: `--ebom <path>` が効くこと・既定で `30-ebom.yaml`(33 と同じディレクトリではなく、既定の `DEFAULT_EBOM`)を読むこと。`main(argv)` を合成ファイルで呼び、標準出力を捕まえて確かめる(一時ディレクトリ・`--xml`・`--cp`・`--ebom` を渡す)
- 別欄(どの行も参照しない ID)が markdown に出ること
- 全件 NotRun の ID → 測定不能
- 期待の確認で辞書を直接引いて KeyError の traceback にならないよう、`.get` で引いて `selftest FAIL` の文で落ちるようにする(既存の ID ごとの期待も同じ)
- F1 の 3 つの入力(list を含む acceptance_refs・UTF-8 として不正な E-BOM・整数の id)→ 例外にならず、行ごとの表のデータが返ること

### F4(non-blocking)— refs を持つ行が無いとき、別欄が隠れる

`render` の「refs を持つ行が無い」の早期 return が別欄(trait にあるが refs に無い ID)を飛ばす。return をやめ、表だけを省いて別欄は出す。

### F5(non-blocking)— 数字だけでない INV の ID が消える

`INV-\d+` は `INV-W1` のような ID を拾わない(実台帳の E-DB-010 に INV-W1 がある)。境界も無い(`INV-009a` → `INV-009`)。
是正: `\bINV-[A-Z]*\d+\b` で拾う(単語境界つき・英大文字の接頭を許す)。selftest に `INV-W1` と `XINV-12`(拾わない)の腕。

### F6(non-blocking)— ID の前後の空白

refs の ID と trait の値は、前後の空白を落としてから突き合わせる(`"REQ-1 "` と `REQ-1` を同じ ID にする)。大文字小文字は変えない。selftest に 1 腕。

### F7(non-blocking)— `build()` を `ebom_path` なしで呼ぶと、存在しないパス名つきの「読めない」になる

`ebom_path=None` のときは、E-BOM を読まず、`ebom_unreadable` を `"E-BOM のパスが渡されていない"` にする(作り物のパスを出さない)。`main` は従来どおり既定の `DEFAULT_EBOM` を渡す。
`--cp` を指定して `--ebom` を指定しない場合は、E-BOM を**読まない**(別の 33 に既定の 30 を結びつけない)— `ebom_unreadable` を `"--cp を指定し --ebom を指定していない"` にする。selftest に 1 腕。

### F8(non-blocking)— 表で「どの行を経由して入った ID か」が見えない

E 品目だけに由来する ID(`rows` が空)は、その品目が `acceptance_refs` に持つ**参加する行**を経由して入る。5 列目を `E-SIMCACHE-033(CP-DB-006 経由)` の形にする(経由する行が複数ならカンマ区切り)。`rows` が空でない ID は従来どおり品目の ID だけ。
JSON の `ruled_ids` の各要素に `via_rows`(E 品目 ID → 経由する行の list の dict)を足す。selftest に 1 腕。

## 自己受入

- `python bomdd/cp_results.py --selftest` が `selftest: OK`・終了コード 0。
- `python -m py_compile bomdd/cp_results.py` が成功。
- F2 の確認: 自分で一時的に「参照する行が合格なら ID も合格にする」変異を入れて selftest が FAILED になることを確かめ、変異を戻す(結果を報告に写す)。
- `git status --short` に、これまでの 8 ファイル以外が出ない(cp_results.py 以外の内容を変えない)。

## ずる報告・報告(最終メッセージ全文・ハーネスが保存する)

```
[INFORM / COMPLETE]

DONE            ← または BLOCKED <理由>

- HEAD: <sha>
- 製造物: bomdd/cp_results.py(<行数>)
- 自己受入: selftest <OK/FAILED> / py_compile <OK/NG> / F2 の変異 <FAILED になった/ならなかった>
- 所見ごとの処置: F1 … / F2 … / F3 … / F4 … / F5 … / F6 … / F7 … / F8 …
- git status --short: …
- 読んだファイル一覧: …
- ずる報告: …
```
