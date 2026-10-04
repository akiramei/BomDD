# 製造ブリーフ r2 — ViewPrism2 ECO-145(表の ID の集合を裁定層から取る・工場= Codex)

- 役割: **producer(工場)**。対象リポ: C:\Users\akira\source\repos\ViewPrism2(作業ディレクトリ= リポのルート・HEAD は `git rev-parse HEAD` で確認して報告に写す)。
- 製造対象(これだけ): `bomdd/cp_results.py`。**他のファイルは変更しない。commit しない。**
- 入力(これがすべて): 本ブリーフ / `bomdd/cp_results.py`(r1 の拡張済み)/ `bomdd/33-control-plan.yaml` の CP-THUMB-007・CP-DB-006 の行 / `bomdd/30-ebom.yaml` の E-THUMB-020・E-DB-010 の品目(欄の形を知るため)。
- 読まないもの: `bomdd/41-fixed-oracle.yaml`・`bomdd/42-*`・`bomdd/60-change-order-*.md`・`.claude/`・`AGENTS.md`・`CLAUDE.md`。

## 変更の理由(受理側の発見)

r1 は ID の集合を 33 の行の `requirement_refs` / `invariant_refs` だけから取る。これだと、行の refs に入れなかった要求は表から消える(実例: E-DB-010 は REQ-005 を負うが、CP-DB-006 の refs に無く、表に出ない)。
表の目的は「人が裁定した ID のうち、検査が届いていないものを見せる」ことなので、ID の集合は裁定層(E-BOM)からも取る。

## 仕様

r1 の動作(CP 行ごとの表・ID ごとの表の区分・別欄・JSON のキー・既存の selftest の期待)は変えない。次を足す。

1. **E-BOM の読み取り**: `bomdd/30-ebom.yaml`(既定のパス。`--ebom <path>` で指定可・`--cp` と同じ扱い)の `ebom.items`(list)を読む。
   読めない・`ebom.items` が無い・list でない場合は、**例外にせず**、E-BOM 由来の ID を足さずに、ID ごとの節の先頭に `- **E-BOM を読めない(<理由>)— 下の表は 33 の行の refs だけから作った。E 品目が負う ID の届かないものは見えていない**` の 1 行を出す(終了コードは変えない)。
2. **参加する行**: `requirement_refs` または `invariant_refs` に ID を 1 つ以上持つ行(retired を除く)。
3. **E-BOM 由来の ID**: E 品目(dict・`id` を持つ)のうち、`acceptance_refs`(list)に「参加する行」の ID を 1 つ以上含むものについて、
   その品目の `requirement_refs`(list の文字列)と、`invariants` の各行(文字列の行だけ・dict の行は `str()` にして同じ扱い)に現れる `INV-\d+`(正規表現)を、ID の集合に加える。
   品目の `lifecycle_state` が `retired` / `superseded` のものは除く(欄が無ければ除かない)。
4. **ID ごとの記録に足す欄**: `ebom_items`(その ID を負う E 品目の ID の list・出現順)。既存の `rows`(その ID を refs に持つ CP 行)は r1 のまま。E-BOM だけに由来する ID は `rows` が空になる。
5. **区分**(テストがある場合は r1 と同じ)。テストが無い場合:
   - `rows` が空でなく、すべて depth が G のみ → 未実行(人の承認で検査)(r1 と同じ)
   - それ以外(`rows` が空の場合を含む)→ 未実行(検査なし)
6. **出力(markdown)**: 表の列を `| ID | 区分 | テスト(Pass/Fail/他) | 参照する CP 行 | 負う E 品目 |` にする(5 列目を足す。空なら `-`)。`rows` が空なら 4 列目は `(どの行の refs にも無い)`。
   2 行目の説明を次に差し替える: `- 対象は、33 の行が requirement_refs / invariant_refs で参照する ID と、その行を acceptance_refs に持つ E 品目が負う ID(requirement_refs・invariants の INV)。他の行のテストが検査していても、trait req / inv が無ければここでは「検査なし」と出る。判定ではない`
7. **別欄**(trait にあるが ID の集合に無い)は、E-BOM 由来の ID を加えた後の集合で判定する。
8. **`--json`**: `ruled_ids` の各要素に `ebom_items` を足す。E-BOM を読めなかった場合は最上位に `ebom_unreadable`(理由の文字列)を足す。
9. **`--selftest`** に足す腕(既存の期待はすべて残す):
   - E 品目が負う REQ が、どの行の refs にも無く、テストも無い → 未実行(検査なし)・`rows` 空・`ebom_items` にその品目
   - E 品目の invariants の行にある INV が集合に入る(文字列の行と dict の行の両方)
   - 参加する行を acceptance_refs に持たない E 品目の REQ は集合に入らない
   - retired の E 品目の REQ は集合に入らない
   - E-BOM のファイルが無い / YAML として読めない / `ebom.items` が list でない → 例外にならず、注意の 1 行が出て、ID の集合は r1 と同じ
   - E-BOM 由来の ID に trait のテストがある → 合格(行の refs に無くても数える)。この ID は別欄に出ない
10. selftest の中で E-BOM を使う腕は一時ディレクトリの合成ファイルで行う(実ファイルを読まない)。既存の腕は E-BOM なし(存在しないパス)でも期待が変わらないようにする。

## 自己受入

- `python bomdd/cp_results.py --selftest` が `selftest: OK`・終了コード 0。
- `python -m py_compile bomdd/cp_results.py` が成功。
- `git status --short` に、r1 までの 8 ファイル以外が出ない(cp_results.py 以外の内容を変えない)。

## ずる報告・報告

r1 と同じ様式(最終メッセージ全文・ハーネスが保存する)。

```
[INFORM / COMPLETE]

DONE            ← または BLOCKED <理由>

- HEAD: <sha>
- 製造物: bomdd/cp_results.py(<行数>)
- 自己受入: selftest <OK/FAILED> / py_compile <OK/NG>
- git status --short: …
- 読んだファイル一覧: …
- ずる報告: …
```
