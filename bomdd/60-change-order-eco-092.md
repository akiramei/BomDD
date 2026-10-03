# Change Order — ECO-092(pre-push witness が検査していない Git の木を証明する — skip-worktree / assume-unchanged 付き entry を一時 index が引き継ぐ偽証明の是正)

> 裁定: user 2026-10-03 DECIDE「2:A」(外部レビュー 2026-10-02 論点 9。前例= 2026-09-29 裁定「検査器の偽陰性は実害待ちにしない」)。
> 出典: [外部レビュー 論点 9](reports/external-review-20261002/review.md) / 照合= [verification.md](reports/external-review-20261002/verification.md) / 再現= [witness-skip-worktree-repro.sh](reports/external-review-20261002/witness-skip-worktree-repro.sh)。
> 目的: **witness の tree が「検査した作業ツリーの bytes」を証明する**ようにする(ECO-046 の契約 (3)「追跡対象+追加可能ファイルの worktree 内容」を実装が満たしていない)。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-001
- inspector: EQ-002
  pre-push の遮断判定の入力(witness の tree)を変える計器変更のため、異系統の独立検査を併用する(ECO-091 と同じ根拠)。range= 境界探索(r1)→ 是正確認+回帰(r2 以降)。
  検査官は一時 git リポを作る必要があるため **workspace-write**(read-only は OS temp 不能・EQ-002 の設備属性)。外部 API 呼出しなし。

## 0. 実測(起票根拠・2026-10-03)

- **機序**(`_write_selfconf_witness`・L1683〜1705 実読): 実 index(`.git/index`)を一時 index へ複製 → `GIT_INDEX_FILE` を一時 index にして `git add -A` → `write-tree` の結果を witness に書く。
  `git add` は **skip-worktree(`S`)/ assume-unchanged(`h`)の付いた entry を更新しない**(git の仕様)ため、複製された index の bytes がそのまま tree に入る。
  C1 ほかの検査は作業ツリーのファイルを読む(L239〜245)。したがって **検査した bytes と証明した bytes が別物**になる状態がある。`git add` の戻り値も見ていない(失敗しても `write-tree` へ進む)。
- **再現**(隔離リポ・2026-10-03・製造者環境): index に不正 YAML(重複キー)を置き skip-worktree を立て、作業ツリーを正しい YAML へ戻す → witness の tree の blob= **index の不正 YAML**。
  対照(フラグなし)= 作業ツリーの正しい YAML。実 index は双方で不変。再現手順はスクリプトとして reports に保存。
- **既存の防御が効かない範囲**: 通常の staged / unstaged 不一致は commit tree と witness tree の不一致として hook が遮断する(ECO-046 限界 (3))。本件は「index と作業ツリーが違うのに
  add -A が index 側を採る」ため、**index の内容で commit すれば tree が一致して通る**(検査は作業ツリーで PASS・push されるのは index の内容)。
- **露出**: 本リポの `S`/`h` entry は照合時点で 0 件(`git ls-files -v | grep -c '^[Sh]'`)。自然発生例は未観測。witness はローカル限定(C18・CI は NA)— CI は別の防御として残る。

## 1. 変更要求(製造対象・凍結)

1. **tree の計算を関数化** `_witness_tree(root, git_dir) -> (tree | None, why)`: 一時 index へ複製したあと、**正規化**を行う —
   `git ls-files -v -z`(一時 index を読む)で `S` / `s` / `h` 系のフラグを持つ path を抽出し、`git update-index --no-skip-worktree --no-assume-unchanged -z --stdin`
   を**一時 index に対して**実行してから `git add -A` → `write-tree`。実 index は触らない(複製にのみ作用)。
2. **成否の確認**: `update-index` / `add -A` / `write-tree` のいずれかが非 0 なら `(None, why)` を返す。呼び出し側は witness を**書かず、既存の witness があれば削除**し、
   `[witness] 書出し省略(<why>)` を stdout と stderr に出す(無音にしない・ECO-065 の温度計の型)。書けない= 証明しない。古い証明を残さない。
