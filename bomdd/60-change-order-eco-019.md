# ECO-019 — 第 2 層の基準統一・証拠要求単位の是正・設備無力化と保護パスの履歴検査(再々独立検査の在庫可能分)

> 状態: **verified(2026-07-27)**。fix= f6a840c・検証 V0〜V4 全 PASS・窓は accept で閉鎖。

## 裁定(gate ① — 2026-07-27)

- **製造承認(2026-07-27・maintainer — 「ECO-019 の製造に入って」= 推奨 4 点の一括採択)**。
  baseline を是正開始直前 f8cab0b(教訓還元の織り込みコミット)へ更新。
- 裁定 4 点は**すべて推奨案を採択**: ①E06/E09 の要求単位を「cutoff 以降に発生した遷移」へ
  ②証拠採用を replay 範囲に限定 ③hook 内容検査は **E11 新設** ④保護パス履歴検査は E01 再利用+
  `history:<sha>`・rev-list で絞る。
- **製造中の設計確定(理由記録)**:
  1. **replay の列挙に `--full-history` を使う** — 既定の履歴簡略化は「片親と TREESAME な merge」を
     省略するため、**merge が親合算に対して持ち込む後退**を再演が取りこぼす。fail-closed 方向へ
     倒す(所要増は受入で実測)。
  2. **保護パス履歴検査の範囲は `cutoff..HEAD`(cutoff を含まない)** — 導入 commit 自体が既存
     `src/` を含む場合に誤 FAIL しないため(台帳再演は `cutoff^..HEAD` で cutoff を含む — 新規
     scaffold では cutoff が台帳を新設するため必要。**面ごとに境界の端点が違う理由を記録する**)。
  3. **hook 判定の単一実装は validator 側に置く** — qualification は importlib で validator を
     ロード済みのため、その関数を参照する(契約の二重定義を作らない= silence §16(e) の自己適用)。
> 出典: ECO-018 再々独立検査(transfer-04 様式・Codex gpt-5.6-sol・REJECT)—
> bomdd/reports/independent-reinspection-eco-018.md(真正判定 全件 CONFIRMED・実プローブ 4)。
> 本 ECO は**在庫可能な機械的欠陥**を是正する。IA-02/IA-03 は是正せず**境界として文書化**する
> (下記「是正しない範囲」— 無限の ECO 連鎖に入らないための明示的裁定)。

## 起票(2026-07-27)

### 是正する 4 件(すべて実プローブで再現確認済み)

1. **IA-05 — 同一走査内の基準不一致(証拠採用が第 1 親比較)**: 履歴再演は親合算を base に
   するのに、trailer 証拠の採用は `reg_at(sha^)`(第 1 親)で遷移を判定している。実測(P-B):
   第 1 親 staged・第 2 親 applied(trailer なし)・merge に accept trailer → **遷移していない
   merge が accept 証拠として採用**され validate OK。
   - 是正: replay で算出した**合算 base を sha ごとにキャッシュ**し、trailer 証拠の採用も
     同じ base との比較でのみ行う。`sha^` 比較は廃止。証拠採用の対象も replay 範囲に限定する
     (範囲外の trailer は E07 の参照検査にのみ計上)。
2. **IA-04 — 証拠要求の単位が「ECO の初出」で切られている**: 導入点より前から台帳にあった ECO は
   ID ごと免除されるため、**導入後に発生した遷移まで免除**される。実測(P-C): legacy ECO を
   導入後に applied へ(trailer なし)→ `証拠要求 0 件・validate OK`。
   - 是正: 免除の単位を **「cutoff 時点で到達済みだった状態」**に変える。replay 中に
     「cutoff 以降に実際に発生した遷移 `(cid, to_state)`」を集め、**その遷移集合に対して**
     E06/E09 を要求する(legacy ECO でも導入後の遷移は対象)。
3. **IA-01 — 設備の無力化(置換)が検出されない**: E10 は存在のみを見るため、両 hook を
   `#!/bin/sh; exit 0` へ**置換**すると第 1 層が自分の無力化を見ず(実行されるのは置換後の
   stub)、第 2 層も無音 PASS。実測(P-A2)で commit 成立・validate OK。
   - 是正: validate に **hook 内容検査(新 E11)** を追加 — hook が validator を該当モードで
     起動する構造を持つか。判定は qualification の `_hook_invokes_validator` と**同一の解釈
     関数を共有**する(契約の二重定義は緩い側が必ず緩む — ViewPrism2 ECO-078 教訓。実装は
     validator 側に公開し qualification が参照)。
