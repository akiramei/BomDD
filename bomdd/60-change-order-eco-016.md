# ECO-016 — process-validator の証拠意味論・台帳解析の fail-closed 強化(独立検査 REV 8 件の是正)

> 状態: **verified(2026-07-26)**。fix= 5d4a266(+衛生追補 b525d01)・検証 V0〜V3 全 PASS・
> 窓は accept で閉鎖。

## 裁定(gate ① — 2026-07-26)

- **製造承認(2026-07-26・maintainer — 「製造承認します。ECO-016 は案a で」)**。
  baseline を起票コミット d5f2493(是正開始直前)へ更新。
- **裁定点= 案a 採択**: 脱出経路「profile 撤去で無効化」を **ECO 経由**へ改訂 —
  設備の武装解除も変更管理の対象。gate ① 裁定 5(ECO-015)の当該部分を supersede する。
- **スコープ裁定(製造承認時・理由記録)**: allowed_paths へ
  `method/templates/process-core/hooks/` を追加。理由= 案a の帰結 — profile が作業ツリーから
  削除された状態では hook が `[ -f profile ] || exit 0` で validator 起動前に素通しするため、
  「HEAD に profile が実在するなら削除中でも validator を起動する」結線は hook 層にしか置けない
  (REV-01 の再現経路そのもの)。起票時 affected_refs の欠落として正直記録。
- 設計確定: 新 reason code 2 件 — **E08** equipment-change-without-open-eco(設備自己保護・
  HEAD に profile が実在する場合のみ発火= scaffold/設置の初回 commit を誤遮断しない)/
  **E09** evidence-state-divergence(逆行乖離+fix→accept 順序= ViewPrism2 E17 相当)。
  placeholder sentinel= `<一行要約>` 完全一致。
> 出典: ECO-015 後追い独立受入検査(transfer-04 様式・Codex gpt-5.6-sol・REJECT)—
> bomdd/reports/independent-inspection-eco-015.md(真正判定 13/13 CONFIRMED・誤検出 0)。
> 本 ECO は validator 系 8 件(REV-01 部分/02/03/04/08/09/10/13)を是正する。
> runner・init・C11 系 5 件は ECO-017。

## 起票(2026-07-26)

対象所見と是正方針(各所見の再現条件・行番号は報告書原本を正本とする):

1. **REV-01(部分)— profile 部分変異の無音無効化+自己保護の欠如**:
   - profile スキーマの厳格検証(nested 必須キー: trailers.fix/accept の存在と非空文字列・
     states/open_states/terminal_extra の型と包含関係・initial ∈ states・重複状態禁止)。
     不正 profile は**測定不能 exit 2**(hook 文脈では遮断)— `if not name: continue` の
     無音 skip を排除。
   - **自己保護パスをコードに固定**: `bomdd/process-profile.yaml`・`bomdd/hooks/`・
     `bomdd/tools/process-validator.py` 等の設備自身の変更・削除は open ECO を要求
     (profile の protected_paths 設定に依存しない常時保護 — 設備が自分の武装解除を検査する)。
   - **裁定点(gate ①)**: 裁定 5 の脱出経路「profile を撤去すれば無効化」の扱い。
     案a= 撤去も ECO 経由に改訂(自己保護の帰結・監査可能な無効化)/案b= 現行維持
     (無審査の脱出経路を残す)。**推奨= 案a**(REV-01 の趣旨・「宣言の解除」も変更管理の対象)。
2. **REV-02 — trailer 解釈の git 意味論乖離**: parse_trailers を**最終 trailer ブロックのみ**
   認識へ変更(ViewPrism2 validate_bom の最終段落ブロック解析と同型)。単一実装の維持
   (commit-msg 検査と履歴証拠検査が引き続き同一関数を共有)。中間段落 trailer・件名行・
   trailer 後に本文が続く形を負例へ追加。
3. **REV-03 — 証拠の SHA・遷移紐付けなし縮約**: trailer 証拠を ID 集合でなく
   **commit SHA つき**で保持し、「trailer を持つ commit で当該 register 遷移が実際に発生した」
   ことを照合(git 履歴の register diff との突合)。**逆行乖離検査を追加**(accept 証拠が
   実在するのに現在状態が staged 等 = ViewPrism2 E17 相当の移植 — ECO-015 対応表の未移植 1 件を解消)。
   事前植込み(無関係 commit への trailer)負例が拒否されること。
4. **REV-04 — 台帳解析の無音 skip**: top-level mapping・changes の list 型・全 entry の
   mapping 型・id 必須・**id 一意性**(重複 = ECO-011/012 の 1 段上の同型)を強制。不正は
   skip でなく測定不能 or 違反。placeholder 判定を title 先頭 `<` から**明示 sentinel の完全一致**へ。
5. **REV-08 — git 障害の証拠ゼロ化**: `git log` 失敗を「履歴ゼロ(HEAD なし)」と区別し、
   git 障害・非 git ディレクトリは**測定不能 exit 2**(docstring 契約との整合回復)。
6. **REV-09 — 未知旧状態の terminal 洗浄**: old/new 両状態の known 検証を terminal 遷移許可より
   **先に**評価(未知→rejected で E03 を洗浄できない)。
7. **REV-10 — E01 の index 側判定**: 保護パス変更の許可判定を **HEAD 時点の open ECO** に変更
   (起票 commit の先行を強制 — donor 不変条件「起票が先」の完全化)。同一 commit での
   起票+保護変更は負例。
