# ViewTube の ECO の下書き(起票前・ViewTube には未投入)

> この文書は、user 裁定「1」(2026-10-11)で決めた ViewTube の ECO の下書きである。起票は ECO-VT-249 の完了の後(user 裁定「1」・同日)。
> 起票のときに、ViewTube の HEAD・ECO 番号・行番号を読み直して書き換える(下の行番号は HEAD `9ad47707` のもの)。
> 書式は ViewTube の `bomdd/eco/ECO-VT-249.md`・`ECO-VT-220.md`(検査の道具の ECO)に合わせた。

---

# ECO-VT-NNN — commit の門の検証器が、同じ入力を何度も処理し直している。判定を変えずに、1 回だけ処理する形に直す

- 状態: staged
- 起票: (起票日)
- 起票の根拠: 利用者の依頼「ViewTube を題材に開発速度の向上を考える。品質・正しさとのトレードオフは採らない」(2026-10-11)と、BomDD 側での測定(`akiramei/BomDD` の `bomdd/reports/viewtube-gate-speed-20261011/README.md`)に対する利用者の裁定「1」(同日)。AGENTS.md の規則 1 による。
- 診断層: inspection_process_equipment(検査の道具の層)。製品・要件・仕様に誤りはない。
- 記録: 第 1 節の数は、BomDD 側の読み取りだけの測定(HEAD `9ad47707`・1 回ずつ)。起票の probe で、この木で数え直す。

## 1. 観察した事実

**commit 前フックの 1 回は、ほぼ `validate_process.py` である。** HEAD `9ad47707` の作業木で、`validate_process.py --quiet` が 109.8 秒、他の検証器は合わせて約 2.5 秒。前の窓(2026-10-07〜10-10)で、commit(フックを含む)の待ちは 502 分、単独の検証器の待ちは 146 分で、本体の待ちの 62% だった(BomDD `viewtube-inspection-cost-20261010/README.md` §7)。

**その時間の大半は、同じ入力の繰り返しの処理である。**
- `validate_record_consistency.py` の `check_release_policy_assertions` は、`moved = {… for eco, state in states(before_register).items() if states(after_register).get(eco) …}` の形で、**同じ過去の register の blob を、before に並ぶ ECO の数だけ解析し直す**(HEAD で 70 回)。単独で 27.6 秒。
- `validate_machinery_claims.py` の `inspect` は、記録の面(`bomdd/`・`test-results/`・`.agents/`・`tools/`)の全ファイルを、**主張 1 件ごとに読み直して正規化する**(1 回の実行で 66,576 回の読み込み)。単独で 48.0 秒。
- `validate_process.py` の `validate_register_document` は、implemented・applied の ECO ごとに `git log --fixed-strings --grep=…` を 1 回ずつ実行する(約 200 回・1 回 約 0.09 秒)。合わせて 17.6 秒。履歴を調べるのは `--commit-msg` を付けない実行だけ(`check_history=not bool(args.commit_msg)`)。

**register を stage した commit では、子の検証器が 2 回走る。** commit 前フックが `--commit-msg <合成のメッセージ>` で、commit-msg フックが `--commit-msg <本当のメッセージ>` で、それぞれ `validate_process.py` を実行し、どちらも子の検証器 5 つを実行する。

## 2. 診断

検査の道具の層である。判定の規則に誤りはない。処理の形(ループの中の再解析・再読込・再問い合わせ)が、検証器が増えるたびに 1 回の費用を積み上げた。誰も 1 回の中身を測っていなかった。

## 3. 利用者の決定

- 正しさと品質は速さと交換しない。速くする変更は、同じ入力に同じ判定を返すことを示せたものだけを採る(2026-10-11)。
- 下の A・B・D の 3 つで ECO を起票する。証明が別に要る候補(第 5 節)は、この ECO に入れない(裁定「1」)。

## 4. 直すもの

| 記号 | ファイル | 書き換え | 同じ判定になる理由 |
|---|---|---|---|
| A | `validate_record_consistency.py` | before を 1 回解析し、before に項目があるときだけ after を 1 回解析して使い回す | 同じバイト列に対する純粋な関数。before が空のとき after を解析しないのは元と同じなので、例外が出る場合と順序も同じ |
| B | `validate_machinery_claims.py` | 記録の面のファイルを、1 回の実行の中で 1 回だけ読んで正規化し、主張ごとに使い回す | 1 回の実行の中で、同じファイルの同じ内容を同じ関数に通している |
| D | `validate_process.py` | 履歴のメッセージを `git log --format=%B%x00` で 1 回だけ読み、メッセージごとに**大文字・小文字を区別した**部分一致で探す | `--fixed-strings --grep`(`-i` なし)は X を含むメッセージを大文字・小文字を区別して選ぶ。X は改行を含まない。元の casefold の比較は、選ばれたメッセージにしか当たらない。casefold で探すと一致が広がるので、そうしない |

