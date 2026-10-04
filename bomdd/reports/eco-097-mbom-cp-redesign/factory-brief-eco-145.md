# 製造ブリーフ — ViewPrism2 ECO-145(テストの trait 付与+表の拡張・工場= Codex)

- 役割: **producer(工場)**。対象リポ: C:\Users\akira\source\repos\ViewPrism2(作業ディレクトリ= リポのルート・HEAD は `git rev-parse HEAD` で確認して報告に写す)。
- 製造対象(これだけ): ①`bomdd/cp_results.py`(拡張)②テスト 4 ファイルへの属性の追加 — `tests/ViewPrism2.Tests/CpThumb007Tests.cs`・`CpThumb049ExifTests.cs`・`CpThumb144VersionPinTests.cs`・`CpDb006Tests.cs`。
  **src は変更しない。他のテスト・他の bomdd/ 配下・csproj も変更しない。テストの本体(メソッドの中身・名前・既存の属性)は変えない。commit しない。**
- 入力(これがすべて。これ以外を参照しない): 本ブリーフ / `bomdd/cp_results.py` / `bomdd/33-control-plan.yaml` の CP-THUMB-007 と CP-DB-006 の行(`requirement_refs`・`invariant_refs` は受理側が先に置いた)/ 上の 4 テストファイル。
- 読まないもの: `bomdd/41-fixed-oracle.yaml`・`bomdd/42-*`・`bomdd/60-change-order-*.md`・`.claude/`・`AGENTS.md`・`CLAUDE.md`。

## 1. テストの trait(属性の追加のみ)

次の表のとおり、各テストメソッドに `[Trait("req", "REQ-NNN")]` を付ける(複数なら属性を複数)。`[Fact]` の直後の行に置く。クラスの `[Trait("cp", …)]` は変えない。
表に「(なし)」とあるメソッドには付けない。表に無いメソッド(`Dispose` 等)には付けない。

| クラス | メソッド | req |
|---|---|---|
| CpThumb007Tests | Jpg1920x1080は256x144のJpegになる | REQ-040 |
| CpThumb007Tests | Png100x50は拡大されずPngのまま_FMEA012 | REQ-040 |
| CpThumb007Tests | GifBmpWebpはJpeg出力になる | REQ-040 |
| CpThumb007Tests | 縦横比維持で縮小し丸めはHalfAwayFromZero最小1px | REQ-040 |
| CpThumb007Tests | キャッシュヒットで再生成しない | REQ-040, REQ-105 |
| CpThumb007Tests | キャッシュキーはMD5小文字絶対パスで大文字小文字を同一視する | REQ-040 |
| CpThumb007Tests | 壊れたJpgはNullでキャッシュ記録なし_FMEA012 | REQ-040, REQ-106 |
| CpThumb007Tests | 破損キャッシュは削除して再生成する | REQ-040, REQ-106 |
| CpThumb007Tests | 解像度取得はフルデコードなしで寸法を返す | (なし) |
| CpThumb049ExifTests | 対照_EXIFなしjpgのサムネと寸法は従来どおり | REQ-085 |
| CpThumb049ExifTests | EXIF回転6のjpgはサムネが正立_縦長になる | REQ-085 |
| CpThumb049ExifTests | EXIF回転6のjpgの寸法メタは実効寸法を返す | REQ-085 |
| CpThumb049ExifTests | キャッシュ世代移行_旧世代ファイルは参照されず新世代で正立生成される | REQ-085, REQ-105 |
| CpThumb049ExifTests | 正立ローダ_EXIF回転6は正立ピクセルを返し向きと内容が一致する | REQ-085 |
| CpThumb049ExifTests | 正立ローダ_EXIFなしはnull_従来の直読経路を変えない | REQ-085 |
| CpThumb144VersionPinTests | SkiaSharp版を三つの実ファイルから抽出できる | REQ-104 |
| CpThumb144VersionPinTests | SkiaSharp版は実装と二つの台帳で一致する | REQ-104 |
| CpThumb144VersionPinTests | SkiaSharp版は三箇所ともExactである | REQ-104 |
| CpDb006Tests | 新規DBはWALかつFK有効 | REQ-003 |
| CpDb006Tests | 新規DBはmigrations行数が定義数と一致し全id記録済み | REQ-004 |
| CpDb006Tests | v0DBに全マイグレーション適用で新規DBとスキーマ同値 | REQ-004 |
| CpDb006Tests | ランナーは未適用分をID昇順で適用し新規DBと同値にする_合成マイグレーション | REQ-004 |
| CpDb006Tests | タグ削除カスケード_4テーブルの状態が仕様どおり | REQ-028 |
| CpDb006Tests | フォルダ削除でimagesと付与が連鎖削除される | REQ-010 |
| CpDb006Tests | パスの大文字小文字違いは重複として拒否される | REQ-010 |
| CpDb006Tests | COLLATE_NOCASEが主要列に付与されている | (なし) |

## 2. `bomdd/cp_results.py` の拡張 — 裁定層の ID ごとの結果

既存の動作(CP 行ごとの表の出力・区分・終了コード・既存の selftest の期待)は**変えない**。次を足す。