3. **陽性対照**(`_witness_selftest()`・C18 の較正行として毎回実測・CI でも走らせる〔関数の性質であり環境の性質ではない〕):
   ①skip-worktree 腕: 一時 git リポで index= 不正 bytes・`S` フラグ・作業ツリー= 正しい bytes → 返った tree の blob が作業ツリーの bytes と一致し、実 index の blob とフラグが不変 /
   ②対照腕: フラグなしで同じ結果 / ③失敗腕: git リポでない root を渡すと `(None, why)` が返る(書かない)。
4. **hook(`bomdd/hooks/pre-push`)は不変**。witness の形式(tree 1 行+PASS 1 行)も不変。
5. **採らない**: 未対応状態の**拒否**(書かない)のみで済ませる案 — skip-worktree を常用する利用者が永久に push 不能になる(hook は witness 不在を遮断)上、検査した作業ツリーを証明できる
   手段があるのに証明しない / sparse-checkout 対応(sparse 外の path は作業ツリーに無く、正規化後の add -A は削除として記録する → commit tree と不一致で遮断= 検査していない内容を通さない側。
   本リポは sparse-checkout 未使用・限界として宣言)/ FAIL 時の古い witness の削除(本 ECO の範囲外。stale witness は検査済み tree にしか一致しない)。

## 2. 影響なし予測(製造前・凍結)

diff= `method/tools/self-conformance.py`(witness 関数の分割・正規化・較正行の追加〔C18〕)+台帳系のみ。hook・templates・.github・schemas は diff 0。
`S`/`h` entry が 0 件の環境(本リポの現状・CI)では **witness の tree は是正前後で同一**(V2 で実測)。C18 の PASS 行が 1 行増える(較正行)以外、C1〜C17 の判定・メッセージは不変。
C18 の NA 宣言(CI)は不変 — 較正行は NA 判定の前に出す。

## 3. 受入条件(製造前に凍結・二部形・ECO-080)

- V1(条件): 較正 3 腕(skip-worktree / 対照 / 失敗)が本番の C18 行で毎回実測され、①で tree の blob= 作業ツリーの bytes・実 index の blob とフラグが不変であること — 検査法: `[C18] PASS witness 較正 …` 行+独立検査官による再現スクリプトの再実行。
- V2(条件): フラグ 0 件の作業木で、是正前(baseline の tool)と是正後の witness tree が同一であること — 検査法: 両版の関数を同じ作業木に適用して tree を比較(製造者が実測・座標を記録)。
- V3(条件): `update-index` / `add` / `write-tree` の失敗で witness が書かれず、既存 witness が削除され、`[witness]` 行が出ること — 検査法: 失敗腕(③)+手動で書込不能にした `.git` の実測 1 回。
- V4(条件): hook の diff 0・witness 形式不変・pre-push が是正後の witness で ADVANCE すること — 検査法: `git diff --stat bomdd/hooks/`・本 ECO の push 自体。
- V5(条件): diff が allowed_paths のみ・self-conformance 全 PASS(exit 0 観測後に commit)・CI success であること。
- V6(条件): 異系統の独立検査(EQ-002・workspace-write)が ACCEPT であること。
- V7(条件): 較正 receipt(trigger ①③・receipt_author_role= producer)があること。

## /preflight receipt(起動経路: **自発** — 既裁定の適用実装の開始時〔bug-fix 類〕)

- 分類= 既裁定の適用実装(user 2026-10-03「2:A」)。baseline `069e0d5`= **confirmed** / 次番 092= **confirmed** / 機序= **confirmed**(L1683〜1705 実読+隔離リポで再現・対照腕つき)/
  `git add -A` が `S`/`h` entry を更新しないこと= **confirmed**(再現の実測)/ `update-index --no-skip-worktree` が `GIT_INDEX_FILE` の index に作用すること= **unknown**(製造時に実測。
  作用しなければ代替= 一時 index を `read-tree HEAD` から作り直す)/ hook の契約= **confirmed**(pre-push 実読・tree 1 行+PASS 1 行)/ 同一ファイルへの進行中 ECO= ECO-091(同時起票・対象関数が別・allowed_paths を共有)。