8. **REV-13 — merge 複数親の非考慮**: merge 中(MERGE_HEAD 実在時)は HEAD と MERGE_HEAD 双方の
   register を読み、状態順序で比較元を合算(ViewPrism2 の複数親合算不変条件の移植)。
   正規遷移済み branch の merge を陽性対照へ追加(誤 FAIL 方向の是正)。

## 受入基準(事前登録 — 製造前に凍結する)

- 陽性対照: 既存 selftest 全項目+新規変異(下記)全 PASS・OQ POS(2 commit 順の正常 lifecycle)回帰
- 負例(selftest へ恒久収載・各所見対応): profile 部分変異 3 種(trailers.accept 削除/空文字列/
  states 型不正)→ exit 2 / 設備自己変更の ECO なし staged → 遮断 / 中間段落 trailer → 証拠
  不成立 / 事前植込み trailer → 拒否 / 逆行乖離(staged+accept 証拠)→ 検出 / 重複 id → 検出 /
  changes 非 list・非 mapping entry → 測定不能 or 違反 / 非 git ディレクトリ validate → exit 2 /
  未知旧状態→terminal → E03 / 同一 commit 起票+保護変更 → E01 / merge 陽性対照 → 誤 FAIL なし
- 決定性: qualification 2 回実行の判定・理由集合一致(ECO-017 との統合検証で可)
- 回帰: self-conformance 全 PASS(C4/C11)・既存 scaffold 生成物の形状不変
- ECO-015 対応表の更新(E17 相当の移植を反映・残る未移植の再明示)

## 影響分析(製造前予測 — 未凍結)

- 影響なし予測: `method/templates/process-core/tools/process-validator.py`・
  `method/templates/process-core/process-profile.yaml`(自己保護のコメント・sentinel 追記)以外
  diff ゼロ。既存の正常系判定(2 状態 lifecycle・placeholder skip の意味論)は不変 —
  変わるのは異常系の遮断方向のみ。REV-10 は正常運用(起票 commit 先行)に影響しない。
  kit 経由の配布物は本テンプレの凍結コピーのため、既存製品リポへは非波及(再設置まで旧版)。
- 順序依存: ECO-017 と対象ファイルが分離(016= validator+profile / 017= runner+init+C11)。
  窓の分離のため **016 → 017 の順で製造**(017 の受入は 016 適用後の validator を前提にできる)。

## スコープ外(明示)

- REV-05/06/07/11/12(runner・bomdd-init・C11)= ECO-017
- ECO-015 対応表で宣言済みの他の未移植(E14 lifecycle_evidence 宣言・ViewTube 7/8/9〜16)は据え置き

## 検証(2026-07-26・受入基準=起票時凍結分)

- **V0(selftest)**: 45 項目全 PASS — REV 対応の変異を恒久収載(profile 変異 5 種・trailer 意味論
  4 種・台帳構造 5 種・E08 4 種・E09 4 種・REV-09/10/13 各対照)。
- **V1(回帰)**: fresh scaffold の初回 IQ/OQ 全 PASS(IQ-01〜06・POS・N1〜N6・DET byte 一致)—
  既存 7 対照は新 validator でも判定不変。self-conformance 全 PASS(C1〜C11)。
- **V2(実 commit 経路の新負例 9 プローブ)**: P1 profile 部分変異(trailers.accept 削除)→
  exit 2 遮断 / P2 profile 削除・open ECO なし → **E08 遮断** / P3 profile 削除・open ECO あり →
  通過(**案a の監査つき撤去**・HEAD 版 profile で検査継続の note 出力)/ P4 同一 commit 起票+
  保護変更 → E01 / P5 中間段落 trailer → E05 / P6 事前植込み trailer+--no-verify → validate E06 /
  P7 重複 ID → 測定不能遮断 / P8 正規 applied 後の --no-verify 逆行 → validate **E09** /
  P9 merge 陽性対照(branch で正規 applied → main へ merge)→ 誤 FAIL なし+validate OK。
- **V3(決定性)**: qualification --runs 2 の判定・理由集合一致(V1 内 DET)。
- **正直記載**: (a) V2 初回実施でプローブ衛生の失敗 2 回 — P1 の復元不備(checkout が変異済み
  index から復元)で P2 が汚染され、さらに P2(再)は前プローブの残存 open ECO により「監査つき
  撤去」として正しく通過 → 以降のプローブが非管理状態で空振り(P8 の「profile なし素通し」が
  検出)。fresh scaffold+BASE 固定 reset で全数再実施した。**「E08 は open ECO があれば通す」
  仕様が検証治具自身の穴になった**教訓(検証環境の状態管理は fixture 再生成が正)。
  (b) 検証プローブの importlib 副産物(__pycache__)が fix commit に混入 → b525d01 で除去。
- 影響なし予測: 的中(diff は process-core 3 面+台帳系のみ・正常系judgment不変は V1 で確認)。

## 不変条件対応表の更新(ECO-015 対応表への追補)

- **E17(fix→accept 祖先順序・逆行乖離)= E09 として移植済み**(本 ECO)。
- E14(lifecycle_evidence 宣言・shallow 検査)= 引き続き未移植(据え置き)。
- 追加: E08(設備自己保護 — ViewPrism2/ViewTube に直接対応物なし・独立検査 REV-01 由来の新規)。

## 教訓(還元候補 — lesson-promote 経由)

- **検証プローブの状態復元は「差分の巻き戻し」でなく「fixture の再生成」で行う** — 検査対象が
  fail-closed/状態依存であるほど、汚染された状態からの「正しい挙動」が偽の PASS/FAIL を作る
  (本 ECO V2 で 2 回実測)。

## 効果測定(宿題)

- 是正後の再独立検査(ECO-017 と合同・fresh 検査官)で validator 系所見 0 件になるか