## 5. 範囲の外

- YAML を C 実装の解析器(`yaml.CSafeLoader`)で読む: 解析結果が同じだと構造からは言えない。証明(検証器が読む全 YAML を両方で読み `==` で比べる・`except yaml.*` で同じ例外になるか)が先に要る。
- フックの中の `git checkout-index --all`(1 ブロック 12〜17 秒+削除 2.4 秒・1.4 GB)を 1 回の commit の中で共有する: どの使い手もその複製に書き込まないことの確認が先に要る。
- register を stage した commit で、commit-msg フックが子の検証器を再実行しないようにする: 保護されたフックの構造を変える。2 つのフックの間で入力が変わらないことの証明が先に要る。
- 撮影の全計画の間引き・push への移動、probe の commit の統合、全体の受け入れテストの削減: 判定または記録の粒度が変わるので、採らない(利用者の決定)。

## 6. 残りの関門

### probe(修理の前に赤を記録する)

時間はばらつくので、**回数**で赤を記録する。修理の前の木で赤、修理の後で緑になるもの:

| probe | 数えるもの | 修理の前(見込み) | 修理の後(期待) |
|---|---|---|---|
| P-A | `check_release_policy_assertions` 1 回の中の `yaml.safe_load` の回数(register の blob に対するもの) | 1 + before の ECO の数(71) | 2 |
| P-B | `inspect` 1 回の中で、記録の面のファイルを開いた回数 ÷ 記録の面のファイルの数 | 主張の数とほぼ同じ倍率 | 1 以下 |
| P-D | `validate_process.py`(`--commit-msg` なし)1 回の中の `git log` の起動回数 | implemented・applied の ECO の数+applied の数 | 1 |

### 同じ判定であることの確かめ(修理の後・据え付けたファイルで)

BomDD の `diffrun.py`・`redrun.py` を、ECO の証拠フォルダに写して使う。メモリ上の書き換えではなく、**HEAD の元のファイルと、作業木の修理後のファイル**を比べる形に直す。

- 合格側: 現在の木で、`validate_record_consistency.py --mode active --json`・`validate_machinery_claims.py --json`・`validate_process.py --json` の標準出力と終了コードが、元と修理後でバイト単位に同一。
- 不合格側(既知の不良):
  - A: ポリシーの主張 2 つをそれぞれ反転 → 同じ所見。before が空で after が壊れた YAML → 同じく所見なし。before に項目があり after が壊れた YAML → 同じ例外。`validate_record_consistency.py` には自分の適格性確認が無い(gate-inventory の `qualification: null`)ので、この 5 ケースが赤側のすべてになる。
  - B: `selftest_machinery_claims.py` が 27/27 arms で通り、出力が元と同一。子プロセスで起動する arm が修理後のファイルを実行していることを確かめる(BomDD の測定では、その arm は元のファイルを実行していた)。
  - D: 履歴にない ID を足した register と、implemented の ECO を applied に置き換えた register → 同じ所見。**大文字・小文字だけ違う trailer を持つ履歴**を一時リポで作り、元と修理後が同じく「見つからない」と判定することを確かめる(BomDD の測定では作っていない)。
- 変異: 修理後のファイルで、使い回しを壊す変異(例: 正規化の結果を別のファイルのものと取り違える・after を解析しない)を入れたとき、上の不合格側か合格側のどれかが赤になることを確かめる。

### 受け入れ

- `validate_process.py --quiet` 全体の実時間を、修理の前と後で 3 回ずつ測り、中央値を記録する(見込み 109.8 秒 → 約 30 秒・判定の基準にはしない)。
- 各検証器の自己検査と、フック一式が通る。
- `evidence.machinery_claims` を宣言する(`bomdd/tools/` を変えるので、machinery-claims の門が要求する)。主張の文の候補:
  - 「記録の一貫性の検査は、過去の登録簿を、1 回の実行の中で before と after の 1 回ずつだけ解析する。判定は元の形と同じである」(probe: P-A)
  - 「機械の主張の検査は、記録の面のファイルを、1 回の実行の中で 1 回だけ読む。判定は元の形と同じである」(probe: P-B)
  - 「工程の検証器は、履歴の trailer を探すとき、履歴を 1 回だけ読み、大文字・小文字を区別して探す。判定は元の形と同じである」(probe: P-D)
- 独立レビュー(R8): 別の新しい文脈で diff を見直す。見る点は、第 4 節の「同じ判定になる理由」が書き換えた差分で本当に成り立っているかどうか。

### 効果の測定(BomDD 側)

EXP-20261011-01(BomDD `method/improvements.md`)で、着地の後の窓の門の待ちの割合(基準線 62%)と、門が止めた回数の推移を測る。
