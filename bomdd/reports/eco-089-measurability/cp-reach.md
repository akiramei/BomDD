# ECO-089 基準線 — Control Plan の特性 ID がコードへ字面で届く率

- 測定日: 2026-10-01
- 母集団= 各リポ bomdd/33-control-plan.yaml に `id: CP-...` の字面で現れる異なる ID。届く= bomdd/ 以外のソースファイル(拡張子を限定)に字面で現れる。
- **限界**: 字面一致のみ。届く≠検査されている(ID を書かないテスト・golden の承認記録・命名規約は拾えない)。届かない≠検査されていない。
  ID を持たない慣行のリポは過小に、コメントに ID を貼るだけの慣行は過大に出る。1 リポ 1 時点・各 1 回。作業木が dirty のリポは未コミットの変更を含む。
- 「lint の選択子で拾える数」= bomdd-lint が読む control_plan.characteristics のリストの件数。字面の定義数と大きく食い違えば、その Control Plan の書き方は lint の想定と違う。

| リポ | HEAD | 作業木 | 33 の解析 | 字面の CP 定義数 | lint の選択子で拾える数 | コードへ届く | 届く率 | 状態 |
|---|---|---|---|---|---|---|---|---|
| BomDD-Plm | d02052b | clean | 解析可 | 21 | 21 | 18 | 86% | 測定済み(字面)(走査 136 ファイル・git ls-files) |
| BomDD-UnitConv-Sample | bb6c090 | clean | 解析不可 | 8 | — | 0 | 0% | 測定済み(字面)(走査 5 ファイル・git ls-files) |
| TimetableAdv | 73b79d47 | dirty(2140) | 解析可 | 25 | 471 | 25 | 100% | 測定済み(字面)・**母集団不一致**(字面 25 ≠ 選択子 471 — 率は字面で拾えた CP- 接頭辞の部分集合にしか当てはまらない)(走査 1684 ファイル・git ls-files) |
| BomDD-LibraryLending-Sample | f7bfc24 | clean | 解析不可 | 12 | — | 6 | 50% | 測定済み(字面)(走査 112 ファイル・git ls-files) |
| ViewTube | a8a9b11f | dirty(1) | 解析可 | 41 | 41 | 12 | 29% | 測定済み(字面)(走査 595 ファイル・git ls-files) |
| ViewPrism2 | e8edbbb | clean | 解析可 | 65 | 65 | 57 | 88% | 測定済み(字面)(走査 360 ファイル・git ls-files) |
| BomDD-Transfer03 | (git なし) | clean | 解析可 | 10 | 10 | 0 | 0% | 測定済み(字面)(走査 11 ファイル・ディレクトリ走査(git 追跡なし)) |

