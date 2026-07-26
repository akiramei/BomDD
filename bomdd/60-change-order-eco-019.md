# ECO-019 — 第 2 層の基準統一・証拠要求単位の是正・設備無力化と保護パスの履歴検査(再々独立検査の在庫可能分)

> 状態: **filed(2026-07-27)**。製造前 — gate ①(製造承認+設計裁定 4 点)待ち。
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

## 効果測定(宿題)

- 再独立検査で IA-01/04/05+保護パス面が CLOSED になるか(通算 25 提起の閉鎖率)
- 「リポ内規則は自己アンカーできない」の境界宣言が、次の検査で**境界として受理される**か
  (= 同じ穴が新規所見として再提起されない — 宣言済み限界と未検出欠陥の区別が成立するか)
