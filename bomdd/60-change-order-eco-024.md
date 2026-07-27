# ECO-024 — 第 4R 独立検査の在庫可能分 5 件(台帳洗浄・dirty worktree 隠蔽・fail-open 残り・qualification の profile 非追随・同名衝突)

> 状態: **filed(2026-07-27・gate ① 待ち)**。
> 発見経緯: ECO-019 是正後の第 4 ラウンド独立検査(EXP-20260727-06 の測定を兼ねる・
> Codex fresh・read-only・情報遮断)。報告= bomdd/reports/independent-reinspection-eco-019.md。
> 検査官提起 5 件は当方実プローブで**全件 CONFIRMED・誤検出 0**(通算 30 提起 30 CONFIRMED)。
> 任務A(ECO-019 の是正 5 件)は **5/5 CLOSED** — 本 ECO は新規所見のみを扱う。

## 起票(2026-07-27)

### 事実(実測 — 真正判定プローブ・報告の後付け注記に全ログ)

1. **IA-01(high)— 台帳の不正化→復旧で ID 削除を洗浄できる**: replay は解析不能 commit を
   warn のみで対象外にし(`reg_at → None → continue`)、復旧 commit は親台帳 None → base={} で
   比較されるため、素の削除なら `[E03] 台帳から削除された` で遮断される操作が、間に不正 YAML
   commit を挟むと `validate OK(0 entries)` になる(P1/P1b 対照で実測)。
2. **IA-02(high)— worktree の台帳書き戻しで HEAD の証拠欠落を隠せる**: 履歴再演は HEAD を
   走査し required を正しく算出するのに、E06 の突合先(現在 entries)は worktree/index から
   読むため、HEAD が trailer なし applied でも**worktree を staged へ書き戻すだけ(add 不要)**で
   validate OK(P2 実測)。
3. **IA-03(medium)— 保護パス履歴走査の git 失敗が fail-open**: 台帳再演の rev-list 失敗は
   die(exit 2)なのに、保護パス走査は `if pp.returncode == 0:`(else なし)で失敗時に
   その面だけ無言省略。親取得 `log -1` の失敗も `parents=[]` へ縮退(コード読解)。
   同一ファイル内で測定不能の扱いが面ごとに分岐 — ECO-017 の fail-closed 統一の残り。
4. **IA-04(medium)— qualification が installed profile の差分注入に追随しない**: sandbox は
   installed profile を複写するのに、台帳設置・遷移・trailer 付与はハードコード既定
   (`REGISTER`・`_reg_text('staged')`・`BomDD-ECO-Accept`)。register パスを正当に adapt した
   設備(validator 自体は validate OK)で full qualification が **FAIL — 製造を開始しない**
   (P4 実測)。発現は ECO-021 と同じ三態(誤 FAIL= IQ-06/08/POS/POS4・負例素通り= N2/N3/N4/N7・
   理由不一致= N5/N8)+DET 不一致。**ECO-021 の同族 — 導出化が protected_paths のみで
   register/initial/trailers が残った(OBS-20260727-16 の 2 例目)**。
5. **IA-05(low)— product/CAD 同名指定を事前拒否しない**: `bomdd-init Same --gui
   --cad-name Same` → 最終 exit 1(fail-closed 側)だが事前拒否がなく、git init 失敗宣言後も
   続行して同一ディレクトリへ product+CAD の生成残骸を重ねる(CAD パスが product 生成物を
   「既存のため保持」と誤認)(P5 実測)。

### 観測(境界帰着 — 是正対象にしない)

- **BOUNDARY-DUP-04(E11 decoy)**: `exit 0` 先行+validator 参照行を後置した decoy hook は
  E11 を素通りする(P3 実測)。検査官・当方とも「実行体は commit 権限者が書き換え可能」の
  宣言済み境界へ帰着と裁定 — 構造検査の強化は偽装との軍拡競争になる。E11 の到達目標が
  「素朴な無力化の検出まで」であることの明文化は裁定点 3。

### 見逃しの構造

1. **例外経路の親状態が「空」へ縮退する**(IA-01/03 共通): 解析不能・git 失敗という測定不能
   事象が、fail-closed(die)でなく「空集合として続行」へ落ちる経路が残っていた。ECO-017 の
   fail-closed 統一は主経路を覆ったが、**replay 内部の縮退分岐**(reg_at None・parents 失敗・
   保護パス走査失敗)が被覆外だった — silence §16(a)(対象集合が空・不在・実行不能な場合に
   無音 PASS しないか)の replay 内部版。
2. **同一検査の入力が 2 つの世界(HEAD と worktree)から来る**(IA-02): required の算出は
   HEAD 世界・突合は worktree 世界 — 単一走査内の基準不一致(silence §16(e) の入力源版)。
