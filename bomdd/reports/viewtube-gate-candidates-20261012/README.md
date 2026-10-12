# ViewTube の門に残る 2 つの候補 — 判定を変えずに縮められるかの証明(2026-10-12)

**依頼**: user「門に残る2つの候補の証明を進めて」(2026-10-12)。候補は ECO-VT-250 で「判定が変わらないことの証明が先に要る」として範囲の外に置いたもの(`../viewtube-gate-speed-20261011/README.md` §6)と、効果の測定(`../viewtube-gate-effect-20261012/README.md`)で門に残ると分かったもの:

- (a) commit-msg フックでの `validate_process.py --commit-msg` の 2 回目(登録簿を stage した commit だけ・約 25 秒)
- (b) commit 前フックの中の `git checkout-index --all`(1.4 GB の複製+削除・約 13〜19 秒)

ViewTube は読むだけで、実験はすべて使い捨ての clone(`git clone --shared -c core.autocrlf=false`)の中で行った。clone の HEAD は `fb2fe0a3`。

## 1. 候補 (b): 変更影響の検証器のための複製を絞る — 判定は同じ(証明済み)

**今の形**(`bomdd/hooks/pre-commit` 316〜365 行): 保護された経路を stage した commit ごとに、index をまるごと一時フォルダへ複製し(`git checkout-index --all`)、その中の `bomdd/tools/validate_change_impact.py` を `--root <本物のリポ> --prospective-index` で実行する。変更影響の道具そのものを stage した commit だけは、複製の中で検査のテスト一式(`selftest_change_impact.py`、`VIEWTUBE_CHANGE_IMPACT_CANDIDATE_ROOT=<複製>`)も走らせる。

**読むものの証明**(読んだ):
- `validate_change_impact.py` は標準ライブラリと `yaml` だけを import し、自分の場所(`__file__`)を使わない。入力はすべて `--root`(本物のリポ)と git から読む(policy は `root / POLICY_PATH`、登録簿・manifest は prospective index)。
- 複製から読まれるのは、(1) スクリプト自身、(2) Python がスクリプトのフォルダ(`<複製>/bomdd/tools/`)を `sys.path[0]` に置くので、import の解決に使われうるそのフォルダの中身、(3) フックが存在を確かめる 3 ファイル(`bomdd/process/change-impact-policy.yaml`・`bomdd/tools/validate_change_impact.py`・`bomdd/tools/selftest_change_impact.py`)だけである。
- だから複製を `bomdd/tools/` と `bomdd/process/change-impact-policy.yaml` に絞っても(同じ index から同じ `checkout-index` で書き出す)、読まれる中身は同じバイト列になる。

**実測**(`narrow_checkout.py` → `narrow-checkout-output.txt`): 3 つの stage の状態で、まるごとの複製と絞った複製から同じ検証器を走らせ、終了コード・標準出力・標準エラーをバイト単位で比べた。

| stage の状態 | 判定 | 複製+削除の時間 |
|---|---|---|
| 登録簿だけ | 同じ(PASS) | 13.4+2.2 秒 → 0.08+0.01 秒 |
| 登録簿+ `src/ViewTube.App` のファイル | 同じ(PASS) | 16.2+2.7 秒 → 0.08+0.00 秒 |
| +壊した変更影響の manifest(既知の不良) | 同じ(REQUIRED_CONSUMER_UNRESOLVED) | 14.3+4.2 秒 → 0.16+0.01 秒 |

複製するファイルは 11,792 → 38。

**範囲**: 絞るのは、変更影響の道具を stage していない commit(ほとんどすべての保護された commit)の経路だけ。道具を stage した commit は、検査のテスト一式が複製を広く読むので、今のまるごとの複製のまま。UI の製造の検査(`src/ViewTube.App` を stage した commit)は、複製の中で .NET をビルドし `src/` 全体を読むので、絞る対象にしない。

**見込み**: 保護された commit 1 回につき約 13〜19 秒短くなる。

## 2. 候補 (a): commit-msg フックの 2 回目の検証を省く — 条件つき、勧めない

**分かったこと**(`a-second-run/`、調査は別のサブエージェント。実測と読んだことを分けて記録):