4. **保護パス変更の履歴検査の不在**(P-A2 後半・報告より重い実測): 第 2 層は台帳の遷移しか
   再演していないため、hook 無力化後の **ECO なし保護パス変更が validate でも検出されない**。
   - 是正: cutoff 以降で保護パスに触れた commit を走査し、その時点で open ECO があったかを
     検査(**E01 の履歴版**・`history:<sha>` 文脈)。

### 是正しない範囲(境界として文書化する — 裁定として明示)

**IA-02(cutoff の前送り)・IA-03(HEAD profile の遡及適用)は本 ECO で是正しない。**
理由: 両者は個別の実装欠陥ではなく「**検査規則が被検査物の中にある**」ことの系である。
profile(規則)・cutoff(適用範囲)・hooks(実行体)はいずれも commit 権限者が書き換えられ、
リポ内でどれだけ検査を足しても、その検査の**パラメータ自体**が攻撃面として残る。
- 真の閉鎖経路= **リポ外の信頼アンカー**(CI 設定・branch protection・外部で固定した規則版と
  内容ハッシュ)。これは process-core(リポ内設備)の守備範囲外であり、運用側の責務。
- 本 ECO では **order とテンプレ(process-profile.yaml のコメント)へ限界を明記**し、
  完了判定に残す。将来の閉鎖は「外部アンカーの設計」として別系列で扱う。
- 影響の非対称性の記録: 攻撃者が cutoff/規則を動かすには profile の変更が要り、それ自体は
  E08(open ECO 必須)+ diff に残る。**無音ではない**(監査可能)が、**阻止はできない**。

## 裁定を要する設計点(gate ① で裁定)

1. **E06/E09 の要求単位**を「現在状態が要求する全 trailer」→「cutoff 以降に発生した遷移」へ
   変更(IA-04)。新規 scaffold では実質同一(全遷移が cutoff 以降)。**推奨= 採用**。
2. **証拠採用の範囲**を replay 範囲に限定(IA-05 の帰結)。cutoff 前の trailer は E07 のみに
   計上。**推奨= 採用**。
3. **hook 内容検査の reason code**: E10 拡張 / 新 **E11**。**推奨= E11 新設**(「欠落」と
   「存在するが無力」は別事象 — 負例・是正・報告文が別になるため分けたほうが診断的)。
4. **保護パス履歴検査の code と走査範囲**: E01 再利用+`history:<sha>` / 走査は
   `rev-list <cutoff>^..HEAD -- <protected_paths>` で絞る。**推奨= 採用**(所要増は受入で実測。
   現在 119s に対し +30s を超えたら最適化を次 ECO へ切り出す)。

## 受入基準(事前登録 — 製造前に凍結する)

- 陽性対照: 既存 24 対照すべて判定不変(POS・POS2・N1〜N14・IQ-01〜07・DET)
- 新規負例(qualification へ恒久収載):
  - **N15**(IA-04): 導入前から staged の legacy ECO を導入後に applied(trailer なし)→ **E06**
  - **N16**(IA-05): 第 1 親 staged・第 2 親 applied(trailer なし)・merge に accept trailer →
    **E06**(偽証拠を採用しない)
  - **N17**(IA-01): 両 hook を pass-through stub へ置換 → validate が **E11**
  - **N18**(保護パス履歴): hook 無力化後に ECO なしで保護パス変更 → validate が **E01(history)**
- 誤 FAIL 方向の陽性対照:
  - **POS3**: 導入前に既に applied へ到達していた legacy ECO は証拠を要求されない
    (IA-04 是正が免除を消しすぎないこと — POS2 の精密版)
  - **POS4**: 正規 merge(両親とも合法・accept trailer つき)が誤 FAIL しない
- 決定性: qualification 2 回実行の判定・理由集合一致
- 回帰: self-conformance 全 PASS・**所要の実測記録**(基準線 119s)
- 再独立検査: 是正後に fresh 検査官で IA-01/04/05+保護パス面の閉鎖確認(IA-02/03 は対象外
  =境界として申告する)

## 影響分析(製造前予測 — 未凍結)

- 影響なし予測: `method/templates/process-core/tools/process-validator.py`・
  `method/templates/process-core/tools/process-qualification.py`・
  `method/templates/process-core/process-profile.yaml`(限界の明記)以外 diff ゼロ予測。
- **正常運用への影響**: 新規 scaffold の判定は不変(全遷移が cutoff 以降のため要求単位の変更が
  効かない)。変わるのは (i) 後から導入したリポで導入後の遷移に証拠が要るようになる(意図的)
  (ii) merge の証拠採用が厳格化(正規 merge は POS4 で誤 FAIL しないことを確認)
  (iii) validate の所要増(保護パス走査の分)。
- 既存製品リポへは kit 再設置まで非波及(ECO-004 設計)。