- 開始判定: **PROCEED_WITH_LIMITS**(限界= 正規化の作用先の実測待ち・代替案を保持)・override 0。

## /converge receipt(起動経路: 自発 — 拒否か正規化かの設計)

- **判定: 収束**(round 軌跡: 4→2→0)。
- DoD: ✔ witness の tree が検査した作業ツリーの bytes を含む / ✔ 実 index を変えない / ✔ 失敗で witness を書かず古い witness も残さない(無音にしない)/ ✔ 対の陽性対照を持つ / ✔ hook は不変。
- round 1(新規 4 件): ①拒否(書かない)か正規化か → 正規化(拒否は skip-worktree 常用者の push を永久に塞ぐ・証明できる手段がある)②assume-unchanged(`h`)も同型 → 両方外す
  ③パスの受け渡しは `-z --stdin`(空白・非 ASCII のパス)④失敗時に古い witness を残すと「書けなかった」ことが見えない → 削除+`[witness]` 行。
- round 2(新規 2 件): ⑤CI では witness は使われない(NA)が、較正は関数の性質なので CI でも走らせる ⑥sparse-checkout は skip-worktree を大量に使う → 正規化後は削除として記録され
  commit tree と不一致= 遮断(安全側)。本リポ未使用・限界として宣言。round 3: 0 件。
- 検証した主張: 機序(実読)/ 再現(隔離リポ・対照腕・実 index 不変)/ 露出 0 件(`git ls-files -v`)/ hook の比較対象(tree 1 行)。
- 敵対自問: 「正規化は『検査していない内容を通さない』という ECO-046 の厳密さを緩めないか」— 緩めない。正規化が入れるのは作業ツリーの bytes= 検査が読んだもの。
  index の bytes を証明していた是正前の方が、検査していない内容(index 側)を通していた。「失敗時の witness 削除は過剰か」— 削除しないと直前 PASS の tree に一致する commit が
  通るが、それは検査済み tree なので実害はない。削除するのは「書けない理由を見せる」ため(温度計)— 判定の意味は変えない。
- 未収束事項: なし(`update-index` の作用先は製造時の実測項目・代替案あり)。

## 4. 製造(2026-10-03・製造者 EQ-001)

- 製造物(`method/tools/self-conformance.py`): `_witness_tree(root, git_dir) -> (tree | None, why)`(複製 → `ls-files -v -z` で `S` / 小文字タグの path を抽出 → 一時 index 上で
  `update-index --no-assume-unchanged -z --stdin` と `update-index --no-skip-worktree -z --stdin` を**別々に** → `add -A` → `write-tree`。各 git の非 0 は `(None, why)`)/
  `_witness_selftest()`(3 腕・`_cleanup_tmp` で後片付け)/ `_write_selfconf_witness`(`(None, why)` のとき `witness.unlink(missing_ok=True)`+`[witness] 書出し省略(判定不変・証明しない・ECO-092): <why>` を stdout と stderr へ)/
  `c18_prepush_witness` 冒頭に較正行(NA 判定の前・CI でも実測)/ C18 の限界宣言に (6) を追記。hook は不変。
- **製造中の発見(preflight の unknown が顕在化)**: `update-index --no-skip-worktree --no-assume-unchanged -z --stdin` を**同じ呼び出し**に並べると、git 2.47.1 は rc 0 を返すが
  skip-worktree のフラグが残る(一時 index の `ls-files -v` が `S` のまま・tree の blob= index の bytes)。Git Bash で引数の与え方 3 変種(path 引数 / `--stdin` / `-z --stdin`)を
  **`--no-skip-worktree` 単独**で試すと全て効く(blob= 作業ツリー)。update-index の実装は assume-unchanged 系の指定があればその処理だけで返る分岐を持つ(片方のみ適用・無音)。
  是正= 2 つのオプションを別々の呼び出しにする(§1-1 の「正規化」の手段の修正・範囲は不変)。代替案(`read-tree HEAD` から一時 index を作る)も実測で有効だったが、
  §1 の宣言どおり正規化で実装した(実 index の複製を基礎にする方が、intent-to-add・staged 削除などの既存の扱いを変えない)。