- `validate_process.py` がコミットメッセージを使うのは、遷移の trailer の確かめ 1 か所だけ。commit 前フックの合成のメッセージは全番号の trailer を持つので、1 回目は trailer で落ちない。だから 2 回目が 1 回目と違う判定を出すのは、trailer の確かめと、**2 つのフックの間に入力が変わった場合**だけである。同じ入力では、6 回の実行(`PYTHONHASHSEED` を変えた 3 回を含む)で標準出力がバイト単位で同じだった。
- **入力は 2 つのフックの間に変わりうる**(実測、`locktest-setup.sh`):
  - 普通の `git commit`(`-a` もパスの指定も無い)では、git は `GIT_INDEX_FILE=.git/index` のまま index のロックを持たずにフックとエディタを走らせる。エディタを開いている間に別のプロセスの `git add` が成功し、commit-msg フックはその追加を stage として見たが、commit のツリーには入らなかった(git は commit 前フックの直後にツリーを決める)。`-a` やパスの指定のときはロックがあり、別のプロセスの `git add` は失敗した。
  - 作業ツリーも変わりうる(利用者、IDE の自動保存、別のエージェント、テストの出力)。6 つの検証器のうち 3 つ(記録の一貫性・記録の言葉・機械の主張)は登録簿を index ではなく作業ツリーから読み、機械の主張の検査は `bomdd/`・`test-results/`・`.agents/`・`tools/` の全ファイル(追跡外を含む)を読む。作業ツリーだけを変えた 4 つの実験(`out/pert_*.stdout`)で、4 つとも判定が変わった。
- **2 回目を省いて判定を同じに保つには**、1 回目と 2 回目の間に index・HEAD・設定・作業ツリーのどれも変わっていないことを確かめる指紋が要る。正確な作業ツリーの読み取りの集合は 5,743 ファイル・368 MB(温かいキャッシュで sha256 に約 0.5〜1 秒)だが、それを決めるには登録簿と方針を読む必要がある。固定の上位集合(`.git` を除く全体)なら 1,462 MB で、温かいキャッシュで 3.9 秒、冷たいキャッシュで 26.4 秒かかった。
- 結論: 省くことはできるが、「同じ判定」は指紋の集合が検証器の読むものを漏れなく覆うことに乗る。ECO-VT-250 で、同じ種類の主張(読み込みをまとめても同じ判定)に独立レビューが 5 回反例を出した。見込める短縮(約 25 秒から指紋の時間を引いたもの)に対して、前提が広すぎる。**勧めない。**

**副産物の観察**(今の形の性質。この調査は直していない):
1. 普通の `git commit` では、commit-msg フックの 2 回目の検証が、commit されるツリーではない index を見うる(上の実験)。今の 2 回目は、その間の変化を拾うが、拾ったものが commit の中身と一致するとは限らない。
2. 一時的な読み取りの失敗で、2 か所が通す側に倒れる(読んだ): `validate_materialisation_divergence.py:161`(作業ツリーのファイルが無いと、その経路を飛ばす)と `validate_machinery_claims.py:91`(記録の面の頭のフォルダが無いと、そのフォルダ全体を飛ばす)。
3. 3 つの検証器が `--commit-msg` でも登録簿を作業ツリーから読む。`--commit-msg` で index に切り替わるのは `validate_process.py` 自身の読み取りだけである(作業ツリーだけを変えた実験 c で、validate_process は PASS、記録の一貫性が止めた)。

## 2.5 候補 (b) の ECO(ViewTube ECO-VT-253)の進み — フックを変える commit が通らない(2026-10-12)

user 裁定「1」で ViewTube ECO-VT-253 を起票し(`ac09abf6`)、probe(`2abdf9c2`)・宣言(`9c129eac`)まで commit した。修理は作業木で済ませ、probe 2/2 緑・元と修理後のフックで 6/6 の状態が同じ判定・変異 3/3 を確かめた。

修理の commit は、ViewTube の門で **止まった**(31 分)。撮影の全計画は 23/23 で通ったが、フックを stage した commit でだけ走る UI 製造の道具の資格確認(HEAD の `selftest_ui_manufacturing.py` が候補の索引の複製で走る)が 49/51 で失敗し、理由は ECO-VT-207・209・213 の記録の言語の比率(フィクスチャの中で本文と登録簿の日本語の比率の差が 0.21〜0.25、上限 0.20)だった。

**修理の前からの欠陥である**: 同じ資格確認を、フックを変えない HEAD(`9c129eac`)の使い捨ての clone で走らせても、同じ 49/51・同じ 3 件で失敗した(`mfg_qual_head.py` → `mfg-qual-head-output.txt`、1361 秒)。フックを最後に変えた commit は 2026-09-25(ECO-VT-190)で、ECO-VT-207 以降はその後に起票された。いまは、フックや UI 製造の道具を stage する commit がすべてこの資格確認で止まる。

ViewTube の作業木は HEAD に戻した(フックは作業木から直接走るので、commit していない修理を置いたままにすると、ほかのセッションの commit がそれで走る)。修理は `eco-vt-253-fix.patch`(`git diff --cached --binary`、HEAD `9c129eac` に `git apply --check --index` で当たることを確かめた)に保存した。ECO-VT-253 は staged のままで、フックの所有権を持っている。

## 3. 限界

- (b) の実測は 3 つの stage の状態だけ。同じ判定であることの主な根拠は、§1 の「読むもの」の証明(読んだ)である。
- (a) の調査は 1 つのサブエージェントによるもので、独立レビューは受けていない。
- 時間は同じマシンで 1 回ずつ。
