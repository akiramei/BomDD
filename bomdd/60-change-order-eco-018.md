# ECO-018 — 強制層の自己保護と履歴合法性の二層化(再独立検査 NEW high 3 件の是正)

> 状態: **implemented(2026-07-26)**。gate ①(製造承認)通過 → 製造中。

## 裁定(gate ① — 2026-07-26)

- **製造承認(2026-07-26・maintainer — 「OK. 製造に入って」= 推奨 4 点の一括採択)**。
  baseline を起票コミット b671571(是正開始直前)へ更新。
- 裁定 4 点は**すべて推奨案を採択**:
  1. replay の cutoff= **profile 追加 commit の自動検出**+ profile の `history_replay_since` で
     上書き可(導入前履歴を違法にしない)
  2. 履歴違反の reason code= **既存 E02/E03 を再利用**し `history:<sha>` を文脈に付す
  3. commit-msg の検査範囲= **equipment+protected の両方**(単一 hook 削除への冗長性)
  4. 性能= 台帳変更 commit 限定・上限なし(所要を受入で実測)
- **製造中の設計確定(裁定 1 の帰結として必要になった追加規則・理由記録)**:
  **証拠要求(E06/E09)の適用範囲も導入点で区切る** — 導入点より前から台帳に存在した ECO は
  trailer 証拠を要求しない(導入前の履歴には trailer 規約が存在しなかったため)。判定は
  「replay 範囲内で初出した cid か」で機械決定する。これがないと、process-core を後から導入した
  リポの既存 applied エントリが全件 E06 で誤 FAIL する(裁定 1「導入前履歴を止めない」と同じ
  趣旨の、証拠面への適用)。新規 scaffold では cutoff= root commit のため全エントリが対象
  (既存挙動は不変)。
> 出典: ECO-016/017 合同再独立検査(transfer-04 様式・Codex gpt-5.6-sol・REJECT)—
> bomdd/reports/independent-reinspection-eco-016-017.md(真正判定 7/7 CONFIRMED・実プローブ 3)。
> 本 ECO は high 3 件(NEW-ECO01617-01/02/03)を是正する。medium 4 件はスコープ外(後述)。

## 起票(2026-07-26)

### 問題の構造(3 件を貫く 1 つの命題)

3 件はいずれも「**強制層(hook+worktree 上の profile)は自分自身を守れない**」の系である:

- **NEW-01**: `git rm bomdd/hooks/pre-commit` → pre-commit 自身が起動しないため E08 が発動しない
  (実プローブで commit 成立を確認)。commit-msg hook は生きているが、現在は equipment/protected
  を検査しない。
- **NEW-02**: 同一 commit で profile の `open_states` を `[applied]` へ書換え → enforcement が
  index 側 profile を読むため、**改竄 profile が自身の通過条件を定義できる**(実プローブで
  commit 成立を確認)。
- **NEW-03**: `--no-verify` で新規 ECO を born-applied+同 commit に accept trailer → validate が
  通す(実プローブで `validate OK` を確認)。linked evidence は「遷移が発生したこと」だけを
  照合し、**その遷移が合法だったか**を照合しない。

**設計方針**: 防止(prevention)を完全化しようとしない — hook は worktree 実体に依存する以上、
実体を消されれば起動しない。BomDD が担保すべきは「**改竄が機械検出可能であること**(証拠の
一貫性)」であり、そのために**二層化**する:

| 層 | 実体 | 守るもの | 回避されたら |
|---|---|---|---|
| 第 1 層 | pre-commit / commit-msg hook | 即時遮断(作業者の眼前) | 第 2 層が検出する |
| 第 2 層 | `validate`(CI・手動・qualification) | 履歴の合法性・設備の完全性 | 記録が「検出可能に不整合」になる |

### 是正方針案(製造前・凍結前の草案)

1. **NEW-03(主軸)= 履歴合法性の再演**: `validate` に **history replay** を新設 —
   台帳を変更した各 commit について `check_transitions(parent 台帳, commit 台帳)` を再計算し、
   履歴上の違法遷移(E02/E03)を検出する。hook を `--no-verify` で回避しても、記録に残った
   違法遷移が後から必ず検出される(第 2 層の核)。
   - linked evidence(E06)は **合法遷移のみを証拠として採用**する(違法遷移で植えた trailer は
     承認証拠にならない)。
   - merge commit は親ごとに比較(ECO-016 の複数親合算と整合)。
2. **NEW-02 = enforcement profile の HEAD 優先**: 遮断判断に使う profile は **HEAD 版**を正とする
   (index/worktree 版は「これから提案される設定」であって現行の規則ではない)。profile 自体の
   変更は E08(open ECO 必須)を通ってから次 commit 以降に効く。HEAD に profile が無い場合
   (初回設置)は従来どおり worktree 版・equipped=False 経路。
   - 「規則の変更が同一 commit で自分を通す」経路の遮断 — ECO-016 の E01 HEAD 側判定(REV-10)の
     profile 面への適用。
