# ViewTube の commit の門を、結果を変えずに速くできるか(2026-10-11)

**依頼**: user「ViewTube を題材に開発速度の向上を考える。無駄を無くし、非効率な方法は効率的な方法に置き換える。
ただし品質・正しさとのトレードオフは採らない」(2026-10-11)。

**採否の基準(この調査で使ったもの)**: 速くする変更は、**同じ入力に同じ判定を返す**ことを示せたものだけを候補にする。
判定が変わりうるもの(検査を間引く・遅らせる・粒度を落とす)は、速さがどれだけ得られても候補にしない。

前の測定(`../viewtube-inspection-cost-20261010/README.md` §7・§8)は、遅さの主因が commit ごとの門だと示した
(commit とその検証器の待ちが本体の待ちの 62%)。今回は、その門の 1 回の中身を測った。

## 1. 条件

- ViewTube HEAD `9ad477077986137d5274431dfe34e53afa11bff8`。ViewTube は**読むだけ**で、何も書いていない。
- 測定の間、ViewTube では別のセッションが ECO-VT-249 の作業中だった(作業木に未 commit の変更がある)。
  検証器はその作業木を読んでいる。数は 1 回ずつの実測(N=1)で、ばらつきは測っていない。
- 改変した検証器は ViewTube に置かず、ソースをメモリ上で書き換えて実行した(`patchrun.py`・`redrun.py`)。
  `__file__` は元のパスのままなので、検証器が自分の位置から決めるリポのルートは変わらない。

## 2. 門の 1 回の中身(`time_gates.py` → `time-gates-output.txt`)

| 段 | 時間 |
|---|---:|
| `validate_process.py --quiet`(commit 前フックで毎回) | 109.8 秒 |
| `validate_release_workflow.py` | 2.0 秒 |
| `validate_run_evidence.py`・`validate_record_citations.py`・`validate_mcp_host_location.py` | 各 0.1〜0.2 秒 |
| `git checkout-index --all`(保護パスや UI の commit で、フックの中の 1 ブロックごとに実行) | 11.8 秒+削除 2.4 秒(1.4 GB) |

`validate_process.py` の中身(cProfile・相対の比率だけを見る。cProfile の秒数は実時間より膨らむので引用しない):

- `validate_record_consistency.py`(子プロセス): 時間のほぼ全部が YAML の解析。原因は 1 行で、
  `moved = {… for eco, state in states(before).items() if states(after).get(eco) …}` が、
  **同じ過去の register を ECO の数(70)だけ解析し直している**。
- `validate_machinery_claims.py`(子プロセス): 記録の面(`bomdd/`・`test-results/`・`.agents/`・`tools/`)の全ファイルを、
  **主張 1 件ごとに読み直して正規化している**(読み込み 66,576 回)。
- `validate_process.py` 本体: 適用済みの ECO ごとに `git log --grep` を 1 回ずつ実行している(約 200 回・1 回 約 0.09 秒)。

## 3. 結果を変えない 3 つの書き換え(`patches.py`)

| 記号 | 書き換え | 同じ判定になる理由 |
|---|---|---|
| A | `states(after)` を 1 回だけ解析して使い回す。before が空のときは、元と同じく after を解析しない | 同じバイト列に対する純粋な関数。例外が出る場合と順序も元と同じ |
| B | 記録の面のファイルを、1 回の実行の中で 1 回だけ読んで正規化し、主張ごとに使い回す | 1 回の実行の中で、同じファイルの同じ内容を同じ関数に通している |
| D | 履歴のメッセージを `git log --format=%B%x00` で 1 回だけ読み、メッセージごとに大文字・小文字を区別した部分一致で探す | `git log --fixed-strings --grep=X`(`-i` なし)は X を含むメッセージを大文字・小文字を区別して選ぶ。X は改行を含まないので、行で含むこととメッセージで含むことは同じ。元の casefold の比較は、選ばれたメッセージにしか当たらない。**casefold で探すと一致が広がって判定が変わる**ので、そうしていない |

