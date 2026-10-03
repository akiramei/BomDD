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

## 4. 製造・受入・クローズ(製造時に追記)