3. **NEW-01 = 設備完全性の二重検査**:
   - (a) **commit-msg も equipment/protected を検査**する(現在は transitions+trailer のみ)。
     片方の hook を消しても、もう片方が E08 を発動する。
   - (b) **validate に設備完全性検査(新 reason code E10)** — HEAD に profile が実在するのに
     CORE_ASSETS(hooks×2・validator・profile)が欠落していれば FAIL。両 hook を同時に消しても
     第 2 層で検出される。
   - **残余の限界(明記する)**: 両 hook を消し、かつ validate/CI を一度も走らせない運用では
     即時検出されない。これは信頼境界の外(意図的な内部者)であり、本 ECO の到達目標は
     「記録が検出可能に不整合になること」までとする — order の完了判定にこの限界を残す。

## 裁定を要する設計点(gate ① で裁定)

1. **history replay の起点(cutoff)**: (a) profile を最初に追加した commit 以降
   〔`git log --diff-filter=A -- bomdd/process-profile.yaml`〕/ (b) profile の
   `history_replay_since` で明示指定可 / (c) 全履歴。**推奨= (a)+(b) 併用** — process-core を
   後から導入したリポの導入前履歴を違法として止めない(fail-closed の誤適用回避)。
2. **履歴違反の reason code**: (a) 既存 E02/E03 を再利用し `history:<sha>` を文脈として付す /
   (b) 新コード E11 を割り当てる。**推奨= (a)** — 不変条件は同一で検出層だけが違う
   (ViewPrism2 の E15〜E19 が層でなく不変条件で採番している設計と整合)。
3. **commit-msg の検査範囲拡大**: equipment のみ / equipment+protected。**推奨= 両方**
   (pre-commit と重複するが、単一 hook 削除に対する冗長性が目的 — 防御の重複は意図的)。
4. **性能**: 台帳変更 commit のみ走査(`git log --format=%H -- <register>`)で十分か、上限件数を
   設けるか。**推奨= 上限なし・台帳変更 commit 限定**(実測を受入基準に含め、遅ければ次 ECO)。

## 受入基準(事前登録 — 製造前に凍結する)

- 陽性対照: 正常 lifecycle(起票→保護変更→accept)が history replay 込みで validate PASS・
  既存 selftest/OQ 全項目 PASS(判定不変)
- 負例(実 Git 経路・qualification へ恒久収載):
  - N9: `--no-verify` の born-applied+同 commit trailer → **validate が E02 を検出**(NEW-03)
  - N10: `--no-verify` の遷移飛び越し(staged→applied を 3 状態 profile で)→ **E03 検出**
  - N11: 同一 commit で `open_states` 書換え+保護パス変更 → **E01 遮断**(HEAD profile 優先・NEW-02)
  - N12: pre-commit のみ削除 → **commit-msg が E08 で遮断**(NEW-01a)
  - N13: 両 hook 削除(--no-verify 相当の状態)→ **validate が E10 を検出**(NEW-01b)
  - N14: 違法遷移で植えた trailer は E06 の証拠に採用されない(合法遷移のみ linked)
- 陽性対照(誤 FAIL 方向): process-core 導入前の履歴を持つリポ(profile 追加前に台帳変更あり)で
  history replay が違反ゼロ(cutoff の効果測定)
- 決定性: qualification 2 回実行の判定・理由集合一致
- 回帰: self-conformance 全 PASS・既存 OQ 8 対照(POS・N1〜N8)判定不変・所要の実測記録
- **再独立検査**: 是正後に fresh 検査官で NEW-01/02/03 の再現条件を再投入し閉鎖確認

## 影響分析(製造前予測 — 未凍結)

- 影響なし予測: `method/templates/process-core/tools/process-validator.py`・
  `method/templates/process-core/hooks/commit-msg`・
  `method/templates/process-core/tools/process-qualification.py`(負例 N9〜N14 の追加)・
  `method/templates/process-core/process-profile.yaml`(`history_replay_since` 任意キーの追記)
  以外 diff ゼロ予測。
- **正常運用への影響**: 起票→是正→accept の正規経路は不変(第 1 層の判定は同じ)。
  変わるのは (i) profile 変更が次 commit から効く(同一 commit 自己適用の禁止)
  (ii) validate の所要が台帳変更 commit 数に比例して増える(実測を受入に含む)。
- **既存リポへの波及**: kit 経由の凍結配布のため再設置まで非波及(ECO-004 設計)。ただし
  **本リポ自身(bomdd/)は process-core 未設置**のため自己適用の影響はない(観測: 方法論リポは
  自リポの hooks を持たない — 自己適用の是非は別途裁定)。

## スコープ外(明示)

- **medium 4 件は据え置き**: NEW-04(IQ-02 の decoy — OQ の実 hook 実行が重複防御として機能する
  ことを再検査官も認めた)/ NEW-05(`GIT_TRACE` side channel — 判定汚染でなく副作用面)/
  **NEW-06(octopus merge の第 3 親以降 — false-reject 方向・実害は誤 FAIL)**/ NEW-07(bomdd-init の
  env 無加工継承)。理由= high 3 件の二層化が構造命題であり、medium は独立した小欠陥。
  次 ECO または rule of three 待ち(NEW-06 は誤 FAIL 方向のため優先度は medium 内で最上位と記録)。
- 本リポ(BomDD harness)自身への process-core 自己適用

## 効果測定(宿題)

- 再独立検査で NEW-01/02/03 が CLOSED になるか(通算 20 提起の閉鎖率)
- 「hook 回避は第 2 層で検出可能」の命題が実測で成立するか(N9/N13 が主証拠)