- **範囲外の発見**: `method/tools/bomdd-witness.py` の `worktree_tree`(運転層の receipt が束縛する tree・W1「C18 と同一の定義」)も同じ機序(実 index の複製 → `add -A`・フラグ正規化なし)を持つ。
  本 ECO の凍結範囲(self-conformance.py)の外。是正後は `S`/`h` entry がある作業木で両者の tree が食い違う(bomdd-witness は自分の produce/verify で自己整合するため機械は止まらないが、
  証明する bytes は index 側のまま)。後続 ECO で同じ正規化を適用する(OBS-20261003-02 の同型・同一リポのため件数には加算しない)。

## 5. 受入の実測(2026-10-03・製造者・独立検査 r1 の前)

- **V1**= PASS(観測: 較正 3 腕を関数で直接実行 — `skip-worktree 腕(tree の blob= 作業ツリー・実 index 不変)=True・対照腕=True・失敗腕(書かない)=True`。
  是正前の 1 回目は skip-worktree 腕= False(上記の発見)→ 2 呼び出しに分けて True。本番の全検査(`--dotnet` 込み・2 回目)で
  `[C18] PASS witness 較正 skip-worktree 腕(tree の blob= 作業ツリー・実 index 不変)=True・対照腕=True・失敗腕(書かない)=True` を観測・`self-conformance passed`・exit 0・witness 書出し `54a560248930…`)。
- **V2**= PASS(観測: 本リポの作業木〔`S`/`h` entry 0 件〕で、是正前の経路〔複製+add -A+write-tree〕と `_witness_tree(ROOT, git_dir)` の tree が同一 `90038fb334139243c6a5d36c274b1aadac97b8d0`・why=「フラグ正規化 0 件」)。
- **V3**= PASS(観測: 隔離リポで `.git/index` を `b"garbage"` で上書き〔実の git 失敗〕→ `ls-files 失敗(exit 128): fatal: … index file smaller t…` を why として `(None, why)` →
  事前に置いた stale witness `deadbeef\nPASS\n` が**削除**され、stdout と stderr に同一の `[witness] 書出し省略(判定不変・証明しない・ECO-092): …` 行。正常経路では witness が書かれ出力なし)。
- **V4**〜**V7**= §6。

## 6. 独立検査(異系統・Codex EQ-002・入口 bomdd-run から `--report`/`--range` つきで起動・workspace-write)

### 6.1 r1(2026-10-03・range= 境界探索)— 報告: [independent-inspection-eco-092.md](reports/independent-inspection-eco-092.md)

- 起動: commit `5d90ba4`(witness tree dbaba17fd20a・入口 `ADVANCE ECO-092 OK → next · launching`)→ `cell exit 0` → `report REJECT sha256:b1859d0f96f0 (EQ-002)`・台帳 `range: 境界探索`。検査官の作業木: 開始・終了とも clean・commit 0・`.git/index` 操作 0・外部 API なし。
- 判定: **REJECT IA-01, IA-02**(blocking 2・non-blocking 2)。対象機能(C18 witness)は V1〜V4 PASS・境界探索 19 行(assume-unchanged / 両フラグ / 複数+サブディレクトリ / 空白・非 ASCII パス / 作業ツリー削除+S /
  未追跡 / .gitignore / intent-to-add / staged 削除 / 非 git root / init 直後 / 破損 index / merge conflict / write-tree 失敗注入 / sparse-checkout / 2 オプション同時指定の独立再現)で「検査した作業ツリーと違う bytes の証明」0・実 index の変化 0。