1. **読み取り**: `load_run` で、trait `cp` に加えて trait `req` と `inv` も集める(`{ID: [result, ...]}`。`req` と `inv` は 1 つの辞書にまとめてよい — ID の接頭辞 REQ- / INV- で区別がつく)。既存の戻り値を使う箇所を壊さない形で渡す。
2. **ID の集合**: 33 の各行(retired を除く)の `requirement_refs` と `invariant_refs`(どちらも list・無い行は無視)に現れる ID。ID ごとに、それを参照する行の ID の一覧と depth を持つ。
3. **区分**(CP 行と同じ語・同じ順):
   - 違反 = その ID の trait を持つテストに Fail が 1 件以上
   - 合格 = Pass が 1 件以上・Fail 0(Skip・未実行の件数を併記)
   - 測定不能 = テストはあるが全件が Pass でも Fail でもない
   - 未実行(人の承認で検査) = テストが無く、その ID を参照する行が**すべて** depth が G のみ(既存の `human_only`)
   - 未実行(検査なし) = テストが無く、上以外
4. **別欄**: trait `req` / `inv` にあるが、どの行の refs にも無い ID(ID・テスト数・Fail 数)。
5. **出力(markdown)**: 既存の出力の**後ろ**に節を足す。既存の部分は 1 文字も変えない。
   - 見出し `# 裁定層の ID ごとの結果(ECO-145)`
   - 1 行: `- 区分: 違反 N / 測定不能 N / 未実行(検査なし) N / 未実行(人の承認で検査) N / 合格 N`
   - 1 行: `- 対象は、33 の行が requirement_refs / invariant_refs で参照する ID だけ(参照を持たない行の検査はここに現れない)。判定ではない`
   - 表(全 ID を区分の順・ID の昇順で 1 行ずつ。合格も 1 行ずつ出す): `| ID | 区分 | テスト(Pass/Fail/他) | 参照する CP 行 |`
   - 別欄があれば `## 別欄: どの行も参照しない ID(trait にあり 33 の refs に無い)`
   - refs を持つ行が 1 本も無いときは、見出しと「refs を持つ行が無い」の 1 行だけを出す。
6. **`--json`**: 既存のキーはそのまま。`ruled_ids`(list of dict: id・category・tests・pass・fail・skip_or_not_run・rows)と `ruled_orphans` を足す。
7. **`--selftest`**: 既存の期待をすべて残し、ID ごとの陽性対照を足す。少なくとも次の腕:
   - 合格の ID / 違反の ID(Fail 1+Pass 1)
   - **行は合格だが ID は測定不能**(同じ行に、Pass のテスト〔別の ID〕と、全件 Skip の ID のテストが同居する)— 本拡張の目的の腕
   - テストが無い ID → 未実行(検査なし)/ 参照する行がすべて depth G → 未実行(人の承認で検査)/ G の行と unit の行の両方から参照 → 未実行(検査なし)
   - 1 つのテストが `req` を 2 つ持つ → 両方の ID に数える
   - 別欄(refs に無い ID の trait)
   - retired の行の refs は ID の集合に入れない
   - refs を持つ行が 1 本も無い 33 → 節は「無い」の 1 行(例外にしない)
   - `requirement_refs` が list でない行(文字列など)→ その行の refs は無視(例外にしない)
8. 先頭の docstring に、ID ごとの表の説明を数行足す。

## 3. 自己受入(製造完了の条件・結果を報告に写す)

- `python bomdd/cp_results.py --selftest` が `selftest: OK`・終了コード 0。
- `dotnet build tests/ViewPrism2.Tests` が 0 error / 0 warning。
- `dotnet test tests/ViewPrism2.Tests --filter "FullyQualifiedName~CpThumb|FullyQualifiedName~CpDb006"` が全合格(**`-p:TestingPlatformCommandLineArguments` を渡さない**)。sandbox が NuGet を拒否して走らない場合は、その旨と build の結果を報告する(全件実行と表は受理側が行う)。
- `git status --short` が、上の 5 ファイル(cp_results.py+テスト 4)と、受理側が先に置いた変更(` M bomdd/32-mbom.yaml`・` M bomdd/33-control-plan.yaml`・` M .claude/skills/eco-fix/SKILL.md` — 工場は触らない・戻さない)だけ。それ以外が出たら戻す。

## 4. ずる報告(cheat-log 形式・必ず書く)

本ブリーフと入力から導けずに慣習で埋めた判断を**全件**列挙する(0 件なら「0 件」と書く)。例: 関数の分け方・JSON のキーの細部・表の文言。

## 5. 報告(最終メッセージ全文・ハーネスが保存する。報告ファイルを自分で書かない)

```
[INFORM / COMPLETE]

DONE            ← または BLOCKED <理由>

- HEAD: <sha>
- 製造物: bomdd/cp_results.py(<行数>)・テスト 4 ファイル(付けた trait の数: <N>)
- 自己受入: selftest <OK/FAILED> / build <0/0> / filter test <N/N または 走らず+理由>
- git status --short: …
- 読んだファイル一覧: …
- ずる報告: …
```