## 4. 同じ判定かの実測

**合格側**(`diffrun.py` → `diffrun-output.txt`。現在の作業木で、元と書き換え後の標準出力をバイト単位で比べた):

| 検証器 | 元 | 書き換え後 | 標準出力 | 終了コード |
|---|---:|---:|---|---|
| record_consistency(A) | 27.6 秒 | 4.7 秒 | 同一(2966 バイト) | 同一(0) |
| machinery_claims(B) | 48.0 秒 | 6.9 秒 | 同一(955 バイト) | 同一(0) |

**不合格側**(`redrun.py` → `redrun-output.txt`。既知の不良を入れて、元と書き換え後の所見を比べた): **8/8 同一**。

- A: ポリシーの主張 2 つをそれぞれ反転(既知の不良)→ 両方とも同じ所見 1 件。before が空で after が壊れた YAML → 両方とも所見なし。
  before に項目があり after が壊れた YAML → 両方とも `ParserError`。
- B: 検証器自身の適格性確認 `selftest_machinery_claims.py` を、元と書き換え後のモジュールに対して実行 → 両方とも 27/27 arms PASS で、出力も同一。
- D: 実際の register → 両方とも所見 0(17.6 秒 → 1.0 秒)。適用済みの項目を写して ID を `ECO-VT-999` と `eco-vt-100` にした 2 項目を足した register →
  両方とも同じ所見 29 件(履歴の所見 3 件を含む)。
  **訂正(2026-10-11)**: 最初の版はこの `eco-vt-100` を「大文字・小文字だけ違う ID」の確認と書いたが、そうなっていない。
  検証器は register の ID を大文字にそろえてから使う(`_entries` の `item["id"].upper()`)ので、この項目は実在の `ECO-VT-100`(状態 implemented)を
  applied に置き換えた。確かめたのは「適用済みなのに受け入れの trailer が履歴にない項目」(所見 `ACCEPT_HISTORY_MISSING`)である。
  大文字・小文字の扱いが同じであることは、§3 の構造の議論だけが根拠である(§8)。

## 5. 見込み(実測ではない)

- `validate_process.py` 1 回: 109.8 秒から、A・B・D の差(約 23 + 41 + 17 秒)を引いて **約 30 秒** の見込み。
  書き換えを 3 つ同時に入れた全体の実測はしていない(子プロセスの検証器にメモリ上の書き換えを渡せないため)。
- D が効くのは、履歴を調べる実行だけである。register を stage した commit では、フックは `--commit-msg` で実行し、履歴を調べない。
  register を stage しない commit(probe の commit の大半)と、エージェントが単独で走らせる実行で効く。
- register を stage した commit では、`validate_process.py` が commit 前フックと commit-msg フックで 2 回走り、子の検証器も 2 回走る。
  A・B の節約は、その 2 回の両方に効く。
- 前の測定の窓では、commit(フックを含む)が 502 分、単独の検証器が 146 分だった。どちらも、この処理を含む。

## 6. 同じ判定であることを先に証明すれば候補になるもの(未実施)

- **YAML を C 実装の解析器(`yaml.CSafeLoader`)で読む**。libyaml は入っている(`yaml.__with_libyaml__ = True`)。
  ただし解析結果が純 Python 版と同じだとは、構造からは言えない。検証器が読むすべての YAML(作業木・index・HEAD・過去の blob)を両方で読んで `==` で比べ、
  さらに `except yaml.*` の箇所で同じ例外になるかを確かめてからでないと、候補にしない。
- **フックの中の `git checkout-index --all` を、1 回の commit の中で共有する**。1 ブロックで 11.8〜16.6 秒+削除 2.4 秒(1.4 GB)。
  ただし UI のブロックは、その複製の中に `cd` して検査器を実行する。どの使い手もその複製に書き込まないことを確かめるまでは、候補にしない。
