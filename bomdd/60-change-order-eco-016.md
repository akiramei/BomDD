# ECO-016 — process-validator の証拠意味論・台帳解析の fail-closed 強化(独立検査 REV 8 件の是正)

> 状態: **filed(2026-07-26)**。製造前 — gate ①(製造承認)待ち。
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

## 効果測定(宿題)

- 是正後の再独立検査(ECO-017 と合同・fresh 検査官)で validator 系所見 0 件になるか