## 是正(2026-07-27・fix= f6a840c)

1. **IA-05(基準統一)**: replay で算出した合算 base を `base_at[sha]` にキャッシュし、trailer 証拠の
   採用も**同じ base** で遷移を判定。`sha^`(第 1 親)比較を廃止し、**証拠採用を replay 範囲へ限定**
   (範囲外の trailer は E07 の参照検査にのみ計上)。
2. **IA-04(証拠要求単位)**: `scoped`(cid 集合)を **`required`(遷移集合 `{(cid, to_state)}`)**へ
   置換。replay 中に「base と cur で状態が変化した」ものを収集し、E06 はその遷移にのみ要求。
   免除されるのは「導入点で到達済みの状態」だけ。
3. **IA-01(E11 新設)**: `hook_invokes_validator()` を validator 側の**単一実装**として公開し、
   validate の E11 と qualification の IQ-02 が共有(判定基準を 2 箇所に置かない= silence §16(e)
   の自己適用)。存在(E10)と有効性(E11)を別 code に分離。
4. **保護パス履歴検査**: `rev-list --full-history <cutoff>..HEAD -- <protected_paths>` で走査し、
   各 commit の親合算状態に open ECO があったかを検査(E01+`history:<sha>`)。
5. **`--full-history`**(設計確定 1): 台帳 replay・保護パス走査とも履歴簡略化を無効化。
6. **境界の文書化**: process-profile.yaml に「既知の限界」節 — 規則・適用範囲・実行体は commit
   権限者が書き換え可能・**無音ではないが阻止はできない**・完全閉鎖はリポ外アンカーの責務。

## 検証(2026-07-27・受入基準=起票時凍結分)

- **V0(selftest)**: 56 項目全 PASS(ECO-019 分= E11 4 項目+IA-04 の要求単位 3 項目)。
- **V1(全対照)**: fresh scaffold の full qualification **30 対照すべて PASS** —
  IQ-01〜07・POS・POS2・**POS3**・**POS4**・N1〜N14・**N15〜N18**・DET(2 回一致)。
  既存 24 対照の判定は不変(回帰)。所要 161s(--runs 2)。
- **V2(再々検査の再現条件を直接プローブ)**: P-A2= hook 置換のみ → **E11 検出**、続く ECO なし
  保護パス変更 → **`[E01] history:d234f18f7` 検出**(第 1 層を回避しても第 2 層が捕捉)/
  P-B= merge 第 1 親トリック → **E06**(偽証拠を採用しない)/ P-C= legacy ECO の導入後遷移 →
  **E06**。**3 件とも閉鎖**。
- **V3(回帰)**: self-conformance 全 PASS(C1〜C11)。所要 119s → **136s**(+17s — 受入の
  「+30s 超なら最適化を切り出す」基準内)。
- **V4(誤 FAIL 方向)**: POS3(導入点で到達済みの状態は証拠不要)・POS4(正規 merge が通る)とも
  PASS — IA-04 の是正が免除を消しすぎず、`--full-history` 化が正規 merge を誤 FAIL しない。
- 影響なし予測: 的中(diff は process-core 3 面+台帳系のみ)。意図的変更 3 点は V1/V2/V3 で実測。

## 是正しなかった項目の状態(申告)

IA-02(cutoff 前送り)・IA-03(規則の遡及適用)は**未是正のまま**であり、上記の限界節へ明記した。
次の独立検査ではこれらを「宣言済み境界」として申告する — 境界と未検出欠陥の区別が成立するかが
EXP-20260727-06 の測定項目。

## 教訓(還元候補 — lesson-promote 経由)

- **検査面ごとに境界の端点が違うことがある**(設計確定 2): 台帳 replay は導入 commit を**含む**
  (新規 scaffold では導入 commit が台帳を新設するため)が、保護パス検査は導入 commit を**含まない**
  (既存 src/ を巻き込む採用 commit を誤 FAIL しないため)。同じ cutoff でも面ごとに端点の
  開閉が変わる — **端点の選択理由を面ごとに記録する**。
- **履歴を検査に使うなら履歴簡略化を切る**: `git log/rev-list` の既定はパス限定時に「片親と
  TREESAME な merge」を省く。人間の閲覧には便利だが、**検査では取りこぼしになる**
  (merge が親合算に対して持ち込む後退が見えない)。

## 効果測定(宿題)

- 再独立検査で IA-01/04/05+保護パス面が CLOSED になるか(通算 25 提起の閉鎖率)
- 「リポ内規則は自己アンカーできない」の境界宣言が、次の検査で**境界として受理される**か
  (= 同じ穴が新規所見として再提起されない — 宣言済み限界と未検出欠陥の区別が成立するか)