- **register を stage した commit で、commit-msg フックが子の検証器を再実行しないようにする**。
  commit 前フックと commit-msg フックの間で index は変わらないので、同じ判定になる見込みがある。ただし保護されたフックの構造を変えるので、
  「その間に何も変わらない」ことの証明が先に要る。
- **エージェントが commit の直前に、同じ検証器を単独で走らせない**(前の窓で 177 回・146 分)。
  単独の実行は作業木を読み、フックは index を読むので、同じ入力とは限らない。どの場合に重複かを数えてから決める。

## 7. 候補にしないもの(判定が変わるため)

- 撮影の全計画を間引く・抜き取りにする・push まで遅らせる: commit の前に止める検出の実績がある
  (前の測定 §7 Q3: 2026-10-08 に、同じ commit の中の道具の宣言の誤りを止めた)。利用者の裁定 (C)(2026-09-22)とも食い違う。
- 門を commit から push や CI へ移す: 不良を見つける時点が後ろにずれる。
- probe の commit をまとめて数を減らす: 「修理の前に赤を記録する」記録の粒度が変わる。これは裁定の対象で、無償の改善ではない。
- 全体の受け入れテストを減らす: 前の測定で、待ちの 1.0% にすぎず主因ではない。また 3 日の窓で「不要」を支えるには足りない。

## 8. この調査の限界

- 合格側の同一性は、いまの作業木 1 つで確かめただけである。同じ判定になることの主な根拠は、§3 の構造の議論である。
- 不合格側は、作った既知の不良 8 件と、検証器自身の適格性確認 27 arms だけである。
- `selftest_machinery_claims.py` の一部の arm は、検証器をファイルのパスから子プロセスで起動する。その arm は、書き換え後でなく元のファイルを実行している。
- `validate_process.py --selftest` は履歴を調べない(`check_history=False`)ので、D の確認には使っていない。D は §4 の register の比較だけで確かめた。
- D の大文字・小文字の扱いは実測していない。register の ID は大文字にそろえられるので、探す文字列はいつも大文字の ID になる。
  違いが出うるのは、履歴の中に大文字・小文字の違う trailer があるときだけで、その履歴は作っていない。根拠は §3 の構造の議論である。
- 同じ型が他の製品にあるかを見た: ViewPrism2 と ViewPrism には、この 3 つの検証器も同じ書き方もない。配布キット(`method/templates/`)にもない。
- 時間は 1 回ずつの実測で、別のセッションが同じマシンで作業していた。

## 9. 器具と出力の sha256(index に入った内容・LF)

出力 3 本は、作業コピーでは CRLF で書かれ、git で LF に正規化される。下の値は `git show :<path> | sha256sum`(stage 後の index)で計算した。

| ファイル | sha256 |
|---|---|
| time_gates.py | bf8e37dc77c34647f31eef8b416d8947e1f9df8d55ff940d56e22266edd37c18 |
| patchrun.py | d91b9dcc8463b8a8c6440079b4ea39f6aa467c341091513a618a627d368e3ffe |
| patches.py | bd228688985a3e79356ccc6f25bd1c3cd2c12416001b44c625b732132a0035f2 |
| diffrun.py | 8baf655994a0df936fcea85712fe57f01760f3553daf9562160e86ba778f92a0 |
| redrun.py | c0beee2bd8776ee9c5baf6042c9ee4df5e44796a4bc453a65926a981eeda8a79 |
| time-gates-output.txt | e55540208d48b0f3055b784d74877855c90ed5657b55e950222faae636c2a603 |
| diffrun-output.txt | 6e758209114b853ef5e0357b451cb5b63ed4a88b3e3493c9e1f34a77eb45fed3 |
| redrun-output.txt | 9fddcc27473affc549babbe93b430233ed1591c4932b017e5e2deffaa457b6a0 |

再実行: 各スクリプトは ViewTube のパスを `C:\Users\akira\source\repos\ViewTube` に固定している。`python time_gates.py`・`python diffrun.py`・`python redrun.py`。