- **IA-01(blocking・V5)— 帰属= 環境(検査官の sandbox)**: 検査官環境で fast tier が C14 kit-freshness の **REAL 腕のみ FAIL**(他は PASS・C18 2 行 PASS)・exit 1。受理側の実測: 同一 tree `dbaba17fd20a` で製造者の fast tier exit 0(commit 前・witness gate)+
  **CI run 37104338649 success**(5d90ba4・ubuntu / windows の fast job とも)。REAL 腕= 実 scaffold を OS temp に作る検査で、**ECO-075 r1・ECO-081 r1 IA-02 と同型(3 例目)**の sandbox 制約。製造物は非改変。
  再発防止= r2 ブリーフに「C14 REAL は sandbox で FAIL することが既知・V5 の self-conformance は製造者実測+CI で測り、検査官は C18 行の文言を読む」と明記(ブリーフの欠陥として受理側に帰属)。
- **IA-02(blocking・V5)— 帰属= 受理側の台帳**: 窓 `069e0d5..5d90ba4` に ECO-094 の起票 2 パス(order・preregistration)が入り、3 ECO の和集合の外。窓が開いている間に別 ECO を起票した受理側の手順の問題。
  是正= ECO-091/092 の allowed_paths に ECO-094 の台帳系 2 パスを追加(理由を register のコメントに記す)。ECO-094 の diff は台帳系のみ・tools 非接触(V5 の意味= 製造物の窓は変わらない)。
- **IA-03(non-blocking)— 帰属= 上流(§1-5 の限界宣言)**: sparse-checkout では `add -A` が sparse の適用範囲を尊重し、フラグを外しても sparse 外の path は index の内容のまま tree に残る(「削除として記録され遮断」は誤り)。
  是正= C18 の限界宣言 (6) を実挙動に合わせて書き直し(index の内容は通常 HEAD と同一で通る・sparse 外で index≠HEAD の稀な場合は検査していない bytes を証明する= 限界)。§1-5 の文は凍結のまま、本節で訂正。
- **IA-04(non-blocking)— 帰属= 受理側のブリーフ**: 未解決 merge conflict は一時 index への `add -A` が作業ツリーの内容で解消するため write-tree の失敗腕にならない(検査官は exit 17 の注入で分岐を確認)。ブリーフの例示の誤り。
- 次: r2(range= 是正確認+回帰: IA-02 の窓・IA-03 の宣言・V1〜V4 の回帰。IA-01 は環境帰属で製造物非改変— r2 では self-conformance の全体 exit を判定に使わず C18 行を読む)。

### 6.2 r2(2026-10-03・range= 是正確認+回帰・範囲限定)— 報告: [independent-inspection-eco-092-r2.md](reports/independent-inspection-eco-092-r2.md)

- 起動: 是正 commit `e096369`(witness tree 3a69231ffb83・入口 `ADVANCE ECO-092 OK → next · launching`)→ `cell exit 0` → `report ACCEPT sha256:a7c1da4c32be (EQ-002)`・台帳 `range: 是正確認+回帰`。
- 判定: **ACCEPT**(所見なし)。1 IA-02 窓= 20 パス全て和集合の内・理由コメントあり / 2 IA-03 宣言= 実挙動どおり・`_witness_tree` 実装は不変(差分はコメント 4 行)/ 3 V1〜V4 回帰= 全 PASS(V2 は隔離 clone で是正前後とも tree 3a69231ffb83)/
  4 境界表 6 行の抜き取り= r1 と同一判定・実 index 不変。
- **環境観測(範囲外・記録)**: 検査官の作業木は **sparse-checkout 状態で S/h entry が 1151 件**(r1 では 0 件— sandbox の構成が round 間で変わった)。V2 は対象 revision を Git bundle 経由で OS temp の隔離リポへ展開して測った。
  初回の隔離 clone は dubious ownership で不成立・2 回目は後片付けの sandbox アクセス拒否で停止(測定値に採用せず)。本 ECO の対象(skip-worktree を持つ作業木で witness が index の bytes を証明する)が検査官自身の環境で**実在した**ことになる—
  是正前の実装なら、その作業木での PASS witness は検査していない bytes を証明していた(自然発生の露出 1 例・ただし本リポの製造者環境ではなく検査官 sandbox の clone)。

## 7. クローズ(クローズ時に追記)