3. **導出化の部分適用**(IA-04): ECO-021 は「既定値のハードコード禁止」を保護パスプローブに
   適用したが、同じ構造(profile 差分注入点 vs sandbox 既定)が register/initial/trailers に
   残った — 是正の閉包走査が「同型の全変数」まで及んでいなかった。

## 是正方針案(製造前・凍結前の草案)

1. **IA-01**: replay 範囲の台帳変更 commit が 1 件でも解析不能なら **die(exit 2・測定不能)**。
   「warn して続行」を廃止(過去に恒久不正 commit が残るリポは validate 不能になるが、それは
   fail-closed の正しい側 — 復旧には履歴修正でなく前進 commit での宣言を要求)。
2. **IA-02**: **validate モードの突合先を HEAD 台帳へ変更**(履歴再演と同一世界)。
   pre-commit/commit-msg モードは現行どおり index(commit 対象の検査 — 正しい設計)。
   worktree/index が HEAD と乖離している場合は validate が注記を出す(判定は HEAD 基準)。
3. **IA-03**: 履歴判定に使う **全 git subprocess の非 0 を die(exit 2)へ統一**
   (保護パス rev-list・親取得 log -1・cutoff 検出)。空結果と実行失敗を構造分離。
4. **IA-04**: sandbox の台帳パス・初期状態・trailer 名を **installed profile から導出する
   単一関数**へ(ECO-021 `_probe_rel` の一般化)。受入に**非既定構成対照**(register/initial/
   trailers を変えた adapt profile での full qualification 全 PASS)を追加。
5. **IA-05**: bomdd-init で product/CAD の **resolved path 同一を生成前に拒否**(残骸ゼロ)。
6. **境界文書の追記**: process-profile.yaml「既知の限界」節へ E11 の到達目標
   (素朴な無力化の検出まで — decoy は境界)を 1 行追記。

## 裁定を要する設計点(gate ①)

1. **IA-01 の die 範囲**: replay 範囲の解析不能 = 即 exit 2(推奨)vs 当該 commit のみ違反化。
   推奨理由= 「読めない台帳」は違反の有無を判定できない測定不能であり、部分継続は洗浄面を残す。
2. **IA-02 の突合先**: validate= HEAD 正本(推奨)vs 乖離検出で測定不能化。推奨理由=
   validate の意味論は「履歴と現在の合法性」であり、未コミット作業で結論が変わるべきでない。
3. **E11 境界追記**: 1 行追記のみ(推奨・軍拡競争に入らない)vs 到達可能性検査の追加。
4. **IA-04 の対照規模**: 導出関数化+非既定構成対照 1 本(推奨)vs 全変数の直積対照。

## 受入基準(事前登録 — 製造前に凍結する)

- **N19**(IA-01): staged 追加 → 台帳不正化 → 復旧(全 --no-verify)→ validate **exit 2**
  (測定不能・洗浄不成立)。素の削除は従来どおり E03(回帰)。
- **N20**(IA-02): HEAD に trailer なし applied・worktree を staged へ書き戻し → validate が
  **E06 を維持**(隠蔽不成立)。index stage 版も同結果。
- **N21**(IA-03): 保護パス走査の git 失敗注入(selftest モック)→ **exit 2**(無言省略しない)。
- **N22**(IA-04): register/initial/trailers を変えた adapt profile で full qualification
  **全 PASS**(誤 FAIL 解消)+既定 profile の全対照回帰不変。
- **IQ/初期**(IA-05): 同名指定 → 生成前拒否・**生成物ゼロ**(残骸なし)。
- 回帰: 既存全対照(30+ECO-023 分)PASS・DET 2 回一致・self-conformance 全 PASS・
  **push 後 CI 緑の実測**(ECO-020 規律)。
- 陽性対照の意味論: POS(正常 ECO 全経路)が全変更後も PASS。

## 影響分析(製造前予測 — 未凍結)

- 変更: `method/templates/process-core/tools/process-validator.py`(IA-01/02/03)・
  `method/templates/process-core/tools/process-qualification.py`(IA-04+N19〜N22)・
  `method/tools/bomdd-init.py`(IA-05)・`method/templates/process-core/process-profile.yaml`
  (限界節 1 行)。
- 正常運用への影響予測: (i) 解析不能履歴を持つリポは validate が exit 2 になる(意図的・
  fail-closed)(ii) validate の判定が未コミット編集に依存しなくなる(意図的)(iii) 既定
  profile の scaffold 判定は不変。既存製品リポへは kit 再設置まで非波及(ECO-004 設計)。

## スコープ外(明示)

- IA-02/03(cutoff 前送り・遡及適用)・BOUNDARY-DUP 系の是正(宣言済み境界 — リポ外アンカー
  系列 EXP-20260727-07 の守備範囲)。
- E11 の構造検査強化(裁定点 3 で追記のみ推奨)。
- 既設リポ(MoviePad)への一括再配布(更新は手動 — ECO-021 記録済みの経路)。
